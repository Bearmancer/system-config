# Tool comparison: AgentQL vs Tavily vs Firecrawl vs Exa vs Dappier vs Browserbase + similars
Format: Chat + Markdown (binding gate). Cited-only, no live burn. Full matrix + depth.

## 1. One-line matrix

| Tool | One job | Wins when | Loses when | Cost shape | Entry routes |
|---|---|---|---|---|---|
| Tavily | Answer-oriented search + extract + map + crawl + research | Need grounded cited discovery fast; reranked chunks + filters | Need semantic similarity, JS-heavy dump, typed JSON | 1cr basic search; 2cr advanced; extract 1-2cr/5; crawl map+extract; research mini 4-110 / pro 15-250 | MCP tavily_search/extract/crawl/map/research; API/SDK full params; CLI tvly; skill reminder |
| Firecrawl | Search to scrape to crawl to extract to monitor, clean markdown | Need full-site ingest, changelog watch, structured dataset from known URLs | Need entity search, cheap SERP, single surgical field | 1cr/page flat; search 2cr/10 + scrape; monitor 1cr/page/check; extract +4/field-type | MCP scrape/map/crawl/search/extract/monitor; API/SDK + webhooks; self-host core |
| Exa | Semantic web index + highlights + verticals + agent_run | Conceptual query without keywords; people/company list-build; token-efficient highlights | Breaking exact-string, JS fetch, bulk cheap SERP | /search $7/1k; contents $1/1k/type; deep $12-15/1k; agent $0.012-1.00 + ACU/search/email/phone | MCP web_search/fetch/advanced/agent_run (subset); API full modes + livecrawl; no CLI |
| Dappier | Licensed realtime answer + curated recommendations | Breaking news/weather/ticker + rights-cleared feeds in one call | Need page content, crawl, diff watch | Fast search free; premium per-query publisher-priced, check catalog live | MCP real_time_search / ai_recommendations; LangChain/LlamaIndex/OpenAI/Zapier |
| AgentQL | Single-URL NL structured extraction + element actions | Surgical typed fields on JS/auth/interaction-heavy page | Need discovery crawl, bulk cheap, webhooks/scheduler | Trial 300; Starter 50/mo then $0.02/call; Pro $99 10k then $0.015; browser hrs extra; PDF per page | MCP extract-web-data (one-shot); REST query-data/document; SDK Playwright wrapper; debugger/playground/CLI |
| Browserbase | Managed Chromium fleet + Contexts + Identity + Stagehand + MCP | Stateful login/multi-step, agent QA with replay, Stagehand agents | Stateless single URL, bulk cheap markdown | Free/20/99/Scale; per-min 1-min min; fetch $1/1k ($4 proxy); extract $4/1k ($7 proxy); search $7/1k; proxy GB extra | MCP hosted/STDIO start/navigate/act/observe/extract/end; SDK Node/Python; REST sessions; CDP Playwright/Puppeteer/Selenium |
| Similars | See section 8 | Price, control, or token shape decides | — | — | — |

## 2. Per-tool specialties

### Tavily
- Search discovers, extract reads, map lists, crawl traverses+reads, research synthesizes. Rigor flow: search advanced 5-10 then extract selected.
- Answer mode: chunks (500 chars, chunks_per_source) vs raw_content full page vs include_answer LLM seed (verify, never trust alone). Agent default: advanced, chunks 3, max 5-10, domains prefer.
- Strengths: single key 180ms p50, rerank scores, firewall + governance, ecosystem.
- Pitfalls: MCP drops answer/auto/chunks/usage/safe; advanced silent via auto_parameters; research pro unbounded; cloud-only.
- URLs: https://docs.tavily.com, /llms.txt, /agents.md, /documentation/api-reference, /documentation/api-credits, /documentation/mcp, /documentation/tavily-cli.md

### Firecrawl
- v2 scrape (markdown/html/links/screenshot/json/branding/product/query) 1cr/page; crawl async + webhooks + errors endpoint; map 1cr/call (approximation, not exhaustive); search per-source limits; extract via scrape-json / batch / /v2/extract; monitor scheduled + NL goal + changeTracking git-diff free / json 5cr.
- JS auto + actions (max 50, wait 60s); proxy auto escalates once on 401/403/429; respects robots (Enterprise ignore); x.com via Grok 30cr.
- Rigor: maxAge 0 on verification; never assert completeness without errors endpoint; map-first cap spend; tag per cadence.
- URLs: https://docs.firecrawl.dev, /llms.txt, /features/scrape, /features/crawl, /features/map, /features/search, /features/llm-extract, /features/monitoring, https://www.firecrawl.dev/pricing

