# Classical: recommend mode

Unfamiliar works, overplayed canon out. Work-level only: every pick names one work with verified timing.

## Steps

1. Confirm SKILL.md domain reads done (classical `sources.md`, `exclusions.md`, music `rules.md`). Done when ban list + streaming domain list in context.
2. Scope: unclear ask = orchestral, post-1750, non-chamber, non-vocal. Renaissance: outside default, not banned; honour explicit ask. Medieval/Baroque: state era ban, decline.
3. Candidates by priority: orchestral first (symphony, concerto, tone poem, overture, suite); chamber only when ask says chamber/quartet/trio/sonata/solo; vocal last, choral-orchestral before solo-vocal, flag `[slim-pickings vocal fallback]`.
4. Banned work named as taste ("I like Rach 2"): anchor only. State once `Anchor: [work] -> deep-cut works below`, never a pick.
5. Verify each candidate via SKILL.md passes: dates, era, forces, movements, durations per `../rules.md` "Timing". Done when every pick carries two timing sources or is dropped.
6. Output picks, then `Skipped: [banned names relevant to request] excluded per ban list.`

## Pick block

```
Composer (dates) — Work, Op./Cat. (year) [forces, duration with two timing sources]
Evidence:
- [review / program note / composer note / analysis]: sourced fact on scoring, form, theme treatment, reception. Name source.
- [second source, different type where possible]: same.
Start with: movement/section to sample first + what to listen for per cited analysis.
Recording: one recording (conductor / orchestra / label).
```

Count: default 5, min 3, max 10; explicit 20/30 request overrides max.
