from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from typing import Iterable, Iterator, Optional, Tuple

import sublime
import sublime_plugin

PACKAGE_NAME = __package__.partition(".")[0]


class EmojiStatus(Enum):
    COMPONENT = "component"
    FULLY = "fully-qualified"
    MINIMALLY = "minimally-qualified"
    UN = "unqualified"


@dataclass
class Emoji:
    chars: Tuple[str, ...]
    codes: Tuple[str, ...]
    description: str
    status: EmojiStatus
    version: str

    _re_line = re.compile(
        # 2764 FE0F 200D 1F525 ; fully-qualified # ❤️‍🔥 E13.1 heart on fire
        r"^(?!#)"  # early fail on comments
        + r"(?P<codes>[^;]+);\s+"
        + r"(?P<status>[^\s]+)\s+"
        + r"#\s*"
        + r"(?P<chars>[^\s]+)\s+"
        + r"E(?P<version>[^\s]+)\s+"
        + r"(?P<description>.*)"
        + r"$"
    )

    def __hash__(self) -> int:
        return hash(self.codes)

    def __str__(self) -> str:
        return f"{''.join(self.chars)} {self.description} ({', '.join(self.codes)})"

    @classmethod
    def from_line(cls, line: str) -> Optional[Emoji]:
        if not (m := cls._re_line.fullmatch(line)):
            return None
        return cls(
            chars=tuple(m.group("chars")),
            codes=tuple(m.group("codes").strip().split(" ")),
            description=m.group("description").strip().title(),
            status=EmojiStatus(m.group("status")),
            version=m.group("version"),
        )


class EmojiCollection:
    def __init__(self, emojis: Optional[Iterable[Emoji]] = None) -> None:
        self._emojis = list(emojis or [])

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
    @lru_cache
    def from_resource(cls, resource_path: str) -> EmojiCollection:
        return cls.from_lines(sublime.load_resource(resource_path).splitlines())

    def to_quick_panel_items(self) -> Tuple[sublime.QuickPanelItem, ...]:
        return tuple(
            sublime.QuickPanelItem(
                trigger="".join(emoji.chars) + " " + emoji.description,
                details="",
                annotation=", ".join(emoji.codes),
                kind=(sublime.KIND_ID_AMBIGUOUS, str(len(emoji.chars)), ""),
            )
            for emoji in self
        )


class SelectEmojiCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit) -> None:
        if not (window := self.view.window()):
            return

        def callback(selected: int) -> None:
            if selected >= 0:
                self.view.run_command("insert", {"characters": "".join(emojis[selected].chars)})

        emojis = EmojiCollection.from_resource(f"Packages/{PACKAGE_NAME}/data/emoji-test.txt")
        window.show_quick_panel(emojis.to_quick_panel_items(), callback)
