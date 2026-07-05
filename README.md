# Vibe Stack

![Vibe Stack cover](assets/vibe-stack-cover.png)

**The optimal default stack for AI-native products.**

Vibe Stack is an opinionated gentleman's kit: a curated set of self-hostable, production-ready technologies that covers the common 95% of product use cases without forcing teams or agents to compare equivalent alternatives.

It is designed for both a smooth fast start and long-running autonomous development and maintenance through AI agents.

## Defaults

### Web Application

| Need | Default |
| --- | --- |
| Language | [TypeScript](https://www.typescriptlang.org/) |
| Package manager | [pnpm](https://pnpm.io/) |
| UI | [React](https://react.dev/) + [Next.js](https://nextjs.org/) |
| Agents | [Mastra](https://mastra.ai/) |
| AI UI layer | [assistant-ui](https://www.assistant-ui.com/) |
| Auth | [Better Auth](https://www.better-auth.com/) |
| Data access | [Prisma](https://www.prisma.io/) + [PostgreSQL](https://www.postgresql.org/) |
| Validation | [Zod](https://zod.dev/) |
| Logging | [Pino](https://getpino.io/) JSON logs to stdout |
| Components | [Mantine](https://mantine.dev/) |
| Styling | [Tailwind CSS v4](https://tailwindcss.com/) |
| Quality | TypeScript strict mode + [Ultracite](https://www.ultracite.ai/) + [Oxlint](https://oxc.rs/docs/guide/usage/linter.html) |
| Animation | [Motion](https://motion.dev/) |

### Vibe Infra

| Need | Default | Replaces |
| --- | --- | --- |
| Deployment | [Dokploy](https://dokploy.com/) | [Vercel](https://vercel.com/)-style hosted deployment |
| Database | [PostgreSQL](https://www.postgresql.org/) | [Supabase](https://supabase.com/)-style managed Postgres platform |
| Error tracking | [Bugsink](https://www.bugsink.com/) | [Sentry](https://sentry.io/); compatible with Sentry SDKs |
| MVP observability | Structured stdout/stderr logs via [Docker](https://docs.docker.com/engine/logging/) / [Dokploy](https://dokploy.com/) | Heavy log platforms too early |
| MVP+ observability | [OpenTelemetry](https://opentelemetry.io/) + [SigNoz](https://signoz.io/) | [Grafana](https://grafana.com/)-style observability stack |

Start with structured logs and Bugsink. Add OpenTelemetry + SigNoz when traces, metrics, retention, and correlation become worth the extra resources.

> **Full guides**
> Detailed docs: [Web application](docs/web-app.md), [TypeScript](docs/languages/typescript.md), [Vibe Infra](docs/vibe-infra.md), and [Common guide](docs/common-guide.md).

## Coverage

| Area | Status |
| --- | --- |
| TypeScript web apps | Covered |
| Vibe Infra | Covered |
| Common agent-ready practices | Covered |
| Python | Planned, not selected yet |
| .NET | Planned, not selected yet |
| Backend-only stacks | Planned, not selected yet |

## For Agents

Use this repo as a decision shortcut, not as a comparison catalog.

1. Read this README first.
2. Open the relevant guide for the project type:

- [TypeScript](docs/languages/typescript.md)
- [Web application](docs/web-app.md)
- [Vibe Infra](docs/vibe-infra.md)
- [Common guide](docs/common-guide.md)
- [Roadmap](ROADMAP.md)

Rules:

- Use the named default unless the project has a concrete constraint that makes it wrong.
- Do not ask users to choose between equivalent alternatives when this repo already names a default.
- Do not add a second equivalent tool just because it is popular.
- Prefer self-hostable, production-ready tools with a low operational burden.
- Keep MVP choices simple: choose the smallest stack that supports fast feedback, clear errors, and autonomous maintenance.
- When deviating from a default, write down the reason in the project docs or implementation notes.
- If a category is not covered yet, make the smallest reversible choice and mark it as project-specific.

## Contributions

Pull requests are welcome for better recommended defaults across languages, app types, infrastructure, observability, auth, deployment, and templates.

The bar is intentionally high: recommendations should stay small, useful, proven, production-ready, and self-hosted first whenever possible. See [CONTRIBUTING.md](CONTRIBUTING.md).
