"""
random_palette.py
-----------------
Generates soothing, harmonious random color palettes
using constrained HSL for a calm aesthetic.
"""

import random
import colorsys
from io import BytesIO

from PIL import Image, ImageDraw

from utils.color_harmony import generate_harmonies


def _nearest_css_name(rgb: tuple[int, int, int]) -> str:
    try:
        import webcolors
        names = []
        for name in webcolors.names("css3"):
            names.append((webcolors.name_to_rgb(name), name))
        min_dist = float("inf")
        closest = "Custom Color"
        for (r, g, b), name in names:
            dist = ((r - rgb[0]) ** 2 + (g - rgb[1]) ** 2 + (b - rgb[2]) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                closest = name
        return closest.replace("-", " ").title()
    except Exception:
        return "Custom Color"


def _hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    r, g, b = colorsys.hls_to_rgb(h / 360.0, l, s)
    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    r, g, b = rgb
    return f"#{r:02X}{g:02X}{b:02X}"


# Soft mood seeds — warm sunset / beige / lavender ranges
_MOODS = [
    ("sunset",   (12, 38)),      # apricot → coral
    ("blush",    (340, 360)),    # soft rose
    ("lavender", (265, 295)),    # light lilac
    ("sand",     (28, 48)),      # warm beige / gold
    ("peach",    (18, 32)),      # peach
    ("dusk",     (300, 330)),    # mauve dusk
]


def generate_random_colors(n_colors: int = 5) -> list[dict]:
    """
    Build a cohesive random palette with soothing saturation/lightness.
    Returns list of color dicts matching the extractor schema.
    """
    n_colors = max(3, min(8, n_colors))
    mood_name, (h_lo, h_hi) = random.choice(_MOODS)
    base_h = random.uniform(h_lo, h_hi)

    # Spread hues gently around the base (analogous + one accent)
    offsets = []
    span = 48.0
    for i in range(n_colors):
        t = i / max(n_colors - 1, 1)
        offsets.append(-span / 2 + t * span)

    # Occasional complementary pop on the last swatch
    if n_colors >= 4 and random.random() < 0.45:
        offsets[-1] = 180.0 + random.uniform(-12, 12)

    colors = []
    weights = []
    for i, offset in enumerate(offsets):
        h = (base_h + offset) % 360
        # Keep saturation soft; mid-range lightness for elegance
        s = random.uniform(0.22, 0.48)
        if i == 0:
            l = random.uniform(0.28, 0.42)   # deeper anchor
        elif i == n_colors - 1:
            l = random.uniform(0.72, 0.88)   # soft highlight
        else:
            l = random.uniform(0.45, 0.68)

        rgb = _hsl_to_rgb(h, s, l)
        # Soft weight curve — first colors slightly more present
        w = random.uniform(0.8, 1.4) * (1.15 - i * 0.08)
        weights.append(w)
        colors.append({
            "rgb": rgb,
            "hex": _rgb_to_hex(rgb),
            "name": _nearest_css_name(rgb),
            "percent": 0.0,
        })

    total = sum(weights)
    for c, w in zip(colors, weights):
        c["percent"] = round((w / total) * 100, 1)

    # Fix rounding so percents sum ~100
    drift = round(100.0 - sum(c["percent"] for c in colors), 1)
    colors[0]["percent"] = round(colors[0]["percent"] + drift, 1)

    colors.sort(key=lambda c: c["percent"], reverse=True)
    return colors


def generate_palette_thumbnail(colors: list[dict], width: int = 480, height: int = 320) -> Image.Image:
    """Create a soft gradient / strip preview image from palette colors."""
    img = Image.new("RGB", (width, height), (245, 242, 238))
    draw = ImageDraw.Draw(img)

    n = max(len(colors), 1)
    # Vertical soft bands
    band_w = width / n
    for i, c in enumerate(colors):
        x0 = int(i * band_w)
        x1 = int((i + 1) * band_w) if i < n - 1 else width
        draw.rectangle([x0, 0, x1, height], fill=tuple(c["rgb"]))

    # Soft bottom fade overlay for depth
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(height // 2, height):
        alpha = int(40 * ((y - height / 2) / (height / 2)))
        od.line([(0, y), (width, y)], fill=(20, 30, 28, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    return img


def build_random_palette_record(n_colors: int = 5) -> dict:
    """Return colors + harmonies + thumbnail PIL image for a random palette."""
    colors = generate_random_colors(n_colors)
    harmonies = generate_harmonies(colors[0]["rgb"]) if colors else {}
    thumb = generate_palette_thumbnail(colors)
    return {
        "colors": colors,
        "harmonies": harmonies,
        "thumb": thumb,
        "orig_size": [thumb.width, thumb.height],
    }
