from __future__ import annotations

from functools import cache

import sublime
import sublime_plugin

from ..constants import DB_REVISION
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
    def run(self, edit: sublime.Edit) -> None:
        if not (window := self.view.window()):
            return

        def callback(selected: int) -> None:
            if selected >= 0:
                self.view.run_command("insert", {"characters": db[selected].char})

        db = get_emoji_db(DB_REVISION)
        window.show_quick_panel(emoji_db_to_quick_panel_items(db), callback)
