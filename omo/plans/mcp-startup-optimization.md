# Plan: MCP + Plugin Startup-Time Optimization (OpenCode)

Status: proposed (not yet executed) — v2, reviewed by Oracle
Machine: Windows, pwsh 7, Node v24.19.0, uvx 0.12.17, codegraph 1.6.0, opencode 1.18.32
Oracle review: verified against OpenCode source (`mcp/index.ts`, `mcp/catalog.ts`, `config/config.ts`, `config/variable.ts`, `config/parse.ts`, `cross-spawn-spawner.ts`, `session/tools.ts`, `tool/registry.ts`).

## 1. Measured startup times (ascending)

Method: spawn each server, complete MCP stdio handshake (`initialize` -> `notifications/initialized` -> `tools/list`); time = ms to `initialize` result. 3 runs each; spawn floor ~15-25 ms. MCP servers boot in parallel, so boot wall-time ~= slowest server, not the sum.

### Enabled MCP servers

| Rank | Server | Cold (ms) | Warm (ms) | Transport / launch | Tools |
|---|---|---|---|---|---|
| 1 | codegraph | 2898 | 650-1752 | native binary `codegraph serve --mcp` | 1 |
| 2 | dappier | 2310 | 1763-2035 | `uvx --with mcp<2 dappier-mcp` (Python) | 2 |
| 3 | scrapegraph | 4299 | 3044-3239 | `uvx scrapegraph-mcp` (Python) | 8 |
| 4 | firecrawl | 5630 | 4219-4801 | `npx -y firecrawl-mcp` (Node) | 29 |
| 5 | exa | 5788 | 5689-5709 | `npx -y mcp-remote` -> remote HTTP | 4 |
| 6 | tavily | 6748 | 7031-7272 | `npx -y mcp-remote` -> remote HTTP | 5 |
| 7 | microsoft-learn | 9377 | 8019-8728 | `npx -y mcp-remote` -> remote HTTP | 3 |
| - | **aws-mcp** | **FAIL** | **FAIL** | `uvx mcp-proxy-for-aws` — no AWS creds | 0 |

### Plugins (in-process module load)

| Plugin | Load (ms) | Note |
|---|---|---|
| caveman (`./plugins/caveman/plugin.js`) | 28-31 | trivial |
| @slkiser/opencode-quota | 545-1707 | cold 1.7s, warm ~0.55s |
| oh-my-openagent | 682-714 | stable ~0.7s |
| **Plugin total** | **~1.3 s** | |

### Disabled (0 startup cost today)

firefox-devtools, azure-mcp, agentql, context7, browserbase, brightdata, apify, brave — all `enabled:false`, never spawned.

## 2. Root causes

1. **aws-mcp duplicate key (critical).** `mcp` defines `aws-mcp` twice (lines ~228 and ~354). OpenCode parses config with jsonc-parser `parse` (no duplicate-key error; last value wins — confirmed `config/parse.ts`). The survivor is the `uvx mcp-proxy-for-aws` entry with **no `enabled` field -> defaults enabled**. It needs AWS credentials, has none, and fails every boot. Log confirms `message="server unavailable" key=aws-mcp status=failed` ~9-11 s after each boot. **Every boot stalls ~9-11 s on this dead server.**
2. **`npx -y` on every boot.** Each npx MCP re-resolves the package (network + registry) and spawns a fresh Node process. `mcp-remote` adds a second Node layer plus an outbound HTTP handshake -> 5.7-8.7 s each.
3. **`uvx` cold resolution.** Python env/tool resolution per launch; first run may install. dappier ~2 s, scrapegraph ~3.2 s warm.
4. **codegraph is the only native binary** -> fastest (0.65-1.75 s warm).
5. **No per-server `timeout`** except firecrawl (120000). A hung/failing server is allowed to block for the full default window. (Source `DEFAULT_TIMEOUT = 30_000`, but published schema/docs say 5000 — unreconciled; always set explicit.)
6. **Only `enabled:false` skips connect.** `mcp/index.ts` `create` early-returns on `enabled === false`; `MCP.state` `forEach` skips those. Per-agent `tools` gating and global `tools` glob disable do **not** prevent connect — `session/tools.ts` calls `mcp.tools()` (forcing full state) before any permission filter.

