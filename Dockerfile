ARG BASE_IMAGE=scratch

FROM alpine:latest AS builder

# Install build dependencies
RUN apk add --no-cache \
        bash \
        build-base \
        bzip2-dev \
        ccache \
        git \
        libffi-dev \
        musl-dev \
        openssl-dev \
        patchelf \
        readline-dev \
        sqlite-dev \
        tk-dev \
        xz-dev \
        zlib-dev \
        zstd-dev

# Install pyenv
ENV PYENV_ROOT="/opt/pyenv"
ENV PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"

RUN git clone https://github.com/pyenv/pyenv.git $PYENV_ROOT

# Install Python
RUN PYTHON_CONFIGURE_OPTS="--disable-shared" pyenv install 3.13 \
 && pyenv global 3.13

# Verify python is fully static
RUN pyenv which python && ldd `pyenv which python` || true

# Upgrade pip and install nuitka
RUN pip install --root-user-action=ignore --no-cache-dir --upgrade pip setuptools wheel nuitka

WORKDIR /app

# Copy your app source files into /app
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
        --nofollow-import-to=setuptools \
        --output-dir=dist \
        --output-filename=bluebeacon \
        src/bluebeacon/cli.py

# Verify the binary is static (should say "not a dynamic executable")
RUN file dist/bluebeacon && ldd dist/bluebeacon || true

# Final stage
FROM ${BASE_IMAGE}

# Copy the binary from the build stage
COPY --from=builder --chmod=755 /app/dist/bluebeacon /usr/local/bin/bluebeacon

# Set the healthcheck
HEALTHCHECK --interval=5s --timeout=2s --start-period=120s --retries=3 \
    CMD ["/usr/local/bin/bluebeacon"]