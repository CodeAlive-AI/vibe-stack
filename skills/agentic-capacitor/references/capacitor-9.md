# Preparing for Capacitor 9

Status checked 2026-08-31. Capacitor 9 is a prerelease line, not the production target of this skill. Recheck official release/migration notes before applying any 9-specific changes.

## Verified channel snapshot

On 2026-08-31, public npm metadata for core, CLI, iOS and Android showed `latest = 8.5.0` (published 31 July) and `next = 9.0.0-alpha.6` (published 14 July). No 9.x beta or RC versions were present. Nightly builds are a separate channel, not stable patches. Sources: [core registry metadata](https://registry.npmjs.org/@capacitor/core), [CLI](https://registry.npmjs.org/@capacitor/cli), [iOS](https://registry.npmjs.org/@capacitor/ios), [Android](https://registry.npmjs.org/@capacitor/android).

These are a dated snapshot: refresh tags, version lists and release notes when advising later. A cached `next` value is not a permanent pin or evidence that development has stopped.

## Announced direction, not a final contract

The [28 August roadmap](https://ionic.io/blog/the-road-to-capacitor-9) forecasts late-November release. It describes optional Cordova support, iOS modernization to Swift and changes away from XCFramework distribution. It also plans foundations for larger/multi-instance environments; full window APIs and per-instance bridge state are not promised for 9.0. These are planning inputs, not invented final SDK/toolchain requirements.

The [May alpha announcement](https://ionic.io/blog/capacitor-9-starts-here) requests testing Capacitor-only, mixed, and Cordova-only plugin combinations. Do not copy its floating `next` installation or peer-conflict bypass into an 8.5 production workflow.

## Current production recommendation

Start a new production app on the verified stable 8.5 line with SPM and UIScene, even when its planned launch is December/January. A late launch does not remove today's alpha/toolchain risk. This is an engineering recommendation, not an upstream guarantee that every app must choose 8.5 forever. Explicit experimental work can target an exact alpha with the user's accepted constraints and a preserved stable baseline.

The native project, SDK packaging and plugin layer deserve particular attention; a thin adapter helps localize changes but does not make migration free or predict its cost. UIScene already shipped in 8.5, so adopting it does not require selecting 9. Source: [8.5 release announcement](https://ionic.io/blog/capacitor-8-5-released).

As a concrete regression to check, [issue #8560](https://github.com/ionic-team/capacitor/issues/8560) was open on the verification date and reports App Store upload rejection for alpha.6 due to nested/duplicate Capacitor frameworks in Cordova packaging. It is a user-reported issue, not proof every alpha app fails. Recheck its resolution against the exact tested version and inspect archive packaging; never delete embedded frameworks blindly to suppress validation.

## Build the 8.5 app so future migration stays local

The everyday implementation rules are in the iOS, configuration and native-capabilities references: standard plugin metadata instead of generated-file patches, native TypeScript-compatible config, stable SPM defaults, scoped bridge/scene ownership, public APIs and feature-sized adapters. Apply them now without installing 9. These practices reduce avoidable coupling; remaining migration cost still depends on the app's native SDKs and plugins.

Read releases by branch and exact contents. For example, the July 14 alpha.6 release predates the July 31 8.5 TS7-loader and UIScene changes; its larger major number is not evidence those later fixes are included. The alpha.6 note about removing Cordova.framework is not an instruction to remove it from an 8.5 project or proof that every archive-packaging issue is resolved. Sources: [8.5.0](https://github.com/ionic-team/capacitor/releases/tag/8.5.0), [alpha.6](https://github.com/ionic-team/capacitor/releases/tag/9.0.0-alpha.6).

## Useful work on 8.5 now

1. Complete and test UIScene adoption instead of postponing it until 9.
2. Prefer supported Capacitor plugins over introducing Cordova into a new project when they meet the actual requirement. Inventory existing Cordova dependencies, including transitive native SDKs and local plugins. Record why each is needed; do not remove a working dependency merely because future builds can omit it.
3. Prefer SPM for new iOS projects and assess migration blockers in existing ones. CocoaPods trunk is scheduled to stop accepting new releases on 2 December 2026; existing pod downloads do not simply disappear. Track upstream/native SDK distribution plans. Source: [CocoaPods announcement](https://blog.cocoapods.org/CocoaPods-Specs-Repo/).
4. Audit plugins for assumptions about Capacitor's binary packaging, ObjC exposure, AppDelegate ownership, global windows and global bridge state. Recheck exact 9 migration tooling when available; do not patch guessed future APIs into 8.5.
5. Keep native plugin access and lifecycle ownership well defined; test adaptive layout and independent screen state without claiming multi-window support already exists.

## Stage the transition by evidence, not calendar dates

| Stage | Decision and verification |
| --- | --- |
| Stable development now | Build the required feature set on 8.5; retain native source and a tested lockfile. |
| Beta/RC becomes available | Re-evaluate plugins and tooling; when a trial is requested, compare an exact prerelease against the stable baseline. October/November is only a possible planning window, not an announced beta/RC schedule. |
| Trial builds | Run the target-version migration tooling only after inspecting its supported path; build/archive iOS and Android and test actual auth, links, lifecycle and plugins. TestFlight/Play Internal uploads need authorization. |
| GA and follow-up releases | Review the final migration guide, regressions and relevant patches; adopt only when this project's compatibility and distribution gates pass. GA, RC, or the first patch is not a safety guarantee. |
| App ships before readiness | Ship the supported, verified 8.5 build; do not force a major upgrade solely to match a release date. |

Do not promise beta/RC dates, a fixed migration cost, or automatic monitoring. Scheduling checks, creating branches/worktrees, and uploading builds remain separate actions requiring the applicable user authorization.

## Upgrade gate

If the user requests a prerelease trial, select an exact prerelease version and an explicitly authorized isolated location. Record toolchain, plugin matrix, lockfile/native diffs and rollback path; do not create a branch/worktree without authorization. Run the same functional checks as the working 8.5 build and report regressions. Avoid broad peer overrides: an unsupported plugin remains a blocker until verified.

Before production adoption verify official stable release status, final requirements, plugin/native SDK compatibility, migration completion, device tests and distribution readiness. This skill offers preparation and a gated migration process, not a guarantee of compatibility with an unfinished major release.
