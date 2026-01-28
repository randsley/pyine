"""Analytics and statistical analysis examples for the pyptine library.

This module demonstrates how to use built-in analytical methods for
calculating year-over-year growth, moving averages, and other statistical measures.
"""

from pyptine import INE


def example_1_yoy_growth() -> None:
    """Example 1: Calculate Year-over-Year (YoY) growth."""
    print("=" * 60)
    print("Example 1: Year-over-Year Growth")
    print("=" * 60)

    ine = INE(language="EN")

    # Get GDP data
    print("Fetching GDP data...")
    response = ine.get_data("0004127")

    # Calculate YoY growth
    print("Calculating year-over-year growth...")
    yoy_response = response.calculate_yoy_growth()

    # Convert to DataFrame
    df = yoy_response.to_dataframe()

    # Display results
    print("\nData with YoY growth:")
    print(f"Columns: {list(df.columns)}")
    print("\nFirst 10 rows:")
    print(df[["Period", "value", "yoy_growth"]].head(10))

    # Save to CSV
    output_file = "gdp_yoy_growth.csv"
    df.to_csv(output_file, index=False)
    print(f"\nSaved to {output_file}")


def example_2_mom_change() -> None:
    """Example 2: Calculate Month-over-Month (MoM) change."""
    print("\n" + "=" * 60)
    print("Example 2: Month-over-Month Change")
    print("=" * 60)

    ine = INE(language="EN")

    # Get unemployment data
    print("Fetching unemployment data...")
    response = ine.get_data("0008074")

    # Calculate MoM change
    print("Calculating month-over-month changes...")
    mom_response = response.calculate_mom_change()

    # Convert to DataFrame
    df = mom_response.to_dataframe()

    # Display results
    print("\nData with MoM change:")
    print(f"Columns: {list(df.columns)}")
    print("\nFirst 10 rows:")
    print(df[["Period", "value", "mom_change"]].head(10))

    # Save to CSV
    output_file = "unemployment_mom_change.csv"
    df.to_csv(output_file, index=False)
    print(f"\nSaved to {output_file}")


def example_3_moving_average() -> None:
    """Example 3: Calculate Simple Moving Average (SMA)."""
    print("\n" + "=" * 60)
    print("Example 3: Simple Moving Average")
    print("=" * 60)

    ine = INE(language="EN")

    # Get data
    print("Fetching data...")
    response = ine.get_data("0004127")

    # Calculate 3-period moving average
    print("Calculating 3-period moving average...")
    ma_response = response.calculate_moving_average(window=3)

    # Convert to DataFrame
    df = ma_response.to_dataframe()

    # Display results
    print("\nData with moving average:")
    print(f"Columns: {list(df.columns)}")
    print("\nFirst 10 rows:")
    print(df[["Period", "value", "moving_avg"]].head(10))

    # Save to CSV
    output_file = "gdp_moving_average.csv"
    df.to_csv(output_file, index=False)
    print(f"\nSaved to {output_file}")


def example_4_exponential_moving_average() -> None:
    """Example 4: Calculate Exponential Moving Average (EMA)."""
    print("\n" + "=" * 60)
    print("Example 4: Exponential Moving Average")
    print("=" * 60)

    ine = INE(language="EN")

    # Get data
    print("Fetching data...")
    response = ine.get_data("0004127")

    # Calculate 5-period exponential moving average
    print("Calculating 5-period exponential moving average...")
    ema_response = response.calculate_exponential_moving_average(span=5)

    # Convert to DataFrame
    df = ema_response.to_dataframe()

    # Display results
    print("\nData with exponential moving average:")
    print(f"Columns: {list(df.columns)}")
    print("\nFirst 10 rows:")
    print(df[["Period", "value", "exp_moving_avg"]].head(10))

    # Save to CSV
    output_file = "gdp_ema.csv"
    df.to_csv(output_file, index=False)
    print(f"\nSaved to {output_file}")


def example_5_chained_analysis() -> None:
    """Example 5: Chain multiple analytical methods."""
    print("\n" + "=" * 60)
    print("Example 5: Chained Analysis")
    print("=" * 60)

    ine = INE(language="EN")

    # Get data
    print("Fetching data...")
    response = ine.get_data("0004127")

    # Chain YoY growth and moving average
    print("Calculating YoY growth + 3-period moving average...")
    result = response.calculate_yoy_growth().calculate_moving_average(window=3)

    # Convert to DataFrame
    df = result.to_dataframe()

    # Display results
    print("\nData with chained analysis:")
    print(f"Columns: {list(df.columns)}")
    print("\nFirst 10 rows:")
    print(df[["Period", "value", "yoy_growth", "moving_avg"]].head(10))

    # Save to CSV
    output_file = "gdp_chained_analysis.csv"
    df.to_csv(output_file, index=False)
    print(f"\nSaved to {output_file}")


def example_6_multiple_window_sizes() -> None:
    """Example 6: Compare different moving average window sizes."""
    print("\n" + "=" * 60)
    print("Example 6: Multiple Window Sizes")
    print("=" * 60)

    ine = INE(language="EN")

    # Get data
    print("Fetching data...")
    response = ine.get_data("0004127")

    # Calculate moving averages with different windows
    windows = [3, 5, 10]
    print(f"Calculating moving averages for windows: {windows}")

    results = {}
    for window in windows:
        ma_response = response.calculate_moving_average(window=window)
        df = ma_response.to_dataframe()
        results[window] = df

    # Combine results for comparison
    print("\nComparison of different window sizes:")
    for window, df in results.items():
        print(f"\nWindow {window}:")
        print(df[["Period", "value", "moving_avg"]].head(5))


