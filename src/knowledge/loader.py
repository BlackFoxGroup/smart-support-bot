"""Load markdown / JSON knowledge into compact retrieval snippets."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.config import Settings

logger = logging.getLogger(__name__)

LANG_FOLDER = {
    "fa": "Persian",
    "en": "English",
    "ru": "Russian",
    "zh": "Chinese",
}

_TOKEN_RE = re.compile(r"[\w\u0600-\u06ff\u0400-\u04ff\u4e00-\u9fff]+", re.UNICODE)


@dataclass(slots=True)
class KnowledgeIndex:
    """In-memory compact knowledge for RAG-style prompts."""

    facts: dict[str, Any] = field(default_factory=dict)
    # lang -> list of (title, body, product_id|None)
    faq_chunks: dict[str, list[tuple[str, str, str | None]]] = field(default_factory=dict)
    decision_summaries: list[str] = field(default_factory=list)
    loaded_files: int = 0


_PRODUCT_GUIDE_ALIASES: dict[str, str] = {
    "smart-support-bot": "agent-bot",
    "smart-support": "agent-bot",
    "telegram-agent-bot": "agent-bot",
    "telegram-agent": "agent-bot",
}


def product_id_from_guide_stem(stem: str) -> str | None:
    """Map product_guides/<product>-*.md stem to catalog product_id."""
    base = re.sub(r"[._-](fa|en|ru|zh)$", "", (stem or "").lower(), flags=re.I)
    base = base.strip("-_.")
    if not base or base == "readme":
        return None
    if base.endswith("-catalog-index"):
        return base[: -len("-catalog-index")] or None
    if base.endswith("-catalog-training"):
        return base[: -len("-catalog-training")] or None
    if base.endswith("-ai-memory"):
        return base[: -len("-ai-memory")] or None
    if base.endswith("-ai-behavior") or base.endswith("-AI_BEHAVIOR"):
        return re.sub(r"-ai-behavior$", "", base, flags=re.I) or None
    for alias, pid in _PRODUCT_GUIDE_ALIASES.items():
        if base == alias or base.startswith(alias + "-") or base.startswith(alias + "_"):
            return pid
    known = ("vpn-installer", "config-builder", "agent-bot")
    for pid in known:
        if base == pid or base.startswith(pid + "-") or base.startswith(pid + "_"):
            return pid
    # vpn_installer style
    dashed = base.replace("_", "-")
    for pid in known:
        if dashed == pid or dashed.startswith(pid + "-"):
            return pid
    return None


def tokenize(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN_RE.findall(text or "") if len(t) > 1}


class KnowledgeLoader:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.index = KnowledgeIndex()

    def load(self) -> KnowledgeIndex:
        self.index = KnowledgeIndex()
        self._load_facts()
        self._load_faq_markdown()
        self._load_product_guides()
        self._load_decision_trees()
        logger.info(
            "Knowledge loaded: files=%s faq_langs=%s trees=%s",
            self.index.loaded_files,
            list(self.index.faq_chunks.keys()),
            len(self.index.decision_summaries),
        )
        return self.index

    def _load_facts(self) -> None:
        intents_root = self.settings.intents_dir
        for name in ("intents/intents_en.json", "all_languages_database.json"):
            path = intents_root / name
            if not path.is_file():
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                logger.warning("Skip facts file %s: %s", path, exc)
                continue
            meta = data.get("meta") if isinstance(data, dict) else None
            if isinstance(meta, dict) and isinstance(meta.get("facts"), dict):
                self.index.facts = dict(meta["facts"])
                self.index.loaded_files += 1
                break
        self._merge_group_community()

    def _merge_group_community(self) -> None:
        """Merge curated @Black_Fox_Group community facts (no prices / no two-mode legacy)."""
        path = self.settings.knowledge_root / "group_community.json"
        if not path.is_file():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Skip group_community.json: %s", exc)
            return
        group = data.get("group") if isinstance(data, dict) else None
        contacts = data.get("contacts") if isinstance(data, dict) else None
        points = data.get("product_points") if isinstance(data, dict) else None
        if isinstance(group, dict):
            self.index.facts["community_group"] = group.get("url") or group.get("username")
            self.index.facts["community_title"] = group.get("title")
        if isinstance(contacts, dict):
            self.index.facts["human_support"] = contacts.get("human_support")
            self.index.facts["community_group"] = contacts.get("group_url") or self.index.facts.get(
                "community_group"
            )
        if isinstance(points, list):
            self.index.facts["community_points"] = [str(p) for p in points if p]
            # Also keep a flat blob for retrieval
            blob = "\n".join(f"- {p}" for p in self.index.facts["community_points"])
            self.index.decision_summaries.append(f"Community / product points:\n{blob}")
        snippets = data.get("reply_snippets") if isinstance(data, dict) else None
        if isinstance(snippets, dict):
            for lang, lines in snippets.items():
                if not isinstance(lines, list):
                    continue
                chunk = "\n".join(str(x) for x in lines if x)
                if chunk:
                    self.index.faq_chunks.setdefault(str(lang), []).append(
                        ("community", chunk, None)
                    )
        self.index.loaded_files += 1

    def _load_faq_markdown(self) -> None:
        from src.knowledge.source_catalog.faq_canonical import load_canonical, render_faq

        canonical = load_canonical(self.settings.knowledge_root)
        if canonical and canonical.get("entries"):
            for lang in LANG_FOLDER:
                chunks: list[tuple[str, str, str | None]] = []
                for entry in canonical["entries"]:
                    if not isinstance(entry, dict):
                        continue
                    q, a = render_faq(entry, lang)
                    if q and a:
                        chunks.append((q, a, "vpn-installer"))
                self.index.faq_chunks[lang] = chunks
            self.index.loaded_files += 1
            return
        root = self.settings.kb_multilingual_dir
        if not root.is_dir():
            logger.warning("KB dir missing: %s", root)
            return
        for lang, folder in LANG_FOLDER.items():
            lang_dir = root / folder
            if not lang_dir.is_dir():
                continue
            chunks: list[tuple[str, str, str | None]] = []
            for path in sorted(lang_dir.glob("*.md")):
                try:
                    text = path.read_text(encoding="utf-8", errors="replace")
                except OSError as exc:
                    logger.warning("Cannot read %s: %s", path, exc)
                    continue
                self.index.loaded_files += 1
                for title, body in _split_markdown_sections(text, path.stem):
                    if body.strip():
                        chunks.append((title, body.strip(), None))
            self.index.faq_chunks[lang] = chunks

    def _load_product_guides(self) -> None:
        """Load API-independent product structure markdown under knowledge/product_guides."""
        root = self.settings.knowledge_root / "product_guides"
        if not root.is_dir():
            return
        for path in sorted(root.glob("*.md")):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                logger.warning("Cannot read product guide %s: %s", path, exc)
                continue
            name = path.stem.lower()
            # vpn-installer-structure.fa.md → lang fa; *.en.md → en; else all langs
            lang = "en"
            if name.endswith(".fa") or name.endswith("_fa") or name.endswith("-fa"):
                lang = "fa"
            elif name.endswith(".en") or name.endswith("_en") or name.endswith("-en"):
                lang = "en"
            elif name.endswith(".ru") or name.endswith("_ru") or name.endswith("-ru"):
                lang = "ru"
            elif name.endswith(".zh") or name.endswith("_zh") or name.endswith("-zh"):
                lang = "zh"
            # Also strip language suffix from title stem for cleaner headings
            title_stem = re.sub(r"[._-](fa|en|ru|zh)$", "", path.stem, flags=re.I)
            product_id = product_id_from_guide_stem(title_stem)
            self.index.loaded_files += 1
            for title, body in _split_markdown_sections(text, title_stem):
                if not body.strip():
                    continue
                chunk = (f"product-guide:{title}", body.strip(), product_id)
                self.index.faq_chunks.setdefault(lang, []).append(chunk)
                # Cross-index FA/EN guides lightly into the other language for fallback
                if lang == "fa":
                    self.index.faq_chunks.setdefault("en", []).append(chunk)
                elif lang == "en":
                    self.index.faq_chunks.setdefault("fa", []).append(chunk)

    def _load_decision_trees(self) -> None:
        root = self.settings.decision_tree_dir
        if not root.is_dir():
            logger.warning("Decision tree dir missing: %s", root)
            return
        for path in sorted(root.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                logger.warning("Skip tree %s: %s", path, exc)
                continue
            self.index.loaded_files += 1
            summary = _summarize_tree(path.stem, data)
            if summary:
                self.index.decision_summaries.append(summary)

    def retrieve(
        self,
        query: str,
        lang: str,
        *,
        faq_refs: list[str] | None = None,
        limit_chars: int | None = None,
        max_chunks: int = 6,
        include_community: bool = False,
        product_id: str | None = None,
    ) -> str:
        """Score FAQ/KB chunks against query; prefer faq_refs when provided.

        When product_id is set, only that product's guide chunks are used
        (shared multilingual FAQ / other products are excluded).
        """
        limit = limit_chars or self.settings.knowledge_snippet_chars
        q_tokens = tokenize(query)
        scope = (product_id or "").strip() or None
        if scope:
            from src.knowledge.product_catalogs import get_product

            prod = get_product(scope)
            if prod is not None and not prod.catalog_enabled:
                return ""
        raw_chunks = list(self.index.faq_chunks.get(lang) or [])
        # Fallback: also search English KB if sparse (only when not product-scoped)
        if not scope and lang != "en" and self.index.faq_chunks.get("en"):
            raw_chunks.extend(self.index.faq_chunks["en"])
        elif scope and lang != "en" and self.index.faq_chunks.get("en"):
            # Still allow EN product guides for the same product_id
            raw_chunks.extend(self.index.faq_chunks["en"])

        scored: list[tuple[float, str, str]] = []
        refs = {r.upper() for r in (faq_refs or [])}
        for item in raw_chunks:
            if len(item) >= 3:
                title, body, chunk_pid = item[0], item[1], item[2]
            else:
                title, body, chunk_pid = item[0], item[1], None
            if not include_community and title.lower() == "community":
                continue
            if scope:
                if not str(title).startswith("product-guide:"):
                    continue
                if (chunk_pid or "") != scope:
                    continue
            else:
                # Unscoped Ask AI should not leak another product's private guides heavily;
                # still allow guides but prefer general FAQ.
                pass
            score = _overlap_score(q_tokens, tokenize(title + " " + body))
            if refs and any(r in title.upper() or r in body.upper() for r in refs):
                score += 0.45
            if scope and str(title).startswith("product-guide:"):
                score += 0.2
            if "ai-memory" in str(title).lower() or "behavior" in str(title).lower():
                score += 0.8
            if score > 0:
                scored.append((score, title, body))
        scored.sort(key=lambda x: x[0], reverse=True)

        blocks: list[str] = []
        for _, title, body in scored[:max_chunks]:
            snippet = body if len(body) <= 1800 else body[:1800] + "…"
            blocks.append(f"### {title}\n{snippet}")

        # Light decision-tree hints when query looks like troubleshooting
        # (skip when product-scoped — trees are shared/installer-oriented)
        if not scope and any(
            w in query.lower()
            for w in ("error", "fail", "timeout", "ssh", "ошиб", "خطا", "失败", "не работ")
        ):
            for tree in self.index.decision_summaries[:3]:
                if not include_community and tree.startswith("Community"):
                    continue
                blocks.append(tree)

        return _join_limited(blocks, limit)


def _split_markdown_sections(text: str, default_title: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    current_title = default_title
    current_lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("#"):
            if current_lines:
                sections.append((current_title, "\n".join(current_lines)))
                current_lines = []
            current_title = line.lstrip("#").strip() or default_title
        else:
            current_lines.append(line)
    if current_lines:
        sections.append((current_title, "\n".join(current_lines)))
    if not sections and text.strip():
        sections.append((default_title, text.strip()))
    return sections


def _summarize_tree(name: str, data: Any) -> str:
    if not isinstance(data, dict):
        return f"Decision tree: {name}"
    title = data.get("title") or data.get("name") or name
    nodes = data.get("nodes") or data.get("steps") or data.get("tree")
    lines = [f"Decision tree: {title}"]
    if isinstance(data.get("description"), str):
        lines.append(data["description"][:400])
    if isinstance(nodes, list):
        for node in nodes[:8]:
            if isinstance(node, dict):
                label = node.get("title") or node.get("id") or node.get("question")
                if label:
                    lines.append(f"- {label}")
            elif isinstance(node, str):
                lines.append(f"- {node[:120]}")
    elif isinstance(nodes, dict):
        for key in list(nodes.keys())[:8]:
            lines.append(f"- {key}")
    return "\n".join(lines)


def _overlap_score(query_tokens: set[str], doc_tokens: set[str]) -> float:
    if not query_tokens or not doc_tokens:
        return 0.0
    inter = query_tokens & doc_tokens
    if not inter:
        return 0.0
    return len(inter) / (len(query_tokens) ** 0.5 * len(doc_tokens) ** 0.35)


def _join_limited(blocks: list[str], limit: int) -> str:
    out: list[str] = []
    used = 0
    for block in blocks:
        if used + len(block) + 2 > limit:
            break
        out.append(block)
        used += len(block) + 2
    return "\n\n".join(out)
