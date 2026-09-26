# Observability For AI-Native Apps

This guide covers how Vibe Stack apps send errors, traces, and logs so that a person or an AI agent can go from "something broke" to the line of code, the request, the model call, and the cost behind it.

[Vibe Infra](vibe-infra.md) picks the tools: Bugsink for errors, OpenObserve + OpenTelemetry for traces, logs, and metrics. [Web application](web-app.md) picks the app stack. This guide says how to wire them.

Every practice below comes from a real Next.js + Mastra product running this stack in production. Each "Pitfall" happened there: it was measured or reproduced, not predicted.

## The Shape

| Signal | Goes to | Owns | Never goes to |
| --- | --- | --- | --- |
| Exceptions (server and browser) | Bugsink via the Sentry SDK | Grouping, regressions, alerting, the autofix trigger | OpenObserve as the only copy |
| Traces: HTTP, DB, model, and tool spans | OpenObserve via OTLP | Latency, cost, token usage, agent steps | Bugsink (it drops transactions) |
| Logs | Pino JSON to stdout, optionally OTLP to OpenObserve | Narrative around a trace | Files inside the container |
| Money and tokens | A `usage_events` table in PostgreSQL, plus span attributes | Billing truth, per-call breakdown | Only a dashboard |

One join key ties them together: the W3C trace id. It appears on the Bugsink event, on every span, and on every log line.

```text
browser ──traceparent──▶ Next.js route ──▶ pg / undici / model / tool spans ──▶ OpenObserve
   │                         │  └─ pino log lines carry trace_id ─────────────▶ OpenObserve
   └─ error event ─▶ /api/monitoring ─▶ Bugsink ◀── server exceptions (same trace_id)
```

## 1. One Composition Root, One SDK Per Process

Build the tracer provider, exporters, and error SDK in exactly one place: Next's `register()` in `instrumentation.ts`. Nothing else constructs a provider.

```ts
// instrumentation.node.ts (imported from register() when NEXT_RUNTIME === "nodejs")
new NodeSDK({
  instrumentations: [new PgInstrumentation({ requireParentSpan: true }),
                     new UndiciInstrumentation({ requireParentforSpans: true }),
                     new PinoInstrumentation({ disableLogSending: true })],
  sampler: new AlwaysOnSampler(),                       // see practice 5
  textMapPropagator: new core.W3CTraceContextPropagator(),
  traceExporter: new OTLPTraceExporter({ url: `${OPENOBSERVE_URL}/v1/traces` }),
}).start();

Sentry.init({ dsn: process.env.BUGSINK_DSN, skipOpenTelemetrySetup: true, beforeSend });
```

- `skipOpenTelemetrySetup: true` lets Sentry report errors while OpenTelemetry owns tracing. Events captured inside a request still carry the OTel trace id; outside any span, Sentry makes up a random one.
- Only one tracer provider takes effect. `trace.setGlobalTracerProvider` keeps the first registration and silently ignores the rest, so a second provider's sampler or propagator never applies.

**Pitfall: two Sentry SDKs in one process.** A framework integration (`@mastra/sentry`) called `@sentry/node.init()` next to `@sentry/nextjs`. The two SDKs wrapped `server.emit` alternately until requests overflowed the stack. The process stayed up but unhealthy, and the proxy answered 404. For ten hours before that, the second SDK's HTTP instrumentation also wrote every request header into spans exported to OpenObserve. Before adding any vendor integration, check whether it initializes an SDK of its own.

## 2. Report Every Error You Swallow

A catch-all that turns an exception into a 500 hides it from every error hook. The framework never sees it, so the SDK never reports it.

```ts
// errors/http.ts — the one place route handlers turn errors into responses
if (isAppError(error)) return error.toResponse();           // expected, not reported
logger.error({ err: error, requestId }, "unhandled route error");
void reportUnhandledError(error, requestId);                // Sentry.captureException, never rejects
return internalError();
```

