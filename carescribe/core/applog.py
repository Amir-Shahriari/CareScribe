"""
File logging — the only way to see inside the packaged app.

The frozen build is windowed: no console, no stdout, no traceback on screen. If
something stalls, this file is the entire evidence trail, so it is always on and
always written to the per-user app-data directory rather than beside the
executable (which may not be writable).

**No PHI is logged.** Document *lengths* and elapsed times, never content, never
an identifier, never a placeholder mapping. A log a clinician might email to
someone for help must be safe to email.
"""

from __future__ import annotations

import logging
import logging.handlers
import time
from contextlib import contextmanager
from pathlib import Path

from . import desktop

LOGGER_NAME = "carescribe"
MAX_BYTES = 2_000_000
BACKUPS = 3

_configured = False


def log_path() -> Path:
    return desktop.app_data_dir() / "logs" / "carescribe.log"


def get_logger() -> logging.Logger:
    """The shared logger, configured on first use."""
    global _configured
    logger = logging.getLogger(LOGGER_NAME)
    if _configured:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False
    try:
        path = log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.handlers.RotatingFileHandler(
            path, maxBytes=MAX_BYTES, backupCount=BACKUPS, encoding="utf-8"
        )
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)-7s %(message)s")
        )
        logger.addHandler(handler)
    except OSError:
        # An unwritable log directory must not stop the app.
        logger.addHandler(logging.NullHandler())
    _configured = True
    return logger


def log(message: str, *args) -> None:
    get_logger().info(message, *args)


def warn(message: str, *args) -> None:
    get_logger().warning(message, *args)


def exception(message: str, *args) -> None:
    """Log with the full traceback — the packaged app has nowhere else to put it."""
    get_logger().exception(message, *args)


@contextmanager
def timed(label: str, **fields):
    """Log the start and end of an operation with its elapsed time.

    ``fields`` are appended as ``key=value``; pass sizes and counts, never text.
    """
    extra = " ".join(f"{k}={v}" for k, v in fields.items())
    log("%s: start %s", label, extra)
    started = time.monotonic()
    try:
        yield
    except Exception:
        exception("%s: FAILED after %.1fs %s", label, time.monotonic() - started, extra)
        raise
    log("%s: done in %.1fs %s", label, time.monotonic() - started, extra)


__all__ = ["exception", "get_logger", "log", "log_path", "timed", "warn"]
