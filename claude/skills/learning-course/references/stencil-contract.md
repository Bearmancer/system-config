# Lesson stencil — shape contract (W1)

Freezes what the template owns, what content owns, and what the gate keeps as a
backstop. Rule → owner mapping derived from `scripts/check_lesson.py`,
`references/workflow.md` (treatise), and the row-id rule shared with
`publish_teach.py`.

## Row-id contract (shared with the publisher)

- Lesson filename MUST be `NN-chK-<slug>.html` (2-digit lesson number, absolute
  chapter `K`). The stamp HARD-FAILS on a filename without `-chK-`.
- Index row id = `chK`. The publisher derives it with
  `(?i)-ch0*(\d+)` → `ch$1` (fallback `^(\d+)` → `lesson-$1`, then
  `lesson-$fallbackNum` for legacy files only).
- Lesson backlink = `../index.html#chK`, derived from the same capture. One
  regex, one meaning, both sides.

## Owner table

| # | Rule (gate check) | Owner | Mechanism |
|---|---|---|---|
| 1 | No quiz block / no "quiz" word | Template | no quiz markup exists |
| 2 | No teacher references | Template | no teacher blocks exist |
| 3 | No boundary phrases | Template + gate | template has none; gate scans narrative |
| 4 | Surtitle `Chapter N of M · range` present | Template | rendered from `chapter`, `chapters_total`, `time_range` |
| 5 | Timestamps ONLY in surtitle | Template + gate | template emits none elsewhere; gate scans content |
| 6 | No method box / primary-source block / next-on-request | Template | none exist |
| 7 | ≥1 hyperlinked source (`href="https://`) | Template | Sources block always rendered; empty list = stamp hard fail |
| 8 | No bare URL text | Content + stamp + gate | stamp scans & fails; gate backstop |
| 9 | Link target ≤2 occurrences | Stamp + gate | stamp pre-counts (context once + Sources once); gate backstop |
| 10 | No fact-check H2 / box-fact / box-record | Template | none exist; verdicts live inline |
| 11 | No "Open Threads" | Template | none exists |
| 12 | Sources `<h2>` present | Template | section 6 is fixed |
| 13 | ≥2 inline verdict words in narrative | Content + stamp | stamp requires ≥2 in `narrative`; gate backstop |
| 14 | Footer present (`lesson-footer`) | Template | fixed block |
| 15 | Glossary link in footer | Template | fixed anchor |
| 16 | Home button `../../index.html` | Template | fixed anchor, always first |
| 17 | Chapter backlink `../index.html#chK` | Template | derived from filename via row-id contract |
| 18 | Section refs (§N) match headings | Template + stamp | template fixes section numbers 1–6; stamp scans § refs |
| 19 | No dangling links (except publish-generated) | Template + stamp | only `../../index.html` + `../index.html#chK` are allowlisted; every other href must resolve on disk (stamp scans) |
| 20 | Assets resolve | Template | template emits no `src` (optional subgraph slot is inline SVG) |
| 21 | Max-twice budget for index targets | Stamp | `../../index.html` ×1; `../index.html*` ×1 (the backlink) — no plain Course-home links exist in the template |

## Section order (fixed by template)

1. What the chapter does · 2. Cast · 3. What matters — and what you can skip ·
4. The narrative · 5. The machinery · 6. Sources · footer (nav only).

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
