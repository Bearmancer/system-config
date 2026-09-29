# deep-research skill edit: review record (#33 steps 4, 7, 8)

These are independent Opus code-review passes on the live skill (`~/.claude/skills/deep-research/SKILL.md` and `references/fleet.md`), each diffed against the pre-edit copies. The edit is mirrored in system-config commit `e630ec3`. Sources of truth: `.claude/docs/research/mcp-cli-post-matrix.md` and `mcp-tool-catalog.md`, the skill sidecar `mcp.json`, and the captain decisions recorded on #33.

## Round 1 (2026-09-29): FAIL on both axes

The review found 11 issues.
- **HIGH:** removing "disabled by default" for AgentQL and Browserbase was wrong, because the OmO sidecar `mcp.json` still has `"enabled": false` for both.
- **MEDIUM:**
  - The #45 gap was stated twice, and line 79 described a workaround.
  - Step 8 named a CLI before MCP `scrape_as_markdown`.
  - Step 7 routed to `@playwright/cli` instead of the Playwright MCP.
  - The matrix pointer named a file that was not on master.
- **LOW:** 6 more:
  - the #37–#43 mapping was not confirmed;
  - some cells said `none` where `-` was meant;
  - the README-documented legend was copied inline;
  - there was temporal wording;
  - "aggressively" was not checkable;
  - the pin sentence was missing.

All 11 were fixed in a Sonnet executor pass. Three follow-up edits were then made in the main session: stage 5 wording, the frontmatter description, and the fleet.md sidecar note.

## Round 2 (2026-09-30): PASS on both axes

- **Axis 1 (spec and facts): PASS.**
  - All 11 round-1 findings are confirmed fixed, with line citations.
  - Every tool name, CLI command, endpoint and issue number matches the matrix, the catalog and `mcp.json`.
  - LOW notes:
    - The live Tavily MCP tool spelling is unpinned (source-derived `tavily_extract`).
    - The Apify crawl/map POST cell is `-`, which fits the legend.
- **Axis 2 (standards): PASS.** The files are caveman-compressed and state current facts only, each rule has one home, and SKILL.md and fleet.md do not contradict each other. LOW notes:
  - "before research" was duplicated at SKILL.md:17 (fixed after the review).
  - `references/domains/music/classical/recommend.md:8` sets a default scope, which could read as skipping intake. This is outside the diff.
