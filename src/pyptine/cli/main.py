"""Command-line interface for pyptine."""

import sys
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

import click
from click import Context
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

from pyptine import INE
from pyptine.__version__ import __version__
from pyptine.cli.utils import (
    console,
    create_dimensions_table,
    create_indicators_table,
    create_themes_table,
    format_indicator_info,
    handle_cli_error,
    print_error,
    print_info,
    print_success,
    spinner_task,
)
from pyptine.utils.exceptions import INEError


def handle_exceptions(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to handle common exceptions for CLI commands."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        try:
            func(*args, **kwargs)
        except INEError as e:
            handle_cli_error(e, verbose=False)
        except Exception as e:
            # Catch any other unexpected exceptions
            handle_cli_error(e, verbose=False)

    return wrapper


@click.group(help="""pyptine - Python client for INE Portugal (Statistics Portugal) API.""")
@click.version_option(version=__version__, prog_name="pyptine")
@click.pass_context
def cli(ctx: Context) -> None:  # type: ignore[misc]
    """pyptine - Python client for INE Portugal (Statistics Portugal) API.

    Access Portuguese statistical data from the command line.

    \b
    Examples:
        pyptine search "population"
        pyptine info 0004167
        pyptine download 0004167 --output data.csv
        pyptine list-commands themes
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
    "--subtheme",
    "-s",
    help="Filter by subtheme",
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
@click.option(
    "--timeout",
    "-w",
    type=int,
    default=10,
    help="Request timeout in seconds (default: 10)",
)
@handle_exceptions
def search(
    query: str,
    theme: Optional[str],
    subtheme: Optional[str],
    lang: str,
    limit: Optional[int],
    timeout: int,
) -> None:
    """Search for indicators by keyword.

    \b
    Examples:
        pyptine search "gdp"
        pyptine search "population" --theme "Population"
        pyptine search "employment" --lang PT --limit 10
        pyptine search "gdp" --timeout 20
    """
    ine = INE(language=lang, cache=True, timeout=timeout)

    # Check if catalogue is cached
    is_cached = ine.browser.is_catalogue_cached()

    # Search with context-aware progress
    if is_cached:
        # Fast path: catalogue is already cached
        with spinner_task("Searching indicators...") as progress:
            task_id = progress.add_task("[cyan]Searching...", total=None)
            results = ine.search(query, theme=theme, subtheme=subtheme)
            progress.update(task_id, completed=True)
    else:
        # Slow path: need to download catalogue with progress bar
        from rich.progress import DownloadColumn, Progress, TransferSpeedColumn

        print_info(
            "First Run",
            "Downloading indicator catalogue (this only happens once, subsequent searches will be fast)",
        )

        # Use spinner progress for indeterminate download (no Content-Length from API)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            DownloadColumn(),
            TransferSpeedColumn(),
            console=console,
            refresh_per_second=10,
        ) as progress:
            download_task = progress.add_task("[cyan]Downloading catalogue...", total=None)

            def progress_callback(downloaded: int, total: int) -> None:
                progress.update(download_task, completed=downloaded)

            results = ine.search(
                query, theme=theme, subtheme=subtheme, progress_callback=progress_callback
            )

    if not results:
        print_error("No Results", f"No indicators found for '{query}'")
        sys.exit(1)

    total_found = len(results)

    # Apply limit if specified
    if limit:
        results = results[:limit]

    # Display results in a table
    table = create_indicators_table(results, limit=len(results))
    console.print(table)

    # Summary
    if total_found > len(results):
        print_info(
            "Results", f"Showing {len(results)} of {total_found} results. Use --limit to see more."
        )


@cli.command()
@click.argument("varcd")
@click.option(
    "--lang",
    "-l",
    default="EN",
    type=click.Choice(["EN", "PT"], case_sensitive=False),
    help="Language (EN or PT)",
)
@handle_exceptions
def info(varcd: str, lang: str) -> None:
    """Get detailed information about an indicator.

    \b
    Examples:
        pyptine info 0004167
        pyptine info 0004167 --lang PT
    """
    ine = INE(language=lang, cache=True)

    # Get indicator info with spinner
    with spinner_task("Fetching indicator information...") as progress:
        task_id = progress.add_task("[cyan]Fetching...", total=None)
        indicator = ine.get_indicator(varcd)
        metadata = ine.get_metadata(varcd)
        progress.update(task_id, completed=True)

    # Display info in panel
    info_text = format_indicator_info(indicator, metadata)
    print_info("Indicator Information", "")
    console.print(info_text)

    # Display dimensions if available
    if metadata.dimensions:
        console.print()
        table = create_dimensions_table(metadata.dimensions)
        console.print(table)


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
@handle_exceptions
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
        pyptine download 0004167
        pyptine download 0004167 --output data.csv
        pyptine download 0004167 --format json
        pyptine download 0004167 --dimension "Dim1=2020"
    """
    ine = INE(language=lang, cache=True)

    # Parse dimensions
    dimensions = None
    if dimension:
        dimensions = {}
        for dim in dimension:
            if "=" not in dim:
                print_error(
                    "Invalid Format", f"Dimension format should be 'DimN=value', got '{dim}'"
                )
                sys.exit(1)
            key, value = dim.split("=", 1)
            dimensions[key] = value

    # Default output filename
    if not output:
        output = varcd + "." + output_format

    output_path = Path(output)

    # Download data with progress bar
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
        TextColumn("•"),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        task_id = progress.add_task(f"[cyan]Downloading {varcd}...", total=None)
        response = ine.get_data(varcd, dimensions=dimensions)
        progress.update(task_id, total=1, completed=1)

        task_id = progress.add_task(f"[cyan]Saving to {output_format.upper()}...", total=None)
        if output_format.lower() == "csv":
            response.to_csv(
                output_path,
                include_metadata=not no_metadata,
            )
        else:  # json
            response.to_json(
                output_path,
                pretty=True,
            )
        progress.update(task_id, total=1, completed=1)

    # Success message
    file_size = output_path.stat().st_size / 1024  # Convert to KB
    print_success("Download Complete", f"Data saved to {output_path} ({file_size:.1f} KB)")


@cli.command()
@click.argument("varcd")
@click.option(
    "--lang",
    "-l",
    default="EN",
    type=click.Choice(["EN", "PT"], case_sensitive=False),
    help="Language (EN or PT)",
)
@handle_exceptions
def dimensions(varcd: str, lang: str) -> None:
    """List available dimensions for an indicator.

    \b
    Examples:
        pyptine dimensions 0004167
        pyptine dimensions 0004167 --lang PT
    """
    ine = INE(language=lang, cache=True)

    # Get dimensions with spinner
    with spinner_task("Fetching dimensions...") as progress:
        task_id = progress.add_task("[cyan]Fetching...", total=None)
        dims = ine.get_dimensions(varcd)
        progress.update(task_id, completed=True)

    if not dims:
        print_error("No Dimensions", f"No dimensions found for indicator {varcd}")
        sys.exit(1)

    # Display dimensions table
    table = create_dimensions_table(dims)
    console.print(table)

    # Display dimension values
    for dim in dims:
        console.print(
            f"\n[bold cyan]Dim{dim.id}: {dim.name}[/bold cyan] ({len(dim.values)} values)"
        )

        # Show all values (or first 20 if too many)
        values_to_show = dim.values[:20]
        for val in values_to_show:
            console.print(f"  [cyan]{val.code}[/cyan] → {val.label}")

        if len(dim.values) > 20:
            console.print(f"  [dim]... and {len(dim.values) - 20} more values[/dim]")


@cli.group()
def list_commands() -> None:
    """List themes and indicators.

    \b
    Examples:
        pyptine list-commands themes
        pyptine list-commands indicators
        pyptine list-commands indicators --theme "Population"
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
@handle_exceptions
def list_themes(lang: str) -> None:
    """List all available themes."""
    ine = INE(language=lang, cache=True)

    # Check if catalogue is cached
    is_cached = ine.browser.is_catalogue_cached()

    # Fetch themes with context-aware progress
    if is_cached:
        # Fast path: catalogue is already cached
        with spinner_task("Fetching themes...") as progress:
            task_id = progress.add_task("[cyan]Fetching...", total=None)
            themes = ine.list_themes()
            progress.update(task_id, completed=True)
    else:
        # Slow path: need to download catalogue with progress bar
        print_info(
            "First Run",
            "Downloading indicator catalogue (this only happens once, subsequent requests will be fast)",
        )

        # Use spinner progress for indeterminate download (no Content-Length from API)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            DownloadColumn(),
            TransferSpeedColumn(),
            console=console,
            refresh_per_second=10,
        ) as progress:
            download_task = progress.add_task("[cyan]Downloading catalogue...", total=None)

            def progress_callback(downloaded: int, total: int) -> None:
                progress.update(download_task, completed=downloaded)

            themes = ine.list_themes(progress_callback=progress_callback)

    if not themes:
        print_error("No Themes", "No themes found in the catalogue")
        sys.exit(1)

    # Display themes in table
    table = create_themes_table(themes)
    console.print(table)


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
@handle_exceptions
def list_indicators(theme: Optional[str], lang: str, limit: int) -> None:
    """List available indicators."""
    ine = INE(language=lang, cache=True)

    # Check if catalogue is cached
    is_cached = ine.browser.is_catalogue_cached()

    # Get indicators with context-aware progress
    if is_cached:
        # Fast path: catalogue is already cached
        with spinner_task("Fetching indicators...") as progress:
            task_id = progress.add_task("[cyan]Fetching...", total=None)
            indicators = ine.search(query="", theme=theme)
            progress.update(task_id, completed=True)
    else:
        # Slow path: need to download catalogue with progress bar
        print_info(
            "First Run",
            "Downloading indicator catalogue (this only happens once, subsequent requests will be fast)",
        )

        # Use spinner progress for indeterminate download (no Content-Length from API)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            DownloadColumn(),
            TransferSpeedColumn(),
            console=console,
            refresh_per_second=10,
        ) as progress:
            download_task = progress.add_task("[cyan]Downloading catalogue...", total=None)

            def progress_callback(downloaded: int, total: int) -> None:
                progress.update(download_task, completed=downloaded)

            indicators = ine.search(query="", theme=theme, progress_callback=progress_callback)

    if not indicators:
        if theme:
            print_error("No Results", f"No indicators found for theme '{theme}'")
        else:
            print_error("No Results", "No indicators found in the catalogue")
        sys.exit(1)

    # Apply limit
    total = len(indicators)
    indicators = indicators[:limit]

    # Display table
    table = create_indicators_table(indicators, limit=len(indicators))
    console.print(table)

    # Show info about remaining results
    if total > limit:
        print_info(
            "Results", f"Showing {len(indicators)} of {total} indicators. Use --limit to see more."
        )


@cli.group()
def cache() -> None:
    """Manage cache.

    \b
    Examples:
        pyptine cache info
        pyptine cache clear
    """
    pass


@cache.command(name="info")
@handle_exceptions
def cache_info() -> None:
    """Show cache statistics."""
    ine = INE(cache=True)

    info = ine.get_cache_info()

    if not info["enabled"]:
        print_info("Cache Status", "Cache is currently disabled")
        return

    print_info("Cache Information", "")

    # Display metadata cache info
    if "metadata_cache" in info:
        meta_info = info["metadata_cache"]
        console.print("[bold cyan]Metadata Cache[/bold cyan]")
        console.print(f"  Entries: {meta_info.get('size', 0)}")

    # Display data cache info
    if "data_cache" in info:
        data_info = info["data_cache"]
        console.print("\n[bold cyan]Data Cache[/bold cyan]")
        console.print(f"  Entries: {data_info.get('size', 0)}")

    # Display total size and location
    if "total_size_mb" in info:
        console.print(f"\n[bold cyan]Total Size[/bold cyan]: {info['total_size_mb']:.1f} MB")

    if "metadata_cache" in info and info["metadata_cache"].get("path"):
        console.print(f"[bold cyan]Location[/bold cyan]: {info['metadata_cache']['path']}")


@cache.command(name="clear")
@click.confirmation_option(prompt="Are you sure you want to clear all cached data?")
@handle_exceptions
def cache_clear() -> None:
    """Clear all cached data."""
    ine = INE(cache=True)

    with spinner_task("Clearing cache...") as progress:
        task_id = progress.add_task("[cyan]Clearing...", total=None)
        ine.clear_cache()
        progress.update(task_id, completed=True)

    print_success("Cache Cleared", "All cached data has been removed successfully")


if __name__ == "__main__":
    cli()
