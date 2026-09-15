"""Chat message handler: Ask AI mode only → intent / LLM with KB + catalog/site."""

from __future__ import annotations

import asyncio
import logging
import time

from aiogram import F, Router
from aiogram.types import Message

from src.ai.client import AIClient, AIClientError
from src.ai.persona import (
    SUPPORT_HANDLE,
    append_sales_if_needed,
    build_system_prompt,
    download_or_site_fallback,
    format_facts_from_meta,
    join_context_blocks,
    excerpt_teaching_for_query,
    looks_incomplete_reply,
    looks_like_prompt_dump,
    looks_like_reasoning_leak,
    sanitize_reply_links,
    strip_internal_prompt_lines,
    wants_contact_links,
    wants_sales_nudge,
)
from src.ai.safety import (
    ResponseBudget,
    bounded_ask_timeout,
    bounded_ask_tokens,
    is_safe_to_persist,
    is_transient_ai_error,
    prepare_user_reply,
)
from src.access import AdminAccess
from src.config import Settings, is_bot_admin
from src.knowledge.ai_memory import (
    append_learned_answer,
    behavior_rules_text,
    catalog_teaching_text,
    memory_prompt_block,
    product_memory_has_content,
)
from src.knowledge.ai_profile import (
    ai_profile_prompt_block,
    load_ai_profile,
    reply_rules as ai_reply_rules,
)
from src.knowledge.catalog_index import wants_send_media
from src.knowledge.catalog_rag import retrieve_catalog_context
from src.knowledge.response_bundle import (
    MediaRef,
    ResponseBundle,
    existing_media_paths,
)
from src.knowledge.catalog_search import CatalogSiteSearch, looks_unsure, unsure_handoff
from src.knowledge.feature_lookup_adapter import (
    feature_lookup_prompt_block,
    has_implementation_exists,
)
from src.knowledge.intents import IntentMatcher, detect_reply_lang, looks_creator, looks_identity, looks_usage_howto
from src.knowledge.loader import KnowledgeLoader
from src.knowledge.product_catalogs import (
    ai_products_snippet,
    feature_howto_text,
    get_product,
    list_all_product_dicts,
    match_feature_for_query,
    resolve_media_paths_for_query,
)
from src.storage.answer_memory import AnswerMemoryStore
from src.storage.metrics import MetricsStore
from src.storage.users import UserStore
from src.ui import admin_keyboards, keyboards, messaging, texts

logger = logging.getLogger(__name__)

router = Router(name="chat")

ASK_AI_KNOWLEDGE_CHARS = 6000


def _ask_ai_timeout(settings: Settings) -> float:
    return bounded_ask_timeout(settings.ai_timeout_seconds)


def _ask_ai_max_tokens(settings: Settings) -> int:
    return bounded_ask_tokens(settings.ai_max_tokens)


class _AskTiming:
    def __init__(self) -> None:
        self.t0 = time.monotonic()
        self.last = self.t0
        self.parts: list[str] = []

    def mark(self, name: str) -> None:
        now = time.monotonic()
        self.parts.append(f"{name}={int((now - self.last) * 1000)}")
        self.last = now

    def flush(self) -> None:
        total = int((time.monotonic() - self.t0) * 1000)
        logger.info("ask_ai_timing total_ms=%s %s", total, " ".join(self.parts))


def _bundle_from_retrieval(
    product_id: str, query: str, retrieval
) -> ResponseBundle:
    refs: list[MediaRef] = []
    for unit in getattr(retrieval, "media_units", None) or []:
        rel = str(getattr(unit, "media_path", "") or "").strip()
        pid = str(getattr(unit, "product_id", "") or "").strip()
        if not rel or not pid:
            continue
        refs.append(
            MediaRef(
                path=rel,
                product_id=pid,
                unit_id=str(getattr(unit, "unit_id", "") or ""),
                feature_ids=list(getattr(unit, "feature_ids", None) or []),
                score=float(getattr(unit, "score", 0.0) or 0.0),
            )
        )
    return ResponseBundle(
        product_id=product_id or "",
        user_query=query,
        knowledge_refs=[
            str(u.unit_id)
            for u in (getattr(retrieval, "units", None) or [])
            if getattr(u, "unit_id", None)
        ],
        media_refs=refs if getattr(retrieval, "attach_media", False) else [],
    )


def _is_free_text(message: Message) -> bool:
    text = (message.text or "").strip()
    if not text or text.startswith("/"):
        return False
    if text in keyboards.all_lang_button_texts():
        return False
    if text in keyboards.all_menu_button_texts():
        return False
    if text in admin_keyboards.all_admin_control_texts():
        return False
    return True


