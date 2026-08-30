# React 19.2 integration

## Preserve the existing React application

Capacitor runs React DOM inside a WebView; React Native is a different runtime. React 19.2 does not require Ionic React, a new router, a Vite migration, or a new design system. Retain providers, routes, query caches, error boundaries, localization, and accessibility behavior. Check `react`/`react-dom` alignment and actual peer requirements of any added UI wrapper. “19.2 support” means the patched release line, not a recommendation to pin 19.2.0.

Check current framework and React security advisories before shipping server components. Vulnerabilities in RSC packages may affect the retained backend even when the mobile bundle is static. Do not assume every client-only React app has the same exposure. Sources: [React versions](https://react.dev/versions), [RSC security advisory](https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components).

## Client-only native integration

Invoke native capabilities after client mount or from user events; do not access `window` or call native plugins during SSR/module evaluation. In Next App Router, put hooks behind a `'use client'` boundary; Client Components may still be pre-rendered. Keep the initial render stable and detect platform after mount when it changes rendered markup. Use `Capacitor.isNativePlatform()` for the runtime boundary and `isPluginAvailable()` as one diagnostic, not proof of native correctness.

React effects must tolerate setup/cleanup/setup and asynchronous listener registration. Remove only the listener owned by the component; `removeAllListeners()` can break unrelated features. Handle registration/removal failures through the app's redacted error path. One possible lifecycle pattern:

```tsx
useEffect(() => {
  if (!Capacitor.isNativePlatform()) return;
  let disposed = false;
  let handle: PluginListenerHandle | undefined;
  void App.addListener('appStateChange', onAppState).then(async (listener) => {
    if (disposed) await listener.remove();
    else handle = listener;
  }).catch(reportNativeError);
  return () => {
    disposed = true;
    if (handle) void handle.remove().catch(reportNativeError);
  };
}, [onAppState, reportNativeError]);
```

Imports: `useEffect` from React, `App` from `@capacitor/app`, `Capacitor` and type `PluginListenerHandle` from `@capacitor/core`. Callback functions belong to the app and should have stable identities where appropriate. Do not disable StrictMode to hide leaks. Activity in React 19.2 tears down effects while hidden: app-global listeners should live at a stable root, not inside a hidden screen. Source: [React 19.2](https://react.dev/blog/2025/10/01/react-19-2).

## Next.js and other server-rendered frameworks

For Next App Router, static export can run build-time Server Components; it cannot retain request-time Server Actions, dynamic cookies, middleware/proxy, or arbitrary server routes inside the binary. Enumerate dynamic paths and inspect framework-specific export restrictions before choosing a build target. Server-dependent functionality stays behind a real server endpoint; preserve authorization and serialization contracts when adding a mobile client path. Image optimization and route refresh behavior need explicit export-compatible handling. Source: [Next static exports](https://nextjs.org/docs/app/guides/static-exports).

React client Actions are not automatically server functions; classify by actual execution location. Browser providers alone do not make a server-dependent route exportable. Hydration mismatch is a bug to investigate, not a reason to suppress warnings globally.

## Routing and streaming

Map a validated native deep link into the existing router after it and the auth state are ready. For Next App Router use its `next/navigation` client API; do not add react-router-dom solely for deep links. Keep pending navigation until initialization completes; deduplicate cold-launch/event delivery. Preserve router base paths and route guards. Do not replace the router with manual DOM navigation or use an arbitrary incoming URL as a route.

For chat/streaming applications, exercise incremental delivery, cancellation, reconnect, attachments, tool/result messages, and background/resume using the application's actual protocol. Do not replace a structured AI/event stream with plain text or globally patch `fetch` without verifying stream semantics. Keep WebSocket/SSE authentication and local-origin policy explicit.
