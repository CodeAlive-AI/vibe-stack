# Web Application

Status: covered.

This is the current default for AI-native web apps: product apps, dashboards, internal tools, AI workbenches, and apps with agent features.

## Use This Stack

| Technology | Role |
| --- | --- |
| TypeScript | Main language |
| pnpm | Package manager |
| React | UI runtime |
| Next.js | App framework |
| Mastra | Agent workflows and agent features |
| assistant-ui | AI chat and assistant UI layer |
| Better Auth | Authentication |
| Prisma | Type-safe PostgreSQL data access |
| Zod | Runtime validation, schemas, and environment validation |
| Pino | Structured JSON logging to stdout |
| Mantine | UI kit |
| Tailwind CSS v4 | Styling |
| Ultracite + Oxlint | Linting and formatting |
| Motion | Animation |

## Setup Direction For Agents

When starting a new web app:

1. Start from a Next.js TypeScript project.
2. Use pnpm as the package manager.
3. Add Mantine for UI.
4. Add Tailwind CSS v4 for styling.
5. Add Mastra when the app needs agent workflows, tools, memory, or model orchestration.
6. Add assistant-ui when the app needs chat, assistant, copilot, or agent-facing UI.
7. Add Better Auth when the app needs users, sessions, social login, organizations, 2FA, passkeys, or other auth features.
8. Use PostgreSQL from Vibe Infra as the default application database.
9. Add Prisma for type-safe database access to PostgreSQL.
10. Add Zod for input validation, shared schemas, and startup config validation.
11. Add Pino for structured JSON logs to stdout.
12. Add Ultracite with Oxlint for linting and formatting.
13. Add Motion only when the UI needs animation.
14. Use Vibe Infra when the app needs deployment, database, error tracking, and observability defaults.

## Boundary

This guide does not choose a standalone backend framework yet. If the app needs backend code today, keep it inside the Next.js project unless a project-specific constraint requires otherwise.

Ultracite supports multiple toolchains. Vibe Stack's default is Ultracite with Oxlint because it gives a fast, opinionated linting and formatting path while preserving a simple setup.

Create T3 App is a useful reference for full-stack TypeScript defaults. Vibe Stack borrows the emphasis on type safety, Prisma, and Zod, but does not make tRPC or NextAuth.js defaults yet: Better Auth owns auth, and the API boundary remains project-specific until a single stronger default is selected.

PostgreSQL + Prisma should be used as a structured core with flexible edges. Model stable entities, relations, uniqueness, and timestamps in Prisma; use PostgreSQL `jsonb` for unstable metadata, provider payloads, and experimental fields. Do not use `jsonb` as a substitute for the whole product model.

assistant-ui is the default AI UI layer for chat, assistant, copilot, and agent-facing interfaces. Use it with Mastra when the product needs a production-ready agent UI instead of building chat primitives from scratch.

Sources: [Create T3 App](https://create.t3.gg/), [pnpm](https://pnpm.io/), [assistant-ui](https://www.assistant-ui.com/), [assistant-ui Mastra integration](https://www.assistant-ui.com/docs/integrations/frameworks/mastra/overview), [Prisma](https://www.prisma.io/docs), [Zod](https://zod.dev/), [Pino](https://getpino.io/).

LogLayer is worth considering when the project outgrows direct Pino usage and needs one logging API that can switch or combine transports. Keep Pino direct for the default MVP path.
