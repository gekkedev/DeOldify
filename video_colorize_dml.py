"""Prototype video colorization on DirectML devices.

This script demonstrates running DeOldify's video colorizer on the DirectML
backend provided by the ``torch-directml`` package. It targets Windows machines
with Intel GPUs, but any DirectML-capable device should work. The script mirrors
``VideoColorizer.py`` while relying on the new automatic device wrapper.
"""

from __future__ import annotations

import os
import warnings

from deoldify import device
from deoldify.visualize import get_video_colorizer


def main() -> None:
    """Entry point for DirectML video colorization."""

    # Import ``torch_directml`` lazily so that the module still parses even when
    # the dependency isn't installed. A clearer error is raised at runtime.
    try:
        import torch_directml  # type: ignore  # noqa: F401
    except ImportError as err:
        raise RuntimeError("torch-directml is required to run this script") from err

    print(f"Using backend: {device.backend()}")

    warnings.filterwarnings(
        "ignore", category=UserWarning, message=".*?Your .*? set is empty.*?"
    )

    print("Loading video colorizer...")
    colorizer = get_video_colorizer()
    print("Video colorizer loaded.")

    render_factor = 21
    source_url = None
    folder_path = "video/source"

    # Iterate over videos in the source folder and colorize each one.
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if not os.path.isfile(file_path):
            continue
        print(f"Processing: {file_name}")
        if source_url is None:
            result_path = colorizer.colorize_from_file_name(
                file_name, render_factor=render_factor
            )
        else:
            result_path = colorizer.colorize_from_url(
                source_url, file_name, render_factor=render_factor
            )
        print(f"Saved: {result_path}")


if __name__ == "__main__":  # pragma: no cover - simple script
    main()
