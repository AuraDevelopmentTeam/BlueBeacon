ARG BASE_IMAGE

# Build stage
FROM python:3.13-slim AS builder

# Install packages required for creating the binary and bundling libc
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        binutils \
        build-essential \
        ccache \
        patchelf \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY . .

# Install dependencies, Nuitka, and staticx
RUN pip install --root-user-action=ignore --no-cache-dir . nuitka staticx

# Create optimized single binary
RUN mkdir dist \
 && nuitka \
        --onefile \
        --standalone \
        --output-dir=dist \
        --output-filename=bluebeacon \
        src/bluebeacon/cli.py

# Repackage the binary with bundled libc using staticx
RUN staticx \
        dist/bluebeacon dist/bluebeacon.static

# Final stage
FROM ${BASE_IMAGE}

# Copy the binary from the build stage
COPY --from=builder --chmod=755 /app/dist/bluebeacon /usr/local/bin/bluebeacon

# Set the healthcheck
HEALTHCHECK --interval=5s --timeout=2s --start-period=120s --retries=3 \
    CMD ["/usr/local/bin/bluebeacon"]