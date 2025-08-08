ARG BASE_IMAGE

# Build stage using musl (Alpine) and Nuitka
FROM python:3.13-alpine AS builder

# Install build tools and musl headers
RUN apk add --no-cache build-base musl-dev

WORKDIR /app

# Copy project files
COPY . .

# Install project and Nuitka (in
RUN pip install --root-user-action=ignore --no-cache-dir . nuitka

# Build onefile binary with Nuitka (linked against musl by virtue of Alpine)
RUN python -m nuitka \
    --onefile \
    --standalone \
    --output-filename=bluebeacon \
    src/bluebeacon/cli.py

# Final stage
FROM ${BASE_IMAGE}

# Copy the binary from the build stage
COPY --from=builder --chmod=755 /app/bluebeacon /usr/local/bin/bluebeacon

# Set the healthcheck
HEALTHCHECK --interval=5s --timeout=2s --start-period=120s --retries=3 \
    CMD ["/usr/local/bin/bluebeacon"]