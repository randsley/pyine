# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-01-27

### Added

- **Real-time Progress Tracking**: First-run catalogue downloads now show real-time progress with spinner, bytes downloaded, and transfer speed
- **Context-aware Progress Display**: Automatically detects cached vs fresh downloads and shows appropriate progress indicators
- **Progress Callback API**: Full API support for progress tracking throughout the call chain (`INE.search()`, `INE.list_themes()`, etc.)
- **Cache Detection**: New `CatalogueBrowser.is_catalogue_cached()` method to determine if catalogue needs downloading

### Fixed

- **Windows Compatibility**: Fixed Unicode symbol encoding issues in CLI output (✓, ✗, ℹ symbols now use ASCII-safe alternatives on Windows)

### Changed

- **Indeterminate Progress**: Uses spinner-based progress for catalogue downloads (INE API doesn't provide Content-Length header)
- **Improved UX**: Users now see clear feedback during first-run downloads with informative messages

## [0.2.0] - 2026-01-16 (Unreleased)

### Added

#### Async Support
- **AsyncINE Client**: Non-blocking I/O for concurrent requests using httpx
- **Async Iterators**: Memory-efficient streaming with `async for` support in `get_all_data()`
- **Connection Pooling**: Automatic connection management and retries for async operations
- **Concurrent Requests**: Fetch multiple indicators simultaneously using `asyncio.gather()`

#### Data Visualization
- **Interactive Charts**: Create plotly visualizations directly from `DataResponse` objects
- **Multiple Chart Types**: Support for line, bar, area, and scatter plots
- **Visualization Methods**: `plot()`, `plot_line()`, `plot_bar()`, `plot_area()`, `plot_scatter()`
- **Customization**: Color coding, custom axes, markers, and export to HTML/PNG/SVG

#### Advanced Analytics
- **Year-over-year Growth**: `calculate_yoy_growth()` method on `DataResponse`
- **Month-over-month Changes**: `calculate_mom_change()` method
- **Moving Averages**: `calculate_moving_average(window)` for trend analysis
- **Exponential Moving Averages**: `calculate_exponential_moving_average(span)` for weighted averages
- **Chainable Operations**: Combine multiple analyses (e.g., `response.calculate_yoy_growth().calculate_moving_average(3)`)

#### CLI Enhancements
- **Rich Formatting**: Beautiful tables, panels, and colored output using rich library
- **Progress Indicators**: Spinners and progress bars for long-running operations
- **Better Error Handling**: User-friendly error messages with context
- **Configurable Timeout**: Added `--timeout` option for search command

#### True Pagination
- **`get_all_data()` Method**: Automatically handles datasets exceeding 40,000 data point limit
- **Streaming Support**: Process large datasets in memory-efficient chunks
- **Customizable Chunk Size**: Control memory usage with configurable chunk sizes

### Changed

- **CLI Parameter**: Renamed `format` to `output_format` in download command
- **Dependencies**: Added httpx (async), plotly (visualization), rich (CLI formatting)

### Fixed

- **Duplicate API Calls**: Eliminated duplicate search API calls in search command
- **Type Checking**: Resolved mypy type checking errors
- **Code Quality**: Fixed ruff linting issues and applied black formatting throughout
- **Test Reliability**: Replaced flaky dimension test with stable download test

## [0.1.3] - 2026-01-15

### Fixed

- **INE API Compatibility**: Updated data and metadata clients to handle new INE Portugal API response format:
  - Modified `DataClient._parse_data_response()` to support PascalCase field names (`IndicadorCod`, `IndicadorDsg`, `UnidadeMedida`) alongside old lowercase names
  - Updated data parsing to handle new nested `Dados` structure (object with years as keys) vs old flat array format
  - Added fallback to fetch unit information from metadata endpoint when not present in data response
  - Modified `MetadataClient._parse_metadata_response()` to support both old and new field naming conventions
  - Added new `_parse_dimensions_new_format()` method to handle complex dimension structure with `Descricao_Dim` and `Categoria_Dim`
  - Updated date parsing to handle both ISO format and YYYY-MM-DD format
  - Library now maintains backward compatibility with old API format while fully supporting the new format

### Changed

- **Error Handling**: Improved error handling for metadata fetching when unit information is missing from data responses

## [0.1.2] - 2026-01-14

### Fixed

- **Python 3.8 Compatibility**:
  - Resolved `TypeError: 'type' object is not subscriptable` by replacing `tuple` with `typing.Tuple` in `src/pyptine/processors/csv.py`.
  - Fixed `NameError` for `Union`, `Path`, and `DataResponse` by adding missing imports in `src/pyptine/client/metadata.py`, `src/pyptine/client/data.py`, and `src/pyptine/ine.py` respectively.
- **Code Style**:
  - Ran `black` on `src/pyptine/processors/dataframe.py` to fix formatting issues.
  - Removed redundant `type: str` comments in `src/pyptine/processors/excel.py`.

### Refactored

- **Client Robustness**: Modified `_make_request` in `src/pyptine/client/base.py` to create a copy of the `params` dictionary, preventing side effects.
- **Type Hinting**: Improved type safety by replacing `Any` with `TextIO` for the `file_handle` parameter in `src/pyptine/processors/csv.py`.

## [0.1.1] - 2026-01-13

### Fixed

- **API Compatibility**: Updated XML parsing logic to align with recent INE API changes, resolving `Could not find NewDataSet in XML` errors.
- **Test Suite**: Fixed failing tests in `tests/test_cli/test_commands.py`, `tests/integration/test_end_to_end.py`, and `tests/test_client/test_catalogue.py` due to API changes and parameter renaming.
- **Code Quality**: Addressed various linting issues (`SIM108`, `B904`, `A002`, `A001`, `N806`, `B007`, `F841`) and applied code formatting with `black`.

### Changed

- **Indicator Model**: Added a `source` field to the `Indicator` Pydantic model to better reflect API responses.
- **CLI Parameters**: Renamed `format` parameter to `output_format` in `pyptine download` command to avoid shadowing Python's built-in `format` function.
- **CLI Commands**: Renamed `list` command group to `list-commands` to avoid shadowing Python's built-in `list` function.

### Added

- **Complete Catalogue Access**: Implemented `opc=2` for `CatalogueClient` to fetch the complete list of indicators, and updated `CatalogueBrowser.get_all_indicators()` to use it.

## [0.1.0] - 2026-01-13

### Added

#### Python 3.14 Support ✨
- Tested and verified full compatibility with Python 3.14.2
- All 133 tests pass successfully (82% coverage)
- Updated CI/CD to test Python 3.8-3.14
- Added compatibility documentation
- Initial release of pyptine
- High-level `INE` class for easy API access
- Support for English and Portuguese languages
- Multiple output formats (DataFrame, JSON, CSV, dict)
- Smart two-tier caching system (metadata: 7 days, data: 1 day)
- Full-text search across indicators
- Theme-based filtering
- Dimension exploration and filtering
- Command-line interface with 8 commands:
  - `search` - Search for indicators
  - `info` - Get indicator details
  - `download` - Download data to file
  - `dimensions` - List available dimensions
  - `list themes` - List all themes
  - `list indicators` - List indicators
  - `cache info` - Show cache statistics
  - `cache clear` - Clear cache
- Comprehensive test suite (133 tests, 82% coverage)
- Type hints on all public APIs
- Google-style docstrings
- Examples directory with usage examples

### Features
- **API Clients**: Low-level clients for catalogue, data, and metadata endpoints
- **Data Models**: Pydantic models for data validation
- **Processors**: DataFrame, CSV, and JSON processing utilities
- **Search**: CatalogueBrowser for metadata search
- **Cache**: SQLite-based HTTP caching with requests-cache
- **Error Handling**: Custom exception hierarchy
- **Retry Logic**: Automatic retries with exponential backoff

### Documentation
- Comprehensive README with usage examples
- API reference documentation
- Project summary document
- Three example files (basic usage, advanced filtering, CLI examples)

[0.3.0]: https://github.com/randsley/pyptine/releases/tag/v0.3.0
[0.2.0]: https://github.com/randsley/pyptine/compare/v0.1.3...v0.2.0
[0.1.3]: https://github.com/randsley/pyptine/releases/tag/v0.1.3
[0.1.0]: https://github.com/nigelrandsley/pyptine/releases/tag/v0.1.0
