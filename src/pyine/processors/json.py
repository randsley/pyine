"""JSON processing utilities for pyine."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from pyine.utils.exceptions import DataProcessingError

logger = logging.getLogger(__name__)


def format_json(
    data: Any,
    pretty: bool = True,
    indent: int = 2,
    ensure_ascii: bool = False,
) -> str:
    """Format data as JSON string.

    Args:
        data: Data to format (dict, list, etc.)
        pretty: Use pretty printing with indentation
        indent: Number of spaces for indentation
        ensure_ascii: Escape non-ASCII characters

    Returns:
        Formatted JSON string

    Example:
        >>> data = {"indicator": "0004167", "value": 123}
        >>> json_str = format_json(data)
        >>> print(json_str)
    """
    try:
        if pretty:
            return json.dumps(
                data,
                indent=indent,
                ensure_ascii=ensure_ascii,
                sort_keys=False,
            )
        else:
            return json.dumps(data, ensure_ascii=ensure_ascii)

    except Exception as e:
        logger.error(f"Failed to format JSON: {str(e)}")
        raise DataProcessingError(f"Failed to format JSON: {str(e)}") from e


def export_to_json(
    data: Any,
    filepath: Path,
    pretty: bool = True,
    indent: int = 2,
    ensure_ascii: bool = False,
) -> None:
    """Export data to JSON file.

    Args:
        data: Data to export
        filepath: Output file path
        pretty: Use pretty printing
        indent: Number of spaces for indentation
        ensure_ascii: Escape non-ASCII characters

    Raises:
        DataProcessingError: If export fails

    Example:
        >>> data = {"indicator": "0004167", "values": [1, 2, 3]}
        >>> export_to_json(data, Path("output.json"))
    """
    try:
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            if pretty:
                json.dump(
                    data,
                    f,
                    indent=indent,
                    ensure_ascii=ensure_ascii,
                    sort_keys=False,
                )
            else:
                json.dump(data, f, ensure_ascii=ensure_ascii)

        logger.info(f"Exported data to {filepath}")

    except Exception as e:
        logger.error(f"Failed to export JSON: {str(e)}")
        raise DataProcessingError(f"Failed to export JSON: {str(e)}") from e


def export_to_jsonl(
    data: List[Dict[str, Any]],
    filepath: Path,
    ensure_ascii: bool = False,
) -> None:
    """Export data to JSON Lines format (one JSON object per line).

    JSON Lines format is useful for streaming large datasets.

    Args:
        data: List of dictionaries to export
        filepath: Output file path
        ensure_ascii: Escape non-ASCII characters

    Raises:
        DataProcessingError: If export fails

    Example:
        >>> data = [
        ...     {"id": 1, "value": 100},
        ...     {"id": 2, "value": 200},
        ... ]
        >>> export_to_jsonl(data, Path("output.jsonl"))
    """
    try:
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            for item in data:
                json_line = json.dumps(item, ensure_ascii=ensure_ascii)
                f.write(json_line + "\n")

        logger.info(f"Exported {len(data)} lines to {filepath}")

    except Exception as e:
        logger.error(f"Failed to export JSON Lines: {str(e)}")
        raise DataProcessingError(f"Failed to export JSON Lines: {str(e)}") from e


def read_jsonl(
    filepath: Path,
    max_lines: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Read JSON Lines file.

    Args:
        filepath: JSON Lines file path
        max_lines: Maximum number of lines to read (None for all)

    Returns:
        List of dictionaries

    Example:
        >>> data = read_jsonl(Path("output.jsonl"))
        >>> len(data)
        2
    """
    try:
        filepath = Path(filepath)
        data = []

        with open(filepath, encoding="utf-8") as f:
            for i, line in enumerate(f):
                if max_lines and i >= max_lines:
                    break

                if line.strip():
                    data.append(json.loads(line))

        logger.debug(f"Read {len(data)} lines from {filepath}")

        return data

    except Exception as e:
        logger.error(f"Failed to read JSON Lines: {str(e)}")
        raise DataProcessingError(f"Failed to read JSON Lines: {str(e)}") from e


def flatten_json(
    data: Dict[str, Any],
    separator: str = ".",
    prefix: str = "",
) -> Dict[str, Any]:
    """Flatten nested JSON structure.

    Args:
        data: Nested dictionary
        separator: Separator for nested keys
        prefix: Prefix for keys

    Returns:
        Flattened dictionary

    Example:
        >>> nested = {
        ...     "indicator": "0004167",
        ...     "metadata": {"source": "INE", "year": 2023}
        ... }
        >>> flattened = flatten_json(nested)
        >>> flattened
        {'indicator': '0004167', 'metadata.source': 'INE', 'metadata.year': 2023}
    """
    flattened = {}

    for key, value in data.items():
        new_key = f"{prefix}{separator}{key}" if prefix else key

        if isinstance(value, dict):
            flattened.update(flatten_json(value, separator, new_key))
        elif isinstance(value, list):
            # Convert list to indexed keys
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    flattened.update(flatten_json(item, separator, f"{new_key}[{i}]"))
                else:
                    flattened[f"{new_key}[{i}]"] = item
        else:
            flattened[new_key] = value

    return flattened


def unflatten_json(
    data: Dict[str, Any],
    separator: str = ".",
) -> Dict[str, Any]:
    """Unflatten a flattened JSON structure.

    Args:
        data: Flattened dictionary
        separator: Separator used in keys

    Returns:
        Nested dictionary

    Example:
        >>> flattened = {'indicator': '0004167', 'metadata.source': 'INE'}
        >>> nested = unflatten_json(flattened)
        >>> nested
        {'indicator': '0004167', 'metadata': {'source': 'INE'}}
    """
    result: Dict[str, Any] = {}

    for key, value in data.items():
        parts = key.split(separator)
        target = result

        for part in parts[:-1]:
            # Handle array indices
            if "[" in part:
                base, idx_str = part.split("[")
                idx: int = int(idx_str.rstrip("]"))

                if base not in target:
                    target[base] = []

                # Extend list if needed
                while len(target[base]) <= idx:
                    target[base].append({})

                target = target[base][idx]
            else:
                if part not in target:
                    target[part] = {}
                target = target[part]

        # Set the final value
        final_key = parts[-1]
        target[final_key] = value

    return result


def merge_json_files(
    filepaths: List[Path],
    output_path: Path,
    merge_key: Optional[str] = None,
) -> None:
    """Merge multiple JSON files into one.

    Args:
        filepaths: List of JSON file paths to merge
        output_path: Output file path
        merge_key: Optional key to merge on (for list of dicts)

    Raises:
        DataProcessingError: If merge fails

    Example:
        >>> files = [Path("data1.json"), Path("data2.json")]
        >>> merge_json_files(files, Path("merged.json"))
    """
    try:
        merged_data = []

        for filepath in filepaths:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)

                if isinstance(data, list):
                    merged_data.extend(data)
                else:
                    merged_data.append(data)

        # Export merged data
        export_to_json(merged_data, output_path)

        logger.info(f"Merged {len(filepaths)} files into {output_path}")

    except Exception as e:
        logger.error(f"Failed to merge JSON files: {str(e)}")
        raise DataProcessingError(f"Failed to merge JSON files: {str(e)}") from e