```ts
// instrumentation.ts — errors Next catches itself (server components, escaped route errors)
export const onRequestError: Instrumentation.onRequestError = async (...args) => {
  if (process.env.NEXT_RUNTIME !== "nodejs") return;
  (await import("@sentry/nextjs")).captureRequestError(...args);
};
```

- Classify first. Expected errors (validation, not found, rate limit) are responses, not issues. Unclassified errors are defects and always go to Bugsink.
- Reduce `event.request` in `beforeSend` to method + sanitized URL. Headers carry cookies, bodies carry what users typed, and neither fixes a bug.

**Pitfall:** from the day Bugsink went live, unhandled route errors reached the log and nothing else, because the shared error mapper returned a 500 before any hook could fire. It surfaced only when someone asked why Bugsink had nothing from real routes.

## 3. Make Stacks Readable Before They Are Stored

A minified frame (`chunk._.js:1 in T`) is useless to a person and worse for an agent, which will guess. Map frames to source **before** anything stores or forwards them.

**Server (Next standalone + Turbopack):**

```ts
// next.config.ts
experimental: { serverSourceMaps: true },
productionBrowserSourceMaps: true,   // for the browser half below
```

```dockerfile
# builder stage, after `next build` (WORKDIR is the app directory; in a monorepo,
# standalone mirrors the workspace, so the app's maps go under standalone/<app-dir>/)
RUN (cd .next/server && find . -name '*.map' | tar -cf - -T - | tar -xf - -C ../standalone/app/.next/server) \
 && mkdir -p .next/browser-maps \
 && (cd .next/static && find . -name '*.map' | tar -cf - -T - | tar -xf - -C ../browser-maps) \
 && find .next/static -name '*.map' -delete
# runner stage
COPY --from=builder /srv/app/src ./app/src            # context lines for mapped frames
COPY --from=builder /srv/app/.next/browser-maps ./app/.next/browser-maps
```

```yaml
# compose
NODE_OPTIONS: --max-old-space-size=2048 --enable-source-maps
```

- Standalone output copies only the maps its file tracer happens to reach (80 of 436 in one build). Copy all of them next to their chunks.
- `--enable-source-maps` rewrites `error.stack` itself, so every consumer sees `src/server/errors/http.ts:23` (logs, Sentry, agents). Function names stay minified.
- Ship `src/` into the image. Sentry's context lines read the file that a mapped frame names.

**Browser:**

- Browser maps contain your whole client source. Move them out of the public `static` directory at build time. Never serve them.
- **Pitfall: Bugsink (2.6) applies source maps only when it renders an event.** It never applies them to the stored event that the API returns. Anything that reads events programmatically, such as an autofix relay or an agent, gets minified frames. So symbolicate on your server before forwarding (practice 4).
- **Pitfall: Turbopack names a chunk's map after its own hash** (`3wj0o18hpwa3a.js` → `2qg1cq02gd566.js.map`). Find the map through the chunk's trailing `sourceMappingURL` comment, not by appending `.map`.
- **Pitfall: `path.join(process.cwd(), …)` in server code** makes Turbopack trace the whole project into standalone. Mark it `/* turbopackIgnore: true */`.

## 4. Browser Errors Through A Tunnel You Control

Post browser envelopes to your own route. Validate them there, then forward to Bugsink on the internal network. The browser never learns the DSN, and Bugsink stays private.

```ts
// instrumentation-client.ts
const KEEP = new Set(["BrowserApiErrors", "BrowserTracing", "Dedupe", "FunctionToString",
  "GlobalHandlers", "HttpContext", "InboundFilters", "LinkedErrors",
  "NextjsClientStackFrameNormalization"]);

Sentry.init({
  dsn: "https://browser@example.invalid/1",       // placeholder; the server swaps in the real DSN
  tunnel: "/api/monitoring",
  enabled: process.env.NODE_ENV === "production",
  integrations: (defaults) => defaults.filter((i) => KEEP.has(i.name)),
  beforeBreadcrumb: () => null,
  sendClientReports: false,
  propagateTraceparent: true,                      // practice 5
  tracePropagationTargets: [/^\/api\//u],
});
export { captureRouterTransitionStart as onRouterTransitionStart } from "@sentry/nextjs";
```

