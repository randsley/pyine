"""Disk-based cache implementation using requests-cache."""

import logging
import os
from pathlib import Path
from typing import Any, Optional

import requests_cache
from platformdirs import user_cache_dir

from pyptine.cache.backend import CacheBackend
from pyptine.utils.exceptions import CacheError

logger = logging.getLogger(__name__)


class DiskCache(CacheBackend):
    """SQLite-based disk cache using requests-cache.

    Uses separate cache databases for metadata and data with different TTLs:
    - Metadata cache: 7 days (indicator metadata, dimensions, catalogue)
    - Data cache: 1 day (indicator data)

    Args:
        cache_dir: Directory for cache storage (None for default)
        metadata_ttl: Metadata cache TTL in seconds (default: 7 days)
        data_ttl: Data cache TTL in seconds (default: 1 day)

    Example:
        >>> cache = DiskCache()
        >>> cache.set("key", "value", ttl=3600)
        >>> value = cache.get("key")
    """

    DEFAULT_METADATA_TTL = 604800  # 7 days
    DEFAULT_DATA_TTL = 86400  # 1 day

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        metadata_ttl: int = DEFAULT_METADATA_TTL,
        data_ttl: int = DEFAULT_DATA_TTL,
    ) -> None:
        """Initialize disk cache."""
        # Determine cache directory
        cache_dir = Path(user_cache_dir("pyptine", "pyptine")) if cache_dir is None else Path(cache_dir)

        self.cache_dir = cache_dir
        self.metadata_ttl = metadata_ttl
        self.data_ttl = data_ttl

        # Create cache directory
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Using cache directory: {self.cache_dir}")
        except OSError as e:
            raise CacheError(f"Failed to create cache directory: {e}") from e

        # Create separate caches for metadata and data
        self.metadata_cache = self._create_session("metadata", expire_after=metadata_ttl)
        self.data_cache = self._create_session("data", expire_after=data_ttl)

    def _create_session(self, cache_name: str, expire_after: int) -> requests_cache.CachedSession:
        """Create a cached session.

        Args:
            cache_name: Name for the cache database
            expire_after: Cache expiration time in seconds

        Returns:
            Configured CachedSession
        """
        cache_path = self.cache_dir / cache_name

        return requests_cache.CachedSession(
            cache_name=str(cache_path),
            backend="sqlite",
            expire_after=expire_after,
            allowable_codes=[200],
            allowable_methods=["GET", "HEAD"],
            stale_if_error=True,
        )

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        # Not used - requests-cache handles caching transparently
        # This is here to satisfy the interface
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None for default)
        """
        # Not used - requests-cache handles caching transparently
        # This is here to satisfy the interface
        pass

    def delete(self, key: str) -> bool:
        """Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if key existed and was deleted
        """
        try:
            # Try to delete from both caches
            deleted = False

            if hasattr(self.metadata_cache.cache, "delete_url"):
                self.metadata_cache.cache.delete_url(key)
                deleted = True

            if hasattr(self.data_cache.cache, "delete_url"):
                self.data_cache.cache.delete_url(key)
                deleted = True

            return deleted
        except Exception as e:
            logger.warning(f"Failed to delete cache key {key}: {e}")
            return False

    def clear(self) -> None:
        """Clear all cached values."""
        try:
            self.metadata_cache.cache.clear()
            self.data_cache.cache.clear()
            logger.info("Cache cleared successfully")
        except Exception as e:
            raise CacheError(f"Failed to clear cache: {e}") from e

    def size(self) -> int:
        """Get number of cached items.

        Returns:
            Total number of items in both caches
        """
        try:
            metadata_count = len(self.metadata_cache.cache.responses)
            data_count = len(self.data_cache.cache.responses)
            return metadata_count + data_count
        except Exception as e:
            logger.warning(f"Failed to get cache size: {e}")
            return 0

    def get_cache_dir(self) -> Path:
        """Get cache directory path.

        Returns:
            Path to cache directory
        """
        return self.cache_dir

    def get_metadata_session(self) -> requests_cache.CachedSession:
        """Get metadata cache session.

        Returns:
            CachedSession for metadata
        """
        return self.metadata_cache

    def get_data_session(self) -> requests_cache.CachedSession:
        """Get data cache session.

        Returns:
            CachedSession for data
        """
        return self.data_cache

    def get_stats(self) -> dict:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        try:
            metadata_responses = len(self.metadata_cache.cache.responses)
            data_responses = len(self.data_cache.cache.responses)

            cache_dir_size = self._get_directory_size(self.cache_dir)

            return {
                "cache_dir": str(self.cache_dir),
                "metadata_entries": metadata_responses,
                "data_entries": data_responses,
                "total_entries": metadata_responses + data_responses,
                "cache_size_bytes": cache_dir_size,
                "cache_size_mb": round(cache_dir_size / (1024 * 1024), 2),
                "metadata_ttl_seconds": self.metadata_ttl,
                "data_ttl_seconds": self.data_ttl,
            }
        except Exception as e:
            logger.warning(f"Failed to get cache stats: {e}")
            return {"error": str(e)}

    def _get_directory_size(self, path: Path) -> int:
        """Get total size of directory in bytes.

        Args:
            path: Directory path

        Returns:
            Total size in bytes
        """
        total = 0
        try:
            for entry in os.scandir(path):
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += self._get_directory_size(Path(entry.path))
        except Exception as e:
            logger.debug(f"Error calculating directory size: {e}")
        return total

    def close(self) -> None:
        """Close cache sessions and cleanup."""
        try:
            self.metadata_cache.close()
            self.data_cache.close()
            logger.debug("Cache sessions closed")
        except Exception as e:
            logger.warning(f"Error closing cache sessions: {e}")
