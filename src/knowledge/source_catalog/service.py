"""Facade for Catalog Manager and CLI: scan, version, media, deploy."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from src.knowledge.product_catalogs import (
    get_product,
    list_all_product_dicts,
    load_product_catalogs,
    update_product_fields,
)
from src.knowledge.source_catalog.classify import classify_filename
from src.knowledge.source_catalog.consistency import validate_consistency
from src.knowledge.source_catalog.deploy import (
    deploy_catalog_local,
    local_deploy_root,
    try_remote_scp,
    upload_media_files,
)
from src.knowledge.source_catalog.media import is_remote_server_item, pending_uploads, scan_local_media
from src.knowledge.source_catalog.pipeline import load_matrix
from src.knowledge.source_catalog.products import (
    discover_pic_products,
    ensure_default_registry,
    pic_dir_for_product,
    product_maps,
    save_registry,
    load_registry,
)
from src.knowledge.source_catalog.sftp_conn import load_sftp_settings, session_status, ssh_ready, test_connection
from src.knowledge.source_catalog.store import (
    append_history,
    load_global_queue,
    load_media_index,
    load_state,
    read_history,
    save_media_index,
    save_state,
)
from src.knowledge.source_catalog.versions import (
    activate_version,
    generate_version,
    load_active,
    rollback,
)


def dashboard(project_root: Path, knowledge_root: Path, data_dir: Path) -> dict[str, Any]:
    load_product_catalogs(knowledge_root)
    ensure_default_registry(data_dir, project_root)
    maps = product_maps(project_root, knowledge_root, data_dir)
    pic = discover_pic_products(project_root, knowledge_root, data_dir)
    sftp = load_sftp_settings(data_dir)
    server = "CONNECTED" if ssh_ready(data_dir) else "OFFLINE"
    products = []
    for row in list_all_product_dicts(knowledge_root):
        pid = str(row.get("product_id") or "")
        state = load_state(data_dir, pid)
        active = load_active(knowledge_root, pid) or {}
        media = load_media_index(data_dir, pid)
        items = [i for i in media.get("items") or [] if isinstance(i, dict)]
        mmap = next((m for m in maps if m.get("product_id") == pid), {})
        cat_on = bool(row.get("catalog_enabled", True))
        status = "DISABLED" if not cat_on else (state.get("catalog_status") or active.get("status") or "DRAFT")
        on_server = [i for i in items if is_remote_server_item(i)]
        products.append(
            {
                "product_id": pid,
                "title": ((row.get("title") or {}).get("en") or pid),
                "menu_enabled": bool(row.get("enabled", True)),
                "catalog_enabled": cat_on,
                "catalog_status": status,
                "catalog_version": active.get("catalog_version") or state.get("active_version"),
                "features": len(get_product(pid).features) if get_product(pid) else 0,
                "last_scan": media.get("scanned_at"),
                "images": len(on_server),
                "pending": len([i for i in items if i.get("status") in {"LOCAL_ONLY", "MODIFIED", "PENDING_UPLOAD"}]),
                "failed": len([i for i in items if i.get("status") == "FAILED"]),
                "unmapped": len([i for i in items if i.get("status") == "UNMAPPED" or not i.get("feature_ids")]),
                "local_deleted": len([i for i in items if i.get("status") == "LOCAL_DELETED"]),
                "synced": len(on_server),
                "pic_dir": mmap.get("images") or str(pic_dir_for_product(project_root, pid, data_dir) or ""),
                "source": mmap.get("source") or "",
                "server_media": mmap.get("server_media") or "",
                "server": server,
            }
        )
    from src.knowledge.source_catalog.queue import visible_queue_jobs

    return {
        "products": products,
        "pic": pic,
        "maps": maps,
        "ssh_configured": ssh_ready(data_dir),
        "server": server,
        "sftp_host": sftp.get("host") or "",
        "queue": visible_queue_jobs(load_global_queue(data_dir)),
        "queue_count": len(visible_queue_jobs(load_global_queue(data_dir))),
        "media_count": sum(int(p.get("images") or 0) for p in products),
    }


def set_catalog_enabled(knowledge_root: Path, product_id: str, enabled: bool) -> None:
    update_product_fields(knowledge_root, product_id, catalog_enabled=enabled)


def source_root_for(data_dir: Path, product_id: str) -> Path | None:
    stored = (load_registry(data_dir).get("paths") or {}).get(product_id) or {}
    raw = str(stored.get("source") or "").strip()
    if raw:
        path = Path(raw)
        if path.is_dir() or path.is_file():
            return path
    env = (os.getenv("VPS_TO_VPN_SOURCE") or "").strip()
    if env:
        path = Path(env)
        if path.is_dir() or path.is_file():
            return path
    return None


def sync_catalog(
    *,
    source_root: Path,
    knowledge_root: Path,
    data_dir: Path,
    product_id: str,
    force: bool = False,
    activate: bool = True,
) -> dict[str, Any]:
    active = load_active(knowledge_root, product_id)
    gen = generate_version(
        source_root=source_root,
        knowledge_root=knowledge_root,
        data_dir=data_dir,
        product_id=product_id,
        force=force,
    )
    if not gen.get("ok"):
        return gen
    if gen.get("unchanged") and active and not force:
        return {"ok": True, "skipped": True, "reason": "source unchanged", "version": active.get("catalog_version")}
    if not activate:
        return gen
    act = activate_version(knowledge_root, data_dir, product_id, int(gen["version"]))
    if not act.get("ok"):
        return act
    dest = local_deploy_root()
    upload = {"ok": True, "mode": "local-only"}
    if dest:
        upload = deploy_catalog_local(knowledge_root, product_id, int(gen["version"]), dest)
        if not upload.get("ok"):
            return {"ok": False, "error": upload.get("error"), "generated": gen, "activated": False}
    scp = {"ok": False, "skipped": True}
    cat_file = knowledge_root / "source_catalog" / "versions" / product_id / f"v{gen['version']}" / "catalog.json"
    if ssh_ready(data_dir) or os.getenv("BOT_SSH_HOST"):
        scp = try_remote_scp(cat_file, f"knowledge/source_catalog/versions/{product_id}/v{gen['version']}/catalog.json")
        if not scp.get("ok"):
            append_history(
                data_dir,
                product_id,
                {
                    "action": "upload",
                    "result": "FAILED",
                    "filename": cat_file.name,
                    "error": scp.get("error"),
                    "source_section": "catalog",
                    "server": session_status().get("host") or "",
                },
            )
            return {"ok": False, "error": scp.get("error"), "local_active": True, "remote": scp}
    append_history(
        data_dir,
        product_id,
        {
            "action": "upload",
            "result": "ok",
            "filename": cat_file.name,
            "new_version": gen["version"],
            "source_section": "catalog",
            "server": session_status().get("host") or "",
        },
    )
    return {"ok": True, "version": gen["version"], "upload": upload, "remote": scp}


def sync_media(project_root: Path, data_dir: Path, product_id: str, *, only_ids: list[str] | None = None) -> dict[str, Any]:
    from src.knowledge.source_catalog.queue import enqueue_media, process_waiting

    scan_local_media(project_root, data_dir, product_id)
    media = load_media_index(data_dir, product_id)
    ids = only_ids or [str(i.get("media_id")) for i in pending_uploads(media)]
    enqueue_media(data_dir, product_id, ids)
    return {"ok": True, "queued": ids, "processed": process_waiting(project_root, data_dir)}


def auto_map_media(project_root: Path, knowledge_root: Path, data_dir: Path, product_id: str, *, threshold: float = 0.7) -> dict[str, Any]:
    scan_local_media(project_root, data_dir, product_id)
    feats: list[str] = []
    prod = get_product(product_id)
    if prod:
        feats.extend(str(f.get("id")) for f in prod.features if isinstance(f, dict) and f.get("id"))
    matrix = load_matrix(knowledge_root)
    if matrix:
        feats.extend(str(x.get("id")) for x in matrix.get("features") or [] if isinstance(x, dict) and x.get("id"))
    feats = sorted({f for f in feats if f})
    index = load_media_index(data_dir, product_id)
    mapped = 0
    review = 0
    for item in index.get("items") or []:
        if not isinstance(item, dict):
            continue
        if item.get("feature_ids"):
            continue
        result = classify_filename(str(item.get("filename") or ""), feats, threshold=threshold)
        item["classify_confidence"] = result["confidence"]
        item["classify_candidates"] = result.get("candidates") or []
        item["needs_review"] = result["needs_review"]
        if result["auto_assigned"]:
            item["feature_ids"] = result["feature_ids"]
            item["catalog_feature_id"] = result["feature_ids"][0]
            if item.get("status") == "UNMAPPED":
                item["status"] = "LOCAL_ONLY"
            mapped += 1
        else:
            review += 1
    save_media_index(data_dir, product_id, index)
    return {"mapped": mapped, "needs_review": review}


def set_mapping(data_dir: Path, product_id: str, media_id: str, feature_ids: list[str]) -> bool:
    index = load_media_index(data_dir, product_id)
    for item in index.get("items") or []:
        if str(item.get("media_id")) != media_id:
            continue
        item["feature_ids"] = feature_ids
        item["catalog_feature_id"] = feature_ids[0] if feature_ids else ""
        item["needs_review"] = not feature_ids
        if feature_ids and item.get("status") == "UNMAPPED":
            item["status"] = "LOCAL_ONLY"
        save_media_index(data_dir, product_id, index)
        return True
    return False


def delete_server_media(data_dir: Path, product_id: str, media_ids: list[str], *, force: bool = False) -> dict[str, Any]:
    from src.knowledge.source_catalog.sftp_conn import delete_remote

    index = load_media_index(data_dir, product_id)
    warnings = []
    deleted = []
    deleted_files = []
    keep = []
    for item in index.get("items") or []:
        if not isinstance(item, dict):
            continue
        mid = str(item.get("media_id") or "")
        if mid not in media_ids:
            keep.append(item)
            continue
        linked = list(item.get("feature_ids") or [])
        if linked and not force:
            warnings.append({"media_id": mid, "filename": item.get("filename"), "features": linked})
            keep.append(item)
            continue
        sp = Path(str(item.get("server_path") or ""))
        if sp.is_file():
            sp.unlink()
        elif str(item.get("server_path") or "").startswith("/"):
            delete_remote(data_dir, str(item.get("server_path")))
        deleted.append(mid)
        deleted_files.append(str(item.get("filename") or ""))
    if warnings and not force:
        return {"ok": False, "warnings": warnings, "deleted": []}
    save_media_index(data_dir, product_id, {"items": keep})
    append_history(
        data_dir,
        product_id,
        {
            "action": "delete_media",
            "result": "ok",
            "filename": deleted_files,
            "object": deleted,
            "source_section": "media",
            "server": session_status().get("host") or "",
        },
    )
    return {"ok": True, "deleted": deleted}


def keep_server_media(data_dir: Path, product_id: str, media_id: str) -> bool:
    index = load_media_index(data_dir, product_id)
    for item in index.get("items") or []:
        if str(item.get("media_id")) == media_id:
            item["keep_on_server"] = True
            save_media_index(data_dir, product_id, index)
            return True
    return False


def product_page(project_root: Path, knowledge_root: Path, data_dir: Path, product_id: str) -> dict[str, Any]:
    dash = dashboard(project_root, knowledge_root, data_dir)
    row = next((p for p in dash["products"] if p["product_id"] == product_id), None)
    media = load_media_index(data_dir, product_id)
    feats = []
    prod = get_product(product_id)
    if prod:
        feats = [str(f.get("id")) for f in prod.features if isinstance(f, dict) and f.get("id")]
    return {
        "product": row,
        "state": load_state(data_dir, product_id),
        "active": load_active(knowledge_root, product_id),
        "media": media.get("items") or [],
        "history": read_history(data_dir, product_id),
        "pending": pending_uploads(media),
        "features": feats,
        "consistency": validate_consistency(knowledge_root, data_dir, product_id),
        "maps": dash.get("maps") or [],
    }


def save_product_paths(data_dir: Path, product_id: str, source: str, images: str, server_media: str, display: str = "") -> None:
    reg = load_registry(data_dir)
    paths = dict(reg.get("paths") or {})
    paths[product_id] = {
        "display": display or paths.get(product_id, {}).get("display") or product_id,
        "source": source,
        "images": images,
        "server_media": server_media,
    }
    aliases = dict(reg.get("aliases") or {})
    if display:
        aliases[" ".join(display.lower().replace("-", " ").split())] = product_id
    save_registry(data_dir, {"aliases": aliases, "paths": paths})


def build_ai_catalog(project_root: Path, knowledge_root: Path, data_dir: Path, product_id: str) -> dict[str, Any]:
    """Build product_catalogs JSON from mapped source via AI, then version it."""
    import asyncio
    import shutil
    import tempfile

    src = source_root_for(data_dir, product_id)
    if src is None:
        return {"ok": False, "error": "err_source"}
    from src.manager.ai_store import ai_ready, manager_ai_client

    if not ai_ready(project_root, data_dir):
        return {"ok": False, "error": "err_ai"}
    tmp: Path | None = None
    folder = src
    extra = ""
    try:
        if src.is_file():
            tmp = Path(tempfile.mkdtemp(prefix="ssm-src-"))
            shutil.copy2(src, tmp / src.name)
            folder = tmp
            extra = f"Single written source file: {src.name}"
        from src.knowledge.catalog_builder import build_one_catalog

        async def _run() -> str:
            ai = manager_ai_client(project_root, data_dir)
            try:
                return await build_one_catalog(
                    folder,
                    ai.chat,
                    knowledge_root=knowledge_root,
                    project_root=project_root,
                    extra_sources=extra,
                    force_product_id=product_id,
                )
            finally:
                await ai.close()

        asyncio.run(_run())
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)[:400]}
    finally:
        if tmp is not None:
            shutil.rmtree(tmp, ignore_errors=True)
    root = folder if src.is_dir() else src.parent
    return sync_catalog(
        source_root=root,
        knowledge_root=knowledge_root,
        data_dir=data_dir,
        product_id=product_id,
        force=True,
        activate=True,
    )

