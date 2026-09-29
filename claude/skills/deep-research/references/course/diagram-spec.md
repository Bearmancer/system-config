# Visuals spec — cast block, chapter subgraph, roster-index & timeline (colour-coded, legend-complete, clash-free)

Two cumulative references grow with every course — a roster-index and a timeline — plus per-lesson visuals when humans are involved. Each lesson with an explicit non-empty `cast` list carries a cast block and a chapter-scoped relationship subgraph (Part 0). Chapter scope keeps a large, tangled cast (e.g. Stalin's circle) readable chapter by chapter, in place of one huge cumulative diagram.

## Part 0 — Per-chapter cast block & subgraph (in the lesson, only when `cast` is an explicit non-empty list)

Table plus diagram both scope toward _this chapter alone_. That scope keeps duplication low and complexity bounded.

### Cast block (table, only with explicit non-empty `cast`)

- One row per person acting on stage this chapter — the on-stage cast, apart from the full roster and apart from passing mentions. Target 5–12 rows; a larger on-stage cast stays whole while each listed person acts.
- Columns: **Name | Role this chapter**. Info alone: current role for this chapter; every row reads standalone. No "first appears" column and no introduction-date column.
- **New player** (introduced this chapter): full role line, stable row id (e.g. `id="cast-yezhov"`).
- **Returning player**: role text fresh for this chapter, ending with its "(chapter N)" link to the lesson holding the full entry — chapter numbers are absolute. Internal "(chapter N)" links count toward the max-twice hyperlink rule: each target at most twice per page. Short role-change phrases ("now NKVD chief") ride inside the role cell where roles shifted.
- Model row: `Rich DeVos | on the stand in 1988, admits abuses persist, pledges unenforced (full line: <a>chapter 2</a>)` — fresh role text plus the chapter link each time.

### Chapter-scoped relationship subgraph (SVG, only with explicit cast plus active ties among the on-stage cast)

- A **subgraph**, scoped toward this chapter: nodes on stage this chapter plus edges active in it. Chapter scope keeps the visual small while total cast grows.
- Node cap 12. On-stage casts above 12 split into two subgraphs clustered by concern (e.g. court cluster, street cluster), each with a complete legend for the colours shown.
- Same hard rules as Part 1 (colour-only edges, clash-free geometry, direction-checked arrows) — the three hard rules apply here in full.
- Canvas 700–950 wide, sized toward node count; cumulative-map size stays out of scope here.
- A solo-narration chapter, or any chapter with `cast: []`, omits the whole §2 Cast block (table plus subgraph) with no renumbering; a solo-narration chapter with a cast list but no active ties carries a one-line coverage line in place of the subgraph, naming the chapter scope.
- The chapter figcaption states the colours shown (matching the cast-map legend); it does not re-link the cast map — the merged nav already links it. Citations are inline-only in the lesson narrative (`references/course/page-design.md`); the subgraph carries no source citations, and verdicts stay inline in narrative prose (never a separate box on the visual).

## Part 1 — Roster-index (`reference/cast-map.html`)

Full-course roster/index in table form, updated chapter by chapter. Readers follow a single chapter through its subgraph (Part 0); they come here for the whole picture, spelled out in words. Cumulative mega-SVG retired — one huge cumulative diagram turns unreadable past a mid-size cast; visual explanation lives in chapter subgraphs, cumulative state lives here as a table.

### Three hard rules (hold for every subgraph; roster prose mirrors them in words)

1. **Colour is the ONLY line difference.** Each line runs solid, same weight (~2.2 px), colour-matched arrowhead. Relation differences ride on colour alone; uncertainty and dispute ride on a dedicated colour or on label text. Line style and thickness hold constant across all relations.
2. **One colour = one concern, legend-defined.** Colour meaning comes from the legend on the diagram in hand, stable per workspace across every chapter subgraph. A reader learns the palette once. Each workspace gives each concern a distinct colour.
3. **Clearance holds everywhere.** Boxes hold clearance from each other; edges run clear of boxes; edge and node labels sit clear of both. Geometry gets checked numerically before writing.

### Choosing colours (legend defines meaning)

Pick visually distinct colours per relation type — distinct in hue AND lightness, distinct from node fills (`#fff`, `#f2efe4`, `#eceae2`), capsule frame (`#c8c2b4`), text colours. Legend carries meaning; labels carry detail. Worked example values from the amway map (illustrative hues): `#1a7f37`, `#1f5fa8`, `#6f6a60`, `#7a3fa0`, `#6b4a1f`, `#c07a00`, `#c2185b`, `#0e7c7b`, `#b3261e`.

### Node conventions (for chapter subgraphs; roster rows mirror these fields)

- Person: white fill, solid border. Organisation: cream fill `#f2efe4`.
- Unknown identity: pale grey fill `#eceae2`, "?" in the name, solid border retained.
- Node label: name plus one role line; `(chN)` marks introduction chapter; the page header states position ("as of chapter N").
- Capsule frames (solid, light `#c8c2b4`) group a defensible cluster (e.g. "the tools kingpins"). Frame membership needs chapter-grounded justification; geography sits on the individual boxes holding it.

### Edge direction (arrow runs actor toward target)

- Each arrow points from actor toward target: plaintiff toward defendant, suer toward sued. Setzer chapter: distributors toward Amway.
- Label each edge as "A [verb] B" and land the arrowhead on B. Direction check: read all edges aloud in that form during review; flip or relabel on mismatch before the geometry pass.

### SVG authoring rules (chapter subgraphs)

- Hand-authored inline SVG in the lesson page; canvas 700–950 wide, sized toward node count (`viewBox` matched toward content, `width="100%"`).
- One arrowhead marker per colour, unique ids per SVG (`ah-<colour>` in art; `lg-<colour>` in legend swatches — duplicate ids across SVGs rebind silently, so scope ids per SVG).
- Geometry arithmetic precedes writing: each segment gets computed against every box rectangle. Reroute around, or move boxes. One line-line crossing in differing colours reads acceptably; two plus calls for layout revision.
- Draw edges as `<line>`, `<polyline>`, or `<path>` (M/L/H/V, absolute or relative) for checker visibility; reroute or move, then re-run.
- Boxes hold separation. Containment serves group frames around members alone; all else counts as clash, flagged by the checker.
- Figure wrapper for readable render: `<figure class="map">` — the sizing rule lives once in `assets/lesson.css` (`figure.map`/`figure.map svg`); never hand-inline it per page.
- **Labels**: short labels placed in wedges between lines, clear of boxes and lines. Each edge carries a short label clear of boxes; diagonals rotate along the line (`transform="rotate(angle cx cy)"`). Explicit `font-size` plus `text-anchor` on all labels; the checker reads attributes, plus CSS stays secondary.
- Coordinate plan stays consistent within a cluster so later chapters extend the layout.

### Page structure (roster-index)

1. H1 "Cast roster — as of chapter N"; short cross-link line (cast roster · glossary · chapter index, no lesson list). No kicker on reference pages.
2. Roster — grouped prose list: every node, one to three lines, relations spelled out in words, each entry carrying its introduction chapter `(chN)` (absolute) plus an anchor link toward that chapter's lesson.
3. Context section for parallels and offstage actors, with reason for table-only coverage.
4. Palette table: workspace colour register mapping each colour toward its concern; each chapter subgraph keeps a complete legend for colours shown. Render each row's colour with `<span class="swatch" style="background:#hex"></span>`, row text with `class="legend-row"` — both classes live in `assets/lesson.css`; never a per-row inline SVG marker or a hand-copied `<style>` block for this.

### Updating per chapter

- New players gain roster rows with `(chN)`; fresh relation kinds gain colours plus legend rows in the affected subgraph; established colour meanings hold steady.
- Resolved unknowns gain updated fill description in roster prose plus corrected labels in the live subgraph; corrected links take the dispute colour while dispute stands, proper colour after resolution.
- Each player stays listed; the roster grows cumulatively toward the position. Header advances toward "as of chapter N+1".
- Cross-link anchors get re-verified after each touch; then publish plus probe.

## Part 2 — Timeline (`reference/timeline.html`)

Cumulative chronology, growing exactly like the roster: append plus move, resolved entries retained, header "as of chapter N".

- **Layout**: era/act sections; each entry holds one date plus one-line event plus standing words. Flow layout (sections and lists) gives overlap-free construction; print-friendly output. No colour tags, no legend.
- **Standing rides in text alone.** Each date states verified-against-record or source-claimed ("1971 (video's claim; records show 1970)"). No kind colours anywhere on this page.
- **Corrections move entries**: record contradictions relocate the entry with correction labelled inside the entry; single current version stands per event.
- In-lesson mini-timelines use `<ul class="tl">` with `<li><span class="when">1967</span><div>…</div></li>` — same standing labelling. Shared stylesheet styles `.tl`; per-page restyle stays out.

A course workspace lacking `reference/timeline.html` gains a fresh build seeded from prior chapters, then the current chapter addition. Each chapter adds roster rows plus timeline entries; a quiet chapter still advances the "as of chapter N" header.

## Part 3 — Verification gates (each time a visual changed)

- **Geometry check (every SVG visual — each per-chapter subgraph in a lesson):**
  `python <skill>/scripts/check_map_geometry.py "<file.html>"`
  parses the first SVG on the page, sets `<defs>` aside, and reports: segments crossing a node box; boxes overlapping each other or nested (containment serves group frames alone); edge endpoints closer than `--arrowhead-gap` (default 8 px) where arrowheads would merge; and labels overlapping a box other than their own, measured on estimated glyph boxes — a node's own caption inside its box reads fine, while a caption spilling past its box edge counts as defect. Labels sitting on a line return as warnings; `--strict-labels` makes them fatal. Exit code 0 is the bar. Plus direction read: each edge label parsed as "A [verb] B" with arrowhead on B.
- **Regression fixture for the checker itself:** after editing `check_map_geometry.py`, run it against `evals/fixtures/geom-fixture.html` and expect exactly one box-overlap (a node placed inside a fellow node) plus one label-on-box (a caption crossing a box edge), zero elsewhere. A framed member inside a group frame and a node's own caption stay unflagged. Numbers shifting means the edit broke a check — fix before trusting the checker on live art.
- **Probe before screenshot skip.** Check for a browser explicitly (`Get-Command msedge, chrome`, or the known `msedge.exe` path — Edge ships with Windows). State the probe result with each pass.
- **Screenshot pass (changed visuals), each time.** Mechanical checks miss text overflow, cramped labels, unreadably small render. After checks pass, screenshot the page and look at the image — the Firefox DevTools MCP (enabled by default) drives plus captures the page directly; the headless-browser route below serves as fallback:
  `msedge --headless=new --disable-gpu --hide-scrollbars --screenshot=out.png "--window-size=1500,2400" "file:///<path>"`
  then review that PNG (multimodal look serves) and fix weak reads. Three traps: window height at 2400 or below (Edge falls back toward a 756x488 default above it); always quote the `--window-size` value (unquoted inside a PowerShell loop it splits at the comma and drops); check PNG dimensions after capture — a 756x488 image means the flag dropped, and conclusions from it hold zero weight. Pages taller than one capture get banded screenshots through an iframe with a negative `top` offset.

Changed artifacts pass all gates each time; untouched files rest.
