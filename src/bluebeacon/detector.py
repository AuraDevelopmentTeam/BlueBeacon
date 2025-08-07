"""Server configuration detector for BlueBeacon.

This module handles the detection and parsing of Minecraft server configuration files.
"""

import ipaddress
import tomllib
from pathlib import Path
from typing import Optional, Tuple

import javaproperties
import yaml


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


def parse_server_config(
    config_file: Path,
) -> Tuple[ipaddress.IPv4Address | ipaddress.IPv6Address, int]:
    """
    Parses a server configuration file and extracts the server address and port.
    The function supports multiple file formats (INI, YAML, TOML) and tries each
    parser in sequence. If the file format is unsupported or parsing fails, an
    exception is raised.

    :param config_file: The path to the configuration file to be parsed.
    :type config_file: Path
    :return: A tuple containing the server IP address (IPv4 or IPv6) and the port
        number.
    :rtype: Tuple[ipaddress.IPv4Address | ipaddress.IPv6Address, int]
    :raises ValueError: If the configuration file format is unsupported.
    """
    for parser in [_parse_ini_config, _parse_yaml_config, _parse_toml_config]:
        result = parser(config_file)
        if result is not None:
            return result

    raise ValueError(f"Unsupported server config file format: {config_file}")


def _parse_ini_config(
    config_file: Path,
) -> Optional[Tuple[ipaddress.IPv4Address | ipaddress.IPv6Address, int]]:
    try:
        with config_file.open("rb") as f:
            config = javaproperties.load(f)
    except javaproperties.InvalidUEscapeError:
        return None

    if "server-address" in config and "server-port" in config:
        return (
            ipaddress.ip_address(config["server-address"]),
            int(config["server-port"]),
        )

    return None


def _parse_yaml_config(
    config_file: Path,
) -> Optional[Tuple[ipaddress.IPv4Address | ipaddress.IPv6Address, int]]:
    try:
        with config_file.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError:
        return None

    if "listeners" in config:
        for listener in config["listeners"]:
            if "host" in listener:
                (address, port) = listener["host"].split(":")

                return (
                    ipaddress.ip_address(address),
                    int(port),
                )

    return None


def _parse_toml_config(
    config_file: Path,
) -> Optional[Tuple[ipaddress.IPv4Address | ipaddress.IPv6Address, int]]:
    try:
        with config_file.open("rb") as f:
            config = tomllib.load(f)
    except tomllib.TOMLDecodeError:
        return None

    if "bind" in config:
        (address, port) = config["bind"].split(":")

        return (
            ipaddress.ip_address(address),
            int(port),
        )

    return None
