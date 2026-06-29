# Contribution Guide

Vibe Stack welcomes pull requests that improve the recommended defaults.

## What Fits

- A better default for an existing category.
- A missing default for a language or product scenario.
- A self-hosted replacement for a common hosted service.
- A starter template that implements the current stack.
- Short documentation that helps an agent set up the stack correctly.

## Selection Bar

A recommendation should be:

- Useful for the common case, not a niche preference.
- Proven in real product work.
- Production-ready and actively maintained.
- Self-hosted or self-hostable whenever possible.
- Simple enough for a coding agent to install, configure, test, and deploy.
- A single default, not a list of equivalent alternatives.

## What Does Not Fit

- Awesome-list entries.
- Multiple competing choices for the same need.
- Tools that are interesting but not proven.
- Recommendations that require large manual setup steps.
- Empty sections for languages or stacks that are not selected yet.

## Pull Request Checklist

Update only what is needed:

- The relevant guide in `docs/`.
- `README.md` only when the top-level default or coverage changes.
- `templates/` only when adding a starter template.

Every recommendation should explain:

- What technology is chosen.
- What need it covers.
- What it replaces or avoids.
- Why it is the default for the common case.
- Whether it is self-hosted or self-hostable.
- The official source link.
