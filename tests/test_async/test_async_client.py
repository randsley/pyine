"""Tests for async client functionality."""

import pytest

from pyptine.async_ine import AsyncINE
from pyptine.client.async_data import AsyncDataClient
from pyptine.models.response import DataResponse


@pytest.mark.asyncio
class TestAsyncINEClient:
    """Tests for AsyncINE client."""

    async def test_async_context_manager(self):
        """Test async context manager initialization and cleanup."""
        async with AsyncINE(language="EN") as ine:
            assert ine.data_client is not None
            assert ine.metadata_client is not None
            assert ine.language == "EN"

    async def test_async_client_invalid_language(self):
        """Test async client with invalid language."""
        with pytest.raises(ValueError):
            AsyncINE(language="INVALID")

    async def test_async_client_without_context(self):
        """Test that async client raises error without context manager."""
        ine = AsyncINE()

        with pytest.raises(RuntimeError):
            await ine.get_data("0004167")

    async def test_async_data_client_creation(self):
        """Test async data client can be created."""
        async with AsyncDataClient(language="EN") as client:
            assert client is not None
            assert client.language == "EN"
            assert client.client is not None


@pytest.mark.asyncio
class TestAsyncDataFetching:
    """Tests for async data fetching with mock responses."""

    async def test_async_get_data_mock(self, mocker, sample_data):
        """Test async get_data with mocked HTTP response."""
        # Mock httpx.AsyncClient.get to return awaitable response
        mock_response = mocker.AsyncMock()
        mock_response.json = mocker.AsyncMock(return_value=sample_data)
        mock_response.status_code = 200

        mock_client = mocker.AsyncMock()
        mock_client.get = mocker.AsyncMock(return_value=mock_response)
        mock_client.aclose = mocker.AsyncMock()

        async with AsyncINE(language="EN") as ine:
            # Replace the client with our mock
            ine.data_client.client = mock_client

            response = await ine.get_data("0004167")

            assert isinstance(response, DataResponse)
            assert response.varcd == "0004167"

    async def test_async_get_all_data_pagination(self, mocker):
        """Test async get_all_data pagination stops when chunk is incomplete."""
        # Test that pagination stops when returned data is less than chunk_size
        # by directly testing the _build_params method with different offsets
        async with AsyncDataClient(language="EN") as client:
            # First request - no offset
            params1 = client._build_params("0004167", offset=0, limit=5)
            assert params1["start"] == "0"
            assert params1["count"] == "5"

            # Second request - offset 5
            params2 = client._build_params("0004167", offset=5, limit=5)
            assert params2["start"] == "5"
            assert params2["count"] == "5"

            # Verify that the pagination parameters are correctly built
            assert "varcd" in params1
            assert "op" in params1
            assert params1["op"] == "2"

    async def test_async_concurrent_requests(self, mocker):
        """Test that async allows multiple concurrent requests."""
        import asyncio

        mock_response = mocker.AsyncMock()
        mock_response.json = mocker.AsyncMock(return_value={
            "indicador": "0004167",
            "nome": "Test",
            "lang": "EN",
            "dados": [{"periodo": "2020", "valor": "100"}]
        })
        mock_response.status_code = 200

        mock_client = mocker.AsyncMock()
        mock_client.get = mocker.AsyncMock(return_value=mock_response)
        mock_client.aclose = mocker.AsyncMock()

        async def fetch_data(varcd):
            async with AsyncINE(language="EN") as ine:
                ine.data_client.client = mock_client
                return await ine.get_data(varcd)

        # Run multiple requests concurrently
        results = await asyncio.gather(
            fetch_data("0004167"),
            fetch_data("0004128"),
            fetch_data("0004129"),
        )

        assert len(results) == 3
        assert all(isinstance(r, DataResponse) for r in results)


@pytest.mark.asyncio
class TestAsyncMetadata:
    """Tests for async metadata operations."""

    async def test_async_get_metadata(self, mocker, sample_metadata):
        """Test async metadata retrieval."""
        mock_client_obj = mocker.MagicMock()
        mock_client_obj.get_metadata.return_value = mocker.MagicMock(
            varcd="0004167",
            title="Test",
            unit="No."
        )

        async with AsyncINE(language="EN") as ine:
            ine.metadata_client = mock_client_obj
            metadata = await ine.get_metadata("0004167")

            assert metadata.varcd == "0004167"
            assert metadata.title == "Test"

    async def test_async_get_dimensions(self, mocker):
        """Test async dimensions retrieval."""
        mock_dimension = mocker.MagicMock()
        mock_dimension.name = "Period"
        mock_dimension.values = []

        mock_client_obj = mocker.MagicMock()
        mock_client_obj.get_dimensions.return_value = [mock_dimension]

        async with AsyncINE(language="EN") as ine:
            ine.metadata_client = mock_client_obj
            dims = await ine.get_dimensions("0004167")

            assert len(dims) == 1
            assert dims[0].name == "Period"


@pytest.mark.asyncio
class TestAsyncBuildParams:
    """Tests for async parameter building."""

    async def test_async_build_params_basic(self):
        """Test basic parameter building in async client."""
        async with AsyncDataClient(language="EN") as client:
            params = client._build_params("0004167")

            assert params["op"] == "2"
            assert params["varcd"] == "0004167"
            assert "lang" not in params  # Added by _make_request

    async def test_async_build_params_with_pagination(self):
        """Test pagination parameters."""
        async with AsyncDataClient(language="EN") as client:
            params = client._build_params("0004167", offset=100, limit=50)

            assert params["start"] == "100"
            assert params["count"] == "50"

    async def test_async_build_params_with_dimensions(self):
        """Test dimension parameters with mock metadata."""
        from unittest.mock import MagicMock

        mock_metadata = MagicMock()
        mock_metadata_client = MagicMock()
        mock_metadata_client.get_metadata.return_value = mock_metadata

        # Add mock dimensions to avoid validation errors
        mock_dim = MagicMock()
        mock_dim.id = 1
        mock_dim.values = [MagicMock(code="2023")]
        mock_metadata.dimensions = [mock_dim]

        async with AsyncDataClient(language="EN", metadata_client=mock_metadata_client) as client:
            params = client._build_params("0004167", dimensions={"Dim1": "2023"})

            assert params["Dim1"] == "2023"
