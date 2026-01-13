"""Tests for DiskCache."""

import pytest
import responses

from pyine.cache.disk import DiskCache


@pytest.fixture
def disk_cache(temp_cache_dir):
    """Create DiskCache instance."""
    cache = DiskCache(cache_dir=temp_cache_dir)
    yield cache
    cache.close()


class TestDiskCache:
    """Tests for DiskCache."""

    def test_initialization(self, disk_cache, temp_cache_dir):
        """Test cache initialization."""
        assert disk_cache.cache_dir == temp_cache_dir
        assert disk_cache.cache_dir.exists()
        assert disk_cache.metadata_ttl == DiskCache.DEFAULT_METADATA_TTL
        assert disk_cache.data_ttl == DiskCache.DEFAULT_DATA_TTL

    def test_initialization_with_custom_ttl(self, temp_cache_dir):
        """Test cache initialization with custom TTL."""
        cache = DiskCache(cache_dir=temp_cache_dir, metadata_ttl=3600, data_ttl=1800)

        assert cache.metadata_ttl == 3600
        assert cache.data_ttl == 1800

        cache.close()

    def test_get_cache_dir(self, disk_cache, temp_cache_dir):
        """Test getting cache directory."""
        assert disk_cache.get_cache_dir() == temp_cache_dir

    def test_default_cache_dir(self):
        """Test default cache directory creation."""
        cache = DiskCache()

        cache_dir = cache.get_cache_dir()
        assert cache_dir.exists()
        assert "pyine" in str(cache_dir).lower()

        cache.close()

    @responses.activate
    def test_metadata_session_caching(self, disk_cache):
        """Test metadata session caches responses."""
        # Add mock response
        responses.add(
            responses.GET,
            "https://test.com/metadata",
            json={"result": "metadata"},
            status=200,
        )

        session = disk_cache.get_metadata_session()

        # First request - should hit API
        response1 = session.get("https://test.com/metadata")
        assert response1.status_code == 200
        assert not getattr(response1, "from_cache", False)

        # Second request - should hit cache
        response2 = session.get("https://test.com/metadata")
        assert response2.status_code == 200
        assert getattr(response2, "from_cache", False)

    @responses.activate
    def test_data_session_caching(self, disk_cache):
        """Test data session caches responses."""
        responses.add(
            responses.GET,
            "https://test.com/data",
            json={"result": "data"},
            status=200,
        )

        session = disk_cache.get_data_session()

        # First request
        response1 = session.get("https://test.com/data")
        assert not getattr(response1, "from_cache", False)

        # Second request - from cache
        response2 = session.get("https://test.com/data")
        assert getattr(response2, "from_cache", False)

    def test_clear_cache(self, disk_cache):
        """Test clearing cache."""
        # Cache should start empty or with some entries
        initial_size = disk_cache.size()

        # Add some cached data by making requests
        session = disk_cache.get_metadata_session()

        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, "https://test.com/test", json={}, status=200)
            session.get("https://test.com/test")

        # Size should increase
        assert disk_cache.size() >= initial_size

        # Clear cache
        disk_cache.clear()

        # Size should be 0
        assert disk_cache.size() == 0

    def test_get_stats(self, disk_cache):
        """Test getting cache statistics."""
        stats = disk_cache.get_stats()

        assert "cache_dir" in stats
        assert "metadata_entries" in stats
        assert "data_entries" in stats
        assert "total_entries" in stats
        assert "cache_size_bytes" in stats
        assert "cache_size_mb" in stats
        assert "metadata_ttl_seconds" in stats
        assert "data_ttl_seconds" in stats

        assert stats["metadata_ttl_seconds"] == disk_cache.metadata_ttl
        assert stats["data_ttl_seconds"] == disk_cache.data_ttl

    @responses.activate
    def test_separate_caches_for_metadata_and_data(self, disk_cache):
        """Test that metadata and data use separate caches."""
        # Add responses
        responses.add(
            responses.GET,
            "https://test.com/metadata",
            json={"type": "metadata"},
            status=200,
        )
        responses.add(
            responses.GET,
            "https://test.com/data",
            json={"type": "data"},
            status=200,
        )

        # Request metadata
        metadata_session = disk_cache.get_metadata_session()
        metadata_session.get("https://test.com/metadata")

        # Request data
        data_session = disk_cache.get_data_session()
        data_session.get("https://test.com/data")

        # Check stats show entries in both caches
        stats = disk_cache.get_stats()
        assert stats["metadata_entries"] > 0
        assert stats["data_entries"] > 0

    def test_close(self, temp_cache_dir):
        """Test closing cache sessions."""
        cache = DiskCache(cache_dir=temp_cache_dir)

        # Should not raise errors
        cache.close()

        # Can close multiple times
        cache.close()

    def test_size_with_multiple_entries(self, disk_cache):
        """Test size calculation with multiple entries."""
        with responses.RequestsMock() as rsps:
            # Add multiple URLs
            for i in range(5):
                rsps.add(
                    responses.GET,
                    f"https://test.com/endpoint{i}",
                    json={"id": i},
                    status=200,
                )

            session = disk_cache.get_metadata_session()

            # Make requests
            for i in range(5):
                session.get(f"https://test.com/endpoint{i}")

            # Size should be at least 5
            assert disk_cache.size() >= 5
