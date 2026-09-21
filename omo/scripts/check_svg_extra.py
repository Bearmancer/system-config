import importlib.util as u
import re
import sys

CHECKER = r"C:\Users\Lance\.claude\skills\learning-course\scripts\check_map_geometry.py"
TOL = 6.0
MIN_OV = 2.0


def load_module():
    spec = u.spec_from_file_location("g", CHECKER)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load spec/loader for {CHECKER}")
    m = u.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def dist_to_rect(px, py, r):
    x, y, w, h = r
    dx = max(x - px, px - (x + w), 0.0)
    dy = max(y - py, py - (y + h), 0.0)
    return (dx * dx + dy * dy) ** 0.5


def dist_to_border(px, py, r):
    x, y, w, h = r
    return min(px - x, x + w - px, py - y, y + h - py)


def attached(px, py, rects):
    for r in rects:
        d = dist_to_rect(px, py, r)
        if d > TOL:
            continue
        if d == 0.0 and dist_to_border(px, py, r) > TOL:
            continue
        return True
    return False


def main():
    m = load_module()
    bad = 0
    for path in sys.argv[1:]:
        html = open(path, encoding="utf-8", errors="replace").read()
        svgs = re.findall(r"<svg\b.*?</svg>", html, re.S)
        if not svgs:
            print(f"ERROR {path}: no svg")
            bad += 1
            continue
        svg = re.sub(r"<defs\b.*?</defs>", "", svgs[0], flags=re.S)
        vb = re.search(r'viewBox="([^"]+)"', svgs[0])
        if vb is None:
            print(f"ERROR {path}: no viewBox attribute on <svg>")
            bad += 1
            continue
        W, H = (float(v) for v in vb.group(1).split()[2:4])
        rects_all = m.load_all_rects(svg)
        boxes = [r for r, is_frame in rects_all if not is_frame]
        frames = [r for r, is_frame in rects_all if is_frame]
        all_rects = boxes + frames
        segs = m.load_segments(svg)
        labels = m.load_labels(svg)
        raw_lines = re.findall(r"<line\b[^>]*>", svg)
        raw_polys = re.findall(r"<polyline\b[^>]*>", svg)

        findings = []

        for i in range(len(labels)):
            for j in range(i + 1, len(labels)):
                ox, oy = m.rect_overlap(labels[i][0], labels[j][0])
                if ox > MIN_OV and oy > MIN_OV:
                    findings.append(
                        f'A label-vs-label: "{labels[i][1][:34]}" and "{labels[j][1][:34]}" '
                        f"overlap {ox:.0f}x{oy:.0f}px"
                    )

        for rect, text in labels:
            x0, y0, w, h = rect
            if x0 < -1 or y0 < -1 or x0 + w > W + 1 or y0 + h > H + 1:
                findings.append(
                    f'B label clipped by canvas: "{text[:34]}" box=({x0:.0f},{y0:.0f},{w:.0f},{h:.0f}) '
                    f"viewBox={W:.0f}x{H:.0f}"
                )

        for bi, r in enumerate(boxes):
            pts = []
            for tag in raw_lines:
                a = m.attrs(tag)
                try:
                    pts.append((float(a["x1"]), float(a["y1"])))
                    pts.append((float(a["x2"]), float(a["y2"])))
                except (KeyError, ValueError):
                    pass
            for tag in raw_polys:
                a = m.attrs(tag)
                nums = [
                    float(p) for p in a.get("points", "").replace(",", " ").split() if p
                ]
                pts.extend(zip(nums[0::2], nums[1::2]))
            if not any(dist_to_rect(px, py, r) <= TOL for px, py in pts):
                findings.append(
                    f"C isolated node: box at x={r[0]:.0f} y={r[1]:.0f} w={r[2]:.0f} h={r[3]:.0f} "
                    f"(no edge touches it)"
                )

        terminals = []
        for tag in raw_lines:
            a = m.attrs(tag)
            try:
                terminals.append(("line start", (float(a["x1"]), float(a["y1"]))))
                terminals.append(("line end", (float(a["x2"]), float(a["y2"]))))
            except (KeyError, ValueError):
                pass
        for tag in raw_polys:
            a = m.attrs(tag)
            nums = [
                float(p) for p in a.get("points", "").replace(",", " ").split() if p
            ]
            pairs = list(zip(nums[0::2], nums[1::2]))
            if pairs:
                terminals.append(("polyline start", pairs[0]))
                terminals.append(("polyline end", pairs[-1]))
        for kind, (px, py) in terminals:
            if not attached(px, py, all_rects):
                findings.append(
                    f"D dangling edge terminal: {kind} at ({px:.0f},{py:.0f}) is not attached to any box"
                )

        print(
            f"{'PROBLEMS' if findings else 'OK'} {path} [{W:.0f}x{H:.0f}] "
            f"boxes={len(boxes)} frames={len(frames)} segments={len(segs)} labels={len(labels)} "
            f"label-label={sum(1 for f in findings if f.startswith('A'))} "
            f"clipped={sum(1 for f in findings if f.startswith('B'))} "
            f"isolated={sum(1 for f in findings if f.startswith('C'))} "
            f"dangling={sum(1 for f in findings if f.startswith('D'))}"
        )
        for f in findings:
            print("   - " + f)
        if findings:
            bad += 1
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
