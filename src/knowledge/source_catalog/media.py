"""Discover local product images, hash them, and keep mapping metadata."""

from __future__ import annotations

import hashlib
import mimetypes
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.knowledge.catalog_builder import IMAGE_EXTS
from src.knowledge.source_catalog.products import ensure_default_registry, pic_dir_for_product
from src.knowledge.source_catalog.store import load_media_index, save_media_index

STATES = (
    "LOCAL_ONLY",
    "PENDING_UPLOAD",
    "UPLOADING",
    "SYNCED",
    "MODIFIED",
    "SERVER_ONLY",
    "LOCAL_DELETED",
    "UNMAPPED",
    "FAILED",
)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 64), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_local_media(project_root: Path, data_dir: Path, product_id: str) -> dict[str, Any]:
    ensure_default_registry(data_dir, project_root)
    folder = pic_dir_for_product(project_root, product_id, data_dir)
    prev = load_media_index(data_dir, product_id)
    by_id = {str(i.get("media_id")): i for i in prev.get("items") or [] if isinstance(i, dict)}
    by_hash = {str(i.get("hash")): i for i in by_id.values() if i.get("hash")}
    seen: set[str] = set()
    items: list[dict[str, Any]] = []
    if folder and folder.is_dir():
        for path in sorted(folder.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in IMAGE_EXTS:
                continue
            digest = _sha256(path)
            old = by_hash.get(digest) or next(
                (i for i in by_id.values() if i.get("filename") == path.name and i.get("status") != "LOCAL_DELETED"),
                None,
            )
            media_id = str((old or {}).get("media_id") or f"{product_id}-{digest[:12]}")
            seen.add(media_id)
            st = "SYNCED" if (old or {}).get("status") == "SYNCED" and (old or {}).get("hash") == digest else "LOCAL_ONLY"
            if old and old.get("hash") and old.get("hash") != digest and old.get("status") == "SYNCED":
                st = "MODIFIED"
            if old and old.get("status") == "FAILED":
                st = "FAILED"
            mapped = list((old or {}).get("feature_ids") or [])
            if not mapped:
                st = "UNMAPPED" if st in {"LOCAL_ONLY", "UNMAPPED"} else st
            rec = {
                "media_id": media_id,
                "product_id": product_id,
                "filename": path.name,
                "path": str(path),
                "mime_type": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
                "size": path.stat().st_size,
                "hash": digest,
                "created_at": datetime.fromtimestamp(path.stat().st_ctime, tz=timezone.utc).isoformat(),
                "modified_at": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(),
                "catalog_feature_id": mapped[0] if mapped else "",
                "feature_ids": mapped,
                "status": st,
                "server_path": (old or {}).get("server_path") or "",
                "uploaded_at": (old or {}).get("uploaded_at") or "",
                "description": (old or {}).get("description") or "",
                "keywords": (old or {}).get("keywords") or [],
                "classify_confidence": (old or {}).get("classify_confidence"),
                "needs_review": bool((old or {}).get("needs_review", not mapped)),
            }
            items.append(rec)
    for mid, old in by_id.items():
        if mid in seen:
            continue
        if old.get("server_path") or old.get("status") == "SYNCED":
            old = dict(old)
            old["status"] = "LOCAL_DELETED"
            items.append(old)
        elif old.get("status") == "SERVER_ONLY":
            items.append(old)
    save_media_index(data_dir, product_id, {"items": items, "scanned_at": datetime.now(timezone.utc).isoformat()})
    return {"items": items, "count": len(items)}


def pending_uploads(index: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for item in index.get("items") or []:
        if not isinstance(item, dict):
            continue
        if item.get("status") in {"LOCAL_ONLY", "MODIFIED", "PENDING_UPLOAD", "UNMAPPED", "FAILED"}:
            if item.get("status") == "UNMAPPED" and not item.get("hash"):
                continue
            if item.get("status") in {"LOCAL_ONLY", "MODIFIED", "PENDING_UPLOAD", "FAILED", "UNMAPPED"}:
                out.append(item)
    return out
