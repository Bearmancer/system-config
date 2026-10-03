# Page design: style + stamp contract

One visual language for every page: lesson pages, `reference/*.html`, course index, site hub. Content fields: `references/course/lesson-schema.md`. Diagrams: `references/course/diagram-spec.md`.

## Lesson page (top to bottom)

Fixed by `assets/lesson.stencil.html`; the bar comes from `render_bar` in `scripts/lesson_rules.py`.

1. **Bar** (sticky `<header class="A-bar">`): topic name on the left, linking the course index (`../index.html`); chapter dropdown; divider; text settings behind an `Aa` mark (font select, size select). Chapter options injected by `assets/shell.js` from `<workspace>/assets/course-index.js`; no static options.
2. **H1**: chapter name alone. No kicker, no surtitle, no "Chapter N of M", no date or time.
3. **Summary** (`<h2>Summary</h2>` + one paragraph): only when the body has >= 1200 words. Otherwise absent.
4. **Diagram** (`<figure class="map">`, at most 2 per chapter): only when the chapter has relationships to show; see `diagram-spec.md`.
5. **Body**: author-written HTML with unnumbered headings named for what the section explains. No "Machinery" heading.
6. **Footer**: previous/next lesson links only.

## Bar states

| State | Where | Contents |
| --- | --- | --- |
| Chapter | lessons, `reference/*.html` | topic name (link to `../index.html`, the course index), chapter dropdown, `Aa` + font + size |
| Home (`data-state="home"`) | site hub, course index | labelled `Topic` picker, labelled `Chapter` picker, `Aa` + font + size |

- Course index: the Topic picker reads the site topic feed (`data-feed="../assets/course-index.js"`) and navigates on change; the Chapter picker reads the course's own feed.
- Site hub: the Topic picker reads `assets/course-index.js` (topics); choosing a topic fills the Chapter picker from `<topic>/assets/course-index.js` (`data-follows-topic`); choosing a chapter navigates.
- `shell.js` reads each feed through `window.COURSE_INDEX` and restores the page's own list afterwards.
- The picker label is `Topic`.

## Course index (`<workspace>/index.html`)

- One row per lesson: `<li id="chK"><a href="lessons/NN-chK-slug.html">N · Chapter name</a></li>`. `N` = the lesson number `NN` from the filename, consecutive across the course. `chK` (absolute source chapter) is the row id only.
- Two source chapters merged into one lesson: one row, filename carries the first chapter's `K`, `N` stays consecutive.
- After the rows: `<nav class="index-extras">` with Cast, Glossary, Timeline links (`reference/cast-map.html`, `reference/glossary.html`, `reference/timeline.html`); each only when that page exists. Cast page only for a long-running narrative with important recurring people.
- No date line, no status/mission/spine wording, no separate "Cast roster · Glossary" section.

## Prose rules (lessons)

Prose follows SKILL.md Voice; the reader learns the subject, not the method.

- Citations: hyperlink on the words that name the source ("the <a>Frontelligence Insight projection</a>"). No `<sup>`, no numeral or "here" as link text, no bare URL, no reference list, no Sources/References/Bibliography heading. A repeat mention links the same way.
- Verification is not narrated: no "confirmed/checked/cross-checked/corrected/verified against", agentless "is/was/stays/remains (un)verified", "unfindable", "partially correct", no bold verdict labels, no "Corrections:" ledger (block-start label or heading). "UN monitors verified 1,200 deaths" and "the unverified video" are ordinary wording. Checking shows in the citations. An unfindable claim reads as the source's own account, stated as such.
- Corrections fold into the sentence where the fact appears ("a million lives lost, not deployed troops"). No "Corrections:" ledger.
- No commentary on the text's own structure ("the chapter works as a ladder", "the closing line delivers the thesis"). Explain the subject.
- Headings carry no numbers; no `§N` cross-references.
- Cast lists only the important people of a long-running narrative, on `reference/cast-map.html`. No per-chapter table of minor or unnamed actors.
- Chapter count is a writing decision: merge two short source chapters into one lesson when it reads better.

## Typography and colour tokens

