# NOTES — political-spectrum

## Chapter map

Single chapter course. Chapter 1 of 1: full spectrum treatise.
Source: synthesis of prior research (no video, no transcript slices).

## YAML shape (from references/lesson-schema.md)

Required fields: kicker, title, chapter (=1, must match -ch1-),
chapters_total (=1), time_range (admin-only, adapted: "research-synthesis"),
transcript (admin-only, adapted: wave file names), lead (§1 plain text),
cast (list of {name, role, ref?}), narrative (§3 restricted HTML, ≥2 verdict
words), machinery (§4 restricted HTML), sources (non-empty, https only,
no YouTube).
Restricted HTML subset in narrative/machinery: p blockquote ul ol li
strong em a. First mention of a URL = bare <a>; every repeat =
<sup><a>n</a></sup>. No bare URL text. No § refs outside 1–4. No timestamps
anywhere in lead/narrative/machinery.

## Row-id rule (from references/stencil-contract.md)

Filename NN-chK-<slug>.html. Row id regex: (?i)-ch0*(\d+) → ch$1.
Top-nav backlink: ../index.html#chK. Home link: ../../index.html.
Stamp fail-closed on: bad filename, chapter mismatch, missing fields,
empty sources, <2 verdict words, unwrapped repeat links, bare URLs,
bad § refs, timestamps, orphan cast refs, YouTube URLs.

## Extraction recipe

N/A (no video). Content drawn from
.omo/ulw-research/20260922-010000-political-spectrum/wave-1-us-synthesis.md
and wave-2-four-axes.md.

## Queue

1. Draft YAML + 3 reference pages. 2. Subgraph SVG. 3. Team reviews.
2. Stamp + gates. 5. Fix + restamp.

## Pinned primaries (2026-09-22 verification)

- Gallup 2024 ideology (37/34/25, GOP 77% cons, Dems 55% lib):
  https://news.gallup.com/poll/655190/political-parties-historically-polarized-ideologically.aspx
- Mudde thin-centered populism definition (UPenn Mitchell Center):
  https://amc.sas.upenn.edu/cas-mudde-populism-twenty-first-century
- Cato mission (liberty, limited govt, free markets, peace):
  https://www.cato.org/about/mission-vision-principles
- Classical liberalism distinction (Wikipedia):
  https://en.wikipedia.org/wiki/Classical_liberalism
- National Review on fusionism (Meyer 1962, Reagan coalition):
  https://www.nationalreview.com/2026/09/where-has-conservatism-been-and-where-is-it-going

## Review log (rewrite, 2026-09-22)

Full rewrite: term-dump narrative replaced with staged teaching (seating,
tool, American translation, three confusions, attachments, DSA worked
example). Cut electoral-sociology detour (diploma divide, Hispanic gap),
NatCon/FreeCon split, Warren-vs-Sanders foreign policy, Mises critique.
Glossary 25 → 16 terms; timeline drops 2008/Jun-2024/1989 rows.

## Expansion pass (2026-09-22)

Lesson 11.4KB → 16.9KB stamped, gate-clean. Restored with citations:
diploma divide (Shepherd + Pew, caveat kept), NatCon/FreeCon statements,
Sharon Statement, LP 2024 convention (CNN), CFR Warren-vs-Sanders, Mises
Nordic critique, Civic Intelligence 250-offices tally, DSA 120k July 2026
(NPC newsletter, passes 1912 SPA peak). Cast 10 → 12 rows (Conservatism US,
Libertarianism). Glossary 16 → 23. Timeline adds 1960/1980s/1989/2008/Jul-2026.
Fixed: Britannica label collision; Cato Mission casing; June qualifier;
Washington endorsed-not-loan gloss; cut unsourced 250-offices tally;
roster qualification; neoliberal-vs-libertarian state-power sentence;
positional-center clause; Liberalism cast entry + sentence + source;
fusionism citation.
Declined with reason: Mises-only critique optional (single-source
exception stands); cast-role cross-refs optional (machinery holds the
test); Liberalism subgraph node deferred (grid rework risk; cast +
glossary + cast-map carry it).

## Merge log (collision resolution, 2026-09-22)

04:14 overwrite by unknown parallel writer: lessons YAML/HTML,
glossary, timeline replaced with expanded variant built on this
workspace (kept structure, SVG, fixes; added PRRI, CNN, Sharon,
NatCon/FreeCon, 120k, Norway nuance, big-tent line, worked example).
User decision: merge manually. Kept their version, restored two
dropped items: June qualifier on independents; roster-side
qualification (Warren progressive capitalist / democratic-socialist
side). Restamped 16935 to 17043 bytes, gates green. Publish held
for sign-off.
