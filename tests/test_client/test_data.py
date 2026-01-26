"""Tests for DataClient."""

from unittest.mock import MagicMock

import pytest
import responses

from pyptine.client.data import DataClient
from pyptine.client.metadata import MetadataClient
from pyptine.models.indicator import Dimension, DimensionValue, IndicatorMetadata
from pyptine.models.response import DataResponse
from pyptine.utils.exceptions import APIError, DimensionError


@pytest.fixture
def metadata_client_mock():
    """Mock MetadataClient instance."""
    mock = MagicMock(spec=MetadataClient)
    # Configure the mock to return a sample IndicatorMetadata
    mock.get_metadata.return_value = IndicatorMetadata(
        varcd="0004167",
        title="Resident population",
        language="EN",
        dimensions=[
            Dimension(
                id=1,
                name="Period",
                values=[
                    DimensionValue(code="2020", label="2020"),
                    DimensionValue(code="2021", label="2021"),
                    DimensionValue(code="2023", label="2023"),
                ],
            ),
            Dimension(
                id=2,
                name="Geographic localization",
                values=[
                    DimensionValue(code="1", label="Portugal"),
                    DimensionValue(code="2", label="North"),
                ],
            ),
        ],
    )
    return mock


@pytest.fixture
def data_client(metadata_client_mock):
    """Create DataClient instance."""
    return DataClient(language="EN", cache_enabled=False, metadata_client=metadata_client_mock)