`assets/lesson.css` `:root` is the single home of every font-size, font-family and colour; a dark theme redefines the colour tokens under `prefers-color-scheme: dark`.

- `--ink` / `--ink-soft`: text / secondary text. `--paper` / `--panel`: page / bar background. `--rule`: hairlines. `--accent`: links.
- `--d1`..`--d6`, `--d-neutral`: diagram palette; each >= 4.5:1 against `--paper` in both themes (`--d-neutral` >= 7:1). Every pair of tokens, and each token against `--accent`, differs by CIE76 delta-E >= 30 in both themes. `scripts/tests/test_lesson_css.py` enforces both.
- `--size-base` is the one size knob; every other size is a `calc()` ratio. `html[data-size="S|M|L|XL"]` sets it; the bar's size select writes the attribute.
- `--font-body` set at runtime by the font select, persisted in `localStorage`. Roster of 12, lazy-loaded from Google Fonts (Charter = system font).
- Sans for small UI text (bar, footer, legend). No third typeface.

## Casing

- Headings and labels: Title Case. Body prose: sentence case. No `text-transform: uppercase`; small-caps look = size + letter-spacing.
- Gate flags 3+ consecutive ALL-CAPS words (acronyms exempt).

## Row-id contract (shared with the publisher)

- Lesson filename `NN-chK-<slug>.html` (2-digit lesson number, absolute chapter `K`); stamp hard-fails otherwise.
- Index row id = `chK`, derived with `(?i)-ch0*(\d+)` -> `ch$1` (fallback `ch$fallbackNum` for legacy files; the gate requires `ch\d+` ids).
- Parity test: stamp's `row_id_from_filename` and `publish_teach.py` derive identical ids (`07-ch13-1996.html` -> `ch13`).

## Owner table (rule -> gate)

| Rule | Owner |
| --- | --- |
| Exactly one bar; topic name links `../index.html`; chapter dropdown; `Aa` behind a divider; font >= 12, size S/M/L/XL; both scripts | template (`render_bar`) + gate |
| Home bar on index pages: Topic picker (+ Chapter picker) | `render_bar(home=True)` + gate |
| H1 chapter name alone; no kicker, surtitle, "Chapter N of M", date, meta row | template + gate |
| Summary only in a chapter >= 1200 words | stamp + gate |
| Unnumbered headings; no "Machinery"; no `§N` | stamp + gate |
| Links on source-naming words; no `<sup>`, no weak link text, no bare URL, no tag codes, no reference list | stamp + gate |
| No verification narration, verdict labels, correction ledger, meta framing | stamp + gate (`lesson_rules.prose_problems`) |
| No timestamps in a lesson; no YouTube URL | stamp + gate |
| >= 1 hyperlinked source per lesson | stamp + gate |
| No quiz, teacher block, method box, boundary phrase, open threads, fact/record box | gate |
| Footer = previous/next only | template + gate |
| Diagram: geometry gate, palette tokens, per-diagram legend, colours only for repeating types | `layout_diagram.py` + gate |
| Index rows `N · name`; extras nav; no date line; no "Book / Video" | gate |
| Link budgets (`../index.html`, glossary, cast-map at most once per lesson; the bar's topic link is the `../index.html` use); no dangling links; assets resolve | gate |

`stamp_lesson.py` and `check_lesson.py` share `lesson_rules.py`; the stamp refuses at write time, the gate is the backstop on rendered pages.

## Gate modes (`scripts/check_lesson.py` by path)

- `lessons/`: full lesson rules.
- Workspace `index.html`: home bar, rows, extras, no date line, nav-only footer.
- `reference/`: no kicker, short cross-link meta (never a lesson list), no Links section, no how-read box, nav-only footer.
- `reference/timeline.html`: reference rules + text-only entries (no kind tags, no legend).
- Fragments, slices, stencil copies: SKIP.

## Cross-references

- Bar behaviour: `assets/shell.js`, copied once to the site root `assets/` by publish; pages link it by relative path.
- Chapter feed: `<workspace>/assets/course-index.js`, generated by the stamp (`window.COURSE_INDEX`, labels `N · name`); never hand-authored.
- Publish + hub/index generation: `references/course/publishing.md`.
