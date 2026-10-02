import itertools
import math
import re
from pathlib import Path

import pytest

CSS = (Path(__file__).resolve().parents[2] / "assets" / "lesson.css").read_text(encoding="utf-8")
TOKENS = [f"--d{i}" for i in range(1, 7)] + ["--d-neutral"]


def tokens(block):
    return dict(re.findall(r"(--[\w-]+):\s*(#[0-9a-fA-F]{6})", block))


def themes():
    light = tokens(CSS[: CSS.index("@media (prefers-color-scheme: dark)")])
    dark_block = CSS[CSS.index("@media (prefers-color-scheme: dark)") :]
    dark = {**light, **tokens(dark_block[: dark_block.index("/* Size presets")])}
    return {"light": light, "dark": dark}


def luminance(hex_colour):
    r, g, b = (int(hex_colour[i : i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def lab(hex_colour):
    """CIE L*a*b* (D65) of an sRGB hex colour."""
    r, g, b = (int(hex_colour[i : i + 2], 16) / 255 for i in (1, 3, 5))
    lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = lin(r), lin(g), lin(b)
    xyz = (
        (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047,
        0.2126 * r + 0.7152 * g + 0.0722 * b,
        (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883,
    )
    fx, fy, fz = (v ** (1 / 3) if v > 0.008856 else 7.787 * v + 16 / 116 for v in xyz)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


MIN_DELTA_E = 30


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("token", TOKENS)
def test_diagram_colour_contrasts_strongly_with_the_page(theme, token):
    t = themes()[theme]
    assert contrast(t[token], t["--paper"]) >= 4.5


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_diagram_colours_are_distinct(theme):
    t = themes()[theme]
    values = [t[k].lower() for k in TOKENS]
    assert len(set(values)) == len(values)


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_diagram_colours_stay_apart_from_each_other_and_from_the_accent(theme):
    t = themes()[theme]
    for a, b in itertools.combinations(TOKENS + ["--accent"], 2):
        assert math.dist(lab(t[a]), lab(t[b])) >= MIN_DELTA_E, (a, b)


def test_neutral_is_a_strong_ink_tone_not_a_faint_grey():
    for theme, t in themes().items():
        assert contrast(t["--d-neutral"], t["--paper"]) >= 7, theme


def test_no_uppercase_transform():
    assert "text-transform: uppercase" not in CSS
