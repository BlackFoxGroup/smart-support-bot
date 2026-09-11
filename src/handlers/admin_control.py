"""Admin Control Center — Statistics → Change Agent & API (FA/EN)."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import re
import time
from pathlib import Path
from typing import Any

from aiogram import Bot, F, Router
from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from src.access import AdminAccess
from src.bot_stats_report import build_bot_stats_report
from src.config import Settings
from src.control.models import AgentRecord, _utcnow
from src.control.service import ControlService
from src.handlers.start import send_main_menu
from src.health_report import build_health_report
from src.news_post_report import build_news_post_report
from src.storage.bot_settings import BotSettingsStore
from src.storage.metrics import MetricsStore
from src.storage.users import UserStore
from src.ui import admin_keyboards as ak
from src.ui import keyboards, texts

logger = logging.getLogger(__name__)

router = Router(name="admin_control")

# Keep Chat-with-Agent snappy: kimi/reasoning models otherwise fill 4k tokens for ~30–60s.
_CHAT_HISTORY_TURNS = 4
_CHAT_MAX_TOKENS = 768
_CHAT_TIMEOUT_SEC = 28.0
_CHAT_BRIEF_HINT = (
    "Reply concisely. Prefer short practical answers (under ~180 words) unless the user asks for detail."
)

_ALLOWED_DOC_EXT = {
    ".pdf",
    ".txt",
    ".docx",
    ".doc",
    ".json",
    ".csv",
    ".zip",
    ".md",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
}
_MAX_FILE_BYTES = 15 * 1024 * 1024

_WIZARD_STEPS: dict[str, dict[str, str]] = {
    "name": {"fa": "نام Agent", "en": "Agent Name"},
    "provider": {
        "fa": "Provider (مثلاً openai-compatible / nube / openrouter)",
        "en": "Provider (e.g. openai-compatible / nube / openrouter)",
    },
    "model": {"fa": "نام Model", "en": "Model Name"},
    "api_endpoint": {
        "fa": "API Endpoint (آدرس پایه، مثل https://api.example.com/v1)",
        "en": "API Endpoint (base URL, e.g. https://api.example.com/v1)",
    },
    "api_key": {
        "fa": "API Key (یک‌بار وارد می‌شود؛ رمزنگاری می‌شود؛ کامل نمایش داده نمی‌شود)",
        "en": "API Key (sent once, stored encrypted, never shown fully)",
    },
    "system_prompt": {
        "fa": "System Prompt / Agent Prompt (یا Skip)",
        "en": "System Prompt / Agent Prompt (or Skip)",
    },
    "max_tokens": {"fa": "Max Tokens (عدد)", "en": "Max Tokens (number)"},
    "temperature": {"fa": "Temperature (مثلاً 0.4)", "en": "Temperature (e.g. 0.4)"},
    "role": {
        "fa": "نقش — دکمه Role را بزنید یا primary/secondary/backup/support بنویسید",
        "en": "Role — tap a Role button or type primary/secondary/backup/support",
    },
}


def _uid(message: Message) -> int:
    return message.from_user.id if message.from_user else 0


async def _lang(users: UserStore, message: Message) -> str:
    uid = _uid(message)
    code = await users.get_lang(
        uid, message.from_user.language_code if message.from_user else None
    )
    return ak.ui_lang(code)


async def _build_users_list_text(
    users: UserStore,
    *,
    lang: str,
    bot: Bot | None = None,
) -> list[str]:
    """Build one or more Telegram messages listing user names."""
    rows = await users.list_users()
    # Enrich missing names from Telegram when possible
    if bot is not None:
        for row in rows:
            if row.get("first_name") or row.get("username"):
                continue
            uid = int(row.get("user_id") or 0)
            if not uid:
                continue
            try:
                chat = await bot.get_chat(uid)
            except Exception:  # noqa: BLE001
                continue
            await users.touch_profile(
                uid,
                username=getattr(chat, "username", None),
                first_name=getattr(chat, "first_name", None)
                or getattr(chat, "full_name", None),
                last_name=getattr(chat, "last_name", None),
            )
        rows = await users.list_users()

    fa = lang.startswith("fa")
    header = (
        f"👥 لیست کاربران\n\nتعداد: {len(rows)}\n"
        if fa
        else f"👥 User List\n\nTotal: {len(rows)}\n"
    )
    if not rows:
        empty = "هنوز کاربری ثبت نشده است." if fa else "No users recorded yet."
        return [header + "\n" + empty]

    lines: list[str] = []
    for i, row in enumerate(rows, 1):
        name = str(row.get("display_name") or "").strip() or f"id:{row.get('user_id')}"
        uname = str(row.get("username") or "").strip()
        uid = row.get("user_id")
        ulang = str(row.get("lang") or "-")
        handle = f" @{uname}" if uname and not name.startswith("@") else ""
        lines.append(f"{i}. {name}{handle} — `{uid}` ({ulang})")

    chunks: list[str] = []
    buf_lines = [header.rstrip()]
    size = len(buf_lines[0])
    for line in lines:
        add = 1 + len(line)
        if size + add > 3500 and len(buf_lines) > 1:
            chunks.append("\n".join(buf_lines))
            cont = "👥 …" if fa else "👥 …"
            buf_lines = [cont, line]
            size = len(cont) + 1 + len(line)
        else:
            buf_lines.append(line)
            size += add
    if buf_lines:
        chunks.append("\n".join(buf_lines))
    return chunks or [header]


def _parse_pick_id(text: str) -> str | None:
    m = re.match(r"^(agt_[a-f0-9]+|api_[a-f0-9]+)\b", (text or "").strip())
    return m.group(1) if m else None


def _agent_labels(agents) -> list[str]:
    return [f"{a.id} — {a.name} [{a.role}]" for a in agents]


def _parse_role(text: str) -> str | None:
    action = ak.resolve_action(text)
    if action and action.startswith("role_"):
        return action.replace("role_", "")
    low = (text or "").strip().lower()
    for role in ("primary", "secondary", "backup", "support"):
        if low == role or low.endswith(role):
            return role
    return None


async def _show_control_home(
    message: Message, control: ControlService, lang: str
) -> None:
    agents = await control.registry.list_agents()
    active = await control.registry.get_active()
    body = control.format_control_home(agents, active, lang=lang)
    await message.answer(body[:3900], reply_markup=ak.control_home_keyboard(lang))


async def _stats_kb(lang: str, *, show_news_report: bool = False):
    generated: list = []
    try:
        from src.generated.buttons import list_generated_buttons

        generated = list_generated_buttons(menu="stats", refresh=True)
    except Exception:  # noqa: BLE001
        generated = []
    return ak.stats_hub_keyboard(
        lang,
        generated_buttons=generated,
        show_news_report=show_news_report,
    )


async def _show_stats_hub(message: Message, lang: str, *, show_news_report: bool = False) -> None:
    await message.answer(
        ak.msg("stats_hub", lang),
        reply_markup=await _stats_kb(lang, show_news_report=show_news_report),
    )


async def _show_settings_hub(
    message: Message, lang: str, bot_settings: BotSettingsStore | None = None
) -> None:
    customs: list = []
    generated: list = []
    if bot_settings is not None:
        customs = await bot_settings.list_custom_buttons(menu="settings")
        try:
            from src.generated.buttons import list_generated_buttons

            generated = list_generated_buttons(menu="settings", refresh=True)
        except Exception:  # noqa: BLE001
            generated = []
        ak.refresh_custom_button_labels(list(customs) + list(generated))
    await message.answer(
        ak.msg("settings_hub", lang),
        reply_markup=ak.settings_hub_keyboard(
            lang, custom_buttons=customs, generated_buttons=generated
        ),
    )


def setup_admin_control_router(
    users: UserStore,
    *,
    settings: Settings,
    metrics: MetricsStore,
    control: ControlService,
    bot_settings: BotSettingsStore | None = None,
    access: AdminAccess | None = None,
) -> Router:
    if access is None and bot_settings is not None:
        access = AdminAccess(settings, bot_settings)

    async def _require_stats(message: Message) -> tuple[bool, str]:
        uid = _uid(message)
        lang = await _lang(users, message)
        ok = False
        if access is not None:
            ok = await access.can_stats(uid)
        else:
            from src.config import is_bot_admin

            ok = bool(uid and is_bot_admin(settings, uid))
        if not ok:
            await message.answer(ak.msg("admin_only", lang))
            return False, lang
        return True, lang

    async def _require_settings(message: Message) -> tuple[bool, str]:
        uid = _uid(message)
        lang = await _lang(users, message)
        ok = False
        if access is not None:
            ok = await access.can_settings(uid)
        else:
            from src.config import is_bot_admin

            ok = bool(uid and is_bot_admin(settings, uid))
        if not ok:
            if access is not None and await access.can_stats(uid):
                await message.answer(ak.msg("settings_denied", lang))
            else:
                await message.answer(ak.msg("admin_only", lang))
            return False, lang
        return True, lang

    async def _stats_show_news(uid: int) -> bool:
        if access is not None:
            return await access.can_news_report(uid)
        from src.config import is_bot_admin

        return bool(uid and is_bot_admin(settings, uid))

    @router.message(F.text.in_(set(texts.MENU_BOT_STATS.values())))
    async def on_bot_stats_entry(message: Message) -> None:
        ok, lang = await _require_stats(message)
        if not ok:
            return
        uid = _uid(message)
        await users.set_ask_ai(uid, False)
        await control.registry.clear_session(uid)
        report = await build_bot_stats_report(settings, metrics)
        show_news = await _stats_show_news(uid)
        await message.answer(
            report[:3900],
            reply_markup=await _stats_kb(lang, show_news_report=show_news),
        )

    @router.message(F.text.in_(ak.texts("news_report")))
    async def on_news_report_from_stats(message: Message) -> None:
        ok, lang = await _require_stats(message)
        if not ok:
            return
        uid = _uid(message)
        if not await _stats_show_news(uid):
            await message.answer(ak.msg("news_report_denied", lang))
            return
        report = await build_news_post_report(
            settings, bot_settings, lang=lang, days=3
        )
        await message.answer(
            report[:3900],
            reply_markup=await _stats_kb(lang, show_news_report=True),
        )

    @router.message(F.text.in_(ak.texts("users_list")))
    async def on_users_list_from_stats(message: Message) -> None:
        ok, lang = await _require_stats(message)
        if not ok:
            return
        uid = _uid(message)
        show_news = await _stats_show_news(uid)
        parts = await _build_users_list_text(users, lang=lang, bot=message.bot)
        kb = await _stats_kb(lang, show_news_report=show_news)
        for i, part in enumerate(parts):
            await message.answer(part[:3900], reply_markup=kb if i == len(parts) - 1 else None)

    @router.message(F.text.in_(ak.texts("health_status")))
    async def on_health_from_stats(message: Message) -> None:
        ok, lang = await _require_stats(message)
        if not ok:
            return
        if bot_settings is None:
            return
        # If settings session is active, let admin_settings handle it
        sess = await bot_settings.get_session(_uid(message))
        if sess.get("mode") in {"health", "backup", "admins", "owner", "panel", "messages_hub", "target", "slot"}:
            raise SkipHandler()
        # Health status lives under Settings now; stats hub uses news Report instead.
        show_news = await _stats_show_news(_uid(message))
        report = await build_health_report(settings, bot_settings, lang=lang)
        await message.answer(
            report[:3900],
            reply_markup=await _stats_kb(lang, show_news_report=show_news),
        )

    @router.message(F.text.in_(ak.all_admin_control_texts()))
    async def on_admin_button(message: Message) -> None:
        action = ak.resolve_action(message.text)
        # Generated buttons (esp. stats menu) — run before settings-only early return.
        if not action:
            try:
                from src.generated.buttons import dispatch_generated, find_generated_by_label

                gen = find_generated_by_label(message.text or "")
            except Exception:  # noqa: BLE001
                gen = None
            if gen:
                menu = str(gen.get("menu") or "settings")
                if menu == "stats":
                    ok, lang = await _require_stats(message)
                    if not ok:
                        return
                    ran = await dispatch_generated(
                        message,
                        gen,
                        lang=lang,
                        settings=settings,
                        bot_settings=bot_settings,
                    )
                    if not ran:
                        await message.answer(
                            "اجرای کلید تولیدشده ناموفق بود."
                            if lang.startswith("fa")
                            else "Generated button failed to run."
                        )
                    return
                # settings/health generated buttons stay in admin_settings
                raise SkipHandler()
        # Settings-only actions are handled elsewhere
        if action in {
            "settings_hub",
            "settings_messages",
            "settings_panel",
            "owner_info",
            "creator_contact",
            "bot_config_chat",
            "build_catalogs",
            "backup_settings",
            "backup_export",
            "backup_import",
            "health_toggle",
            "health_times",
            "health_chat",
            "manage_admins",
            "admin_role_full",
            "admin_role_stats",
            "admin_remove",
            "owner_bot_name",
            "owner_site",
            "owner_channel",
            "owner_group",
            "owner_support",
            "msg_channel",
            "msg_group",
            "msg_support",
            "msg_test",
            "msg_account",
            "catalog_src_site",
            "catalog_src_channel",
            "catalog_src_group",
            "catalog_run",
            "slot_1",
            "slot_2",
            "slot_3",
            "edit_dest",
            "edit_template",
            "edit_schedule",
            "edit_rules",
        }:
            raise SkipHandler()
        if action == "health_status":
            # Prefer stats keyboard path above; ignore duplicate here when settings owns it
            if bot_settings is not None:
                sess = await bot_settings.get_session(_uid(message))
                if sess.get("mode") == "health":
                    raise SkipHandler()
            ok, lang = await _require_stats(message)
            if not ok or bot_settings is None:
                return
            show_news = await _stats_show_news(_uid(message))
            report = await build_health_report(settings, bot_settings, lang=lang)
            await message.answer(
                report[:3900],
                reply_markup=await _stats_kb(lang, show_news_report=show_news),
            )
            return

        if action == "news_report":
            ok, lang = await _require_stats(message)
            if not ok:
                return
            uid = _uid(message)
            if not await _stats_show_news(uid):
                await message.answer(ak.msg("news_report_denied", lang))
                return
            report = await build_news_post_report(
                settings, bot_settings, lang=lang, days=3
            )
            await message.answer(
                report[:3900],
                reply_markup=await _stats_kb(lang, show_news_report=True),
            )
            return

        if action == "stats_report":
            ok, lang = await _require_stats(message)
            if not ok:
                return
            uid = _uid(message)
            show_news = await _stats_show_news(uid)
            report = await build_bot_stats_report(settings, metrics)
            await message.answer(
                report[:3900],
                reply_markup=await _stats_kb(lang, show_news_report=show_news),
            )
            return

        if action == "users_list":
            ok, lang = await _require_stats(message)
            if not ok:
                return
            uid = _uid(message)
            show_news = await _stats_show_news(uid)
            parts = await _build_users_list_text(users, lang=lang, bot=message.bot)
            kb = await _stats_kb(lang, show_news_report=show_news)
            for i, part in enumerate(parts):
                await message.answer(
                    part[:3900], reply_markup=kb if i == len(parts) - 1 else None
                )
            return

        # Agent control requires full settings role
        ok, lang = await _require_settings(message)
        if not ok:
            return
        uid = _uid(message)
        if not action:
            return

        # Handled primarily by admin_settings router; ignore here if pure settings nav
        if action in {
            "settings_hub",
            "settings_messages",
            "settings_panel",
            "owner_info",
            "creator_contact",
            "bot_config_chat",
            "build_catalogs",
            "owner_bot_name",
            "owner_site",
            "owner_channel",
            "owner_group",
            "owner_support",
            "msg_channel",
            "msg_group",
            "msg_support",
            "msg_test",
            "msg_account",
            "catalog_src_site",
            "catalog_src_channel",
            "catalog_src_group",
            "catalog_run",
            "slot_1",
            "slot_2",
            "slot_3",
            "edit_dest",
            "edit_template",
            "edit_schedule",
            "edit_rules",
            "edit_slot_kind",
            "edit_panel_url",
            "edit_panel_token",
            "edit_panel_inbound",
        }:
            raise SkipHandler()

        if action == "change_agent_api":
            await users.set_ask_ai(uid, False)
            await control.registry.set_session(uid, {"mode": "control_home"})
            await _show_control_home(message, control, lang)
            return

        if action == "settings_back":
            await control.registry.clear_session(uid)
            await _show_settings_hub(message, lang, bot_settings)
            return

        if action == "nav_back":
            sess = await control.registry.get_session(uid)
            mode = str(sess.get("mode") or "")
            if mode == "add_agent":
                await _wizard_step_back_agent(message, control, uid, lang, sess)
                return
            if mode == "add_api":
                await _wizard_step_back_api(message, control, uid, lang, sess)
                return
            if mode in {"pick_active", "pick_test", "pick_config", "pick_chat", "pick_api"}:
                await control.registry.set_session(uid, {"mode": "control_home"})
                await _show_control_home(message, control, lang)
                return
            if mode in {"config_agent", "chat_agent"}:
                await control.registry.set_session(uid, {"mode": "control_home"})
                await _show_control_home(message, control, lang)
                return
            await control.registry.set_session(uid, {"mode": "control_home"})
            await _show_control_home(message, control, lang)
            return

        if action == "stats_back":
            await control.registry.clear_session(uid)
            full_lang = await users.get_lang(
                uid, message.from_user.language_code if message.from_user else None
            )
            await send_main_menu(
                message, full_lang, users=users, user_id=uid, settings=settings
            )
            return

        if action in {"control_home", "cancel"}:
            await control.registry.clear_session(uid)
            await control.registry.set_session(uid, {"mode": "control_home"})
            await _show_control_home(message, control, lang)
            return

        if action == "list_agents":
            agents = await control.registry.list_agents()
            if not agents:
                await message.answer(
                    ak.msg("no_agents", lang), reply_markup=ak.control_home_keyboard(lang)
                )
                return
            chunks = []
            for a in agents:
                chunks.append(control.format_agent_card(a, lang=lang))
                chunks.append("—" * 24)
            await message.answer(
                "\n".join(chunks)[:3900], reply_markup=ak.control_home_keyboard(lang)
            )
            return

        if action == "add_agent":
            await control.registry.set_session(
                uid, {"mode": "add_agent", "step": "name", "draft": {}}
            )
            await message.answer(
                ak.msg("add_agent_start", lang), reply_markup=ak.cancel_keyboard(lang)
            )
            return

        if action == "support_agent":
            await control.registry.set_session(
                uid,
                {"mode": "add_agent", "step": "name", "draft": {"role": "support"}},
            )
            await message.answer(
                ak.msg("support_agent_start", lang),
                reply_markup=ak.cancel_keyboard(lang),
            )
            return

        if action == "set_active":
            agents = await control.registry.list_agents()
            await control.registry.set_session(uid, {"mode": "set_active"})
            await message.answer(
                ak.msg("pick_set_active", lang),
                reply_markup=ak.agent_pick_keyboard(_agent_labels(agents), lang),
            )
            return

        if action == "test_agent":
            agents = await control.registry.list_agents()
            await control.registry.set_session(uid, {"mode": "test_agent"})
            await message.answer(
                ak.msg("pick_test", lang),
                reply_markup=ak.agent_pick_keyboard(_agent_labels(agents), lang),
            )
            return

        if action == "config_agent":
            agents = await control.registry.list_agents()
            await control.registry.set_session(uid, {"mode": "config_pick"})
            await message.answer(
                ak.msg("pick_config", lang),
                reply_markup=ak.agent_pick_keyboard(_agent_labels(agents), lang),
            )
            return

        if action == "failover":
            chain = await control.failover_chain()
            active = await control.registry.get_active()
            preferred = await control.registry.get_preferred_primary()
            if lang == "fa":
                lines = [
                    "🔁 وضعیت جایگزینی خودکار",
                    f"ایجنت فعال: {active.name if active else '-'}",
                    f"ایجنت اصلی ترجیحی: {preferred.name if preferred else '-'}",
                    "",
                    "زنجیره به‌ترتیب اولویت:",
                ]
            else:
                lines = [
                    "🔁 Failover Status",
                    f"Active: {active.name if active else '-'}",
                    f"Preferred Primary: {preferred.name if preferred else '-'}",
                    "",
                    "Chain (priority order):",
                ]
            for a in chain:
                mark = "← ACTIVE" if active and a.id == active.id else ""
                lines.append(
                    f"- [{a.role}] prio={a.priority} {a.name} ({a.status}) {mark}"
                )
            lines.append("")
            lines.append(
                "جایگزینی خودکار را لایه کنترل انجام می‌دهد، نه خودِ ایجنت."
                if lang == "fa"
                else "Automatic failover is handled by Control Layer, not by Agents."
            )
            await message.answer(
                "\n".join(lines), reply_markup=ak.control_home_keyboard(lang)
            )
            return

        if action == "return_primary":
            await message.answer(ak.msg("activating_now", lang))
            _ok, body = await control.return_to_primary(admin_id=uid, lang=lang)
            await message.answer(body, reply_markup=ak.control_home_keyboard(lang))
            return

        if action == "token_monitor":
            agents = await control.registry.list_agents()
            title = "💎 پایش اعتبار و توکن" if lang == "fa" else "💎 Token / Credit Monitoring"
            lines = [title, ""]
            for a in agents:
                lines.append(f"• {a.name}")
                lines.append(
                    f"  {'مصرف کل' if lang == 'fa' else 'Total Usage'}: "
                    f"{a.total_tokens} tokens / ${a.spend_usd:.4f}"
                )
                if a.budget_usd > 0:
                    rem = max(0.0, a.budget_usd - a.spend_usd)
                    pct = (a.spend_usd / a.budget_usd) * 100.0
                    lines.append(
                        f"  {'باقی‌مانده' if lang == 'fa' else 'Remaining'}: ${rem:.4f}"
                    )
                    lines.append(
                        f"  {'درصد مصرف' if lang == 'fa' else 'Usage Percentage'}: {pct:.1f}%"
                    )
                    warn = control.usage_warning(a, lang=lang)
                    if warn:
                        lines.append(f"  {warn}")
                else:
                    lines.append(
                        f"  {'بودجه تنظیم نشده' if lang == 'fa' else 'Budget: not set'}"
                    )
                lines.append("")
            await message.answer(
                "\n".join(lines)[:3900], reply_markup=ak.control_home_keyboard(lang)
            )
            return

        if action == "audit_log":
            rows = await control.audit.tail(25)
            await message.answer(
                control.audit.format_tail(rows)[:3900],
                reply_markup=ak.control_home_keyboard(lang),
            )
            return

        if action == "api_mgmt":
            await message.answer(
                ak.msg("api_mgmt_intro", lang), reply_markup=ak.api_mgmt_keyboard(lang)
            )
            return

        if action == "api_list":
            await _api_list(message, control, lang)
            return

        if action == "api_add":
            await control.registry.set_session(
                uid, {"mode": "add_api", "step": "name", "draft": {}}
            )
            await message.answer(
                ak.msg("api_add_name", lang), reply_markup=ak.cancel_keyboard(lang)
            )
            return

        if action == "api_delete":
            apis = await control.registry.list_apis()
            labels = [f"{a.id} — {a.provider_name}" for a in apis]
            await control.registry.set_session(uid, {"mode": "delete_api"})
            await message.answer(
                ak.msg("pick_api_delete", lang),
                reply_markup=ak.agent_pick_keyboard(labels, lang),
            )
            return

        if action == "api_test":
            apis = await control.registry.list_apis()
            labels = [f"{a.id} — {a.provider_name}" for a in apis]
            await control.registry.set_session(uid, {"mode": "test_api"})
            await message.answer(
                ak.msg("pick_api_test", lang),
                reply_markup=ak.agent_pick_keyboard(labels, lang),
            )
            return

        if action == "chat_agent":
            agents = await control.registry.list_agents()
            await control.registry.set_session(uid, {"mode": "chat_pick"})
            await message.answer(
                ak.msg("pick_chat", lang),
                reply_markup=ak.agent_pick_keyboard(_agent_labels(agents), lang),
            )
            return

        if action == "clear_chat":
            sess = await control.registry.get_session(uid)
            if sess.get("mode") != "chat_agent":
                await message.answer(ak.msg("not_in_chat", lang))
                return
            sess["history"] = []
            await control.registry.set_session(uid, sess)
            await message.answer(
                ak.msg("chat_cleared", lang),
                reply_markup=ak.chat_with_agent_keyboard(lang),
            )
            return

        if action == "end_chat":
            await control.registry.set_session(uid, {"mode": "control_home"})
            await _show_control_home(message, control, lang)
            return

        if action == "upload_hint":
            extra = (
                f"\nمجاز: {', '.join(sorted(_ALLOWED_DOC_EXT))}\n"
                f"حداکثر: {_MAX_FILE_BYTES // (1024 * 1024)} MB"
                if lang == "fa"
                else f"\nAllowed: {', '.join(sorted(_ALLOWED_DOC_EXT))}\n"
                f"Max: {_MAX_FILE_BYTES // (1024 * 1024)} MB"
            )
            await message.answer(
                ak.msg("upload_help", lang) + extra,
                reply_markup=ak.chat_with_agent_keyboard(lang),
            )
            return

        # Role / skip buttons are consumed by wizards via on_admin_text
        if action in {
            "skip",
            "role_primary",
            "role_secondary",
            "role_backup",
            "role_support",
        }:
            sess = await control.registry.get_session(uid)
            if sess.get("mode") in {"add_agent", "add_api"}:
                await _dispatch_wizard_text(
                    message, users, control, uid, lang, sess, message.text or ""
                )
            return

    @router.message(
        F.chat.type == "private",
        F.text,
        ~F.text.startswith("/"),
        ~F.text.in_(ak.all_admin_control_texts()),
        ~F.text.in_(keyboards.all_menu_button_texts()),
        ~F.text.in_(keyboards.all_lang_button_texts()),
    )
    async def on_admin_text(message: Message) -> None:
        uid = _uid(message)
        if access is None or not await access.can_settings(uid):
            raise SkipHandler()
        # Ask AI must reach the public chat router — never swallow free text there.
        if await users.is_ask_ai(uid):
            raise SkipHandler()
        lang = await _lang(users, message)
        sess = await control.registry.get_session(uid)
        mode = sess.get("mode")
        if not mode or mode in {"control_home"}:
            raise SkipHandler()
        await _dispatch_wizard_text(
            message, users, control, uid, lang, sess, (message.text or "").strip()
        )

    async def _dispatch_wizard_text(
        message: Message,
        users: UserStore,
        control: ControlService,
        uid: int,
        lang: str,
        sess: dict[str, Any],
        text: str,
    ) -> None:
        mode = sess.get("mode")
        pick = _parse_pick_id(text)

        if mode == "set_active" and pick:
            await message.answer(ak.msg("activating_now", lang))
            _ok, body = await control.activate_agent(
                pick, admin_id=uid, require_test=True, lang=lang
            )
            await control.registry.set_session(uid, {"mode": "control_home"})
            await message.answer(body, reply_markup=ak.control_home_keyboard(lang))
            return

        if mode == "test_agent" and pick:
            await message.answer(ak.msg("testing_now", lang))
            _ok, body = await control.test_agent(pick, admin_id=uid, lang=lang)
            await control.registry.set_session(uid, {"mode": "control_home"})
            await message.answer(body, reply_markup=ak.control_home_keyboard(lang))
            return

        if mode == "config_pick" and pick:
            await control.registry.set_session(
                uid, {"mode": "config_agent", "agent_id": pick, "step": "field"}
            )
            body = (
                "⚙️ تنظیمات ایجنت\nیک خط بفرستید:\nfield=value\n\n"
                "فیلدها: name, provider, model, api_endpoint, api_key, system_prompt, "
                "temperature, max_tokens, timeout_seconds, retry_count, priority, role, "
                "enabled, budget_usd\n\nمثال:\nmodel=gpt-4o-mini\n\n"
                "برای حذف ایجنت بنویسید: Delete"
                if lang == "fa"
                else "⚙️ Agent Configuration\nSend one line:\nfield=value\n\n"
                "Fields: name, provider, model, api_endpoint, api_key, system_prompt, "
                "temperature, max_tokens, timeout_seconds, retry_count, priority, role, "
                "enabled, budget_usd\n\nExample:\nmodel=gpt-4o-mini\n\n"
                "Or send Delete to remove this agent."
            )
            await message.answer(body, reply_markup=ak.cancel_keyboard(lang))
            return

        if mode == "config_agent":
            await _config_agent(message, control, uid, lang, sess, text)
            return

        if mode == "delete_api" and pick:
            deleted = await control.registry.delete_api(pick)
            await control.audit.write(
                "delete_api",
                admin_id=uid,
                detail=f"Deleted API {pick}",
                meta={"api_id": pick},
            )
            await control.registry.set_session(uid, {"mode": "control_home"})
            await message.answer(
                ("✅ API حذف شد" if deleted else "❌ پیدا نشد")
                if lang == "fa"
                else ("✅ API deleted" if deleted else "❌ Not found"),
                reply_markup=ak.control_home_keyboard(lang),
            )
            return

        if mode == "test_api" and pick:
            await _test_api(message, control, settings, uid, lang, pick)
            return

        if mode == "chat_pick" and pick:
            agent = await control.registry.get_agent(pick)
            if not agent:
                await message.answer(
                    "❌ ایجنت پیدا نشد." if lang == "fa" else "❌ Agent not found"
                )
                return
            await control.registry.set_session(
                uid, {"mode": "chat_agent", "agent_id": pick, "history": []}
            )
            body = (
                f"💬 گفتگو با ایجنت\n"
                f"ایجنت انتخاب‌شده: {agent.name}\n"
                "پیام‌ها در همین چت نمایش داده می‌شوند.\n"
                "متن بفرستید یا فایل/تصویر/سند آپلود کنید."
                if lang == "fa"
                else f"💬 Chat with Agent: {agent.name}\n"
                "Message list is this Telegram thread.\n"
                "Type a message, or upload a file/image/document."
            )
            await message.answer(body, reply_markup=ak.chat_with_agent_keyboard(lang))
            return

        if mode == "chat_agent":
            await _chat_send(message, control, uid, lang, sess, user_text=text)
            return

        if mode == "add_agent":
            await _add_agent_wizard(message, control, uid, lang, sess, text)
            return

        if mode == "add_api":
            await _add_api_wizard(message, control, uid, lang, sess, text)
            return

        # Unknown / idle wizard mode — let Ask AI and other routers handle the text.
        raise SkipHandler()

    @router.message(F.chat.type == "private", F.document | F.photo)
    async def on_admin_file(message: Message, bot: Bot) -> None:
        uid = _uid(message)
        if access is None or not await access.can_settings(uid):
            raise SkipHandler()
        lang = await _lang(users, message)
        sess = await control.registry.get_session(uid)
        if sess.get("mode") != "chat_agent":
            raise SkipHandler()

        file_id = None
        filename = "file"
        mime = "application/octet-stream"
        size = 0
        if message.document:
            file_id = message.document.file_id
            filename = message.document.file_name or "document"
            mime = message.document.mime_type or mime
            size = int(message.document.file_size or 0)
        elif message.photo:
            photo = message.photo[-1]
            file_id = photo.file_id
            filename = "photo.jpg"
            mime = "image/jpeg"
            size = int(photo.file_size or 0)

        if not file_id:
            return
        if size and size > _MAX_FILE_BYTES:
            await message.answer(
                "❌ فایل خیلی بزرگ است." if lang == "fa" else "❌ File too large."
            )
            return
        ext = Path(filename).suffix.lower()
        if ext and ext not in _ALLOWED_DOC_EXT and not message.photo:
            await message.answer(
                f"❌ پسوند مجاز نیست: {ext}"
                if lang == "fa"
                else f"❌ Extension not allowed: {ext}"
            )
            return

        await message.answer(
            (
                f"📎 پیش‌نمایش پیوست\nنام: {filename}\nنوع: {mime}\nحجم: {size} bytes\n\n"
                "در حال ارسال به Agent…"
            )
            if lang == "fa"
            else (
                f"📎 Attachment preview\nName: {filename}\nType: {mime}\n"
                f"Size: {size} bytes\n\nDownloading and sending to Agent…"
            )
        )
        try:
            tg_file = await bot.get_file(file_id)
            buf = await bot.download_file(tg_file.file_path)
            raw = buf.read() if buf else b""
        except Exception as exc:  # noqa: BLE001
            await message.answer(f"❌ Download failed: {type(exc).__name__}")
            return

        caption = message.caption or ""
        snippet = ""
        if ext in {".txt", ".md", ".json", ".csv"} or mime.startswith("text/"):
            try:
                snippet = raw.decode("utf-8", errors="replace")[:8000]
            except Exception:  # noqa: BLE001
                snippet = ""
        user_blob = (
            f"[Uploaded file]\nName: {filename}\nType: {mime}\nSize: {size} bytes\n"
            f"Caption: {caption}\n"
        )
        if snippet:
            user_blob += f"\n--- file content ---\n{snippet}\n--- end ---"
        else:
            user_blob += "\n(Binary/image content not inlined as text.)"
        await _chat_send(message, control, uid, lang, sess, user_text=user_blob)

    # ----- Slash commands -----
    @router.message(Command("agents"))
    async def cmd_agents(message: Message) -> None:
        ok, _lang_code = await _require_settings(message)
        if not ok:
            return
        agents = await control.registry.list_agents()
        lines = ["/agents"] + [
            f"- {a.id} | {a.name} | {a.role} | active={a.active}" for a in agents
        ]
        await message.answer("\n".join(lines) or "No agents")

    @router.message(Command("agent_status"))
    async def cmd_agent_status(message: Message) -> None:
        ok, lang = await _require_settings(message)
        if not ok:
            return
        agents = await control.registry.list_agents()
        body = "\n\n".join(control.format_agent_card(a, lang=lang) for a in agents) or "No agents"
        await message.answer(body[:3900])

    @router.message(Command("active_agent"))
    async def cmd_active(message: Message) -> None:
        ok, lang = await _require_settings(message)
        if not ok:
            return
        active = await control.registry.get_active()
        if not active:
            await message.answer("No active agent")
            return
        await message.answer(control.format_agent_card(active, lang=lang))

    @router.message(Command("change_agent"))
    async def cmd_change(message: Message, command: CommandObject) -> None:
        ok, lang = await _require_settings(message)
        if not ok:
            return
        arg = (command.args or "").strip()
        if not arg:
            await message.answer("Usage: /change_agent <agent_id>")
            return
        await message.answer(ak.msg("activating_now", lang))
        _ok, body = await control.activate_agent(
            arg, admin_id=_uid(message), require_test=True, lang=lang
        )
        await message.answer(body)

    @router.message(Command("add_agent"))
    async def cmd_add(message: Message) -> None:
        ok, lang = await _require_settings(message)
        if not ok:
            return
        uid = _uid(message)
        await control.registry.set_session(
            uid, {"mode": "add_agent", "step": "name", "draft": {}}
        )
        await message.answer(
            ak.msg("add_agent_start", lang), reply_markup=ak.cancel_keyboard(lang)
        )

    @router.message(Command("test_agent"))
    async def cmd_test(message: Message, command: CommandObject) -> None:
        ok, lang = await _require_settings(message)
        if not ok:
            return
        arg = (command.args or "").strip()
        if not arg:
            await message.answer("Usage: /test_agent <agent_id>")
            return
        await message.answer(ak.msg("testing_now", lang))
        _ok, body = await control.test_agent(arg, admin_id=_uid(message), lang=lang)
        await message.answer(body)

    @router.message(Command("api_status"))
    async def cmd_api_status(message: Message) -> None:
        ok, lang = await _require_settings(message)
        if not ok:
            return
        await _api_list(message, control, lang)

    @router.message(Command("failover"))
    async def cmd_failover(message: Message) -> None:
        ok, lang = await _require_settings(message)
        if not ok:
            return
        # Reuse button path
        message.text = ak.label("failover", lang)
        await on_admin_button(message)

    return router


async def _api_list(message: Message, control: ControlService, lang: str) -> None:
    apis = await control.registry.list_apis()
    if not apis:
        await message.answer(ak.msg("no_apis", lang), reply_markup=ak.api_mgmt_keyboard(lang))
        return
    lines = [("🔌 ارائه‌دهندگان API:" if lang == "fa" else "🔌 API Providers:"), ""]
    for api in apis:
        from src.control.secrets import mask_api_key

        masked = mask_api_key(control.registry.decrypt_api_key(api))
        lines.extend(
            [
                f"• {api.provider_name} ({api.id})",
                f"  Endpoint: {api.api_endpoint}",
                f"  Model: {api.model or '-'}",
                f"  Key: {masked}",
                f"  Status: {api.status} | Priority: {api.priority}",
                f"  Usage: {api.usage_tokens} | Errors: {api.error_count}",
                f"  Last OK: {api.last_successful_request or '-'}",
                f"  Enabled: {api.enabled}",
                "",
            ]
        )
    await message.answer("\n".join(lines)[:3900], reply_markup=ak.api_mgmt_keyboard(lang))


async def _config_agent(
    message: Message,
    control: ControlService,
    uid: int,
    lang: str,
    sess: dict[str, Any],
    text: str,
) -> None:
    agent_id = str(sess.get("agent_id") or "")
    if text.lower() == "delete":
        active = await control.registry.get_active()
        if active and active.id == agent_id:
            await message.answer(
                "❌ نمی‌توان Agent فعال را حذف کرد. ابتدا Agent دیگری را Active کنید."
                if lang == "fa"
                else "❌ Cannot delete the active agent. Activate another first.",
                reply_markup=ak.cancel_keyboard(lang),
            )
            return
        deleted = await control.registry.delete_agent(agent_id)
        await control.audit.write(
            "delete_agent",
            admin_id=uid,
            detail=f"Deleted agent {agent_id}",
            meta={"agent_id": agent_id},
        )
        await control.registry.set_session(uid, {"mode": "control_home"})
        await message.answer(
            ("✅ حذف شد" if deleted else "❌ پیدا نشد")
            if lang == "fa"
            else ("✅ Deleted" if deleted else "❌ Not found"),
            reply_markup=ak.control_home_keyboard(lang),
        )
        return
    if "=" not in text:
        await message.answer(
            "فرمت: field=value" if lang == "fa" else "Use field=value format.",
            reply_markup=ak.cancel_keyboard(lang),
        )
        return
    field, value = text.split("=", 1)
    field = field.strip().lower()
    value = value.strip()
    fields: dict[str, Any] = {}
    if field == "api_key":
        fields["api_key"] = value
    elif field in {"temperature", "timeout_seconds", "budget_usd"}:
        fields[field] = float(value)
    elif field in {"max_tokens", "retry_count", "priority"}:
        fields[field] = int(value)
    elif field == "enabled":
        fields["enabled"] = value.lower() in {"1", "true", "yes", "on"}
    elif field in {"name", "provider", "model", "api_endpoint", "system_prompt", "role"}:
        fields[field] = value
    else:
        await message.answer(
            f"فیلد ناشناخته: {field}" if lang == "fa" else f"Unknown field: {field}",
            reply_markup=ak.cancel_keyboard(lang),
        )
        return
    updated = await control.registry.update_agent(agent_id, **fields)
    await control.audit.write(
        "update_agent",
        admin_id=uid,
        detail=f"Updated {field} on {agent_id}",
        meta={"agent_id": agent_id, "field": field},
    )
    await control.registry.set_session(uid, {"mode": "control_home"})
    if updated:
        await message.answer(
            f"✅ {field} به‌روز شد\n\n{control.format_agent_card(updated, lang=lang)}"
            if lang == "fa"
            else f"✅ Updated {field}\n\n{control.format_agent_card(updated, lang=lang)}",
            reply_markup=ak.control_home_keyboard(lang),
        )
    else:
        await message.answer(
            "❌ به‌روزرسانی ناموفق" if lang == "fa" else "❌ Update failed",
            reply_markup=ak.control_home_keyboard(lang),
        )


async def _test_api(
    message: Message,
    control: ControlService,
    settings: Settings,
    uid: int,
    lang: str,
    pick: str,
) -> None:
    api = await control.registry.get_api(pick)
    if not api:
        await message.answer(
            "❌ API پیدا نشد" if lang == "fa" else "❌ API not found",
            reply_markup=ak.api_mgmt_keyboard(lang),
        )
        return
    ephemeral = AgentRecord(
        id=api.id,
        name=api.provider_name,
        provider=api.provider_name,
        model=api.model or settings.ai_model,
        api_endpoint=api.api_endpoint,
        api_key_enc=api.api_key_enc,
        max_tokens=256,
        temperature=0,
        timeout_seconds=30,
        role="secondary",
        enabled=True,
    )
    try:
        text_out, tokens = await control._raw_chat(  # noqa: SLF001
            ephemeral,
            [{"role": "user", "content": "Reply with exactly: PONG"}],
            max_tokens=32,
            temperature=0,
        )
        await control.registry.update_api(
            api.id, status="healthy", last_successful_request=_utcnow()
        )
        await message.answer(
            f"✅ اتصال موفق\nپاسخ: {text_out[:120]}\nTokens: {tokens}"
            if lang == "fa"
            else f"✅ Connection successful\nReply: {text_out[:120]}\nTokens: {tokens}",
            reply_markup=ak.api_mgmt_keyboard(lang),
        )
    except Exception as exc:  # noqa: BLE001
        safe = re.sub(r"sk-[A-Za-z0-9_-]+", "sk-••••", str(exc))[:200]
        await control.registry.update_api(api.id, status="down")
        await message.answer(
            f"❌ اتصال ناموفق\n{safe}" if lang == "fa" else f"❌ Connection failed\n{safe}",
            reply_markup=ak.api_mgmt_keyboard(lang),
        )
    await control.registry.set_session(uid, {"mode": "control_home"})


async def _keep_typing(bot: Bot, chat_id: int, stop: asyncio.Event) -> None:
    while not stop.is_set():
        try:
            await bot.send_chat_action(chat_id, action="typing")
        except Exception:  # noqa: BLE001
            pass
        try:
            await asyncio.wait_for(stop.wait(), timeout=4.0)
        except asyncio.TimeoutError:
            continue


async def _chat_send(
    message: Message,
    control: ControlService,
    uid: int,
    lang: str,
    sess: dict[str, Any],
    *,
    user_text: str,
) -> None:
    agent_id = str(sess.get("agent_id") or "")
    history: list[dict[str, str]] = list(sess.get("history") or [])
    agent = await control.registry.get_agent(agent_id)
    if not agent:
        await message.answer(
            "❌ ایجنت موجود نیست." if lang == "fa" else "❌ Agent missing",
            reply_markup=ak.control_home_keyboard(lang),
        )
        return

    wait_msg = await message.answer(ak.msg("chatting_now", lang))
    stop_typing = asyncio.Event()
    typing_task = asyncio.create_task(
        _keep_typing(message.bot, message.chat.id, stop_typing),
        name="admin-chat-typing",
    )

    messages: list[dict[str, Any]] = []
    if agent.system_prompt:
        sp = agent.system_prompt.strip()
        if len(sp) > 2500:
            sp = sp[:2500]
        messages.append({"role": "system", "content": sp})
    else:
        messages.append({"role": "system", "content": _CHAT_BRIEF_HINT})
    for turn in history[-_CHAT_HISTORY_TURNS:]:
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": user_text})

    token_cap = min(_CHAT_MAX_TOKENS, max(256, int(agent.max_tokens or _CHAT_MAX_TOKENS)))
    timeout_cap = min(_CHAT_TIMEOUT_SEC, float(agent.timeout_seconds or _CHAT_TIMEOUT_SEC))
    started = time.monotonic()
    try:
        result = await control.chat_with_failover(
            messages,
            prefer_agent_id=agent_id,
            allow_failover=False,
            admin_id=uid,
            timeout_override=timeout_cap,
            max_tokens_override=token_cap,
        )
        reply = result.text
        elapsed_ms = int((time.monotonic() - started) * 1000)
        logger.info(
            "admin chat ok agent=%s model=%s tokens=%s elapsed_ms=%s",
            agent.name,
            agent.model,
            result.usage_tokens,
            elapsed_ms,
        )
        history.append({"role": "user", "content": user_text[:2000]})
        history.append({"role": "assistant", "content": reply[:2000]})
        sess["history"] = history[-20:]
        await control.registry.set_session(uid, sess)
        try:
            await wait_msg.delete()
        except Exception:  # noqa: BLE001
            pass
        await message.answer(reply[:3900], reply_markup=ak.chat_with_agent_keyboard(lang))
    except Exception as exc:  # noqa: BLE001
        elapsed_ms = int((time.monotonic() - started) * 1000)
        safe = re.sub(r"sk-[A-Za-z0-9_-]+", "sk-••••", str(exc))[:300]
        logger.warning(
            "admin chat fail agent=%s elapsed_ms=%s err=%s",
            agent.name,
            elapsed_ms,
            type(exc).__name__,
        )
        try:
            await wait_msg.delete()
        except Exception:  # noqa: BLE001
            pass
        await message.answer(
            f"❌ پاسخ دریافت نشد\n{safe}"
            if lang == "fa"
            else f"❌ Agent chat failed\n{safe}",
            reply_markup=ak.chat_with_agent_keyboard(lang),
        )
    finally:
        stop_typing.set()
        typing_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await typing_task


async def _wizard_step_back_agent(
    message: Message,
    control: ControlService,
    uid: int,
    lang: str,
    sess: dict[str, Any],
) -> None:
    order = list(_WIZARD_STEPS.keys())
    step = str(sess.get("step") or "name")
    draft: dict[str, Any] = dict(sess.get("draft") or {})
    if step not in order:
        await control.registry.set_session(uid, {"mode": "control_home"})
        await _show_control_home(message, control, lang)
        return
    idx = order.index(step)
    if idx <= 0:
        await control.registry.set_session(uid, {"mode": "control_home"})
        await _show_control_home(message, control, lang)
        return
    prev = order[idx - 1]
    # Drop value for the step we leave so re-entry can overwrite cleanly.
    drop_map = {"api_key": "api_key_draft"}
    draft.pop(drop_map.get(step, step), None)
    sess.update({"mode": "add_agent", "step": prev, "draft": draft})
    await control.registry.set_session(uid, sess)
    prefix = "➕ افزودن ایجنت" if lang == "fa" else "➕ Add Agent"
    step_label = _WIZARD_STEPS[prev][lang if lang in _WIZARD_STEPS[prev] else "en"]
    kb = ak.role_keyboard(lang) if prev == "role" else ak.cancel_keyboard(lang)
    if prev == "system_prompt":
        kb = ak.skip_keyboard(lang)
    await message.answer(f"{prefix} — {step_label}:", reply_markup=kb)


async def _wizard_step_back_api(
    message: Message,
    control: ControlService,
    uid: int,
    lang: str,
    sess: dict[str, Any],
) -> None:
    order = ["name", "endpoint", "key", "model"]
    step = str(sess.get("step") or "name")
    draft: dict[str, Any] = dict(sess.get("draft") or {})
    if step not in order:
        await control.registry.set_session(uid, {"mode": "control_home"})
        await _show_control_home(message, control, lang)
        return
    idx = order.index(step)
    if idx <= 0:
        await control.registry.set_session(uid, {"mode": "control_home"})
        await _show_control_home(message, control, lang)
        return
    prev = order[idx - 1]
    drop = {
        "name": "provider_name",
        "endpoint": "api_endpoint",
        "key": "api_key_draft",
        "model": "model",
    }
    draft.pop(drop.get(step, step), None)
    sess.update({"mode": "add_api", "step": prev, "draft": draft})
    await control.registry.set_session(uid, sess)
    prompts = {
        "name": ak.msg("api_add_name", lang),
        "endpoint": ("API Endpoint:" if lang != "fa" else "آدرس API Endpoint:"),
        "key": ("API Key:" if lang != "fa" else "کلید API:"),
        "model": ("Model (optional):" if lang != "fa" else "Model (اختیاری):"),
    }
    await message.answer(prompts[prev], reply_markup=ak.cancel_keyboard(lang))


async def _add_agent_wizard(
    message: Message,
    control: ControlService,
    uid: int,
    lang: str,
    sess: dict[str, Any],
    text: str,
) -> None:
    step = str(sess.get("step") or "name")
    draft: dict[str, Any] = dict(sess.get("draft") or {})
    if ak.resolve_action(text) == "skip":
        text = ""

    order = list(_WIZARD_STEPS.keys())
    if step == "role":
        role = _parse_role(text)
        if not role:
            await message.answer(
                "نقش نامعتبر است. یکی از دکمه‌های نقش را بزنید."
                if lang == "fa"
                else "Invalid role. Choose a Role button.",
                reply_markup=ak.role_keyboard(lang),
            )
            return
        draft["role"] = role
        try:
            agent = await control.registry.add_agent(
                name=str(draft.get("name") or "Agent"),
                provider=str(draft.get("provider") or "openai-compatible"),
                model=str(draft.get("model") or ""),
                api_endpoint=str(draft.get("api_endpoint") or ""),
                api_key=str(draft.get("api_key_draft") or ""),
                system_prompt=str(draft.get("system_prompt") or ""),
                max_tokens=int(draft.get("max_tokens") or 4096),
                temperature=float(draft.get("temperature") or 0.4),
                role=role,
                priority={"primary": 10, "secondary": 20, "backup": 30, "support": 90}.get(
                    role, 100
                ),
            )
        except Exception as exc:  # noqa: BLE001
            await message.answer(
                f"❌ ذخیره ناموفق: {type(exc).__name__}"
                if lang == "fa"
                else f"❌ Save failed: {type(exc).__name__}",
                reply_markup=ak.cancel_keyboard(lang),
            )
            return
        await control.audit.write(
            "add_agent",
            admin_id=uid,
            detail=f"Added agent {agent.name}",
            meta={"agent_id": agent.id, "role": agent.role},
        )
        await control.registry.clear_session(uid)
        await control.registry.set_session(uid, {"mode": "control_home"})
        _ok, test_msg = await control.test_agent(agent.id, admin_id=uid, lang=lang)
        tip = (
            "پس از تست موفق، از «تنظیم به‌عنوان فعال» استفاده کنید."
            if lang == "fa"
            else "Use Set as Active to promote after a successful test."
        )
        await message.answer(
            f"✅ ایجنت ذخیره شد: {agent.name}\nشناسه: {agent.id}\n\n"
            f"{'نتیجه تست' if lang == 'fa' else 'Test Mode'}:\n{test_msg}\n\n{tip}",
            reply_markup=ak.control_home_keyboard(lang),
        )
        return

    if step not in order:
        step = "name"
    idx = order.index(step)
    field = order[idx]

    if field == "api_key":
        draft["api_key_draft"] = text
    elif field == "max_tokens":
        try:
            draft["max_tokens"] = int(text or "4096")
        except ValueError:
            await message.answer(
                "Max Tokens باید عدد باشد." if lang == "fa" else "Max Tokens must be a number.",
                reply_markup=ak.cancel_keyboard(lang),
            )
            return
    elif field == "temperature":
        try:
            draft["temperature"] = float(text or "0.4")
        except ValueError:
            await message.answer(
                "Temperature باید عدد باشد." if lang == "fa" else "Temperature must be a number.",
                reply_markup=ak.cancel_keyboard(lang),
            )
            return
    else:
        draft[field] = text

    if idx + 1 >= len(order):
        sess.update({"mode": "add_agent", "step": "role", "draft": draft})
        await control.registry.set_session(uid, sess)
        await message.answer(ak.msg("choose_role", lang), reply_markup=ak.role_keyboard(lang))
        return

    next_key = order[idx + 1]
    sess.update({"mode": "add_agent", "step": next_key, "draft": draft})
    await control.registry.set_session(uid, sess)
    step_label = _WIZARD_STEPS[next_key][lang if lang in _WIZARD_STEPS[next_key] else "en"]
    prefix = f"گام {idx + 2}/{len(order)}" if lang == "fa" else f"Step {idx + 2}/{len(order)}"
    kb = ak.role_keyboard(lang) if next_key == "role" else ak.cancel_keyboard(lang)
    if next_key == "system_prompt":
        kb = ak.skip_keyboard(lang)
    await message.answer(f"{prefix} — {step_label}:", reply_markup=kb)


async def _add_api_wizard(
    message: Message,
    control: ControlService,
    uid: int,
    lang: str,
    sess: dict[str, Any],
    text: str,
) -> None:
    step = str(sess.get("step") or "name")
    draft: dict[str, Any] = dict(sess.get("draft") or {})
    if step == "name":
        draft["provider_name"] = text
        sess.update({"step": "endpoint", "draft": draft, "mode": "add_api"})
        await control.registry.set_session(uid, sess)
        await message.answer(
            "API Endpoint:" if lang != "fa" else "آدرس API Endpoint:",
            reply_markup=ak.cancel_keyboard(lang),
        )
        return
    if step == "endpoint":
        draft["api_endpoint"] = text
        sess.update({"step": "key", "draft": draft, "mode": "add_api"})
        await control.registry.set_session(uid, sess)
        await message.answer(
            "API Key:" if lang != "fa" else "کلید API Key:",
            reply_markup=ak.cancel_keyboard(lang),
        )
        return
    if step == "key":
        draft["api_key_draft"] = text
        sess.update({"step": "model", "draft": draft, "mode": "add_api"})
        await control.registry.set_session(uid, sess)
        await message.answer(
            "Model (اختیاری، یا Skip):" if lang == "fa" else "Model (optional, or Skip):",
            reply_markup=ak.skip_keyboard(lang),
        )
        return
    if step == "model":
        model = "" if ak.resolve_action(text) == "skip" else text
        api = await control.registry.add_api(
            provider_name=str(draft.get("provider_name") or "API"),
            api_endpoint=str(draft.get("api_endpoint") or ""),
            api_key=str(draft.get("api_key_draft") or ""),
            model=model,
        )
        await control.audit.write(
            "add_api",
            admin_id=uid,
            detail=f"Added API {api.provider_name}",
            meta={"api_id": api.id},
        )
        await control.registry.clear_session(uid)
        await control.registry.set_session(uid, {"mode": "control_home"})
        await message.answer(
            f"✅ API ذخیره شد: {api.provider_name}\nID: {api.id}"
            if lang == "fa"
            else f"✅ API saved: {api.provider_name}\nID: {api.id}",
            reply_markup=ak.control_home_keyboard(lang),
        )