## 3. Target

Boot MCP+plugin wall from **~11 s** (aws-mcp stall + slowest remote) to **<3 s**.

## 4. Actions (ordered by impact)

### A. Fix the aws-mcp duplicate key  (expected -9 to -11 s)
- Delete the stub at lines ~228-231. Do **not** rename.
- The correct disabled form is a **full valid config + `"enabled": false`** — not a bare stub. A `{type:"local",enabled:false}` stub is schema-invalid (local requires `command`); a bare `{"enabled":false}` stub is skipped with `"Ignoring MCP config entry without type"` (only adds log noise).
- Decision: disable AWS MCP, or keep enabled with `--skip-auth` + short `timeout`.
```jsonc
"aws-mcp": {
  "type": "local",
  "command": ["uvx", "mcp-proxy-for-aws@latest", "https://aws-mcp.us-east-1.api.aws/mcp", "--metadata", "INSTALL_SOURCE=aws-cli"],
  "enabled": false
}
```

### B. Convert remote-backed MCPs from `npx mcp-remote` to native `type:"remote"`  (expected -2 to -4 s each)
- `type:"remote"` is first-class (`McpRemoteConfig`: `url`, `headers`, `oauth`, `timeout`). `connectRemote` builds `StreamableHTTPClientTransport`, falls back to `SSEClientTransport`; headers passed as `requestInit.headers`.
- `{env:VAR}` substitutes in **both** `url` and `headers` (whole-config text substitution before parse).
- **Set `"oauth": false`** on API-key servers, else default OAuth auto-detect turns a 401 into `needs_auth` + toast instead of a clean failure.
- Behavior delta: mcp-remote `--transport http-only` = streamable only; native tries streamable then SSE (superset) — a dead remote host costs **2x timeout**.
- Mapping: exa `--header x-api-key:X` -> `headers:{"x-api-key":"{env:EXA_API_KEY}"}`; tavily key stays in `url` query; microsoft-learn no auth.
```jsonc
"exa": {
  "type": "remote",
  "url": "https://mcp.exa.ai/mcp?tools=web_search_exa,web_fetch_exa,web_search_advanced_exa,agent_run",
  "headers": { "x-api-key": "{env:EXA_API_KEY}" },
  "oauth": false, "enabled": true, "timeout": 20000
},
"tavily": {
  "type": "remote",
  "url": "https://mcp.tavily.com/mcp/?tavilyApiKey={env:TAVILY_API_KEY}",
  "oauth": false, "enabled": true, "timeout": 20000
},
"microsoft-learn": {
  "type": "remote",
  "url": "https://learn.microsoft.com/api/mcp",
  "oauth": false, "enabled": true, "timeout": 20000
}
```
Future remote conversions (disabled today): context7 / apify -> `headers:{"Authorization":"Bearer {env:...}"}`; browserbase key stays in `url`; brightdata already correct.

### C. Pin + locally install the local npm MCP (firecrawl)  (expected -2 to -4 s)
- Preferred: `["node","<abs>/node_modules/firecrawl-mcp/dist/index.js"]` — no shim, version-pinned. Alternative: `["bun","x","firecrawl-mcp@<pin>"]` — bun native, no `cmd /c` layer.
- `npx --prefer-offline` / `npm_config_prefer_offline` only help a warm cache; npx still spawns + resolves.
- Note: cross-spawn **does** resolve Windows `.cmd` shims, so a bare global bin likely works; the existing `cmd /c npx` is belt-and-braces, not required.
```jsonc
"firecrawl": {
  "type": "local",
  "command": ["node", "C:/Users/Lance/.config/opencode/node_modules/firecrawl-mcp/dist/index.js"],
  "environment": { "FIRECRAWL_API_KEY": "{env:FIRECRAWL_API_KEY}" },
  "enabled": true, "timeout": 120000
}
```
Install + verify entry (one line): `npm install --prefix "$env:USERPROFILE\.config\opencode" firecrawl-mcp@<pin> ; Get-ChildItem "$env:USERPROFILE\.config\opencode\node_modules\firecrawl-mcp\dist" ; opencode mcp list`

