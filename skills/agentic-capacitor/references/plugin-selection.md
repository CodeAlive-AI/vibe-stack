# Practical plugin shortlist for Capacitor 8.5

Use this shortlist during web-to-native planning, before adding a native feature, and during dependency reviews. It covers common application needs (the “80%+” heuristic), not a measured adoption statistic or a universal installation bundle. Map requirements to capabilities and install only the selected subset. Preserve working browser APIs and existing integrations when they meet the native requirement.

## Verification scope

Checked **2026-08-31** against npm metadata and published `Package.swift`, podspec and Android Gradle declarations. Version links below identify exact registry records. The 25 listed plugins had no npm deprecation marker. All ship SPM manifests declaring Capacitor Swift PM from 8.0.0 and iOS 15; Android source defaults are minSdk 24 / compileSdk and targetSdk 36, except InAppBrowser's minSdk 26. Transitive SDKs, overrides and individual features can impose higher requirements.

All declare `@capacitor/core >=8.0.0`, except Updater (`^8.0.0`) and Aparajita Secure Storage (no peer declaration; its documentation and native manifests target Capacitor 8). These are **metadata/native-declaration candidates for core 8.5.0**, not a device-tested combination or security certification. No plugin was installed or built for this review. Recheck releases, advisories, source and resolved native graph before adoption; do not downgrade an existing patched dependency to match this dated table.

Plugin versions are independent: File Transfer 2.x and InAppBrowser 4.x are valid candidates. A broad `>=8` peer does not certify Capacitor 9; the native SPM range from 8.0.0 still stays within 8.x. See [version rules](versions.md) and [9 readiness](capacitor-9.md).

## Common capability set

These npm packages declare **MIT**. SystemBars is bundled with core, not an additional install.

