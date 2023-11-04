#!/usr/bin/env bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

curl \
    -o "${SCRIPT_DIR}/emoji-test.txt" \
    "https://unicode.org/Public/emoji/latest/emoji-test.txt"