class TestDataClient:
    """Tests for DataClient."""

    @responses.activate
    def test_get_data_success(self, data_client, sample_data):
        """Test successful data retrieval."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindica.jsp",
            json=sample_data,
            status=200,
        )

        response = data_client.get_data("0004167")

        assert isinstance(response, DataResponse)
        assert response.varcd == "0004167"
        assert response.language == "EN"
        assert len(response.data) > 0

    @responses.activate
    def test_get_data_with_dimensions(self, data_client, sample_data):
        """Test data retrieval with dimension filters."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindica.jsp",
            json=sample_data,
            status=200,
        )

        dimensions = {"Dim1": "2023", "Dim2": "1"}
        response = data_client.get_data("0004167", dimensions=dimensions)

        assert isinstance(response, DataResponse)
        assert response.varcd == "0004167"

        # Verify the request was made with correct parameters
        assert len(responses.calls) == 1
        request_params = responses.calls[0].request.url
        assert "Dim1=2023" in request_params
        assert "Dim2=1" in request_params

    @responses.activate
    def test_invalid_dimension_key(self, data_client, metadata_client_mock):
        """Test error handling for invalid dimension keys."""
        with pytest.raises(DimensionError, match="Invalid dimension key 'Dim3'"):
            data_client._build_params("0004167", {"Dim3": "value"})

    @responses.activate
    def test_data_to_dataframe(self, data_client, sample_data):
        """Test converting data response to DataFrame."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindica.jsp",
            json=sample_data,
            status=200,
        )

        response = data_client.get_data("0004167")
        df = response.to_dataframe()

        assert df is not None
        assert len(df) == len(response.data)
        assert not df.empty

    @responses.activate
    def test_get_data_paginated(self, data_client, sample_data):
        """Test paginated data retrieval."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindica.jsp",
            json=sample_data,
            status=200,
        )

        chunks = list(data_client.get_all_data("0004167"))

        assert len(chunks) >= 1
        assert all(isinstance(chunk, DataResponse) for chunk in chunks)

    @responses.activate
    def test_process_data_point_with_numeric_value(self, data_client):
        """Test processing data point with numeric value."""
        data_point = {"periodo": "2023", "geocod": "1", "geodsg": "Portugal", "valor": "10639726"}

        processed = data_client._process_data_point(data_point)

        assert processed is not None
        assert "value" in processed
        assert isinstance(processed["value"], float)
        assert processed["value"] == 10639726.0
        assert processed["periodo"] == "2023"

    @responses.activate
    def test_process_data_point_with_null_value(self, data_client):
        """Test processing data point with null value."""
        data_point = {"periodo": "2023", "valor": None}

        processed = data_client._process_data_point(data_point)

        assert processed is not None
        assert "value" in processed
        assert processed["value"] is None

    @responses.activate
    def test_empty_data_response(self, data_client):
        """Test handling of empty data response."""
        empty_response = {"indicador": "0004167", "nome": "Test", "lang": "EN", "dados": []}

        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindica.jsp",
            json=empty_response,
            status=200,
        )

        response = data_client.get_data("0004167")

        assert isinstance(response, DataResponse)
        assert len(response.data) == 0

        df = response.to_dataframe()
        assert df.empty

    @responses.activate
    def test_api_error_handling(self, data_client):
        """Test handling of API errors."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindica.jsp",
            status=500,
        )

        with pytest.raises(APIError):
            data_client.get_data("0004167")

    def test_build_params_basic(self, data_client):
        """Test building parameters without dimensions."""
        params = data_client._build_params("0004167")

        assert "op" in params
        assert params["op"] == "2"
        assert "varcd" in params
        assert params["varcd"] == "0004167"

    @responses.activate
    def test_invalid_dimension_value(self, data_client, metadata_client_mock):
        """Test error handling for invalid dimension values."""
        with pytest.raises(DimensionError, match="Invalid value '9999' for dimension 'Dim1'"):
            data_client._build_params("0004167", {"Dim1": "9999"})

    def test_build_params_with_dimensions(self, data_client):
        """Test building parameters with dimensions."""
        dimensions = {"Dim1": "2023", "Dim2": "1"}
        params = data_client._build_params("0004167", dimensions)

        assert params["Dim1"] == "2023"
        assert params["Dim2"] == "1"
        assert params["varcd"] == "0004167"

    def test_build_params_with_pagination(self, data_client):
        """Test building parameters with pagination parameters."""
        params = data_client._build_params("0004167", offset=100, limit=50)

        assert params["start"] == "100"
        assert params["count"] == "50"
        assert params["varcd"] == "0004167"
        assert params["op"] == "2"

    def test_build_params_with_offset_only(self, data_client):
        """Test building parameters with only offset."""
        params = data_client._build_params("0004167", offset=0)

        assert params["start"] == "0"
        assert "count" not in params

    def test_build_params_with_limit_only(self, data_client):
        """Test building parameters with only limit."""
        params = data_client._build_params("0004167", limit=1000)

        assert params["count"] == "1000"
        assert "start" not in params

    @responses.activate
    def test_get_all_data_single_chunk(self, data_client, sample_data):
        """Test pagination with a single chunk (less than chunk_size)."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindica.jsp",
            json=sample_data,
            status=200,
        )

        chunks = list(data_client.get_all_data("0004167", chunk_size=40000))

        assert len(chunks) == 1
        assert isinstance(chunks[0], DataResponse)
        assert len(responses.calls) == 1
        assert "start=0" in responses.calls[0].request.url
        assert "count=40000" in responses.calls[0].request.url

    @responses.activate
    def test_get_all_data_multiple_chunks(self, data_client):
        """Test pagination with multiple chunks."""
        # Create two chunks of data
        chunk1_data = {
            "indicador": "0004167",
            "nome": "Population",
            "lang": "EN",
            "dados": [{"periodo": f"202{i}", "valor": f"1000{i}"} for i in range(5)],
        }

        chunk2_data = {
            "indicador": "0004167",
            "nome": "Population",
            "lang": "EN",
            "dados": [{"periodo": f"202{i}", "valor": f"2000{i}"} for i in range(3)],
        }

        # First request returns full chunk
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindica.jsp",
            json=chunk1_data,
            status=200,
        )

        # Second request returns partial chunk (indicating end)
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindica.jsp",
            json=chunk2_data,
            status=200,
        )

        chunks = list(data_client.get_all_data("0004167", chunk_size=5))

        # Should have 2 chunks: first with 5 points, second with 3 points
        assert len(chunks) == 2
        assert len(chunks[0].data) == 5
        assert len(chunks[1].data) == 3

        # Verify pagination parameters in requests
        assert "start=0" in responses.calls[0].request.url
        assert "count=5" in responses.calls[0].request.url
        assert "start=5" in responses.calls[1].request.url
        assert "count=5" in responses.calls[1].request.url

    @responses.activate
    def test_get_all_data_with_dimensions(self, data_client, sample_data):
        """Test pagination with dimension filters."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindica.jsp",
            json=sample_data,
            status=200,
        )

        dimensions = {"Dim1": "2023", "Dim2": "1"}
        chunks = list(data_client.get_all_data("0004167", dimensions=dimensions, chunk_size=100))

        assert len(chunks) >= 1
        # Verify dimensions are included in request
        request_url = responses.calls[0].request.url
        assert "Dim1=2023" in request_url
        assert "Dim2=1" in request_url
        assert "start=0" in request_url
        assert "count=100" in request_url
