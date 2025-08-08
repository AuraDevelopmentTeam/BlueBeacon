"""Command-line interface for BlueBeacon.

This module provides the main entry point for the BlueBeacon utility.
"""

import sys
from pathlib import Path

import click

from bluebeacon import detector

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_ERROR = 2


@click.command(help="Docker healthcheck utility for Minecraft servers")
@click.argument(
    "config_path", type=click.Path(path_type=Path), required=False, default=Path.home()
)
def main(config_path: Path) -> int:
    """Main entry point for the application.

    Args:
        config_path: Path to server config file or directory (default: user home)
    """
    try:
        server_config = detector.find_server_config(config_path)
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}")
        raise click.exceptions.Exit(EXIT_ERROR)

    try:
        server_address, server_port = detector.parse_server_config(server_config)
    except ValueError as exc:
        click.echo(f"Error: {exc}")
        raise click.exceptions.Exit(EXIT_ERROR)

    raise click.exceptions.Exit(EXIT_SUCCESS)


if __name__ == "__main__":  # pragma: no cover
    main()
