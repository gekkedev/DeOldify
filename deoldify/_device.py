"""Runtime device selection utilities.

This module provides a small wrapper that automatically selects an appropriate
torch device. CUDA is preferred when available, otherwise a DirectML device is
used if the ``torch_directml`` package can be imported. If neither backend is
available the code falls back to CPU.  The helper is intentionally lightweight
so it can be imported early in the application lifecycle.
"""

from __future__ import annotations

import logging
from typing import Optional

import torch

from .device_id import DeviceId


class DeviceException(Exception):
    """Raised when a requested device backend cannot be initialized."""


class _Device:
    """Simple wrapper that tracks the active compute device.

    The instance selects a backend on creation and exposes convenience helpers
    to query and change it later.  ``set`` may be used to manually switch CUDA
    GPUs using the legacy :class:`~deoldify.device_id.DeviceId` enum, otherwise
    the best available backend is chosen automatically.
    """

    def __init__(self) -> None:
        self._backend: str = "cpu"
        self._torch_device: torch.device = torch.device("cpu")
        # Auto-select a device during initialization so callers don't need to.
        self.set()
        print(f"Using backend: {self.backend()}")

    # Public API ---------------------------------------------------------
    def is_gpu(self) -> bool:
        """Return ``True`` if a GPU backend is active."""

        return self._backend in {"cuda", "directml"}

    def backend(self) -> str:
        """Return the name of the active backend (``cuda``, ``directml`` or ``cpu``)."""

        return self._backend

    def torch_device(self) -> torch.device:
        """Return the underlying :class:`torch.device` instance."""

        return self._torch_device

    def set(self, device: Optional[DeviceId] = None) -> torch.device:
        """Select a compute backend.

        Passing a :class:`DeviceId` forces a specific CUDA GPU or CPU.  When no
        argument is supplied the best available backend is chosen
        automatically.
        """

        if device is not None:
            if device == DeviceId.CPU:
                self._backend = "cpu"
                self._torch_device = torch.device("cpu")
                logging.info("Using CPU")
                return self._torch_device

            if not torch.cuda.is_available():
                raise DeviceException("CUDA is not available")

            torch.cuda.set_device(device.value)
            torch.backends.cudnn.benchmark = False
            self._backend = "cuda"
            self._torch_device = torch.device("cuda", device.value)
            logging.info("Using CUDA device %s", device.value)
            return self._torch_device

        # Auto-detect best available backend
        if torch.cuda.is_available():
            self._backend = "cuda"
            self._torch_device = torch.device("cuda")
            logging.info("Using CUDA device")
        else:
            try:
                import torch_directml  # type: ignore

                self._backend = "directml"
                self._torch_device = torch_directml.device()
                logging.info("Using DirectML device")
            except Exception:
                self._backend = "cpu"
                self._torch_device = torch.device("cpu")
                logging.info("Falling back to CPU")

        return self._torch_device


# The module-level ``device`` instance lives in :mod:`deoldify.__init__` where it
# can be imported as ``from deoldify import device``.  Having a central instance
# avoids scattering device detection logic across the codebase.
