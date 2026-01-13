"""Catalogue browsing and search functionality for pyine."""

import logging
from typing import List, Optional

from pyine.client.catalogue import CatalogueClient
from pyine.models.indicator import Indicator

logger = logging.getLogger(__name__)


class CatalogueBrowser:
    """Browse and search INE indicator catalogue.

    Provides functionality to search indicators by keyword, filter by theme,
    and discover available statistical data.

    Args:
        client: CatalogueClient instance for API access
        language: Language code ('PT' or 'EN')

    Example:
        >>> from pyine import INE
        >>> ine = INE(language="EN")
        >>> browser = CatalogueBrowser(ine.catalogue_client)
        >>> results = browser.search("population")
        >>> for indicator in results:
        ...     print(indicator.title)
    """

    def __init__(self, client: CatalogueClient, language: str = "EN"):
        """Initialize catalogue browser.

        Args:
            client: CatalogueClient instance
            language: Language code ('PT' or 'EN')
        """
        self.client = client
        self.language = language
        self._cached_indicators: Optional[List[Indicator]] = None

    def get_all_indicators(self, use_cache: bool = True) -> List[Indicator]:
        """Get all available indicators from catalogue.

        Args:
            use_cache: Use cached indicators if available

        Returns:
            List of all indicators

        Example:
            >>> browser = CatalogueBrowser(client)
            >>> all_indicators = browser.get_all_indicators()
            >>> len(all_indicators)
            500
        """
        if use_cache and self._cached_indicators is not None:
            logger.debug("Using cached indicator list")
            return self._cached_indicators

        logger.info("Fetching all indicators from catalogue")
        indicators = self.client.get_main_indicators()
        self._cached_indicators = indicators

        logger.info(f"Retrieved {len(indicators)} indicators")
        return indicators

    def search(
        self,
        query: str,
        search_fields: Optional[List[str]] = None,
        case_sensitive: bool = False,
        exact_match: bool = False,
    ) -> List[Indicator]:
        """Search indicators by text query.

        Searches across indicator title, description, keywords, theme, and subtheme.

        Args:
            query: Search query string
            search_fields: Fields to search in (default: all text fields)
            case_sensitive: Perform case-sensitive search
            exact_match: Require exact match (not substring)

        Returns:
            List of matching indicators

        Example:
            >>> browser = CatalogueBrowser(client)
            >>> results = browser.search("population")
            >>> results = browser.search("GDP", search_fields=["title", "keywords"])
        """
        if not query:
            return []

        indicators = self.get_all_indicators()

        # Default to searching all text fields
        if search_fields is None:
            search_fields = ["title", "description", "keywords", "theme", "subtheme"]

        # Prepare query
        search_query = query if case_sensitive else query.lower()

        results = []
        for indicator in indicators:
            if self._matches_query(
                indicator, search_query, search_fields, case_sensitive, exact_match
            ):
                results.append(indicator)

        logger.debug(f"Search for '{query}' found {len(results)} results")
        return results

    def _matches_query(
        self,
        indicator: Indicator,
        query: str,
        search_fields: List[str],
        case_sensitive: bool,
        exact_match: bool,
    ) -> bool:
        """Check if indicator matches search query.

        Args:
            indicator: Indicator to check
            query: Search query
            search_fields: Fields to search
            case_sensitive: Case-sensitive matching
            exact_match: Require exact match

        Returns:
            True if indicator matches query
        """
        for field in search_fields:
            value = getattr(indicator, field, None)

            if value is None:
                continue

            # Handle list fields (keywords)
            if isinstance(value, list):
                for item in value:
                    item_str = str(item) if case_sensitive else str(item).lower()
                    if exact_match:
                        if item_str == query:
                            return True
                    else:
                        if query in item_str:
                            return True
            else:
                # Handle string fields
                value_str = str(value) if case_sensitive else str(value).lower()
                if exact_match:
                    if value_str == query:
                        return True
                else:
                    if query in value_str:
                        return True

        return False

    def filter_by_theme(
        self,
        theme: Optional[str] = None,
        subtheme: Optional[str] = None,
        case_sensitive: bool = False,
    ) -> List[Indicator]:
        """Filter indicators by theme or subtheme.

        Args:
            theme: Theme name to filter by
            subtheme: Subtheme name to filter by
            case_sensitive: Perform case-sensitive matching

        Returns:
            List of indicators matching theme/subtheme

        Example:
            >>> browser = CatalogueBrowser(client)
            >>> pop_indicators = browser.filter_by_theme(theme="Population")
            >>> employment = browser.filter_by_theme(
            ...     theme="Labour Market",
            ...     subtheme="Employment"
            ... )
        """
        indicators = self.get_all_indicators()
        results = []

        for indicator in indicators:
            # Check theme match
            if theme is not None:
                indicator_theme = indicator.theme or ""
                theme_compare = theme if case_sensitive else theme.lower()
                indicator_theme_compare = (
                    indicator_theme if case_sensitive else indicator_theme.lower()
                )

                if theme_compare not in indicator_theme_compare:
                    continue

            # Check subtheme match
            if subtheme is not None:
                indicator_subtheme = indicator.subtheme or ""
                subtheme_compare = subtheme if case_sensitive else subtheme.lower()
                indicator_subtheme_compare = (
                    indicator_subtheme if case_sensitive else indicator_subtheme.lower()
                )

                if subtheme_compare not in indicator_subtheme_compare:
                    continue

            results.append(indicator)

        logger.debug(f"Theme filter found {len(results)} results")
        return results

    def list_themes(self) -> List[str]:
        """Get list of all unique themes in catalogue.

        Returns:
            Sorted list of theme names

        Example:
            >>> browser = CatalogueBrowser(client)
            >>> themes = browser.list_themes()
            >>> print(themes)
            ['Agriculture', 'Economy', 'Population', ...]
        """
        indicators = self.get_all_indicators()
        themes = set()

        for indicator in indicators:
            if indicator.theme:
                themes.add(indicator.theme)

        return sorted(themes)

    def list_subthemes(self, theme: Optional[str] = None) -> List[str]:
        """Get list of subthemes, optionally filtered by theme.

        Args:
            theme: Optional theme name to filter subthemes

        Returns:
            Sorted list of subtheme names

        Example:
            >>> browser = CatalogueBrowser(client)
            >>> all_subthemes = browser.list_subthemes()
            >>> pop_subthemes = browser.list_subthemes(theme="Population")
        """
        indicators = self.filter_by_theme(theme=theme) if theme else self.get_all_indicators()

        subthemes = set()
        for indicator in indicators:
            if indicator.subtheme:
                subthemes.add(indicator.subtheme)

        return sorted(subthemes)

    def get_recently_updated(self, limit: int = 10) -> List[Indicator]:
        """Get recently updated indicators.

        Args:
            limit: Maximum number of indicators to return

        Returns:
            List of indicators sorted by last update (most recent first)

        Example:
            >>> browser = CatalogueBrowser(client)
            >>> recent = browser.get_recently_updated(limit=5)
            >>> for indicator in recent:
            ...     print(f"{indicator.title}: {indicator.last_update}")
        """
        indicators = self.get_all_indicators()

        # Filter indicators with last_update date
        dated_indicators = [ind for ind in indicators if ind.last_update is not None]

        # Sort by last_update descending
        sorted_indicators = sorted(
            dated_indicators,
            key=lambda x: x.last_update,  # type: ignore
            reverse=True,
        )

        return sorted_indicators[:limit]

    def get_by_code(self, varcd: str) -> Optional[Indicator]:
        """Get indicator by code.

        Args:
            varcd: Indicator code

        Returns:
            Indicator if found, None otherwise

        Example:
            >>> browser = CatalogueBrowser(client)
            >>> indicator = browser.get_by_code("0004167")
            >>> print(indicator.title)
        """
        try:
            return self.client.get_indicator(varcd)
        except Exception as e:
            logger.warning(f"Failed to get indicator {varcd}: {str(e)}")
            return None

    def validate_indicator(self, varcd: str) -> bool:
        """Check if indicator code is valid.

        Args:
            varcd: Indicator code to validate

        Returns:
            True if indicator exists, False otherwise

        Example:
            >>> browser = CatalogueBrowser(client)
            >>> browser.validate_indicator("0004167")
            True
            >>> browser.validate_indicator("invalid")
            False
        """
        indicator = self.get_by_code(varcd)
        return indicator is not None

    def clear_cache(self) -> None:
        """Clear cached indicator list.

        Forces next call to get_all_indicators() to fetch fresh data.
        """
        logger.debug("Clearing catalogue cache")
        self._cached_indicators = None
