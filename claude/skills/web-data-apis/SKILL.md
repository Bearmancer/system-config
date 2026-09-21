---
name: web-data-apis
description: "Capability audit + house rules for the web-data MCP fleet wired into OpenCode (14 servers: Firecrawl, Tavily, Exa, Brave, Crawl4AI, ScrapeGraphAI, AgentQL, Apify, Bright Data, Browserbase, Firefox DevTools, Context7, Microsoft Learn, Dappier). Holds the decision table that maps a job's capability needs — JS-heavy pages, academic papers, structured extraction, bulk-cheap crawling, anti-bot/geo-blocked pages, realtime feeds, first-party docs — to the right server, with a use-when rule per row. Consult it before any scrape, extract, search, crawl, or monitor call, whenever two providers could do the same job, and whenever a tool fails on credit exhaustion."
---

# Web data APIs

MCP servers only — no vendor ships an OpenCode skill, plugin, or agent for these. Tools auto-expose to every agent; nothing else to install.

## Capability audit — pick by capability, not by habit

| Server               | Capability tags                                                                                     | Use when                                                                                                             |
| -------------------- | --------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Firecrawl            | js-render, clean-markdown, site-crawl, site-map, llm-extract, search, change-monitor, paper-research | Default workhorse for a known URL or a whole-site harvest that must return clean markdown. Also the academic-papers chain (`firecrawl_research_*` — confirmed registered). |
| Tavily               | llm-tuned-search, synthesized-answer, extract, crawl, map                                           | A question goes in and a cited answer plus ranked URLs must come out — first stop for query-unknown factual lookups. |
| Exa                  | semantic-search, similarity-search, long-form/academic-leaning index, fetch, agent-run              | The query is conceptual rather than keyword-shaped, or you need papers and long-form that keyword engines miss.      |
| Brave                | independent-crawler-index, web/news/image/video search, local-poi                                   | Cross-checking when Tavily and Exa agree — they can share upstream bias; also local and place queries.               |
| Crawl4AI             | self-hosted, bulk-cheap, playwright-crawl, markdown                                                 | Bulk crawling where volume would burn paid credits and slower turnaround is acceptable.                              |
| ScrapeGraphAI        | ai-extract, scrape, search, async-crawl (start→poll), monitor — 17 tools confirmed                   | Schema-shaped extraction across many pages, or a crawl that outlives one tool call.                                  |
| AgentQL              | structured-extraction, nl→typed-json, single-url, browser-rendered                                  | You already know the page and want one specific JSON shape out of it — that is its only job.                         |
| Apify                | purpose-built actors (social / e-commerce / maps / reviews), platform-structured                    | A platform has a dedicated actor that beats any generic scrape of it.                                                |
| Bright Data          | anti-bot, proxy-network, geo-routing, unlocker, dataset-apis                                        | The page is WAF/Cloudflare/geo-blocked and cheaper tiers already returned 403 or empty.                              |
| Browserbase          | stateful-session, login-flows, multi-step-interaction, hosted-browser                               | The data sits behind a login or a multi-step flow and state must persist across steps.                               |
| Firefox DevTools MCP | js-heavy-pages, browser-control, dom/a11y-snapshot, console+network inspection, screenshot, js-eval | A JS-gated page you must see rendered, or you need the network/console truth behind what the page displays.          |
| Context7             | library-api-docs, version-pinned                                                                    | A coding task needs current SDK/framework docs. Not a fact-checking source for course verification.                  |
| Microsoft Learn      | first-party ms/azure docs, code-samples, full-page-fetch                                            | Anything Microsoft, Azure, or .NET — first-party docs beat a general web search every time.                          |
| Dappier              | realtime-feeds (news / finance / sports / weather), licensed-publisher content, recommendations     | Freshness is the actual requirement — today's price, score, or headline — not general web recall.                    |

### Quick index

- JS-heavy page → Firecrawl → Firefox DevTools MCP → Browserbase
- Academic papers → Exa → Tavily → Firecrawl `firecrawl_research_*` (confirmed registered)
- Structured extraction → AgentQL (single URL) / ScrapeGraphAI (many URLs)
- Bulk-cheap → Crawl4AI
- Anti-bot / geo-blocked → Bright Data → Browserbase
- First-party docs → Microsoft Learn (MS stack) / Context7 (libraries)

### House rules (operational detail behind the table)

