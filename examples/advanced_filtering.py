"""Advanced filtering and data manipulation examples for the pyine library."""

from pyine import INE
from pyine.processors.dataframe import (
    aggregate_by_period,
    filter_by_geography,
    get_latest_period,
)

# Initialize the client
ine = INE(language="EN")
indicator_code = "0004167"  # Resident population

print("=" * 60)
print("Advanced Filtering and Data Processing Examples")
print("=" * 60)

print(f"Using indicator: {indicator_code} (Resident population)")

# --- 1. Get base data for processing ---
print("\nFetching base data for examples...")
response = ine.get_data(indicator_code)
df = response.to_dataframe()
print(f"Base DataFrame shape: {df.shape}")

# --- 2. Get data for the latest period ---
print("\n" + "=" * 60)
print("Example 1: Get Data for the Latest Period")
print("=" * 60)
if "periodo" in df.columns:
    latest_df = get_latest_period(df, n=1)
    latest_period = latest_df["periodo"].iloc[0]
    print(f"Successfully filtered for the latest period: {latest_period}")
    print(f"DataFrame shape: {latest_df.shape}")
    print(latest_df.head())
else:
    print("Skipping: 'periodo' column not found.")

# --- 3. Geographic Filtering ---
print("\n" + "=" * 60)
print("Example 2: Filter by Geographic Area")
print("=" * 60)
if "geodsg" in df.columns:
    geography_to_filter = "Portugal"
    print(f"Filtering data for geography: '{geography_to_filter}'...")
    portugal_df = filter_by_geography(df, geography_to_filter)
    print(f"Found {len(portugal_df)} rows for '{geography_to_filter}'.")
    print(portugal_df.head())
else:
    print("Skipping: 'geodsg' column not found for geographic filtering.")

# --- 4. Time Series Aggregation ---
print("\n" + "=" * 60)
print("Example 3: Aggregate Data by Time Period")
print("=" * 60)
if "periodo" in df.columns and "valor" in df.columns:
    print("Aggregating total 'valor' by 'periodo'...")
    # Use a subset of columns for clarity
    subset_df = df[["periodo", "valor"]]
    period_agg = aggregate_by_period(subset_df, value_column="valor", agg_func="sum")
    period_agg = period_agg.sort_values("periodo", ascending=False)
    print("Aggregated data (latest 5 periods):")
    print(period_agg.head())
else:
    print("Skipping: 'periodo' or 'valor' column not found.")

# --- 5. Batch Exporting ---
print("\n" + "=" * 60)
print("Example 4: Batch Search and Export")
print("=" * 60)
search_term = "gdp"
print(f"Searching for indicators matching '{search_term}' and exporting first 2...")
results = ine.search(search_term)
for i, indicator in enumerate(results[:2], 1):
    output_file = f"advanced_export_{indicator.varcd}.json"
    try:
        print(f"  {i}. Exporting '{indicator.title}' ({indicator.varcd}) to {output_file}")
        ine.export_json(indicator.varcd, output_file, pretty=False)
    except Exception as e:
        print(f"  - Failed to export {indicator.varcd}: {e}")

# --- 6. Working with Multiple Data Formats ---
print("\n" + "=" * 60)
print("Example 5: Comparing Data Formats")
print("=" * 60)
print(f"Fetching data for {indicator_code} in multiple formats...")
response = ine.get_data(indicator_code, dimensions={"Dim1": "2023"})

# To DataFrame
df_format = response.to_dataframe()
print(f"- As DataFrame: {type(df_format)}, shape: {df_format.shape}")

# To Dictionary
dict_format = response.to_dict()
print(f"- As Dictionary: {type(dict_format)}, keys: {list(dict_format.keys())}")

# To JSON String
json_format = response.to_json()
print(f"- As JSON String: {type(json_format)}, length: {len(json_format)} chars")


print("\n" + "=" * 60)
print("All advanced examples completed!")
print("=" * 60)