# ScrapeGraphAI

Pick: schema-shaped extraction, many-page crawl outliving one call, page-change monitors. Stealth = `fetchConfig.stealth` (+5 credits per page / call / monitor tick).
Costs: scrape md 1, json 5, screenshot 2, branding 25; extract 5; crawl 2 + per page; monitor tick = scrape cost, +5 on change.

## MCP (hosted v2)

- `https://mcp.scrapegraphai.com/mcp`, Streamable HTTP, 20 tools, auth per `keys-errors.md` (Bearer verified live 2026-10-01 with `credits` and `scrape`; no header = 401 `missing authorization header`, `Authorization` without `Bearer` = 401 `no token payload`, bad key = `auth_invalid_key`).
- Tools: `scrape`, `extract`, `search`; `crawl_start`, `crawl_get`, `crawl_pages`, `crawl_stop`, `crawl_resume`, `crawl_delete`; `monitor_create`, `monitor_list`, `monitor_get`, `monitor_update`, `monitor_pause`, `monitor_resume`, `monitor_delete`, `monitor_activity`; `credits`, `history_list`, `history_get`. No sitemap, map or schema-generation tool: pass `schema` to extract/search.
- Tool call cap 60 s: long work = `crawl_*` / `monitor_*`.

## CLI `just-scrape` (npm, Node >=22; `--json` everywhere; key: see `keys-errors.md`)

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

## Routes

All documented v2 routes exist except `/schema` (documented, 404 at probe 2026-10-01); no `/sitemap` or `/map`. Smoke test: `vendor_request.py scrapegraph GET /credits`, then `POST /scrape` on `https://example.com`. Docs index: https://docs.scrapegraphai.com/llms.txt.
