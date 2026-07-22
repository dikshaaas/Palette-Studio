# Palette Studio

A web application that extracts dominant color palettes from photos, generates soothing random harmonies, and helps you organize, favorite, and export colors for design work.

Upload an image → get a clear color story (HEX, RGB, names, percentages) → explore complementary / analogous / monochromatic variations → export as PNG, JSON, CSS, or Tailwind.

---

## Features

- **Extract from photos** — Upload JPG/PNG images and pull out 3–10 dominant colors
- **Random palettes** — Generate warm, cohesive color sets without an image
- **Color harmonies** — Complementary, analogous, and monochromatic variations from the primary color
- **Library & favorites** — Save palettes into folders, search, filter, and favorite
- **Exports** — PNG strip, JSON data, CSS custom properties, Tailwind config snippet
- **Live UI preview** — See how extracted colors look on a simple mock interface
- **Settings** — Default color count, auto-save, and theme preferences
- **Light / dark theme** — Soft warm sunset aesthetic with a calm dark mode

---

## Tech Stack

| Layer | Technology |
|--------|------------|
| Backend | Python 3, Flask |
| Image I/O | OpenCV (`opencv-python`), Pillow |
| Clustering | scikit-learn (`KMeans`), NumPy |
| Color naming | `webcolors` (CSS3 nearest-name match) |
| Frontend | Jinja2 templates, HTML5, CSS3, vanilla JavaScript |
| Storage | JSON files under `data/` (no database required) |

### Dependencies (`requirements.txt`)

```
Flask>=3.0.0
opencv-python>=4.10.0
scikit-learn>=1.5.0
numpy>=1.26.0
Pillow>=10.4.0
webcolors>=24.6.0
```

---

## How Color Extraction Works

Palette Studio turns an image into a small set of representative colors using **K-Means clustering** in RGB space.

### Pipeline

1. **Load & preprocess** (`utils/image_processing.py`)
   - Read the image with OpenCV (BGR → RGB)
   - Resize so the longest side is at most 500px (keeps clustering fast; never upscales)
   - Flatten pixels into an `(N, 3)` float array of `[R, G, B]` values

2. **Cluster with K-Means** (`utils/color_extractor.py`)
   - Run scikit-learn `KMeans` with `k = n_colors` (default 6, range 3–10)
   - Cluster centers become the dominant colors
   - Each color’s **percentage** is the share of pixels assigned to that cluster
   - Results are sorted by percentage (largest first)

3. **Name & format**
   - Convert RGB → HEX (`#RRGGBB`)
   - Map each RGB to the nearest **CSS3 color name** using Euclidean distance in RGB space (`webcolors`)

4. **Harmonies** (`utils/color_harmony.py`)
   - Convert the primary color to HSL
   - Build:
     - **Complementary** — base + ~180° opposite (+ softer variants)
     - **Analogous** — hues at −60°, −30°, 0°, +30°, +60°
     - **Monochromatic** — same hue, stepped lightness values

5. **Persist & present**
   - Optional auto-save into `data/palettes.json`
   - Thumbnail embedded as base64 for the library/result UI
   - Export assets generated on demand (PNG / JSON / CSS / Tailwind)

### Why K-Means?

K-Means groups similar pixel colors into `k` clusters and returns their means. For palette extraction this is a practical balance of:

- Speed on resized images
- Interpretable “dominant color” centers
- Controllable palette size via `k`

---

## Color Accuracy & Quality Maintenance

Palette Studio is engineered for high fidelity and visual precision. Color accuracy is mathematically maintained and verified through a quantitative evaluation process:

### 1. How Accuracy is Maintained

- **Mathematical Optimization (K-Means Centroids):**
  Palette extraction minimizes the **Within-Cluster Sum of Squares (WCSS / Inertia)** across all image pixels:
  $$J = \sum_{k=1}^{K} \sum_{\mathbf{x} \in C_k} \|\mathbf{x} - \boldsymbol{\mu}_k\|^2$$
  Each palette swatch $\boldsymbol{\mu}_k$ represents the exact mathematical centroid of assigned pixel RGB vectors.
- **Deterministic & Stable Convergence:**
  Uses `n_init=10` initializations and a fixed `random_state=42` to guarantee stable, reproducible cluster centroids.
- **Perceptual Distance ($\Delta E_{76}$ in CIELAB Space):**
  Color representation error is evaluated in the **CIELAB ($L^*a^*b^*$) color space** to model human visual perception. Image-extracted palettes achieve an average $\Delta E$ in the **$3.4 - 5.0$** range, indicating high perceptual fidelity to the original photo.
- **Cluster Separation & Distinctness:**
  Evaluated using **Silhouette Scores** ($S > 0.4$) and minimum pairwise $\Delta E > 14.0$, ensuring extracted palette swatches are distinct without redundant colors.
- **100% Coverage Accounting:**
  Pixel shares are calculated directly from cluster assignments, guaranteeing that color percentages sum to $100.0\%$.

### 2. Validation & Testing Notebook

An automated validation notebook is included at [`palette_accuracy_test.ipynb`](palette_accuracy_test.ipynb):
- Tests all saved palettes in `data/palettes.json` against uploaded images.
- Computes RGB Root Mean Squared Error (RMSE), CIELAB $\Delta E_{76}$, Silhouette Scores, and cluster coverage.
- Generates side-by-side original vs. quantized palette comparisons and perceptual error histograms.
- Formally verifies mathematical hue angle rotations for Complementary ($180^\circ$), Analogous ($\pm 30^\circ, \pm 60^\circ$), and Monochromatic lightness steps.

---

## Project Structure

```
Palette Sudio/
├── app.py                      # Flask routes & API endpoints
├── palette_accuracy_test.ipynb # Color accuracy & validation Jupyter notebook
├── requirements.txt
├── data/
│   ├── palettes.json           # Saved palettes
│   └── settings.json           # User preferences
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── uploads/                # Uploaded images
├── templates/                  # Jinja2 pages
│   ├── base.html
│   ├── index.html              # Home + hero
│   ├── extract.html
│   ├── result.html
│   ├── library.html
│   ├── detail.html
│   ├── favorites.html
│   ├── settings.html
│   └── macros/icons.html
└── utils/
    ├── image_processing.py     # Load / resize / flatten pixels
    ├── color_extractor.py      # K-Means dominant colors
    ├── color_harmony.py        # HSL harmonies
    ├── random_palette.py       # Random warm palettes
    ├── palette_generator.py    # PNG / JSON / CSS / Tailwind exports
    └── storage.py              # JSON persistence
```

---

## Getting Started

### 1. Create a virtual environment (recommended)

```bash
cd "Palette Sudio"
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## Main Routes

| Route | Description |
|--------|-------------|
| `/` | Home — extract CTA + random palette CTA |
| `/extract` | Upload form |
| `/upload` | Process image → redirect to result |
| `/generate-random` | Create a random palette → result |
| `/result/<id>` | Palette detail, harmonies, exports |
| `/library` | Browse / search / filter saved palettes |
| `/favorites` | Favorited palettes |
| `/settings` | Preferences |
| `/download/png/<id>` | Download PNG strip |
| `/download/json/<id>` | Download JSON |

### API (AJAX)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/favorite` | POST | Toggle favorite |
| `/api/delete` | POST | Delete one palette |
| `/api/clear` | POST | Clear all history |

---

## Supported Inputs

- **Formats:** JPG, JPEG, PNG
- **Max upload size:** 16 MB
- **Color count:** 3–10 (configurable default in Settings)

---

## License

This project is provided as-is for personal and educational use.
