# Fleet: route a web call

Order per capability: MCP tool the host carries -> vendor CLI -> POST script. Hosts carry different servers: list your tools first (this Claude cloud session: Firecrawl `scrape`/`search`/`research_*` only). OpenCode wiring: `~/.config/opencode/opencode.jsonc` `mcp.servers`, keys from `secrets/<pool>`; OmO: `~/.omo/agent/mcp.json`, keys from user env. No skill `mcp.json` (senpi sends remote servers without auth). Exa URL lists all 4 tools; Apify URL enables actors, docs, runs, storage (no schedules/tasks/builds/dev: paid-key cost control) plus `apify/rag-web-browser`, `apify/web-fetch`, `get-actor-list`.

Detail lives in one file per vendor, read only the one you route to: `scrapers/<vendor>.md` (MCP tool names, CLI commands, POST endpoints + presets). On failure: `scrapers/keys-errors.md`.

## Pick by need

| Need | First | Then |
|---|---|---|
| Unknown-URL factual question, cited answer | Tavily `search` / `research` | Exa `answer`, ScrapeGraph `search`, Firecrawl `search` |
| Conceptual query, papers, similar pages | Exa `web_search_exa` | Firecrawl `research_*` (academic), `POST /findSimilar` |
| Known URL -> markdown | Firecrawl `scrape` | ScrapeGraph `scrape`, Tavily `extract` |
| Many known URLs | Firecrawl batch script | Tavily `extract` (list) |
| Whole site | `map` then `crawl` with limit (Firecrawl, Tavily) | ScrapeGraph `crawl` |
| Schema-shaped extraction | ScrapeGraph `extract` | Firecrawl `json` format, AgentQL |
| Site-specific data (Maps, social, retail) | Apify Actor | Bright Data `web_data_*` / `pipelines`, Firecrawl Alexandria |
| Page-change watch | Firecrawl monitor | ScrapeGraph monitor |
| JS-gated page, network truth | Firefox DevTools / Playwright | Browserbase |
| WAF / geo block | chain below | Bright Data |
| Code, library, repo question | Context7, gh_grep, Firecrawl `developer_search` | |
| Microsoft / Azure / .NET | Microsoft Learn MCP before any web search | |

## Capability map

M = MCP, C = CLI, S = dedicated script in `scripts/`, R = raw REST via `scripts/vendor_request.py`, - = none. `*` = not on this cloud host's MCP. Names and bodies: the vendor file. Tool names marked `(readme)` there come from vendor README/source, not a live `tools/list`; OpenCode registers `<server>_<tool>`.

| Vendor | search | fetch | extract | crawl | map | research / answer | batch / async | monitor | browser |
|---|---|---|---|---|---|---|---|---|---|
| Tavily | MCR | MCR | - | MCR | MCR | MCR | `tvly research --no-wait` | - | - |
| Firecrawl | MCR | MCR | M(json fmt) | M*CR | M*CR | M*CR agent, M papers | S batch | M*CR | - |
| Exa | MR | MR | - | - | - | M `agent_run`, S stop/cancel, S answer | S batches | R | - |
| ScrapeGraph | MCR | MCR | MCR | MCSR | M (legacy `sitemap`; none in v2 REST) | MCR search | S crawl mgmt | CR (hosted M untested) | - |
| Apify | MCR | MCR (rag-web-browser) | MCR (Actor) | Actor | Actor | - | MCR runs | R schedules | - |
| AgentQL | - | - | MR | - | - | - | - | - | - |
| Bright Data | MCR | MCR | - | - | - | - | M `scrape_batch`/`search_engine_batch`, S async Unlocker | - | - |
| Browserbase | CR | CR | M | - | - | S agent runs | S agent runs | - | MC |

## Bot-block chain

First step returning the target content wins. Credit/auth failure: rotate that server's key first (SKILL.md), then move on. Blocked: next step.

1. Tavily `tavily_extract`.
2. Firecrawl `scrape` `proxy: "auto"`, `maxAge: 0`.
3. Exa `web_fetch_exa` (cached); `SOURCE_NOT_AVAILABLE` -> next.
4. ScrapeGraph `scrape` via CLI `--stealth` / REST `fetchConfig.stealth: true` (+5 credits per page); legacy MCP stealth support unverified.
5. Apify `apify--rag-web-browser`, or site Actor via `search-actors` + `call-actor`.
6. AgentQL `extract-web-data`.
7. Firefox DevTools MCP, or Playwright `browser_navigate` -> `browser_snapshot`.
8. Bright Data: MCP `scrape_as_markdown`, then CLI `brightdata scrape`, then `POST /request` / async script; 502 `reject_block` -> retry once.
9. Browserbase (paid tier for CAPTCHA).

Host lacks a step's MCP and CLI: REST via `vendor_request.py`: Tavily `POST /extract {"urls":[U]}`; Firecrawl `POST /scrape {"url":U,"proxy":"auto","maxAge":0}`; Exa `POST /contents {"urls":[U],"text":true}`; Apify `POST /actors/apify~rag-web-browser/run-sync-get-dataset-items {"query":U}`; ScrapeGraph and Bright Data rows in their vendor files. Nothing returns content: URL blocked, never guess.

## POST scripts

PEP 723 stdlib only: `uv run scripts/<name>.py ...`. Key from `~/.config/opencode/secrets/<pool>`, JSON to stdout, HTTP error -> exit 1 with `{"status","code","message"}` on stderr. Redirects refused.

| Script | Does |
|---|---|
| `vendor_request.py <pool> <METHOD> </path> [--body J\|@f] [--param k=v] [--header k=v]` | any REST call; pools exa, firecrawl, brightdata, browserbase, scrapegraph, tavily, apify, agentql; base URL and auth fixed per pool |
| `exa_answer.py`, `exa_agent_run.py`, `exa_batches.py` | Exa answer; agent stop/cancel; batches (beta) |
| `firecrawl_batch_scrape.py` | start / status / cancel / errors |
| `scrapegraph_crawl.py` | start / status / stop / resume / delete / pages |
| `brightdata_unlocker.py` | async Unlocker start / result `--wait` |
| `browserbase_agent_run.py` | agent run start / status |

Not scripted because MCP or CLI covers it: everything else in the capability map.

## House rules

- One URL, markdown: `firecrawl_scrape` or ScrapeGraph `scrape`.
- Whole site: `map` before `crawl`, explicit limit.
- Tavily `extract_depth: advanced` = depth only; Exa `livecrawl` = freshness only; neither bypasses blocks.
- Wired but not covered by a vendor file: Context7 (`resolve-library-id`, `query-docs`), gh_grep (`searchGitHub`) via `oh-my-opencode-slim`; Microsoft Learn (`microsoft_docs_search`, `microsoft_code_sample_search`, `microsoft_docs_fetch`). Not wired (pool entries only): Dappier, Brave, Crawl4AI.
- Matrix source with endpoint research and unverified items: system-config `.claude/docs/research/mcp-cli-post-matrix.md`, catalog `mcp-tool-catalog.md`.
