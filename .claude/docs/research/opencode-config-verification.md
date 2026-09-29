# Verifying the staged OpenCode v2.0.18 config

Date: 2026-09-29. Scope: every factual value in the staged `C:/Users/Lance/.config/opencode/opencode.json.next`, checked against primary sources only (vendor docs, upstream source at a pinned ref, npm registry, and live isolated runs of OpenCode v2.0.18). Nothing in `~/.config/opencode` was read, edited or run against. Prior research reused, not redone: `mcp-chain-unknowns.md`, `researcher-subagent-mcp.md`, `file-key-hot-reload.md`.

## Question

Are the MCP URLs, auth headers, package names, environment variable names, tool names, config keys and model id in `opencode.json.next` correct, and does OpenCode v2.0.18 load the file as intended? A value counts as VERIFIED only with a quoted vendor doc, a file:line in upstream source, or a live test result. Verdicts are VERIFIED, CONTRADICTED or UNVERIFIABLE.

## Summary

| # | Item | Verdict | Correct value |
|---|---|---|---|
| 1 | Exa auth header `Authorization: Bearer` | VERIFIED | `x-api-key` also accepted and has higher priority |
| 1b | Exa `?tools=web_search_exa,web_fetch_exa,web_search_advanced_exa,agent_run` | VERIFIED | all four names registered |
| 2a | Apify `?tools=` syntax, `apify/rag-web-browser`, `search-actors`, `call-actor` | VERIFIED | comma-separated |
| 2b | Apify `get-actor-output` | CONTRADICTED | no such tool; use `get-dataset-items` (auto-injected) |
| 3 | AgentQL `npx -y agentql-mcp`, `AGENTQL_API_KEY` | VERIFIED | unchanged |
| 4a | Tavily `https://mcp.tavily.com/mcp/` + Bearer | VERIFIED | unchanged |
| 4b | Firecrawl `https://mcp.firecrawl.dev/v2/mcp` + Bearer | VERIFIED | unchanged |
| 4c | Browserbase `https://mcp.browserbase.com/mcp` + Bearer | VERIFIED | `x-bb-api-key` also accepted |
| 4d | Bright Data `npx -y @brightdata/mcp`, `API_TOKEN` | VERIFIED | unchanged |
| 4e | ScrapeGraph `scrapegraph-mcp`, `SGAI_API_KEY` | VERIFIED | unchanged; Python console script, not npm |
| 5a | `disabled: true` with a missing `{file:}` still loads | CONTRADICTED | config load fails with `ConfigInvalidError` |
| 5b | `disabled` is the v2 key | VERIFIED | `enabled: false` is silently ignored |
| 5c | model `opencode/muse-spark-1.3-contributor-free` resolves | VERIFIED | unchanged |
| 6a | legacy `agent.explore.disable` / `agent.general.disable` | CONTRADICTED | dropped; use `agents.<name>.disabled: true` |
| 6b | `#xhigh` variant suffix | VERIFIED (syntax) | variant existence for this model UNVERIFIABLE |
| 6c | Remaining keys | see item 6 | |

## 1. Exa remote MCP

Verdict: VERIFIED. Both header forms work, and a plain API key in `Authorization: Bearer` is treated as an API key.

Source: `exa-labs/exa-mcp-server`, `api/mcp.ts` (HEAD on 2026-09-29, `package.json` version 3.4.1).

- Lines 369-383 document the contract: "x-api-key: YOUR_KEY - Pass API key via header (recommended)", "Authorization: Bearer YOUR_KEY - Pass API key via header (alternative)", "Priority: x-api-key header > Authorization header > URL query parameter > environment variable."
- Lines 443-474 implement it. `request.headers.get("x-api-key")` wins. Otherwise `getBearerToken` (regex `/^Bearer\s+(.+)$/i`, lines 394-399) is read. If the bearer looks like a JWT it goes through OAuth verification; otherwise it is used as the API key (`// Plain API key in Bearer header`, `exaApiKey = bearerToken`).
- `README.md` line 132: "You can also send it as a `Authorization: Bearer …` header or an `x-api-key` header."
- The CORS allow-list (line 29) includes both `Authorization` and `x-api-key`.

Tool names in `?tools=`: `src/mcp-handler.ts` registers `web_search_exa` (line 80), `web_search_advanced_exa` (85), `web_fetch_exa` (95) and `agent_run` (137). `README.md` lines 109-110 show the comma-separated form, `https://mcp.exa.ai/mcp?tools=web_search_exa,web_fetch_exa,agent_run`, and say the list "will replace the defaults". `agent_run` needs authentication ("Exa Agent requires authentication (OAuth or an API key)"), which the Bearer header provides.

