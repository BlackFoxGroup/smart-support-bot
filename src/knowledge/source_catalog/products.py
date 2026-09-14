"""Product path registry. Display folders are mapped in data, not hardcoded names."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from src.knowledge.product_catalogs import list_all_product_dicts, slugify_product_id
from src.knowledge.source_catalog.store import live_root



def registry_path(data_dir: Path) -> Path:
    return live_root(data_dir) / "product_paths.json"


def _norm(name: str) -> str:
    return " ".join((name or "").strip().lower().replace("_", " ").replace("-", " ").split())


def load_registry(data_dir: Path) -> dict[str, Any]:
    path = registry_path(data_dir)
    if not path.is_file():
        return {"aliases": {}, "paths": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"aliases": {}, "paths": {}}
    if not isinstance(data, dict):
        return {"aliases": {}, "paths": {}}
    data.setdefault("aliases", {})
    data.setdefault("paths", {})
    return data


def ensure_default_registry(data_dir: Path, project_root: Path) -> None:
    reg = load_registry(data_dir)
    aliases = dict(reg.get("aliases") or {})
    paths = dict(reg.get("paths") or {})
    changed = False
    knowledge_root = project_root / "knowledge"
    if knowledge_root.is_dir():
        for row in list_all_product_dicts(knowledge_root):
            pid = str(row.get("product_id") or "")
            if not pid:
                continue
            title = row.get("title") or {}
            for name in (pid, str(title.get("en") or ""), str(title.get("fa") or "")):
                key = _norm(name)
                if key and aliases.get(key) != pid:
                    aliases[key] = pid
                    changed = True
    if "vps to vpn" not in aliases:
        aliases["vps to vpn"] = "vpn-installer"
        changed = True
    if "vpn-installer" not in paths:
        src = (os.getenv("VPS_TO_VPN_SOURCE") or r"F:\VPS to VPN").strip()
        img = project_root / "pic" / "VPS to VPN"
        paths["vpn-installer"] = {
            "display": "VPS to VPN",
            "source": src if Path(src).is_dir() else "",
            "images": str(img) if img.is_dir() else "",
        }
        changed = True
    if changed:
        save_registry(data_dir, {"aliases": aliases, "paths": paths})


def save_registry(data_dir: Path, data: dict[str, Any]) -> None:
    path = registry_path(data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def resolve_product_id(name: str, data_dir: Path | None = None, knowledge_root: Path | None = None) -> str | None:
    key = _norm(name)
    if not key:
        return None
    if data_dir:
        aliases = load_registry(data_dir).get("aliases") or {}
        if isinstance(aliases, dict) and key in aliases:
            return str(aliases[key])
    if knowledge_root:
        for row in list_all_product_dicts(knowledge_root):
            pid = str(row.get("product_id") or "")
            title = (row.get("title") or {})
            names = {_norm(pid), _norm(str(title.get("en") or "")), _norm(str(title.get("fa") or ""))}
            names.discard("")
            if key in names or slugify_product_id(key.replace(" ", "-")) == pid:
                return pid
    return None


def pic_root(project_root: Path) -> Path:
    return project_root / "pic"


def pic_dir_for_product(project_root: Path, product_id: str, data_dir: Path | None = None) -> Path | None:
    if data_dir:
        stored = (load_registry(data_dir).get("paths") or {}).get(product_id) or {}
        img_raw = str(stored.get("images") or "").strip()
        img = Path(img_raw) if img_raw else None
        if img is not None and img.is_dir():
            return img
    root = pic_root(project_root)
    if not root.is_dir():
        return None
    knowledge_root = project_root / "knowledge"
    kr = knowledge_root if knowledge_root.is_dir() else None
    for child in root.iterdir():
        if child.is_dir() and resolve_product_id(child.name, data_dir, kr) == product_id:
            return child
    direct = root / product_id
    return direct if direct.is_dir() else None


def product_maps(
    project_root: Path,
    knowledge_root: Path,
    data_dir: Path,
    *,
    default_source: str = "",
) -> list[dict[str, Any]]:
    reg = load_registry(data_dir)
    paths = reg.get("paths") if isinstance(reg.get("paths"), dict) else {}
    out = []
    seen: set[str] = set()
    for row in list_all_product_dicts(knowledge_root):
        pid = str(row.get("product_id") or "")
        seen.add(pid)
        title = (row.get("title") or {}).get("en") or (row.get("title") or {}).get("fa") or pid
        stored = paths.get(pid) if isinstance(paths.get(pid), dict) else {}
        img = pic_dir_for_product(project_root, pid, data_dir)
        src = str(stored.get("source") or "")
        if not src and default_source:
            src = default_source
        out.append(
            {
                "product_id": pid,
                "display": title,
                "source": src or "Missing",
                "images": str(img) if img else "Missing",
                "server_media": f"/opt/smart-support/products/{pid}",
                "registered": True,
                "enabled": bool(row.get("enabled", True)),
            }
        )
    root = pic_root(project_root)
    if root.is_dir():
        for child in sorted(root.iterdir(), key=lambda p: p.name.lower()):
            if not child.is_dir():
                continue
            pid = resolve_product_id(child.name, data_dir, knowledge_root)
            if pid and pid in seen:
                continue
            out.append(
                {
                    "product_id": pid or "",
                    "display": child.name,
                    "source": "Missing",
                    "images": str(child),
                    "server_media": "",
                    "registered": False,
                    "enabled": False,
                    "status": "unregistered",
                }
            )
    return out


def set_alias(data_dir: Path, folder_name: str, product_id: str) -> None:
    reg = load_registry(data_dir)
    aliases = dict(reg.get("aliases") or {})
    aliases[_norm(folder_name)] = product_id
    reg["aliases"] = aliases
    save_registry(data_dir, reg)


def discover_pic_products(project_root: Path, knowledge_root: Path, data_dir: Path | None = None) -> dict[str, Any]:
    dd = data_dir or (project_root / "data")
    maps = product_maps(project_root, knowledge_root, dd)
    return {
        "registered": [m["product_id"] for m in maps if m.get("registered")],
        "pic_folders": [
            {
                "folder": Path(m["images"]).name if m.get("images") not in {"", "Missing"} else m["display"],
                "path": m.get("images"),
                "product_id": m.get("product_id") or None,
                "status": "registered" if m.get("registered") else "unregistered",
            }
            for m in maps
        ],
    }
