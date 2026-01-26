"""Tests for chart visualization functions."""

import pytest

try:
    import plotly.graph_objects as go

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

import pandas as pd

from pyptine.visualization.charts import (
    plot_indicator,
    plot_line_chart,
    plot_bar_chart,
    plot_area_chart,
    plot_scatter_chart,
)


@pytest.fixture
def sample_data():
    """Sample data for visualization tests."""
    return [
        {"Period": "2020", "value": 100, "region": "PT"},
        {"Period": "2021", "value": 110, "region": "PT"},
        {"Period": "2022", "value": 120, "region": "PT"},
        {"Period": "2023", "value": 132, "region": "PT"},
    ]


@pytest.fixture
def sample_dataframe(sample_data):
    """Sample DataFrame for visualization tests."""
    return pd.DataFrame(sample_data)


@pytest.fixture
def sample_multiregion_data():
    """Sample data with multiple regions for coloring."""
    return [
        {"Period": "2020", "value": 100, "region": "North"},
        {"Period": "2020", "value": 150, "region": "South"},
        {"Period": "2021", "value": 110, "region": "North"},
        {"Period": "2021", "value": 160, "region": "South"},
        {"Period": "2022", "value": 120, "region": "North"},
        {"Period": "2022", "value": 170, "region": "South"},
    ]


@pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="plotly not installed")
class TestPlotIndicator:
    """Tests for plot_indicator function."""

    def test_plot_indicator_line(self, sample_data):
        """Test creating a line chart."""
        fig = plot_indicator(sample_data, title="Test Indicator", chart_type="line")

        assert fig is not None
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Test Indicator"

    def test_plot_indicator_bar(self, sample_data):
        """Test creating a bar chart."""
        fig = plot_indicator(sample_data, title="Test Indicator", chart_type="bar")

        assert fig is not None
        assert isinstance(fig, go.Figure)

    def test_plot_indicator_area(self, sample_data):
        """Test creating an area chart."""
        fig = plot_indicator(sample_data, title="Test Indicator", chart_type="area")

        assert fig is not None
        assert isinstance(fig, go.Figure)

    def test_plot_indicator_scatter(self, sample_data):
        """Test creating a scatter chart."""
        fig = plot_indicator(sample_data, title="Test Indicator", chart_type="scatter")

        assert fig is not None
        assert isinstance(fig, go.Figure)

    def test_plot_indicator_with_dataframe(self, sample_dataframe):
        """Test plot_indicator with DataFrame input."""
        fig = plot_indicator(sample_dataframe, title="Test", chart_type="line")

        assert fig is not None
        assert isinstance(fig, go.Figure)

    def test_plot_indicator_invalid_chart_type(self, sample_data):
        """Test plot_indicator with invalid chart type."""
        with pytest.raises(ValueError):
            plot_indicator(sample_data, chart_type="invalid")

    def test_plot_indicator_empty_data(self):
        """Test plot_indicator with empty data."""
        fig = plot_indicator([], title="Empty")

        assert fig is None

    def test_plot_indicator_with_color_column(self, sample_multiregion_data):
        """Test plot_indicator with color column."""
        fig = plot_indicator(
            sample_multiregion_data,
            title="By Region",
            chart_type="line",
            color_column="region",
        )

        assert fig is not None
        assert isinstance(fig, go.Figure)


@pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="plotly not installed")
class TestLineChart:
    """Tests for plot_line_chart function."""

    def test_line_chart_basic(self, sample_data):
        """Test basic line chart creation."""
        fig = plot_line_chart(sample_data, title="Population")

        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Population"

    def test_line_chart_with_markers(self, sample_data):
        """Test line chart with markers."""
        fig = plot_line_chart(sample_data, title="Test", markers=True)

        assert isinstance(fig, go.Figure)

    def test_line_chart_without_markers(self, sample_data):
        """Test line chart without markers."""
        fig = plot_line_chart(sample_data, title="Test", markers=False)

        assert isinstance(fig, go.Figure)

    def test_line_chart_custom_columns(self, sample_data):
        """Test line chart with custom column names."""
        fig = plot_line_chart(
            sample_data,
            title="Test",
            x_column="Period",
            y_column="value",
        )

        assert isinstance(fig, go.Figure)


@pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="plotly not installed")
class TestBarChart:
    """Tests for plot_bar_chart function."""

    def test_bar_chart_basic(self, sample_data):
        """Test basic bar chart creation."""
        fig = plot_bar_chart(sample_data, title="Growth")

        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Growth"

    def test_bar_chart_with_color(self, sample_multiregion_data):
        """Test bar chart with color column."""
        fig = plot_bar_chart(
            sample_multiregion_data,
            title="By Region",
            color_column="region",
        )

        assert isinstance(fig, go.Figure)


@pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="plotly not installed")
class TestAreaChart:
    """Tests for plot_area_chart function."""

    def test_area_chart_basic(self, sample_data):
        """Test basic area chart creation."""
        fig = plot_area_chart(sample_data, title="Trend")

        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Trend"

    def test_area_chart_with_color(self, sample_multiregion_data):
        """Test area chart with color column."""
        fig = plot_area_chart(
            sample_multiregion_data,
            title="By Region",
            color_column="region",
        )

        assert isinstance(fig, go.Figure)


@pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="plotly not installed")
class TestScatterChart:
    """Tests for plot_scatter_chart function."""

    def test_scatter_chart_basic(self, sample_data):
        """Test basic scatter chart creation."""
        fig = plot_scatter_chart(sample_data, title="Distribution")

        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Distribution"

    def test_scatter_chart_with_size(self, sample_multiregion_data):
        """Test scatter chart with size column."""
        fig = plot_scatter_chart(
            sample_multiregion_data,
            title="With Size",
            size_column="value",
        )

        assert isinstance(fig, go.Figure)

    def test_scatter_chart_with_color_and_size(self, sample_multiregion_data):
        """Test scatter chart with both color and size columns."""
        fig = plot_scatter_chart(
            sample_multiregion_data,
            title="Colored and Sized",
            color_column="region",
            size_column="value",
        )

        assert isinstance(fig, go.Figure)


@pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="plotly not installed")
class TestChartLayout:
    """Tests for chart layout and styling."""

    def test_chart_has_styling(self, sample_data):
        """Test that charts have consistent styling applied."""
        fig = plot_line_chart(sample_data, title="Test")

        # Check that layout has styling applied
        assert fig.layout.plot_bgcolor is not None
        assert fig.layout.paper_bgcolor is not None
        assert fig.layout.font is not None

    def test_chart_title_formatting(self, sample_data):
        """Test that chart titles are properly formatted."""
        title = "Population Growth 2020-2023"
        fig = plot_indicator(sample_data, title=title, chart_type="line")

        assert fig.layout.title.text == title

    def test_chart_hover_mode(self, sample_data):
        """Test that charts have appropriate hover mode."""
        line_fig = plot_line_chart(sample_data)
        bar_fig = plot_bar_chart(sample_data)

        # Line chart should have unified hover mode for better multi-line viewing
        assert line_fig.layout.hovermode == "x unified"
        # Bar chart should have standard hover mode
        assert bar_fig.layout.hovermode == "x"
