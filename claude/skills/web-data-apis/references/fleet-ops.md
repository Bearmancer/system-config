# Fleet ops — wiring, startup quirks, companion skills

Operational detail behind the capability table in `SKILL.md`. Consult this file when a server looks broken, misconfigured, or you need its exact config entry/env var — not needed for routine capability-based tool selection.

## Fleet (wiring/ops — keyed subset only; the capability table in `SKILL.md` covers all 14)

| Server        | Config entry  | Key env var (in OpenCode)                          | Pool service name | Tools                                                                    |
| ------------- | ------------- | -------------------------------------------------- | ----------------- | ------------------------------------------------------------------------ |
| Firecrawl     | `firecrawl`   | `FIRECRAWL_API_KEY`                                | `firecrawl`       | scrape, map, crawl, search, extract, monitor_*                           |
| Tavily        | `tavily`      | `TAVILY_API_KEY`                                   | `tavily`          | tavily_search, tavily_extract, tavily_crawl, tavily_map, tavily_research |
| Exa           | `exa`         | none wired — bare remote URL, no `{env:EXA_API_KEY}` | `exa`             | web_search_exa, web_fetch_exa, web_search_advanced_exa, agent_run        |
| Dappier       | `dappier`     | `DAPPIER_API_KEY`                                  | `dappier`         | `dappier_real_time_search`, `dappier_ai_recommendations`                 |
| AgentQL       | `agentql`     | `AGENTQL_API_KEY`                                  | `agentql`         | `extract-web-data`                                                       |
| ScrapeGraphAI | `scrapegraph` | `SGAI_API_KEY` (mapped from `SCRAPEGRAPH_API_KEY`) | `scrapegraph`     | scrape, extract, search, crawl__, monitor__, credits, history_*          |

Dappier and ScrapeGraphAI run via `uvx` (Python); AgentQL via `cmd /c npx -y` (Node, Windows shim). First `uvx` launch per package pays a cold-start install: `~4s`.

OpenCode-only companion tool skills (Brave-backed servers, `~/.agents/skills/` and `~/.config/opencode/skills/`): `~/.config/opencode/AGENTS.md`. Under Claude Code, equivalent capability comes from MCP servers configured in the session instead.

## Exa rotation is a no-op

`switch_api_key.py --service exa` rewrites the `EXA_API_KEY` pointer, but `opencode.jsonc`'s `exa` MCP entry is a bare remote URL (`https://mcp.exa.ai/mcp?tools=...`) with no `{env:EXA_API_KEY}` reference anywhere in it. Rotating the Exa key changes nothing until the config entry itself is fixed to reference the env var.

## Startup behaviour (matters when a server looks broken)

- Dappier: exits immediately if `DAPPIER_API_KEY` missing (`ValueError`).
- AgentQL: exits immediately if `AGENTQL_API_KEY` missing.
- ScrapeGraphAI: **starts with no key** and fails per-call instead — a silent-looking dead server is usually a missing key, not a broken package.
- Dappier needs its pin: `uvx --with "mcp<2" dappier-mcp`. Unpinned, uvx resolves `mcp` 2.x — where `FastMCP` was renamed to `MCPServer` — and the package dies on import (`ModuleNotFoundError: No module named 'mcp.server.fastmcp'`). Keep the `--with` flag in the config entry.
- Hosted alternatives exist (Dappier `https://mcp.dappier.com/mcp?apiKey=…`; ScrapeGraphAI `https://mcp.scrapegraphai.com/mcp` bearer) — not used; local stdio keeps key handling uniform. ScrapeGraphAI's README flags that hosted URL as deprecating, so re-check before ever switching.
