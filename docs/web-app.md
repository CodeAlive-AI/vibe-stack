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
| Mantine | UI kit |
| Tailwind CSS v4 | Styling |
| Ultracite | Linting and formatting preset |
| Motion | Animation |

## Setup Direction For Agents

When starting a new web app:

1. Start from a Next.js TypeScript project.
2. Add Mantine for UI.
3. Add Tailwind CSS v4 for styling.
4. Add Mastra when the app needs agent workflows, tools, memory, or model orchestration.
5. Add Ultracite for linting and formatting.
6. Add Motion only when the UI needs animation.
7. Use Vibe Infra when the app needs deployment, database, error tracking, and observability defaults.

## Boundary

This guide does not choose a standalone backend framework yet. If the app needs backend code today, keep it inside the Next.js project unless a project-specific constraint requires otherwise.
