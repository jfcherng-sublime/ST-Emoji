from __future__ import annotations

from pathlib import Path

import sublime

assert __package__

PACKAGE_NAME = __package__.partition(".")[0]

DB_CACHE_DIR = Path(sublime.cache_path()) / PACKAGE_NAME

DB_DATA_DIR = f"Packages/{PACKAGE_NAME}/data"
DB_FILE_IN_PACKAGE = f"{DB_DATA_DIR}/emoji-test.txt"
DB_FILE_MD5_IN_PACKAGE = f"{DB_DATA_DIR}/emoji-test.txt.md5"

DB_GENERATOR_HASH = "v0"
"""Change this value to invalidate existing cache files when the database generation logic changes."""
