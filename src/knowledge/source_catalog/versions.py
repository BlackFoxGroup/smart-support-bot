"""Catalog versions: generate → validate → activate. Never activate a failed draft."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.knowledge.source_catalog.pipeline import load_matrix, run_sync
from src.knowledge.source_catalog.store import append_history, load_state, save_state

CATALOG_STATES = (
    "DRAFT",
    "VALIDATING",
    "VALID",
    "UPLOADING",
    "ACTIVE",
    "FAILED",
    "ROLLED_BACK",
)


def versions_dir(knowledge_root: Path, product_id: str) -> Path:
    p = knowledge_root / "source_catalog" / "versions" / product_id
    p.mkdir(parents=True, exist_ok=True)
    return p


def active_pointer_path(knowledge_root: Path, product_id: str) -> Path:
    return knowledge_root / "source_catalog" / "versions" / product_id / "active.json"


def load_active(knowledge_root: Path, product_id: str) -> dict[str, Any] | None:
    path = active_pointer_path(knowledge_root, product_id)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def next_version_number(knowledge_root: Path, product_id: str) -> int:
    folder = versions_dir(knowledge_root, product_id)
    nums = []
    for child in folder.iterdir():
        if child.is_dir() and child.name.startswith("v"):
            try:
                nums.append(int(child.name[1:]))
            except ValueError:
                continue
    return (max(nums) + 1) if nums else 1


def generate_version(
    *,
    source_root: Path,
    knowledge_root: Path,
    data_dir: Path,
    product_id: str,
    force: bool = False,
) -> dict[str, Any]:
    state = load_state(data_dir, product_id)
    state["catalog_status"] = "DRAFT"
    save_state(data_dir, product_id, state)
    previous = load_matrix(knowledge_root)
    if product_id == "vpn-installer":
        payload = run_sync(source_root, knowledge_root, data_dir, force=force)
    else:
        from src.knowledge.product_catalogs import product_json_path

        path = product_json_path(knowledge_root, product_id)
        if not path.is_file():
            return {"ok": False, "error": "product catalog json missing", "status": "FAILED"}
        payload = {
            "schema_version": "1.0",
            "product_id": product_id,
            "source_revision": str(path.stat().st_mtime_ns),
            "features": json.loads(path.read_text(encoding="utf-8")).get("features") or [],
            "validation": {"missing": [], "extra": []},
            "stats": {"features": len(json.loads(path.read_text(encoding="utf-8")).get("features") or [])},
        }
    active = load_active(knowledge_root, product_id)
    if (
        not force
        and active
        and str(active.get("source_hash") or "") == str(payload.get("source_revision") or "")
    ):
        return {
            "ok": True,
            "unchanged": True,
            "version": active.get("catalog_version"),
            "status": "ACTIVE",
        }
    val = payload.get("validation") or {}
    state["catalog_status"] = "VALIDATING"
    save_state(data_dir, product_id, state)
    missing = val.get("missing") or []
    if missing:
        state["catalog_status"] = "FAILED"
        save_state(data_dir, product_id, state)
        append_history(
            data_dir,
            product_id,
            {"action": "validate", "result": "FAILED", "error": "missing features", "source_section": "catalog"},
        )
        return {"ok": False, "error": "validation failed", "missing": missing, "status": "FAILED"}
    n = next_version_number(knowledge_root, product_id)
    dest = versions_dir(knowledge_root, product_id) / f"v{n}"
    incoming = versions_dir(knowledge_root, product_id) / f"v{n}.tmp"
    if incoming.exists():
        shutil.rmtree(incoming, ignore_errors=True)
    incoming.mkdir(parents=True)
    body = {
        "product_id": product_id,
        "catalog_version": n,
        "schema_version": payload.get("schema_version") or "1.0",
        "source_revision": payload.get("source_revision") or payload.get("catalog_version"),
        "source_hash": payload.get("source_revision") or "",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "VALID",
        "stats": payload.get("stats") or {},
        "validation": val,
        "features": payload.get("features") or [],
    }
    (incoming / "catalog.json").write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")
    incoming.replace(dest)
    state["catalog_status"] = "VALID"
    state["draft_version"] = n
    save_state(data_dir, product_id, state)
    append_history(
        data_dir,
        product_id,
        {"action": "generate", "result": "VALID", "new_version": n, "source_section": "catalog"},
    )
    return {"ok": True, "version": n, "status": "VALID", "stats": body["stats"], "unchanged": previous and previous.get("source_revision") == payload.get("source_revision") and not force}


def activate_version(knowledge_root: Path, data_dir: Path, product_id: str, version: int) -> dict[str, Any]:
    dest = versions_dir(knowledge_root, product_id) / f"v{version}" / "catalog.json"
    if not dest.is_file():
        return {"ok": False, "error": "version missing"}
    data = json.loads(dest.read_text(encoding="utf-8"))
    if data.get("status") not in {"VALID", "ACTIVE"}:
        return {"ok": False, "error": "version not VALID"}
    prev = load_active(knowledge_root, product_id)
    pointer = {
        "product_id": product_id,
        "catalog_version": version,
        "status": "ACTIVE",
        "activated_at": datetime.now(timezone.utc).isoformat(),
        "source_hash": data.get("source_hash"),
    }
    path = active_pointer_path(knowledge_root, product_id)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(pointer, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)
    data["status"] = "ACTIVE"
    dest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    state = load_state(data_dir, product_id)
    state["previous_version"] = (prev or {}).get("catalog_version")
    state["active_version"] = version
    state["catalog_status"] = "ACTIVE"
    save_state(data_dir, product_id, state)
    append_history(
        data_dir,
        product_id,
        {
            "action": "activate",
            "result": "ACTIVE",
            "new_version": version,
            "old_version": state.get("previous_version"),
            "source_section": "catalog",
        },
    )
    return {"ok": True, "version": version, "status": "ACTIVE"}


def rollback(knowledge_root: Path, data_dir: Path, product_id: str) -> dict[str, Any]:
    state = load_state(data_dir, product_id)
    prev = state.get("previous_version")
    if not prev:
        return {"ok": False, "error": "no previous version"}
    result = activate_version(knowledge_root, data_dir, product_id, int(prev))
    if result.get("ok"):
        state = load_state(data_dir, product_id)
        state["catalog_status"] = "ROLLED_BACK"
        save_state(data_dir, product_id, state)
        append_history(
            data_dir,
            product_id,
            {"action": "rollback", "result": "ROLLED_BACK", "new_version": prev, "source_section": "products"},
        )
        result["status"] = "ROLLED_BACK"
    return result
