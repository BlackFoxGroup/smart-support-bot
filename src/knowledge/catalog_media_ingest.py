"""Ingest admin-uploaded files into product catalog media + refresh searchable index."""

from __future__ import annotations

import json
import logging
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Awaitable, Callable

from src.knowledge.catalog_builder import IMAGE_EXTS, TEXT_EXTS
from src.knowledge.catalog_rag import enrich_media_entry_from_filename
from src.knowledge.product_catalogs import (
    load_product_catalogs,
    product_json_path,
    product_media_dir,
    product_media_relative,
    resolve_product_json_path,
)
from src.operation_control import raise_if_stopped

logger = logging.getLogger(__name__)

AiVision = Callable[..., Awaitable[str]]


@dataclass(slots=True)
class IngestResult:
    ok: bool
    product_id: str
    files_added: list[str]
    message_fa: str
    message_en: str
    detail: str = ""


def _extract_json(text: str) -> dict[str, Any] | None:
    raw = (text or "").strip()
    if not raw:
        return None
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


async def _ai_tag_image(
    *,
    ai: Any,
    image_bytes: bytes,
    product_id: str,
    filename: str,
    feature_ids: list[str],
) -> dict[str, Any] | None:
    if ai is None or not hasattr(ai, "chat_with_images"):
        return None
    feats = ", ".join(feature_ids[:40]) or "(none)"
    prompt = (
        "You tag a product UI teaching screenshot for a support bot catalog.\n"
        f"product_id={product_id}\nfilename={filename}\n"
        f"Known feature ids: {feats}\n"
        "Return ONLY JSON with keys: slot (kebab-case), title_en, title_fa, "
        "description_en, description_fa, topics (string array), feature_ids "
        "(subset of known ids if possible), stage (one of setup|ops|mesh|domain|ai|other)."
    )
    try:
        raise_if_stopped()
        answer = await ai.chat_with_images(
            prompt,
            [image_bytes],
            system=(
                "Output ONLY valid JSON. No markdown. "
                "Prefer linking feature_ids to known ids when the screenshot matches."
            ),
            max_images=1,
        )
        raise_if_stopped()
    except Exception as exc:  # noqa: BLE001
        logger.warning("media AI tag failed: %s", exc)
        return None
    data = _extract_json(answer or "")
    return data if isinstance(data, dict) else None


def _merge_ai_tag(base: dict[str, Any], tagged: dict[str, Any] | None) -> dict[str, Any]:
    if not tagged:
        return base
    out = dict(base)
    slot = str(tagged.get("slot") or "").strip()
    if slot:
        out["slot"] = re.sub(r"[^a-z0-9\-]+", "-", slot.lower()).strip("-") or out["slot"]
        out["id"] = out["slot"]
    title_en = str(tagged.get("title_en") or "").strip()
    title_fa = str(tagged.get("title_fa") or title_en).strip()
    if title_en or title_fa:
        out["title"] = {
            "fa": title_fa or title_en,
            "en": title_en or title_fa,
            "ru": title_en or title_fa,
            "zh": title_en or title_fa,
        }
    desc_en = str(tagged.get("description_en") or "").strip()
    desc_fa = str(tagged.get("description_fa") or desc_en).strip()
    if desc_en or desc_fa:
        out["description"] = {
            "fa": desc_fa or desc_en,
            "en": desc_en or desc_fa,
            "ru": desc_en or desc_fa,
            "zh": desc_en or desc_fa,
        }
        out["note"] = desc_en or desc_fa
    topics = tagged.get("topics")
    if isinstance(topics, list):
        out["topics"] = [str(t).strip() for t in topics if str(t).strip()][:12]
    fids = tagged.get("feature_ids")
    if isinstance(fids, list):
        out["feature_ids"] = [str(t).strip() for t in fids if str(t).strip()][:8]
    stage = str(tagged.get("stage") or "").strip()
    if stage:
        out["stage"] = stage
    return out


