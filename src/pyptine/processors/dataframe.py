"""DataFrame processing utilities for pyptine."""

import logging
from typing import Any, Optional, Union, cast

import pandas as pd

from pyptine.utils.exceptions import DataProcessingError

logger = logging.getLogger(__name__)


def json_to_dataframe(
    data: Union[list[dict[str, Any]], dict[str, Any]],
    normalize: bool = True,
    parse_dates: bool = True,
) -> pd.DataFrame:
    """Convert INE JSON data to pandas DataFrame.

    Args:
        data: Raw JSON data from API (list of dicts or dict with 'dados' key)
        normalize: Flatten nested structures
        parse_dates: Attempt to parse date columns

    Returns:
        Processed DataFrame

    Raises:
        DataProcessingError: If conversion fails

    Example:
        >>> data = [
        ...     {"periodo": "2023", "geocod": "1", "valor": "10639726"},
        ...     {"periodo": "2022", "geocod": "1", "valor": "10467366"},
        ... ]
        >>> df = json_to_dataframe(data)
        >>> print(df.head())
    """
    try:
        # Handle dict with 'dados' key (full API response)
        # If data is a dict without 'dados', treat it as a single data point
        if isinstance(data, dict):
            data = data.get("dados", [data])

        # Handle empty data
        if not data:
            logger.warning("Empty data provided, returning empty DataFrame")
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(data)

        if df.empty:
            return df

        # Clean up column names (remove internal prefixes)
        df.columns = [col.replace("_", " ").strip() for col in df.columns]

        # Convert value column to numeric
        value_cols = [col for col in df.columns if "valor" in col.lower() or col.lower() == "value"]
        for col in value_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Parse date columns if requested
        if parse_dates:
            date_cols = [
                col
                for col in df.columns
                if any(
                    keyword in col.lower()
                    for keyword in ["periodo", "period", "date", "ano", "year"]
                )
            ]
            for col in date_cols:
                df[col] = _parse_date_column(df[col])

        logger.debug(f"Converted data to DataFrame with shape {df.shape}")

        return df

    except Exception as e:
        logger.error(f"Failed to convert data to DataFrame: {str(e)}")
        raise DataProcessingError(f"Failed to convert to DataFrame: {str(e)}") from e


def pivot_by_dimension(
    df: pd.DataFrame,
    dimension: str,
    value_column: Union[str, list[str]] = "valor",
    aggfunc: str = "first",
) -> pd.DataFrame:
    """Pivot DataFrame by specific dimension.

    Args:
        df: Input DataFrame
        dimension: Column to pivot on
        value_column: Column(s) containing values
        aggfunc: Aggregation function for duplicate values

    Returns:
        Pivoted DataFrame

    Example:
        >>> df = pd.DataFrame({
        ...     "periodo": ["2023", "2023", "2022"],
        ...     "region": ["North", "South", "North"],
        ...     "valor": [100, 200, 150]
        ... })
        >>> pivoted = pivot_by_dimension(df, "region")
    """
    try:
        # Ensure value_column is a list for consistent handling
        value_cols_list = [value_column] if isinstance(value_column, str) else value_column

        # Find index columns (all except dimension and value columns)
        index_cols = [col for col in df.columns if col not in [dimension] + value_cols_list]

        if not index_cols:
            # If no other columns, use dimension as index
            return df.set_index(dimension)

        # Create pivot table
        pivoted = df.pivot_table(
            values=value_cols_list,
            index=index_cols,
            columns=dimension,
            aggfunc=aggfunc,
        )

        return pivoted

    except Exception as e:
        logger.error(f"Failed to pivot DataFrame: {str(e)}")
        raise DataProcessingError(f"Failed to pivot DataFrame: {str(e)}") from e


def clean_dataframe(
    df: pd.DataFrame,
    drop_internal_columns: bool = True,
    rename_columns: Optional[dict[str, str]] = None,
) -> pd.DataFrame:
    """Clean and standardize DataFrame.

    Args:
        df: Input DataFrame
        drop_internal_columns: Drop columns starting with underscore
        rename_columns: Optional dict of column renames

    Returns:
        Cleaned DataFrame

    Example:
        >>> df = pd.DataFrame({"_internal": [1, 2], "data": [3, 4]})
        >>> cleaned = clean_dataframe(df)
        >>> "_internal" in cleaned.columns
        False
    """
    df = df.copy()

    # Drop internal columns
    if drop_internal_columns:
        internal_cols = [col for col in df.columns if col.startswith("_")]
        if internal_cols:
            df = df.drop(columns=internal_cols)
            logger.debug(f"Dropped internal columns: {internal_cols}")

    # Rename columns
    if rename_columns:
        df = df.rename(columns=rename_columns)
        logger.debug(f"Renamed columns: {rename_columns}")

    return df


