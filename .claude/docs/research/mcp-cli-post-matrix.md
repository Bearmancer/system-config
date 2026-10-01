# MCP vs CLI vs direct POST matrix for the deep-research skill fleet

Date: 2026-09-29. Scope: issue #33 steps 1-2 (research only). Every claim below was read from a primary source (vendor API docs or OpenAPI spec, vendor CLI docs or README, npm or PyPI registry, or source code) on this date. No API that needs a key was called and nothing was installed.

> Update 2026-10-01: ScrapeGraph now documents a hosted v2 MCP (`https://mcp.scrapegraphai.com/mcp`, 20 tools incl. `crawl_*`, `monitor_*`, `credits`, `history_*`), so section 4 row 7 (crawl management) is covered by MCP, which the configs now use. Exa `/findSimilar` and `/monitors*` have no MCP or CLI (POST-only). A generic REST preset `scripts/vendor_request.py` was added (dedicated scripts remain); current routing lives in `claude/skills/deep-research/references/fleet.md` and `references/scrapers/`.

## Questions

Per service (Exa, Tavily, Firecrawl, Apify, Bright Data, ScrapeGraphAI, Browserbase, AgentQL):

1. Direct HTTP API: for each capability the deep-research skill uses (search, extract or fetch a URL, crawl or map, deep research or answer, async jobs), what is the exact endpoint (method and URL), auth header format, and one minimal request body? Verify these candidates specifically:
   - Exa `POST /answer` (does an "Ultra" or research tier exist? also `POST /research` if present)
   - Tavily `POST /research`
   - Firecrawl `POST /v2/batch/scrape`
   - Apify builds, schedules and actor-tasks endpoints
   - Bright Data `POST /request` and the Web Unlocker endpoint