| API | Package / checked version | Select when / limit |
| --- | --- | --- |
| [App](https://capacitorjs.com/docs/apis/app) | `@capacitor/app` [8.1.1](https://registry.npmjs.org/@capacitor/app/8.1.1) | Native lifecycle, cold/warm links, Android back and restored results; coordinate router readiness and owned listeners |
| [SystemBars](https://capacitorjs.com/docs/apis/system-bars) | In `@capacitor/core` [8.5.0](https://registry.npmjs.org/@capacitor/core/8.5.0) | One bars/insets owner; no extra StatusBar/safe-area plugin by default |
| [Keyboard](https://capacitorjs.com/docs/apis/keyboard) | `@capacitor/keyboard` [8.0.5](https://registry.npmjs.org/@capacitor/keyboard/8.0.5) | Forms/chat need native events or resize control; verify platform options and avoid double compensation |
| [SplashScreen](https://capacitorjs.com/docs/apis/splash-screen) | `@capacitor/splash-screen` [8.0.2](https://registry.npmjs.org/@capacitor/splash-screen/8.0.2) | App-controlled launch handoff; retain auto-hide unless a bounded manual lifecycle is needed |
| [Network](https://capacitorjs.com/docs/apis/network) | `@capacitor/network` [8.0.1](https://registry.npmjs.org/@capacitor/network/8.0.1) | Connectivity hints/reconnect UX; connected does not prove backend reachability or authorize retrying non-idempotent work |
| [Preferences](https://capacitorjs.com/docs/apis/preferences) | `@capacitor/preferences` [8.0.1](https://registry.npmjs.org/@capacitor/preferences/8.0.1) | Small non-sensitive settings; no tokens, bulk DB or cookie replacement; review required-reason APIs |
| [Browser](https://capacitorjs.com/docs/apis/browser) | `@capacitor/browser` [8.0.4](https://registry.npmjs.org/@capacitor/browser/8.0.4) | External pages in system browser UI; not a complete OAuth/session integration |
| [Share](https://capacitorjs.com/docs/apis/share) | `@capacitor/share` [8.0.1](https://registry.npmjs.org/@capacitor/share/8.0.1) | Send approved text/URLs/files; scope Android file paths; receiving shares is separate |
| [Haptics](https://capacitorjs.com/docs/apis/haptics) | `@capacitor/haptics` [8.0.2](https://registry.npmjs.org/@capacitor/haptics/8.0.2) | Tactile feedback for meaningful actions; never the only success/error signal |

For a typical authenticated app, assess App and core SystemBars first, then Keyboard/SplashScreen for its UI. Add Network, Preferences, Browser, Share and Haptics where flows use them. This is a decision sequence, not an install command.

## Common conditional features

These official packages also declare **MIT**. Diagnostics, clipboard and notifications do not justify collecting extra data or prompting at launch.

| API | Package / checked version | Boundary to verify |
| --- | --- | --- |
| [Camera](https://capacitorjs.com/docs/apis/camera) | `@capacitor/camera` [8.2.3](https://registry.npmjs.org/@capacitor/camera/8.2.3) | Capture/selected media; installed takePhoto/chooseFromGallery types, limited access and process restoration |
| [Filesystem](https://capacitorjs.com/docs/apis/filesystem) | `@capacitor/filesystem` [8.1.3](https://registry.npmjs.org/@capacitor/filesystem/8.1.3) | Sandbox/cache files, privacy reasons, URI lifetime and cleanup; not a document picker |
| [File Transfer](https://capacitorjs.com/docs/apis/file-transfer) | `@capacitor/file-transfer` [2.0.5](https://registry.npmjs.org/@capacitor/file-transfer/2.0.5) | Native upload/download before another SDK; no deprecated Filesystem.downloadFile or assumed durable background/resume support |
| [Push Notifications](https://capacitorjs.com/docs/apis/push-notifications) | `@capacitor/push-notifications` [8.1.2](https://registry.npmjs.org/@capacitor/push-notifications/8.1.2) | A push use case/backend; APNs versus FCM, grants, account ownership and delivery limits |
| [Local Notifications](https://capacitorjs.com/docs/apis/local-notifications) | `@capacitor/local-notifications` [8.3.1](https://registry.npmjs.org/@capacitor/local-notifications/8.3.1) | On-device reminders; notification permission and exact-alarm eligibility differ |
| [Device](https://capacitorjs.com/docs/apis/device) | `@capacitor/device` [8.0.3](https://registry.npmjs.org/@capacitor/device/8.0.3) | Support diagnostics/capability information; not an authentication identity or fingerprinting license |
| [Clipboard](https://capacitorjs.com/docs/apis/clipboard) | `@capacitor/clipboard` [8.0.1](https://registry.npmjs.org/@capacitor/clipboard/8.0.1) | Explicit copy/paste when browser behavior is insufficient; no silent reading or secret persistence |
| [InAppBrowser](https://capacitorjs.com/docs/apis/inappbrowser) | `@capacitor/inappbrowser` [4.0.3](https://registry.npmjs.org/@capacitor/inappbrowser/4.0.3) | Choose instead of Browser for required extra modes. Android minSdk 26; embedded WebView storage isolation is limited below API 28. Do not weaken isolation for login convenience |

Browser, InAppBrowser and social login are different tools, not three mandatory dependencies. Preserve the backend session design; do not embed OAuth in a WebView when the provider requires a system authentication session. See [authentication](auth-network.md).

## Third-party candidates by requirement

The checked Capgo packages declare **MPL-2.0**, not the MIT license of Capgo's skill repository. Check distribution obligations, native SDK licenses, service cost and privacy. A source license does not include hosted service usage. The MIT alternatives below are independently maintained, not official Capacitor plugins.

| Need / documentation | Package / checked version | License / selection gate |
| --- | --- | --- |
| [Native social login](https://capgo.app/docs/plugins/social-login/) | `@capgo/capacitor-social-login` [8.5.0](https://registry.npmjs.org/@capgo/capacitor-social-login/8.5.0) | MPL-2.0; required providers only; redirects, nonce/state where applicable and server token verification; no backend auth replacement |
| [Biometric access](https://capgo.app/docs/plugins/native-biometric/) | `@capgo/capacitor-native-biometric` [8.6.7](https://registry.npmjs.org/@capgo/capacitor-native-biometric/8.6.7) | MPL-2.0; optional local protection, not server identity; encrypted storage, verifyIdentity and authentication-bound retrieval differ |
| [Secure storage](https://github.com/aparajita/capacitor-secure-storage) | `@aparajita/capacitor-secure-storage` [8.0.0](https://registry.npmjs.org/@aparajita/capacitor-secure-storage/8.0.0) | MIT; only if the protocol needs client-held secrets; no peer declaration. **Web uses unencrypted localStorage for debugging: prohibit production web secret use.** Review iCloud sync/retention/logout; avoid duplicate credential stores |
| [Document picker](https://capawesome.io/docs/plugins/file-picker/) | `@capawesome/capacitor-file-picker` [8.0.4](https://registry.npmjs.org/@capawesome/capacitor-file-picker/8.0.4) | MIT/public npm; when file input/Camera is insufficient; check content/security-scoped URIs, size limits, permissions and JS memory |
| [Receive shares](https://capgo.app/docs/plugins/share-target/) | `@capgo/capacitor-share-target` [8.0.49](https://registry.npmjs.org/@capgo/capacitor-share-target/8.0.49) | MPL-2.0; content/chat/document use cases; iOS extension/App Group, Android intents, cold launch and hostile input need review |
| [Record audio](https://capgo.app/docs/plugins/audio-recorder/) | `@capgo/capacitor-audio-recorder` [8.2.7](https://registry.npmjs.org/@capgo/capacitor-audio-recorder/8.2.7) | MPL-2.0; voice/memo feature; compare existing MediaRecorder first; grants, interruptions, routes, files and recording indicator |
| [Native purchases](https://capgo.app/docs/plugins/native-purchases/) | `@capgo/native-purchases` [8.7.0](https://registry.npmjs.org/@capgo/native-purchases/8.7.0) | MPL-2.0; billing when applicable; server entitlements, transaction validation, pending/restore/refund handling and sandbox tests remain necessary; SPM conditionally detects StoreKit SDK features |
| [Uploader](https://capgo.app/docs/plugins/uploader/) | `@capgo/capacitor-uploader` [8.3.11](https://registry.npmjs.org/@capgo/capacitor-uploader/8.3.11) | MPL-2.0; only for unmet File Transfer requirements; verify background/retry/resume semantics and server idempotency per OS |
| [OTA updater](https://capgo.app/docs/plugins/updater/) | `@capgo/capacitor-updater` [8.51.15](https://registry.npmjs.org/@capgo/capacitor-updater/8.51.15) | MPL-2.0; optional after a stable binary; signatures, native/schema compatibility, safe activation, rollback and store-policy review |

Apply [native capability](native-capabilities.md), [security](security.md), [OTA](verification.md) and [store-readiness](store-readiness.md) rules. Listing a package does not authorize installing services, uploading credentials/builds or releasing bundles.

## Full catalogs and when to consult them

No single list continuously certifies the whole ecosystem. Follow the exact package source/release from the relevant catalog; promotional install snippets are not setup policy.

| Catalog | Consult when |
| --- | --- |
| [Official Capacitor plugins/APIs](https://capacitorjs.com/docs/plugins) | Initial inventory and before third-party additions; core/official APIs may already cover the need |
| [Community directory](https://capacitorjs.com/docs/plugins/community) / [organization](https://github.com/capacitor-community) | Official functionality is missing; inspect maintenance per project |
| [Capgo full plugin catalog](https://capgo.app/plugins/) | Need auth, share-target, media, billing, native UX or other SDK bridges beyond this shortlist; filter by capability |
| [Capawesome catalog](https://capawesome.io/docs/plugins/) | Compare file/media/Firebase/device integrations or support; distinguish public packages from Insider/private-registry products, terms and license keys |

Revisit when requirements change, a package is deprecated/unmaintained, SDK/OS requirements change, security findings appear, or a Capacitor 9 trial begins. Do not survey/install everything during an unrelated UI fix. Unlisted does not mean unsupported; popular does not mean audited; public npm 404 does not prove a private product is nonexistent.

## Adoption gate

1. Name the user-facing need, existing implementation and missing native behavior. Select one owner per capability; justify overlaps.
2. Recheck exact version, releases/advisories, maintainer, license, peers, native dependencies and SPM. Inspect executable package/native build manifests before running them.
3. Confirm OS minimums, permissions/entitlements, privacy, service cost and backend changes. Record unsupported platforms and deliberate alternatives or visible errors; never fall back from secure storage to plaintext.
4. Pin the reviewed selection through the existing package manager/lockfile; sync chosen targets only. No bulk `@latest`, peer bypass or forced Cordova/SPM graph edits.
5. Typecheck/build the actual 8.5 app, then test success, cancellation, denial, cold launch, resume and relevant hardware paths. Track iOS/Android/web evidence separately and repeat for 9.
