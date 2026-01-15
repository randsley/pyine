"""CSV export functionality for pyptine."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, TextIO

import pandas as pd

from pyptine.utils.exceptions import DataProcessingError

logger = logging.getLogger(__name__)


def export_to_csv(
    df: pd.DataFrame,
    filepath: Path,
    include_metadata: bool = True,
    metadata: Optional[dict[str, Any]] = None,
    encoding: str = "utf-8-sig",
    **kwargs: Any,
) -> None:
    """Export DataFrame to CSV with optional metadata header.

    Args:
        df: DataFrame to export
        filepath: Output file path
        include_metadata: Include metadata as comment header
        metadata: Optional metadata dictionary
        encoding: File encoding (utf-8-sig for Excel compatibility)
        **kwargs: Additional arguments passed to df.to_csv()

    Raises:
        DataProcessingError: If export fails

    Example:
        >>> df = pd.DataFrame({"value": [1, 2, 3]})
        >>> metadata = {"indicator": "0004167", "source": "INE Portugal"}
        >>> export_to_csv(df, Path("output.csv"), metadata=metadata)
    """
    try:
        filepath = Path(filepath)

        # Create parent directories if needed
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Write metadata header if requested
        if include_metadata and metadata:
            with open(filepath, "w", encoding=encoding) as f:
                _write_metadata_header(f, metadata)

            # Append DataFrame
            df.to_csv(
                filepath,
                mode="a",
                encoding=encoding,
                index=False,
                **kwargs,
            )
        else:
            # Write DataFrame directly
            df.to_csv(
                filepath,
                encoding=encoding,
                index=False,
                **kwargs,
            )

        logger.info(f"Exported {len(df)} rows to {filepath}")

    except Exception as e:
        logger.error(f"Failed to export CSV: {str(e)}")
        raise DataProcessingError(f"Failed to export CSV: {str(e)}") from e


def _write_metadata_header(file_handle: TextIO, metadata: dict[str, Any]) -> None:
    """Write metadata as CSV comments.

    Args:
        file_handle: Open file handle
        metadata: Metadata dictionary
    """
    # Write header
    file_handle.write("# INE Portugal Data Export\n")
    file_handle.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    file_handle.write("#\n")

    # Write metadata fields
    for key, value in metadata.items():
        if value is not None:
            file_handle.write(f"# {key}: {value}\n")

    file_handle.write("#\n")


def read_csv_with_metadata(
    filepath: Path,
    encoding: str = "utf-8-sig",
    **kwargs: Any,
) -> tuple[pd.DataFrame, dict[str, str]]:
    """Read CSV file and extract metadata from comments.

    Args:
        filepath: CSV file path
        encoding: File encoding
        **kwargs: Additional arguments passed to pd.read_csv()

    Returns:
        Tuple of (DataFrame, metadata_dict)

    Example:
        >>> df, metadata = read_csv_with_metadata(Path("output.csv"))
        >>> print(metadata["indicator"])
    """
    try:
        filepath = Path(filepath)

        # Read metadata from comments
        metadata = {}
        with open(filepath, encoding=encoding) as f:
            for line in f:
                if not line.startswith("#"):
                    break

                # Parse metadata lines (format: "# key: value")
                if ":" in line and not line.startswith("# Generated:"):
                    line = line.lstrip("#").strip()
                    if ":" in line:
                        key, value = line.split(":", 1)
                        metadata[key.strip()] = value.strip()

        # Read DataFrame
        df = pd.read_csv(filepath, encoding=encoding, comment="#", **kwargs)

        logger.debug(f"Read {len(df)} rows from {filepath}")

        return df, metadata

    except Exception as e:
        logger.error(f"Failed to read CSV: {str(e)}")
        raise DataProcessingError(f"Failed to read CSV: {str(e)}") from e
