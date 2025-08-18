"""Helpers for estimating render parameters."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import Iterable

from PIL import Image


def _is_video(path: Path, video_exts: Iterable[str]) -> bool:
    """Return ``True`` if *path* looks like a video file."""

    return path.suffix.lower() in video_exts


def guess_render_factor(media_path: str, subject_type: str = "portrait") -> int:
    """Heuristically guess a render factor for an image or video.

    If a video path is provided, the first frame is extracted using ``ffmpeg`` and
    analysed to determine the render factor. This keeps callers from having to
    manually handle temporary frame extraction.

    Parameters
    ----------
    media_path: str
        Path to an image or video file on disk.
    subject_type: str, optional
        Either ``"portrait"`` (default) or ``"landscape"``/``"detail"``. Portraits
        generally benefit from slightly lower ``render_factor`` values to avoid
        skin artifacts, whereas other scenes can render at higher values for more
        detail.

    Returns
    -------
    int
        A suggested ``render_factor`` value within a sensible range. Falls back to
        ``21`` if a video frame cannot be extracted.
    """

    path = Path(media_path)
    video_extensions = {".mp4", ".mov", ".avi", ".mkv"}

    frame_path = None
    created_temp_frame = False

    if _is_video(path, video_extensions):
        # Prefer any pre-extracted frame rather than guessing a specific name.
        existing_frames = sorted(path.parent.glob(f"{path.stem}_*.jpg"))
        if existing_frames:
            frame_path = existing_frames[0]
        else:
            # Extract a single frame using ffmpeg. Swallow errors to keep the
            # caller running even if ffmpeg is missing.
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                frame_path = Path(tmp.name)
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                str(path),
                "-frames:v",
                "1",
                str(frame_path),
            ]
            try:
                subprocess.run(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
                )
                created_temp_frame = True
            except (FileNotFoundError, subprocess.CalledProcessError):
                frame_path.unlink(missing_ok=True)
                return 21

    # If we didn't detect a video, treat the given path as an image.
    image_path = frame_path if frame_path is not None else path

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

    if created_temp_frame:
        # Clean up the temporary frame we extracted earlier.
        frame_path.unlink(missing_ok=True)

    return int(factor)
