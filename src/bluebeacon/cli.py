"""Command-line interface for BlueBeacon.

This module provides the main entry point for the BlueBeacon utility.
"""

from pathlib import Path

import click

from bluebeacon import detector, ping

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_ERROR = 2


@click.command()
@click.help_option("--help", "-h")
@click.argument(
    "config_path", type=click.Path(path_type=Path), required=False, default=Path.home()
)
def main(config_path: Path) -> int:
    """Docker healthcheck utility for Minecraft servers.

    This tool checks if a Minecraft server is running and responding to ping requests.
    It automatically detects server configuration from the provided path.

    \b
    Args:
        config_path: Path to server config file or directory (default: user home)

    \b
    Exit codes:
        0 - Success: Server is reachable and responding
        1 - Failure: Server is not reachable or not responding
        2 - Error: Configuration error or invalid arguments
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

    server_reachable = ping.ping_server(server_address, server_port)

    if server_reachable:
        raise click.exceptions.Exit(EXIT_SUCCESS)
    else:
        raise click.exceptions.Exit(EXIT_FAILURE)


if __name__ == "__main__":  # pragma: no cover
    main()
