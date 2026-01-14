"""End-to-end integration tests for pyine."""

import json
import pandas as pd
import pytest
import responses
from pathlib import Path

from pyine import INE


class TestINEIntegration:
    """Integration tests for INE class."""

    @responses.activate
    def test_basic_workflow(self, sample_catalogue, sample_metadata, sample_data, tmp_path):
        """Test basic workflow: search, get data, export."""
        # Mock catalogue endpoint
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
            content_type="application/xml",
        )

        # Mock metadata endpoint
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindicaMeta.jsp",
            json=sample_metadata,
            status=200,
        )

        # Mock data endpoint
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindica.jsp",
            json=sample_data,
            status=200,
        )

        # Initialize client
        ine = INE(language="EN", cache=False)

        # Search for indicators
        results = ine.search("population")
        assert len(results) > 0
        assert any("population" in ind.title.lower() for ind in results)

        # Get data as DataFrame
        response = ine.get_data("0004167")
        df = response.to_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert not df.empty

        # Get data as JSON
        json_output_file = tmp_path / "basic_workflow_output.json"
        response.to_json(json_output_file)
        assert json_output_file.exists()
        assert "0004167" in json_output_file.read_text()

        # Get data as dict
        data_dict = response.to_dict()
        assert isinstance(data_dict, dict)

    @responses.activate
    def test_metadata_and_dimensions(self, sample_metadata):
        """Test metadata and dimension retrieval."""
        # Mock metadata endpoint
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindicaMeta.jsp",
            json=sample_metadata,
            status=200,
        )

        ine = INE(language="EN", cache=False)

        # Get metadata
        metadata = ine.get_metadata("0004167")
        assert metadata.varcd == "0004167"
        assert metadata.title
        assert len(metadata.dimensions) > 0

        # Get dimensions
        dimensions = ine.get_dimensions("0004167")
        assert len(dimensions) > 0
        assert all(hasattr(dim, "name") for dim in dimensions)
        assert all(hasattr(dim, "values") for dim in dimensions)

    @responses.activate
    def test_export_csv(self, sample_metadata, sample_data, tmp_path):
        """Test CSV export functionality."""
        # Mock endpoints
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindicaMeta.jsp",
            json=sample_metadata,
            status=200,
        )

        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindica.jsp",
            json=sample_data,
            status=200,
        )

        ine = INE(language="EN", cache=False)

        # Export to CSV
        output_file = tmp_path / "test_export.csv"
        ine.export_csv("0004167", output_file)

        # Verify file exists and has content
        assert output_file.exists()
        assert output_file.stat().st_size > 0

        # Read back and verify
        df = pd.read_csv(output_file, comment="#")
        assert not df.empty

    @responses.activate
    def test_export_json(self, sample_data, tmp_path):
        """Test JSON export functionality."""
        # Mock data endpoint
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindica.jsp",
            json=sample_data,
            status=200,
        )

        ine = INE(language="EN", cache=False)

        # Export to JSON
        output_file = tmp_path / "test_export.json"
        ine.export_json("0004167", output_file)
        assert output_file.exists()

        # Verify JSON content
        with open(output_file) as f:
            data = json.load(f)
        assert isinstance(data, dict)
        assert data["varcd"] == "0004167"
        assert "data" in data
        assert len(data["data"]) > 0
        assert output_file.stat().st_size > 0

    @responses.activate
    def test_theme_filtering(self, sample_catalogue):
        """Test theme-based filtering."""
        # Mock catalogue endpoint
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
            content_type="application/xml",
        )

        ine = INE(language="EN", cache=False)

        # Get all themes
        themes = ine.list_themes()
        assert len(themes) > 0

        # Filter by theme
        if themes:
            indicators = ine.search(query="", theme=themes[0])
            assert all(ind.theme == themes[0] for ind in indicators if ind.theme)

    @responses.activate
    def test_indicator_validation(self, sample_catalogue):
        """Test indicator validation."""
        # Mock catalogue endpoint
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
            content_type="application/xml",
        )

        ine = INE(language="EN", cache=False)

        # Valid indicator
        assert ine.validate_indicator("0004167")

        # Mock invalid indicator
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            json={"error": "Invalid indicator"},
            status=404,
        )

        # Invalid indicator
        assert not ine.validate_indicator("invalid_code")

    def test_cache_management(self, tmp_path):
        """Test cache management."""
        # Initialize with cache
        ine = INE(language="EN", cache=True, cache_dir=tmp_path)

        # Get cache info
        info = ine.get_cache_info()
        assert info["enabled"] is True
        assert "metadata_cache" in info
        assert "data_cache" in info

        # Clear cache
        ine.clear_cache()

        # Test without cache
        ine_no_cache = INE(language="EN", cache=False)
        info = ine_no_cache.get_cache_info()
        assert info["enabled"] is False

    @responses.activate
    def test_dimension_filtering(self, sample_metadata, sample_data):
        """Test data filtering by dimensions."""
        # Mock endpoints
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindicaMeta.jsp",
            json=sample_metadata,
            status=200,
        )

        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindica.jsp",
            json=sample_data,
            status=200,
        )

        ine = INE(language="EN", cache=False)

        # Get dimensions
        dimensions = ine.get_dimensions("0004167")
        assert len(dimensions) > 0

        # Get data with dimension filter
        if dimensions and dimensions[0].values:
            dim_filter = {"Dim1": dimensions[0].values[0].code}
            response = ine.get_data("0004167", dimensions=dim_filter)
            df = response.to_dataframe()
            assert isinstance(df, pd.DataFrame)

    def test_language_setting(self):
        """Test language configuration."""
        # English
        ine_en = INE(language="EN")
        assert ine_en.language == "EN"

        # Portuguese
        ine_pt = INE(language="PT")
        assert ine_pt.language == "PT"

        # Case insensitive
        ine_lower = INE(language="en")
        assert ine_lower.language == "EN"

        # Invalid language
        with pytest.raises(ValueError, match="Language must be"):
            INE(language="FR")

    @responses.activate
    def test_error_handling(self):
        """Test error handling for API failures."""
        # Mock API error
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindica.jsp",
            json={"error": "Internal server error"},
            status=500,
        )

        ine = INE(language="EN", cache=False)

        from pyine.utils.exceptions import APIError

        # Should raise APIError after retries
        with pytest.raises(APIError):  # Will be APIError or similar
            ine.get_data("0004167")
