"""Canonical FAQ: English technical truth, other languages are renderings."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

Q_RE = re.compile(r"^###\s+(Q\d+)\s*[—\-:]?\s*(.*)$", re.M)

CANONICAL_NAME = "faq_canonical.json"


def parse_faq_md(text: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    parts = re.split(r"(?=^###\s+Q\d+)", text, flags=re.M)
    for part in parts:
        part = part.strip()
        if not part.startswith("###"):
            continue
        first, _, rest = part.partition("\n")
        m = re.match(r"^###\s+(Q\d+)\s*[—\-:]?\s*(.*)$", first.strip())
        if not m:
            continue
        qid, qtext = m.group(1), m.group(2).strip()
        items.append({"id": qid, "question": qtext, "answer": rest.strip()})
    return items


def build_canonical(knowledge_root: Path) -> dict[str, Any]:
    base = knowledge_root / "AI_Knowledge_Base_Multilingual"
    en_path = base / "English" / "FAQ_EN.md"
    langs = {
        "en": en_path,
        "fa": base / "Persian" / "FAQ_FA.md",
        "ru": base / "Russian" / "FAQ_RU.md",
        "zh": base / "Chinese" / "FAQ_ZH.md",
    }
    parsed = {code: parse_faq_md(p.read_text(encoding="utf-8")) if p.is_file() else [] for code, p in langs.items()}
    by_en = {item["id"]: item for item in parsed["en"]}
    entries: list[dict[str, Any]] = []
    for qid, src in by_en.items():
        renderings: dict[str, dict[str, str]] = {
            "en": {"question": src["question"], "answer": src["answer"]},
        }
        for code in ("fa", "ru", "zh"):
            match = next((x for x in parsed[code] if x["id"] == qid), None)
            if match:
                renderings[code] = {"question": match["question"], "answer": match["answer"]}
        entries.append(
            {
                "id": qid,
                "canonical_lang": "en",
                "question": src["question"],
                "answer": src["answer"],
                "renderings": renderings,
                "source_verified": False,
                "from_user_question": False,
            }
        )
    payload = {
        "schema_version": "1.0",
        "canonical_lang": "en",
        "count": len(entries),
        "entries": entries,
    }
    out = knowledge_root / "source_catalog" / CANONICAL_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def load_canonical(knowledge_root: Path) -> dict[str, Any] | None:
    path = knowledge_root / "source_catalog" / CANONICAL_NAME
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def render_faq(entry: dict[str, Any], lang: str) -> tuple[str, str]:
    block = (entry.get("renderings") or {}).get(lang) or (entry.get("renderings") or {}).get("en") or {}
    q = str(block.get("question") or entry.get("question") or "")
    a = str(block.get("answer") or entry.get("answer") or "")
    return q, a
