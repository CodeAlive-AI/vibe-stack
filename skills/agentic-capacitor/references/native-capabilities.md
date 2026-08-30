# Native capabilities, storage, and files

## Choose and verify plugins

Use browser functionality where it actually meets requirements. For native features check core and official plugins before adding dependencies; compare third-party options without assuming a vendor is mandatory. Record exact version, peer range, iOS/SPM/CocoaPods support, Android SDK/JDK requirements, Cordova dependency, maintenance, license, cost and privacy obligations. A compatible major is not proof every platform works.

Inspect package metadata and relevant native code before installation. Sync the selected target, build it, and exercise the feature. `isPluginAvailable()` does not verify permissions or native SDK setup. For custom plugin work, inspect the official versioned Swift/Java/TypeScript plugin guides and validate argument types and trusted operations; do not expose arbitrary filesystem/network/native commands to the bridge. Source: [Plugin development](https://capacitorjs.com/docs/plugins/creating-plugins).

## Keep the native boundary small

Group native integrations behind focused, typed capabilities such as auth, notifications, sharing or files. Reuse existing service boundaries; avoid scattering platform checks throughout UI components or inventing a universal platform framework for one plugin call. Preserve explicit unsupported/error outcomes and the real streaming/permission contract. An adapter localizes changes; it does not hide native failures or prove 9 compatibility.

For new custom iOS code prefer the standard Swift plugin pattern. Follow the existing supported Java/Kotlin conventions on Android; Kotlin is an option, not a requirement to rewrite Java. Check bridge registration, lifecycle, SPM/package metadata, resources and transitive SDKs against the exact target version. Do not assume writing Swift alone solves future binary-packaging changes.

For custom native work, associate bridge/controller references, pending callbacks and listeners with the owning instance. Avoid storing a global first window, bridge or presentation controller and reusing it across unrelated sessions. Use the bridge's presentation context and supported scene callbacks, clean up subscriptions, and distinguish app-level services from per-scene state. This improves 8.5 correctness and prepares for future multi-instance support; do not invent or promise 9 window APIs. Preserve existing public integrations while removing unnecessary reliance on private Capacitor/Cordova internals.

Install only capabilities the product needs. A suggested “minimal stack” is not an instruction to add Browser, Haptics, Share, Push, secure storage and every other plugin up front. SystemBars already comes from core for ordinary modern bar handling; do not add a competing StatusBar owner by default.

## Permissions and lifecycle

Declare only required permissions/capabilities and meaningful usage strings. Request access at the feature's point of use; handle granted, denied, restricted/limited and settings-return paths according to the actual plugin/OS. Never auto-grant, silently fake success, or repeatedly prompt. For push distinguish permission, device token registration, backend token ownership, token refresh, and foreground/background delivery; logout must disassociate tokens as required. Test hardware-specific behavior on devices.

## Storage classification

Before choosing persistent storage, decide which state must survive process death and which is bound to the current account. For plugins opening Android Activities, register `App`'s `appRestoredResult` handler early: Camera results can arrive after the original JS process and promise are gone. Validate plugin/method/result, restore only the relevant pending operation and prevent duplicate uploads or applying a previous account's result. This is distinct from `appUrlOpen` and ordinary resume. Source: [App restored results](https://capacitorjs.com/docs/apis/app).

Persist the minimal pending operation/context yourself; restored plugin results do not restore arbitrary React/router state. Handle unsuccessful results, errors and cancellation explicitly before resuming an upload or workflow.

| Data | Suitable boundary |
| --- | --- |
| Small non-sensitive preferences | Preferences, using namespaced keys |
| Cache/structured offline data | Chosen IndexedDB/SQLite/filesystem solution with migration, eviction and user isolation |
| Session credentials | Existing secure session design; vetted native Keychain/Keystore-backed storage only if the auth protocol needs client-held credentials |
| Backend secrets/private signing keys | Never ship in client assets or runtime config |

Preferences is not encrypted secure storage. Do not recommend it for bearer/refresh tokens or as a universal cookie replacement. Native secure storage guarantees depend on device and configuration; “hardware-backed” is not universal. Keychain/backup/reinstall behavior needs explicit retention and logout tests. Remove owned data, not all unrelated preferences; server-side revocation remains necessary. Validate persisted values with schema/version checks, handle malformed data explicitly, and prevent asynchronous hydration from updating an unmounted or different-user view. Source: [Preferences](https://capacitorjs.com/docs/apis/preferences).

## Files and transfers

For new native downloads use the compatible `@capacitor/file-transfer` API; `Filesystem.downloadFile` is deprecated. Resolve a sandbox destination URI with Filesystem and pass it to FileTransfer. Check the installed version for supported options rather than assuming all HttpOptions apply. Source: [Filesystem](https://capacitorjs.com/docs/apis/filesystem), [FileTransfer](https://capacitorjs.com/docs/apis/file-transfer).

Prefer streaming/native transfer for large files; neither Blob nor native APIs guarantee zero JS memory use. Avoid base64 round-trips for large payloads. Bound size, validate MIME/content, generate safe filenames, reject traversal and untrusted destination URLs, restrict credential forwarding on redirects, and clean owned temporary files. Keep cache separate from durable/private files. Handle Android content URIs with the plugin's documented URI support; `convertFileSrc` is not a universal file-access grant. Use scoped storage/pickers rather than broad external-storage permissions. Share only the intended files and avoid logging file contents or signed URLs.

## Capture, media selection and document access

Distinguish WebView file-input capture from the native Camera plugin, capture from saving to Photos, and user-selected media from broad library access. Camera plugin 8.1+ introduced `takePhoto` and `chooseFromGallery`; verify the installed plugin's types before choosing these rather than assuming the core 8.5 version determines the Camera API. Test cancellation, large/multiple media, URI lifetime and process-death restoration. Prefer URI-backed display/transfer over whole-file base64. Source: [Camera](https://capacitorjs.com/docs/apis/camera).

The system Photos picker can provide selected items without full-library permission. Direct PhotoKit use has its own permission/limited-access contract; do not request broad access for a simple upload. For external iOS documents, use the chosen plugin's security-scoped/coordinated access contract and release access correctly; a raw URL stored in Preferences is not a durable access grant. Source: [Photos picker](https://developer.apple.com/documentation/photokit/selecting-photos-and-videos-in-ios), [Document picker](https://developer.apple.com/documentation/uikit/uidocumentpickerviewcontroller).

## Notifications and scheduled work

The official Push Notifications token is APNs on iOS and FCM on Android; do not feed an APNs token into an FCM-token backend path. Keep platform/provider/environment and account ownership explicit. Test permission denial, token replacement, notification taps after cold launch, foreground presentation and Android channel settings. Never put privileged provider credentials in the app.

On iOS verify the Push capability/APS entitlement and AppDelegate forwarding; register on launch and update backend token associations from registration events, rather than assuming a cached token is permanently valid.

The official plugin does not handle iOS silent push. On Android, data-only messages do not invoke its JS receive listener after the app is killed; a suitable native service/integration is needed. Push delivery is not a durable task queue. Source: [Push Notifications](https://capacitorjs.com/docs/apis/push-notifications).

Local notification permission and exact-alarm access are different. Choose inexact scheduling unless precise delivery is an actual feature requirement; review the permission/policy route before requesting exact alarms. Recheck revoked settings on return, reconcile schedules, and communicate degraded delivery instead of silently promising precision. Test timezone/DST, reboot, cancellation and duplicate IDs. Android private-space locking can prevent visible notifications; do not promise delivery while the app is locked/stopped. Source: [Local Notifications](https://capacitorjs.com/docs/apis/local-notifications).

Android 13+ has runtime `POST_NOTIFICATIONS`. On Android 14+, most fresh installs targeting 33+ do not receive `SCHEDULE_EXACT_ALARM` by default; `USE_EXACT_ALARM` is restricted to qualifying use cases such as calendar/alarm-clock apps. Check the actual grant instead of only manifest presence. Sources: [Notification permission](https://developer.android.com/develop/ui/views/notifications/notification-permission), [Exact alarm changes](https://developer.android.com/about/versions/14/changes/schedule-exact-alarms).

## Background execution

Background Runner is an optional headless JS environment, not the React/WebView/Node runtime: no DOM, shared React state or arbitrary access to installed browser plugins. Its scheduling and execution budgets are OS-controlled. Use bounded work, completion/error handling, durable checkpoints and idempotency; do not promise exact intervals, uninterrupted sockets or indefinite background AI streams. Select platform-native background transfer/task APIs when those are the real requirement, and enable only justified background modes/services. Source: [Background Runner](https://capacitorjs.com/docs/apis/background-runner).

For that plugin, verify iOS Background Modes, matching `BGTaskSchedulerPermittedIdentifiers`, AppDelegate registration and the bundled headless entry. Its documented iOS budget is about 30 seconds and requires device testing; Android repeating work has a minimum 15-minute interval, with scheduling still subject to OS heuristics. Treat limits as version-specific ceilings, not delivery guarantees. Never add unrestricted battery exemptions or a foreground service merely to keep a WebView alive.
