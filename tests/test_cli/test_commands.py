"""Tests for CLI commands."""

import json
from pathlib import Path

import responses
from click.testing import CliRunner

from pyptine.cli.main import cli


class TestSearchCommand:
    """Tests for search command."""

    @responses.activate
    def test_search_basic(self, sample_catalogue):
        """Test basic search command."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
            content_type="application/xml",
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["search", "population"])

        assert result.exit_code == 0
        assert "0004167" in result.output  # Check for indicator code
        assert "Indicators" in result.output  # Check for table title

    @responses.activate
    def test_search_with_theme(self, sample_catalogue):
        """Test search with theme filter."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
            content_type="application/xml",
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["search", "population", "--theme", "Population"])

        assert result.exit_code == 0

    @responses.activate
    def test_search_with_limit(self, sample_catalogue):
        """Test search with result limit."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
            content_type="application/xml",
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["search", "population", "--limit", "5"])

        assert result.exit_code == 0

    @responses.activate
    def test_search_no_results(self, sample_catalogue):
        """Test search with no results."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
            content_type="application/xml",
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["search", "nonexistent_keyword_12345"])

        assert result.exit_code == 1
        assert "No indicators found" in result.output


class TestInfoCommand:
    """Tests for info command."""

    @responses.activate
    def test_info_basic(self, sample_catalogue, sample_metadata):
        """Test basic info command."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
            content_type="application/xml",
        )

        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindicaMeta.jsp",
            json=sample_metadata,
            status=200,
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["info", "0004167"])

        assert result.exit_code == 0
        assert "Indicator Information" in result.output
        assert "0004167" in result.output

    @responses.activate
    def test_info_with_language(self, sample_catalogue, sample_metadata):
        """Test info command with language option."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
            content_type="application/xml",
        )

        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindicaMeta.jsp",
            json=sample_metadata,
            status=200,
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["info", "0004167", "--lang", "PT"])

        assert result.exit_code == 0


class TestDownloadCommand:
    """Tests for download command."""

    @responses.activate
    def test_download_csv(self, sample_metadata, sample_data, tmp_path):
        """Test download to CSV."""
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

        runner = CliRunner()
        output_file = tmp_path / "test_output.csv"

        result = runner.invoke(
            cli, ["download", "0004167", "--output", str(output_file), "--output-format", "csv"]
        )

        assert result.exit_code == 0
        assert output_file.exists()
        assert "Data saved" in result.output

    @responses.activate
    def test_download_json(self, sample_data, tmp_path):
        """Test download to JSON."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindica.jsp",
            json=sample_data,
            status=200,
        )

        runner = CliRunner()
        output_file = tmp_path / "test_output.json"

        result = runner.invoke(
            cli, ["download", "0004167", "--output", str(output_file), "--output-format", "json"]
        )

        assert result.exit_code == 0
        assert output_file.exists()

        # Verify JSON is valid
        with open(output_file) as f:
            data = json.load(f)
        assert isinstance(data, dict)

    @responses.activate
    def test_download_default_filename(self, sample_data, tmp_path):
        """Test download with default filename."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindica.jsp",
            json=sample_data,
            status=200,
        )

        runner = CliRunner()
        # Run in temp directory
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["download", "0004167", "--output-format", "csv"])
            print(f"CLI result output: {result.output}")
            print(f"CLI result exit_code: {result.exit_code}")
            print(f"Current working directory in test: {Path.cwd()}")
            print(f"Expected file path: {Path('0004167.csv').absolute()}")

            assert result.exit_code == 0
            assert Path("0004167.csv").exists()

    @responses.activate
    def test_download_with_dimensions(self, sample_metadata, sample_data, tmp_path):
        """Test download with dimension filters."""
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

        runner = CliRunner()
        output_file = tmp_path / "filtered.csv"

        result = runner.invoke(
            cli,
            [
                "download",
                "0004167",
                "--output",
                str(output_file),
                "--dimension",
                "Dim1=2020",
            ],
        )

        assert result.exit_code == 0
        assert output_file.exists()


class TestDimensionsCommand:
    """Tests for dimensions command."""

    @responses.activate
    def test_dimensions_basic(self, sample_metadata):
        """Test basic dimensions command."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/json_indicador/pindicaMeta.jsp",
            json=sample_metadata,
            status=200,
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["dimensions", "0004167"])

        assert result.exit_code == 0
        assert "Dim1" in result.output or "Dimensions" in result.output


class TestListCommands:
    """Tests for list commands."""

    @responses.activate
    def test_list_themes(self, sample_catalogue):
        """Test list themes command."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
            content_type="application/xml",
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["list-commands", "themes"])

        assert result.exit_code == 0
        assert "Population" in result.output or "Themes" in result.output

    @responses.activate
    def test_list_indicators(self, sample_catalogue):
        """Test list indicators command."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
            content_type="application/xml",
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["list-commands", "indicators"])

        assert result.exit_code == 0
        assert "Indicators" in result.output
        assert "0004167" in result.output
        assert "0008074" in result.output

    @responses.activate
    def test_list_indicators_with_theme(self, sample_catalogue):
        """Test list indicators with theme filter."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
            content_type="application/xml",
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["list-commands", "indicators", "--theme", "Population"])

        assert result.exit_code == 0

    @responses.activate
    def test_list_indicators_with_limit(self, sample_catalogue):
        """Test list indicators with custom limit."""
        responses.add(
            responses.GET,
            "https://www.ine.pt/ine/xml_indic.jsp",
            body=sample_catalogue,
            status=200,
            content_type="application/xml",
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["list-commands", "indicators", "--limit", "1"])

        assert result.exit_code == 0
        assert "Indicators" in result.output
        assert "0004167" in result.output
        assert "of 2" in result.output  # Assuming sample_catalogue has 2 indicators


class TestCacheCommands:
    """Tests for cache commands."""

    def test_cache_info(self):
        """Test cache info command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["cache", "info"])

        assert result.exit_code == 0
        assert "Cache" in result.output

    def test_cache_clear(self, tmp_path):
        """Test cache clear command."""
        runner = CliRunner()

        # Use --yes to skip confirmation
        result = runner.invoke(cli, ["cache", "clear"], input="y\n")

        assert result.exit_code == 0
        assert "cleared" in result.output.lower() or "Cache cleared" in result.output


class TestCLIHelp:
    """Tests for CLI help and version."""

    def test_cli_help(self):
        """Test main help command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "pyptine" in result.output.lower()
        assert "search" in result.output.lower()

    def test_cli_version(self):
        """Test version command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "version" in result.output.lower() or "0.1.0" in result.output

    def test_search_help(self):
        """Test search command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["search", "--help"])

        assert result.exit_code == 0
        assert "keyword" in result.output.lower()

    def test_download_help(self):
        """Test download command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["download", "--help"])

        assert result.exit_code == 0
        assert "output" in result.output.lower()


class TestExceptionHandling:
    """Tests for CLI exception handling."""

    @responses.activate
    def test_exception_is_handled(self, monkeypatch):
        """Test that a generic INEError is handled."""
        # Mock the INE class to raise an exception
        from pyptine.utils.exceptions import INEError

        def mock_get_indicator(*args, **kwargs):
            raise INEError("A test error occurred")

        monkeypatch.setattr("pyptine.INE.get_indicator", mock_get_indicator)

        runner = CliRunner()
        result = runner.invoke(cli, ["info", "0004167"])

        assert result.exit_code == 1
        assert "API Error" in result.output or "A test error occurred" in result.output
