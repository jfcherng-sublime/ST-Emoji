from __future__ import annotations

# __future__ must be the first import
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from typing import Optional, Tuple
import re
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
        r"^(?P<codes>[^;]+);\s+"
        + r"(?P<status>[^\s]+)\s+"
        + r"#\s+(?P<chars>[^\s]+)\s+"
        + r"E(?P<version>[^\s]+)\s+"
        + r"(?P<description>.*)$"
    )

    def __hash__(self) -> int:
        return hash(self.codes)

    def __str__(self) -> str:
        return f"{''.join(self.chars)} {self.description} ({', '.join(self.codes)})"

    @classmethod
    def from_line(cls, line: str) -> Optional[Emoji]:
        if not (m := cls._re_line.match(line)):
            return None
        return cls(
            chars=tuple(m.group("chars")),
            codes=tuple(m.group("codes").strip().split(" ")),
            description=m.group("description").strip().title(),
            status=EmojiStatus(m.group("status")),
            version=m.group("version"),
        )


@lru_cache
def get_emojis() -> Tuple[Emoji, ...]:
    data = sublime.load_resource(f"Packages/{PACKAGE_NAME}/data/emoji-test.txt").strip()
    return tuple(filter(None, map(Emoji.from_line, data.splitlines(keepends=False))))


@lru_cache
def convert_emojis_to_quick_panel_items(emojis: Tuple[Emoji, ...]) -> Tuple[sublime.QuickPanelItem, ...]:
    return tuple(
        sublime.QuickPanelItem(
            trigger="".join(emoji.chars) + " " + emoji.description,
            details="",
            annotation=", ".join(emoji.codes),
            kind=(sublime.KIND_ID_AMBIGUOUS, str(len(emoji.chars)), ""),
        )
        for emoji in emojis
    )


class SelectEmojiCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit) -> None:
        if not (window := self.view.window()):
            return

        emojis = get_emojis()
        items = convert_emojis_to_quick_panel_items(emojis)

        def callback(selected: int) -> None:
            if selected >= 0:
                self.view.run_command("insert", {"characters": "".join(emojis[selected].chars)})

        window.show_quick_panel(items, callback)
