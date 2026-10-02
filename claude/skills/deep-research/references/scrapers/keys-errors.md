# Keys and error codes

Read on a credit/auth/quota failure or a missing-secret problem only.

## Key policy (the only place it is stated)

1. A key is always sent. No keyless access for any vendor, any host, any call. A free-plan key is fine.
2. One env var per vendor, named in the table; configs, scripts and docs use only that name. Vendor tools that natively require their own var name get it set from ours at launch: `just-scrape` reads only `SGAI_API_KEY` (its README, "Environment variable"), the Bright Data MCP server reads only `API_TOKEN` (`@brightdata/mcp/server.js`: `process.env.API_TOKEN`), GitHub MCP reads `GITHUB_PERSONAL_ACCESS_TOKEN`.
3. Source order: `~/.config/opencode/secrets/<pool>` (written by `switch_api_key.py`), else the env var. A missing or empty secrets file falls through to the env var. Neither -> exit 1 `key_unreadable`.
4. A key goes only into the vendor's auth header (fixed per pool in `_post_common.VENDORS`), never into logs, output, URLs or repo files. Redirects are refused.
5. Rotation: `switch_api_key.py --next` rewrites the secrets file; OpenCode reconnects only that server; OmO needs a restart from a new terminal (SKILL.md Key rotation).
6. Missing secrets file breaks config load: `switch_api_key.py --service all --materialize` creates every missing one.

| Server | Config entry | Env var | Pool | Auth header |
|---|---|---|---|---|
| Tavily | `tavily` | `TAVILY_API_KEY` | `tavily` | `Authorization: Bearer tvly-...` |
| Firecrawl | `firecrawl` | `FIRECRAWL_API_KEY` | `firecrawl` | `Authorization: Bearer fc-...` |
| Exa | `exa` | `EXA_API_KEY` | `exa` | `x-api-key` (Bearer also accepted) |
| ScrapeGraphAI | `scrapegraph` | `SCRAPEGRAPH_API_KEY` | `scrapegraph` | `Authorization: Bearer` (also `SGAI-APIKEY`, `X-API-Key`); CLI `just-scrape` requires `SGAI_API_KEY`: `SGAI_API_KEY=$SCRAPEGRAPH_API_KEY just-scrape ...` |
| Apify | `apify` | `APIFY_TOKEN` | `apify` | `Authorization: Bearer` (`?token=` works, less secure) |
| AgentQL | `agentql` | `AGENTQL_API_KEY` | `agentql` | `X-API-Key` |
| Bright Data | `brightdata` | `BRIGHTDATA_API_KEY` (Bright Data MCP requires `API_TOKEN`: config `env: {"API_TOKEN": "${BRIGHTDATA_API_KEY}"}`) | `brightdata` | `Authorization: Bearer` |
| Browserbase | `browserbase` | `BROWSERBASE_API_KEY` | `browserbase` | `X-BB-API-Key` |

- ScrapeGraphAI hosted MCP answers 401 without a valid key: a dead server = missing or wrong key.

## Error codes per service

Rotate on "Out of credit" and on "Bad key" after a working key. Next chain step on "Blocked". Retry once on "Rate limit". Source: `.claude/docs/research/mcp-chain-unknowns.md`.

| Service | Bad key | Out of credit | Blocked | Rate limit |
|---|---|---|---|---|
| Tavily | unverified | unverified | empty result + `Failed to fetch url`, no status code (live drill, system-config#20) | unverified |
| Firecrawl | 401 | 402 | 403, empty body or challenge page in result (still 1 credit) | 429 |
| Exa | 401 | 402 | `SOURCE_NOT_AVAILABLE` per URL | 429 + `Retry-After` |
| ScrapeGraph | 401 `auth_missing_key`; 403 `auth_invalid_key` (live 2026-10-01) | 402 `insufficient_credits` | undocumented | 429 `rate_limited` |
| Apify | 401 `invalid-token` / `token-not-provided` | 402 `not-enough-usage-to-run-paid-actor`, `monthly-usage-limit-too-low` (inferred) | check Actor run output | 429 `rate-limit-exceeded` |
| AgentQL | 401 `API Key Required` | unverified | unverified | unverified |
| Bright Data | 407 `client_10000`, `client_10002` (zone); 401 `client_10050` | 407 `client_10020` (suspended, negative balance); 502 `client_10100` (zone limit) | 502 `reject_block`, `resolve_failed_*` (retry, new peer); 403 `policy_*` = policy, not a block | undocumented |
| Browserbase | unverified | unverified | unverified | unverified |

- POST scripts: HTTP error -> exit 1, JSON line on stderr `{"status","code","message"}`.
- Unverified cell = no published code; treat any auth/credit-looking failure as rotate, then next step.
