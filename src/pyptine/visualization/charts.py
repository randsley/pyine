"""Chart creation functions for indicator data visualization."""

import logging
from typing import Any, Optional, Union

try:
    import plotly.express as px

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

logger = logging.getLogger(__name__)


def plot_indicator(
    data: Union[list[dict[str, Any]], "pd.DataFrame"],
    title: str = "Indicator Data",
    x_column: str = "Period",
    y_column: str = "value",
    chart_type: str = "line",
    color_column: Optional[str] = None,
    **kwargs: Any,
) -> Optional[Any]:
    """Create a visualization of indicator data.

    Creates an interactive plotly chart for the given data. Supports multiple
    chart types and optional dimension-based coloring.

    Args:
        data: List of dictionaries or pandas DataFrame with indicator data
        title: Chart title
        x_column: Column name for x-axis (default: "Period")
        y_column: Column name for y-axis values (default: "value")
        chart_type: Type of chart - "line", "bar", "area", "scatter" (default: "line")
        color_column: Optional column to use for coloring by dimension
        **kwargs: Additional arguments passed to plotly express functions

    Returns:
        Plotly figure object or None if plotly not available

    Raises:
        ImportError: If plotly or pandas is not installed
        ValueError: If chart_type is invalid

    Example:
        >>> data = [{"Period": "2021", "value": 100}, {"Period": "2022", "value": 110}]
        >>> fig = plot_indicator(data, title="Population Growth", chart_type="line")
        >>> fig.show()
    """
    if not PLOTLY_AVAILABLE:
        raise ImportError("plotly is required for visualization. Install with: pip install plotly")

    if not PANDAS_AVAILABLE:
        raise ImportError("pandas is required for visualization. Install with: pip install pandas")

    # Convert to DataFrame if needed
    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data.copy()

    if df.empty:
        logger.warning("Data is empty, cannot create visualization")
        return None

    # Validate chart type
    valid_types = {"line", "bar", "area", "scatter"}
    if chart_type.lower() not in valid_types:
        raise ValueError(f"chart_type must be one of {valid_types}, got '{chart_type}'")

    chart_type = chart_type.lower()

    # Create appropriate chart
    if chart_type == "line":
        return plot_line_chart(
            df,
            title=title,
            x_column=x_column,
            y_column=y_column,
            color_column=color_column,
            **kwargs,
        )
    elif chart_type == "bar":
        return plot_bar_chart(
            df,
            title=title,
            x_column=x_column,
            y_column=y_column,
            color_column=color_column,
            **kwargs,
        )
    elif chart_type == "area":
        return plot_area_chart(
            df,
            title=title,
            x_column=x_column,
            y_column=y_column,
            color_column=color_column,
            **kwargs,
        )
    elif chart_type == "scatter":
        return plot_scatter_chart(
            df,
            title=title,
            x_column=x_column,
            y_column=y_column,
            color_column=color_column,
            **kwargs,
        )


def plot_line_chart(
    data: Union[list[dict[str, Any]], "pd.DataFrame"],
    title: str = "Line Chart",
    x_column: str = "Period",
    y_column: str = "value",
    color_column: Optional[str] = None,
    markers: bool = True,
    **kwargs: Any,
) -> Any:
    """Create an interactive line chart.

    Args:
        data: List of dictionaries or pandas DataFrame
        title: Chart title
        x_column: Column for x-axis
        y_column: Column for y-axis values
        color_column: Optional column for coloring lines
        markers: Show markers on line points (default: True)
        **kwargs: Additional plotly express arguments

    Returns:
        Plotly figure object

    Raises:
        ImportError: If plotly or pandas not installed
    """
    if not PLOTLY_AVAILABLE or not PANDAS_AVAILABLE:
        raise ImportError("plotly and pandas are required")

    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data.copy()

    fig = px.line(
        df,
        x=x_column,
        y=y_column,
        color=color_column,
        title=title,
        markers=markers,
        labels={
            x_column: x_column.replace("_", " ").title(),
            y_column: y_column.replace("_", " ").title(),
        },
        **kwargs,
    )

    fig.update_layout(
        hovermode="x unified",
        plot_bgcolor="rgba(240, 240, 240, 0.5)",
        paper_bgcolor="white",
        font={"family": "Arial, sans-serif", "size": 12},
    )

    logger.debug(f"Created line chart: {title}")
    return fig


