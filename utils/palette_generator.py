"""
palette_generator.py
--------------------
Generates downloadable palette assets:
  - PNG: colored rectangle strips with HEX labels
  - JSON: structured color data
  - CSS: CSS Custom Properties (:root variables)
  - Tailwind: Tailwind CSS color configuration object
"""

import io
import json
from PIL import Image, ImageDraw, ImageFont


def generate_palette_png(colors: list[dict], swatch_w: int = 200, swatch_h: int = 120) -> bytes:
    """
    Create a horizontal palette PNG strip.
    """
    n = len(colors)
    img_w = swatch_w * n
    img = Image.new("RGB", (img_w, swatch_h + 40), (250, 250, 250))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 14)
        small_font = ImageFont.truetype("arial.ttf", 11)
    except Exception:
        font = ImageFont.load_default()
        small_font = font

    for idx, color in enumerate(colors):
        r, g, b = color["rgb"]
        x_start = idx * swatch_w

        # Swatch rectangle
        draw.rectangle(
            [x_start, 0, x_start + swatch_w - 2, swatch_h - 1],
            fill=(r, g, b),
        )

        # Label card background
        draw.rectangle(
            [x_start, swatch_h, x_start + swatch_w - 2, swatch_h + 39],
            fill=(250, 250, 250),
        )

        # HEX label
        hex_text = color["hex"]
        draw.text(
            (x_start + 12, swatch_h + 6),
            hex_text,
            fill=(17, 24, 39),
            font=font,
        )

        # Percentage label
        pct_text = f"{color['percent']}%" if "percent" in color else color.get("name", "")
        draw.text(
            (x_start + 12, swatch_h + 22),
            pct_text,
            fill=(107, 114, 128),
            font=small_font,
        )

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def generate_palette_json(colors: list[dict], harmonies: dict = None) -> str:
    """
    Serialize palette colors & harmonies to a JSON string.
    """
    payload = {
        "dominant": [
            {
                "hex":     c["hex"],
                "rgb":     list(c["rgb"]),
                "name":    c["name"],
                "percent": c.get("percent", 0),
            }
            for c in colors
        ]
    }
    if harmonies:
        payload["harmonies"] = harmonies

    return json.dumps(payload, indent=2)


def generate_css_variables(colors: list[dict]) -> str:
    """
    Generate CSS custom properties.
    """
    lines = [":root {"]
    for i, c in enumerate(colors, 1):
        clean_name = c["name"].lower().replace(" ", "-")
        lines.append(f"  --palette-color-{i}: {c['hex']}; /* {c['name']} */")
    lines.append("}")
    return "\n".join(lines)


def generate_tailwind_config(colors: list[dict]) -> str:
    """
    Generate Tailwind CSS theme color extension.
    """
    lines = ["// tailwind.config.js snippet", "module.exports = {", "  theme: {", "    extend: {", "      colors: {", "        palette: {"]
    for i, c in enumerate(colors, 1):
        key = f"color-{i}"
        lines.append(f"          '{key}': '{c['hex']}', // {c['name']}")
    lines.append("        }")
    lines.append("      }")
    lines.append("    }")
    lines.append("  }")
    lines.append("}")
    return "\n".join(lines)
