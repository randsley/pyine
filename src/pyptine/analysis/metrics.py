"""Statistical metrics for data analysis."""

import logging
from typing import Any, Optional

try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

logger = logging.getLogger(__name__)


def calculate_yoy_growth(
    data: list[dict[str, Any]],
    value_column: str = "value",
    period_column: str = "Period",
) -> list[dict[str, Any]]:
    """Calculate year-over-year growth rates.

    Compares each period's value to the same period in the previous year.
    Returns a list of data points with an added 'yoy_growth' column containing
    the percentage change from year to year.

    Args:
        data: List of data dictionaries with at least 'value' and period columns
        value_column: Name of the column containing values (default: "value")
        period_column: Name of the column containing time period (default: "Period")

    Returns:
        List of data points with added 'yoy_growth' column (None for first year)

    Raises:
        ValueError: If required columns are missing or if no period data is available

    Example:
        >>> data = [
        ...     {"Period": "2021", "value": 100},
        ...     {"Period": "2022", "value": 110},
        ...     {"Period": "2023", "value": 120},
        ... ]
        >>> result = calculate_yoy_growth(data)
        >>> # result[0]['yoy_growth'] is None
        >>> # result[1]['yoy_growth'] is 10.0 (10% growth)
        >>> # result[2]['yoy_growth'] is ~9.09% growth
    """
    if not PANDAS_AVAILABLE:
        raise ImportError("pandas is required for YoY growth calculation. Install with: pip install pandas")

    if not data:
        return []

    if value_column not in data[0] or period_column not in data[0]:
        raise ValueError(f"Data must contain '{value_column}' and '{period_column}' columns")

    df = pd.DataFrame(data).copy()

    # Ensure period is sorted
    df = df.sort_values(by=period_column)

    # Calculate YoY growth
    df["yoy_growth"] = None
    if value_column in df.columns and df[value_column].dtype in [float, int]:
        # Calculate percentage change year-over-year
        df["yoy_growth"] = df[value_column].pct_change() * 100

    logger.debug(f"Calculated YoY growth for {len(df)} data points")

    return df.to_dict(orient="records")


def calculate_mom_change(
    data: list[dict[str, Any]],
    value_column: str = "value",
    period_column: str = "Period",
) -> list[dict[str, Any]]:
    """Calculate month-over-month percentage changes.

    Compares each period's value to the immediately preceding period.
    Returns a list of data points with an added 'mom_change' column containing
    the percentage change from period to period.

    Args:
        data: List of data dictionaries with at least 'value' and period columns
        value_column: Name of the column containing values (default: "value")
        period_column: Name of the column containing time period (default: "Period")

    Returns:
        List of data points with added 'mom_change' column (None for first period)

    Raises:
        ValueError: If required columns are missing

    Example:
        >>> data = [
        ...     {"Period": "2023-01", "value": 100},
        ...     {"Period": "2023-02", "value": 105},
        ...     {"Period": "2023-03", "value": 102},
        ... ]
        >>> result = calculate_mom_change(data)
        >>> # result[0]['mom_change'] is None
        >>> # result[1]['mom_change'] is 5.0 (5% growth)
        >>> # result[2]['mom_change'] is ~-2.86% (decline)
    """
    if not PANDAS_AVAILABLE:
        raise ImportError("pandas is required for MoM change calculation. Install with: pip install pandas")

    if not data:
        return []

    if value_column not in data[0] or period_column not in data[0]:
        raise ValueError(f"Data must contain '{value_column}' and '{period_column}' columns")

    df = pd.DataFrame(data).copy()

    # Ensure period is sorted
    df = df.sort_values(by=period_column)

    # Calculate MoM change
    df["mom_change"] = None
    if value_column in df.columns and df[value_column].dtype in [float, int]:
        # Calculate percentage change month-over-month
        df["mom_change"] = df[value_column].pct_change() * 100

    logger.debug(f"Calculated MoM change for {len(df)} data points")

    return df.to_dict(orient="records")


