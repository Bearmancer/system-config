# Bright Data

Pick: WAF/Cloudflare/geo-blocked after cheaper tiers fail (chain step 8); SERP; structured platform data (`web_data_*`). Key `BRIGHTDATA_API_KEY` (MCP env `API_TOKEN`), pool `brightdata`, Bearer. No crawl/map.

## MCP (readme; server needs token to start)

`search_engine`, `search_engine_batch`, `scrape_as_markdown`, `scrape_as_html`, `scrape_batch`, `discover`, many `web_data_*` (full list not captured).

## CLI `brightdata` / `bdata` (npm `@brightdata/cli`, Node >=20; `BRIGHTDATA_API_KEY` or `brightdata login`)

`brightdata search`, `scrape` (`--async` rejected live: 400 `"async" is not allowed`, so no CLI id reaches the result call), `discover`, `pipelines <type> <url>`.

## POST (base `https://api.brightdata.com`, preset `vendor_request.py brightdata`)

| Need | Call |
|---|---|
| fetch (Unlocker) | `POST /request` `{"zone":"web_unlocker1","url":U,"format":"raw","data_format":"markdown"}`; optional `country`, `render`; `data_format` markdown or screenshot; `POST /request?async=true` documented, retrieval endpoint unverified |
| search (SERP) | `POST /request` `{"zone":"serp_api1","url":"https://www.google.com/search?q=Q","format":"json"}` |
| async Unlocker | raw `POST /unblocker/req?zone=Z` `{"url":U}` -> `response_id`, `GET /unblocker/get_result?response_id=ID` (202 pending); or `scripts/brightdata_unlocker.py start --zone <zone> <url>` then `result <response_id> [--wait] [--timeout S]` (zone needs "Asynchronous requests" on; `mcp_unlocker` works, live 2026-09-30; polls 20 s, 10 s, then 5 s) |
| discover | `POST /discover` `{"query":Q}` then `GET /discover?task_id=ID` (contract from CLI source only; fields `intent`, `city`, `country`, `language`, `num_results`, `filter_keywords`, `include_content`, `remove_duplicates`, `start_date`, `end_date`) |
| platform data | `POST /datasets/v3/trigger?dataset_id=ID` `{"input":[{...}]}`; `GET /datasets/v3/progress/{snapshot}`; `GET /datasets/v3/snapshot/{snapshot}?format=json` |

Zones are account resources. 502 `reject_block`: retry once.
