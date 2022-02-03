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

    re_line = re.compile(
        # 2764 FE0F 200D 1F525 ; fully-qualified # ❤️‍🔥 E13.1 heart on fire
        r"^(?P<codes>[^;]+);\s+(?P<status>[^\s]+)\s+#\s+(?P<chars>[^\s]+)\s+E(?P<version>[^\s]+)\s+(?P<description>.*)$"
    )

    def __str__(self) -> str:
        return f"{''.join(self.chars)} {self.description} ({', '.join(self.codes)})"

    @classmethod
    def from_line(cls, line: str) -> Optional[Emoji]:
        if not (m := cls.re_line.match(line)):
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


class SelectEmojiCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit) -> None:
        if not (window := self.view.window()):
            return

        emojis = get_emojis()
        items = tuple(map(str, emojis))

        def callback(selected: int) -> None:
            if selected >= 0:
                self.view.run_command("insert", {"characters": "".join(emojis[selected].chars)})

        window.show_quick_panel(items, callback)
