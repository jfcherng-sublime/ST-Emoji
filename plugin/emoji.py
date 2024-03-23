from __future__ import annotations

import pickle
import re
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import asdict, dataclass, field
from functools import lru_cache
from typing import Any

import sublime

from .constants import DB_FILE_CACHED, DB_FILE_IN_PACKAGE, DB_REVISION
from .data_types import StrEnum
from .utils import pp_error, pp_info, pp_warning


@lru_cache
def get_emoji_db(db_revision: int) -> EmojiDatabase:
    def _create_cache() -> EmojiDatabase:
        pp_info(f"Create database cache: {DB_FILE_CACHED}")
        db_content = sublime.load_resource(DB_FILE_IN_PACKAGE)
        db = EmojiDatabase.from_content(db_content)
        DB_FILE_CACHED.parent.mkdir(parents=True, exist_ok=True)
        DB_FILE_CACHED.write_bytes(db.to_pickle())
        return db

    def _load_cache() -> EmojiDatabase | None:
        try:
            db_dict: dict[str, Any] = pickle.loads(DB_FILE_CACHED.read_bytes())
            db = EmojiDatabase.from_dict(db_dict)
            if db.db_revision == db_revision:
                pp_info(f"Load database cache: {DB_FILE_CACHED}")
                return db
            pp_warning("Mismatched database cache revision...")
        except Exception as e:
            pp_error(f"Failed to load database cache: {e}")
        return None

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
    def from_dict(cls, db: dict[str, Any]) -> Emoji:
        return cls(
            char=db["char"],  # required
            codes=db.get("codes") or cls.str_to_code_points(db["char"]),
            description=db.get("description") or "",
            status=EmojiStatus(db.get("status") or EmojiStatus.UNKNOWN),
            version=db.get("version") or "",
        )

    @classmethod
    def from_line(cls, line: str) -> Emoji | None:
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
    db_revision: int = 0
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
        return hash((self.db_revision, self.date, self.version))

    def __iter__(self) -> Iterator[Emoji]:
        return iter(self.emojis)

    def __len__(self) -> int:
        return len(self.emojis)

    def __str__(self) -> str:
        """Returns a string like "emoji-test.txt"."""
        data = "\n".join(map(str, self.emojis))
        return f"""
# DB Revision: {self.db_revision}
# Date: {self.date}
# Version: {self.version}
{data}
# EOF
"""

    @classmethod
    def from_content(cls, content: str) -> EmojiDatabase:
        return cls.from_lines(content.splitlines())

    @classmethod
    def from_dict(cls, db: dict[str, Any]) -> EmojiDatabase:
        return cls(
            db_revision=db.get("db_revision", DB_REVISION),
            date=db.get("date", ""),
            version=db.get("version", ""),
            emojis=list(map(Emoji.from_dict, db.get("emojis", []))),
        )

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> EmojiDatabase:
        collection = cls(db_revision=DB_REVISION)
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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_pickle(self) -> bytes:
        return pickle.dumps(self.to_dict(), protocol=pickle.HIGHEST_PROTOCOL)
