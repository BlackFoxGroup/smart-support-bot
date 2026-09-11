"""Filename/feature classification. Low confidence stays needs_review."""

from __future__ import annotations

import re
from typing import Any

_SPLIT = re.compile(r"[^a-z0-9]+")


def classify_filename(filename: str, feature_ids: list[str], *, threshold: float = 0.7) -> dict[str, Any]:
    tokens = [t for t in _SPLIT.split((filename or "").lower()) if len(t) >= 3]
    scored: list[tuple[float, str]] = []
    for fid in feature_ids:
        parts = [p for p in fid.lower().replace("-", "_").split("_") if p]
        if not parts:
            continue
        hits = sum(1 for p in parts if p in tokens or any(p in t or t in p for t in tokens))
        score = hits / max(1, len(parts))
        if any(p in (filename or "").lower() for p in parts):
            score = max(score, 0.5)
        scored.append((score, fid))
    scored.sort(reverse=True)
    best_s, best_id = scored[0] if scored else (0.0, "")
    auto = best_s >= threshold and bool(best_id)
    candidates = [
        {"feature_id": fid, "confidence": round(score, 3), "percent": int(round(score * 100))}
        for score, fid in scored
        if score > 0
    ][:8]
    return {
        "feature_ids": [best_id] if best_id and best_s >= 0.4 else [],
        "confidence": round(best_s, 3),
        "auto_assigned": auto,
        "needs_review": not auto,
        "candidates": candidates,
    }
