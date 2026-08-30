# Existing web app to Capacitor

## Inventory the runtime boundary

Identify the deployable client artifact and server-only dependencies. Capacitor hosts web assets in a native WebView; it does not embed a Node SSR server. List request-time rendering, API routes, Server Functions, cookies, file processing, secrets, and background jobs separately from browser UI. Inspect representative authenticated and dynamic routes, not just the landing page.

| Existing application | Integration decision |
| --- | --- |
| Client-rendered React SPA | Reuse its build, router, providers, and UI; point `webDir` at the emitted artifact. |
| Static-export-capable site | Verify all mobile routes/assets export and navigate correctly; retain a separate web deployment if needed. |
| Mixed SSR/RSC framework | Audit server-dependent routes; create a bounded mobile client build that calls the existing backend where feasible. Preserve the deployed server build. |
| Fundamentally request-rendered website | Explain what cannot run from local assets; design the minimum client/server separation before changing code. Do not promise a zero-change wrapper. |

The decision should name the client artifact, API/auth origins, routing approach, retained server responsibilities, and smallest representative journey. Do not replace the framework, globally enable static export, remove authentication, or disable server features to make the native build pass. A separate mobile build target is an option justified by evidence, not a mandatory rewrite.

## Prove the artifact

The output must contain an entry `index.html`, its referenced assets, and a usable document head. Confirm base paths, lazy chunks, fonts, images, localization, client routing, reload, and offline launch of the shell. Inspect the output for accidental server files and secret-bearing configuration without printing secrets. Public build variables are public after bundling.

Use explicit HTTPS backend endpoints for native builds; relative `/api` requests address the local app origin. Keep auth and transport semantics intact. For Next.js read the React reference before configuring export. Do not use `server.url` to disguise an unresolved server/client split in production.

## Sequence implementation

1. Establish the existing web build/test baseline and the requested native platform.
2. Add compatible Capacitor packages to the owning package; initialize only if absent, with the actual product identifier and app name.
3. Configure the verified `webDir`; build and sync only the requested platform.
4. Exercise a real login-to-primary-action journey. Check cold start, deep links, reload, back, network loss, and app resume.
5. Add needed keyboard/insets, sharing, notifications, camera, or other native capabilities without redesigning working web UI.
6. Assess store-facing login, deletion, billing and product usefulness early when distribution is in scope, using the store-readiness reference indexed in SKILL.md. Do not postpone architectural blockers until submission. A native container or a quota of native plugins does not guarantee review acceptance.

Keep web service workers/PWA caching deliberate: a stale worker must not serve an old JS bridge against a new native binary. Test cache/version transitions; disabling native service-worker registration can be an intentional build-specific choice without removing the PWA's worker.

Source: [Adding Capacitor to an existing web app](https://capacitorjs.com/docs/getting-started).
