"""Tests for CatalogueBrowser functionality."""

import pytest
import responses

from pyptine.client.catalogue import CatalogueClient
from pyptine.models.indicator import Indicator
from pyptine.search.catalog import CatalogueBrowser


class TestCatalogueBrowser:
    """Tests for CatalogueBrowser class."""

    @pytest.fixture
    def browser(self):
        """Create browser instance."""
        client = CatalogueClient(language="EN", cache_enabled=False)
        return CatalogueBrowser(client, language="EN")

    @responses.activate
    def test_get_all_indicators(self, browser, sample_catalogue):
        """Test fetching all indicators."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
            content_type="application/xml",
        )

        indicators = browser.get_all_indicators()

        assert len(indicators) > 0
        assert all(isinstance(ind, Indicator) for ind in indicators)

    @responses.activate
    def test_search_basic(self, browser, sample_catalogue):
        """Test basic search functionality."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
            content_type="application/xml",
        )

        results = browser.search("population")

        assert len(results) > 0
        assert all(isinstance(ind, Indicator) for ind in results)

        # Check that results match search query
        for ind in results:
            text_fields = [
                ind.title.lower(),
                (ind.description or "").lower(),
                " ".join(ind.keywords).lower(),
            ]
            assert any("population" in field for field in text_fields)

    @responses.activate
    def test_search_case_sensitive(self, browser, sample_catalogue):
        """Test case-sensitive search."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
            content_type="application/xml",
        )

        # Case-insensitive (default)
        results_ci = browser.search("POPULATION")
        assert len(results_ci) > 0

        # Case-sensitive
        browser.search("POPULATION", case_sensitive=True)
        # May have fewer results than case-insensitive

    @responses.activate
    def test_search_specific_fields(self, browser, sample_catalogue):
        """Test searching specific fields."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
            content_type="application/xml",
        )

        # Search only in title
        results = browser.search("population", search_fields=["title"])
        assert all(isinstance(ind, Indicator) for ind in results)

    @responses.activate
    def test_search_empty_query(self, browser, sample_catalogue):
        """Test search with empty query."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
            content_type="application/xml",
        )
        results = browser.search("")
        assert len(results) > 0
        assert all(isinstance(ind, Indicator) for ind in results)

    @responses.activate
    def test_list_themes(self, browser, sample_catalogue):
        """Test listing all themes."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
            content_type="application/xml",
        )

        themes = browser.list_themes()

        assert isinstance(themes, list)
        assert all(isinstance(theme, str) for theme in themes)
        # Themes should be sorted
        assert themes == sorted(themes)

    @responses.activate
    def test_list_subthemes(self, browser, sample_catalogue):
        """Test listing subthemes."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
            content_type="application/xml",
        )

        # Get all subthemes
        subthemes = browser.list_subthemes()
        assert isinstance(subthemes, list)

        # Get subthemes for specific theme
        themes = browser.list_themes()
        if themes:
            theme_subthemes = browser.search(query="", theme=themes[0])
            assert isinstance(theme_subthemes, list)

    @responses.activate
    def test_get_recently_updated(self, browser, sample_catalogue):
        """Test getting recently updated indicators."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
            content_type="application/xml",
        )

        recent = browser.get_recently_updated(limit=5)

        assert len(recent) <= 5
        assert all(isinstance(ind, Indicator) for ind in recent)

        # Check that indicators with dates are included
        if len(recent) > 1:
            # Should be sorted by date descending
            for i in range(len(recent) - 1):
                if recent[i].last_update and recent[i + 1].last_update:
                    assert recent[i].last_update >= recent[i + 1].last_update

    @responses.activate
    def test_get_by_code(self, browser, sample_catalogue):
        """Test getting indicator by code."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
            content_type="application/xml",
        )

        indicator = browser.get_by_code("0004167")

        assert indicator is not None
        assert isinstance(indicator, Indicator)
        assert indicator.varcd == "0004167"

    @responses.activate
    def test_get_by_code_invalid(self, browser):
        """Test getting invalid indicator code."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            json={"error": "Not found"},
            status=404,
        )

        indicator = browser.get_by_code("invalid")
        assert indicator is None

    @responses.activate
    def test_validate_indicator(self, browser, sample_catalogue):
        """Test indicator validation."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
            content_type="application/xml",
        )

        # Valid indicator
        assert browser.validate_indicator("0004167") is True

        # Invalid indicator (will fail when trying to get it)
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            json={"error": "Not found"},
            status=404,
        )

        assert browser.validate_indicator("invalid") is False

    @responses.activate
    def test_cache_functionality(self, browser, sample_catalogue):
        """Test cache clearing."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
            content_type="application/xml",
        )

        # First call - fetches from API
        indicators1 = browser.get_all_indicators()
        assert len(indicators1) > 0

        # Second call - uses cache
        indicators2 = browser.get_all_indicators(use_cache=True)
        assert len(indicators2) == len(indicators1)

        # Clear cache
        browser.clear_cache()

        # Third call - fetches from API again
        indicators3 = browser.get_all_indicators(use_cache=False)
        assert len(indicators3) == len(indicators1)

    @responses.activate
    def test_exact_match_search(self, browser, sample_catalogue):
        """Test exact match search."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
            content_type="application/xml",
        )

        # Substring match (default)
        results_substring = browser.search("pop", exact_match=False)

        # Exact match
        results_exact = browser.search("pop", exact_match=True)

        # Exact match should return fewer or equal results
        assert len(results_exact) <= len(results_substring)
