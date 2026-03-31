"""FlashShot -- Python SDK for the FlashShot Screenshot API."""

from .client import FlashShot
from .exceptions import FlashShotError

__all__ = ["FlashShot", "FlashShotError"]
__version__ = "1.0.0"
