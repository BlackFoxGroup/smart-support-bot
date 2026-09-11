"""Authoritative markdown index of catalog files for the AI + bot send path."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from src.knowledge.catalog_builder import IMAGE_EXTS
from src.knowledge.product_catalogs import get_product_catalogs

logger = logging.getLogger(__name__)


def wants_send_media(query: str) -> bool:
    """True when the user asks to see/send a catalog photo now."""
    q = (query or "").strip().lower().replace("‌", "")
    if not q:
        return False
    hints = (
        "ببینم",
        "بفرست",
        "بفرستش",
        "ارسالش",
        "ارسال کن",
        "همینجا",
        "نشون بده",
        "نشان بده",
        "عکسش",
        "عکس از",
        "عکس داری",
        "عکس هم",
        "تصویر",
        "اسکرین",
        "screenshot",
        "show me",
        "send it",
        "send the",
        "send photo",
        "send the photo",
        "send the image",
    )
    return any(h in q for h in hints) or wants_overview_ui(query)


def wants_overview_ui(query: str) -> bool:
    """True when the user asks for a general product UI / app screenshot."""
    q = (query or "").strip().lower().replace("‌", "")
    if not q:
        return False
    photo = any(
        x in q
        for x in ("عکس", "تصویر", "اسکرین", "screenshot", "ui", "رابط")
    )
    app = any(
        x in q
        for x in ("برنامه", "نرم افزار", "نرم‌افزار", "محصول", "ویندوز", "installer", "vpn", "نما", "رابط")
    )
    ask = any(
        x in q
        for x in ("داری", "دارید", "دارین", "هست", "بفرست", "ببینم", "نشان", "نشون")
    )
    return bool(photo and (app or ask))


def listed_image_paths(project_root: Path, product_id: str, *, limit: int = 8) -> list[Path]:
    """Resolve catalog + folder images for one product (existing files only)."""
    pid = (product_id or "").strip()
    if not pid:
        return []
    root = project_root.resolve()
    seen: set[str] = set()
    out: list[Path] = []

    def _add(path: Path) -> None:
        try:
            resolved = path.resolve()
        except OSError:
            return
        if not resolved.is_file():
            return
        key = str(resolved).lower()
        if key in seen:
            return
        seen.add(key)
        out.append(resolved)

    for cat in get_product_catalogs():
        if cat.product_id != pid:
            continue
        for media in cat.media or []:
            if not isinstance(media, dict):
                continue
            rel = str(media.get("path") or "").strip().replace("\\", "/")
            if not rel:
                continue
            _add(root / rel)

    folder = root / "media" / "catalogs" / pid
    if folder.is_dir():
        for path in sorted(folder.iterdir()):
            if path.suffix.lower() in IMAGE_EXTS:
                _add(path)
    return out[: max(1, limit)]


def build_catalog_index_markdown(*, product_id: str | None = None) -> str:
    """Human/AI readable index of catalog photos and how the bot sends them."""
    catalogs = get_product_catalogs()
    if product_id:
        catalogs = [c for c in catalogs if c.product_id == product_id]
    lines = [
        "# Catalog media index",
        "",
        "This file is the source of truth for catalog files.",
        "The Telegram bot can send these files with sendPhoto.",
        "If a file is listed here, it exists. Never say the catalog has no photo.",
        "Do not invent files that are not listed.",
        "When the user asks to see or send a photo, the bot attaches the file;",
        "the AI only describes it and must not claim it cannot send files.",
        "",
    ]
    if not catalogs:
        lines.append("No product catalogs are loaded.")
        return "\n".join(lines) + "\n"

    for cat in catalogs:
        title = (cat.title or {}).get("fa") or (cat.title or {}).get("en") or cat.product_id
        lines.append(f"## {cat.product_id} — {title}")
        media = [m for m in (cat.media or []) if isinstance(m, dict)]
        images = [
            m
            for m in media
            if str(m.get("path") or "").strip()
            and Path(str(m.get("path"))).suffix.lower() in IMAGE_EXTS
        ]
        lines.append(f"photo_count: {len(images)}")
        lines.append(f"folder: media/catalogs/{cat.product_id}/")
        if not images:
            lines.append("- (no photos indexed yet)")
            lines.append("")
            continue
        for media in images:
            rel = str(media.get("path") or "").replace("\\", "/")
            slot = str(media.get("slot") or media.get("id") or Path(rel).stem)
            note = str(media.get("ai_guide") or media.get("note") or "").strip()
            title_m = ""
            raw_title = media.get("title")
            if isinstance(raw_title, dict):
                title_m = str(raw_title.get("fa") or raw_title.get("en") or "").strip()
            topics = media.get("topics") if isinstance(media.get("topics"), list) else []
            topic_s = ", ".join(str(t) for t in topics[:8] if t)
            lines.append(f"- file: {rel}")
            lines.append(f"  slot: {slot}")
            if title_m:
                lines.append(f"  title: {title_m}")
            if topic_s:
                lines.append(f"  topics: {topic_s}")
            if note:
                lines.append(f"  note: {note}")
            lines.append("  access: Telegram sendPhoto from this path on the bot server")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_catalog_indexes(knowledge_root: Path, project_root: Path) -> list[Path]:
    """Write master + per-product markdown indexes. Safe to call after every upload."""
    written: list[Path] = []
    catalogs_dir = knowledge_root / "product_catalogs"
    guides_dir = knowledge_root / "product_guides"
    catalogs_dir.mkdir(parents=True, exist_ok=True)
    guides_dir.mkdir(parents=True, exist_ok=True)

    master = catalogs_dir / "CATALOG_INDEX.md"
    try:
        master.write_text(build_catalog_index_markdown(), encoding="utf-8")
        written.append(master)
    except OSError as exc:
        logger.warning("cannot write %s: %s", master, exc)

    for cat in get_product_catalogs():
        body = build_catalog_index_markdown(product_id=cat.product_id)
        guide = guides_dir / f"{cat.product_id}-catalog-index.md"
        media_md = project_root / "media" / "catalogs" / cat.product_id / "CATALOG_INDEX.md"
        for path in (guide, media_md):
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(body, encoding="utf-8")
                written.append(path)
            except OSError as exc:
                logger.warning("cannot write %s: %s", path, exc)
    logger.info("catalog index markdown written: %s files", len(written))
    return written


def media_caption(media: dict[str, Any] | None, *, lang: str = "fa") -> str:
    if not isinstance(media, dict):
        return "تصویر کاتالوگ محصول" if (lang or "").startswith("fa") else "Product catalog photo"
    title = media.get("title")
    if isinstance(title, dict):
        label = str(title.get(lang) or title.get("en") or title.get("fa") or "").strip()
    else:
        label = str(title or "").strip()
    note = str(media.get("ai_guide") or media.get("note") or "").strip()
    if label and note:
        return f"{label}\n{note}"[:1000]
    return (label or note or (
        "تصویر کاتالوگ محصول" if (lang or "").startswith("fa") else "Product catalog photo"
    ))[:1000]
