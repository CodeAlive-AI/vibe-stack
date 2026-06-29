# Vibe Stack

![Vibe Stack cover](assets/vibe-stack-cover.png)

**The optimal default stack for AI-native products.**

Vibe Stack is an opinionated gentleman's kit: a curated set of self-hostable, production-ready technologies that covers the common 95% of product use cases without forcing teams or agents to compare equivalent alternatives.

It is designed for both a smooth fast start and long-running autonomous development and maintenance through AI agents.

## Defaults

### Web Application

| Need | Default |
| --- | --- |
| Language | TypeScript |
| Package manager | pnpm |
| UI | React + Next.js |
| Agents | Mastra |
| AI UI layer | assistant-ui |
| Auth | Better Auth |
| Data access | Prisma + PostgreSQL |
| Validation | Zod |
| Logging | Pino JSON logs to stdout |
| Components | Mantine |
| Styling | Tailwind CSS v4 |
| Quality | TypeScript strict mode + Ultracite + Oxlint |
| Motion | Motion |

### Vibe Infra

| Need | Default | Replaces |
| --- | --- | --- |
| Deployment | Dokploy | Vercel-style hosted deployment |
| Database | PostgreSQL | Supabase-style managed Postgres platform |
| Error tracking | Bugsink | Sentry; compatible with Sentry SDKs |
| MVP observability | Structured stdout/stderr logs via Docker/Dokploy | Heavy log platforms too early |
| MVP+ observability | OpenTelemetry + SigNoz | Grafana-style observability stack |

Start with structured logs and Bugsink. Add OpenTelemetry + SigNoz when traces, metrics, retention, and correlation become worth the extra resources.

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

Read this README first, then the relevant guide:

- [TypeScript](docs/languages/typescript.md)
- [Web application](docs/web-app.md)
- [Vibe Infra](docs/vibe-infra.md)
- [Common guide](docs/common-guide.md)
- [Roadmap](ROADMAP.md)

Do not ask users to choose between equivalent alternatives when this repo already names a default.

## Contributions

Pull requests are welcome for better recommended defaults across languages, app types, infrastructure, observability, auth, deployment, and templates.

The bar is intentionally high: recommendations should stay small, useful, proven, production-ready, and self-hosted first whenever possible. See [CONTRIBUTING.md](CONTRIBUTING.md).