Caveat: `oauth: false` in the OpenCode entry only stops OpenCode from starting an OAuth flow. It does not affect Exa.

## 2. Apify hosted MCP

Verdict: URL, `tools` syntax and three of four names VERIFIED. `get-actor-output` CONTRADICTED.

Sources: `apify/apify-mcp-server` README and `src/const.ts` (HEAD on 2026-09-29), plus https://docs.apify.com/platform/integrations/mcp.

- Syntax. README, "Configuring the hosted server": `https://mcp.apify.com?tools=actors,docs,apify/rag-web-browser,apify/web-fetch`. The tools parameter takes "either categories or specific tools directly, and Apify Actors", comma-separated. `apify/rag-web-browser` is a documented Actor selector (README lines 319, 335). The Apify docs page gives `https://mcp.apify.com?tools=apify/instagram-scraper,apify/google-search-scraper`.
- `search-actors` and `call-actor` are real tool names (README table lines 264 and 266; `src/const.ts`: `STORE_SEARCH: 'search-actors'`, `ACTOR_CALL: 'call-actor'`).
- `get-actor-output` does not exist. A search for `get-actor-output` and `actor-output` across the repo's source, docs, tests and CHANGELOG returned nothing. The output tools are `get-dataset-items` (`src/const.ts:62`, `DATASET_GET_ITEMS`) and `get-key-value-store-record`. README: "When `call-actor`, an Actor tool, or `get-actor-run` is present, the server auto-injects `get-actor-run`, `get-dataset-items`, `get-key-value-store-record`, and `abort-actor-run`."
- Worse than a typo. `src/utils/tools_loader.ts` (`resolveActorsToLoad` doc comment) classifies any selector that is not a retired selector, a category or an internal tool name as an Actor name. So `get-actor-output` would be treated as an Actor to fetch, not ignored. The effect on the live server was not tested with a real token.
- Corrected URL: `https://mcp.apify.com/?tools=apify/rag-web-browser,search-actors,call-actor`. `get-dataset-items` arrives automatically because `call-actor` is present. Add it explicitly only if wanted.
- Auth: README line 73 and the Apify docs: "Authorization: Bearer <APIFY_TOKEN>". VERIFIED for the header.

Note on the slash before `?`: the docs write `https://mcp.apify.com?tools=...`. The staged `https://mcp.apify.com/?tools=...` is the same URL after normalisation, but no source shows the server accepting both spellings. UNVERIFIABLE, low risk.

## 3. AgentQL MCP

Verdict: VERIFIED. Source: `tinyfish-io/agentql-mcp` (HEAD on 2026-09-29) and npm.

- `package.json`: `"name": "agentql-mcp"`, `"bin": {"agentql-mcp": "dist/index.js"}`, version 1.0.1. `npm view agentql-mcp version bin` returned the same on 2026-09-29.
- `README.md` line 113: "Command: `env AGENTQL_API_KEY=YOUR_API_KEY npx -y agentql-mcp`"; config blocks (lines 33-36) use `"command": "npx"` with `AGENTQL_API_KEY`.
- `src/index.ts:26`: `const AGENTQL_API_KEY = process.env.AGENTQL_API_KEY;` and line 29: "Error: AGENTQL_API_KEY environment variable is required".

The executor's guess was right.

## 4. Remaining servers

- Tavily: VERIFIED. `tavily-ai/tavily-mcp` README lines 25-32: URL `https://mcp.tavily.com/mcp/?tavilyApiKey=<your-api-key>`, and "Alternatively, you can pass your API key through an Authorization header ... `Authorization: Bearer <your-api-key>`". Line 147 repeats it. Not exercised live (no key).
- Firecrawl: VERIFIED. https://docs.firecrawl.dev/mcp-server: the API-key path uses `https://mcp.firecrawl.dev/v2/mcp` with "a bearer token instead" (OAuth uses `/v2/mcp-oauth`). Already recorded in `mcp-chain-unknowns.md`.
- Browserbase: VERIFIED. https://docs.stagehand.dev/v3/integrations/mcp/setup: endpoint `https://mcp.browserbase.com/mcp`; "Pass your Browserbase API key as an HTTP authorization header: `Authorization: Bearer YOUR_BROWSERBASE_API_KEY`"; alternative `x-bb-api-key`; the `browserbaseApiKey` query parameter is "a deprecated compatibility fallback".
- Bright Data: VERIFIED. `brightdata/brightdata-mcp` `package.json` name `@brightdata/mcp` (2.11.3; the npm `bin` is `mcp`, a single bin, so `npx -y @brightdata/mcp` resolves); README lines 80-86: `"command": "npx", "args": ["@brightdata/mcp"], "env": {"API_TOKEN": "<your-api-token-here>"}`. The README's headline hosted option is `https://mcp.brightdata.com/mcp?token=...` (query token; no header form documented), which the staged config does not use.
- ScrapeGraph: VERIFIED. `ScrapeGraphAI/scrapegraph-mcp` `pyproject.toml:38`: `scrapegraph-mcp = "scrapegraph_mcp.server:main"` (a Python console script, installed here at `C:\Users\Lance\.local\bin\scrapegraph-mcp.exe`); README line 40: "`SGAI_API_KEY` — API key" and lines 256-257 "Using the installed command: scrapegraph-mcp". The README's `npx` entries are Smithery or `mcp-remote` wrappers, not this local command.