### D. Pre-warm / pin `uvx` tools
- `uv tool install` dappier-mcp / scrapegraph-mcp (persistent venvs) or keep uvx but pin versions. Eliminates cold-install latency.
```jsonc
"dappier": { "type":"local", "command":["uvx","--with","mcp<2","dappier-mcp"], "environment":{"DAPPIER_API_KEY":"{env:DAPPIER_API_KEY}"}, "enabled":true, "timeout":20000 },
"scrapegraph": { "type":"local", "command":["uvx","scrapegraph-mcp"], "environment":{"SGAI_API_KEY":"{env:SCRAPEGRAPH_API_KEY}"}, "enabled":true, "timeout":20000 }
```

### E. Per-server `timeout` — scope-corrected  (bounds the stall)
- `mcp.timeout` is **one field** used for connect handshake, `tools/list`, **and every tool call** (`catalog.ts` `convertTool` -> `client.callTool(...,{timeout})`). A 15s value also caps tool calls.
- `experimental.mcp_timeout` is a global fallback for **calls only**, never connect.
- firecrawl's `120000` also bounds its connect — a hung firecrawl blocks first access up to 120 s. Lower it unless large crawls need it.
```jsonc
"experimental": { "batch_tool": true, "continue_loop_on_deny": true, "disable_paste_summary": true, "mcp_timeout": 20000 }
```

### F. Lazy-enable rarely used servers
- Only `enabled:false` skips connect (see root cause 6). "Enable on demand" = toggle `enabled`, not tool gating.
- Keep slow tail (microsoft-learn / scrapegraph / dappier) disabled; boot wall = slowest *remaining* enabled server.
- **There is NO `opencode mcp connect` CLI.** Runtime enable is the service method `connect(name)` exposed as HTTP `POST /mcp/:name/connect` on a *running* server (also `/disconnect`). It works on an `enabled:false` entry (connect overrides enabled), persists for the instance lifetime, and its tools appear in `mcp.tools()`. Gone on restart. Two-step: config `enabled:false` + **restart** to drop boot cost; HTTP connect to re-enable in-session.
```powershell
# endpoint: POST /mcp/:name/connect  (also /mcp/:name/disconnect, GET /mcp for status)
# default port 4096 (fallback: random); query ?directory= optional (defaults to server cwd)
# auth REQUIRED here because OPENCODE_SERVER_PASSWORD is set (Basic, user default "opencode")
curl.exe -sS -u "opencode:$env:OPENCODE_SERVER_PASSWORD" -X POST "http://localhost:4096/mcp/scrapegraph/connect?directory=C%3A%2FUsers%2FLance"
curl.exe -sS -u "opencode:$env:OPENCODE_SERVER_PASSWORD" -X POST "http://localhost:4096/mcp/scrapegraph/disconnect"
```
- Caveat: `storeClient` publishes **no** `ToolsChanged` on runtime connect; a session tool registry built before the connect may not refresh (only a fresh `mcp.tools()` call picks it up). Uncertain whether the registry re-resolves per request.
- Caveat: config is **not** hot-reloaded (no fs watcher; instance config memoized TTL=∞). `enabled`/transport edits need a restart.

### G. Optional future lever: warm daemon + `type:"remote"` gateway
- Biggest remaining lever beyond disabling. Run each slow server once behind a local HTTP/SSE gateway (`mcp-proxy` / `supergateway`), then configure opencode `type:"remote"` -> `http://127.0.0.1:<port>/mcp`. Boot pays only an HTTP handshake (ms), not the `uvx`/`npx` spawn.
- Trade-off: daemon lifecycle + port management. Out of current scope; mark optional.

