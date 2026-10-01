# Visuals spec: chapter diagram, cast page, timeline

Three visuals: a per-lesson relationship diagram (computed), a course-level cast page, a cumulative timeline. Answer and fact-check pages carry no cast list; cast pages belong to explanation courses.

## Part 0: chapter diagram (in the lesson, only when the chapter has relationships worth drawing)

Authored as a `diagram:` mapping (or a list of up to 2 mappings) in the lesson YAML; `scripts/layout_diagram.py` computes the layout and emits static SVG + legend at stamp time. Never hand-draw SVG. A chapter carries at most 2 diagrams; two diagrams split the cast by concern.

### Spec

```yaml
diagram:
  title: "Chapter 5 relationships"     # aria-label
  rows:                                # top to bottom; each row a list of nodes
    - - {id: kand, name: "Taliban in Kandahar", note: "Decrees and gold money"}
      - {id: kabul, name: "Taliban in Kabul", note: "Officials defying orders"}
    - - {id: nrf, name: "National Resistance Front", note: "Massoud exile network"}
  types:                               # legend text per relationship type
    attack: "Attack"
  edges:
    - {from: nrf, to: kand, label: "NRF raids north", type: attack, directed: true}
    - {from: kabul, to: kand, label: "Kabul defies the cutoff", directed: false}
```

- Node: `id` (unique), `name`, optional `note`. Node cap 12 per diagram; larger casts split into two diagrams by concern.
- Edge: `from`, `to`, `label`, `directed` (required bool), optional `type`. Two edges never join the same pair.

### Colour = relationship type, chosen per diagram

- Colour encodes the type of relationship (attack, alliance, rift, kinship-style), the same colour for every edge of that type whoever the actor.
- A type earns a colour only when 2+ edges in the same diagram share it. A type used once is drawn neutral. Colours come from `--d1`..`--d6` in `lesson.css`, assigned in order of first use over the edge list; there is no global palette. Max 6 repeating types.
- One-off events and untyped edges: solid `--d-neutral` (a strong ink tone in both themes) with their own label. Never a faint grey, never dashed.
- The legend (HTML list below the SVG, `.swatch` + `.legend-row`) explains each colour, the neutral row, and "An arrow runs from the actor to the target."
- All lines solid, one weight (2.5). No `stroke-dasharray`.
- Every colour token holds >= 4.5:1 against the page in light and dark (`test_lesson_css.py`).

### Direction = arrow

- `directed: true` draws an arrowhead at `to`; `from` is the actor, `to` the target (NRF -> Taliban in Kandahar for an attack). Read every edge aloud as "from [label] to": the label continues the sentence from actor to target ("Party" + "loses the runoff to" + "Boris Yeltsin").
- `directed: false` (alliance, split) draws no arrowhead.

### Computed layout (in `layout_diagram.py`)

1. Row 0 keeps the authored order. Every later row sorts by the barycentre (mean x) of the nodes it connects to in the rows above, so lines do not cross. With 3+ rows, an up-sweep and a second down-sweep replace that order only when they cross fewer lines and keep every same-row edge between neighbours. The stamp prints `WARN: diagram N: K line crossings` when K > 0; reroute a node to another row until it prints 0.
2. Edge ends spread evenly along the box side they touch, ordered by the far end's x.
3. Each label slides from the line midpoint (offsets .5, .42, .58, .34, .66, .27, .73, both sides) until its padded box clears every node, every line and every earlier label. Labels sit beside their line, never on it; text is never rotated. A label must sit at least 8 px nearer its own line than any other line; when no slot does, the nearest clear slot is used.
4. Canvas widens (760 up to 1400) until every label fits.
5. Refusals (`diagram: ...` from the stamp): wrongly typed spec (rows, nodes, ids, names, notes, edges, types, labels), unknown node, duplicate id, missing `directed`, type without a `types` entry, > 6 repeating types, a same-row edge between non-neighbours, a line passing through a box, a label with no clear spot. Fix the spec (move a node to another row, shorten the label); never patch the SVG.

### Geometry gate

`check_lesson.py` runs `check_map_geometry.analyze` on every `<svg>` in a lesson and FAILS on: a line through a box, overlapping boxes, a label over a box, label over label, a label on a line, merged arrowheads, anything outside the viewBox. It also fails: `stroke-dasharray`, rotated text, a line colour that is not a palette token, a colour on one line only, a colour with no legend row, a line without its own label, an arrowhead marker not defined in the SVG, marker ids repeated across a page (each figure gets its own `uid`: `d1`, `d2`), a legend row missing from the figure that uses the colour (legends are checked per `<figure class="map">`), more than 2 figures, an edge drawn as anything but a `<line>` (`<path>`, `<polyline>`, `<polygon>`, curves refused), an SVG outside `<figure class="map">`. Glyph width is `0.56 * font-size * characters` in both the layout and the checker (`glyph_width` in `check_map_geometry.py`).

Standalone: `python <skill>/scripts/check_map_geometry.py <file.html>` (`--strict-labels` also fails labels on lines; `check_lesson.py` always does). Regression fixture `evals/fixtures/geom-fixture.html` must report exactly one box-overlap and one label-on-box, zero elsewhere; `test_lesson_gate.py` asserts it.

### Screenshot pass

Mechanical checks miss cramped or unreadable renders. After a diagram changes, screenshot the stamped page and look. Probe first: `Get-Command msedge, chrome`. `msedge --headless=new --disable-gpu --hide-scrollbars --screenshot=out.png "--window-size=1500,2400" "file:///<path>"`. Window height <= 2400; quote `--window-size`; check the PNG size (756x488 = flag dropped).

## Part 1: cast page (`reference/cast-map.html`)

Exists only for a long-running narrative with important recurring people. Lists only those people, not everyone mentioned; no per-chapter table of minor or unnamed actors.

- H1 "Cast", short cross-link line (glossary, timeline); no kicker.
- Entries grouped in prose: name, role, relations in words, the chapter of first appearance linking to that lesson.
- Updated once per lesson; reached from the `Cast` link in the course index.

## Part 2: timeline (`reference/timeline.html`)

Cumulative chronology, HTML flow layout (era sections, lists), no colour tags, no legend.

- Each entry: one date, one-line event, standing in words ("the video's claim; records show 1970").
- A record contradiction relocates the entry with the correction inside it; one current version per event.
- In-lesson mini-timelines: `<ul class="tl"><li><span class="when">1967</span><div>...</div></li></ul>`, styled by `lesson.css`.
- Reached from the `Timeline` link in the course index.
