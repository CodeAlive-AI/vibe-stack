# Performance after web-to-native conversion

Use this workflow when conversion changes startup, responsiveness, memory, energy use or binary size. Preserve the existing framework and measure the actual bottleneck before adding dependencies or native settings. These are runtime investigations; the bundled static validator cannot certify performance.

## Establish comparable measurements

Record the binary/build, web bundle, device, OS/WebView, network state and test data. Compare release-like builds on the same device and repeat scenarios; development React checks, live reload and attached debuggers can change results. Include a supported lower-memory device rather than relying on a desktop browser or simulator.

| Scenario | Evidence to collect |
| --- | --- |
| Cold launch, then warm resume | Time to visible usable UI and the representative action; separate native launch, JS startup, hydration and backend wait |
| Route change or first native feature | Chunk load/parse time, UI delay, bridge operation duration and native presentation |
| Long list, chat stream, keyboard interaction | Main-thread work, dropped frames, DOM growth, repeated rendering/layout |
| Repeated capture/upload and navigation | JS/native memory before and after, retained listeners, buffers and temporary files |
| Background/foreground and poor network | Pending operations, duplicate retries, lost state, sustained CPU/network work |

Agree on app-specific budgets from a baseline; do not invent universal millisecond or memory targets. Use existing instrumentation with sanitized operation IDs and timings, never tokens, chat text, document contents or signed URLs. WebKit Web Inspector can inspect WebView JavaScript/timelines; use platform profilers for native CPU/memory as well. Keep inspection enabled only for authorized development builds. Source: [Web Inspector](https://webkit.org/web-inspector/).

## Startup and code loading

Inspect the actual emitted chunks before changing imports. Defer expensive optional feature code when its startup cost is measurable. A dynamic import can defer a JS wrapper or feature chunk; it does not remove the plugin's native SDK from the binary or guarantee deferred native initialization. Avoid turning every tiny plugin proxy into a loading boundary.

Keep lifecycle handlers needed for cold links, restored results and early notifications registered in time. Mount React lazy components through the existing Suspense/error-boundary design and handle chunk failures visibly. A failed chunk or missing native implementation is not an unsupported-platform success. Do not fetch executable feature chunks from a CDN to bypass the bundled production-artifact boundary. Source: [React lazy](https://react.dev/reference/react/lazy).

If manual splash hiding is already needed, release it after a usable local shell/error screen is ready, with a bounded failure path. Do not introduce `launchAutoHide: false` without a matching lifecycle or wait indefinitely for login/network. Splash hiding and OTA readiness are different decisions; neither should mask a broken launch. See [native UX](native-ux.md) and [SplashScreen](https://capacitorjs.com/docs/apis/splash-screen).

## Bridge traffic, rendering and memory

Measure call frequency, payload size and latency. Coalesce redundant progress/UI updates and batch related operations only when the plugin supports the required semantics. One giant serialized object is not automatically faster, atomic or safe for concurrent updates. Preferences is for small non-sensitive values, not bulk application state; a JS `Promise.all` still makes separate bridge calls. Preserve cancellation, ordering and durable checkpoints.

Avoid persistence or native calls on every streamed token, scroll event or render. Use bounded update frequency where the product tolerates it, and explicitly flush or checkpoint state needed after interruption. Keep critical permission, purchase and auth results unthrottled. For large lists or chat histories, profile before introducing virtualization; preserve accessibility, focus, selection and scroll restoration.

Prefer URI-backed media paths and constrain dimensions/quality to the actual product requirement. A fixed JPEG quality of 80 or width of 1024 is not suitable for every document/photo. Release owned object URLs, buffers and listeners; clean temporary files after their consumers finish, including cancellation paths. Large `blob()`/base64 conversions can multiply memory usage. Follow [native file and transfer rules](native-capabilities.md).

Do not enable Android `largeHeap` as a standard WebView optimization: it is not a leak fix or a guaranteed memory increase. Inspect the merged manifest and renderer before changing hardware acceleration; do not add iOS `UIViewGroupOpacity` as an equivalent acceleration switch. Profile the failing layer and verify visual behavior after any justified setting change. Sources: [Android application attributes](https://developer.android.com/guide/topics/manifest/application-element), [UIViewGroupOpacity](https://developer.apple.com/documentation/bundleresources/information-property-list/uiviewgroupopacity).

## Android release optimization

Enable and validate R8 code/resource optimization for the release variant using the existing compatible toolchain. For the verified AGP 8.13 baseline, the Groovy settings are `minifyEnabled true`, `shrinkResources true` and the default `proguard-android-optimize.txt` plus the app's targeted rules. Merge into the existing build configuration; do not replace its SDK values or copy newer AGP DSL into 8.13. Evaluate optional resource-shrinker changes separately from the initial working conversion.

Inspect plugin consumer rules and reflection/native entry points. Test the optimized release binary's plugin calls, auth return, push and restored-result paths where used; a debug build does not validate them. Retain the exact release mapping file for crash symbolication under the approved artifact policy. Diagnose targeted keep rules rather than adding global keep-all/dontwarn directives. R8 does not optimize the bundled React JavaScript; measure web and native size separately. Source: [R8 optimization, including the pre-9.3 DSL](https://developer.android.com/topic/performance/app-optimization/enable-app-optimization).

Report before/after measurements and the same-device scenarios actually run. Preserve correctness, offline behavior, privacy and energy use; a smaller bundle alone is not proof of a better native experience.
