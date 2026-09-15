"""Build product_catalogs/*.json from a folder path or staged uploads via AI."""

from __future__ import annotations

import json
import logging
import re
import shutil
import zipfile
from pathlib import Path
from typing import Any, Awaitable, Callable

from src.knowledge.product_catalogs import (
    product_json_path,
    product_media_dir,
    product_media_relative,
    resolve_product_json_path,
)
from src.operation_control import raise_if_stopped

logger = logging.getLogger(__name__)

TEXT_EXTS = {
    ".txt",
    ".md",
    ".json",
    ".csv",
    ".html",
    ".rst",
    ".log",
    ".go",
    ".py",
    ".ts",
    ".js",
    ".pdf",
    ".docx",
    ".doc",
}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

AiChat = Callable[[list[dict[str, str]]], Awaitable[str]]


def catalog_inbox_dir(knowledge_root: Path) -> Path:
    return knowledge_root / "catalog_inbox"


def media_catalogs_dir(project_root: Path) -> Path:
    """Legacy compatibility helper; new media uses product_media_dir."""
    return project_root / "media" / "catalogs"


def _load_build_prompt(inbox: Path) -> str:
    path = inbox / "_build_prompt.txt"
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return (
        "Build a product catalog JSON. Output ONLY valid JSON with schema_version 1, "
        "product_id, title/short_summary/long_summary/features in fa/en/ru/zh. "
        "Each feature should include id, title, summary, optional howto, optional media_slot. "
        "Media metadata will be attached separately; focus on accurate feature meanings."
    )


def _read_source_text(path: Path) -> str:
    suf = path.suffix.lower()
    if suf == ".docx":
        try:
            with zipfile.ZipFile(path) as zf:
                xml = zf.read("word/document.xml").decode("utf-8", errors="replace")
            return re.sub(r"<[^>]+>", " ", xml)
        except (OSError, zipfile.BadZipFile, KeyError):
            return path.name
    if suf == ".pdf":
        try:
            from pypdf import PdfReader

            pages = PdfReader(str(path)).pages
            return "\n".join((p.extract_text() or "") for p in pages[:40])
        except Exception:
            raw = path.read_bytes()[:200000]
            return raw.decode("latin-1", errors="replace")
    if suf == ".doc":
        return path.read_bytes().decode("latin-1", errors="replace")
    return path.read_text(encoding="utf-8", errors="replace")


def _folder_payload(folder: Path) -> str:
    parts: list[str] = [f"Folder name (product_id hint): {folder.name}"]
    media_names: list[str] = []
    for path in sorted(folder.rglob("*")):
        raise_if_stopped()
        if not path.is_file():
            continue
        if path.name.startswith("_"):
            continue
        suf = path.suffix.lower()
        rel = str(path.relative_to(folder))
        if suf in TEXT_EXTS:
            try:
                text = _read_source_text(path)
            except OSError:
                continue
            if len(text) > 8000:
                text = text[:8000] + "\n…"
            parts.append(f"\n### FILE {rel}\n{text}")
        elif suf in IMAGE_EXTS:
            media_names.append(rel)
        else:
            parts.append(f"\n### FILE {rel} (binary/other, name only)")
    if media_names:
        parts.append("\n### MEDIA FILES\n" + "\n".join(f"- {n}" for n in media_names))
        parts.append(
            "\n### NOTE\n"
            "These images are product UI screenshots / photos. "
            "If no text docs exist, still build a complete catalog JSON from the product_id hint "
            "and the fact that UI screenshots were provided. Include features typical for that product."
        )
    return "\n".join(parts)