## 5. OpenCode v2.0.18 behaviour (live, isolated)

Isolation: `HOME`, `USERPROFILE`, all `XDG_*`, `OPENCODE_CONFIG_DIR`, `OPENCODE_DB` and `OPENCODE_TEST_HOME` pointed at a temp dir; project-level `opencode.json` in a temp cwd; every run used `opencode run --standalone`. The error path in run A shows the isolated home (`...\live\home\.config\opencode\secrets\exa`), confirming the live secrets directory was never touched. Dummy secret files contained the text `DUMMY`. Source checked at tag `v2.0.18` of `anomalyco/opencode`.

### 5a. `disabled: true` does not protect a missing `{file:}`

Verdict: CONTRADICTED. The staged file, with the secrets directory absent, fails to load.

- Live: a minimal config with one remote server, `"disabled": true`, header `Bearer {file:~/.config/opencode/secrets/x}` and no such file gave `ConfigInvalidError` (`PlatformError: NotFound: FileSystem.readFile ...\secrets\x`, HTTP 500 on `/api/location`, exit code 1). The full staged file gave the same error for `...\secrets\exa`. With the file present the same config exited 0, the model replied `OK`, and no connection to the (invalid) URL was attempted.
- Source: `packages/core/src/config/variable.ts` substitutes `{file:...}` in the raw config text before parsing. Lines 55-77: on a read failure it returns `InvalidError` with `bad file reference: "{file:...}" <path> does not exist` unless `input.missing === "empty"`. The `disabled` flag is never consulted at that stage. Effect: one missing secret file for a disabled server takes down the whole config, so every agent fails, not only the MCP entry.
- Exceptions in the same file: `{file:}` tokens on a line whose text before the token starts with `//` are skipped (lines 44-50; live-confirmed with a commented token); `~/` expands via `os.homedir()`; content is trimmed, so an empty file yields an empty string. `{env:VAR}` never errors: an unset variable becomes `""` (lines 31-34).
- Fix options: create every referenced secret file (empty is acceptable for disabled servers), or switch disabled servers to `{env:VAR}`, or comment out the disabled entries. The `{file:}` references for enabled servers (exa, tavily, firecrawl, apify, brightdata, scrapegraph) need real files anyway.

### 5b. `disabled` is the correct v2 key

Verdict: VERIFIED. `packages/schema/src/mcp.ts:33` (`LocalConfig`) and `:58` (`RemoteConfig`) both define `disabled: Schema.Boolean.pipe(optional)`. There is no `enabled` field. Live: `"disabled": true` produced no connection attempt; `"enabled": false` on an otherwise identical entry was silently ignored and OpenCode tried to connect (`mcp connect failed ... ENOTFOUND example.invalid`). `packages/core/src/config/normalize.ts` `normalizeMcp` only treats `enabled` as legacy for old-style entries that contain nothing else.

### 5c. Model resolves

Verdict: VERIFIED. `opencode models` against the running service lists `opencode/muse-spark-1.3-contributor-free` among the `opencode/` models (read-only listing). In the isolated env, `opencode run --standalone --model opencode/muse-spark-1.3-contributor-free "reply with exactly: OK"` returned `OK` (exit 0), while `--model opencode/does-not-exist-free` returned `provider.no-route: Model unavailable` (exit 1). `opencode models --standalone` printed nothing in the isolated env, so the list check rests on the live-service listing and the run test.

## 6. Everything else in the staged file

Checked by loading a copy of the staged file (plugins removed, all MCP servers forced to `disabled`, dummy secrets present) in the isolated env: exit 0, no schema errors, the `researcher` agent answered.

