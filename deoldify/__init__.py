import sys
import logging

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logging.getLogger().setLevel(logging.INFO)

from deoldify._device import _Device

# Expose a shared device wrapper for convenience across the library.
device = _Device()
