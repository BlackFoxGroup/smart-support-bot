"""Load host-editable product catalogs for menu buttons and AI answers."""

from __future__ import annotations

import json
import logging
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SUPPORTED = ("fa", "en", "ru", "zh")


@dataclass(slots=True)
class ProductCatalog:
    product_id: str
    catalog_id: str
    enabled: bool
    menu_order: int
    menu_emoji: str
    title: dict[str, str]
    short_summary: dict[str, str]
    long_summary: dict[str, str]
    features: list[dict[str, Any]] = field(default_factory=list)
    does_not: dict[str, list[str]] = field(default_factory=dict)
    keywords: list[str] = field(default_factory=list)
    media: list[dict[str, Any]] = field(default_factory=list)
    support: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def catalog_enabled(self) -> bool:
        if "catalog_enabled" in self.raw:
            return bool(self.raw.get("catalog_enabled"))
        return True

    def label(self, lang: str) -> str:
        title = self.title.get(lang) or self.title.get("en") or self.product_id
        emoji = (self.menu_emoji or "").strip()
        return f"{emoji} {title}".strip() if emoji else title

    def summary(self, lang: str) -> str:
        return (
            self.long_summary.get(lang)
            or self.short_summary.get(lang)
            or self.long_summary.get("en")
            or self.short_summary.get("en")
            or ""
        )

    def menu_body(self, lang: str) -> str:
        # Hub intro: short educational copy (prefer short_summary).
        intro = (
            self.short_summary.get(lang)
            or self.long_summary.get(lang)
            or self.short_summary.get("en")
            or self.long_summary.get("en")
            or ""
        ).strip()
        lines = [f"{self.label(lang)}", "", intro]
        feats = self.features or []
        if feats:
            lines.append("")
            tip = "کلیدها را بزنید تا کوتاه یاد بگیرید:" if lang == "fa" else "Tap a key for a short tip:"
            lines.append(tip)
            for feat in feats[:8]:
                if not isinstance(feat, dict):
                    continue
                title = (feat.get("title") or {}).get(lang) or (feat.get("title") or {}).get("en")
                if title:
                    lines.append(f"• {title}")
        empty_media = [m for m in self.media if isinstance(m, dict) and not str(m.get("path") or "").strip()]
        if empty_media and lang == "fa":
            lines.append("")
            lines.append("عکس‌های محصول به‌زودی اضافه می‌شوند.")
        elif empty_media:
            lines.append("")
            lines.append("Product photos coming soon.")
        return "\n".join(lines).strip()


_CACHE: list[ProductCatalog] = []


def product_catalogs_dir(knowledge_root: Path) -> Path:
    """Legacy flat catalog directory kept for migration reads."""
    return knowledge_root / "product_catalogs"


def products_root(knowledge_root: Path) -> Path:
    project_root = knowledge_root.parent if knowledge_root.name == "knowledge" else knowledge_root
    return project_root / "products"


def product_root(knowledge_root: Path, product_id: str) -> Path:
    safe = slugify_product_id(product_id) if product_id else "product"
    return products_root(knowledge_root) / safe


def product_media_relative(product_id: str, filename: str = "") -> str:
    safe = slugify_product_id(product_id) if product_id else "product"
    base = f"products/{safe}/media"
    return f"{base}/{Path(filename).name}" if filename else base


