# Market Feed Parser. Debug Task

We are working on a team that builds systems for high speed trading. The market feed parser is an important tool that takes raw binary market data and turns it into something useful.

## Binary Protocol

The data we get is a stream of bytes. Each message in this stream has a format:

it starts with 2 bytes that tell us the length of the message and then it has the actual message.

These messages are packed tightly together one after the other with no gaps or extra bytes between them.

Sometimes the stream might end with a bytes that are not enough to make a complete message.

We should just ignore these bytes in the market feed parser.

## The Tool

The market feed parser tool is a program that we can run from the command line.

It lives in /usr//bin/market-feed-parser.

The code for this tool is in the /app/ directory.

It is a Rust project with files like Cargo.toml, src/lib.rs and src/main.rs.

When we run the market feed parser it reads bytes from the input and writes out one line of JSON for each message it parses to the standard output:

```json

{"index":0,"length":5,"payload_hex":"48656c6c6f"}

```

Each line of JSON has a few important pieces of information:

- the index, which is a number that keeps track of how many messages we have seen so far in the market feed parser

- the length, which is how many bytes are in the message

- the payload hex which is the message itself but in a special hex code format.

## The Problem

Users are telling us that the market feed parser is not working correctly.

There are two problems:

1. **Crashes**: Sometimes the parser stops working with an index out of bounds error when it sees streams that're empty or have a few extra bytes at the end.

We want the market feed parser to handle these situations smoothly by stopping and exiting without any errors.

2. **Missing or corrupted messages**: When we have messages packed together the parser sometimes loses some of them. Gets their contents wrong.

## Your Task

1. Look at the Rust code for the market feed parser in /app/src/.

Find out what is causing these two problems in the market feed parser.

2. Fix the parser so it can handle:

- Streams that're empty

- Streams with just one message

- Streams with multiple messages packed together

- Streams that end with a few bytes that are not enough to make a complete message

The market feed parser should just ignore these extra bytes.

3. Rebuild the market feed parser tool.

Install it in the place:

```bash

cd /app

cargo build --release

cp target/release/market-feed-parser /usr/local/bin/market-feed-parser

```

Remember we do not want to change the format of the output.

Each parsed message should still be one line of JSON with index, length and payload hex fields, in the market feed parser.