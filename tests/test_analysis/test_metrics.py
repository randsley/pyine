"""Tests for analysis metrics module."""

import math

import pytest

from pyptine.analysis.metrics import (
    calculate_exponential_moving_average,
    calculate_mom_change,
    calculate_moving_average,
    calculate_yoy_growth,
)


@pytest.fixture
def sample_annual_data():
    """Sample annual data for YoY growth testing."""
    return [
        {"Period": "2020", "value": 100},
        {"Period": "2021", "value": 110},
        {"Period": "2022", "value": 120},
        {"Period": "2023", "value": 132},
    ]


@pytest.fixture
def sample_monthly_data():
    """Sample monthly data for MoM change testing."""
    return [
        {"Period": "2023-01", "value": 100},
        {"Period": "2023-02", "value": 105},
        {"Period": "2023-03", "value": 110},
        {"Period": "2023-04", "value": 108},
        {"Period": "2023-05", "value": 115},
    ]


@pytest.fixture
def sample_timeseries_data():
    """Sample time series data for moving average testing."""
    return [
        {"Period": "2023-01", "value": 100},
        {"Period": "2023-02", "value": 110},
        {"Period": "2023-03", "value": 105},
        {"Period": "2023-04", "value": 120},
        {"Period": "2023-05", "value": 115},
        {"Period": "2023-06", "value": 125},
    ]


class TestYoYGrowth:
    """Tests for year-over-year growth calculation."""

    def test_yoy_growth_basic(self, sample_annual_data):
        """Test basic YoY growth calculation."""
        result = calculate_yoy_growth(sample_annual_data)

        assert len(result) == 4
        assert "yoy_growth" in result[0]
        # First year has no previous year
        assert result[0]["yoy_growth"] is None or math.isnan(result[0]["yoy_growth"])
        # Check growth calculations
        assert abs(result[1]["yoy_growth"] - 10.0) < 0.01  # 10% growth
        assert abs(result[2]["yoy_growth"] - 9.09) < 0.01  # ~9.09% growth
        assert abs(result[3]["yoy_growth"] - 10.0) < 0.01  # 10% growth

    def test_yoy_growth_custom_columns(self, sample_annual_data):
        """Test YoY growth with custom column names."""
        data = [
            {"Year": "2020", "Sales": 1000},
            {"Year": "2021", "Sales": 1200},
            {"Year": "2022", "Sales": 1440},
        ]
        result = calculate_yoy_growth(data, value_column="Sales", period_column="Year")

        assert len(result) == 3
        assert "yoy_growth" in result[0]
        assert abs(result[2]["yoy_growth"] - 20.0) < 0.01

    def test_yoy_growth_empty_data(self):
        """Test YoY growth with empty data."""
        result = calculate_yoy_growth([])
        assert result == []

    def test_yoy_growth_missing_column(self):
        """Test YoY growth with missing column."""
        data = [{"Period": "2020"}]  # Missing 'value' column
        with pytest.raises(ValueError):
            calculate_yoy_growth(data)


class TestMoMChange:
    """Tests for month-over-month change calculation."""

    def test_mom_change_basic(self, sample_monthly_data):
        """Test basic MoM change calculation."""
        result = calculate_mom_change(sample_monthly_data)

        assert len(result) == 5
        assert "mom_change" in result[0]
        # First month has no previous month
        assert result[0]["mom_change"] is None or math.isnan(result[0]["mom_change"])
        # Check change calculations
        assert abs(result[1]["mom_change"] - 5.0) < 0.01  # 5% growth
        assert abs(result[2]["mom_change"] - 4.76) < 0.01  # ~4.76% growth
        assert abs(result[3]["mom_change"] - (-1.82)) < 0.01  # ~-1.82% decline

    def test_mom_change_custom_columns(self, sample_monthly_data):
        """Test MoM change with custom column names."""
        data = [
            {"Month": "2023-01", "Revenue": 1000},
            {"Month": "2023-02", "Revenue": 1100},
            {"Month": "2023-03", "Revenue": 1050},
        ]
        result = calculate_mom_change(data, value_column="Revenue", period_column="Month")

        assert len(result) == 3
        assert "mom_change" in result[0]
        assert abs(result[2]["mom_change"] - (-4.55)) < 0.01

    def test_mom_change_empty_data(self):
        """Test MoM change with empty data."""
        result = calculate_mom_change([])
        assert result == []

    def test_mom_change_missing_column(self):
        """Test MoM change with missing column."""
        data = [{"Period": "2023-01"}]  # Missing 'value' column
        with pytest.raises(ValueError):
            calculate_mom_change(data)


