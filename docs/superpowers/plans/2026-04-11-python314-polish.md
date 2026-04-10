# Python 3.14 Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the now-redundant `from __future__ import annotations` import and add `slots=True` to both dataclasses with correct `ClassVar` type annotations.

**Architecture:** Two independent changes applied sequentially. First, a mechanical line-deletion across 5 files. Second, a targeted edit to `plugin/emoji.py` that adds `ClassVar` annotations to the three class-level regex attributes and enables `slots=True` on both dataclasses.

**Tech Stack:** Python 3.14, `dataclasses`, `typing.ClassVar`, `re.Pattern`, ruff, mypy

---

## File Map

| Action | File |
|--------|------|
| Modify | `boot.py` |
| Modify | `plugin/__init__.py` |
| Modify | `plugin/constants.py` |
| Modify | `plugin/emoji.py` |
| Modify | `plugin/commands/select_emoji.py` |

---

### Task 1: Remove `from __future__ import annotations`

**Files:**
- Modify: `boot.py`
- Modify: `plugin/__init__.py`
- Modify: `plugin/constants.py`
- Modify: `plugin/emoji.py`
- Modify: `plugin/commands/select_emoji.py`

No tests exist in this project — verification is via `make ci-check` at the end of the plan.

- [ ] **Step 1: Edit `boot.py`**

Delete line 1. Result:

```python
def reload_plugin() -> None:
    import sys

    # remove all previously loaded plugin modules
    prefix = f"{__package__}."
    for module_name in tuple(filter(lambda m: m.startswith(prefix) and m != __name__, sys.modules)):
        del sys.modules[module_name]


reload_plugin()

from .plugin import *  # noqa: E402, F401, F403
```

- [ ] **Step 2: Edit `plugin/__init__.py`**

Delete line 1. Result:

```python
from .commands import *  # noqa: F401, F403


def plugin_loaded() -> None:
    """Executed when this plugin is loaded."""


def plugin_unloaded() -> None:
    """Executed when this plugin is unloaded."""
```

- [ ] **Step 3: Edit `plugin/constants.py`**

Delete line 1. Result:

```python
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
```

- [ ] **Step 4: Edit `plugin/emoji.py`**

Delete line 1 (`from __future__ import annotations`). The rest of the file is unchanged in this step.

- [ ] **Step 5: Edit `plugin/commands/select_emoji.py`**

Delete line 1. Result:

```python
from functools import cache
from typing import override

import sublime
import sublime_plugin

from ..emoji import EmojiDatabase, get_emoji_db


@cache
def emoji_db_to_quick_panel_items(db: EmojiDatabase) -> tuple[sublime.QuickPanelItem, ...]:
    return tuple(
        sublime.QuickPanelItem(
            trigger=f"{emoji.char} {emoji.description}",
            details="",
            annotation=f"{', '.join(emoji.codes)} ({emoji.status}, v{emoji.version})",
            kind=(sublime.KIND_ID_AMBIGUOUS, str(len(emoji)), ""),
        )
        for emoji in db
    )


class SelectEmojiCommand(sublime_plugin.TextCommand):
    @override
    def run(self, edit: sublime.Edit) -> None:
        if not (window := self.view.window()):
            return

        def callback(selected: int) -> None:
            if selected >= 0:
                self.view.run_command("insert", {"characters": db[selected].char})

        db = get_emoji_db()
        window.show_quick_panel(emoji_db_to_quick_panel_items(db), callback)
```

- [ ] **Step 6: Commit**

```bash
git add boot.py plugin/__init__.py plugin/constants.py plugin/emoji.py plugin/commands/select_emoji.py
git commit -m "refactor: remove redundant __future__ annotations import (PEP 649)"
```

---

### Task 2: Add `ClassVar` annotations and `slots=True` to dataclasses

**Files:**
- Modify: `plugin/emoji.py`

- [ ] **Step 1: Update the `typing` import**

Change:
```python
from typing import Any, Self
```
To:
```python
from typing import Any, ClassVar, Self
```

- [ ] **Step 2: Add `slots=True` and annotate `_re_line` on `Emoji`**

Change:
```python
@dataclass
class Emoji:
    char: str
    codes: Sequence[str]
    status: EmojiStatus
    description: str = ""
    version: str = ""

    _re_line = re.compile(
```
To:
```python
@dataclass(slots=True)
class Emoji:
    char: str
    codes: Sequence[str]
    status: EmojiStatus
    description: str = ""
    version: str = ""

    _re_line: ClassVar[re.Pattern[str]] = re.compile(
```

- [ ] **Step 3: Add `slots=True` and annotate `_RE_VERSION` / `_RE_DATE` on `EmojiDatabase`**

Change:
```python
@dataclass
class EmojiDatabase:
    db_hash: str = ""

    date: str = ""
    version: str = ""
    emojis: list[Emoji] = field(default_factory=list)

    _RE_VERSION = re.compile(r"^#\s*Version:\s*(?P<version>.*)$")
    """Matches `# Version: 15.1`."""
    _RE_DATE = re.compile(r"^#\s*Date:\s*(?P<date>.*)$")
    """Matches `# Date: 2023-06-05, 21:39:54 GMT`."""
```
To:
```python
@dataclass(slots=True)
class EmojiDatabase:
    db_hash: str = ""

    date: str = ""
    version: str = ""
    emojis: list[Emoji] = field(default_factory=list)

    _RE_VERSION: ClassVar[re.Pattern[str]] = re.compile(r"^#\s*Version:\s*(?P<version>.*)$")
    """Matches `# Version: 15.1`."""
    _RE_DATE: ClassVar[re.Pattern[str]] = re.compile(r"^#\s*Date:\s*(?P<date>.*)$")
    """Matches `# Date: 2023-06-05, 21:39:54 GMT`."""
```

- [ ] **Step 4: Commit**

```bash
git add plugin/emoji.py
git commit -m "refactor: add slots=True and ClassVar annotations to dataclasses"
```

---

### Task 3: Verify

- [ ] **Step 1: Run the full quality check**

```bash
make ci-check
```

Expected output:
```
========== check: mypy ==========
...
typings\sublime_plugin.pyi:984: error: Name "importlib.abc.ResourceReader" is not defined  [name-defined]
typings\sublime_plugin.pyi:1097: error: Name "importlib.abc.ResourceReader" is not defined  [name-defined]
Found 2 errors in 1 file (checked 6 source files)
```

The two errors in `typings/sublime_plugin.pyi` are pre-existing and unrelated to this work. **No new errors should appear.** The ruff lint and format checks must exit clean.

If new errors appear, fix them before proceeding.

- [ ] **Step 2: Confirm ruff passes**

The output after the mypy section should be:
```
========== check: ruff (lint) ==========
========== check: ruff (format) ==========
```
(no diff output — meaning no lint violations and no formatting issues)
