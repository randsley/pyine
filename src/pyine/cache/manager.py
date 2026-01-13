"""Cache management utilities."""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from pyine.cache.disk import DiskCache

logger = logging.getLogger(__name__)


class CacheManager:
    """Cache manager for convenient cache operations.

    Provides high-level methods for cache management without
    needing to interact with the cache directly.

    Example:
        >>> manager = CacheManager()
        >>> stats = manager.get_stats()
        >>> print(f"Cache has {stats['total_entries']} entries")
        >>> manager.clear()
    """

    def __init__(self, cache_dir: Optional[Path] = None) -> None:
        """Initialize cache manager.

        Args:
            cache_dir: Cache directory (None for default)
        """
        self.cache = DiskCache(cache_dir=cache_dir)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics including:
            - cache_dir: Cache directory path
            - metadata_entries: Number of metadata cache entries
            - data_entries: Number of data cache entries
            - total_entries: Total cache entries
            - cache_size_bytes: Total cache size in bytes
            - cache_size_mb: Total cache size in megabytes
            - metadata_ttl_seconds: Metadata cache TTL
            - data_ttl_seconds: Data cache TTL

        Example:
            >>> manager = CacheManager()
            >>> stats = manager.get_stats()
            >>> print(f"Cache location: {stats['cache_dir']}")
            >>> print(f"Total entries: {stats['total_entries']}")
            >>> print(f"Cache size: {stats['cache_size_mb']} MB")
        """
        return self.cache.get_stats()

    def clear(self) -> None:
        """Clear all cached data.

        Example:
            >>> manager = CacheManager()
            >>> manager.clear()
        """
        logger.info("Clearing cache...")
        self.cache.clear()
        logger.info("Cache cleared successfully")

    def get_cache_dir(self) -> Path:
        """Get cache directory path.

        Returns:
            Path to cache directory

        Example:
            >>> manager = CacheManager()
            >>> print(manager.get_cache_dir())
        """
        return self.cache.get_cache_dir()

    def format_stats(self) -> str:
        """Format cache statistics as human-readable string.

        Returns:
            Formatted statistics string

        Example:
            >>> manager = CacheManager()
            >>> print(manager.format_stats())
        """
        stats = self.get_stats()

        if "error" in stats:
            return f"Error getting cache stats: {stats['error']}"

        lines = [
            "Cache Statistics",
            "=" * 50,
            f"Location: {stats['cache_dir']}",
            "",
            "Entries:",
            f"  Metadata: {stats['metadata_entries']}",
            f"  Data:     {stats['data_entries']}",
            f"  Total:    {stats['total_entries']}",
            "",
            f"Size: {stats['cache_size_mb']} MB ({stats['cache_size_bytes']} bytes)",
            "",
            "TTL Settings:",
            f"  Metadata: {stats['metadata_ttl_seconds']} seconds ({stats['metadata_ttl_seconds'] // 86400} days)",
            f"  Data:     {stats['data_ttl_seconds']} seconds ({stats['data_ttl_seconds'] // 86400} days)",
        ]

        return "\n".join(lines)

    def close(self) -> None:
        """Close cache sessions.

        Example:
            >>> manager = CacheManager()
            >>> # ... use cache ...
            >>> manager.close()
        """
        self.cache.close()

    def __enter__(self) -> "CacheManager":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
