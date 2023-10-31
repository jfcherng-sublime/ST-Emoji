from __future__ import annotations

from pathlib import Path

import sublime

PACKAGE_NAME = __package__.partition(".")[0]

DB_FILE_IN_PACKAGE = f"Packages/{PACKAGE_NAME}/data/emoji-test.txt"
DB_FILE_CACHED = Path(sublime.cache_path()) / f"{PACKAGE_NAME}/db.json"
DB_GENERATOR_REVISION = 1
