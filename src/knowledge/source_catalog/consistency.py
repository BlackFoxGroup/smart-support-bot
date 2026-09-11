"""Catalog feature ↔ media mapping ↔ server file consistency."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.knowledge.product_catalogs import get_product
from src.knowledge.source_catalog.pipeline import load_matrix
from src.knowledge.source_catalog.store import load_media_index
from src.knowledge.source_catalog.versions import load_active


def validate_consistency(knowledge_root: Path, data_dir: Path, product_id: str) -> dict[str, Any]:
    feats: set[str] = set()
    prod = get_product(product_id)
    if prod:
        feats.update(str(f.get("id")) for f in prod.features if isinstance(f, dict) and f.get("id"))
    matrix = load_matrix(knowledge_root)
    if matrix and product_id == str(matrix.get("product_id") or "vpn-installer"):
        feats.update(str(x.get("id")) for x in matrix.get("features") or [] if isinstance(x, dict) and x.get("id"))
    active = load_active(knowledge_root, product_id) or {}
    index = load_media_index(data_dir, product_id)
    items = [i for i in index.get("items") or [] if isinstance(i, dict)]
    orphaned = []
    unmapped = []
    missing_file = []
    synced = []
    for item in items:
        fids = [str(x) for x in (item.get("feature_ids") or []) if x]
        if not fids:
            unmapped.append(item.get("filename"))
        for fid in fids:
            if feats and fid not in feats:
                orphaned.append({"filename": item.get("filename"), "feature_id": fid})
        path = Path(str(item.get("path") or ""))
        server = Path(str(item.get("server_path") or ""))
        if item.get("status") != "LOCAL_DELETED" and not path.is_file():
            missing_file.append(item.get("filename"))
        if item.get("status") == "SYNCED" and (server.is_file() or str(item.get("server_path") or "").startswith("/")):
            synced.append(item.get("filename"))
    return {
        "product_id": product_id,
        "catalog_version": active.get("catalog_version"),
        "features": len(feats),
        "media": len(items),
        "mapped": len(items) - len(unmapped),
        "unmapped": unmapped,
        "orphaned_media": orphaned,
        "missing_local": missing_file,
        "synced": len(synced),
        "ok": not orphaned,
    }