def migrate_legacy_product_layout(knowledge_root: Path) -> dict[str, int]:
    """Copy legacy flat catalogs/media into the fixed per-product layout."""
    project_root = knowledge_root.parent if knowledge_root.name == "knowledge" else knowledge_root
    migrated_catalogs = 0
    migrated_media = 0
    legacy_dir = product_catalogs_dir(knowledge_root)
    if not legacy_dir.is_dir():
        return {"catalogs": 0, "media": 0}
    for legacy in sorted(legacy_dir.glob("*.json")):
        try:
            legacy_data = json.loads(legacy.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(legacy_data, dict):
            continue
        pid = slugify_product_id(str(legacy_data.get("product_id") or legacy.stem))
        destination = product_json_path(knowledge_root, pid)
        destination.parent.mkdir(parents=True, exist_ok=True)
        data = legacy_data
        if destination.is_file():
            try:
                current = json.loads(destination.read_text(encoding="utf-8"))
                if isinstance(current, dict):
                    data = current
            except (OSError, json.JSONDecodeError):
                pass
        old_media = project_root / "media" / "catalogs" / pid
        new_media = product_media_dir(project_root, pid)
        if old_media.is_dir():
            for source in old_media.iterdir():
                if not source.is_file():
                    continue
                target = new_media / source.name
                if not target.exists():
                    shutil.copy2(source, target)
                    migrated_media += 1
        changed = not destination.is_file()
        for item in data.get("media") or []:
            if not isinstance(item, dict):
                continue
            rel = str(item.get("path") or "").replace("\\", "/")
            legacy_prefix = f"media/catalogs/{pid}/"
            if rel.startswith(legacy_prefix):
                item["path"] = product_media_relative(pid, Path(rel).name)
                changed = True
            if str(item.get("local_folder") or "").replace("\\", "/") == legacy_prefix.rstrip("/"):
                item["local_folder"] = product_media_relative(pid)
                changed = True
        if changed:
            destination.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            migrated_catalogs += 1
    return {"catalogs": migrated_catalogs, "media": migrated_media}


def load_product_catalogs(knowledge_root: Path) -> list[ProductCatalog]:
    """Scan canonical product folders, with legacy flat-file compatibility."""
    global _CACHE
    migrated = migrate_legacy_product_layout(knowledge_root)
    if migrated["catalogs"] or migrated["media"]:
        logger.info("Migrated product layout: %s", migrated)
    out: list[ProductCatalog] = []
    paths = list_product_files(knowledge_root)
    if not paths:
        logger.warning("product catalogs missing under: %s", products_root(knowledge_root))
        _CACHE = []
        return _CACHE
    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Skip catalog %s: %s", path.name, exc)
            continue
        if not isinstance(data, dict) or not data.get("enabled", True):
            continue
        fallback_id = path.parent.name if path.name == "catalog.json" else path.stem
        product_id = str(data.get("product_id") or fallback_id).strip()
        if not product_id:
            continue
        title = data.get("title") if isinstance(data.get("title"), dict) else {}
        short_summary = data.get("short_summary") if isinstance(data.get("short_summary"), dict) else {}
        long_summary = data.get("long_summary") if isinstance(data.get("long_summary"), dict) else {}
        does_not = data.get("does_not") if isinstance(data.get("does_not"), dict) else {}
        features = data.get("features") if isinstance(data.get("features"), list) else []
        media = data.get("media") if isinstance(data.get("media"), list) else []
        keywords = data.get("keywords") if isinstance(data.get("keywords"), list) else []
        support = data.get("support") if isinstance(data.get("support"), dict) else {}
        out.append(
            ProductCatalog(
                product_id=product_id,
                catalog_id=str(data.get("catalog_id") or product_id),
                enabled=True,
                menu_order=int(data.get("menu_order") or 100),
                menu_emoji=str(data.get("menu_emoji") or ""),
                title={k: str(v) for k, v in title.items()},
                short_summary={k: str(v) for k, v in short_summary.items()},
                long_summary={k: str(v) for k, v in long_summary.items()},
                features=[f for f in features if isinstance(f, dict)],
                does_not={k: [str(x) for x in (v or [])] for k, v in does_not.items() if isinstance(v, list)},
                keywords=[str(k) for k in keywords],
                media=[m for m in media if isinstance(m, dict)],
                support=support,
                raw=data,
            )
        )
    out.sort(key=lambda p: (p.menu_order, p.product_id))
    _CACHE = out
    logger.info("Product catalogs loaded: %s", [p.product_id for p in out])
    return _CACHE


def get_product_catalogs() -> list[ProductCatalog]:
    return list(_CACHE)


def get_product(product_id: str) -> ProductCatalog | None:
    for item in _CACHE:
        if item.product_id == product_id:
            return item
    return None


def product_action_id(product_id: str) -> str:
    return f"product:{product_id}"


def parse_product_action(action: str | None) -> str | None:
    if not action or not action.startswith("product:"):
        return None
    # Ignore feature actions that also start with product: — use product:id only
    rest = action.split(":", 1)[1].strip()
    if not rest or ":" in rest:
        return None
    return rest or None


def feature_action_id(product_id: str, feature_id: str) -> str:
    return f"pfeat:{product_id}:{feature_id}"


def parse_feature_action(action: str | None) -> tuple[str, str] | None:
    if not action or not action.startswith("pfeat:"):
        return None
    parts = action.split(":", 2)
    if len(parts) != 3:
        return None
    _, product_id, feature_id = parts
    product_id = product_id.strip()
    feature_id = feature_id.strip()
    if not product_id or not feature_id:
        return None
    return product_id, feature_id


def feature_label(product: ProductCatalog, feature: dict[str, Any], lang: str) -> str:
    title = (feature.get("title") or {}).get(lang) or (feature.get("title") or {}).get("en") or feature.get("id")
    title = str(title or "").strip()
    emoji = str(feature.get("emoji") or "").strip()
    if emoji and not title.startswith(emoji):
        return f"{emoji} {title}".strip()
    return title


def feature_body(product: ProductCatalog, feature: dict[str, Any], lang: str) -> str:
    """Short educational reply for a product feature key (1–2 lines)."""
    title = feature_label(product, feature, lang)
    howto = (feature.get("howto") or {}).get(lang) or (feature.get("howto") or {}).get("en") or ""
    if str(howto).strip():
        return str(howto).strip()
    summary = (feature.get("summary") or {}).get(lang) or (feature.get("summary") or {}).get("en") or ""
    summary = str(summary).strip()
    if lang == "fa":
        # Keep replies educational and very concise for Telegram.
        if summary:
            return f"{title}\n{summary}".strip()
        return str(title)
    lines = [str(title)]
    if summary:
        lines.append(summary)
    return "\n".join(lines).strip()


def _normalize_query(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower().replace("‌", ""))


def match_feature_for_query(
    query: str, *, lang: str = "fa"
) -> tuple[ProductCatalog, dict[str, Any], float] | None:
    """Best matching catalog feature for an Ask AI question."""
    catalogs = get_product_catalogs()
    if not catalogs:
        return None
    q = _normalize_query(query)
    if len(q) < 3:
        return None
    tokens = [t for t in re.findall(r"[\w\u0600-\u06ff]+", q) if len(t) >= 3]
    best: tuple[ProductCatalog, dict[str, Any], float] | None = None
    for cat in catalogs:
        for feat in cat.features or []:
            if not isinstance(feat, dict):
                continue
            fid = str(feat.get("id") or "").strip().lower().replace("_", " ").replace("-", " ")
            titles = " ".join(str(v) for v in (feat.get("title") or {}).values()).lower()
            howto = " ".join(str(v) for v in (feat.get("howto") or {}).values()).lower()
            summary = " ".join(str(v) for v in (feat.get("summary") or {}).values()).lower()
            blob = f"{fid} {titles} {howto} {summary} {cat.product_id}"
            score = 0.0
            # Strong exact-ish hits for Full Deploy / Connect SSH style asks
            compact_fid = fid.replace(" ", "")
            compact_q = q.replace(" ", "").replace("-", "").replace("_", "")
            if compact_fid and compact_fid in compact_q:
                score += 12.0
            if fid and fid in q:
                score += 8.0
            for token in tokens:
                if token in blob:
                    score += 1.5
                if token in fid.replace(" ", ""):
                    score += 2.0
            # Persian teaching verbs boost when feature already matched a bit
            if score >= 4 and any(w in q for w in ("آموزش", "اموزش", "چطور", "چگونه", "استفاده", "how", "tutorial")):
                score += 3.0
            if best is None or score > best[2]:
                best = (cat, feat, score)
    if best is None or best[2] < 6.0:
        return None
    return best


def feature_howto_text(feature: dict[str, Any], lang: str) -> str:
    howto = (feature.get("howto") or {}).get(lang) or (feature.get("howto") or {}).get("en") or ""
    if str(howto).strip():
        return str(howto).strip()
    summary = (feature.get("summary") or {}).get(lang) or (feature.get("summary") or {}).get("en") or ""
    title = (feature.get("title") or {}).get(lang) or (feature.get("title") or {}).get("en") or ""
    parts = [str(title).strip(), str(summary).strip()]
    return "\n".join(p for p in parts if p).strip()


def resolve_media_paths_for_query(
    query: str,
    *,
    project_root: Path,
    lang: str = "fa",
    limit: int = 2,
    feature: dict[str, Any] | None = None,
    product: ProductCatalog | None = None,
) -> list[Path]:
    """Pick relevant catalog screenshots for the question (most relevant first)."""
    catalogs = [product] if product is not None else get_product_catalogs()
    if not catalogs:
        return []
    q = _normalize_query(query)
    tokens = [t for t in re.findall(r"[\w\u0600-\u06ff]+", q) if len(t) >= 3]
    wanted_slots: list[str] = []
    if feature:
        slot = str(feature.get("media_slot") or "").strip()
        if slot:
            wanted_slots.append(slot)
        related = feature.get("related_media_slots")
        if isinstance(related, list):
            for item in related:
                s = str(item or "").strip()
                if s and s not in wanted_slots:
                    wanted_slots.append(s)

    scored: list[tuple[float, Path]] = []
    seen: set[str] = set()
    for cat in catalogs:
        if cat is None:
            continue
        for media in cat.media or []:
            if not isinstance(media, dict):
                continue
            rel = str(media.get("path") or "").strip().replace("\\", "/")
            if not rel or rel in seen:
                continue
            slot = str(media.get("slot") or "").strip().lower()
            note = str(media.get("note") or "").lower()
            blob = f"{slot} {note} {rel} {cat.product_id}".lower()
            score = 0.0
            if slot and slot in wanted_slots:
                # Prefer listed related slots in order
                score += 20.0 - wanted_slots.index(slot) * 0.5
            for token in tokens:
                if token in blob.replace("-", " ").replace("_", " "):
                    score += 1.2
                compact = token.replace("-", "").replace("_", "")
                if compact and compact in slot.replace("-", "").replace("_", ""):
                    score += 3.0
            if "fulldeploy" in q.replace(" ", "").replace("-", "").replace("_", ""):
                if "full-deploy" in slot or "full_deploy" in slot or "fulldeploy" in rel.replace("-", ""):
                    score += 8.0
                if slot == "panel-login":
                    score += 3.0
                if "operations" in slot:
                    score += 2.0
            if score <= 0:
                continue
            path = (project_root / rel).resolve()
            if not path.is_file():
                continue
            seen.add(rel)
            scored.append((score, path))

    scored.sort(key=lambda x: (-x[0], str(x[1])))
    return [p for _, p in scored[: max(1, limit)]]


def ai_products_snippet(
    query: str,
    *,
    lang: str = "en",
    limit_chars: int = 4500,
    product_id: str | None = None,
) -> str:
    """Build a prompt block from product catalogs matching the query (or one product)."""
    catalogs = get_product_catalogs()
    if not catalogs:
        return ""
    scope = (product_id or "").strip()
    if scope:
        cat = next((c for c in catalogs if c.product_id == scope), None)
        if not cat:
            return f"Product catalog scope={scope}: no catalog loaded."
        body = cat.menu_body(lang)
        # Include feature howto/summary for richer product-only answers
        feat_lines: list[str] = []
        for feat in cat.features or []:
            if not isinstance(feat, dict):
                continue
            fid = str(feat.get("id") or "").strip()
            title = (feat.get("title") or {}).get(lang) or (feat.get("title") or {}).get("en") or fid
            summary = (feat.get("summary") or {}).get(lang) or (feat.get("summary") or {}).get("en") or ""
            howto = (feat.get("howto") or {}).get(lang) or (feat.get("howto") or {}).get("en") or ""
            block = f"- {title}: {summary}".strip()
            if howto:
                block += f"\n  howto: {howto}"
            feat_lines.append(block)
        parts = [
            f"Official product catalog (scoped to {scope} only):",
            f"### {cat.product_id}\n{body}",
        ]
        if feat_lines:
            parts.append("Features:\n" + "\n".join(feat_lines))
        train = str((cat.raw or {}).get("ai_training_text") or "").strip()
        if train:
            parts.append("Operator training notes (authoritative for user answers):\n" + train)
        mats = (cat.raw or {}).get("operator_materials")
        if isinstance(mats, list) and mats:
            lines = ["Operator catalog materials:"]
            for item in mats[:20]:
                if not isinstance(item, dict):
                    continue
                txt = str(item.get("text") or "").strip()
                guide = str(item.get("ai_guide") or "").strip()
                if txt:
                    lines.append(f"- material: {txt}")
                if guide:
                    lines.append(f"  ai_guide: {guide}")
            parts.append("\n".join(lines))
        media_guides = []
        for media in cat.media or []:
            if not isinstance(media, dict):
                continue
            guide = str(media.get("ai_guide") or media.get("note") or "").strip()
            path = str(media.get("path") or "").strip()
            if guide:
                media_guides.append(f"- {path or 'photo'}: {guide}")
        if media_guides:
            parts.append("Photo/text AI guides:\n" + "\n".join(media_guides[:24]))
        try:
            from src.knowledge.catalog_index import build_catalog_index_markdown

            parts.append(build_catalog_index_markdown(product_id=scope))
        except Exception:  # noqa: BLE001
            logger.exception("catalog index snippet failed")
        return "\n\n".join(parts)[: max(limit_chars, 7000)]

    q = (query or "").lower()
    product_ask = any(
        w in q
        for w in (
            "product",
            "محصول",
            "catalog",
            "کاتالوگ",
            "installer",
            "config builder",
            "ربات",
            "bot",
            "what is",
            "چیست",
        )
    )
    scored: list[tuple[int, ProductCatalog]] = []
    for cat in catalogs:
        score = 0
        blob = " ".join(
            [
                cat.product_id,
                cat.catalog_id,
                " ".join(cat.keywords),
                " ".join(cat.title.values()),
                " ".join(cat.short_summary.values()),
            ]
        ).lower()
        for token in re.findall(r"[\w\u0600-\u06ff]+", q):
            if len(token) < 3:
                continue
            if token in blob:
                score += 2
        if product_ask:
            score += 1
        if score > 0:
            scored.append((score, cat))
    if not scored and product_ask:
        scored = [(1, c) for c in catalogs]
    if not scored:
        # Always expose a short index so AI knows which products exist.
        lines = ["Product catalog index:"]
        for cat in catalogs:
            lines.append(f"- {cat.product_id}: {cat.short_summary.get(lang) or cat.short_summary.get('en') or cat.title.get('en')}")
        return "\n".join(lines)[:limit_chars]

    scored.sort(key=lambda x: (-x[0], x[1].menu_order))
    blocks = ["Official product catalogs (authoritative feature facts):"]
    used = 0
    for _, cat in scored:
        body = cat.menu_body(lang)
        train = str((cat.raw or {}).get("ai_training_text") or "").strip()
        extra = f"\nOperator training notes:\n{train[:1200]}" if train else ""
        chunk = f"### {cat.product_id}\n{body}{extra}"
        if used + len(chunk) > limit_chars:
            break
        blocks.append(chunk)
        used += len(chunk)
    return "\n\n".join(blocks)[:limit_chars]


def slugify_product_id(name: str) -> str:
    raw = (name or "").strip().lower()
    raw = re.sub(r"[^\w\u0600-\u06ff]+", "-", raw, flags=re.UNICODE)
    raw = re.sub(r"-{2,}", "-", raw).strip("-")
    if not raw:
        raw = "product"
    # Prefer ASCII-ish ids for filenames; keep unicode letters if present.
    ascii_only = re.sub(r"[^a-z0-9\-]+", "", raw)
    return (ascii_only or "product")[:48]


def _lang_map(text: str) -> dict[str, str]:
    t = (text or "").strip()
    return {code: t for code in SUPPORTED}


def product_json_path(knowledge_root: Path, product_id: str) -> Path:
    return product_root(knowledge_root, product_id) / "catalog.json"


def list_product_files(knowledge_root: Path) -> list[Path]:
    canonical = sorted(
        p for p in products_root(knowledge_root).glob("*/catalog.json") if p.is_file()
    )
    canonical_ids = {p.parent.name for p in canonical}
    legacy = sorted(
        p
        for p in product_catalogs_dir(knowledge_root).glob("*.json")
        if p.is_file() and slugify_product_id(p.stem) not in canonical_ids
    )
    return canonical + legacy


def list_all_product_dicts(knowledge_root: Path) -> list[dict[str, Any]]:
    """All catalog JSON files including disabled (for admin product manager)."""
    out: list[dict[str, Any]] = []
    for path in list_product_files(knowledge_root):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict):
            data = dict(data)
            data["_path"] = str(path)
            out.append(data)
    out.sort(key=lambda d: (int(d.get("menu_order") or 100), str(d.get("product_id") or "")))
    return out


