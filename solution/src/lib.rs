#[derive(Debug, Clone, PartialEq)]
pub struct Message {
    pub payload: Vec<u8>,
}

/// Parse a packed binary stream of length-prefixed messages.
///
/// Each message is framed as:
///   [ 2-byte little-endian length ][ payload ]
///
/// Messages are packed back-to-back with no padding.
/// Trailing bytes that cannot form a complete frame are silently skipped.
pub fn parse_stream(data: &[u8]) -> Vec<Message> {
    let mut messages = Vec::new();
    let mut offset = 0;

    while offset + 2 <= data.len() {
        // Read the 2-byte little-endian length prefix
        let len = u16::from_le_bytes([
            data[offset],
            data[offset + 1],
        ]) as usize;

        // Advance past the length header
        offset += 2;

        // Check that the full payload is available
        if offset + len > data.len() {
            break;
        }

        // Read the payload
        let payload = data[offset..offset + len].to_vec();

        messages.push(Message { payload });

        // Advance past the payload only
        offset += len;
    }

    messages
}
