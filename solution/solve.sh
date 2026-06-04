#!/bin/bash
set -e

# Copy the fixed source into the project
cp /solution/src/lib.rs /app/src/lib.rs

# Rebuild the binary with the fix
cd /app
cargo build --release

# Install the fixed binary
cp target/release/market-feed-parser /usr/local/bin/market-feed-parser