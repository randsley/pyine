"""Advanced filtering and data manipulation examples for the pyptine library."""

from pyptine import INE
from pyptine.processors.dataframe import (
    aggregate_by_period,
    filter_by_geography,
    get_latest_period,
)

# Initialize the client
ine = INE(language="EN")

print("=" * 60)
print("Advanced Filtering and Data Processing Examples")
print("=" * 60)

# --- Example 1: Using an indicator with time series data ---
print("\n" + "=" * 60)
print("Example 1: Working with GDP Time Series Data")
print("=" * 60)
varcd_gdp = "0011776"  # GDP indicator
print(f"Fetching data for indicator {varcd_gdp}...")
response_gdp = ine.get_data(varcd_gdp)
df_gdp = response_gdp.to_dataframe()
print(f"Data shape: {df_gdp.shape}")
print(f"Columns: {list(df_gdp.columns)}")
print("\nFirst 5 rows:")
print(df_gdp.head())

# --- Example 2: Geographic Filtering ---
print("\n" + "=" * 60)
print("Example 2: Filter by Geographic Area")
print("=" * 60)
varcd = "0004167"  # Resident population
response = ine.get_data(varcd, dimensions={"Dim1": "S7A2023"})  # Year 2023
df = response.to_dataframe()

if "geodsg" in df.columns:
    geography_to_filter = "Lisboa"
    print(f"Filtering data for geography containing '{geography_to_filter}'...")
    lisboa_df = filter_by_geography(df, geography_to_filter, geography_column="geodsg")
    print(f"Found {len(lisboa_df)} rows for '{geography_to_filter}'.")
    print(lisboa_df.head())
else:
    print("Skipping: 'geodsg' column not found for geographic filtering.")

# --- Example 3: Exploring Dimensions ---
print("\n" + "=" * 60)
print("Example 3: Explore Indicator Dimensions")
print("=" * 60)
print(f"Getting dimensions for indicator {varcd}...")
dimensions = ine.get_dimensions(varcd)
for dim in dimensions:
    print(f"\nDimension {dim.id}: {dim.name}")
    print(f"  - Total values: {len(dim.values)}")
    print(f"  - Sample values: {[f'{v.code}: {v.label}' for v in dim.values[:3]]}")

# --- Example 4: Filtering with Multiple Dimensions ---
print("\n" + "=" * 60)
print("Example 4: Multi-Dimension Filtering")
print("=" * 60)
print("Fetching data filtered by year, region, and sex...")
filtered_response = ine.get_data(
    varcd,
    dimensions={
        "Dim1": "S7A2023",  # Year 2023
        "Dim2": "PT",  # Portugal
        "Dim3": "T"  # Total (both sexes)
    }
)
filtered_df = filtered_response.to_dataframe()
print(f"Filtered data shape: {filtered_df.shape}")
print(filtered_df)

# --- Example 5: Batch Search and Export ---
print("\n" + "=" * 60)
print("Example 5: Batch Search and Export to JSON")
print("=" * 60)
search_term = "employment rate"
print(f"Searching for indicators matching '{search_term}'...")
results = ine.search(search_term)
print(f"Found {len(results)} indicators. Exporting first 2...")

for i, indicator in enumerate(results[:2], 1):
    output_file = f"advanced_export_{indicator.varcd}.json"
    try:
        print(f"  {i}. Exporting '{indicator.title[:50]}...' ({indicator.varcd})")
        ine.export_json(indicator.varcd, output_file, pretty=False)
        print(f"      -> Saved to {output_file}")
    except Exception as e:
        print(f"      -> Failed: {e}")

# --- Example 6: Working with Multiple Data Formats ---
print("\n" + "=" * 60)
print("Example 6: Data Format Comparison")
print("=" * 60)
print(f"Fetching data for {varcd} in multiple formats...")
response_formats = ine.get_data(varcd, dimensions={"Dim1": "S7A2023"})

# To DataFrame
df_format = response_formats.to_dataframe()
print(f"- As DataFrame: {type(df_format)}, shape: {df_format.shape}")

# To Dictionary
dict_format = response_formats.to_dict()
print(f"- As Dictionary: {type(dict_format)}, keys: {list(dict_format.keys())}")
print(f"  - Data points: {len(dict_format['data'])}")

# Get JSON representation
json_dict = response_formats.model_dump_json(indent=2)
print(f"- As JSON string: {type(json_dict)}, length: {len(json_dict)} chars")

# --- Example 7: Exporting with Metadata ---
print("\n" + "=" * 60)
print("Example 7: Export with Full Metadata")
print("=" * 60)
output_file = "population_with_metadata.csv"
print(f"Exporting data with full metadata to '{output_file}'...")
ine.export_csv(varcd, output_file, include_metadata=True, dimensions={"Dim1": "S7A2023"})
print(f"Successfully exported to '{output_file}'")
print("The CSV file includes metadata as comments at the top.")

# --- Example 8: Compare Multiple Indicators ---
print("\n" + "=" * 60)
print("Example 8: Compare Multiple Indicators")
print("=" * 60)
print("Fetching metadata for multiple related indicators...")
population_indicators = ["0004167", "0007533"]  # Population, Deaths

for ind_code in population_indicators:
    try:
        metadata = ine.get_metadata(ind_code)
        print(f"\n{ind_code}: {metadata.title[:60]}...")
        print(f"  - Unit: {metadata.unit}")
        print(f"  - Periodicity: {metadata.periodicity}")
        print(f"  - Dimensions: {len(metadata.dimensions)}")
    except Exception as e:
        print(f"\n{ind_code}: Error - {e}")

# --- Example 9: Cache Management ---
print("\n" + "=" * 60)
print("Example 9: Cache Management")
print("=" * 60)
cache_info = ine.get_cache_info()
print("Current cache info:")
print(f"  - Enabled: {cache_info['enabled']}")
if cache_info['enabled']:
    print("  - Metadata cache and data cache are active")
    print("  - Metadata cached for 7 days, data for 1 day")
# To clear cache: ine.clear_cache()

# --- Example 10: Theme-based Discovery ---
print("\n" + "=" * 60)
print("Example 10: Theme-based Indicator Discovery")
print("=" * 60)
themes = ine.list_themes()
print(f"Available themes: {len(themes)}")
print("\nSearching within 'Population' theme:")
pop_indicators = ine.search("", theme="Population")
print(f"Found {len(pop_indicators)} indicators in Population theme")
print("Sample indicators:")
for indicator in pop_indicators[:3]:
    print(f"  - {indicator.varcd}: {indicator.title[:50]}...")

print("\n" + "=" * 60)
print("All advanced examples completed!")
print("=" * 60)
