# Browserbase

Pick: hosted browser, CAPTCHA (paid tier); chain step 9. Key `BROWSERBASE_API_KEY`, pool `browserbase`, header `X-BB-API-Key`.

- MCP (live, unauthenticated list; authenticated may be larger): `start`, `end`, `navigate`, `act`, `observe`, `extract`.
- CLI `browse` (npm `browse`, Node ^20.19 or >=22.12): `browse cloud search`, `browse cloud fetch`, `browse cloud sessions`, `browse open|snapshot|click|fill|screenshot`. No agent-run command.
- POST (base `https://api.browserbase.com/v1`, preset `vendor_request.py browserbase`): `POST /search` `{"query":Q,"numResults":10}` (query <=200 chars, 1-25); `POST /fetch` `{"url":U,"format":"markdown"}`; `POST /sessions` `{}`; agent runs: `scripts/browserbase_agent_run.py start "<task>" [--result-schema J|@file]` then `status <run_id>` (PENDING, RUNNING, COMPLETED, FAILED, STOPPED, TIMED_OUT, PAUSED).
- No crawl/map.
