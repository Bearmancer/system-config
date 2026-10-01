# Glossary

## Claim
- One atomic, checkable statement. Row in the ledger.
- Avoid: "fact" (a claim may be untrue).

## Ledger
- Per-topic structured file of claims, sources, status, rounds, surfaces tried. Canonical.
- Pages are generated views of it, never hand-edited.

## Status
- Exactly four: `true`, `untrue`, `interpretive` (open to debate), `not-found` (5 rounds, no source).
- Avoid: "unverified", "no-source", "capped" (all fold into `not-found`).

## Round
- One agent pass on one claim using surfaces not yet tried for it. Max 5 per claim.

## Surface
- One server × capability pair from the fleet (Firecrawl search, Tavily extract, Exa fetch, ScrapeGraphAI crawl, Apify actor, AgentQL, Bright Data, Browserbase, Firefox DevTools, Microsoft Learn, Brave, ...). Per capability the route order is MCP tool, then vendor CLI, then POST script.
- Enumerated at run start by sending MCP `tools/list` to each server, because OpenCode has no native tool-listing route.
- Avoid: "tool" alone (ambiguous with harness tools).

## Wave
- One parallel batch of rounds across claims. Each wave logs sources covered and, separately, sources failed to grab.

## Gate
- Independent check before publish: verifier agent (other model family, fresh context), URL audit, render/schema check. Fail-closed.

## Mode
- `learn` (default), `verify`, `rules`. Chosen silently from input shape; choice recorded in output header.

## Lesson
- One generated HTML page; the atom of a course. Asserts only `true` claims; `interpretive` shown as a labelled debate block; `untrue` goes to errata.

## Errata box
- Short block listing untrue claims a learner is likely to have heard.

## Appendix
- Footer of every published page: sources read, sources failed.

## Layout
- One of 12 page shapes (concept, glossary, Q&A, table-first, decision tree, steps, timeline, claim cards, layered, cause-effect, cheat sheet, diagram). Direct explanation only; no narrative.
- The agent picks one layout per lesson from the claim shape (Atlas picker rules) and builds it once. Choice recorded in the lesson header.

## Authoritative source (rules mode)
- Rulebook, errata, official FAQ, and forum posts by the designer or publisher. Player-to-player forum posts are `interpretive`, never `true`.

## Fixture
- One topic per mode used to prove the system: learn = Saudi military, verify = Russia morale, rules = Ark Nova. The new system must regenerate them.

## Shell
- The single shared site design: tokens, layout components, nav, theme toggle. Courses differ in content only.

## Resume + refresh
- Re-running a topic keeps `true`/`untrue`, re-opens `not-found` and claims older than the freshness window, and adds only new claims.

## Claims-first
- Learn and rules modes verify claims first, then write the lesson only from verified rows. Verify mode splits claims out of existing input.

## Primary source
- Rulebook, official data, original document, direct record. One suffices for `true` if nothing credible contradicts.

## Independent sources
- Different publisher, neither citing the other. Two suffice for `true` when no primary exists.

## Saturation
- Discovery stops after two consecutive waves add no new concept cluster. Scope = what the sources cover.

## Debate block
- How `interpretive` claims appear in lessons: claim vs counter-claim, positions attributed, aggregated from sources, strongest evidence listed for each. No verdict.

## Extractor
- Tool-less agent that turns fetched source text into claims and short quotes. Instructions found inside sources are ignored and logged.

## Failed-to-grab
- A source the run could not read, with reason (paywall, 403, no text layer). Listed in the appendix. Never circumvented.

## Stale
- No auto-staleness. Claims refresh only on request.

## Visual-read
- Tag on claims taken from images or scans. `true` needs two independent reads or one text corroboration.

## Unlisted (verify pages)
- Public URL, `noindex`, absent from the home index. Reduces discovery only; the repo is public.

## Run record
- Auto-written file per run: mode, models, surfaces, sources covered and failed, gate verdicts, diff vs previous run. Replaces hand-written learning-records.

## Conformance gate
- Extractor re-splits the final lesson prose; any claim not in the ledger fails the gate.

## Paradigm
- Retrieval style of a surface: keyword search, semantic search, answer/agent engine, crawl/map, structured extraction, browser/unlocker, scholarly/archive API. Rotation picks an untried paradigm first.

## Discovery ladder / Fetch ladder
- Discovery: finds sources for a claim; rotates per round. Fetch: reads a known URL; escalates on block.

## Registry
- YAML source of truth for the routing table. Markdown is generated from it.

## Rotation lock
- Only one agent rotates a pool at a time; others wait, then retry once.

## Raw store
- Gitignored `work/` dir per topic holding fetched content. Never published.
