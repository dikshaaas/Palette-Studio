"""
app.py — Palette Studio
-----------------------
Flask application entry point with top navbar layout, folders support,
library filtering, and custom color harmonies.
"""

import os
import uuid
import json
from io import BytesIO
from datetime import datetime

from flask import (
    Flask, render_template, request,
    redirect, url_for, send_file, jsonify
)

from utils.image_processing import load_and_preprocess, load_thumbnail
from utils.color_extractor   import extract_colors
from utils.color_harmony     import generate_harmonies
from utils.palette_generator import (
    generate_palette_png, generate_palette_json,
    generate_css_variables, generate_tailwind_config
)
from utils.random_palette import build_random_palette_record
from utils.storage import (
    get_all_palettes, get_palette_by_id, save_palette,
    toggle_favorite, delete_palette, clear_all_palettes,
    load_settings, save_settings, get_folders
)

# ── App setup ─────────────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "palette-studio-human-2024")

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def image_to_b64(img) -> str:
    import base64
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode()


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    settings = load_settings()
    all_palettes = get_all_palettes()
    recent = all_palettes[:6]
    folders = get_folders()
    return render_template("index.html", recent_palettes=recent, folders=folders, settings=settings, active_page="home")


@app.route("/extract")
def extract():
    settings = load_settings()
    folders = get_folders()
    return render_template("extract.html", folders=folders, settings=settings, active_page="extract")


@app.route("/generate-random", methods=["GET", "POST"])
def generate_random():
    """Create a soothing random palette and open it like an extracted result."""
    settings = load_settings()
    try:
        n_colors = int(request.args.get("n", settings.get("n_colors_default", 5)))
        n_colors = max(3, min(8, n_colors))
    except (ValueError, TypeError):
        n_colors = 5

    built = build_random_palette_record(n_colors=n_colors)
    file_id = uuid.uuid4().hex
    thumb_b64 = image_to_b64(built["thumb"])

    palette_record = {
        "id":          file_id,
        "filename":    "Random Harmony",
        "saved_file":  None,
        "thumb_b64":   thumb_b64,
        "orig_size":   built["orig_size"],
        "n_colors":    n_colors,
        "folder":      "Personal Inspiration",
        "colors":      built["colors"],
        "harmonies":   built["harmonies"],
        "date":        datetime.now().strftime("%b %d, %Y"),
        "created_at":  datetime.now().isoformat(),
        "is_favorite": False,
        "is_random":   True,
    }

    save_palette(palette_record)
    return redirect(url_for("result", palette_id=file_id))


@app.route("/upload", methods=["POST"])
def upload():
    settings = load_settings()
    folders = get_folders()

    if "image" not in request.files:
        return render_template("extract.html", error="Please choose an image to extract colors.", folders=folders, settings=settings, active_page="extract")

    file = request.files["image"]
    if file.filename == "":
        return render_template("extract.html", error="No image selected.", folders=folders, settings=settings, active_page="extract")

    if not allowed_file(file.filename):
        return render_template("extract.html", error="Only JPG, JPEG, and PNG images are supported.", folders=folders, settings=settings, active_page="extract")

    ext      = file.filename.rsplit(".", 1)[1].lower()
    file_id  = uuid.uuid4().hex
    filename = f"{file_id}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        n_colors = int(request.form.get("n_colors", settings.get("n_colors_default", 6)))
        n_colors = max(3, min(10, n_colors))
    except (ValueError, TypeError):
        n_colors = settings.get("n_colors_default", 6)

    selected_folder = request.form.get("folder", "Personal Inspiration").strip()

    try:
        pixels, orig_size = load_and_preprocess(filepath, max_size=500)
        colors    = extract_colors(pixels, n_colors=n_colors)
        harmonies = generate_harmonies(colors[0]["rgb"]) if colors else {}
        thumb     = load_thumbnail(filepath)
        thumb_b64 = image_to_b64(thumb)
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return render_template("extract.html", error=f"Could not process image: {e}", folders=folders, settings=settings, active_page="extract")

    palette_record = {
        "id":          file_id,
        "filename":    file.filename,
        "saved_file":  filename,
        "thumb_b64":   thumb_b64,
        "orig_size":   orig_size,
        "n_colors":    n_colors,
        "folder":      selected_folder,
        "colors":      colors,
        "harmonies":   harmonies,
        "date":        datetime.now().strftime("%b %d, %Y"),
        "created_at":  datetime.now().isoformat(),
        "is_favorite": False
    }

    if settings.get("auto_save", True):
        save_palette(palette_record)

    return redirect(url_for("result", palette_id=file_id))