The tunnel route:

1. Checks same origin, requires a session, caps the body (64 KiB), and rate-limits per user.
2. **Rebuilds** the event from an allowlist: exception type and value, frames, sanitized page URL, user agent, trace ids. It never forwards the event as sent: breadcrumbs, user, cookies, extra and contexts are dropped.
3. Maps frames to source with the private maps. It drops the event if no frame lands in your source; extensions, third-party scripts, and stackless rejections are noise.
4. Rewrites the envelope's DSN and posts one event item to `http://bugsink:8000/api/<project>/envelope/`.

- **Pitfall: SDK defaults.** `@sentry/nextjs` quietly adds web vitals, sessions, and tracing, and breadcrumbs record clicks and console output. Use an allowlist of integrations, not a denylist.
- **Pitfall: the tunnel is a public write endpoint.** Anyone can post a forged envelope. If issues start automated work (practice 10), a forged message becomes input to an agent. Require auth, rate-limit, and never trust the payload's shape.

## 5. One Trace From The Page To The Database

Carry the trace from the browser to the server with the W3C `traceparent` header. Then a browser issue in Bugsink leads straight to the server spans in OpenObserve.

- **Browser.** Keep `BrowserTracing` but set **no** `tracesSampleRate`. That is Sentry's "tracing without performance": no spans are recorded or sent, only headers on requests. With `propagateTraceparent: true`, `tracePropagationTargets` limited to your API, and `onRouterTransitionStart`, you get one trace per page or navigation.
- **Server.** Next already runs each request under the incoming context. But the header comes from the internet, so let it choose which trace a request joins and nothing else:
  - `AlwaysOnSampler`, not the default `ParentBased(AlwaysOn)`;
  - a trace-context-only propagator, which drops `baggage`.

**Pitfall: the silent sampling switch.** Without a sample rate, the browser SDK sends flag `00`. The default `ParentBased` sampler obeys a remote parent, so turning on propagation stopped recording **every** browser-initiated request. Any client could also switch tracing off for itself. This follows the W3C Trace Context security guidance: at a trust boundary, a service decides what to take from an incoming context.

Keep `trace_id` and `span_id` on the browser event, validated as exact hex, so the Bugsink issue carries the link.

## 6. Privacy By Construction, Not By Redaction

Telemetry is read by people, and by agents that paste it into prompts. It outlives the request. Build it from allowlists.

```ts
// telemetry.ts — the only way business code opens a span
export const SPAN_ATTR_KEYS = ["requestId", "errorCode", "durationMs", "cost_usd", "model",
  "tokens_in", "cached_tokens", "cache_write_tokens", "corpus_version"] as const;
type SpanAttrs = Partial<Record<(typeof SPAN_ATTR_KEYS)[number], string | number>>;

// withSpan copies only SPAN_ATTR_KEYS onto the span, sets ERROR status on throw,
// records durationMs, and is the single caller of tracer.startActiveSpan.
await withSpan("provider.openrouter", { model, requestId }, async (span) => {
  const result = await callModel();
  span.setAttribute("tokens_in", result.usage.inputTokens);
  return result;
});
```

- Pin the attribute allowlist with a test, including a denylist of names that must never appear (`phone`, `userId`, `content`, `messages`).
- Put redaction in Pino's `redact` centrally. A new log line with a personal field is a review blocker, not a redaction opportunity.
- Use a dev profile that records everything to a local file, and a prod profile that records what it is allowed to. "Why was this answer wrong?" is a development question, answered in development.

