"""High-level API for INE Portugal data access."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union, cast

import pandas as pd

from pyine.client.base import INEClient
from pyine.client.catalogue import CatalogueClient
from pyine.client.data import DataClient
from pyine.client.metadata import MetadataClient
from pyine.models.indicator import Dimension, Indicator, IndicatorMetadata
from pyine.processors.csv import export_to_csv
from pyine.processors.dataframe import json_to_dataframe
from pyine.processors.json import export_to_json, format_json
from pyine.search.catalog import CatalogueBrowser

logger = logging.getLogger(__name__)

OutputFormat = Literal["dataframe", "json", "dict"]


class INE:
    """High-level interface to INE Portugal API.

    This is the main entry point for using pyine. It provides simple methods
    to search indicators, fetch data, and export results.

    Args:
        language: Language for API responses ('PT' or 'EN')
        cache: Enable HTTP caching
        cache_dir: Custom cache directory (default: platform-specific)
        cache_ttl: Cache time-to-live in seconds (default: 86400 / 1 day)
        timeout: Request timeout in seconds (default: 30)

    Example:
        >>> from pyine import INE
        >>> ine = INE(language="EN")
        >>>
        >>> # Search for indicators
        >>> results = ine.search("population")
        >>> print(f"Found {len(results)} indicators")
        >>>
        >>> # Get data as DataFrame
        >>> df = ine.get_data("0004127")
        >>> print(df.head())
        >>>
        >>> # Export to CSV
        >>> ine.export_csv("0004127", "output.csv")
    """

    def __init__(
        self,
        language: str = "EN",
        cache: bool = True,
        cache_dir: Optional[Path] = None,
        cache_ttl: Optional[int] = None,
        timeout: int = 30,
    ):
        """Initialize INE client.

        Args:
            language: Language code ('PT' or 'EN')
            cache: Enable HTTP caching
            cache_dir: Custom cache directory
            cache_ttl: Cache TTL in seconds
            timeout: Request timeout in seconds
        """
        self.language = language.upper()
        if self.language not in ("PT", "EN"):
            raise ValueError("Language must be 'PT' or 'EN'")

        # Store cache configuration
        self.cache_enabled = cache
        self.cache_dir = cache_dir

        common_client_params = {
            "language": self.language,
            "timeout": timeout,
            "cache_enabled": cache,
            "cache_dir": cache_dir,
        }

        # Initialize base client
        self.base_client = INEClient(**common_client_params)

        # Initialize specialized clients
        self.catalogue_client = CatalogueClient(**common_client_params)

        self.metadata_client = MetadataClient(**common_client_params)

        self.data_client = DataClient(
            **common_client_params,
            metadata_client=self.metadata_client,  # Pass metadata_client
        )

        # Initialize catalogue browser
        self.browser = CatalogueBrowser(self.catalogue_client, language=self.language)

        logger.info(f"Initialized INE client (language={self.language}, cache={cache})")

    def search(
        self,
        query: str,
        search_fields: Optional[List[str]] = None,
        case_sensitive: bool = False,
        theme: Optional[str] = None,
        subtheme: Optional[str] = None,
    ) -> List[Indicator]:
        """Search for indicators by keyword, with optional theme/subtheme filtering.

        Searches across indicator titles, descriptions, keywords, themes, and subthemes.

        Args:
            query: Search query string
            search_fields: Specific fields to search (default: all)
            case_sensitive: Perform case-sensitive search
            theme: Optional theme name to filter by
            subtheme: Optional subtheme name to filter by

        Returns:
            List of matching indicators

        Example:
            >>> ine = INE()
            >>> results = ine.search("gdp")
            >>> for ind in results:
            ...     print(f"{ind.varcd}: {ind.title}")
        """
        return self.browser.search(
            query=query,
            search_fields=search_fields,
            case_sensitive=case_sensitive,
            theme=theme,
            subtheme=subtheme,
        )

    def get_data(
        self,
        varcd: str,
        dimensions: Optional[Dict[str, str]] = None,
    ) -> DataResponse:
        """Get indicator data.

        Args:
            varcd: Indicator code
            dimensions: Optional dimension filters (e.g., {"Dim1": "2020"})

        Returns:
            DataResponse object with indicator data.
            Use .to_dataframe(), .to_json(), or .to_dict() for specific formats.

        Raises:
            InvalidIndicatorError: If indicator code is invalid
            APIError: If API request fails

        Example:
            >>> ine = INE()
            >>> response = ine.get_data("0004167")
            >>> df = response.to_dataframe()
            >>> json_str = response.to_json()
            >>> data_dict = response.to_dict()
        """
        logger.info(f"Fetching data for indicator {varcd}")

        # Fetch data from API
        response = self.data_client.get_data(varcd=varcd, dimensions=dimensions)
        return response

    def get_metadata(self, varcd: str) -> IndicatorMetadata:
        """Get indicator metadata.

        Retrieves complete metadata including dimensions, units, and descriptions.

        Args:
            varcd: Indicator code

        Returns:
            Indicator metadata

        Example:
            >>> ine = INE()
            >>> metadata = ine.get_metadata("0004167")
            >>> print(metadata.title)
            >>> print(f"Dimensions: {len(metadata.dimensions)}")
        """
        logger.info(f"Fetching metadata for indicator {varcd}")
        return self.metadata_client.get_metadata(varcd)

    def get_dimensions(self, varcd: str) -> List[Dimension]:
        """Get available dimensions for an indicator.

        Dimensions are used to filter data (e.g., by year, region, gender).

        Args:
            varcd: Indicator code

        Returns:
            List of available dimensions

        Example:
            >>> ine = INE()
            >>> dims = ine.get_dimensions("0004167")
            >>> for dim in dims:
            ...     print(f"{dim.name}: {len(dim.values)} values")
            >>>
            >>> # Use dimension values to filter data
            >>> df = ine.get_data("0004167", dimensions={"Dim1": dims[0].values[0].code})
        """
        logger.info(f"Fetching dimensions for indicator {varcd}")
        return self.metadata_client.get_dimensions(varcd)

    def get_indicator(self, varcd: str) -> Indicator:
        """Get indicator information from catalogue.

        Args:
            varcd: Indicator code

        Returns:
            Indicator object

        Example:
            >>> ine = INE()
            >>> indicator = ine.get_indicator("0004167")
            >>> print(indicator.title)
            >>> print(indicator.theme)
        """
        logger.info(f"Fetching indicator info for {varcd}")
        return self.catalogue_client.get_indicator(varcd)

    def validate_indicator(self, varcd: str) -> bool:
        """Check if indicator code is valid.

        Args:
            varcd: Indicator code

        Returns:
            True if indicator exists, False otherwise

        Example:
            >>> ine = INE()
            >>> ine.validate_indicator("0004167")
            True
            >>> ine.validate_indicator("invalid")
            False
        """
        return self.browser.validate_indicator(varcd)

    def list_themes(self) -> List[str]:
        """Get list of all themes in catalogue.

        Returns:
            Sorted list of theme names

        Example:
            >>> ine = INE()
            >>> themes = ine.list_themes()
            >>> print(themes)
            ['Agriculture', 'Economy', 'Population', ...]
        """
        return self.browser.list_themes()

    def export_csv(
        self,
        varcd: str,
        filepath: Union[str, Path],
        dimensions: Optional[Dict[str, str]] = None,
        include_metadata: bool = True,
    ) -> None:
        """Export indicator data to CSV file.

        Args:
            varcd: Indicator code
            filepath: Output file path
            dimensions: Optional dimension filters
            include_metadata: Include metadata as header comments

        Example:
            >>> ine = INE()
            >>> ine.export_csv("0004167", "data.csv")
            >>> ine.export_csv("0004167", "filtered.csv", dimensions={"Dim1": "2020"})
        """
        logger.info(f"Exporting indicator {varcd} to {filepath}")

        # Get data as DataFrame
        response = self.get_data(varcd, dimensions=dimensions)
        df = response.to_dataframe()

        # Get metadata if requested
        metadata_dict = None
        if include_metadata:
            metadata = self.get_metadata(varcd)
            metadata_dict = {
                "indicator": metadata.varcd,
                "title": metadata.title,
                "unit": metadata.unit,
                "source": metadata.source or "INE Portugal",
            }

        # Export to CSV
        export_to_csv(
            df=df,
            filepath=Path(filepath),
            include_metadata=include_metadata,
            metadata=metadata_dict,
        )

        logger.info(f"Successfully exported to {filepath}")

    def export_json(
        self,
        varcd: str,
        filepath: Union[str, Path],
        dimensions: Optional[Dict[str, str]] = None,
        pretty: bool = True,
    ) -> None:
        """Export indicator data to JSON file.

        Args:
            varcd: Indicator code
            filepath: Output file path
            dimensions: Optional dimension filters
            pretty: Use pretty printing

        Example:
            >>> ine = INE()
            >>> ine.export_json("0004127", "data.json")
            >>> ine.export_json("0004127", "compact.json", pretty=False)
        """
        logger.info(f"Exporting indicator {varcd} to {filepath}")

        # Get data - fetch from API
        response = self.get_data(varcd=varcd, dimensions=dimensions)

        # Convert to dict with JSON serialization for datetime objects
        data = response.model_dump(mode="json")

        # Export to JSON
        export_to_json(data=data, filepath=Path(filepath), pretty=pretty)

        logger.info(f"Successfully exported to {filepath}")

    def clear_cache(self) -> None:
        """Clear all cached data.

        Clears both HTTP cache and in-memory catalogue cache.

        Example:
            >>> ine = INE()
            >>> ine.clear_cache()
        """
        if self.cache_enabled and self.base_client.cache:
            self.base_client.cache.clear()
        self.browser.clear_cache()
        logger.info("Cache cleared")

    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache information

        Example:
            >>> ine = INE()
            >>> info = ine.get_cache_info()
            >>> print(info)
        """
        if not self.cache_enabled:
            return {"enabled": False}

        if self.base_client.cache:
            stats = self.base_client.cache.get_stats()
            return {
                "enabled": True,
                "metadata_cache": stats.get("metadata", {}),
                "data_cache": stats.get("data", {}),
            }
        else:
            return {"enabled": False}
