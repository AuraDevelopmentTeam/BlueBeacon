"""Command-line interface for BlueBeacon.

This module provides the main entry point for the BlueBeacon utility.
"""

import sys
from pathlib import Path
from typing import Optional

import click


@click.command(help="Docker healthcheck utility for Minecraft servers")
@click.argument("config_path", type=click.Path(path_type=Path), required=False)
def main(config_path: Optional[Path] = None) -> int:
    """Main entry point for the application.

    Args:
        config_path: Path to server config file or directory (default: user home)
    """

    if config_path is None:
        config_path = Path.home()

    return 0


if __name__ == "__main__":
    sys.exit(main())
