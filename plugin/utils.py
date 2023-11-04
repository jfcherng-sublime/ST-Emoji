from __future__ import annotations

from typing import Literal

from .constants import PACKAGE_NAME


def _pp(level: Literal["DEBUG", "INFO", "WARNING", "ERROR"], msg: str) -> None:
    """Print plugin message."""
    print(f"[{PACKAGE_NAME}][{level}] {msg}")


def pp_debug(msg: str) -> None:
    """Print "[DEBUG]" plugin message."""
    _pp("DEBUG", msg)


def pp_info(msg: str) -> None:
    """Print "[INFO]" plugin message."""
    _pp("INFO", msg)


def pp_warning(msg: str) -> None:
    """Print "[WARNING]" plugin message."""
    _pp("WARNING", msg)


def pp_error(msg: str) -> None:
    """Print "[ERROR]" plugin message."""
    _pp("ERROR", msg)
