---
name: deep-cut-classical
description: Find obscure classical works by skipping the overplayed canon. Use whenever user asks for classical recommendations, says bored of Beethoven/Mozart/Tchaikovsky, wants new orchestral works, new symphony/concerto/overture to explore, says ulw-research classical, or wants deep cuts beyond usual suspects. Triggers even if user does not name this skill.
---

# Deep-Cut Classical Work Finder

Recommend unfamiliar orchestral works. Exclude famous, over-recorded repertoire. Work-level only: every pick names one specific work with verified timing.

## Core rules

- **Ban list:** read `references/exclusions.md` before every recommendation pass. Skip every listed composer unless the user names that composer to unban it. Unban scope = that composer, that turn ("allow Dvorak this once" unlocks Dvorak only). No "just one Beethoven exception."
- **Banned work as style reference** ("I like Rach 2, what next?"): anchor only, never a pick. State once — "Anchor: [banned work] -> deep-cut works below" — then drop it.
- **Music streaming services: ignore entirely** (Spotify, Apple Music/Classical, Amazon Music, YouTube Music, Tidal, Deezer, Qobuz, Idagio, etc.). Never search, fetch, cite, link, or mention them — no facts, timings, credits, or listen pointers; `Recording:` names conductor/orchestra/label only. Exclude their domains on every search and discard any result landing on one; full service + domain list: `web-data-apis` `references/discography-search.md`. Fact whose only witness is streaming: `[unverified — dropped]`. Applies in both depth modes, including knowledge-only answers. YouTube is not in this ban: listen pointer only, never facts or timings.

## Priority order

1. Orchestral first: substantial symphony, concerto, tone poem, overture, suite output.
2. Chamber: only when the ask uses chamber, quartet, trio, sonata, solo piano, or solo instrumental.
3. Vocal: last resort. Choral-orchestral before solo-vocal; flag `[slim-pickings vocal fallback]`. Never lead with vocal.

## Depth: `ulw-research` keyword

- Present: extract checkable claims (dates, era, output types, durations, movement breakdowns, instrumentation), load `rigorous-research` with the source order below as its domain ordering, apply Timing verification to every returned duration. Return an evidence-backed shortlist.
- Absent: answer from knowledge. Web calls only when a composer detail is uncertain.

Keyword controls depth, never lifts a ban.

## Source order

1. Grove / Oxford reference: composer dates, era, output.
2. Publishers (Universal, Barenreiter, Schott, Eschig): scoring, catalog scope.
3. Orchestra program notes (LSO, Berlin Phil, Concertgebouw, LA Phil): context.
4. Deep-catalog labels: Chandos, Hyperion, BIS, Naxos, CPO, Capriccio.
5. Release/discography lookups (catalog numbers, pressings, "every recording"): `web-data-apis` skill's `references/discography-search.md`.

Sources conflict on dates: prefer the catalog entry; state the conflict in one line.

URL audit: every URL emitted passes `web-data-apis` SKILL.md "URL audit" (200 or firecrawl-verified) before it reaches the user.
## Timing verification (every duration)

1. Cite publisher-stated duration (if any) plus two independent label track totals (Naxos / CPO / Chandos / Hyperion / BIS / Discogs / Presto). Give the movement breakdown with its sum. Example: Glass 5 CPO 35:20 = 10:28 + 6:42 + 5:50 + 12:20.
2. Cross-check the movement sum; say so if it contradicts the stated total. Never copy an album total covering two works (Naxos 68:26 = Glass 5+6).
3. Flag complete-vs-cut for works with known cuts: "74:13 complete Maksymiuk – 63:39 cut Boguszewski/DUX" (Paderewski cuts in mvt I + finale per Hyperion). Never collapse to one number.
4. Recordings differ beyond tempo variance: state the range with names ("35:36 Raiskin – 41:37 Todorov"). Never a memory number.
5. Instrumentation exactly from publisher score/parts. Never add chorus, organ, or soloists the publisher/label doesn't list.
6. Disambiguate namesakes every time — Louis Glass (1864-1936) is not Philip Glass (1937-).
7. Forum posts (TalkClassical, Reddit) = leads only; back every forum number with a publisher or label citation.
8. Length-constrained request (e.g. 45-60 min): exclude works whose verified maximum is below the minimum (Glass 5 max 41:37, excluded from 45+).
9. No finale/chorus claim without movement-track evidence. Unverifiable claim: `[unverified — dropped]`, omitted from length-filtered answers.

## Output

Per pick:

```
Composer (dates) — Work, Op./Cat. (year) [forces, duration with two timing sources]
Evidence:
- [review / program note / composer note / analysis]: sourced fact about scoring, form, theme treatment, reception. Name the source.
- [second source, different type where possible]: same.
Start with: movement/section to sample first + what to listen for per cited analysis.
Recording: one specific recording (conductor / orchestra / label).
```

Default 5 works, min 3, max 10; an explicit 20/30-work request overrides the max. End with: `Skipped: [banned names relevant to request] excluded per ban list.`

## Edge cases

- Unclear scope: orchestral, post-1750, non-chamber, non-vocal.
- Pre-1750 non-Baroque/Medieval (e.g. Renaissance): outside default scope, not banned; honor an explicit request.
