"""BlueBeacon - A Docker healthcheck utility for Minecraft servers.

BlueBeacon automatically detects server settings and pings the server to verify
responsiveness, making it easy to monitor containerized Minecraft servers.
"""

from importlib.metadata import version

__version__ = version("bluebeacon")
