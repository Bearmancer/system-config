# ScrapeGraphAI

Pick: schema-shaped extraction, many-page crawl outliving one call, page-change monitors. Stealth = `fetchConfig.stealth` (+5 credits per page / call / monitor tick).
Key: `SGAI_API_KEY`, pool `scrapegraph`. Header `SGAI-APIKEY`. Costs: scrape md 1, json 5, screenshot 2, branding 25; extract 5; crawl 2 + per page; monitor tick = scrape cost, +5 on change.

## MCP: hosted v2 (config mirrors point here; legacy local 1.0.1 retired)

- Hosted v2 MCP (docs 2026-10-01): `https://mcp.scrapegraphai.com/mcp`, Streamable HTTP, 20 tools, auth `Authorization: Bearer sgai-...` / `SGAI-APIKEY` / `X-API-Key` or Google OAuth. Unauthenticated call returns 401 `missing authorization header` (live). Mirrors send the pool key as Bearer; acceptance untested (no key in CI/cloud).
- Legacy local `scrapegraph-mcp` 1.0.1 (PyPI, last release, v1-style, 8 tools): `scrape`, `markdownify`, `smartscraper` (= extract), `searchscraper` (= search), `smartcrawler_initiate`, `smartcrawler_fetch_results`, `sitemap`, `agentic_scrapper`. Hosts still running it use these names.
- Hosted tools: `scrape`, `extract`, `search`; `crawl_start`, `crawl_get`, `crawl_pages`, `crawl_stop`, `crawl_resume`, `crawl_delete`; `monitor_create`, `monitor_list`, `monitor_get`, `monitor_update`, `monitor_pause`, `monitor_resume`, `monitor_delete`, `monitor_activity`; `credits`, `history_list`, `history_get`. Gone vs legacy (per hosted docs): `sitemap`, `agentic_scrapper`, `generate_schema` (pass `schema` to extract/search).
- Tool call cap 60 s: long work = `crawl_*` / `monitor_*`.

## CLI `just-scrape` (npm, Node >=22; `SGAI_API_KEY`; `--json` everywhere)

| Need | Command |
|---|---|
| scrape | `just-scrape scrape <url> [-f markdown,html,links,images,summary,branding,screenshot,json] [-p prompt] [--schema J] [--html-mode normal\|reader\|prune] [--scrolls N] [-m auto\|fast\|js] [--stealth] [--country iso]` |
| extract | `just-scrape extract <url> -p <prompt> [--schema J] [--scrolls N] [--stealth] [--mode] [--cookies J] [--headers J] [--country]` |
| search | `just-scrape search <q> [-p prompt] [--num-results 1-20] [--schema J] [--country] [--time-range past_hour\|past_24_hours\|past_week\|past_month\|past_year] [--format markdown\|html]` |
| crawl | `just-scrape crawl <url> [--max-pages 50] [--max-depth 2] [--max-links-per-page 10] [--allow-external] [--include-patterns J] [--exclude-patterns J] [-f fmt] [--stealth]`: starts and polls to the end; no stop/resume/delete |
| monitor | `just-scrape monitor create --url U --interval 1h [--name N] [--webhook-url U] [-f fmt]`; `list`; `get\|pause\|resume\|delete --id I`; `update --id I --interval 2h`; `activity --id I [--limit N] [--cursor C]` |
| account | `just-scrape credits`; `history [service] [id] [--page N --page-size N]` (services scrape, extract, search, monitor, crawl); `validate` |

## POST (host `https://v2-api.scrapegraphai.com/api`, preset `vendor_request.py scrapegraph`)

| Need | Call |
|---|---|
| balance, key check | `GET /credits`; `GET /validate` (health) |
| scrape | `POST /scrape` `{"url":U,"formats":[{"type":"markdown"}],"fetchConfig":{"stealth":true}}` |
| extract | `POST /extract` `{"url":U,"prompt":P,"schema":{...}}` (one of url/html/markdown) |
| search | `POST /search` `{"query":Q,"prompt":P,"numResults":3}` |
| crawl | `scripts/scrapegraph_crawl.py start <url> [--max-pages N]` then `status\|stop\|resume\|delete\|pages <id>` |
| monitor | `POST /monitor` `{"url":U,"name":N,"interval":"*/30 * * * *","formats":[{"type":"markdown"}]}`; `GET /monitor`; `GET\|PATCH\|DELETE /monitor/{id}`; `POST /monitor/{id}/pause\|resume`; `GET /monitor/{id}/activity` |
| history | `GET /history?service=scrape&limit=20`; `GET /history/{id}` (crawl page body via page `scrapeRefId`) |

Optional header `SGAI-Session-Id` groups a workflow in history. Script usage: `uv run scripts/vendor_request.py scrapegraph POST /scrape --body '...'`.

## Live check

Dated audit (2026-10-01, unauthenticated): `.claude/docs/research/scrapegraph-live-check.md` in system-config. Summary: all documented v2 routes exist except `/schema` (documented, 404); no `/sitemap` or `/map`. Smoke with a key: `vendor_request.py scrapegraph GET /credits`, then `POST /scrape` on `https://example.com`. Docs index https://docs.scrapegraphai.com/llms.txt; its `api-reference/openapi.json` is the stale v1 spec.
