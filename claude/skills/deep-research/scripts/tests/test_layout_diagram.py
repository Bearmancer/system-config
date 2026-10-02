import copy
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import check_map_geometry as geo
import layout_diagram as ld

SPEC = {
    "title": "Chapter 5 relationships",
    "rows": [
        [
            {"id": "kand", "name": "Taliban in Kandahar", "note": "Decrees and gold money"},
            {"id": "kabul", "name": "Taliban in Kabul", "note": "Officials defying orders"},
        ],
        [
            {"id": "isk", "name": "Islamic State", "note": "Khorasan spoiler"},
            {"id": "auf", "name": "United Front", "note": "Sadat Kandahar base"},
            {"id": "aff", "name": "Freedom Front", "note": "Zia shadow cells"},
            {"id": "nrf", "name": "National Resistance Front", "note": "Massoud exile network"},
        ],
    ],
    "types": {"attack": "Attack"},
    "edges": [
        {"from": "nrf", "to": "kand", "label": "NRF raids north", "type": "attack", "directed": True},
        {"from": "aff", "to": "kabul", "label": "AFF ambushes Taliban", "type": "attack", "directed": True},
        {"from": "auf", "to": "kand", "label": "AUF hits Kandahar police", "type": "attack", "directed": True},
        {"from": "isk", "to": "kabul", "label": "IS-K bombs rivals", "type": "attack", "directed": True},
        {"from": "kabul", "to": "kand", "label": "Kabul defies the cutoff", "directed": False},
    ],
}


def spec(**changes):
    s = copy.deepcopy(SPEC)
    s.update(changes)
    return s


def parsed_lines(svg):
    return [
        ((float(a), float(b)), (float(c), float(e)))
        for a, b, c, e in re.findall(
            r'<line class="edge"[^>]*x1="([\d.]+)" y1="([\d.]+)" x2="([\d.]+)" y2="([\d.]+)"', svg
        )
    ]


