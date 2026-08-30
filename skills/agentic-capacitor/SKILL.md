---
name: agentic-capacitor
description: Develops Capacitor 8.5 apps and converts existing web apps (web-app-to-capacitor), especially React 19.2. Use when adding iOS/Android, integrating native features, diagnosing native builds, migrating to UIScene, or preparing for Capacitor 9. Not for React Native or unrelated React UI work.
license: MIT
metadata:
  version: "0.1.0"
---

# Agentic Capacitor

Build on the application's existing web architecture. Target the verified Capacitor 8.5 release line; treat Capacitor 9 preparation as a separate compatibility assessment, not permission to install prereleases. This skill covers web-app-to-Capacitor integration and continued native development without requiring Ionic or another UI framework.

For a new production integration under the verified baseline, start with 8.5 and the default iOS SPM/UIScene template. Keep native dependencies easy to audit; use the 9 readiness gate to decide when to trial or adopt the next major, regardless of the application's planned launch month.

When implementing on 8.5, reduce future migration work through public APIs, explicit native ownership, reproducible SPM metadata and small feature adapters. Modern does not mean enabling every experimental option or copying 9 alpha internals into 8.5. Apply these choices during normal development, not only when an upgrade is requested.

## Establish the working boundary

1. Identify the actual app/workspace root, package manager and lockfile, resolved Capacitor packages, web build output, native targets, and iOS dependency manager. Inspect scoped manifests and source; do not dump scripts, environment values, signing material, or entire dependency trees into output. Package scripts and TypeScript config are executable code: review relevant code before invoking them in an unfamiliar repository.
2. Determine the requested mode: existing web conversion, native feature, diagnosis, 8.5 migration, or 9 readiness. Follow the user's platform order; do not create Android when only iOS is requested, or vice versa.
3. Preserve the framework, router, UI, package manager, native customizations, and deployed backend. Separate facts verified in files from assumptions. Ask only for missing choices that block a safe implementation, such as the app identifier; continue independent work first.
4. Read [version and toolchain rules](references/versions.md), then only the relevant references below. Verify changed APIs against installed types and official versioned sources, not recollection or vendor examples. A failed lookup leaves compatibility unverified; it is not permission to invent an API.

## Choose the workflow

Select the mode from the requested outcome; do not run every mode for a small task.

- **Convert a web app:** establish the client/server boundary, reuse the working web UI, and prove a representative native journey before adding capabilities.
- **Develop a native feature:** inspect existing platform integration, implement the smallest compatible change, and verify the real permission/lifecycle/error paths.
- **Diagnose a failure:** reproduce and identify the failing layer before changing configuration, dependency resolution, or generated files.
- **Migrate to 8.5:** compare the current version and native project with the target requirements; merge custom native behavior and verify regressions.
- **Prepare for 9:** produce a compatibility inventory and blockers while keeping the stable build intact; perform prerelease work only when requested.

Use this shared reference map in every mode. Conversion continues into normal native development using the same configuration, security, and verification rules; it is not a separate nested skill.

| Request | Read before implementing |
| --- | --- |
| Existing web app, SPA, PWA to mobile | [Web conversion](references/web-conversion.md) |
| React 19.2, Next.js, effects, SSR, routing | [React integration](references/react.md) |
| CLI, native setup, configuration, live reload | [Configuration and builds](references/configuration.md) |
| iOS 8.5 lifecycle, SPM, native migration | [iOS and UIScene](references/ios.md) |
| Android toolchain, back behavior, adaptive UI | [Android](references/android.md) |
| Insets, system bars, keyboard, splash, accessibility | [Native UX](references/native-ux.md) |
| Login, deep links, CORS, cookies, streaming | [Authentication and networking](references/auth-network.md) |
| Plugins, permissions, files, persistence | [Native capabilities](references/native-capabilities.md) |
| Supply chain, secrets, bridge exposure, privacy | [Security](references/security.md) |
| Failures, testing, CI, signing, distribution, OTA | [Verification and release](references/verification.md) |
| Deterministic post-conversion/config/assets checks | [Validation scripts](references/validation-scripts.md) |
| Store-facing login, account deletion, billing, minimum functionality | [Store readiness](references/store-readiness.md) |
| Upcoming major version | [Capacitor 9 readiness](references/capacitor-9.md) |
| Full integration/release review, feature applicability | [Platform coverage and limits](references/platform-coverage.md) |

## Implement a working vertical slice

For a conversion, first prove that the selected client artifact runs inside the selected native target, reaches its existing backend, and completes a representative authenticated journey. Add required native features after this boundary works. For an existing app, make the smallest change that resolves the requested behavior.

Use the repository's package manager and locally resolved CLI. Keep core, CLI, and installed platform packages aligned; plugins have independent version numbers and compatibility requirements. Scope commands to the app package. Do not use floating `latest`/`next`, force peer conflicts away, or change all workspace dependencies as a setup shortcut.

Build web assets before copying/syncing; `cap sync` does not compile React or Next.js. Inspect native diffs after sync. Native projects are maintained source: never delete/recreate them to fix a routine build failure. Do not remove lockfiles or global caches as a first repair.

Preserve web behavior while adding explicit native capability boundaries. An intentionally unavailable web feature can have a designed alternative; a missing native plugin, failed permission check, or failed authentication must remain an observable error. Do not silently substitute mock data, insecure transport, or unauthenticated requests.

## Release and safety boundaries

- Keep privileged backend code and credentials out of the shipped web bundle. Never read secret stores merely to diagnose setup; use variable names and redacted diagnostics.
- Package local production assets. Development server URLs, broad navigation permissions, disabled TLS checks, and HTTP exceptions are not production conversion strategies.
- Prefer capabilities already in the app or Capacitor core. Compare additional plugins by compatibility, native dependencies, maintenance, license, privacy, and cost; do not automatically add a vendor SDK or OTA service.
- Preparing code or a local build does not authorize app-store submission, OTA upload, cloud scanning, signing-account changes, purchases, or installing agent hooks. Reuse explicit authorization when present; otherwise finish the reviewable local result before asking about an external action.

## Verify and report

Run the existing relevant checks, then exercise native behavior on the selected platform. Web unit/E2E tests cannot prove native permissions, lifecycle, signing, or bridge correctness. For migration test cold and warm launch, links, resume, and custom plugins. For conversion test authentication, navigation, network failures, keyboard/insets, and any streaming or file paths the app uses.

Report changes, commands/checks actually run, target versions, and remaining blockers. Distinguish inspected, typechecked, built, simulator-tested, and device-tested. Never claim complete plugin compatibility, store acceptance, or production readiness from a documentation audit alone.

For maintenance, see [provenance and update rules](references/provenance.md).
