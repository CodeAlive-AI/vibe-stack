# agentic-capacitor

**Version 0.1.1.** [Open the skill](SKILL.md).

Add Capacitor to an existing web app without rewriting its UI or moving its backend into the mobile bundle. The skill supports continued native development as well as the initial web-to-mobile conversion, follows the requested platform order, and does not require Ionic or a particular UI library.

The verified baseline is **Capacitor 8.5**, with specific guidance for **React 19.2** and Next.js client/server boundaries. Capacitor 9 material explains choices to make on 8.5 now and a later upgrade assessment; it does not authorize installing prereleases. Release and toolchain facts are dated **2026-08-31** and must be rechecked when changing targets.

## What it covers

- Existing SPA/PWA/web apps to bundled iOS and Android clients, retaining their deployed backend.
- React lifecycle, routing, authentication, cold/warm deep links, streaming, and native capability boundaries.
- iOS SPM and UIScene; Android toolchain, back navigation, edge-to-edge layout, and adaptive UI.
- Plugins, permissions, files, storage, keyboard/insets, lifecycle recovery, security, privacy, and release checks.
- [Performance](references/performance.md): measured startup, bridge traffic, memory, media handling and Android release optimization; explicit plugin-error, biometric-access and optional OTA contracts.
- Deterministic checks of dependencies, built web assets, copied native configuration/assets, and selected iOS/Android metadata.

Read the [coverage matrix](references/platform-coverage.md) for conditional features and limits, the [version rules](references/versions.md) for prerequisites, and [Capacitor 9 readiness](references/capacitor-9.md) for the upgrade strategy.

For Apple submission or resubmission, pair this engineering workflow with [apple-app-store-reviewer](https://github.com/CodeAlive-AI/vibe-stack/blob/main/skills/apple-app-store-reviewer/README.md). It reviews release evidence, metadata, screenshots and Apple-specific requirements; return implementation findings here for fixes and then re-review the candidate. The skills work independently and do not install or invoke each other automatically. See the [handoff rules](references/store-readiness.md).

## Install

Review the skill and choose the agent and installation scope before installing. Keep one active implementation named `agentic-capacitor`; do not overwrite a divergent local copy without reviewing it.

Using the optional [Agent Skills CLI](https://github.com/vercel-labs/skills), from the project where you want to use the skill:

```sh
npx skills@1.5.23 add CodeAlive-AI/vibe-stack --skill agentic-capacitor
```

This pins the installer version, requires Node.js 22.20+ for that installer, and downloads and runs a third-party CLI. Select the intended agent in its prompts. The repository source follows the default branch; for reproducibility, check out a reviewed repository commit and install the local `skills/agentic-capacitor` directory instead. Installer syntax is documented [upstream](https://github.com/vercel-labs/skills#install-a-skill).

Alternatively, download or clone this repository and use your agent's installer or documented skill directory. Install the **entire** `skills/agentic-capacitor` folder, including `references/`, `scripts/`, and all three license/attribution files. Do not install only `SKILL.md`, the parent `skills/README.md`, or the whole repository as one skill. No additional agent skill, commercial service, or npm/pip package is a runtime dependency of the bundled validator.

## Example requests

> Use agentic-capacitor to add an iOS app to this existing React web app on Capacitor 8.5. Preserve the web UI and backend; leave Android for later.

> Use agentic-capacitor to audit this Capacitor 8.5 migration. Check the client/server boundary, copied assets, authentication, native lifecycle, and release configuration. Report file checks separately from builds and device tests.

> Use agentic-capacitor to make this 8.5 app easier to migrate to Capacitor 9 later, without installing prereleases or adopting unverified native changes.

## Validate an app

The validator requires **Python 3.10+**, uses only the standard library, and runs offline without executing app configs, package scripts, build tools, or hooks. Run it after the app's reviewed web build and Capacitor copy/sync steps; it does not perform those steps itself.

Replace the paths with the actual installed skill and app locations. For a standalone app omit `--workspace`; `out` is an example web artifact directory, not a required name.

```sh
python3 -I /path/to/agentic-capacitor/scripts/validate_capacitor.py \
  --app /repo/apps/mobile --workspace /repo \
  --checks all --platform ios --web-dir out
```

Add `--platform android` when Android is in scope. JSON is the default output; add `--format text` for human-readable findings. Exit codes: `0` selected static checks passed, `1` confirmed failure, `2` review required, `64` invalid arguments, `70` unexpected validator error. Do not suppress nonzero statuses in CI.

See [validation scripts](references/validation-scripts.md) for individual check groups, custom layouts, safety boundaries, and unsupported checks.

## Verification and maintenance

The initial release passed **31 regression tests** against synthetic fixtures. It has not yet been validated by migrating a real application and completing native builds and device tests on both platforms. A passing static check does not establish plugin compatibility, authentication correctness, signing, privacy compliance, or store acceptance.

Run the regression suite from the repository root after changing the validator:

```sh
python3 -I skills/agentic-capacitor/scripts/test_validate_capacitor.py
```

Keep the entry point short and place detailed workflows in the relevant references. Update version claims against official releases and installed types. Do not commit generated reports, edit logs, snapshots, Python bytecode, or release ZIPs into the skill directory.

## License and sources

MIT, with the [main license](LICENSE), the preserved [Capawesome license](LICENSE.capawesome), and [Capgo attribution](NOTICE.capgo). Keep all three when redistributing the skill.

The skill consolidates and corrects reviewed material from Capgo's `webapp-to-capacitor` and `capacitor-best-practices` and Capawesome's `capacitor-app-development`; [provenance](references/provenance.md) records the source commits and license evidence. Upstream examples are selectively rewritten, not imported as executable setup instructions. It is not an official or endorsed product of Ionic, Capgo, or Capawesome.
