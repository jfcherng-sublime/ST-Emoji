from __future__ import annotations

import pickle
import re
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from functools import cache
from pathlib import Path
from typing import Any, Self

import sublime

from .constants import DB_CACHE_DIR, DB_FILE_IN_PACKAGE, DB_FILE_MD5_IN_PACKAGE, DB_GENERATOR_HASH
from .utils import pp_error, pp_info


@cache
def get_emoji_db() -> EmojiDatabase:
    def _get_db_hash() -> str:
        try:
            pp_info(f"Loading database cache hash file: {DB_FILE_MD5_IN_PACKAGE}")
            db_md5 = sublime.load_resource(DB_FILE_MD5_IN_PACKAGE).strip()
            return f"{db_md5}@{DB_GENERATOR_HASH}"
        except Exception as e:
            pp_error(f"Failed to load database hash file: {e}")
            raise

    def _create_cache() -> EmojiDatabase:
        pp_info(f"Creating database cache: {cached_db_file}")
        db_content = sublime.load_resource(DB_FILE_IN_PACKAGE)
        db = EmojiDatabase.from_string(db_content)
        db.db_hash = db_hash
        db.to_pickle_file(cached_db_file)
        return db

    def _load_cache() -> EmojiDatabase | None:
        try:
            pp_info(f"Loading database cache file: {cached_db_file}")
            return EmojiDatabase.from_pickle_file(cached_db_file)
        except Exception as e:
            pp_error(f"Failed to load database cache file: {e}")
        return None

    db_hash = _get_db_hash()
    cached_db_file = DB_CACHE_DIR / f"{db_hash}.bin"
    return _load_cache() or _create_cache()


class EmojiStatus(StrEnum):
    COMPONENT = "component"
    FULLY_QUALIFIED = "fully-qualified"
    MINIMALLY_QUALIFIED = "minimally-qualified"
    UNQUALIFIED = "unqualified"
    # -----------------
    UNKNOWN = "unknown"


@dataclass
class Emoji:
    char: str
    codes: Sequence[str]
    status: EmojiStatus
    description: str = ""
    version: str = ""

    _re_line = re.compile(
        # 2764 FE0F 200D 1F525 ; fully-qualified # ❤️‍🔥 E13.1 heart on fire
        r"^(?!#)"  # early fail on comments
        + r"(?P<codes>[^;]+)"
        + r";\s+(?P<status>[^\s]+)\s+"
        + r"#\s*(?P<char>[^\s]+)\s+"
        + r"E(?P<version>[^\s]+)\s+"
        + r"(?P<description>.*)$"
    )

    def __getitem__(self, index: int) -> str:
        return self.char[index]

    def __hash__(self) -> int:
        return hash(self.char)

    def __len__(self) -> int:
        return len(self.codes)

    def __str__(self) -> str:
        return (
            " ".join(self.codes)
            + f" ; {self.status.value}"
            + f" # {self.char}"
            + f" E{self.version}"
            + f" {self.description}"
        )

    @classmethod
    def from_dict(cls, db: dict[str, Any]) -> Self:
        return cls(
            char=db["char"],  # required
            codes=db.get("codes") or cls.str_to_code_points(db["char"]),
            description=db.get("description") or "",
            status=EmojiStatus(db.get("status") or EmojiStatus.UNKNOWN),
            version=db.get("version") or "",
        )

    @classmethod
    def from_line(cls, line: str) -> Self | None:
        if m := cls._re_line.fullmatch(line):
            return cls(
                char=m.group("char").strip(),
                codes=m.group("codes").strip().split(" "),
                description=m.group("description").strip().title(),
                status=EmojiStatus(m.group("status")),
                version=m.group("version"),
            )
        return None

    @staticmethod
    def str_to_code_points(s: str) -> list[str]:
        """
        Converts a string to a list of code points.

        E.g., `"👂🏻"` becomes `["1F442", "1F3FB"]`.
        """
        return [f"{ord(c):X}" for c in s]


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

    def __getitem__(self, index: int) -> Emoji:
        return self.emojis[index]

    def __hash__(self) -> int:
        return hash((self.db_hash, self.date, self.version))

    def __iter__(self) -> Iterator[Emoji]:
        return iter(self.emojis)

    def __len__(self) -> int:
        return len(self.emojis)

    def __str__(self) -> str:
        """Returns a string like "emoji-test.txt"."""
        data = "\n".join(map(str, self.emojis))
        return f"""
# DB Revision: {self.db_hash}
# Date: {self.date}
# Version: {self.version}
{data}
# EOF
"""

    @classmethod
    def from_dict(cls, db: dict[str, Any]) -> Self:
        return cls(
            date=db.get("date", ""),
            version=db.get("version", ""),
            emojis=list(map(Emoji.from_dict, db.get("emojis", []))),
        )

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        collection = cls()
        for line in lines:
            if emoji := Emoji.from_line(line):
                collection.emojis.append(emoji)
                continue
            if m := cls._RE_VERSION.fullmatch(line):
                collection.version = m.group("version").strip()
                continue
            if m := cls._RE_DATE.fullmatch(line):
                collection.date = m.group("date").strip()
                continue
        return collection

    @classmethod
    def from_pickle_file(cls, pickle_file: str | Path) -> Self:
        with open(pickle_file, "rb") as f:
            return cls.from_dict(pickle.load(f))

    @classmethod
    def from_string(cls, content: str) -> Self:
        return cls.from_lines(content.splitlines())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_pickle_file(self, pickle_file: str | Path) -> None:
        pickle_file = Path(pickle_file)
        pickle_file.parent.mkdir(parents=True, exist_ok=True)
        pickle_file.write_bytes(pickle.dumps(self.to_dict()))
