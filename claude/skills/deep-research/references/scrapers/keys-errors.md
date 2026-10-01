# Keys and error codes

Read on a credit/auth/quota failure or a missing-secret problem only.

## Keys

| Server | Config entry | Key env var | Pool |
|---|---|---|---|
| Tavily | `tavily` | `TAVILY_API_KEY` | `tavily` |
| Firecrawl | `firecrawl` | `FIRECRAWL_API_KEY` | `firecrawl` |
| Exa | `exa` | `EXA_API_KEY` | `exa` |
| ScrapeGraphAI | `scrapegraph` | `SGAI_API_KEY` (from `SCRAPEGRAPH_API_KEY`) | `scrapegraph` |
| Apify | `apify` | `APIFY_TOKEN` | `apify` |
| AgentQL | `agentql` | `AGENTQL_API_KEY` | `agentql` |
| Bright Data | `brightdata` | `API_TOKEN` (from `BRIGHTDATA_API_KEY`) | `brightdata` |
| Browserbase | `browserbase` | `BROWSERBASE_API_KEY` | `browserbase` |

- Active key sits in `~/.config/opencode/secrets/<pool>`; POST scripts read it there and send it only as the vendor auth header. `switch_api_key.py --next` rewrites that file; OpenCode reconnects only the changed server. OmO: SKILL.md Key rotation.
- Missing secrets file breaks config load: `switch_api_key.py --service all --materialize` creates every missing one.
- ScrapeGraphAI hosted MCP answers 401 without a valid key: a dead server = missing or wrong key.
- Container hosts (no secrets dir): POST scripts fall back to the pool env var (`POOL_ENV` in `_post_common.py`, e.g. `TAVILY_API_KEY`); neither set -> exit 1 `key_unreadable`.
- A key is always required: no keyless or free-tier path is used for any vendor.

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
- Hosts still on legacy ScrapeGraph MCP 1.0.1 raise `Error {status}: {body}` for any status >= 400: match status number and `insufficient_credits`.
- Unverified cell = no published code; treat any auth/credit-looking failure as rotate, then next step.
