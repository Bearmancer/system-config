---
name: rigorous-research
description: "Tiered, multi-source verification engine: take a list of checkable claims, run a cheap→grounded→contested ladder across the web-data MCP fleet, fan parallel research passes out when the claim list justifies it, and return every claim as claim → verdict → URL → quote. Self-activates whenever a task requires facts to be checked rather than recalled — verifying dates, figures, names, chronology, attributions or contested statements; fact-checking a source; or any request to research something properly, rigorously, or with citations. Does NOT wait for a trigger word: invoke it from other skills and from ordinary requests alike. Routes tool selection through the web-data-apis skill's capability table rather than choosing servers itself."
---
# Rigorous Research

Tiered, multi-source claim verification. Runs under OpenCode + oh-my-openagent (OMO) — the only runtime this domain has. No portability guarding, no alternate-host fallback: `team_create`, `team_task_create`, and `skill()` are OMO tools, called directly.

## Input contract

**The caller extracts the claims; this skill begins at "claim list in."** This skill does not read, segment, or mine source content — it receives an already-extracted list of checkable claims and returns a verdict per claim. Claim extraction from chapter text, transcripts, or any other source material belongs to the calling skill.

## Tier ladder

- **Tier 0 (cheap):** cached search + highlights/chunks, score > 0.7, dedupe canonical URL, wiki paired with a second source.
- **Tier 1 (grounded):** search-then-extract on selected URLs, `maxAge` 0 / refresh only stale, full markdown, query-reranked.
- **Tier 2 (contested):** 2+ independent domains + a primary source + counter-search + `observed_at`/`valid_at`; code-verify behavior claims; unresolved/refuted claims go to an annex, never into the synthesis.

## Pass protocol — the ungated default

1-2 parallel research passes via research subagents. Each pass receives: the claim list, the source ordering defined below (see "Source selection and handling"), and the required output format.

Output shape per claim: `claim → verdict (confirmed / partially correct / wrong / unfindable) → URL → quote`. Loop until every claim resolves; stop after 5 passes and mark whatever remains plainly unverified — a claim with no witness stays unverified. Coordinate passes so each claim is searched once.

This path runs unconditionally, regardless of `team_mode.enabled` — see the gating note under "Fan-out threshold" below.

## Fan-out threshold

Default to **2 parallel passes** — the existing upper bound. Escalate to a full worker-per-axis fan-out only when the claim list splits into **3 or more distinct source territories** (e.g. court records / contemporaneous press / scholarship), or when 2 passes have not resolved every claim by **pass 3 of the 5-pass budget**. Below that, 2 passes is the correct answer and spinning up a team is waste.

**`team_mode.enabled` gates only the escalation above this threshold; the default 1-2 pass path below it runs unconditionally.**

## Fan-out contract — the gated escalation

When the fan-out threshold above is crossed, call `team_create`, then `team_task_create` once per claim cluster or source territory — one member per axis, never two members on the same angle. Call them directly: these are OMO tools, unconditionally available, and they require no trigger keyword from the user. Do not wait for the user to type "team mode".

The only gate is `team_mode.enabled` in `~/.omo/omo.jsonc`. If it is false, **report the fan-out as blocked and stop escalating** — do not substitute another orchestration mechanism. The default pass path above is unaffected and continues to run.

Members research their axis and report. No member stands up its own team, loads this skill, or fans out further.

## Source selection and handling

Single home for every source-choice rule:

- **Apparatus first:** start from the source's own apparatus (its description / bibliography citations), then add independent sources.
- **Preference ordering:** primaries → records → press → scholarship → wikis.
- **Pairing:** wiki paired with a second source; distributor-run wikis treated as a second source alongside a primary.
- **Labelling:** advocacy sources labelled as advocacy.
- **Attribution hygiene:** "as quoted in the source", "attributed to X, primary not located".

## Burn guards

Map before crawl with an explicit limit; never `raw_content` at scale; never request a summary for a large N that goes unused; pin agent effort and bound arrays; pilot-measure bytes-per-record on 50-100 pages; block media and fonts; track cost per usable record.

## Tool routing — pointer only

Do not choose servers here. Call `skill(name="web-data-apis")` and pick from its capability table, citing the row you used.

## Failover — pointer only

Credit exhaustion during a research pass: the rotation mechanics, the hard-stop rule, and the never-read-`~/.secrets/.env` prohibition live in `learning-course` skill's "API key failover" section. Consult it there — not restated here.
