# BlueBeacon

[![Pipeline Status](https://gitlab.project-creative.net/AuraDev/BlueBeacon/badges/master/pipeline.svg)](https://gitlab.project-creative.net/AuraDev/BlueBeacon/-/pipelines)
[![Coverage](https://gitlab.project-creative.net/AuraDev/BlueBeacon/badges/master/coverage.svg)](https://gitlab.project-creative.net/AuraDev/BlueBeacon/-/graphs/master/charts)

<p align="center">
  <img src="logo_200.png" alt="BlueBeacon Logo" width="200"/>
</p>

BlueBeacon is a Python utility designed to serve as a Docker healthcheck for Minecraft servers. It automatically detects server settings and pings the server to verify responsiveness, making it easy to monitor containerized Minecraft servers without additional configuration.

## Features

- **Automatic Server Detection**: Automatically finds and reads Minecraft server configuration files
- **Multi-Platform Support**: Works with Java Edition servers (vanilla, Spigot, Paper, Forge, Fabric, etc.), Bedrock Edition servers, and proxies (BungeeCord, Velocity)
- **Zero Configuration**: No need to manually specify server ports or settings
- **Standalone Binary**: Distributed as source code but compiled to a standalone binary in the Docker build process

## Usage

### As a Docker Healthcheck

Add BlueBeacon to your Minecraft server Dockerfile:

```dockerfile
# Add healthcheck using BlueBeacon
HEALTHCHECK --interval=5s --timeout=1s --start-period=5s --retries=3 \
    CMD ["/path/to/bluebeacon"]
```

### Command Line Options

BlueBeacon accepts one optional command line parameter:

```
bluebeacon [CONFIG_PATH]
```

Where `CONFIG_PATH` can be either:
- A specific config file path
- A directory to search for config files

If no path is provided, BlueBeacon will search the current user's home directory, which is where most Docker images place server files.

## How It Works

1. BlueBeacon searches for Minecraft server configuration files in the specified location (or home directory by default)
2. It parses the configuration to determine the server type and port
3. It sends a ping request using the appropriate protocol (Java or Bedrock)
4. It returns a success exit code (0) if the server responds properly, or a failure code otherwise

## Distribution

BlueBeacon is distributed as source code, with a template Dockerfile that includes a build stage to compile it into a standalone binary. This ensures no additional dependencies are needed in the final Docker image.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
