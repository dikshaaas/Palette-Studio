"""
color_harmony.py
----------------
Provides mathematical color harmony generation (Complementary, Analogous,
Monochromatic) from RGB color tuples.
"""

import colorsys
import webcolors

# Cache CSS3 color names and RGB tuples for fast nearest-neighbor calculation
_CSS3_COLORS = []
try:
    for _name in webcolors.names("css3"):
        _rgb = webcolors.name_to_rgb(_name)
        _CSS3_COLORS.append((_rgb, _name))
except Exception:
    pass


def _nearest_name(rgb: tuple[int, int, int]) -> str:
    if not _CSS3_COLORS:
        return "Custom Color"
    min_dist = float("inf")
    closest = "unknown"
    for (r, g, b), name in _CSS3_COLORS:
        dist = ((r - rgb[0])**2 + (g - rgb[1])**2 + (b - rgb[2])**2) ** 0.5
        if dist < min_dist:
            min_dist = dist
            closest = name
    return closest.replace("-", " ").title()


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    r, g, b = [max(0, min(255, int(v))) for v in rgb]
    return f"#{r:02X}{g:02X}{b:02X}"


def hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    """h: 0-360, s: 0-1, l: 0-1 -> (r, g, b) 0-255"""
    r, g, b = colorsys.hls_to_rgb(h / 360.0, l, s)
    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))


def rgb_to_hsl(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    """(r, g, b) 0-255 -> h: 0-360, s: 0-1, l: 0-1"""
    r, g, b = [v / 255.0 for v in rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (h * 360.0, s, l)


def format_color_item(rgb: tuple[int, int, int]) -> dict:
    hex_val = rgb_to_hex(rgb)
    return {
        "rgb": rgb,
        "hex": hex_val,
        "name": _nearest_name(rgb)
    }


def generate_harmonies(primary_rgb: tuple[int, int, int]) -> dict[str, list[dict]]:
    """
    Given a primary RGB color tuple, generate:
    - Complementary palette (2-4 colors)
    - Analogous palette (4-5 colors)
    - Monochromatic palette (5 colors)
    """
    h, s, l = rgb_to_hsl(primary_rgb)

    # 1. Complementary Palette
    # Base color, 180° opposite, plus slightly desaturated/lighter variants
    comp_h = (h + 180.0) % 360.0
    complementary_rgbs = [
        primary_rgb,
        hsl_to_rgb(comp_h, s, l),
        hsl_to_rgb(comp_h, max(0.1, s * 0.7), min(0.9, l * 1.25)),
        hsl_to_rgb(h, max(0.1, s * 0.5), min(0.95, l * 1.35))
    ]

    # 2. Analogous Palette
    # Base color + -60°, -30°, +30°, +60°
    analogous_angles = [-60.0, -30.0, 0.0, 30.0, 60.0]
    analogous_rgbs = [
        hsl_to_rgb((h + angle) % 360.0, s, l)
        for angle in analogous_angles
    ]

    # 3. Monochromatic Palette
    # Same hue, varying lightness steps (15%, 35%, 55%, 75%, 90%)
    mono_lightness_steps = [0.15, 0.35, 0.55, 0.75, 0.90]
    mono_rgbs = [
        hsl_to_rgb(h, min(1.0, max(0.2, s)), l_step)
        for l_step in mono_lightness_steps
    ]

    return {
        "complementary": [format_color_item(c) for c in complementary_rgbs],
        "analogous":     [format_color_item(c) for c in analogous_rgbs],
        "monochromatic": [format_color_item(c) for c in mono_rgbs],
    }
