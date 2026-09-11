"""python -m src.knowledge.source_catalog scan|validate|faq"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.config import KNOWLEDGE_ROOT, PROJECT_ROOT
from src.knowledge.source_catalog.faq_canonical import build_canonical
from src.knowledge.source_catalog.pipeline import load_matrix, run_sync
from src.knowledge.source_catalog.questions import load_forum_topics


def default_source() -> Path:
    import os

    raw = (os.getenv("VPS_TO_VPN_SOURCE") or r"F:\VPS to VPN").strip()
    return Path(raw)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Live VPS to VPN catalog scan")
    parser.add_argument("cmd", choices=["scan", "validate", "faq", "topics"])
    parser.add_argument("--source", type=Path, default=default_source())
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    data_dir = PROJECT_ROOT / "data"
    if args.cmd == "faq":
        payload = build_canonical(KNOWLEDGE_ROOT)
        print(json.dumps({"canonical_count": payload.get("count")}, ensure_ascii=False))
        return 0
    if args.cmd == "topics":
        print(json.dumps(load_forum_topics(KNOWLEDGE_ROOT), ensure_ascii=False))
        return 0
    if args.cmd == "validate":
        matrix = load_matrix(KNOWLEDGE_ROOT)
        if not matrix:
            print("NO_MATRIX", file=sys.stderr)
            return 2
        val = matrix.get("validation") or {}
        print(json.dumps({"missing": val.get("missing"), "stats": matrix.get("stats")}, ensure_ascii=False, indent=2))
        return 0 if not val.get("missing") else 1
    payload = run_sync(args.source, KNOWLEDGE_ROOT, data_dir, force=args.force)
    val = payload.get("validation") or {}
    print(
        json.dumps(
            {
                "stats": payload.get("stats"),
                "catalog_version": payload.get("catalog_version"),
                "missing": val.get("missing"),
                "extra": val.get("extra"),
                "outdated": len(val.get("outdated") or []),
                "deprecated": val.get("deprecated"),
                "scan_errors": len(val.get("scan_errors") or []),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if not val.get("missing") else 1


if __name__ == "__main__":
    raise SystemExit(main())
