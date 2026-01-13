"""Command-line interface for pyine."""

import sys
from pathlib import Path
from typing import Optional

import click
from click import Context

from pyine import INE
from pyine.__version__ import __version__


@click.group()
@click.version_option(version=__version__, prog_name="pyine")
@click.pass_context
def cli(ctx: Context) -> None:  # type: ignore[misc]
    """pyine - Python client for INE Portugal (Statistics Portugal) API.

    Access Portuguese statistical data from the command line.

    \b
    Examples:
        pyine search "population"
        pyine info 0004167
        pyine download 0004167 --output data.csv
        pyine list themes
    """
    # Ensure context object exists
    ctx.ensure_object(dict)


@cli.command()
@click.argument("query")
@click.option(
    "--theme",
    "-t",
    help="Filter by theme",
)
@click.option(
    "--lang",
    "-l",
    default="EN",
    type=click.Choice(["EN", "PT"], case_sensitive=False),
    help="Language (EN or PT)",
)
@click.option(
    "--limit",
    "-n",
    type=int,
    help="Maximum number of results to display",
)
def search(query: str, theme: Optional[str], lang: str, limit: Optional[int]) -> None:
    """Search for indicators by keyword.

    \b
    Examples:
        pyine search "gdp"
        pyine search "population" --theme "Population"
        pyine search "employment" --lang PT --limit 10
    """
    try:
        ine = INE(language=lang, cache=True)

        # Search
        if theme:
            results = ine.filter_by_theme(theme=theme)
            # Further filter by query within theme results
            results = [
                ind
                for ind in results
                if query.lower() in ind.title.lower()
                or query.lower() in (ind.description or "").lower()
            ]
        else:
            results = ine.search(query)

        if not results:
            click.echo(f"No indicators found for '{query}'", err=True)
            sys.exit(1)

        # Apply limit if specified
        if limit:
            results = results[:limit]

        # Display results
        click.echo(f"\nFound {len(results)} indicator(s):\n")
        for ind in results:
            click.echo(f"  {click.style(ind.varcd, fg='cyan', bold=True)}: {ind.title}")
            if ind.theme:
                click.echo(f"    Theme: {ind.theme}")
            if ind.description:
                # Truncate long descriptions
                desc = (
                    ind.description[:100] + "..." if len(ind.description) > 100 else ind.description
                )
                click.echo(f"    {desc}")
            click.echo()

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("varcd")
@click.option(
    "--lang",
    "-l",
    default="EN",
    type=click.Choice(["EN", "PT"], case_sensitive=False),
    help="Language (EN or PT)",
)
def info(varcd: str, lang: str) -> None:
    """Get detailed information about an indicator.

    \b
    Examples:
        pyine info 0004167
        pyine info 0004167 --lang PT
    """
    try:
        ine = INE(language=lang, cache=True)

        # Get indicator info
        indicator = ine.get_indicator(varcd)
        metadata = ine.get_metadata(varcd)

        # Display info
        click.echo(f"\n{click.style('Indicator Information', bold=True)}")
        click.echo(f"Code: {click.style(indicator.varcd, fg='cyan')}")
        click.echo(f"Title: {indicator.title}")

        if indicator.description:
            click.echo(f"Description: {indicator.description}")

        if indicator.theme:
            click.echo(f"Theme: {indicator.theme}")

        if indicator.subtheme:
            click.echo(f"Subtheme: {indicator.subtheme}")

        if indicator.periodicity:
            click.echo(f"Periodicity: {indicator.periodicity}")

        if indicator.last_period:
            click.echo(f"Last Period: {indicator.last_period}")

        if metadata.unit:
            click.echo(f"Unit: {metadata.unit}")

        # Display dimensions
        if metadata.dimensions:
            click.echo(f"\n{click.style('Dimensions:', bold=True)}")
            for dim in metadata.dimensions:
                click.echo(f"  - {dim.name} ({len(dim.values)} values)")

        click.echo()

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("varcd")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path (default: <varcd>.<format>)",
)
@click.option(
    "--output-format",
    "-f",
    type=click.Choice(["csv", "json"], case_sensitive=False),
    default="csv",
    help="Output format (csv or json)",
)
@click.option(
    "--lang",
    "-l",
    default="EN",
    type=click.Choice(["EN", "PT"], case_sensitive=False),
    help="Language (EN or PT)",
)
@click.option(
    "--no-metadata",
    is_flag=True,
    help="Don't include metadata in output",
)
@click.option(
    "--dimension",
    "-d",
    multiple=True,
    help="Filter by dimension (format: Dim1=value)",
)
def download(
    varcd: str,
    output: Optional[str],
    output_format: str,
    lang: str,
    no_metadata: bool,
    dimension: tuple,
) -> None:
    """Download indicator data to file.

    \b
    Examples:
        pyine download 0004167
        pyine download 0004167 --output data.csv
        pyine download 0004167 --format json
        pyine download 0004167 --dimension "Dim1=2020"
    """
    try:
        ine = INE(language=lang, cache=True)

        # Parse dimensions
        dimensions = None
        if dimension:
            dimensions = {}
            for dim in dimension:
                if "=" not in dim:
                    click.echo(f"Invalid dimension format: {dim}. Use 'DimN=value'", err=True)
                    sys.exit(1)
                key, value = dim.split("=", 1)
                dimensions[key] = value

        # Default output filename
        if not output:
            output = varcd + "." + output_format

        output_path = Path(output)

        # Download data
        click.echo(f"Downloading indicator {varcd}...")

        if output_format.lower() == "csv":
            ine.export_csv(
                varcd,
                output_path,
                dimensions=dimensions,
                include_metadata=not no_metadata,
            )
        else:  # json
            ine.export_json(
                varcd,
                output_path,
                dimensions=dimensions,
                pretty=True,
            )

        click.echo(f"✓ Data saved to {click.style(str(output_path), fg='green')}")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("varcd")
