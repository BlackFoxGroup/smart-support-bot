"""Catalog RAG: semantic topic retrieval + educational context for Ask AI.

Not a parallel answer system — feeds the existing LLM path with better evidence.
Does not hardcode per-question replies.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.knowledge.product_catalogs import ProductCatalog, get_product_catalogs
from src.knowledge.source_catalog.pipeline import load_matrix
from src.knowledge.source_catalog.schema import STATUS_DEPRECATED, STATUS_LIVE

logger = logging.getLogger(__name__)

# Concept aliases → boost matching without per-question hardcoding.
# Keys are normalized (lower, ZWNJ stripped). Values are tokens merged into the query.
TOPIC_ALIASES: dict[str, tuple[str, ...]] = {
    "پیکربندی": ("configure", "panel", "configure_panel", "inbound", "outbound", "config"),
    "پیکربندی پنل": ("configure_panel", "configure", "panel", "inbound", "outbound"),
    "کانفیگ": ("configure", "configure_panel", "config", "panel"),
    "کانفیگ پنل": ("configure_panel", "configure", "panel"),
    "configure": ("configure_panel", "panel", "inbound", "outbound"),
    "configuration": ("configure_panel", "configure", "panel"),
    "inbound": ("configure_panel", "inbounds", "panel"),
    "outbound": ("configure_panel", "add_outbounds", "outbounds"),
    "outbounds": ("add_outbounds", "configure_panel"),
    "اسکریپت": ("script", "scripts", "cli", "launch"),
    "اسکریپ": ("script", "scripts"),
    "script": ("اسکریپت", "cli", "launch"),
    "نصب": ("full_deploy", "deploy", "setup", "install"),
    "دیپلوی": ("full_deploy", "deploy"),
    "فول دیپلوی": ("full_deploy", "deploy", "wireguard", "3x-ui"),
    "full deploy": ("full_deploy", "deploy", "wireguard"),
    "fulldeploy": ("full_deploy", "deploy"),
    "ssh": ("connect_ssh", "central", "setup_central"),
    "اتصال": ("connect_ssh", "ssh", "link"),
    "مش": ("mesh", "topology", "mesh_topology"),
    "توپولوژی": ("topology", "mesh", "view"),
    "دامنه": ("domain", "dns", "cdn", "add_domain", "free_domain"),
    "دامنه رایگان": ("free_domain", "freedns", "subdomain", "pro", "ai pro"),
    "ساب دامین": ("free_domain", "subdomain", "domain"),
    "ساب‌دامین": ("free_domain", "subdomain", "domain"),
    "free domain": ("free_domain", "subdomain", "pro", "ai pro"),
    "add domain": ("add_domain_dns", "external_proxy", "free_domain", "domain"),
    "external proxy": ("external_proxy", "domain", "inbound"),
    "mesh servers": ("mesh_servers", "mesh_topology", "mesh", "link monitor"),
    "مش سرور": ("mesh_servers", "mesh_topology", "mesh"),
    "سی‌دی‌ان": ("cdn", "cloudflare"),
    "cdn": ("cdn", "cloudflare", "domain"),
    "لایسنس": ("registration", "license", "pro"),
    "ریست": ("factory_reset", "reset"),
    "ترمینال": ("terminal",),
    "ربات": ("telegram", "mirza", "smart_support", "agent"),
    "نود": ("add_node_servers", "node"),
    "اگزیت": ("add_exit_servers", "exit"),
    "تونل": ("add_tunnel_servers", "tunnel"),
    # Disambiguated backup senses only — bare "backup" must NOT alias to mesh/telegram.
    "backup panel": ("move_central", "panel_manager", "restore_panel", "backup_panel"),
    "panel backup": ("move_central", "backup_panel", "restore_panel"),
    "بکاپ پنل": ("move_central", "backup_panel", "restore_panel"),
    "بک‌آپ پنل": ("move_central", "backup_panel", "restore_panel"),
    "restore panel": ("move_central", "restore_panel", "backup_panel"),
    "panel manager": ("move_central", "panel_manager", "backup_panel"),
    "backup path": ("mesh_servers", "mesh_deploy", "ssh_protected"),
    "backup paths": ("mesh_servers", "mesh_deploy", "ssh_protected"),
    "مسیر پشتیبان": ("mesh_servers", "mesh_deploy", "ssh_protected"),
    "مسیرهای پشتیبان": ("mesh_servers", "mesh_deploy", "ssh_protected"),
    "install backup paths": ("mesh_servers", "mesh_deploy"),
    "ssh protected backup": ("mesh_servers", "ssh_protected", "mesh_deploy"),
    "move bot": ("add_telegram_move", "telegram_move", "mirza"),
    "انتقال ربات": ("add_telegram_move", "telegram_move", "mirza"),
    "update mirza": ("add_telegram_update_mirza", "mirza_update"),
    "آپدیت میرزا": ("add_telegram_update_mirza", "mirza_update"),
}

# Tokens that inflate scores without naming a product surface.
_STOPWORD_TOKENS = frozenset(
    {
        "برنامه",
        "سیستم",
        "داره",
        "دارد",
        "آیا",
        "ایا",
        "هم",
        "چی",
        "چه",
        "یک",
        "does",
        "have",
        "has",
        "is",
        "there",
        "any",
        "the",
        "and",
        "for",
        "with",
        "this",
        "that",
        "from",
        "into",
        "also",
        "yes",
        "no",
    }
)

_BACKUP_TOKEN_FAMILY = frozenset(
    {
        "backup",
        "backups",
        "بکاپ",
        "بکآپ",
        "پشتیبان",
    }
)

# Feature → backup sense cluster (vpn-installer).
_BACKUP_FEATURE_CLUSTER: dict[str, str] = {
    "move_central": "backup_panel",
    "mesh_servers": "backup_mesh_link",
    "link_test": "backup_mesh_link",
    "add_telegram_move": "backup_telegram_bot",
    "add_telegram_update_mirza": "backup_telegram_bot",
}

_CLUSTER_PRIMARY_SLOTS: dict[str, tuple[str, ...]] = {
    "backup_panel": ("panel-manager", "restore-panel", "move-central"),
    "backup_mesh_link": ("mesh-backup-paths", "mesh-deploy", "mesh-links"),
    "backup_telegram_bot": ("telegram-move", "mirza-update"),
}

_CLUSTER_DISAMBIG_CUES: dict[str, tuple[str, ...]] = {
    "backup_panel": (
        "panel backup",
        "backup panel",
        "restore panel",
        "panel manager",
        "move central",
        "path a",
        "path b",
        "بکاپ پنل",
        "بکآپ پنل",
        "بازیابی پنل",
        "پنل منیجر",
        "انتقال سنترال",
    ),
    "backup_mesh_link": (
        "backup path",
        "backup paths",
        "install backup",
        "ssh_protected",
        "ssh protected",
        "mesh backup",
        "مسیر پشتیبان",
        "مسیرهای پشتیبان",
        "لینک پشتیبان",
        "مش",
        "mesh",
        "server connection",
    ),
    "backup_telegram_bot": (
        "move bot",
        "telegram bot",
        "mirza",
        "update mirza",
        "انتقال ربات",
        "ربات تلگرام",
        "میرزا",
        "smart support",
    ),
}

_CAPABILITY_YESNO = (
    "هم داره",
    "داره؟",
    "داره",
    "دارد؟",
    "دارد",
    "آیا",
    "does it have",
    "is there",
    "do you have",
    "any backup",
)

EDU_HINTS = (
    "آموزش",
    "اموزش",
    "چطور",
    "چگونه",
    "توضیح",
    "توضیح بده",
    "راهنما",
    "مراحل",
    "چیست",
    "چی هست",
    "how",
    "what is",
    "explain",
    "tutorial",
    "steps",
)

# Questions that are usually text-only (no UI screenshot needed).
_NO_MEDIA_HINTS = (
    "دانلود",
    "download",
    "از کجا",
    "where can i",
    "where do i get",
    "قیمت",
    "price",
    "خرید",
    "buy",
    "سایت",
    "website",
    "foxnext",
    "پشتیبانی",
    "support",
    "تماس",
    "contact",
    "کانال",
    "channel",
    "گروه",
    "group",
)


def wants_send_media(query: str) -> bool:
    from src.knowledge.catalog_index import wants_send_media as _wants_send

    return _wants_send(query)


def wants_catalog_media(query: str) -> bool:
    """True when the question likely benefits from a product UI screenshot."""
    q = _norm(query)
    if not q:
        return False
    if wants_send_media(query):
        return True
    if any(h in q for h in _NO_MEDIA_HINTS):
        return False
    ui_hints = (
        "پیکربندی",
        "configure",
        "full deploy",
        "دیپلوی",
        "ssh",
        "دامنه",
        "free domain",
        "mesh",
        "inbound",
        "outbound",
        "پنل",
        "panel",
        "اسکرین",
        "screenshot",
        "تصویر",
        "عکس",
        "نشان بده",
        "show me",
        "howto",
        "مراحل",
        "چطور",
        "چگونه",
        "آموزش",
    )
    return any(h in q for h in ui_hints) or is_educational_question(query)


@dataclass(slots=True)
class CatalogUnit:
    """One searchable knowledge unit (feature or media card)."""

    kind: str  # feature | media | product
    product_id: str
    unit_id: str
    title: str
    body: str
    search_blob: str
    feature_ids: list[str] = field(default_factory=list)
    media_slots: list[str] = field(default_factory=list)
    media_path: str = ""
    score: float = 0.0


@dataclass(slots=True)
class CatalogRetrieval:
    query_expanded: str
    units: list[CatalogUnit]
    media_paths: list[Path]
    is_educational: bool
    insufficient: bool
    prompt_block: str
    media_units: list[CatalogUnit] = field(default_factory=list)
    attach_media: bool = False
    needs_clarification: bool = False
    clarifying_question: str | None = None
    dominant_cluster: str | None = None


def _norm(text: str) -> str:
    t = (text or "").strip().lower().replace("‌", "")
    # Unify common Persian backup spellings for matching only.
    t = t.replace("بک آپ", "بکاپ").replace("بک-آپ", "بکاپ")
    t = t.replace("بکآپ", "بکاپ")
    return re.sub(r"\s+", " ", t)


def _tokens(text: str) -> list[str]:
    raw = re.findall(r"[\w\u0600-\u06ff]+", _norm(text))
    out: list[str] = []
    for t in raw:
        t = t.strip("؟?!.،,;:…")
        if len(t) >= 2:
            out.append(t)
    return out


def _query_mentions_backup(q: str) -> bool:
    n = _norm(q)
    if "backup" in n or "بکاپ" in n or "پشتیبان" in n:
        # "پشتیبانی" alone is support contact, not backup.
        if "پشتیبانی" in n and "بکاپ" not in n and "backup" not in n and "پشتیبان " not in n and "مسیر پشتیبان" not in n:
            if "پشتیبان" not in n.replace("پشتیبانی", ""):
                return False
        return True
    return False


def _cue_cluster(q: str) -> str | None:
    n = _norm(q)
    hits: list[str] = []
    for cluster, cues in _CLUSTER_DISAMBIG_CUES.items():
        if any(c in n for c in cues):
            hits.append(cluster)
    if len(hits) == 1:
        return hits[0]
    return None


def _clusters_from_evidence(evidence: list[CatalogUnit]) -> set[str]:
    found: set[str] = set()
    for u in evidence:
        for fid in u.feature_ids or []:
            c = _BACKUP_FEATURE_CLUSTER.get(fid)
            if c:
                found.add(c)
        uid = (u.unit_id or "").split(":")[-1]
        c2 = _BACKUP_FEATURE_CLUSTER.get(uid)
        if c2:
            found.add(c2)
    return found


def backup_clarifying_question(lang: str) -> str:
    if (lang or "").startswith("fa"):
        return (
            "چند جور بک‌آپ/پشتیبان در VPN Installer هست. منظورتان کدام است؟\n"
            "۱) Backup / Restore پنل (Panel manager / Move Central)\n"
            "۲) مسیر پشتیبان لینک مش (Install backup paths / ssh_protected_backup)\n"
            "۳) بک‌آپ ربات تلگرام (Move Bot / Update Mirza)"
        )
    return (
        "VPN Installer has several backup-related paths. Which do you mean?\n"
        "1) Panel Backup / Restore (Panel manager / Move Central)\n"
        "2) Mesh backup link paths (Install backup paths / ssh_protected_backup)\n"
        "3) Telegram bot backup (Move Bot / Update Mirza)"
    )


def is_capability_yesno(query: str) -> bool:
    q = _norm(query)
    return any(h in q for h in _CAPABILITY_YESNO)


def is_ambiguous_backup_retrieval(query: str, evidence: list[CatalogUnit]) -> bool:
    if not _query_mentions_backup(query):
        return False
    if _cue_cluster(query):
        return False
    clusters = _clusters_from_evidence(evidence)
    if len(clusters) >= 2:
        return True
    # Bare "does it have backup?" with no disambiguator → always clarify.
    if is_capability_yesno(query) or len(clusters) != 1:
        return True
    return False


def expand_query(query: str) -> str:
    """Merge alias tokens so Persian teaching phrases map to catalog English ids."""
    q = _norm(query)
    extra: list[str] = []
    # Longer phrases first
    for phrase, aliases in sorted(TOPIC_ALIASES.items(), key=lambda x: -len(x[0])):
        if phrase in q:
            extra.extend(aliases)
    # Also map space-insensitive compact forms
    compact = q.replace(" ", "").replace("-", "").replace("_", "")
    for phrase, aliases in TOPIC_ALIASES.items():
        pcompact = phrase.replace(" ", "").replace("-", "").replace("_", "")
        if len(pcompact) >= 4 and pcompact in compact:
            extra.extend(aliases)
    if not extra:
        return q
    return f"{q} " + " ".join(dict.fromkeys(extra))


def is_educational_question(query: str) -> bool:
    q = _norm(query)
    return any(h in q for h in EDU_HINTS)


def _lang_text(obj: Any, lang: str) -> str:
    if isinstance(obj, dict):
        return str(obj.get(lang) or obj.get("en") or obj.get("fa") or "").strip()
    return str(obj or "").strip()


def _feature_body(feat: dict[str, Any], lang: str) -> str:
    title = _lang_text(feat.get("title"), lang)
    summary = _lang_text(feat.get("summary"), lang)
    howto = _lang_text(feat.get("howto"), lang)
    parts = [p for p in (title, summary, howto) if p]
    return "\n".join(parts)


def build_catalog_units(*, lang: str = "fa") -> list[CatalogUnit]:
    units: list[CatalogUnit] = []
    for cat in get_product_catalogs():
        if not cat.catalog_enabled:
            continue
        # Product overview unit
        prod_title = cat.title.get(lang) or cat.title.get("en") or cat.product_id
        prod_body = (
            cat.long_summary.get(lang)
            or cat.short_summary.get(lang)
            or cat.long_summary.get("en")
            or cat.short_summary.get("en")
            or ""
        )
        keywords = " ".join(str(k) for k in (cat.keywords or []))
        units.append(
            CatalogUnit(
                kind="product",
                product_id=cat.product_id,
                unit_id=f"product:{cat.product_id}",
                title=str(prod_title),
                body=str(prod_body),
                search_blob=_norm(
                    f"{cat.product_id} {prod_title} {prod_body} {keywords} "
                    + " ".join(cat.title.values())
                    + " "
                    + " ".join(cat.short_summary.values())
                ),
                feature_ids=[],
                media_slots=[],
            )
        )
        slot_to_feat: dict[str, str] = {}
        for feat in cat.features or []:
            if not isinstance(feat, dict):
                continue
            fid = str(feat.get("id") or "").strip()
            if not fid:
                continue
            title = _lang_text(feat.get("title"), lang)
            body = _feature_body(feat, lang)
            slot = str(feat.get("media_slot") or "").strip()
            related = [
                str(x).strip()
                for x in (feat.get("related_media_slots") or [])
                if str(x).strip()
            ]
            slots = []
            if slot:
                slots.append(slot)
                slot_to_feat[slot] = fid
            for s in related:
                if s not in slots:
                    slots.append(s)
                slot_to_feat.setdefault(s, fid)
            blob = _norm(
                f"{fid} {title} {body} {slot} {' '.join(slots)} "
                + " ".join(str(v) for v in (feat.get("title") or {}).values())
                + " "
                + " ".join(str(v) for v in (feat.get("summary") or {}).values())
            )
            units.append(
                CatalogUnit(
                    kind="feature",
                    product_id=cat.product_id,
                    unit_id=f"feature:{cat.product_id}:{fid}",
                    title=title or fid,
                    body=body,
                    search_blob=blob,
                    feature_ids=[fid],
                    media_slots=slots,
                )
            )

        for media in cat.media or []:
            if not isinstance(media, dict):
                continue
            rel = str(media.get("path") or "").strip().replace("\\", "/")
            if not rel:
                continue
            slot = str(media.get("slot") or "").strip()
            note = str(media.get("note") or "").strip()
            mid = str(media.get("id") or slot or Path(rel).stem).strip()
            title = _lang_text(media.get("title"), lang) or note or slot or mid
            desc = _lang_text(media.get("description"), lang) or note
            topics = media.get("topics") if isinstance(media.get("topics"), list) else []
            feat_ids = (
                media.get("feature_ids")
                if isinstance(media.get("feature_ids"), list)
                else []
            )
            feat_ids_s = [str(x).strip() for x in feat_ids if str(x).strip()]
            if not feat_ids_s and slot in slot_to_feat:
                feat_ids_s = [slot_to_feat[slot]]
            # Derive soft links from slot naming
            soft = slot.replace("-", "_").replace(" ", "_")
            blob = _norm(
                f"{mid} {slot} {note} {title} {desc} {' '.join(map(str, topics))} "
                f"{' '.join(feat_ids_s)} {soft} {rel}"
            )
            units.append(
                CatalogUnit(
                    kind="media",
                    product_id=cat.product_id,
                    unit_id=f"media:{cat.product_id}:{mid}",
                    title=str(title),
                    body=str(desc or note),
                    search_blob=blob,
                    feature_ids=feat_ids_s,
                    media_slots=[slot] if slot else [],
                    media_path=rel,
                )
            )

    units.extend(_units_from_source_matrix(lang))
    units.extend(_units_from_live_media(lang))
    return units


def _units_from_live_media(lang: str) -> list[CatalogUnit]:
    from src.config import DATA_DIR, KNOWLEDGE_ROOT
    from src.knowledge.product_catalogs import get_product
    from src.knowledge.source_catalog.store import load_media_index

    out: list[CatalogUnit] = []
    for cat in get_product_catalogs():
        if not cat.catalog_enabled:
            continue
        index = load_media_index(DATA_DIR, cat.product_id)
        for item in index.get("items") or []:
            if not isinstance(item, dict):
                continue
            if item.get("status") != "SYNCED":
                continue
            fids = [str(x) for x in (item.get("feature_ids") or []) if str(x).strip()]
            if not fids:
                continue
            title = str(item.get("filename") or item.get("media_id"))
            desc = str(item.get("description") or "")
            blob = _norm(f"{title} {desc} {' '.join(fids)} {' '.join(item.get('keywords') or [])}")
            out.append(
                CatalogUnit(
                    kind="media",
                    product_id=cat.product_id,
                    unit_id=f"live-media:{item.get('media_id')}",
                    title=title,
                    body=desc,
                    search_blob=blob,
                    feature_ids=fids,
                    media_slots=[str(item.get("catalog_feature_id") or "")],
                    media_path=str(item.get("server_path") or item.get("path") or ""),
                )
            )
    return out


def _units_from_source_matrix(lang: str) -> list[CatalogUnit]:
    from src.config import KNOWLEDGE_ROOT

    matrix = load_matrix(KNOWLEDGE_ROOT)
    if not matrix:
        return []
    from src.knowledge.product_catalogs import get_product
    from src.knowledge.source_catalog.versions import load_active

    prod = get_product(str(matrix.get("product_id") or "vpn-installer"))
    if prod is not None and not prod.catalog_enabled:
        return []
    active = load_active(KNOWLEDGE_ROOT, str(matrix.get("product_id") or "vpn-installer"))
    if active and str(active.get("status") or "") not in {"", "ACTIVE"}:
        return []
    if active is None:
        # First-run: allow current matrix until a version is activated.
        pass
    out: list[CatalogUnit] = []
    for item in matrix.get("features") or []:
        if not isinstance(item, dict):
            continue
        fid = str(item.get("id") or "").strip()
        if not fid:
            continue
        status = str(item.get("status") or STATUS_LIVE)
        name = str(item.get("name") or fid)
        purpose = str(item.get("purpose") or "")
        if status in {STATUS_DEPRECATED, "legacy"}:
            body = (
                f"DEPRECATED/LEGACY: {name}. Do not recommend as the current product path. "
                f"{purpose}"
            )
        else:
            parts = [
                purpose,
                "Files: " + ", ".join(item.get("source_files") or [])[:400],
                "Ops: " + ", ".join(item.get("operation_ids") or []),
                "Workflow: " + " | ".join(item.get("workflow") or []),
                "APIs: " + ", ".join(item.get("api_calls") or [])[:300],
                "UNKNOWN fields stay UNKNOWN — do not invent.",
            ]
            body = "\n".join(p for p in parts if p)
        blob = _norm(
            f"{fid} {name} {item.get('category')} {purpose} "
            f"{' '.join(item.get('source_files') or [])} "
            f"{' '.join(item.get('operation_ids') or [])} "
            f"{' '.join(item.get('source_symbols') or [])} {status}"
        )
        out.append(
            CatalogUnit(
                kind="feature",
                product_id=str(matrix.get("product_id") or "vpn-installer"),
                unit_id=f"source:{fid}",
                title=name,
                body=body,
                search_blob=blob,
                feature_ids=[fid],
                media_slots=list(item.get("media_slots") or []),
            )
        )
    return out


def score_unit(query_expanded: str, unit: CatalogUnit) -> float:
    q = _norm(query_expanded)
    tokens = _tokens(q)
    if not tokens:
        return 0.0
    blob = unit.search_blob
    compact_q = q.replace(" ", "").replace("-", "").replace("_", "")
    compact_blob = blob.replace(" ", "").replace("-", "").replace("_", "")
    score = 0.0
    hits = 0
    content_hits = 0
    mesh_cue = _cue_cluster(q) == "backup_mesh_link" or any(
        x in q for x in ("mesh", "مش", "لینک", "link type", "ssh_protected")
    )
    for tok in tokens:
        if len(tok) < 3:
            continue
        if tok in _STOPWORD_TOKENS:
            continue
        # Bare "backup" must not score via link-type id ssh_protected_backup
        # unless the user actually asked about mesh backup paths.
        if tok in _BACKUP_TOKEN_FAMILY or tok == "backup":
            if "ssh_protected_backup" in blob and not mesh_cue:
                # Still allow score if "backup" appears as a real word outside that id.
                stripped = blob.replace("ssh_protected_backup", " ")
                if tok not in stripped and tok.replace("بکاپ", "backup") not in stripped:
                    if "backup" not in stripped and "بکاپ" not in stripped and "پشتیبان" not in stripped:
                        continue
        if tok in blob:
            score += 1.6
            hits += 1
            content_hits += 1
        ctok = tok.replace("-", "").replace("_", "")
        if len(ctok) >= 4 and ctok in compact_blob:
            score += 1.2
            hits += 1
            content_hits += 1
    # Coverage: prefer units that match a larger share of meaningful tokens
    meaningful = [t for t in tokens if len(t) >= 3 and t not in _STOPWORD_TOKENS]
    if meaningful:
        cov = hits / max(1, len(meaningful))
        score *= 0.55 + min(1.0, cov)
    if content_hits == 0 and not any(
        fid.replace("_", "").replace("-", "").lower() in compact_q
        for fid in unit.feature_ids
    ):
        return 0.0
    # Strong id/title containment
    for fid in unit.feature_ids:
        fcompact = fid.replace("_", "").replace("-", "").lower()
        if fcompact and fcompact in compact_q:
            score += 10.0
    title_c = _norm(unit.title).replace(" ", "")
    if len(title_c) >= 5 and title_c in compact_q:
        score += 6.0
    # Kind weights: features > media cards for text evidence
    if unit.kind == "feature":
        if "DEPRECATED" in (unit.body or "").upper() and "legacy" not in q and "deprecated" not in q:
            score *= 0.15
        else:
            score *= 1.15
    elif unit.kind == "media":
        score *= 0.85
    elif unit.kind == "product":
        score *= 0.7
    return score


def retrieve_catalog_context(
    query: str,
    *,
    lang: str = "fa",
    project_root: Path,
    limit_features: int = 4,
    limit_media: int = 2,
    min_score: float = 4.5,
    product_id: str | None = None,
    prior_text: str = "",
) -> CatalogRetrieval:
    """Retrieve related catalog sections + only relevant images for a user question."""
    search_query = f"{prior_text} {query}".strip() if (prior_text or "").strip() else query
    expanded = expand_query(search_query)
    educational = is_educational_question(query) or is_educational_question(search_query)
    send_now = wants_send_media(query)
    units = build_catalog_units(lang=lang)
    pid_filter = (product_id or "").strip()
    if pid_filter:
        units = [u for u in units if u.product_id == pid_filter]
    scored: list[CatalogUnit] = []
    for u in units:
        s = score_unit(expanded, u)
        if s < min_score:
            continue
        u.score = s
        scored.append(u)
    scored.sort(key=lambda x: (-x.score, x.unit_id))

    # Prefer feature units for evidence; keep product overview only if strong
    features = [u for u in scored if u.kind == "feature"][:limit_features]
    products = [u for u in scored if u.kind == "product"][:1]
    media_units = [u for u in scored if u.kind == "media"]

    evidence = features or products
    # If educational and we have a weak top hit, still keep it when clearly themed
    if not evidence and scored:
        top = scored[0]
        if top.score >= min_score * 0.85:
            evidence = [top]

    needs_clarification = False
    clarifying_question: str | None = None
    dominant_cluster: str | None = None
    if pid_filter == "vpn-installer" and is_ambiguous_backup_retrieval(query, evidence):
        # Also respect prior_text disambiguation (e.g. user replied "پنل")
        if not _cue_cluster(search_query):
            needs_clarification = True
            clarifying_question = backup_clarifying_question(lang)

    cue = _cue_cluster(search_query) or _cue_cluster(query)
    if cue:
        dominant_cluster = cue
    else:
        clusters = _clusters_from_evidence(evidence[:1] if evidence else [])
        if len(clusters) == 1:
            dominant_cluster = next(iter(clusters))

    # Dominant feature only for media slots (avoid union of top-3 unrelated senses).
    dominant_feats = evidence[:1] if evidence else []
    if dominant_cluster:
        filtered = [
            u
            for u in evidence
            if any(
                _BACKUP_FEATURE_CLUSTER.get(fid) == dominant_cluster
                or _BACKUP_FEATURE_CLUSTER.get((u.unit_id or "").split(":")[-1])
                == dominant_cluster
                for fid in (u.feature_ids or [ (u.unit_id or "").split(":")[-1] ])
            )
        ]
        if filtered:
            dominant_feats = filtered[:1]
            # Keep clarifying evidence to the chosen sense when disambiguated
            if not needs_clarification:
                evidence = [
                    u
                    for u in evidence
                    if u in filtered
                    or not any(
                        _BACKUP_FEATURE_CLUSTER.get(fid) in _CLUSTER_PRIMARY_SLOTS
                        for fid in (u.feature_ids or [])
                    )
                ] or filtered

    wanted_feats = {fid for u in dominant_feats for fid in u.feature_ids}
    wanted_slots = {s for u in dominant_feats for s in u.media_slots}
    if dominant_cluster:
        for slot in _CLUSTER_PRIMARY_SLOTS.get(dominant_cluster, ()):
            wanted_slots.add(slot)
    # Topology only when explicitly asked
    qn = _norm(search_query)
    if "topology" not in qn and "توپولوژی" not in qn and "view mesh" not in qn:
        wanted_slots.discard("mesh-topology-live")

    media_scored: list[tuple[float, CatalogUnit]] = []
    seen_paths: set[str] = set()

    def _slot_allowed(slot: str) -> bool:
        if not slot:
            return True
        if dominant_cluster:
            allowed = set(_CLUSTER_PRIMARY_SLOTS.get(dominant_cluster, ()))
            # Also allow the dominant feature's own media_slot
            allowed |= wanted_slots
            if slot.startswith("mesh-topology") and slot not in wanted_slots:
                return False
            if dominant_cluster == "backup_panel" and slot.startswith("telegram"):
                return False
            if dominant_cluster == "backup_telegram_bot" and (
                slot.startswith("mesh") or slot in ("panel-manager", "restore-panel")
            ):
                return False
            if dominant_cluster == "backup_mesh_link" and (
                slot.startswith("telegram") or slot in ("panel-manager", "restore-panel", "move-central")
            ):
                return False
        # Never use Move Bot shot for panel backup language
        if slot == "telegram-move" and (
            dominant_cluster == "backup_panel"
            or any(x in qn for x in ("panel backup", "backup panel", "بکاپ پنل", "restore panel"))
        ):
            return False
        return True

    for mu in media_units:
        if any(s and not _slot_allowed(s) for s in mu.media_slots):
            continue
        bonus = mu.score
        if any(f in wanted_feats for f in mu.feature_ids):
            bonus += 8.0
        if any(s in wanted_slots for s in mu.media_slots):
            bonus += 10.0
        if bonus < min_score + 1.0 and not (
            any(f in wanted_feats for f in mu.feature_ids)
            or any(s in wanted_slots for s in mu.media_slots)
        ):
            continue
        if not mu.media_path or mu.media_path in seen_paths:
            continue
        path = (project_root / mu.media_path).resolve()
        if not path.is_file():
            continue
        seen_paths.add(mu.media_path)
        mu.score = bonus
        media_scored.append((bonus, mu))

    # Resolve paths for dominant feature slots only (not free 20.0 for every top-K slot)
    catalogs = {c.product_id: c for c in get_product_catalogs()}
    for u in dominant_feats:
        cat = catalogs.get(u.product_id)
        if not cat:
            continue
        for media in cat.media or []:
            if not isinstance(media, dict):
                continue
            slot = str(media.get("slot") or "").strip()
            rel = str(media.get("path") or "").strip().replace("\\", "/")
            if not rel or rel in seen_paths:
                continue
            if not slot or slot not in wanted_slots or not _slot_allowed(slot):
                continue
            path = (project_root / rel).resolve()
            if path.is_file():
                seen_paths.add(rel)
                media_scored.append(
                    (
                        14.0,
                        CatalogUnit(
                            kind="media",
                            product_id=u.product_id,
                            unit_id=f"media-slot:{slot}",
                            title=slot,
                            body=str(media.get("note") or ""),
                            search_blob=slot,
                            feature_ids=list(u.feature_ids or []),
                            media_slots=[slot],
                            media_path=rel,
                            score=14.0,
                        ),
                    )
                )

    media_scored.sort(key=lambda x: -x[0])
    if dominant_cluster:
        primary = list(_CLUSTER_PRIMARY_SLOTS.get(dominant_cluster, ()))

        def _media_rank(item: tuple[float, CatalogUnit]) -> tuple[int, float]:
            score, mu = item
            slots = mu.media_slots or []
            best = 99
            for s in slots:
                if s in primary:
                    best = min(best, primary.index(s))
            return (best, -score)

        media_scored.sort(key=_media_rank)
    media_paths = [
        (project_root / mu.media_path).resolve()
        for _, mu in media_scored[:limit_media]
        if mu.media_path
    ]
    media_paths = [p for p in media_paths if p.is_file()]

    # Small-catalog folder fallback only
    if pid_filter and not media_scored:
        from src.knowledge.catalog_index import listed_image_paths

        folder_paths = listed_image_paths(project_root, pid_filter, limit=8)
        if 1 <= len(folder_paths) <= 2:
            for path in folder_paths:
                try:
                    rel = str(path.resolve().relative_to(project_root.resolve())).replace("\\", "/")
                except ValueError:
                    rel = str(path)
                mu = CatalogUnit(
                    kind="media",
                    product_id=pid_filter,
                    unit_id=f"media:{pid_filter}:section:{path.name}",
                    title=path.stem,
                    body="Catalog screenshot for this product section",
                    search_blob=_norm(f"{pid_filter} {path.name} screenshot"),
                    media_path=rel,
                    score=12.0,
                )
                media_scored.append((12.0, mu))
            media_paths = [p.resolve() for p in folder_paths if p.is_file()][:2]

    top_media_score = media_scored[0][0] if media_scored else 0.0
    linked = bool(wanted_feats or wanted_slots)
    ui_intent = (
        wants_catalog_media(query)
        or wants_catalog_media(expanded)
        or educational
        or send_now
        or bool(dominant_cluster)
    )
    # Build candidate paths before the attach gate.
    candidate_paths = [
        (project_root / mu.media_path).resolve()
        for _, mu in media_scored[:limit_media]
        if mu.media_path
    ]
    candidate_paths = [p for p in candidate_paths if p.is_file()]
    if pid_filter and not media_scored:
        # folder fallback already filled media_scored/media_paths above
        candidate_paths = list(media_paths)

    attach_media = bool(
        candidate_paths
        and pid_filter
        and not needs_clarification
        and linked
        and top_media_score >= 12.0
        and ui_intent
        and not (is_capability_yesno(query) and not educational and not send_now and not dominant_cluster)
    )
    if needs_clarification or not attach_media:
        media_paths = []
        picked_media: list[CatalogUnit] = []
    else:
        media_paths = candidate_paths
        picked_media = [m for _, m in media_scored[:limit_media]]

    insufficient = not evidence
    prompt_block = _format_prompt_block(
        evidence=evidence,
        media_units=picked_media if attach_media else [],
        educational=educational,
        insufficient=insufficient,
        lang=lang,
        clarifying_question=clarifying_question if needs_clarification else None,
    )
    if pid_filter:
        prompt_block = (
            f"### Product scope\nAnswer only about product_id={pid_filter}. "
            "Do not mix other product catalogs.\n\n"
            + prompt_block
        )
    return CatalogRetrieval(
        query_expanded=expanded,
        units=evidence,
        media_paths=media_paths,
        is_educational=educational,
        insufficient=insufficient,
        prompt_block=prompt_block,
        media_units=picked_media,
        attach_media=attach_media,
        needs_clarification=needs_clarification,
        clarifying_question=clarifying_question,
        dominant_cluster=dominant_cluster,
    )


def _format_prompt_block(
    *,
    evidence: list[CatalogUnit],
    media_units: list[CatalogUnit],
    educational: bool,
    insufficient: bool,
    lang: str,
    clarifying_question: str | None = None,
) -> str:
    lines: list[str] = ["### Catalog evidence (authoritative — do not invent beyond this)"]
    if clarifying_question:
        lines.append(
            "The user question is AMBIGUOUS across backup senses. "
            "Ask the clarifying question below and do NOT invent a single path. "
            "Do not claim screenshots were selected."
        )
        lines.append(f"Clarifying question to send:\n{clarifying_question}")
        return "\n".join(lines)
    if insufficient:
        lines.append(
            "NO sufficiently related catalog sections were found for this question. "
            "Say clearly that catalog information is insufficient. "
            "Do NOT invent product steps or limits."
        )
        return "\n".join(lines)

    for i, u in enumerate(evidence, 1):
        lines.append(f"\n#### Section {i}: {u.title} [{u.kind}/{u.product_id}]")
        lines.append(u.body or "(no body)")
        if u.feature_ids:
            lines.append(f"feature_ids: {', '.join(u.feature_ids)}")

    if media_units:
        lines.append("\n#### Related teaching screenshots (selected only if on-topic)")
        for m in media_units:
            lines.append(f"- {m.title}: {m.body or m.media_path}")
    else:
        lines.append("\n#### Media policy\nNo screenshot selected for this turn — answer with text only.")

    lines.append("\n#### Reply style rules")
    if educational or lang.startswith("fa"):
        lines.append(
            "Write like a patient product tutor. Cover: (1) what it is, "
            "(2) what it is for, (3) ordered steps, (4) useful tip/limit if present in evidence. "
            "Do not dump only button names. Finish every sentence completely. "
            "Reply in the user's language. Keep official UI labels in English Title Case."
        )
    else:
        lines.append(
            "Answer completely from evidence. Finish sentences. User language. "
            "Official UI labels stay in English Title Case."
        )
    return "\n".join(lines)


def enrich_media_entry_from_filename(
    filename: str, *, product_id: str, index: int
) -> dict[str, Any]:
    """Heuristic metadata so new uploads are searchable without hand-editing JSON."""
    stem = Path(filename).stem.lower()
    slot = re.sub(r"[^a-z0-9]+", "-", stem).strip("-") or f"{product_id}-{index}"
    topics = [t for t in re.split(r"[-_]+", stem) if len(t) >= 3][:8]
    feature_guess = []
    joined = stem.replace("-", "_")
    for token in topics:
        feature_guess.append(token)
    return {
        "id": slot,
        "role": "screenshot" if index else "hero",
        "slot": slot,
        "path": f"media/catalogs/{product_id}/{Path(filename).name}",
        "local_folder": f"media/catalogs/{product_id}",
        "note": f"auto-indexed from {Path(filename).name}",
        "title": {"fa": slot, "en": slot, "ru": slot, "zh": slot},
        "description": {
            "fa": f"تصویر آموزشی مرتبط با {slot}",
            "en": f"Teaching screenshot for {slot}",
            "ru": f"Teaching screenshot for {slot}",
            "zh": f"Teaching screenshot for {slot}",
        },
        "topics": topics,
        "feature_ids": feature_guess[:3],
        "stage": "guide",
    }
