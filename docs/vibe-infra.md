# Vibe Infra

Status: covered.

Vibe Infra is the default language-independent infrastructure stack for Vibe Stack applications. It covers deployment, database, error tracking, and observability.

## Use This Stack

| Technology | Role | Alternative to |
| --- | --- | --- |
| Dokploy | Deployment platform | Vercel-style hosted deployment |
| PostgreSQL | Primary database | Supabase-style managed Postgres platform |
| Bugsink | Error tracking compatible with Sentry SDKs | Sentry |
| SigNoz | Observability based on OpenTelemetry | Grafana-style observability stack |

## What Each Choice Means

Dokploy is the default when a project needs a practical self-hosted deployment platform instead of sending the app to a hosted platform like Vercel.

PostgreSQL is the default database. Supabase can still be useful as a hosted product, but Vibe Infra starts from the database itself so the deployment model stays portable.

Bugsink is the default error tracking tool when the project wants a self-hosted Sentry-compatible path. It is compatible with Sentry SDKs, so applications can keep using standard Sentry client instrumentation while sending events to Bugsink.

SigNoz is the default observability tool. It is based on OpenTelemetry and should receive traces, metrics, and logs.

## Setup Direction For Agents

When preparing infrastructure:

1. Deploy the application through Dokploy.
2. Use PostgreSQL as the primary persistent database.
3. Send application errors to Bugsink.
4. Send traces, metrics, and logs to SigNoz through OpenTelemetry.
5. Keep secrets in the deployment platform or host secret store. Do not commit them.
6. Document deploy, rollback, backup, and restore commands in the project README.

## Minimal Requirements

These are starting points for a strong MVP, not capacity guarantees. Real requirements depend on traffic, build strategy, database size, telemetry volume, and retention.

| Component | Documented or practical minimum | Notes |
| --- | --- | --- |
| Dokploy | 2 GB RAM, 30 GB disk | Official install docs list this to avoid Docker build resource freezes. Ports 80, 443, and 3000 must be available. |
| PostgreSQL | No universal official hardware minimum | PostgreSQL runs on ordinary modern Unix-compatible systems; plan disk from real data size, indexes, WAL, backups, and growth. For Vibe Stack MVPs, avoid tiny DB hosts: start with at least 1-2 vCPU, 2 GB RAM, SSD storage, and backups. |
| Bugsink | 2 GB RAM class server | Bugsink positions itself as a lightweight single-container Sentry-compatible tracker. Its production guide notes workers are well below 100 MiB each and can fit comfortably on a 2 GiB server. |
| SigNoz | 4 GB memory allocated to Docker | Official Docker standalone docs require Docker Engine 20.10+, Docker Compose v2, and at least 4 GB Docker memory. SigNoz is the heaviest component because it stores and queries telemetry. |

## Minimal Vibe Infra Shape

For a typical low-traffic MVP, use one of these shapes:

| Shape | Minimum | Use when |
| --- | --- | --- |
| Single-server MVP | 4 vCPU, 8 GB RAM, 80-100 GB SSD | Everything runs on one VPS: app, Dokploy, PostgreSQL, Bugsink, and SigNoz with modest telemetry retention. |
| Cheaper split | App host: 2 vCPU, 4 GB RAM, 50-60 GB SSD. Observability host: 2-4 vCPU, 4-8 GB RAM, 50+ GB SSD | You want to keep the application host small and isolate SigNoz. |
| No local SigNoz yet | 2 vCPU, 4 GB RAM, 50-60 GB SSD | Early MVP where logs and Bugsink are enough temporarily. Add SigNoz when runtime debugging needs traces/metrics. |

SigNoz usually decides whether the stack fits on a small VPS. If telemetry volume grows, reduce retention, sample traces, or move SigNoz to its own machine before scaling everything else.

## Boundary

This guide does not yet define Kubernetes, cloud-provider-specific infrastructure, or a full production SRE playbook. The default target is a practical self-hosted infrastructure path for small AI-native product teams.

## Sources

- [Dokploy installation requirements](https://docs.dokploy.com/docs/core/installation)
- [PostgreSQL installation requirements](https://www.postgresql.org/docs/current/install-requirements.html)
- [PostgreSQL resource configuration](https://www.postgresql.org/docs/current/runtime-config-resource.html)
- [Bugsink self-hosted Sentry support](https://www.bugsink.com/self-hosted-sentry-support/)
- [Bugsink single server production setup](https://www.bugsink.com/docs/single-server-production/)
- [SigNoz Docker standalone install](https://signoz.io/docs/install/docker/)
