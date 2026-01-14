"""Data client for INE Portugal API."""

import logging
from typing import Any, Dict, Iterator, List, Optional, Union, cast

from pyine.client.base import INEClient
from pyine.client.metadata import MetadataClient  # Import MetadataClient
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

    def __init__(
        self,
        language: str = "EN",
        timeout: int = 30,
        cache_enabled: bool = True,
        cache_dir: Optional[Path] = None,
        metadata_client: Optional[MetadataClient] = None,  # New parameter
    ):
        super().__init__(language, timeout, cache_enabled, cache_dir)
        self.metadata_client = metadata_client

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
            raw_response = self._make_request(
                self.DATA_ENDPOINT, params=params, response_format="json"
            )

            # Parse response
            data_response = self._parse_data_response(
                varcd, cast(Union[Dict[str, Any], List[Dict[str, Any]]], raw_response)
            )

            logger.info(f"Retrieved {len(data_response.data)} data points for {varcd}")

            return data_response

        except Exception as e:
            logger.error(f"Failed to get data for {varcd}: {str(e)}")
            raise

    def get_all_data(
        self,
        varcd: str,
        dimensions: Optional[Dict[str, str]] = None,
        chunk_size: int = DEFAULT_PAGE_SIZE,
    ) -> Iterator[DataResponse]:
        """Fetch all data for a given indicator.

        Note: The INE API does not support true pagination. This method
        fetches all available data for the specified indicator and dimensions
        in a single request (up to the API's internal limit of 40,000 data points).
        For larger datasets, consider breaking down requests by dimensions manually.

        Args:
            varcd: Indicator code
            dimensions: Optional dimension filters
            chunk_size: This parameter is ignored as true pagination is not supported.

        Yields:
            DataResponse objects, one per chunk (currently always one chunk)

        Example:
            >>> client = DataClient()
            >>> for chunk in client.get_all_data("0004167"):
            ...     df = chunk.to_dataframe()
            ...     # Process chunk
        """
        logger.info(f"Fetching all data for indicator {varcd}")

        # For now, fetch all data at once
        # TODO: Implement true pagination if API supports it (by dimensions)
        response = self.get_data(varcd, dimensions)
        yield response

        logger.info(f"Completed fetch for {varcd}")

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

    def _parse_data_response(
        self, varcd: str, response: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> DataResponse:
        """Parse data API response into DataResponse model.

        Args:
            varcd: Indicator code (used if response is a list)
            response: Raw JSON response from API (can be dict or list)

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
                # If response is a list, assume it's directly the data array
                data_array = response
                # Fetch metadata separately to get title and unit
                if self.metadata_client:
                    try:
                        metadata = self.metadata_client.get_metadata(varcd)
                        title = metadata.title
                        unit = metadata.unit
                    except Exception as e:
                        logger.warning(
                            f"Could not fetch metadata for {varcd} when parsing list data response: {e}"
                        )
                else:
                    logger.warning(
                        "MetadataClient not available in DataClient to fetch indicator name and unit."
                    )

                if not title and data_array:
                    # Fallback: try to get unit from first data point if metadata not available
                    first_point = data_array[0]
                    unit = first_point.get("unidade") or first_point.get("unit")

            elif isinstance(response, dict):
                # If response is a dict, parse as before
                varcd_val = response.get("indicador", "")
                title = response.get("nome", "")
                language = response.get("lang", self.language)
                unit = response.get("unidade")
                data_array = response.get("dados", [])
            else:
                raise DataProcessingError(
                    "Unexpected data API response format: neither dict nor list"
                )

            # Process data points
            processed_data = []
            for data_point in data_array:
                processed_point = self._process_data_point(data_point)
                if processed_point:
                    processed_data.append(processed_point)

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
                        processed["value"] = float(value) if value is not None else None
                    except (ValueError, TypeError) as e:
                        logger.warning(
                            f"Could not convert value '{value}' for key '{key}' to float in data point {data_point}. "
                            f"Setting to None. Error: {e}"
                        )
                        processed["value"] = None
                else:
                    # Keep other fields as-is
                    processed[key] = value

            return processed

        except Exception as e:
            logger.warning(f"Failed to process data point {data_point}: {str(e)}")
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
