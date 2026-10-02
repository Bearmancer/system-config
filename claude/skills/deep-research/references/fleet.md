# Fleet: pick server by capability

Wired in OpenCode (`~/.config/opencode/opencode.jsonc` `mcp.servers`, keys from `secrets/` files) and OmO (`~/.omo/agent/mcp.json`, same servers, keys from user env vars). No skill sidecar `mcp.json`: senpi sends skill-declared remote servers without auth. Exa MCP URL pins 4 tools (`web_search_exa`, `web_fetch_exa`, `web_search_advanced_exa`, `agent_run`), Apify pins 3 (`apify/rag-web-browser`, `search-actors`, `call-actor`); keep pins. Other hosts expose whatever MCP servers they carry; same rows apply by capability.

| Server | Use when |
|---|---|
| Firecrawl | Known URL or whole-site harvest to clean markdown; academic chain `firecrawl_research_*`; chain step 2 (`proxy: "auto"`). |
| Tavily | Question in, cited answer + ranked URLs out; first stop for query-unknown factual lookups; chain step 1 (`tavily_extract`). |
| Exa | Conceptual (not keyword) query; papers and long-form keyword engines miss; chain step 3 (`web_fetch_exa`). |
| ScrapeGraphAI | Schema-shaped extraction across many pages; crawl outliving one call; chain step 4 (`stealth`). |
| Apify | Site-specific Actor or Actor `apify/rag-web-browser` (tool `apify--rag-web-browser`); chain step 5. |
| AgentQL | Query-shaped extraction; chain step 6. |
| Firefox DevTools | JS-gated page seen rendered; network/console truth behind page; chain step 7. |
| Bright Data | WAF/Cloudflare/geo-blocked after cheaper tiers fail; chain step 8. |
| Browserbase | Hosted browser, CAPTCHA (paid tier); chain step 9. |
| Microsoft Learn | Anything Microsoft, Azure, .NET: before general web search. |

Also connected, loaded by the `oh-my-opencode-slim` plugin (not `opencode.jsonc`): Context7 (`resolve-library-id`, `query-docs`), gh_grep (`searchGitHub`).

Not wired (pool entries only in `switch_api_key.py`; wire before use): Dappier, Brave, Crawl4AI.

## Routing: MCP first, then vendor CLI, then POST script