def count_crossings(lines):
    def side(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    total = 0
    for i, (a, b) in enumerate(lines):
        for c, e in lines[i + 1 :]:
            if side(a, b, c) * side(a, b, e) < 0 and side(c, e, a) * side(c, e, b) < 0:
                total += 1
    return total


def fatal(svg):
    h = geo.analyze(svg)
    return {k: v for k, v in h.items() if k != "counts" and v}


def test_render_has_no_geometry_defect_including_labels_on_lines():
    d = ld.layout(SPEC)
    assert fatal(d.svg) == {}


def test_barycentre_order_removes_crossings():
    d = ld.layout(SPEC)
    assert d.crossings == 0
    assert count_crossings(parsed_lines(d.svg)) == 0
    order = re.findall(r'<text x="([\d.]+)"[^>]*font-weight="600"[^>]*>([^<]+)</text>', d.svg)
    bottom = [
        name
        for x, name in sorted(order, key=lambda t: float(t[0]))
        if name in ("Islamic State", "United Front", "Freedom Front", "National Resistance Front")
    ]
    assert bottom == ["United Front", "National Resistance Front", "Islamic State", "Freedom Front"]


def test_edge_ends_spread_along_the_box_side():
    d = ld.layout(SPEC)
    ends = re.findall(r'<line class="edge"[^>]*x2="([\d.]+)" y2="([\d.]+)"', d.svg)
    tops = [(x, y) for x, y in ends if y == ends[0][1]]
    assert len({x for x, _ in tops}) == len(tops) > 1


def test_colour_is_relationship_type_and_repeats_only():
    d = ld.layout(SPEC)
    attack = re.findall(r'data-type="attack"[^>]*stroke="([^"]+)"', d.svg)
    assert attack == ["var(--d1)"] * 4
    assert re.search(r'<line class="edge" x1[^>]*stroke="var\(--d-neutral\)"', d.svg)
    assert 'background:var(--d1)"></span>Attack' in d.legend
    assert "Single event, named on its line" in d.legend


def test_type_used_once_falls_back_to_neutral():
    s = spec(types={"attack": "Attack", "split": "Split"})
    s["edges"][4]["type"] = "split"
    d = ld.layout(s)
    assert "var(--d2)" not in d.svg
    assert "Split" not in d.legend


def test_arrowheads_only_on_directed_edges_actor_to_target():
    d = ld.layout(SPEC)
    assert d.svg.count("marker-end") == 4
    assert len(re.findall(r'<line class="edge"[^>]*/>', d.svg)) == 5


def test_solid_lines_plain_text_and_token_colours_only():
    d = ld.layout(SPEC)
    assert "stroke-dasharray" not in d.svg
    assert "transform" not in d.svg
    assert not re.search(r'(?:stroke|fill)="#', d.svg)


def test_marker_ids_carry_the_diagram_uid():
    assert 'id="ah-x-d1"' in ld.layout(SPEC, uid="x").svg


def test_names_are_escaped():
    s = copy.deepcopy(SPEC)
    s["rows"][0][0]["name"] = "Taliban & Co"
    assert "Taliban &amp; Co" in ld.layout(s).svg


def test_narrow_gap_widens_the_canvas_until_the_label_fits():
    s = spec(
        rows=[[{"id": "a", "name": "Alpha"}, {"id": "b", "name": "Beta"}]],
        edges=[{"from": "a", "to": "b", "label": "a rather long label sitting between two boxes", "directed": False}],
    )
    d = ld.layout(s)
    assert fatal(d.svg) == {}


def test_label_that_never_fits_raises():
    s = spec(
        rows=[[{"id": "a", "name": "Alpha"}, {"id": "b", "name": "Beta"}]],
        edges=[{"from": "a", "to": "b", "label": "x" * 400, "directed": False}],
    )
    with pytest.raises(ld.DiagramError, match="no clear spot"):
        ld.layout(s)


def test_line_through_an_intermediate_box_raises():
    s = {
        "rows": [
            [{"id": "a", "name": "A"}],
            [{"id": "b", "name": "B"}],
            [{"id": "c", "name": "C"}],
        ],
        "edges": [{"from": "a", "to": "c", "label": "skips b", "directed": True}],
    }
    with pytest.raises(ld.DiagramError, match="passes through b"):
        ld.layout(s)


def test_same_row_edge_between_non_neighbours_raises():
    s = {
        "rows": [[{"id": "a", "name": "A"}, {"id": "b", "name": "B"}, {"id": "c", "name": "C"}]],
        "edges": [{"from": "a", "to": "c", "label": "far", "directed": False}],
    }
    with pytest.raises(ld.DiagramError, match="not neighbours"):
        ld.layout(s)


@pytest.mark.parametrize(
    "mutate,message",
    [
        (lambda s: s["edges"][0].pop("directed"), "needs directed"),
        (lambda s: s["edges"][0].update({"type": "unknown"}), "no entry in types"),
        (lambda s: s["edges"][0].update({"to": "ghost"}), "unknown node"),
        (lambda s: s["edges"][0].pop("label"), "needs label"),
        (lambda s: s["rows"][1][0].update({"id": "kand"}), "unique id"),
    ],
)
def test_invalid_specs_raise(mutate, message):
    s = copy.deepcopy(SPEC)
    mutate(s)
    with pytest.raises(ld.DiagramError, match=message):
        ld.layout(s)


def test_more_repeating_types_than_palette_raises():
    rows = [
        [{"id": f"t{i}", "name": f"T{i}"} for i in range(6)],
        [{"id": f"b{i}", "name": f"B{i}"} for i in range(6)],
    ]
    pairs = [(f"b{i}", f"t{i}", f"k{i}") for i in range(6)]
    pairs += [(f"b{(i + 1) % 6}", f"t{i}", f"k{i}") for i in range(6)]
    pairs += [("b0", "t2", "k6"), ("b3", "t5", "k6")]
    edges = [
        {"from": a, "to": b, "label": f"e{n}", "type": k, "directed": True}
        for n, (a, b, k) in enumerate(pairs)
    ]
    types = {f"k{i}": f"Kind {i}" for i in range(7)}
    with pytest.raises(ld.DiagramError, match="palette"):
        ld.layout({"rows": rows, "edges": edges, "types": types})


def test_more_than_twelve_nodes_raises():
    rows = [[{"id": f"n{i}", "name": f"N{i}"} for i in range(13)]]
    with pytest.raises(ld.DiagramError, match="cap is 12"):
        ld.layout({"rows": rows, "edges": []})


def test_each_label_sits_nearer_its_own_line_than_any_other():
    d = ld.layout(SPEC)
    lines = parsed_lines(d.svg)
    labels = re.findall(r'<text class="elabel" x="([\d.]+)" y="([\d.]+)"', d.svg)
    for i, (x, y) in enumerate(labels):
        centre = (float(x), float(y) - 0.25 * ld.LABEL_SIZE)
        own = ld._distance(centre, lines[i])
        assert all(own + ld.OWNER_MARGIN <= ld._distance(centre, ln) for j, ln in enumerate(lines) if j != i)


def test_up_sweep_removes_a_crossing_the_down_sweep_leaves():
    rows = [
        [{"id": "t0", "name": "T0"}, {"id": "t1", "name": "T1"}],
        [{"id": "m0", "name": "M0"}, {"id": "m1", "name": "M1"}, {"id": "m2", "name": "M2"}],
        [{"id": "b0", "name": "B0"}, {"id": "b1", "name": "B1"}, {"id": "b2", "name": "B2"}],
    ]
    pairs = [("t0", "m1"), ("t0", "m2"), ("m2", "b2"), ("m0", "b2"), ("m1", "b1")]
    edges = [{"from": a, "to": b, "label": f"e{i}", "directed": False} for i, (a, b) in enumerate(pairs)]
    down_only, x_of = ld._sweep(rows, edges, 900, 160, up=False)
    assert ld._crossings(down_only, edges, x_of) == 1
    d = ld.layout({"rows": rows, "edges": edges})
    assert d.crossings == 0
    assert count_crossings(parsed_lines(d.svg)) == 0


def test_colours_follow_first_use_over_the_edges():
    two_rows = [
        [{"id": "a", "name": "A"}, {"id": "b", "name": "B"}],
        [{"id": "c", "name": "C"}, {"id": "d", "name": "D"}],
    ]
    edges = [
        {"from": "c", "to": "a", "label": "p", "type": "second", "directed": False},
        {"from": "d", "to": "b", "label": "q", "type": "second", "directed": False},
        {"from": "c", "to": "b", "label": "r", "type": "first", "directed": False},
        {"from": "d", "to": "a", "label": "s", "type": "first", "directed": False},
    ]
    types = {"first": "First kind", "second": "Second kind"}
    d = ld.layout({"rows": two_rows, "edges": edges, "types": types})
    assert re.findall(r'data-type="second"[^>]*stroke="([^"]+)"', d.svg) == ["var(--d1)"] * 2
    assert re.findall(r'data-type="first"[^>]*stroke="([^"]+)"', d.svg) == ["var(--d2)"] * 2


@pytest.mark.parametrize(
    "mutate",
    [
        lambda s: s.update({"rows": "abc"}),
        lambda s: s.update({"rows": [["kand"]]}),
        lambda s: s["rows"][0][0].update({"id": 7}),
        lambda s: s["rows"][0][0].update({"name": ["x"]}),
        lambda s: s["rows"][0][0].update({"note": 5}),
        lambda s: s.update({"edges": "none"}),
        lambda s: s.update({"edges": ["kand-kabul"]}),
        lambda s: s.update({"types": ["attack"]}),
        lambda s: s.update({"types": {"attack": 3}}),
        lambda s: s["edges"][0].update({"label": 4}),
    ],
)
def test_wrongly_typed_specs_raise_diagram_error(mutate):
    s = copy.deepcopy(SPEC)
    mutate(s)
    with pytest.raises(ld.DiagramError):
        ld.layout(s)


def test_a_spec_that_is_not_a_mapping_raises():
    with pytest.raises(ld.DiagramError):
        ld.layout(["rows"])
