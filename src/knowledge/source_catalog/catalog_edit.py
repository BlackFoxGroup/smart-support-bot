"""Edit catalog JSON texts and catalog-bound photos. No raw dumps in UI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.knowledge.product_catalogs import load_product_catalogs, product_json_path
from src.knowledge.source_catalog.store import load_media_index, save_media_index


def read_catalog(knowledge_root: Path, product_id: str) -> dict[str, Any]:
    path = product_json_path(knowledge_root, product_id)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def write_catalog(knowledge_root: Path, product_id: str, data: dict[str, Any]) -> None:
    path = product_json_path(knowledge_root, product_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    load_product_catalogs(knowledge_root)


def catalog_media_list(knowledge_root: Path, product_id: str) -> list[dict[str, Any]]:
    data = read_catalog(knowledge_root, product_id)
    out = []
    for i, row in enumerate(data.get("media") or []):
        if not isinstance(row, dict):
            continue
        rel = str(row.get("path") or "").replace("\\", "/").strip()
        if not rel:
            continue
        feats = row.get("feature_ids") if isinstance(row.get("feature_ids"), list) else []
        slot = str(row.get("slot") or "")
        out.append(
            {
                "index": i,
                "path": rel,
                "filename": Path(rel).name,
                "slot": slot,
                "feature": (feats[0] if feats else slot),
                "note": str(row.get("note") or ""),
            }
        )
    return out


def catalog_feature_ids(knowledge_root: Path, product_id: str) -> list[str]:
    data = read_catalog(knowledge_root, product_id)
    ids = []
    for feat in data.get("features") or []:
        if isinstance(feat, dict) and feat.get("id"):
            ids.append(str(feat["id"]))
    return ids


def _safe_rel(project_root: Path, rel: str) -> Path | None:
    raw = (rel or "").replace("\\", "/").lstrip("/")
    if not raw.startswith("media/catalogs/"):
        return None
    dest = (project_root / raw).resolve()
    root = (project_root / "media" / "catalogs").resolve()
    try:
        dest.relative_to(root)
    except ValueError:
        return None
    return dest


def set_catalog_media_feature(
    knowledge_root: Path,
    data_dir: Path,
    product_id: str,
    rel_path: str,
    feature_id: str,
) -> dict[str, Any]:
    feat = str(feature_id or "").strip()
    if not feat:
        return {"ok": False, "error": "no_feature"}
    data = read_catalog(knowledge_root, product_id)
    media = list(data.get("media") or [])
    found = False
    for row in media:
        if not isinstance(row, dict):
            continue
        if str(row.get("path") or "").replace("\\", "/") != rel_path.replace("\\", "/"):
            continue
        row["slot"] = feat
        row["feature_ids"] = [feat]
        found = True
        break
    if not found:
        return {"ok": False, "error": "not found"}
    data["media"] = media
    write_catalog(knowledge_root, product_id, data)
    index = load_media_index(data_dir, product_id)
    for item in index.get("items") or []:
        if str(item.get("catalog_path") or "").replace("\\", "/") == rel_path.replace("\\", "/"):
            item["catalog_feature_id"] = feat
            fids = [str(x) for x in (item.get("feature_ids") or []) if str(x).strip()]
            if feat not in fids:
                fids.append(feat)
            item["feature_ids"] = fids
    save_media_index(data_dir, product_id, index)
    return {"ok": True}


def return_catalog_media_to_index(
    knowledge_root: Path,
    data_dir: Path,
    product_id: str,
    rel_path: str,
) -> dict[str, Any]:
    data = read_catalog(knowledge_root, product_id)
    want = rel_path.replace("\\", "/")
    media = [
        m
        for m in (data.get("media") or [])
        if not (isinstance(m, dict) and str(m.get("path") or "").replace("\\", "/") == want)
    ]
    data["media"] = media
    write_catalog(knowledge_root, product_id, data)
    index = load_media_index(data_dir, product_id)
    for item in index.get("items") or []:
        if str(item.get("catalog_path") or "").replace("\\", "/") == want:
            item["catalog_path"] = ""
    save_media_index(data_dir, product_id, index)
    return {"ok": True}


def delete_catalog_media(
    project_root: Path,
    knowledge_root: Path,
    data_dir: Path,
    product_id: str,
    rel_path: str,
    *,
    from_server: bool,
) -> dict[str, Any]:
    want = rel_path.replace("\\", "/")
    data = read_catalog(knowledge_root, product_id)
    data["media"] = [
        m
        for m in (data.get("media") or [])
        if not (isinstance(m, dict) and str(m.get("path") or "").replace("\\", "/") == want)
    ]
    write_catalog(knowledge_root, product_id, data)
    local = _safe_rel(project_root, want)
    if local and local.is_file():
        try:
            local.unlink()
        except OSError:
            pass
    index = load_media_index(data_dir, product_id)
    for item in index.get("items") or []:
        if str(item.get("catalog_path") or "").replace("\\", "/") != want:
            continue
        item["catalog_path"] = ""
        if from_server:
            remote = str(item.get("server_path") or "")
            if remote.startswith("/"):
                from src.knowledge.source_catalog.sftp_conn import delete_remote

                delete_remote(data_dir, remote)
                item["server_path"] = ""
                if item.get("status") == "SYNCED":
                    item["status"] = "LOCAL_ONLY"
    save_media_index(data_dir, product_id, index)
    return {"ok": True}


def save_catalog_texts(
    knowledge_root: Path,
    product_id: str,
    *,
    lang: str,
    title: str,
    short_summary: str,
    long_summary: str,
    features: list[dict[str, str]],
) -> dict[str, Any]:
    data = read_catalog(knowledge_root, product_id)
    if not data:
        return {"ok": False, "error": "missing"}
    code = lang if lang in ("fa", "en", "ru", "zh") else "en"

    def _set_map(key: str, value: str) -> None:
        cur = data.get(key)
        if not isinstance(cur, dict):
            cur = {}
        cur[code] = value
        data[key] = cur

    _set_map("title", title)
    _set_map("short_summary", short_summary)
    _set_map("long_summary", long_summary)
    by_id = {str(f.get("id")): f for f in features if f.get("id")}
    rows = list(data.get("features") or [])
    for row in rows:
        if not isinstance(row, dict):
            continue
        fid = str(row.get("id") or "")
        patch = by_id.get(fid)
        if not patch:
            continue
        title_m = row.get("title") if isinstance(row.get("title"), dict) else {}
        sum_m = row.get("summary") if isinstance(row.get("summary"), dict) else {}
        if patch.get("title") is not None:
            title_m[code] = patch["title"]
            row["title"] = title_m
        if patch.get("summary") is not None:
            sum_m[code] = patch["summary"]
            row["summary"] = sum_m
    data["features"] = rows
    write_catalog(knowledge_root, product_id, data)
    return {"ok": True}


def add_catalog_feature(
    knowledge_root: Path,
    product_id: str,
    *,
    feature_id: str,
    title: str,
    summary: str,
    lang: str,
) -> dict[str, Any]:
    from src.knowledge.product_catalogs import SUPPORTED, slugify_product_id

    data = read_catalog(knowledge_root, product_id)
    if not data:
        return {"ok": False, "error": "missing"}
    fid = slugify_product_id(feature_id or title)
    if fid == "product":
        return {"ok": False, "error": "bad_id"}
    rows = list(data.get("features") or [])
    if any(isinstance(r, dict) and str(r.get("id") or "") == fid for r in rows):
        return {"ok": False, "error": "exists"}
    code = lang if lang in SUPPORTED else "en"
    title_map = {c: (title if c == code else title) for c in SUPPORTED}
    sum_map = {c: (summary if c == code else summary) for c in SUPPORTED}
    rows.append(
        {
            "id": fid,
            "title": title_map,
            "summary": sum_map,
            "media_slot": fid.replace("_", "-"),
        }
    )
    data["features"] = rows
    write_catalog(knowledge_root, product_id, data)
    return {"ok": True, "id": fid}


def lang_text(block: Any, lang: str) -> str:
    if isinstance(block, dict):
        return str(block.get(lang) or block.get("en") or block.get("fa") or "")
    return str(block or "")
