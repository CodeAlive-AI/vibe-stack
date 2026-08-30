# Deterministic validation after web-to-Capacitor conversion

Use `scripts/validate_capacitor.py` after the existing web build and Capacitor copy/sync have completed. It checks selected **production file invariants**, offline, without changing the app. Python 3.10+ and its standard library are sufficient; no npm/pip install is needed. Invoke the trusted script by its absolute path with `python3 -I`, which excludes app-local Python imports, PYTHONPATH and user site packages. The script imports only its bundled helper and the standard library.

Do not run build/install/sync automatically to satisfy a missing-file result. First inspect the repository's scripts/config and follow the normal execution policy. The validator never runs JavaScript, TypeScript, Swift, Gradle, shell hooks, package managers, native tools or network requests. It does not evaluate `capacitor.config.ts`, `capacitor.config.js`, next.config, Package.swift or Gradle expressions.

## Invocation

In these examples replace `/path/to/agentic-capacitor` with the actual skill directory, `/repo/apps/mobile` with the app package, and `/repo` with the explicit monorepo read boundary. For a standalone app omit `--workspace`; its default is `--app`. Relative file arguments resolve against the app, never the shell's current directory.

Project dependencies only, before native setup (platform optional; add it to validate that native dependency):

```sh
python3 -I /path/to/agentic-capacitor/scripts/validate_capacitor.py --app /repo/apps/mobile --workspace /repo --checks project
```

Web build only; use the actual mobile artifact (`dist`, `out`, or another directory), not Next's server output:

```sh
python3 -I /path/to/agentic-capacitor/scripts/validate_capacitor.py --app /repo/apps/mobile --workspace /repo --checks web --web-dir out
```

After iOS copy/sync, all groups, with optional intended identity:

```sh
python3 -I /path/to/agentic-capacitor/scripts/validate_capacitor.py --app /repo/apps/mobile --workspace /repo --checks all --platform ios --web-dir out --expected-app-id com.example.mobile
```

When Android is actually in scope, repeat `--platform android` to inspect both. `--checks native` runs the copied-config/assets and native-file checks without the dependency or HTML checks. `--checks all` is the default. Both native/all require a platform and webDir; web requires only webDir. Add `--format text` for human output; JSON is the default and is suitable for CI output capture. Do not pipe away the exit status or use `|| true` in a validation gate.

Custom platform directories use `--ios-root native/ios` / `--android-root native/android`. Within them the standard layouts are:

- iOS: `App/App/capacitor.config.json`, `App/App/public`, `App/App/Info.plist`; package-manager/project evidence under `App/`.
- Android: `app/src/main/assets/capacitor.config.json`, `app/src/main/assets/public`, `app/src/main/AndroidManifest.xml`.

For a resolved/built plist or merged release manifest, pass `--ios-plist build/Release/App.app/Info.plist` or `--android-manifest build/release/AndroidManifest.xml` with the actual existing path. Those arguments replace only the metadata input: copied assets/config are still inspected in the selected native project. This is **not** an archive/binary validator. Copy only the needed non-secret build metadata into the workspace if the original resides outside the explicit boundary; do not broaden the boundary to the home directory. Custom Xcode names, Android modules/flavors and nonstandard asset layouts require an adapted checker or explicit manual evidence, not guessed success.

## What each group establishes

| Group | Deterministic checks |
| --- | --- |
| project | App declares core/CLI and selected platform dependencies; installed manifests resolve through app/workspace node_modules to stable 8.5.x at the same patch; exact declarations match installed versions; lockfile presence/ownership and declared package manager agree; hooks and competing config files are flagged. |
| web | A bounded artifact inventory and SHA-256 hashes; index.html with a head element; static HTML script/style/preload targets exist; decoded path traversal and obvious uncompiled TS/JSX startup references fail; base URLs and external startup resources require review. |
| native config | Copied JSON has appId and, when present, matching webDir; expected appId/platform identities agree; dev server URLs, cleartext, mixed content, forced web debugging and wildcard navigation are excluded; exact remote navigation and production logging need review; known credential keys are flagged without values. |
| native assets | Every source artifact file exists in the copied public directory with the same hash; extra files need review except known Capacitor/Cordova-generated names and the plugins directory. |
| iOS | XML/binary plist parsing, UIScene declaration, literal bundle identity, broad ATS exceptions, app-bound-domain/config consistency and standard SPM/CocoaPods/project evidence. An unresolved bundle-id build variable requires a built plist. |
| Android | Supplied manifest debug/cleartext flags and exported-field uncertainty; default main invocation also checks an existing release overlay, not debug overlays; referenced standard main/release network-security XML is inspected for cleartext and user CA trust outside debug overrides; wrapper metadata presence. |

