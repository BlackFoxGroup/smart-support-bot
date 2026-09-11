"""Local JSON store for catalog versions, media index, history, queue."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


def live_root(data_dir: Path) -> Path:
    return data_dir / "live_catalog"


def product_dir(data_dir: Path, product_id: str) -> Path:
    p = live_root(data_dir) / product_id
    p.mkdir(parents=True, exist_ok=True)
    return p


def _read(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _write(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def load_state(data_dir: Path, product_id: str) -> dict[str, Any]:
    data = _read(product_dir(data_dir, product_id) / "state.json", {})
    if not isinstance(data, dict):
        data = {}
    data.setdefault("product_id", product_id)
    data.setdefault("catalog_status", "DRAFT")
    data.setdefault("active_version", None)
    data.setdefault("previous_version", None)
    return data


def save_state(data_dir: Path, product_id: str, state: dict[str, Any]) -> None:
    _write(product_dir(data_dir, product_id) / "state.json", state)


def load_media_index(data_dir: Path, product_id: str) -> dict[str, Any]:
    data = _read(product_dir(data_dir, product_id) / "media_index.json", {"items": []})
    if not isinstance(data, dict):
        return {"items": []}
    data.setdefault("items", [])
    return data


def save_media_index(data_dir: Path, product_id: str, index: dict[str, Any]) -> None:
    _write(product_dir(data_dir, product_id) / "media_index.json", index)


def append_history(data_dir: Path, product_id: str, event: dict[str, Any]) -> None:
    path = product_dir(data_dir, product_id) / "history.jsonl"
    event = dict(event)
    event.setdefault("timestamp", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    event.setdefault("product_id", product_id)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")


def read_history(data_dir: Path, product_id: str, limit: int = 80) -> list[dict[str, Any]]:
    path = product_dir(data_dir, product_id) / "history.jsonl"
    if not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[dict[str, Any]] = []
    for line in lines[-limit:]:
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            out.append(item)
    return list(reversed(out))


def load_queue(data_dir: Path, product_id: str) -> list[dict[str, Any]]:
    data = _read(product_dir(data_dir, product_id) / "queue.json", {"items": []})
    items = data.get("items") if isinstance(data, dict) else []
    return [x for x in items if isinstance(x, dict)] if isinstance(items, list) else []


def save_queue(data_dir: Path, product_id: str, items: list[dict[str, Any]]) -> None:
    _write(product_dir(data_dir, product_id) / "queue.json", {"items": items})


def load_global_queue(data_dir: Path) -> list[dict[str, Any]]:
    data = _read(live_root(data_dir) / "upload_queue.json", {"items": []})
    items = data.get("items") if isinstance(data, dict) else []
    return [x for x in items if isinstance(x, dict)] if isinstance(items, list) else []


def save_global_queue(data_dir: Path, items: list[dict[str, Any]]) -> None:
    _write(live_root(data_dir) / "upload_queue.json", {"items": items})
