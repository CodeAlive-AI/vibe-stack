# Contributing

Vibe Stack accepts changes that improve the default path. It does not accept broad lists of alternatives without a decision.

## Contribution Types

- Tighten an existing default.
- Add a missing layer with one clear default.
- Move a candidate to default with evidence.
- Move a default to rejected or exception with evidence.
- Add a project template that implements the current `stack.yaml`.

## Required Format

For any tool recommendation, include:

- Status: `default`, `exception`, `candidate`, or `rejected`.
- Layer owned by the tool.
- Why it wins for the common case.
- When not to use it.
- Official source link.
- Review date.

## Default Replacement Rule

Replacing a default needs a decision record in `docs/decisions/`. The decision should explain why the new tool is meaningfully better for AI-native development, not merely newer or more interesting.
