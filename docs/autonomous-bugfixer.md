# Autonomous Bug Fixer

This manual sets up an agent that fixes production errors on its own. A new error in Bugsink starts Claude Code on the production host. The agent reads the error, the trace, the logs and the database. It writes a fix with a regression test, pushes it, watches the deploy, and resolves the issue. Nobody reviews the change before it ships.

This guide is for a prototype, where the owner accepts that risk. The bounds are the CI gate, hard limits, and the skill's rules, not the model's judgement. Read [Observability for AI-native apps](observability.md) first. The agent is only as good as the stacks and traces it reads.

## The Shape

```
web ──exception──▶ Bugsink ──webhook──▶ agent container (same host) ──claude -p──▶ fix
                      ▲                    │ ssh host, prod.sh, psql                │
                      └───── resolve ──────┘                                        │ git push
                                   production ◀── deploy workflow (full gate) ◀─────┘
```

| Part | What it is |
| --- | --- |
| Trigger | Bugsink's *custom* webhook alert: new, regressed, or unmuted issue |
| Agent | A compose service: a small receiver (queue, limits) plus the Claude Code CLI, logged in to a Max subscription |
| Access | SSH to its own host as the operator user, a write deploy key, the internet |
| Test database | A sidecar Postgres on tmpfs, only for tests |
| Instructions | A repository skill: investigate, decide, fix, verify, push, watch the deploy, resolve |
| Gate | CI runs the full check before deploy; an optional guarded branch route lands small fixes |

## Why On The Host, Not In A Cloud Routine

A common first attempt is a Claude Code routine in Anthropic's cloud, fed a scrubbed brief by a relay that polled Bugsink. It is safe and nearly blind. It sees a stack and nothing else: no trace, no logs, no database. It can fix only what the stack alone explained.

The cloud cannot give it more access. Cloud sessions reach the internet through an HTTP(S) proxy, so SSH and Postgres do not work. Self-hosted cloud environments exist only on Team and Enterprise plans. Allowlisting Anthropic's egress range (`160.79.104.0/21`) opens the port to every Claude user, so it filters noise but does not authenticate anyone.

A container on the production host needs none of that. No port opens and no key leaves the machine. On a Max plan the CLI runs headless on the subscription.

| | Cloud routine | Agent on the host |
| --- | --- | --- |
| Sees | A scrubbed stack | Everything the operator sees |
| Network to prod | None (HTTP proxy only) | Local: SSH to the host, internal Docker networks |
| Data sent to the model provider | Only an allowlisted brief | Whatever it reads becomes model context, the same as an operator's own Claude session |
| Cost of mistakes | A bad commit | A bad commit, or a bad action on production |
| Setup | Routine plus environment plus relay | One compose service plus a login |

Choose the host only when you accept the second column. For a product with real users and regulated data, keep the cloud routine and its allowlisted brief. [Observability](observability.md), practice 10, covers that variant.

## 1. Measure The Host First

The agent shares the host with production. Before building anything, run a throwaway container with the limits you plan to give it. Inside it, run a clone, an install, one test file, a typecheck and a lint. Meanwhile, probe the site's latency.

A two-core, 8 GB host with `cpus: 1`, `mem_limit: 3g` and `cpu_shares: 256` gave numbers like these:

| Step | Result |
| --- | --- |
| Install | 47 s |
| One test file | 6 s |
| `tsc` | 19 s |
| Peak memory | 1.84 GB |
| Site latency, mean | 69 → 88 ms, no errors |

`cpu_shares` below the web service's default of 1024 makes the agent yield to users. Forbid `next build` and full suites on the host. CI runs them.

## 2. Keys Generated On The Host

Run one idempotent script on the host (`sudo bash -s < provision-host.sh`). It creates `/etc/app/agent/`, a root-owned directory whose private files only the agent's uid can read:

- **`host_key`** gives SSH to the host as the operator user. Its `authorized_keys` line is limited to Docker bridges, so the key opens nothing from outside the machine:

  ```
  from="172.16.0.0/12",no-agent-forwarding,no-X11-forwarding ssh-ed25519 AAAA… app-agent
  ```

- **`known_hosts`** pins the host's own key for `host.docker.internal`.
- **`github_key`** is added as a *write* deploy key: `gh repo deploy-key add key.pub --allow-write`.
- **`hook_secret`** is the path secret for the webhook, because Bugsink signs nothing.

The container gets `extra_hosts: host.docker.internal:host-gateway` and an `ssh_config` that makes `ssh prod` mean the host. Your operator scripts (`prod.sh status|logs|sql|oo|bugsink`) then work unchanged inside the container. Traffic from the container to the host's sshd takes the host's INPUT path, so no firewall rule changes.

Revoking the agent takes two steps: delete the `authorized_keys` line and the deploy key.

## 3. The Image

