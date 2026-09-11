"""Create and restore install-tree backups for safe changes."""

from __future__ import annotations

import json
import logging
import shutil
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path

from src.safety.paths import (
    BACKUPS_DIR,
    BACKUP_EXCLUDE_PREFIXES,
    BACKUP_INCLUDE,
    INSTALL_ROOT,
    LAST_GOOD_META,
    LAST_GOOD_PATH,
)
from src.safety.state import ensure_safety_dirs

log = logging.getLogger("blackfox-bot-safety.backup")


def _should_exclude(member_name: str) -> bool:
    name = member_name.replace("\\", "/").lstrip("./")
    for prefix in BACKUP_EXCLUDE_PREFIXES:
        if name == prefix.rstrip("/") or name.startswith(prefix):
            return True
    return False


def create_backup(*, change_id: str) -> Path:
    """Tar selected install paths into SAFETY backups dir. Returns archive path."""
    ensure_safety_dirs()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = BACKUPS_DIR / f"{stamp}_{change_id}.tar.gz"
    with tarfile.open(out, "w:gz") as tar:
        for rel in BACKUP_INCLUDE:
            src = INSTALL_ROOT / rel
            if not src.exists():
                continue
            tar.add(src, arcname=rel, filter=_tar_filter)
    log.info("Backup created: %s", out)
    return out


def save_last_good(*, reason: str = "healthy") -> Path:
    """Refresh the known-good snapshot used for crash-loop auto-recovery."""
    ensure_safety_dirs()
    tmp = LAST_GOOD_PATH.with_suffix(".tar.gz.tmp")
    if tmp.exists():
        tmp.unlink(missing_ok=True)
    with tarfile.open(tmp, "w:gz") as tar:
        for rel in BACKUP_INCLUDE:
            src = INSTALL_ROOT / rel
            if not src.exists():
                continue
            tar.add(src, arcname=rel, filter=_tar_filter)
    tmp.replace(LAST_GOOD_PATH)
    meta = {
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "reason": reason,
        "path": str(LAST_GOOD_PATH),
    }
    LAST_GOOD_META.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    log.info("last_good snapshot refreshed (%s)", reason)
    return LAST_GOOD_PATH


def restore_last_good() -> Path:
    if not LAST_GOOD_PATH.is_file():
        raise FileNotFoundError("last_good.tar.gz missing")
    restore_backup(LAST_GOOD_PATH)
    return LAST_GOOD_PATH


def _tar_filter(tarinfo: tarfile.TarInfo) -> tarfile.TarInfo | None:
    if _should_exclude(tarinfo.name):
        return None
    return tarinfo


def restore_backup(archive: Path) -> None:
    """Extract backup over INSTALL_ROOT (does not touch data/ or .venv/)."""
    if not archive.is_file():
        raise FileNotFoundError(f"Backup not found: {archive}")
    # Extract to a temp dir then copy allowed members — safer than blind extract.
    tmp = BACKUPS_DIR / f"_restore_{int(time.time())}"
    if tmp.exists():
        shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True, exist_ok=True)
    try:
        with tarfile.open(archive, "r:gz") as tar:
            # Python 3.12+ has filter=; keep compatible extract.
            tar.extractall(tmp)
        for rel in BACKUP_INCLUDE:
            src = tmp / rel
            dst = INSTALL_ROOT / rel
            if not src.exists():
                continue
            if src.is_dir():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        log.info("Restored backup %s into %s", archive, INSTALL_ROOT)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def list_backups(limit: int = 20) -> list[Path]:
    ensure_safety_dirs()
    files = sorted(BACKUPS_DIR.glob("*.tar.gz"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[:limit]