def product_stub_data(
    product_id: str,
    *,
    title: str,
    emoji: str = "📦",
    summary: str = "",
    menu_order: int = 10,
) -> dict[str, Any]:
    pid = slugify_product_id(product_id or title)
    title_map = _lang_map(title or pid)
    summary_map = _lang_map(summary or title or pid)
    return {
        "schema_version": 1,
        "catalog_id": pid,
        "product_id": pid,
        "enabled": True,
        "menu_order": int(menu_order),
        "menu_emoji": (emoji or "📦").strip() or "📦",
        "title": title_map,
        "short_summary": summary_map,
        "long_summary": summary_map,
        "features": [],
        "does_not": {code: [] for code in SUPPORTED},
        "keywords": [title or pid],
        "media": [],
        "support": {},
        "ai_training_text": "",
        "catalog_sources": {
            "site": {"value": "", "use": False},
            "channel": {"value": "", "use": False},
            "group": {"value": "", "use": False},
        },
        "operator_materials": [],
    }


def create_product_stub(
    knowledge_root: Path,
    *,
    title: str,
    emoji: str = "📦",
    summary: str = "",
    product_id: str | None = None,
    menu_order: int | None = None,
) -> ProductCatalog:
    """Create a minimal enabled catalog JSON and reload cache."""
    pid = slugify_product_id(product_id or title)
    path = product_json_path(knowledge_root, pid)
    n = 1
    base = pid
    while path.exists():
        n += 1
        pid = f"{base}-{n}"
        path = product_json_path(knowledge_root, pid)
    path.parent.mkdir(parents=True, exist_ok=True)
    order = menu_order
    if order is None:
        existing = load_product_catalogs(knowledge_root)
        order = (max((p.menu_order for p in existing), default=0) + 10) if existing else 10
    data = product_stub_data(
        pid, title=title, emoji=emoji, summary=summary, menu_order=int(order)
    )
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ensure_product_asset_dirs(knowledge_root.parent, knowledge_root, pid)
    load_product_catalogs(knowledge_root)
    from src.knowledge.refresh import notify_knowledge_changed

    notify_knowledge_changed()
    found = get_product(pid)
    if found is None:
        raise RuntimeError(f"failed to load new product {pid}")
    return found


