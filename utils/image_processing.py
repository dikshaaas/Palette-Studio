"""
image_processing.py
-------------------
Handles reading an image file, converting it to RGB, and flattening
it into a 2D NumPy array of pixel values ready for K-Means clustering.
"""

import cv2
import numpy as np
from PIL import Image


def load_and_preprocess(image_path: str, max_size: int = 500) -> tuple[np.ndarray, tuple[int, int]]:
    """
    Load an image, resize (preserving aspect ratio), convert to RGB,
    and return the pixel array plus original dimensions.

    Args:
        image_path: Absolute path to the uploaded image file.
        max_size:   Maximum side length for resizing (default 500px).

    Returns:
        pixels:     NumPy array of shape (N, 3) where N = width * height.
        orig_size:  (original_width, original_height) tuple.
    """
    # Read with OpenCV (returns BGR)
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        raise ValueError(f"Could not read image at: {image_path}")

    orig_h, orig_w = img_bgr.shape[:2]

    # Convert BGR → RGB
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    # Resize preserving aspect ratio so the longest side ≤ max_size
    scale = min(max_size / orig_w, max_size / orig_h, 1.0)  # never upscale
    new_w = max(1, int(orig_w * scale))
    new_h = max(1, int(orig_h * scale))

    img_resized = cv2.resize(img_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Flatten to (N, 3) — each row is one [R, G, B] pixel
    pixels = img_resized.reshape(-1, 3).astype(np.float32)

    return pixels, (orig_w, orig_h)


def load_thumbnail(image_path: str, size: tuple[int, int] = (400, 400)) -> Image.Image:
    """
    Return a PIL Image thumbnail for embedding in the result page.
    """
    img = Image.open(image_path).convert("RGB")
    img.thumbnail(size, Image.LANCZOS)
    return img
