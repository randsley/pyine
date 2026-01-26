"""Tests for DataResponse analysis methods."""

import pytest

from pyptine.models.response import DataResponse


@pytest.fixture
def sample_response():
    """Create a sample DataResponse for testing."""
    return DataResponse(
        varcd="0004127",
        title="Test Indicator",
        language="EN",
        data=[
            {"Period": "2020", "value": 100, "region": "PT"},
            {"Period": "2021", "value": 110, "region": "PT"},
            {"Period": "2022", "value": 120, "region": "PT"},
            {"Period": "2023", "value": 132, "region": "PT"},
        ],
        unit="No.",
    )


@pytest.fixture
def sample_monthly_response():
    """Create a sample monthly DataResponse."""
    return DataResponse(
        varcd="0004128",
        title="Monthly Data",
        language="EN",
        data=[
            {"Period": "2023-01", "value": 100},
            {"Period": "2023-02", "value": 105},
            {"Period": "2023-03", "value": 110},
            {"Period": "2023-04", "value": 108},
            {"Period": "2023-05", "value": 115},
            {"Period": "2023-06", "value": 125},
        ],
        unit="No.",
    )


class TestDataResponseYoYGrowth:
    """Tests for DataResponse.calculate_yoy_growth()."""

    def test_yoy_growth_adds_column(self, sample_response):
        """Test that YoY growth adds the 'yoy_growth' column."""
        result = sample_response.calculate_yoy_growth()

        assert isinstance(result, DataResponse)
        assert result.varcd == sample_response.varcd
        assert result.title == sample_response.title
        assert "yoy_growth" in result.data[0]

    def test_yoy_growth_preserves_metadata(self, sample_response):
        """Test that YoY growth preserves response metadata."""
        result = sample_response.calculate_yoy_growth()

        assert result.varcd == sample_response.varcd
        assert result.title == sample_response.title
        assert result.language == sample_response.language
        assert result.unit == sample_response.unit

    def test_yoy_growth_does_not_mutate_original(self, sample_response):
        """Test that original response is not mutated."""
        original_data_copy = [d.copy() for d in sample_response.data]
        result = sample_response.calculate_yoy_growth()

        assert sample_response.data == original_data_copy
        assert result.data != original_data_copy

    def test_yoy_growth_custom_columns(self, sample_response):
        """Test YoY growth with custom column names."""
        result = sample_response.calculate_yoy_growth(
            value_column="value", period_column="Period"
        )

        assert "yoy_growth" in result.data[0]
        df = result.to_dataframe()
        assert "yoy_growth" in df.columns


class TestDataResponseMoMChange:
    """Tests for DataResponse.calculate_mom_change()."""

    def test_mom_change_adds_column(self, sample_monthly_response):
        """Test that MoM change adds the 'mom_change' column."""
        result = sample_monthly_response.calculate_mom_change()

        assert isinstance(result, DataResponse)
        assert "mom_change" in result.data[0]

    def test_mom_change_preserves_metadata(self, sample_monthly_response):
        """Test that MoM change preserves response metadata."""
        result = sample_monthly_response.calculate_mom_change()

        assert result.varcd == sample_monthly_response.varcd
        assert result.unit == sample_monthly_response.unit

    def test_mom_change_does_not_mutate_original(self, sample_monthly_response):
        """Test that original response is not mutated."""
        original_data_copy = [d.copy() for d in sample_monthly_response.data]
        result = sample_monthly_response.calculate_mom_change()

        assert sample_monthly_response.data == original_data_copy
        assert result.data != original_data_copy


class TestDataResponseMovingAverage:
    """Tests for DataResponse.calculate_moving_average()."""

    def test_moving_average_adds_column(self, sample_monthly_response):
        """Test that moving average adds the 'moving_avg' column."""
        result = sample_monthly_response.calculate_moving_average(window=3)

        assert isinstance(result, DataResponse)
        assert "moving_avg" in result.data[0]

    def test_moving_average_window_size(self, sample_monthly_response):
        """Test moving average with different window sizes."""
        result_w2 = sample_monthly_response.calculate_moving_average(window=2)
        result_w3 = sample_monthly_response.calculate_moving_average(window=3)

        assert len(result_w2.data) == len(sample_monthly_response.data)
        assert len(result_w3.data) == len(sample_monthly_response.data)

    def test_moving_average_preserves_metadata(self, sample_monthly_response):
        """Test that moving average preserves response metadata."""
        result = sample_monthly_response.calculate_moving_average(window=3)

        assert result.varcd == sample_monthly_response.varcd
        assert result.unit == sample_monthly_response.unit

    def test_moving_average_does_not_mutate_original(self, sample_monthly_response):
        """Test that original response is not mutated."""
        original_data_copy = [d.copy() for d in sample_monthly_response.data]
        result = sample_monthly_response.calculate_moving_average(window=3)

        assert sample_monthly_response.data == original_data_copy
        assert result.data != original_data_copy


class TestDataResponseExponentialMovingAverage:
    """Tests for DataResponse.calculate_exponential_moving_average()."""

    def test_ema_adds_column(self, sample_monthly_response):
        """Test that EMA adds the 'ema' column."""
        result = sample_monthly_response.calculate_exponential_moving_average(span=3)

        assert isinstance(result, DataResponse)
        assert "ema" in result.data[0]

    def test_ema_span_parameter(self, sample_monthly_response):
        """Test EMA with different span parameters."""
        result_s2 = sample_monthly_response.calculate_exponential_moving_average(span=2)
        result_s5 = sample_monthly_response.calculate_exponential_moving_average(span=5)

        assert len(result_s2.data) == len(sample_monthly_response.data)
        assert len(result_s5.data) == len(sample_monthly_response.data)

    def test_ema_preserves_metadata(self, sample_monthly_response):
        """Test that EMA preserves response metadata."""
        result = sample_monthly_response.calculate_exponential_moving_average(span=3)

        assert result.varcd == sample_monthly_response.varcd
        assert result.unit == sample_monthly_response.unit

    def test_ema_does_not_mutate_original(self, sample_monthly_response):
        """Test that original response is not mutated."""
        original_data_copy = [d.copy() for d in sample_monthly_response.data]
        result = sample_monthly_response.calculate_exponential_moving_average(span=3)

        assert sample_monthly_response.data == original_data_copy
        assert result.data != original_data_copy


class TestChainedAnalysis:
    """Tests for chaining multiple analysis methods."""

    def test_chain_yoy_and_moving_average(self, sample_response):
        """Test chaining YoY growth with moving average."""
        result = sample_response.calculate_yoy_growth().calculate_moving_average(window=2)

        assert "yoy_growth" in result.data[0]
        assert "moving_avg" in result.data[0]
        df = result.to_dataframe()
        assert "yoy_growth" in df.columns
        assert "moving_avg" in df.columns

    def test_chain_mom_and_ema(self, sample_monthly_response):
        """Test chaining MoM change with EMA."""
        result = sample_monthly_response.calculate_mom_change().calculate_exponential_moving_average(
            span=3
        )

        assert "mom_change" in result.data[0]
        assert "ema" in result.data[0]

    def test_convert_to_dataframe_after_analysis(self, sample_response):
        """Test converting to DataFrame after analysis."""
        result = sample_response.calculate_yoy_growth()
        df = result.to_dataframe()

        assert len(df) == len(sample_response.data)
        assert "yoy_growth" in df.columns
        assert "Period" in df.columns
