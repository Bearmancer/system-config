# MCP tool catalog: deterministic listing on OpenCode 2.0.19

Date: 2026-09-29. Host: Windows 10, OpenCode v2.0.19 (`opencode --version`), background service on 127.0.0.1:49374.

## Question

Is there a deterministic way (no LLM in the loop, no secret read by us) to list every tool name for each of the 17 configured MCP servers? Candidates: (a) `opencode mcp` subcommands, (b) an OpenCode server HTTP GET route, (c) `opencode debug` subcommands, (d) `opencode run --format json` event streams. Then: which tool names does the deep-research skill chain rely on, and are they present in the live catalog?

## Answer in brief

- No native OpenCode route lists MCP tool names. (a), (b), (c) return server connection status only; (d) requires a model turn.
- Working native command: `opencode api mcp.list` (server names and status only).
- Working fallback, outside OpenCode: send MCP `tools/list` directly to each server. This gave live lists for 11 servers with no secret (9 from the 15 in opencode.jsonc that started or answered with no key, plus context7 and gh_grep, which the oh-my-opencode-slim plugin defines with `oauth: false`). Five servers (agentql, apify, brightdata, exa, tavily) refuse to start or answer without a key, and aws-mcp was deliberately not probed (needs the user's AWS credentials). Their names come from upstream docs or source and are labelled as such.
- The unauthenticated Firecrawl list has 3 tools, while the Firecrawl README documents many more. The authenticated catalog OpenCode sees is therefore not confirmed.
- Two skill mismatches found: ScrapeGraph `crawl_start` / `crawl_get_status` / `monitor_*` are absent from the installed ScrapeGraph MCP (v1.0.1); Tavily `tavily-extract` conflicts with the upstream source name `tavily_extract`.

## Candidate results

### (a) `opencode mcp` subcommands

Source: live `opencode mcp --help`, `opencode mcp add --help`, `opencode mcp list`.

- Subcommands: `list` (list configured servers and status), `add`, `auth`, `logout`. None lists tools.
- `opencode mcp list` output (trimmed):

```
✓ agentql              connected
✓ apify                connected
...
✓ tavily               connected
```

- Docs agree: https://opencode.ai/v2/docs/mcp-servers/ documents `opencode mcp list` as "List servers and their current connection state" and no tool-listing command. The `/mcps` view is interactive (TUI) and not scriptable.
- Verdict: no tool names. Servers only.

### (b) Server HTTP API

Sources: live `opencode api --help`, live `GET /openapi.json` from the running service (saved and inspected with `jaq`), https://opencode.ai/v2/docs/api (states the spec is at `/v2/openapi.json`; the live service serves it at `/openapi.json`), https://opencode.ai/docs/server/ (v1 docs).

- `opencode api <operation | method path...>` calls the running service and handles its own authentication. It needs no credentials from us. Flags: `--standalone`, `--server`, `--data`, `--header`, `--param`.
- Working commands:

```
opencode api mcp.list
opencode api GET /api/mcp                       # PowerShell
MSYS_NO_PATHCONV=1 opencode api GET /api/mcp    # git-bash
```

- Sample output (trimmed):

```
{"location":{"directory":"C:\\Users\\Lance"},"data":[{"name":"agentql","status":{"status":"connected"}}, ... ,{"name":"microsoft-learn","status":{"status":"connected"},"integrationID":"mcp_1a89ae3fd386875c"}, ...]}
```

- The live OpenAPI spec (title "opencode HttpApi", 3.1.0) has these MCP routes only: `GET /api/mcp` (`mcp.list`), `GET /api/mcp/resource` (`mcp.resource.catalog`, resources and resource templates, not tools), and the experimental `PUT`/`DELETE /api/experimental/mcp/{server}`, `POST .../connect`, `POST .../disconnect`. The `Mcp.Server` schema has only `name`, `status`, `integrationID`; `Mcp.Status.Connected` is `{status: "connected"}`. No schema or route carries tool names. `/api/agent` (`Agent.Info`) lists permissions, not tools.
- The v1 docs name `GET /experimental/tool/ids`, `GET /experimental/tool` and `GET /mcp`. On the live v2 service `opencode api GET /experimental/tool/ids` and `GET /mcp` return the web app HTML (SPA fallback), so those routes are not served. The v1 route still exists in the SDK source (`gh search code "tool/ids" --repo anomalyco/opencode` hits `packages/sdk/js/src/gen/sdk.gen.ts` and `packages/web/src/content/docs/server.mdx`), but it is not on the v2 spec.
- `GET /api/debug/location` (`debug.location.list`) and `GET /api/location` (`location.get`) return directories and a project id only.
- Routes deliberately not called: `config.get` (`GET /api/config`) could return resolved config including `{file:...}` secret substitutions; `rpc.call` is a plugin dispatch with unknown effect; every non-GET route.
- Verdict: status only, no tool names.

### (c) `opencode debug`

Source: live `opencode debug --help`.

- Subcommands: `agents`, `config`, `paths`. `agents` prints agent definitions and permissions (ran it, no tool catalog). `paths` prints directories. `config` ("List configuration sources") was not run because resolved configuration may contain substituted secrets; only its `--help` was read.
- The v2 CLI docs page https://opencode.ai/v2/docs/cli/ documents only `debug paths`.
- Verdict: no tool names.

### (d) `opencode run --format json`

Source: live `opencode run --help` (`--format choice: default, json`), live OpenAPI spec.

- `opencode run` sends a message to a model, so it is LLM-driven by definition and fails the constraint. Not run.
- The event stream (`GET /api/event`, `event.subscribe`) has payload type `V2EventEncoded`. A scan of every enum value in the spec for "mcp" or "tool" found only `McpServerNotFoundError`, `InstructionEntryValueTooLargeError`, and the message part types `tool` and `tool-calls`. No event type carries a catalog. Tool names appear only after a model calls a tool.
- Verdict: unsuitable.

## Fallback: direct MCP `tools/list`

Method: a small Python stdlib client (`initialize`, `notifications/initialized`, `tools/list` with pagination) launched with a scrubbed environment (PATH and system variables only, no secret variables) using the exact `command` arrays and URLs from `C:\Users\Lance\.config\opencode\opencode.jsonc` (`mcp.servers`; the secrets files were never opened). Remote servers were contacted with no Authorization header. The script lives at `C:\Users\Lance\AppData\Local\Temp\claude\C--Users-Lance\da241933-6515-4cda-b768-7c74d6cfe33a\scratchpad\probe.py` (session scratch, may be purged). Usage:

```
python probe.py http <name> <url>
python probe.py stdio <name> <command> [args...]
```

Sample output:

```
{"server": "microsoft-learn", "ok": true, "tools": ["microsoft_docs_search", "microsoft_code_sample_search", "microsoft_docs_fetch"]}
{"server": "agentql", "ok": false, "error": "RuntimeError('stdout closed')", "stderr_head": "Error: AGENTQL_API_KEY environment variable is required\n"}
```

Caveats: this reports what the server returns to this client, not what OpenCode registers. OpenCode names tools `<server>_<tool>` with characters other than letters, numbers, `_`, `-` replaced by `_` (https://opencode.ai/v2/docs/mcp-servers/). An authenticated session may see more tools than an unauthenticated one. Firefox DevTools was launched with a temp profile, `--headless`, `--tool-preset all` (config uses the same preset with the real profile); the tool list came back without launching a browser (no firefox.exe process remained).

## Catalog: server and tool names

Basis column: LIVE = returned by `tools/list` from the configured command or URL in this session; LIVE-unauth = remote answered without credentials, authenticated list unverified; DOCS = upstream README or source; CONFIG = pinned by the `?tools=` query in the config URL.

| Server | Basis | Tools (upstream names) |
|---|---|---|
| browserbase | LIVE-unauth (6) | start, end, navigate, act, observe, extract |
| codegraph | LIVE (1) | codegraph_explore |
| context7 | LIVE-unauth (2) | resolve-library-id, query-docs |
| firecrawl | LIVE-unauth (3) | firecrawl_scrape, firecrawl_search, firecrawl_parse |
| firefox-devtools | LIVE (48, preset all) | list_pages, new_page, navigate_page, select_page, close_page, get_page_text, take_snapshot, resolve_uid_to_selector, clear_snapshot, click_by_uid, hover_by_uid, fill_by_uid, drag_by_uid_to_uid, fill_form_by_uid, upload_file_by_uid, press_key, type_text, list_network_requests, get_network_request, set_network_cache, list_console_messages, clear_console_messages, screenshot_page, screenshot_by_uid, list_downloads, clear_downloads, set_download_behavior, accept_dialog, dismiss_dialog, navigate_history, set_viewport_size, get_firefox_output, get_firefox_info, close_firefox_session, install_extension, uninstall_extension, profiler_is_active, profiler_start, profiler_stop, screencast_start, screencast_stop, evaluate_script, enable_debugger, list_scripts, get_script_source, set_logpoint, remove_logpoint, get_logpoint_results |
| gh_grep | LIVE-unauth (1) | searchGitHub |
| github | LIVE (45, token-less start) | add_comment_to_pending_review, add_issue_comment, add_reply_to_pull_request_comment, assign_copilot_to_issue, create_branch, create_or_update_file, create_pull_request, create_repository, delete_file, fork_repository, get_commit, get_file_contents, get_label, get_latest_release, get_me, get_release_by_tag, get_tag, get_team_members, get_teams, issue_read, issue_write, list_branches, list_commits, list_issue_fields, list_issue_types, list_issues, list_pull_requests, list_releases, list_repository_collaborators, list_tags, merge_pull_request, pull_request_read, pull_request_review_write, push_files, request_copilot_review, search_code, search_commits, search_issues, search_pull_requests, search_repositories, search_users, sub_issue_write, update_issue_comment, update_pull_request, update_pull_request_branch |
| microsoft-learn | LIVE-unauth (3) | microsoft_docs_search, microsoft_code_sample_search, microsoft_docs_fetch |
| playwright | LIVE (25) | browser_close, browser_resize, browser_console_messages, browser_handle_dialog, browser_emulate_media, browser_evaluate, browser_file_upload, browser_drop, browser_find, browser_fill_form, browser_press_key, browser_type, browser_navigate, browser_navigate_back, browser_network_requests, browser_network_request, browser_run_code_unsafe, browser_take_screenshot, browser_snapshot, browser_click, browser_drag, browser_hover, browser_select_option, browser_tabs, browser_wait_for |
| scrapegraph | LIVE (8, v1.0.1, key-less start) | markdownify, smartscraper, searchscraper, smartcrawler_initiate, smartcrawler_fetch_results, scrape, sitemap, agentic_scrapper |
| sequential-thinking | LIVE (1) | sequentialthinking |
| exa | CONFIG + DOCS (live 403) | web_search_exa, web_fetch_exa, web_search_advanced_exa, agent_run |
| apify | CONFIG + DOCS (live 401) | apify--rag-web-browser (Actor tool), search-actors, call-actor; auto-injected when call-actor is present: get-actor-run, get-dataset-items, get-key-value-store-record, abort-actor-run |
| tavily | DOCS (live 401) | tavily_search, tavily_extract, tavily_crawl, tavily_map, tavily_research, tavily_feedback (source of the npm server; the hosted remote may differ) |
| agentql | DOCS (server exits without key) | extract-web-data |
| brightdata | DOCS (server exits without token) | search_engine, search_engine_batch, scrape_as_markdown, scrape_batch, discover, plus many `web_data_*` tools; full list not captured |
| aws-mcp | NOT PROBED | tool discovery is dynamic through the proxy with SigV4 and local AWS credentials; no static list documented |

## Deep-research skill chain: tools relied on

Sources: `C:\Users\Lance\.claude\skills\deep-research\SKILL.md` (Fast path steps 1-9, House rules) and `C:\Users\Lance\.claude\skills\deep-research\references\fleet.md`. OpenCode-side name = `<server>_<tool>` per the sanitization rule.

| Skill reference | Server | OpenCode-side name | Status |
|---|---|---|---|
| Step 1 `tavily-extract` | tavily | tavily_tavily_extract (if source spelling holds) | UNVERIFIED live (401). Spelling conflict: skill and README say `tavily-extract`, source says `tavily_extract` |
| Step 2 `firecrawl_scrape` | firecrawl | firecrawl_firecrawl_scrape | PRESENT (live, unauthenticated list) |
| Step 3 `web_fetch_exa` | exa | exa_web_fetch_exa | EXPECTED, not live-verified: pinned in config URL and documented in README; live probe 403 |
| Step 4 `scrape` (`stealth: true`) | scrapegraph | scrapegraph_scrape | PRESENT (tool); `stealth` parameter not inspected |
| Step 5 `apify/rag-web-browser` | apify | apify_apify--rag-web-browser, or `call-actor` with `actor: "apify/rag-web-browser"` | NAME DIFFERS: README tool name is `apify--rag-web-browser`; the slash form is an Actor ID. Live unverified (401) |
| Step 5 `search-actors`, `call-actor` | apify | apify_search-actors, apify_call-actor | EXPECTED, not live-verified (config-pinned, README) |
| Step 6 AgentQL (no tool named) | agentql | agentql_extract-web-data | Server connected in `opencode mcp list`; tool name from README only. fleet.md says "disabled by default", but it is connected |
| Step 7 Firefox DevTools MCP | firefox-devtools | firefox-devtools_* | PRESENT (48 tools live) |
| Step 7 `@playwright/cli` | none | not an MCP tool | OUT OF SCOPE: a CLI, distinct from the connected `playwright` MCP (25 `browser_*` tools) |
| Step 8 Bright Data Web Unlocker (no tool named) | brightdata | brightdata_scrape_as_markdown | UNVERIFIED live (server needs token to start); README only |
| Step 9 Browserbase (no tool named) | browserbase | browserbase_* | PRESENT (6 tools live, unauthenticated list). fleet.md says "disabled by default", but it is connected |
| House rule `firecrawl_map`, `firecrawl_crawl` | firecrawl | firecrawl_firecrawl_map, ..._crawl | NOT CONFIRMED: in Firecrawl README, absent from the unauthenticated live list |
| House rule `firecrawl_monitor_*` | firecrawl | firecrawl_firecrawl_monitor_* | NOT CONFIRMED: same as above |
| Fleet `firecrawl_research_*` | firecrawl | firecrawl_firecrawl_research_* | NOT CONFIRMED: same as above |
| House rule ScrapeGraph `crawl_start`, `crawl_get_status` | scrapegraph | scrapegraph_crawl_start ... | MISSING in installed scrapegraph-mcp v1.0.1 (live has `smartcrawler_initiate`, `smartcrawler_fetch_results`) |
| House rule ScrapeGraph `monitor_*` | scrapegraph | scrapegraph_monitor_* | MISSING in the live list |
| Fleet "Microsoft Learn" (no tool named) | microsoft-learn | microsoft-learn_microsoft_docs_search etc. | PRESENT (3 tools) |
| Fleet "Context7 not wired" | context7 | context7_* | Skill text is stale: connected, 2 tools (resolve-library-id, query-docs). `context7` and `gh_grep` come from the `oh-my-opencode-slim` plugin built-ins, not `opencode.jsonc` |

## Sources

- OpenCode v2 API reference: https://opencode.ai/v2/docs/api
- OpenCode v2 MCP servers doc (naming rule, `catalog` timeout, `opencode mcp list`): https://opencode.ai/v2/docs/mcp-servers/
- OpenCode v2 CLI doc: https://opencode.ai/v2/docs/cli/
- OpenCode v1 server doc (routes absent from v2): https://opencode.ai/docs/server/
- OpenCode source hits for the v1 route: `gh search code "tool/ids" --repo anomalyco/opencode`
- Live commands run this session: `opencode --help`, `opencode mcp --help`, `opencode mcp list`, `opencode debug --help`, `opencode debug agents`, `opencode debug paths`, `opencode api mcp.list`, `opencode api location.get`, `opencode api debug.location.list`, `opencode api GET /openapi.json`
- Tavily server source: https://github.com/tavily-ai/tavily-mcp (`src/index.ts`, `README.md`)
- AgentQL README: https://github.com/tinyfish-io/agentql-mcp
- Bright Data README: https://github.com/brightdata/brightdata-mcp
- Exa README: https://github.com/exa-labs/exa-mcp-server
- Apify README: https://github.com/apify/apify-mcp-server
- Firecrawl README: https://github.com/firecrawl/firecrawl-mcp-server
- AWS MCP proxy README: https://github.com/aws/mcp-proxy-for-aws
- Plugin built-in MCP definitions (context7, gh_grep URLs): `C:\Users\Lance\.cache\opencode\npm\oh-my-opencode-slim@latest\1790593106915\node_modules\oh-my-opencode-slim\dist\index.js`
- Config lines used: `C:\Users\Lance\.config\opencode\opencode.jsonc` lines 112-295 (`mcp.servers`, `type`, `command`, `url` only; exa line 116, apify line 152)

## Unverified

- Authenticated tool catalogs for firecrawl, browserbase, context7, gh_grep, microsoft-learn: probes were unauthenticated; the authenticated list may be larger (Firecrawl in particular: README documents `firecrawl_map`, `firecrawl_crawl`, `firecrawl_monitor_*`, `firecrawl_research_*`, none in the 3-tool unauthenticated list).
- exa, apify, tavily live tool names: remote answered 403/401 without credentials. Names come from README, source, or the config `?tools=` filter. The hosted Tavily remote may use different spellings from the npm source (`tavily_extract` vs README `tavily-extract`).
- agentql and brightdata: servers exit at startup without a key; tool names are README-only. Bright Data's full `web_data_*` list not captured.
- aws-mcp: not probed (needs the user's AWS credentials); tool names unknown.
- What OpenCode itself registers: OpenCode's own catalog (after permission filtering or the `?tools=` filters) was not observed. `<server>_<tool>` names are derived from the documented rule, not read from OpenCode.
- Effect of the config `timeout.catalog` values on which servers time out in OpenCode: not tested.
- ScrapeGraph `scrape` supporting `stealth: true`: parameter schema not inspected.
- Cause of the Bash failure `opencode api GET /mcp` ("Expected an operation name or an HTTP method and path"): `MSYS_NO_PATHCONV=1` makes `GET /api/mcp` work, which points to git-bash path rewriting, but the rewritten argument was not printed.
- `opencode debug config` and `GET /api/config` output was not inspected (secret-substitution risk), so whether they list tools is unconfirmed.
- Whether an OpenCode plugin or a supported non-experimental route could expose the catalog: not investigated (would modify config).