"""Metadata client for INE Portugal API."""

import logging
from typing import Any, Dict, List, Union, cast

from pyine.client.base import INEClient
from pyine.models.indicator import (
    Dimension,
    DimensionValue,
    IndicatorMetadata,
)
from pyine.utils.exceptions import DataProcessingError

logger = logging.getLogger(__name__)


class MetadataClient(INEClient):
    """Client for INE metadata API endpoint.

    Fetches and parses indicator metadata including dimensions and their values.

    Example:
        >>> client = MetadataClient(language="EN")
        >>> metadata = client.get_metadata("0004167")
        >>> print(metadata.title)
        'Resident population'
    """

    METADATA_ENDPOINT = "/ine/json_indicador/pindicaMeta.jsp"

    def get_metadata(self, varcd: str) -> IndicatorMetadata:
        """Get complete metadata for an indicator.

        Args:
            varcd: Indicator code (e.g., "0004167")

        Returns:
            IndicatorMetadata object with dimensions and other info

        Raises:
            InvalidIndicatorError: If indicator not found
            DataProcessingError: If response parsing fails

        Example:
            >>> client = MetadataClient()
            >>> metadata = client.get_metadata("0004167")
            >>> for dim in metadata.dimensions:
            ...     print(f"{dim.name}: {len(dim.values)} values")
        """
        logger.info(f"Fetching metadata for indicator {varcd}")

        params = {"varcd": varcd}

        try:
            response = self._make_request(
                self.METADATA_ENDPOINT, params=params, response_format="json"
            )

            # Parse response
            metadata = self._parse_metadata_response(cast(Dict[str, Any], response))

            logger.info(
                f"Retrieved metadata for {varcd}: " f"{len(metadata.dimensions)} dimensions"
            )

            return metadata

        except Exception as e:
            logger.error(f"Failed to get metadata for {varcd}: {str(e)}")
            raise

    def get_dimensions(self, varcd: str) -> List[Dimension]:
        """Get dimension definitions for an indicator.

        Args:
            varcd: Indicator code

        Returns:
            List of Dimension objects

        Example:
            >>> client = MetadataClient()
            >>> dimensions = client.get_dimensions("0004167")
            >>> for dim in dimensions:
            ...     print(f"Dimension {dim.id}: {dim.name}")
        """
        metadata = self.get_metadata(varcd)
        return metadata.dimensions

    def get_dimension_values(self, varcd: str, dimension_id: int) -> List[DimensionValue]:
        """Get available values for a specific dimension.

        Args:
            varcd: Indicator code
            dimension_id: Dimension identifier (1, 2, 3, etc.)

        Returns:
            List of DimensionValue objects

        Raises:
            ValueError: If dimension_id not found

        Example:
            >>> client = MetadataClient()
            >>> values = client.get_dimension_values("0004167", 1)
            >>> for value in values:
            ...     print(f"{value.code}: {value.label}")
        """
        dimensions = self.get_dimensions(varcd)

        for dim in dimensions:
            if dim.id == dimension_id:
                return dim.values

        raise ValueError(
            f"Dimension {dimension_id} not found for indicator {varcd}. "
            f"Available dimensions: {[d.id for d in dimensions]}"
        )

    def _parse_metadata_response(
        self, response: Union[Dict[str, Any], List[Any]]
    ) -> IndicatorMetadata:
        """Parse metadata API response into IndicatorMetadata model.

        Args:
            response: Raw JSON response from API (can be dict or list)

        Returns:
            Parsed IndicatorMetadata object

        Raises:
            DataProcessingError: If parsing fails
        """
        try:
            if isinstance(response, list):
                if len(response) == 1 and isinstance(response[0], dict):
                    # If it's a list with a single dictionary, use that dictionary
                    response = response[0]
                elif not response:
                    # If it's an empty list, treat as no metadata found
                    raise DataProcessingError(
                        "No metadata found for indicator (empty list response)."
                    )
                else:
                    # If it's a list with multiple items or non-dict items, it's unexpected
                    raise DataProcessingError(
                        f"Unexpected metadata API response format: received a list with {len(response)} items. "
                        f"Expected a single dictionary for indicator metadata."
                    )

            if isinstance(response, dict):
                # Extract basic info
                varcd = response.get("indicador", "")
                title = response.get("nome", "")
                language = response.get("lang", self.language)
                unit = response.get("unidade")
                source = response.get("fonte")
                notes = response.get("notas")

                # Parse dimensions
                dimensions = []
                dims_data = response.get("dimensoes", [])

                for i, dim_data in enumerate(dims_data, start=1):
                    dimension = self._parse_dimension(dim_data, dimension_id=i)
                    dimensions.append(dimension)

                return IndicatorMetadata(
                    varcd=varcd,
                    title=title,
                    language=language,
                    dimensions=dimensions,
                    unit=unit,
                    source=source,
                    notes=notes,
                )
            else:
                # This case should ideally not be reached after the list check
                raise DataProcessingError(
                    "Unexpected metadata API response format: not a dictionary after list check."
                )

        except Exception as e:
            logger.error(f"Failed to parse metadata response: {str(e)}")
            raise DataProcessingError(f"Failed to parse metadata: {str(e)}") from e

    def _parse_dimension(self, dim_data: Dict[str, Any], dimension_id: int) -> Dimension:
        """Parse a single dimension from API response.

        Args:
            dim_data: Dimension data from API
            dimension_id: Dimension identifier

        Returns:
            Parsed Dimension object
        """
        # Get dimension info
        dim_id = dim_data.get("id", dimension_id)
        name = dim_data.get("nome", f"Dimension {dim_id}")
        description = dim_data.get("descricao")

        # Parse dimension values
        values = []
        values_data = dim_data.get("valores", [])

        for val_data in values_data:
            value = DimensionValue(
                code=val_data.get("codigo", ""),
                label=val_data.get("label", ""),
                order=val_data.get("ordem"),
            )
            values.append(value)

        return Dimension(id=dim_id, name=name, description=description, values=values)
