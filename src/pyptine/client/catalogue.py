"""Catalogue client for INE Portugal API."""

import logging
from datetime import datetime
from typing import Any, Optional, cast
from xml.etree import ElementTree as ET

from pyptine.client.base import INEClient
from pyptine.models.indicator import Indicator
from pyptine.models.response import CatalogueResponse
from pyptine.utils.exceptions import DataProcessingError

logger = logging.getLogger(__name__)


class CatalogueClient(INEClient):
    """Client for INE catalogue API endpoint.

    Fetches and parses indicator catalogue from XML responses.

    Example:
        >>> client = CatalogueClient(language="EN")
        >>> indicator = client.get_indicator("0004167")
        >>> print(indicator.title)
        'Resident population'
    """

    CATALOGUE_ENDPOINT = "/ine/xml_indic.jsp"

    def _get_element_text(self, element: ET.Element, tag: str, default: str = "") -> str:
        """Helper to get text from a child element."""
        child = element.find(tag)
        if child is not None and child.text:
            return child.text.strip()
        return default

    def get_indicator(self, varcd: str) -> Indicator:
        """Get single indicator metadata from catalogue.

        Args:
            varcd: Indicator code (e.g., "0004167")

        Returns:
            Indicator object with metadata

        Example:
            >>> client = CatalogueClient()
            >>> indicator = client.get_indicator("0004167")
            >>> print(f"{indicator.varcd}: {indicator.title}")
        """
        logger.info(f"Fetching indicator {varcd} from catalogue")

        params = {
            "opc": "1",  # Single indicator
            "varcd": varcd,
        }

        try:
            xml_response = self._make_request(
                self.CATALOGUE_ENDPOINT, params=params, response_format="xml"
            )

            indicators = self._parse_catalogue_xml(cast(str, xml_response))

            if not indicators:
                raise DataProcessingError(f"Indicator {varcd} not found in catalogue")

            logger.info(f"Retrieved indicator {varcd}: {indicators[0].title}")
            return indicators[0]

        except Exception as e:
            logger.error(f"Failed to get indicator {varcd}: {str(e)}")
            raise

    def get_main_indicators(self) -> list[Indicator]:
        """Get all main indicators from catalogue.

        Returns:
            List of Indicator objects

        Note:
            This can return a large number of indicators. Consider using
            the search functionality instead for specific queries.

        Example:
            >>> client = CatalogueClient()
            >>> indicators = client.get_main_indicators()
            >>> print(f"Found {len(indicators)} indicators")
        """
        logger.info("Fetching main indicators group from catalogue")

        params = {
            "opc": "3",  # Main indicators group
        }

        try:
            xml_response = self._make_request(
                self.CATALOGUE_ENDPOINT, params=params, response_format="xml"
            )

            indicators = self._parse_catalogue_xml(cast(str, xml_response))

            logger.info(f"Retrieved {len(indicators)} main indicators")
            return indicators

        except Exception as e:
            logger.error(f"Failed to get main indicators: {str(e)}")
            raise

    def get_complete_catalogue(self, progress_callback: Optional[Any] = None) -> list[Indicator]:
        """Get the complete catalogue of indicators.

        Args:
            progress_callback: Optional callback function(downloaded_bytes, total_bytes)

        Returns:
            List of all Indicator objects in the complete catalogue.

        Raises:
            DataProcessingError: If XML parsing fails.
            Exception: For other API request failures.

        Example:
            >>> client = CatalogueClient()
            >>> all_indicators = client.get_complete_catalogue()
            >>> print(f"Found {len(all_indicators)} indicators in complete catalogue")
        """
        logger.info("Fetching complete catalogue of indicators (opc=2)")

        params = {
            "opc": "2",  # Complete catalogue
        }

        try:
            xml_response = self._make_request(
                self.CATALOGUE_ENDPOINT,
                params=params,
                response_format="xml",
                progress_callback=progress_callback,
            )

            indicators = self._parse_catalogue_xml(cast(str, xml_response))

            logger.info(f"Retrieved {len(indicators)} indicators from complete catalogue")
            return indicators

        except Exception as e:
            logger.error(f"Failed to get complete catalogue: {str(e)}")
            raise

    def get_catalogue_response(self, varcd: Optional[str] = None) -> CatalogueResponse:
        """Get catalogue response wrapped in CatalogueResponse model.

        Args:
            varcd: Optional indicator code for single indicator

        Returns:
            CatalogueResponse with list of indicators

        Example:
            >>> client = CatalogueClient()
            >>> response = client.get_catalogue_response()
            >>> print(f"Total: {response.total_count} indicators")
        """
        indicators = [self.get_indicator(varcd)] if varcd else self.get_main_indicators()

        return CatalogueResponse(
            indicators=indicators, language=self.language, total_count=len(indicators)
        )

    def _parse_catalogue_xml(self, xml_string: str) -> list[Indicator]:
        """Parse XML catalogue response into list of Indicators.

        Args:
            xml_string: Raw XML response from API

        Returns:
            List of parsed Indicator objects

        Raises:
            DataProcessingError: If XML parsing fails
        """
        try:
            root = ET.fromstring(xml_string)

            indicators: list[Indicator] = []

            # Find all <indicator> elements directly under the <catalog> root
            indicator_elements = root.findall(".//indicator")

            if not indicator_elements:
                logger.warning("Could not find any <indicator> elements in XML")
                return indicators

            logger.debug(f"Found {len(indicator_elements)} indicator(s) in XML")

            for indicator_elem in indicator_elements:
                indicator = self._parse_indicator_xml(indicator_elem)
                if indicator:
                    indicators.append(indicator)

            return indicators

        except ET.ParseError as e:
            logger.error(f"XML parsing error: {str(e)}")
            raise DataProcessingError(f"Invalid XML response: {str(e)}") from e
        except Exception as e:
            logger.error(f"Failed to parse XML response: {str(e)}")
            raise DataProcessingError(f"Failed to parse catalogue: {str(e)}") from e

    def _parse_indicator_xml(self, indicator_elem: ET.Element) -> Optional[Indicator]:
        """Parse a single <indicator> element into an Indicator.

        Args:
            indicator_elem: XML element representing one indicator

        Returns:
            Parsed Indicator object or None if parsing fails
        """
        try:
            # Extract fields using new tag names
            varcd = self._get_element_text(indicator_elem, "varcd")
            if not varcd:
                logger.warning("Found indicator without varcd, skipping")
                return None

            title = self._get_element_text(indicator_elem, "title")
            theme = self._get_element_text(indicator_elem, "theme")
            subtheme = self._get_element_text(indicator_elem, "subtheme")
            periodicity = self._get_element_text(indicator_elem, "periodicity")
            geo_last_level = self._get_element_text(indicator_elem, "geo_lastlevel")
            source = self._get_element_text(indicator_elem, "source")

            # URLs are nested under <html> and <json>
            html_elem = indicator_elem.find("html")
            html_url = self._get_element_text(html_elem, "bdd_url") if html_elem is not None else ""

            json_elem = indicator_elem.find("json")
            metadata_url = (
                self._get_element_text(json_elem, "json_metainfo") if json_elem is not None else ""
            )
            data_url = (
                self._get_element_text(json_elem, "json_dataset") if json_elem is not None else ""
            )

            # Parse last_period and last_update from <dates>
            last_period = None
            last_update = None
            dates_elem = indicator_elem.find("dates")
            if dates_elem is not None:
                last_period = self._get_element_text(dates_elem, "last_period_available")
                last_update_str = self._get_element_text(dates_elem, "last_update")
                if last_update_str:
                    try:
                        # The date format is 'DD-MM-YYYY'
                        last_update = datetime.strptime(last_update_str, "%d-%m-%Y")
                    except ValueError:
                        logger.debug(f"Could not parse date: {last_update_str}")

            description = self._get_element_text(indicator_elem, "description")
            unit = self._get_element_text(indicator_elem, "unit")

            # Create Indicator object
            indicator = Indicator(
                varcd=varcd,
                title=title,
                description=description or None,
                theme=theme or None,
                subtheme=subtheme or None,
                periodicity=periodicity or None,
                last_period=last_period or None,
                last_update=last_update,
                geo_last_level=geo_last_level or None,
                html_url=html_url or None,
                metadata_url=metadata_url or None,
                data_url=data_url or None,
                source=source or None,  # Added source field
                unit=unit or None,
            )

            return indicator

        except Exception as e:
            logger.warning(f"Failed to parse indicator XML: {str(e)}")
            return None
