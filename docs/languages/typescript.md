# TypeScript

TypeScript is the current default language for Vibe Stack because it fits the main supported scenario: AI-native web applications with an app UI and agent features.

## Recommended Stack

Use this when the project is a web application:

| Need | Choice |
| --- | --- |
| Package manager | [pnpm](https://pnpm.io/) |
| UI runtime | [React](https://react.dev/) |
| App framework | [Next.js](https://nextjs.org/) |
| Agent workflows | [Mastra](https://mastra.ai/) |
| AI UI layer | [assistant-ui](https://www.assistant-ui.com/) |
| Authentication | [Better Auth](https://www.better-auth.com/) |
| Data access | [Prisma](https://www.prisma.io/) + [PostgreSQL](https://www.postgresql.org/) |
| Validation | [Zod](https://zod.dev/) |
| Logging | [Pino](https://getpino.io/) JSON logs to stdout |
| UI kit | [Mantine](https://mantine.dev/) |
| Styling | [Tailwind CSS v4](https://tailwindcss.com/) |
| Code quality | TypeScript strict mode + [Ultracite](https://www.ultracite.ai/) + [Oxlint](https://oxc.rs/docs/guide/usage/linter.html) |
| Animation | [Motion](https://motion.dev/) |

## Current Boundary

Vibe Stack does not yet define a separate TypeScript backend-only stack. For now, backend choices are project-specific unless the work fits naturally inside the Next.js application.

assistant-ui is the default AI UI layer for chat, assistant, copilot, and agent-facing interfaces. Mastra owns agent logic; assistant-ui owns the React UI primitives and state layer for talking to those agents.

Better Auth is the default auth choice for TypeScript web apps because it lives inside the application, is framework-agnostic, and supports PostgreSQL.

Prisma is the default data access layer for PostgreSQL because it gives TypeScript apps a type-safe generated client. Keep stable entities and relations in the Prisma schema, and use PostgreSQL `jsonb` only for unstable metadata, provider payloads, and experimental fields. Zod is the default validation layer for runtime inputs, shared schemas, and startup config validation. Pino is the default logger because it produces fast structured JSON logs that Docker and later log collectors can consume.

LogLayer can be added later when the project needs a logger abstraction over Pino and other transports. It is not the default MVP choice because direct Pino is simpler.

## Not The Default

Radix UI is not the default UI kit. Use it only when Mantine cannot cover a required primitive or when a project is intentionally building its own component system.
