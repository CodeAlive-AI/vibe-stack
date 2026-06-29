# Contributing

Vibe Stack accepts changes that make the recommended path clearer.

## Rules

- Keep one recommended choice for the common case.
- Do not add lists of alternatives.
- Do not add empty sections for technologies that are not selected yet.
- If a language or scenario is not ready, mark it as `planned_not_selected_yet` in `stack.yaml`.
- Keep docs short enough that a coding agent can read them before starting work.

## Adding A Recommendation

For a new language, scenario, or deploy tool, update:

1. `stack.yaml`
2. The relevant file in `docs/`
3. `README.md` if the current coverage changes

Include:

- The chosen technology.
- What it is used for.
- When to use it.
- What is explicitly not covered yet.
- Official source link.
