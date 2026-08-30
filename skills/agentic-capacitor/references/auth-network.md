# Authentication, links, and networking

## Model the origins and session

Record the web origin, native local origin on each platform, API origin, and identity-provider callback. Preserve the existing session protocol. A WebView cookie jar, an external system browser, and a native HTTP client are not automatically shared. Test login, expiration, refresh, logout/revocation, reinstall, and returning from an external identity provider on a real native build.

Credentialed web requests need the intended exact CORS origins, credentials policy, cookie attributes, and CSRF protection. Changing SameSite or using native HTTP is not a blanket authentication fix. Do not broaden origins to `*`, turn off CSRF, move HttpOnly sessions into JS storage, or place a client secret in the app. Choose a documented public-client/native auth flow compatible with the provider; authorization-code flows normally need PKCE and state (and OIDC nonce where used).

Sources: [Capacitor security](https://capacitorjs.com/docs/guides/security), [OAuth native apps](https://www.rfc-editor.org/rfc/rfc8252), [OAuth security practices](https://www.rfc-editor.org/rfc/rfc9700).

## Deep links are untrusted input

Configure Associated Domains/AASA for iOS and intent filters/assetlinks for Android with the actual app IDs and signing identity. Verify association delivery and installed-build behavior; TestFlight is not a general prerequisite for universal links. Serve association files from the real HTTPS domain, not only the native bundle. For static-export deployments verify CDN/file headers directly; framework server rewrites may not run. Custom schemes are not verified ownership; verified HTTPS links reduce interception risk but still require validation.

Handle both `App.getLaunchUrl()` and `appUrlOpen`; subscribe early enough not to lose startup events, queue until router/auth readiness, and deduplicate delivery. Parse with URL, allowlist exact scheme/host/port and route shapes, and reject malformed/unexpected destinations. Never substring-match a trusted host or navigate an arbitrary URL. Treat auth callbacks separately: validate state, PKCE, nonce and expected flow before navigation; do not log callback codes/tokens. Remove owned listeners when their owner ends.

Under UIScene verify native forwarding too; a correct JS listener cannot repair a missing SceneDelegate callback. Source: [Deep links](https://capacitorjs.com/docs/guides/deep-links), [App API](https://capacitorjs.com/docs/apis/app).

## HTTP and streaming

Keep normal browser `fetch` unless evidence requires a different transport. CapacitorHttp can patch fetch/XHR when enabled, but its API and native bridge are not a guarantee of browser streaming compatibility. Test SSE/chunk boundaries, aborts, credentials, redirects, upload bodies, errors, and background interruption before changing transport globally. Prefer a narrow adapter over a global patch where feasible. Fix server-origin policy rather than bypassing it invisibly. Source: [CapacitorHttp](https://capacitorjs.com/docs/apis/http).

Network status is advisory, not proof an endpoint is reachable. Handle timeout, captive portal, TLS, auth, rate-limit and server errors distinctly. Offline queues require idempotency, ownership and conflict handling; do not replay non-idempotent writes blindly after resume. Mobile OSes may suspend web execution in background; do not promise uninterrupted streams or timers without an appropriate native design.
