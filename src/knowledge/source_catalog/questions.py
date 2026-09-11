"""Normalize and cluster user questions. Questions are signals, not product truth."""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

_WS = re.compile(r"\s+")
_PUNCT = re.compile(r"[^\w\u0600-\u06ff\u0400-\u04ff\u4e00-\u9fff]+", re.UNICODE)

ALIASES = (
    ("چطور", "how"),
    ("چگونه", "how"),
    ("روش", "how"),
    ("دامنه", "domain"),
    ("domain", "domain"),
    ("ssh", "ssh"),
    ("لایسنس", "license"),
    ("cloudflare", "cloudflare"),
    ("کلودفلر", "cloudflare"),
)


def normalize_question(text: str) -> str:
    t = (text or "").strip().lower().replace("‌", "")
    t = _PUNCT.sub(" ", t)
    t = _WS.sub(" ", t).strip()
    for a, b in ALIASES:
        t = t.replace(a, b)
    return t


def fingerprint(text: str) -> str:
    return hashlib.sha256(normalize_question(text).encode("utf-8")).hexdigest()[:16]


def cluster_questions(samples: list[str], *, min_count: int = 3) -> list[dict[str, Any]]:
    buckets: dict[str, list[str]] = defaultdict(list)
    for s in samples:
        key = normalize_question(s)
        if len(key) < 6:
            continue
        buckets[key].append(s)
    out = []
    for key, items in sorted(buckets.items(), key=lambda x: -len(x[1])):
        if len(items) < min_count:
            continue
        out.append(
            {
                "norm": key,
                "fingerprint": fingerprint(key),
                "count": len(items),
                "samples": items[:5],
                "verified_against_source": False,
            }
        )
    return out


def load_edu_index(data_dir: Path) -> dict[str, Any]:
    path = data_dir / "edu_posts.json"
    if not path.is_file():
        return {"posts": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"posts": []}
    if not isinstance(data, dict):
        return {"posts": []}
    return data


def is_duplicate_post(data_dir: Path, fingerprint_s: str, content_fp: str) -> bool:
    idx = load_edu_index(data_dir)
    for post in idx.get("posts") or []:
        if not isinstance(post, dict):
            continue
        if post.get("question_fp") == fingerprint_s or post.get("content_fp") == content_fp:
            return True
    return False


def record_post(data_dir: Path, *, question_fp: str, content_fp: str, langs: list[str]) -> None:
    path = data_dir / "edu_posts.json"
    idx = load_edu_index(data_dir)
    posts = list(idx.get("posts") or [])
    posts.append({"question_fp": question_fp, "content_fp": content_fp, "langs": langs})
    path.write_text(json.dumps({"posts": posts[-500:]}, ensure_ascii=False, indent=2), encoding="utf-8")


def load_forum_topics(knowledge_root: Path) -> dict[str, int | None]:
    path = knowledge_root / "group_community.json"
    empty: dict[str, int | None] = {"fa": None, "en": None, "ru": None, "zh": None}
    if not path.is_file():
        return empty
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return empty
    raw = data.get("forum_topics") if isinstance(data, dict) else None
    if not isinstance(raw, dict):
        return empty
    out: dict[str, int | None] = {}
    for lang in ("fa", "en", "ru", "zh"):
        val = raw.get(lang)
        if val is None or val == "":
            out[lang] = None
        else:
            try:
                out[lang] = int(val)
            except (TypeError, ValueError):
                out[lang] = None
    return out
