"""
image_loader.py
---------------
Handles loading, validating, and preprocessing images
before they are sent to the extraction engine.
"""

import os
import base64
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
from rich.console import Console

console = Console()

SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}


def load_images_from_folder(folder_path: str) -> list[dict]:
    """
    Scans a folder and loads all supported image files.

    Returns a list of dicts:
        [{ "filename": "card1.jpg", "path": "/full/path/card1.jpg" }, ...]
    """
    folder = Path(folder_path)

    if not folder.exists():
        console.print(f"[red]❌ Folder not found:[/red] {folder_path}")
        return []

    images = []
    for file in sorted(folder.iterdir()):
        if file.suffix.lower() in SUPPORTED_FORMATS:
            images.append({
                "filename": file.name,
                "path": str(file.resolve())
            })

    if not images:
        console.print(f"[yellow]⚠️  No supported images found in:[/yellow] {folder_path}")
    else:
        console.print(f"[green]✅ Found {len(images)} image(s) in:[/green] {folder_path}")

    return images


def load_single_image(image_path: str) -> dict | None:
    """
    Loads a single image file.

    Returns a dict: { "filename": "card1.jpg", "path": "/full/path/card1.jpg" }
    """
    path = Path(image_path)

    if not path.exists():
        console.print(f"[red]❌ Image not found:[/red] {image_path}")
        return None

    if path.suffix.lower() not in SUPPORTED_FORMATS:
        console.print(f"[red]❌ Unsupported format:[/red] {path.suffix}. Supported: {SUPPORTED_FORMATS}")
        return None

    console.print(f"[green]✅ Loaded image:[/green] {path.name}")
    return {"filename": path.name, "path": str(path.resolve())}


def preprocess_image(image_path: str, save_debug: bool = False) -> str:
    """
    Preprocesses an image for better extraction accuracy:
      - Converts to RGB
      - Auto-rotates if needed
      - Sharpens and enhances contrast
      - Denoises
      - Resizes if too small

    Returns the preprocessed image as a base64 string (JPEG).
    """
    # --- Load with OpenCV for preprocessing ---
    img_cv = cv2.imread(image_path)

    if img_cv is None:
        console.print(f"[red]❌ Could not read image:[/red] {image_path}")
        return ""

    # Convert BGR (OpenCV default) → RGB
    img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)

    # Denoise
    img_cv = cv2.fastNlMeansDenoisingColored(img_cv, None, 10, 10, 7, 21)

    # Convert to PIL for enhancement
    pil_img = Image.fromarray(img_cv)

    # Auto-rotate based on EXIF data (handles phone photos)
    pil_img = _fix_rotation(pil_img)

    # Resize if image is too small (min 800px wide for readability)
    if pil_img.width < 800:
        scale = 800 / pil_img.width
        new_size = (800, int(pil_img.height * scale))
        pil_img = pil_img.resize(new_size, Image.LANCZOS)

    # Enhance sharpness
    pil_img = ImageEnhance.Sharpness(pil_img).enhance(2.0)

    # Enhance contrast slightly
    pil_img = ImageEnhance.Contrast(pil_img).enhance(1.3)

    if save_debug:
        debug_path = image_path.replace(".", "_debug.")
        pil_img.save(debug_path)
        console.print(f"[dim]💾 Debug image saved:[/dim] {debug_path}")

    # Convert to base64 JPEG
    import io
    buffer = io.BytesIO()
    pil_img.save(buffer, format="JPEG", quality=90)
    base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return base64_image


def _fix_rotation(pil_img: Image.Image) -> Image.Image:
    """Fixes image rotation based on EXIF orientation tag."""
    try:
        exif = pil_img._getexif()
        if exif:
            orientation = exif.get(274)  # 274 = Orientation tag
            rotations = {3: 180, 6: 270, 8: 90}
            if orientation in rotations:
                pil_img = pil_img.rotate(rotations[orientation], expand=True)
    except Exception:
        pass  # No EXIF data — skip rotation fix
    return pil_img
