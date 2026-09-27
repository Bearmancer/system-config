---
name: rigorous-research
description: "Whenever a research or search query or analysis is requested: a tiered, multi-source verification engine: take a list of checkable claims, run a cheap→grounded→contested ladder across the web-data MCP fleet, fan parallel research passes out when the claim list justifies it, and return every claim as claim → verdict → URL → quote. Self-activates whenever a task requires facts to be checked rather than recalled — verifying dates, figures, names, chronology, attributions or contested statements; fact-checking a source; or any request to research something properly, rigorously, or with citations."
---

# Rigorous Research

## Input contract

Input = already-extracted claim list. Output = verdict per claim. Claim extraction from any source material (chapters, transcripts, etc.) belongs to the caller; this skill never reads or mines source content.

## Tier ladder

- **Tier 0 (cheap):** cached search + highlights/chunks, score > 0.7, dedupe canonical URL, wiki paired with a second source.
- **Tier 1 (grounded):** search-then-extract on selected URLs, `maxAge` 0 / refresh only stale, full markdown, query-reranked.
- **Tier 2 (contested):** 2+ independent domains + a primary source + counter-search + `observed_at`/`valid_at`; code-verify behavior claims; unresolved/refuted claims go to an annex, never into the synthesis.

## Pass protocol

1-2 parallel research passes via research subagents. Each pass gets: claim list, source ordering (below), output format.

Output shape per claim: `claim → verdict (confirmed / partially correct / wrong / unfindable) → URL → quote`. Loop until every claim resolves; stop after 5 passes and mark whatever remains plainly unverified — a claim with no witness stays unverified. Coordinate passes so each claim is searched once.

**Another pass on already-run claims:** open with the exhausted-resources list (every domain, source, tool already queried, per claim). New pass targets only sources outside it; re-querying an exhausted source is not a new pass. Keep that list as its own block beside the verdict table.

### Scaling beyond 2 passes

Default **2 parallel passes**. Needing more (3+ distinct source territories, or unresolved by pass 3) = caller's orchestration decision: hand it claim list, source ordering, output format, split by axis, one worker per axis.

## Source selection and handling

- **Apparatus first:** start from the source's own apparatus (its description / bibliography citations), then add independent sources.
- **Preference ordering:** primaries → records → press → scholarship → wikis.
- **Pairing:** wiki paired with a second source; distributor-run wikis treated as a second source alongside a primary.
- **Labelling:** advocacy sources labelled as advocacy.
- **Attribution hygiene:** "as quoted in the source", "attributed to X, primary not located".

URL audit: every URL emitted passes `web-data-apis` SKILL.md "URL audit" (200 or firecrawl-verified) before it reaches the user.
**Domain-supplied source order:** a caller's own ordering (e.g. `deep-cut-classical` Grove → publisher → program notes → labels) replaces the default preference ordering; caller-level source bans (e.g. music streaming services) also apply. Tier ladder, pass protocol, burn guards unchanged.

## Burn guards

Map before crawl with an explicit limit; never `raw_content` at scale; never request a summary for a large N that goes unused; pin agent effort and bound arrays; block media and fonts.

## Tool routing and failover — pointer only

Load `web-data-apis`; pick servers from its capability table (cite the row used); credit exhaustion → its "Keys + credit failover" section.