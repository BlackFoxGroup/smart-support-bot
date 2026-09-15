# -*- coding: utf-8 -*-
"""Phase 2 adapter: catalog first, then Implementation feature.lookup (bundled)."""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_AUTOMATION = Path(r"F:\Automation Black fox")


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
