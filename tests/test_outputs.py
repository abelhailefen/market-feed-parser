"""
Tests for the market-feed-parser binary.

Each test constructs a raw binary input stream, pipes it to the compiled
CLI at /usr/local/bin/market-feed-parser via subprocess, and asserts
correct JSON-line output and exit codes.
"""

import json
import struct
import subprocess

BINARY = "/usr/local/bin/market-feed-parser"


def _run(input_bytes: bytes) -> subprocess.CompletedProcess:
    """Helper: invoke the parser binary with the given stdin bytes."""
    return subprocess.run(
        [BINARY],
        input=input_bytes,
        capture_output=True,
        timeout=10,
    )


def _frame(payload: bytes) -> bytes:
    """Build a single length-prefixed frame: [u16-LE length][payload]."""
    return struct.pack("<H", len(payload)) + payload


def _parse_output_lines(stdout: bytes) -> list[dict]:
    """Parse newline-delimited JSON output from the binary."""
    lines = stdout.decode("utf-8").strip().splitlines()
    return [json.loads(line) for line in lines] if lines else []


# ─────────────────────────────────────────────────────────────────────
# Test cases
# ─────────────────────────────────────────────────────────────────────


def test_single_message():
    """A single well-formed frame produces exactly one JSON line."""
    payload = b"Hello"
    result = _run(_frame(payload))

    assert result.returncode == 0, f"non-zero exit: {result.stderr.decode()}"

    msgs = _parse_output_lines(result.stdout)
    assert len(msgs) == 1

    assert msgs[0]["index"] == 0
    assert msgs[0]["length"] == 5
    assert msgs[0]["payload_hex"] == payload.hex()


def test_multiple_messages():
    """Three back-to-back frames must all be parsed correctly.

    This catches the double-advance bug: if the cursor skips 2 extra bytes
    per message, the second and third messages will be garbled or missing.
    """
    payloads = [b"AAAA", b"BBBB", b"CCCC"]
    stream = b"".join(_frame(p) for p in payloads)
    result = _run(stream)

    assert result.returncode == 0, f"non-zero exit: {result.stderr.decode()}"

    msgs = _parse_output_lines(result.stdout)
    assert len(msgs) == 3, f"expected 3 messages, got {len(msgs)}"

    for i, p in enumerate(payloads):
        assert msgs[i]["index"] == i
        assert msgs[i]["length"] == len(p)
        assert msgs[i]["payload_hex"] == p.hex()


def test_empty_input():
    """Empty input (0 bytes) must produce no output and exit 0.

    This catches the missing bounds check: the buggy parser indexes
    data[0] and data[1] unconditionally, panicking on empty input.
    """
    result = _run(b"")

    assert result.returncode == 0, f"crashed on empty input: {result.stderr.decode()}"

    msgs = _parse_output_lines(result.stdout)
    assert len(msgs) == 0


def test_trailing_fragment():
    """A complete frame followed by trailing bytes too short for a full frame.

    The parser must output the one valid message and silently ignore the
    trailing bytes that cannot form another complete frame.
    """
    stream = _frame(b"OK") + b"\xff\xee\xdd"
    result = _run(stream)

    assert result.returncode == 0, f"crashed on trailing fragment: {result.stderr.decode()}"

    msgs = _parse_output_lines(result.stdout)
    assert len(msgs) == 1
    assert msgs[0]["payload_hex"] == b"OK".hex()


def test_zero_length_message():
    """A frame with length=0 is valid and should produce an empty payload."""
    stream = _frame(b"")
    result = _run(stream)

    assert result.returncode == 0

    msgs = _parse_output_lines(result.stdout)
    assert len(msgs) == 1
    assert msgs[0]["index"] == 0
    assert msgs[0]["length"] == 0
    assert msgs[0]["payload_hex"] == ""


def test_large_payload():
    """A single message with a 1000-byte payload must be parsed correctly."""
    payload = bytes(range(256)) * 4  # 1024 bytes, take first 1000
    payload = payload[:1000]
    stream = _frame(payload)
    result = _run(stream)

    assert result.returncode == 0

    msgs = _parse_output_lines(result.stdout)
    assert len(msgs) == 1
    assert msgs[0]["length"] == 1000
    assert msgs[0]["payload_hex"] == payload.hex()


def test_multiple_then_truncated():
    """Two complete frames followed by a truncated third (header present,
    but payload cut short). Must output exactly 2 messages and not crash.

    This exercises both bugs simultaneously: the double-advance would
    mis-position the cursor after the first message, and the missing
    bounds check would panic on the truncated third frame.
    """
    p1 = b"\x01\x02\x03"
    p2 = b"\x04\x05\x06"
    # Third frame header says 10 bytes, but only 2 bytes of payload follow
    truncated_third = struct.pack("<H", 10) + b"\x07\x08"
    stream = _frame(p1) + _frame(p2) + truncated_third
    result = _run(stream)

    assert result.returncode == 0, f"crashed on truncated frame: {result.stderr.decode()}"

    msgs = _parse_output_lines(result.stdout)
    assert len(msgs) == 2, f"expected 2 messages, got {len(msgs)}"

    assert msgs[0]["payload_hex"] == p1.hex()
    assert msgs[1]["payload_hex"] == p2.hex()


def test_two_messages_different_sizes():
    """Two messages with different payload sizes must both parse correctly.

    With the double-advance bug, the cursor over-shoots by 2 bytes after
    the first message, causing the second message's header to be read from
    the wrong position — producing garbled length or a panic.
    """
    p1 = b"\xAA\xBB\xCC"          # 3 bytes
    p2 = b"\xDD\xEE\xFF\x11\x22"  # 5 bytes
    stream = _frame(p1) + _frame(p2)
    result = _run(stream)

    assert result.returncode == 0, f"non-zero exit: {result.stderr.decode()}"

    msgs = _parse_output_lines(result.stdout)
    assert len(msgs) == 2, f"expected 2 messages, got {len(msgs)}"

    assert msgs[0]["payload_hex"] == p1.hex()
    assert msgs[1]["payload_hex"] == p2.hex()


def test_exit_code_success():
    """Well-formed input must always produce exit code 0."""
    stream = _frame(b"test")
    result = _run(stream)
    assert result.returncode == 0
