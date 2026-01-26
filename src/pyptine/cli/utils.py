"""Utilities for CLI formatting and output."""

import sys
from typing import Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from pyptine.utils.exceptions import INEError

# Create a rich console for output
console = Console()
error_console = Console(stderr=True, style="red")


def print_error(title: str, message: str) -> None:
    """Print an error message with consistent formatting.

    Args:
        title: Error title
        message: Error message details
    """
    error_panel = Panel(
        f"[red]{message}[/red]",
        title=f"[bold red]✗ {title}[/bold red]",
        border_style="red",
    )
    error_console.print(error_panel)


def print_success(title: str, message: str = "") -> None:
    """Print a success message with consistent formatting.

    Args:
        title: Success title
        message: Optional additional message
    """
    content = f"[green]{message}[/green]" if message else ""
    success_panel = Panel(
        content,
        title=f"[bold green]✓ {title}[/bold green]",
        border_style="green",
        padding=(0, 1) if message else (0, 0),
    )
    console.print(success_panel)


def print_info(title: str, message: str = "") -> None:
    """Print an info message with consistent formatting.

    Args:
        title: Info title
        message: Optional additional message
    """
    content = f"[cyan]{message}[/cyan]" if message else ""
    info_panel = Panel(
        content,
        title=f"[bold cyan]ℹ {title}[/bold cyan]",
        border_style="cyan",
        padding=(0, 1) if message else (0, 0),
    )
    console.print(info_panel)


def create_indicators_table(indicators: Any, limit: Optional[int] = None) -> Table:
    """Create a formatted table of indicators.

    Args:
        indicators: List of indicator objects
        limit: Maximum number of indicators to display

    Returns:
        Rich Table object with indicator data
    """
    table = Table(title="Indicators", show_header=True, header_style="bold cyan")
    table.add_column("Code", style="cyan", width=12)
    table.add_column("Title", style="white")
    table.add_column("Theme", style="magenta")

    for ind in indicators[:limit] if limit else indicators:
        theme = ind.theme or "-"
        table.add_row(ind.varcd, ind.title, theme)

    return table


def create_dimensions_table(dimensions: Any) -> Table:
    """Create a formatted table of dimensions.

    Args:
        dimensions: List of dimension objects

    Returns:
        Rich Table object with dimension data
    """
    table = Table(title="Dimensions", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="cyan", width=6)
    table.add_column("Name", style="white")
    table.add_column("Values", style="green", justify="right")

    for dim in dimensions:
        table.add_row(f"Dim{dim.id}", dim.name, str(len(dim.values)))

    return table


def create_themes_table(themes: list[str]) -> Table:
    """Create a formatted table of themes.

    Args:
        themes: List of theme names

    Returns:
        Rich Table object with theme data
    """
    table = Table(title=f"Themes ({len(themes)})", show_header=True, header_style="bold cyan")
    table.add_column("Theme", style="white")

    for theme in themes:
        table.add_row(theme)

    return table


def spinner_task(description: str) -> Progress:
    """Create a progress spinner for loading operations.

    Args:
        description: Description text for the spinner

    Returns:
        Rich Progress object with spinner
    """
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    )
    return progress


def handle_cli_error(exception: Exception, verbose: bool = False) -> None:
    """Handle and display CLI errors with consistent formatting.

    Args:
        exception: The exception to handle
        verbose: If True, include full traceback

    Raises:
        SystemExit: Always exits with code 1
    """
    if isinstance(exception, INEError):
        print_error("API Error", str(exception))
    else:
        print_error("Unexpected Error", str(exception))

    if verbose:
        console.print_exception()

    sys.exit(1)


def format_indicator_info(indicator: Any, metadata: Any) -> str:
    """Format detailed indicator information for display.

    Args:
        indicator: Indicator object
        metadata: Indicator metadata

    Returns:
        Formatted string with indicator details
    """
    lines = []

    # Code
    lines.append(f"[cyan]Code:[/cyan] {indicator.varcd}")

    # Title
    lines.append(f"[cyan]Title:[/cyan] {indicator.title}")

    # Description
    if indicator.description:
        lines.append(f"[cyan]Description:[/cyan] {indicator.description}")

    # Theme
    if indicator.theme:
        lines.append(f"[cyan]Theme:[/cyan] {indicator.theme}")

    # Subtheme
    if indicator.subtheme:
        lines.append(f"[cyan]Subtheme:[/cyan] {indicator.subtheme}")

    # Periodicity
    if indicator.periodicity:
        lines.append(f"[cyan]Periodicity:[/cyan] {indicator.periodicity}")

    # Last period
    if indicator.last_period:
        lines.append(f"[cyan]Last Period:[/cyan] {indicator.last_period}")

    # Unit
    if metadata.unit:
        lines.append(f"[cyan]Unit:[/cyan] {metadata.unit}")

    # Source
    if indicator.source:
        lines.append(f"[cyan]Source:[/cyan] {indicator.source}")

    return "\n".join(lines)
