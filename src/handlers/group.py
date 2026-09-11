"""Group / forum handlers: answer in topics + multilingual announce."""

from __future__ import annotations

import json
import logging
from typing import Any

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from src.ai.client import AIClient, AIClientError
from src.ai.persona import (
    SUPPORT_HANDLE,
    build_system_prompt,
    download_or_site_fallback,
    looks_like_reasoning_leak,
    strip_reasoning_leak,
    wants_contact_links,
)
from src.config import Settings, normalize_lang
from src.knowledge.catalog_search import CatalogSiteSearch
from src.knowledge.loader import KnowledgeLoader
from src.knowledge.product_catalogs import ai_products_snippet
from src.storage.users import UserStore
from src.ui import texts

logger = logging.getLogger(__name__)

router = Router(name="group")


def _silent_for_lang(lang: str) -> bool:
    """RU/ZH topic posts should be sent silently."""
    return lang in {"ru", "zh"}


def _load_group_config(settings: Settings) -> dict[str, Any]:
    path = settings.knowledge_root / "group_community.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save_group_config(settings: Settings, data: dict[str, Any]) -> None:
    path = settings.knowledge_root / "group_community.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _topic_map(cfg: dict[str, Any]) -> dict[str, int]:
    topics = cfg.get("forum_topics") or {}
    out: dict[str, int] = {}
    if isinstance(topics, dict):
        for lang, tid in topics.items():
            if tid is None:
                continue
            try:
                out[str(lang)] = int(tid)
            except (TypeError, ValueError):
                continue
    return out


def _detect_lang(text: str, telegram_code: str | None) -> str:
    t = text or ""
    if any("\u0600" <= ch <= "\u06ff" for ch in t):
        return "fa"
    if any("\u4e00" <= ch <= "\u9fff" for ch in t):
        return "zh"
    if any("\u0400" <= ch <= "\u04ff" for ch in t):
        return "ru"
    return normalize_lang(telegram_code)


def format_facts_safe(knowledge: KnowledgeLoader) -> str:
    from src.ai.persona import format_facts_from_meta

    return format_facts_from_meta(knowledge.index.facts)


