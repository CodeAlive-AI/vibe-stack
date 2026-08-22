# Vibe Infra

Vibe Infra is the default language-independent infrastructure stack for Vibe Stack applications. It covers deployment, database, error tracking, and the minimum observability needed for agent investigation.

## Use This Stack

| Technology | Role | Alternative to |
| --- | --- | --- |
| [Dokploy](https://dokploy.com/) | Self-hosted app deployment without cloud-platform lock-in | [Vercel](https://vercel.com/)-style hosted deployment |
| [PostgreSQL](https://www.postgresql.org/) | Durable relational database with broad tooling and escape hatches like `jsonb` | [Supabase](https://supabase.com/)-style managed Postgres platform |
| [Bugsink](https://www.bugsink.com/) | Lightweight self-hosted error tracking compatible with Sentry SDKs | [Sentry](https://sentry.io/) |
| Structured stdout/stderr logs | Cheapest useful MVP observability through [Docker](https://docs.docker.com/engine/logging/) / [Dokploy](https://dokploy.com/) logs | Heavy log platforms too early |
| [OpenObserve](https://openobserve.ai/) + [OpenTelemetry](https://opentelemetry.io/) | Unified MVP+ logs, metrics, traces, retention, dashboards, and correlation with OTLP ingestion | [Grafana](https://grafana.com/)-style observability stack |
| [OpenObserve AI/LLM observability](https://openobserve.ai/docs/integration/ai/llm-applications/) | Agent and LLM traces with model metadata, token usage, cost, latency, errors, tool calls, retrieval steps, and agent turns | A separate agent-observability backend |

## What Each Choice Means

Dokploy is the default when a project needs a practical self-hosted deployment platform instead of sending the app to a hosted platform like Vercel.

PostgreSQL is the default database. Supabase can still be useful as a hosted product, but Vibe Infra starts from the database itself so the deployment model stays portable.

Bugsink is the default error tracking tool when the project wants a self-hosted Sentry-compatible path. It is compatible with Sentry SDKs, so applications can keep using standard Sentry client instrumentation while sending events to Bugsink.

Structured logs are the default observability baseline for MVPs. Applications should write structured logs to stdout/stderr so Docker and Dokploy can capture them and agents can investigate with log queries.

OpenObserve is the MVP+ observability upgrade. Instrument applications with OpenTelemetry and send logs, metrics, and traces to OpenObserve over OTLP when the project needs retention, dashboards, alerts, and cross-service correlation.

For products with agents or LLM calls, use OpenObserve as the agent observability backend too. Trace the full execution path across model calls, tools, retrieval, workflows, and agent turns; preserve model, token, cost, latency, and error attributes needed to debug behavior and control spend. OpenObserve Online Evaluations can score spans, traces, or sessions with LLM judges or remote scorers, but it is an Enterprise feature and should not be assumed in an OSS deployment.

## Setup Direction For Agents

When preparing infrastructure:

1. Deploy the application through Dokploy.
2. Use PostgreSQL as the primary persistent database.
3. Send application errors to Bugsink.
4. Write structured application logs to stdout/stderr.
5. Use Docker/Dokploy logs as the default investigation surface.
6. Add OpenTelemetry instrumentation and export telemetry to OpenObserve when traces, metrics, retention, dashboards, alerts, or correlation are needed.
7. For agent products, instrument model calls, tool calls, retrieval, workflows, and agent turns, then verify that token usage, cost, latency, model metadata, and errors are queryable in OpenObserve.
8. Add OpenObserve Online Evaluations only when the Enterprise feature is available and continuous quality scoring is a product requirement.
9. Keep secrets in the deployment platform or host secret store. Do not commit them.
10. Document deploy, rollback, log access, backup, restore, and telemetry investigation commands in the project README.

## MVP Logging Baseline

For a typical MVP:

- Log JSON to stdout/stderr.
- Include timestamp, level, message, request id, user or tenant id when safe, job id, route, duration, and error details.
- Do not log secrets, tokens, raw credentials, or sensitive payloads.
- Let Docker/Dokploy capture container output.
- Do not write application logs only to files inside the container.
- Configure log rotation on the host or Docker logging driver so logs do not fill the disk.
- Keep error events in Bugsink for stack traces and issue triage.

This keeps investigation cheap: an agent can start with deploy time, Bugsink events, and Docker/Dokploy logs. If this stops being enough, add OpenTelemetry instrumentation and OpenObserve.

For TypeScript apps, Pino is the default logger. LogLayer can be used later as a wrapper when the project needs a stable logging API across multiple transports, but it is not required for the MVP baseline.

## Minimal Requirements

These are starting points for a strong MVP, not capacity guarantees. Real requirements depend on traffic, build strategy, database size, telemetry volume, and retention.

| Component | Documented or practical minimum | Notes |
| --- | --- | --- |
| Dokploy | 2 GB RAM, 30 GB disk | Official install docs list this to avoid Docker build resource freezes. Ports 80, 443, and 3000 must be available. |
| PostgreSQL | No universal official hardware minimum | PostgreSQL runs on ordinary modern Unix-compatible systems; plan disk from real data size, indexes, WAL, backups, and growth. For Vibe Stack MVPs, avoid tiny DB hosts: start with at least 1-2 vCPU, 2 GB RAM, SSD storage, and backups. |
| Bugsink | 2 GB RAM class server | Bugsink positions itself as a lightweight single-container Sentry-compatible tracker. Its production guide notes workers are well below 100 MiB each and can fit comfortably on a 2 GiB server. |
| Docker/Dokploy logs | Included with the container runtime | The MVP default. Watch disk usage and configure rotation. |
| OpenObserve | No universal documented hardware minimum | The self-hosted quickstart runs as a single binary or container with local storage. Size CPU, memory, disk, retention, and trace sampling from measured ingestion and query load; use the documented HA architecture when one node is no longer sufficient. |

## Minimal Vibe Infra Shape

For a typical low-traffic MVP, use one of these shapes:

| Shape | Minimum | Use when |
| --- | --- | --- |
| Single-server MVP | 2 vCPU, 4 GB RAM, 50-60 GB SSD | App, Dokploy, PostgreSQL, Bugsink, and structured Docker/Dokploy logs. Best starting point when traffic and telemetry are modest. |
| Single-server MVP+ | 4 vCPU, 8 GB RAM, 80-100 GB SSD | Everything above plus single-node OpenObserve with modest telemetry volume and retention. Validate this practical starting point against measured ingestion and query load. |
| Split observability | App host: 2 vCPU, 4 GB RAM, 50-60 GB SSD. Observability host: 2-4 vCPU, 4-8 GB RAM, 50+ GB SSD | You want to isolate OpenObserve ingestion, storage, and queries from the application host. |

OpenObserve usually decides whether the stack fits on a small VPS. Start without it when MVP logs and Bugsink are enough. If telemetry volume grows, reduce retention, sample traces, or move OpenObserve to its own machine before scaling everything else.

## Boundary

This guide does not yet define Kubernetes, cloud-provider-specific infrastructure, or a full production SRE playbook. The default target is a practical self-hosted infrastructure path for small AI-native product teams.

## Sources

- [Dokploy installation requirements](https://docs.dokploy.com/docs/core/installation)
- [PostgreSQL installation requirements](https://www.postgresql.org/docs/current/install-requirements.html)
- [PostgreSQL resource configuration](https://www.postgresql.org/docs/current/runtime-config-resource.html)
- [Bugsink self-hosted Sentry support](https://www.bugsink.com/self-hosted-sentry-support/)
- [Bugsink single server production setup](https://www.bugsink.com/docs/single-server-production/)
- [Docker logging drivers](https://docs.docker.com/engine/logging/configure/)
- [The Twelve-Factor App: Logs](https://12factor.net/logs)
- [Pino documentation](https://getpino.io/)
- [LogLayer](https://github.com/loglayer/loglayer)
- [OpenTelemetry JavaScript logs](https://opentelemetry.io/docs/languages/js/instrumentation/#logs)
- [OpenObserve self-hosted quickstart](https://openobserve.ai/docs/getting-started/)
- [OpenObserve architecture and deployment modes](https://openobserve.ai/docs/architecture/)
- [OpenObserve OTLP ingestion](https://openobserve.ai/docs/ingestion/logs/otlp/)
- [OpenObserve LLM applications](https://openobserve.ai/docs/integration/ai/llm-applications/)
- [OpenObserve AI framework integrations](https://openobserve.ai/docs/integration/ai/frameworks/)
- [OpenObserve LLM evaluations](https://openobserve.ai/docs/integration/ai/llm-evaluations/)
