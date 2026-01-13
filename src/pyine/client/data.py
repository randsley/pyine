"""Data client for INE Portugal API."""

import logging
from typing import Any, Dict, Iterator, Optional, cast

from pyine.client.base import INEClient
from pyine.models.response import DataResponse
from pyine.utils.exceptions import DataProcessingError, DimensionError

logger = logging.getLogger(__name__)


class DataClient(INEClient):
    """Client for INE data API endpoint.

    Fetches and parses indicator data with support for dimension filtering
    and pagination for large datasets.

    Example:
        >>> client = DataClient(language="EN")
        >>> response = client.get_data("0004167")
        >>> df = response.to_dataframe()
    """

    DATA_ENDPOINT = "/ine/json_indicador/pindica.jsp"
    DEFAULT_PAGE_SIZE = 40000  # API limit for data points per request

    def get_data(
        self,
        varcd: str,
        dimensions: Optional[Dict[str, str]] = None,
    ) -> DataResponse:
        """Fetch indicator data with optional dimension filters.

        Args:
            varcd: Indicator code (e.g., "0004167")
            dimensions: Optional dimension filters (e.g., {"Dim1": "2023", "Dim2": "1"})

        Returns:
            DataResponse object with indicator data

        Raises:
            DimensionError: If dimension filters are invalid
            DataProcessingError: If response parsing fails

        Example:
            >>> client = DataClient()
            >>> # Get all data
            >>> response = client.get_data("0004167")
            >>> # Get filtered data
            >>> response = client.get_data(
            ...     "0004167",
            ...     dimensions={"Dim1": "2023", "Dim2": "1"}
            ... )
            >>> df = response.to_dataframe()
        """
        logger.info(f"Fetching data for indicator {varcd}")

        params = self._build_params(varcd, dimensions)

        try:
            response = self._make_request(self.DATA_ENDPOINT, params=params, response_format="json")

            # Parse response
            data_response = self._parse_data_response(cast(Dict[str, Any], response))

            logger.info(f"Retrieved {len(data_response.data)} data points for {varcd}")

            return data_response

        except Exception as e:
            logger.error(f"Failed to get data for {varcd}: {str(e)}")
            raise

    def get_data_paginated(
        self,
        varcd: str,
        dimensions: Optional[Dict[str, str]] = None,
        chunk_size: int = DEFAULT_PAGE_SIZE,
    ) -> Iterator[DataResponse]:
        """Fetch large datasets in chunks (paginated).

        This is useful for indicators with more than 40,000 data points.
        Note: The API itself may not support true pagination, so this
        method currently returns all data in one chunk. Future versions
        may implement proper pagination if the API supports it.

        Args:
            varcd: Indicator code
            dimensions: Optional dimension filters
            chunk_size: Maximum data points per chunk (default: 40000)

        Yields:
            DataResponse objects, one per chunk

        Example:
            >>> client = DataClient()
            >>> for chunk in client.get_data_paginated("0004167"):
            ...     df = chunk.to_dataframe()
            ...     # Process chunk
        """
        logger.info(f"Fetching paginated data for indicator {varcd}")

        # For now, fetch all data at once
        # TODO: Implement true pagination if API supports it
        response = self.get_data(varcd, dimensions)
        yield response

        logger.info(f"Completed paginated fetch for {varcd}")

    def _build_params(
        self, varcd: str, dimensions: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Build query parameters for data API request.

        Args:
            varcd: Indicator code
            dimensions: Optional dimension filters

        Returns:
            Dictionary of query parameters

        Raises:
            DimensionError: If dimension keys are invalid
        """
        params = {
            "op": "2",  # Operation code for data retrieval
            "varcd": varcd,
        }

        # Add dimension filters
        if dimensions:
            for key, value in dimensions.items():
                # Validate dimension key format (should be Dim1, Dim2, etc.)
                if not key.startswith("Dim"):
                    raise DimensionError(
                        f"Invalid dimension key: {key}. "
                        f"Dimension keys must be in format 'Dim1', 'Dim2', etc."
                    )

                params[key] = str(value)

        return params

    def _parse_data_response(self, response: Dict[str, Any]) -> DataResponse:
        """Parse data API response into DataResponse model.

        Args:
            response: Raw JSON response from API

        Returns:
            Parsed DataResponse object

        Raises:
            DataProcessingError: If parsing fails
        """
        try:
            # Extract basic info
            indicator_code = response.get("indicador", "")
            indicator_name = response.get("nome", "")
            language = response.get("lang", self.language)
            unit = response.get("unidade")

            # Extract data array
            data_array = response.get("dados", [])

            # Process data points
            processed_data = []
            for data_point in data_array:
                processed_point = self._process_data_point(data_point)
                if processed_point:
                    processed_data.append(processed_point)

            return DataResponse(
                indicator_code=indicator_code,
                indicator_name=indicator_name,
                language=language,
                data=processed_data,
                unit=unit,
            )

        except Exception as e:
            logger.error(f"Failed to parse data response: {str(e)}")
            raise DataProcessingError(f"Failed to parse data: {str(e)}") from e

    def _process_data_point(self, data_point: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single data point from the API response.

        Args:
            data_point: Raw data point dictionary

        Returns:
            Processed data point dictionary or None if invalid
        """
        try:
            processed = {}

            # Iterate through all fields in the data point
            for key, value in data_point.items():
                # Skip internal fields
                if key.startswith("_"):
                    continue

                # Handle value field specially (convert to float)
                if key == "valor" or key == "value":
                    try:
                        # Try to convert to float
                        processed["value"] = float(value) if value else None
                    except (ValueError, TypeError):
                        processed["value"] = None
                else:
                    # Keep other fields as-is
                    processed[key] = value

            return processed

        except Exception as e:
            logger.warning(f"Failed to process data point: {str(e)}")
            return None

    def validate_dimensions(self, varcd: str, dimensions: Dict[str, str]) -> bool:
        """Validate dimension filters against indicator metadata.

        This method would check if the provided dimension codes are valid
        for the indicator. Currently returns True as a placeholder.

        Args:
            varcd: Indicator code
            dimensions: Dimension filters to validate

        Returns:
            True if dimensions are valid

        Note:
            Full validation would require fetching metadata and checking
            dimension codes. This is left as a future enhancement.
        """
        # TODO: Implement full validation by fetching metadata
        # and checking dimension codes against available values
        return True
