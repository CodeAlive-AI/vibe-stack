# iOS: UIScene and native dependencies

## New projects versus existing projects

The 8.5 templates already use UIScene. Do not migrate a freshly generated project again. Updating dependencies alone retains the legacy AppDelegate path; Xcode 27 requires scene adoption. On Xcode 26, adopting scenes is preparation to plan and test, not a claim that every unchanged app stops working. Existing native files may contain app-specific controllers, lifecycle logic, entitlements, and SDK callbacks; inspect before changing them.

For an 8.4-to-8.5 migration, audit SceneDelegate, the scene manifest, AppDelegate scene configuration, and target membership. A template-shaped app can use the resolved 8.5 CLI migrator. Custom or partially migrated projects need a merged manual change; never overwrite native files with a template.

The scene delegate owns the window and chosen bridge controller. Forward cold connection, URL-open, and universal-link callbacks through `SceneDelegateProxy`. Move app-specific URL and foreground/background delegate logic into scene callbacks or suitable notifications. Push-registration callbacks remain app-level. Preserve custom controller construction and initialization order. Remove usages of the deleted temporary-window APIs.

Test launch, warm/cold links, `App.getLaunchUrl()`, pause/resume, and custom plugins. Sources: [8.5 migration](https://capacitorjs.com/docs/updating/8-5), [tagged SceneDelegate template](https://github.com/ionic-team/capacitor/blob/8.5.0/ios-spm-template/App/App/SceneDelegate.swift).

Treat maintained `ios/` project sources, capabilities and custom code as version-controlled application source; generated caches/build outputs and signing secrets are different. Prepare appropriate changes for version control, but do not create a commit without task authorization. Do not assume an iOS/iPadOS target also validates macOS, visionOS or watchOS: define the requested device/target matrix separately.

## Audit the dependency surface

For iPad targets, test dynamic window resizing, hardware keyboards, pointer input, sheet/popover presentation and scene state. `UIRequiresFullScreen` is deprecated in iPadOS 26; do not add it as the routine solution to an unresponsive layout. If a specialized product needs sizing restrictions, use the documented scene APIs after checking target availability. A single scene-enabled Capacitor app is not automatically a tested multi-window app. Source: [TN3192: migrating from UIRequiresFullScreen](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key).

Inspect all installed native plugins, including third-party scopes, local packages, and Cordova plugins. Search bounded native source for AppDelegate URL/lifecycle hooks, removed `tmpWindow`/`TmpViewController`, singleton/global window assumptions, and custom bridge controllers. JavaScript semver compatibility alone does not prove scene behavior. Legacy Capacitor URL notifications remain compatible; scene-scoped notifications require 8.5 or later.

Use the upstream migrator's output as evidence, not as proof that skipped files need no work. If it reports a partial/manual migration, inspect that state explicitly. Preserve the Xcode project's existing grouping conventions; verify the new source belongs to the app target and compiles.

## SPM and CocoaPods

SPM is the default and preferred starting point for newly added Capacitor 8 iOS projects. Choose CocoaPods for a new app only when an essential, audited dependency currently requires it; document the blocker and revisit its SPM path. Do not silently migrate existing CocoaPods projects during unrelated work. Detect actual `CapApp-SPM/Package.swift`, Xcode package references, Podfile, and lock state. Absence of a Podfile alone does not prove a valid SPM project.

Before migrating, inventory every plugin and transitive native SDK's SPM support, resources, privacy manifests, linker requirements, and any local pods. Plan blocked dependencies explicitly. Preserve Podfile.lock/Package.resolved where tracked; never delete them to force resolution. Use the existing Ruby/Bundler setup for CocoaPods; do not install Ruby tools or edit shell profiles during routine diagnosis.

Inspect the real project/scheme: SPM generally builds the xcodeproj; CocoaPods uses the generated xcworkspace. Do not hardcode a workspace path across both. Native package manager migration is a distinct change with a build/behavior comparison, not a hidden side effect of updating Capacitor.

For Pod failures, distinguish a locked-version constraint conflict from missing specs, network/CDN errors, and Ruby/Bundler mismatch. Reproduce with the project's existing Bundler command when present. Resolve conflicting constraints through the smallest supported plugin/SDK update; refresh specs only when missing/stale specs are the cause. Preserve the old lockfile for comparison and inspect the newly resolved diff. Repeated installation attempts will not fix incompatible constraints or a failing network.

## Preserve the package graph instead of patching generated output

Use supported plugin metadata to declare SPM dependencies, resources, linker/compiler requirements and binary targets. The 8.3.2 and 8.4.1 releases improve this generation and plugin dependency-version handling; diagnose with the resolved 8.5 CLI before copying old manual workarounds. Presence of Package.swift alone is still not proof of compatibility. Sources: [8.3.2](https://github.com/ionic-team/capacitor/releases/tag/8.3.2), [8.4.1](https://github.com/ionic-team/capacitor/releases/tag/8.4.1).

Distinguish maintained native application source from CLI-owned manifests and dependency output. `CapApp-SPM/Package.swift` is regenerated by sync: durable customizations belong in supported configuration/plugin metadata or deliberately owned native modules. Inspect CLI-driven dependency adjustments; do not hand-edit node_modules or generated manifests as the long-term source of truth. Check that needed resources and privacy manifests survive a fresh install/sync/build.

On 8.5, generated SPM metadata can legitimately include the Cordova product even without user-installed Cordova plugins. Do not remove it to make an 8.5 app resemble 9. Avoid adding custom dependencies on Capacitor's XCFramework paths or manually embedding its internal frameworks. Third-party SDK XCFrameworks are a separate matter and are not globally forbidden. Source: [8.5 SPM generator](https://github.com/ionic-team/capacitor/blob/8.5.0/cli/src/util/spm.ts).

## Use stable language/tooling defaults

Writing new Swift code does not require forcing Swift 6 language/tooling settings. In 8.5, `experimental.ios.spm.swiftToolsVersion`, `packageTraits` and `packageOptions` remain experimental; the default tools version is 5.9, and traits need 6.1+ with additional compatibility testing. Keep defaults unless an actual SDK requirement justifies a tested override. Do not preemptively rename these keys to a guessed 9 API. A newer Xcode does not by itself require opting into those settings. Source: [8.5 config declarations](https://github.com/ionic-team/capacitor/blob/8.5.0/cli/src/declarations.ts).

## Preserve navigation restrictions

An existing `WKAppBoundDomains` allowlist is not disposable troubleshooting state. Read the app-bound-domain instructions in [configuration.md](configuration.md): retain the list, include the local hostname, and verify `ios.limitsNavigationsToAppBoundDomains`. Check OAuth callbacks and required navigation against that boundary rather than removing it to make injection work.

Distinguish top-level WebView navigation from fetch/API origins and external authentication sessions. Do not add every API host or OAuth provider to the app-bound list. Keep external login in the provider-supported system authentication/browser flow; return only the validated callback to the app. If top-level remote navigation is genuinely required, assess its bridge exposure separately. Source: [WebKit app-bound domains](https://webkit.org/blog/10882/app-bound-domains/).

Sources: [SPM guide](https://capacitorjs.com/docs/ios/spm), [iOS troubleshooting](https://capacitorjs.com/docs/ios/troubleshooting).

## Optional native extensions

Widgets/Live Activities, notification-service and Share extensions require native targets with their own lifecycle, resources, entitlements and signing. They cannot assume the app's WebView, React state or bridge is running. Design only the necessary shared App Group storage and validated return links; test the extension and containing app separately. App Intents require their own native intent integration and do not automatically map JS handlers into system actions. Do not add these capabilities just to make a wrapper look native. Sources: [ActivityKit](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities), [App Groups](https://developer.apple.com/documentation/xcode/configuring-app-groups).

For user-initiated long-running iOS/iPadOS 26 work, evaluate supported BackgroundTasks APIs such as `BGContinuedProcessingTask` as an explicit native feature with availability, cancellation and expiration handling. It is not permission for unlimited background processing and is not automatically exposed by Capacitor Background Runner. Source: [Long-running tasks](https://developer.apple.com/documentation/backgroundtasks/performing-long-running-tasks-on-ios-and-ipados).
