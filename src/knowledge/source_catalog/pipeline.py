"""Build matrix, migrate manual catalog, validate, incremental persist."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.knowledge.source_catalog.scanner import ScanRaw, discover_features, scan_source_tree
from src.knowledge.source_catalog.schema import (
    PRODUCT_ID,
    SCHEMA_VERSION,
    STATUS_DEPRECATED,
    FeatureRecord,
    empty_validation_report,
)

logger = logging.getLogger(__name__)

MANUAL_ID_ALIASES = {
    "setup_central": "setup_central",
    "connect_ssh": "connect_ssh",
    "full_deploy": "full_deploy",
    "add_tunnel_servers": "add_tunnel_servers",
    "add_exit_servers": "add_exit_servers",
    "add_node_servers": "add_node_servers",
    "configure_panel": "configure_panel",
    "add_outbounds": "add_outbounds",
    "panel_login_info": "panel_login_info",
    "test_client": "test_client",
    "add_domain_dns": "add_domain_dns",
    "external_proxy": "external_proxy",
    "free_domain": "free_domain",
    "configure_cdn": "configure_cdn",
    "mesh_topology": "mesh_topology",
    "mesh_servers": "mesh_topology",
    "link_test": "link_type_change",
    "diagnose_repair": "diagnose_repair",
    "check_system": "check_system",
    "add_telegram_mirza": "add_telegram_mirza",
    "add_telegram_smart_support": "telegram_other_delete_vpn",
    "add_telegram_move": "telegram_other_delete_vpn",
    "add_telegram_update_mirza": "add_telegram_mirza",
    "move_central": "move_central",
    "proxy_settings": "proxy_settings",
    "ai_chatbox": "ai_chatbox",
    "ai_conversations": "ai_chatbox",
    "ai_tasks": "ai_chatbox",
    "blackfox_mcp": "blackfox_mcp",
    "terminal": "terminal",
    "status_bar": "status_bar",
    "factory_reset": "factory_reset_ssh",
    "delete_tools": "delete_tools",
    "modes": "modes",
    "registration": "registration",
}


def matrix_path(knowledge_root: Path) -> Path:
    return knowledge_root / "source_catalog" / "vpn-installer.matrix.json"


def report_path(knowledge_root: Path) -> Path:
    return knowledge_root / "source_catalog" / "last_validation.json"


def file_hash_cache_path(data_dir: Path) -> Path:
    return data_dir / "source_catalog" / "file_index.json"


def load_manual_catalog(knowledge_root: Path) -> dict[str, Any]:
    from src.knowledge.product_catalogs import resolve_product_json_path

    path = resolve_product_json_path(knowledge_root, "vpn-installer")
    if path is None or not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def migrate_manual(features: list[FeatureRecord], manual: dict[str, Any]) -> list[FeatureRecord]:
    by_id = {f.id: f for f in features}
    media = manual.get("media") if isinstance(manual.get("media"), list) else []
    slot_to_feat: dict[str, str] = {}
    for feat in manual.get("features") or []:
        if not isinstance(feat, dict):
            continue
        mid = str(feat.get("id") or "").strip()
        mapped = MANUAL_ID_ALIASES.get(mid, mid)
        rec = by_id.get(mapped)
        if rec is None:
            continue
        rec.migrated_from_manual = True
        rec.menu_feature = True
        howto = feat.get("howto") if isinstance(feat.get("howto"), dict) else {}
        summary = feat.get("summary") if isinstance(feat.get("summary"), dict) else {}
        title = feat.get("title") if isinstance(feat.get("title"), dict) else {}
        if howto.get("en"):
            rec.workflow = [str(howto.get("en"))]
        if summary.get("en") and rec.purpose in {"UNKNOWN", rec.name}:
            rec.purpose = str(summary.get("en"))
        if title.get("en"):
            rec.name = str(title.get("en"))
        slot = str(feat.get("media_slot") or "").strip()
        if slot:
            rec.media_slots.append(slot)
            slot_to_feat[slot] = rec.id
    for item in media:
        if not isinstance(item, dict):
            continue
        slot = str(item.get("slot") or "").strip()
        fid = slot_to_feat.get(slot)
        if not fid:
            continue
        rec = by_id.get(fid)
        if rec and slot not in rec.media_slots:
            rec.media_slots.append(slot)
    return list(by_id.values())


def validate(features: list[FeatureRecord], previous: dict[str, Any] | None) -> dict[str, Any]:
    report = empty_validation_report()
    now_ids = {f.id for f in features}
    prev_feats = {}
    if previous and isinstance(previous.get("features"), list):
        for item in previous["features"]:
            if isinstance(item, dict) and item.get("id"):
                prev_feats[str(item["id"])] = item
    prev_ids = set(prev_feats)
    report["missing"] = []  # filled vs discovered — after persist, catalog == discovered
    report["extra"] = sorted(prev_ids - now_ids)
    for rec in features:
        old = prev_feats.get(rec.id)
        if rec.status in {STATUS_DEPRECATED, "legacy"}:
            report["deprecated"].append(rec.id)
        if rec.scan_errors:
            report["scan_errors"].append({"id": rec.id, "errors": rec.scan_errors})
        if old is None:
            report["updated"].append(rec.id)
            continue
        if str(old.get("source_hash") or "") != rec.source_hash:
            report["outdated"].append(rec.id)
        else:
            report["unchanged"].append(rec.id)
    # Catalog IDs are exactly discovered IDs after builder writes the matrix.
    report["catalog_ids"] = sorted(now_ids)
    report["missing"] = []
    return report


def build_payload(raw: ScanRaw, features: list[FeatureRecord], previous: dict[str, Any] | None) -> dict[str, Any]:
    report = validate(features, previous)
    return {
        "schema_version": SCHEMA_VERSION,
        "catalog_version": raw.file_index_hash[:16],
        "product_id": PRODUCT_ID,
        "source_root": raw.root,
        "source_scan_time": raw.scanned_at,
        "source_revision": raw.file_index_hash,
        "stats": {
            "go_files": raw.go_files,
            "ui_prod_files": raw.ui_prod_files,
            "packages": len(raw.packages),
            "features": len(features),
        },
        "features": [f.to_dict() for f in features],
        "validation": report,
    }


def atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def load_matrix(knowledge_root: Path) -> dict[str, Any] | None:
    path = matrix_path(knowledge_root)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("matrix unreadable: %s", exc)
        return None
    if not isinstance(data, dict) or not isinstance(data.get("features"), list):
        return None
    return data


def needs_full_scan(raw_hash: str, previous: dict[str, Any] | None) -> bool:
    if not previous:
        return True
    return str(previous.get("source_revision") or "") != raw_hash


def run_sync(
    source_root: Path,
    knowledge_root: Path,
    data_dir: Path,
    *,
    force: bool = False,
) -> dict[str, Any]:
    previous = load_matrix(knowledge_root)
    cache_p = file_hash_cache_path(data_dir)
    cache_p.parent.mkdir(parents=True, exist_ok=True)

    if not source_root.is_dir():
        if previous:
            logger.warning("source missing at %s — keeping previous matrix", source_root)
            return previous
        raise FileNotFoundError(f"VPS to VPN source not found: {source_root}")

    raw = scan_source_tree(source_root)
    if not force and previous and not needs_full_scan(raw.file_index_hash, previous):
        logger.info("source unchanged (%s) — skip rebuild", raw.file_index_hash[:12])
        return previous

    if raw.go_files < 50:
        logger.error("scan too small (%s go files) — refuse overwrite", raw.go_files)
        if previous:
            return previous
        raise RuntimeError("incomplete scan")

    features = discover_features(raw)
    features = migrate_manual(features, load_manual_catalog(knowledge_root))
    payload = build_payload(raw, features, previous)
    atomic_write(matrix_path(knowledge_root), payload)
    atomic_write(report_path(knowledge_root), payload["validation"])
    cache_p.write_text(
        json.dumps({"revision": raw.file_index_hash, "at": datetime.now(timezone.utc).isoformat()}),
        encoding="utf-8",
    )
    return payload
