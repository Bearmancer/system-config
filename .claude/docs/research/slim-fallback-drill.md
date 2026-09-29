# Live-proving the oh-my-opencode-slim fallback swap on OpenCode 2.0.19

Research date: 2026-09-29. Read-only research; no config file was modified and no secret file was read.

## Questions restated

1. What is the proper, safe, on-demand way to live-prove that oh-my-opencode-slim swaps a failing model for its configured fallback? Specifically: is a local mock OpenAI-compatible HTTP endpoint that always returns 429, registered as a custom provider in OpenCode v2, a sound approach? Give the exact v2 config shape with a source, confirm which GitHub repo is current (anomalyco/opencode or sst/opencode), give a minimal mock-server one-liner, and give the drill steps using the subagent path (because `run --agent` ignores agent models).
2. Why does `opencode run --agent X` ignore the agent's configured model? Is that documented, a known issue, or fixed by `--model`?
3. Where is the authoritative OpenCode v2 config schema (plural keys)?

## Short answers

- Q1: Yes, a loopback mock returning 429 is sound. It exercises exactly the code path slim hooks (`v2.session.retry`, fired by OpenCode's own retry policy on a retryable provider error). A 429 is converted to a session error of type `provider.rate-limit` with `status: 429`, and slim treats both the type and the status as failover triggers. Register the mock and a slim fixer override in a throwaway project directory's `.opencode/`, so global configs stay untouched. Main drill: orchestrator delegating to fixer through the `subagent` tool. Optional cheaper shortcut: `run --agent fixer --model mock429/always-429`.
- Q2: Documented behavior, plus an open upstream issue (#42561). `run --agent X` only publishes an agent-selected event; the session model is separate. `--model` is honored and is the workaround. Subagent spawn is different: v2.0.19 applies the agent's configured model.
- Q3: No published plural-key JSON Schema exists. The canonical definition is the Effect schema class `Config.Info` in `packages/schema/src/config.ts` of anomalyco/opencode at tag v2.0.19. `https://opencode.ai/config.json` is still generated from v1 shapes (open issues #43748, #50724).

## Source pinning

- Current repo: `anomalyco/opencode`. `gh api repos/sst/opencode` returns `full_name: anomalyco/opencode` (live command, 2026-09-29), so sst/opencode redirects to it.
- Installed CLI: `opencode --version` printed `opencode v2.0.19`. Tag `v2.0.19` resolves to commit `1fd016ef32286de9489b7b24f1029f52c49a27b3` (`gh api repos/anomalyco/opencode/git/ref/tags/v2.0.19`). The latest GitHub Release is `v1.18.33`; v2.x exists as tags only (`gh api repos/anomalyco/opencode/releases/latest`). All "source:line" citations below are at that tag, read from a shallow clone of it. Paths are relative to the repo root.
- Slim plugin citations are line numbers in `C:/Users/Lance/.cache/opencode/npm/oh-my-opencode-slim@latest/1790593106915/node_modules/oh-my-opencode-slim/dist/index.js` (called `slim dist` below).

## Q3: authoritative v2 config schema

Findings, in order of authority:

1. Canonical definition (source of truth): `packages/schema/src/config.ts` at v2.0.19.
   - `class Info ... "Config.Info"` defines the plural keys: `agents` (line 57), `mcp` (line 78), `plugins` (line 99), `providers` (line 108), plus `permissions`, `commands`, `skills`, `instructions`, and others.
   - Sub-schemas: `packages/schema/src/config/provider.ts` (`Config.Provider` at line 85, `models` at line 91, per-model `disabled` in the `Model` class), `packages/schema/src/config/agent.ts` (`Config.Agent` at line 11, includes `model`, `mode`, `disabled`, `permissions`), `packages/schema/src/config/mcp.ts` (`servers` at line 21), `packages/schema/src/config/plugin.ts`.
   - Permalink: https://github.com/anomalyco/opencode/blob/v2.0.19/packages/schema/src/config.ts
2. The runtime loader decodes with `onExcessProperty: "ignore"` (`packages/core/src/config.ts:102`), so unknown or misspelled keys are silently dropped. `packages/core/src/config/normalize.ts` also maps v1 singular keys to the canonical shape and emits normalization diagnostics (`ConfigNormalize.normalize`, called at `packages/core/src/config.ts:116`).
3. Published JSON Schema: none for v2 runtime config.
   - `https://opencode.ai/config.json` (live fetch, top-level property keys listed with `jaq`): `agent, provider, plugin, permission, mcp, ...` (singular). It is generated from v1: on `dev`, `packages/opencode/script/schema.ts:72` is `generateEffect(ConfigV1.Info)` (`gh api repos/anomalyco/opencode/contents/packages/opencode/script/schema.ts?ref=dev`).
   - Upstream tracks this as open issues https://github.com/anomalyco/opencode/issues/43748 (published schema rejects documented V2 fields), https://github.com/anomalyco/opencode/issues/50724, https://github.com/anomalyco/opencode/issues/48812. Issue https://github.com/anomalyco/opencode/issues/50852 (closed as duplicate of #43748) states "There is also no V2 schema at any of the obvious URLs" and that SchemaStore's `opencode` entry points editors at the v1 document.
   - Live probes (curl, 2026-09-29): `https://opencode.ai/v2/config.json`, `/v2/opencode.json`, `/v2/core.json`, `/v2/server.json` all return 404. `https://opencode.ai/v2/cli.json` returns 200 but is the TUI/CLI config schema (`SchemaURL` at `packages/cli/src/config/schema.ts:4`, file `cli.json`), not the runtime config.
   - The live v2 docs page https://opencode.ai/v2/docs/config/ shows plural-key examples (`providers`, `agents`) yet still prints `"$schema": "https://opencode.ai/config.json"`. The docs and the hosted schema disagree.
4. Practical consequence: use `opencode debug config` (help text: "List configuration sources") and `opencode models` as the validators, not an editor schema. Issue #43748 states `debug config` "parses and normalizes everything" for a v2-shaped file.

## Q2: why `run --agent X` ignores the agent's model

- Documented. The v2 agents docs (https://opencode.ai/v2/docs/agents/, fetched 2026-09-29) say: "A session stores its selected model separately. Selecting a primary agent by ID does not change that model." and, for subagents, "A subagent uses its configured model, or inherits the parent session's model when none is configured."
- Code path at v2.0.19:
  - `packages/cli/src/run/noninteractive.ts:651-652`: `if (input.agent) { await input.client.session.switchAgent(...) }` is the only thing `--agent` does.
  - `packages/core/src/session/session.ts:90-96`: `switchAgent` only publishes `SessionEvent.AgentSelected`. `packages/core/src/session/projector.ts:546-555` projects it as `SessionTable.agent = ...` only.
  - `packages/cli/src/run/noninteractive.ts:654-670`: `switchModel` is called only when a `--model` (or a variant) is supplied.
  - `packages/core/src/session/runner/model.ts:77-90`: the runner resolves the model from `session.model` only.
- Known issue, still open: https://github.com/anomalyco/opencode/issues/42561 "run --agent ignores the agent's declared model and silently resolves the global default" (created 2026-08-14, updated 2026-09-10). Comments reproduce it with `--standalone` and JSON `agents.<name>.model`. Related: https://github.com/anomalyco/opencode/issues/43179 (interactive primary-agent switch also keeps the previous model).
- `--model` is the workaround: the reporter's repro in #42561 shows `run --agent modelprobe --model opencode/nemotron-3.5-lightning-free` printing the agent's model; code confirms at `noninteractive.ts:654-669`. `opencode run --help` lists `--model, -m string  Model to use in the format provider/model#variant`.
- Subagents behave differently. `packages/core/src/tool/plugin/subagent.ts:184`: `const model = override ?? agent.model ?? parent.model`. This matches the observation that the orchestrator-to-fixer call used fixer's configured primary. The tool's `model` parameter description tells the calling LLM never to set it unless the user asks (`subagent.ts:36-38`), so the default path uses `agent.model`.
- Regression history worth knowing: https://github.com/anomalyco/opencode/issues/49765 reported "subagent spawn ignores agents.*.model" on 2.0.8; the 2.0.19 source above applies `agent.model`, which is consistent with your live observation. https://github.com/anomalyco/opencode/issues/50925 (2.0.10, open) reports that an agent with `mode: all` loses its configured model at subagent spawn while `mode: subagent` works. Check the fixer's `mode` if a subagent spawn ever shows the parent model.

## Q1: the drill

### Why the mock approach is valid

- OpenCode's retry loop is in `packages/core/src/session/runner/retry.ts`. Its `policy` builds a `session.retry` event and awaits the plugin hook before waiting (`retry.ts:70-78`, hook call at line 78). The event's `error` is a `SessionError.Error` (`retry.ts:18, 74`), and the hook may set `event.decision` (lines 79-82).
- HTTP 429 to session error, traced end to end:
  - `packages/ai/src/provider-error.ts:212-222`: `input.status === 429` returns `RateLimitError` (unless the text matches the quota regex, see body hygiene below).
  - `packages/core/src/session/to-session-error.ts:13-14`: a `RateLimit` reason becomes `providerError("provider.rate-limit", ...)`; `providerError` (line 69 onward) takes `status` from `reason.http?.status`. The `SessionError.Error` struct carries `type`, `message`, and optional `status` (`packages/schema/src/session-error.ts:7-11`).
  - Slim's `isFailoverError` (`slim dist:29684`) returns true on either branch: `extractStatusCode` reads `error.status` (`slim dist:29677-29680`) and status 429 is in the failover list (`slim dist:29694`); and `type` `provider.rate-limit` is in `FAILOVER_ERROR_TYPES` (`slim dist:29633-29638`).
  - `RateLimit` is retryable (`packages/ai/src/provider-error.ts:65-72`), so OpenCode reaches the retry policy and the hook.
- Slim registers the hook: `slim dist:48845` (`v1Hooks["v2.session.retry"]`) and `slim dist:49641` (`handleV2Retry`). `handleV2Retry` (`slim dist:29942`) returns early unless the error is a failover error and `initialRetryDelayMs` is 0 (your config), then calls `switchModel` and sets `event.decision = { retry: true, delay: retryDelayMs }`, logging `[foreground-fallback] retry hook switched model in place` (`slim dist:29979`).
- If the swap does not happen, OpenCode retries the mock up to 10 times over about 84 seconds (`retry.ts:42-56`). The mock's request count therefore discriminates a swap (1 request) from no swap (many requests).
- Body hygiene: a 429 whose text matches `/insufficient[-_\s]?quota|quota[-_\s]?exceeded|budget exceeded|usage limit/i` becomes `QuotaExceededError`, which is not retryable (`provider-error.ts:148, 206-209`; non-retryable cases at `provider-error.ts:87-92`). Use a plain rate-limit body. Do not send a large `Retry-After` (it only raises the built-in delay, `retry.ts:34-55`).

### Exact v2 config shape for the mock provider

Sources for the shape:
- Live v2 docs, custom provider example: https://opencode.ai/v2/docs/providers/ (keys `providers.<id>.{name, env, package, settings.baseURL, models.<id>.{name}}`, package `@opencode/ai/providers/openai-compatible`).
- Schema: `packages/schema/src/config/provider.ts:85-92`, `Settings` at lines 9-17 (`settings` is an open record; `apiKey` and `baseURL` pass through).
- OpenAI-compatible package settings: `packages/ai/src/providers/openai-compatible.ts:11, 19` (`apiKey` is optional, `baseURL` required); the route appends `/chat/completions` (`packages/ai/src/protocols/openai-compatible-chat.ts:20`), so `baseURL` should end in `/v1`.
- Package id is a built-in: `packages/core/src/provider.ts:93`.
- Shape precedent in tests: `packages/server/test/provider.test.ts:26-34` uses `providers.custom = { name, package: "@opencode/ai/providers/openai-compatible", settings: { apiKey: "secret" }, models: { chat: {} } }`. That test is a config-shape precedent only; it asserts the provider is absent from `/api/provider` at a specific plugin-timing moment. Issue https://github.com/anomalyco/opencode/issues/50852 shows the same shape with `baseURL`.
- Any configured provider is activated regardless of credentials: `packages/core/src/config/plugin/provider.ts:67` (`provider.activation = "enabled"`).

Project-local file `<DRILL>/.opencode/opencode.jsonc` (project `.opencode/opencode.json(c)` files are loaded above global config: `packages/core/src/config/discovery.ts:11, 41, 66-68` and load order at `packages/core/src/config.ts:194-236`):

```jsonc
{
  "providers": {
    "mock429": {
      "name": "Mock 429",
      "package": "@opencode/ai/providers/openai-compatible",
      "settings": { "baseURL": "http://127.0.0.1:18429/v1", "apiKey": "mock" },
      "models": { "always-429": { "name": "Always 429" } }
    }
  }
}
```

Slim override `<DRILL>/.opencode/oh-my-opencode-slim.jsonc` (slim reads `<directory>/.opencode/oh-my-opencode-slim.json(c)` and merges it over the user file: `slim dist:20154-20176`; `agents` are deep-merged and arrays are replaced, `slim dist:19703-19720`; top-level `agents` override the active preset's agents, `slim dist:20222`):

```jsonc
{
  "agents": {
    "fixer": {
      "model": [
        { "id": "mock429/always-429" },
        { "id": "alibaba-token-plan/deepseek-v4.1-flash" }
      ]
    }
  }
}
```

This leaves `fallback.initialRetryDelayMs = 0` from your global slim file in force (`fallback` is deep-merged, `slim dist:20169`).

### Mock server (node 24.19.0 present)

Save as `<DRILL>/mock429.js` (a file avoids nested-quote breakage when launched through tmux or psmux):

```js
let n = 0
require("http").createServer((q, r) => {
  console.log(new Date().toISOString(), ++n, q.method, q.url)
  q.resume()
  r.writeHead(429, { "content-type": "application/json" })
  r.end(JSON.stringify({ error: { message: "Too Many Requests", type: "rate_limit_error", code: "rate_limit_exceeded" } }))
}).listen(18429, "127.0.0.1")
```

Equivalent single line for a plain shell (not for embedding in a tmux command string):
`node -e "let n=0;require('http').createServer((q,r)=>{console.log(new Date().toISOString(),++n,q.method,q.url);q.resume();r.writeHead(429,{'content-type':'application/json'});r.end(JSON.stringify({error:{message:'Too Many Requests',type:'rate_limit_error',code:'rate_limit_exceeded'}}))}).listen(18429,'127.0.0.1')"`

I dry-ran the handler logic against stub request/response objects (no socket opened): it wrote status `429`, header `content-type: application/json`, and the body above. The server itself was not started, because the brief allowed read-only commands only. Launch detached per your tmux rule: `tmux new-session -d -s mock429 "node <DRILL>/mock429.js"`; read it with `tmux capture-pane -t mock429 -p`.

### Drill steps

0. Pre-flight, free, read-only. In `<DRILL>` (a throwaway directory containing `.opencode/opencode.jsonc`, `.opencode/oh-my-opencode-slim.jsonc`, `mock429.js`):
   - `opencode debug config` should list the two project files as sources.
   - `opencode models` should list `mock429/always-429`. Because excess keys are silently ignored (`config.ts:102`), a missing model here means the provider block was not decoded.
   - `opencode debug agents` should show fixer resolving to the mock model (issue #42561 shows `debug agents` reports the configured model correctly).
1. Start the mock (command above). Confirm nothing else uses port 18429.
2. Main drill, subagent path (matches production delegation; one orchestrator call on the global model plus one fallback call): from `<DRILL>`, run `opencode run --standalone --auto --agent orchestrator "Call the subagent tool exactly once with agent=fixer and prompt='Reply OK'. Do not pass a model parameter. Then stop."`. The child session is created with `agent.model` (`subagent.ts:184`), i.e. the mock, which returns 429; the retry hook then fires with the child's agent and model. `--standalone` makes the plugin initialize in `<DRILL>`, so it reads the project slim file. Add `--print-logs --log-level debug` to see server logs (help text: "server logs require --standalone").
3. Evidence to collect:
   - Slim log (`getLogDir()` at `slim dist:20511` is `~/.local/share/opencode/log/oh-my-opencode-slim.<timestamp>.log`; new file per process). Run `rg "foreground-fallback|\[v2\] retry hook" <newest slim log>`. Pass condition: `[v2] retry hook registered` and `[foreground-fallback] retry hook switched model in place` with `from: mock429/always-429`, `to: alibaba-token-plan/deepseek-v4.1-flash`.
   - Mock log: exactly 1 request line. 10 or more lines means OpenCode's built-in retry ran and slim did not swap.
   - Run output: the run prints `> <agent> · <model>` (`noninteractive.ts:240-246`).
   - Optional persisted proof: `opencode session list` then `opencode session export <id>` shows the final model of the session or child (both subcommands appear in `opencode session --help`).
4. Optional shortcut (one real call, to the fallback model, no orchestrator LLM): from `<DRILL>`, run `opencode run --standalone --auto --agent fixer --model mock429/always-429 "Reply with the single word OK"`. `--model` makes the session model equal fixer's chain head (`noninteractive.ts:654-669`), so slim's chain logic (`slim dist:30150-30215`) picks the next entry. Failure case: if the swap log shows `to:` as some other agent's primary rather than `alibaba-token-plan/deepseek-v4.1-flash`, the session agent was not fixer (the #36764 risk for subagent-mode agents), slim walked the wrong chain, and step 2 is the valid drill.
5. Cleanup: `tmux kill-session -t mock429`; `opencode session delete <id>` for each session the drill created (parent and child; help text: "Delete a session and its child sessions"); remove `<DRILL>` with the fd-based deletion procedure from CLAUDE.md.

### Reading a failed drill

- Mock never hit: provider not registered or the wrong project directory. Re-check pre-flight; `--standalone` must be run from `<DRILL>`.
- Mock hit once, no swap log line, but `[v2] retry hook registered` present: `isFailoverError` returned false or `initialRetryDelayMs` is non-zero; inspect the `event.error` shape.
- Mock hit about 11 times: built-in retry ran to exhaustion; the hook did not switch (also check the `sessionTried`/chain state lines in the slim log).
- The run reports a 404 on a path: `baseURL` or the mock port was wrong; the mock answers every path with 429 and never returns 404.

### Cost and safety

- The mock binds `127.0.0.1` only and returns a static error. `apiKey: "mock"` is not a credential.
- No global file is edited; the only files created are in `<DRILL>`.
- Real spend: one orchestrator call plus one fallback call (main drill), or one fallback call (shortcut).
- Side effect: sessions persist in OpenCode's database until deleted (step 5).

## Unverified

- I did not start the mock server or run any drill. The mock handler was checked only by invoking its logic against stub objects.
- Not verified that `run --agent fixer` works when fixer has `mode: subagent` (optional shortcut). The v1 issue https://github.com/anomalyco/opencode/issues/36764 reports `--agent <subagent>` falling back to the default primary; v2 behavior for subagent-mode agents was not tested. Your earlier `run --agent oracle` did switch agents without error, but whether the session then ran with oracle's prompt and permissions is unknown.
- Not verified how slim resolves the session's agent name in the main drill (`registerSessionAgent` at `slim dist:29961` uses `event.agent` from the retry event); this is inferred from `retry.ts:70-77`, which includes `agent`.
- Not verified that slim accepts a model id from a provider it has never seen (`mock429/...`) without validating it against the catalog. Pre-flight step 0 covers OpenCode's side only.
- Not verified that a project-level `<DRILL>/.opencode/oh-my-opencode-slim.jsonc` is honored by the plugin under `--standalone` on Windows; the loader code (`slim dist:20154-20176`) says it is, but this was not run. Also inferred, not run: a non-standalone run would talk to the background service, whose plugin instance was initialized in a different directory.
- Not verified that the orchestrator LLM will follow the delegation prompt and omit the `model` parameter of the `subagent` tool; if it passes one, that model overrides `agent.model` (`subagent.ts:184`) and the drill proves nothing.
- Not verified whether a fix for #42561 exists on any branch newer than tag v2.0.19; the `dev` branch file layout differs and the latest GitHub Release is v1.18.33, so the v2.0.19 tag was used.
- The hosted `https://opencode.ai/config.json` singular-key claim rests on the key list I printed today plus #43748/#50852; whether a v2 schema is planned was not found in any source.
- The `mode: all` caveat (#50925) is from an open issue on 2.0.10 and was not re-tested on 2.0.19.
