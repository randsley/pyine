"""Async high-level API for INE Portugal data access."""

import logging
from collections.abc import AsyncIterator
from typing import Any, Optional

from pyptine.client.async_data import AsyncDataClient
from pyptine.client.metadata import MetadataClient
from pyptine.models.response import DataResponse

logger = logging.getLogger(__name__)


class AsyncINE:
    """High-level async API for accessing INE Portugal statistical data.

    Provides convenient async methods for fetching and analyzing Portuguese
    statistical data. Supports concurrent requests for high-performance
    data retrieval when querying multiple indicators or large datasets.

    Args:
        language: Language for API responses ("EN" or "PT", default: "EN")
        timeout: Request timeout in seconds (default: 30)

    Example:
        >>> async with AsyncINE(language="EN") as ine:
        ...     response = await ine.get_data("0004167")
        ...     df = response.to_dataframe()
        ...
        ...     # Fetch multiple indicators concurrently
        ...     async for chunk in ine.get_all_data("0004127"):
        ...         print(f"Processing {len(chunk.data)} records")

    Features:
        - Non-blocking I/O with async/await
        - Concurrent requests for multiple indicators
        - Full pagination support with streaming
        - Dimension filtering
        - Automatic retry logic
    """

    def __init__(
        self,
        language: str = "EN",
        timeout: int = 30,
    ) -> None:
        """Initialize async INE client."""
        self.language = language.upper()
        self.timeout = timeout
        self.data_client: Optional[AsyncDataClient] = None
        self.metadata_client: Optional[MetadataClient] = None

        # Validate language
        if self.language not in ("EN", "PT"):
            raise ValueError(f"Language must be 'EN' or 'PT', got: {language}")

        logger.info(
            f"Initialized AsyncINE client (language={self.language}, timeout={self.timeout}s)"
        )

    async def __aenter__(self) -> "AsyncINE":
        """Async context manager entry."""
        self.metadata_client = MetadataClient(language=self.language, timeout=self.timeout)
        self.data_client = AsyncDataClient(
            language=self.language,
            timeout=self.timeout,
            metadata_client=self.metadata_client,
        )
        await self.data_client.__aenter__()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self.data_client:
            await self.data_client.__aexit__(exc_type, exc_val, exc_tb)
            logger.debug("Closed AsyncINE client")

    async def get_data(
        self,
        varcd: str,
        dimensions: Optional[dict[str, str]] = None,
    ) -> DataResponse:
        """Fetch indicator data asynchronously.

        Retrieves data for a single indicator without blocking.

        Args:
            varcd: Indicator code (e.g., "0004167")
            dimensions: Optional dimension filters

        Returns:
            DataResponse object with indicator data

        Raises:
            ValueError: If indicator code is invalid
            DimensionError: If dimension filters are invalid

        Example:
            >>> async with AsyncINE() as ine:
            ...     response = await ine.get_data("0004167")
            ...     print(response.title)
        """
        if not self.data_client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")

        return await self.data_client.get_data(varcd, dimensions)

    async def get_all_data(
        self,
        varcd: str,
        dimensions: Optional[dict[str, str]] = None,
        chunk_size: int = 40000,
    ) -> AsyncIterator[DataResponse]:
        """Fetch all data for an indicator with async pagination.

        Streams data in chunks without loading everything into memory.
        Ideal for large datasets.

        Args:
            varcd: Indicator code
            dimensions: Optional dimension filters
            chunk_size: Number of records per chunk (default: 40,000)

        Yields:
            DataResponse objects, one per chunk

        Example:
            >>> async with AsyncINE() as ine:
            ...     async for chunk in ine.get_all_data("0004127"):
            ...         print(f"Got {len(chunk.data)} records")
        """
        if not self.data_client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")

        async for chunk in self.data_client.get_all_data(varcd, dimensions, chunk_size):
            yield chunk

    async def get_metadata(self, varcd: str) -> Any:
        """Fetch indicator metadata.

        Args:
            varcd: Indicator code

        Returns:
            IndicatorMetadata object

        Example:
            >>> async with AsyncINE() as ine:
            ...     metadata = await ine.get_metadata("0004167")
            ...     print(metadata.unit)
        """
        if not self.metadata_client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")

        return self.metadata_client.get_metadata(varcd)

    async def get_dimensions(self, varcd: str) -> Any:
        """Fetch available dimensions for an indicator.

        Args:
            varcd: Indicator code

        Returns:
            List of Dimension objects

        Example:
            >>> async with AsyncINE() as ine:
            ...     dims = await ine.get_dimensions("0004167")
            ...     for dim in dims:
            ...         print(f"{dim.name}: {len(dim.values)} values")
        """
        if not self.metadata_client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")

        return self.metadata_client.get_dimensions(varcd)

    async def get_indicator(self, varcd: str) -> Any:
        """Fetch indicator metadata from catalogue.

        Args:
            varcd: Indicator code

        Returns:
            Indicator object

        Example:
            >>> async with AsyncINE() as ine:
            ...     indicator = await ine.get_indicator("0004167")
            ...     print(indicator.title)
        """
        if not self.metadata_client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")

        return self.metadata_client.get_metadata(varcd)
