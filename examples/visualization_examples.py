"""Visualization examples for the pyptine library.

This module demonstrates how to create interactive charts and visualizations
using plotly directly from DataResponse objects.
"""

from pyptine import INE


def example_1_basic_line_chart():
    """Example 1: Create a basic line chart."""
    print("=" * 60)
    print("Example 1: Basic Line Chart")
    print("=" * 60)

    ine = INE(language="EN")

    # Get GDP data
    print("Fetching GDP data...")
    response = ine.get_data("0004127")

    # Create line chart
    print("Creating line chart...")
    fig = response.plot_line()

    # Show in browser (comment out if running headless)
    fig.show()

    # Save to HTML file
    output_file = "gdp_line_chart.html"
    fig.write_html(output_file)
    print(f"Chart saved to {output_file}")


def example_2_line_chart_with_markers():
    """Example 2: Line chart with markers."""
    print("\n" + "=" * 60)
    print("Example 2: Line Chart with Markers")
    print("=" * 60)

    ine = INE(language="EN")

    # Get population data
    print("Fetching population data...")
    response = ine.get_data("0004167", dimensions={"Dim1": "S7A2023"})

    # Create line chart with markers
    print("Creating line chart with markers...")
    fig = response.plot_line(markers=True)

    # Customize the layout
    fig.update_layout(
        title="Population Data 2023",
        xaxis_title="Region",
        yaxis_title="Population",
        height=600,
        width=1000,
    )

    # Save to file
    output_file = "population_line_markers.html"
    fig.write_html(output_file)
    print(f"Chart saved to {output_file}")


def example_3_bar_chart():
    """Example 3: Create a bar chart."""
    print("\n" + "=" * 60)
    print("Example 3: Bar Chart")
    print("=" * 60)

    ine = INE(language="EN")

    # Get unemployment data
    print("Fetching unemployment data...")
    response = ine.get_data("0008074")

    # Create bar chart
    print("Creating bar chart...")
    fig = response.plot_bar()

    # Customize
    fig.update_layout(
        title="Unemployment Rate",
        xaxis_title="Period",
        yaxis_title="Rate (%)",
    )

    # Save to file
    output_file = "unemployment_bar_chart.html"
    fig.write_html(output_file)
    print(f"Chart saved to {output_file}")


def example_4_area_chart():
    """Example 4: Create an area chart."""
    print("\n" + "=" * 60)
    print("Example 4: Area Chart")
    print("=" * 60)

    ine = INE(language="EN")

    # Get GDP data
    print("Fetching GDP data...")
    response = ine.get_data("0004127")

    # Create area chart
    print("Creating area chart...")
    fig = response.plot_area()

    # Customize
    fig.update_layout(
        title="GDP Over Time (Area Chart)",
        xaxis_title="Period",
        yaxis_title="GDP Value",
        hovermode="x unified",
    )

    # Save to file
    output_file = "gdp_area_chart.html"
    fig.write_html(output_file)
    print(f"Chart saved to {output_file}")


def example_5_scatter_plot():
    """Example 5: Create a scatter plot."""
    print("\n" + "=" * 60)
    print("Example 5: Scatter Plot")
    print("=" * 60)

    ine = INE(language="EN")

    # Get data
    print("Fetching data...")
    response = ine.get_data("0004167", dimensions={"Dim1": "S7A2023"})

    # Create scatter plot
    print("Creating scatter plot...")
    fig = response.plot_scatter()

    # Customize
    fig.update_layout(
        title="Population Scatter Plot",
        xaxis_title="Data Point Index",
        yaxis_title="Population Value",
    )

    # Save to file
    output_file = "population_scatter.html"
    fig.write_html(output_file)
    print(f"Chart saved to {output_file}")


def example_6_generic_plot():
    """Example 6: Use generic plot method with chart type parameter."""
    print("\n" + "=" * 60)
    print("Example 6: Generic Plot Method")
    print("=" * 60)

    ine = INE(language="EN")

    # Get data
    print("Fetching data...")
    response = ine.get_data("0004127")

    # Create different chart types using generic plot method
    chart_types = ["line", "bar", "area", "scatter"]

    for chart_type in chart_types:
        print(f"Creating {chart_type} chart...")
        fig = response.plot(chart_type=chart_type)

        # Save each chart
        output_file = f"gdp_{chart_type}_chart.html"
        fig.write_html(output_file)
        print(f"  Saved to {output_file}")