Alignment of core/CLI/platform patches is an intentional profile invariant; independently versioned official/community plugins are not forced to match. Installed node_modules manifests are evidence of what is present, **not proof of lockfile integrity, peer compatibility, absence of tampering or a successful frozen install**. Missing installations produce review without fetching anything. A source config located by name has not been semantically validated; production settings are checked in the copied JSON instead. CLI 8.5 strips buildOptions when copying config, so this check does not certify that source config has no signing secrets.

## Results and limits

JSON schema version is `1`, with stable rule IDs, sorted findings, relative paths and no timestamps. Same inputs produce the same output. Each finding is `pass`, `fail` or `review`; overall fail takes precedence over review. Counts refer to individual findings, not a coverage score.

| Exit | Meaning |
| --- | --- |
| 0 | All selected static checks passed; not a production-readiness certificate. |
| 1 | At least one concrete invariant failed, even if other checks also need review. |
| 2 | No confirmed failure, but missing/ambiguous evidence, a boundary or a resource limit requires review. |
| 64 | Invalid command arguments. |
| 70 | Unexpected validator error; never treat as success. |

This is a conservative production profile. A development cleartext configuration can legitimately fail it. A main-manifest restriction can be overridden by a release variant; evaluate the actual merged output before deciding how to fix it. Standard source plists commonly yield review for unresolved bundle IDs. An intentional copy-time transformation, such as inline source maps, yields a content difference: verify the transform instead of blindly re-copying or weakening the check. Missing selected native output after migration is a failure; unselected platforms are not required.

Inputs are bounded to 16 MiB per file, 20,000 artifact entries and 512 MiB total per artifact. Sensitive paths (including .env files and signing-key extensions), nonregular files, out-of-workspace symlinks and symlinked artifact directories are not read. In-workspace pnpm package symlinks are supported. Limits/exclusions produce review, never silently skipped success. Reports suppress config values, script bodies and resource URLs; paths may still contain project names. Review paths before sharing reports. This is not an OS sandbox against a process concurrently rewriting the filesystem: run against a quiescent trusted snapshot.

The validator does **not** scan all shipped JS for secrets, remote API/dev URLs or source-map disclosure; grep heuristics there would confuse valid origins, framework code and example strings with actual runtime behavior. It also does not verify dynamic chunks, CSS url()/imports, route coverage, Next server/client separation, auth/cookies, CSP, plugin registration/compatibility, effective SDK/toolchain values, source membership, callback forwarding, privacy manifests, signing, store policy, device behavior or final archived assets. Continue with the verification reference and focused runtime/native tests; do not infer these properties from exit 0.

## Maintain the checks

Run the bundled regression fixtures after changing the scripts:

```sh
python3 -I /path/to/agentic-capacitor/scripts/test_validate_capacitor.py
```

Fixtures use an isolated temporary directory and include failures, incomplete evidence, no-execution/no-mutation checks, symlink/pipe boundaries, hoisted pnpm packages, copied-asset drift, redaction and Android release network policy. They do not install packages, build an app or access a real project. Keep tests for consequential behavior, not counts/wording. Revisit profile rules against versioned Capacitor sources before supporting a new major.

Rule sources: [Capacitor configuration](https://capacitorjs.com/docs/config), [8.5 migration](https://capacitorjs.com/docs/updating/8-5), [8.5 copy implementation](https://github.com/ionic-team/capacitor/blob/8.5.0/cli/src/tasks/copy.ts), [8.5 iOS plist template](https://github.com/ionic-team/capacitor/blob/8.5.0/ios-spm-template/App/App/Info.plist), [Android network security configuration](https://developer.android.com/privacy-and-security/security-config).
