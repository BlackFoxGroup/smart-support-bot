"""Persist AI endpoint/key for Manager + bot (.env merge). Secrets never logged."""

from __future__ import annotations

import os
import re
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from src.control.secrets import decrypt_secret, encrypt_secret, mask_api_key
from src.knowledge.source_catalog.sftp_conn import _master_secret
from src.knowledge.source_catalog.store import live_root


def _ai_path(data_dir: Path) -> Path:
    return live_root(data_dir) / "ai.json"


def load_ai_settings(project_root: Path, data_dir: Path) -> dict[str, Any]:
    import json

    stored: dict[str, Any] = {}
    path = _ai_path(data_dir)
    if path.is_file():
        try:
            stored = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            stored = {}
    if not isinstance(stored, dict):
        stored = {}
    key = ""
    if stored.get("api_key_enc"):
        key = decrypt_secret(str(stored["api_key_enc"]), _master_secret(data_dir))
    if not key:
        key = (os.getenv("AI_API_KEY") or "").strip()
    base = str(stored.get("base_url") or os.getenv("AI_BASE_URL") or "").strip()
    model = str(stored.get("model") or os.getenv("AI_MODEL") or "").strip()
    return {
        "base_url": base,
        "model": model,
        "has_key": bool(key),
        "key_mask": mask_api_key(key) if key else "",
        "api_key": key,
    }


def save_ai_settings(
    project_root: Path,
    data_dir: Path,
    *,
    base_url: str,
    model: str,
    api_key: str | None,
) -> None:
    import json

    current = load_ai_settings(project_root, data_dir)
    key = (api_key or "").strip() or current.get("api_key") or ""
    data = {
        "base_url": (base_url or current.get("base_url") or "").strip().rstrip("/"),
        "model": (model or current.get("model") or "").strip(),
        "api_key_enc": encrypt_secret(key, _master_secret(data_dir)) if key else "",
    }
    path = _ai_path(data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    _upsert_env(
        project_root / ".env",
        {
            "AI_BASE_URL": data["base_url"],
            "AI_MODEL": data["model"],
            **({"AI_API_KEY": key} if key else {}),
        },
    )


def ai_ready(project_root: Path, data_dir: Path) -> bool:
    s = load_ai_settings(project_root, data_dir)
    return bool(s.get("base_url") and s.get("api_key"))


def manager_ai_client(project_root: Path, data_dir: Path):
    from src.ai.client import AIClient

    s = load_ai_settings(project_root, data_dir)
    settings = SimpleNamespace(
        ai_base_url=s["base_url"],
        ai_api_key=s["api_key"],
        ai_model=s["model"] or "kimi-k2.5",
        ai_timeout_seconds=45.0,
        ai_max_tokens=400,
        ai_temperature=0.4,
        ai_usd_per_million_tokens=2.0,
    )
    return AIClient(settings)  # type: ignore[arg-type]


def _upsert_env(env_path: Path, updates: dict[str, str]) -> None:
    lines: list[str] = []
    if env_path.is_file():
        lines = env_path.read_text(encoding="utf-8").splitlines()
    seen: set[str] = set()
    out: list[str] = []
    for line in lines:
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)=", line)
        if m and m.group(1) in updates:
            key = m.group(1)
            val = updates[key]
            if val:
                out.append(f"{key}={val}")
            seen.add(key)
            continue
        out.append(line)
    for key, val in updates.items():
        if key not in seen and val:
            out.append(f"{key}={val}")
    text = "\n".join(out).rstrip() + "\n"
    env_path.write_text(text, encoding="utf-8")
