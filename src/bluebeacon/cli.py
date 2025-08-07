"""Command-line interface for BlueBeacon.

This module provides the main entry point for the BlueBeacon utility.
"""

import sys
from pathlib import Path

import click

from bluebeacon import detector


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
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