- One URL, plain text/markdown → `scrape` (ScrapeGraphAI) or `firecrawl_scrape`.
- One URL, structured JSON from a natural-language description → `agentql extract-web-data` (its only job) or `scrapegraph extract`.
- Whole-site harvest → `firecrawl_map` before `firecrawl_crawl` with an explicit limit, or ScrapeGraphAI `crawl_start` → `crawl_get_status` (start returns an id; poll it — never assume the first call has results).
- Recurring page-change watching → `firecrawl_monitor_*` or ScrapeGraphAI `monitor_*`.
- ScrapeGraphAI `credits` doubles as the connection/auth smoke test for that server.
- Context7 (library/API doc lookup) is out of scope for course fact-checking — it serves coding tasks only.

## Fleet (wiring/ops — keyed subset only; the capability table above covers all 15)

| Server        | Config entry  | Key env var (in OpenCode)                          | Pool service name | Tools                                                                    |
| ------------- | ------------- | -------------------------------------------------- | ----------------- | ------------------------------------------------------------------------ |
| Firecrawl     | `firecrawl`   | `FIRECRAWL_API_KEY`                                | `firecrawl`       | scrape, map, crawl, search, extract, monitor_*                           |
| Tavily        | `tavily`      | `TAVILY_API_KEY`                                   | `tavily`          | tavily_search, tavily_extract, tavily_crawl, tavily_map, tavily_research |
| Exa           | `exa`         | none wired — bare remote URL, no `{env:EXA_API_KEY}` | `exa`             | web_search_exa, web_fetch_exa, web_search_advanced_exa, agent_run        |
| Dappier       | `dappier`     | `DAPPIER_API_KEY`                                  | `dappier`         | `dappier_real_time_search`, `dappier_ai_recommendations`                 |
| AgentQL       | `agentql`     | `AGENTQL_API_KEY`                                  | `agentql`         | `extract-web-data`                                                       |
| ScrapeGraphAI | `scrapegraph` | `SGAI_API_KEY` (mapped from `SCRAPEGRAPH_API_KEY`) | `scrapegraph`     | scrape, extract, search, crawl__, monitor__, credits, history_*          |

Dappier and ScrapeGraphAI run via `uvx` (Python); AgentQL via `cmd /c npx -y` (Node, Windows shim). First `uvx` launch per package pays a cold-start install: `~4s`.

## Music search

Looking up a release, recording, or work's metadata (catalog number, credits, dates, discography)? Source priority + banned streaming services: `references/music-search.md`. Never cite Spotify/Apple Music/Apple Classical/Amazon Music/Tidal/Deezer/Qobuz as a source — see that file for why and for the MusicBrainz → Discogs → Presto Classical → label-website order.

## Companion tool skills

The house rules above route to dedicated skills for some servers. Split across two roots — check both, neither is stale:

- `~/.agents/skills/`: `bright-data-mcp`, `scrape`, `browser`, `apify-ultimate-scraper`, `context7`, `just-scrape`
- `~/.config/opencode/skills/`: `web-search`, `answers`, `news-search`, `images-search`, `videos-search`, `suggest`, `spellcheck`, `local-place-search`, `local-pois`, `local-descriptions`, `bx`, `bx-search`, `llm-context` (Brave-backed skills)

## Keys + credit failover

Account pools live in `~/.secrets/.env`. **Never read that file.** Rotation mechanics, the hard-stop rule, and the sanctioned reader (`switch_api_key.py`) live in one place: `learning-course` skill's "API key failover" section (`SKILL.md`). Consult it there — not restated here.

**Exa is the one exception where rotation is a no-op.** `switch_api_key.py --service exa` rewrites the `EXA_API_KEY` pointer, but `opencode.jsonc`'s `exa` MCP entry is a bare remote URL (`https://mcp.exa.ai/mcp?tools=...`) with no `{env:EXA_API_KEY}` reference anywhere in it — confirmed by reading the config directly. Rotating the Exa key changes nothing until the config entry itself is fixed to reference the env var.

## Startup behaviour (matters when a server looks broken)

- Dappier: exits immediately if `DAPPIER_API_KEY` missing (`ValueError`).
- AgentQL: exits immediately if `AGENTQL_API_KEY` missing.
- ScrapeGraphAI: **starts with no key** and fails per-call instead — a silent-looking dead server is usually a missing key, not a broken package.
- Dappier needs its pin: `uvx --with "mcp<2" dappier-mcp`. Unpinned, uvx resolves `mcp` 2.x — where `FastMCP` was renamed to `MCPServer` — and the package dies on import (`ModuleNotFoundError: No module named 'mcp.server.fastmcp'`). Keep the `--with` flag in the config entry.
- Hosted alternatives exist (Dappier `https://mcp.dappier.com/mcp?apiKey=…`; ScrapeGraphAI `https://mcp.scrapegraphai.com/mcp` bearer) — not used; local stdio keeps key handling uniform. ScrapeGraphAI's README flags that hosted URL as deprecating, so re-check before ever switching.
