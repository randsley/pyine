"""Basic usage examples for the pyine library."""

from pyine import INE

# Initialize the client. Caching is enabled by default.
ine = INE(language="EN")

print("=" * 60)
print("Example 1: Search for indicators by keyword")
print("=" * 60)
results = ine.search("gdp")
print(f"Found {len(results)} indicators for 'gdp':")
for indicator in results[:5]:  # Print top 5 results
    print(f"- {indicator.varcd}: {indicator.title} (Theme: {indicator.theme})")

print("\n" + "=" * 60)
print("Example 2: Get detailed metadata for an indicator")
print("=" * 60)
varcd = "0004167"  # Resident population
metadata = ine.get_metadata(varcd)
print(f"Metadata for indicator {metadata.varcd}:")
print(f"- Title: {metadata.title}")
print(f"- Unit: {metadata.unit}")
print(f"- Source: {metadata.source}")
print(f"- Dimensions: {len(metadata.dimensions)}")

print("\n" + "=" * 60)
print("Example 3: Explore indicator dimensions")
print("=" * 60)
dimensions = ine.get_dimensions(varcd)
for dim in dimensions:
    print(f"\nDimension '{dim.name}' (ID: {dim.id}) has {len(dim.values)} values.")
    print("  Sample values:")
    for value in dim.values[:3]:
        print(f"  - Code: {value.code}, Label: {value.label}")

print("\n" + "=" * 60)
print("Example 4: Get data and convert to a pandas DataFrame")
print("=" * 60)
response = ine.get_data(varcd)
df = response.to_dataframe()
print("Data converted to DataFrame:")
print(f"- Shape: {df.shape}")
print(f"- Columns: {list(df.columns)}")
print("First 5 rows:")
print(df.head())

print("\n" + "=" * 60)
print("Example 5: Filter data using dimensions")
print("=" * 60)
# Use a dimension code from the metadata explored in Example 3
# For indicator 0004167, Dim1 is 'Period' and Dim2 is 'Geographic localization'
dimension_filter = {"Dim1": "2023", "Dim2": "1"}  # Year 2023, Region 'Portugal'
print(f"Fetching data with filter: {dimension_filter}...")
filtered_response = ine.get_data(varcd, dimensions=dimension_filter)
filtered_df = filtered_response.to_dataframe()
print("Filtered DataFrame:")
print(f"- Shape: {filtered_df.shape}")
print(filtered_df.head())

print("\n" + "=" * 60)
print("Example 6: Export data directly to a CSV file")
print("=" * 60)
output_csv_file = "population_data.csv"
print(f"Exporting data for {varcd} to '{output_csv_file}'...")
ine.export_csv(varcd, output_csv_file, include_metadata=True)
print(f"Successfully exported to '{output_csv_file}'.")

print("\n" + "=" * 60)
print("Example 7: List all available themes")
print("=" * 60)
themes = ine.list_themes()
print(f"Found {len(themes)} themes. First 10:")
for theme in themes[:10]:
    print(f"- {theme}")

print("\n" + "=" * 60)
print("Example 8: Search for indicators within a specific theme")
print("=" * 60)
theme_to_search = "Labour market"
print(f"Searching for indicators in theme '{theme_to_search}'...")
theme_indicators = ine.search(query="", theme=theme_to_search)
print(f"Found {len(theme_indicators)} indicators in the '{theme_to_search}' theme.")
for indicator in theme_indicators[:3]:
    print(f"- {indicator.varcd}: {indicator.title}")

print("\n" + "=" * 60)
print("Example 9: Manage the cache")
print("=" * 60)
cache_info = ine.get_cache_info()
print("Current cache info:")
print(cache_info)
# To clear the cache, you would run:
# ine.clear_cache()
# print("\nCache cleared.")

print("\n" + "=" * 60)
print("Example 10: Validate an indicator code")
print("=" * 60)
valid_code = "0004167"
invalid_code = "9999999"
print(f"Is '{valid_code}' a valid indicator code? {ine.validate_indicator(valid_code)}")
print(f"Is '{invalid_code}' a valid indicator code? {ine.validate_indicator(invalid_code)}")

print("\n" + "=" * 60)
print("All examples completed!")
print("=" * 60)