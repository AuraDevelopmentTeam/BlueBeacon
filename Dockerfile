ARG BASE_IMAGE=scratch

# Build stage
FROM python:3.13-slim AS builder

# Install packages required for creating the binary and bundling libc
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        binutils \
        patchelf \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY . .

# Install dependencies, PyInstaller, and staticx
RUN pip install --root-user-action=ignore --no-cache-dir . pyinstaller staticx

# Create optimized single binary
RUN pyinstaller \
        --onefile \
        --name bluebeacon \
        --strip \
        --optimize 2 \
        --console \
        src/bluebeacon/cli.py

# Repackage the binary with bundled libc using staticx
RUN staticx \
        --strip \
        dist/bluebeacon dist/bluebeacon.static

# Final stage
FROM ${BASE_IMAGE}

# Copy the binary from the build stage
COPY --from=builder --chmod=755 /app/dist/bluebeacon.static /usr/local/bin/bluebeacon

# Set the healthcheck
HEALTHCHECK --interval=5s --timeout=2s --start-period=120s --retries=3 \
    CMD ["/usr/local/bin/bluebeacon"]