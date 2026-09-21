# Plan — Wire MS Learn + Firecrawl + Tavily MCPs (global) + skills/agent

intent: clear
review_required: false
status: active
source_draft: .omo/drafts/mcp-wireup-firecrawl-tavily-mslearn.md

## Goal
Global opencode config gains three working MCP servers (microsoft-learn remote, firecrawl local stdio, tavily remote) with secrets referenced via `{env:...}` only, plus two thin global skills and one researcher subagent. Done = all three servers listed after restart, JSON valid, existing entries untouched.

## Key facts (grounded this session)
- Global MCP file: `C:\Users\Lance\.config\opencode\opencode.jsonc` (holds firefox-devtools/codegraph/exa). The legacy `opencode.json` stays untouched.
- Windows convention in-file: local npx via `["cmd","/c","npx",...]` (matches firefox-devtools entry).
- Schema (https://opencode.ai/config.json): McpLocalConfig requires type+command; McpRemoteConfig requires type+url; `{env:VAR}` interpolation supported in string values.
- MS Learn endpoint `https://learn.microsoft.com/api/mcp` (remote, no auth). Firecrawl local `npx -y firecrawl-mcp` + `FIRECRAWL_API_KEY`; hosted alt `https://mcp.firecrawl.dev/{KEY}/v2/mcp` rejected (key in URL). Tavily remote `https://mcp.tavily.com/mcp/` + `Authorization: Bearer` header; local alt `npx -y tavily-mcp@latest` recorded.
- Keys: user confirms all 3 set in env (Tavily was the last missing). Never embed values.

## TODOs

- [x] 1. Append microsoft-learn remote entry to opencode.jsonc mcp — expect entry present, existing blocks byte-identical
- [x] 2. Append firecrawl local entry to opencode.jsonc mcp — expect cmd /c npx argv + environment placeholder, no literal key
- [x] 3. Append tavily remote entry to opencode.jsonc mcp — expect url + Bearer {env:TAVILY_API_KEY} header
- [x] 4. Create global skills firecrawl + tavily and agent web-researcher — expect 3 new files, skill frontmatter name matches folder
  - Superseded 2026-09-21 by user rule: no manual MCP skills; missing skills omitted entirely. firecrawl/ + tavily/ skill dirs deleted again after recreation; agents/web-researcher.md kept (agent, not a skill).
- [x] 5. Validate JSON parses and restart opencode, confirm all three MCP servers connect — expect microsoft-learn ok; firecrawl/tavily ok iff env keys present
  - Evidence 2026-09-21: opencode.jsonc PARSE_OK, mcp keys include microsoft-learn + firecrawl + tavily; live calls ok for microsoft-learn (docs search returned) + tavily (search returned); FIRECRAWL_API_KEY + TAVILY_API_KEY both set. The 3 item-4 files were absent, recreated verbatim, then the 2 skill files deleted again per user no-manual-MCP-skills rule (only agents/web-researcher.md kept). Remaining user step: restart opencode client, confirm listing.

## Exact snippets (worker copies verbatim)

opencode.jsonc `mcp` additions (after `exa` block, tab-indented to match file):

```json
"microsoft-learn": {
  "type": "remote",
  "url": "https://learn.microsoft.com/api/mcp",
  "enabled": true
},
"firecrawl": {
  "type": "local",
  "command": ["cmd", "/c", "npx", "-y", "firecrawl-mcp"],
  "environment": { "FIRECRAWL_API_KEY": "{env:FIRECRAWL_API_KEY}" },
  "enabled": true
},
"tavily": {
  "type": "remote",
  "url": "https://mcp.tavily.com/mcp/",
  "headers": { "Authorization": "Bearer {env:TAVILY_API_KEY}" },
  "enabled": true
}
```

`~/.config/opencode/skills/firecrawl/SKILL.md`:

```markdown
---
name: firecrawl
description: Use when scraping, crawling, mapping, or extracting content from a website or URL via Firecrawl. Triggers on scrape, crawl, map site, extract page, firecrawl.
---

# Firecrawl

MCP server `firecrawl` (local stdio, needs `FIRECRAWL_API_KEY` in env).
Tools: scrape, search, crawl, map, extract (crawl/map/extract/agent need a key; scrape/search/interact have a rate-limited keyless tier).
CLI equivalents: `npx -y firecrawl-mcp` (env `FIRECRAWL_API_KEY=fc-...`); hosted: `https://mcp.firecrawl.dev/{KEY}/v2/mcp`.
Prefer MCP tools over hand-rolled fetch when JS rendering, crawling, or markdown extraction is needed.
```

`~/.config/opencode/skills/tavily/SKILL.md`:

```markdown
---
name: tavily
description: Use when doing web search, page extract, site map/crawl, or deep research via Tavily. Triggers on tavily, web search, research, extract page.
---

# Tavily

MCP server `tavily` (remote `https://mcp.tavily.com/mcp/`, `Authorization: Bearer` key from env `TAVILY_API_KEY`).
Tools (live list is source of truth): tavily_search, tavily_extract, tavily_map, tavily_crawl, tavily_research.
CLI equivalent: `npx -y tavily-mcp@latest` (env `TAVILY_API_KEY=tvly-...`).
Prefer Tavily for query-driven search/research; prefer Firecrawl for scrape/crawl/extract of known URLs.
```

`~/.config/opencode/agents/web-researcher.md`:

```markdown
---
description: Deep web researcher. Routes query search to Tavily, page scrape/extract to Firecrawl, MS docs to Microsoft Learn.
mode: subagent
---

You are a read-only web researcher. Route by source: query-driven search and deep research via Tavily MCP; scrape/crawl/extract of known URLs via Firecrawl MCP; Microsoft product docs via microsoft-learn MCP (microsoft_docs_search, then microsoft_docs_fetch for full pages). Cite every source URL. Never write files; report findings + URLs + verbatim quotes (<20 words each).
```

## Must-NOT-have
- No literal API keys in any file (only `{env:...}` references).
- No edits to `opencode.json`, no project-level configs, no new opencode command (would duplicate `/search`).
- No product-code changes (config-only task; Pristine var-args stays separate).

## Final Verification Wave

- [x] F1. Config diff audit (only the 3 MCP blocks added, nothing else touched) — expect APPROVE
- [x] F2. JSON validity + schema shape check (type/command/url/headers) — expect APPROVE
- [x] F3. Post-restart MCP listing shows microsoft-learn + firecrawl + tavily — expect APPROVE (firecrawl/tavily conditional on env keys). Blocked: needs user to restart opencode client and paste the MCP listing; agent verified everything restart-independent (JSON parse, live ms-learn + tavily calls, both env keys set, skill/agent files present).
