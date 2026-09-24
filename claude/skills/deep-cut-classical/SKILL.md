---
name: deep-cut-classical
description: Find obscure classical works by skipping the overplayed canon. Use whenever user asks for classical recommendations, says bored of Beethoven/Mozart/Tchaikovsky, wants new orchestral works, new symphony/concerto/overture to explore, says ulw-research classical, or wants deep cuts beyond usual suspects. Triggers even if user does not name this skill.
---

# Deep-Cut Classical Work Finder

Recommend unfamiliar orchestral works. Default bias: exclude famous, over-recorded repertoire. Dig past canon. Work-level only. Every pick names a specific work with verified timing.

## Core rule

Never recommend a banned composer unless the user explicitly names it to unban it. No "just one Beethoven exception." Unbanning is scoped to that composer, that turn — "allow Dvorak this once" unlocks only Dvorak, not the rest of the list.

If the user names a banned work as a style reference ("I like Rach 2, what next?"), use it as an anchor only, never as a pick. State the anchor once — "Anchor: [banned work] -> deep-cut works below" — then drop it.

## Ban list — see `references/exclusions.md`

Full composer list, origins, reasons, era bans, and exclusion-specific edge cases (explicit-unban compliance, arrangement-loophole rule) live there, not here. Read it before any recommendation pass — skip every composer it lists unless the user names that composer explicitly.

## Priority order

1. Orchestral composers first: substantial symphony, concerto, tone poem, overture, suite output.
2. Chamber: ignore unless the user explicitly asks — the ask must use one of these words: chamber, quartet, trio, sonata, solo piano, solo instrumental.
3. Vocal: deprioritize to last resort. When forced to include it, order choral-orchestral composers before solo-vocalist composers, and flag the fallback: `[slim-pickings vocal fallback]`. Never lead with vocal.

## ulw-research hook

Two modes, same ban list and priority order in both:

- Keyword `ulw-research` present: run a full research pass. Extract the checkable claims (composer dates, era, output types, durations, movement breakdowns, instrumentation) and load the `rigorous-research` skill, supplying the source order below as this pass's domain-specific ordering — `rigorous-research`'s tier ladder, pass protocol, and burn guards apply as normal; only the source list is classical-specific. Apply this skill's own "Timing verification" rules to every duration claim `rigorous-research` returns. Return an evidence-backed shortlist.
- Keyword absent: answer from knowledge directly. No web calls required unless a composer detail is uncertain.

The keyword controls depth, not taste — it never lifts a ban.

## Source order (verify in this order)

1. Grove / Oxford reference for composer dates, era, output
2. Publisher pages (Universal, Barenreiter, Schott, Eschig) for scoring and catalog scope
3. Orchestra program notes (LSO, Berlin Phil, Concertgebouw, LA Phil) for context
4. Labels with deep catalog: Chandos, Hyperion, BIS, Naxos, CPO, Capriccio
5. For release/discography lookups (catalog numbers, pressing detail, "every recording of this work"): `web-data-apis` skill's `references/discography-search.md` — entry-point → trace → verify method and citation sources.
6. Streaming / YouTube only for a listen pointer, never for facts

If sources conflict on dates, prefer the catalog entry. State the conflict in one line.

## Timing verification (mandatory)

Rules for every duration stated:

1. Cite the publisher-stated duration (if any) plus two independent label track totals (Naxos / CPO / Chandos / Hyperion / BIS / Discogs / Presto). Give the movement breakdown with the sum. Example: Glass 5 CPO 35:20 = 10:28 + 6:42 + 5:50 + 12:20.
2. Cross-check the movement sum yourself; if it contradicts the stated total, say so. Never copy an album total that covers two works (Apple 1h29 = Sym7+Sym3; Naxos 68:26 = Glass 5+6).
3. Flag complete-vs-cut for any work with known cuts. Paderewski's cuts fall in movement I and the finale per Hyperion — state "74:13 complete Maksymiuk – 63:39 cut Boguszewski/DUX." Never collapse to one number.
4. If recordings differ beyond tempo variance, state the range with names: "35:36 Raiskin – 41:37 Todorov." Never collapse to a memory number.
5. Copy instrumentation exactly from the publisher score/parts. Never add chorus, organ, or soloists unless the publisher/label lists them.
6. Disambiguate namesakes — Louis Glass (1864-1936) is not Philip Glass (1937-). Check this every time.
7. Forum posts (TalkClassical, Reddit) are leads only, never a timing source on their own; back every forum-sourced number with a publisher or label citation.
8. For a length-constrained request (e.g. 45-60 min, "epic"), exclude a work whose verified maximum falls below the requested minimum. Glass 5's max is 41:37, so it's excluded from a 45+ request.
9. Never claim a finale or chorus without movement-track evidence. Mark an unverifiable claim `[unverified — dropped]` and omit it from length-filtered answers.

## Output format

Work-level only. Every pick names one specific work. For each pick, return:

```
Composer (dates) — Work, Op./Cat. (year) [forces, duration with two timing sources]
Evidence:
- [review / program note / composer note / analysis]: sourced fact about scoring, form, theme treatment, reception. Name the source.
- [second source, different type where possible]: same.
Start with: movement/section to sample first + what to listen for per cited analysis.
Recording: one specific recording (conductor / orchestra / label).
```

Every duration carries its two timing sources — no unsourced numbers. The timing verification rules above apply to every pick.

Default 5 works, max 10, minimum 3. An explicit 20/30-work request overrides the max.

Always end with one line: `Skipped: [banned names relevant to request] excluded per ban list.`

## Edge cases

- Request scope is unclear: default to orchestral, post-1750, non-chamber, non-vocal.
- Pre-1750, non-Baroque/Medieval (e.g. Renaissance): not banned, just outside default scope — an explicit request for it is honored, same as chamber/vocal.
