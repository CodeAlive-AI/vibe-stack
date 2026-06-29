# Selection Rubric

Use this rubric before adding or replacing a recommendation.

## Required Evidence

| Question | Required answer |
| --- | --- |
| Is there one clear default? | Yes. If not, keep it in `docs/radar/`. |
| Does it cover common product work? | It should fit most CRUD, SaaS, internal tools, AI products, and agent workflows. |
| Is it agent-friendly? | Install, configure, test, and deploy steps should be scriptable. |
| Is it production-ready? | The tool should have documentation, active maintenance, and a credible operational story. |
| Does it reduce choices? | It must remove decisions from the common path, not add another branch. |

## Status Values

- `default`: the recommended choice for new projects.
- `exception`: approved only for a named scenario.
- `candidate`: promising, but not default yet.
- `rejected`: evaluated and intentionally not used.

## Review Cadence

Review defaults monthly while the stack is young. Mature layers can move to quarterly review once they have survived real projects and templates.