def plot_bar_chart(
    data: Union[list[dict[str, Any]], "pd.DataFrame"],
    title: str = "Bar Chart",
    x_column: str = "Period",
    y_column: str = "value",
    color_column: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    """Create an interactive bar chart.

    Args:
        data: List of dictionaries or pandas DataFrame
        title: Chart title
        x_column: Column for x-axis (categories)
        y_column: Column for y-axis values
        color_column: Optional column for coloring bars
        **kwargs: Additional plotly express arguments

    Returns:
        Plotly figure object

    Raises:
        ImportError: If plotly or pandas not installed
    """
    if not PLOTLY_AVAILABLE or not PANDAS_AVAILABLE:
        raise ImportError("plotly and pandas are required")

    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data.copy()

    fig = px.bar(
        df,
        x=x_column,
        y=y_column,
        color=color_column,
        title=title,
        labels={
            x_column: x_column.replace("_", " ").title(),
            y_column: y_column.replace("_", " ").title(),
        },
        **kwargs,
    )

    fig.update_layout(
        hovermode="x",
        plot_bgcolor="rgba(240, 240, 240, 0.5)",
        paper_bgcolor="white",
        font={"family": "Arial, sans-serif", "size": 12},
    )

    logger.debug(f"Created bar chart: {title}")
    return fig


def plot_area_chart(
    data: Union[list[dict[str, Any]], "pd.DataFrame"],
    title: str = "Area Chart",
    x_column: str = "Period",
    y_column: str = "value",
    color_column: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    """Create an interactive area chart.

    Args:
        data: List of dictionaries or pandas DataFrame
        title: Chart title
        x_column: Column for x-axis
        y_column: Column for y-axis values
        color_column: Optional column for coloring areas
        **kwargs: Additional plotly express arguments

    Returns:
        Plotly figure object

    Raises:
        ImportError: If plotly or pandas not installed
    """
    if not PLOTLY_AVAILABLE or not PANDAS_AVAILABLE:
        raise ImportError("plotly and pandas are required")

    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data.copy()

    fig = px.area(
        df,
        x=x_column,
        y=y_column,
        color=color_column,
        title=title,
        labels={
            x_column: x_column.replace("_", " ").title(),
            y_column: y_column.replace("_", " ").title(),
        },
        **kwargs,
    )

    fig.update_layout(
        hovermode="x unified",
        plot_bgcolor="rgba(240, 240, 240, 0.5)",
        paper_bgcolor="white",
        font={"family": "Arial, sans-serif", "size": 12},
    )

    logger.debug(f"Created area chart: {title}")
    return fig


def plot_scatter_chart(
    data: Union[list[dict[str, Any]], "pd.DataFrame"],
    title: str = "Scatter Chart",
    x_column: str = "Period",
    y_column: str = "value",
    color_column: Optional[str] = None,
    size_column: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    """Create an interactive scatter chart.

    Args:
        data: List of dictionaries or pandas DataFrame
        title: Chart title
        x_column: Column for x-axis
        y_column: Column for y-axis values
        color_column: Optional column for coloring points
        size_column: Optional column for point size
        **kwargs: Additional plotly express arguments

    Returns:
        Plotly figure object

    Raises:
        ImportError: If plotly or pandas not installed
    """
    if not PLOTLY_AVAILABLE or not PANDAS_AVAILABLE:
        raise ImportError("plotly and pandas are required")

    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data.copy()

    fig = px.scatter(
        df,
        x=x_column,
        y=y_column,
        color=color_column,
        size=size_column,
        title=title,
        labels={
            x_column: x_column.replace("_", " ").title(),
            y_column: y_column.replace("_", " ").title(),
        },
        **kwargs,
    )

    fig.update_layout(
        hovermode="closest",
        plot_bgcolor="rgba(240, 240, 240, 0.5)",
        paper_bgcolor="white",
        font={"family": "Arial, sans-serif", "size": 12},
    )

    logger.debug(f"Created scatter chart: {title}")
    return fig