def update_product_fields(
    knowledge_root: Path,
    product_id: str,
    *,
    title: str | None = None,
    emoji: str | None = None,
    summary: str | None = None,
    enabled: bool | None = None,
    catalog_enabled: bool | None = None,
    menu_order: int | None = None,
) -> ProductCatalog:
    path = resolve_product_json_path(knowledge_root, product_id)
    if path is None or not path.is_file():
        raise FileNotFoundError(product_id)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("invalid catalog json")
    if title is not None:
        data["title"] = _lang_map(title)
        if not (summary or "").strip():
            # keep summaries unless explicitly set
            pass
    if summary is not None:
        sm = _lang_map(summary)
        data["short_summary"] = sm
        data["long_summary"] = sm
    if emoji is not None:
        data["menu_emoji"] = (emoji or "").strip() or data.get("menu_emoji") or "📦"
    if enabled is not None:
        data["enabled"] = bool(enabled)
    if catalog_enabled is not None:
        data["catalog_enabled"] = bool(catalog_enabled)
    if menu_order is not None:
        data["menu_order"] = int(menu_order)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    load_product_catalogs(knowledge_root)
    from src.knowledge.refresh import notify_knowledge_changed

    notify_knowledge_changed()
    found = get_product(str(data.get("product_id") or product_id))
    if found is None and not data.get("enabled", True):
        # disabled products are filtered out of cache — rebuild a lightweight view
        return ProductCatalog(
            product_id=str(data.get("product_id") or product_id),
            catalog_id=str(data.get("catalog_id") or product_id),
            enabled=False,
            menu_order=int(data.get("menu_order") or 100),
            menu_emoji=str(data.get("menu_emoji") or ""),
            title={k: str(v) for k, v in (data.get("title") or {}).items()},
            short_summary={k: str(v) for k, v in (data.get("short_summary") or {}).items()},
            long_summary={k: str(v) for k, v in (data.get("long_summary") or {}).items()},
        )
    if found is None:
        raise RuntimeError(f"failed to reload product {product_id}")
    return found