def calculate_moving_average(
    data: list[dict[str, Any]],
    window: int = 3,
    value_column: str = "value",
    period_column: str = "Period",
) -> list[dict[str, Any]]:
    """Calculate simple moving average over a time window.

    Computes the rolling mean of values over a specified window size.
    Returns a list of data points with an added 'moving_avg' column.

    Args:
        data: List of data dictionaries with at least 'value' and period columns
        window: Number of periods to include in the moving average (default: 3)
        value_column: Name of the column containing values (default: "value")
        period_column: Name of the column containing time period (default: "Period")

    Returns:
        List of data points with added 'moving_avg' column (None for first window-1 periods)

    Raises:
        ValueError: If required columns are missing or window size is invalid

    Example:
        >>> data = [
        ...     {"Period": "2023-01", "value": 100},
        ...     {"Period": "2023-02", "value": 110},
        ...     {"Period": "2023-03", "value": 105},
        ...     {"Period": "2023-04", "value": 120},
        ... ]
        >>> result = calculate_moving_average(data, window=3)
        >>> # result[0]['moving_avg'] is None
        >>> # result[1]['moving_avg'] is None
        >>> # result[2]['moving_avg'] is 105.0 (mean of 100, 110, 105)
        >>> # result[3]['moving_avg'] is 111.67 (mean of 110, 105, 120)
    """
    if not PANDAS_AVAILABLE:
        raise ImportError(
            "pandas is required for moving average calculation. Install with: pip install pandas"
        )

    if not data:
        return []

    if window < 1:
        raise ValueError(f"Window size must be at least 1, got {window}")

    if value_column not in data[0] or period_column not in data[0]:
        raise ValueError(f"Data must contain '{value_column}' and '{period_column}' columns")

    df = pd.DataFrame(data).copy()

    # Ensure period is sorted
    df = df.sort_values(by=period_column)

    # Calculate moving average
    df["moving_avg"] = None
    if value_column in df.columns and df[value_column].dtype in [float, int]:
        df["moving_avg"] = df[value_column].rolling(window=window, center=False).mean()

    logger.debug(f"Calculated {window}-period moving average for {len(df)} data points")

    return df.to_dict(orient="records")


def calculate_exponential_moving_average(
    data: list[dict[str, Any]],
    span: int = 3,
    value_column: str = "value",
    period_column: str = "Period",
) -> list[dict[str, Any]]:
    """Calculate exponential moving average.

    Computes the exponentially weighted moving mean, giving more weight to recent values.
    Returns a list of data points with an added 'ema' column.

    Args:
        data: List of data dictionaries with at least 'value' and period columns
        span: Span parameter for EMA calculation - higher values give less weight to recent data (default: 3)
        value_column: Name of the column containing values (default: "value")
        period_column: Name of the column containing time period (default: "Period")

    Returns:
        List of data points with added 'ema' column

    Raises:
        ValueError: If required columns are missing or span is invalid

    Example:
        >>> data = [
        ...     {"Period": "2023-01", "value": 100},
        ...     {"Period": "2023-02", "value": 110},
        ...     {"Period": "2023-03", "value": 105},
        ...     {"Period": "2023-04", "value": 120},
        ... ]
        >>> result = calculate_exponential_moving_average(data, span=3)
        >>> # EMA gives more weight to recent values than simple MA
    """
    if not PANDAS_AVAILABLE:
        raise ImportError(
            "pandas is required for EMA calculation. Install with: pip install pandas"
        )

    if not data:
        return []

    if span < 1:
        raise ValueError(f"Span must be at least 1, got {span}")

    if value_column not in data[0] or period_column not in data[0]:
        raise ValueError(f"Data must contain '{value_column}' and '{period_column}' columns")

    df = pd.DataFrame(data).copy()

    # Ensure period is sorted
    df = df.sort_values(by=period_column)

    # Calculate exponential moving average
    df["ema"] = None
    if value_column in df.columns and df[value_column].dtype in [float, int]:
        df["ema"] = df[value_column].ewm(span=span, adjust=False).mean()

    logger.debug(f"Calculated EMA (span={span}) for {len(df)} data points")

    return df.to_dict(orient="records")
