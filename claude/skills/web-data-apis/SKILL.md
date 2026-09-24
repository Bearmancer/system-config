---
name: web-data-apis
description: "Capability audit + house rules for the web-data MCP fleet wired into OpenCode (14 servers: Firecrawl, Tavily, Exa, Brave, Crawl4AI, ScrapeGraphAI, AgentQL, Apify, Bright Data, Browserbase, Firefox DevTools, Context7, Microsoft Learn, Dappier). Holds the decision table that maps a job's capability needs — JS-heavy pages, academic papers, structured extraction, bulk-cheap crawling, anti-bot/geo-blocked pages, realtime feeds, first-party docs — to the right server, with a use-when rule per row. Consult it before any scrape, extract, search, crawl, or monitor call, whenever two providers could do the same job, and whenever a tool fails on credit exhaustion."
---

# Web data APIs

## Capability audit — pick by capability, not by habit

| Server               | Use when                                                                                                             |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Firecrawl            | Default workhorse for a known URL or a whole-site harvest that must return clean markdown. Also the academic-papers chain (`firecrawl_research_*`). |
| Tavily               | A question goes in and a cited answer plus ranked URLs must come out — first stop for query-unknown factual lookups. |
| Exa                  | The query is conceptual rather than keyword-shaped, or you need papers and long-form that keyword engines miss.      |
| Brave                | Cross-checking when Tavily and Exa agree — they can share upstream bias; also local and place queries.               |
| Crawl4AI             | Bulk crawling where volume would burn paid credits and slower turnaround is acceptable.                              |
| ScrapeGraphAI        | Schema-shaped extraction across many pages, or a crawl that outlives one tool call.                                  |
| AgentQL              | You already know the page and want one specific JSON shape out of it — that is its only job.                         |
| Apify                | A platform has a dedicated actor that beats any generic scrape of it.                                                |
| Bright Data          | The page is WAF/Cloudflare/geo-blocked and cheaper tiers already returned 403 or empty.                              |
| Browserbase          | The data sits behind a login or a multi-step flow and state must persist across steps.                               |
| Firefox DevTools MCP | A JS-gated page you must see rendered, or you need the network/console truth behind what the page displays.          |
| Context7             | A coding task needs current SDK/framework docs.                                                                       |
| Microsoft Learn      | Anything Microsoft, Azure, or .NET — first-party docs beat a general web search every time.                          |
| Dappier              | Freshness is the actual requirement — today's price, score, or headline — not general web recall.                    |

### Quick index

- JS-heavy page → Firecrawl → Firefox DevTools MCP → Browserbase
- Academic papers → Exa → Tavily → Firecrawl `firecrawl_research_*`
- Structured extraction → AgentQL (single URL) / ScrapeGraphAI (many URLs)
- Bulk-cheap → Crawl4AI
- Anti-bot / geo-blocked → Bright Data → Browserbase
- First-party docs → Microsoft Learn (MS stack) / Context7 (libraries)

### House rules (operational detail behind the table)

- One URL, plain text/markdown → `scrape` (ScrapeGraphAI) or `firecrawl_scrape`.
- One URL, structured JSON from a natural-language description → `agentql extract-web-data` (its only job) or `scrapegraph extract`.
- Whole-site harvest → `firecrawl_map` before `firecrawl_crawl` with an explicit limit, or ScrapeGraphAI `crawl_start` → `crawl_get_status` (start returns an id; poll it — never assume the first call has results).
- Recurring page-change watching → `firecrawl_monitor_*` or ScrapeGraphAI `monitor_*`.
- Context7 serves coding tasks only — not a fact-checking source for course verification.

## Music metadata lookups

Looking up a release, recording, or work's metadata (catalog number, credits, dates, discography)? `references/discography-search.md` covers entry points (MusicBrainz, Discogs), tracing each candidate to its underlying session, duration verification, and citation sources — genre-agnostic, reusable by any music task. `deep-cut-classical` points here for its own discography lookups.

## Keys + credit failover (11 keyed services)

Research-tool account pools live in `~/.secrets/.env`. **Never read that file — no Read, no cat, no rg, not even for variable names. `scripts/switch_api_key.py` (this skill) is its only sanctioned reader**, and it prints nothing but account names + sha256 fingerprints; key material never enters chat, logs, or context.

Trigger: a research call fails on credit/quota exhaustion — Tavily usage limit, Firecrawl insufficient credits / 402, Exa credits exhausted, key suddenly 401s after working earlier. Transient rate limit: retry once first; rotate only on credit/quota/payment/auth signatures.

Rotate (exact order):

1. Run: `python <path-to-web-data-apis-skill>/scripts/switch_api_key.py --service <tavily|exa|firecrawl|dappier|agentql|scrapegraph|context7|brave|apify|brightdata|browserbase> --next`
2. Report the script's output line to the user verbatim (already masked).
3. Tell the user to **restart OpenCode** — MCP servers read env at startup only.
4. **HARD STOP.** No retries with the old key, no further tool calls, no carrying on the remaining work this session. Resume after restart.

Controls: `--list` peeks pool + active account (no write); `--service all --list` covers every supported service; `--set <ACCOUNT>` pins one; `--next --dry-run` previews. Pointer = the User-scope env var (`TAVILY_API_KEY`, `EXA_API_KEY`, `FIRECRAWL_API_KEY`, `CONTEXT7_API_KEY`, `BRAVE_API_KEY`, `APIFY_TOKEN`, `BRIGHTDATA_API_KEY`, `BROWSERBASE_API_KEY`); OpenCode's `{env:...}` references resolve against it. If any other loader re-imports `.env` wholesale, rerun the script.

**Not in the failover pool, by design:** Dappier, AgentQL, ScrapeGraphAI — keyed and wired, see their own usage detail in the capability table (ScrapeGraphAI also has `just-scrape`).

Config entries, key env vars, exact tool lists, Exa's rotation-is-a-no-op quirk, and per-server startup-failure symptoms: `references/fleet-ops.md`.