def delete_product(knowledge_root: Path, product_id: str) -> bool:
    folder = product_catalogs_dir(knowledge_root)
    candidates = [
        product_json_path(knowledge_root, product_id),
        folder / f"{product_id}.json",
        folder / f"{slugify_product_id(product_id)}.json",
    ]
    removed = False
    for path in candidates:
        if path.is_file():
            path.unlink()
            removed = True
    root = product_root(knowledge_root, product_id)
    if root.is_dir():
        shutil.rmtree(root, ignore_errors=True)
        removed = True
    versions = knowledge_root / "source_catalog" / "versions" / slugify_product_id(product_id)
    if versions.is_dir():
        shutil.rmtree(versions, ignore_errors=True)
        removed = True
    load_product_catalogs(knowledge_root)
    if removed:
        from src.knowledge.refresh import notify_knowledge_changed

        notify_knowledge_changed()
    return removed


def find_product_by_label(label: str, *, lang: str = "en") -> ProductCatalog | None:
    needle = (label or "").strip()
    if not needle:
        return None
    for cat in get_product_catalogs():
        if cat.label(lang) == needle or cat.label("en") == needle or cat.label("fa") == needle:
            return cat
        if cat.product_id == needle:
            return cat
        titles = {str(v).strip() for v in cat.title.values()}
        if needle in titles:
            return cat
    return None


