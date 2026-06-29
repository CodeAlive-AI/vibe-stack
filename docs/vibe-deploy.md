# Vibe Deploy

Status: covered.

Vibe Deploy is the current default deployment profile for Vibe Stack applications.

## Use This Stack

| Technology | Role |
| --- | --- |
| Dokploy | Deployment platform |
| PostgreSQL | Primary database |
| Bugsink | Error tracking |
| SigNoz | Observability |

## Setup Direction For Agents

When preparing deployment:

1. Deploy the application through Dokploy.
2. Use PostgreSQL as the primary persistent database.
3. Send application errors to Bugsink.
4. Send traces, metrics, and logs to SigNoz.
5. Keep secrets in the deployment platform or host secret store. Do not commit them.
6. Document deploy, rollback, backup, and restore commands in the project README.

## Boundary

This guide does not yet define Kubernetes, cloud-provider-specific infrastructure, or a full production SRE playbook. The default target is a practical self-hosted deployment path for small AI-native product teams.
