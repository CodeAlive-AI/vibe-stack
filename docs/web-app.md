# Web Application

This is the current default for AI-native web apps: product apps, dashboards, internal tools, AI workbenches, and apps with agent features.

## Use This Stack

| Technology | Role |
| --- | --- |
| [TypeScript](https://www.typescriptlang.org/) | Main language with strict static types |
| [pnpm](https://pnpm.io/) | Fast, strict, disk-efficient package manager |
| [React](https://react.dev/) | UI runtime with the strongest ecosystem |
| [Next.js](https://nextjs.org/) | Full-stack React framework with routing, rendering, and build defaults |
| [Mastra](https://mastra.ai/) | TypeScript agent framework for workflows, tools, memory, and model orchestration |
| [Mastra Memory](https://mastra.ai/docs/memory/overview) + [`@mastra/pg`](https://mastra.ai/docs/storage) | Persistent conversation and user memory backed by PostgreSQL when agents need state across interactions |
| [assistant-ui](https://www.assistant-ui.com/) | AI chat and assistant UI layer focused on production-grade UX |
| [Better Auth](https://www.better-auth.com/) | App-local auth with database-backed sessions, plugins, and advanced auth features |
| [Drizzle ORM](https://orm.drizzle.team/) + [Drizzle Kit](https://orm.drizzle.team/docs/kit-overview) | SQL-like, type-safe PostgreSQL access with TypeScript schemas and generated SQL migrations |
| [Zod](https://zod.dev/) | TypeScript-first runtime validation for inputs, schemas, and startup config |
| [Pino](https://getpino.io/) | Low-overhead structured JSON logging to stdout |
| [Mantine](https://mantine.dev/) | Complete accessible React component kit for fast product UI |
| [Tailwind CSS v4](https://tailwindcss.com/) | Utility styling for fast custom UI without leaving markup |
| [Ultracite](https://www.ultracite.ai/) + [Oxlint](https://oxc.rs/docs/guide/usage/linter.html) | Opinionated AI-friendly code quality with fast linting |
| [Motion](https://motion.dev/) | Production-grade React animation, previously Framer Motion |

## Setup Direction For Agents

When starting a new web app:

1. Start from a Next.js TypeScript project.
2. Use pnpm as the package manager.
3. Add Mantine for UI.
4. Add Tailwind CSS v4 for styling.
5. Add Mastra when the app needs agent workflows, tools, memory, or model orchestration.
6. Add Mastra Memory when an agent needs multi-turn history, persistent user preferences, or context across sessions. Skip it for stateless and single-turn agents; use `@mastra/pg` with PostgreSQL for production persistence.
7. Add assistant-ui when the app needs chat, assistant, copilot, or agent-facing UI.
8. Add Better Auth when the app needs users, sessions, social login, organizations, 2FA, passkeys, or other auth features.
9. Use PostgreSQL from Vibe Infra as the default application database.
10. Add Drizzle ORM for type-safe, SQL-like PostgreSQL access and Drizzle Kit for schema migrations. Generate and review SQL migrations before applying them in production.
11. Add Zod for input validation, shared schemas, and startup config validation.
12. Add Pino for structured JSON logs to stdout.
13. Add Ultracite with Oxlint for linting and formatting.
14. Add Motion only when the UI needs animation.
15. Use Vibe Infra when the app needs deployment, database, error tracking, and observability defaults.

## Boundary

This guide does not choose a standalone backend framework yet. If the app needs backend code today, keep it inside the Next.js project unless a project-specific constraint requires otherwise.

Ultracite supports multiple toolchains. Vibe Stack's default is Ultracite with Oxlint because it gives a fast, opinionated linting and formatting path while preserving a simple setup.

Create T3 App is a useful reference for full-stack TypeScript defaults. Vibe Stack borrows its emphasis on end-to-end type safety, but selects Better Auth for auth and Drizzle for PostgreSQL access. Add tRPC when a client-heavy application benefits from a typed query and mutation layer across the client-server boundary, or when multiple TypeScript clients share the same internal API. Prefer direct server calls, Server Actions, and Route Handlers for simpler Next.js applications; do not use tRPC as the default public or polyglot API contract.

PostgreSQL + Drizzle should be used as a structured core with flexible edges. Model stable entities, relations, constraints, and timestamps in the Drizzle schema; use PostgreSQL `jsonb` for unstable metadata, provider payloads, and experimental fields. Do not use `jsonb` as a substitute for the whole product model.

Mastra Memory is the default memory implementation for stateful Mastra agents, not a requirement for every agent. Use stable, tenant-safe `resource` and `thread` identifiers, define retention and deletion behavior, and inspect memory context through tracing. Start with message history; enable working memory, semantic recall, or Observational Memory only when the product needs those capabilities.

assistant-ui is the default AI UI layer for chat, assistant, copilot, and agent-facing interfaces. Use it with Mastra when the product needs a production-ready agent UI instead of building chat primitives from scratch.

Sources: [Create T3 App](https://create.t3.gg/), [pnpm](https://pnpm.io/), [assistant-ui](https://www.assistant-ui.com/), [assistant-ui Mastra integration](https://www.assistant-ui.com/docs/integrations/frameworks/mastra/overview), [Mastra](https://mastra.ai/), [Mastra Memory](https://mastra.ai/docs/memory/overview), [Mastra Storage](https://mastra.ai/docs/storage), [Better Auth](https://www.better-auth.com/), [Drizzle ORM](https://orm.drizzle.team/docs/overview), [Drizzle migrations](https://orm.drizzle.team/docs/migrations), [tRPC](https://trpc.io/docs), [Zod](https://zod.dev/), [Pino](https://getpino.io/), [Mantine](https://mantine.dev/), [Tailwind CSS](https://tailwindcss.com/), [Ultracite](https://www.ultracite.ai/), [Oxlint](https://oxc.rs/docs/guide/usage/linter.html), [Motion](https://motion.dev/).

LogLayer is worth considering when the project outgrows direct Pino usage and needs one logging API that can switch or combine transports. Keep Pino direct for the default MVP path.