- Order per capability: MCP tool; none -> vendor CLI; none -> POST script.
- POST script column: `-` = MCP or CLI covers it, no script. `uv run scripts/<name>.py ...` = POST-only capability, run the script (PEP 723, stdlib only; key from `~/.config/opencode/secrets/<pool>`; JSON to stdout; HTTP error -> exit 1, JSON line on stderr with `status` + vendor `code`). `none` = no route found.
- MCP names without `(live)` come from vendor README/source, not a live authenticated `tools/list`. Names are upstream; OpenCode registers `<server>_<tool>`.
- CLIs installed: `tvly`, `firecrawl`, `apify`, `brightdata`, `just-scrape`, `browse`. AgentQL: no usable CLI (`agentql-cli` only scaffolds SDK projects). Exa: no CLI.
- Endpoints, bodies, sources: system-config `.claude/docs/research/mcp-cli-post-matrix.md` (PR #36). Tool catalog: system-config `.claude/docs/research/mcp-tool-catalog.md` (PR #35).

| Server | Capability | MCP tool | CLI command | POST script |
|---|---|---|---|---|
| Exa | search | `web_search_exa`, `web_search_advanced_exa` | none | - |
| Exa | fetch | `web_fetch_exa` | none | - |
| Exa | answer | none | none | `uv run scripts/exa_answer.py "<q>"` |
| Exa | deep research | `agent_run` (`ultra` effort via MCP unverified) | none | - |
| Exa | agent stop/cancel | none | none | `uv run scripts/exa_agent_run.py stop\|cancel <id>` (stop: ultra only) |
| Exa | batches | none | none | `uv run scripts/exa_batches.py start\|status\|cancel` (beta; 403 `FEATURE_DISABLED` until Exa enables batches for the team, live 2026-09-30) |
| Exa | crawl/map | none | none | none |
| Tavily | search, extract, crawl, map, research | `tavily_search`, `tavily_extract`, `tavily_crawl`, `tavily_map`, `tavily_research` (live) | `tvly search`, `extract`, `crawl`, `map`, `research` (`--no-wait`, `status <id>`, `poll <id>`) | - |
| Firecrawl | search, scrape | `firecrawl_search` (live), `firecrawl_scrape` (live) | `firecrawl search`, `firecrawl scrape` | - |
| Firecrawl | crawl, map | `firecrawl_crawl`, `firecrawl_check_crawl_status`, `firecrawl_map` | `firecrawl crawl [--wait \| --cancel]`, `firecrawl map` | - |
| Firecrawl | batch scrape | none | none | `uv run scripts/firecrawl_batch_scrape.py start\|status\|cancel\|errors` |
| Firecrawl | agent, research papers, monitors | `firecrawl_agent`, `firecrawl_agent_status`, `firecrawl_research_*`, `firecrawl_monitor_*` | `firecrawl agent`, `firecrawl research`, `firecrawl monitor` | - |
| Apify | search Actors, run Actor | `search-actors`, `apify--rag-web-browser`, `call-actor` | `apify actors search`, `apify actors call` | - |
| Apify | run status, dataset, abort | `get-actor-run`, `get-dataset-items`, `abort-actor-run` | `apify runs info`, `runs wait`, `runs abort`, `apify datasets get-items` | - |
| Apify | builds, schedules, tasks | opt-in categories, not enabled in config | `apify builds ...`, `apify task run`, `apify api POST /v2/schedules` | - |
| Apify | crawl/map | none dedicated (Actor via `call-actor`) | none dedicated | - |
| Bright Data | search | `search_engine`, `search_engine_batch` | `brightdata search` | - |
| Bright Data | fetch | `scrape_as_markdown`, `scrape_as_html`, `scrape_batch` | `brightdata scrape` | - |
| Bright Data | discover, platform data | `discover`, `web_data_*` | `brightdata discover`, `brightdata pipelines` | - |
| Bright Data | async Unlocker | none | `brightdata scrape --async` (rejected by API, see POST) | `uv run scripts/brightdata_unlocker.py start --zone <zone>` then `result <response_id> --wait` (zone needs async on; `mcp_unlocker` works, live 2026-09-30). CLI `scrape --async` returns 400 `"async" is not allowed` (live 2026-09-30): no CLI id reaches `result` |
| Bright Data | crawl/map | none | none | none |
| ScrapeGraph | scrape, extract, search | `scrape`, `extract`, `search` (live 2026-10-01 on remote endpoint) | `just-scrape scrape`, `extract`, `search` | - |
| ScrapeGraph | crawl start, poll | `crawl_start`, `crawl_get` (live) | `just-scrape crawl` | managed crawl (stop, resume, delete, pages): `uv run scripts/scrapegraph_crawl.py start\|status` |
| ScrapeGraph | crawl management (stop, resume, delete, pages) | `crawl_stop`, `crawl_resume`, `crawl_delete`, `crawl_pages` (live) | none | `uv run scripts/scrapegraph_crawl.py stop\|resume\|delete\|pages <id>`; ids come from the script's `start` |
| ScrapeGraph | history, credits | `history_list`, `history_get`, `credits` (live) | none | - |
| ScrapeGraph | monitors | `monitor_list`, `monitor_create`, `monitor_get`, `monitor_activity`, `monitor_pause`, `monitor_resume`, `monitor_update`, `monitor_delete` (live) | `just-scrape monitor` | - |
| Browserbase | search, fetch | none | `browse cloud search`, `browse cloud fetch` | - |
| Browserbase | browser session | `start`, `end`, `navigate`, `act`, `observe`, `extract` (live, unauthenticated list) | `browse open`, `snapshot`, `click`, `fill`, `screenshot`, `browse cloud sessions` | - |
| Browserbase | agent runs | none | none documented | `uv run scripts/browserbase_agent_run.py start\|status` |
| AgentQL | extract | `extract-web-data` | none | - |

## House rules

- One URL, markdown: `firecrawl_scrape` or ScrapeGraph `scrape`.
- Whole site: `firecrawl_map` before `firecrawl_crawl` with explicit limit (CLI `firecrawl map` / `firecrawl crawl` otherwise); or ScrapeGraph `crawl_start` then poll `crawl_get`.
- Page-change watching: `firecrawl_monitor_*` or ScrapeGraph `monitor_create` (MCP and CLI `just-scrape monitor`).
- Tavily `extract_depth: advanced` = depth only, not a bypass. Exa `livecrawl` = freshness knob, not bot-block bypass.

## Keys and ops

| Server | Config entry | Key env var | Pool name |
|---|---|---|---|
| Tavily | `tavily` | `TAVILY_API_KEY` | `tavily` |
| Firecrawl | `firecrawl` | `FIRECRAWL_API_KEY` | `firecrawl` |
| Exa | `exa` | `EXA_API_KEY` | `exa` |
| ScrapeGraphAI | `scrapegraph` | `SGAI_API_KEY` (from `SCRAPEGRAPH_API_KEY`) | `scrapegraph` |
| Apify | `apify` | `APIFY_TOKEN` | `apify` |
| AgentQL | `agentql` | `AGENTQL_API_KEY` | `agentql` |
| Bright Data | `brightdata` | `API_TOKEN` (from `BRIGHTDATA_API_KEY`) | `brightdata` |
| Browserbase | `browserbase` | `BROWSERBASE_API_KEY` | `browserbase` |

- Every server takes its key as a bearer header or env var; the active key sits in `~/.config/opencode/secrets/<pool name>`. `switch_api_key.py --next` rewrites that file; on OpenCode the watcher reconnects only the changed server. OmO: see SKILL.md Key rotation.
- Missing secrets file breaks config load: `switch_api_key.py --service all --materialize` creates every missing one.
- ScrapeGraph serves from the remote MCP `https://mcp.scrapegraphai.com/mcp` with `Authorization: Bearer <key>`; the local `scrapegraph-mcp.exe` wrapper points at `api.scrapegraphai.com`, whose Cloudflare edge fails every TLS handshake from Windows (Schannel, OpenSSL, BoringSSL alike, `SEC_E_ILLEGAL_MESSAGE` / `SSLV3_ALERT_HANDSHAKE_FAILURE` / `ERR_SSL_VERSION_OR_CIPHER_MISMATCH`) while `www.scrapegraphai.com` on the same IPs works, so the local wrapper is unusable, not misconfigured. CLI `just-scrape` reaches the API fine.
- ScrapeGraphAI starts without key, fails per call: silent dead server = missing key. Its free plan meters per call: `credits` reports the balance before a batch.
- `uvx` servers pay ~4 s cold install on first launch.

## Error codes per service

Rotate on "Out of credit" and on "Bad key" after a working key. Move to next chain step on "Blocked". Retry once on "Rate limit". Source: R3, `.claude/docs/research/mcp-chain-unknowns.md`.

| Service | Bad key | Out of credit | Blocked | Rate limit |
|---|---|---|---|---|
| Tavily | unverified | unverified | empty result + `Failed to fetch url`, no status code (live drill, system-config#20) | unverified |
| Firecrawl | 401 | 402 | 403, empty body or challenge page in result (still 1 credit) | 429 |
| Exa | 401 | 402 | `SOURCE_NOT_AVAILABLE` per URL | 429 + `Retry-After` |
| ScrapeGraph | 401 `auth_missing_key`; 403 `auth_invalid_key` | 402 `insufficient_credits` | undocumented | 429 `rate_limited` |
| Apify | 401 `invalid-token` / `token-not-provided` | 402 `not-enough-usage-to-run-paid-actor`, `monthly-usage-limit-too-low` (inferred) | check Actor run output | 429 `rate-limit-exceeded` |
| AgentQL | 401 `API Key Required` | unverified | unverified | unverified |
| Bright Data | 407 `client_10000`, `client_10002` (zone); 401 `client_10050` | 407 `client_10020` (suspended, negative balance); 502 `client_10100` (zone limit) | 502 `reject_block`, `resolve_failed_*` (retry, new peer); 403 `policy_*` = policy, not a block | undocumented |
| Browserbase | unverified | unverified | unverified | unverified |

- ScrapeGraph MCP wrapper raises `Error {status}: {body}` for any status >= 400: match status number and `insufficient_credits`.
- Unverified cell = no published code; treat any auth/credit-looking failure as rotate, then next step.
