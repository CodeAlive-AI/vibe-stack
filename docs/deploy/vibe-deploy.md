# Vibe Deploy

Vibe Deploy is the default deployment and observability profile for Vibe Stack web and agent applications.

## Default Profile

| Layer | Choice | Responsibility |
| --- | --- | --- |
| Deployment platform | Dokploy | Build, deploy, and operate apps on owned infrastructure. |
| Database | PostgreSQL | Primary durable relational data store. |
| Error tracking | Bugsink | Self-hosted Sentry-compatible error collection. |
| Observability | SigNoz | OpenTelemetry-native traces, metrics, and logs. |

## Target Use Case

Use this profile for small teams and AI-native projects that want:

- A deployment path that can be automated by agents.
- Ownership of runtime infrastructure.
- A default relational database.
- Error reporting without committing to a hosted-only vendor.
- OpenTelemetry-based observability from the start.

## Minimal Production Checklist

- Application deploys through Dokploy from the repository.
- PostgreSQL is provisioned with backups enabled.
- Runtime secrets are stored in the deployment platform or host secret store, never committed.
- Bugsink receives backend and frontend exceptions.
- SigNoz receives traces, logs, and service-level metrics.
- Health checks are exposed for the app and background workers.
- Deploy, rollback, migration, and backup restore steps are documented in the project README.

## Boundaries

Bugsink and SigNoz are complementary:

- Bugsink owns exception triage and Sentry-compatible error workflows.
- SigNoz owns distributed observability through traces, metrics, and logs.

Do not use both to track the same signal unless the duplication is intentional and documented.

## Open Questions

- Standard Docker Compose baseline for Dokploy-hosted templates.
- Default OpenTelemetry SDK setup for Next.js and Mastra.
- Recommended PostgreSQL backup provider and restore drill.
- Default alert thresholds for small production apps.
