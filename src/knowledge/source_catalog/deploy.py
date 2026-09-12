"""Copy catalog/media to a deploy root. Never reports success without checksum match."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from src.knowledge.source_catalog.store import append_history, load_media_index, save_media_index
from src.knowledge.source_catalog.versions import active_pointer_path, versions_dir


def _file_sha(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def local_deploy_root() -> Path | None:
    raw = (os.getenv("CATALOG_DEPLOY_ROOT") or "").strip()
    return Path(raw) if raw else None


def ssh_configured() -> bool:
    return bool((os.getenv("BOT_SSH_HOST") or "").strip() and (os.getenv("BOT_SSH_USER") or "").strip())


def deploy_catalog_local(knowledge_root: Path, product_id: str, version: int, dest_root: Path) -> dict[str, Any]:
    src = versions_dir(knowledge_root, product_id) / f"v{version}" / "catalog.json"
    if not src.is_file():
        return {"ok": False, "error": "local version missing"}
    expected = _file_sha(src)
    incoming = dest_root / "knowledge" / "source_catalog" / "versions" / product_id / f"v{version}.tmp"
    final = dest_root / "knowledge" / "source_catalog" / "versions" / product_id / f"v{version}"
    if incoming.exists():
        shutil.rmtree(incoming, ignore_errors=True)
    incoming.mkdir(parents=True)
    target = incoming / "catalog.json"
    shutil.copy2(src, target)
    got = _file_sha(target)
    if got != expected:
        shutil.rmtree(incoming, ignore_errors=True)
        return {"ok": False, "error": "checksum mismatch", "expected": expected, "got": got}
    if final.exists():
        shutil.rmtree(final, ignore_errors=True)
    incoming.replace(final)
    pointer_src = active_pointer_path(knowledge_root, product_id)
    pointer_dst = dest_root / "knowledge" / "source_catalog" / "versions" / product_id / "active.json"
    pointer_dst.parent.mkdir(parents=True, exist_ok=True)
    if pointer_src.is_file():
        tmp = pointer_dst.with_suffix(".json.tmp")
        shutil.copy2(pointer_src, tmp)
        tmp.replace(pointer_dst)
    return {"ok": True, "checksum": expected, "dest": str(final)}


def upload_media_files(
    *,
    data_dir: Path,
    product_id: str,
    dest_media: Path,
    only_ids: list[str] | None = None,
) -> dict[str, Any]:
    index = load_media_index(data_dir, product_id)
    uploaded = []
    failed = []
    dest_media.mkdir(parents=True, exist_ok=True)
    for item in index.get("items") or []:
        if not isinstance(item, dict):
            continue
        mid = str(item.get("media_id") or "")
        if only_ids is not None and mid not in only_ids:
            continue
        if item.get("status") not in {"LOCAL_ONLY", "MODIFIED", "PENDING_UPLOAD", "FAILED", "UNMAPPED", "UPLOADING"}:
            continue
        src = Path(str(item.get("path") or ""))
        if not src.is_file():
            failed.append({"media_id": mid, "error": "local file missing"})
            item["status"] = "FAILED"
            continue
        item["status"] = "UPLOADING"
        dest = dest_media / f"{mid}{src.suffix.lower()}"
        shutil.copy2(src, dest)
        got = _file_sha(dest)
        if got != item.get("hash"):
            item["status"] = "FAILED"
            failed.append({"media_id": mid, "error": "checksum mismatch"})
            continue
        item["status"] = "SYNCED"
        item["server_path"] = str(dest)
        item["uploaded_at"] = dest.stat().st_mtime
        uploaded.append(mid)
    save_media_index(data_dir, product_id, index)
    append_history(
        data_dir,
        product_id,
        {
            "action": "media_upload",
            "result": "ok" if not failed else "partial",
            "filename": [
                str(x.get("filename") or "")
                for x in (index.get("items") or [])
                if isinstance(x, dict) and str(x.get("media_id") or "") in uploaded
            ],
            "object": uploaded,
            "source_section": "media",
            "server": str(dest_media),
        },
    )
    return {"ok": not failed, "uploaded": uploaded, "failed": failed}


def try_remote_scp(local_path: Path, remote_rel: str) -> dict[str, Any]:
    host = (os.getenv("BOT_SSH_HOST") or "").strip()
    user = (os.getenv("BOT_SSH_USER") or "").strip()
    remote_root = (os.getenv("BOT_REMOTE_ROOT") or "/opt/Smart Support Bot").strip()
    if not host or not user:
        return {"ok": False, "error": "BOT_SSH_HOST/USER not configured"}
    remote = f"{user}@{host}:{remote_root.rstrip('/')}/{remote_rel.lstrip('/')}"
    try:
        proc = subprocess.run(
            ["scp", "-q", str(local_path), remote],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "error": str(exc)}
    if proc.returncode != 0:
        return {"ok": False, "error": (proc.stderr or proc.stdout or "scp failed")[:500]}
    return {"ok": True, "remote": remote}
