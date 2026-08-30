# Platform coverage and feature gates

This skill is a practical Capacitor 8.5 integration/development workflow, not an exhaustive implementation of every iOS/Android API. Coverage reviewed 2026-08-31. Keep the production baseline distinct from new OS behavior, separately versioned plugins and unfinished Capacitor 9 work.

At project intake, mark each area **required**, **not applicable**, or **needs a product decision**. Record the relevant platform/runtime/plugin versions and evidence. Do not install features merely to turn the checklist green. Read the matching references from the SKILL.md map; the table below states the depth and limits of coverage rather than duplicating their instructions.

| Area | Skill coverage | Evidence still required in an app |
| --- | --- | --- |
| Web/React 19.2 conversion | Client/server boundary, native origins, routing, effects, local artifacts and copied config | Real mobile routes, retained backend/auth, lazy chunks, CSS/browser support, offline and resume behavior |
| Capacitor/package setup | Stable 8.5 alignment, manager/lock ownership, SPM/CocoaPods, reproducible config and generated-output boundaries | Frozen install, native dependency graph, compile and release archive |
| iOS lifecycle | UIScene migration, bridge ownership, iPad resizing, custom native code, platform minimum versus submission SDK | Source membership, cold/warm callbacks, selected devices/windows, native SDK behavior |
| Android behavior | Target36 edge-to-edge/predictive back/adaptive UI, process restoration, release network policy, native 16 KB checks | Actual target/OS combinations, merged manifest, ELF/APK/AAB tools, release build and 16 KB device |
| UI and accessibility | Insets/keyboard/portals, text scaling, screen readers, reduced motion, modern system appearance and icons | Oldest supported WebView, current devices, keyboard/pointer and assistive-technology testing |
| Auth, files and persistence | Native session origins, verified links, secure-storage boundaries, pickers, streamed transfers and user isolation | Provider return, logout/reinstall, temporary grants, permission/limited states, interruption and large-file memory |
| Notifications/background | APNs versus FCM, silent/data-message limits, channels, exact alarms, headless runner and OS scheduling | Registration, delivery/taps, killed-app behavior, scheduling denial, physical-device background tests |
| Privacy/distribution | Required-reason/SDK manifests, ATT applicability, store disclosures, account deletion and provider-specific billing | Archive privacy report, accurate declarations, signing, purchase/restore and store review |
| Capacitor 9 preparation | Public interfaces, minimal packaging assumptions, plugin inventory and gated trials | Final migration guide, target-version builds/tests, SDK compatibility and release acceptance |

## Optional native features need a separate implementation contract

Widgets/Live Activities, Share/notification extensions and App Intents are described as native integration work; no bundled script certifies them. Likewise passkeys/biometrics, Bluetooth/NFC, location/geofencing, health data, background audio/recording, maps, on-device models and platform-specific system UI need feature-specific official documentation, a reviewed compatible plugin or native adapter, permissions/entitlements, lifecycle/error contracts and device tests. These are supported task categories for investigation, not prevalidated implementations or mandatory dependencies.

For each chosen feature record what exists in core, what needs an independently versioned plugin, what requires native code/another target, the minimum OS/device, external service needs, privacy/security implications and test evidence. If a required API is unavailable, report that explicitly rather than silently substituting a web mock. Capabilities involving health, payments, children, tracking or background collection require their applicable product/policy review.

## Do not equate documentation with automated coverage

The bundled scripts check package/config/file invariants, copied hashes and selected plist/manifest fields. They do **not** currently prove 16 KB binary alignment, privacy-manifest correctness, scene execution, predictive-back animation, permissions, push, background tasks, billing, auth, plugin compatibility, extension packaging or device UX. Keep their `pass/fail/review` report separate from native build and device evidence. The regression suite tests the validator, not a real Capacitor application.

Define an app-specific acceptance matrix from these areas. A useful completion claim names exactly which platform/version/features were built and tested, and which remain unchecked; “all modern features supported” is not a reproducible claim.
