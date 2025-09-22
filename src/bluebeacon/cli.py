"""Command-line interface for BlueBeacon.

This module provides the main entry point for the BlueBeacon utility.
"""

from pathlib import Path

import click

from bluebeacon import __version__, detector, ping

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_ERROR = 2


def set_server_type(ctx: click.Context, param: click.Parameter, value: bool) -> None:
    """Callback to handle mutually exclusive server type flags."""
    if not value:
        return

    # Get the option name without dashes
    server_type = param.name

    # Store the server type in the context
    ctx.ensure_object(dict)
    ctx.obj["server_type"] = server_type


@click.command(
    help="Docker healthcheck utility for Minecraft servers. This tool checks if a Minecraft server is running and responding to ping requests. It automatically detects server configuration from the provided path.",
    short_help="Minecraft server healthcheck utility",
    epilog="""CONFIG_PATH: Path to server config file or directory (default: user home directory)

\b
Exit codes:
  0 - Success: Server is reachable and responding
  1 - Failure: Server is not reachable or not responding
  2 - Error: Configuration error or invalid arguments""",
)
@click.help_option("--help", "-h")
@click.option("--version", "-V", is_flag=True, help="Show the version and exit")
@click.option(
    "--java",
    is_flag=True,
    callback=set_server_type,
    expose_value=False,
    help="Target Java Edition servers only",
)
@click.option(
    "--bedrock",
    is_flag=True,
    callback=set_server_type,
    expose_value=False,
    help="Target Bedrock Edition servers only",
)
@click.option(
    "--both",
    is_flag=True,
    callback=set_server_type,
    expose_value=False,
    help="Target both Java and Bedrock Edition servers (default)",
)
@click.argument(
    "config_path",
    type=click.Path(path_type=Path),
    required=False,
    metavar="CONFIG_PATH",
    default=Path.home(),
)
@click.pass_context
def main(ctx: click.Context, config_path: Path, version: bool) -> int:
    """Implementation of the BlueBeacon CLI."""
    if version:
        click.echo(f"BlueBeacon v{__version__}")
        ctx.exit(EXIT_SUCCESS)

    server_type = ctx.obj.get("server_type", "both") if ctx.obj else "both"

    try:
        server_config = detector.find_server_config(config_path)
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}")
        ctx.exit(EXIT_ERROR)

    try:
        server_address, server_port = detector.parse_server_config(server_config)
    except ValueError as exc:
        click.echo(f"Error: {exc}")
        ctx.exit(EXIT_ERROR)

    server_reachable = ping.ping_server(server_address, server_port, server_type)

    ctx.exit(EXIT_SUCCESS if server_reachable else EXIT_FAILURE)


if __name__ == "__main__":  # pragma: no cover
    main()
