# 0002: Web Stack Baseline

Date: 2026-06-29

## Status

Accepted.

## Decision

The default web application stack is TypeScript, React, Next.js, Mantine, Tailwind CSS v4, Motion, TypeScript strict mode, and Ultracite.

Radix UI is an approved exception for missing accessibility primitives, not the default component system.

## Context

The stack needs to support fast AI-native product development while staying maintainable under heavy coding-agent contribution. The primary risk is not that a team lacks options; the risk is that every project starts with the same unresolved UI, quality, deployment, and observability debates.

## Consequences

- Mantine is the first UI choice for product surfaces.
- Tailwind CSS is used for composition around the component system, not as a reason to avoid components.
- `tsc` remains mandatory because lint presets do not replace the TypeScript compiler.
- Ultracite is the default lint/format consistency layer.