def setup_group_router(
    settings: Settings,
    users: UserStore,
    ai: AIClient,
    knowledge: KnowledgeLoader,
    catalog: CatalogSiteSearch,
) -> Router:
    @router.message(F.chat.type.in_({"group", "supergroup"}), Command("map_topic"))
    async def cmd_map_topic(message: Message) -> None:
        """Admin: /map_topic fa  (run inside the target forum topic)."""
        if not message.from_user or not message.text:
            return
        member = await message.chat.get_member(message.from_user.id)
        if member.status not in {"creator", "administrator"}:
            await message.reply("Admin only.", disable_notification=True)
            return
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply("Usage: /map_topic fa|en|ru|zh", disable_notification=True)
            return
        lang = normalize_lang(parts[1])
        thread_id = message.message_thread_id
        if thread_id is None:
            await message.reply("Run this command inside a forum topic.", disable_notification=True)
            return
        cfg = _load_group_config(settings)
        topics = dict(cfg.get("forum_topics") or {})
        topics[lang] = thread_id
        cfg["forum_topics"] = topics
        cfg["group_chat_id"] = message.chat.id
        _save_group_config(settings, cfg)
        await message.reply(f"Mapped topic {thread_id} → {lang}", disable_notification=True)

    @router.message(F.chat.type.in_({"group", "supergroup"}), Command("announce"))
    async def cmd_announce(message: Message) -> None:
        """Admin: /announce <topic text> → generate FA/EN/RU/ZH posts into mapped topics."""
        if not message.from_user or not message.text:
            return
        member = await message.chat.get_member(message.from_user.id)
        if member.status not in {"creator", "administrator"}:
            await message.reply("Admin only.", disable_notification=True)
            return
        raw = message.text.split(maxsplit=1)
        if len(raw) < 2 or not raw[1].strip():
            await message.reply("Usage: /announce your source notes…", disable_notification=True)
            return
        source = raw[1].strip()
        from src.knowledge.source_catalog.questions import (
            fingerprint,
            is_duplicate_post,
            record_post,
        )

        qfp = fingerprint(source)
        if is_duplicate_post(settings.data_dir, qfp, qfp):
            await message.reply(
                "Duplicate educational topic (same fingerprint). Not posted.",
                disable_notification=True,
            )
            return
        cfg = _load_group_config(settings)
        topics = _topic_map(cfg)
        if not topics:
            await message.reply(
                "No forum topics mapped yet. In each language topic run: /map_topic fa",
                disable_notification=True,
            )
            return

        wait = await message.reply("Generating multilingual posts…", disable_notification=True)
        kb = knowledge.retrieve(source, "en", limit_chars=4000)
        cat = catalog.catalog_snippet(source, lang="en")
        products = ai_products_snippet(source, lang="en")
        posted = 0
        for lang, thread_id in topics.items():
            system = build_system_prompt(lang, facts_block=format_facts_safe(knowledge))
            prompt = (
                "Write a short Telegram group post (max 900 chars) for Black Fox Group.\n"
                "Product name is VPS to VPN. Do not invent facts beyond Knowledge/Catalog.\n"
                "No invented prices/versions. Persian: start every sentence with a Persian word; "
                "prefer Persian wording; never rename official product names.\n"
                f"Source notes:\n{source}\n\nKnowledge:\n{kb}\n\n"
                f"Products:\n{products or '(none)'}\n\nCatalog:\n{cat or '(none)'}"
            )
            try:
                body = await ai.chat(
                    [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ]
                )
            except AIClientError as exc:
                logger.exception("announce AI fail %s: %s", lang, exc)
                continue
            try:
                await message.bot.send_message(
                    chat_id=message.chat.id,
                    text=body[:3900],
                    message_thread_id=thread_id,
                    disable_notification=_silent_for_lang(lang),
                )
                posted += 1
            except Exception as exc:
                logger.warning("announce send fail %s: %s", lang, exc)
        if posted:
            record_post(settings.data_dir, question_fp=qfp, content_fp=qfp, langs=list(topics))
        try:
            await wait.edit_text(f"Posted to {posted}/{len(topics)} topics.")
        except Exception:
            pass

    @router.message(
        F.chat.type.in_({"group", "supergroup"}),
        F.text,
        ~F.text.startswith("/"),
    )
    async def on_group_text(message: Message) -> None:
        """Answer when the bot is mentioned or replied to in a group topic."""
        if not message.from_user or not message.text or not message.bot:
            return
        text = message.text.strip()
        me = await message.bot.get_me()
        mentioned = bool(me.username and f"@{me.username}".lower() in text.lower())
        is_reply_to_bot = bool(
            message.reply_to_message
            and message.reply_to_message.from_user
            and message.reply_to_message.from_user.id == me.id
        )
        if not mentioned and not is_reply_to_bot:
            return

        clean = text
        if me.username:
            clean = clean.replace(f"@{me.username}", "").replace(
                f"@{me.username.lower()}", ""
            )
        clean = clean.strip()
        if not clean:
            return

        lang = _detect_lang(clean, message.from_user.language_code)
        wait = await message.reply(
            texts.t(texts.THINKING, lang),
            disable_notification=_silent_for_lang(lang),
        )
        kb = knowledge.retrieve(clean, lang, limit_chars=6000)
        cat = catalog.catalog_snippet(clean, lang=lang)
        products = ai_products_snippet(clean, lang=lang)
        system = build_system_prompt(lang, facts_block=format_facts_safe(knowledge))
        prompt = (
            f"Group question:\n{clean}\n\n"
            f"Knowledge:\n{kb or '(none)'}\n\n"
            f"Products:\n{products or '(none)'}\n\n"
            f"Catalog:\n{cat or '(none)'}\n\n"
            "Reply briefly for Telegram group. If unsure, say so and point to "
            f"{SUPPORT_HANDLE}. Persian: start every sentence with a Persian word; "
            "prefer Persian wording; never rename official product names.\n"
            "CRITICAL: Output ONLY the final reply — no reasoning or meta analysis."
        )
        try:
            answer = await ai.chat(
                [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ]
            )
        except AIClientError:
            if wants_contact_links(clean):
                answer = download_or_site_fallback(lang)
            else:
                await wait.edit_text(texts.t(texts.AI_ERROR, lang))
                return
        answer = strip_reasoning_leak(answer)
        if looks_like_reasoning_leak(answer):
            answer = (
                download_or_site_fallback(lang)
                if wants_contact_links(clean)
                else texts.t(texts.AI_ERROR, lang)
            )
        try:
            await wait.edit_text(answer[:3900])
        except Exception:
            await message.reply(answer[:3900], disable_notification=_silent_for_lang(lang))

    return router
