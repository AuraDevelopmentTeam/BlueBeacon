ARG BASE_IMAGE=alpine:latest

# Build stage
FROM python:3.13-slim AS builder

WORKDIR /app

# Copy project files
COPY . .

# Install dependencies and PyInstaller
RUN pip install --no-cache-dir -e . && \
    pip install --no-cache-dir pyinstaller

# Create optimized single binary
RUN pyinstaller --onefile \
    --name bluebeacon \
    --strip \
    --optimize 2 \
    --console \
    src/bluebeacon/cli.py

# Final stage
FROM ${BASE_IMAGE}

# Copy the binary from the build stage
COPY --from=builder /app/dist/bluebeacon /usr/local/bin/bluebeacon

# Make the binary executable
RUN chmod +x /usr/local/bin/bluebeacon

# Set the healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ["/usr/local/bin/bluebeacon"]