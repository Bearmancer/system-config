# Tavily

Pick: question in, cited answer + ranked URLs out; first stop for unknown-query factual lookups; chain step 1 (`tavily_extract`). Key `TAVILY_API_KEY`, pool `tavily`, Bearer `tvly-...`. Always call with the key; no keyless use.

## MCP (names from npm server source (readme); hosted remote spelling unverified, docs prose says `tavily-search`)

`tavily_search`, `tavily_extract`, `tavily_crawl`, `tavily_map`, `tavily_research`, `tavily_feedback`. `extract_depth: advanced` = depth, not a bot-block bypass.

## CLI `tvly` (PyPI `tavily-cli`; `uv tool install tavily-cli`; `TAVILY_API_KEY` or `tvly login`)

`tvly search`, `extract`, `crawl`, `map`, `research` (`--no-wait`, `status <id>`, `poll <id>`).

## POST (base `https://api.tavily.com`, preset `vendor_request.py tavily`)

| Need | Call |
|---|---|
| search | `POST /search` `{"query":Q}` |
| extract | `POST /extract` `{"urls":[U]}` |
| crawl / map | `POST /crawl` `{"url":U}`; `POST /map` `{"url":U}` |
| research (async) | `POST /research` `{"input":Q,"model":"mini\|pro\|auto"}` -> 201 + `request_id`; `GET /research/{request_id}` -> 202 pending, 200 done/failed |

Blocked fetch = empty result + `Failed to fetch url`, no status code.
