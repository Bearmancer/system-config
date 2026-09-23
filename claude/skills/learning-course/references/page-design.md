# Page design — the single style doc

One visual language for every page this skill produces: lesson pages, `reference/*.html`, and the publish-generated hub/index pages. `stencil-contract.md` freezes the mechanical owner table (rule → template/gate); this doc is the rationale + rendered example behind it, and the place typography/color/casing decisions live once instead of scattered across `lesson.css`, the stencil, and `SKILL.md`.

## Page structure (top to bottom)

Fixed by `assets/lesson.stencil.html`; identical on every lesson page.

1. **Kicker** — series name, small caps-weight sans, not literal uppercase text.
2. **H1** — chapter title.
3. **Merged nav** — Home · Chapter Index · Glossary · Cast Map in one `<nav class="top-nav">`, Title Case, directly under the H1. Zero dupe links, no meta paragraph anywhere.
4. **Surtitle** — `Chapter N of M`. No time range, no timestamp anywhere on the page — not the surtitle, not narrative/machinery/lead.
5. **Numbered sections** — 1 Summary, [2 Cast only when `cast` is an explicit non-empty list,] 3 Narrative, 4 Machinery. Fixed Title Case headings, no renumbering when §2 omitted.
6. **Footer** — previous/next lesson links only. No home, no glossary, no chapter index, no Sources/bibliography block, no workspace line.

Reference and hub/index pages reuse the same typography and color tokens (below) but drop the lesson-specific nav elements they don't need — a hub page has no chapter to back-link to, no glossary of its own.

## Typography & color tokens

Canonical values live in `assets/lesson.css`'s `:root` block — this section names what they're *for*, not the values themselves, so the two never disagree:

- `--ink` / `--ink-soft` — body text / de-emphasized text (surtitle, footer, nav).
- `--paper` — page background.
- `--rule` — hairline borders (headings' top rule, table borders, footer top rule).
- `--accent` — links, kicker, table `.when` column. The one accent color on the page.
- `--mono` — the rare monospace run (timeline `.when`, inline code-like tokens).

Serif body text (`"Sitka Text", Constantia, Charter, Georgia`), sans-serif for small UI text (kicker, surtitle, top-nav, footer) — that split is the whole typographic system. No third typeface.

## Casing

- Headings and labels (h1, h2, box titles, kicker) — Title Case.
- Body prose — sentence case.
- No `text-transform: uppercase` anywhere, on any page. If a heading needs the *look* of a small-caps kicker, that's font-size + letter-spacing + color (see `.kicker` in `lesson.css`), never a CSS transform on real text.
- Gate: `check_lesson.py` flags any run of 3+ consecutive ALL-CAPS words typed directly into content (acronyms like "FBI" are exempt).

## Citations

Inline-only, forever — no Sources block, no bibliography, no footer citation list, on any page type.

- First mention of a source in a chapter: a full inline `<a href="https://...">`.
- Every later mention of the *same* URL: a superscript character that is itself the link — `<sup><a href="...">n</a></sup>`. Never a bare superscript marker, never an unlinked repeat.
- Gate: `check_lesson.py` flags any heading matching `/sources|references|bibliography/i` and any `<sup>` not wrapped in `<a>`; `stamp_lesson.py` refuses at write time if a repeat isn't wrapped.
- No bare tag codes: claim/observation shorthands like `[C4]` or `[O2]` point nowhere — numerals stand alone in prose and every claim carries a real hyperlink beside it.

## Rendered example (annotated skeleton)

```html
<body>
  <p class="kicker">Putin: The Rise to Power</p>                    <!-- 1. series name -->
  <h1>1996</h1>                                                      <!-- 2. chapter title -->
  <nav class="top-nav">                                              <!-- 3. merged nav under H1, Title Case, zero dupes -->
    <a href="../../index.html">Home</a>
    <a href="../index.html#ch13">Chapter Index</a>
    <a href="../reference/glossary.html">Glossary</a>
    <a href="../reference/cast-map.html">Cast Map</a>
  </nav>
  <p class="surtitle">Chapter 13 of 18</p>                          <!-- 4. no time range -->

  <h2>1. Summary</h2> ... [<h2>2. Cast</h2> only when humans involved] ... <h2>3. Narrative</h2> ... <h2>4. Machinery</h2>

  <footer class="lesson-footer">                                     <!-- 7. previous/next only -->
    <nav><a href="...">Previous: ...</a> <a href="...">Next: ...</a></nav>
  </footer>
</body>
```

## Cross-references

- Mechanical rule → owner mapping: `references/stencil-contract.md`.
- Content field contract (what goes in the YAML, fail-closed rules): `references/lesson-schema.md`.
- Canonical stylesheet: `assets/lesson.css` — copy into each workspace verbatim, never restyle per-page.
- Publish/hub page generation: `references/publishing.md`.