### No non-blocking option exists
- Connects run concurrently (`concurrency: "unbounded"`) so wall = slowest, not sum. State is lazy + memoized (`InstanceState.make`); the `forEach` **joins all** enabled servers, so whatever first touches MCP (status endpoint / first session tool resolve / system prompt) waits for the slowest. No `lazy`/`defer` flag. Only levers: fewer enabled servers, shorter `timeout`.

## 5. Failure-prevention assessment

- **Duplicate keys:** jsonc-parser last-wins, no error -> silent. Forbid dup keys; schema-lint config. Exact cause of the 10 s stall.
- **Missing `{env:X}` is silent:** `config/variable.ts` resolves `{env:}` to `... || ""` (no error, unlike `{file:}`). A missing key becomes an empty header/URL. Add a preflight asserting every referenced `{env:}` is set.
- **Schema is lenient:** `config/parse.ts` decodes with `onExcessProperty:"ignore"` — a typo like `"enabld":false` is silently dropped and the server stays enabled. Add own lint.
- **Version drift:** `autoupdate:true` + `@latest` (oh-my-openagent, azure-mcp, firefox-devtools, aws proxy) can change behavior between boots. Pin anything on the boot path.
- **Credential presence:** aws-mcp fails on absent creds. Gate optional servers on env presence so a missing secret is a no-op, not a boot stall.
- **Cold cache:** `npx -y` / `uvx` first run downloads; first boot after a cache wipe is slow. Pre-install (Actions C, D).
- **Remote double-transport:** streamable then SSE = 2x timeout worst case.
- **OAuth auto-detect:** on API-key remotes -> spurious `needs_auth` + toast; set `oauth:false`. OAuth callback port 19876 can conflict across instances.
- **Antivirus/Defender** scanning fresh node/uvx spawns — plausible cold-variance cause (unverified); optional exclusions.
- **Observability:** the failure is visible only as `message="server unavailable" ... status=failed` in `~/.local/share/opencode/log/opencode.log`. Add a boot-time grep warning.
- **Secrets:** keys referenced via `{env:...}` (good). Never inline.
- **Unread `stderr:"pipe"` (verified in source, not reproduced):** `connectLocal` sets `stderr:"pipe"`; the SDK pipes child stderr into a `PassThrough` that nothing reads (opencode never consumes `transport.stderr`). A server writing >~16KB to stderr applies backpressure and stalls. Mitigation: quiet server env, e.g. `"environment":{"LOG_LEVEL":"error"}`.
- **No auto-reconnect:** `watch()` `onclose` deletes the client, sets `status:"failed"`, publishes `ToolsChanged`, no retry. A server that dies mid-session stays dead until restart or HTTP connect.
- **Config not hot-reloaded:** `enabled`/transport edits need a restart (no fs watcher; instance config memoized TTL=∞).
- **`opencode mcp debug <name>` refuses `oauth:false` remotes** (prints "OAuth explicitly disabled" and exits) — do not use it to diagnose exa/tavily/microsoft-learn after conversion; use `opencode mcp list`.

## 6. Verification (after executing)

1. `opencode mcp list` — expect codegraph/exa/firecrawl/tavily `connected`, no FAIL.
2. `opencode mcp list` (alias `ls`) shows all servers connected — note it FORCES a full connect of every configured server. For remote auth diagnosis use `opencode mcp debug <name>` (OAuth remotes only; it refuses local and `oauth:false` remotes). There is no `mcp connect`/`mcp status`/`mcp tools` CLI.
3. Confirm `Select-String ~/.local/share/opencode/log/opencode.log -Pattern 'server unavailable'` returns nothing after a fresh boot.
4. Measure end-to-end boot: time from first log line to first MCP/tool availability; target <3 s MCP+plugin wall.

## 7. Uncertainties — RESOLVED (round 2)

