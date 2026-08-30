#!/usr/bin/env python3
"""Regression fixtures only. No real app, package installation or native tool invocation."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_capacitor import run


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='capacitor-validator-')
        self.root = Path(self.tmp.name).resolve()
        self.app = self.root / 'apps/mobile'
        self.app.mkdir(parents=True)
        self.write(self.root / 'package.json', {'private': True, 'packageManager': 'pnpm@11.0.0'})
        self.write(self.root / 'pnpm-lock.yaml', 'lockfileVersion: 9.0\n')
        deps = {f'@capacitor/{name}': '8.5.0' for name in ('core', 'cli', 'ios', 'android')}
        deps['@capacitor/app'] = '8.1.1'
        self.write(self.app / 'package.json', {'dependencies': deps})
        for name, version in deps.items():
            self.write(self.root / 'node_modules' / name / 'package.json', {'name': name, 'version': version})
        self.write(self.app / 'capacitor.config.ts', 'throw new Error("DO NOT EXECUTE");\n')
        self.write(self.app / 'dist/index.html', '<html><head><script src="/assets/main.js?v=3#x"></script><link rel="stylesheet" href="assets/style.css"></head><body></body></html>')
        self.write(self.app / 'dist/assets/main.js', 'console.log("hello");')
        self.write(self.app / 'dist/assets/style.css', 'body { margin: 0; }')
        self.config = {'appId': 'com.example.mobile', 'webDir': 'dist'}
        self.native = self.app / 'ios/App/App'
        self.write(self.native / 'capacitor.config.json', self.config)
        self.plist = {'CFBundleIdentifier': 'com.example.mobile', 'UIApplicationSceneManifest': {'UISceneConfigurations': {'UIWindowSceneSessionRoleApplication': [{'UISceneDelegateClassName': '$(PRODUCT_MODULE_NAME).SceneDelegate'}]}}}
        self.write_plist()
        self.write(self.app / 'ios/App/CapApp-SPM/Package.swift', '// static evidence, never execute\n')
        self.write(self.app / 'ios/App/App.xcodeproj/project.pbxproj', '// fixture\n')
        self.sync()

    def tearDown(self): self.tmp.cleanup()

    def write(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value) if isinstance(value, dict) else value)

    def write_plist(self):
        (self.native / 'Info.plist').write_bytes(plistlib.dumps(self.plist))

    def sync(self):
        shutil.copytree(self.app / 'dist', self.native / 'public', dirs_exist_ok=True)

    def call(self, *extra, checks='all'):
        args = ['--app', str(self.app), '--workspace', str(self.root), '--checks', checks, '--platform', 'ios']
        if checks != 'project': args += ['--web-dir', 'dist']
        with contextlib.redirect_stdout(io.StringIO()) as output:
            code = run(args + list(extra))
        return code, json.loads(output.getvalue())

    def has(self, result, rule, status):
        return any(f['id'] == rule and f['status'] == status for f in result['findings'])

    def test_valid_ios_only_independent_plugin_version_and_deterministic(self):
        before = self.snapshot()
        first = self.call()
        self.assertEqual(first[0], 0, first)
        self.assertEqual(first, self.call())
        self.assertEqual(before, self.snapshot())

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.rglob('*') if p.is_file()}

    def test_mismatched_platform_patch(self):
        self.write(self.root / 'node_modules/@capacitor/ios/package.json', {'name': '@capacitor/ios', 'version': '8.5.1'})
        code, result = self.call(checks='project')
        self.assertEqual(code, 1)
        self.assertTrue(self.has(result, 'project.alignment', 'fail'))

    def test_alpha_rejected(self):
        self.write(self.root / 'node_modules/@capacitor/core/package.json', {'name': '@capacitor/core', 'version': '9.0.0-alpha.6'})
        code, result = self.call(checks='project')
        self.assertEqual(code, 1)
        self.assertTrue(self.has(result, 'project.version', 'fail'))

    def test_missing_install_is_review(self):
        shutil.rmtree(self.root / 'node_modules')
        code, result = self.call(checks='project')
        self.assertEqual(code, 2)
        self.assertTrue(self.has(result, 'project.installed', 'review'))

    def test_pnpm_symlinks_inside_workspace(self):
        src = self.root / 'node_modules/@capacitor/core'
        dest = self.root / 'node_modules/.pnpm/core@8.5.0/node_modules/@capacitor/core'
        dest.parent.mkdir(parents=True)
        src.rename(dest)
        src.symlink_to(dest, target_is_directory=True)
        self.assertEqual(self.call(checks='project')[0], 0)

    def test_hook_review_without_execution_or_printing(self):
        package = json.loads((self.app / 'package.json').read_text())
        package['scripts'] = {'capacitor:sync:before': 'echo PRIVATE_SENTINEL && touch owned'}
        self.write(self.app / 'package.json', package)
        code, result = self.call(checks='project')
        self.assertEqual(code, 2)
        self.assertNotIn('PRIVATE_SENTINEL', json.dumps(result))
        self.assertFalse((self.app / 'owned').exists())

    def test_missing_static_asset(self):
        (self.app / 'dist/assets/main.js').unlink()
        code, result = self.call(checks='web')
        self.assertEqual(code, 1)
        self.assertTrue(self.has(result, 'web.resource-missing', 'fail'))

    def test_wrong_next_output(self):
        (self.app / 'dist/index.html').unlink()
        code, result = self.call(checks='web')
        self.assertEqual(code, 1)
        self.assertTrue(self.has(result, 'web.entry', 'fail'))

    def test_external_resources_are_review_and_redacted(self):
        self.write(self.app / 'dist/index.html', '<head><script src="https://example.org/main.js?token=PRIVATE_SENTINEL"></script></head>')
        code, result = self.call(checks='web')
        self.assertEqual(code, 2)
        self.assertNotIn('PRIVATE_SENTINEL', json.dumps(result))

    def test_base_url_does_not_claim_reference_resolution(self):
        self.write(self.app / 'dist/index.html', '<head><base href="/sub/"><script src="main.js"></script></head>')
        code, result = self.call(checks='web')
        self.assertEqual(code, 2)
        self.assertTrue(self.has(result, 'web.base-url', 'review'))

    def test_changed_native_copy(self):
        self.write(self.native / 'public/assets/main.js', 'old bundle')
        code, result = self.call(checks='native')
        self.assertEqual(code, 1)
        self.assertTrue(self.has(result, 'ios.copy-comparison', 'fail'))

    def test_generated_cordova_asset_does_not_fail(self):
        self.write(self.native / 'public/cordova.js', '// generated')
        self.assertEqual(self.call()[0], 0)

    def test_stale_extra_asset_review(self):
        self.write(self.native / 'public/old-release.js', 'stale')
        code, result = self.call(checks='native')
        self.assertEqual(code, 2)
        self.assertTrue(self.has(result, 'ios.copy-extra', 'review'))

    def test_remote_url_and_secret_fields_fail_without_values(self):
        self.config.update({'server': {'url': 'http://dev.invalid/?token=PRIVATE_SENTINEL'}, 'android': {'buildOptions': {'keystorePassword': 'PRIVATE_SENTINEL'}}})
        self.write(self.native / 'capacitor.config.json', self.config)
        code, result = self.call(checks='native')
        self.assertEqual(code, 1)
        self.assertNotIn('PRIVATE_SENTINEL', json.dumps(result))
        self.assertTrue(self.has(result, 'ios.config.local-assets', 'fail'))
        self.assertTrue(self.has(result, 'ios.config.credential-fields', 'fail'))

    def test_source_config_cannot_mask_stale_native_config(self):
        self.write(self.app / 'capacitor.config.json', self.config)
        self.write(self.native / 'capacitor.config.json', {**self.config, 'server': {'cleartext': True}})
        code, result = self.call(checks='native')
        self.assertEqual(code, 1)
        self.assertTrue(self.has(result, 'ios.config.cleartext', 'fail'))

    def test_duplicate_json_keys_rejected(self):
        self.write(self.native / 'capacitor.config.json', '{"server":{},"server":{"url":"PRIVATE_SENTINEL"}}')
        code, result = self.call(checks='native')
        self.assertEqual(code, 1)
        self.assertNotIn('PRIVATE_SENTINEL', json.dumps(result))

    def test_malformed_types_do_not_crash(self):
        self.write(self.native / 'capacitor.config.json', {**self.config, 'ios': []})
        code, _ = self.call(checks='native')
        self.assertEqual(code, 1)

    def test_app_bound_both_directions(self):
        self.config['ios'] = {'limitsNavigationsToAppBoundDomains': True}
        self.write(self.native / 'capacitor.config.json', self.config)
        self.assertEqual(self.call(checks='native')[0], 1)
        self.plist['WKAppBoundDomains'] = ['localhost']
        self.write_plist()
        self.assertEqual(self.call(checks='native')[0], 0)
        self.config['ios'] = {}
        self.write(self.native / 'capacitor.config.json', self.config)
        self.assertEqual(self.call(checks='native')[0], 1)

    def test_legacy_scene_is_review_not_fake_build_failure(self):
        self.plist.pop('UIApplicationSceneManifest')
        self.write_plist()
        code, result = self.call(checks='native')
        self.assertEqual(code, 2)
        self.assertTrue(self.has(result, 'ios.scene-manifest', 'review'))

    def test_xml_and_binary_plists(self):
        (self.native / 'Info.plist').write_bytes(plistlib.dumps(self.plist, fmt=plistlib.FMT_BINARY))
        self.assertEqual(self.call(checks='native')[0], 0)

    def test_sensitive_file_never_opened(self):
        # FIFO blocks if read: path exclusion must happen before opening it.
        os.mkfifo(self.app / 'dist/.env.production')
        code, result = self.call(checks='web')
        self.assertEqual(code, 2)
        self.assertTrue(self.has(result, 'web.inventory', 'review'))

    def test_nonregular_file_never_opened(self):
        os.mkfifo(self.app / 'dist/pipe.js')
        self.assertEqual(self.call(checks='web')[0], 2)

    def test_escaping_symlink_never_read(self):
        (self.app / 'dist/escape.js').symlink_to(self.root.parent / 'not-in-workspace')
        self.assertEqual(self.call(checks='web')[0], 2)

    def test_encoded_traversal_is_failure(self):
        self.write(self.app / 'dist/index.html', '<head><script src="%2e%2e/elsewhere.js"></script></head>')
        code, result = self.call(checks='web')
        self.assertEqual(code, 1)
        self.assertTrue(self.has(result, 'web.resource-path', 'fail'))

    def test_resource_limit_is_not_pass(self):
        with (self.app / 'dist/huge.bin').open('wb') as f: f.truncate(16 * 1024 * 1024 + 1)
        self.assertEqual(self.call(checks='web')[0], 2)

    def test_android_source_debug_overlay_not_read(self):
        root = self.app / 'android'
        native = root / 'app/src/main/assets'
        self.write(native / 'capacitor.config.json', self.config)
        shutil.copytree(self.app / 'dist', native / 'public')
        self.write(root / 'app/src/main/AndroidManifest.xml', '<manifest xmlns:android="http://schemas.android.com/apk/res/android"><application><activity android:name=".MainActivity" android:exported="true"><intent-filter/></activity></application></manifest>')
        self.write(root / 'app/src/debug/AndroidManifest.xml', '<manifest><application debugOnly="true"/></manifest>')
        self.write(root / 'gradle/wrapper/gradle-wrapper.properties', 'distributionUrl=not-executed')
        self.assertEqual(self.call('--platform', 'android')[0], 0)
        self.write(root / 'app/src/main/AndroidManifest.xml', '<manifest xmlns:android="http://schemas.android.com/apk/res/android"><application android:debuggable="true"/></manifest>')
        code, result = self.call('--platform', 'android')
        self.assertEqual(code, 1)
        self.assertTrue(self.has(result, 'android.debuggable', 'fail'))

    def test_cli_invalid_usage_and_no_bytecode_side_effect(self):
        cli = Path(__file__).with_name('validate_capacitor.py')
        p = subprocess.run([sys.executable, '-I', str(cli), '--app', str(self.app)], capture_output=True, text=True, timeout=5)
        self.assertEqual(p.returncode, 64)

    def test_project_cli_does_not_require_platform(self):
        cli = Path(__file__).with_name('validate_capacitor.py')
        p = subprocess.run([sys.executable, '-I', str(cli), '--app', str(self.app), '--workspace', str(self.root), '--checks', 'project'], capture_output=True, text=True, timeout=5)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_android_release_overlay_and_network_policy(self):
        from capacitor_checks import Audit, check_android
        root = self.app / 'android'
        manifest = root / 'app/src/main/AndroidManifest.xml'
        self.write(manifest, '<manifest xmlns:android="http://schemas.android.com/apk/res/android"><application android:networkSecurityConfig="@xml/network_security_config"/></manifest>')
        self.write(root / 'gradle/wrapper/gradle-wrapper.properties', 'not executed')
        policy = root / 'app/src/main/res/xml/network_security_config.xml'
        self.write(policy, '<network-security-config><base-config cleartextTrafficPermitted="false"/><debug-overrides><trust-anchors><certificates src="user"/></trust-anchors></debug-overrides></network-security-config>')
        audit = Audit(self.app, self.root)
        check_android(audit, root, manifest)
        self.assertTrue(all(f['status'] == 'pass' for f in audit.findings), audit.findings)
        self.write(policy, '<network-security-config><domain-config cleartextTrafficPermitted="true"><domain>example.org</domain></domain-config></network-security-config>')
        self.write(root / 'app/src/release/AndroidManifest.xml', '<manifest xmlns:android="http://schemas.android.com/apk/res/android"><application android:debuggable="true"/></manifest>')
        audit = Audit(self.app, self.root)
        check_android(audit, root, manifest)
        self.assertTrue(any(f['id'] == 'android.network-cleartext' and f['status'] == 'fail' for f in audit.findings))
        self.assertTrue(any(f['id'] == 'android.debuggable' and f['status'] == 'fail' for f in audit.findings))

    def test_isolated_cli_does_not_import_app_python(self):
        self.write(self.app / 'sitecustomize.py', 'raise RuntimeError("PRIVATE_SENTINEL")')
        self.write(self.app / 'capacitor_checks.py', 'raise RuntimeError("PRIVATE_SENTINEL")')
        cli = Path(__file__).with_name('validate_capacitor.py')
        env = dict(os.environ, PYTHONPATH=str(self.app))
        p = subprocess.run([sys.executable, '-I', str(cli), '--app', str(self.app), '--workspace', str(self.root), '--checks', 'project'], cwd=self.app, env=env, capture_output=True, text=True, timeout=5)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertNotIn('PRIVATE_SENTINEL', p.stdout + p.stderr)

    def test_unresolved_native_bundle_id_is_review(self):
        self.plist['CFBundleIdentifier'] = '$(PRODUCT_BUNDLE_IDENTIFIER)'
        self.write_plist()
        code, result = self.call(checks='native')
        self.assertEqual(code, 2)
        self.assertTrue(self.has(result, 'ios.bundle-id', 'review'))


if __name__ == '__main__':
    unittest.main()
