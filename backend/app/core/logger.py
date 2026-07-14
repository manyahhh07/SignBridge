"""
Application-wide logger setup.

Import `get_logger(__name__)` in any module instead of configuring
logging ad hoc, so log format/level stays consistent across the app.
"""

import logging
import sys

from app.core.config import settings

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _configure_root_logger() -> None:
    level = logging.DEBUG if settings.debug else logging.INFO

    root = logging.getLogger()
    root.setLevel(level)

    # Avoid duplicate handlers if this module is imported more than once
    if root.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
    root.addHandler(handler)


_configure_root_logger()


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)