- **DEFAULT_TIMEOUT = `30_000`.** Confirmed in source (`mcp/index.ts` `const DEFAULT_TIMEOUT = 30_000`). Published docs saying 5000 are stale. `McpCatalog.defs` also uses 30000 when `mcp.timeout` is unset, so an explicit `timeout` bounds both connect and boot `tools/list`.
- **TUI blocking:** MCP state is lazy + memoized (`InstanceState.make`), connects run `{concurrency:"unbounded"}`, and the `forEach` JOINS ALL enabled servers. Log proves state is forced during startup. Net: MCP availability is gated by the slowest enabled server; no config defers it.
- **firecrawl entry = `dist/index.js`** (npm `bin` field), package version 3.25.4. Confirmed.
- **cross-spawn resolves Windows `.cmd` shims** via `cmd.exe /d /s /c` (`cross-spawn/lib/parse.js`: `needsShell = !/\.(com|exe)$/i`). A bare global bin works. Confirmed.

## 8. Round-2 findings

- **No `opencode mcp connect` CLI.** CLI = `add` / `list` / `auth` / `logout` / `debug` only. Runtime connect = service method + HTTP `POST /mcp/:name/connect` on a running server.
- **Config is not hot-reloaded.** No fs watcher; instance config memoized (TTL=∞). Restart needed for `enabled`/transport edits.
- **Conversion verdicts:** exa `x-api-key` header safe (`requestInit.headers`, no URL parse); tavily key in query safe (`URL.canParse` accepts query strings; only URL-unsafe chars or an unset key break it, and unset -> `""` -> 401 -> loud `failed` with `oauth:false`); microsoft-learn `oauth:false` correct and safe (skips OAuth provider; makes `mcp auth`/`debug` refuse it, which is desired).
- **New gap: unread `stderr:"pipe"`** backpressure stall risk (see section 5).
- **New gap: no auto-reconnect** in `watch()` (see section 5).
- **Optional lever: warm daemon + `type:"remote"` gateway** (Action G).

### Residual uncertainty — ALL RESOLVED (round 3)

- **Session tool-registry refresh after runtime `connect` — RESOLVED: YES it refreshes.** `SessionTools.resolve` is called inside the agent loop (`session/prompt.ts:1221`) and does `for (const [key, entry] of Object.entries(yield* mcp.tools()))` — a fresh `mcp.tools()` each step. A runtime connect is visible on the **next** agent step (not the in-flight one). The earlier "no `ToolsChanged` publish" caveat only affects event-driven consumers, not the per-step tool resolve.
- **HTTP connect endpoint reachability/auth — RESOLVED.** Route `POST /mcp/:name/connect` (and `/disconnect`), group middleware `InstanceContextMiddleware` + `WorkspaceRoutingMiddleware` + `Authorization` (`groups/mcp.ts`). Query fields `directory` (optional) and `workspace` (optional); directory defaults to `?directory=` -> `x-opencode-directory` header -> server cwd. Server auth is ON whenever `OPENCODE_SERVER_PASSWORD` is set (**it is set on this machine**): Basic auth, username default `opencode` (`server/auth.ts`). Default port **4096** (fallback random; `server/server.ts`). So plain curl with `-u "opencode:$env:OPENCODE_SERVER_PASSWORD"` works against a running instance.
- **`stderr` stall — RESOLVED: reproduced.** Reproduced by a standalone probe: child writing 4MB to stderr with the parent NOT reading it HUNG after 6s (`read=0`); with the parent reading, it exited clean (`read=4194304`). Mechanism confirmed.
- **`mcp.cwd` impact — RESOLVED: negligible.** Measured on scrapegraph: empty-cwd 3322/3234/3287 ms vs huge-cwd 4908/3649/3225 ms — within run-to-run noise (the 4908 is a cold first run). No measurable cwd effect on startup.

## 9. Maximalist startup-speed plan (round 3)

MCP boots parallel -> wall = slowest enabled. Savings below are cumulative down the list.

### 9.1 Lever ranking (by wall-time saved)

