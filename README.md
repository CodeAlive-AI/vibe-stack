# Vibe Stack

Verified AI-native development stack with one recommended choice for the common case.

This repo is not an awesome-list. It is a small knowledge base that a human or coding agent can read and use to choose the default stack, set up a project, or find the right template.

## Current Coverage

| Area | Status | Guide |
| --- | --- | --- |
| TypeScript | Covered for web applications | [docs/languages/typescript.md](docs/languages/typescript.md) |
| Web application | Covered | [docs/web-app.md](docs/web-app.md) |
| Vibe Deploy | Covered | [docs/vibe-deploy.md](docs/vibe-deploy.md) |
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
| UI kit | Mantine |
| Styling | Tailwind CSS v4 |
| Code quality | TypeScript strict mode + Ultracite |
| Animation | Motion |

Radix UI is not the default. Use it only when Mantine cannot cover a required primitive.

## Recommended Deploy Stack

Use this for deployment:

| Need | Choice |
| --- | --- |
| Deployment platform | Dokploy |
| Database | PostgreSQL |
| Error tracking | Bugsink |
| Observability | SigNoz |

## Repository Structure

```text
vibe-stack/
├── README.md
├── stack.yaml
├── docs/
│   ├── languages/
│   │   └── typescript.md
│   ├── web-app.md
│   └── vibe-deploy.md
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
- [Mastra](https://mastra.ai/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [Dokploy](https://dokploy.com/)
- [Bugsink](https://github.com/bugsink/bugsink)
- [SigNoz](https://signoz.io/docs/)
