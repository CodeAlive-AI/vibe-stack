# Android integration

Use the version table before changing build files. Preserve the project's Gradle wrapper, native package names, flavors, signing setup, custom activity, and Java/Kotlin choice. Compare with the tagged template rather than copying an old Gradle snippet.

## Native behavior

- Handle system back through the existing router/modal history. Test root behavior, overlays, predictive back where applicable, and navigation restored after process death. Do not exit the app on every back event.
- Test rotation, window resizing, split screen, large screens, gesture navigation, and three-button navigation. Inspect `configChanges`, including the Capacitor 8 density change, without dropping existing flags.
- Apply edge-to-edge insets in the web layout. Removed margin settings and OS opt-outs are not durable substitutes for a correct layout.
- Request permissions for the actual API level and feature. Runtime permissions predate Android 13; notification permission is a separate version-sensitive case. Test denied and limited access, process recreation, and returning from system settings.
- Keep cleartext and debugging exceptions scoped to development; do not change release network security to fix a LAN dev server.

For camera capture launched through WebView file inputs, test URI permission grants and cancellation on real supported devices. Stable 8.4.2 already fixed grants to the capture intent; 8.5 includes that baseline. Do not compensate with broad storage permissions or an exported provider. Distinguish this WebView path from a separate camera plugin. Source: [8.4.2](https://github.com/ionic-team/capacitor/releases/tag/8.4.2).

## Target SDK behavior is part of the migration

Separate device OS version from targetSdk. On Android 16 with target 36, edge-to-edge opt-out no longer works; legacy `onBackPressed`/KEYCODE_BACK interception also stops receiving the former callbacks. Inspect custom Activities and plugin back handlers against supported predictive-back APIs, then exercise web-router history, modal dismissal, root behavior and gesture cancellation. Do not add a permanent opt-out or globally exit to suppress broken navigation.

For target 36 on displays with smallest width at least 600dp, orientation/aspect-ratio/resizability restrictions generally stop controlling layout, subject to documented exceptions. Test fold/unfold, resize, keyboard/pointer, density changes, dialogs and state retention. A portrait lock is not an adaptive layout strategy. Retest newer OS changes separately instead of raising targetSdk beyond the verified Capacitor/plugin baseline by guesswork. Source: [Android 16 target behavior](https://developer.android.com/about/versions/16/behavior-changes-16).

## Native libraries and 16 KB pages

Inventory every packaged `.so`, including transitive SDKs. Uncompressed libraries need AGP 8.5.1+ for appropriate packaging; NDK r28+ defaults to 16 KB ELF alignment, while older NDKs need the documented settings. Precompiled dependencies still need compatible binaries. Check ELF LOAD alignment, APK zip alignment, AAB `PAGE_ALIGNMENT_16K` and execution on a 16 KB device. Java/Kotlin-only apps differ; ordinary APK launch alone proves neither packaging nor runtime compatibility.

Use inspected local tools: `zipalign -c -P 16 -v 4 <release.apk>` checks packaging; `adb shell getconf PAGE_SIZE` should report `16384` on the selected device. Do not run unreviewed downloaded checkers, hide failure through compatibility mode, or hand-patch packaged binaries.

As checked 2026-08-31, Google's updated page says updates without support will be blocked from 1 February 2027; older announcements used November 2025. Recheck current documentation and the app's Play Console requirements at release. The engineering requirement remains relevant now. Source: [16 KB support and verification](https://developer.android.com/guide/practices/page-sizes).

## Background execution

For persistent deferrable native work, evaluate WorkManager rather than a JS timer or exact alarm. Foreground services are a separate user-visible mechanism: target 34+ requires the appropriate service type/permissions, and foreground execution does not erase newer job quotas or background-start restrictions. Test interruption, retries, cancellation and battery constraints on the supported OS matrix. Sources: [Persistent work](https://developer.android.com/develop/background-work/background-tasks/persistent), [Foreground service types](https://developer.android.com/about/versions/14/changes/fgs-types-required), [Android 16 job behavior](https://developer.android.com/about/versions/16/behavior-changes-all).

## Diagnosis

Record the first failing Gradle task and sanitized compiler error. Compare Java/AGP/Gradle compatibility and plugin native SDK requirements before editing. Use project-local build cleanup only when generated output is implicated; never wipe the user's Gradle cache or rewrite shell rc files as a standard recipe. For R8 failures inspect the plugin's consumer rules and use targeted, justified rules; broad keep-all rules can hide missing integration and bloat the binary.

Test on an emulator and a real device when hardware, permissions, file access, or release behavior matters. A successful browser test does not validate the Android bridge.

Sources: [Android configuration](https://capacitorjs.com/docs/android/configuration), [Android troubleshooting](https://capacitorjs.com/docs/android/troubleshooting), [Android 16 adaptive layouts](https://developer.android.com/about/versions/16/behavior-changes-16#adaptive-layouts).
