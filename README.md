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
| Data access | [Drizzle ORM](https://orm.drizzle.team/) + [PostgreSQL](https://www.postgresql.org/) |
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
| MVP+ observability | [OpenObserve](https://openobserve.ai/) + [OpenTelemetry](https://opentelemetry.io/) | [Grafana](https://grafana.com/)-style observability stack |
| Agent observability | [OpenObserve AI/LLM observability](https://openobserve.ai/docs/integration/ai/llm-applications/) | A separate agent-observability backend |

Start with structured logs and Bugsink. Add OpenTelemetry + OpenObserve when traces, metrics, retention, and correlation become worth the extra resources. For agent products, send model, tool, retrieval, workflow, and agent-turn spans to the same OpenObserve backend; its built-in Online Evaluations are an optional Enterprise feature.

> **Full guides**
> Detailed docs: [Web application](docs/web-app.md), [TypeScript](docs/languages/typescript.md), [Vibe Infra](docs/vibe-infra.md), [Security Practices](docs/security-practices.md), and [Common guide](docs/common-guide.md).

## Coverage

| Area | Status |
| --- | --- |
| TypeScript web apps | Covered |
| Vibe Infra | Covered |
| Common agent-ready practices | Covered |
| Security practices | Covered |
| Existing web apps to iOS/Android | [Capacitor 8.5 agent skill](skills/agentic-capacitor/README.md) |
| Python | Planned, not selected yet |
| .NET | Planned, not selected yet |
| Backend-only stacks | Planned, not selected yet |

## Agent Skills

[agentic-capacitor](skills/agentic-capacitor/README.md) helps agents add Capacitor 8.5 to an existing web app, especially React 19.2, maintain iOS/Android integrations, and prepare for a later Capacitor 9 upgrade. It preserves the existing web architecture and includes offline validation scripts.

See the [skill README](skills/agentic-capacitor/README.md) for installation, example requests, validation commands, and coverage limits.

## For Agents

Use this repo as a decision shortcut, not as a comparison catalog.

1. Read this README first.
2. Open the relevant guide for the project type:

- [TypeScript](docs/languages/typescript.md)
- [Web application](docs/web-app.md)
- [Vibe Infra](docs/vibe-infra.md)
- [Security Practices](docs/security-practices.md)
- [Common guide](docs/common-guide.md)
- [Agent skills](skills/README.md)
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
