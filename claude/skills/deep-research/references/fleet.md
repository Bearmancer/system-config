# Fleet: pick server by capability

Wired in OpenCode (`~/.config/opencode/opencode.jsonc` `mcp.servers`) and, for OmO, in the skill sidecar `mcp.json` (all except ScrapeGraph and Bright Data; see SKILL.md Key rotation step 5). Other hosts expose whatever MCP servers they carry; same rows apply by capability.

| Server | Use when |
|---|---|
| Firecrawl | Known URL or whole-site harvest to clean markdown; academic chain `firecrawl_research_*`; chain step 2 (`proxy: "auto"`). |
| Tavily | Question in, cited answer + ranked URLs out; first stop for query-unknown factual lookups; chain step 1 (`tavily-extract`). |
| Exa | Conceptual (not keyword) query; papers and long-form keyword engines miss; chain step 3 (`web_fetch_exa`). |
| ScrapeGraphAI | Schema-shaped extraction across many pages; crawl outliving one call; chain step 4 (`stealth`). |
| Apify | Site-specific Actor or `apify/rag-web-browser`; chain step 5. |
| AgentQL | Query-shaped extraction; chain step 6; `disabled` by default. |
| Firefox DevTools | JS-gated page seen rendered; network/console truth behind page; chain step 7. |
| Bright Data | WAF/Cloudflare/geo-blocked after cheaper tiers fail; chain step 8. |
| Browserbase | Hosted browser, CAPTCHA (paid tier); chain step 9; `disabled` by default. |
| Microsoft Learn | Anything Microsoft, Azure, .NET: before general web search. |

Not wired (pool entries only in `switch_api_key.py`; wire before use): Dappier, Context7, Brave, Crawl4AI.

## House rules

- One URL, markdown: `firecrawl_scrape` or ScrapeGraph `scrape`.
- Whole site: `firecrawl_map` before `firecrawl_crawl` with explicit limit; or ScrapeGraph `crawl_start` then poll `crawl_get_status` (start returns id only).
- Page-change watching: `firecrawl_monitor_*` or ScrapeGraph `monitor_*`.
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
- ScrapeGraphAI starts without key, fails per call: silent dead server = missing key.
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