@click.option(
    "--lang",
    "-l",
    default="EN",
    type=click.Choice(["EN", "PT"], case_sensitive=False),
    help="Language (EN or PT)",
)
def dimensions(varcd: str, lang: str) -> None:
    """List available dimensions for an indicator.

    \b
    Examples:
        pyine dimensions 0004167
        pyine dimensions 0004167 --lang PT
    """
    try:
        ine = INE(language=lang, cache=True)

        # Get dimensions
        dims = ine.get_dimensions(varcd)

        if not dims:
            click.echo(f"No dimensions found for indicator {varcd}", err=True)
            sys.exit(1)

        # Display dimensions
        click.echo(f"\n{click.style('Available Dimensions', bold=True)} for {varcd}:\n")

        for dim in dims:
            click.echo(f"  {click.style(f'Dim{dim.id}', fg='cyan')}: {dim.name}")
            click.echo(f"    Values ({len(dim.values)}):")

            # Show first 10 values
            for _i, val in enumerate(dim.values[:10]):
                click.echo(f"      - {val.code}: {val.label}")

            if len(dim.values) > 10:
                click.echo(f"      ... and {len(dim.values) - 10} more")

            click.echo()

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.group()
def list_commands() -> None:
    """List themes and indicators.

    \b
    Examples:
        pyine list themes
        pyine list indicators
        pyine list indicators --theme "Population"
    """
    pass


@list_commands.command(name="themes")
@click.option(
    "--lang",
    "-l",
    default="EN",
    type=click.Choice(["EN", "PT"], case_sensitive=False),
    help="Language (EN or PT)",
)
def list_themes(lang: str) -> None:
    """List all available themes."""
    try:
        ine = INE(language=lang, cache=True)

        themes = ine.list_themes()

        if not themes:
            click.echo("No themes found", err=True)
            sys.exit(1)

        click.echo(f"\n{click.style('Available Themes', bold=True)} ({len(themes)}):\n")

        for theme in themes:
            click.echo(f"  • {theme}")

        click.echo()

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@list_commands.command(name="indicators")
@click.option(
    "--theme",
    "-t",
    help="Filter by theme",
)
@click.option(
    "--lang",
    "-l",
    default="EN",
    type=click.Choice(["EN", "PT"], case_sensitive=False),
    help="Language (EN or PT)",
)
@click.option(
    "--limit",
    "-n",
    type=int,
    default=20,
    help="Maximum number of indicators to display",
)
def list_indicators(theme: Optional[str], lang: str, limit: int) -> None:
    """List available indicators."""
    try:
        ine = INE(language=lang, cache=True)

        # Get indicators
        indicators = ine.filter_by_theme(theme=theme) if theme else ine.browser.get_all_indicators()

        if not indicators:
            if theme:
                click.echo(f"No indicators found for theme '{theme}'", err=True)
            else:
                click.echo("No indicators found", err=True)
            sys.exit(1)

        # Apply limit
        total = len(indicators)
        indicators = indicators[:limit]

        # Display
        click.echo(f"\n{click.style('Indicators', bold=True)} ({len(indicators)} of {total}):\n")

        for ind in indicators:
            click.echo(f"  {click.style(ind.varcd, fg='cyan')}: {ind.title}")
            if ind.theme:
                click.echo(f"    Theme: {ind.theme}")
            click.echo()

        if total > limit:
            click.echo(f"... and {total - limit} more. Use --limit to see more.")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.group()
def cache() -> None:
    """Manage cache.

    \b
    Examples:
        pyine cache info
        pyine cache clear
    """
    pass


@cache.command(name="info")
def cache_info() -> None:
    """Show cache statistics."""
    try:
        ine = INE(cache=True)

        info = ine.get_cache_info()

        if not info["enabled"]:
            click.echo("Cache is disabled")
            return

        click.echo(f"\n{click.style('Cache Information', bold=True)}\n")

        # Metadata cache
        if "metadata_cache" in info:
            meta_info = info["metadata_cache"]
            click.echo(f"{click.style('Metadata Cache:', fg='cyan')}")
            click.echo(f"  Size: {meta_info.get('size', 0)} entries")
            if "path" in meta_info:
                click.echo(f"  Location: {meta_info['path']}")

        # Data cache
        if "data_cache" in info:
            data_info = info["data_cache"]
            click.echo(f"\n{click.style('Data Cache:', fg='cyan')}")
            click.echo(f"  Size: {data_info.get('size', 0)} entries")
            if "path" in data_info:
                click.echo(f"  Location: {data_info['path']}")

        click.echo()

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cache.command(name="clear")
@click.confirmation_option(prompt="Are you sure you want to clear the cache?")
def cache_clear() -> None:
    """Clear all cached data."""
    try:
        ine = INE(cache=True)
        ine.clear_cache()

        click.echo(f"{click.style('✓', fg='green')} Cache cleared successfully")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
