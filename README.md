# BlueBeacon

[![Pipeline Status](https://gitlab.project-creative.net/AuraDev/BlueBeacon/badges/master/pipeline.svg)](https://gitlab.project-creative.net/AuraDev/BlueBeacon/-/pipelines)
[![Coverage](https://gitlab.project-creative.net/AuraDev/BlueBeacon/badges/master/coverage.svg)](https://gitlab.project-creative.net/AuraDev/BlueBeacon/-/graphs/master/charts)

<div style="text-align: center;">
  <img src="logo_200.png" alt="BlueBeacon Logo" width="200"/>
</div>

BlueBeacon is a Python utility designed to serve as a Docker healthcheck for Minecraft servers. It automatically detects
server settings and pings the server to verify responsiveness, making it easy to monitor containerized Minecraft servers
without additional configuration.

## Features

- **Automatic Server Detection**: Automatically finds and reads Minecraft server configuration files
- **Multi-Platform Support**: Works with Java Edition servers (vanilla, Spigot, Paper, Forge, Fabric, etc.), Bedrock
  Edition servers, and proxies (BungeeCord, Velocity)
- **Zero Configuration**: No need to manually specify server ports or settings
- **Standalone Binary**: Distributed as source code but compiled to a standalone binary in the Docker build process

## Usage

### As a Docker Healthcheck

Add BlueBeacon to your Minecraft server Dockerfile:

```dockerfile
# Add healthcheck using BlueBeacon
HEALTHCHECK --interval=5s --timeout=2s --start-period=120s --retries=3 \
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

If no path is provided, BlueBeacon will search the current user's home directory, which is where most Docker images
place server files.

## How It Works

1. BlueBeacon searches for Minecraft server configuration files in the specified location (or home directory by default)
2. It parses the configuration to determine the server type and port
3. It sends a ping request using the appropriate protocol (Java or Bedrock)
4. It returns a success exit code (0) if the server responds properly, or a failure code otherwise

## Distribution

BlueBeacon is distributed as source code, with a template Dockerfiles that include a build stage to compile it into a
standalone binary. This ensures no additional dependencies are needed in the final Docker image.

### Building your own image (Dockerfile templates)

This repository includes two Dockerfiles you can use as templates when building images that embed the BlueBeacon binary:

- Dockerfile.simple: Use this as the base template when targeting up-to-date, glibc-based images (for example, current
  Debian/Ubuntu with glibc). It uses a modern Python base image and is the recommended starting point for most cases.
- Dockerfile: Use this example when you specifically need compatibility with older glibc versions in the target
  environment. It builds Python via pyenv on an older Ubuntu base to maximize runtime compatibility with legacy systems.

Note for Alpine-based images: If your target/base image is Alpine (musl), you can change the builder image in
`Dockerfile.simple` from `python:3.13-slim` to `python:3.13-alpine` to produce a binary suitable for Alpine-based
images.

Examples:

- Build with the simple template (recommended):
    - docker build -f Dockerfile.simple -t bluebeacon:latest .
- Build with the legacy-compat template:
    - docker build -f Dockerfile -t bluebeacon:legacy .

### Note on the binary format

The build process uses Nuitka to create a single-file executable. The resulting binary links against the system's libc
present in the build environment. If you need broader runtime compatibility with older glibc versions, build using the
legacy-compat Dockerfile (`Dockerfile`) on an older base image; otherwise, `Dockerfile.simple` is recommended for
up-to-date glibc-based targets.

## Prebuilt Docker images for Pterodactyl

Prebuilt container images are provided for use with Pterodactyl. These images are designed to be used as base images ("
yolks") for your Eggs and are built on top of the official Pterodactyl yolk images:

- Official yolks: https://github.com/pterodactyl/yolks/pkgs/container/yolks

Registry:

- Pull URL: registry.gitlab.project-creative.net/auradev/bluebeacon:TAG
- Tag overview: https://gitlab.project-creative.net/AuraDev/BlueBeacon/container_registry/2

Key details:

- Tags align with the upstream yolk tags (e.g., `java_8`, `java_11`, `java_17`, `java_21`, as well as `java_17j9`,
  etc.).
- Each BlueBeacon image layer adds the BlueBeacon binary, and the Dockerfile includes a HEALTHCHECK that runs BlueBeacon
  automatically. No extra setup is needed — using these images automatically enables the container health check.
- Images are published to this project's Container Registry at the URL above.

Examples:

- Pull a specific tag with Docker:
    - `docker pull registry.gitlab.project-creative.net/auradev/bluebeacon:java_17`
- Use as a Pterodactyl image for a Java 17 server Egg:
    - Image: `registry.gitlab.project-creative.net/auradev/bluebeacon:java_17`
    - Health check: already configured and active by default (no additional configuration required).

Note: The images are built in CI using the corresponding upstream yolk as the base (e.g.,
`ghcr.io/pterodactyl/yolks:java_17`), ensuring compatibility with Pterodactyl's ecosystem.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
