import argparse
import re
import sys

ATTR = re.compile(r'([a-zA-Z][a-zA-Z0-9-]*)="([^"]*)"')


def attrs(tag):
    return {k: v for k, v in ATTR.findall(tag)}


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
        anchor = a.get("text-anchor", "start")
        width = 0.5 * size * len(text)
        if anchor == "middle":
            x0 = x - width / 2
        elif anchor == "end":
            x0 = x - width
        else:
            x0 = x
        labels.append(((x0, y - 0.75 * size, width, size), text))
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


def main():
    ap = argparse.ArgumentParser(
        description="Check a cast-map SVG: edges through boxes, overlapping boxes (including a node inside another node), merged arrowheads, labels on lines or boxes."
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
            html = open(path, encoding="utf-8", errors="replace").read()
        except OSError as exc:
            print(f"ERROR {path}: {exc}")
            failed += 1
            continue
        svg_matches = re.findall(r"<svg\b.*?</svg>", html, re.S)
        svg = svg_matches[0] if svg_matches else ""
        svg = re.sub(r"<defs\b.*?</defs>", "", svg, flags=re.S)

        rects_all = load_all_rects(svg)
        boxes = [r for r, is_frame in rects_all if not is_frame]
        segs = load_segments(svg)
        labels = load_labels(svg)
        terminals = load_terminals(svg)

        edge_hits = []
        for si, (p1, p2) in enumerate(segs):
            for bi, r in enumerate(boxes):
                ov = overlap_length(p1, p2, r)
                if ov > args.min_overlap:
                    edge_hits.append((si, bi, ov, r, p1, p2))

        box_hits = []
        for i in range(len(rects_all)):
            for j in range(i + 1, len(rects_all)):
                ri, i_is_frame = rects_all[i]
                rj, j_is_frame = rects_all[j]
                ox, oy = rect_overlap(ri, rj)
                if ox > args.min_overlap and oy > args.min_overlap:
                    if (contains(rj, ri) and j_is_frame) or (
                        contains(ri, rj) and i_is_frame
                    ):
                        continue
                    box_hits.append((i, j, ox, oy, ri, rj))

        label_line_hits = []
        for rect, text in labels:
            for si, (p1, p2) in enumerate(segs):
                if overlap_length(p1, p2, rect) > args.min_overlap:
                    label_line_hits.append((text, si, p1, p2))

        label_box_hits = []
        for rect, text in labels:
            for bi, r in enumerate(boxes):
                ox, oy = rect_overlap(rect, r)
                if ox > args.min_overlap and oy > args.min_overlap:
                    if contains(r, rect):
                        continue
                    label_box_hits.append((text, bi, r, ox, oy))

        arrow_hits = []
        for i in range(len(terminals)):
            for j in range(i + 1, len(terminals)):
                (ax, ay), (bx, by) = terminals[i], terminals[j]
                gap = ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5
                if gap < args.arrowhead_gap:
                    arrow_hits.append((i, j, gap, terminals[i], terminals[j]))

        fatal = (
            len(edge_hits)
            + len(box_hits)
            + len(label_box_hits)
            + len(arrow_hits)
            + (len(label_line_hits) if args.strict_labels else 0)
        )
        print(
            f"{'OK' if fatal == 0 else 'PROBLEMS'} {path}: {len(boxes)} boxes, {len(segs)} segments, "
            f"{len(labels)} labels | edges-through-boxes={len(edge_hits)} box-overlaps={len(box_hits)} "
            f"merged-arrowheads={len(arrow_hits)} labels-on-boxes={len(label_box_hits)} "
            f"labels-on-lines={len(label_line_hits)}{' (fatal)' if args.strict_labels else ' (warnings)'}"
        )
        for si, bi, ov, r, p1, p2 in edge_hits:
            print(
                f"   edge {si} {p1}->{p2} passes through box {bi} at x={r[0]} y={r[1]} w={r[2]} h={r[3]} by {ov:.1f}px"
            )
        for i, j, ox, oy, a, b in box_hits:
            print(f"   boxes {i} {a} and {j} {b} overlap by {ox:.1f}x{oy:.1f}px")
        for i, j, gap, p, q in arrow_hits:
            print(f"   arrowheads merge: endpoints {p} and {q} are {gap:.1f}px apart")
        for text, bi, r, ox, oy in label_box_hits:
            print(
                f'   label "{safe(text[:40])}" covers box {bi} at x={r[0]} y={r[1]} by {ox:.1f}x{oy:.1f}px'
            )
        for text, si, p1, p2 in label_line_hits:
            print(f'   label "{safe(text[:40])}" sits on edge {si} {p1}->{p2}')
        if fatal:
            failed += 1
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
