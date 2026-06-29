# Vibe Stack

The optimal default stack for AI-native products.

A curated set of self-hostable, production-ready technologies that covers the common 95% of product use cases without forcing teams or agents to compare equivalent alternatives.

This is an opinionated gentleman's kit for building modern products with AI agents: one strong default choice for each common need.

## Current Coverage

| Area | Status | Guide |
| --- | --- | --- |
| TypeScript | Covered for web applications | [docs/languages/typescript.md](docs/languages/typescript.md) |
| Web application | Covered | [docs/web-app.md](docs/web-app.md) |
| Vibe Infra | Covered | [docs/vibe-infra.md](docs/vibe-infra.md) |
| Python | Planned | Not selected yet |
| .NET | Planned | Not selected yet |
| Backend-only stacks | Planned | Not selected yet |

## Recommended Web App Stack

Use this for a new AI-native web application:

| Need | Choice |
| --- | --- |
| Language | TypeScript |
| UI runtime | React |
| App framework | Next.js |
| Agent features | Mastra |
| Authentication | Better Auth |
| UI kit | Mantine |
| Styling | Tailwind CSS v4 |
| Code quality | TypeScript strict mode + Ultracite + Oxlint |
| Animation | Motion |

Radix UI is not the default. Use it only when Mantine cannot cover a required primitive.

## Recommended Infra Stack

Use this for deployment, database, error tracking, and observability:

| Need | Choice | Alternative to |
| --- | --- | --- |
| Deployment platform | Dokploy | Vercel-style hosted deployment |
| Database | PostgreSQL | Supabase-style managed Postgres platform |
| Error tracking | Bugsink | Sentry, compatible with Sentry SDKs |
| Observability | SigNoz | Grafana-style observability stack |

SigNoz is based on OpenTelemetry and is the default place for traces, metrics, and logs.

## Repository Structure

```text
vibe-stack/
├── README.md
├── stack.yaml
├── docs/
│   ├── languages/
│   │   └── typescript.md
│   ├── web-app.md
│   └── vibe-infra.md
└── templates/
    └── README.md
```

## How Agents Should Use This Repo

1. Read `README.md` for the current supported scenarios.
2. Read `stack.yaml` for the machine-readable defaults.
3. Read the relevant guide in `docs/`.
4. Use `templates/` when templates are added.

Do not ask the user to choose between equivalent alternatives unless the repo marks that area as not selected yet.

## Sources

The initial stack was checked against official project pages and docs on 2026-06-29:

- [React](https://react.dev/)
- [Next.js](https://nextjs.org/docs)
- [Mantine](https://mantine.dev/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Radix UI](https://www.radix-ui.com/primitives)
- [Motion](https://motion.dev/)
- [Ultracite](https://www.ultracite.ai/)
- [Oxlint](https://oxc.rs/docs/guide/usage/linter.html)
- [Mastra](https://mastra.ai/)
- [Better Auth](https://www.better-auth.com/docs)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [Dokploy](https://dokploy.com/)
- [Bugsink](https://github.com/bugsink/bugsink)
- [SigNoz](https://signoz.io/docs/)
- [OpenTelemetry](https://opentelemetry.io/docs/)
