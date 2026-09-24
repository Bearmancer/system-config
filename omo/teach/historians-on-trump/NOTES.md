# Notes — chapter map, extraction recipe, course-source pointers, queue

## Chapter map (Wave1 decision)

| # | Section | Date-span | Essential? |
|---|---------|-----------|------------|
| 1 | NYT April survey — 35 historians, 22 actions, 4 buckets | Apr 2025 | yes |
| 2 | NYT December survey — 36 experts, second round | Dec 2025 | yes |
| 3 | C-SPAN 2021 survey — 142 historians, 10 traits, 41/44 | 2021 | yes |
| 4 | PGP 2024 + Siena 2022 — ranking instruments compared | 2022–2024 | yes |
| 5 | The denial claim — Meacham degree-vs-kind | 2020–2026 | yes |
| 6 | No-firewall + steroids — Brinkley monetization, Riley frame | 2025 | yes |
| 7 | Historian frames — dictatorship, braggadocio, norms rupture | 2025–2026 | yes |
| 8 | Annex + method — A1–A3 barred, how the instruments differ | 2021–2026 | skippable |

- Course-source note: primary source is `report.html` in the source dir (ulw-research 20260921-010000-historians-trump). SYNTHESIS pointer: `bg_7f09dd81` full text (local SYNTHESIS.md carries the lock header only). Claim-graph lock: verified C4–C10b / A1–A3 per `claim-graph.md` (from `bg_8e30dca9`); O1–O28 frozen per observation-manifest.
- Ch8 is reference/annex: barred claims stay framing-only; method comparison is the teachable core.

## time_range convention (text source — no video timestamps)

Lessons use `Section N of 8 · <date-span>` in the surtitle slot (the page's only range line). Example: `Section 1 of 8 · Apr 2025`. Calendar dates inside prose are untouched. No `mm:ss` ranges exist for this course; do not invent any.

## Extraction recipe (text source — no yt-dlp)

1. Course source lives at: `C:\Users\Lance\.omo\agents-config\.claude\worktrees\agents-config-setup\omo\ulw-research\20260921-010000-historians-trump\report.html` (+ `.pdf`, `.docx` mirrors).
2. Per-section slice (Wave3): copy the section's report HTML block into `reference/transcripts/sec<N>-<slug>.md`, preserve claim/counter `[C#]/[O#]` tags verbatim, prepend a corrections table (typo / garble → canonical → basis).
3. Cross-check: first claim tag in the slice matches the claim-graph lock range for that section; SYNTHESIS `bg_7f09dd81` output is the verdict authority for C-claims.
4. Re-run rule: slices derive from `report.html` bytes only — never from memory or snippet recall.

## Corrections log

- 2026-09-21 Wave3 slices sec1–sec8 (report.html bytes only): snippet-vs-full-page — NYT Dec22 Sinha boats/felon-nominee quote per BrightData full pages (O2/O25), never snippet recall; PGP figures canonical 10.92/62.66/95.03 with stale Lincoln 93.87 (wave-2 Dappier RT snippet drift) refuted; C-SPAN methodology page (1–10, ten traits, equal, [O4]) vs overall page (41st/312, [O3]) cited separately; Siena overall-last misread refuted (third-worst, category-last stands [C7][O22]); Brinkley MTP 2026-01-20 video-only (O32) never quoted beyond frozen snippet; Roosevelt House + CNN context-only, no single imperial transcript (O18); 228v58 RollCall count qualified, no WH primary [C10][O21].
- Canonical numerals: C-SPAN Trump 41st (312); PGP Trump 10.92 / Biden 62.66 / Lincoln 95.03; EOs 228 vs 58.

## Quirks

- NYT pages are JS-walled (Apify 3/5 200, NYT fail) — BrightData full pages are the frozen primaries (O1, O2, O25).
- No single Brinkley imperial transcript exists (O18) — Roosevelt House + CNN transcripts are context only.
- Beschloss long-form transcript missing (O30); Goodwin MorningJoe transcript absent (O31); Brinkley MTP video-only (O32).

## Queue & standing

- 2026-09-21 — scaffold only (this pass). No lessons, no slices (Wave3), no stamp/check/publish runs.
 - Next: Wave3 slices sec1–sec8 DONE 2026-09-21 → lesson 01 (ch1 NYT April) with verification fan-out per claim-graph lock.
- Skippable: ch8 (annex+method) — build last, reference-first.
