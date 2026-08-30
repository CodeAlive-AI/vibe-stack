"""Read-only, offline Capacitor 8.5 file checks. Python 3.10+, standard library."""
import hashlib
import json
import os
import plistlib
import re
import stat
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

MAX_FILE = 16 * 1024 * 1024
MAX_FILES = 20000
MAX_TOTAL = 512 * 1024 * 1024
LOCKS = {'pnpm': 'pnpm-lock.yaml', 'npm': 'package-lock.json', 'yarn': 'yarn.lock', 'bun': 'bun.lock'}
VERSION = re.compile(r'8\.5\.\d+\Z')
FORBIDDEN = {'.git', '.ssh', '.aws', '.azure', '.gnupg', '.npmrc', '.pypirc', '.netrc',
             '.zshrc', '.bashrc', '.bash_profile', '.profile', 'credentials', 'id_rsa', 'id_ed25519'}


class Unverified(Exception):
    pass


class Audit:
    def __init__(self, app, workspace):
        self.app = Path(app).resolve()
        self.workspace = Path(workspace).resolve()
        if not self.app.is_relative_to(self.workspace):
            raise Unverified('App must be inside the explicit workspace boundary.')
        self.findings = []

    def add(self, rule, status, message, path=None):
        item = {'id': rule, 'status': status, 'message': message}
        if path is not None:
            p = Path(path)
            item['path'] = p.relative_to(self.workspace).as_posix() if p.is_relative_to(self.workspace) else '[outside workspace]'
        self.findings.append(item)

    def safe(self, path):
        p = Path(path)
        for candidate in (p, p.resolve()):
            if not candidate.is_relative_to(self.workspace):
                raise Unverified('Path or symlink escapes workspace; no content read.')
            for part in candidate.relative_to(self.workspace).parts:
                if part in FORBIDDEN or part.startswith('.env') or part.lower().endswith(('.key', '.p12', '.pfx', '.pem', '.jks', '.keystore')):
                    raise Unverified('Sensitive path excluded; no content read.')
        return p.resolve()

    def read(self, path):
        p = self.safe(path)
        mode = p.stat().st_mode
        if not stat.S_ISREG(mode):
            raise Unverified('Expected a regular file; devices, directories and pipes are not read.')
        if p.stat().st_size > MAX_FILE:
            raise Unverified('File exceeds bounded inspection limit.')
        with p.open('rb') as stream:
            data = stream.read(MAX_FILE + 1)
        if len(data) > MAX_FILE:
            raise Unverified('File exceeds bounded inspection limit.')
        return data

    def json(self, path):
        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError('duplicate key')
                result[key] = value
            return result
        data = json.loads(self.read(path), object_pairs_hook=unique,
                          parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite')))
        if not isinstance(data, dict):
            raise ValueError('object required')
        return data

    def attempt(self, rule, path, operation):
        try:
            return operation()
        except FileNotFoundError:
            self.add(rule, 'fail', 'Required file is missing.', path)
        except Unverified as exc:
            self.add(rule, 'review', str(exc), path)
        except (RuntimeError, RecursionError):
            self.add(rule, 'review', 'Cannot inspect recursive input or resolve symlink path.', path)
        except (ValueError, TypeError, KeyError, UnicodeError, ET.ParseError, plistlib.InvalidFileException):
            self.add(rule, 'fail', 'Malformed or unsupported input; raw content suppressed.', path)
        except OSError:
            self.add(rule, 'review', 'Input could not be read; check access and file type.', path)
        return None

    def tree(self, directory):
        directory = self.safe(directory)
        if not directory.is_dir():
            raise FileNotFoundError()
        result, total, count = {}, 0, 0
        for parent, dirs, files in os.walk(directory, followlinks=False):
            dirs.sort(); files.sort()
            for name in dirs:
                p = Path(parent) / name
                self.safe(p)
                if name == 'node_modules':
                    raise Unverified('node_modules inside a shipped artifact requires inspection; dependencies not recursively read.')
                if p.is_symlink():
                    raise Unverified('Symlinked artifact directories require separate inspection.')
            count += len(dirs) + len(files)
            if count > MAX_FILES:
                raise Unverified('Artifact exceeds bounded entry count.')
            for name in files:
                p = Path(parent) / name
                data = self.read(p)
                total += len(data)
                if total > MAX_TOTAL:
                    raise Unverified('Artifact exceeds bounded total bytes.')
                result[p.relative_to(directory).as_posix()] = hashlib.sha256(data).hexdigest()
        return result


def check_project(audit, platforms):
    path = audit.app / 'package.json'
    package = audit.attempt('project.manifest', path, lambda: audit.json(path))
    if package is None:
        return
    declarations = {}
    for section in ('dependencies', 'devDependencies'):
        values = package.get(section, {})
        if not isinstance(values, dict):
            audit.add('project.manifest', 'fail', 'Dependency sections must be objects.', path)
            return
        declarations.update(values)
    versions = []
    for name in ['@capacitor/core', '@capacitor/cli'] + ['@capacitor/' + p for p in platforms]:
        if name not in declarations:
            audit.add('project.declared', 'fail', name + ' must be declared by the app package.', path)
        current, resolved = audit.app, None
        while current.is_relative_to(audit.workspace):
            candidate = current / 'node_modules' / name / 'package.json'
            if candidate.exists() or candidate.is_symlink():
                resolved = candidate
                break
            if current == audit.workspace:
                break
            current = current.parent
        if resolved is None:
            audit.add('project.installed', 'review', name + ' not locally resolved; no installation attempted.')
            continue
        manifest = audit.attempt('project.installed', resolved, lambda: audit.json(resolved))
        if manifest is None:
            continue
        version = manifest.get('version')
        valid = manifest.get('name') == name and isinstance(version, str) and VERSION.fullmatch(version)
        audit.add('project.version', 'pass' if valid else 'fail', name + (' resolves to stable 8.5.x.' if valid else ' does not resolve to a valid stable 8.5.x manifest.'), resolved)
        if valid:
            versions.append(version)
        declared = declarations.get(name)
        if isinstance(declared, str) and re.fullmatch(r'\d+\.\d+\.\d+', declared) and declared != version:
            audit.add('project.install-drift', 'fail', 'Exact declaration differs from installed package.', path)
    if len(versions) == 2 + len(platforms):
        audit.add('project.alignment', 'pass' if len(set(versions)) == 1 else 'fail', 'Core, CLI and selected native packages must resolve to the same patch.')
    ancestors = [audit.app]
    while ancestors[-1] != audit.workspace:
        ancestors.append(ancestors[-1].parent)
    locks = [(p / filename, manager) for p in ancestors for manager, filename in LOCKS.items() if (p / filename).is_file()]
    locks += [(p / 'bun.lockb', 'bun') for p in ancestors if (p / 'bun.lockb').is_file()]
    audit.add('project.lockfile', 'pass' if len(locks) == 1 else 'review', 'Exactly one lockfile found in app ancestry.' if len(locks) == 1 else 'Missing or multiple lockfiles; resolve workspace/package-manager ownership. Lock contents are not evaluated.')
    owners = [package]
    if audit.app != audit.workspace:
        owner = audit.attempt('project.workspace', audit.workspace / 'package.json', lambda: audit.json(audit.workspace / 'package.json'))
        if owner is not None:
            owners.append(owner)
    managers = [m.get('packageManager') for m in owners if m.get('packageManager') is not None]
    if managers:
        names = {m.split('@')[0] for m in managers if isinstance(m, str)}
        okay = len(names) == 1 and all(isinstance(m, str) for m in managers) and (not locks or all(v in names for _, v in locks))
        audit.add('project.manager', 'pass' if okay else 'fail', 'Declared package manager must agree with app/workspace lockfile ownership.')
    scripts = package.get('scripts', {})
    if not isinstance(scripts, dict):
        audit.add('project.scripts', 'fail', 'Scripts must be an object.', path)
    elif any(k in {'preinstall', 'install', 'postinstall', 'prepare'} or k.startswith('capacitor:') for k in scripts):
        audit.add('project.hooks', 'review', 'Install/Capacitor hooks exist; review them before executing project tools. Bodies were not printed.', path)
    configs = [audit.app / ('capacitor.config.' + ext) for ext in ('ts', 'js', 'json')]
    count = sum(p.is_file() for p in configs)
    audit.add('project.config-source', 'pass' if count == 1 else 'review', 'One source config located; JS/TS was not executed or validated.' if count == 1 else 'Missing or competing source configs; confirm CLI selection.')


class EntryParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.head = False
        self.resources = []
        self.bases = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'head': self.head = True
        if tag == 'base' and attrs.get('href'): self.bases.append(attrs['href'])
        if tag == 'script' and attrs.get('src'): self.resources.append(attrs['src'])
        if tag == 'link' and set(attrs.get('rel', '').lower().split()) & {'stylesheet', 'modulepreload', 'preload'} and attrs.get('href'):
            self.resources.append(attrs['href'])


def check_web(audit, web):
    manifest = audit.attempt('web.inventory', web, lambda: audit.tree(web))
    if manifest is None:
        return None
    audit.add('web.inventory', 'pass', 'Artifact files read within limits and hashed.', web)
    if 'index.html' not in manifest:
        audit.add('web.entry', 'fail', 'webDir needs a built index.html, not a Next server/.next directory.', web)
        return manifest
    for rel in sorted(manifest):
        if not rel.lower().endswith('.html'):
            continue
        path = web / rel
        def inspect():
            parser = EntryParser()
            parser.feed(audit.read(path).decode('utf-8'))
            if rel == 'index.html':
                audit.add('web.entry', 'pass' if parser.head else 'fail', 'index.html must contain a head element for Capacitor injection.', path)
            if parser.bases:
                audit.add('web.base-url', 'review', 'Explicit HTML base URL needs router/asset resolution review; references in this document not certified.', path)
                return
            for value in parser.resources:
                url = urlsplit(value)
                if url.scheme or url.netloc:
                    audit.add('web.external-resource', 'review', 'External/inline-scheme startup resource; assess offline behavior and script trust. URL suppressed.', path)
                    continue
                local = unquote(url.path)
                if not local:
                    continue
                if local.lower().endswith(('.tsx', '.jsx', '.ts')):
                    audit.add('web.unbuilt-script', 'fail', 'Startup resource uses an uncompiled TypeScript/JSX extension; inspect the production build.', path)
                target = web / local.lstrip('/') if local.startswith('/') else path.parent / local
                target = target.resolve()
                if not target.is_relative_to(web.resolve()):
                    audit.add('web.resource-path', 'fail', 'Startup resource escapes webDir.', path)
                elif target.relative_to(web.resolve()).as_posix() not in manifest:
                    audit.add('web.resource-missing', 'fail', 'Referenced local startup resource is absent from the artifact. URL suppressed.', path)
            audit.add('web.html-inspected', 'pass', 'Static script/style/preload references inspected; dynamic chunks, fetches and routes need runtime tests.', path)
        audit.attempt('web.html', path, inspect)
    return manifest


def check_config(audit, path, platform, web, expected_id):
    config = audit.attempt(platform + '.config', path, lambda: audit.json(path))
    if config is None:
        return None
    def emit(key, okay, message): audit.add(platform + '.config.' + key, 'pass' if okay else 'fail', message, path)
    app_id = config.get('appId')
    emit('identity', isinstance(app_id, str) and bool(re.fullmatch(r'[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)+', app_id)), 'A reverse-domain appId must be present.')
    if expected_id is not None: emit('expected-id', app_id == expected_id, 'Native config appId must match the explicitly selected identity.')
    if 'webDir' in config:
        value = config['webDir']
        emit('web-dir', isinstance(value, str) and (audit.app / value).resolve() == web.resolve(), 'Copied webDir must match the explicitly inspected artifact.')
    for section in ('server', 'ios', 'android'):
        if section in config and not isinstance(config[section], dict):
            emit('shape', False, 'Server/platform configuration must be an object.')
            return config
    server = config.get('server', {})
    emit('local-assets', 'url' not in server or server['url'] == '', 'Production must use bundled assets, without server.url.')
    for section, keys in [('server', ('cleartext',)), ('android', ('allowMixedContent', 'webContentsDebuggingEnabled')), ('ios', ('webContentsDebuggingEnabled',))]:
        for key in keys:
            value = config.get(section, {}).get(key, False)
            emit(key, value is False, 'Production unsafe/debug boolean must be absent or false: ' + section + '.' + key)
    nav = server.get('allowNavigation', [])
    if not isinstance(nav, list): emit('navigation', False, 'allowNavigation must be a list.')
    elif any(not isinstance(v, str) for v in nav): emit('navigation', False, 'Navigation entries must be strings.')
    elif any('*' in v for v in nav): emit('navigation', False, 'Wildcard navigation permissions are excluded by this production profile.')
    elif nav: audit.add(platform + '.config.navigation', 'review', 'Nonempty WebView navigation allowlist requires explicit bridge/trust review; values suppressed.', path)
    for section in [config, config.get('ios', {}), config.get('android', {})]:
        if section.get('loggingBehavior') == 'production':
            audit.add(platform + '.config.logging', 'review', 'Production logging requires a privacy review.', path)
    def secret_fields(value):
        if isinstance(value, dict):
            return any((isinstance(k, str) and k.lower() in {'keystorepassword', 'keystorealiaspassword', 'password', 'clientsecret', 'privatekey'} and v not in (None, '')) or secret_fields(v) for k, v in value.items())
        return isinstance(value, list) and any(secret_fields(v) for v in value)
    emit('credential-fields', not secret_fields(config), 'Known credential fields must not contain values. This is not a complete secret scanner.')
    return config


def compare_copy(audit, platform, source, destination):
    target = audit.attempt(platform + '.copy', destination, lambda: audit.tree(destination))
    if source is None or target is None:
        audit.add(platform + '.copy-comparison', 'review', 'Both complete artifact inventories are needed to compare copied assets.')
        return
    missing = sum(name not in target for name in source)
    changed = sum(name in target and target[name] != digest for name, digest in source.items())
    audit.add(platform + '.copy-comparison', 'fail' if missing or changed else 'pass', f'Source-to-native content comparison: {missing} missing, {changed} changed files. No timestamps used.', destination)
    generated = {'capacitor.js', 'capacitor.js.map', 'cordova.js', 'cordova_plugins.js'}
    extra = [name for name in target if name not in source and name not in generated and not name.startswith('plugins/')]
    if extra:
        audit.add(platform + '.copy-extra', 'review', f'{len(extra)} extra files in native web assets; distinguish generated files from stale bundles.', destination)


def check_ios(audit, root, config, plist_path):
    def inspect_plist():
        data = plistlib.loads(audit.read(plist_path))
        if not isinstance(data, dict): raise ValueError()
        scenes = data.get('UIApplicationSceneManifest', {})
        if not isinstance(scenes, dict): raise ValueError()
        roles = scenes.get('UISceneConfigurations', {})
        if not isinstance(roles, dict): raise ValueError()
        entries = roles.get('UIWindowSceneSessionRoleApplication', [])
        okay = isinstance(entries, list) and bool(entries) and all(isinstance(v, dict) and isinstance(v.get('UISceneDelegateClassName'), str) and v['UISceneDelegateClassName'] for v in entries)
        audit.add('ios.scene-manifest', 'pass' if okay else 'review', 'Scene delegate declared; target membership and callback forwarding still need a build/runtime check.' if okay else 'UIScene declaration not established. Resolve for modern 8.5/Xcode 27; custom generated plist may need an explicit --ios-plist.', plist_path)
        ats = data.get('NSAppTransportSecurity', {})
        if not isinstance(ats, dict): raise ValueError()
        permissive = any(ats.get(k) is not False for k in ('NSAllowsArbitraryLoads', 'NSAllowsArbitraryLoadsInWebContent', 'NSAllowsLocalNetworking') if k in ats)
        audit.add('ios.ats', 'fail' if permissive else 'pass', 'Broad ATS/local-network exceptions must not remain in this production profile.', plist_path)
        if ats.get('NSExceptionDomains'):
            audit.add('ios.ats-domains', 'review', 'Domain-specific ATS exceptions need transport/security review.', plist_path)
        domains = data.get('WKAppBoundDomains')
        if domains is None and isinstance(config, dict) and isinstance(config.get('ios', {}), dict) and config.get('ios', {}).get('limitsNavigationsToAppBoundDomains') is True:
            audit.add('ios.app-bound', 'fail', 'App-bound navigation is enabled but WKAppBoundDomains is absent from the supplied plist.', plist_path)
        if domains is not None:
            settings = config.get('ios', {}) if isinstance(config, dict) else {}
            server = config.get('server', {}) if isinstance(config, dict) else {}
            if not isinstance(settings, dict) or not isinstance(server, dict): raise ValueError()
            okay = isinstance(domains, list) and all(isinstance(d, str) for d in domains) and server.get('hostname', 'localhost') in domains and settings.get('limitsNavigationsToAppBoundDomains') is True
            audit.add('ios.app-bound', 'pass' if okay else 'fail', 'Keep app-bound restrictions; enable limitsNavigationsToAppBoundDomains and include the local hostname.', plist_path)
        bundle_id = data.get('CFBundleIdentifier')
        if isinstance(config, dict) and isinstance(bundle_id, str) and '$' not in bundle_id:
            audit.add('ios.bundle-id', 'pass' if bundle_id == config.get('appId') else 'fail', 'Literal plist bundle identifier must match copied appId.', plist_path)
        else:
            audit.add('ios.bundle-id', 'review', 'Bundle identifier not resolved; inspect a built plist with --ios-plist. Source build variables are not evaluated.', plist_path)
    audit.attempt('ios.plist', plist_path, inspect_plist)
    spm = root / 'App/CapApp-SPM/Package.swift'
    pods = root / 'App/Podfile'
    has_spm, has_pods = spm.is_file(), pods.is_file()
    if has_spm != has_pods:
        audit.add('ios.package-manager', 'pass', 'Detected SPM project shape.' if has_spm else 'Detected CocoaPods project shape; not automatically migrated.', root)
    else: audit.add('ios.package-manager', 'review', 'Ambiguous/custom native package-manager layout; inspect project references.', root)
    project = root / 'App/App.xcodeproj/project.pbxproj'
    audit.add('ios.project', 'pass' if project.is_file() else 'review', 'Standard Xcode project located; no compile or scheme/target validation performed.' if project.is_file() else 'Custom/missing Xcode project requires manual resolution.', root)


def check_android(audit, root, manifest_path):
    def parse_xml(path):
        content = audit.read(path)
        if b'<!DOCTYPE' in content.upper() or b'<!ENTITY' in content.upper(): raise ValueError()
        return ET.fromstring(content)

    def network_policy(reference, origin):
        if not re.fullmatch(r'@xml/[a-z0-9_]+', reference):
            audit.add('android.network-security', 'review', 'Network security resource cannot be resolved statically; inspect merged release resources.', origin)
            return
        name = reference.split('/')[1] + '.xml'
        candidates = [root / 'app/src' / kind / 'res/xml' / name for kind in ('main', 'release')]
        candidates = [p for p in candidates if p.is_file()]
        if not candidates:
            audit.add('android.network-security', 'review', 'Network security resource missing/custom; inspect merged release resources.', origin)
        for candidate in candidates:
            def inspect_policy():
                tree = parse_xml(candidate)
                if tree.tag != 'network-security-config': raise ValueError()
                # debug-overrides are deliberately excluded from a production policy check.
                for scope in tree:
                    if scope.tag == 'debug-overrides': continue
                    for node in scope.iter():
                        value = node.get('cleartextTrafficPermitted')
                        if value not in (None, 'false'):
                            audit.add('android.network-cleartext', 'fail' if value == 'true' else 'review', 'Release-relevant network config allows cleartext or contains an unresolved value.', candidate)
                        if node.tag == 'certificates' and node.get('src') == 'user':
                            audit.add('android.user-ca', 'review', 'User-installed certificate authority trusted outside debug overrides; security review required.', candidate)
                audit.add('android.network-resource', 'pass', 'Static network-security resource inspected; final variant/resource merging remains a build check.', candidate)
            audit.attempt('android.network-resource', candidate, inspect_policy)

    def inspect(path, overlay=False):
        element = parse_xml(path)
        if element.tag != 'manifest': raise ValueError()
        app = element.find('application')
        if app is None:
            if overlay: return
            raise ValueError()
        ns = '{http://schemas.android.com/apk/res/android}'
        for attr in ('debuggable', 'usesCleartextTraffic'):
            value = app.get(ns + attr)
            status = 'pass' if value in (None, 'false') else ('fail' if value == 'true' else 'review')
            audit.add('android.' + attr, status, 'Manifest attribute must not enable production debugging/cleartext; unresolved placeholders require merged-manifest inspection.', path)
        if app.get(ns + 'networkSecurityConfig'):
            network_policy(app.get(ns + 'networkSecurityConfig'), path)
        for child in app:
            if child.tag in ('activity', 'activity-alias', 'service', 'receiver') and child.find('intent-filter') is not None:
                exported = child.get(ns + 'exported')
                if exported not in ('true', 'false'):
                    audit.add('android.exported', 'review', 'Intent-filter component has no resolved exported boolean; validate final merged manifest.', path)
        audit.add('android.manifest', 'pass', 'Supplied XML inspected. Main source does not prove merged release manifest, SDK levels or Gradle/toolchain correctness.', path)
    audit.attempt('android.manifest', manifest_path, lambda: inspect(manifest_path))
    if manifest_path == root / 'app/src/main/AndroidManifest.xml':
        release = root / 'app/src/release/AndroidManifest.xml'
        if release.is_file():
            audit.attempt('android.release-overlay', release, lambda: inspect(release, overlay=True))
    wrapper = root / 'gradle/wrapper/gradle-wrapper.properties'
    audit.add('android.wrapper', 'pass' if wrapper.is_file() else 'review', 'Gradle wrapper metadata located; no Gradle code executed.' if wrapper.is_file() else 'Gradle wrapper metadata missing/custom; inspect build setup.', root)