def merge_metadata(
    df: pd.DataFrame,
    metadata: dict[str, Any],
    prefix: str = "meta_",
) -> pd.DataFrame:
    """Add metadata as columns to DataFrame.

    Args:
        df: Input DataFrame
        metadata: Metadata dictionary
        prefix: Prefix for metadata columns

    Returns:
        DataFrame with metadata columns

    Example:
        >>> df = pd.DataFrame({"value": [1, 2, 3]})
        >>> metadata = {"indicator": "0004167", "unit": "No."}
        >>> df_with_meta = merge_metadata(df, metadata)
        >>> "meta_indicator" in df_with_meta.columns
        True
    """
    df = df.copy()

    for key, value in metadata.items():
        col_name = f"{prefix}{key}"
        df[col_name] = value

    return df


def _parse_date_column(series: pd.Series) -> pd.Series:
    """Parse date column with various formats.

    Args:
        series: Pandas Series with date strings

    Returns:
        Series with parsed dates (or original if parsing fails)
    """
    try:
        # Try different date formats

        # Check if it's just a year
        if series.astype(str).str.match(r"^\d{4}$").all():
            # Keep as string for years
            return series

        # Try pandas date parsing
        return cast(pd.Series, pd.to_datetime(series, errors="coerce"))

    except Exception as e:
        logger.debug(f"Could not parse dates in column: {str(e)}")
        return series


def aggregate_by_period(
    df: pd.DataFrame,
    period_column: str = "periodo",
    value_column: Union[str, list[str]] = "valor",
    agg_func: Union[str, list[str]] = "sum",
) -> pd.DataFrame:
    """Aggregate data by time period.

    Args:
        df: Input DataFrame
        period_column: Column containing time periods
        value_column: Column(s) containing values to aggregate
        agg_func: Aggregation function(s) - "sum", "mean", "count", etc.

    Returns:
        Aggregated DataFrame

    Example:
        >>> df = pd.DataFrame({
        ...     "periodo": ["2023", "2023", "2022"],
        ...     "region": ["A", "B", "A"],
        ...     "valor": [100, 200, 150]
        ... })
        >>> agg = aggregate_by_period(df)
    """
    try:
        if period_column not in df.columns:
            raise ValueError(f"Period column '{period_column}' not found in DataFrame")

        # Ensure value_column is a list for consistent handling
        value_cols_list = [value_column] if isinstance(value_column, str) else value_column

        for col in value_cols_list:
            if col not in df.columns:
                raise ValueError(f"Value column '{col}' not found in DataFrame")

        # Group by period and aggregate
        result = df.groupby(period_column)[value_cols_list].agg(agg_func).reset_index()

        return cast(pd.DataFrame, result)

    except Exception as e:
        logger.error(f"Failed to aggregate by period: {str(e)}")
        raise DataProcessingError(f"Failed to aggregate: {str(e)}") from e


def filter_by_geography(
    df: pd.DataFrame,
    geography: str,
    geography_column: Optional[str] = None,
) -> pd.DataFrame:
    """Filter DataFrame by geographic region.

    Args:
        df: Input DataFrame
        geography: Geographic region to filter (e.g., "Portugal", "Lisboa")
        geography_column: Column name for geography (auto-detected if None)

    Returns:
        Filtered DataFrame

    Example:
        >>> df = pd.DataFrame({
        ...     "geodsg": ["Portugal", "Lisboa", "Porto"],
        ...     "valor": [100, 50, 30]
        ... })
        >>> filtered = filter_by_geography(df, "Portugal")
        >>> len(filtered)
        1
    """
    if geography_column is None:
        # Auto-detect geography column
        geo_keywords = ["geo", "geography", "region", "area", "location"]
        geography_column = next(
            (col for col in df.columns if any(kw in col.lower() for kw in geo_keywords)), None
        )

        if geography_column is None:
            raise ValueError("Could not auto-detect geography column")

    # Filter by geography
    mask: pd.Series[bool] = (
        df[geography_column].astype(str).str.contains(geography, case=False, na=False)
    )
    filtered: pd.DataFrame = cast(pd.DataFrame, df[mask].copy())

    logger.debug(f"Filtered to {len(filtered)} rows for geography: {geography}")

    return filtered


def get_latest_period(
    df: pd.DataFrame,
    period_column: str = "periodo",
    n: int = 1,
) -> pd.DataFrame:
    """Get data for the latest N periods.

    Args:
        df: Input DataFrame
        period_column: Column containing time periods
        n: Number of latest periods to return

    Returns:
        DataFrame with latest period(s)

    Example:
        >>> df = pd.DataFrame({
        ...     "periodo": ["2021", "2022", "2023"],
        ...     "valor": [100, 150, 200]
        ... })
        >>> latest = get_latest_period(df)
        >>> latest["periodo"].iloc[0]
        '2023'
    """
    if period_column not in df.columns:
        raise ValueError(f"Period column '{period_column}' not found")

    # Sort by period descending
    df_sorted = df.sort_values(period_column, ascending=False)

    # Get unique periods and take top N
    unique_periods = df_sorted[period_column].unique()[:n]

    # Filter to those periods
    mask: pd.Series[bool] = df_sorted[period_column].isin(unique_periods)
    result: pd.DataFrame = cast(pd.DataFrame, df_sorted[mask].copy())

    return result
