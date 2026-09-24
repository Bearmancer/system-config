---
name: rigorous-research
description: "Tiered, multi-source verification engine: take a list of checkable claims, run a cheap→grounded→contested ladder across the web-data MCP fleet, fan parallel research passes out when the claim list justifies it, and return every claim as claim → verdict → URL → quote. Self-activates whenever a task requires facts to be checked rather than recalled — verifying dates, figures, names, chronology, attributions or contested statements; fact-checking a source; or any request to research something properly, rigorously, or with citations. Does NOT wait for a trigger word: invoke it from other skills and from ordinary requests alike. Routes tool selection through the web-data-apis skill's capability table rather than choosing servers itself."
---

# Rigorous Research

## Input contract

**The caller extracts the claims; this skill begins at "claim list in."** This skill does not read, segment, or mine source content — it receives an already-extracted list of checkable claims and returns a verdict per claim. Claim extraction from chapter text, transcripts, or any other source material belongs to the calling skill.

## Tier ladder

- **Tier 0 (cheap):** cached search + highlights/chunks, score > 0.7, dedupe canonical URL, wiki paired with a second source.
- **Tier 1 (grounded):** search-then-extract on selected URLs, `maxAge` 0 / refresh only stale, full markdown, query-reranked.
- **Tier 2 (contested):** 2+ independent domains + a primary source + counter-search + `observed_at`/`valid_at`; code-verify behavior claims; unresolved/refuted claims go to an annex, never into the synthesis.

## Pass protocol

1-2 parallel research passes via research subagents. Each pass receives: the claim list, the source ordering defined below (see "Source selection and handling"), and the required output format.

Output shape per claim: `claim → verdict (confirmed / partially correct / wrong / unfindable) → URL → quote`. Loop until every claim resolves; stop after 5 passes and mark whatever remains plainly unverified — a claim with no witness stays unverified. Coordinate passes so each claim is searched once.

**Looping on request.** When the caller asks for another pass on claims already run through this skill, the response opens with the exhausted-resources list for those claims: every domain, source, and tool already queried, per claim, before any new pass starts. The new pass targets sources outside that list; querying an already-exhausted source again is not a new pass. The exhausted-resources list stays in the output alongside the claim → verdict → URL → quote table, not folded into it.

### Scaling beyond 2 passes

Default to **2 parallel passes**. A claim list needing more (3+ distinct source territories, or unresolved claims by pass 3) is the calling session's orchestration call, not this skill's: hand it the claim list, source ordering, and output format, split by axis, one worker per axis.

## Source selection and handling

Single home for every source-choice rule:

- **Apparatus first:** start from the source's own apparatus (its description / bibliography citations), then add independent sources.
- **Preference ordering:** primaries → records → press → scholarship → wikis.
- **Pairing:** wiki paired with a second source; distributor-run wikis treated as a second source alongside a primary.
- **Labelling:** advocacy sources labelled as advocacy.
- **Attribution hygiene:** "as quoted in the source", "attributed to X, primary not located".

**Domain-supplied source order.** A caller with its own authoritative source ordering (e.g. `deep-cut-classical`'s Grove → publisher → program-notes → label order) passes that ordering as this pass's source list in place of the default preference ordering above. The tier ladder, pass protocol, and burn guards stay this skill's job regardless of whose source order is in effect.

## Burn guards

Map before crawl with an explicit limit; never `raw_content` at scale; never request a summary for a large N that goes unused; pin agent effort and bound arrays; block media and fonts.

## Tool routing and failover — pointer only

Do not choose servers here: load the `web-data-apis` skill, pick from its capability table (citing the row used), and consult its "API key failover" section for credit-exhaustion rotation — not restated here.