| # | Lever | Wall saved | Effort | Certainty |
|---|---|---|---|---|
| 1 | Fix `aws-mcp` dup key (remove 2nd key / `enabled:false`) | -9,000 to -11,000 ms | Quick | high |
| 2 | Convert exa/tavily/microsoft-learn `npx mcp-remote` -> `type:"remote"` | -3,500 to -4,500 ms | Short | high |
| 3 | Local-install + pin firecrawl (`node .../dist/index.js`) | -1,500 to -3,000 ms | Short | med |
| 4 | Disable slow uvx tail (scrapegraph 3.2 s, dappier 1.8 s, microsoft-learn) | -1,500 to -3,200 ms | Quick | high |
| 5 | Explicit short `timeout` (0 ms happy-path; bounds worst case) | 0 (up to -22,000 on hang) | Quick | high |
| 6 | Drop `@slkiser/opencode-quota` plugin | -550 to -1,700 ms | Quick | high |
| 7 | Pre-warm uvx (`uv tool install`) if keeping dappier/scrapegraph | -600 to -1,700 ms | Quick | med |
| 8 | LSP servers | 0 (lazy — verified) | — | verified |
| 9 | `formatter:true` | 0 (lazy probing — verified) | — | verified |
| 10 | models.dev / autoupdate | 0 (background/forked — verified) | — | verified |
| 11 | Warm-daemon + `type:"remote"` gateway (keep uvx servers) | -1,500 to -3,000 ms | Large | med |

### 9.2 Maximalist `opencode.jsonc` shape

```jsonc
{
  "plugin": ["./plugins/caveman/plugin.js", "oh-my-openagent@latest"],
  "autoupdate": false,
  "mcp": {
    "codegraph": { "type": "local", "command": ["codegraph","serve","--mcp"], "enabled": true, "timeout": 10000 },
    "firecrawl": {
      "type": "local",
      "command": ["node","C:/Users/Lance/.config/opencode/node_modules/firecrawl-mcp/dist/index.js"],
      "environment": { "FIRECRAWL_API_KEY": "{env:FIRECRAWL_API_KEY}", "LOG_LEVEL": "error" },
      "enabled": true, "timeout": 30000
    },
    "exa": {
      "type": "remote",
      "url": "https://mcp.exa.ai/mcp?tools=web_search_exa,web_fetch_exa,web_search_advanced_exa,agent_run",
      "headers": { "x-api-key": "{env:EXA_API_KEY}" },
      "oauth": false, "enabled": true, "timeout": 10000
    },
    "tavily": {
      "type": "remote",
      "url": "https://mcp.tavily.com/mcp/?tavilyApiKey={env:TAVILY_API_KEY}",
      "oauth": false, "enabled": true, "timeout": 10000
    },
    "dappier":     { "type":"local", "command":["uvx","--with","mcp<2","dappier-mcp"], "environment":{"DAPPIER_API_KEY":"{env:DAPPIER_API_KEY}"}, "enabled": false },
    "scrapegraph": { "type":"local", "command":["uvx","scrapegraph-mcp"], "environment":{"SGAI_API_KEY":"{env:SCRAPEGRAPH_API_KEY}"}, "enabled": false },
    "microsoft-learn": { "type":"remote", "url":"https://learn.microsoft.com/api/mcp", "oauth": false, "enabled": false },
    "aws-mcp": { "type":"local", "command":["uvx","mcp-proxy-for-aws@latest","https://aws-mcp.us-east-1.api.aws/mcp","--metadata","INSTALL_SOURCE=aws-cli"], "enabled": false }
  },
  "lsp": { "unchanged": "see section 4 of the current config — costs 0 at boot" },
  "experimental": { "batch_tool": true, "continue_loop_on_deny": true, "disable_paste_summary": true, "mcp_timeout": 10000 },
  "formatter": true
}
```

LSP left intact — it costs 0 at boot (9.4). Trim only for first-file-open latency, not startup.

