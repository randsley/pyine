"""Excel export functionality for pyptine."""

import logging
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from pyptine.utils.exceptions import DataProcessingError

logger = logging.getLogger(__name__)


def export_multiple_sheets(
    data_dict: dict[str, pd.DataFrame],
    filepath: Path,
    include_metadata: bool = True,
    metadata: Optional[dict[str, Any]] = None,
) -> None:
    """Export multiple DataFrames to Excel file with separate sheets.

    Args:
        data_dict: Dictionary of {sheet_name: DataFrame}
        filepath: Output Excel file path
        include_metadata: Include metadata sheet
        metadata: Optional metadata dictionary

    Raises:
        DataProcessingError: If export fails

    Example:
        >>> data = {
        ...     "2023": df_2023,
        ...     "2022": df_2022,
        ... }
        >>> export_multiple_sheets(data, Path("output.xlsx"))
    """
    try:
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
            # Write metadata sheet if requested
            if include_metadata and metadata:
                metadata_df = pd.DataFrame(list(metadata.items()), columns=["Key", "Value"])
                metadata_df.to_excel(writer, sheet_name="Metadata", index=False)

            # Write data sheets
            for sheet_name, df in data_dict.items():
                # Truncate sheet name to Excel's 31 character limit
                sheet_name = str(sheet_name)[:31]
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        logger.info(f"Exported {len(data_dict)} sheets to {filepath}")

    except ImportError:
        raise DataProcessingError(
            "openpyxl is required for Excel export. Install with: pip install openpyxl"
        ) from None
    except Exception as e:
        logger.error(f"Failed to export Excel: {str(e)}")
        raise DataProcessingError(f"Failed to export Excel: {str(e)}") from e


def format_for_excel(
    df: pd.DataFrame,
    date_format: str = "%Y-%m-%d",
    float_format: str = "%.2f",
) -> pd.DataFrame:
    """Format DataFrame for Excel export.

    Args:
        df: Input DataFrame
        date_format: Format string for dates
        float_format: Format string for floats

    Returns:
        Formatted DataFrame

    Example:
        >>> df = pd.DataFrame({"value": [1.2345, 2.3456]})
        >>> formatted = format_for_excel(df)
    """
    df = df.copy()

    # Format datetime columns
    for col in df.select_dtypes(include=["datetime64"]).columns:  # type: str
        df[col] = df[col].dt.strftime(date_format)

    # Format float columns
    for float_col in df.select_dtypes(include=["float64"]).columns:  # type: str
        df[float_col] = df[float_col].apply(lambda x: float(float_format % x) if pd.notna(x) else x)

    return df
