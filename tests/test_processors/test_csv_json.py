"""Tests for CSV and JSON processing utilities."""

import json

import pandas as pd

from pyine.processors.csv import export_to_csv, read_csv_with_metadata
from pyine.processors.json import (
    export_to_json,
    export_to_jsonl,
    flatten_json,
    format_json,
    read_jsonl,
    unflatten_json,
)


class TestCSVExport:
    """Tests for CSV export functionality."""

    def test_basic_export(self, tmp_path):
        """Test basic CSV export."""
        df = pd.DataFrame({"value": [1, 2, 3], "name": ["A", "B", "C"]})
        output = tmp_path / "test.csv"

        export_to_csv(df, output, include_metadata=False)

        assert output.exists()

        # Read back
        df_read = pd.read_csv(output)
        assert len(df_read) == 3

    def test_export_with_metadata(self, tmp_path):
        """Test CSV export with metadata header."""
        df = pd.DataFrame({"value": [1, 2, 3]})
        output = tmp_path / "test_meta.csv"
        metadata = {"indicator": "0004167", "source": "INE"}

        export_to_csv(df, output, metadata=metadata)

        assert output.exists()

        # Check file content includes metadata
        with open(output) as f:
            content = f.read()
            assert "indicator" in content
            assert "0004167" in content

    def test_read_csv_with_metadata(self, tmp_path):
        """Test reading CSV with metadata."""
        df = pd.DataFrame({"value": [1, 2, 3]})
        output = tmp_path / "test_read.csv"
        metadata = {"indicator": "0004167", "unit": "No."}

        export_to_csv(df, output, metadata=metadata)

        # Read back
        df_read, meta_read = read_csv_with_metadata(output)

        assert len(df_read) == 3
        assert "indicator" in meta_read
        assert meta_read["indicator"] == "0004167"

    def test_utf8_encoding(self, tmp_path):
        """Test UTF-8 encoding for Portuguese characters."""
        df = pd.DataFrame({"região": ["Norte", "Sul"], "população": [1000, 2000]})
        output = tmp_path / "test_utf8.csv"

        export_to_csv(df, output)

        # Read back
        df_read = pd.read_csv(output)
        assert "região" in df_read.columns


class TestJSONExport:
    """Tests for JSON export functionality."""

    def test_format_json_pretty(self):
        """Test pretty JSON formatting."""
        data = {"indicator": "0004167", "values": [1, 2, 3]}

        json_str = format_json(data, pretty=True)

        assert isinstance(json_str, str)
        assert "indicator" in json_str
        assert "\n" in json_str  # Pretty print includes newlines

    def test_format_json_compact(self):
        """Test compact JSON formatting."""
        data = {"indicator": "0004167"}

        json_str = format_json(data, pretty=False)

        assert "\n" not in json_str  # Compact has no newlines

    def test_export_to_json(self, tmp_path):
        """Test JSON file export."""
        data = {"indicator": "0004167", "values": [1, 2, 3]}
        output = tmp_path / "test.json"

        export_to_json(data, output)

        assert output.exists()

        # Read back
        with open(output) as f:
            data_read = json.load(f)

        assert data_read == data

    def test_export_to_jsonl(self, tmp_path):
        """Test JSON Lines export."""
        data = [
            {"id": 1, "value": 100},
            {"id": 2, "value": 200},
        ]
        output = tmp_path / "test.jsonl"

        export_to_jsonl(data, output)

        assert output.exists()

        # Read back
        data_read = read_jsonl(output)

        assert len(data_read) == 2
        assert data_read[0]["id"] == 1

    def test_read_jsonl_with_limit(self, tmp_path):
        """Test reading JSON Lines with max lines limit."""
        data = [{"id": i} for i in range(10)]
        output = tmp_path / "test_limit.jsonl"

        export_to_jsonl(data, output)

        # Read only first 3 lines
        data_read = read_jsonl(output, max_lines=3)

        assert len(data_read) == 3


class TestJSONFlattening:
    """Tests for JSON flattening/unflattening."""

    def test_flatten_json(self):
        """Test flattening nested JSON."""
        nested = {"indicator": "0004167", "metadata": {"source": "INE", "year": 2023}}

        flattened = flatten_json(nested)

        assert "indicator" in flattened
        assert "metadata.source" in flattened
        assert flattened["metadata.source"] == "INE"

    def test_flatten_with_list(self):
        """Test flattening JSON with lists."""
        nested = {"values": [1, 2, 3], "items": [{"name": "A"}, {"name": "B"}]}

        flattened = flatten_json(nested)

        assert "values[0]" in flattened
        assert "items[0].name" in flattened
        assert flattened["items[0].name"] == "A"

    def test_unflatten_json(self):
        """Test unflattening JSON."""
        flattened = {"indicator": "0004167", "metadata.source": "INE", "metadata.year": 2023}

        nested = unflatten_json(flattened)

        assert "indicator" in nested
        assert "metadata" in nested
        assert nested["metadata"]["source"] == "INE"

    def test_flatten_unflatten_roundtrip(self):
        """Test flatten and unflatten roundtrip."""
        original = {"indicator": "0004167", "metadata": {"source": "INE", "year": 2023}}

        flattened = flatten_json(original)
        restored = unflatten_json(flattened)

        assert restored["indicator"] == original["indicator"]
        assert restored["metadata"]["source"] == original["metadata"]["source"]

    def test_custom_separator(self):
        """Test flattening with custom separator."""
        nested = {"a": {"b": {"c": 1}}}

        flattened = flatten_json(nested, separator="_")

        assert "a_b_c" in flattened
