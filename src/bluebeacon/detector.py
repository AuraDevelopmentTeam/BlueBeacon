"""Server configuration detector for BlueBeacon.

This module handles the detection and parsing of Minecraft server configuration files.
"""

from pathlib import Path


def find_server_config(path: Path) -> Path:
    """Find Minecraft server configuration.

    Args:
        path: Path to a specific config file or directory to search.

    Returns:
        Dictionary containing server configuration details.

    Raises:
        FileNotFoundError: If no valid server configuration could be found.
    """

    if path.is_file():
        return path

    for file_name in ["server.properties", "config.yml", "velocity.toml"]:
        file_path = path / file_name
        if file_path.exists():
            return file_path

    raise FileNotFoundError(f"No valid server configuration found in {path}.")
