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

## Random Palette Generation

`utils/random_palette.py` builds cohesive palettes without an upload:

- Picks a warm mood seed (sunset, blush, lavender, sand, peach, dusk)
- Spreads hues in a gentle analogous range (occasionally a complementary accent)
- Keeps saturation soft and lightness elegant
- Creates a strip thumbnail and the same harmony set as extracted palettes

---

## Project Structure

```
Palette Sudio/
├── app.py                      # Flask routes & API endpoints
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
