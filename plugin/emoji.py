from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from typing import Iterable, Iterator

import sublime

from .constants import DB_FILE


@lru_cache
def get_emoji_collection() -> EmojiCollection:
    return EmojiCollection.from_resource(DB_FILE)


class EmojiStatus(Enum):
    COMPONENT = "component"
    FULLY_QUALIFIED = "fully-qualified"
    MINIMALLY_QUALIFIED = "minimally-qualified"
    UNQUALIFIED = "unqualified"


@dataclass
class Emoji:
    chars: tuple[str, ...]
    codes: tuple[str, ...]
    status: EmojiStatus
    description: str = ""
    version: str = ""

    _re_line = re.compile(
        # 2764 FE0F 200D 1F525 ; fully-qualified # ❤️‍🔥 E13.1 heart on fire
        r"^(?!#)"  # early fail on comments
        + r"(?P<codes>[^;]+)"
        + r";\s+(?P<status>[^\s]+)\s+"
        + r"#\s*(?P<chars>[^\s]+)\s+"
        + r"E(?P<version>[^\s]+)\s+"
        + r"(?P<description>.*)$"
    )

    def __hash__(self) -> int:
        return hash(self.codes)

    def __str__(self) -> str:
        return (
            " ".join(self.codes)
            + f" ; {self.status.value}"
            + f" # {''.join(self.chars)}"
            + f" E{self.version}"
            + f" {self.description}"
        )

    @classmethod
    def from_line(cls, line: str) -> Emoji | None:
        if m := cls._re_line.fullmatch(line):
            return cls(
                chars=tuple(m.group("chars")),
                codes=tuple(m.group("codes").strip().split(" ")),
                description=m.group("description").strip().title(),
                status=EmojiStatus(m.group("status")),
                version=m.group("version"),
            )
        return None


class EmojiCollection:
    def __init__(self, emojis: Iterable[Emoji] | None = None) -> None:
        self._emojis = list(emojis or [])

    def __str__(self) -> str:
        return "\n".join(map(str, self))

    def __iter__(self) -> Iterator[Emoji]:
        return iter(self._emojis)

    def __len__(self) -> int:
        return len(self._emojis)

    def __getitem__(self, index: int) -> Emoji:
        return self._emojis[index]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> EmojiCollection:
        return cls(filter(None, map(Emoji.from_line, lines)))

    @classmethod
    def from_resource(cls, resource_path: str) -> EmojiCollection:
        return cls.from_lines(sublime.load_resource(resource_path).splitlines())

    def to_quick_panel_items(self) -> tuple[sublime.QuickPanelItem, ...]:
        return tuple(
            sublime.QuickPanelItem(
                trigger="".join(emoji.chars) + " " + emoji.description,
                details="",
                annotation=", ".join(emoji.codes) + f" - E{emoji.version}",
                kind=(sublime.KIND_ID_AMBIGUOUS, str(len(emoji.chars)), ""),
            )
            for emoji in self
        )
