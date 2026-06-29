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

## Boundary

This guide does not yet define Kubernetes, cloud-provider-specific infrastructure, or a full production SRE playbook. The default target is a practical self-hosted infrastructure path for small AI-native product teams.
