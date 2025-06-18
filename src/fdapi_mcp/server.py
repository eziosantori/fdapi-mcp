"""FDAPI MCP Server main entry point."""

import asyncio
import logging
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from .config import ServerConfig
from .mcp_server import create_mcp_server

app = typer.Typer(name="fdapi-mcp", help="FDAPI Model Context Protocol Server")
console = Console()


def setup_logging(level: str = "INFO") -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )


def main() -> None:
    """Main entry point for the FDAPI MCP server."""
    console.print(
        Panel.fit(
            "[bold green]FDAPI MCP Server[/bold green]\n"
            "[dim]A Model Context Protocol server for FDAPI integration[/dim]\n\n"
            "[yellow]Status:[/yellow] [green]Ready[/green]\n"
            "[yellow]Phase:[/yellow] [blue]Core Infrastructure[/blue]",
            title="🚀 FDAPI MCP Server",
            border_style="green",
        )
    )


@app.command()
def serve(
    host: str = typer.Option("localhost", help="Host to bind to"),
    port: int = typer.Option(8000, help="Port to bind to"),
    debug: bool = typer.Option(False, help="Enable debug mode"),
) -> None:
    """Start the MCP server."""
    config = ServerConfig.load()

    # Override config with CLI arguments
    config.host = host
    config.port = port
    config.debug = debug

    # Set up logging
    log_level = "DEBUG" if debug else config.log_level
    setup_logging(log_level)

    console.print(f"[yellow]Starting MCP server on {host}:{port}[/yellow]")

    if debug:
        console.print("[yellow]Debug mode enabled[/yellow]")

    try:
        # Create and run the MCP server
        server = create_mcp_server(config)
        asyncio.run(server.run())
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Server error: {e}[/red]")
        if debug:
            console.print_exception()
        sys.exit(1)


@app.command()
def version() -> None:
    """Show version information."""
    from fdapi_mcp import __version__
    console.print(f"FDAPI MCP Server version: [green]{__version__}[/green]")


@app.command()
def config() -> None:
    """Show current configuration."""
    try:
        config = ServerConfig.load()
        console.print(Panel.fit(
            f"[bold]Server Configuration[/bold]\n\n"
            f"Host: {config.host}\n"
            f"Port: {config.port}\n"
            f"Debug: {config.debug}\n"
            f"Log Level: {config.log_level}\n\n"
            f"[bold]FDAPI Configuration[/bold]\n\n"
            f"Base URL: {config.fdapi.base_url}\n"
            f"Timeout: {config.fdapi.timeout}s\n"
            f"Max Retries: {config.fdapi.max_retries}\n"
            f"API Key: {'***' if config.fdapi.api_key else 'Not set'}",
            title="Configuration",
            border_style="blue",
        ))
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")


if __name__ == "__main__":
    app()
