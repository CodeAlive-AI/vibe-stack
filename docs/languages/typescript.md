# TypeScript

Status: covered for web applications.

TypeScript is the current default language for Vibe Stack because it fits the main supported scenario: AI-native web applications with an app UI and agent features.

## Recommended Stack

Use this when the project is a web application:

| Need | Choice |
| --- | --- |
| Package manager | pnpm |
| UI runtime | React |
| App framework | Next.js |
| Agent workflows | Mastra |
| Authentication | Better Auth |
| Data access | Prisma + PostgreSQL |
| Validation | Zod |
| Logging | Pino JSON logs to stdout |
| UI kit | Mantine |
| Styling | Tailwind CSS v4 |
| Code quality | TypeScript strict mode + Ultracite + Oxlint |
| Animation | Motion |

## Current Boundary

Vibe Stack does not yet define a separate TypeScript backend-only stack. For now, backend choices are project-specific unless the work fits naturally inside the Next.js application.

Better Auth is the default auth choice for TypeScript web apps because it lives inside the application, is framework-agnostic, and supports PostgreSQL.

Prisma is the default data access layer for PostgreSQL because it gives TypeScript apps a type-safe generated client. Zod is the default validation layer for runtime inputs, shared schemas, and startup config validation. Pino is the default logger because it produces fast structured JSON logs that Docker and later log collectors can consume.

LogLayer can be added later when the project needs a logger abstraction over Pino and other transports. It is not the default MVP choice because direct Pino is simpler.

## Not The Default

Radix UI is not the default UI kit. Use it only when Mantine cannot cover a required primitive or when a project is intentionally building its own component system.
