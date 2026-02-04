from __future__ import annotations

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
