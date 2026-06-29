# Vibe Stack

Opinionated, production-minded technology stack for AI-native software development.

The goal is not to list every good tool. The goal is to keep one verified default choice per layer that covers roughly 95% of product work, so teams and coding agents can start from a strong baseline without decision fatigue.

## Default Stack

| Layer | Default choice | Why |
| --- | --- | --- |
| Primary language | TypeScript | Best current fit for full-stack web, AI SDKs, tooling, and agent-written code reviewability. |
| Web app framework | Next.js on React | Mature full-stack React baseline with routing, server rendering, API routes, and deployment support. |
| UI components | Mantine | Complete component system that reduces design-system work for product apps. |
| Styling | Tailwind CSS v4 | Utility styling for layout, spacing, and app-specific polish around the component system. |
| Accessibility primitives | Radix UI, exception only | Use when Mantine does not expose a needed primitive or when building a custom component system. |
| Animation | Motion | Default animation layer for React UI transitions and micro-interactions. |
| Code quality | TypeScript strict mode + Ultracite | `tsc` remains the type gate; Ultracite standardizes linting and formatting around ESLint, Biome, and Oxlint. |
| Agent framework | Mastra | TypeScript-native agent framework for workflows, tools, memory, and eval-oriented agent work. |
| Database | PostgreSQL | Durable default relational database; start here unless there is a hard reason not to. |
| Deployment | Dokploy | Self-hosted deployment control plane for small teams and AI-native apps. |
| Error tracking | Bugsink | Self-hosted Sentry-compatible error tracking default for apps that need ownership and low ops overhead. |
| Observability | SigNoz | OpenTelemetry-native traces, metrics, and logs in one product. |

## Repository Map

```text
vibe-stack/
├── stack.yaml                 # Machine-readable canonical choices
├── docs/
│   ├── principles.md          # Selection rules and anti-goals
│   ├── selection-rubric.md    # How tools are admitted, replaced, or rejected
│   ├── stacks/
│   │   ├── web-app.md         # Default AI-native web app stack
│   │   └── agent-app.md       # Agent and workflow stack
│   ├── deploy/
│   │   └── vibe-deploy.md     # Deployment, database, errors, observability
│   ├── decisions/             # Stable decision records
│   └── radar/                 # Considered alternatives and exceptions
└── templates/
    └── README.md              # Future starter templates
```

## How To Use

Start with the default stack. Deviate only when a specific project constraint beats the baseline, and record that exception in the project README or in `docs/radar/`.

The default is intentionally narrow. A useful stack is a decision engine, not a catalog.

## Sources

The initial stack was checked against the official project pages and docs on 2026-06-29:

- [React](https://react.dev/)
- [Next.js](https://nextjs.org/docs)
- [Mantine](https://mantine.dev/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Radix UI](https://www.radix-ui.com/primitives)
- [Motion](https://motion.dev/)
- [Ultracite](https://www.ultracite.ai/)
- [Mastra](https://mastra.ai/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [Dokploy](https://dokploy.com/)
- [Bugsink](https://github.com/bugsink/bugsink)
- [SigNoz](https://signoz.io/docs/)
