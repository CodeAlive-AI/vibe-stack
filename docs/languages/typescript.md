# TypeScript

Status: covered for web applications.

TypeScript is the current default language for Vibe Stack because it fits the main supported scenario: AI-native web applications with an app UI and agent features.

## Recommended Stack

Use this when the project is a web application:

| Need | Choice |
| --- | --- |
| UI runtime | React |
| App framework | Next.js |
| Agent workflows | Mastra |
| Authentication | Better Auth |
| UI kit | Mantine |
| Styling | Tailwind CSS v4 |
| Code quality | TypeScript strict mode + Ultracite |
| Animation | Motion |

## Current Boundary

Vibe Stack does not yet define a separate TypeScript backend-only stack. For now, backend choices are project-specific unless the work fits naturally inside the Next.js application.

Better Auth is the default auth choice for TypeScript web apps because it lives inside the application, is framework-agnostic, and supports PostgreSQL.

## Not The Default

Radix UI is not the default UI kit. Use it only when Mantine cannot cover a required primitive or when a project is intentionally building its own component system.
