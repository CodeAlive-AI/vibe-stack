# Version and toolchain rules

Verified 2026-08-31. Recheck official releases, package metadata, and installed lockfiles before a dependency change. Date labels are evidence timestamps, not guarantees of continued freshness.

## Supported working baseline

| Component | Capacitor 8.5 baseline |
| --- | --- |
| Core, CLI, installed iOS/Android packages | 8.5.0 at verification time; align exact resolved versions |
| Node | 22 or newer; retain a newer compatible project requirement |
| iOS / Xcode | iOS 15 minimum; Xcode 26+; UIScene required for Xcode 27 builds |
| Android | minSdk 24; compileSdk / targetSdk 36 |
| Android toolchain | JDK 21; AGP 8.13.0; Gradle 8.14.3; Android Studio Otter 2025.2.1+ |
| Kotlin, when used | 2.2.20 baseline; do not convert Java code merely to adopt Kotlin |

Sources: [8.0 migration](https://capacitorjs.com/docs/updating/8-0), [Android environment](https://capacitorjs.com/docs/android), [8.5 release](https://github.com/ionic-team/capacitor/releases/tag/8.5.0).

Check higher requirements imposed by plugins/SDKs; never lower an existing supported deployment target to match this table. Use a coherent toolchain, not isolated upgrades of Gradle, AGP, and Java. Official plugins often use an 8.x release but are independently versioned; other official plugins may use a different major. Inspect peer dependencies and platform requirements for the exact package.

Store submission SDK requirements are separate from minimum supported device OS. Since 28 April 2026, App Store Connect requires iOS/iPadOS uploads built with SDK 26 or later; this does not require raising every app's deployment target to iOS 26. Recheck upload rules when shipping and keep beta SDK/OS testing distinct from the production toolchain. Source: [Apple SDK requirements](https://developer.apple.com/news/?id=ueeok6yw).

For ordinary Google Play mobile apps, the checked rule from 31 August 2026 requires new submissions/updates to target API 36+, with a separate API 35 availability rule for existing apps and different form-factor exceptions. Do not confuse targetSdk with minSdk or assume an extension is automatic. Recheck the app's deadline/eligibility before submission. Source: [Play target API policy](https://support.google.com/googleplay/android-developer/answer/11926878).

For a new 8.5 integration, resolve a stable patch within 8.5, inspect its changelog/advisories, then pin the selected version and preserve lockfiles. For a current working 8.5 app, do not downgrade or update unrelated dependencies just to match examples. For older apps, read every intervening major migration guide plus 8.5; do not treat the UIScene migration as the complete Capacitor 6/7 upgrade.

For TypeScript 7, CLI 8.5's config-loader fix also depends on Node's native TS-loading capabilities. Read the configuration reference before treating the broad Node minimum as sufficient. Do not assume an older 9 alpha contains every fix shipped later on 8.x: version numbers across release branches are not a chronological inclusion order.

## Dependency ranges are not a migration plan

`^8.5.0` permits later 8.x minors, including 8.6; it does not constrain resolution to 8.5 patches. If the task explicitly targets the 8.5 line, use a reviewed exact patch (the default here), or an intentionally chosen `~8.5.0` range with a committed lockfile. Preserve a repository's existing range policy unless changing it is part of the task, but report any mismatch with the requested target. Frozen/immutable installs reproduce the lock; dependency updates still need review and tests.

“Keep all plugins on latest 8.x” is not a valid blanket rule. Select supported, patched releases per plugin, including packages with different version schemes, and check native SDK and SPM compatibility. Do not infer safety from a release tag or the age of a release alone.

The dated [plugin shortlist](plugin-selection.md) records exact candidates and exceptions for this 8.5 baseline. For example, File Transfer 2.0.5 and InAppBrowser 4.0.3 target Capacitor 8; InAppBrowser also raises Android minSdk to 26. Validate plugin requirements separately from core alignment. Broad npm peers and an SPM manifest are evidence to inspect, not proof of native builds or Capacitor 9 support.

## Evidence hierarchy

Use installed public type definitions and native source for API signatures, tagged templates for generated project shape, and official migration guides for behavior changes. Check package registry metadata without installing packages merely to inspect them. Resolve conflicts by exact version; document remaining uncertainty. Do not let a future change of `latest` silently turn an 8.5 task into a 9 migration.
