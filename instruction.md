# Market Feed Parser — Debug Task

You are working on a high-frequency trading infrastructure team. A critical component is a Rust command-line tool called `market-feed-parser` that decodes raw binary market-data feeds.

## Binary Protocol

The feed is a packed byte stream. Each message is framed as:

```
[ 2-byte little-endian length (u16) ][ payload of that many bytes ]
```

Messages appear back-to-back with no delimiters or padding between them. A stream may end with trailing bytes that are too short to form a complete frame — these should be silently ignored.

## The Tool

The compiled binary lives at `/usr/local/bin/market-feed-parser`. Its source code is in `/app/` (a standard Cargo project: `Cargo.toml`, `src/lib.rs`, `src/main.rs`).

When invoked, it reads raw bytes from **stdin** and writes one JSON line per parsed message to **stdout**:

```json
{"index":0,"length":5,"payload_hex":"48656c6c6f"}
```

Each line contains:
- `index` — zero-based message sequence number
- `length` — payload byte count
- `payload_hex` — lowercase hex encoding of the payload bytes

## The Problem

Users are reporting two classes of failures:

1. **Crashes**: The parser panics with `index out of bounds` when fed streams that contain short trailing data or are empty. It should handle these gracefully by stopping parsing and exiting successfully.

2. **Missing / corrupted messages**: When a stream contains multiple back-to-back messages, some are silently dropped or their payloads are garbled. For example, a stream with three 5-byte messages only produces one or two output lines, and the payloads after the first one are wrong.

## Your Task

1. Examine the Rust source code in `/app/src/` and identify the root cause(s) of both issues.
2. Fix the parser so that it correctly handles:
   - Empty input (no output, clean exit)
   - Single messages
   - Multiple packed messages
   - Streams ending with incomplete frames (silently skip the trailing bytes)
3. Rebuild the binary and install it:
   ```bash
   cd /app
   cargo build --release
   cp target/release/market-feed-parser /usr/local/bin/market-feed-parser
   ```

Do **not** change the output format — each parsed message must still be a JSON line with `index`, `length`, and `payload_hex` fields.
