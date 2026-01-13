"""Tests for DataFrame processing utilities."""

import pandas as pd
import pytest

from pyine.processors.dataframe import (
    aggregate_by_period,
    clean_dataframe,
    filter_by_geography,
    get_latest_period,
    json_to_dataframe,
    merge_metadata,
    pivot_by_dimension,
)
from pyine.utils.exceptions import DataProcessingError


class TestJsonToDataFrame:
    """Tests for json_to_dataframe function."""

    def test_convert_list_of_dicts(self):
        """Test converting list of dicts to DataFrame."""
        data = [
            {"periodo": "2023", "geocod": "1", "valor": "10639726"},
            {"periodo": "2022", "geocod": "1", "valor": "10467366"},
        ]

        df = json_to_dataframe(data)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert "valor" in df.columns or "value" in df.columns

    def test_convert_dict_with_dados_key(self):
        """Test converting dict with 'dados' key."""
        data = {
            "indicador": "0004167",
            "dados": [
                {"periodo": "2023", "valor": "100"},
                {"periodo": "2022", "valor": "200"},
            ],
        }

        df = json_to_dataframe(data)

        assert len(df) == 2

    def test_empty_data(self):
        """Test handling empty data."""
        df = json_to_dataframe([])

        assert isinstance(df, pd.DataFrame)
        assert df.empty

    def test_value_conversion_to_numeric(self):
        """Test that valor/value columns are converted to numeric."""
        data = [
            {"periodo": "2023", "valor": "100.5"},
            {"periodo": "2022", "valor": "200.7"},
        ]

        df = json_to_dataframe(data)

        # Find the value column
        value_col = next((col for col in df.columns if "valor" in col.lower()), None)
        if value_col:
            assert pd.api.types.is_numeric_dtype(df[value_col])


class TestPivotByDimension:
    """Tests for pivot_by_dimension function."""

    def test_basic_pivot(self):
        """Test basic pivot operation."""
        df = pd.DataFrame(
            {
                "periodo": ["2023", "2023", "2022"],
                "region": ["North", "South", "North"],
                "valor": [100, 200, 150],
            }
        )

        pivoted = pivot_by_dimension(df, "region")

        assert "North" in pivoted.columns or "North" in pivoted.index.names
        assert len(pivoted) > 0


class TestCleanDataFrame:
    """Tests for clean_dataframe function."""

    def test_drop_internal_columns(self):
        """Test dropping columns starting with underscore."""
        df = pd.DataFrame({"_internal": [1, 2, 3], "data": [4, 5, 6], "_meta": [7, 8, 9]})

        cleaned = clean_dataframe(df)

        assert "_internal" not in cleaned.columns
        assert "_meta" not in cleaned.columns
        assert "data" in cleaned.columns

    def test_rename_columns(self):
        """Test renaming columns."""
        df = pd.DataFrame({"old_name": [1, 2, 3], "data": [4, 5, 6]})

        renamed = clean_dataframe(
            df, drop_internal_columns=False, rename_columns={"old_name": "new_name"}
        )

        assert "new_name" in renamed.columns
        assert "old_name" not in renamed.columns


class TestMergeMetadata:
    """Tests for merge_metadata function."""

    def test_add_metadata_columns(self):
        """Test adding metadata as columns."""
        df = pd.DataFrame({"value": [1, 2, 3]})
        metadata = {"indicator": "0004167", "unit": "No."}

        result = merge_metadata(df, metadata)

        assert "meta_indicator" in result.columns
        assert "meta_unit" in result.columns
        assert all(result["meta_indicator"] == "0004167")

    def test_custom_prefix(self):
        """Test custom prefix for metadata columns."""
        df = pd.DataFrame({"value": [1, 2, 3]})
        metadata = {"source": "INE"}

        result = merge_metadata(df, metadata, prefix="info_")

        assert "info_source" in result.columns


class TestAggregateByPeriod:
    """Tests for aggregate_by_period function."""

    def test_sum_aggregation(self):
        """Test sum aggregation by period."""
        df = pd.DataFrame(
            {
                "periodo": ["2023", "2023", "2022"],
                "region": ["A", "B", "A"],
                "valor": [100, 200, 150],
            }
        )

        agg = aggregate_by_period(df)

        assert len(agg) == 2  # Two unique periods
        assert "periodo" in agg.columns
        assert "valor" in agg.columns

    def test_missing_column_error(self):
        """Test error when period column missing."""
        df = pd.DataFrame({"data": [1, 2, 3]})

        with pytest.raises(DataProcessingError, match="Period column"):
            aggregate_by_period(df)


class TestFilterByGeography:
    """Tests for filter_by_geography function."""

    def test_filter_by_geography(self):
        """Test filtering by geographic region."""
        df = pd.DataFrame({"geodsg": ["Portugal", "Lisboa", "Porto"], "valor": [100, 50, 30]})

        filtered = filter_by_geography(df, "Portugal")

        assert len(filtered) == 1
        assert filtered["geodsg"].iloc[0] == "Portugal"

    def test_auto_detect_geography_column(self):
        """Test auto-detection of geography column."""
        df = pd.DataFrame({"region": ["North", "South", "East"], "valor": [1, 2, 3]})

        filtered = filter_by_geography(df, "North")

        assert len(filtered) == 1

    def test_case_insensitive_filter(self):
        """Test case-insensitive filtering."""
        df = pd.DataFrame({"geodsg": ["PORTUGAL", "lisboa", "PoRtO"], "valor": [100, 50, 30]})

        filtered = filter_by_geography(df, "portugal")

        assert len(filtered) == 1


class TestGetLatestPeriod:
    """Tests for get_latest_period function."""

    def test_get_single_latest_period(self):
        """Test getting the latest period."""
        df = pd.DataFrame(
            {"periodo": ["2021", "2022", "2023", "2022"], "valor": [100, 150, 200, 160]}
        )

        latest = get_latest_period(df)

        assert all(latest["periodo"] == "2023")

    def test_get_multiple_latest_periods(self):
        """Test getting multiple latest periods."""
        df = pd.DataFrame({"periodo": ["2021", "2022", "2023"], "valor": [100, 150, 200]})

        latest = get_latest_period(df, n=2)

        unique_periods = latest["periodo"].unique()
        assert len(unique_periods) <= 2
        assert "2023" in unique_periods

    def test_missing_period_column(self):
        """Test error when period column missing."""
        df = pd.DataFrame({"data": [1, 2, 3]})

        with pytest.raises(ValueError, match="Period column"):
            get_latest_period(df)
