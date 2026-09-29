# Researcher subagent reaches web MCP tools (OpenCode v2 and slim)

Question (ticket R2, Bearmancer/system-config #4): Does a native `researcher` subagent defined in OpenCode v2 config reach web MCP tools, on bare OpenCode v2.0.18 and under oh-my-opencode-slim 2.2.25? Can slim's orchestrator delegate to it?

Answer: yes to all three. Tested 2026-09-29 on Windows against a local stdio MCP server.

## Method

- Isolated environment: `HOME`, `XDG_*`, `OPENCODE_CONFIG_DIR`, `OPENCODE_DB` and `OPENCODE_TEST_HOME` point at a temp dir (the variable set from `packages/cli/test/fixture/environment.ts` in the OpenCode v2 source). Project-level `opencode.json`. Runs used `opencode run --standalone --auto --format json`.
- MCP: a 20-line Node stdio server exposing `web_search`. It appends every `tools/call` (including `_meta.ai.opencode/sessionID`) to `calls.log`.
- Model: `opencode/muse-spark-1.3-contributor-free`.
- Raw evidence: `C:\Users\Lance\.claude\jobs\da241933\tmp\r2\` (`run1.jsonl`, `runB.jsonl`, `runS2.jsonl`, `runN.jsonl`, `*/calls.log`).

## Minimal working config

```json
"agents": {
  "researcher": {
    "description": "Web researcher. Use for any web lookup.",
    "mode": "subagent",
    "system": "Use the web MCP search tool (via execute) for every question. Report exact returned text."
  }
}
```

No `permissions` block is needed. Never add a rule with `action: "execute"` and `effect: "deny"`.

## Claims and evidence

1. **MCP tools reach a native subagent on bare v2.** Parent `build` called `subagent {agent:"researcher"}`. `calls.log` shows `web_search` with a sessionID equal to the sessionID in the `<subagent sessionID=...>` result, and the result text `PINEAPPLE-42`. Runs: `runB.jsonl` (no permissions), `run1.jsonl` (allow-all permissions).
2. **Config shape.** v2 key is `agents` (`packages/schema/src/config/agent.ts:11-22`): model, system, description, mode, hidden, steps, disabled, permissions[]. Servers live under `mcp.servers`.
3. **`execute` is the gate.** MCP tools are Code Mode tools reached via `execute` (`packages/core/src/tool.ts:225-262`, `whollyDisabled("execute", rules)`). With `permissions: [{action:"execute",resource:"*",effect:"deny"}]` the subagent answered `NO TOOL` and the server logged no call (`runN.jsonl`).
4. **Works under slim 2.2.25.** Plugin loaded via `plugin: ["oh-my-opencode-slim@2.2.25"]` (log: `loading plugin ... dist/server/index.js`). The `orchestrator` primary called `subagent {agent:"researcher"}`; the MCP call was logged from the subagent session and returned `PINEAPPLE-42` (`runS2.jsonl`, `projS/calls.log`).
5. **Slim does not restrict `subagent` targets.** Slim's default permissions grant `*` allow (`oh-my-opencode-slim/dist/server/index.js:40684-40690`). It maps v1 keys `task` and `bash` only for its own agents (`:40691-40699`). Delegation vocabulary is `subagent` with an `agent` param (`:40738`).
6. **Plugin loading gotcha.** A `file://` path to the package directory loaded nothing. `Host.resolve` checks only `<dir>/server` and `<dir>/index` (`packages/plugin/src/host.ts:16-42`), while slim exposes `./server` through package `exports`. Use the npm name. A file path to a file gives "configured plugin path must be a directory" (`packages/core/src/config/plugin/source.ts:152`). Legacy v1 `plugin` is normalized to `plugins` (`packages/core/src/config/normalize.ts:185-190`).

## Caveats

- The orchestrator prompt lists only slim agents (`AGENT_DESCRIPTIONS`), so it delegates to `researcher` only when told to or when the prompt is extended.
- With `background: true`, `opencode run` exits before the job finishes. Asking for `background false` produced the completed call.
- Non-standalone `opencode` subcommands (`plugin list`, `debug config`) spawn a second `serve --service` under the isolated env. Use `--standalone`.

## Unverified

- Real remote MCP servers (Exa, Tavily, Firecrawl, Microsoft Learn): only a local stdio stub was tested. Remote transport and auth were not exercised.
- Per-server permission actions (`<server>_<tool>`): not tested.
- Whether the user's v1 keys `agent.general.disable` and `agent.explore.disable` take effect in v2.
- Orchestrator delegating to `researcher` unprompted: the agent was named explicitly.
- Interactive (TUI) delegation with background notifications: only `opencode run` tested.
- The user's real slim config (presets, model overrides): only a minimal per-agent model override was used.
