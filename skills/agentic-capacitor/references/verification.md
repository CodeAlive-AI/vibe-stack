# Verification, diagnosis, CI and release

## Evidence ladder

After a web-to-native conversion, use the bundled [validation scripts](validation-scripts.md) for offline, read-only checks of resolved packages, built web files, copied native config/assets and selected plist/manifest invariants. A `review` result is incomplete evidence, not success. These checks precede and do not replace the evidence ladder below.

| Layer | What to prove |
| --- | --- |
| Existing web checks | Types, lint, focused unit/integration tests, framework build, route behavior |
| Web artifact | Correct entry/assets, client/server boundary, no development endpoints or secrets |
| Native build | Selected package manager, toolchain, plugin linking, source membership, release config |
| Simulator/emulator | Launch, navigation, links, lifecycle, keyboard/insets, network error UI |
| Real device/release build | Auth return, permissions, hardware, push, signing/entitlements, performance |

Keep the project's existing test stack. Web Playwright/jsdom and plugin mocks do not validate native bridge behavior. Select native automation only if it supports this app's WebView and native screens; Detox is not an automatic fit for every Capacitor application. Browser/app automation must follow the user's tool permissions. Record manual checks still required instead of claiming they ran.

For conversion/migration cover cold/warm link handling, startup offline, login/logout/expiry, resume, router restoration, unavailable permissions, plugin failure, keyboard overlap, and actual streaming/files where used. Check cancellation/listener cleanup and duplicate effects in React development mode. Use focused regression tests for consequential logic; do not add tests that only repeat configuration text.

For startup, memory or responsiveness regressions use the [performance workflow](performance.md). Keep release optimization and device measurements separate from web unit tests and static validation.

## Prove distribution-sensitive paths early

Prepare an early release-like prototype that exercises auth return, required deep/universal links, keyboard/insets, cold launch and push when the product uses it. Test foreground, background and terminated launch states on the relevant device. Do not add unused features just to complete a checklist, or assume one successful simulator login validates them all.

Inspect signed-archive packaging, embedded frameworks, bundle identifiers, entitlements and privacy resources as part of native verification. A compile can succeed while a store rejects the bundle. With existing authorization, use TestFlight or Play Internal to validate the distribution path early; otherwise finish the local artifact and report that upload/device checks remain. Use the store-readiness reference for product-policy decisions.

During normal 8.5 work, verify that a clean dependency install plus sync preserves the intended native graph/resources, and that config loads under the project's actual Node/TypeScript combination. Exercise scene return/presentation and independent bar/inset behavior where touched. These are regression checks for the current app, not a reason to run a speculative 9 migration on every change.

## Diagnose before cleaning

Capture the first actionable, redacted error and identify web-build, copy, config, dependency resolution, compiler, signing, or runtime failure. Check resolved versions, paths, target membership, package manager and plugin setup before editing.

- Blank screen: confirm artifact and asset URLs, inspect JS startup errors and CSP, then native bridge/config; do not disable security or switch to remote production hosting.
- iOS resolution: use the existing SPM/CocoaPods path and lock state. Do not delete Pods/lockfiles/global SPM caches or blindly downgrade Xcode `objectVersion`.
- Architecture errors: verify SDK binary slices and active destination; do not globally exclude arm64 or invoke Rosetta as a universal Apple Silicon fix.
- Android build: check the coherent Java/Gradle/AGP set and the specific failing plugin; avoid global cache deletion and broad R8 suppression.
- Plugin unavailable: inspect installed package, native implementation/linking, sync output, selected binary and permissions. Do not hide a native failure with the web mock.

Use bounded project-local cleanup only when evidence implicates generated output. Preserve native customizations and user changes; if an invasive repair is needed, explain scope and recovery before proceeding under applicable authorization.

## CI and release preparation

Use existing CI conventions. Pin compatible runner/toolchain and action revisions as appropriate; choose actual project/workspace and scheme. Restore native caches keyed to dependency/toolchain state, build web assets before sync, then archive the intended configuration. Avoid nested working-directory mistakes and assumptions that every iOS project has a CocoaPods workspace. No new cloud build service is required.

Keep signing credentials in the user's approved secret mechanism and out of config/examples/logs. Prepare unsigned or local test builds when signing access is unavailable; explain exactly which release checks remain. Inspect the generated production config and packaged assets after sync, not only source config.

Before submission consult current [Apple review rules](https://developer.apple.com/app-store/review/guidelines/) and [Google Play policy](https://play.google.com/about/developer-content-policy/). Verify app identity, version/build number, privacy metadata, screenshots, account access and deletion/payment flows as applicable. Packaging a website is not assurance of acceptance. Preparing these artifacts does not authorize submission.

For Apple releases, hand the exact candidate and this evidence to [apple-app-store-reviewer](https://github.com/CodeAlive-AI/vibe-stack/blob/main/skills/apple-app-store-reviewer/SKILL.md) when available, following the [store-readiness handoff](store-readiness.md). Preserve each tool's version scope, exit status and limitations: a passing Capacitor file check is supporting evidence, not the reviewer's final gate. After implementation fixes, rebuild and re-review affected artifacts and runtime paths rather than carrying forward a stale verdict.

## Optional OTA updates

Do not add an OTA vendor or run an upload merely because the app uses Capacitor. When requested, compare the existing strategy, native/plugin compatibility, integrity/signature checks, rollback, staged channels, telemetry/privacy and cost. A web update cannot supply missing native code or change native entitlements. Test failed/interrupted downloads and rollback against the intended binary version. Verify applicable store rules; do not describe OTA as a way around review. Obtain authorization for the exact external rollout unless already supplied.

Separate checking, downloading, scheduling, activation and readiness confirmation. Persist safe resumable state before activation; never reload through an active payment, auth return, recording, unsaved edit or upload/stream without the product's explicit interruption policy. Backgrounding can be part of those flows and is not automatically a safe activation point. Validate the update's native compatibility and data-schema compatibility, including whether rolling back JS can still read data written by the new bundle.

If Capgo is selected, review its installed types rather than copying generic live-update snippets. In the reviewed `@capgo/capacitor-updater@8.51.15` definitions, `set({ id })` reloads immediately; `next({ id })` schedules a downloaded bundle without immediately destroying the JS context, with subsequent activation governed by lifecycle/delay settings. `updateAvailable` supplies `{ bundle }`, not top-level `url`/`version` to pass to another download. Avoid duplicate downloads or competing automatic/manual activation owners. Source: [versioned package](https://registry.npmjs.org/@capgo/capacitor-updater/-/capacitor-updater-8.51.15.tgz), [Updater API](https://capgo.app/docs/plugins/updater/api/).

Confirm readiness on each launch only after a bounded local startup-health check, within the installed updater's configured timeout. Do not acknowledge a broken bundle at module import, or wait indefinitely for a remote service and cause unnecessary rollback. Await/handle non-terminal plugin calls and own listener cleanup across React effects. Test a healthy offline launch, a deliberately broken bundle, interrupted download, unsafe activation timing and recovery to a compatible known-good/built-in bundle. Package/type inspection alone does not certify OTA behavior on a device. Source: [Readiness and rollback](https://capgo.app/docs/plugins/updater/notify-app-ready/).
