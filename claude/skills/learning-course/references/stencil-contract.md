# Lesson stencil — shape contract (W1)

Freezes what the template owns, what content owns, and what the gate keeps as a
backstop. Rule → owner mapping derived from `scripts/check_lesson.py`,
`references/page-design.md` (the single style doc), and the row-id rule shared
with `publish_teach.py`.

## Row-id contract (shared with the publisher)

- Lesson filename MUST be `NN-chK-<slug>.html` (2-digit lesson number, absolute
  chapter `K`). The stamp HARD-FAILS on a filename without `-chK-`.
- Index row id = `chK`. The publisher derives it with
  `(?i)-ch0*(\d+)` → `ch$1` (fallback `^(\d+)` → `lesson-$1`, then
  `lesson-$fallbackNum` for legacy files only).
- Lesson backlink (top nav, below the heading) = `../index.html#chK`, derived
  from the same capture. One regex, one meaning, both sides.

## Owner table

| #  | Rule (gate check)                                      | Owner                  | Mechanism                                                                                                          |
| -- | ------------------------------------------------------ | ---------------------- | ------------------------------------------------------------------------------------------------------------------- |
| 1  | No quiz block / no "quiz" word                         | Template               | no quiz markup exists                                                                                              |
| 2  | No teacher references                                  | Template               | no teacher blocks exist                                                                                            |
| 3  | No boundary phrases                                    | Template + gate        | template has none; gate scans narrative                                                                            |
| 4  | Surtitle `Chapter N of M` present                      | Template               | rendered from `chapter`, `chapters_total`; no time range, no timestamp anywhere on the page                        |
| 5  | No timestamps anywhere on the page                     | Template + gate        | template emits none; gate scans the whole page, no surtitle exception                                              |
| 6  | No method box / primary-source block / next-on-request | Template               | none exist                                                                                                         |
| 7  | ≥1 hyperlinked source                                  | Content + stamp        | first citation is a full inline `<a href="https://...">` in narrative/machinery; stamp requires it                |
| 8  | No bare URL text                                       | Content + stamp + gate | stamp scans & fails; gate backstop                                                                                 |
| 9  | Link target ≤2 occurrences, repeats superscripted      | Stamp + gate           | first mention bare `<a>`, every repeat `<sup><a>`; stamp pre-counts; gate backstop                                 |
| 10 | No fact-check H2 / box-fact / box-record               | Template               | none exist; verdicts live inline                                                                                   |
| 11 | No "Open Threads"                                      | Template               | none exists                                                                                                        |
| 12 | No Sources/References/Bibliography heading, anywhere   | Template + gate        | citations are inline-only — no separate section ever; gate scans every heading                                    |
| 13 | ≥2 inline verdict words in narrative                   | Content + stamp        | stamp requires ≥2 in `narrative`; gate backstop                                                                    |
| 14 | Footer present (`lesson-footer`)                       | Template               | fixed block, nav = previous/next lesson only                                                                       |
| 15 | Glossary link in top nav                               | Template               | fixed anchor below the heading, not the footer                                                                     |
| 16 | Home link at top, above the kicker, small text         | Template               | fixed `<p class="home-link">` anchor, `../../index.html`, first thing in `<body>`                                  |
| 17 | Chapter-index backlink in top nav                      | Template               | derived from filename via row-id contract, `../index.html#chK`                                                    |
| 18 | Section refs (§N) match headings                       | Template + stamp       | template fixes section numbers 1–4; stamp scans § refs                                                             |
| 19 | No dangling links (except publish-generated)           | Template + stamp       | only `../../index.html` + `../index.html#chK` are allowlisted; every other href must resolve on disk (stamp scans) |
| 20 | Assets resolve                                         | Template               | template emits no `src` (optional subgraph slot is inline SVG)                                                     |
| 21 | Max-twice budget for index targets                     | Stamp                  | `../../index.html` ×1; `../index.html*` ×1 (the top-nav backlink)                                                  |
| 22 | No YouTube URL, anywhere                                | Stamp + gate           | a YouTube URL is never a source; stamp refuses at write time, gate backstop                                        |
| 23 | Headings below H1 use Title Case                       | Template                | `Summary`, `Cast`, `Narrative`, `Machinery`, `Role This Chapter` — fixed text in the template                     |

## Section order (fixed by template)

1. Summary · 2. Cast · 3. Narrative · 4. Machinery · footer (previous/next
   nav only).

## Page structure (top to bottom)

1. Home link (`<p class="home-link">`, small text) — first element in `<body>`.
2. Kicker (series name).
3. H1 (chapter title).
4. Surtitle — `Chapter N of M`, no time range.
5. Top nav — Chapter Index · Glossary, directly below the surtitle.
6. Meta line — Lesson NN · cast map · glossary.
7. §1–§4 numbered sections.
8. Footer — previous/next lesson links only.

Full rationale + rendered example: `references/page-design.md`.

## Surviving (not precluded by the stencil)

- Content truth (verdicts, facts, citations) — verification fan-out + review.
- Banned-phrase smuggle inside narrative HTML — gate scan stays.
- Worker non-delivery — stamp contract (repo path + diff stat + mtime + gate
  exit in every report) + lead disk-verify.

## Publisher parity test (W4)

A contract test must assert the stamp's row-id capture and
`publish_teach.py`'s `get_chapter_row_id` produce identical ids for a fixture
set of filenames (`07-ch13-1996.html` → `ch13`; `01-ch7-…` → `ch7`; a legacy
`nochapter.html` → `lesson-NN`), so the two sides can never drift.