@app.route("/result/<palette_id>")
def result(palette_id: str):
    palette = get_palette_by_id(palette_id)
    if not palette:
        return redirect(url_for("home"))

    css_vars  = generate_css_variables(palette["colors"])
    tailwind  = generate_tailwind_config(palette["colors"])
    settings  = load_settings()
    folders   = get_folders()

    return render_template(
        "result.html",
        palette=palette,
        css_vars=css_vars,
        tailwind=tailwind,
        folders=folders,
        settings=settings,
        active_page="result"
    )


@app.route("/library")
def library():
    palettes = get_all_palettes()
    settings = load_settings()
    folders  = get_folders()
    
    q = request.args.get("q", "").strip().lower()
    selected_folder = request.args.get("folder", "").strip()
    sort = request.args.get("sort", "newest")
    fav_only = request.args.get("favorites", "false") == "true"

    if q:
        palettes = [p for p in palettes if q in p["filename"].lower() or any(q in c["name"].lower() or q in c["hex"].lower() for c in p["colors"])]

    if selected_folder:
        palettes = [p for p in palettes if p.get("folder", "") == selected_folder]

    if fav_only:
        palettes = [p for p in palettes if p.get("is_favorite", False)]

    if sort == "oldest":
        palettes = sorted(palettes, key=lambda x: x.get("created_at", ""))
    else:
        palettes = sorted(palettes, key=lambda x: x.get("created_at", ""), reverse=True)

    return render_template(
        "library.html",
        palettes=palettes,
        folders=folders,
        query=q,
        selected_folder=selected_folder,
        sort=sort,
        fav_only=fav_only,
        settings=settings,
        active_page="library"
    )


@app.route("/library/<palette_id>")
def palette_detail(palette_id: str):
    palette = get_palette_by_id(palette_id)
    if not palette:
        return redirect(url_for("library"))
        
    css_vars = generate_css_variables(palette["colors"])
    tailwind = generate_tailwind_config(palette["colors"])
    settings = load_settings()
    folders  = get_folders()

    return render_template(
        "detail.html",
        palette=palette,
        css_vars=css_vars,
        tailwind=tailwind,
        folders=folders,
        settings=settings,
        active_page="library"
    )


@app.route("/favorites")
def favorites():
    palettes = [p for p in get_all_palettes() if p.get("is_favorite", False)]
    settings = load_settings()
    folders  = get_folders()
    return render_template("favorites.html", palettes=palettes, folders=folders, settings=settings, active_page="favorites")


@app.route("/settings", methods=["GET", "POST"])
def settings():
    current_settings = load_settings()
    folders = get_folders()
    if request.method == "POST":
        n_colors_default = int(request.form.get("n_colors_default", 6))
        auto_save = "auto_save" in request.form
        dark_mode = "dark_mode" in request.form

        current_settings.update({
            "n_colors_default": max(3, min(10, n_colors_default)),
            "auto_save": auto_save,
            "dark_mode": dark_mode
        })
        save_settings(current_settings)
        return render_template("settings.html", settings=current_settings, folders=folders, success="Preferences saved successfully!", active_page="settings")

    return render_template("settings.html", settings=current_settings, folders=folders, active_page="settings")


# ── AJAX API Endpoints ───────────────────────────────────────────────────────

@app.route("/api/favorite", methods=["POST"])
def api_favorite():
    data = request.get_json() or {}
    palette_id = data.get("id")
    if not palette_id:
        return jsonify({"error": "Missing id"}), 400
        
    new_state = toggle_favorite(palette_id)
    return jsonify({"success": True, "is_favorite": new_state})


@app.route("/api/delete", methods=["POST"])
def api_delete():
    data = request.get_json() or {}
    palette_id = data.get("id")
    if not palette_id:
        return jsonify({"error": "Missing id"}), 400
        
    success = delete_palette(palette_id)
    return jsonify({"success": success})


@app.route("/api/clear", methods=["POST"])
def api_clear():
    clear_all_palettes()
    return jsonify({"success": True})


@app.route("/download/png/<palette_id>")
def download_png(palette_id: str):
    palette = get_palette_by_id(palette_id)
    if not palette:
        return "Not found", 404

    png_bytes = generate_palette_png(palette["colors"])
    buf = BytesIO(png_bytes)
    buf.seek(0)
    return send_file(
        buf,
        mimetype="image/png",
        as_attachment=True,
        download_name=f"palette-{palette_id[:8]}.png",
    )


@app.route("/download/json/<palette_id>")
def download_json(palette_id: str):
    palette = get_palette_by_id(palette_id)
    if not palette:
        return "Not found", 404

    json_str = generate_palette_json(palette["colors"], palette.get("harmonies"))
    buf = BytesIO(json_str.encode())
    buf.seek(0)
    return send_file(
        buf,
        mimetype="application/json",
        as_attachment=True,
        download_name=f"palette-{palette_id[:8]}.json",
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
