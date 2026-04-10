# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Sublime Text 4 plugin written in Python 3.14. No external runtime dependencies — only stdlib and the Sublime Text API.

## Commands

```sh
uv sync --all-groups          # install dev deps
make ci-check                 # mypy + ruff lint + ruff format check
make ci-fix                   # ruff lint --fix + ruff format (in-place)
make ci-fix-unsafe            # same as ci-fix but with --unsafe-fixes
```

Run `make ci-check` before committing.

## Code Style

- Line length: 120 characters
- Formatter: ruff (preview mode enabled)
- Type checking: mypy strict + pyright
- `boot.py` is intentionally exempt from E402 (module-level imports not at top)

## Testing

No automated tests. Verification is done by loading the plugin in Sublime Text manually.

## Emoji Data

`data/emoji-test.txt` is the Unicode emoji database. Update it via `data/update_data.sh` — do not edit it manually. The plugin caches the parsed database as a pickle (`.bin`) file in `sublime.cache_path()`, invalidated by MD5 hash + `DB_GENERATOR_HASH`.

## Approach

- Think before acting. Read existing files before writing code.
- Be concise in output but thorough in reasoning.
- Prefer editing over rewriting whole files.
- Do not re-read files you have already read unless the file may have changed.
- Test your code before declaring done.
- No sycophantic openers or closing fluff.
- Keep solutions simple and direct.
- User instructions always override this file.
