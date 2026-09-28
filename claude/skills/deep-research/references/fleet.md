# Fleet: pick server by capability

Wired in OpenCode (`~/.config/opencode/opencode.json` `mcp.servers`). Claude Code sessions expose whatever MCP servers they carry; same rows apply by capability.

| Server | Use when |
|---|---|
| Firecrawl | Known URL or whole-site harvest to clean markdown; academic chain `firecrawl_research_*`; bot-block step 1 (`proxy: "auto"`). |
| Tavily | Question in, cited answer + ranked URLs out; first stop for query-unknown factual lookups. |
| Exa | Conceptual (not keyword) query; papers and long-form keyword engines miss. |
| ScrapeGraphAI | Schema-shaped extraction across many pages; crawl outliving one call; bot-block step 2 (`stealth`). |
| Firefox DevTools | JS-gated page seen rendered; network/console truth behind page; bot-block step 3. |
| Bright Data | WAF/Cloudflare/geo-blocked after cheaper tiers fail; bot-block step 4. |
| Microsoft Learn | Anything Microsoft, Azure, .NET: before general web search. |

Not wired (pool entries only in `switch_api_key.py`; wire before use): Dappier, AgentQL, Context7, Brave, Apify, Browserbase, Crawl4AI.

## House rules

- One URL, markdown: `firecrawl_scrape` or ScrapeGraph `scrape`.
- Whole site: `firecrawl_map` before `firecrawl_crawl` with explicit limit; or ScrapeGraph `crawl_start` then poll `crawl_get_status` (start returns id only).
- Page-change watching: `firecrawl_monitor_*` or ScrapeGraph `monitor_*`.
- Tavily `extract_depth: advanced` and Exa `livecrawl` = depth/freshness knobs, not bot-block bypass.

## Keys and ops

| Server | Config entry | Key env var | Pool name |
|---|---|---|---|
| Firecrawl | `firecrawl` | `FIRECRAWL_API_KEY` | `firecrawl` |
| Tavily | `tavily` | `TAVILY_API_KEY` (in URL) | `tavily` |
| Exa | `exa` | none: bare remote URL | `exa` |
| ScrapeGraphAI | `scrapegraph` | `SGAI_API_KEY` (mapped from `SCRAPEGRAPH_API_KEY`) | `scrapegraph` |
| Bright Data | `brightdata` | `BRIGHTDATA_API_KEY` | `brightdata` |

- Exa rotation = no-op: `exa` entry carries no `{env:EXA_API_KEY}`; rotating changes nothing until config references the var.
- ScrapeGraphAI starts without key, fails per call: silent dead server = missing key.
- `uvx` servers pay ~4 s cold install on first launch.
