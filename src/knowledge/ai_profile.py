"""Per-product Ask AI profile (small JSON next to catalog.json).

Canonical path: products/<product_id>/ai_profile.json

Product Ask AI must work from catalog + this file alone — it must NOT require
knowledge/AI_BOT_DATABASE or knowledge/AI_Knowledge_Base_Multilingual.

Schema (schema_version 1):
{
  "schema_version": 1,
  "product_id": "...",
  "reply_rules": {
    "stay_in_product": true,
    "use_howto": true,
    "attach_catalog_media": true,
    "language_from_question": true
  },
  "aliases": { "fa": [], "en": [] },
  "notes": "optional short support notes for AI"
}
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SCHEMA_VERSION = 1

DEFAULT_REPLY_RULES: dict[str, bool] = {
    "stay_in_product": True,
    "use_howto": True,
    "attach_catalog_media": True,
    "language_from_question": True,
}


def ai_profile_path(knowledge_root: Path, product_id: str) -> Path:
    from src.knowledge.product_catalogs import product_root

    return product_root(knowledge_root, product_id) / "ai_profile.json"


def _flatten_keywords(raw: Any) -> list[str]:
    out: list[str] = []
    if isinstance(raw, dict):
        for v in raw.values():
            out.extend(_flatten_keywords(v))
    elif isinstance(raw, (list, tuple)):
        for v in raw:
            out.extend(_flatten_keywords(v))
    elif raw is not None:
        s = str(raw).strip()
        if s:
            out.append(s)
    # de-dupe preserve order
    seen: set[str] = set()
    uniq: list[str] = []
    for item in out:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        uniq.append(item)
    return uniq


def _split_aliases_by_script(keywords: list[str]) -> dict[str, list[str]]:
    fa: list[str] = []
    en: list[str] = []
    for kw in keywords:
        if any("\u0600" <= ch <= "\u06ff" for ch in kw):
            fa.append(kw)
        else:
            en.append(kw)
    return {"fa": fa[:24], "en": en[:24]}


def default_ai_profile(
    product_id: str,
    catalog_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Sensible defaults from catalog title/keywords (no huge FAQ dumps)."""
    pid = (product_id or "").strip() or "product"
    data = catalog_data if isinstance(catalog_data, dict) else {}
    keywords = _flatten_keywords(data.get("keywords"))
    title = data.get("title") if isinstance(data.get("title"), dict) else {}
    for code in ("fa", "en"):
        t = str((title or {}).get(code) or "").strip()
        if t and t.lower() not in {k.lower() for k in keywords}:
            keywords.insert(0, t)
    if pid and pid.lower() not in {k.lower() for k in keywords}:
        keywords.insert(0, pid.replace("-", " "))
    aliases = _split_aliases_by_script(keywords)
    notes = str(data.get("ai_training_text") or "").strip()
    if len(notes) > 400:
        notes = notes[:400].rstrip() + "…"
    return {
        "schema_version": SCHEMA_VERSION,
        "product_id": pid,
        "reply_rules": dict(DEFAULT_REPLY_RULES),
        "aliases": aliases,
        "notes": notes,
    }


def _normalize_profile(raw: dict[str, Any], product_id: str) -> dict[str, Any]:
    base = default_ai_profile(product_id)
    rules_in = raw.get("reply_rules") if isinstance(raw.get("reply_rules"), dict) else {}
    rules = dict(DEFAULT_REPLY_RULES)
    for key in DEFAULT_REPLY_RULES:
        if key in rules_in:
            rules[key] = bool(rules_in[key])
    aliases_in = raw.get("aliases") if isinstance(raw.get("aliases"), dict) else {}
    aliases = {
        "fa": _flatten_keywords(aliases_in.get("fa") or base["aliases"]["fa"]),
        "en": _flatten_keywords(aliases_in.get("en") or base["aliases"]["en"]),
    }
    notes = str(raw.get("notes") if "notes" in raw else base.get("notes") or "").strip()
    return {
        "schema_version": int(raw.get("schema_version") or SCHEMA_VERSION),
        "product_id": str(raw.get("product_id") or product_id).strip() or product_id,
        "reply_rules": rules,
        "aliases": aliases,
        "notes": notes,
    }


