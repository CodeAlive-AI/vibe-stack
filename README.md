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
| UI | React + Next.js |
| Agents | Mastra |
| Auth | Better Auth |
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
| Observability | SigNoz | Grafana-style observability stack |

SigNoz is based on OpenTelemetry and is the default place for traces, metrics, and logs.

## Coverage

| Area | Status |
| --- | --- |
| TypeScript web apps | Covered |
| Vibe Infra | Covered |
| Python | Planned, not selected yet |
| .NET | Planned, not selected yet |
| Backend-only stacks | Planned, not selected yet |

## For Agents

Read [stack.yaml](stack.yaml) first, then the relevant guide:

- [TypeScript](docs/languages/typescript.md)
- [Web application](docs/web-app.md)
- [Vibe Infra](docs/vibe-infra.md)
- [Roadmap](ROADMAP.md)

Do not ask users to choose between equivalent alternatives when this repo already names a default.

## Contributions

Pull requests are welcome for better recommended defaults across languages, app types, infrastructure, observability, auth, deployment, and templates.

The bar is intentionally high: recommendations should stay small, useful, proven, production-ready, and self-hosted first whenever possible. See [CONTRIBUTION.md](CONTRIBUTION.md).
