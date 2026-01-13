"""Basic usage examples for pyine."""

from pyine import INE

# Initialize client with English language
ine = INE(language="EN", cache=True)

print("=" * 60)
print("Example 1: Search for indicators")
print("=" * 60)

# Search for indicators about population
results = ine.search("population")
print(f"\nFound {len(results)} indicators about population:")
for i, indicator in enumerate(results[:5], 1):  # Show first 5
    print(f"{i}. {indicator.varcd}: {indicator.title}")
    if indicator.theme:
        print(f"   Theme: {indicator.theme}")

print("\n" + "=" * 60)
print("Example 2: Get indicator metadata")
print("=" * 60)

# Get metadata for resident population indicator
varcd = "0004167"
metadata = ine.get_metadata(varcd)
print(f"\nIndicator: {metadata.indicator_code}")
print(f"Name: {metadata.indicator_name}")
print(f"Unit: {metadata.unit}")
print(f"Number of dimensions: {len(metadata.dimensions)}")

print("\n" + "=" * 60)
print("Example 3: Explore dimensions")
print("=" * 60)

# Get available dimensions
dimensions = ine.get_dimensions(varcd)
print(f"\nAvailable dimensions for {varcd}:")
for dim in dimensions:
    print(f"\n  Dimension {dim.id}: {dim.name}")
    print(f"  Number of values: {len(dim.values)}")
    # Show first few values
    print("  Sample values:")
    for val in dim.values[:3]:
        print(f"    - {val.code}: {val.label}")

print("\n" + "=" * 60)
print("Example 4: Get data as DataFrame")
print("=" * 60)

# Get all data for the indicator
df = ine.get_data(varcd, format="dataframe")
print(f"\nDataFrame shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print("\nFirst few rows:")
print(df.head())

print("\n" + "=" * 60)
print("Example 5: Filter data by dimensions")
print("=" * 60)

# Get data for specific year and region
# First, let's see what dimension values are available
dims = ine.get_dimensions(varcd)
if dims and dims[0].values:
    # Use the first value from first dimension as example
    dim_filter = {f"Dim{dims[0].id}": dims[0].values[0].code}

    filtered_df = ine.get_data(varcd, dimensions=dim_filter, format="dataframe")
    print(f"\nFiltered data with {dim_filter}:")
    print(f"Shape: {filtered_df.shape}")
    print(filtered_df.head())

print("\n" + "=" * 60)
print("Example 6: Export data to CSV")
print("=" * 60)

# Export to CSV with metadata
output_file = "population_data.csv"
ine.export_csv(varcd, output_file, include_metadata=True)
print(f"\nData exported to {output_file}")

print("\n" + "=" * 60)
print("Example 7: List available themes")
print("=" * 60)

# Get all themes
themes = ine.list_themes()
print(f"\nTotal themes: {len(themes)}")
print("Sample themes:")
for theme in themes[:10]:
    print(f"  - {theme}")

print("\n" + "=" * 60)
print("Example 8: Filter indicators by theme")
print("=" * 60)

# Get indicators for a specific theme
if themes:
    theme_indicators = ine.filter_by_theme(theme=themes[0])
    print(f"\nIndicators in '{themes[0]}' theme: {len(theme_indicators)}")
    for ind in theme_indicators[:3]:  # Show first 3
        print(f"  - {ind.varcd}: {ind.title}")

print("\n" + "=" * 60)
print("Example 9: Cache management")
print("=" * 60)

# Get cache information
cache_info = ine.get_cache_info()
print(f"\nCache enabled: {cache_info['enabled']}")
if cache_info["enabled"]:
    print("Metadata cache:", cache_info.get("metadata_cache", {}))
    print("Data cache:", cache_info.get("data_cache", {}))

print("\n" + "=" * 60)
print("Example 10: Validate indicator")
print("=" * 60)

# Check if indicator exists
valid_code = "0004167"
invalid_code = "9999999"

print(f"\nIs '{valid_code}' valid? {ine.validate_indicator(valid_code)}")
print(f"Is '{invalid_code}' valid? {ine.validate_indicator(invalid_code)}")

print("\n" + "=" * 60)
print("All examples completed!")
print("=" * 60)
