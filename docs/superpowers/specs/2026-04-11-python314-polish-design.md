# Python 3.14 Polish — Design Spec

**Date:** 2026-04-11
**Scope:** Structural and type-system modernisation only. No idiom/style changes, no frozen dataclasses.

---

## Goal

Polish the codebase to use Python 3.14 language features:
1. Remove the now-redundant `from __future__ import annotations` import (PEP 649)
2. Add `slots=True` to both dataclasses with correct `ClassVar` annotations

---

## Change 1 — Remove `from __future__ import annotations`

**Why:** Python 3.14 implements PEP 649 (lazy annotation evaluation) as the default. Annotations are no longer eagerly evaluated, so forward references work without stringification. The `from __future__ import annotations` import (PEP 563) is now a no-op.

**Files affected:**
- `boot.py`
- `plugin/__init__.py`
- `plugin/constants.py`
- `plugin/emoji.py`
- `plugin/commands/select_emoji.py`

**Action:** Delete the `from __future__ import annotations` line from each file.

**Risk:** None. The codebase has no `get_type_hints()` calls and no runtime annotation inspection that would depend on PEP 563's string-based representation.

---

## Change 2 — `@dataclass(slots=True)` + `ClassVar` annotations

**Why:** `slots=True` generates `__slots__` automatically, restricting instances to declared fields. Benefits: lower per-instance memory usage, faster attribute access, and earlier detection of typo'd attribute names at the class level.

**File:** `plugin/emoji.py`

### `Emoji` dataclass

- Add `slots=True` to `@dataclass`
- Annotate `_re_line` as `ClassVar[re.Pattern[str]]`

Before:
```python
@dataclass
class Emoji:
    ...
    _re_line = re.compile(...)
```

After:
```python
@dataclass(slots=True)
class Emoji:
    ...
    _re_line: ClassVar[re.Pattern[str]] = re.compile(...)
```

### `EmojiDatabase` dataclass

- Add `slots=True` to `@dataclass`
- Annotate `_RE_VERSION` and `_RE_DATE` as `ClassVar[re.Pattern[str]]`

Before:
```python
@dataclass
class EmojiDatabase:
    ...
    _RE_VERSION = re.compile(...)
    _RE_DATE = re.compile(...)
```

After:
```python
@dataclass(slots=True)
class EmojiDatabase:
    ...
    _RE_VERSION: ClassVar[re.Pattern[str]] = re.compile(...)
    _RE_DATE: ClassVar[re.Pattern[str]] = re.compile(...)
```

**Import addition:** Add `ClassVar` to the `from typing import` line in `plugin/emoji.py`.

**Compatibility notes:**
- `asdict()` serialisation is unaffected — it only reflects instance fields.
- The post-construction mutation `db.db_hash = db_hash` continues to work: `db_hash` is a declared instance field and is included in `__slots__`.
- `__hash__` implementations are unaffected.

---

## Verification

Run `make ci-check` after all changes. Expected: mypy and ruff both pass with no errors in plugin source files.

(The two pre-existing mypy errors in `typings/sublime_plugin.pyi` — `importlib.abc.ResourceReader` — are unrelated and pre-date this work.)
