# Page design — style + stamp contract

One visual language, one owner table, for every page this skill produces: lesson pages, `reference/*.html`, publish-generated hub/index pages. Content-field contract (what goes in the YAML): `references/course/lesson-schema.md`.

## Page structure (top to bottom)

Fixed by `assets/lesson.stencil.html`; identical on every lesson page.

1. **Top bar** — sticky `<header class="A-bar">` above everything: chapter title, a chapter-index `<select>` (every chapter of this course plus Home, Chapter Index, Glossary, Cast Map), a font `<select>`, a size `<select>`. Chapter options are injected at runtime by `assets/shell.js` from `assets/course-index.js`; the four utility options are static markup.
2. **Kicker** — series name, small caps-weight sans, not literal uppercase text.
3. **H1** — chapter title.
4. **Surtitle** — `Chapter N of M`. No time range, no timestamp anywhere on the page.
5. **Numbered sections** — 1 Summary, [2 Cast only when `cast` is an explicit non-empty list,] 3 Narrative, 4 Machinery. Fixed Title Case headings, no renumbering when §2 omitted.
6. **Footer** — previous/next lesson links only. No home, no glossary, no chapter index, no Sources/bibliography block, no workspace line.

Reference and hub/index pages reuse the same typography/color tokens but drop lesson-specific nav elements they don't need — a hub page has no chapter to back-link to, no glossary of its own.

## Typography & color tokens

Canonical values live in `assets/lesson.css`'s `:root` block — the single home for every font-size and font-family; no other file hardcodes one.

