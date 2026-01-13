"""Advanced filtering and data manipulation examples for pyine."""

from pyine import INE
from pyine.processors.dataframe import (
    aggregate_by_period,
    filter_by_geography,
    get_latest_period,
)

# Initialize client
ine = INE(language="EN", cache=True)

print("=" * 60)
print("Advanced Filtering Examples")
print("=" * 60)

# Example indicator code
varcd = "0004167"  # Resident population

print("\n" + "=" * 60)
print("Example 1: Multi-dimension filtering")
print("=" * 60)

# Get available dimensions first
dimensions = ine.get_dimensions(varcd)
print(f"\nIndicator {varcd} has {len(dimensions)} dimensions:")
for dim in dimensions:
    print(f"  - Dim{dim.id}: {dim.name} ({len(dim.values)} values)")

# Build a filter using multiple dimensions
if len(dimensions) >= 2:
    dim_filter = {
        f"Dim{dimensions[0].id}": dimensions[0].values[0].code,
        f"Dim{dimensions[1].id}": dimensions[1].values[0].code,
    }

    print(f"\nApplying filter: {dim_filter}")
    df = ine.get_data(varcd, dimensions=dim_filter, format="dataframe")
    print(f"Filtered data shape: {df.shape}")
    print(df.head())

print("\n" + "=" * 60)
print("Example 2: Get latest period data")
print("=" * 60)

# Get all data
df = ine.get_data(varcd, format="dataframe")
print(f"\nTotal data points: {len(df)}")

# Get only latest period
if "periodo" in df.columns:
    latest_df = get_latest_period(df, n=1)
    print(f"Latest period data points: {len(latest_df)}")
    print(latest_df.head())

print("\n" + "=" * 60)
print("Example 3: Geographic filtering")
print("=" * 60)

# Filter by geography
if "geodsg" in df.columns:
    unique_geos = df["geodsg"].unique()
    print(f"\nAvailable geographies: {len(unique_geos)}")
    print("Sample:", unique_geos[:5])

    # Filter for Portugal
    portugal_df = filter_by_geography(df, "Portugal")
    print(f"\nData for Portugal: {len(portugal_df)} rows")
    print(portugal_df.head())

print("\n" + "=" * 60)
print("Example 4: Time series analysis")
print("=" * 60)

# Get data and analyze time series
if "periodo" in df.columns and "valor" in df.columns:
    # Aggregate by period
    period_agg = aggregate_by_period(df, value_col="valor", agg_func="sum")
    print("\nAggregated data by period:")
    print(period_agg.head())

    # Sort by period and show trend
    if len(period_agg) > 1:
        period_agg = period_agg.sort_values("periodo")
        print(f"\nTime series from {period_agg['periodo'].min()} to {period_agg['periodo'].max()}")

print("\n" + "=" * 60)
print("Example 5: Compare multiple indicators")
print("=" * 60)

# Search for related indicators
results = ine.search("population")
if len(results) >= 2:
    print("\nComparing first 2 population indicators:")

    for i, indicator in enumerate(results[:2], 1):
        print(f"\n{i}. {indicator.varcd}: {indicator.title}")
        try:
            ind_df = ine.get_data(indicator.varcd, format="dataframe")
            print(f"   Data points: {len(ind_df)}")
            if "periodo" in ind_df.columns:
                print(f"   Period range: {ind_df['periodo'].min()} - {ind_df['periodo'].max()}")
        except Exception as e:
            print(f"   Error: {str(e)}")

print("\n" + "=" * 60)
print("Example 6: Export with filters")
print("=" * 60)

# Export filtered data to CSV
if dimensions:
    # Filter for specific dimension
    export_filter = {f"Dim{dimensions[0].id}": dimensions[0].values[-1].code}

    output_file = f"{varcd}_filtered.csv"
    ine.export_csv(
        varcd,
        output_file,
        dimensions=export_filter,
        include_metadata=True,
    )
    print(f"\nFiltered data exported to {output_file}")
    print(f"Filter applied: {export_filter}")

print("\n" + "=" * 60)
print("Example 7: Data format comparisons")
print("=" * 60)

# Get same data in different formats
print("\nGetting data in multiple formats:")

# As DataFrame
df_format = ine.get_data(varcd, format="dataframe")
print(f"1. DataFrame: {type(df_format)}, shape: {df_format.shape}")

# As dictionary
dict_format = ine.get_data(varcd, format="dict")
print(f"2. Dictionary: {type(dict_format)}, keys: {list(dict_format.keys())[:5]}")

# As JSON string
json_format = ine.get_data(varcd, format="json")
print(f"3. JSON string: {type(json_format)}, length: {len(json_format)} chars")

print("\n" + "=" * 60)
print("Example 8: Search with filters")
print("=" * 60)

# Get all themes
themes = ine.list_themes()
print(f"\nTotal themes available: {len(themes)}")

# Filter indicators by theme
if themes:
    selected_theme = themes[0]
    print(f"\nIndicators in '{selected_theme}':")

    theme_indicators = ine.filter_by_theme(theme=selected_theme)
    print(f"Total: {len(theme_indicators)}")

    # Show first 5
    for ind in theme_indicators[:5]:
        print(f"  - {ind.varcd}: {ind.title}")

print("\n" + "=" * 60)
print("Example 9: Working with missing data")
print("=" * 60)

# Get data and check for missing values
df = ine.get_data(varcd, format="dataframe")

print("\nDataFrame info:")
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# Check for missing values
print("\nMissing values per column:")
print(df.isnull().sum())

# Remove rows with missing values
if df.isnull().sum().sum() > 0:
    clean_df = df.dropna()
    print(f"\nAfter removing missing values: {clean_df.shape}")

print("\n" + "=" * 60)
print("Example 10: Batch operations")
print("=" * 60)

# Search and export multiple indicators
search_term = "population"
results = ine.search(search_term)

print(f"\nExporting first 3 indicators matching '{search_term}':")
for i, indicator in enumerate(results[:3], 1):
    output_file = f"export_{indicator.varcd}.json"
    try:
        ine.export_json(indicator.varcd, output_file, pretty=True)
        print(f"{i}. Exported {indicator.varcd} to {output_file}")
    except Exception as e:
        print(f"{i}. Failed to export {indicator.varcd}: {str(e)}")

print("\n" + "=" * 60)
print("All advanced examples completed!")
print("=" * 60)