def example_7_custom_columns():
    """Example 7: Specify custom columns for x and y axes."""
    print("\n" + "=" * 60)
    print("Example 7: Custom Column Selection")
    print("=" * 60)

    ine = INE(language="EN")

    # Get data
    print("Fetching data...")
    response = ine.get_data("0004127")
    df = response.to_dataframe()

    print(f"Available columns: {list(df.columns)}")

    # Create chart with specific columns
    print("Creating chart with custom columns...")
    fig = response.plot_line(x_column="Period", y_column="value")

    # Save to file
    output_file = "custom_columns_chart.html"
    fig.write_html(output_file)
    print(f"Chart saved to {output_file}")


def example_8_multiple_indicators():
    """Example 8: Compare multiple indicators on separate charts."""
    print("\n" + "=" * 60)
    print("Example 8: Multiple Indicators")
    print("=" * 60)

    ine = INE(language="EN")

    # Define indicators to compare
    indicators = {
        "0004127": "GDP",
        "0008074": "Unemployment Rate",
        "0007533": "Deaths",
    }

    print(f"Creating charts for {len(indicators)} indicators...")

    for varcd, name in indicators.items():
        print(f"  Processing {name} ({varcd})...")

        # Fetch data
        response = ine.get_data(varcd)

        # Create line chart
        fig = response.plot_line()

        # Customize
        fig.update_layout(title=f"{name} - Time Series")

        # Save
        output_file = f"indicator_{varcd}_{name.replace(' ', '_').lower()}.html"
        fig.write_html(output_file)
        print(f"    Saved to {output_file}")


def example_9_advanced_customization():
    """Example 9: Advanced chart customization."""
    print("\n" + "=" * 60)
    print("Example 9: Advanced Customization")
    print("=" * 60)

    ine = INE(language="EN")

    # Get data
    print("Fetching data...")
    response = ine.get_data("0004127")

    # Create line chart
    print("Creating highly customized chart...")
    fig = response.plot_line(markers=True)

    # Advanced customization
    fig.update_layout(
        title={
            "text": "GDP Analysis - Portugal",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 24, "color": "#2c3e50"},
        },
        xaxis={
            "title": "Time Period",
            "showgrid": True,
            "gridcolor": "#ecf0f1",
            "linecolor": "#34495e",
        },
        yaxis={
            "title": "GDP Value",
            "showgrid": True,
            "gridcolor": "#ecf0f1",
            "linecolor": "#34495e",
        },
        plot_bgcolor="#ffffff",
        paper_bgcolor="#f8f9fa",
        hovermode="x unified",
        height=700,
        width=1200,
        font={"family": "Arial, sans-serif", "size": 12},
    )

    # Update trace styling
    fig.update_traces(
        line={"width": 3, "color": "#3498db"},
        marker={"size": 8, "color": "#e74c3c", "line": {"width": 2, "color": "#c0392b"}},
    )

    # Save to file
    output_file = "gdp_advanced_customization.html"
    fig.write_html(output_file)
    print(f"Chart saved to {output_file}")


def example_10_export_formats():
    """Example 10: Export charts to different formats."""
    print("\n" + "=" * 60)
    print("Example 10: Export to Multiple Formats")
    print("=" * 60)

    ine = INE(language="EN")

    # Get data
    print("Fetching data...")
    response = ine.get_data("0004127")

    # Create chart
    print("Creating chart...")
    fig = response.plot_line()

    # Export to HTML (interactive)
    html_file = "chart_export.html"
    fig.write_html(html_file)
    print(f"Saved HTML (interactive): {html_file}")

    # Note: PNG, SVG, PDF export requires kaleido package
    # Uncomment if you have kaleido installed:
    # fig.write_image("chart_export.png", width=1200, height=600)
    # print("Saved PNG: chart_export.png")
    #
    # fig.write_image("chart_export.svg", width=1200, height=600)
    # print("Saved SVG: chart_export.svg")
    #
    # fig.write_image("chart_export.pdf", width=1200, height=600)
    # print("Saved PDF: chart_export.pdf")

    print("\nNote: Install 'kaleido' package to export to PNG, SVG, PDF:")
    print("  pip install kaleido")


def main():
    """Run all visualization examples."""
    print("\n" + "=" * 80)
    print("PYPTINE VISUALIZATION EXAMPLES")
    print("=" * 80)

    example_1_basic_line_chart()
    example_2_line_chart_with_markers()
    example_3_bar_chart()
    example_4_area_chart()
    example_5_scatter_plot()
    example_6_generic_plot()
    example_7_custom_columns()
    example_8_multiple_indicators()
    example_9_advanced_customization()
    example_10_export_formats()

    print("\n" + "=" * 80)
    print("All visualization examples completed!")
    print("=" * 80)
    print("\nGenerated files can be opened in your web browser to view interactive charts.")


if __name__ == "__main__":
    main()
