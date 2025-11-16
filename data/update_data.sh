#!/usr/bin/env bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

pushd "${SCRIPT_DIR}" || exit

curl \
    -o "emoji-test.txt" \
    "https://unicode.org/Public/emoji/latest/emoji-test.txt"

# culculate file md5, only the md5 part
md5sum "emoji-test.txt" | cut -d ' ' -f 1 >"emoji-test.txt.md5"

popd || exit