```dockerfile
FROM node:24-bookworm-slim@sha256:…              # same base as web: layers already on the host
RUN apt-get install -y git openssh-client python3 make g++ jq curl ripgrep procps
ENV COREPACK_HOME=/usr/local/share/corepack
RUN corepack enable && corepack prepare pnpm@11 --activate
ENV CLAUDE_CONFIG_DIR=/work/claude DISABLE_AUTOUPDATER=1
RUN npm install -g @anthropic-ai/claude-code@<pinned>
RUN curl -fsS https://api.github.com/meta | jq -r '.ssh_keys[] | "github.com " + .' > /etc/ssh/ssh_known_hosts
RUN useradd --uid 10002 -m agent && mkdir /work && chown agent /work
USER agent
CMD ["node", "main.ts"]
```

- **Pin the CLI and turn off auto-update.** An agent that deploys without review should not change under itself.
- **Take GitHub's host keys from its API over TLS**, not from `ssh-keyscan`, which trusts on first use.
- **Put `CLAUDE_CONFIG_DIR` on the work volume**, so the login survives new images.

## 4. Compose

```yaml
agent:
  build: { context: ./agent }
  cpus: "1.0"
  cpu_shares: 256
  mem_limit: 3g
  environment:
    AGENT_MODEL: ${AGENT_MODEL:-opus}
    CLAUDE_CODE_EFFORT_LEVEL: ${AGENT_EFFORT:-medium}
    TEST_PG_URL: postgres://test:test@agent-postgres:5432/postgres
  expose: ["8080"]
  extra_hosts: ["host.docker.internal:host-gateway"]
  networks: { agent: {}, egress: {} }
  volumes: ["agentwork:/work", "/etc/app/agent:/run/agent:ro"]

agent-postgres:
  image: postgres:18-alpine
  command: [postgres, -c, fsync=off, -c, full_page_writes=off, -c, synchronous_commit=off, -c, max_connections=400]
  tmpfs: ["/var/lib/postgresql:size=1g"]
  networks: { agent: {} }

bugsink:
  environment:
    ALERTS_WEBHOOK_OUTBOUND_MODE: allowlist_only
    ALERTS_WEBHOOK_ALLOW_LIST: agent
    ALERTS_WEBHOOK_DENY_NON_GLOBAL: "false"
  networks: { agent: {}, back: {} }

networks:
  agent: { internal: true }
```

- **Pitfall: testcontainers do not work from the agent's network.** Tests start Postgres on Docker's default bridge. Docker isolates bridges from each other, so the agent cannot reach the mapped ports and fails with `Failed to connect to Reaper`. Compose cannot attach a service to the default bridge either (`network-scoped alias is supported only for containers in user defined networks`). Give the agent a sidecar cluster, and let the test global setup take an external URL. When the URL is set, the setup drops old test databases, rebuilds the seed, migrates it, and creates the template from it.
- **Pitfall: Bugsink 2.6's allowlist does not lift the non-global block.** An allowlisted internal host is still refused as `non-global IP`. `allowlist_only` together with `DENY_NON_GLOBAL=false` keeps every alert confined to `agent`.

## 5. The Receiver

About 250 lines of dependency-free Node, run with type stripping. It is split into pure decisions (`dispatch.ts`, unit-tested) and I/O (`main.ts`).

