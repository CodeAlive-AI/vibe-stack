#!/usr/bin/env python3
"""Deterministic production-profile checks; never execute the inspected repository."""
import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from capacitor_checks import (Audit, Unverified, check_project, check_web, check_config,
                              compare_copy, check_ios, check_android)


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(64, 'Invalid arguments; use --help.\n')


def run(argv=None):
    parser = Parser(description=__doc__)
    parser.add_argument('--app', required=True, type=Path, help='Exact app package directory')
    parser.add_argument('--workspace', type=Path, help='Explicit read boundary (default: app); needed for hoisted pnpm/npm dependencies')
    parser.add_argument('--checks', choices=('project', 'web', 'native', 'all'), default='all')
    parser.add_argument('--platform', action='append', choices=('ios', 'android'), help='Repeat for both; unselected platform is not required')
    parser.add_argument('--web-dir', type=Path, help='Built local artifact path relative to app, or absolute within workspace')
    parser.add_argument('--ios-root', type=Path, default=Path('ios'))
    parser.add_argument('--android-root', type=Path, default=Path('android'))
    parser.add_argument('--ios-plist', type=Path, help='Optional source or built plist, relative to app (default ios-root/App/App/Info.plist)')
    parser.add_argument('--android-manifest', type=Path, help='Optional merged release XML, relative to app (default android-root/app/src/main/AndroidManifest.xml)')
    parser.add_argument('--expected-app-id', help='Optional intended app identifier, compared to copied native config')
    parser.add_argument('--format', choices=('json', 'text'), default='json')
    args = parser.parse_args(argv)
    if args.checks != 'project' and args.web_dir is None:
        parser.error('--web-dir required')
    if args.checks in ('native', 'all') and not args.platform:
        parser.error('--platform required')
    platforms = sorted(set(args.platform or []))
    try:
        audit = Audit(args.app, args.workspace or args.app)
        if not audit.app.is_dir() or not audit.workspace.is_dir():
            raise Unverified('App/workspace must be existing directories.')
    except (Unverified, OSError, RuntimeError):
        print(json.dumps({'schema_version': 1, 'status': 'review', 'findings': [{'id': 'input.boundary', 'status': 'review', 'message': 'Cannot establish existing app/workspace boundary.'}]}, sort_keys=True))
        return 2
    def path(value):
        # Do not resolve here: Audit.safe inspects both lexical and resolved paths.
        return audit.app / value
    web = path(args.web_dir) if args.web_dir is not None else None
    try:
        if args.checks in ('project', 'all'):
            check_project(audit, platforms)
        source = None
        if args.checks in ('web', 'all'):
            source = check_web(audit, web)
        elif args.checks == 'native':
            source = audit.attempt('web.inventory', web, lambda: audit.tree(web))
        configs = []
        if args.checks in ('native', 'all'):
            for platform in platforms:
                root = path(args.ios_root if platform == 'ios' else args.android_root)
                native = root / ('App/App' if platform == 'ios' else 'app/src/main/assets')
                config = check_config(audit, native / 'capacitor.config.json', platform, web, args.expected_app_id)
                if config is not None: configs.append(config.get('appId'))
                compare_copy(audit, platform, source, native / 'public')
                if platform == 'ios':
                    check_ios(audit, root, config, path(args.ios_plist) if args.ios_plist else native / 'Info.plist')
                else:
                    check_android(audit, root, path(args.android_manifest) if args.android_manifest else root / 'app/src/main/AndroidManifest.xml')
            if len(configs) > 1:
                audit.add('native.identity-alignment', 'pass' if all(v == configs[0] for v in configs) else 'fail', 'Selected platforms must share the intended appId; deliberate differences need separate invocations/identity checks.')
    except (Unverified, OSError, RuntimeError, RecursionError):
        audit.add('input.incomplete', 'review', 'Inspection incomplete due to boundary, resource limit or filesystem state; no implicit success.')
    except Exception:
        # Avoid tracebacks containing parsed project values. This is an internal failure, never a pass.
        print(json.dumps({'schema_version': 1, 'status': 'error', 'findings': [{'id': 'validator.internal', 'status': 'error', 'message': 'Validator failed; inspect its implementation with a sanitized reproduction.'}]}, sort_keys=True))
        return 70
    audit.findings.sort(key=lambda f: (f['id'], f.get('path', ''), f['status'], f['message']))
    counts = {s: sum(f['status'] == s for f in audit.findings) for s in ('pass', 'fail', 'review')}
    status = 'fail' if counts['fail'] else ('review' if counts['review'] else 'pass')
    result = {'schema_version': 1, 'profile': 'capacitor-8.5-production-files', 'checks': args.checks,
              'platforms': platforms, 'status': status, 'counts': counts, 'findings': audit.findings,
              'limitations': ['Only selected file invariants were checked; pass is not production readiness.',
                              'No config evaluation, dependency install, lockfile resolution, native build, device test or network request.',
                              'No complete secret scan, dynamic route/chunk verification, effective signing, permissions or SDK/toolchain validation.',
                              'Source native plist/manifest may differ from final release output; inspect built artifacts too.']}
    if args.format == 'json':
        print(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True))
    else:
        print(status.upper() + ' — selected static file checks')
        for f in audit.findings:
            print(f"{f['status'].upper()} {f['id']} {f.get('path', '')}: {f['message']}")
        for item in result['limitations']: print('LIMIT: ' + item)
    return {'pass': 0, 'fail': 1, 'review': 2}[status]


if __name__ == '__main__':
    sys.exit(run())
