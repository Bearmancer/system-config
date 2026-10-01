# Exa

Pick: conceptual (not keyword) queries; papers and long-form that keyword engines miss; cached fetch (chain step 3). `livecrawl` = freshness, not a bypass. Key `EXA_API_KEY`, pool `exa`; script header `x-api-key` (Bearer also accepted). No official CLI (npm `exa-cli` is third-party, unexamined).

## MCP (config pins 4 tools in the URL; live list 403 without key, names from README (readme))

`web_search_exa`, `web_search_advanced_exa`, `web_fetch_exa`, `agent_run` (create and poll; whether `effort: ultra`, `budget`, stop reach MCP is undocumented).

## POST (base `https://api.exa.ai`, preset `vendor_request.py exa`; the spec https://exa.ai/docs/exa-spec.yaml is the source of truth)

| Need | Call |
|---|---|
| search | `POST /search` `{"query":Q}`; `type` instant, fast, auto, deep-lite, deep, deep-reasoning |
| contents | `POST /contents` `{"urls":[U],"text":true}`; `subpages`, `subpageTarget` for shallow crawl |
| similar (POST-only) | `POST /findSimilar` `{"url":U}` |
| answer | `POST /answer` `{"query":Q}` or `scripts/exa_answer.py "<q>" [--model exa\|exa-pro\|exa-research\|exa-fast] [--system-prompt T] [--text] [--output-schema J]` (no ultra tier) |
| agent | `POST /agent/runs` `{"query":Q,"effort":"ultra","budget":{"maxCostDollars":20,"maxDurationSeconds":3600}}` (cost 1-100, duration 300-10800); effort minimal, low, medium, high, xhigh, auto, ultra; ultra ~30 min to 3 h, default cap $20; `GET /agent/runs/{id}`, `/events`; stop/cancel: raw `POST /agent/runs/{id}/stop\|cancel` or `scripts/exa_agent_run.py stop\|cancel <run_id>` (stop = ultra only, keeps results; cancel drops them; both bill accrued) |
| batches (beta) | raw `POST /batches` `{"requests":[{"customId","method":"POST","url":"/search","body":{}}]}`, `GET /batches/{id}`, `POST /batches/{id}/cancel` (header `Exa-Beta`); or `scripts/exa_batches.py start --requests '[...]'\|@file`, `status <id>` (`resultsUrl` presigned JSONL), `cancel <id>`; sends `Exa-Beta: batches-2026-06-06`; 403 `FEATURE_DISABLED` until Exa enables batches for the team (live 2026-09-30) |
| monitors (POST-only) | `POST /monitors`, `/monitors/batch`, `GET /monitors/{id}`, `POST /monitors/{id}/trigger`, `GET /monitors/{id}/runs` |
| other | `/v0/websets*`, `/v0/imports`, `/v0/webhooks`, `/v0/events`: out of scope |

No crawl, map, or `/research` path in the spec.