- `--ink` / `--ink-soft` — body text / de-emphasized text (surtitle, footer, nav).
- `--paper` / `--panel` — page background / A-bar background.
- `--rule` — hairline borders (headings' top rule, table borders, footer top rule, A-bar bottom border).
- `--accent` — links, kicker, table `.when` column. The one accent color on the page.
- `--mono` — the rare monospace run (timeline `.when`, inline code-like tokens).
- `--size-base` — the one size knob; every other size is a `calc()` ratio of it: `--size-kicker`, `--size-h1`, `--size-h2`, `--size-h3`, `--size-body`, `--size-lead`, `--size-table`, `--size-nav`, `--size-footer`, `--size-code`. `html[data-size="S|M|L|XL"]` sets `--size-base`; the A-bar's size `<select>` writes that attribute.
- `--font-body` — set at runtime by the A-bar's font `<select>` (`assets/shell.js`), persisted to `localStorage`. Roster of 12, lazy-loaded from Google Fonts on selection (Charter is the one system font, no network fetch): Literata, Source Serif 4, Newsreader, Crimson Pro, EB Garamond, Merriweather, Lora, Libre Baskerville, Atkinson Hyperlegible, Inter, IBM Plex Sans, Charter.

Sans-serif for small UI text (kicker, surtitle, A-bar, footer). No third typeface.

## Casing

- Headings and labels (h1, h2, box titles, kicker) — Title Case. Body prose — sentence case.
- No `text-transform: uppercase` anywhere. Small-caps kicker *look* = font-size + letter-spacing + color (`.kicker` in `lesson.css`), never a CSS transform on real text.
- Gate: `check_lesson.py` flags any run of 3+ consecutive ALL-CAPS words typed directly into content (acronyms like "FBI" are exempt).

## Citations

Inline-only, forever — no Sources block, no bibliography, no footer citation list, on any page type.

- First mention of a source in a chapter: a full inline `<a href="https://...">`.
- Every later mention of the *same* URL: a superscript character that is itself the link — `<sup><a href="...">n</a></sup>`. Never a bare superscript marker, never an unlinked repeat.
- No bare tag codes: `[C4]`/`[O2]` point nowhere — numerals stand alone, every claim carries a real hyperlink beside it.
- Gate: `check_lesson.py` flags any heading matching `/sources|references|bibliography/i` and any `<sup>` not wrapped in `<a>`; `stamp_lesson.py` refuses at write time if a repeat isn't wrapped.

## Rendered example (annotated skeleton)

```html
<body>
  <header class="A-bar">                                             <!-- 1. sticky top bar -->
    <div class="row">
      <span class="title">1996</span>
      <select data-index data-current="ch13">                        <!-- chapter list injected by shell.js -->
        <option value="../../index.html">Home</option>
        <option value="../index.html#ch13">Chapter Index</option>
        <option value="../reference/glossary.html">Glossary</option>
        <option value="../reference/cast-map.html">Cast Map</option>
      </select>
      <select data-font-select>...12 fonts...</select>
      <select data-size-select><option>S</option><option>M</option><option>L</option><option>XL</option></select>
    </div>
  </header>

  <p class="kicker">Putin: The Rise to Power</p>                    <!-- 2. series name -->
  <h1>1996</h1>                                                      <!-- 3. chapter title -->
  <p class="surtitle">Chapter 13 of 18</p>                          <!-- 4. no time range -->

  <h2>1. Summary</h2> ... [<h2>2. Cast</h2> only when humans involved] ... <h2>3. Narrative</h2> ... <h2>4. Machinery</h2>

  <footer class="lesson-footer">                                     <!-- previous/next only -->
    <nav><a href="...">Previous: ...</a> <a href="...">Next: ...</a></nav>
  </footer>

  <script src="../assets/course-index.js"></script>
  <script src="../assets/shell.js"></script>
</body>
```

## Row-id contract (shared with the publisher)

- Lesson filename MUST be `NN-chK-<slug>.html` (2-digit lesson number, absolute chapter `K`). The stamp HARD-FAILS on a filename without `-chK-`.
- Index row id = `chK`. The publisher derives it with `(?i)-ch0*(\d+)` → `ch$1` (fallback `^(\d+)` → `lesson-$1`, then `lesson-$fallbackNum` for legacy files only).
- Lesson backlink (merged top nav) = `../index.html#chK`, derived from the same capture. One regex, one meaning, both sides.

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
| 11 | No "Open Threads"                                      | Template               | none exists                                                                                                         |
| 12 | No Sources/References/Bibliography heading, anywhere   | Template + gate        | citations are inline-only — no separate section ever; gate scans every heading                                    |
| 13 | ≥2 inline verdict words in narrative                   | Content + stamp        | stamp requires ≥2 in `narrative`; gate backstop                                                                    |
| 14 | Footer present (`lesson-footer`)                       | Template               | fixed block, nav = previous/next lesson only                                                                       |
| 15 | Single A-bar top bar, non-empty title | Template + gate | one `<header class="A-bar">` with a non-empty `.title`; gate refuses a second bar or any `<p class="meta">` |
| 16 | Index select carries the four utility options, budget x1 each | Template + gate | Home → `../../index.html`; Chapter Index → `../index.html#chK` (derived from filename via row-id contract); Glossary → `../reference/glossary.html`; Cast Map → `../reference/cast-map.html` — each an `<option value=...>` in the `data-index` select, at most once; gate scans the select's option values |
| 17 | Font + size menus present; per-workspace chapter feed | Template + gate | `data-font-select` (≥12 fonts) and `data-size-select` (S/M/L/XL) are static markup; `<script src=...course-index.js>` + `<script src=...shell.js>` load the chapter list and wire behaviour; `stamp_lesson.py` refreshes `assets/course-index.js` and copies `assets/shell.js` on every stamp so adding a lesson updates one file, not every page; gate requires both script tags |
| 18 | Section refs (§N) match headings; no §2 ref when Cast omitted | Template + stamp + gate | headings are 1 Summary, 2 Cast (only when `cast: []` absent — explicit non-empty list), 3 Narrative, 4 Machinery; stamp refuses §2 refs when Cast omitted; gate matches refs against existing headings |
| 19 | No dangling links (except publish-generated)           | Template + stamp       | `../../index.html`, `../index.html#chK`, `../reference/glossary.html`, `../reference/cast-map.html` are allowlisted; every other href must resolve on disk (stamp scans) |
| 20 | Assets resolve                                         | Template               | template emits no `src` (optional subgraph slot is inline SVG)                                                     |
| 22 | No YouTube URL, anywhere                                | Stamp + gate           | a YouTube URL is never a source; stamp refuses at write time, gate backstop                                        |
| 23 | Headings and nav cells use Title Case                 | Template                | `Summary`, `Cast`, `Narrative`, `Machinery`, `Role This Chapter`, nav `Home`, `Chapter Index`, `Glossary`, `Cast Map` — fixed text in the template |

## Section order (conditional)

1. Summary · 2. Cast (only when `cast` is an explicit non-empty list — humans involved) · 3. Narrative · 4. Machinery · footer (previous/next nav only). When `cast: []`, §2 is omitted and headings run 1, 3, 4 with no renumbering.

## Surviving (not precluded by the stencil)

- Content truth (verdicts, facts, citations) — verification fan-out + review.
- Banned-phrase smuggle inside narrative HTML — gate scan stays.
- Worker non-delivery — stamp contract (repo path + diff stat + mtime + gate exit in every report) + lead disk-verify.

## Publisher parity test

A contract test asserts the stamp's row-id capture and `publish_teach.py`'s `get_chapter_row_id` produce identical ids for a fixture set of filenames (`07-ch13-1996.html` → `ch13`; `01-ch7-…` → `ch7`; a legacy `nochapter.html` → `lesson-NN`), so the two sides can never drift.

## Holistic gate modes (`scripts/check_lesson.py` by path)

- `lessons/` → full lesson rules (merged nav, inline verdicts, superscript repeats, no bare tag codes, budgets).
- Workspace `index.html` → chapter links present, no Status/Spine/Live/Pages/How-works/Mission wording, nav-only footer.
- `reference/` (cast-map, glossary) → no kicker, short cross-link meta (never a lesson/slice list), no Links section, no how-read box, nav-only footer.
- `reference/timeline.html` → reference rules plus text-only entries (no kind tags, no legend, standing words alone).
- Fragments, slices, and stencil copies report SKIP.

## Cross-references

- Content field contract (YAML fields, fail-closed rules): `references/course/lesson-schema.md`.
- Canonical stylesheet: `assets/lesson.css` — copy into each workspace verbatim, never restyle per-page.
- Publish/hub page generation: `references/course/publishing.md`.
