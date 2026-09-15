# -*- coding: utf-8 -*-
"""Phase 2 adapter: Knowledge API first, then bundled, then automation tree."""
from __future__ import annotations

import json
import logging
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_AUTOMATION = Path("/opt/blackfox-automation")
_API_TIMEOUT = 2.5


def _api_base() -> str | None:
    u = (os.environ.get("BLACKFOX_KNOWLEDGE_API_URL") or "").strip().rstrip("/")
    return u or None


def _http_get_json(url: str) -> dict[str, Any] | None:
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=_API_TIMEOUT) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        data = json.loads(raw)
        return data if isinstance(data, dict) else None
    except Exception as exc:  # noqa: BLE001
        logger.warning("knowledge API call failed: %s", exc)
        return None


def _from_api(*, query: str = "", capability: str = "", product_id: str = "vps-to-vpn") -> dict[str, Any] | None:
    base = _api_base()
    if not base:
        return None
    cap = (capability or "").strip()
    q = (query or "").strip()
    if not cap and q:
        # Heuristic for common capability ids
        low = q.lower()
        if any(x in low for x in ("ip", "health", "valid", "سلامت", "آی‌پی", "ایپی")):
            cap = "ip-health"
    if cap:
        data = _http_get_json(f"{base}/feature/{urllib.parse.quote(cap)}")
        if data is not None:
            data.setdefault("via", "knowledge_api")
            # Normalize EXISTS shape
            if data.get("exists") is True or str(data.get("status", "")).upper() == "EXISTS":
                data["status"] = "EXISTS"
                data["exists"] = True
            return data
    if q:
        data = _http_get_json(f"{base}/knowledge/search?q={urllib.parse.quote(q)}")
        if data is not None:
            # Map search hits to EXISTS if feature notes present
            hits = data.get("results") or data.get("hits") or []
            exists = bool(hits)
            return {
                "status": "EXISTS" if exists else "UNKNOWN",
                "exists": exists,
                "hits": hits,
                "product_id": product_id,
                "via": "knowledge_api_search",
                "raw": data,
            }
    return None


def _try_bundled():
    try:
        from src.knowledge.implementation_lookup import (
            feature_lookup as _lookup,
            feature_lookup_prompt_block as _block,
        )
        return _lookup, _block
    except Exception as exc:  # noqa: BLE001
        logger.debug("bundled feature.lookup unavailable: %s", exc)
        return None, None


def _try_automation():
    root = Path((os.environ.get("BLACKFOX_AUTOMATION_ROOT") or "").strip() or _DEFAULT_AUTOMATION)
    if not (root / "services" / "feature_lookup").is_dir():
        return None, None, None
    root_s = str(root)
    if root_s not in sys.path:
        sys.path.insert(0, root_s)
    try:
        from services.feature_lookup import feature_lookup as _lookup
        from services.feature_lookup import feature_lookup_prompt_block as _block
        return _lookup, _block, root
    except Exception as exc:  # noqa: BLE001
        logger.warning("automation feature.lookup unavailable: %s", exc)
        return None, None, None


def feature_lookup(*, query: str = "", capability: str = "", product_id: str = "vps-to-vpn") -> dict[str, Any]:
    api = _from_api(query=query, capability=capability, product_id=product_id or "vps-to-vpn")
    if api is not None and (api.get("exists") or api.get("status") == "EXISTS" or api.get("hits") is not None):
        return api

    bl, _ = _try_bundled()
    if bl is not None:
        try:
            return bl(product_id=product_id or "vps-to-vpn", capability=capability, query=query)
        except Exception as exc:  # noqa: BLE001
            logger.warning("bundled feature.lookup failed: %s", exc)
    al, _, root = _try_automation()
    if al is not None:
        try:
            return al(product_id=product_id or "vps-to-vpn", capability=capability, query=query, root=root)
        except Exception as exc:  # noqa: BLE001
            logger.warning("automation feature.lookup failed: %s", exc)
    return {"status": "UNKNOWN", "exists": False, "hits": []}


def feature_lookup_prompt_block(query: str, *, product_id: str = "vps-to-vpn") -> str:
    r = feature_lookup(query=query, product_id=product_id)
    if r.get("status") == "EXISTS" and r.get("exists"):
        notes = str(r.get("notes") or "").strip()
        if notes:
            return notes[:4000]
        return f"Implementation EXISTS for query={query!r} product={product_id}."
    _, bb = _try_bundled()
    if bb is not None:
        try:
            return bb(query, product_id=product_id or "vps-to-vpn") or ""
        except Exception as exc:  # noqa: BLE001
            logger.warning("bundled prompt block failed: %s", exc)
    _, ab, root = _try_automation()
    if ab is not None:
        try:
            return ab(query, product_id=product_id or "vps-to-vpn", root=root) or ""
        except Exception as exc:  # noqa: BLE001
            logger.warning("automation prompt block failed: %s", exc)
    return ""


def has_implementation_exists(query: str, *, product_id: str = "vps-to-vpn") -> bool:
    r = feature_lookup(query=query, product_id=product_id)
    return bool(r.get("exists")) and r.get("status") == "EXISTS"
