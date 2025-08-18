"""Helpers for estimating render parameters."""
from __future__ import annotations

from PIL import Image

# Inspect a single frame to estimate a good render_factor
def guess_render_factor(image_path: str) -> int:
    try:
        with Image.open(image_path) as img:
            width, height = img.size
    except FileNotFoundError:
        print(f"File not found: {image_path}. Using default render_factor.")
        return 21

    # The smaller side determines how much detail the model can leverage.
    smaller_side = min(width, height)
    factor = smaller_side // 32

    # Clamp to values that are known to work well with DeOldify.
    factor = max(8, min(factor, 26))

    # differentiate by image aspect ratio
    if width / height > 1.5:
        # Portraits often look better with lower factors to reduce skin glitches.
        factor = max(8, min(factor, 18))
        print(f"Portrait detected")
    else:
        # Non-portraits can use slightly higher factors for richer detail.
        factor = max(factor, 12)
        print(f"Landscape detected")

    return int(factor)
