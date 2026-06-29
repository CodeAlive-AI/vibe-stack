# Common Guide

Status: covered.

This is the shared baseline for Vibe Stack projects.

Vibe Stack is optimized for a strong MVP with a low cost of mistake. Follow YAGNI: add only the practices that keep the project easy to change, verify, deploy, and debug with AI agents.

## Principle

Do the simplest thing that keeps the agent effective.

That usually means:

- One obvious way to run the app.
- One obvious way to verify the app.
- One obvious place for configuration.
- One obvious place to inspect errors and runtime behavior.
- Small reversible changes instead of large process-heavy work.

## Fail Fast And Fast Feedback

Agents should not sweep problems under the rug.

- Prefer fast feedback over delayed surprises.
- Prefer clear exceptions with actionable messages over silent fallbacks.
- Fail startup when required config, dependencies, or services are invalid.
- Keep fallback behavior rare, explicit, tested, and visible.
- Do not hide broken production behavior behind a default value.
- Make the shortest useful verification loop easy to run after every change.

## Minimum Agent-Ready Contract

Before an agent starts work, it should know:

- What to change.
- How to run the app.
- How to verify the change.
- What not to touch.
- When to stop and ask.

If this is unclear, clarify only that. Do not introduce a large process.

## Lightweight Runtime Rules

Borrow only the useful part of 12-Factor:

- Put config and secrets outside the code.
- Validate config on startup.
- Keep dependencies explicit.
- Use PostgreSQL, Bugsink, SigNoz, and other services as attached resources.
- Keep durable state out of the local filesystem.
- Make logs, errors, traces, and metrics visible.
- Run migrations and maintenance as explicit commands.

This is enough for most MVPs. Do not add Kubernetes, service mesh, complex release machinery, or heavy compliance process unless the product actually needs it.

## Config Validation

Validate all required configuration values when the app starts.

- Fail fast when required config is missing or invalid.
- Use the validation tool that fits the language and framework.
- Prefer explicit config over hidden defaults.
- Use defaults only for safe local-development values.
- Use fallbacks only when the fallback behavior is intentionally designed and tested.
- Do not silently downgrade production behavior because a config value is missing.

## Verification

Every project should expose a short verification path:

```bash
lint
typecheck
test
build
```

Names can differ by project. The important part is that an agent can find and run the checks without guessing.

## Observability

For an MVP, observability should answer:

- Did it crash? Use Bugsink.
- Is it slow or broken in production? Use SigNoz with OpenTelemetry.
- Did the last deploy make things worse? Compare deploy time with errors, traces, metrics, and logs.

Do not build a full SRE program before the product has that level of risk.

## Evidence

Keep evidence lightweight:

- Code changes should mention the checks that passed.
- Production fixes should point to the error, trace, metric, or log that motivated them.
- Technology recommendations should point to official docs or real project use.

Generated summaries are not evidence unless they link back to source files, test output, logs, traces, issues, or docs.

## Safety

Agents should:

- Prefer small reversible changes.
- Avoid destructive operations unless explicitly approved.
- Never commit secrets.
- Keep database migrations reviewable.
- Stop when a risky change has no clear verification path.

## Sources

- [The Twelve-Factor App](https://12factor.net/)
- [OpenTelemetry](https://opentelemetry.io/docs/)