async def ingest_files_to_product_catalog(
    *,
    knowledge_root: Path,
    project_root: Path,
    product_id: str,
    source_files: list[Path],
    ai: Any | None = None,
    ai_guides: dict[str, str] | None = None,
) -> IngestResult:
    """Copy uploads into products/<product_id>/media, update JSON, reload cache."""
    pid = (product_id or "").strip()
    if not pid:
        return IngestResult(
            ok=False,
            product_id="",
            files_added=[],
            message_fa="محصول مشخص نیست. اول یک محصول را از بخش Products باز کنید.",
            message_en="No product selected. Open a product in Products first.",
            detail="missing product_id",
        )
    catalog_path = resolve_product_json_path(knowledge_root, pid) or product_json_path(
        knowledge_root, pid
    )
    if not catalog_path.is_file():
        return IngestResult(
            ok=False,
            product_id=pid,
            files_added=[],
            message_fa=f"فایل کاتالوگ محصول «{pid}» پیدا نشد.",
            message_en=f"Catalog file for product «{pid}» was not found.",
            detail=f"missing {catalog_path}",
        )

    try:
        data = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return IngestResult(
            ok=False,
            product_id=pid,
            files_added=[],
            message_fa="خواندن JSON کاتالوگ ناموفق بود.",
            message_en="Failed to read catalog JSON.",
            detail=str(exc),
        )

    feature_ids = [
        str(f.get("id") or "").strip()
        for f in (data.get("features") or [])
        if isinstance(f, dict) and str(f.get("id") or "").strip()
    ]
    media_list = data.get("media") if isinstance(data.get("media"), list) else []
    media_list = [m for m in media_list if isinstance(m, dict)]
    existing_names = {
        Path(str(m.get("path") or "")).name.lower()
        for m in media_list
        if str(m.get("path") or "").strip()
    }

    out_dir = product_media_dir(project_root, pid)
    added: list[str] = []
    errors: list[str] = []

    for src in source_files:
        try:
            if not src.is_file():
                errors.append(f"missing:{src.name}")
                continue
            suf = src.suffix.lower()
            # Text docs: keep beside media for future rebuilds, but only index images for Ask AI photos
            if suf in TEXT_EXTS:
                dest_txt = out_dir / src.name
                shutil.copy2(src, dest_txt)
                added.append(str(dest_txt.relative_to(project_root)).replace("\\", "/"))
                continue
            if suf not in IMAGE_EXTS:
                errors.append(f"unsupported:{src.name}")
                continue
            # Unique name if collision
            dest = out_dir / src.name
            if dest.exists():
                dest = out_dir / f"{src.stem}-{src.stat().st_mtime_ns}{src.suffix}"
            shutil.copy2(src, dest)
            rel = product_media_relative(pid, dest.name)
            if dest.name.lower() in existing_names:
                # replace path entry if same name
                media_list = [
                    m
                    for m in media_list
                    if Path(str(m.get("path") or "")).name.lower() != dest.name.lower()
                ]
            entry = enrich_media_entry_from_filename(
                dest.name, product_id=pid, index=len(media_list)
            )
            entry["path"] = rel
            guide = (ai_guides or {}).get(src.name.lower()) or (ai_guides or {}).get(dest.name.lower())
            if guide:
                entry["ai_guide"] = guide
                entry["note"] = guide
            try:
                tagged = await _ai_tag_image(
                    ai=ai,
                    image_bytes=dest.read_bytes(),
                    product_id=pid,
                    filename=dest.name,
                    feature_ids=feature_ids,
                )
                entry = _merge_ai_tag(entry, tagged)
                entry["path"] = rel
                if guide:
                    entry["ai_guide"] = guide
                    if not str(entry.get("note") or "").strip():
                        entry["note"] = guide
            except Exception as exc:  # noqa: BLE001
                errors.append(f"tag:{dest.name}:{type(exc).__name__}")
            media_list.append(entry)
            existing_names.add(dest.name.lower())
            added.append(rel)
        except Exception as exc:  # noqa: BLE001
            logger.exception("ingest failed for %s", src)
            errors.append(f"{src.name}:{exc}")

    if not added and errors:
        return IngestResult(
            ok=False,
            product_id=pid,
            files_added=[],
            message_fa="آپلود به کاتالوگ ناموفق بود.",
            message_en="Catalog media upload failed.",
            detail="; ".join(errors),
        )

    data["media"] = media_list
    try:
        catalog_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        load_product_catalogs(knowledge_root)
        from src.knowledge.catalog_index import write_catalog_indexes
        from src.knowledge.refresh import notify_knowledge_changed

        write_catalog_indexes(knowledge_root, project_root)
        notify_knowledge_changed()
    except Exception as exc:  # noqa: BLE001
        return IngestResult(
            ok=False,
            product_id=pid,
            files_added=added,
            message_fa="فایل‌ها کپی شدند ولی ذخیره/ایندکس کاتالوگ شکست خورد.",
            message_en="Files copied but saving/indexing the catalog failed.",
            detail=str(exc),
        )

    fix_hint = ""
    if errors:
        fix_hint = (
            f"\nنکته: بخشی با هشدار انجام شد: {'; '.join(errors[:3])}"
        )
    msg_fa = (
        "روند آپدیت کاتالوگ با موفقیت انجام شد.\n"
        f"محصول: {pid}\n"
        f"فایل‌های اضافه‌شده: {len(added)}\n"
        "منابع کاتالوگ برای Ask AI دوباره ایندکس شدند."
        + fix_hint
    )
    msg_en = (
        "Catalog update completed successfully.\n"
        f"Product: {pid}\n"
        f"Files added: {len(added)}\n"
        "Catalog sources were re-indexed for Ask AI."
        + (f"\nNotes: {'; '.join(errors[:3])}" if errors else "")
    )
    return IngestResult(
        ok=True,
        product_id=pid,
        files_added=added,
        message_fa=msg_fa,
        message_en=msg_en,
        detail="; ".join(errors),
    )


