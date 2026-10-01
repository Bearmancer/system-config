"""Computed relationship diagram: spec mapping in, static SVG figure out.

Rows are ordered by barycentre so lines do not cross, edge ends are spread
evenly along the box side they touch, and each line label slides along its own
line, beside it, until it clears every box, line and earlier label. Anything
that cannot be placed raises DiagramError; nothing is drawn on top of anything.
Geometry helpers come from check_map_geometry.py, so the layout and the gate
measure text identically.
"""

import html
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_map_geometry import glyph_width, overlap_length, rect_overlap

NODE_H = 44
NAME_SIZE, NOTE_SIZE, LABEL_SIZE = 12, 10, 11
ROW_GAP = 240
MARGIN = 60
BOX_PAD = 4
OWNER_MARGIN = 8
LABEL_PAD = 3
SLIDES = (0.5, 0.42, 0.58, 0.34, 0.66, 0.27, 0.73)
MAX_WIDTH = 1400
MAX_NODES = 12
PALETTE = tuple(f"var(--d{i})" for i in range(1, 7))
NEUTRAL = "var(--d-neutral)"


class DiagramError(ValueError):
    pass


class Diagram:
    def __init__(self, svg, legend, crossings):
        self.svg = svg
        self.legend = legend
        self.crossings = crossings
        self.figure = f'<figure class="map">\n{svg}\n{legend}\n</figure>'


def _node_width(rows):
    widest = 0
    for row in rows:
        for n in row:
            widest = max(
                widest,
                glyph_width(n["name"], NAME_SIZE),
                glyph_width(n.get("note", ""), NOTE_SIZE),
            )
    return max(160, math.ceil(widest + 24))


def _validate(spec):
    if not isinstance(spec, dict):
        raise DiagramError("diagram: must be a mapping with rows, types and edges")
    rows = spec.get("rows")
    if (
        not isinstance(rows, list)
        or not rows
        or not all(isinstance(r, list) and r and all(isinstance(n, dict) for n in r) for r in rows)
    ):
        raise DiagramError("diagram: rows must be a non-empty list of non-empty node lists")
    ids = [n.get("id") for r in rows for n in r]
    if not all(isinstance(i, str) and i for i in ids) or len(set(ids)) != len(ids):
        raise DiagramError("diagram: every node needs a unique id (text)")
    if len(ids) > MAX_NODES:
        raise DiagramError(f"diagram: {len(ids)} nodes, the cap is {MAX_NODES}; split by concern")
    for r in rows:
        for n in r:
            if not isinstance(n.get("name"), str) or not n["name"]:
                raise DiagramError(f"diagram: node {n['id']} needs a name (text)")
            if n.get("note") is not None and not isinstance(n["note"], str):
                raise DiagramError(f"diagram: node {n['id']} note must be text")
    edges = spec.get("edges") or []
    types = spec.get("types") or {}
    if not isinstance(edges, list) or not all(isinstance(e, dict) for e in edges):
        raise DiagramError("diagram: edges must be a list of mappings")
    if not isinstance(types, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in types.items()):
        raise DiagramError("diagram: types must map a type name to its legend text")
    seen = set()
    for e in edges:
        for key in ("from", "to", "label"):
            if not e.get(key):
                raise DiagramError(f"diagram: every edge needs {key}")
        if not isinstance(e["label"], str):
            raise DiagramError(f"diagram: edge {e['from']} -> {e['to']} label must be text")
        if e["from"] not in ids or e["to"] not in ids:
            raise DiagramError(f"diagram: edge {e['from']} -> {e['to']} names an unknown node")
        if e["from"] == e["to"]:
            raise DiagramError(f"diagram: edge {e['from']} loops to itself")
        if not isinstance(e.get("directed"), bool):
            raise DiagramError(
                f"diagram: edge {e['from']} -> {e['to']} needs directed: true (actor -> target) or false"
            )
        if e.get("type") and e["type"] not in types:
            raise DiagramError(f"diagram: edge type '{e['type']}' has no entry in types")
        pair = frozenset((e["from"], e["to"]))
        if pair in seen:
            raise DiagramError(f"diagram: two edges join {e['from']} and {e['to']}")
        seen.add(pair)
    return rows, edges, types


