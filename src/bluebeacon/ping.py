"""Server ping functionality for BlueBeacon.

This module handles pinging Minecraft servers to check their availability.
"""

import ipaddress
import threading
from typing import Callable

from mcstatus import BedrockServer, JavaServer


def ping_server(
    server_address: ipaddress.IPv4Address | ipaddress.IPv6Address, server_port: int
) -> bool:
    """Ping a Minecraft server using parallel protocol checks using daemon threads.

    Attempts both Java and Bedrock status checks concurrently and returns True
    as soon as one of them succeeds. Keeps a simple synchronous API.

    Args:
        server_address: IPv4 or IPv6 address of the Minecraft server to ping
        server_port: Network port number the Minecraft server is listening on

    Returns:
        True if the server responds successfully, False otherwise.
    """

    host = str(server_address)
    if isinstance(server_address, ipaddress.IPv6Address):
        host = f"[{host}]"

    # 250 ms are enough for local servers. This results in a failure taking ~750 ms, as the library performs 3 checks in
    # total. This keeps the total runtime under 1 s.
    timeout = 0.25

    # Use condition-based synchronization to avoid fixed-time waiting
    lock = threading.Lock()
    cond = threading.Condition(lock)
    success = False
    finished_threads = 0

    def worker(
        server_factory: Callable[[str, int, float], JavaServer | BedrockServer],
    ) -> None:
        nonlocal success, finished_threads
        try:
            server = server_factory(host, server_port, timeout)
            server.status()
            success = True
        except (TimeoutError, IOError):
            # Treat these simply as a failed check
            pass

        with cond:
            finished_threads += 1
            cond.notify()

    threads = [
        threading.Thread(target=worker, args=(JavaServer,), daemon=True),
        threading.Thread(target=worker, args=(BedrockServer,), daemon=True),
    ]

    for t in threads:
        t.start()

    # Wait until either one succeeds or both have finished, without a fixed timeout
    with cond:
        while not success and finished_threads < len(threads):
            cond.wait()

    return success
