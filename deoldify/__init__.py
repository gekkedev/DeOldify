import sys
import logging

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logging.getLogger().setLevel(logging.INFO)

from deoldify._device import _Device
from .render_factor import guess_render_factor

# Expose a shared device wrapper for convenience across the library.
device = _Device()

# Re-export common utilities for easy access.
__all__ = ["device", "guess_render_factor"]
