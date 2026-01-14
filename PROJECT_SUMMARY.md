# pyine - Project Summary

## Overview

**pyine** is a high-level Python client for the INE Portugal (Statistics Portugal) API. It provides a simple, intuitive interface to query and download statistical data from https://www.ine.pt.

## Project Statistics

- **Source Files**: 25 Python files
- **Test Files**: 18 test files
- **Total Tests**: 136 tests
- **Test Coverage**: 73%
- **Python Version**: 3.8+
- **License**: MIT

## Package Structure

```
pyine/
├── src/pyine/                    # Main package (1,265 lines of code)
│   ├── __init__.py               # Public API exports
│   ├── __version__.py            # Version string
│   ├── ine.py                    # High-level INE class (82 lines)
│   │
│   ├── client/                   # Low-level API clients (332 lines)
│   │   ├── base.py               # Base HTTP client with retry logic
│   │   ├── catalogue.py          # XML catalogue endpoint
│   │   ├── data.py               # JSON data endpoint
│   │   └── metadata.py           # JSON metadata endpoint
│   │
│   ├── models/                   # Pydantic data models (86 lines)
│   │   ├── indicator.py          # Indicator, Dimension models
│   │   └── response.py           # API response wrappers
│   │
│   ├── cache/                    # Caching system (144 lines)
│   │   ├── backend.py            # Cache interface
│   │   ├── disk.py               # SQLite cache implementation
│   │   └── manager.py            # Cache management utilities
│   │
│   ├── processors/               # Data transformation (265 lines)
│   │   ├── dataframe.py          # JSON to pandas DataFrame
│   │   ├── csv.py                # CSV export with metadata
│   │   └── json.py               # JSON utilities
│   │
│   ├── search/                   # Metadata search (104 lines)
│   │   └── catalog.py            # Catalogue browser/search
│   │
│   ├── utils/                    # Utilities (20 lines)
│   │   └── exceptions.py         # Custom exceptions
│   │
│   └── cli/                      # Command-line interface (212 lines)
│       └── main.py               # CLI with Click framework
│
├── tests/                        # Test suite (136 tests)
│   ├── conftest.py               # pytest fixtures
│   ├── fixtures/                 # Sample API responses
│   ├── test_client/              # Client tests (46 tests)
│   ├── test_cache/               # Cache tests (11 tests)
│   ├── test_processors/          # Processor tests (31 tests)
│   ├── test_search/              # Search tests (14 tests)
│   ├── test_integration/         # Integration tests (10 tests)
│   └── test_cli/                 # CLI tests (21 tests)
│
└── examples/                     # Usage examples
    ├── basic_usage.py            # 10 basic examples
    ├── advanced_filtering.py     # 10 advanced examples
    └── cli_examples.sh           # CLI usage examples
```

## Key Features

### 1. High-Level API
- Simple, intuitive interface with the `INE` class
- Methods: `search()`, `get_data()`, `get_metadata()`, `export_csv()`, etc.
- Support for both English and Portuguese languages
- Type-hinted for excellent IDE support

### 2. Multiple Output Formats
- **pandas DataFrame** - For data analysis
- **JSON** - For web applications
- **CSV** - For Excel and other tools
- **Dictionary** - For programmatic access

### 3. Smart Caching
- Two-tier caching: metadata (7 days) and data (1 day)
- SQLite-based with requests-cache
- Platform-specific cache directories
- Cache management commands

### 4. Metadata Browsing
- Full-text search across indicators
- Theme-based filtering
- Recently updated indicators
- Dimension exploration

### 5. Command-Line Interface
- 8 main commands: `search`, `info`, `download`, `dimensions`, `list-commands`, `cache`
- Colored output for better readability
- Progress feedback and error handling
- Help text with examples

### 6. Comprehensive Testing
- Unit tests for all components
- Integration tests for end-to-end workflows
- CLI tests with Click's testing framework
- Mocked HTTP requests using responses library
- 73% code coverage

## API Endpoints Used

The package interacts with three INE Portugal API endpoints:

1. **Catalogue API** (`/ine/xml_indic.jsp`) - XML indicator metadata
2. **Data API** (`/ine/json_indicador/pindica.jsp`) - JSON statistical data
3. **Metadata API** (`/ine/json_indicador/pindicaMeta.jsp`) - JSON dimension metadata

## Dependencies

### Core Dependencies
- `requests>=2.28.0` - HTTP client
- `pandas>=1.5.0` - DataFrame processing
- `click>=8.0.0` - CLI framework
- `requests-cache>=1.0.0` - HTTP caching
- `lxml>=4.9.0` - XML parsing
- `pydantic>=2.0.0` - Data validation
- `platformdirs>=3.0.0` - Cross-platform paths

### Development Dependencies
- `pytest>=7.0.0` - Testing framework
- `pytest-cov>=4.0.0` - Coverage reporting
- `responses>=0.22.0` - Mock HTTP requests
- `black>=23.0.0` - Code formatting
- `ruff>=0.1.0` - Fast linting
- `mypy>=1.0.0` - Type checking

## Usage Examples

### Python API

```python
from pyine import INE

# Initialize
ine = INE(language="EN")

# Search for indicators
results = ine.search("population")

# Get data as DataFrame
df = ine.get_data("0004167").to_dataframe()

# Export to CSV
ine.export_csv("0004167", "data.csv")
```

### Command Line

```bash
# Search
pyine search "gdp"

# Download
pyine download 0004167 --output data.csv

# Get info
pyine info 0004167

# List themes
pyine list-commands themes
```

## Test Coverage Breakdown

| Module | Coverage |
|--------|----------|
| INE class | 99% |
| Base client | 95% |
| Metadata client | 86% |
| Data client | 77% |
| Catalogue client | 85% |
| Search module | 86% |
| DataFrame processors | 34% |
| CLI | 91% |
| JSON processors | 67% |
| CSV processors | 87% |
| Cache | 67% |
| **Overall** | **73%** |

## Code Quality

- ✅ Full type hints on all public APIs
- ✅ Comprehensive docstrings (Google style)
- ✅ PEP 8 compliant (black formatted)
- ✅ Linting passed (ruff)
- ✅ Type checking addressed (mypy)
- ✅ 136 tests, all passing
- ✅ No critical security issues

## Error Handling

Custom exception hierarchy:
- `INEError` - Base exception
- `APIError` - API request failures
- `InvalidIndicatorError` - Invalid indicator codes
- `DimensionError` - Dimension-related errors
- `CacheError` - Cache operations
- `RateLimitError` - Rate limiting
- `DataProcessingError` - Data processing failures

## Performance Considerations

- **Caching**: Reduces API calls significantly (7-day metadata cache, 1-day data cache)
- **Retry logic**: Automatic retries with exponential backoff
- **Connection pooling**: Reuses HTTP connections
- **Lazy imports**: Circular import avoidance with lazy loading

## Installation

```bash
# From source (development)
pip install -e .

# With development dependencies
pip install -e ".[dev]"
```

## Future Enhancements (Not Implemented)

Possible future improvements:
- Async API support
- Data visualization helpers
- More export formats (Parquet, Excel with formulas)
- Live API tests (currently mocked)
- Pre-commit hooks setup
- CI/CD pipeline
- ReadTheDocs documentation
- PyPI publication

## Contributors

- Initial implementation: Nigel Randsley
- Project owner: Nigel Randsley

## Acknowledgments

- Data provided by [INE Portugal](https://www.ine.pt)

## License

MIT License - See LICENSE file for details

---

**Project Status**: ✅ Complete and ready for use

**Last Updated**: 2026-01-14

**Version**: 0.1.2