def _colours(edges, types):
    """Palette tokens go to types used by 2+ edges, in order of first use."""
    counts = {}
    for e in edges:
        if e.get("type"):
            counts[e["type"]] = counts.get(e["type"], 0) + 1
    repeating = [t for t in dict.fromkeys(e["type"] for e in edges if e.get("type")) if counts[t] >= 2]
    if len(repeating) > len(PALETTE):
        raise DiagramError(f"diagram: {len(repeating)} repeating types, the palette holds {len(PALETTE)}")
    return {t: PALETTE[i] for i, t in enumerate(repeating)}


def _place(row, width, node_w, x_of):
    gap = (width - len(row) * node_w) / (len(row) + 1)
    for i, n in enumerate(row):
        x_of[n["id"]] = gap + node_w / 2 + i * (node_w + gap)


def _bary_sort(row, edges, anchor, x_of, width):
    def bary(item):
        idx, n = item
        xs = [
            x_of[o]
            for e in edges
            for me, o in ((e["from"], e["to"]), (e["to"], e["from"]))
            if me == n["id"] and o in anchor
        ]
        return (sum(xs) / len(xs) if xs else width * (idx + 0.5) / len(row), idx)

    return [n for _, n in sorted(enumerate(row), key=bary)]


def _sweep(ordered, edges, width, node_w, up):
    """One barycentre pass. Down: each row below row 0 sorts by every row above
    it. Up: each row above the last, below row 0, sorts by every row below it."""
    ordered = [list(r) for r in ordered]
    x_of = {}
    for row in ordered:
        _place(row, width, node_w, x_of)
    last = len(ordered)
    for r in range(last - 2, 0, -1) if up else range(1, last):
        rest = ordered[r + 1 :] if up else ordered[:r]
        anchor = {n["id"] for row in rest for n in row}
        ordered[r] = _bary_sort(ordered[r], edges, anchor, x_of, width)
        _place(ordered[r], width, node_w, x_of)
    return ordered, x_of


def _crossings(ordered, edges, x_of):
    at = {n["id"]: (x_of[n["id"]], r) for r, row in enumerate(ordered) for n in row}
    lines = [(at[e["from"]], at[e["to"]]) for e in edges if at[e["from"]][1] != at[e["to"]][1]]
    return sum(1 for i in range(len(lines)) for j in range(i + 1, len(lines)) if _cross(lines[i], lines[j]))


def _neighbours_kept(ordered, edges):
    col = {n["id"]: (r, c) for r, row in enumerate(ordered) for c, n in enumerate(row)}
    return all(
        abs(col[e["from"]][1] - col[e["to"]][1]) == 1
        for e in edges
        if col[e["from"]][0] == col[e["to"]][0]
    )


def _order(rows, edges, width, node_w):
    """Row 0 keeps its order; each later row sorts by the mean x of its
    neighbours in the rows above (barycentre). An up-sweep and a second
    down-sweep replace that order only when they cross fewer lines and keep
    every same-row edge between neighbours."""
    best, x_of = _sweep(rows, edges, width, node_w, up=False)
    if len(rows) > 2:
        cand, cand_x = _sweep(best, edges, width, node_w, up=True)
        cand, cand_x = _sweep(cand, edges, width, node_w, up=False)
        if _crossings(cand, edges, cand_x) < _crossings(best, edges, x_of) and _neighbours_kept(cand, edges):
            best, x_of = cand, cand_x
    return best, x_of