### Exa
- Modes auto/fast/instant/deep-lite/deep/deep-reasoning; neural = describe ideal page; auto misroutes hedges, force mode; scores not cross-comparable.
- Freshness via contents.maxAgeHours (0 fresh, -1 cache); livecrawl 2-3x cost +2-5s, validate len>500. Cached first, live only stale. Highlights 10x token cut; summary per-result LLM, never bulk.
- Verticals company/people require category set, reject date/exclude filters (encode in NL). agent_run async with effort pin, outputSchema bound arrays, previousRunId for more.
- URLs: https://exa.ai/docs, /docs/llms.txt, /pricing, /docs/reference/search-api-guide-for-coding-agents, /docs/reference/contents-api-guide, /docs/reference/agent-api-guide

### Dappier
- 2 tools only, no scrape/crawl. real_time_search: broad model am_01j06ytn18ejftedz6dyhz2b15 vs stock model am_01j749h8pbf7ns8r1bq9s2evrh (needs ticker, Polygon summary). ai_recommendations: dm sports/lifestyle/dogs/cats/green/WISH-TV, returns title/summary/url/author/pubdate/image/score, algorithm most_recent/semantic/most_recent_semantic/trending.
- Strengths: rights-cleared pay-per-query, finance/sports/news, LLM-agnostic.
- Pitfalls: opaque publisher pricing, summarized stocks, marketplace-only coverage, MCP exits without key, needs uvx pin mcp<2, score != factuality.
- URLs: https://docs.dappier.com/llms.txt, /api-reference/endpoint/real-time-search, /api-reference/endpoint/ai-recommendations, /quickstart, https://marketplace.dappier.com/marketplace

### AgentQL (TinyFish)
- Query shape defines output: {products[]{name price(integer)}}; [] list, (type) hint, (...) context.
- REST public pages; SDK full automation (login, pagination, stealth/proxy, credential cache); MCP thin one-shot.
- Pricing: trial 300; starter 50/mo then 0.02; pro 99 10k then 0.015; PDF per page.
- Wins surgical single page + click/type flows vs Firecrawl bulk vs ScrapeGraph prompt ease.
- Rigor: explicit fields + types, prompt context, standard mode for record, screenshot on miss, validate counts.
- URLs: https://docs.agentql.com/home, /agentql-query/query-intro, /scraping/scraping-data-api, /rest-api/api-reference, /integrations/mcp, https://www.agentql.com/pricing

### Browserbase
- Sessions (CDP URL, keep_alive to 6h, region, viewport, blockAds, record/log, allowedDomains) + Contexts (persist cookies/storage, sync delay) + Identity (Verified fingerprints, Cloudflare Signed Agents, managed/BYO proxy geolocation, solveCaptchas default, 1Password, 2FA handoff) + LiveView/Replay/logs + Search/Fetch/Extract ladder + Stagehand act/observe/extract/agent + Runtime functions + MCP.
- Pricing Free/Developer20/Startup99/Scale; per-min 1-min min; proxy GB meter; Verified/stealth paywalled Scale; cloud-only.
- Wins: authenticated portals (Contexts+proxy+captcha), agent QA (live+replay+logs), Stagehand/MCP agents. Loses stateless bulk vs Firecrawl, zero-orchestration vs AgentQL, dev-loop vs local Playwright.
- URLs: https://www.browserbase.com/, /pricing, https://docs.browserbase.com/platform/browser/getting-started/create-browser-session, /platform/identity/overview, /platform/browser/core-features/contexts, /platform/browser/observability/session-live-view, /integrations/mcp/setup, https://github.com/browserbase/stagehand

## 3. When-to-choose (skill vs MCP vs agent vs CLI)

