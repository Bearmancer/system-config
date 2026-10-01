# Apify

Pick: site-specific Actor (Amazon, Maps, social) or generic `apify/rag-web-browser`; chain step 5. Key `APIFY_TOKEN`, pool `apify`, Bearer. No dedicated crawl/map (run an Actor).

## MCP (config URL enables all categories; names from README (R), live 401)

- `apify--rag-web-browser` (Actor tool; Actor ID `apify/rag-web-browser`, input `query`, required), `search-actors`, `call-actor`.
- Auto-added with `call-actor`: `get-actor-run`, `get-dataset-items`, `get-key-value-store-record`, `abort-actor-run`.
- Also enabled by the config URL: `docs` (`search-apify-docs`, `fetch-apify-docs`), `apify--web-fetch`, `fetch-actor-details`, `get-actor-list`, `dev` (`report-problem`), `runs` (+ `get-actor-run-list`, `get-actor-run-log`), `storage` (+ dataset/KV list, get, keys, schema tools). Categories `builds` (`build-actor`, `get-actor-build`, `get-actor-build-log`, `get-actor-build-list`), `schedules` (`create-schedule`, `get-schedule`, `update-schedule`, `delete-schedule`), `tasks` (`create-actor-task`, `get-actor-task`, `update-actor-task`, `publish-actor-task`, `unpublish-actor-task`). An explicit `tools=` list replaces defaults, so the URL names every category.

## CLI `apify` (npm `apify-cli`; `APIFY_TOKEN` or `apify login`)

`apify actors search`, `apify actors call` (alias `apify call`), `actors start`, `apify runs info|wait|abort`, `apify datasets get-items`, `apify builds create|info|wait|log`, `apify task run`, generic `apify api POST /v2/schedules -d '<json>'`.

## POST (base `https://api.apify.com/v2`, preset `vendor_request.py apify`; `{actorId}` = ID or `user~name`)

| Need | Call |
|---|---|
| search Actors | `GET /store?search=Q` |
| run async | `POST /actors/{actorId}/runs` (body = Actor input) |
| run sync + items | `POST /actors/{actorId}/run-sync-get-dataset-items` (408 after 300 s) |
| status, abort, items | `GET /actor-runs/{runId}`; `POST /actor-runs/{runId}/abort`; `GET /datasets/{id}/items` |
| builds | `POST /actors/{actorId}/builds?version=N`; `GET /actor-builds/{buildId}[/log]` |
| schedules | `POST /schedules` `{"name":N,"isEnabled":true,"cronExpression":"0 * * * *","timezone":"UTC","actions":[{"type":"RUN_ACTOR","actorId":ID}]}`; `GET\|PUT\|DELETE /schedules/{id}` |
| tasks | `POST /actor-tasks` `{"actId":ID,"name":N,"input":{}}`; `POST /actor-tasks/{id}/runs` |