- CONTRADICTED: the top-level `agent` block (`explore.disable`, `general.disable`) collides with `agents.explore` and `agents.general`. Live warning: `configuration normalization diagnostic path=$.agents.explore kind=conflict action="retained native value over legacy value"` (same for `general`). Source: `normalize.ts` `mergeMaps` (lines 731-743) replaces the whole legacy object with the native one, so the legacy `disable: true` (migrated to `disabled` in `v1/config/migrate.ts` `migrateAgent`) is lost. Live: with the staged shape, `opencode run --agent explore` succeeded (the agent is still enabled). With `agents.explore.disabled: true` and `agent` removed, the same command failed with `Agent not found: "explore"`. Correct form: put `"disabled": true` inside `agents.explore` and `agents.general` (and drop their `model` overrides if the agents are meant to be off), and delete the `agent` block.
- VERIFIED (syntax): `provider/model#variant`. `packages/schema/src/model.ts` `Ref.parse` splits on the first `#` after the provider slash; `opencode run --help` says "provider/model#variant". A bogus variant (`#bogusvariant`) loaded without error, so a clean load does not prove `xhigh` exists for muse-spark. UNVERIFIABLE: that `xhigh` is a real variant of that model.
- VERIFIED: `agents` as the native key, with fields `description`, `mode` (`subagent`), `model`, `system`, `disabled` (`packages/schema/src/config/agent.ts:11-22`). Live: `--agent researcher` ran and issued `execute` tool calls.
- VERIFIED: `mcp.servers` and `mcp.servers.*.timeout.{startup,catalog,execution}` (`TimeoutConfig`, `packages/schema/src/mcp.ts:7-15`); `oauth: false` (`RemoteConfig`, line 57); `type` `remote` or `local`, `command` as an array, `environment`, `headers`.
- VERIFIED: top-level `shell` (string), `lsp: true` and `formatter: true` (both `Union([Boolean, Record])` in `packages/schema/src/config/lsp.ts` and `formatter.ts`), and the `$schema` string. `C:\Users\Lance\.local\pwsh\pwsh.exe` exists on this machine.
- VERIFIED: `//` comments inside the JSON. The staged file contains one; comments parse (live test) and a `{file:}` token inside a comment line is skipped.
- VERIFIED (npm): `oh-my-opencode-slim` latest is 2.2.25, the version tested in `researcher-subagent-mcp.md`. The unpinned name in the staged file follows future releases.
- VERIFIED (local CLI): `codegraph serve --mcp` ("Run as MCP server (stdio transport)"). `firefox-devtools-mcp --help` lists `--profilePath`, `--firefoxPath`, `--viewport`, `--toolPreset` (yargs also accepts the kebab forms used in the staged file; the help examples use `--firefox-path`). On `--tool-preset all`: "Privileged modules (mozilla/all) require MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1", so `all` may lack privileged tools unless that variable is set for the process.
- VERIFIED (URL): `https://learn.microsoft.com/api/mcp`, from `MicrosoftDocs/mcp` README line 39 (raw: https://raw.githubusercontent.com/MicrosoftDocs/mcp/main/README.md). It is keyless, matching the staged entry with no headers.

## Unverified

- Live behaviour of the real remote MCP servers (Exa, Tavily, Firecrawl, Apify, Browserbase, Microsoft Learn): no real keys were used, so header acceptance is proven from vendor docs and server source, not by a live call. Tavily's Bearer form has only README backing.
- Apify: the effect of the unknown selector `get-actor-output` on the hosted server (inferred from `tools_loader.ts`, not tested), and whether `https://mcp.apify.com/?tools=` (slash before `?`) behaves identically to the documented `https://mcp.apify.com?tools=`.
- Whether `xhigh` is a valid variant for `opencode/muse-spark-1.3-contributor-free` (an invalid variant does not error at load).
- `@slkiser/opencode-quota@next`: npm shows `next` = 5.0.0-beta.1 while `latest` = 4.10.6. Loading and compatibility with OpenCode v2.0.18 were not tested (plugins were excluded from the isolated runs to avoid installs). `oh-my-opencode-slim` under v2 was covered by `researcher-subagent-mcp.md`.
- Local servers `agentql`, `brightdata`, `scrapegraph`, `codegraph`, `firefox-devtools` were not launched under OpenCode (they need keys, network installs or a browser); only their command and flag names were checked.
- The `researcher` agent's `system` text and the `timeout` values (30000, 60000, 120000) are choices, not facts, and have no upstream source.
- Which disabled servers will be re-enabled, and whether their secret files will exist by then (see 5a).