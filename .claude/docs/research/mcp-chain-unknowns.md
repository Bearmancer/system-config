# MCP chain unknowns (R3, #5)

Date: 2026-09-29. Read-only research from primary sources.

## Questions

1. Does the Browserbase hosted MCP accept header auth instead of `?browserbaseApiKey=`?
2. Does the Firecrawl remote MCP accept `Authorization: Bearer`? Does the enhanced proxy cost extra credits?
3. What is the exact stealth argument on the ScrapeGraph MCP `scrape` tool?
4. What out-of-credit error codes do Bright Data, AgentQL, Apify and ScrapeGraph return?
5. Does the Tavily remote MCP accept a Bearer header?

## Answers

1. **Browserbase: yes.** `https://mcp.browserbase.com/mcp` takes `Authorization: Bearer <key>` (recommended) or `x-bb-api-key: <key>`. The query param is a "deprecated compatibility fallback" ([Stagehand MCP setup](https://docs.stagehand.dev/v3/integrations/mcp/setup)). The older [Browserbase MCP page](https://docs.browserbase.com/integrations/mcp/setup) still shows only the query param.
2. **Firecrawl: yes.** The API-key method uses `https://mcp.firecrawl.dev/v2/mcp` "with a Bearer token authorization header" ([MCP docs](https://docs.firecrawl.dev/mcp-server)).
   - The enhanced proxy costs no extra credits: `proxy: "enhanced"`, or `auto` escalating, is billed at 1 credit ([billing](https://docs.firecrawl.dev/billing)). This contradicts third-party "+4" claims.
   - `stealth` is not in the proxy enum `basic|enhanced|auto` ([scrape reference](https://docs.firecrawl.dev/api-reference/endpoint/scrape)).
3. **ScrapeGraph: `stealth: bool`.** Its docstring reads "residential proxies to bypass bot detection (+5 credits)" ([`src/scrapegraph_mcp/server.py`](https://github.com/ScrapeGraphAI/scrapegraph-mcp)). Sibling arguments: `mode` (`fast`|`js`), `timeout`, `wait`, `headers`, `cookies`, `country`, `scrolls`.
4. **Out-of-credit codes:** see the table below.
5. **Tavily: yes, per the [README](https://github.com/tavily-ai/tavily-mcp):** "pass your API key through an Authorization header ... `Authorization: Bearer <your-api-key>`". Not exercised live.

## Error table

| Service | Bad key | Out of credit | Blocked | Rate limit |
|---|---|---|---|---|
| Bright Data | 407 `client_10000`; 407 `client_10002` (zone); 401 `client_10050` | 407 `client_10020` (account suspended after a negative balance); 502 `client_10100` (zone usage limit) | 502 `reject_block`, `resolve_failed_*` (retry, new peer); 403 `policy_*` = policy, not a block | undocumented |
| Firecrawl | 401 | 402 | 403, empty body or challenge page in the scrape result (still 1 credit) | 429 |
| Exa | 401 | 402 | `SOURCE_NOT_AVAILABLE` per URL | 429 + `Retry-After` |
| ScrapeGraph | 401 `auth_missing_key`; 403 `auth_invalid_key` | 402 `insufficient_credits` | undocumented | 429 `rate_limited` |
| AgentQL | 401 `API Key Required` (observed) | unverified | unverified | unverified |
| Apify | 401 `invalid-token` / `token-not-provided` | 402 `not-enough-usage-to-run-paid-actor`, `monthly-usage-limit-too-low` | check the Actor run output | 429 `rate-limit-exceeded` |

Sources: [Bright Data error catalog](https://docs.brightdata.com/proxy-networks/errorCatalog), [ScrapeGraph errors](https://docs.scrapegraphai.com/api-reference/errors), [Apify run Actor](https://docs.apify.com/api/v2/act-runs-post), [Firecrawl API intro](https://docs.firecrawl.dev/api-reference/introduction), [Exa errors](https://exa.ai/docs/reference/error-codes), [AgentQL OpenAPI](https://api.agentql.com/openapi.json).

Notes:
- The ScrapeGraph MCP wrapper raises `Error {status}: {body}` for any status of 400 or above, so match on the status number and on `insufficient_credits`.
- Apify's hosted MCP authenticates with `Authorization: Bearer <APIFY_TOKEN>` or OAuth ([docs](https://docs.apify.com/platform/integrations/mcp)).

## Chain consequence

Every chain server can authenticate by header, so no key has to sit in a URL. `{file:}` goes in `headers`, or in `environment` for local servers.

## Unverified

- AgentQL: out-of-credit, blocked and rate-limit codes. Only a generic 4XX is published.
- Bright Data: a dedicated out-of-balance code and a rate-limit code.
- Tavily Bearer against the live endpoint.
- ScrapeGraph: what a blocked-page response looks like.
- Apify: `monthly-usage-limit-too-low` as an out-of-credit signal is inferred from its description.