class TestMovingAverage:
    """Tests for moving average calculation."""

    def test_moving_average_basic(self, sample_timeseries_data):
        """Test basic moving average calculation."""
        result = calculate_moving_average(sample_timeseries_data, window=3)

        assert len(result) == 6
        assert "moving_avg" in result[0]
        # First 2 values should be None/NaN
        assert result[0]["moving_avg"] is None or math.isnan(result[0]["moving_avg"])
        assert result[1]["moving_avg"] is None or math.isnan(result[1]["moving_avg"])
        # Third value should be mean of first 3
        assert abs(result[2]["moving_avg"] - 105.0) < 0.01  # (100+110+105)/3

    def test_moving_average_window_size(self, sample_timeseries_data):
        """Test moving average with different window sizes."""
        result_w2 = calculate_moving_average(sample_timeseries_data, window=2)
        result_w4 = calculate_moving_average(sample_timeseries_data, window=4)

        assert len(result_w2) == 6
        assert len(result_w4) == 6
        # Window of 2 should have fewer NaN at start
        assert result_w2[1]["moving_avg"] is not None and not math.isnan(result_w2[1]["moving_avg"])
        # Window of 4 should have more NaN at start
        assert result_w4[2]["moving_avg"] is None or math.isnan(result_w4[2]["moving_avg"])

    def test_moving_average_custom_columns(self, sample_timeseries_data):
        """Test moving average with custom column names."""
        data = [
            {"Date": "2023-01", "Stock": 100},
            {"Date": "2023-02", "Stock": 110},
            {"Date": "2023-03", "Stock": 105},
            {"Date": "2023-04", "Stock": 115},
        ]
        result = calculate_moving_average(
            data, window=2, value_column="Stock", period_column="Date"
        )

        assert len(result) == 4
        assert "moving_avg" in result[0]

    def test_moving_average_empty_data(self):
        """Test moving average with empty data."""
        result = calculate_moving_average([], window=3)
        assert result == []

    def test_moving_average_invalid_window(self):
        """Test moving average with invalid window size."""
        data = [{"Period": "2023-01", "value": 100}]
        with pytest.raises(ValueError):
            calculate_moving_average(data, window=0)

    def test_moving_average_missing_column(self):
        """Test moving average with missing column."""
        data = [{"Period": "2023-01"}]  # Missing 'value' column
        with pytest.raises(ValueError):
            calculate_moving_average(data)


class TestExponentialMovingAverage:
    """Tests for exponential moving average calculation."""

    def test_ema_basic(self, sample_timeseries_data):
        """Test basic exponential moving average calculation."""
        result = calculate_exponential_moving_average(sample_timeseries_data, span=3)

        assert len(result) == 6
        assert "ema" in result[0]
        # EMA should have values for all points (including first)
        assert result[0]["ema"] is not None
        assert not math.isnan(result[0]["ema"])

    def test_ema_span_effect(self, sample_timeseries_data):
        """Test that different spans produce different results."""
        result_s3 = calculate_exponential_moving_average(sample_timeseries_data, span=3)
        result_s5 = calculate_exponential_moving_average(sample_timeseries_data, span=5)

        # Last values should be different for different spans
        assert result_s3[-1]["ema"] != result_s5[-1]["ema"]

    def test_ema_custom_columns(self, sample_timeseries_data):
        """Test EMA with custom column names."""
        data = [
            {"Date": "2023-01", "Price": 100},
            {"Date": "2023-02", "Price": 110},
            {"Date": "2023-03", "Price": 105},
        ]
        result = calculate_exponential_moving_average(
            data, span=2, value_column="Price", period_column="Date"
        )

        assert len(result) == 3
        assert "ema" in result[0]

    def test_ema_empty_data(self):
        """Test EMA with empty data."""
        result = calculate_exponential_moving_average([])
        assert result == []

    def test_ema_invalid_span(self):
        """Test EMA with invalid span."""
        data = [{"Period": "2023-01", "value": 100}]
        with pytest.raises(ValueError):
            calculate_exponential_moving_average(data, span=0)

    def test_ema_missing_column(self):
        """Test EMA with missing column."""
        data = [{"Period": "2023-01"}]  # Missing 'value' column
        with pytest.raises(ValueError):
            calculate_exponential_moving_average(data)


class TestDataIntegrity:
    """Tests to ensure data integrity during calculations."""

    def test_original_columns_preserved(self, sample_annual_data):
        """Test that original columns are preserved in calculations."""
        result = calculate_yoy_growth(sample_annual_data)

        for i, item in enumerate(result):
            assert item["Period"] == sample_annual_data[i]["Period"]
            assert item["value"] == sample_annual_data[i]["value"]

    def test_data_not_mutated(self, sample_annual_data):
        """Test that original data is not mutated."""
        original_copy = [d.copy() for d in sample_annual_data]
        calculate_yoy_growth(sample_annual_data)

        assert sample_annual_data == original_copy

    def test_chained_calculations(self, sample_annual_data):
        """Test that calculations can be chained."""
        result1 = calculate_yoy_growth(sample_annual_data)
        result2 = calculate_moving_average(result1, window=2)

        assert len(result2) == len(sample_annual_data)
        assert "yoy_growth" in result2[0]
        assert "moving_avg" in result2[0]