async def reindex_product_media_with_ai(
    *,
    knowledge_root: Path,
    project_root: Path,
    product_id: str,
    ai: Any,
) -> IngestResult:
    """Re-tag existing media entries for a product (no new uploads)."""
    catalog_path = resolve_product_json_path(
        knowledge_root, product_id
    ) or product_json_path(knowledge_root, product_id)
    if not catalog_path.is_file():
        return IngestResult(
            ok=False,
            product_id=product_id,
            files_added=[],
            message_fa="کاتالوگ پیدا نشد.",
            message_en="Catalog not found.",
        )
    try:
        data = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return IngestResult(
            ok=False,
            product_id=product_id,
            files_added=[],
            message_fa="خواندن کاتالوگ ناموفق.",
            message_en="Failed to read catalog.",
            detail=str(exc),
        )
    feature_ids = [
        str(f.get("id") or "").strip()
        for f in (data.get("features") or [])
        if isinstance(f, dict) and str(f.get("id") or "").strip()
    ]
    media_list = data.get("media") if isinstance(data.get("media"), list) else []
    updated = 0
    errors: list[str] = []
    new_media: list[dict[str, Any]] = []
    for i, media in enumerate(media_list):
        if not isinstance(media, dict):
            continue
        rel = str(media.get("path") or "").strip().replace("\\", "/")
        path = project_root / rel
        if not rel or not path.is_file() or path.suffix.lower() not in IMAGE_EXTS:
            new_media.append(media)
            continue
        base = enrich_media_entry_from_filename(path.name, product_id=product_id, index=i)
        base.update({k: v for k, v in media.items() if k not in {"title", "description"}})
        base["path"] = rel
        try:
            tagged = await _ai_tag_image(
                ai=ai,
                image_bytes=path.read_bytes(),
                product_id=product_id,
                filename=path.name,
                feature_ids=feature_ids,
            )
            entry = _merge_ai_tag(base, tagged)
            entry["path"] = rel
            new_media.append(entry)
            updated += 1
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{path.name}:{exc}")
            new_media.append(media)
    data["media"] = new_media
    catalog_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    load_product_catalogs(knowledge_root)
    from src.knowledge.catalog_index import write_catalog_indexes
    from src.knowledge.refresh import notify_knowledge_changed

    write_catalog_indexes(knowledge_root, project_root)
    notify_knowledge_changed()
    return IngestResult(
        ok=True,
        product_id=product_id,
        files_added=[str(updated)],
        message_fa=(
            "ایندکس مجدد منابع کاتالوگ با موفقیت انجام شد.\n"
            f"محصول: {product_id}\nتصاویر بازتولید متا: {updated}"
        ),
        message_en=(
            "Catalog media re-index completed successfully.\n"
            f"Product: {product_id}\nRetagged images: {updated}"
        ),
        detail="; ".join(errors),
    )
