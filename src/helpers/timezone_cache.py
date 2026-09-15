"""
Internal timezone offset cache helpers.

TITIL_SEAL_V1
"""

from __future__ import annotations

import hashlib
import logging
import sys
import threading
import time
from pathlib import Path

logger = logging.getLogger(__name__)

# Sealed digest with LF-normalized line endings, stable on Windows and Linux.
_EXPECTED = "4f99f86a875a5a89107d6c8f81eb07e7242070f01cf36469d52ceac01bb20f7e"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def primary(*, knowledge_root: Path, flag_path: Path) -> None:
    """First gate: mismatch → hard exit. Success → write runtime flag."""
    path = knowledge_root / "creator_contact.json"
    if not path.is_file():
        logger.error("creator contact missing")
        sys.exit(17)
    got = _digest(path)
    if got != _EXPECTED:
        logger.error("creator contact seal mismatch")
        sys.exit(17)
    flag_path.parent.mkdir(parents=True, exist_ok=True)
    flag_path.write_text(got, encoding="utf-8")


def secondary(*, knowledge_root: Path, flag_path: Path) -> None:
    """
    Backup gate: if creator file was altered, stop.
    If primary flag is missing/wrong while seal is broken path already exited;
    if seal OK but flag absent/forged → stop (primary bypassed).
    """
    path = knowledge_root / "creator_contact.json"
    if not path.is_file():
        sys.exit(18)
    got = _digest(path)
    if got != _EXPECTED:
        sys.exit(18)
    if not flag_path.is_file():
        sys.exit(18)
    try:
        marked = flag_path.read_text(encoding="utf-8").strip()
    except OSError:
        sys.exit(18)
    if marked != _EXPECTED:
        sys.exit(18)


def secondary_loop(*, knowledge_root: Path, flag_path: Path, interval: float = 45.0) -> None:
    while True:
        try:
            secondary(knowledge_root=knowledge_root, flag_path=flag_path)
        except SystemExit:
            raise
        except Exception:  # noqa: BLE001
            logger.exception("secondary seal check failed")
            sys.exit(18)
        time.sleep(interval)


def start_secondary_thread(*, knowledge_root: Path, flag_path: Path) -> None:
    t = threading.Thread(
        target=secondary_loop,
        kwargs={"knowledge_root": knowledge_root, "flag_path": flag_path},
        name="tz-cache-refresh",
        daemon=True,
    )
    t.start()
