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
- Lesson backlink (merged top nav, under the H1 above the surtitle) = `../index.html#chK`, derived
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
| 9b | No bare tag codes (`[C4]`/`[O2]` outside a link)        | Stamp + gate           | numerals stand alone; every claim carries a real hyperlink; stamp refuses at write time, gate backstop              |
| 10 | No fact-check H2 / box-fact / box-record               | Template               | none exist; verdicts live inline                                                                                   |
| 11 | No "Open Threads"                                      | Template               | none exists                                                                                                        |
| 12 | No Sources/References/Bibliography heading, anywhere   | Template + gate        | citations are inline-only — no separate section ever; gate scans every heading                                    |
| 13 | ≥2 inline verdict words in narrative                   | Content + stamp        | stamp requires ≥2 in `narrative`; gate backstop                                                                    |
| 14 | Footer present (`lesson-footer`)                       | Template               | fixed block, nav = previous/next lesson only                                                                       |
| 15 | Single merged nav row, Title Case, zero dupes | Template + gate | one `<nav class="top-nav">`: Home + Chapter Index + Glossary + Cast Map; gate refuses a second nav row or any `<p class="meta">` |
| 16 | Each of the four merged-nav links, budget x1 each | Template + gate | Home → `../../index.html`; Chapter Index → `../index.html#chK` (derived from filename via row-id contract); Glossary → `../reference/glossary.html`; Cast Map → `../reference/cast-map.html` (no Lesson NN cell anywhere) — each fixed text, appears at most once on the page |
| 18 | Section refs (§N) match headings; no §2 ref when Cast omitted | Template + stamp + gate | headings are 1 Summary, 2 Cast (only when `cast: []` absent — explicit non-empty list), 3 Narrative, 4 Machinery; stamp refuses §2 refs when Cast omitted; gate matches refs against existing headings |
| 19 | No dangling links (except publish-generated)           | Template + stamp       | `../../index.html`, `../index.html#chK`, `../reference/glossary.html`, `../reference/cast-map.html` are allowlisted; every other href must resolve on disk (stamp scans) |
| 20 | Assets resolve                                         | Template               | template emits no `src` (optional subgraph slot is inline SVG)                                                     |
| 22 | No YouTube URL, anywhere                                | Stamp + gate           | a YouTube URL is never a source; stamp refuses at write time, gate backstop                                        |
| 23 | Headings and nav cells use Title Case                 | Template                | `Summary`, `Cast`, `Narrative`, `Machinery`, `Role This Chapter`, nav `Home`, `Chapter Index`, `Glossary`, `Cast Map` — fixed text in the template |

## Section order (conditional)

1. Summary · 2. Cast (only when `cast` is an explicit non-empty list — humans involved) · 3. Narrative · 4. Machinery · footer (previous/next
   nav only). When `cast: []`, §2 is omitted and headings run 1, 3, 4 with no renumbering.

## Page structure (top to bottom)

1. Kicker (series name).
2. H1 (chapter title).
3. Merged nav — Home · Chapter Index · Glossary · Cast Map in one `<nav class="top-nav">`, Title Case, directly under the H1.
4. Surtitle — `Chapter N of M`, no time range.
5. §1 Summary, [§2 Cast only when humans involved,] §3 Narrative, §4 Machinery.
6. Footer — previous/next lesson links only. No meta paragraph anywhere.

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

## Holistic gate modes (`scripts/check_lesson.py` by path)

- `lessons/` → full lesson rules (merged nav, inline verdicts, superscript repeats, no bare tag codes, budgets).
- Workspace `index.html` → chapter links present, no Status/Spine/Live/Pages/How-works/Mission wording, nav-only footer.
- `reference/` (cast-map, glossary) → no kicker, short cross-link meta (never a lesson/slice list), no Links section, no how-read box, nav-only footer.
- `reference/timeline.html` → reference rules plus text-only entries (no kind tags, no legend, standing words alone).
- Fragments, slices, and stencil copies report SKIP.
