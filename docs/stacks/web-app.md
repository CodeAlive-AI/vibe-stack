# Web App Stack

This is the default stack for AI-native web applications: SaaS products, dashboards, internal tools, AI workbenches, and customer-facing app surfaces.

## Default

| Layer | Choice | Notes |
| --- | --- | --- |
| Language | TypeScript | Use strict mode. Treat types as agent guardrails, not documentation decoration. |
| Runtime | React | Default UI runtime. |
| Framework | Next.js | Default full-stack app framework. Use App Router unless a legacy constraint says otherwise. |
| Components | Mantine | Default component system for product UI. Start here before creating custom primitives. |
| Styling | Tailwind CSS v4 | Use for layout, spacing, responsive composition, and app-specific visual polish. |
| Accessibility primitives | Radix UI | Exception layer, not default UI kit. Use only when Mantine lacks the required primitive. |
| Animation | Motion | Use for interaction polish and view transitions. Keep animation purposeful. |
| Quality gates | TypeScript strict mode, `tsc`, Ultracite | `tsc` owns type correctness. Ultracite owns lint/format consistency across ESLint, Biome, and Oxlint. |

## Why This Combination

The stack optimizes for a fast product loop with strong defaults:

- Next.js keeps frontend, server routes, rendering, and deployment patterns in one ecosystem.
- Mantine prevents teams from spending early product time rebuilding common product UI.
- Tailwind CSS remains useful for page layout and project-specific composition around Mantine.
- Radix UI is preserved as an escape hatch for custom accessible primitives, not as a competing default.
- Motion gives one animation model instead of ad hoc CSS and library mixing.
- Ultracite gives coding agents a stricter, more consistent lint/format target.

## When Not To Use This Stack

Use a different stack only when the project has a hard constraint:

- Native mobile first: choose a mobile-native stack.
- Static content site only: consider a content-first framework.
- Backend-heavy service with minimal UI: split the backend stack and keep this only for the admin UI.
- Existing product already has a mature design system: use its component library, but keep the quality gates.
