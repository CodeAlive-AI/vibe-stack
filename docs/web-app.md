# Web Application

Status: covered.

This is the current default for AI-native web apps: product apps, dashboards, internal tools, AI workbenches, and apps with agent features.

## Use This Stack

| Technology | Role |
| --- | --- |
| TypeScript | Main language |
| React | UI runtime |
| Next.js | App framework |
| Mastra | Agent workflows and agent features |
| Better Auth | Authentication |
| Mantine | UI kit |
| Tailwind CSS v4 | Styling |
| Ultracite + Oxlint | Linting and formatting |
| Motion | Animation |

## Setup Direction For Agents

When starting a new web app:

1. Start from a Next.js TypeScript project.
2. Add Mantine for UI.
3. Add Tailwind CSS v4 for styling.
4. Add Mastra when the app needs agent workflows, tools, memory, or model orchestration.
5. Add Better Auth when the app needs users, sessions, social login, organizations, 2FA, passkeys, or other auth features.
6. Use PostgreSQL from Vibe Infra as the default Better Auth database.
7. Add Ultracite with Oxlint for linting and formatting.
8. Add Motion only when the UI needs animation.
9. Use Vibe Infra when the app needs deployment, database, error tracking, and observability defaults.

## Boundary

This guide does not choose a standalone backend framework yet. If the app needs backend code today, keep it inside the Next.js project unless a project-specific constraint requires otherwise.

Ultracite supports multiple toolchains. Vibe Stack's default is Ultracite with Oxlint because it gives a fast, opinionated linting and formatting path while preserving a simple setup.
