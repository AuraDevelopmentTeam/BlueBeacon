"""Server ping functionality for BlueBeacon.

This module handles pinging Minecraft servers to check their availability.
"""

import ipaddress

from mcstatus import BedrockServer, JavaServer


def ping_server(
    server_address: ipaddress.IPv4Address | ipaddress.IPv6Address, server_port: int
) -> bool:
    """Ping a Minecraft server to check if it's responsive.

    Args:
        server_address: IPv4 or IPv6 address of the Minecraft server to ping
        server_port: Network port number the Minecraft server is listening on


    Returns:
        True if the server responds successfully, False otherwise.
    """

    host = str(server_address)
    if isinstance(server_address, ipaddress.IPv6Address):
        host = f"[{host}]"

    for protocol in [JavaServer, BedrockServer]:
        try:
            server = protocol(host, server_port, 0.5)
            server.status()

            # If we get here, the server responded successfully and is consequently up.
            return True
        except (TimeoutError, IOError):
            pass

    return False