def load_ai_profile(knowledge_root: Path, product_id: str) -> dict[str, Any]:
    """Load profile; missing/invalid file → safe catalog-only defaults."""
    pid = (product_id or "").strip()
    if not pid:
        return default_ai_profile("product")
    path = ai_profile_path(knowledge_root, pid)
    if not path.is_file():
        return default_ai_profile(pid)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("ai_profile load failed for %s: %s", pid, exc)
        return default_ai_profile(pid)
    if not isinstance(raw, dict):
        return default_ai_profile(pid)
    return _normalize_profile(raw, pid)


def ensure_ai_profile(
    knowledge_root: Path,
    product_id: str,
    *,
    catalog_data: dict[str, Any] | None = None,
    overwrite: bool = False,
) -> Path:
    """Create ai_profile.json if missing (or overwrite when requested)."""
    from src.knowledge.product_catalogs import load_product_raw

    pid = (product_id or "").strip()
    path = ai_profile_path(knowledge_root, pid)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file() and not overwrite:
        return path
    data = catalog_data
    if data is None:
        data = load_product_raw(knowledge_root, pid) or {}
    profile = default_ai_profile(pid, data)
    path.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def reply_rules(profile: dict[str, Any] | None) -> dict[str, bool]:
    rules = dict(DEFAULT_REPLY_RULES)
    if not isinstance(profile, dict):
        return rules
    raw = profile.get("reply_rules")
    if isinstance(raw, dict):
        for key in DEFAULT_REPLY_RULES:
            if key in raw:
                rules[key] = bool(raw[key])
    return rules


def all_aliases(profile: dict[str, Any] | None) -> list[str]:
    if not isinstance(profile, dict):
        return []
    aliases = profile.get("aliases") if isinstance(profile.get("aliases"), dict) else {}
    return _flatten_keywords(list(aliases.get("fa") or []) + list(aliases.get("en") or []))


def ai_profile_prompt_block(profile: dict[str, Any] | None) -> str:
    """Short block injected into Ask AI when a product is scoped."""
    if not isinstance(profile, dict):
        return ""
    rules = reply_rules(profile)
    lines = [
        f"Product AI profile: {profile.get('product_id') or ''}",
        "Reply rules:",
        f"- stay_in_product={rules.get('stay_in_product', True)} "
        "(answer only about this product; do not mix other catalogs)",
        f"- use_howto={rules.get('use_howto', True)} "
        "(prefer catalog feature howto / summary over inventing steps)",
        f"- attach_catalog_media={rules.get('attach_catalog_media', True)} "
        "(attach matching catalog screenshots when relevant)",
        f"- language_from_question={rules.get('language_from_question', True)} "
        "(reply in the user's question language)",
    ]
    aliases = all_aliases(profile)
    if aliases:
        lines.append("Product aliases / paraphrases: " + ", ".join(aliases[:20]))
    notes = str(profile.get("notes") or "").strip()
    if notes:
        lines.append("Operator notes: " + notes[:400])
    return "\n".join(lines).strip()


def expand_with_profile_aliases(query: str, profile: dict[str, Any] | None) -> str:
    """Append alias tokens so paraphrases map toward catalog vocabulary."""
    q = (query or "").strip()
    if not q or not isinstance(profile, dict):
        return q
    aliases = all_aliases(profile)
    if not aliases:
        return q
    q_low = q.lower()
    extra: list[str] = []
    for alias in aliases:
        a = alias.strip()
        if not a:
            continue
        if a.lower() in q_low:
            # already present; still keep short tokens for scoring
            continue
        # If any significant token of the alias appears, boost with full alias
        parts = [p for p in a.replace("-", " ").split() if len(p) >= 3]
        if parts and any(p.lower() in q_low for p in parts):
            extra.append(a)
    if not extra:
        return q
    return f"{q} {' '.join(extra[:8])}".strip()
