ARG BASE_IMAGE=scratch

# Build stage
FROM ubuntu:20.04 AS builder

# Install packages required for creating the binary and bundling libc
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        ccache \
        curl \
        git \
        libbz2-dev \
        libffi-dev \
        liblzma-dev \
        libncursesw5-dev \
        libreadline-dev \
        libsqlite3-dev \
        libssl-dev \
        libxml2-dev \
        libxmlsec1-dev \
        make \
        patchelf \
        tk-dev \
        xz-utils \
        zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

# Install pyenv
ENV PYENV_ROOT="/opt/pyenv"
ENV PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"

RUN git clone https://github.com/pyenv/pyenv.git $PYENV_ROOT

# Install Python 3.13
RUN pyenv install 3.13 \
 && pyenv global 3.13

# Upgrade pip and install pyinstaller
RUN pip install --root-user-action=ignore --no-cache-dir --upgrade pip setuptools wheel nuitka

# Copy project files
WORKDIR /app
COPY . .

# Install project dependencies
RUN pip install --root-user-action=ignore --no-cache-dir .

# Build static executable with Nuitka
RUN mkdir dist \
 && nuitka \
        --onefile \
        --standalone \
        --static-libpython=yes \
        --lto=yes \
        --onefile-no-compression \
        --output-dir=dist \
        --output-filename=bluebeacon \
        src/bluebeacon/cli.py

# Final stage
FROM ${BASE_IMAGE}

# Copy the binary from the build stage
COPY --from=builder --chmod=755 /app/dist/bluebeacon /usr/local/bin/bluebeacon

# Set the healthcheck
HEALTHCHECK --interval=5s --timeout=1s --start-period=120s --retries=3 \
    CMD ["/usr/local/bin/bluebeacon"]