def setup_chat_router(
    settings: Settings,
    users: UserStore,
    ai: AIClient,
    intents: IntentMatcher,
    knowledge: KnowledgeLoader,
    catalog: CatalogSiteSearch,
    metrics: MetricsStore,
    access: AdminAccess | None = None,
) -> Router:
    memory = AnswerMemoryStore(settings.data_dir / "answer_memory.json")

    @router.message(F.chat.type == "private", F.text.func(lambda t: bool(t) and not str(t).startswith("/")))
    async def on_text(message: Message) -> None:
        if not _is_free_text(message):
            return
        user = message.from_user
        if not user or not message.text:
            return

        try:
            await users.touch_from_telegram_user(user)
            await _handle_ask_ai_text(message, user)
        except Exception:
            logger.exception("Ask AI handler crashed")
            try:
                lang = await users.get_lang(user.id, user.language_code)
                await message.answer(texts.t(texts.AI_ERROR, lang))
            except Exception:  # noqa: BLE001
                pass

    async def _handle_ask_ai_text(message: Message, user) -> None:
        if not await users.has_lang(user.id):
            hint = await users.get_lang(user.id, user.language_code)
            await message.answer(
                texts.t(texts.NEED_LANGUAGE_FIRST, hint),
                reply_markup=keyboards.language_keyboard(),
            )
            return

        lang = await users.get_lang(user.id, user.language_code)
        # Answer in the language of THIS question (not only profile preference).
        text_for_lang = (message.text or "").strip()
        lang = detect_reply_lang(text_for_lang, lang)
        if access is not None:
            menu_kb = keyboards.main_menu_keyboard(
                lang,
                can_settings=await access.can_settings(user.id),
                can_stats=await access.can_stats(user.id),
            )
        else:
            admin = is_bot_admin(settings, user.id)
            menu_kb = keyboards.main_menu_keyboard(lang, is_admin=admin)

        if not await users.is_ask_ai(user.id):
            await message.answer(
                texts.t(texts.USE_MENU_OR_ASK_AI, lang),
                reply_markup=menu_kb,
            )
            if not await users.was_group_invited(user.id):
                await message.answer(
                    texts.t(texts.GROUP_INVITE, lang),
                    reply_markup=menu_kb,
                )
                await users.set_group_invited(user.id, True)
            return

        text = message.text.strip()
        if not text:
            return

        await metrics.record_conversation(user.id)

        if looks_identity(text):
            body = texts.bot_intro(lang)
            ask_product = await users.get_ask_ai_product(user.id)
            if ask_product:
                product = get_product(ask_product)
                title = product.label(lang) if product else ask_product
                if (lang or "").startswith("fa"):
                    body = (
                        f"{body}\n\n"
                        f"الان داخل کاتالوگ «{title}» هستی؛ "
                        "سوال‌های این محصول را اینجا بپرس تا جواب همان بخش را بدهم."
                    )
                else:
                    body = (
                        f"{body}\n\n"
                        f"You are in the «{title}» catalog — ask about this product here."
                    )
            await users.append_chat(user.id, "user", text)
            await users.append_chat(user.id, "assistant", body)
            await metrics.record_answered(referred_support=False, ai_solved=True)
            await message.answer(
                body,
                reply_markup=keyboards.ask_ai_keyboard(
                    lang, product_id=ask_product
                ),
            )
            return

        if looks_creator(text):
            from src.branding import load_creator_contact
            creator = load_creator_contact(settings.knowledge_root)
            body = creator.format_card(lang)
            ask_product = await users.get_ask_ai_product(user.id)
            if ask_product:
                product = get_product(ask_product)
                title = product.label(lang) if product else ask_product
                if (lang or "").startswith("fa"):
                    body = (
                        f"{body}\n\n"
                        f"اگر سوالت دربارهٔ محصول «{title}» است، همان را بپرس تا راهنمای همان بخش را بدهم."
                    )
                else:
                    body = (
                        f"{body}\n\n"
                        f"If your question is about «{title}», ask it here for that product's guide."
                    )
            await users.append_chat(user.id, "user", text)
            await users.append_chat(user.id, "assistant", body)
            await metrics.record_answered(referred_support=False, ai_solved=True)
            await message.answer(
                body,
                reply_markup=keyboards.ask_ai_keyboard(
                    lang, product_id=ask_product
                ),
            )
            return

        ask_product = await users.get_ask_ai_product(user.id)
        if ask_product:
            row = next(
                (
                    d
                    for d in list_all_product_dicts(settings.knowledge_root)
                    if str(d.get("product_id") or "") == ask_product
                ),
                None,
            )
            if row is None or row.get("enabled", True) is False:
                await users.set_ask_ai(user.id, False)
                await message.answer(
                    "این محصول دیگر در دسترس نیست. از منو دوباره «سوال از AI» را برای یک محصول فعال بزنید."
                    if (lang or "").startswith("fa")
                    else "This product is no longer available. Open Ask AI again from an active product.",
                    reply_markup=keyboards.main_menu_keyboard(lang),
                )
                return
        ask_kb = keyboards.ask_ai_keyboard(lang, product_id=ask_product)
        stages = _AskTiming()
        history = await users.get_chat_history(user.id)
        history_blob = "\n".join(
            f"{h['role']}: {h['content']}"
            for h in history[-4:]
            if not looks_like_prompt_dump(str(h.get("content") or ""))
        )
        stages.mark("session")

        if wants_send_media(text):
            last = ResponseBundle.from_dict(await users.get_last_ask_context(user.id))
            pid = (ask_product or (last.product_id if last else "") or "").strip()
            paths = []
            if last and pid and last.product_id == pid:
                paths = existing_media_paths(
                    last.media_refs,
                    product_id=pid,
                    knowledge_refs=last.knowledge_refs,
                    project_root=settings.project_root,
                    limit=2,
                )
                # If prior answer matched a feature but forgot media_refs, resolve from catalog.
                if not paths:
                    feat_id = ""
                    for ref in last.knowledge_refs or []:
                        r = str(ref or "")
                        prefix = f"feature:{pid}:"
                        if r.startswith(prefix):
                            feat_id = r[len(prefix):].strip()
                            if feat_id:
                                break
                    prod = get_product(pid) if feat_id else None
                    matched_feat = None
                    if prod is not None and feat_id:
                        for feat in prod.features or []:
                            if isinstance(feat, dict) and str(feat.get("id") or "") == feat_id:
                                matched_feat = feat
                                break
                    if matched_feat is None and prod is not None:
                        # Fall back to paraphrase match on recent history / last answer context
                        hist_q = ""
                        for h in reversed(history[-6:] or []):
                            if str(h.get("role") or "") == "user":
                                cand = str(h.get("content") or "").strip()
                                if cand and not wants_send_media(cand):
                                    hist_q = cand
                                    break
                        if hist_q:
                            hit = match_feature_for_query(
                                hist_q, lang=lang, product_id=pid
                            )
                            if hit is not None:
                                _c, matched_feat, _s = hit
                                prod = _c
                    if matched_feat is not None and prod is not None:
                        paths = resolve_media_paths_for_query(
                            text,
                            project_root=settings.project_root,
                            lang=lang,
                            limit=2,
                            feature=matched_feat,
                            product=prod,
                        )
            if paths:
                caption = (
                    "تصویر همان بخشی که الان درباره‌اش صحبت شد."
                    if (lang or "").startswith("fa")
                    else "Photo for the section we just discussed."
                )
                await users.append_chat(user.id, "user", text)
                await users.append_chat(user.id, "assistant", caption)
                await metrics.record_answered(referred_support=False, ai_solved=True)
                await messaging.answer_with_media(
                    message, caption, images=paths, reply_markup=ask_kb
                )
                stages.mark("followup_media")
                stages.flush()
                return
            await message.answer(
                "برای این بخش تصویر مرتبط موجود نیست."
                if (lang or "").startswith("fa")
                else "No related image is stored for this section.",
                reply_markup=ask_kb,
            )
            stages.mark("followup_none")
            stages.flush()
            return

        operator_style = behavior_rules_text(settings.knowledge_root, ask_product)
        ai_profile = (
            load_ai_profile(settings.knowledge_root, ask_product) if ask_product else None
        )
        profile_rules = ai_reply_rules(ai_profile) if ask_product else ai_reply_rules(None)
        profile_block = ai_profile_prompt_block(ai_profile) if ask_product else ""
        # Product-scoped Ask AI must not reuse answers from another catalog.
        mem_hit = None if ask_product else memory.lookup(text, lang=lang)
        if (
            mem_hit is not None
            and mem_hit.score >= 12.0
            and not looks_unsure(mem_hit.answer)
            and not looks_incomplete_reply(mem_hit.answer)
            and not looks_like_reasoning_leak(mem_hit.answer)
        ):
            final = mem_hit.answer
            memory.touch_hit(mem_hit.topic_key, lang)
            await users.append_chat(user.id, "user", text)
            await users.append_chat(user.id, "assistant", final)
            await metrics.record_answered(referred_support=False, ai_solved=True)
            await message.answer(final, reply_markup=ask_kb)
            stages.mark("memory_hit")
            stages.flush()
            return

        match = None if ask_product else intents.match(text, lang, prior_blob=history_blob)
        wait = await message.answer(texts.t(texts.THINKING, lang))
        request_timeout = _ask_ai_timeout(settings)
        budget = ResponseBudget(request_timeout + 8.0)
        stages.mark("wait_msg")

        intent_name = match.record.intent if match and match.record else None
        faq_refs = None if ask_product else (match.record.faq_refs if match and match.record else None)

        def _run_rag():
            return retrieve_catalog_context(
                text,
                lang=lang,
                project_root=settings.project_root,
                limit_features=3,
                limit_media=2,
                product_id=ask_product,
                prior_text=history_blob,
            )

        def _run_kb():
            return knowledge.retrieve(
                text,
                lang,
                faq_refs=faq_refs,
                limit_chars=min(ASK_AI_KNOWLEDGE_CHARS, settings.knowledge_snippet_chars),
                include_community=wants_contact_links(text) and not ask_product,
                max_chunks=3 if ask_product else 4,
                product_id=ask_product,
            )

        retrieval, kb_snip = await asyncio.gather(
            asyncio.to_thread(_run_rag),
            asyncio.to_thread(_run_kb),
        )
        stages.mark("retrieve")
        if ask_product:
            retrieval.units = [
                u for u in retrieval.units if getattr(u, "product_id", "") == ask_product
            ]
            retrieval.media_units = [
                u
                for u in (retrieval.media_units or [])
                if getattr(u, "product_id", "") == ask_product
            ]
        bundle = _bundle_from_retrieval(ask_product or "", text, retrieval)
        media_paths = []
        if (
            ask_product
            and getattr(retrieval, "attach_media", False)
            and profile_rules.get("attach_catalog_media", True)
        ):
            media_paths = existing_media_paths(
                bundle.media_refs,
                product_id=ask_product or "",
                knowledge_refs=bundle.knowledge_refs,
                project_root=settings.project_root,
                limit=2,
                min_score=12.0,
            )

        # Matched catalog feature media is language-independent and must win over
        # weaker RAG media picks (e.g. EN install wrongly attaching Backup).
        if ask_product:
            feat_hit = match_feature_for_query(
                text, lang=lang, product_id=ask_product
            )
            if feat_hit is not None:
                matched_cat, matched_feat, _matched_score = feat_hit
                feat_paths = resolve_media_paths_for_query(
                    text,
                    project_root=settings.project_root,
                    lang=lang,
                    limit=2,
                    feature=matched_feat,
                    product=matched_cat,
                )
                want_media = bool(feat_paths) and profile_rules.get(
                    "attach_catalog_media", True
                ) and (
                    getattr(retrieval, "attach_media", False)
                    or wants_send_media(text)
                    or looks_usage_howto(text)
                )
                if not want_media and feat_paths:
                    from src.knowledge.catalog_rag import (
                        is_educational_question,
                        wants_catalog_media,
                    )

                    want_media = wants_catalog_media(text) or is_educational_question(
                        text
                    )
                if want_media and feat_paths:
                    media_paths = feat_paths
                    retrieval.attach_media = True
                    fid = str(matched_feat.get("id") or "").strip()
                    refs: list[MediaRef] = []
                    root = settings.project_root.resolve()
                    for path in feat_paths:
                        try:
                            rel = str(path.resolve().relative_to(root)).replace("\\", "/")
                        except ValueError:
                            rel = str(path)
                        refs.append(
                            MediaRef(
                                path=rel,
                                product_id=ask_product,
                                unit_id=f"feature-media:{fid}:{path.name}",
                                feature_ids=[fid] if fid else [],
                                score=20.0,
                            )
                        )
                    bundle.media_refs = refs
                    if fid:
                        feat_ref = f"feature:{ask_product}:{fid}"
                        bundle.knowledge_refs = list(
                            dict.fromkeys(
                                [feat_ref] + list(bundle.knowledge_refs or [])
                            )
                        )

        if (
            ask_product
            and getattr(retrieval, "needs_clarification", False)
            and getattr(retrieval, "clarifying_question", None)
        ):
            clarify = str(retrieval.clarifying_question)
            try:
                await wait.delete()
            except Exception:  # noqa: BLE001
                pass
            await message.answer(clarify, reply_markup=ask_kb)
            await users.append_chat(user.id, "user", text)
            await users.append_chat(user.id, "assistant", clarify)
            await metrics.record_answered(referred_support=False, ai_solved=False)
            if ask_product:
                bundle.answer_text = clarify
                await users.set_last_ask_context(user.id, bundle.as_dict())
            stages.mark("clarify_backup")
            stages.flush()
            return

        if (
            not ask_product
            and retrieval.insufficient
            and match is not None
            and match.low_confidence
            and match.clarifying_question
        ):
            try:
                await wait.delete()
            except Exception:  # noqa: BLE001
                pass
            await message.answer(match.clarifying_question, reply_markup=ask_kb)
            await users.append_chat(user.id, "user", text)
            await users.append_chat(user.id, "assistant", match.clarifying_question)
            await metrics.record_answered(referred_support=False, ai_solved=False)
            stages.flush()
            return

        # License/site catalogs are Installer-oriented — only when that product is scoped
        catalog_snip = ""
        if not ask_product or ask_product == "vpn-installer":
            catalog_snip = catalog.catalog_snippet(text, lang=lang)
        if ask_product:
            cat = get_product(ask_product)
            title = ""
            if cat is not None:
                title = (
                    (cat.title or {}).get(lang)
                    or (cat.title or {}).get("en")
                    or ask_product
                )
            products_snip = f"Product identity: {ask_product}" + (
                f" — {title}" if title else ""
            )
        else:
            products_snip = ai_products_snippet(
                text, lang=lang, product_id=ask_product
            )
        site_snip = ""
        try:
            if (
                not ask_product
                and (
                    retrieval.insufficient
                    or match.low_confidence
                    or wants_sales_nudge(text, intent_name)
                    or wants_contact_links(text)
                )
            ):
                site_snip = await catalog.site_snippet(text)
            elif ask_product == "vpn-installer" and (
                wants_sales_nudge(text, intent_name) or wants_contact_links(text)
            ):
                site_snip = await catalog.site_snippet(text)
        except Exception:
            logger.exception("site search failed")

        intent_block = ""
        if match and match.record and not ask_product:
            intent_block = join_context_blocks(
                [
                    f"Matched intent: {match.record.intent} (score={match.score:.2f})",
                    f"Category: {match.record.category}",
                    f"Short answer: {match.record.short_answer}",
                    f"Full answer: {match.record.full_answer}",
                ],
                3500,
            )
        facts = format_facts_from_meta(knowledge.index.facts or intents.facts)
        system = build_system_prompt(
            lang, facts_block=facts, operator_style=operator_style
        )
        catalog_teach = (
            catalog_teaching_text(settings.knowledge_root, ask_product)
            if ask_product
            else ""
        )
        memory_snip = (
            ""
            if ask_product
            else memory_prompt_block(settings.knowledge_root, ask_product)
        )

        md_priority_note = (
            "### Priority\n"
            "1) Operator AI memory (behavior + taught facts + learned Q&A).\n"
            "2) Product catalog / screenshots.\n"
            "3) Other markdown only if memory and catalog lack the fact.\n"
            "Never invent steps. Follow operator behavior rules in every reply.\n"
            "Write a tutor reply. Do not paste the entire teaching document.\n"
        )

        def _user_facing_fallback() -> str:
            # Prefer a single feature howto in the question language (no bilingual dump).
            if ask_product and profile_rules.get("use_howto", True):
                hit = match_feature_for_query(text, lang=lang, product_id=ask_product)
                if hit is not None:
                    _c, feat, _s = hit
                    howto = feature_howto_text(feat, lang)
                    title = (
                        (feat.get("title") or {}).get(lang)
                        or (feat.get("title") or {}).get("en")
                        or str(feat.get("id") or "")
                    )
                    if howto and not looks_like_prompt_dump(howto):
                        if (lang or "").startswith("fa"):
                            return f"{title}\n\n{howto}"
                        return f"{title}\n\n{howto}"
            teach = strip_internal_prompt_lines(catalog_teach)
            # Drop English Design goal / Behavior lines when answering Persian (and vice versa).
            if (lang or "").startswith("fa"):
                teach = "\n".join(
                    ln
                    for ln in teach.splitlines()
                    if not ln.strip().lower().startswith(("design goal:", "behavior:"))
                    and not ln.strip().startswith("## ")
                )
            elif (lang or "").startswith("en"):
                teach = "\n".join(
                    ln
                    for ln in teach.splitlines()
                    if not ln.strip().startswith(("هدف طراحی:", "عملکرد:"))
                    and not ln.strip().startswith("## ")
                )
            excerpt = excerpt_teaching_for_query(teach, text, limit=900)
            if excerpt and not looks_like_prompt_dump(excerpt):
                if (lang or "").startswith("fa"):
                    return "بر اساس راهنمای همین محصول:\n\n" + excerpt
                return "From this product catalog:\n\n" + excerpt
            for unit in retrieval.units or []:
                body = excerpt_teaching_for_query(unit.body or "", text, limit=700)
                if body and not looks_like_prompt_dump(body):
                    return body
            return ""

        if ask_product:
            teach_excerpt = excerpt_teaching_for_query(
                strip_internal_prompt_lines(catalog_teach), text, limit=900
            )
            extra_sources = join_context_blocks(
                [
                    products_snip,
                    (
                        "Relevant catalog teaching (do not paste the whole file):\n"
                        + teach_excerpt
                    )
                    if teach_excerpt
                    else "",
                    retrieval.prompt_block,
                ],
                4000,
            )
        else:
            extra_sources = join_context_blocks(
                [
                    memory_snip,
                    retrieval.prompt_block,
                    md_priority_note,
                    products_snip,
                    catalog_snip,
                    site_snip,
                ],
                7000,
            )

        
        # Phase 2: Implementation feature.lookup before Catalog false-negative
        _impl_pid = ask_product or "vps-to-vpn"
        if _impl_pid in ("vpn-installer", "vps-to-vpn", "") or not ask_product:
            _impl_block = feature_lookup_prompt_block(text, product_id="vps-to-vpn")
            if _impl_block:
                extra_sources = join_context_blocks([_impl_block, extra_sources], 7500)

        history_section = history_blob or "(none)"
        product_scope = (
            f"Product catalog scope: {ask_product}\n"
            "Answer ONLY from this product's catalog, ai_profile.json, and this product's AI_BEHAVIOR.md.\n"
            "If those sources lack the fact, say you do not know. "
            "Do not use another product catalog. Do not invent steps.\n"
            + (profile_block + "\n\n" if profile_block else "\n")
            if ask_product
            else ""
        )
        # Product-scoped usage tutor: paraphrases → closest catalog howto
        # for ANY ask_product that has a feature catalog (not only Expert/VPS).
        expert_usage_block = ""
        _tutor_prod = get_product(ask_product) if ask_product else None
        if (
            ask_product
            and profile_rules.get("use_howto", True)
            and _tutor_prod is not None
            and (_tutor_prod.features or [])
        ):
            matched_howto = ""
            matched_title = ""
            product_label = (
                ((_tutor_prod.title or {}).get(lang) if _tutor_prod else None)
                or ((_tutor_prod.title or {}).get("en") if _tutor_prod else None)
                or (
                    "VPS to VPN"
                    if ask_product == "vpn-installer"
                    else (
                        "Expert Installer"
                        if ask_product == "telegram-bot-expert-installer"
                        else (
                            "Config Builder"
                            if ask_product == "config-builder"
                            else (
                                "Smart Support Bot"
                                if ask_product == "agent-bot"
                                else ask_product
                            )
                        )
                    )
                )
            )
            hit = match_feature_for_query(
                text, lang=lang, product_id=ask_product
            )
            if hit is not None:
                _cat_hit, feat_hit, _score = hit
                matched_howto = feature_howto_text(feat_hit, lang)
                matched_title = (
                    (feat_hit.get("title") or {}).get(lang)
                    or (feat_hit.get("title") or {}).get("en")
                    or str(feat_hit.get("id") or "")
                )
            want_tutor = looks_usage_howto(text) or bool(matched_howto)
            if not matched_howto and want_tutor:
                prod = get_product(ask_product)
                if prod is not None:
                    chunks = []
                    for feat in prod.features or []:
                        if not isinstance(feat, dict):
                            continue
                        body = feature_howto_text(feat, lang)
                        if body:
                            title = (feat.get("title") or {}).get(lang) or feat.get("id") or ""
                            chunks.append(f"{title}\n{body}")
                    matched_howto = "\n\n".join(chunks[:8])
            if (lang or "").startswith("fa"):
                expert_usage_block = (
                    f"### {product_label} intent + usage (ONLY this product)\n"
                    "کاربر ممکن است سوال را با هر عبارتی بپرسد. اول مفهوم و نیت سوال را عمیق بفهم، "
                    f"بعد نزدیک‌ترین بخش کاتالوگ {product_label} را انتخاب کن و فقط همان را جواب بده.\n"
                    "اگر سوال دربارهٔ نحوهٔ کار / گیر کردن / از کجا بزنم / ثبت سرور است، مثل همکار پشتیبانی دقیق جواب بده:\n"
                    "۱) این بخش چیست\n"
                    "۲) برای چه است\n"
                    "۳) مراحل مرتب با نام دکمه/صفحه\n"
                    "۴) یک نکته، محدودیت یا اشتباه رایج از کاتالوگ\n"
                    f"قدم اختراع نکن. ویژگی‌ای که در کاتالوگ نیست نساز. فقط {product_label}.\n"
                    "اگر عکس در media index همان بخش هست، انکار نکن؛ ربات خودش می‌فرستد.\n"
                    + (
                        f"بخش تشخیص‌داده‌شده: {matched_title}\n"
                        if matched_title
                        else "اگر مطمئن نیستی کدام بخش است، از روی مفهوم سوال نزدیک‌ترین howto را انتخاب کن.\n"
                    )
                    + f"منبع howto:\n{matched_howto or '(از evidence کاتالوگ)'}\n\n"
                )
            else:
                expert_usage_block = (
                    f"### {product_label} intent + usage (ONLY this product)\n"
                    "Users phrase questions many ways. Infer intent carefully first, "
                    f"map to the closest {product_label} catalog section, then answer only that section.\n"
                    "If it is about how to use / stuck / which button / register a server, reply as a careful support teammate:\n"
                    "1) what it is  2) what it is for  3) ordered UI steps  4) one limit/tip/common mistake from the catalog.\n"
                    f"Do not invent steps or features. {product_label} catalog only.\n"
                    "If the catalog media index lists a photo for that section, never deny it — the bot attaches files.\n"
                    + (
                        f"Detected section: {matched_title}\n"
                        if matched_title
                        else "If unsure which section, pick the closest howto by meaning.\n"
                    )
                    + f"Howto source:\n{matched_howto or '(use catalog evidence)'}\n\n"
                )
        user_prompt = (
            f"{product_scope}"
            f"{expert_usage_block}"
            f"Prior turns in this Ask AI session:\n{history_section}\n\n"
            f"User question:\n{text}\n\n"
            f"Expanded topic hints (internal):\n{retrieval.query_expanded}\n\n"
            f"Intent context:\n{intent_block or '(none)'}\n\n"
            f"Knowledge / product-map markdown snippets:\n{kb_snip or '(none)'}\n\n"
            f"Catalog / site sources:\n{extra_sources or '(none)'}\n\n"
            "Write a helpful Telegram support reply as a real tutor/support agent.\n"
            f"CRITICAL language rule: reply ONLY in language code={lang}. "
            "Match the question language exactly. Do not mix FA/EN/RU/ZH in one reply. "
            "Do not paste Design goal/Behavior/هدف طراحی labels from another language.\n"
            "Do not paste catalog training headers or ## section ids.\n"
            "Source order: (1) Operator AI memory, (2) catalog evidence, "
            "(3) other markdown — never invent steps.\n"
            "When the question is educational, explain: what it is, what it is for, "
            "ordered steps, and any limit/tip present in the evidence.\n"
            "Do not list only button names. Finish every sentence completely.\n"
            "Do not invent versions or fake limits.\n"
            "If catalog lists prices and the user asked price/buy, you may quote catalog figures.\n"
            "If sources are insufficient, say you do not know and tell them to message "
            f"{SUPPORT_HANDLE}.\n"
            "Do not include website/group/@support links unless contact/purchase was asked "
            "or you are honestly handing off because you do not know.\n"
            "If the catalog media index lists a photo, it exists. Never deny that the photo exists.\n"
            "The bot sends catalog files itself. Do not say you cannot send images.\n"
            "If prior turns show Exit Server, answer Add Exit Server only — not Central Full Deploy.\n"
            "Persian: start every sentence with a Persian word; prefer Persian wording; "
            "never rename official product names "
            "(VPS to VPN by Black Fox Group, Config Builder, Ask AI, 3X-UI, …).\n"
            "CRITICAL: Output ONLY the final Telegram reply. "
            "Do not write reasoning, constraint lists, or English meta analysis. "
            "Do not paste catalog teaching or memory files verbatim."
        )

        async def _compact_retry() -> str:
            teach = excerpt_teaching_for_query(
                strip_internal_prompt_lines(catalog_teach), text, limit=900
            )
            if not teach:
                return ""
            compact = (
                f"User question:\n{text}\n\n"
                f"Product teaching (source only; do not paste the whole file):\n{teach}\n\n"
                "Write a short Telegram tutor reply in the user's language. "
                "Explain the asked part in a few lines. No file headers."
            )
            try:
                return await asyncio.wait_for(
                    ai.chat(
                        [
                            {"role": "system", "content": system},
                            {"role": "user", "content": compact},
                        ],
                        max_tokens=min(1024, _ask_ai_max_tokens(settings)),
                    ),
                    timeout=max(8.0, min(12.0, budget.remaining())),
                )
            except (AIClientError, asyncio.TimeoutError):
                logger.exception("Ask AI compact retry failed")
                return ""

        try:
            answer = await asyncio.wait_for(
                ai.chat(
                    [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user_prompt},
                    ],
                    max_tokens=_ask_ai_max_tokens(settings),
                ),
                timeout=request_timeout,
            )
        except (AIClientError, asyncio.TimeoutError) as exc:
            logger.exception("AI chat failed: %s", exc)
            retry = ""
            if not isinstance(exc, asyncio.TimeoutError) and is_transient_ai_error(exc) and budget.can_retry():
                retry = await _compact_retry()
            safe_retry = prepare_user_reply(retry) if retry else ""
            if safe_retry:
                answer = safe_retry
            else:
                fallback = _user_facing_fallback()
                if not fallback and not ask_product and match and match.record:
                    fallback = (
                        (match.record.full_answer or "").strip()
                        or (match.record.short_answer or "").strip()
                    )
                if not fallback and (
                    wants_contact_links(text) or wants_sales_nudge(text, intent_name)
                ):
                    fallback = download_or_site_fallback(lang)
                if fallback:
                    answer = fallback
                elif media_paths:
                    answer = (
                        "تصویر کاتالوگ از فایل ذخیره‌شده ارسال می‌شود."
                        if (lang or "").startswith("fa")
                        else "Sending the stored catalog photo."
                    )
                else:
                    try:
                        await wait.delete()
                    except Exception:  # noqa: BLE001
                        pass
                    await message.answer(
                        texts.t(texts.AI_ERROR, lang),
                        reply_markup=ask_kb,
                    )
                    return

        safe = prepare_user_reply(answer)
        if not safe or looks_incomplete_reply(safe):
            logger.warning("Ask AI reply rejected (leak/incomplete); retry then fallback")
            retry = ""
            if budget.can_retry():
                retry = await _compact_retry()
            safe_retry = prepare_user_reply(retry) if retry else ""
            if safe_retry:
                answer = safe_retry
            else:
                fallback = _user_facing_fallback()
                if not fallback and not ask_product and match and match.record:
                    fallback = (
                        (match.record.full_answer or "").strip()
                        or (match.record.short_answer or "").strip()
                    )
                if wants_contact_links(text) or wants_sales_nudge(text, intent_name):
                    answer = download_or_site_fallback(lang)
                elif fallback:
                    answer = fallback
                elif media_paths:
                    answer = (
                        "تصویر کاتالوگ از فایل ذخیره‌شده ارسال می‌شود."
                        if (lang or "").startswith("fa")
                        else "Sending the stored catalog photo."
                    )
                else:
                    answer = texts.t(texts.AI_ERROR, lang)

        if looks_like_prompt_dump(answer) or not prepare_user_reply(answer):
            answer = _user_facing_fallback() or texts.t(texts.AI_ERROR, lang)
        else:
            answer = prepare_user_reply(answer) or answer

        usage = ai.last_usage
        await metrics.record_token_usage(
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            spend_usd=ai.estimate_spend_usd(usage),
        )

        final = append_sales_if_needed(
            answer,
            lang,
            user_text=text,
            intent_name=intent_name,
        )
        referred = False
        solved = True
        if looks_unsure(final):
            if has_implementation_exists(text, product_id="vps-to-vpn"):
                from src.knowledge.feature_lookup_adapter import feature_lookup as _fl

                hit = _fl(query=text, product_id="vps-to-vpn")
                notes = (hit.get("notes") or "").strip()
                if (lang or "").startswith("fa"):
                    final = (
                        "بر اساس کد محصول (Implementation)، این قابلیت وجود دارد (EXISTS).\n"
                        + notes[:1200]
                    )
                else:
                    final = (
                        "Per product Implementation, this capability EXISTS.\n"
                        + notes[:1200]
                    )
                referred = False
                solved = True
            else:
                handoff = unsure_handoff(lang)
                if SUPPORT_HANDLE.lower() not in final.lower():
                    final = f"{final.rstrip()}\n\n{handoff}"
                referred = True
                solved = False
        else:
            final = sanitize_reply_links(final, text)
            if SUPPORT_HANDLE.lower() in final.lower():
                referred = True

        if len(final) > 4000:
            final = final[:3990] + "…"
        if looks_like_prompt_dump(final) or not is_safe_to_persist(final):
            if looks_like_prompt_dump(final):
                final = texts.t(texts.AI_ERROR, lang)

        await users.append_chat(user.id, "user", text)
        if is_safe_to_persist(final) or final == texts.t(texts.AI_ERROR, lang):
            await users.append_chat(user.id, "assistant", final)
        else:
            safe_final = texts.t(texts.AI_ERROR, lang)
            await users.append_chat(user.id, "assistant", safe_final)
            final = safe_final
        await metrics.record_answered(referred_support=referred, ai_solved=solved)

        has_catalog = bool(retrieval.units) and not retrieval.insufficient
        has_md = bool((kb_snip or "").strip()) and (
            "product-guide:" in kb_snip or len(kb_snip) > 200
        )
        grounded = solved and not referred and (has_catalog or has_md)
        source = "catalog" if has_catalog else ("md" if has_md else "none")
        if has_catalog and has_md:
            source = "catalog+md"
        stages.mark("ai_and_safety")
        try:
            await wait.delete()
        except Exception:
            pass
        await message.answer(final, reply_markup=ask_kb)
        stages.mark("send_text")
        if ask_product and media_paths and getattr(retrieval, "attach_media", False):
            try:
                await messaging.answer_with_media(
                    message,
                    " ",
                    images=media_paths,
                    reply_markup=ask_kb,
                )
            except Exception:  # noqa: BLE001
                logger.exception("related media send failed")
            stages.mark("send_media")
        if ask_product:
            bundle.answer_text = final
            await users.set_last_ask_context(user.id, bundle.as_dict())
        if (
            ask_product
            and solved
            and not referred
            and final != texts.t(texts.AI_ERROR, lang)
            and not looks_like_prompt_dump(final)
        ):
            try:
                append_learned_answer(settings.knowledge_root, ask_product, text, final)
            except Exception:  # noqa: BLE001
                logger.exception("ai memory learned save failed")
        try:
            memory.remember(
                query=text,
                lang=lang,
                answer=final,
                unit_ids=[u.unit_id for u in retrieval.units],
                source=source,
                grounded=grounded,
            )
        except Exception:  # noqa: BLE001
            logger.exception("answer memory save failed")
        stages.flush()

    return router