- Tavily: MCP for shared org rollout (narrowed params ok). Agent/API for full params + usage + streaming. CLI tvly for ad-hoc. Skill as in-session reminder.
- Firecrawl: MCP for standard scrape/crawl/monitor. API/SDK for webhooks, batch, lockdown, maxAge 0. Self-host for control. CLI via API wrappers only.
- Exa: MCP for quick semantic/highlights. API for modes, livecrawl, verticals, agent_run. No CLI; agent_run is the agent.
- Dappier: MCP for both tools. API direct for catalog-priced premium. No scrape CLI; marketplace for model pick.
- AgentQL: MCP for one-shot field grab. REST for public bulk. SDK for auth/JS/interaction. Debugger/playground/CLI for query authoring.
- Browserbase: MCP for agent act/observe/extract. SDK/REST/CDP for owned Playwright code. Stagehand for resilient agents. Dashboard for live/replay debug.
- Rule: known URL + plain text = scrape; known URL + typed JSON = AgentQL/extract; whole site = Firecrawl crawl/map; change watch = monitor; query unknown = Tavily/Exa; realtime/licensed = Dappier; login/multi-step = Browserbase/SDK.

## 4. Rigor-without-burn (learning-course)

- Tier 0 cheap: cached search + highlights/chunks, score>0.7, dedupe canonical URL, wiki paired with second source.
- Tier 1 grounded: search-then-extract selected URLs, maxAge 0 / fresh only stale, full markdown, query-reranked.
- Tier 2 contested: 2+ independent domains + primary source + counter-search + observed_at/valid_at; code-verify behavior claims; unresolved/refuted to annex, never synthesis.
- Burn guards: map before crawl with explicit limit; never raw_content at scale; never summary for large N unused; pin agent effort + bound arrays; pilot-measure bytes-per-record 50-100 pages; block media/fonts; track cost per usable record.
- Failover: credit exhaustion 402/usage-limit/credits-out/sudden 401 = retry once if rate-limit, else Switch-ApiKey.ps1 -Service <tavily|exa|firecrawl|dappier|agentql|scrapegraph> -Next, report masked line, restart OpenCode, HARD STOP this session.

## 5. Local fleet wiring (web-data-apis)
- Firecrawl FIRECRAWL_API_KEY; Tavily TAVILY_API_KEY; Exa keyless MCP URL; Dappier DAPPIER_API_KEY + uvx pin mcp<2; AgentQL AGENTQL_API_KEY (MCP exits if missing); ScrapeGraph SGAI_API_KEY (starts keyless, fails per-call).
- Pools in ~/.secrets/.env, never read directly; only Switch-ApiKey.ps1.

## 6. Similars sweep (condensed)
- ScrapeGraphAI: NL scrape/extract/search/crawl/monitor; md 1cr extract 5cr; https://scrapegraphai.com/pricing
- Bright Data: 400M proxies + Scraper APIs; $1.5/1K PAYG pay-per-success; https://brightdata.com/pricing
- Apify: 60K Actors + CU; Starter 29 Scale 199; proxy $7-8/GB; https://apify.com/pricing
- Serper: cheapest SERP $0.30-1.00/1K; https://serper.dev/
- Brave: own 30B index + ZDR; $5/1K; https://api-dashboard.search.brave.com/documentation/pricing
- Jina: r.jina.ai / s.jina.ai; 10M free tokens; https://jina.ai/reader/
- Crawl4AI: Apache self-host $0; https://github.com/unclecode/crawl4AI
- Playwright-direct: $0 automation; https://playwright.dev/
- agent-browser: Rust CLI token-efficient; $0; https://agent-browser.dev/
- TCO: 100K defended pages BrightData ~$150 bundled beats Apify ~$350-2300 proxy-metered; Apify wins datacenter/lean/bursty/Actor-fit.

## 7. Trigger reliability (debug addendum)
- Verdict: behavioral, not plugin. Skill loads (dist/skills/ulw-research SKILL.md intact, opencode.jsonc registered). Miss = mode arbitration (ultrawork first-line won, marker dropped, wave pre-gate) + weak phrase match (space variant, bare fragment).
- Hard fix: explicit skill(name=ulw-research) first on any ulw turn; print ULTRAWORK line1 + ULW-RESEARCH line2 before tools; format gate WAIT before wave1; journal dir pre-spawn; match /ulw[\s$-]?research/i.

## 8. Sources appendix
- Wave-1 librarian returns bg_f8487700/bg_3ef195d6/bg_bdc04897/bg_ac164352/bg_a404893e; team browserbase-lane 3ef96b81, similars-lane ce6768b2 + LEAD1 aee6a503, trigger-debug c3028241. Journal dir C:\Users\Lance\.omo\ulw-research\20260920-042352.

## 9. Expansion trace
- Wave1: 5 librarians complete. Wave2: Browserbase + similars + LEAD1 TCO complete. Open: Verified lift, Model Gateway savings, Functions latency, 1M-page TCO, token-saving measure. Convergence: core ask covered, leads queued.
