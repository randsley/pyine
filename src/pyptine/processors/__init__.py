"""Data processing utilities for pyptine package."""

from pyptine.processors.csv import (
    export_to_csv,
    read_csv_with_metadata,
)
from pyptine.processors.dataframe import (
    aggregate_by_period,
    clean_dataframe,
    filter_by_geography,
    get_latest_period,
    json_to_dataframe,
    merge_metadata,
    pivot_by_dimension,
)
from pyptine.processors.excel import (
    export_multiple_sheets,
    format_for_excel,
)
from pyptine.processors.json import (
    export_to_json,
    export_to_jsonl,
    flatten_json,
    format_json,
    merge_json_files,
    read_jsonl,
    unflatten_json,
)

__all__ = [
    # DataFrame processing
    "json_to_dataframe",
    "pivot_by_dimension",
    "clean_dataframe",
    "merge_metadata",
    "aggregate_by_period",
    "filter_by_geography",
    "get_latest_period",
    # CSV export
    "export_to_csv",
    "read_csv_with_metadata",
    "export_multiple_sheets",
    "format_for_excel",
    # JSON processing
    "format_json",
    "export_to_json",
    "export_to_jsonl",
    "read_jsonl",
    "flatten_json",
    "unflatten_json",
    "merge_json_files",
]
