"""Tests for CatalogueClient."""

import pytest
import responses

from pyptine.client.catalogue import CatalogueClient
from pyptine.models.indicator import Indicator
from pyptine.models.response import CatalogueResponse
from pyptine.utils.exceptions import APIError, DataProcessingError


@pytest.fixture
def catalogue_client():
    """Create CatalogueClient instance."""
    return CatalogueClient(language="EN", cache_enabled=False)


class TestCatalogueClient:
    """Tests for CatalogueClient."""

    @responses.activate
    def test_get_indicator_success(self, catalogue_client, sample_catalogue):
        """Test successful single indicator retrieval."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
            content_type="text/xml",
        )

        indicator = catalogue_client.get_indicator("0004167")

        assert isinstance(indicator, Indicator)
        assert indicator.varcd == "0004167"
        assert indicator.title is not None
        assert indicator.theme is not None

    @responses.activate
    def test_get_indicator_verifies_params(self, catalogue_client, sample_catalogue):
        """Test that get_indicator sends correct parameters."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
        )

        catalogue_client.get_indicator("0004167")

        # Verify request parameters
        assert len(responses.calls) == 1
        request_url = responses.calls[0].request.url
        assert "opc=1" in request_url  # Single indicator
        assert "varcd=0004167" in request_url
        assert "lang=EN" in request_url

    @responses.activate
    def test_get_main_indicators(self, catalogue_client, sample_catalogue):
        """Test retrieving main indicators group."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
        )

        indicators = catalogue_client.get_main_indicators()

        assert isinstance(indicators, list)
        assert len(indicators) == 2  # Sample fixture has 2 indicators
        assert all(isinstance(ind, Indicator) for ind in indicators)

    @responses.activate
    def test_get_main_indicators_verifies_params(self, catalogue_client, sample_catalogue):
        """Test that get_main_indicators sends correct parameters."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
        )

        catalogue_client.get_main_indicators()

        # Verify request parameters
        request_url = responses.calls[0].request.url
        assert "opc=3" in request_url  # Main indicators group

    @responses.activate
    def test_get_catalogue_response_single(self, catalogue_client, sample_catalogue):
        """Test get_catalogue_response for single indicator."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
        )

        response = catalogue_client.get_catalogue_response(varcd="0004167")

        assert isinstance(response, CatalogueResponse)
        assert response.total_count == 1
        assert len(response) == 1
        assert response.language == "EN"

    @responses.activate
    def test_get_catalogue_response_all(self, catalogue_client, sample_catalogue):
        """Test get_catalogue_response for all indicators."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
        )

        response = catalogue_client.get_catalogue_response()

        assert isinstance(response, CatalogueResponse)
        assert response.total_count == 2
        assert len(response) == 2

    @responses.activate
    def test_catalogue_response_iteration(self, catalogue_client, sample_catalogue):
        """Test iterating over CatalogueResponse."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
        )

        response = catalogue_client.get_catalogue_response()

        # Test iteration
        for indicator in response:
            assert isinstance(indicator, Indicator)

        # Test indexing
        assert isinstance(response[0], Indicator)

    @responses.activate
    def test_parse_indicator_fields(self, catalogue_client, sample_catalogue):
        """Test parsing of all indicator fields from XML."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
        )

        indicator = catalogue_client.get_indicator("0004167")

        # Check all expected fields
        assert indicator.varcd == "0004167"
        assert indicator.title is not None
        assert indicator.theme == "Population"
        assert indicator.subtheme == "Demographic estimates"
        assert indicator.periodicity == "Annual"
        assert indicator.last_period == "2023"
        assert indicator.geo_last_level == "Municipality"
        assert indicator.html_url is not None
        assert indicator.metadata_url is not None
        assert indicator.data_url is not None

    @responses.activate
    def test_invalid_xml(self, catalogue_client):
        """Test handling of invalid XML response."""
        invalid_xml = "<broken><xml"

        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=invalid_xml,
            status=200,
        )

        with pytest.raises(DataProcessingError, match="Invalid XML"):
            catalogue_client.get_indicator("0004167")

    @responses.activate
    def test_empty_xml_response(self, catalogue_client):
        """Test handling of empty XML response."""
        empty_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <diffgr:diffgram xmlns:msdata="urn:schemas-microsoft-com:xml-msdata"
                         xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1">
            <NewDataSet xmlns="">
            </NewDataSet>
        </diffgr:diffgram>
        """

        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=empty_xml,
            status=200,
        )

        with pytest.raises(DataProcessingError, match="not found in catalogue"):
            catalogue_client.get_indicator("0004167")

    @responses.activate
    def test_api_error_handling(self, catalogue_client):
        """Test handling of API errors."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            status=500,
        )

        with pytest.raises(APIError):
            catalogue_client.get_indicator("0004167")

    @responses.activate
    def test_datetime_parsing(self, catalogue_client):
        """Test parsing of last_update datetime field."""
        xml_with_date = """<?xml version="1.0" encoding="UTF-8"?>
        <catalog>
            <indicator id="0004167">
                <varcd>0004167</varcd>
                <title>Test Indicator</title>
                <dates>
                    <last_update>14-06-2024</last_update>
                </dates>
            </indicator>
        </catalog>
        """

        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=xml_with_date,
            status=200,
        )

        indicator = catalogue_client.get_indicator("0004167")

        assert indicator.last_update is not None
        assert indicator.last_update.year == 2024
        assert indicator.last_update.month == 6
        assert indicator.last_update.day == 14
