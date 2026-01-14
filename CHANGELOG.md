# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2026-01-14

### Fixed

- **Python 3.8 Compatibility**:
  - Resolved `TypeError: 'type' object is not subscriptable` by replacing `tuple` with `typing.Tuple` in `src/pyine/processors/csv.py`.
  - Fixed `NameError` for `Union`, `Path`, and `DataResponse` by adding missing imports in `src/pyine/client/metadata.py`, `src/pyine/client/data.py`, and `src/pyine/ine.py` respectively.
- **Code Style**:
  - Ran `black` on `src/pyine/processors/dataframe.py` to fix formatting issues.
  - Removed redundant `type: str` comments in `src/pyine/processors/excel.py`.

### Refactored

- **Client Robustness**: Modified `_make_request` in `src/pyine/client/base.py` to create a copy of the `params` dictionary, preventing side effects.
- **Type Hinting**: Improved type safety by replacing `Any` with `TextIO` for the `file_handle` parameter in `src/pyine/processors/csv.py`.

## [0.1.1] - 2026-01-13

### Fixed

- **API Compatibility**: Updated XML parsing logic to align with recent INE API changes, resolving `Could not find NewDataSet in XML` errors.
- **Test Suite**: Fixed failing tests in `tests/test_cli/test_commands.py`, `tests/integration/test_end_to_end.py`, and `tests/test_client/test_catalogue.py` due to API changes and parameter renaming.
- **Code Quality**: Addressed various linting issues (`SIM108`, `B904`, `A002`, `A001`, `N806`, `B007`, `F841`) and applied code formatting with `black`.

### Changed

- **Indicator Model**: Added a `source` field to the `Indicator` Pydantic model to better reflect API responses.
- **CLI Parameters**: Renamed `format` parameter to `output_format` in `pyine download` command to avoid shadowing Python's built-in `format` function.
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
- Initial release of pyine
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

[0.1.0]: https://github.com/nigelrandsley/pyine/releases/tag/v0.1.0
