# Project TODO List

This document outlines suggested improvements and refactorings for the `pyine` project, categorized by impact and area.

## High-Level / Architectural Improvements

*   **Centralized Error Handling for CLI:** Implement a decorator or Click's context-based error handling to reduce repetitive `try...except` blocks in `src/pyine/cli/main.py`. This will make the CLI more robust and maintainable.
*   **`Indicator` and `IndicatorMetadata` Model Relationship:** Refactor `src/pyine/models/indicator.py` to make `IndicatorMetadata` inherit from `Indicator` to reduce redundancy and clarify their relationship. Standardize naming (`varcd` vs. `indicator_code`, `title` vs. `indicator_name`) across these models.
*   **`CacheManager` Role Clarification:** Re-evaluate the need for `src/pyine/cache/manager.py`. If the `INE` class's cache methods are sufficient, consider removing `CacheManager`. Otherwise, clearly define its distinct purpose and usage guidelines.

## Mid-Level / Design Improvements

*   **`INE.__init__` Client Initialization:** Reduce boilerplate in `src/pyine/ine.py` by potentially using a helper function or a configuration object to handle common client initialization parameters.
*   **`INE.get_data` Return Type Consistency:** Consider making `INE.get_data` always return a `DataResponse` object. Users can then call `to_dataframe()`, `to_json()`, etc., directly on the `DataResponse` object, simplifying the `get_data` signature and improving consistency.
*   **`CatalogueBrowser.search` and `filter_by_theme` Integration:** Modify `CatalogueBrowser.search` in `src/pyine/search/catalog.py` to accept a `theme` parameter. This would allow the CLI's `search` command to use a single, more intuitive filtering mechanism when both query and theme are provided.
*   **`DataClient.get_data_paginated` Implementation:** Implement true pagination in `src/pyine/client/data.py` if the INE API supports it. If not, adjust the method's behavior or rename it to accurately reflect its "get all data" functionality.
*   **`DataClient._process_data_point` Error Handling:** Refine error handling in `src/pyine/client/data.py` to catch more specific exceptions (e.g., `ValueError`, `TypeError`) and reconsider silently dropping data points. Provide clearer warnings or errors if data points are frequently dropped.
*   **`DataClient.validate_dimensions` Implementation:** Prioritize implementing full dimension validation in `src/pyine/client/data.py`. This would prevent invalid API requests and provide better feedback to users.
*   **`CatalogueClient._parse_indicator_xml` Helper Function:** Move the nested `get_text` helper function from `_parse_indicator_xml` in `src/pyine/client/catalogue.py` to be a private method of the `CatalogueClient` class (e.g., `self._get_element_text`) or a static method.
*   **`json_to_dataframe` `data` Parameter Handling:** Clarify and potentially refine the logic for handling dictionary inputs without a "dados" key in `src/pyine/processors/dataframe.py` to avoid unexpected behavior.
*   **`pivot_by_dimension` and `aggregate_by_period` `value_column` Handling:** Adjust the logic in `src/pyine/processors/dataframe.py` to correctly handle `value_column` when it is provided as a list of strings.
*   **`merge_json_files` `merge_key` Parameter:** In `src/pyine/processors/json.py`, either implement the merging logic based on the `merge_key` parameter or remove the parameter if it's not intended for use. Add a `TODO` comment if it's a planned future enhancement.

## Low-Level / Code Quality Improvements

*   **`INEClient._parse_json_response` Debug Logging:** Optimize the debug logging in `src/pyine/client/base.py` to avoid potentially expensive `len(str(data))` calls for very large JSON responses.
*   **`CatalogueClient` Consistent Error Re-raising:** In `src/pyine/client/catalogue.py`, ensure all `try...except` blocks re-raise exceptions using `raise SomeSpecificError(...) from e` to preserve the original exception chain.
*   **`MetadataClient` Custom `DimensionNotFoundError`:** Consider creating a more specific custom exception (e.g., `DimensionNotFoundError`) in `src/pyine/client/metadata.py` to distinguish it from generic `ValueError` types.
*   **`unflatten_json` Unit Tests:** Add more comprehensive unit tests for the array indexing logic in `unflatten_json` in `src/pyine/processors/json.py` to cover various edge cases.
*   **`CatalogueBrowser.get_recently_updated` `type: ignore`:** Review and potentially remove the `type: ignore` comment in `src/pyine/search/catalog.py` by ensuring the type checker correctly infers the type after filtering `None` values.
*   **`cli.main.py` `cache_info` Output:** In `src/pyine/cli/main.py`, leverage the `CacheManager.format_stats()` method for displaying cache information to ensure consistent and well-formatted output.
*   **`_get_disk_cache` Type Hinting:** In `src/pyine/client/base.py`, ensure `_disk_cache` is correctly typed as `Optional[Type[DiskCache]]` to improve type safety.
*   **`_create_session` and `_get_session_for_endpoint` `cast` Usage:** Review and remove unnecessary `cast` calls in `src/pyine/client/base.py` if the types are correctly inferred or explicitly defined.
*   **`json_to_dataframe` Column Renaming:** While generally fine, be aware that `col.replace("_", " ").strip()` might not handle all possible "internal prefixes" if they are not just underscores.
*   **`json_to_dataframe` Date Parsing:** The `_parse_date_column` function is a good approach to centralize date parsing logic.
*   **`_get_directory_size` Error Handling:** The error handling in `src/pyine/cache/disk.py` is generally fine for a utility function.

## API Documentation Alignment & Robustness

These suggestions are based on comparing the `pyine` implementation with the official INE API documentation for the Catalogue, Database, and Metadata endpoints.


*   **Refine Pagination in `DataClient.get_data_paginated`:**
    *   **Location:** `src/pyine/client/data.py`
    *   **Details:** The Database API documentation mentions "data in chunks." Investigate the API documentation for specific pagination mechanisms (e.g., offset/limit, page numbers). Implement true pagination in `DataClient.get_data_paginated` to efficiently handle very large datasets.
*   **Robustness of List Responses (Documentation Clarification):**
    *   **Location:** `src/pyine/client/data.py`, `src/pyine/client/metadata.py`
    *   **Details:** `pyine` has been updated to handle cases where the API returns a list instead of a dictionary for single indicator data/metadata. While the current fix works, if the API consistently returns a list for certain indicators, it might be worth clarifying this behavior in the API documentation or adapting `pyine` to explicitly expect this for specific `varcd`s if that's the pattern.
*   **Implement Full Dimension Validation:**
    *   **Location:** `src/pyine/client/data.py`
    *   **Details:** The Database API explicitly mentions `DimX={value}` for dimension filters. `pyine` has `DataClient.validate_dimensions` as a placeholder. Use the API documentation (for specific indicators) to implement full validation of `DimX` keys and their possible `value`s.