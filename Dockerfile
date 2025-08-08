ARG BASE_IMAGE

# Build stage
FROM python:3.13-alpine AS builder

# Install build tools and musl headers
RUN apk add --no-cache build-base musl-dev patchelf

WORKDIR /app

# Copy project files
COPY . .

# Install dependencies and PyInstaller
RUN pip install --root-user-action=ignore --no-cache-dir . pyinstaller

# Create optimized single binary
RUN pyinstaller \
    --onefile \
    --name bluebeacon \
    --strip \
    --optimize 2 \
    --console \
    src/bluebeacon/cli.py

# Final stage
FROM ${BASE_IMAGE}

# Copy the binary from the build stage
COPY --from=builder --chmod=755 /app/dist/bluebeacon /usr/local/bin/bluebeacon

# Set the healthcheck
HEALTHCHECK --interval=5s --timeout=2s --start-period=120s --retries=3 \
    CMD ["/usr/local/bin/bluebeacon"]