def collect_folder_images(folder: Path, *, limit: int = 6) -> list[bytes]:
    out: list[bytes] = []
    for path in sorted(folder.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in IMAGE_EXTS:
            continue
        try:
            out.append(path.read_bytes())
        except OSError:
            continue
        if len(out) >= limit:
            break
    return out


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


def list_inbox_products(knowledge_root: Path) -> list[Path]:
    inbox = catalog_inbox_dir(knowledge_root)
    if not inbox.is_dir():
        return []
    return [
        p
        for p in sorted(inbox.iterdir())
        if p.is_dir() and not p.name.startswith("_") and not p.name.startswith(".")
    ]


def prepare_work_folder(
    *,
    knowledge_root: Path,
    folder_path: str | None = None,
    staging_dir: Path | None = None,
    product_hint: str = "product",
) -> Path:
    """
    Resolve a readable product folder:
    - absolute/relative path on the bot host, or
    - staging_dir filled by Telegram uploads (may contain zip).
    Copies into catalog_inbox/<product_id>/ as the server copy.
    """
    inbox = catalog_inbox_dir(knowledge_root)
    inbox.mkdir(parents=True, exist_ok=True)

    source: Path | None = None
    if folder_path:
        candidate = Path(folder_path).expanduser()
        if not candidate.is_absolute():
            candidate = (knowledge_root.parent / candidate).resolve()
        if candidate.is_dir():
            source = candidate
        elif candidate.is_file() and candidate.suffix.lower() == ".zip":
            staging = inbox / "_staging_zip"
            if staging.exists():
                shutil.rmtree(staging, ignore_errors=True)
            staging.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(candidate, "r") as zf:
                zf.extractall(staging)
            source = staging
        elif candidate.is_file():
            staging = inbox / "_staging_file"
            if staging.exists():
                shutil.rmtree(staging, ignore_errors=True)
            staging.mkdir(parents=True, exist_ok=True)
            shutil.copy2(candidate, staging / candidate.name)
            source = staging
        else:
            raise FileNotFoundError(f"Folder not found: {folder_path}")

    if source is None and staging_dir is not None and staging_dir.is_dir():
        # Expand any zip inside staging
        for zpath in list(staging_dir.glob("*.zip")):
            with zipfile.ZipFile(zpath, "r") as zf:
                zf.extractall(staging_dir)
        source = staging_dir

    if source is None:
        raise FileNotFoundError("No folder path or uploaded files provided")

    product_id = re.sub(r"[^a-zA-Z0-9_-]+", "-", product_hint or source.name).strip("-").lower() or "product"
    dest = inbox / product_id
    if dest.exists():
        shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(source, dest, dirs_exist_ok=True)
    return dest


def copy_media_to_server(folder: Path, *, project_root: Path, product_id: str) -> list[str]:
    """Copy images into the product's fixed media folder; return relative paths."""
    out_dir = product_media_dir(project_root, product_id)
    copied: list[str] = []
    for path in sorted(folder.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in IMAGE_EXTS:
            continue
        target = out_dir / path.name
        shutil.copy2(path, target)
        rel = product_media_relative(product_id, path.name)
        copied.append(rel)
    return copied


async def build_one_catalog(
    folder: Path,
    ai_chat: AiChat,
    *,
    knowledge_root: Path,
    project_root: Path,
    extra_sources: str = "",
    reload_fn=None,
    force_product_id: str = "",
    enrich_notes: list[dict[str, Any]] | None = None,
) -> str:
    inbox = catalog_inbox_dir(knowledge_root)
    prompt = _load_build_prompt(inbox)
    payload = _folder_payload(folder)
    if extra_sources.strip():
        payload += "\n\n### OWNER SELECTED SOURCES\n" + extra_sources.strip()
    # Photos-only folders are valid; don't reject when media exists.
    has_media = any(
        p.is_file() and p.suffix.lower() in IMAGE_EXTS for p in folder.rglob("*")
    )
    if len(payload) < 40 and not has_media and not force_product_id:
        raise ValueError(f"Folder too empty: {folder}")

    # Prefer vision when screenshots exist and ai_chat supports it.
    images = collect_folder_images(folder, limit=5)
    answer = ""
    raise_if_stopped()
    vision_fn = getattr(ai_chat, "chat_with_images", None)
    # ai_chat may be bound method ai.chat — look for sibling chat_with_images
    owner = getattr(ai_chat, "__self__", None)
    if owner is not None and hasattr(owner, "chat_with_images"):
        vision_fn = owner.chat_with_images
    if callable(vision_fn) and images:
        try:
            answer = await vision_fn(
                "Analyze these product screenshots and output ONLY valid catalog JSON "
                "(schema_version 1, product_id, title/short_summary/long_summary/features "
                "in fa/en/ru/zh). Use this context:\n\n"
                + payload,
                images,
                system=prompt,
                max_images=5,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("catalog vision failed, falling back to text: %s", exc)
            answer = ""
    if not (answer or "").strip():
        raise_if_stopped()
        answer = await ai_chat(
            [
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": "Analyze these product materials and produce the catalog JSON.\n\n"
                    + payload,
                },
            ]
        )
    data = _extract_json(answer)
    raise_if_stopped()
    if not data:
        raise ValueError("AI did not return valid catalog JSON")

    existing: dict[str, Any] = {}
    if force_product_id:
        existing_path = resolve_product_json_path(knowledge_root, force_product_id)
        if existing_path is not None and existing_path.is_file():
            try:
                loaded = json.loads(existing_path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    existing = loaded
            except (OSError, json.JSONDecodeError):
                existing = {}
        product_id = force_product_id.strip().lower().replace(" ", "-")
    else:
        product_id = str(data.get("product_id") or folder.name).strip().lower().replace(" ", "-")
    data["product_id"] = product_id
    data.setdefault("enabled", True)
    data.setdefault("catalog_id", f"user-{product_id}")
    data.setdefault("menu_emoji", "📦")
    data.setdefault("menu_order", 50)

    media_paths = copy_media_to_server(folder, project_root=project_root, product_id=product_id)
    if media_paths:
        from src.knowledge.catalog_rag import enrich_media_entry_from_filename

        feature_ids = [
            str(f.get("id") or "").strip()
            for f in (data.get("features") or [])
            if isinstance(f, dict) and str(f.get("id") or "").strip()
        ]
        data["media"] = []
        for i, p in enumerate(media_paths):
            entry = enrich_media_entry_from_filename(
                Path(p).name, product_id=product_id, index=i
            )
            entry["path"] = p
            # Soft-link feature ids that appear in the filename
            name_l = Path(p).stem.lower().replace("-", "_")
            linked = [fid for fid in feature_ids if fid.replace("-", "_") in name_l]
            if linked:
                entry["feature_ids"] = linked[:4]
            data["media"].append(entry)
    else:
        data.setdefault(
            "media",
            [
                {
                    "id": f"{product_id}-hero",
                    "role": "hero",
                    "slot": f"{product_id}-hero",
                    "path": "",
                    "local_folder": product_media_relative(product_id),
                    "note": "no photos in folder",
                    "topics": [],
                    "feature_ids": [],
                    "stage": "other",
                }
            ],
        )

    notes = [n for n in (enrich_notes or []) if isinstance(n, dict)]
    notes_by_file = {
        Path(str(n.get("path") or "")).name.lower(): str(n.get("ai_note") or "").strip()
        for n in notes
        if Path(str(n.get("path") or "")).name
    }
    media_list = data.get("media") if isinstance(data.get("media"), list) else []
    for entry in media_list:
        if not isinstance(entry, dict):
            continue
        name = Path(str(entry.get("path") or "")).name.lower()
        guide = notes_by_file.get(name, "")
        if guide:
            entry["ai_guide"] = guide
            if not str(entry.get("note") or "").strip():
                entry["note"] = guide
    text_mats = [
        {"text": str(n.get("text") or "").strip(), "ai_guide": str(n.get("ai_note") or "").strip()}
        for n in notes
        if str(n.get("kind") or "") == "text" and str(n.get("text") or "").strip()
    ]
    if existing.get("operator_materials") and not text_mats:
        data["operator_materials"] = existing.get("operator_materials")
    elif text_mats:
        data["operator_materials"] = text_mats
    if isinstance(existing.get("ai_training_text"), str):
        data["ai_training_text"] = existing["ai_training_text"]
    if isinstance(existing.get("catalog_sources"), dict):
        data["catalog_sources"] = existing["catalog_sources"]
    if existing:
        data["enabled"] = bool(existing.get("enabled", True))
        if existing.get("menu_order") is not None:
            data["menu_order"] = existing.get("menu_order")
        if existing.get("menu_emoji"):
            data["menu_emoji"] = existing.get("menu_emoji")
        if isinstance(existing.get("title"), dict) and existing.get("title"):
            data["title"] = existing["title"]

    path = product_json_path(knowledge_root, product_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        from src.knowledge.ai_profile import ensure_ai_profile

        ensure_ai_profile(knowledge_root, product_id, catalog_data=data)
    except Exception:  # noqa: BLE001
        logger.exception("ensure_ai_profile failed for %s", product_id)
    # Keep a copy inside the inbox folder too
    (folder / f"{product_id}.catalog.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if reload_fn is not None:
        reload_fn()
    else:
        from src.knowledge.refresh import notify_knowledge_changed

        notify_knowledge_changed()
    logger.info("Wrote catalog %s (+ %s media)", path, len(media_paths))
    return product_id


async def build_catalogs_from_inbox(
    knowledge_root: Path,
    ai_chat: AiChat,
    *,
    reload_fn=None,
    project_root: Path | None = None,
    extra_sources: str = "",
) -> list[str]:
    root = project_root or knowledge_root.parent
    written: list[str] = []
    for folder in list_inbox_products(knowledge_root):
        try:
            pid = await build_one_catalog(
                folder,
                ai_chat,
                knowledge_root=knowledge_root,
                project_root=root,
                extra_sources=extra_sources,
                reload_fn=None,
            )
            written.append(pid)
        except Exception as exc:  # noqa: BLE001
            logger.exception("catalog build failed for %s: %s", folder.name, exc)
    if written and reload_fn is not None:
        reload_fn()
    return written