- **`POST /hook/<secret>`** takes a timing-safe secret comparison. The body is Bugsink's issue serializer plus `alert_reason`. Validate `id` as a UUID, and answer the reason `TEST` without running anything.
- **Queue, one run at a time, persisted to `/work/state.json`.** A duplicate is an issue already queued *or running*. A naive version misses the running case and fires a second run the moment the first ends.
- **Limits:** runs per rolling 24 hours (they share the owner's subscription), two attempts per issue, and a wall-time cap enforced with `spawn(..., { signal: AbortSignal.timeout(ms) })`. A run with no outcome at startup is marked `interrupted`.
- **Before each run:** `git fetch`, `git checkout -f -B autofix origin/main`, `git clean -fd` (not `-x`, so `node_modules` survives), then `pnpm install --frozen-lockfile`. Use async `spawn`, so the webhook keeps answering during the install.
- **Run:** `claude -p <prompt> --model opus --output-format stream-json --verbose --dangerously-skip-permissions`, with the stream written to `/work/runs/<time>-<issue>.jsonl`. That file is the whole audit trail.
- **Prompt:** the instruction comes first, then the issue title inside `<issue_title>` tags, stated to be data. Any signed-in user can choose an exception message.

## 6. The Skill Is The Policy

The receiver only says which issue to work on. A skill in the repository says how:

1. **Investigate.** `bugsink event <id>` gives the stack, the request and the **trace id**. Then pull the trace's spans and logs from OpenObserve, the error history, and the recent deploys. Read the git history of the files involved.
2. **Decline** when the cause is upstream or transient, when the fix is a product, legal or money decision, when the root cause cannot be stated in two sentences with evidence, or when the only fix hides the error. Declining is a good outcome.
3. **Fix.** Write the regression test first and make the smallest root-cause change.
4. **Verify** only the changed files: lint, types, their tests with one worker.
5. **Push.** Small fixes in `src/` and `tests/` go to a guarded branch that CI checks and fast-forwards. Anything else goes to `main`, where the deploy gate stands before production.
6. **Watch the deploy** until the new commit is live, then **resolve** the issue.
7. **Report** the root cause, the change, the checks run, and the push target.

Rules that have no exception:

- **Users' data never goes into commits, fixtures or reports.** Tests use synthetic data.
- **Never print secrets.** Read env keys, never values.
- **Dump before any database write.** Never delete rows without a counted `where`.
- **Never make paid model calls.**
- **Never restart a service to hide an error.**

**Pitfall: Bugsink alerts on an issue only once.** It fires when an issue is new, regressed (it came back after being resolved), or unmuted. An open issue that keeps failing stays silent. So the agent must resolve the issue after its fix is live. Then a recurrence alerts again as a regression and uses the second attempt. A declined issue stays open and silent until a person looks at it.

## 7. Log In Once

```bash
ssh -t host 'sudo docker exec -it -u agent <agent-container> claude'   # then /login, subscription
```

**Pitfall: a narrow terminal wraps the OAuth URL,** and copying it breaks the link. Copy the full URL on one line, open it, and paste the returned code, including the part after `#`. The owner types the code; an assistant never does.

The login lands in `/work/claude` and survives new images. Check it:

```bash
claude -p "Reply with the single word ready." --output-format json
```

The result should have `"is_error": false`.

## 8. Wire Bugsink

In Bugsink's shell, once per project:

```python
MessagingServiceConfig.objects.update_or_create(
    project=Project.objects.get(name="web"), display_name="autofix agent",
    defaults={"kind": "custom", "config": json.dumps({"webhook_url": HOOK_URL})})
config.get_backend().send_test_message()   # the agent should log admission "test"
```

The project's `alert_on_new_issue`, `alert_on_regression` and `alert_on_unmute` flags are on by default.

## 9. Verify Before You Trust It

Test each link where it lives, in this order. Each test is cheap and catches its own class of failure.

| Check | Proves |
| --- | --- |
| Resource trial on the host, with latency probed | The agent will not starve production |
| From the container: `ssh prod`, `prod.sh status`, `sql`, `oo`, `bugsink` | The access works without improvised keys |
| Clone plus `git push --dry-run` through the deploy key | The agent can push, and nothing else can |
| Server tests against the sidecar | The agent can verify database code |
| Receiver: wrong secret, test payload, bad body, new alert, duplicate | Limits and queue behave before a real run spends an attempt |
| `claude -p` before the login | The pipeline reaches the model; it stops at "Not logged in" |
| `claude -p` after the login, with a read-only task | It runs on the subscription with the intended model |
| Bugsink's test message | Webhook delivery through the allowlist |

- **Pitfall: a green deploy workflow is not a running container.** The platform accepts the webhook and restarts containers minutes later. Wait for the new container to be healthy before testing it.
- **Pitfall: do not enable the webhook before the login works.** Every alert before that ends as a failed run and spends an attempt.

## 10. Operate It

| Need | Command |
| --- | --- |
| Watch | `prod.sh logs agent`: alerts, runs started and ended, exit codes |
| Read a run | The JSONL in `/work/runs/` |
| See queue and attempts | `/work/state.json` |
| Pause | `docker stop` the agent. Alerts that arrive meanwhile are lost, not replayed. |
| Stop for good | Remove the Bugsink messaging service and delete `/work/claude` |
| Revoke access | Delete the `authorized_keys` line and the deploy key |
| Budget | Runs share the owner's Max plan. The daily cap is a plan-budget choice, not a technical limit. |

When you replace a cloud routine, clean up behind it:

- disable or delete the routine and its cloud environment;
- delete the relay's Bugsink token;
- remove the routine's env keys from the platform.

## Checklist

- [ ] The owner has accepted, in writing, an unattended agent with production access, and that data it reads becomes model context.
- [ ] A resource trial ran on the real host, with the site's latency measured.
- [ ] Keys were generated on the host. The SSH key is `from=`-restricted, the deploy key is write, and the hook secret is in the URL path.
- [ ] The CLI is pinned with auto-update off, and the login lives on a volume.
- [ ] Tests run against a sidecar database, not testcontainers.
- [ ] The receiver enforces the daily cap, attempts, one run at a time, duplicate-while-running, and a timeout.
- [ ] The skill investigates through traces, declines freely, dumps before writes, and resolves after deploy.
- [ ] CI's full gate stands between every push and production.
- [ ] Every link was verified in order, and the webhook was enabled last.

## Sources

- [Claude Code cloud environments](https://code.claude.com/docs/en/cloud-environments): security proxy, network levels, API credentials
- [Self-hosted environments](https://code.claude.com/docs/en/self-hosted-environments): Team and Enterprise only
- [Routines](https://code.claude.com/docs/en/routines): `claude/` branch pushes
- [Anthropic IP addresses](https://platform.claude.com/docs/en/api/ip-addresses)
- Bugsink source, tag 2.6.1: `alerts/service_backends/custom.py` and `webhook_security.py`
