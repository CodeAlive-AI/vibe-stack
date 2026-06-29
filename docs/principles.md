# Principles

Vibe Stack is an opinionated baseline for AI-native development. It should make the common path obvious for humans and coding agents.

## Selection Rules

1. One default per layer.
2. Prefer boring production reliability over novelty.
3. Prefer tools with strong TypeScript, automation, and documentation ergonomics.
4. Prefer tools that coding agents can install, configure, test, and debug without hidden manual steps.
5. Prefer self-hostable infrastructure when it materially improves ownership or cost control.
6. Add exceptions only when they are narrower than the default and clearly named.

## Anti-Goals

- This is not an awesome-list.
- This is not a market map.
- This is not a place to track every promising startup or library.
- This is not a benchmark of every alternative.

## Decision Shape

Every recommendation should answer:

- What is the default?
- What job does it own?
- Why is it the default?
- When should it not be used?
- What replaces it only in that exception?

## Replacement Bar

A new tool replaces the default only when it is clearly better on at least two of these dimensions:

- Lower operational complexity.
- Better agent ergonomics.
- Better type safety or correctness feedback.
- Better production observability.
- Better local development loop.
- Stronger ecosystem fit.
- Lower total cost for the expected team size.
