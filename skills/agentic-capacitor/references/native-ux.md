# Native UX without a framework rewrite

## System bars and insets

Use `SystemBars` from `@capacitor/core` for modern edge-to-edge UI. It has `setStyle`, `show`, and `hide`, with optional singular `bar`; there is no `setVisible` API. Example:

```ts
import { SystemBars, SystemBarsStyle, SystemBarType } from '@capacitor/core';
await SystemBars.setStyle({
  style: SystemBarsStyle.Dark,
  bar: SystemBarType.StatusBar,
});
```

`Dark` means light foreground content on a dark background; check contrast with the app theme. iOS needs controller-based status bar appearance. Assign one owner per bar; avoid fighting calls from legacy StatusBar and SystemBars.

Capacitor injects inset CSS variables for affected older Android WebViews. Keep `SystemBars.insetsHandling` at `css` unless replacing that behavior intentionally. Example for the single chosen layout boundary:

```css
.app-shell {
  padding-top: var(--safe-area-inset-top, env(safe-area-inset-top, 0px));
  padding-right: var(--safe-area-inset-right, env(safe-area-inset-right, 0px));
  padding-bottom: var(--safe-area-inset-bottom, env(safe-area-inset-bottom, 0px));
  padding-left: var(--safe-area-inset-left, env(safe-area-inset-left, 0px));
}
```

Use `viewport-fit=cover`. Do not pad html, root, shell and fixed footer with the same inset. Portal dialogs and toasts may need their own boundary; verify placement. Do not add a third-party inset plugin by default. Source: [SystemBars](https://capacitorjs.com/docs/apis/system-bars).

The stable 8.x line already corrected several bar/inset behaviors, including older Android API levels, independent bar targeting and disabled inset handling. On 8.5, verify the actual binary before retaining workarounds written for early 8.0: remove a workaround only after reproducing its effect and confirming the native behavior replaces it. Prefer CSS/layout correctness over obsolete margin flags or hard-coded device offsets. Source: [8.4.0 fixes](https://github.com/ionic-team/capacitor/releases/tag/8.4.0).

## Keyboard and layout

Start with the app's current scroll/container model. Choose keyboard resize behavior for that model and the platform; `body`, `native`, and `none` are not interchangeable fixes. Test focus near the bottom, multiline chat composers, input accessory behavior, modals, orientation, and keyboard dismissal. Avoid double compensation from OS resizing plus JS keyboard height plus safe-area padding. Observe visual viewport changes when needed, with cleanup and bounded updates. Source: [Keyboard](https://capacitorjs.com/docs/apis/keyboard).

## App polish and launch

Build a WebView support matrix from the app's minimum iOS version and supported Android System WebView versions. A Capacitor native minimum does not prove that the existing CSS framework, JavaScript output, media codecs or web APIs run there. Test the oldest supported runtime as well as the current release, including route/chunk loading, text input and memory pressure. Use explicit capability checks or a justified minimum-version change when a required feature is unavailable; do not silently render a broken screen.

Keep established navigation and styling; native usefulness comes from correct interactions, not mandatory tabs or a new component library. Test touch targets, text scaling, screen readers, reduced motion, selection, and dark mode. Avoid desktop hover-only actions.

Generate icons/splash assets only from the user's approved artwork and with an inspected, pinned compatible asset tool. Scope generation to intended targets and inspect changes. A launch splash must not wait indefinitely for auth/network: render a usable loading/error screen and release the splash through a bounded path. Do not fabricate successful initialization to hide a startup failure.

Modern Apple system appearance does not convert a React DOM layout into native UIKit/SwiftUI controls. Review iOS/iPadOS 26 system sheets, native navigation surfaces and light/dark/tinted/clear icon variants without forcing a UI rewrite or glass effects onto every web element. Use current Xcode/Icon Composer support when the product needs layered icons, preserving compatible assets for older targets. Validate VoiceOver/TalkBack, text zoom, reduce motion/transparency and contrast in the actual WebView. Sources: [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass), [Icon Composer](https://developer.apple.com/documentation/xcode/creating-your-app-icon-using-icon-composer).

Sources: [Splash screens and icons](https://capacitorjs.com/docs/guides/splash-screens-and-icons), [SplashScreen API](https://capacitorjs.com/docs/apis/splash-screen).
