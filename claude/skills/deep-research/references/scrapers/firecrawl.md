# Firecrawl

Pick: known URL or whole site to clean markdown; academic papers; proxy ladder `proxy: "auto"`; keyed typed data (Alexandria). Key `FIRECRAWL_API_KEY`, pool `firecrawl`, Bearer `fc-...`.

## MCP

| Host | Tools |
|---|---|
| This Claude cloud session (live) | `firecrawl_scrape`, `firecrawl_search`, `firecrawl_find_tools`, `firecrawl_developer_search`, `firecrawl_research_search_papers`, `_read_paper`, `_related_papers`, `_inspect_paper`. No crawl/map/agent/monitor tools here. |
| OpenCode / OmO hosted `https://mcp.firecrawl.dev/v2/mcp` | Live unauthenticated: `firecrawl_scrape`, `firecrawl_search`, `firecrawl_parse`. README adds (authenticated list unverified): `firecrawl_map`, `firecrawl_crawl`, `firecrawl_check_crawl_status`, `firecrawl_agent`, `firecrawl_agent_status`, `firecrawl_monitor_{create,list,get,update,delete,run,checks,check}`, `firecrawl_research_*` |

- `firecrawl_scrape`: `url`; `formats` markdown, html, rawHtml, screenshot, links, summary, json, query, branding, changeTracking, audio; `onlyMainContent`; `maxAge` (0 = live); `proxy` basic|stealth|enhanced|auto; `waitFor`; `includeTags`/`excludeTags`; `location`; `mobile`; `jsonOptions {prompt,schema}`; `queryOptions {prompt,mode}`; `profile {name,saveChanges}`; `parsers ["pdf"]`; `lockdown`; `zeroDataRetention`. `alexandria {provider,capability,options}` replaces `url` to run a typed data capability.
- `firecrawl_search`: `query`; `sources` web|images|news|alexandria|exchange; `categories` research|pdf|developer; `includeDomains` xor `excludeDomains`; `limit` <=100; `tbs`; `location`; `highlights`; `toolDetail`.
- `firecrawl_developer_search` `{query,k<=100,skills:"only"}`: repos, issues, merged PRs, READMEs, docs. `firecrawl_find_tools`: browse Alexandria providers (free); execute via scrape `alexandria`.
- Research: `search_papers {query,authors,categories,from,to,k<=500}`; `inspect_paper {paperId}`; `read_paper {paperId,question,k}`; `related_papers {seed_ids<=10,intent,mode similar|citers|references}`. IDs `arxiv:`, `pmid:`, `pmcid:`, `doi:`.

## CLI `firecrawl` (npm `firecrawl-cli`, Node >=22; `FIRECRAWL_API_KEY` or `firecrawl login`)

`firecrawl search`, `scrape` (several URLs concurrent), `crawl <url> [--wait | --cancel]`, `crawl <job-id>`, `map`, `agent "<prompt>" [--wait]` / `agent <job-id>`, `research`, `monitor`.

## POST (base `https://api.firecrawl.dev/v2`, preset `vendor_request.py firecrawl`)

| Need | Call |
|---|---|
| search / scrape / map | `POST /search` `{"query":Q,"limit":3}`; `POST /scrape` `{"url":U}`; `POST /map` `{"url":U}` |
| crawl | `POST /crawl` `{"url":U,"limit":10}`; `GET\|DELETE /crawl/{id}`; `GET /crawl/{id}/errors` |
| batch scrape | `scripts/firecrawl_batch_scrape.py start <url>... [--formats ...]` then `status\|cancel\|errors <id>` |
| agent | `POST /agent` `{"prompt":P,"maxCredits":100}`; `GET\|DELETE /agent/{jobId}` |
| papers | `GET /search/research/papers?query=Q&k=10` |
| monitors | `POST /monitor` and siblings |

Burn: map before crawl, set `limit`. Blocked page still costs 1 credit.
