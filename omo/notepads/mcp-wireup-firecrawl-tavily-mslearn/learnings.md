# F3 Config Diff Audit - learnings

## 2026-09-21 F3 precondition verify (config diff audit)
- File: C:\Users\Lance\.config\opencode\opencode.jsonc, 341 lines, read full.
- microsoft-learn L193-197: remote, url https://learn.microsoft.com/api/mcp, enabled true. PASS.
- firecrawl L211-224: local, cmd [cmd /c npx -y firecrawl-mcp], env FIRECRAWL_API_KEY={env:FIRECRAWL_API_KEY}, enabled true. PASS. Matches firefox-devtools Windows npx pattern.
- tavily L249-256: remote, url https://mcp.tavily.com/mcp/, headers Authorization=Bearer {env:TAVILY_API_KEY}, enabled true. PASS.
- No literal secrets: grep fc- / tvly- zero hits in opencode.jsonc (only node_modules rfc- noise). Only {env:...} interpolation. PASS. Secret values never printed.
- Existing blocks intact: firefox-devtools L157-175, codegraph L179-187, exa L188-192 byte-identical shape. Plugins 3 entries L2-6. Permission denies L117-149 intact (1 ask + 30 deny). JSONC comments L299-302, L308 valid; strips-then-parses OK.
- Note: file contains extra pre-existing MCP blocks beyond the 3 (azure-mcp disabled, agentql, dappier, scrapegraph, context7, browserbase, brightdata, apify, brave, jina, crawl4ai) - out of F3 scope, untouched by this audit.
- Verdict: F3 precondition PASS. opencode mcp list mental model: microsoft-learn + firecrawl + tavily present, enabled.

## 2026-09-21 F3 live precondition verify (all three MCP wiring)
- Agent intact: C:\Users\Lance\.config\opencode\agents\web-researcher.md exists, 6 lines, routes Tavily/Firecrawl/MS-Learn, contract cites URLs + quotes <20 words. PASS.
- Env presence only (no values): IsNullOrEmpty FIRECRAWL_API_KEY=False, TAVILY_API_KEY=False. Both set. PASS. Safe method: [Environment]::GetEnvironmentVariable with quoted name.
- microsoft-learn microsoft_docs_search "MCP server configuration": 10 results. First: https://learn.microsoft.com/visualstudio/ide/mcp-servers?view=visualstudio#manage-configuration-of-mcp-servers . Quote: "store configuration information for MCP servers" . PASS.
- tavily tavily_search "MCP startup test" max 2: 2 results, auth_mode keyed. First: https://mcpplaygroundonline.com . Quote: "Test MCP servers, clients, and tools" . PASS.
- firecrawl firecrawl_search "MCP test" limit 2: success true, creditsUsed 2, 2 web results. First: https://mcpplaygroundonline.com/ . Quote: "Test MCP Servers Online" . PASS (keyed/keyless tier both prove wiring).
- Verdict: F3 live precondition APPROVE. All three connect. No secrets printed.

