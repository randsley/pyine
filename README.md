# pyptine - INE Portugal API Client

[![PyPI version](https://badge.fury.io/py/pyptine.svg)](https://badge.fury.io/py/pyptine)
[![Build Status](https://github.com/nigelrandsley/pyptine/actions/workflows/tests.yml/badge.svg)](https://github.com/nigelrandsley/pyptine)
[![codecov](https://codecov.io/gh/nigelrandsley/pyptine/branch/main/graph/badge.svg?token=YOUR_CODECOV_TOKEN)](https://codecov.io/gh/nigelrandsley/pyptine)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

High-level Python client for Statistics Portugal (INE) API. Query and download statistical data from [INE Portugal](https://www.ine.pt) with a simple, intuitive interface.

## Features

- 🎯 **High-level Convenience API**: Simple interface for common data retrieval and analysis tasks.
- 📊 **Multiple Output Formats**: Export data to pandas DataFrames, JSON, or CSV with ease.
- 💾 **Smart Caching**: Disk-based caching reduces redundant API calls, speeding up repeated queries.
- 🔍 **Metadata Browsing**: Search and discover indicators, themes, and dimensions.
- 🖥️ **Command-Line Interface**: A powerful CLI for quick data access and scripting.
- 📖 **Modern Python**: Fully type-annotated for better developer experience and IDE support.
- ✅ **Well-Tested**: Comprehensive test suite with 73% code coverage.
- 🔄 **API Compatible**: Supports both old and new INE API response formats seamlessly.

## Installation

```bash
pip install pyptine
```

For development, install with all extra dependencies:

```bash
pip install "pyptine[dev,docs]"
```

## Quick Start

```python
from pyptine import INE

# Initialize the client
ine = INE(language="EN")

# 1. Search for an indicator
print("Searching for 'gdp' indicators...")
results = ine.search("gdp")
for indicator in results[:5]:  # Print top 5 results
    print(f"- {indicator.varcd}: {indicator.title}")

# 2. Get data for a specific indicator
varcd = "0004167"  # Resident population
print(f"\nFetching data for indicator {varcd}...")
response = ine.get_data(varcd)

# 3. Convert to a pandas DataFrame
df = response.to_dataframe()
print("\nData as DataFrame:")
print(df.head())

# 4. Export data to a CSV file
output_file = "population_data.csv"
print(f"\nExporting data to {output_file}...")
ine.export_csv(varcd, output_file)
print("Done!")
```

## Command-Line Usage

The pyptine CLI provides a convenient way to access INE data from your terminal, with rich formatting and progress indicators for a better user experience.

```bash
# Search for indicators related to "pib" (GDP in Portuguese)
pyptine search "pib"

# Get detailed information about a specific indicator
pyptine info 0004127

# Download data for an indicator to a CSV file (with progress bar)
pyptine download 0004127 --output data.csv

# Download data and filter by dimensions
pyptine download 0004167 --output filtered_data.csv -d Dim1=S7A2023 -d Dim2=PT

# List all available statistical themes (in formatted table)
pyptine list-commands themes

# List all indicators (with pagination support)
pyptine list-commands indicators --limit 50

# View available dimensions for an indicator
pyptine dimensions 0004167

# Clear the local cache
pyptine cache clear
```

**CLI Features:**
- **Rich Formatting** - Tables, panels, and colored output for better readability
- **Progress Indicators** - Spinners and progress bars for long-running operations
- **Error Handling** - Centralized, user-friendly error messages with context
- **Better Organization** - Data displayed in well-formatted tables rather than plain text

## Documentation

### Initializing the Client

The `INE` class is the main entry point.

```python
from pyptine import INE
from pathlib import Path

# Default client (language='EN', caching=True)
ine = INE()

# Client with Portuguese language
ine_pt = INE(language="PT")

# Disable caching
ine_no_cache = INE(cache=False)

# Use a custom cache directory
ine_custom_cache = INE(cache_dir=Path("/path/to/custom/cache"))
```

### Working with Indicators

#### Searching for Indicators

You can search for indicators by keyword and filter by theme or sub-theme.

```python
# Basic search
results = ine.search("unemployment rate")

# Search within a specific theme
results = ine.search("employment", theme="Labour market")
```

#### Getting Indicator Metadata

Retrieve detailed information about an indicator, including its dimensions.

```python
metadata = ine.get_metadata("0004167")
print(f"Title: {metadata.title}")
print(f"Unit: {metadata.unit}")
print(f"Source: {metadata.source}")

# List available dimensions
dimensions = ine.get_dimensions("0004167")
for dim in dimensions:
    print(f"\nDimension: {dim.name}")
    for value in dim.values[:5]:  # Show first 5 values
        print(f"- {value.code}: {value.label}")
```

### Fetching and Exporting Data

#### Getting Data

The `get_data` method returns a `DataResponse` object, which can be easily converted to different formats.

```python
response = ine.get_data("0004127")

# Convert to pandas DataFrame
df = response.to_dataframe()

# Convert to a dictionary
data_dict = response.to_dict()

# Get data as a JSON string
json_str = response.to_json()
```

#### Filtering Data with Dimensions

Use the `dimensions` parameter to filter data before downloading.

```python
# Get data for the year 2023 and region "Portugal"
# Note: Dimension values use specific codes (e.g., 'S7A2023' for year 2023)
filtered_response = ine.get_data(
    "0004167",
    dimensions={
        "Dim1": "S7A2023",  # Year 2023
        "Dim2": "PT"        # Geographic region 'Portugal'
    }
)
df_filtered = filtered_response.to_dataframe()
```

#### Exporting Data

You can export data directly to CSV or JSON files.

```python
# Export to CSV
ine.export_csv("0004127", "output.csv")

# Export to JSON with pretty printing
ine.export_json("0004127", "output.json", pretty=True)

# Export filtered data
ine.export_csv(
    "0004167",
    "filtered_output.csv",
    dimensions={"Dim1": "S7A2023"}
)
```

#### Working with Large Datasets

For large datasets that exceed the default 40,000 data point limit, use the `get_all_data()` method which automatically handles pagination:

```python
from pyptine.client.data import DataClient

client = DataClient(language="EN")

# Fetch data in chunks (default chunk_size=40,000)
for chunk in client.get_all_data("0004127"):
    df = chunk.to_dataframe()
    print(f"Processed {len(df)} rows")
    # Process each chunk

# Custom chunk size
for chunk in client.get_all_data("0004127", chunk_size=5000):
    # Process smaller chunks
    pass

# Combine all chunks into a single dataset
all_chunks = list(client.get_all_data("0004127"))
all_data = [point for chunk in all_chunks for point in chunk.data]
```

#### Advanced Data Analysis

Perform statistical calculations on indicator data directly within the library:

```python
# Get data and calculate year-over-year growth
response = ine.get_data("0004127")
yoy_response = response.calculate_yoy_growth()
df_yoy = yoy_response.to_dataframe()
print(df_yoy[['Period', 'value', 'yoy_growth']])

# Calculate month-over-month changes
mom_response = response.calculate_mom_change()
df_mom = mom_response.to_dataframe()

# Calculate simple moving average (3-period)
ma_response = response.calculate_moving_average(window=3)
df_ma = ma_response.to_dataframe()

# Calculate exponential moving average
ema_response = response.calculate_exponential_moving_average(span=5)
df_ema = ema_response.to_dataframe()

# Chain multiple analyses
result = response.calculate_yoy_growth().calculate_moving_average(window=2)
df = result.to_dataframe()
print(df[['Period', 'value', 'yoy_growth', 'moving_avg']])
```

Available analysis methods on `DataResponse`:
- `calculate_yoy_growth()` - Year-over-year percentage change
- `calculate_mom_change()` - Month-over-month percentage change
- `calculate_moving_average(window)` - Simple moving average
- `calculate_exponential_moving_average(span)` - Exponential weighted moving average

All methods support custom `value_column` and `period_column` parameters to work with different data structures.

## API Reference

### `INE` Class

The main class for interacting with the INE API.

`INE(language: str = "EN", cache: bool = True, cache_dir: Optional[Path] = None, cache_ttl: int = 86400)`

| Method | Description |
| --- | --- |
| `search(query, ...)` | Search for indicators. |
| `get_data(varcd, ...)` | Get data for an indicator as a `DataResponse` object. |
| `get_metadata(varcd)` | Get detailed metadata for an indicator. |
| `get_dimensions(varcd)` | Get available dimensions for an indicator. |
| `get_indicator(varcd)` | Get catalogue information for a single indicator. |
| `validate_indicator(varcd)` | Check if an indicator code is valid. |
| `list_themes()` | Get a list of all available themes. |
| `export_csv(varcd, ...)` | Export indicator data to a CSV file. |
| `export_json(varcd, ...)` | Export indicator data to a JSON file. |
| `clear_cache()` | Clear all cached data. |
| `get_cache_info()` | Get statistics about the cache. |

---

## Development

### Setup

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/nigelrandsley/pyptine.git
cd pyptine

# Install in editable mode with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks to ensure code quality
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=src/pyptine --cov-report=term-missing
```

### Code Quality

This project uses `black` for formatting, `ruff` for linting, and `mypy` for type checking.

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type check
mypy src/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/amazing-feature`).
3.  Commit your changes (`git commit -m 'Add amazing feature'`).
4.  Push to the branch (`git push origin feature/amazing-feature`).
5.  Open a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.