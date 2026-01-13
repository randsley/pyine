# pyine - INE Portugal API Client

[![Python 3.8-3.14](https://img.shields.io/badge/python-3.8--3.14-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

High-level Python client for Statistics Portugal (INE) API. Query and download statistical data from [INE Portugal](https://www.ine.pt) with a simple, intuitive interface.

## Features

- 🎯 **High-level convenience API** - Simple interface for common tasks
- 📊 **Multiple output formats** - pandas DataFrames, JSON, CSV
- 💾 **Smart caching** - Disk-based caching to reduce API calls
- 🔍 **Metadata browsing** - Search and discover indicators
- 🖥️ **Command-line interface** - CLI tool for quick data access
- 📖 **Type hints** - Full type annotations for IDE support
- ✅ **Comprehensive testing** - 82% test coverage

## Installation

```bash
pip install pyine
```

For development:

```bash
pip install pyine[dev]
```

## Quick Start

```python
from pyine import INE

# Initialize client
ine = INE(language="EN")

# Search for indicators
results = ine.search("population")
for indicator in results:
    print(f"{indicator.varcd}: {indicator.title}")

# Get data as DataFrame
df = ine.get_data("0004167")
print(df.head())

# Get data with dimension filters
df = ine.get_data(
    "0004167",
    dimensions={"Dim1": "2023", "Dim2": "1"}  # Year 2023, Portugal
)

# Export to CSV
ine.export_csv("0004167", "population.csv")
```

## Command Line Usage

```bash
# Search for indicators
pyine search "gdp"

# Download data
pyine download 0004167 --output data.csv

# Get indicator information
pyine info 0004167

# List available themes
pyine list-commands themes

# Clear cache
pyine cache clear
```

## Documentation

### Basic Usage

#### Initialize Client

```python
from pyine import INE

# English language (default)
ine = INE(language="EN")

# Portuguese language
ine = INE(language="PT")

# Disable caching
ine = INE(cache=False)

# Custom cache directory
from pathlib import Path
ine = INE(cache_dir=Path("/custom/cache"))
```

#### Search for Indicators

```python
# Search by keyword
results = ine.search("population")

# Filter by theme
results = ine.filter_by_theme(theme="Labour Market")
```

#### Get Indicator Data

```python
# Get all data for an indicator
df = ine.get_data("0004167")

# Get data with filters
df = ine.get_data(
    "0004167",
    dimensions={
        "Dim1": "2023",  # Year
        "Dim2": "5"      # Geographic region
    }
)

# Get data as JSON
json_data = ine.get_data("0004167", output_format="json")

# Get data as dictionary
dict_data = ine.get_data("0004167", output_format="dict")
```

#### Get Metadata

```python
# Get indicator metadata
metadata = ine.get_metadata("0004167")
print(metadata.indicator_name)
print(metadata.unit)

# Get available dimensions
dimensions = ine.get_dimensions("0004167")
for dim in dimensions:
    print(f"Dimension {dim.id}: {dim.name}")
    for value in dim.values:
        print(f"  {value.code}: {value.label}")
```

#### Export Data

```python
# Export to CSV
ine.export_csv("0004167", "output.csv")

# Export with metadata header
ine.export_csv(
    "0004167",
    "output.csv",
    include_metadata=True
)

# Export with dimension filters
ine.export_csv(
    "0004167",
    "output.csv",
    dimensions={"Dim1": "2023"}
)
```

### CLI Commands

#### Search Command

```bash
# Basic search
pyine search "population"

# Search with theme filter
pyine search "population" --theme "Population"

# Limit results
pyine search "gdp" --limit 5

# Portuguese language
pyine search "população" --lang PT
```

#### Download Command

```bash
# Download to CSV (default)
pyine download 0004167 --output data.csv

# Download as JSON
pyine download 0004167 --output data.json --output-format json

# Download with dimension filters
pyine download 0004167 --output data.csv -d Dim1=2023 -d Dim2=1
```

#### Info Command

```bash
# Get indicator information
pyine info 0004167

# Portuguese language
pyine info 0004167 --lang PT
```

#### List Command

```bash
# List all themes
pyine list-commands themes

# List indicators in a theme
pyine list-commands indicators --theme "Population"
```

#### Dimensions Command

```bash
# Get available dimensions for an indicator
pyine dimensions 0004167
```

#### Cache Commands

```bash
# Show cache information
pyine cache info

# Clear cache
pyine cache clear
```

## API Reference

### INE Class

Main interface to INE Portugal API.

```python
INE(
    language: str = "EN",
    cache: bool = True,
    cache_dir: Optional[Path] = None,
    cache_ttl: int = 86400
)
```

#### Methods

- `search(query: str, **kwargs) -> List[Indicator]` - Search for indicators
- `get_data(varcd: str, dimensions=None, output_format="dataframe")` - Get indicator data
- `get_metadata(varcd: str) -> IndicatorMetadata` - Get indicator metadata
- `get_dimensions(varcd: str) -> List[Dimension]` - Get available dimensions
- `export_csv(varcd: str, filepath: str, ...)` - Export data to CSV
- `validate_indicator(varcd: str) -> bool` - Check if indicator exists

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/nigelrandsley/pyine.git
cd pyine

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pyine --cov-report=html

# Run specific test file
pytest tests/test_client/test_base.py

# Run live API tests (optional)
pytest tests/ -m live
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type check
mypy src/
```

## Project Structure

```
pyine/
├── src/pyine/           # Main package
│   ├── client/          # API clients
│   ├── models/          # Data models
│   ├── cache/           # Caching system
│   ├── processors/      # Data transformation
│   ├── search/          # Metadata search
│   ├── utils/           # Utilities
│   └── cli/             # Command-line interface
├── tests/               # Test suite
├── examples/            # Usage examples
└── docs/                # Documentation
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Data provided by [INE Portugal](https://www.ine.pt)
- Inspired by the [ineptR](https://c-matos.github.io/ineptR/) R package

## Links

- **Homepage**: https://github.com/nigelrandsley/pyine
- **Documentation**: https://pyine.readthedocs.io
- **PyPI**: https://pypi.org/project/pyine/
- **INE Portugal**: https://www.ine.pt
- **INE API Documentation**: https://www.ine.pt/xportal/xmain?xpid=INE&xpgid=ine_api&INST=322751522

## Changelog

### 0.1.0 (2026-01-13)

- Initial release
- Core API client functionality
- Data retrieval and processing
- Caching system
- Command-line interface
- Basic search functionality