**Pitfall: framework exporters bypass your allowlist.** Mastra's `SensitiveDataFilter` redacted the field names `content` and `messages`. The OTLP exporter writes the same data under GenAI semantic-convention names (`gen_ai.response.text`, `gen_ai.tool.call.result`) and metadata keys the filter never sees. So production kept model answers and tool results in full while the config said otherwise. **Audit the sink, not the config.** Query a sample of each text field for its shape only (length, whether it holds `[REDACTED]`, which script it uses) without printing values.

**Pitfall: deletion is coarse.** OpenObserve deletes by time range and deletes traces by whole days. There is no row filter. "Never ingest it" is the only precise control; "delete it later" costs every other trace from those days.

**Good news worth knowing:** the Sentry SDK replaced cookie and auth-header values with `[Filtered]` even when a stray instrumentation captured headers. So a scary field name in the schema is not yet a leak. Check the values' shape before rotating secrets.

## 7. Telemetry That Explains Model Spend

For AI features, the expensive questions are "why did this turn cost that much" and "did caching work". Answer them from primary data:

- Store **per model call** usage (input, output, cached-read, cache-write tokens, cost, model, provider) in the database, next to the product event. A span alone is not billing truth.
- Put the cache triple on the turn span: `cached_tokens`, `cache_write_tokens`, `tokens_in`. A hit rate is evidence only when its denominator sits beside it. Reads and writes stay separate, because some providers bill writes above the input rate.
- **Absent is not zero.** A provider that reports nothing about caching must leave the attribute unset. Writing `0` fabricates the denominator of every ratio built on it.
- Report input and output tokens before money, and split input into fresh and cached.
- Keep three quantities apart: peak context, sum of input over all steps, and number of steps.
- Tag spans with what produced the answer: model id, prompt or corpus version. A bad answer then traces back to the revision that caused it.
- **Pitfall:** a 245k-token turn was blamed on a tool's output ceiling. Its peak context was 36k. A limit says what *could* happen; the per-call breakdown says what *did*.

## 8. Trace And Log Agents Like Any Other Code Path

An agent turn is a request with many steps: model calls, tool calls, guardrails, memory reads. Trace it inside the request's trace, under the same privacy rules. Answer "why was this answer wrong" with a separate development profile.

```ts
// mastra/index.ts — one Observability instance, two profiles
const prod = {
  serviceName: "app-agent",
  bridge: new OtelBridge(),                        // agent spans join the active request span
  exporters: [new OtelExporter({
    provider: { custom: { endpoint: `${OPENOBSERVE_URL}/v1/traces`, protocol: "http/protobuf",
                          headers: { Authorization: `Basic ${OPENOBSERVE_BASIC}` } } },
    signals: { traces: true, logs: false },        // logs go through Pino only
  })],
  excludeSpanTypes: [SpanType.MODEL_CHUNK],        // practice 9
  spanOutputProcessors: [errorPrivacy,
    new SensitiveDataFilter({ sensitiveFields: [...SECRETS, ...IDENTITY, "content", "messages"] })],
};
const dev = {
  serviceName: "app-agent",                        // no bridge: outside a request there is no span to join
  exporters: [new FileExporter({ filePath: ".traces/mastra.jsonl" })],
  excludeSpanTypes: env.TRACE_CHUNKS === "1" ? [] : [SpanType.MODEL_CHUNK],
  includeInternalSpans: env.TRACE_INTERNAL === "1",
  serializationOptions: { maxStringLength: 20_000, maxObjectKeys: 200, maxArrayLength: 200, maxDepth: 12 },
  spanOutputProcessors: [errorPrivacy,
    new SensitiveDataFilter({ sensitiveFields: [...SECRETS, ...IDENTITY] })],   // keeps the conversation
};
new Mastra({ agents, observability: new Observability({ configs: { default: isProd ? prod : dev } }) });

// Keep the span's error status; drop the SDK's exception payload.
const errorPrivacy: SpanOutputProcessor = {
  name: "error-privacy",
  process: (span) => { if (span?.errorInfo) span.errorInfo = { message: "Operation failed" }; return span; },
  shutdown: async () => {},
};
```

