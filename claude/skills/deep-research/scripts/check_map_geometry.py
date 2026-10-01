import argparse
import re
import sys

ATTR = re.compile(r'([a-zA-Z][a-zA-Z0-9-]*)="([^"]*)"')


def attrs(tag):
    return {k: v for k, v in ATTR.findall(tag)}


GLYPH_EM = 0.56


def glyph_width(text, size):
    return GLYPH_EM * size * len(text)


def text_rect(x, y, size, anchor, text):
    width = glyph_width(text, size)
    x0 = x - width / 2 if anchor == "middle" else x - width if anchor == "end" else x
    return (x0, y - 0.75 * size, width, size)


def safe(text):
    return text.encode("ascii", "backslashreplace").decode("ascii")


def load_all_rects(html):
    rects = []
    for tag in re.findall(r"<rect\b[^>]*>", html):
        a = attrs(tag)
        try:
            r = (float(a["x"]), float(a["y"]), float(a["width"]), float(a["height"]))
        except (KeyError, ValueError):
            continue
        rects.append((r, a.get("fill", "").strip() == "none"))
    return rects


def load_segments(html):
    segs = []
    for tag in re.findall(r"<line\b[^>]*>", html):
        a = attrs(tag)
        try:
            segs.append(
                ((float(a["x1"]), float(a["y1"])), (float(a["x2"]), float(a["y2"])))
            )
        except (KeyError, ValueError):
            continue
    for tag in re.findall(r"<polyline\b[^>]*>", html):
        a = attrs(tag)
        pts = a.get("points", "").replace(",", " ").split()
        nums = [float(p) for p in pts if p]
        pairs = list(zip(nums[0::2], nums[1::2]))
        for i in range(len(pairs) - 1):
            segs.append((pairs[i], pairs[i + 1]))
    for tag in re.findall(r"<path\b[^>]*>", html):
        a = attrs(tag)
        tokens = re.findall(r"[MLHVmlhv]|-?\d*\.?\d+", a.get("d", ""))
        pts = []
        cx = cy = 0.0
        cmd = None
        i = 0
        while i < len(tokens):
            tok = tokens[i]
            if tok in ("M", "L", "H", "V", "m", "l", "h", "v"):
                cmd = tok
                i += 1
                continue
            if cmd is None:
                i += 1
                continue
            if cmd in ("H", "h"):
                x = float(tok)
                cx = x if cmd == "H" else cx + x
                pts.append((cx, cy))
                i += 1
            elif cmd in ("V", "v"):
                y = float(tok)
                cy = y if cmd == "V" else cy + y
                pts.append((cx, cy))
                i += 1
            else:
                x = float(tok)
                y = float(tokens[i + 1]) if i + 1 < len(tokens) else 0.0
                if cmd in ("m", "l"):
                    cx, cy = cx + x, cy + y
                else:
                    cx, cy = x, y
                pts.append((cx, cy))
                i += 2
        for j in range(len(pts) - 1):
            segs.append((pts[j], pts[j + 1]))
    return segs


def load_terminals(html):
    pts = []
    for tag in re.findall(r"<line\b[^>]*>", html):
        a = attrs(tag)
        try:
            pts.append((float(a["x2"]), float(a["y2"])))
        except (KeyError, ValueError):
            continue
    for tag in re.findall(r"<polyline\b[^>]*>", html):
        a = attrs(tag)
        nums = [float(p) for p in a.get("points", "").replace(",", " ").split() if p]
        pairs = list(zip(nums[0::2], nums[1::2]))
        if pairs:
            pts.append(pairs[-1])
    return pts


def load_labels(html):
    labels = []
    for tag in re.findall(r"<text\b([^>]*)>(.*?)</text>", html, re.S):
        raw_attrs, body = tag
        a = attrs("<text " + raw_attrs + ">")
        if "transform" in a:
            continue
        try:
            x = float(a["x"])
            y = float(a["y"])
        except (KeyError, ValueError):
            continue
        size = float(a.get("font-size", "11"))
        text = re.sub(r"<[^>]*>", "", body).strip()
        if not text:
            continue
        labels.append((text_rect(x, y, size, a.get("text-anchor", "start"), text), text))
    return labels


