# ScrapeGraph v2 live check, 2026-10-01 (no key: unauthenticated)

- Every route above except `/schema` answers 401 `auth_missing_key` = route exists: scrape, extract, search, crawl (+ `/{id}`, `/pages`, `/stop`, `/resume`), monitor (+ list, `/{id}`, PATCH, pause, resume, activity), credits, history (+ `/{id}`), validate.
- 404: `/sitemap`, `/map` (no map endpoint in v2), and `/schema` (documented at `POST /api/schema`, not served at probe time: docs ahead of deploy).
- Not verified (needs key): response shapes, `stealth` credit charge, `/monitor` PATCH body, hosted-MCP Bearer acceptance (if Bearer is refused, set `SGAI-APIKEY` header instead). Smoke with a key: `vendor_request.py scrapegraph GET /credits`, then `POST /scrape` on `https://example.com`.
- Trust the docs index https://docs.scrapegraphai.com/llms.txt; `api-reference/openapi.json` there is the stale v1 spec (`/v1/smartscraper`).