2. Official CLI: does the vendor ship one? Package name, install command, Windows support, auth mechanism.
3. MCP vs CLI vs POST: one table, service by capability, columns MCP tool name, CLI command, POST endpoint, with "none" where it does not exist. MCP names start from the live catalog in `.claude/docs/research/mcp-tool-catalog.md` (it lives on the `research-drill-catalog-topgrade` branch, PR #35, commit f95ea40, and is not on master yet).
4. Which capabilities exist only as a POST (no MCP tool, no CLI command)? Each becomes a child issue labelled "needs py script".

## Answers in brief

- Exa `POST /answer`: verified. It has no Ultra tier. Its `model` enum is `exa`, `exa-pro`, `exa-research`, `exa-fast`. "Ultra" exists only as `effort: "ultra"` on the Agent API (`POST /agent/runs`). `POST /research` is dropped: no such path in Exa's OpenAPI spec.
- Tavily `POST /research`: verified (async, `201` plus `request_id`, poll `GET /research/{request_id}`). It also has an MCP tool and a CLI command, so it is not POST-only.
- Firecrawl `POST /v2/batch/scrape`: verified, with `GET /v2/batch/scrape/{id}` status and `DELETE` cancel. No MCP tool and no CLI command: POST-only. Crawl status (`GET /v2/crawl/{id}`) and cancel (`DELETE /v2/crawl/{id}`) are verified and covered by MCP status plus CLI `--cancel`.
- Apify builds, schedules, actor-tasks: verified. MCP has opt-in categories for all three (not in the default tool set) and the CLI has `apify builds ...`, `apify task run`, and a generic authenticated `apify api`. No script needed.
- Bright Data `POST /request`: verified (Web Unlocker and SERP share it, selected by `zone`). There is no bare `/unblocker` endpoint; the async Unlocker flow is `POST /unblocker/req?zone=` then `GET /unblocker/get_result?response_id=`.
- Official CLIs exist for Tavily, Firecrawl, Apify, Bright Data, ScrapeGraph, Browserbase. AgentQL's `agentql-cli` only scaffolds SDK projects. Exa has none.
- Needs py script (7 rows, see section 4): Exa `/answer`, Exa agent stop/cancel, Exa `/batches`, Firecrawl batch scrape, Bright Data async Unlocker result retrieval, Browserbase agent runs, ScrapeGraph crawl management.

## 1. Direct HTTP API per service

Auth header per service:

| Service | Base URL | Auth header |
|---|---|---|
| Exa | `https://api.exa.ai` | `Authorization: Bearer $EXA_API_KEY` or `x-api-key: $EXA_API_KEY` |
| Tavily | `https://api.tavily.com` | `Authorization: Bearer tvly-...` |
| Firecrawl | `https://api.firecrawl.dev` (paths below carry the `/v2` prefix) | `Authorization: Bearer fc-...` |
| Apify | `https://api.apify.com` | `Authorization: Bearer <token>` (or `?token=` query, documented as less secure) |
| Bright Data | `https://api.brightdata.com` | `Authorization: Bearer <api key>` |
| ScrapeGraphAI | `https://v2-api.scrapegraphai.com` (paths below carry the `/api` prefix) | `SGAI-APIKEY: sgai-...` |
| Browserbase | `https://api.browserbase.com` | `X-BB-API-Key: <key>` |
| AgentQL | `https://api.agentql.com` | `X-API-Key: <key>` |

Sources: Exa https://exa.ai/docs/reference/answer (Agent Instructions block) and https://exa.ai/docs/exa-spec.yaml (`securitySchemes`); Tavily https://docs.tavily.com/documentation/api-reference/endpoint/research (`bearerAuth`); Firecrawl https://docs.firecrawl.dev/api-reference/v2-openapi.json (`bearerAuth`); Apify https://docs.apify.com/api/openapi.json (`httpBearer`, `apiKey` in query `token`); Bright Data https://docs.brightdata.com/api-reference/rest-api/unlocker/unlock-website (`bearerAuth`); ScrapeGraph https://docs.scrapegraphai.com/api-reference/introduction; Browserbase https://docs.browserbase.com/reference/api/fetch-a-page (`BrowserbaseAuth`); AgentQL https://docs.agentql.com/rest-api/api-reference.

### Exa

| Capability | Method and URL | Minimal body |
|---|---|---|
| Search | `POST /search` | `{"query":"..."}` (required: `query`; `type` enum `instant`, `fast`, `auto`, `deep-lite`, `deep`, `deep-reasoning`) |
| Extract or fetch | `POST /contents` | `{"urls":["https://example.com"],"text":true}` (one of `ids` or `urls` required) |
| Crawl or map | none | `/contents` has `subpages` and `subpageTarget` options; no crawl or map endpoint in the spec |
| Answer | `POST /answer` | `{"query":"..."}` (required: `query`; optional `model`: `exa`, `exa-pro`, `exa-research`, `exa-fast`; `stream`, `outputSchema`) |
| Deep research (Agent) | `POST /agent/runs` | `{"query":"...","effort":"ultra"}` (required: `query`; `effort` enum `minimal`, `low`, `medium`, `high`, `xhigh`, `auto`, `ultra`; optional `budget.maxCostDollars` 1-100 and `budget.maxDurationSeconds` 300-10800) |
| Async jobs | `GET /agent/runs/{id}`, `POST /agent/runs/{id}/stop` (ultra only), `POST /agent/runs/{id}/cancel`, `GET /agent/runs/{id}/events`; `POST /batches`, `GET /batches/{id}`, `POST /batches/{id}/cancel` | `/batches`: `{"requests":[...]}` (required: `requests`, each with a unique `customId`) |

- Run statuses: `queued`, `running`, `completed`, `failed`, `cancelled`. Ultra runs "typically complete complex tasks in about 30 minutes, but can take up to three hours" and default to a $20 cap.
- `POST /research`: the OpenAPI spec (stated by Exa to be "the source of truth") lists `/search`, `/contents`, `/answer`, `/findSimilar`, `/monitors*`, `/agent/runs*`, `/batches*`, `/v0/*` and no `/research`. Dropped.
- Sources: https://exa.ai/docs/exa-spec.yaml, https://exa.ai/docs/reference/answer, https://exa.ai/docs/reference/agent-api/create-a-run, https://exa.ai/docs/agent/agent-ultra, https://exa.ai/docs/search/quickstart, https://exa.ai/docs/contents/quickstart.

### Tavily

| Capability | Method and URL | Minimal body |
|---|---|---|
| Search | `POST /search` | `{"query":"..."}` |
| Extract | `POST /extract` | `{"urls":["https://example.com"]}` |
| Crawl | `POST /crawl` | `{"url":"https://docs.example.com"}` |
| Map | `POST /map` | `{"url":"https://docs.example.com"}` |
| Deep research | `POST /research` | `{"input":"..."}` (required: `input`; `model` enum `mini`, `pro`, `auto`) |
| Async job | `GET /research/{request_id}` | none. `POST /research` returns `201` with `request_id`, `status: pending`; the GET returns `200` (`completed` or `failed`) or `202` (`pending` or `in_progress`) |

- Tavily also documents a keyless mode (rate limited); this repo always sends an API key (any plan, free plans included) and never uses keyless access.
- Sources: https://docs.tavily.com/documentation/api-reference/endpoint/research, https://docs.tavily.com/documentation/api-reference/endpoint/research-get, and the `search`, `extract`, `crawl`, `map` pages under the same `endpoint/` path.

### Firecrawl

| Capability | Method and URL | Minimal body |
|---|---|---|
| Search | `POST /v2/search` | `{"query":"...","limit":3}` |
| Scrape | `POST /v2/scrape` | `{"url":"https://docs.firecrawl.dev"}` |
| Batch scrape | `POST /v2/batch/scrape` | `{"urls":["https://firecrawl.dev","https://docs.firecrawl.dev"],"formats":["markdown"]}`; response object has `success`, `id`, `url`, `invalidURLs` |
| Batch status, errors, cancel | `GET /v2/batch/scrape/{id}`, `GET /v2/batch/scrape/{id}/errors`, `DELETE /v2/batch/scrape/{id}` | none |
| Crawl | `POST /v2/crawl` | `{"url":"https://docs.firecrawl.dev","limit":10}` |
| Crawl status, errors, cancel | `GET /v2/crawl/{id}`, `GET /v2/crawl/{id}/errors`, `DELETE /v2/crawl/{id}` | none |
| Map | `POST /v2/map` | `{"url":"https://firecrawl.dev"}` |
| Deep research (Agent) | `POST /v2/agent`, `GET /v2/agent/{jobId}`, `DELETE /v2/agent/{jobId}` | `{"prompt":"Find the founders of Firecrawl","maxCredits":100}` (agent runs asynchronously; poll the GET) |
| Research papers | `GET /v2/search/research/papers?query=...&k=10` | none |

- The OpenAPI spec marks no field as required; the bodies above are the ones shown in the vendor examples.
- The docs' search example omits the `Authorization` header (keyless tier described in the MCP README); whether raw REST accepts it was not tested.
- Sources: https://docs.firecrawl.dev/api-reference/v2-openapi.json (paths list), https://docs.firecrawl.dev/features/batch-scrape, https://docs.firecrawl.dev/features/crawl, https://docs.firecrawl.dev/features/map, https://docs.firecrawl.dev/features/search, https://docs.firecrawl.dev/features/agent.

### Apify

| Capability | Method and URL | Minimal body |
|---|---|---|
| Search Actors | `GET /v2/store` | none |
| Run Actor (async) | `POST /v2/actors/{actorId}/runs` | Actor input JSON, e.g. `{"query":"san francisco weather"}` for `apify~rag-web-browser` (`query` is its only required input) |
| Run Actor (sync, items) | `POST /v2/actors/{actorId}/run-sync-get-dataset-items` | same; returns `408` if the run exceeds 300 seconds |
| Run status, abort | `GET /v2/actor-runs/{runId}`, `POST /v2/actor-runs/{runId}/abort` | none |
| Dataset items | `GET /v2/datasets/{datasetId}/items` | none |
| Builds | `POST /v2/actors/{actorId}/builds?version=<n>` (`version` query param required), `GET /v2/actors/{actorId}/builds`, `GET /v2/actor-builds/{buildId}`, `POST /v2/actor-builds/{buildId}/abort`, `GET /v2/actor-builds/{buildId}/log` | none |
| Schedules | `POST /v2/schedules`, `GET/PUT/DELETE /v2/schedules/{scheduleId}`, `GET /v2/schedules/{scheduleId}/log` | `{"name":"my-schedule","isEnabled":true,"cronExpression":"0 * * * *","timezone":"UTC","actions":[{"type":"RUN_ACTOR","actorId":"<id>"}]}` (action `type` is `RUN_ACTOR` with `actorId`, or `RUN_ACTOR_TASK` with `actorTaskId`) |
| Actor tasks | `POST /v2/actor-tasks`, `GET/PUT/DELETE /v2/actor-tasks/{actorTaskId}`, `PUT /v2/actor-tasks/{actorTaskId}/input`, `POST /v2/actor-tasks/{actorTaskId}/runs`, `POST /v2/actor-tasks/{actorTaskId}/run-sync-get-dataset-items` | create: `{"actId":"<id>","name":"my-task","input":{"hello":"world"}}` (required: `actId`) |

- `{actorId}` accepts an Actor ID or `username~actor-name` (tilde form).
- No dedicated crawl or map endpoint exists in the spec; those are Actor runs.
- Sources: https://docs.apify.com/api/openapi.json (paths, `ScheduleCreate`, `CreateTaskRequest`, `securitySchemes`), https://github.com/apify/rag-web-browser (`actors/apify_rag-web-browser/.actor/input_schema.json`).

### Bright Data

| Capability | Method and URL | Minimal body |
|---|---|---|
| Fetch URL (Web Unlocker) | `POST /request` | `{"zone":"web_unlocker1","url":"https://geo.brdtest.com/welcome.txt","format":"raw"}` (required: `zone`, `url`, `format` in `raw`, `json`; optional `data_format` `markdown` or `screenshot`, `country`, `render`) |
| Search (SERP) | `POST /request` | `{"zone":"serp_api1","url":"https://www.google.com/search?q=pizza","format":"json"}` |
| Async Unlocker submit | `POST /unblocker/req?zone=<zone>` | `{"url":"https://geo.brdtest.com/welcome.txt"}`; returns `{"response_id":"..."}` |
| Async Unlocker result | `GET /unblocker/get_result?response_id=<id>` | none. Returns `202` "Request is pending" while running; poll after 20 s, then 10 s, then every 5 s. The zone needs "Asynchronous requests" switched on in Advanced settings |
| Async via `/request` | `POST /request?async=true` | OpenAPI documents the `async` query parameter; the retrieval endpoint for this variant is not documented (see Unverified) |
| Discover | `POST /discover`, then `GET /discover?task_id=<id>` | `{"query":"..."}` (fields from CLI source: `intent`, `city`, `country`, `language`, `num_results`, `filter_keywords`, `include_content`, `remove_duplicates`, `start_date`, `end_date`) |
| Structured platform data (async) | `POST /datasets/v3/trigger?dataset_id=<id>`, `GET /datasets/v3/progress/{snapshot_id}`, `GET /datasets/v3/snapshot/{snapshot_id}?format=json` | `{"input":[{"user_name":"zoobarcelona"}]}` |
| Crawl or map | none documented | none |

- Zones are account resources (created in the control panel or by API); Web Unlocker and SERP pass the zone as the `zone` parameter.
- Sources: https://docs.brightdata.com/api-reference/rest-api/unlocker/unlock-website (OpenAPI for `POST /request`), https://docs.brightdata.com/products/web-unlocker/send-your-first-request (async flow), https://docs.brightdata.com/api-reference/rest-api/serp/serp-api, https://docs.brightdata.com/products/scrapers/scrapers-library/async-requests, `/discover` from https://github.com/brightdata/cli `src/commands/discover.ts` and `src/utils/client.ts` (base URL `https://api.brightdata.com`, Bearer auth). The llms.txt index at https://docs.brightdata.com/llms.txt has no REST page for discover.

### ScrapeGraphAI (API v2)

| Capability | Method and URL | Minimal body |
|---|---|---|
| Scrape | `POST /api/scrape` | `{"url":"https://example.com","formats":[{"type":"markdown"}]}` (required: `url`, `formats`; `fetchConfig.stealth` bool for residential proxy plus anti-bot headers) |
| Extract | `POST /api/extract` | `{"url":"https://example.com","prompt":"..."}` (required: `prompt` plus exactly one of `url`, `html`, `markdown`) |
| Search and answer | `POST /api/search` | `{"query":"...","prompt":"..."}` (required: `query`; `prompt` adds AI extraction across results) |
| Crawl (async) | `POST /api/crawl`, `GET /api/crawl/:id`, `GET /api/crawl/:id/pages` | `{"url":"https://scrapegraphai.com/","formats":[{"type":"markdown"}],"maxPages":5}` (required: `url`); status `running`, `completed`, `failed`, `stopped` |
| Crawl manage | `POST /api/crawl/:id/stop`, `POST /api/crawl/:id/resume`, `DELETE /api/crawl/:id` | none |
| Monitor | `POST /api/monitor` | `{"url":"https://example.com","name":"watch","interval":"*/30 * * * *"}` |
| Map or sitemap | none in v2 | none |

- The v1 host (`https://api.scrapegraphai.com/v1`) and v1 names (`smartscraper`, `searchscraper`, `markdownify`, `smartcrawler`) are documented as deprecated.
- Sources: https://docs.scrapegraphai.com/api-reference/introduction and the `endpoint/` pages (`scrape`, `extract`, `search`, `crawl/start`, `crawl/get-status`, `crawl/manage`, `monitor/create`).

### Browserbase

| Capability | Method and URL | Minimal body |
|---|---|---|
| Search | `POST /v1/search` | `{"query":"..."}` (required: `query`, max 200 chars; `numResults` 1-25) |
| Fetch a page | `POST /v1/fetch` | `{"url":"https://example.com"}` (required: `url`; `format` `raw`, `json`, `markdown`) |
| Browser session | `POST /v1/sessions` | `{}` (`projectId` optional, inferred from the API key) |
| Agent run (async) | `POST /v1/agents/runs`, `GET /v1/agents/runs/{runId}` | `{"task":"..."}` (required: `task`; response `201`, run starts `pending`) |
| Crawl or map | none | none |

- Sources: https://docs.browserbase.com/reference/api/fetch-a-page, https://docs.browserbase.com/reference/api/web-search, https://docs.browserbase.com/reference/api/create-a-session, https://docs.browserbase.com/reference/api/run-an-agent, https://docs.browserbase.com/reference/api/get-a-run.

### AgentQL

| Capability | Method and URL | Minimal body |
|---|---|---|
| Extract structured data | `POST /v1/query-data` | `{"query":"{ products[] { product_name product_price(integer) } }","url":"https://scrapeme.live/?s=fish&post_type=product"}` (needs `query` or `prompt`, and `url` or `html`) |
| Other | `POST /v1/query-document` (files), `POST /v1/tetra/sessions` (remote browser CDP session) | out of scope |

- Source: https://docs.agentql.com/rest-api/api-reference. AgentQL has no search, crawl, map or deep-research endpoint.
## 2. Official CLIs

| Service | Official CLI | Package and version | Install | Windows | Auth |
|---|---|---|---|---|---|
| Tavily | yes, `tvly` | PyPI `tavily-cli` 0.1.8 | `uv tool install tavily-cli` (also `pip install tavily-cli`, or `curl -fsSL https://cli.tavily.com/install.sh \| bash`) | PyPI classifier "Operating System :: OS Independent"; no explicit Windows statement | `TAVILY_API_KEY`, or `tvly login --api-key <key>` (stored in `~/.tavily/config.json`), or `tvly login` (browser OAuth) |
| Firecrawl | yes, `firecrawl` | npm `firecrawl-cli` 1.24.6, Node >=22 | `npm install -g firecrawl-cli` (or `npx -y firecrawl-cli@latest init -y --browser`) | not stated in the README | `FIRECRAWL_API_KEY`, `firecrawl login [--api-key <key>]`, or per-command `--api-key` |
| Apify | yes, `apify` | npm `apify-cli` 1.10.0 | `npm install -g apify-cli`; `brew install apify-cli`; `irm https://apify.com/install-cli.ps1 \| iex` (Windows); `curl -fsSL https://apify.com/install-cli.sh \| bash` (macOS, Linux) | yes, the installation page lists a Windows installer | `APIFY_TOKEN` (read before the stored login), or `apify login` |
| Exa | none found | none | none | not applicable | not applicable |
| Bright Data | yes, `brightdata` and `bdata` | npm `@brightdata/cli` 0.3.7, Node >=20 | `npm install -g @brightdata/cli` (Windows and any platform); `curl -fsSL https://cli.brightdata.com/install.sh \| sh` (macOS, Linux) | yes, the installation page has a Windows section (npm `.cmd` shim, PowerShell execution policy, cp1252 code page notes) | `BRIGHTDATA_API_KEY`, or `brightdata login [--api-key <key> \| --device \| --github]` |
| ScrapeGraphAI | yes, `just-scrape` | npm `just-scrape` 1.1.0, Node >=22 | `npm install -g just-scrape` (also `npx just-scrape`) | not stated in the docs | `SGAI_API_KEY` (then `.env`, `~/.scrapegraphai/config.json`, interactive prompt) |
| Browserbase | yes, `browse` | npm `browse` 0.11.0, Node ^20.19 or >=22.12 | `npm install -g browse` | not stated in the docs | `BROWSERBASE_API_KEY` |
| AgentQL | scaffolding only, `agentql` | npm `agentql-cli` 1.17.2, Node >=18 | `npm install -g agentql-cli` | not stated | none: commands are `agentql init` and `agentql new-script`, which set up SDK projects and query nothing |

- Exa: the docs index (https://exa.ai/docs/llms.txt), the MCP page, and the exa-labs GitHub org repository list show no CLI. The npm package `exa-cli` exists but its maintainer is an individual and it is not referenced by Exa (third-party, see Unverified). Exa's own tooling is the hosted MCP server and `npx skills add exa-labs/agent-skills`.
- Sources: https://docs.tavily.com/documentation/tavily-cli, https://github.com/tavily-ai/tavily-cli, https://pypi.org/pypi/tavily-cli/json; https://github.com/firecrawl/cli, `npm view firecrawl-cli`; https://docs.apify.com/cli/docs/installation, https://docs.apify.com/cli/docs/reference, https://github.com/apify/apify-cli (`src/lib/auth.ts`); https://docs.brightdata.com/products/cli/installation, https://github.com/brightdata/cli; https://docs.scrapegraphai.com/services/cli/introduction; https://docs.browserbase.com/integrations/skills/browse-cli; https://docs.agentql.com/cli-reference; npm registry metadata for `just-scrape`, `browse`, `agentql-cli`, `@brightdata/cli`, `apify-cli`.
- Apify's docs say Node 22 or higher for the npm route while the registry `engines` field says >=20.

## 3. MCP vs CLI vs POST matrix

Legend for the MCP column: (L) name returned by a live `tools/list` in the catalog file; (R) upstream README or source only; (cfg) pinned in the OpenCode config URL. Servers whose live list needs a key (Exa, Apify, Tavily, AgentQL, Bright Data) are all (R). "none" means no such route was located in the primary sources. Rows marked SCRIPT have no MCP tool and no CLI command.

| Service | Capability | MCP tool | CLI command | POST endpoint | Script? | Source |
|---|---|---|---|---|---|---|
| Exa | search | `web_search_exa` (R, cfg), `web_search_advanced_exa` (R, cfg) | none | `POST /search` | no | [spec][exa-spec], [mcp][exa-mcp] |
| Exa | extract or fetch | `web_fetch_exa` (R, cfg) | none | `POST /contents` | no | [spec][exa-spec], [mcp][exa-mcp] |
| Exa | crawl or map | none | none | none | no | [spec][exa-spec], [mcp][exa-mcp] |
| Exa | answer | none | none | `POST /answer` | SCRIPT | [spec][exa-spec], [mcp][exa-mcp] |
| Exa | deep research (Agent, incl. ultra) | `agent_run` (R, cfg; its `effort` field exists, accepted values not documented) | none | `POST /agent/runs` | no (verify `ultra` via MCP) | [spec][exa-spec], [mcp][exa-mcp] |
| Exa | async: poll, stop, cancel, events | `agent_run` re-called with `runId` for polling; stop and cancel: none | none | `GET /agent/runs/{id}`, `POST /agent/runs/{id}/stop`, `POST /agent/runs/{id}/cancel`, `GET /agent/runs/{id}/events` | SCRIPT (stop, cancel) | [spec][exa-spec], [mcp][exa-mcp] |
| Exa | async batches | none | none | `POST /batches`, `GET /batches/{id}`, `POST /batches/{id}/cancel` | SCRIPT (low priority) | [spec][exa-spec], [mcp][exa-mcp] |
| Tavily | search | `tavily_search` (R) | `tvly search` | `POST /search` | no | [api][tav-api], [cli][tav-cli], [mcp][tav-mcp] |
| Tavily | extract | `tavily_extract` (R) | `tvly extract` | `POST /extract` | no | [api][tav-api], [cli][tav-cli], [mcp][tav-mcp] |
| Tavily | crawl | `tavily_crawl` (R) | `tvly crawl` | `POST /crawl` | no | [api][tav-api], [cli][tav-cli], [mcp][tav-mcp] |
| Tavily | map | `tavily_map` (R) | `tvly map` | `POST /map` | no | [api][tav-api], [cli][tav-cli], [mcp][tav-mcp] |
| Tavily | deep research | `tavily_research` (R) | `tvly research` | `POST /research` | no | [api][tav-api], [cli][tav-cli], [mcp][tav-mcp] |
| Tavily | async research | `tavily_research` (blocking behavior not documented) | `tvly research --no-wait`, `tvly research status <id>`, `tvly research poll <id>` | `GET /research/{request_id}` | no | [api][tav-api], [cli][tav-cli], [mcp][tav-mcp] |
| Firecrawl | search | `firecrawl_search` (L, unauthenticated list) | `firecrawl search` | `POST /v2/search` | no | [api][fc-api], [cli][fc-cli], [mcp][fc-mcp] |
| Firecrawl | scrape | `firecrawl_scrape` (L) | `firecrawl scrape` (multiple URLs are scraped concurrently) | `POST /v2/scrape` | no | [api][fc-api], [cli][fc-cli], [mcp][fc-mcp] |
| Firecrawl | batch scrape | none | none | `POST /v2/batch/scrape`, `GET`/`DELETE /v2/batch/scrape/{id}` | SCRIPT | [api][fc-api], [cli][fc-cli], [mcp][fc-mcp] |
| Firecrawl | crawl | `firecrawl_crawl` (R) | `firecrawl crawl <url> [--wait]` | `POST /v2/crawl` | no | [api][fc-api], [cli][fc-cli], [mcp][fc-mcp] |
| Firecrawl | crawl status, cancel | `firecrawl_check_crawl_status` (R); cancel: none | `firecrawl crawl <job-id>`; `firecrawl crawl --cancel` (flag documented as "Cancel an active crawl job by job ID") | `GET /v2/crawl/{id}`, `DELETE /v2/crawl/{id}` | no | [api][fc-api], [cli][fc-cli], [mcp][fc-mcp] |
| Firecrawl | map | `firecrawl_map` (R) | `firecrawl map` | `POST /v2/map` | no | [api][fc-api], [cli][fc-cli], [mcp][fc-mcp] |
| Firecrawl | deep research (Agent) | `firecrawl_agent`, `firecrawl_agent_status` (R) | `firecrawl agent "<prompt>" [--wait]`, `firecrawl agent <job-id>` | `POST /v2/agent`, `GET /v2/agent/{jobId}` | no | [api][fc-api], [cli][fc-cli], [mcp][fc-mcp] |
| Firecrawl | research papers | `firecrawl_research_search_papers`, `_read_paper`, `_related_papers`, `_inspect_paper` (R) | `firecrawl research` | `GET /v2/search/research/papers` | no | [api][fc-api], [cli][fc-cli], [mcp][fc-mcp] |
| Firecrawl | monitors | `firecrawl_monitor_create`, `_list`, `_get`, `_update`, `_delete`, `_run`, `_checks`, `_check` (R) | `firecrawl monitor` | `POST /v2/monitor` and siblings | no | [api][fc-api], [cli][fc-cli], [mcp][fc-mcp] |
| Apify | search Actors | `search-actors` (R, cfg) | `apify actors search` | `GET /v2/store` | no | [api][ap-api], [cli][ap-cli], [mcp][ap-mcp] |
| Apify | run Actor (incl. rag-web-browser) | `apify--rag-web-browser` (R, cfg), `call-actor` (R, cfg) | `apify actors call` (alias `apify call`), `apify actors start` | `POST /v2/actors/{actorId}/runs`, `POST /v2/actors/{actorId}/run-sync-get-dataset-items` | no | [api][ap-api], [cli][ap-cli], [mcp][ap-mcp] |
| Apify | async: run status, dataset items, abort | `get-actor-run`, `get-dataset-items`, `abort-actor-run`, `get-key-value-store-record` (R, auto-injected once `call-actor` is present) | `apify runs info`, `apify runs wait`, `apify runs abort`, `apify datasets get-items` | `GET /v2/actor-runs/{runId}`, `POST /v2/actor-runs/{runId}/abort`, `GET /v2/datasets/{id}/items` | no | [api][ap-api], [cli][ap-cli], [mcp][ap-mcp] |
| Apify | builds | `build-actor`, `get-actor-build`, `get-actor-build-log` (R, `builds` category, opt-in, not in cfg) | `apify builds create` (alias `apify actors build`), `apify builds info`, `apify builds wait`, `apify builds log` | `POST /v2/actors/{actorId}/builds?version=` | no | [api][ap-api], [cli][ap-cli], [mcp][ap-mcp] |
| Apify | schedules | `create-schedule`, `get-schedule`, `update-schedule`, `delete-schedule` (R, `schedules` category, opt-in, not in cfg) | no dedicated command; generic `apify api POST /v2/schedules -d '<json>'` | `POST /v2/schedules` | no | [api][ap-api], [cli][ap-cli], [mcp][ap-mcp] |
| Apify | actor tasks | `create-actor-task`, `get-actor-task`, `update-actor-task` (R, `tasks` category, opt-in, not in cfg) | `apify task run` (also `publish`, `unpublish`); create via generic `apify api` | `POST /v2/actor-tasks`, `POST /v2/actor-tasks/{id}/runs` | no | [api][ap-api], [cli][ap-cli], [mcp][ap-mcp] |
| Apify | crawl or map | none dedicated (run an Actor via `call-actor`) | none dedicated | none dedicated | no | [api][ap-api], [cli][ap-cli], [mcp][ap-mcp] |
| Bright Data | search | `search_engine`, `search_engine_batch` (R) | `brightdata search` | `POST /request` (SERP zone) | no | [api][bd-api], [cli][bd-cli], [mcp][bd-mcp] |
| Bright Data | fetch URL | `scrape_as_markdown`, `scrape_as_html`, `scrape_batch` (R) | `brightdata scrape` | `POST /request` (Web Unlocker zone) | no | [api][bd-api], [cli][bd-cli], [mcp][bd-mcp] |
| Bright Data | crawl or map | none | none | none documented | no | [api][bd-api], [cli][bd-cli], [mcp][bd-mcp] |
| Bright Data | discover (AI-ranked web discovery) | `discover` (R) | `brightdata discover` | `POST /discover`, `GET /discover?task_id=` | no | [api][bd-api], [cli][bd-cli], [mcp][bd-mcp] |
| Bright Data | structured platform data | `web_data_*` (R, many; full list not captured) | `brightdata pipelines <type> <url>` | `POST /datasets/v3/trigger`, `GET /datasets/v3/progress/{id}`, `GET /datasets/v3/snapshot/{id}` | no | [api][bd-api], [cli][bd-cli], [mcp][bd-mcp] |
| Bright Data | async Unlocker | none | `brightdata scrape --async` (submit only, prints Response ID; no result command in `src/commands`) | `POST /unblocker/req?zone=`, `GET /unblocker/get_result?response_id=` | SCRIPT (result retrieval) | [api][bd-api], [cli][bd-cli], [mcp][bd-mcp] |
| ScrapeGraphAI | scrape | `scrape`, `markdownify` (L, installed 1.0.1) | `just-scrape scrape` | `POST /api/scrape` | no | [api][sg-api], [cli][sg-cli], [mcp][sg-mcp] |
| ScrapeGraphAI | extract | `smartscraper` (L, 1.0.1); `extract` in unpublished v3 | `just-scrape extract` | `POST /api/extract` | no | [api][sg-api], [cli][sg-cli], [mcp][sg-mcp] |
| ScrapeGraphAI | search and answer | `searchscraper` (L, 1.0.1); `search` in unpublished v3 | `just-scrape search` | `POST /api/search` | no | [api][sg-api], [cli][sg-cli], [mcp][sg-mcp] |
| ScrapeGraphAI | crawl (start, poll) | `smartcrawler_initiate`, `smartcrawler_fetch_results` (L, 1.0.1); `crawl_start`, `crawl_get_status` in unpublished v3 | `just-scrape crawl` | `POST /api/crawl`, `GET /api/crawl/:id` | no | [api][sg-api], [cli][sg-cli], [mcp][sg-mcp] |
| ScrapeGraphAI | crawl manage (stop, resume, delete, pages) | none installed; `crawl_stop`, `crawl_resume` only in unpublished v3 | none | `POST /api/crawl/:id/stop`, `POST /api/crawl/:id/resume`, `DELETE /api/crawl/:id`, `GET /api/crawl/:id/pages` | SCRIPT | [api][sg-api], [cli][sg-cli], [mcp][sg-mcp] |
| ScrapeGraphAI | map or sitemap | `sitemap` (L, 1.0.1) | none | none in v2 | no | [api][sg-api], [cli][sg-cli], [mcp][sg-mcp] |
| ScrapeGraphAI | monitors | `monitor_*` only in unpublished v3 | `just-scrape monitor` | `POST /api/monitor` | no | [api][sg-api], [cli][sg-cli], [mcp][sg-mcp] |
| Browserbase | search | none | `browse cloud search` | `POST /v1/search` | no | [api][bb-api], [cli][bb-cli], [mcp][cat] |
| Browserbase | fetch a page | none | `browse cloud fetch` | `POST /v1/fetch` | no | [api][bb-api], [cli][bb-cli], [mcp][cat] |
| Browserbase | browser session | `start`, `end`, `navigate`, `act`, `observe`, `extract` (L, unauthenticated list) | `browse open`, `snapshot`, `click`, `fill`, `screenshot`, `browse cloud sessions` | `POST /v1/sessions` | no | [api][bb-api], [cli][bb-cli], [mcp][cat] |
| Browserbase | agent run (async) | none | none documented | `POST /v1/agents/runs`, `GET /v1/agents/runs/{runId}` | SCRIPT | [api][bb-api], [cli][bb-cli], [mcp][cat] |
| Browserbase | crawl or map | none | none | none | no | [api][bb-api], [cli][bb-cli], [mcp][cat] |
| AgentQL | extract | `extract-web-data` (R) | none (`agentql-cli` is scaffolding only) | `POST /v1/query-data` | no | [api][aq-api], [mcp][aq-mcp] |

[exa-spec]: https://exa.ai/docs/exa-spec.yaml
[exa-mcp]: https://exa.ai/docs/get-started/exa-mcp
[tav-api]: https://docs.tavily.com/documentation/api-reference/endpoint/research
[tav-cli]: https://docs.tavily.com/documentation/tavily-cli
[tav-mcp]: https://github.com/tavily-ai/tavily-mcp/blob/main/src/index.ts
[fc-api]: https://docs.firecrawl.dev/api-reference/v2-openapi.json
[fc-cli]: https://github.com/firecrawl/cli
[fc-mcp]: https://github.com/firecrawl/firecrawl-mcp-server
[ap-api]: https://docs.apify.com/api/openapi.json
[ap-cli]: https://docs.apify.com/cli/docs/reference
[ap-mcp]: https://github.com/apify/apify-mcp-server
[bd-api]: https://docs.brightdata.com/api-reference/rest-api/unlocker/unlock-website
[bd-cli]: https://github.com/brightdata/cli
[bd-mcp]: https://github.com/brightdata/brightdata-mcp
[sg-api]: https://docs.scrapegraphai.com/api-reference/introduction
[sg-cli]: https://docs.scrapegraphai.com/services/cli/commands
[sg-mcp]: https://github.com/ScrapeGraphAI/scrapegraph-mcp
[bb-api]: https://docs.browserbase.com/reference/api/fetch-a-page
[bb-cli]: https://docs.browserbase.com/integrations/skills/browse-cli
[aq-api]: https://docs.agentql.com/rest-api/api-reference
[aq-mcp]: https://github.com/tinyfish-io/agentql-mcp
[cat]: https://github.com/Bearmancer/system-config/blob/research-drill-catalog-topgrade/.claude/docs/research/mcp-tool-catalog.md

Config-hidden gaps recorded in the catalog: the Exa URL pins 4 tools and the Apify URL pins 3, so the Apify builds, schedules and tasks tools above exist upstream but are not enabled in the current config, and Exa `agent_run` depends on the pinned list including it. Enabling them is a config change, not a script.

## 4. Needs py script (each row becomes a child issue)

Limited to the skill's five capability buckets. Each row has no MCP tool and no CLI command in the primary sources above.

1. Exa answer: `POST /answer` (LLM answer with citations, optional `stream`, `outputSchema`, `model` `exa-research`).
2. Exa agent stop and cancel: `POST /agent/runs/{id}/stop` (ultra runs only) and `POST /agent/runs/{id}/cancel`. Creating and polling runs is covered by `agent_run`.
3. Exa async batches: `POST /batches`, `GET /batches/{id}`, `POST /batches/{id}/cancel` (low priority; only if the skill needs queued request batches).
4. Firecrawl batch scrape: `POST /v2/batch/scrape` plus `GET`/`DELETE /v2/batch/scrape/{id}` and `GET .../errors`.
5. Bright Data async Unlocker: submit via `POST /unblocker/req?zone=` and retrieve via `GET /unblocker/get_result?response_id=` (poll schedule 20 s, 10 s, then 5 s). The CLI `scrape --async` posts `async: true` to `POST /request`; whether its response IDs work with `get_result` is unverified.
6. Browserbase agent runs: `POST /v1/agents/runs` and `GET /v1/agents/runs/{runId}`.
7. ScrapeGraphAI crawl management: `POST /api/crawl/:id/stop`, `POST /api/crawl/:id/resume`, `DELETE /api/crawl/:id`, `GET /api/crawl/:id/pages`.

Not needing a script: all Tavily capabilities (MCP and CLI cover `/research`), all Apify capabilities (opt-in MCP categories plus CLI `apify api`), AgentQL (MCP `extract-web-data`), Firecrawl everything except batch scrape, Bright Data everything except async result retrieval.

## Unverified

- No live call was made (no keys were used, per the rules). Response shapes, rate limits and pricing were not tested; request and response facts come from docs, OpenAPI specs and source read on 2026-09-29.
- The MCP tool names for Exa, Apify, Tavily, AgentQL and Bright Data are from upstream README or source, not from a live authenticated `tools/list` (see the catalog file). Firecrawl's authenticated tool list is likewise unconfirmed: the README documents map, crawl, agent, monitor and research tools that were absent from the 3-tool unauthenticated list.
- Tavily: the hosted remote's tool spelling (`tavily-search` in the docs prose versus `tavily_search` in the npm server source) and whether `tavily_research` blocks or returns a `request_id`. `tavily-cli` Windows support rests on the PyPI classifier only, and the CLI README notes known gaps for browser OAuth login (https://github.com/tavily-ai/tavily-cli/issues/24).
- Exa: no official CLI was located, but absence of evidence is not proof (docs index, MCP page and org repository list only). The npm package `exa-cli` (maintained by an individual) is third-party and unexamined. The accepted values of the MCP `agent_run` `effort` field, and whether `ultra`, `budget` or stop are reachable through MCP, are not documented on the MCP page. Which `/search` `type` values the MCP tools expose was not checked.
- Firecrawl: whether `firecrawl scrape` with several URLs calls `/v2/batch/scrape` (GitHub code search on the default branch found no `batchScrape` call, so the SCRIPT verdict assumes it does not). Whether raw REST accepts unauthenticated search as the docs example implies. Windows support for `firecrawl-cli`. Whether MCP or CLI can cancel an agent job.
- Apify: the exact hosted-URL syntax for adding the `builds`, `schedules`, `tasks` categories was read from the README `tools=` description but not exercised. The CLI Node requirement differs between docs (22+) and the registry (>=20).
- Bright Data: the `POST /discover` contract comes from CLI source only (no REST doc page was located). Which endpoint retrieves a result after `POST /request` with `async` (the CLI sends `async: true` in the body, the OpenAPI documents an `async` query parameter, and the documented poll flow uses `/unblocker/req` plus `/unblocker/get_result`). Whether Bright Data has a crawl or map API (none located in the docs index). `brightdata pipelines` polling behavior and the full `web_data_*` list.
- ScrapeGraphAI: the installed MCP is `scrapegraph-mcp` 1.0.1, the latest PyPI release (2025-11-19), with v1-style tool names; GitHub main is 3.0.0 (v3 names such as `crawl_start`) and was not on PyPI at fetch time. Whether 1.0.1 calls the deprecated v1 host is unverified. The CLI's documented default `SGAI_API_URL` (`https://api.scrapegraphai.com/api/v2`) differs from the API docs base URL (`https://v2-api.scrapegraphai.com/api`). MCP `scrape` support for `stealth` was not inspected (the REST `fetchConfig.stealth` field is documented). Windows support and any crawl stop or resume command for `just-scrape`.
- Browserbase: the MCP list is the unauthenticated live list from the catalog; an authenticated list may be larger. No CLI command for agent runs is documented (`browse cloud` documents projects, sessions, contexts, extensions, fetch, search). Windows support for `browse`.
- AgentQL: the MCP tool name is from the README and source only (the server exits without a key). Windows support for `agentql-cli`.
- The catalog file cited throughout is on PR #35's branch (`research-drill-catalog-topgrade`), not master; its live results were not re-run here.