def overlap_length(p1, p2, rect):
    x1, y1 = p1
    x2, y2 = p2
    rx, ry, rw, rh = rect
    xmin, xmax = rx, rx + rw
    ymin, ymax = ry, ry + rh
    dx, dy = x2 - x1, y2 - y1
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x1 - xmin), (dx, xmax - x1), (-dy, y1 - ymin), (dy, ymax - y1)):
        if p == 0:
            if q < 0:
                return 0.0
        else:
            r = q / p
            if p < 0:
                if r > t1:
                    return 0.0
                if r > t0:
                    t0 = r
            else:
                if r < t0:
                    return 0.0
                if r < t1:
                    t1 = r
    if t0 > t1:
        return 0.0
    length = ((dx) ** 2 + (dy) ** 2) ** 0.5
    return (t1 - t0) * length


def rect_overlap(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ox = min(ax + aw, bx + bw) - max(ax, bx)
    oy = min(ay + ah, by + bh) - max(ay, by)
    return ox, oy


def contains(outer, inner):
    ox, oy, ow, oh = outer
    ix, iy, iw, ih = inner
    return ox <= ix and oy <= iy and ox + ow >= ix + iw and oy + oh >= iy + ih


def view_box(svg):
    m = re.search(r'<svg\b[^>]*\bviewBox="([^"]+)"', svg)
    if not m:
        return None
    nums = [float(n) for n in m.group(1).replace(",", " ").split()]
    return tuple(nums) if len(nums) == 4 else None


def analyze(svg, min_overlap=2.0, arrowhead_gap=8.0):
    """Every geometry defect of one <svg> string, as lists of hit tuples."""
    vb = view_box(svg)
    svg = re.sub(r"<defs\b.*?</defs>", "", svg, flags=re.S)
    rects_all = load_all_rects(svg)
    boxes = [r for r, is_frame in rects_all if not is_frame]
    segs = load_segments(svg)
    labels = load_labels(svg)
    terminals = load_terminals(svg)
    hits = {
        "edge_box": [],
        "box_box": [],
        "label_line": [],
        "label_box": [],
        "label_label": [],
        "arrow": [],
        "bounds": [],
    }
    for si, (p1, p2) in enumerate(segs):
        for bi, r in enumerate(boxes):
            ov = overlap_length(p1, p2, r)
            if ov > min_overlap:
                hits["edge_box"].append((si, bi, ov, r, p1, p2))
    for i in range(len(rects_all)):
        for j in range(i + 1, len(rects_all)):
            ri, i_is_frame = rects_all[i]
            rj, j_is_frame = rects_all[j]
            ox, oy = rect_overlap(ri, rj)
            if ox > min_overlap and oy > min_overlap:
                if (contains(rj, ri) and j_is_frame) or (
                    contains(ri, rj) and i_is_frame
                ):
                    continue
                hits["box_box"].append((i, j, ox, oy, ri, rj))
    for rect, text in labels:
        for si, (p1, p2) in enumerate(segs):
            if overlap_length(p1, p2, rect) > min_overlap:
                hits["label_line"].append((text, si, p1, p2))
        for bi, r in enumerate(boxes):
            ox, oy = rect_overlap(rect, r)
            if ox > min_overlap and oy > min_overlap and not contains(r, rect):
                hits["label_box"].append((text, bi, r, ox, oy))
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            ox, oy = rect_overlap(labels[i][0], labels[j][0])
            if ox > min_overlap and oy > min_overlap:
                hits["label_label"].append((labels[i][1], labels[j][1], ox, oy))
    for i in range(len(terminals)):
        for j in range(i + 1, len(terminals)):
            (ax, ay), (bx, by) = terminals[i], terminals[j]
            gap = ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5
            if gap < arrowhead_gap:
                hits["arrow"].append((i, j, gap, terminals[i], terminals[j]))
    if vb:
        vx, vy, vw, vh = vb

        def outside(x, y):
            return x < vx or y < vy or x > vx + vw or y > vy + vh

        for r in boxes + [rect for rect, _ in labels]:
            if outside(r[0], r[1]) or outside(r[0] + r[2], r[1] + r[3]):
                hits["bounds"].append(r)
        for p1, p2 in segs:
            if outside(*p1) or outside(*p2):
                hits["bounds"].append((p1, p2))
    hits["counts"] = (len(boxes), len(segs), len(labels))
    return hits


FATAL_KEYS = ("edge_box", "box_box", "label_box", "label_label", "arrow", "bounds")


def main():
    ap = argparse.ArgumentParser(
        description="Check a cast-map SVG: edges through boxes, overlapping boxes (including a node inside another node), merged arrowheads, labels on lines, boxes or other labels, anything outside the viewBox."
    )
    ap.add_argument("files", nargs="+", help="HTML file(s) containing the inline SVG")
    ap.add_argument(
        "--min-overlap", type=float, default=2.0, help="px before an overlap counts"
    )
    ap.add_argument(
        "--strict-labels",
        action="store_true",
        help="count labels sitting on lines as failures too",
    )
    ap.add_argument(
        "--arrowhead-gap",
        type=float,
        default=8.0,
        help="px between two edge endpoints before their arrowheads count as merged",
    )
    args = ap.parse_args()

    failed = 0
    for path in args.files:
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                html = fh.read()
        except OSError as exc:
            print(f"ERROR {path}: {exc}")
            failed += 1
            continue
        svg_matches = re.findall(r"<svg\b.*?</svg>", html, re.S)
        if not svg_matches:
            print(f"ERROR {path}: no <svg> block found")
            failed += 1
            continue

        file_fatal = 0
        for svg_idx, svg in enumerate(svg_matches, start=1):
            label = f"{path} SVG #{svg_idx}" if len(svg_matches) > 1 else path
            h = analyze(svg, args.min_overlap, args.arrowhead_gap)
            nboxes, nsegs, nlabels = h["counts"]
            fatal = sum(len(h[k]) for k in FATAL_KEYS) + (
                len(h["label_line"]) if args.strict_labels else 0
            )
            print(
                f"{'OK' if fatal == 0 else 'PROBLEMS'} {label}: {nboxes} boxes, {nsegs} segments, "
                f"{nlabels} labels | edges-through-boxes={len(h['edge_box'])} box-overlaps={len(h['box_box'])} "
                f"merged-arrowheads={len(h['arrow'])} labels-on-boxes={len(h['label_box'])} "
                f"labels-on-labels={len(h['label_label'])} out-of-bounds={len(h['bounds'])} "
                f"labels-on-lines={len(h['label_line'])}{' (fatal)' if args.strict_labels else ' (warnings)'}"
            )
            for si, bi, ov, r, p1, p2 in h["edge_box"]:
                print(
                    f"   edge {si} {p1}->{p2} passes through box {bi} at x={r[0]} y={r[1]} w={r[2]} h={r[3]} by {ov:.1f}px"
                )
            for i, j, ox, oy, a, b in h["box_box"]:
                print(f"   boxes {i} {a} and {j} {b} overlap by {ox:.1f}x{oy:.1f}px")
            for i, j, gap, p, q in h["arrow"]:
                print(f"   arrowheads merge: endpoints {p} and {q} are {gap:.1f}px apart")
            for text, bi, r, ox, oy in h["label_box"]:
                print(
                    f'   label "{safe(text[:40])}" covers box {bi} at x={r[0]} y={r[1]} by {ox:.1f}x{oy:.1f}px'
                )
            for a, b, ox, oy in h["label_label"]:
                print(
                    f'   label "{safe(a[:40])}" overlaps label "{safe(b[:40])}" by {ox:.1f}x{oy:.1f}px'
                )
            for r in h["bounds"]:
                print(f"   outside the viewBox: {r}")
            for text, si, p1, p2 in h["label_line"]:
                print(f'   label "{safe(text[:40])}" sits on edge {si} {p1}->{p2}')
            file_fatal += fatal

        if file_fatal:
            failed += 1
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
