"""AI image description/classification. AI is not source of truth."""

from __future__ import annotations

import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Any

from src.knowledge.source_catalog.classify import classify_filename
from src.knowledge.source_catalog.pipeline import load_matrix
from src.knowledge.source_catalog.store import load_media_index, save_media_index

logger = logging.getLogger(__name__)

LOW = 0.7


def _feature_ids(knowledge_root: Path, product_id: str) -> list[str]:
    from src.knowledge.product_catalogs import get_product

    feats: list[str] = []
    prod = get_product(product_id)
    if prod:
        feats.extend(str(f.get("id")) for f in prod.features if isinstance(f, dict) and f.get("id"))
    matrix = load_matrix(knowledge_root)
    if matrix:
        feats.extend(str(x.get("id")) for x in matrix.get("features") or [] if isinstance(x, dict) and x.get("id"))
    return sorted({f for f in feats if f})


def _extract_json(text: str) -> dict[str, Any] | None:
    raw = (text or "").strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        m = re.search(r"\{[\s\S]*\}", raw)
        if not m:
            return None
        try:
            data = json.loads(m.group(0))
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            return None


async def _ai_describe(image_bytes: bytes, product_id: str, filename: str, feature_ids: list[str]) -> dict[str, Any] | None:
    try:
        from src.ai.client import AIClient
        from src.config import load_settings
    except Exception:
        return None
    try:
        settings = load_settings()
        ai = AIClient(settings)
    except Exception:
        return None
    if not hasattr(ai, "chat_with_images"):
        return None
    raw = image_bytes
    try:
        from io import BytesIO

        from PIL import Image

        im = Image.open(BytesIO(image_bytes)).convert("RGB")
        buf = BytesIO()
        im.save(buf, format="JPEG", quality=80)
        raw = buf.getvalue()
    except Exception:
        raw = image_bytes
    prompt = (
        "Describe a product UI screenshot for support mapping.\n"
        f"product_id={product_id} filename={filename}\n"
        f"Known feature ids: {', '.join(feature_ids[:60])}\n"
        "Return ONLY JSON keys: description, visible_ui_elements (array), "
        "likely_feature, likely_screen, keywords (array), "
        "candidates (array of {feature_id, confidence 0-1}). "
        "confidence must be honest. Do not invent feature ids."
    )
    try:
        answer = await ai.chat_with_images(
            prompt,
            [raw],
            system="Output ONLY valid JSON. Classification only. Not source of truth.",
            max_images=1,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("image AI analysis failed: %s", exc)
        return None
    finally:
        try:
            await ai.close()
        except Exception:
            pass
    return _extract_json(answer or "")


def analyze_media(knowledge_root: Path, data_dir: Path, product_id: str, media_id: str) -> dict[str, Any]:
    feats = _feature_ids(knowledge_root, product_id)
    index = load_media_index(data_dir, product_id)
    item = next((i for i in index.get("items") or [] if str(i.get("media_id")) == media_id), None)
    if not item:
        return {"ok": False, "error": "media not found"}
    fn = classify_filename(str(item.get("filename") or ""), feats)
    ai_data: dict[str, Any] | None = None
    path = Path(str(item.get("path") or ""))
    if path.is_file():
        try:
            ai_data = asyncio.run(_ai_describe(path.read_bytes(), product_id, path.name, feats))
        except RuntimeError:
            ai_data = None
        except Exception as exc:  # noqa: BLE001
            logger.warning("analyze_media: %s", exc)
    candidates = list(fn.get("candidates") or [])
    if isinstance(ai_data, dict):
        extra = ai_data.get("candidates")
        if isinstance(extra, list):
            for row in extra:
                if not isinstance(row, dict):
                    continue
                fid = str(row.get("feature_id") or "")
                if fid and fid in feats:
                    candidates.append(
                        {
                            "feature_id": fid,
                            "confidence": float(row.get("confidence") or 0),
                            "percent": int(round(float(row.get("confidence") or 0) * 100)),
                        }
                    )
        item["description"] = str(ai_data.get("description") or item.get("description") or "")
        item["visible_ui"] = ai_data.get("visible_ui_elements") or []
        item["likely_screen"] = str(ai_data.get("likely_screen") or "")
        item["keywords"] = ai_data.get("keywords") if isinstance(ai_data.get("keywords"), list) else item.get("keywords")
        likely = str(ai_data.get("likely_feature") or "")
        if likely:
            item["ai_likely_feature"] = likely
    merged: dict[str, dict[str, Any]] = {}
    for c in candidates:
        fid = str(c.get("feature_id") or "")
        if not fid:
            continue
        prev = merged.get(fid)
        if not prev or float(c.get("confidence") or 0) > float(prev.get("confidence") or 0):
            merged[fid] = {
                "feature_id": fid,
                "confidence": round(float(c.get("confidence") or 0), 3),
                "percent": int(c.get("percent") or round(float(c.get("confidence") or 0) * 100)),
            }
    ranked = sorted(merged.values(), key=lambda x: x["confidence"], reverse=True)
    best = ranked[0] if ranked else {"confidence": 0.0, "feature_id": ""}
    item["classify_candidates"] = ranked
    item["classify_confidence"] = best.get("confidence") or 0
    item["needs_review"] = float(best.get("confidence") or 0) < LOW
    item["ai_source"] = "classification"
    save_media_index(data_dir, product_id, index)
    return {
        "ok": True,
        "media_id": media_id,
        "description": item.get("description") or "",
        "visible_ui": item.get("visible_ui") or [],
        "likely_feature": item.get("ai_likely_feature") or best.get("feature_id"),
        "likely_screen": item.get("likely_screen") or "",
        "keywords": item.get("keywords") or [],
        "confidence": item.get("classify_confidence"),
        "candidates": ranked,
        "auto_assign": False,
        "needs_review": item["needs_review"],
        "ai_available": bool(ai_data),
    }


def apply_mapping_decision(
    data_dir: Path,
    product_id: str,
    media_id: str,
    *,
    action: str,
    feature_ids: list[str] | None = None,
) -> bool:
    index = load_media_index(data_dir, product_id)
    for item in index.get("items") or []:
        if str(item.get("media_id")) != media_id:
            continue
        if action == "reject":
            item["feature_ids"] = []
            item["catalog_feature_id"] = ""
            item["needs_review"] = True
            item["status"] = "UNMAPPED"
        elif action == "accept":
            cand = item.get("classify_candidates") or []
            pick = []
            if cand and float((cand[0] or {}).get("confidence") or 0) >= LOW:
                pick = [str(cand[0]["feature_id"])]
            if feature_ids:
                pick = feature_ids
            if not pick:
                item["needs_review"] = True
            else:
                item["feature_ids"] = pick
                item["catalog_feature_id"] = pick[0]
                item["needs_review"] = False
                if item.get("status") == "UNMAPPED":
                    item["status"] = "LOCAL_ONLY"
        elif action == "change" and feature_ids:
            item["feature_ids"] = feature_ids
            item["catalog_feature_id"] = feature_ids[0]
            item["needs_review"] = False
            if item.get("status") == "UNMAPPED":
                item["status"] = "LOCAL_ONLY"
        save_media_index(data_dir, product_id, index)
        return True
    return False
