"""Async data client for INE Portugal API."""

import logging
from typing import Any, AsyncIterator, Optional, Union

from pyptine.client.async_base import AsyncINEClient
from pyptine.client.metadata import MetadataClient
from pyptine.models.response import DataResponse
from pyptine.utils.exceptions import DataProcessingError, DimensionError

logger = logging.getLogger(__name__)


class AsyncDataClient(AsyncINEClient):
    """Async client for INE data API endpoint.

    Provides async methods for fetching and parsing indicator data with support
    for dimension filtering and pagination for large datasets.

    Example:
        >>> async with AsyncDataClient(language="EN") as client:
        ...     response = await client.get_data("0004167")
        ...     df = response.to_dataframe()
    """

    DATA_ENDPOINT = "/ine/json_indicador/pindica.jsp"
    DEFAULT_PAGE_SIZE = 40000

    def __init__(
        self,
        language: str = "EN",
        timeout: int = 30,
        metadata_client: Optional[MetadataClient] = None,
    ):
        super().__init__(language, timeout)
        self.metadata_client = metadata_client

    async def get_data(
        self,
        varcd: str,
        dimensions: Optional[dict[str, str]] = None,
    ) -> DataResponse:
        """Fetch indicator data asynchronously with optional dimension filters.

        Args:
            varcd: Indicator code (e.g., "0004167")
            dimensions: Optional dimension filters

        Returns:
            DataResponse object with indicator data

        Raises:
            DimensionError: If dimension filters are invalid
            DataProcessingError: If response parsing fails

        Example:
            >>> async with AsyncDataClient() as client:
            ...     response = await client.get_data("0004167")
            ...     df = response.to_dataframe()
        """
        logger.info(f"Fetching data asynchronously for indicator {varcd}")

        params = self._build_params(varcd, dimensions)

        try:
            raw_response = await self._make_request(
                self.DATA_ENDPOINT, params=params, response_format="json"
            )

            # Parse response
            data_response = self._parse_data_response(varcd, raw_response)

            logger.info(f"Retrieved {len(data_response.data)} data points for {varcd}")

            return data_response

        except Exception as e:
            logger.error(f"Failed to get data for {varcd}: {str(e)}")
            raise

    async def get_all_data(
        self,
        varcd: str,
        dimensions: Optional[dict[str, str]] = None,
        chunk_size: int = DEFAULT_PAGE_SIZE,
    ) -> AsyncIterator[DataResponse]:
        """Fetch all data for a given indicator with async pagination support.

        Implements asynchronous chunked data fetching to handle large datasets
        efficiently without blocking.

        Args:
            varcd: Indicator code
            dimensions: Optional dimension filters
            chunk_size: Number of data points per chunk (default: 40,000)

        Yields:
            DataResponse objects, one per chunk

        Example:
            >>> async with AsyncDataClient() as client:
            ...     async for chunk in client.get_all_data("0004167"):
            ...         df = chunk.to_dataframe()
            ...         print(f"Processed {len(df)} rows")
        """
        logger.info(f"Fetching all data asynchronously for {varcd} with chunk_size={chunk_size}")

        offset = 0
        total_fetched = 0
        chunk_count = 0

        while True:
            chunk_count += 1
            logger.debug(f"Fetching chunk {chunk_count} with offset={offset}")

            params = self._build_params(varcd, dimensions, offset=offset, limit=chunk_size)

            try:
                raw_response = await self._make_request(
                    self.DATA_ENDPOINT, params=params, response_format="json"
                )

                # Parse response
                data_response = self._parse_data_response(varcd, raw_response)

                chunk_size_received = len(data_response.data)
                total_fetched += chunk_size_received

                logger.info(
                    f"Chunk {chunk_count}: Retrieved {chunk_size_received} data points "
                    f"(total so far: {total_fetched})"
                )

                yield data_response

                # If we received fewer data points than requested, we've reached the end
                if chunk_size_received < chunk_size:
                    logger.info(f"Completed fetch for {varcd}: total {total_fetched} data points")
                    break

                offset += chunk_size

            except Exception as e:
                logger.error(f"Failed to fetch chunk {chunk_count} for {varcd}: {str(e)}")
                raise

    def _build_params(
        self,
        varcd: str,
        dimensions: Optional[dict[str, str]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> dict[str, str]:
        """Build query parameters for data API request.

        Args:
            varcd: Indicator code
            dimensions: Optional dimension filters
            offset: Starting offset for pagination
            limit: Maximum number of records to return

        Returns:
            Dictionary of query parameters

        Raises:
            DimensionError: If dimension keys or values are invalid
        """
        params = {
            "op": "2",
            "varcd": varcd,
        }

        # Add pagination parameters if provided
        if offset is not None:
            params["start"] = str(offset)
        if limit is not None:
            params["count"] = str(limit)

        # Validate dimensions before building params
        if dimensions:
            self.validate_dimensions(varcd, dimensions)
            for key, value in dimensions.items():
                params[key] = str(value)

        return params

    def _parse_data_response(
        self, varcd: str, response: Union[dict[str, Any], list[dict[str, Any]]]
    ) -> DataResponse:
        """Parse data API response into DataResponse model.

        Args:
            varcd: Indicator code
            response: Raw JSON response from API

        Returns:
            Parsed DataResponse object

        Raises:
            DataProcessingError: If parsing fails
        """
        try:
            varcd_val = varcd
            title = ""
            language = self.language
            unit = None
            data_array = []

            if isinstance(response, list):
                if len(response) == 1 and isinstance(response[0], dict):
                    response = response[0]
                elif len(response) > 1:
                    data_array = response
                    if self.metadata_client:
                        try:
                            metadata = self.metadata_client.get_metadata(varcd)
                            title = metadata.title
                            unit = metadata.unit
                        except Exception as e:
                            logger.warning(f"Could not fetch metadata for {varcd}: {e}")

                    if not title and data_array:
                        first_point = data_array[0]
                        unit = first_point.get("unidade") or first_point.get("unit")

            if isinstance(response, dict):
                varcd_val = response.get("IndicadorCod") or response.get("indicador", varcd)
                title = (
                    response.get("IndicadorDsg")
                    or response.get("IndicadorNome")
                    or response.get("nome", "")
                )
                language = response.get("Lingua") or response.get("lang", self.language)
                unit = response.get("UnidadeMedida") or response.get("unidade")

                dados = response.get("Dados") or response.get("dados")
                if isinstance(dados, dict):
                    data_array = []
                    for year_data in dados.values():
                        if isinstance(year_data, list):
                            data_array.extend(year_data)
                elif isinstance(dados, list):
                    data_array = dados
                else:
                    data_array = []

            # Process data points
            processed_data = []
            for data_point in data_array:
                processed_point = self._process_data_point(data_point)
                if processed_point:
                    processed_data.append(processed_point)

            if unit is None and self.metadata_client:
                try:
                    metadata = self.metadata_client.get_metadata(varcd)
                    unit = metadata.unit
                    if not title:
                        title = metadata.title
                except Exception as e:
                    logger.debug(f"Could not fetch unit from metadata for {varcd}: {e}")

            return DataResponse(
                varcd=varcd_val,
                title=title,
                language=language,
                data=processed_data,
                unit=unit,
            )

        except Exception as e:
            logger.error(f"Failed to parse data response: {str(e)}")
            raise DataProcessingError(f"Failed to parse data: {str(e)}") from e

    def _process_data_point(self, data_point: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Process a single data point from the API response.

        Args:
            data_point: Raw data point dictionary

        Returns:
            Processed data point dictionary or None if invalid
        """
        try:
            processed = {}

            for key, value in data_point.items():
                if key.startswith("_"):
                    continue

                if key == "valor" or key == "value":
                    try:
                        processed["value"] = float(value) if value is not None else None
                    except (ValueError, TypeError) as e:
                        logger.warning(
                            f"Could not convert value '{value}' to float. Setting to None. Error: {e}"
                        )
                        processed["value"] = None
                else:
                    processed[key] = value

            return processed

        except Exception as e:
            logger.warning(f"Failed to process data point {data_point}: {str(e)}")
            return None

    def validate_dimensions(self, varcd: str, dimensions: dict[str, str]) -> bool:
        """Validate dimension filters against indicator metadata.

        Args:
            varcd: Indicator code
            dimensions: Dimension filters to validate

        Returns:
            True if dimensions are valid

        Raises:
            DimensionError: If any dimension is invalid
        """
        if not self.metadata_client:
            raise DimensionError("MetadataClient not available for dimension validation.")

        metadata = self.metadata_client.get_metadata(varcd)
        available_dimensions = {f"Dim{d.id}": d for d in metadata.dimensions}

        for dim_key, dim_value in dimensions.items():
            if dim_key not in available_dimensions:
                raise DimensionError(
                    f"Invalid dimension key '{dim_key}' for indicator {varcd}. "
                    f"Available keys: {list(available_dimensions.keys())}"
                )

            dimension = available_dimensions[dim_key]
            valid_values = {val.code for val in dimension.values}

            if dim_value not in valid_values:
                raise DimensionError(
                    f"Invalid value '{dim_value}' for dimension '{dim_key}' "
                    f"of indicator {varcd}. Available values: {list(valid_values)}"
                )

        return True
