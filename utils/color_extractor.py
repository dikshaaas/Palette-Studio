"""
color_extractor.py
------------------
Runs K-Means clustering on pixel data to find dominant colors,
calculates their percentage share, and maps them to HEX / color names.
"""

import numpy as np
from sklearn.cluster import KMeans
import webcolors


# Cache CSS3 color names and RGB tuples for fast nearest-neighbor calculation
_CSS3_COLORS = []
try:
    for _name in webcolors.names("css3"):
        _rgb = webcolors.name_to_rgb(_name)
        _CSS3_COLORS.append((_rgb, _name))
except Exception:
    pass

def _nearest_css_name(rgb: tuple[int, int, int]) -> str:
    """
    Find the closest CSS3 named color to the given RGB tuple using
    Euclidean distance in RGB space.
    """
    if not _CSS3_COLORS:
        return "Custom Color"

    min_dist = float("inf")
    closest_name = "unknown"

    for (r, g, b), name in _CSS3_COLORS:
        dist = ((r - rgb[0]) ** 2 + (g - rgb[1]) ** 2 + (b - rgb[2]) ** 2) ** 0.5
        if dist < min_dist:
            min_dist = dist
            closest_name = name

    return closest_name.replace("-", " ").title()



# ── Main extraction function ──────────────────────────────────────────────────

def extract_colors(pixels: np.ndarray, n_colors: int = 6) -> list[dict]:
    """
    Run K-Means on the (N, 3) pixel array and return a sorted list of
    dominant color dicts.

    Args:
        pixels:   NumPy array of shape (N, 3) with float32 RGB values.
        n_colors: Number of dominant colors to extract (k for KMeans).

    Returns:
        List of dicts, sorted by percentage descending:
        [
          {
            "rgb":     (R, G, B),
            "hex":     "#RRGGBB",
            "name":    "Sky Blue",
            "percent": 42.5,
          },
          ...
        ]
    """
    n_colors = max(2, min(n_colors, 12))  # clamp to sane range

    kmeans = KMeans(
        n_clusters=n_colors,
        n_init=10,
        max_iter=300,
        random_state=42,
    )
    kmeans.fit(pixels)

    centers = kmeans.cluster_centers_.astype(int)   # shape (k, 3)
    labels  = kmeans.labels_                         # shape (N,)
    total   = len(labels)

    colors = []
    for i, center in enumerate(centers):
        r, g, b = int(center[0]), int(center[1]), int(center[2])
        count   = int(np.sum(labels == i))
        percent = round((count / total) * 100, 1)

        hex_color = "#{:02X}{:02X}{:02X}".format(r, g, b)
        name      = _nearest_css_name((r, g, b))

        colors.append({
            "rgb":     (r, g, b),
            "hex":     hex_color,
            "name":    name,
            "percent": percent,
        })

    # Sort by percentage, largest first
    colors.sort(key=lambda c: c["percent"], reverse=True)
    return colors
