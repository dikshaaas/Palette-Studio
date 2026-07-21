"""
storage.py
----------
JSON file-backed persistent storage for Palette Studio.
Manages palettes history, folder categorization, favoriting, deletion, and user settings.
"""

import os
import json
from datetime import datetime

DATA_DIR      = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
PALETTES_FILE = os.path.join(DATA_DIR, "palettes.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

DEFAULT_FOLDERS = [
    "Personal Inspiration",
    "Sunset",
    "Game UI",
    "Corporate",
    "Coffee Shop",
    "Nature"
]

DEFAULT_SETTINGS = {
    "n_colors_default": 6,
    "auto_save": True,
    "dark_mode": False
}


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(PALETTES_FILE):
        with open(PALETTES_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=2)


def get_folders() -> list[str]:
    return DEFAULT_FOLDERS


def load_settings() -> dict:
    _ensure_data_dir()
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict):
    _ensure_data_dir()
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def get_all_palettes() -> list[dict]:
    _ensure_data_dir()
    try:
        with open(PALETTES_FILE, "r", encoding="utf-8") as f:
            palettes = json.load(f)
            # Ensure folder field exists
            for p in palettes:
                if "folder" not in p or not p["folder"]:
                    p["folder"] = "Personal Inspiration"
            return palettes
    except Exception:
        return []


def save_palette(palette_data: dict) -> dict:
    """
    Save a new palette to persistent JSON storage.
    """
    _ensure_data_dir()
    palettes = get_all_palettes()
    
    if "date" not in palette_data:
        palette_data["date"] = datetime.now().strftime("%b %d, %Y")
    if "created_at" not in palette_data:
        palette_data["created_at"] = datetime.now().isoformat()
    if "is_favorite" not in palette_data:
        palette_data["is_favorite"] = False
    if "folder" not in palette_data or not palette_data["folder"]:
        palette_data["folder"] = "Personal Inspiration"

    palettes.insert(0, palette_data)

    with open(PALETTES_FILE, "w", encoding="utf-8") as f:
        json.dump(palettes, f, indent=2)

    return palette_data


def get_palette_by_id(palette_id: str) -> dict | None:
    palettes = get_all_palettes()
    for p in palettes:
        if p["id"] == palette_id:
            return p
    return None


def toggle_favorite(palette_id: str) -> bool:
    _ensure_data_dir()
    palettes = get_all_palettes()
    new_state = False
    for p in palettes:
        if p["id"] == palette_id:
            p["is_favorite"] = not p.get("is_favorite", False)
            new_state = p["is_favorite"]
            break
            
    with open(PALETTES_FILE, "w", encoding="utf-8") as f:
        json.dump(palettes, f, indent=2)
        
    return new_state


def delete_palette(palette_id: str) -> bool:
    _ensure_data_dir()
    palettes = get_all_palettes()
    initial_len = len(palettes)
    palettes = [p for p in palettes if p["id"] != palette_id]
    
    with open(PALETTES_FILE, "w", encoding="utf-8") as f:
        json.dump(palettes, f, indent=2)
        
    return len(palettes) < initial_len


def clear_all_palettes():
    _ensure_data_dir()
    with open(PALETTES_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)
