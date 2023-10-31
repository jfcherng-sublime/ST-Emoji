from __future__ import annotations

from typing import Literal

from .constants import PACKAGE_NAME


def pp(level: Literal["DEBUG", "INFO", "WARNING", "ERROR"], msg: str) -> None:
    """Print plugin message."""
    print(f"[{PACKAGE_NAME}][{level}] {msg}")
