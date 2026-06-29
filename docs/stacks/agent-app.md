# Agent App Stack

This is the default stack for TypeScript agent applications and AI workflows.

## Default

| Layer | Choice | Notes |
| --- | --- | --- |
| Language | TypeScript | Keeps app code, web code, and agent code in one type system. |
| Agent framework | Mastra | Default engine for agents, workflows, tools, and memory-oriented product work. |
| Web surface | Next.js + React | Use the web stack when the agent needs a UI, dashboard, or customer-facing app. |
| Database | PostgreSQL | Store durable state, user data, workflow runs, and audit records here unless a more specialized store is required. |
| Observability | SigNoz | Instrument agent workflows with traces, logs, and metrics. |
| Error tracking | Bugsink | Capture application exceptions and frontend/backend error events. |

## Operating Rule

Agent applications need stronger observability than ordinary CRUD apps. Every workflow should be inspectable after the fact: inputs, tool calls, model calls, decisions, errors, and latency.

## Exceptions

Do not introduce a second agent framework until there is a concrete missing capability in Mastra that blocks a real project.