- **One trace per turn.** The OTel bridge makes `agent_run → model_step → tool_call` children of the HTTP span. The Bugsink event, the log lines, and the agent's steps then share one trace id. Without the bridge, agent spans land in separate traces that nothing joins to the request.
- **Two profiles, chosen by one pure function.** An explicit `OBSERVABILITY_PROFILE` wins; otherwise `NODE_ENV=production` selects `prod`. A test pins the single intended difference: whether the conversation is kept. Default to recording. **Pitfall:** with no exporter configured in development, five benchmark runs were scored on an agent nobody could inspect.
- **The dev exporter is an append-only JSONL file, written synchronously.** It needs no OpenObserve and no Postgres, it can be grepped, and it keeps the tail. A buffered exporter loses exactly the last spans of a run that dies mid-flight. Never use it on a hot path.
- **Pitfall: cycle-safe serialization that erases data.** A `WeakSet` "seen" check marks any object reached twice as `[circular]`, for example the same tool result under both `toolCalls` and `toolResults`. Every tool result in a trace read `[circular]`. Detect cycles against the current ancestor path, not against everything already visited.
- **Redact secrets and identity in every profile, dev included.** Dev databases hold real people often enough that "it is only local" is not a policy. Keep the conversation only in dev, then shape-audit what prod actually stores (practice 6: exporters rename fields past name-based filters).
- **Mask exception payloads, keep the error class.** Provider SDK errors can carry the request body, which means the prompt. Keep status and a closed error code as attributes, so a masked "Operation failed" is still diagnosable.
- **Keep the agent's request context to closed enums** (locale, role, attachment kind). Whatever sits in it can reach prompts, the cacheable prompt prefix, and spans. User fields never go there.
- **Log agent events, not content,** through the app's Pino logger so every line carries `trace_id`: tool name, outcome, duration, sizes (a `transcript_chars` length, never the text). Turn off the framework's own log signal. Mastra's ships tool arguments (user queries) through a second, differently configured pipeline; keep one auditable log path.
- **Count every paid call, including the framework's own.** A guardrail such as a moderation processor makes a model call and throws its usage away. Collect usage at the provider layer into a per-request ledger (`AsyncLocalStorage`) and write it to the database (practice 7). Otherwise part of the spend is invisible.
- **Put quality next to errors.** Attach cheap deterministic scorers to agent runs, for example "does every citation name a real document", so a quality regression is queryable the way an exception is.

## 9. Keep Agent Traces Affordable

Agent frameworks emit spans that copy state.

- **Streaming chunk spans carry the accumulated output,** so their total size grows quadratically with answer length. One benchmark episode wrote a 9.8 GB trace file with them on. Exclude `MODEL_CHUNK` spans by default, in production too.
- **Internal workflow spans carry the whole workflow state.** One episode produced 416 internal spans totalling 380 MB, against 1.5 MB for the agent spans themselves. Keep them opt-in.
- Health checks are traced like any request (one every 30 seconds adds up). Filter them if they drown the stream.
- Full sampling is fine for a product with few users. Revisit it when OpenObserve's ingest or disk says so, not before.

## 10. Close The Loop With Agents, Safely

When a new Bugsink issue can start an autofix agent, the error stream becomes an agent input. Treat it like one.

- Build the agent's brief from an **allowlist**: issue id, counts, exception type and message passed through a scrubber (emails, tokens, long numbers, prose, quoted values masked), frame locations, and source lines of in-app files. Never include request data, locals, breadcrumbs, or code from `eval` frames.
- Symbolicate first (practices 3 and 4). The agent should read `app/src/...:line`, not minified chunks.
- Bound it: runs per day, gap between runs, attempts per issue, changed lines, and an allowlist of paths it may touch. Land through a guard plus the full check gate, never by trusting the model.
- Resolve a dispatched issue after a grace period, so a fix that did not work comes back as a regression instead of going quiet.
- Give the agent's environment what verification needs: the pinned runtime version and a container engine for database-backed tests. An agent that cannot run tests will push untested fixes.

