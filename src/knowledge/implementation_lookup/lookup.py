# -*- coding: utf-8 -*-
"""Bundled Implementation feature.lookup for Smart Support Bot (Phase 2)."""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

@dataclass(slots=True)
class FeatureHit:
    capability_id: str
    exists: bool
    status: str
    source: str
    notes: str
    product_id: str = "vps-to-vpn"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

_ALIAS = {
    "ip-health": (
        "ip", "health", "validity", "valid", "netcheck", "reach", "probe", "diagnose", "healthy",
        "سلامت", "اعتبار", "آیپی", "ایپی", "آی پی", "چک آیپی", "بررسی آیپی",
        "ip health", "ip validity", "check ip",
    ),
}

def features_dir() -> Path:
    return Path(__file__).resolve().parent / "features"

def _parse_feature_md(path: Path) -> FeatureHit:
    text = path.read_text(encoding="utf-8", errors="replace")
    exists = bool(re.search(r"\bEXISTS\b", text))
    notes = text.strip()
    if len(notes) > 1800:
        notes = notes[:1800] + "\n…"
    return FeatureHit(
        capability_id=path.stem,
        exists=exists,
        status="EXISTS" if exists else "UNKNOWN",
        source=str(path),
        notes=notes,
    )

def load_features() -> list[FeatureHit]:
    d = features_dir()
    if not d.is_dir():
        return []
    return [_parse_feature_md(p) for p in sorted(d.glob("*.md"))]

def _norm(s: str) -> str:
    t = (s or "").lower().replace("\u200c", " ")
    return re.sub(r"\s+", " ", t).strip()

def feature_lookup(*, product_id: str = "vps-to-vpn", capability: str = "", query: str = "") -> dict[str, Any]:
    all_feats = load_features()
    if not all_feats:
        return {"status": "UNKNOWN", "reason": "no_feature_docs", "hits": [], "exists": False}
    cap = _norm(capability)
    blob = f"{cap} {_norm(query)}".strip()
    matched: list[FeatureHit] = []
    for feat in all_feats:
        if cap and (cap == feat.capability_id or cap.replace("_", "-") == feat.capability_id):
            matched.append(feat); continue
        aliases = _ALIAS.get(feat.capability_id, ())
        if blob and any(a in blob for a in aliases):
            matched.append(feat); continue
        if blob and feat.capability_id.replace("-", " ") in blob:
            matched.append(feat)
    if not matched:
        return {"status": "UNKNOWN", "product_id": product_id, "capability": capability, "exists": False, "hits": []}
    primary = next((h for h in matched if h.exists), matched[0])
    return {
        "status": primary.status,
        "product_id": product_id or primary.product_id,
        "capability": primary.capability_id,
        "exists": primary.exists,
        "source": primary.source,
        "notes": primary.notes,
        "hits": [h.as_dict() for h in matched],
    }

def feature_lookup_prompt_block(query: str, *, product_id: str = "vps-to-vpn") -> str:
    result = feature_lookup(product_id=product_id, query=query)
    if result.get("status") != "EXISTS" or not result.get("exists"):
        return ""
    notes = (result.get("notes") or "").strip()
    return (
        "Implementation feature.lookup (AUTHORITATIVE — do NOT say this capability is missing "
        "just because Support Catalog omitted it):\n"
        f"capability={result.get('capability')} status=EXISTS\n"
        f"source={result.get('source')}\n"
        f"{notes}"
    )
