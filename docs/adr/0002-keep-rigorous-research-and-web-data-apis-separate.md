# ADR-0002: Keep rigorous-research and web-data-apis as separate skills

## Status

Accepted.

## Context

`rigorous-research` (claim verification: tier ladder, pass protocol, burn guards) always routes tool selection through `web-data-apis` (capability table, server wiring, credit failover) rather than choosing servers itself. Because `rigorous-research` is never invoked without `web-data-apis` in its call chain, merging the two into one skill was raised twice during a restructuring pass over `~/.claude/skills`.

## Decision

Keep them as two skills. Each has a distinct trigger surface (verifying a claim vs. picking a scraping/search tool) and a distinct job (verification protocol vs. tool routing). A frontmatter description is always loaded for every skill in a session, regardless of whether the skill fires; combining two skills with different trigger conditions into one description either bloats that always-loaded text or degrades trigger precision for one of the two surfaces. A skill's body loads in full once its name matches a trigger; merging means a tool-routing-only task also loads verification-protocol content it doesn't need, and vice versa.

Two merge directions were considered and rejected:
- `rigorous-research` folded into `web-data-apis`.
- `web-data-apis` folded into `rigorous-research` (treating tool selection as an implementation detail of verification).

Both were rejected for the same reason: the two concerns are used independently often enough (many tasks call `web-data-apis` for tool selection with no claim to verify) that collapsing them costs more in description bloat and unnecessary body-load than the one-line internal pointer (`rigorous-research` says "load `web-data-apis` and pick from its capability table") costs in indirection.

A related decision from the same pass: `web-data-apis` is written for OpenCode's full MCP server fleet but lives at `~/.claude/skills/`, where a typical Claude Code session has only a subset of those servers wired as tools. Rather than forking the skill per runtime, the OpenCode-exclusive companion-skill list was moved out to `~/.config/opencode/AGENTS.md` (`<web_data_companion_skills>`), and the shared skill kept assuming its documented fleet is live — no availability-check or per-runtime routing logic was added to the shared file.

Also decided in the same pass: `github-create-issue`, `github-create-pr`, and `github-create-feature` (three sibling skills sharing near-identical diagnostic-bar structure and a `references/shared-conventions.md`) were merged into one `github-create` skill, since — unlike the rigorous-research/web-data-apis case — their per-shape content (closure triage vs. upstream triage vs. feature triage) differs enough to live as sections of one file rather than three files, and their trigger conditions (issue vs. PR vs. feature) are cleanly distinguishable within a single description.

## Consequences

- `rigorous-research`, `web-data-apis`, and `learning-course` remain a three-layer stack (workflow → verification protocol → tool routing; see CONTEXT.md).
- Any future skill that needs claim verification loads `rigorous-research` by name; any skill that needs tool selection loads `web-data-apis` by name. Neither absorbs the other's trigger surface.
- If a second domain skill (beyond `deep-cut-classical`) ever needs its own source-order override, revisit whether `rigorous-research/references/source-profiles.md` (a named-profile file) is worth the added indirection over the current single-paragraph override — deferred, not needed while only one caller uses it.
