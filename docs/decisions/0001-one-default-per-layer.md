# 0001: One Default Per Layer

Date: 2026-06-29

## Status

Accepted.

## Decision

Vibe Stack will keep one default recommendation per layer. Alternatives are allowed only as named exceptions or candidates in `docs/radar/`.

## Context

The repository exists to remove decision fatigue for AI-native development. A broad catalog would recreate the problem it is supposed to solve.

## Consequences

- New tools need a high replacement bar.
- The README stays narrow.
- Alternatives move to radar files until they earn default status.
- Templates can be generated directly from `stack.yaml` without asking users to choose between equivalent options.
