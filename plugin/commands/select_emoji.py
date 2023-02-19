from __future__ import annotations

import sublime
import sublime_plugin

from ..emoji import get_emoji_collection


class SelectEmojiCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit) -> None:
        if not (window := self.view.window()):
            return

        def callback(selected: int) -> None:
            if selected >= 0:
                self.view.run_command("insert", {"characters": "".join(emojis[selected].chars)})

        emojis = get_emoji_collection()
        window.show_quick_panel(emojis.to_quick_panel_items(), callback)
