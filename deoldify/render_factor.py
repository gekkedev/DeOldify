"""Helpers for estimating render parameters."""
from __future__ import annotations

from PIL import Image


def guess_render_factor(image_path: str, subject_type: str = "portrait") -> int:
    """Heuristically guess a render factor for an image.

    Parameters
    ----------
    image_path: str
        Path to the image file on disk.
    subject_type: str, optional
        Either ``"portrait"`` (default) or ``"landscape"``/``"detail"``. Portraits
        generally benefit from slightly lower ``render_factor`` values to avoid
        skin artifacts, whereas other scenes can render at higher values for more
        detail.

    Returns
    -------
    int
        A suggested ``render_factor`` value within a sensible range.
    """

    with Image.open(image_path) as img:
        width, height = img.size

    # The smaller side determines how much detail the model can leverage.
    smaller_side = min(width, height)
    factor = smaller_side // 32

    # Clamp to values that are known to work well with DeOldify.
    factor = max(8, min(factor, 26))

    if subject_type.lower() == "portrait":
        # Portraits often look better with lower factors to reduce skin glitches.
        factor = max(8, min(factor, 18))
    else:
        # Non-portraits can use slightly higher factors for richer detail.
        factor = max(factor, 12)

    return int(factor)