def _distance(point, line):
    (x1, y1), (x2, y2) = line
    dx, dy = x2 - x1, y2 - y1
    t = max(0.0, min(1.0, ((point[0] - x1) * dx + (point[1] - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(point[0] - (x1 + t * dx), point[1] - (y1 + t * dy))


def _cross(a, b):
    def orient(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    (p1, p2), (p3, p4) = a, b
    d1, d2 = orient(p3, p4, p1), orient(p3, p4, p2)
    d3, d4 = orient(p1, p2, p3), orient(p1, p2, p4)
    return d1 * d2 < 0 and d3 * d4 < 0


def _layout_at(spec, rows, edges, types, width, node_w, uid):
    ordered, x_of = _order(rows, edges, width, node_w)
    row_of, col_of, y_of = {}, {}, {}
    for r, row in enumerate(ordered):
        for c, n in enumerate(row):
            row_of[n["id"]], col_of[n["id"]] = r, c
            y_of[n["id"]] = MARGIN + NODE_H / 2 + r * ROW_GAP
    height = MARGIN * 2 + NODE_H + (len(ordered) - 1) * ROW_GAP
    boxes = {
        i: (x_of[i] - node_w / 2, y_of[i] - NODE_H / 2, node_w, NODE_H) for i in x_of
    }

    ends = {}
    segs = []
    for e in edges:
        a, b = e["from"], e["to"]
        if row_of[a] == row_of[b]:
            if abs(col_of[a] - col_of[b]) != 1:
                raise DiagramError(
                    f"diagram: {a} and {b} share a row but are not neighbours; put one on another row"
                )
            left = x_of[a] < x_of[b]
            seg = {
                "e": e,
                "p1": (x_of[a] + (node_w / 2 if left else -node_w / 2), y_of[a]),
                "p2": (x_of[b] + (-node_w / 2 if left else node_w / 2), y_of[b]),
            }
        else:
            seg = {"e": e}
            upper_is_a = row_of[a] < row_of[b]
            ends.setdefault((a, "b" if upper_is_a else "t"), []).append((x_of[b], seg, "p1"))
            ends.setdefault((b, "t" if upper_is_a else "b"), []).append((x_of[a], seg, "p2"))
        segs.append(seg)
    for (node, side), items in ends.items():
        items.sort(key=lambda it: it[0])
        for i, (_, seg, key) in enumerate(items):
            x = x_of[node] - node_w / 2 + node_w * (i + 1) / (len(items) + 1)
            y = y_of[node] + (NODE_H / 2 if side == "b" else -NODE_H / 2)
            seg[key] = (x, y)

    for s in segs:
        for nid, box in boxes.items():
            if nid in (s["e"]["from"], s["e"]["to"]):
                continue
            if overlap_length(s["p1"], s["p2"], box) > 0:
                raise DiagramError(
                    f"diagram: line {s['e']['from']} -> {s['e']['to']} passes through {nid}; "
                    "route it through adjacent rows"
                )
    lines = [(s["p1"], s["p2"]) for s in segs]
    crossings = sum(
        1 for i in range(len(lines)) for j in range(i + 1, len(lines)) if _cross(lines[i], lines[j])
    )

    placed = [
        (b[0] - BOX_PAD, b[1] - BOX_PAD, b[2] + 2 * BOX_PAD, b[3] + 2 * BOX_PAD)
        for b in boxes.values()
    ]
    for s in segs:
        (x1, y1), (x2, y2) = s["p1"], s["p2"]
        e = s["e"]
        w = glyph_width(e["label"], LABEL_SIZE)
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        nx, ny = -dy / length, dx / length
        off = abs(nx) * (w / 2) + abs(ny) * (LABEL_SIZE / 2) + LABEL_PAD + 4
        chosen = None
        own = (s["p1"], s["p2"])
        rivals = [ln for ln in lines if ln != own]
        # First pass keeps a label clearly nearer its own line than any other,
        # so a reader never has to guess which event a label names.
        for clear_owner in (True, False):
            for t in SLIDES:
                for side in (1, -1):
                    cx, cy = x1 + dx * t + nx * off * side, y1 + dy * t + ny * off * side
                    rect = (
                        cx - w / 2 - LABEL_PAD,
                        cy - LABEL_SIZE / 2 - LABEL_PAD,
                        w + 2 * LABEL_PAD,
                        LABEL_SIZE + 2 * LABEL_PAD,
                    )
                    if (
                        rect[0] >= 0
                        and rect[1] >= 0
                        and rect[0] + rect[2] <= width
                        and rect[1] + rect[3] <= height
                        and not any(min(rect_overlap(rect, p)) > 0 for p in placed)
                        and not any(overlap_length(*ln, rect) > 0 for ln in lines)
                        and (
                            not clear_owner
                            or all(
                                _distance((cx, cy), own) + OWNER_MARGIN <= _distance((cx, cy), ln)
                                for ln in rivals
                            )
                        )
                    ):
                        chosen = (cx, cy, rect)
                        break
                if chosen:
                    break
            if chosen:
                break
        if not chosen:
            raise DiagramError(f"diagram: no clear spot for label '{e['label']}'")
        cx, cy, rect = chosen
        placed.append(rect)
        s["label_xy"] = (cx, cy + 0.25 * LABEL_SIZE)

    colour_of = _colours(edges, types)
    used = []
    body = []
    for s in segs:
        e = s["e"]
        colour = colour_of.get(e.get("type"), NEUTRAL)
        marker = ""
        if e["directed"]:
            if colour not in used:
                used.append(colour)
            token = colour[len("var(--") : -1]
            marker = f' marker-end="url(#ah-{uid}-{token})"'
        typ = f' data-type="{html.escape(e["type"])}"' if colour != NEUTRAL else ""
        (x1, y1), (x2, y2) = s["p1"], s["p2"]
        body.append(
            f'<line class="edge"{typ} x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{colour}" stroke-width="2.5"{marker}/>'
        )
    for row in ordered:
        for n in row:
            x, y, w, h = boxes[n["id"]]
            cx, cy = x + w / 2, y + h / 2
            body.append(
                f'<rect class="node" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="4" '
                'fill="var(--panel)" stroke="var(--ink-soft)" stroke-width="1.2"/>'
            )
            body.append(
                f'<text x="{cx:.1f}" y="{cy - 3:.1f}" font-size="{NAME_SIZE}" font-weight="600" '
                f'text-anchor="middle" fill="var(--ink)">{html.escape(n["name"])}</text>'
            )
            if n.get("note"):
                body.append(
                    f'<text x="{cx:.1f}" y="{cy + 13:.1f}" font-size="{NOTE_SIZE}" '
                    f'text-anchor="middle" fill="var(--ink-soft)">{html.escape(n["note"])}</text>'
                )
    for s in segs:
        e = s["e"]
        colour = colour_of.get(e.get("type"), NEUTRAL)
        lx, ly = s["label_xy"]
        body.append(
            f'<text class="elabel" x="{lx:.1f}" y="{ly:.1f}" font-size="{LABEL_SIZE}" '
            f'text-anchor="middle" fill="{colour}">{html.escape(e["label"])}</text>'
        )
    defs = "".join(
        f'<marker id="ah-{uid}-{c[len("var(--"):-1]}" viewBox="0 0 10 10" refX="9" refY="5" '
        f'markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
        for c in used
    )
    title = html.escape(spec.get("title") or "Relationship diagram")
    svg = (
        f'<svg viewBox="0 0 {width:g} {height:g}" role="img" aria-label="{title}">'
        + (f"<defs>{defs}</defs>" if defs else "")
        + "".join(body)
        + "</svg>"
    )

    legend = []
    for t, colour in colour_of.items():
        legend.append(
            f'<li class="legend-row"><span class="swatch" style="background:{colour}"></span>{html.escape(types[t])}</li>'
        )
    if any(colour_of.get(e.get("type"), NEUTRAL) == NEUTRAL for e in edges):
        legend.append(
            f'<li class="legend-row"><span class="swatch" style="background:{NEUTRAL}"></span>'
            "Single event, named on its line</li>"
        )
    if any(e["directed"] for e in edges):
        legend.append('<li class="legend-row">An arrow runs from the actor to the target.</li>')
    return Diagram(svg, '<ul class="legend">\n' + "\n".join(legend) + "\n</ul>", crossings)


def layout(spec, uid="d"):
    rows, edges, types = _validate(spec)
    _colours(edges, types)
    node_w = _node_width(rows)
    width = max(760, max(len(r) for r in rows) * (node_w + 50) + 50)
    cap = max(MAX_WIDTH, width)
    last = None
    while width <= cap:
        try:
            return _layout_at(spec, rows, edges, types, width, node_w, uid)
        except DiagramError as err:
            if "no clear spot" not in str(err):
                raise
            last = err
            width += 80
    raise last