## 11. Verify On The Sink, Not On A Proxy

Most observability "works on my config" bugs survive because the check looked at something other than the stored data.

| Looked convincing | Was not proof because | Real check |
| --- | --- | --- |
| The active span has the incoming trace id | A non-recording span has one too | Query the trace id in OpenObserve |
| The deploy workflow is green | It passes when the platform accepts the webhook; the container restarts minutes later | Compare the container start time with the test time |
| The option's name is in the JS bundle | The SDK contains the string either way | Observe the behavior (headers on a real request) |
| The redaction config lists the field | The exporter renames fields | Shape-audit the stored values |
| The dashboard shows cached tokens | Absent was written as zero | Check the provider's per-call usage |

After every observability change, produce one real event of each kind and find it in the sink by id. Use a harmless request with a chosen `traceparent`, not a production error.

## Checklist

- [ ] One provider and one error SDK, built in `register()`. No integration initializes its own.
- [ ] Unclassified errors reach Bugsink from the shared error mapper and from `onRequestError`.
- [ ] Server stacks name source files: `serverSourceMaps`, all maps copied into standalone, `--enable-source-maps`, `src/` in the image.
- [ ] Browser maps are private, and frames are symbolicated before Bugsink stores them.
- [ ] Browser errors go through an authenticated, rate-limited, allowlisting tunnel.
- [ ] `traceparent` flows browser → server. The server samples with `AlwaysOn` and ignores baggage.
- [ ] Span attributes come from a tested allowlist. Stored values are shape-audited after every exporter change.
- [ ] Per-call token and cost records exist. The cache triple is on spans, and absent stays absent.
- [ ] Agent spans join the request trace through the OTel bridge. Dev writes a local JSONL trace; prod keeps no conversation and masks error payloads.
- [ ] Per-call usage includes the framework's internal calls, such as guardrails.
- [ ] Chunk and internal workflow spans are excluded in production.
- [ ] Each change is verified by finding a real event in the sink.

## Sources

- [Next.js instrumentation](https://nextjs.org/docs/app/api-reference/file-conventions/instrumentation), [instrumentation-client](https://nextjs.org/docs/app/api-reference/file-conventions/instrumentation-client), [OpenTelemetry guide](https://nextjs.org/docs/app/guides/open-telemetry), [productionBrowserSourceMaps](https://nextjs.org/docs/app/api-reference/config/next-config-js/productionBrowserSourceMaps)
- [Node.js `--enable-source-maps`](https://nodejs.org/api/cli.html)
- [Sentry for Next.js](https://docs.sentry.io/platforms/javascript/guides/nextjs/), [tunnel option](https://docs.sentry.io/platforms/javascript/troubleshooting/), [distributed tracing](https://docs.sentry.io/platforms/javascript/tracing/distributed-tracing/), [trace propagation (SDK spec)](https://develop.sentry.dev/sdk/foundations/trace-propagation/)
- [W3C Trace Context](https://www.w3.org/TR/trace-context/)
- [OpenTelemetry JS sampling](https://opentelemetry.io/docs/languages/js/sampling/), [GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/), [Pino instrumentation](https://github.com/open-telemetry/opentelemetry-js-contrib/tree/main/packages/instrumentation-pino)
- [Bugsink docs](https://www.bugsink.com/docs/), [Bugsink source](https://github.com/bugsink/bugsink) (`events/utils.py`: source maps applied at render time)
- [OpenObserve stream data deletion](https://openobserve.ai/docs/reference/api/stream/delete/)
- [Mastra observability](https://mastra.ai/docs/observability/overview), [Mastra tracing](https://mastra.ai/docs/observability/tracing/overview)
- [Pino redaction](https://getpino.io/#/docs/redaction)
