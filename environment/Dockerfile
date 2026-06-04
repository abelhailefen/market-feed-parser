FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies: build tools, Python, pip
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Rust via rustup (minimal profile, stable toolchain)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable --profile minimal
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy the Rust project source into the image
WORKDIR /app
COPY Cargo.toml ./
COPY src/ ./src/

# Build the binary (buggy version) during image build
RUN cargo build --release \
    && cp target/release/market-feed-parser /usr/local/bin/market-feed-parser

# Install pytest globally (completely offline-ready at runtime)
RUN pip install --break-system-packages pytest pytest-json-ctrf

WORKDIR /app