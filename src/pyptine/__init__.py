"""pyptine - Python client for INE Portugal (Statistics Portugal) API."""

from pyptine.__version__ import __version__
from pyptine.async_ine import AsyncINE
from pyptine.ine import INE

__all__ = ["__version__", "AsyncINE", "INE"]
