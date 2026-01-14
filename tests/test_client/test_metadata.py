"""Tests for MetadataClient."""

import pytest
import responses

from pyine.client.metadata import MetadataClient
from pyine.models.indicator import Dimension, DimensionValue, IndicatorMetadata
from pyine.utils.exceptions import APIError


@pytest.fixture
def metadata_client():
    """Create MetadataClient instance."""
    return MetadataClient(language="EN", cache_enabled=False)


class TestMetadataClient:
    """Tests for MetadataClient."""

    @responses.activate
    def test_get_metadata_success(self, metadata_client, sample_metadata):
        """Test successful metadata retrieval."""
        # Mock the API response
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindicaMeta.jsp",
            json=sample_metadata,
            status=200,
        )

        # Get metadata
        metadata = metadata_client.get_metadata("0004167")

        # Verify response
        assert isinstance(metadata, IndicatorMetadata)
        assert metadata.varcd == "0004167"
        assert metadata.language == "EN"
        assert len(metadata.dimensions) == 2

        # Verify first dimension
        dim1 = metadata.dimensions[0]
        assert isinstance(dim1, Dimension)
        assert dim1.name == "Period"
        assert len(dim1.values) > 0
        assert isinstance(dim1.values[0], DimensionValue)

    @responses.activate
    def test_get_dimensions(self, metadata_client, sample_metadata):
        """Test getting dimensions list."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindicaMeta.jsp",
            json=sample_metadata,
            status=200,
        )

        dimensions = metadata_client.get_dimensions("0004167")

        assert isinstance(dimensions, list)
        assert len(dimensions) == 2
        assert all(isinstance(d, Dimension) for d in dimensions)

    @responses.activate
    def test_get_dimension_values(self, metadata_client, sample_metadata):
        """Test getting values for specific dimension."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindicaMeta.jsp",
            json=sample_metadata,
            status=200,
        )

        values = metadata_client.get_dimension_values("0004167", 1)

        assert isinstance(values, list)
        assert len(values) > 0
        assert all(isinstance(v, DimensionValue) for v in values)
        assert values[0].code == "2011"
        assert values[0].label == "2011"

    @responses.activate
    def test_get_dimension_values_invalid_id(self, metadata_client, sample_metadata):
        """Test getting values for non-existent dimension."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindicaMeta.jsp",
            json=sample_metadata,
            status=200,
        )

        with pytest.raises(ValueError, match="Dimension 999 not found"):
            metadata_client.get_dimension_values("0004167", 999)

    @responses.activate
    def test_metadata_with_missing_fields(self, metadata_client):
        """Test metadata parsing with missing optional fields."""
        minimal_metadata = {
            "indicador": "0004167",
            "nome": "Test Indicator",
            "lang": "EN",
            "dimensoes": [],
        }

        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindicaMeta.jsp",
            json=minimal_metadata,
            status=200,
        )

        metadata = metadata_client.get_metadata("0004167")

        assert metadata.varcd == "0004167"
        assert metadata.title == "Test Indicator"
        assert metadata.unit is None
        assert metadata.source is None
        assert len(metadata.dimensions) == 0

    @responses.activate
    def test_api_error_handling(self, metadata_client):
        """Test handling of API errors."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindicaMeta.jsp",
            status=404,
        )

        with pytest.raises(APIError):  # Should raise APIError from base client
            metadata_client.get_metadata("invalid")

    def test_context_manager(self):
        """Test client can be used as context manager."""
        with MetadataClient(language="EN") as client:
            assert client is not None
            assert isinstance(client, MetadataClient)
