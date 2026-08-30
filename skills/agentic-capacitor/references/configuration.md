# Configuration and builds

## Commands belong to the app package

Detect npm/pnpm/Yarn/Bun from the repository; do not replace its package manager. With pnpm, run from the app directory or use the workspace filter. Example only, after selecting 8.5.0 and iOS:

```sh
pnpm add --save-exact @capacitor/core@8.5.0 @capacitor/ios@8.5.0
pnpm add --save-dev --save-exact @capacitor/cli@8.5.0
pnpm exec cap init
pnpm exec cap add ios
pnpm run build
pnpm exec cap sync ios
```

Supply the real app name/id during initialization; never reinitialize an existing config. Use the mobile build script if different from `build`. Add Android and its aligned package when Android is in scope. Commands execute package hooks/config and may download native dependencies: review unfamiliar code and dependency provenance first.

`copy` copies web assets/config; `sync` also updates native dependencies; `run` syncs, builds, and deploys to a target. None substitutes for the framework build. Verify exact options with the installed CLI. Use local executables (`pnpm exec`, `npm exec` after checking local availability, or repository scripts), not a floating remote runner.

## Keep TypeScript configuration executable by the real loader

CLI 8.5 fixes loading `capacitor.config.ts` with TypeScript 7. When the classic TS compiler API is absent, it imports the file using Node's native type stripping; a successful frontend typecheck does not prove this path works. Verify the locally resolved CLI and actual Node runtime before diagnosing a config-load failure. Source: [8.5 release](https://github.com/ionic-team/capacitor/releases/tag/8.5.0), [tagged loader](https://github.com/ionic-team/capacitor/blob/8.5.0/cli/src/util/node.ts).

Use `import type { CapacitorConfig } from '@capacitor/cli'`, erasable TS syntax and explicit Node-resolvable imports. Avoid bundler-only path aliases, JSX, runtime enums and parameter properties in config and its helpers. Native stripping does not honor tsconfig paths or typecheck the file. Respect existing module semantics; do not flip the entire app's package type to repair one config. Source: [Node TypeScript loading](https://nodejs.org/api/typescript.html).

The general Node 22 minimum is not sufficient for every TS7 setup. Prefer a maintained runtime with native stripping enabled; Node 24.12+ is one supported stable path. Node 22.18+ enables stripping by default; earlier 22 releases require checking availability and launch flags. Keep configuration simple and verify loading without printing secret-bearing config; do not downgrade TypeScript or add a global loader hack by default.

## Production configuration

Start with only app identity and the verified web output directory. Treat native build, runtime bridge config, and backend environment as different layers. Config passed to the binary must not contain signing passwords or backend credentials. Typecheck against `CapacitorConfig`; unknown fields are not a feature.

Keep production `server.url` absent, cleartext disabled, TLS validation intact, and external domains out of `allowNavigation`. Open untrusted external links in an appropriate browser instead of granting their pages the app bridge. Avoid changing local hostname/scheme casually: they affect storage, origins, routing, and auth.

If iOS already uses `WKAppBoundDomains`, preserve that restriction. Verify `ios.limitsNavigationsToAppBoundDomains: true` and the precise required domains, including the configured local hostname. Do not delete the allowlist to fix bridge injection. Source: [Configuration](https://capacitorjs.com/docs/config).

## Live reload without release leakage

Start the existing framework dev server separately. On a trusted network configure its reachable host/port and a development-only origin policy; do not expose it publicly. Capacitor 8.5 `cap run ios --live-reload --host <host> --port <port>` configures the URL; it does not start that server. Confirm installed options, HTTPS/certificate behavior, and any platform-specific debug network requirements. Source: [cap run](https://capacitorjs.com/docs/cli/commands/run).

The 8.x CLI already includes live-reload HTTPS support and failure-restoration fixes; do not build permanent custom scripts that rewrite production config for this purpose. Automatic restoration does not cover every interrupted process or stale native artifact.

Before release, stop using the reload profile, build local production assets and sync again. Inspect the generated iOS and Android config actually embedded in the release artifact. A clean source config or `NODE_ENV` branch alone does not prove stale development settings were removed. Fail release verification if remote dev URLs, permissive ATS/network policy, debugging, or test credentials remain.
