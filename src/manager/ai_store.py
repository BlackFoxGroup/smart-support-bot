"""Persist AI endpoint/key for Manager + bot (.env merge). Secrets never logged."""

from __future__ import annotations

import os
import re
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from urllib.request import Request, urlopen

from src.control.secrets import decrypt_secret, encrypt_secret, mask_api_key
from src.knowledge.source_catalog.sftp_conn import _master_secret, settings_root


def _ai_path(data_dir: Path) -> Path:
    return settings_root(data_dir) / "ai.json"


def load_ai_settings(project_root: Path, data_dir: Path) -> dict[str, Any]:
    import json

    stored: dict[str, Any] = {}
    path = _ai_path(data_dir)
    legacy = data_dir / "live_catalog" / "ai.json"
    if not path.is_file() and legacy.is_file() and legacy != path:
        path = legacy
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
        "connected": bool(stored.get("connected")),
        "bot_linked": bool(stored.get("bot_linked")),
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
        "connected": False,
        "bot_linked": False,
    }
    path = _ai_path(data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    _upsert_env(
        project_root / ".env",
        {
            "AI_BASE_URL": data["base_url"],
            "AI_MODEL": data["model"],
            **({"AI_API_KEY": key} if key else {}),
        },
    )


def set_ai_connection_state(
    project_root: Path,
    data_dir: Path,
    *,
    connected: bool | None = None,
    bot_linked: bool | None = None,
) -> None:
    import json

    path = _ai_path(data_dir)
    raw: dict[str, Any] = {}
    if path.is_file():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            raw = loaded if isinstance(loaded, dict) else {}
        except (OSError, json.JSONDecodeError):
            raw = {}
    if connected is not None:
        raw["connected"] = bool(connected)
        if not connected:
            raw["bot_linked"] = False
    if bot_linked is not None:
        raw["bot_linked"] = bool(bot_linked)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(raw, indent=2), encoding="utf-8")
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def test_ai_connection(project_root: Path, data_dir: Path, timeout: float = 10.0) -> dict[str, Any]:
    settings = load_ai_settings(project_root, data_dir)
    base = str(settings.get("base_url") or "").rstrip("/")
    key = str(settings.get("api_key") or "")
    model = str(settings.get("model") or "")
    if not base or not key:
        return {"ok": False, "error": "AI endpoint and API key are required"}
    request = Request(f"{base}/models", headers={"Authorization": f"Bearer {key}"})
    try:
        with urlopen(request, timeout=timeout) as response:
            if not 200 <= int(response.status) < 300:
                return {"ok": False, "error": f"HTTP {response.status}"}
            body = response.read()
        if model and body:
            import json

            payload = json.loads(body.decode("utf-8"))
            ids = {
                str(item.get("id") or "").lower()
                for item in (payload.get("data") or [])
                if isinstance(item, dict)
            }
            if ids and model.lower() not in ids:
                return {"ok": False, "error": "configured model is unavailable"}
        return {"ok": True}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": type(exc).__name__}


def ai_ready(project_root: Path, data_dir: Path) -> bool:
    s = load_ai_settings(project_root, data_dir)
    return bool(s.get("connected") and s.get("base_url") and s.get("api_key"))


def manager_ai_client(project_root: Path, data_dir: Path):
    from src.ai.client import AIClient

    s = load_ai_settings(project_root, data_dir)
    settings = SimpleNamespace(
        ai_base_url=s["base_url"],
        ai_api_key=s["api_key"],
        ai_model=s["model"] or "kimi-k2.5",
        ai_timeout_seconds=float(os.getenv("MANAGER_AI_TIMEOUT_SECONDS") or "25"),
        ai_max_tokens=300,
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