def example_7_trend_analysis() -> None:
    """Example 7: Analyze trends using YoY and moving averages."""
    print("\n" + "=" * 60)
    print("Example 7: Trend Analysis")
    print("=" * 60)

    ine = INE(language="EN")

    # Get population data
    print("Fetching population data...")
    response = ine.get_data("0004167", dimensions={"Dim2": "PT"})

    # Calculate both YoY and moving average
    print("Performing trend analysis...")
    yoy_result = response.calculate_yoy_growth()
    ma_result = response.calculate_moving_average(window=5)

    # Get DataFrames
    yoy_df = yoy_result.to_dataframe()
    ma_df = ma_result.to_dataframe()

    print("\nYear-over-Year Growth Trends:")
    print(yoy_df[["Period", "value", "yoy_growth"]].tail(10))

    print("\n5-Period Moving Average Trends:")
    print(ma_df[["Period", "value", "moving_avg"]].tail(10))


def example_8_volatility_analysis() -> None:
    """Example 8: Analyze volatility using MoM changes."""
    print("\n" + "=" * 60)
    print("Example 8: Volatility Analysis")
    print("=" * 60)

    ine = INE(language="EN")

    # Get data
    print("Fetching data...")
    response = ine.get_data("0008074")

    # Calculate MoM changes
    print("Calculating month-over-month changes...")
    mom_result = response.calculate_mom_change()
    df = mom_result.to_dataframe()

    # Analyze volatility
    print("\nVolatility Analysis (MoM Changes):")
    print(f"Mean MoM change: {df['mom_change'].mean():.2f}%")
    print(f"Std dev of MoM change: {df['mom_change'].std():.2f}%")
    print(f"Max MoM change: {df['mom_change'].max():.2f}%")
    print(f"Min MoM change: {df['mom_change'].min():.2f}%")

    print("\nRecent MoM changes:")
    print(df[["Period", "value", "mom_change"]].tail(10))


def example_9_smoothing_comparison() -> None:
    """Example 9: Compare simple and exponential moving averages."""
    print("\n" + "=" * 60)
    print("Example 9: Smoothing Comparison (SMA vs EMA)")
    print("=" * 60)

    ine = INE(language="EN")

    # Get data
    print("Fetching data...")
    response = ine.get_data("0004127")

    # Calculate both SMA and EMA
    print("Calculating SMA and EMA with window/span = 5...")
    sma_result = response.calculate_moving_average(window=5)
    ema_result = response.calculate_exponential_moving_average(span=5)

    # Get DataFrames
    sma_df = sma_result.to_dataframe()
    ema_df = ema_result.to_dataframe()

    # Compare
    print("\nComparison of SMA vs EMA:")
    print("Period | Value | SMA | EMA")
    print("-" * 50)

    # Merge data for comparison
    comparison_df = sma_df[["Period", "value", "moving_avg"]].copy()
    comparison_df["exp_moving_avg"] = ema_df["exp_moving_avg"]

    for _, row in comparison_df.tail(10).iterrows():
        print(
            f"{row['Period']} | {row['value']:.2f} | "
            f"{row['moving_avg']:.2f} | {row['exp_moving_avg']:.2f}"
        )


def example_10_comprehensive_analysis() -> None:
    """Example 10: Comprehensive multi-metric analysis."""
    print("\n" + "=" * 60)
    print("Example 10: Comprehensive Analysis")
    print("=" * 60)

    ine = INE(language="EN")

    # Get data
    print("Fetching GDP data...")
    response = ine.get_data("0004127")

    # Perform all analytical calculations
    print("Performing comprehensive analysis...")

    # Chain all methods
    result = (
        response.calculate_yoy_growth()
        .calculate_mom_change()
        .calculate_moving_average(window=3)
        .calculate_exponential_moving_average(span=5)
    )

    # Convert to DataFrame
    df = result.to_dataframe()

    # Display comprehensive results
    print("\nComprehensive Analysis Results:")
    print(f"Columns: {list(df.columns)}")
    print("\nRecent data (last 10 periods):")
    print(
        df[["Period", "value", "yoy_growth", "mom_change", "moving_avg", "exp_moving_avg"]].tail(10)
    )

    # Summary statistics
    print("\nSummary Statistics:")
    print(f"Average YoY growth: {df['yoy_growth'].mean():.2f}%")
    print(f"Average MoM change: {df['mom_change'].mean():.2f}%")
    print(f"Current 3-period MA: {df['moving_avg'].iloc[-1]:.2f}")
    print(f"Current 5-period EMA: {df['exp_moving_avg'].iloc[-1]:.2f}")

    # Save comprehensive analysis
    output_file = "gdp_comprehensive_analysis.csv"
    df.to_csv(output_file, index=False)
    print(f"\nComprehensive analysis saved to {output_file}")


def main() -> None:
    """Run all analytics examples."""
    print("\n" + "=" * 80)
    print("PYPTINE ANALYTICS EXAMPLES")
    print("=" * 80)

    example_1_yoy_growth()
    example_2_mom_change()
    example_3_moving_average()
    example_4_exponential_moving_average()
    example_5_chained_analysis()
    example_6_multiple_window_sizes()
    example_7_trend_analysis()
    example_8_volatility_analysis()
    example_9_smoothing_comparison()
    example_10_comprehensive_analysis()

    print("\n" + "=" * 80)
    print("All analytics examples completed!")
    print("=" * 80)
    print("\nGenerated CSV files contain detailed analytical results.")


if __name__ == "__main__":
    main()
