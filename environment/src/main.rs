use std::io::{self, Read};

fn main() {
    let mut data = Vec::new();
    io::stdin().read_to_end(&mut data).expect("failed to read stdin");

    let messages = market_feed_parser::parse_stream(&data);

    for (i, msg) in messages.iter().enumerate() {
        let hex: String = msg.payload.iter().map(|b| format!("{:02x}", b)).collect();
        println!(
            "{{\"index\":{},\"length\":{},\"payload_hex\":\"{}\"}}",
            i,
            msg.payload.len(),
            hex
        );
    }
}