Firecrawl install (one line): `npm install --prefix "$env:USERPROFILE\.config\opencode" firecrawl-mcp@3.25.4 ; Get-ChildItem "$env:USERPROFILE\.config\opencode\node_modules\firecrawl-mcp\dist" ; opencode mcp list`

If keeping uvx servers, pre-warm: `uv tool install dappier-mcp ; uv tool install scrapegraph-mcp`

### 9.3 Projected boot wall

| Phase | Current | Maximalist |
|---|---|---|
| MCP wall (slowest enabled) | 9,000-11,000 (aws stall) | ~1,500-1,800 (codegraph/firecrawl) |
| Plugin wall | ~1,300 | ~730 (quota dropped) / ~1,300 (kept) |
| **Total, serial** | **~10,300-12,300** | **~2,200-3,100** |
| **Total, overlapped** | — | **~1,800-2,200** |

Target `<3 s` met either way. Serial assumes `plugin.init()` (awaited in bootstrap) finishes before the first MCP consumer forces state; overlap assumes MCP connect starts during bootstrap.

### 9.4 Unaccounted boot costs (verified from source)

- **LSP — NOT gating, lazy.** `lsp.ts`: `init()` only materializes state (config read + server registry). Process spawn lives in `getClients(file)` <- `touchFile` <- first file open/edit.
- **formatter — NOT gating, lazy.** `format/index.ts`: `init()` builds the formatter map; command probing runs only on first `status()`/`formatFile()`.
- **models.dev — background.** `get()` cached infinity; `populate` reads disk cache; `refresh()` forked every 60 min, early-returns if disk <5 min old.
- **Vcs — forked.** `vcs.ts`: `init()` = `InstanceState.get(state).pipe(Effect.forkIn(scope))`.
- **Snapshot — cheap.** `init()` materializes state; `cleanup()` forked with 1-min delay.
- **ripgrep — lazy.** `Effect.cached`; `which("rg")` first, download only if absent.
- **plugins — GATING.** `bootstrap.ts`: `plugin.init()` awaited before the parallel init batch; `loadExternal` awaits `config.waitForDependencies()` + dynamic import. This is the 1.3 s.

### 9.5 Risk / rollback

- Drop quota plugin -> lose usage/quota UI. Rollback: re-add `"@slkiser/opencode-quota"`.
- Disable scrapegraph/dappier/microsoft-learn -> tools gone at boot; restore in-session via `POST /mcp/:name/connect` (Basic `-u "opencode:$env:OPENCODE_SERVER_PASSWORD"` on :4096), or `enabled:true` + restart.
- `type:"remote"` -> dead host = 2x timeout (streamable then SSE). `timeout:10000` bounds it. `oauth:false` makes `opencode mcp auth/debug` refuse these (intended). Rollback: revert to `npx mcp-remote`.
- Local firecrawl -> version frozen; `timeout:30000` also caps crawls (raise if needed). Rollback: `npx -y firecrawl-mcp`.
- `autoupdate:false` -> manual opencode updates. Rollback: `true`.

**Safe subset (zero feature loss, ~-6,500 ms):** fix `aws-mcp` dup key + convert exa/tavily/microsoft-learn to `type:"remote"` + keep everything enabled. Wall 9-11 s -> ~4.8 s (firecrawl npx still slowest). Then local-install firecrawl -> ~3.2 s. Then disable tail -> ~1.8 s.

### 9.6 Uncertain (round 3)

- Native `type:"remote"` handshake ms on this network (est. 0.3-1.2 s/server).
- Local-node firecrawl ms (est. 0.8-1.8 s).
- Whether `plugin.init` and MCP-state force serialize (2.2-3.1 s) or overlap (1.8-2.2 s) — needs a boot trace.
- `shareNext.init()` / `project.init()` cost — unmeasured; appears sub-MCP-wall.
- Whether a TUI/boot consumer forces MCP before `plugin.init()` returns.
- `autoupdate` boot-time network check (presumed background).
- uv pre-warm exact savings.
- Provider auth: no network refresh at boot presumed (disk read); OAuth refresh on use. Not re-verified in source.
