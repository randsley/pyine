"""Tests for DataResponse visualization methods."""

import pytest

try:
    import plotly.graph_objects as go

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from pyptine.models.response import DataResponse


@pytest.fixture
def sample_response():
    """Create a sample DataResponse for testing."""
    return DataResponse(
        varcd="0004127",
        title="Population Data",
        language="EN",
        data=[
            {"Period": "2020", "value": 100},
            {"Period": "2021", "value": 110},
            {"Period": "2022", "value": 120},
            {"Period": "2023", "value": 132},
        ],
        unit="No.",
    )


@pytest.fixture
def sample_response_multiregion():
    """Create a DataResponse with multiple regions."""
    return DataResponse(
        varcd="0004128",
        title="Regional Population",
        language="EN",
        data=[
            {"Period": "2020", "value": 100, "region": "North"},
            {"Period": "2020", "value": 150, "region": "South"},
            {"Period": "2021", "value": 110, "region": "North"},
            {"Period": "2021", "value": 160, "region": "South"},
            {"Period": "2022", "value": 120, "region": "North"},
            {"Period": "2022", "value": 170, "region": "South"},
        ],
        unit="No.",
    )


@pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="plotly not installed")
class TestDataResponsePlot:
    """Tests for DataResponse.plot() method."""

    def test_plot_basic(self, sample_response):
        """Test basic plot creation."""
        fig = sample_response.plot()

        assert fig is not None
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == sample_response.title

    def test_plot_line_chart(self, sample_response):
        """Test plot with line chart type."""
        fig = sample_response.plot(chart_type="line")

        assert isinstance(fig, go.Figure)

    def test_plot_bar_chart(self, sample_response):
        """Test plot with bar chart type."""
        fig = sample_response.plot(chart_type="bar")

        assert isinstance(fig, go.Figure)

    def test_plot_area_chart(self, sample_response):
        """Test plot with area chart type."""
        fig = sample_response.plot(chart_type="area")

        assert isinstance(fig, go.Figure)

    def test_plot_scatter_chart(self, sample_response):
        """Test plot with scatter chart type."""
        fig = sample_response.plot(chart_type="scatter")

        assert isinstance(fig, go.Figure)

    def test_plot_invalid_type(self, sample_response):
        """Test plot with invalid chart type."""
        with pytest.raises(ValueError):
            sample_response.plot(chart_type="invalid")

    def test_plot_with_color_column(self, sample_response_multiregion):
        """Test plot with color column for dimensions."""
        fig = sample_response_multiregion.plot(
            chart_type="line",
            color_column="region",
        )

        assert isinstance(fig, go.Figure)


@pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="plotly not installed")
class TestDataResponsePlotLine:
    """Tests for DataResponse.plot_line() method."""

    def test_plot_line_default(self, sample_response):
        """Test plot_line with defaults."""
        fig = sample_response.plot_line()

        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == sample_response.title
        assert fig.layout.hovermode == "x unified"

    def test_plot_line_with_markers(self, sample_response):
        """Test plot_line with markers enabled."""
        fig = sample_response.plot_line(markers=True)

        assert isinstance(fig, go.Figure)

    def test_plot_line_without_markers(self, sample_response):
        """Test plot_line with markers disabled."""
        fig = sample_response.plot_line(markers=False)

        assert isinstance(fig, go.Figure)

    def test_plot_line_with_color(self, sample_response_multiregion):
        """Test plot_line with color column."""
        fig = sample_response_multiregion.plot_line(color_column="region")

        assert isinstance(fig, go.Figure)


@pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="plotly not installed")
class TestDataResponsePlotBar:
    """Tests for DataResponse.plot_bar() method."""

    def test_plot_bar_default(self, sample_response):
        """Test plot_bar with defaults."""
        fig = sample_response.plot_bar()

        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == sample_response.title

    def test_plot_bar_with_color(self, sample_response_multiregion):
        """Test plot_bar with color column."""
        fig = sample_response_multiregion.plot_bar(color_column="region")

        assert isinstance(fig, go.Figure)


@pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="plotly not installed")
class TestDataResponsePlotArea:
    """Tests for DataResponse.plot_area() method."""

    def test_plot_area_default(self, sample_response):
        """Test plot_area with defaults."""
        fig = sample_response.plot_area()

        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == sample_response.title

    def test_plot_area_with_color(self, sample_response_multiregion):
        """Test plot_area with color column."""
        fig = sample_response_multiregion.plot_area(color_column="region")

        assert isinstance(fig, go.Figure)


@pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="plotly not installed")
class TestDataResponsePlotScatter:
    """Tests for DataResponse.plot_scatter() method."""

    def test_plot_scatter_default(self, sample_response):
        """Test plot_scatter with defaults."""
        fig = sample_response.plot_scatter()

        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == sample_response.title

    def test_plot_scatter_with_color(self, sample_response_multiregion):
        """Test plot_scatter with color column."""
        fig = sample_response_multiregion.plot_scatter(color_column="region")

        assert isinstance(fig, go.Figure)

    def test_plot_scatter_with_size(self, sample_response):
        """Test plot_scatter with size column."""
        fig = sample_response.plot_scatter(size_column="value")

        assert isinstance(fig, go.Figure)

    def test_plot_scatter_with_color_and_size(self, sample_response_multiregion):
        """Test plot_scatter with both color and size columns."""
        fig = sample_response_multiregion.plot_scatter(
            color_column="region",
            size_column="value",
        )

        assert isinstance(fig, go.Figure)


@pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="plotly not installed")
class TestPlotCustomization:
    """Tests for plot customization options."""

    def test_plot_custom_columns(self, sample_response):
        """Test plot with custom column names."""
        fig = sample_response.plot(
            x_column="Period",
            y_column="value",
        )

        assert isinstance(fig, go.Figure)

    def test_plot_preserves_metadata(self, sample_response):
        """Test that plotting preserves response metadata."""
        fig = sample_response.plot()

        # Response should remain unchanged
        assert sample_response.varcd == "0004127"
        assert sample_response.title == "Population Data"
        assert len(sample_response.data) == 4

    def test_plot_chain_with_analysis(self, sample_response):
        """Test plotting after analysis operations."""
        yoy_response = sample_response.calculate_yoy_growth()
        fig = yoy_response.plot(y_column="yoy_growth", chart_type="bar")

        assert isinstance(fig, go.Figure)