def resolve_product_json_path(knowledge_root: Path, product_id: str) -> Path | None:
    folder = product_catalogs_dir(knowledge_root)
    for cand in (
        product_json_path(knowledge_root, product_id),
        folder / f"{product_id}.json",
        folder / f"{slugify_product_id(product_id)}.json",
    ):
        if cand.is_file():
            return cand
    return None


def load_product_raw(knowledge_root: Path, product_id: str) -> dict[str, Any] | None:
    path = resolve_product_json_path(knowledge_root, product_id)
    if path is None:
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def save_product_raw(knowledge_root: Path, product_id: str, data: dict[str, Any]) -> None:
    path = resolve_product_json_path(knowledge_root, product_id)
    if path is None:
        path = product_json_path(knowledge_root, product_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    load_product_catalogs(knowledge_root)
    from src.knowledge.refresh import notify_knowledge_changed

    notify_knowledge_changed()


def product_media_dir(project_root: Path, product_id: str) -> Path:
    pid = slugify_product_id(product_id) if product_id else "product"
    path = project_root / "products" / pid / "media"
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_product_asset_dirs(project_root: Path, knowledge_root: Path, product_id: str) -> Path:
    """One folder per product for catalog photos/text (named like the product id)."""
    media = product_media_dir(project_root, product_id)
    inbox = knowledge_root / "catalog_inbox" / slugify_product_id(product_id)
    inbox.mkdir(parents=True, exist_ok=True)
    return media


def count_product_photos(
    knowledge_root: Path,
    project_root: Path,
    product_id: str,
    *,
    staging: Path | None = None,
) -> int:
    names: set[str] = set()
    data = load_product_raw(knowledge_root, product_id) or {}
    for media in data.get("media") or []:
        if not isinstance(media, dict):
            continue
        rel = str(media.get("path") or "").strip().replace("\\", "/")
        if rel:
            names.add(Path(rel).name.lower())
    for media_dir in (
        product_media_dir(project_root, product_id),
        project_root / "media" / "catalogs" / product_id,
    ):
        if media_dir.is_dir():
            for path in media_dir.iterdir():
                if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
                    names.add(path.name.lower())
    if staging is not None and staging.is_dir():
        for path in staging.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
                names.add(path.name.lower())
    return len(names)

