"""Admin Settings: owner info, destinations, catalog wizard."""

from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path
from typing import Any

from aiogram import F, Router
from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.filters import Filter
from aiogram.types import LinkPreviewOptions, Message

from src.access import AdminAccess
from src.ai.client import AIClient, AIClientError
from src.ai.persona import apply_owner_info, looks_like_reasoning_leak, strip_reasoning_leak
from src.branding import load_creator_contact
from src.config import Settings
from src.control.audit import AuditLog
from src.control.service import ControlService
from src.custom_buttons import (
    ALLOWED_ACTIONS,
    CustomButton,
    action_catalog_help,
    dispatch_custom_button,
    new_button_id,
)
from src.health_report import build_health_report
from src.knowledge.catalog_builder import build_one_catalog, prepare_work_folder
from src.knowledge.product_catalogs import (
    ai_products_snippet,
    count_product_photos,
    create_product_stub,
    delete_product,
    ensure_product_asset_dirs,
    find_product_by_label,
    get_product,
    list_all_product_dicts,
    load_product_catalogs,
    load_product_raw,
    product_media_dir,
    save_product_raw,
    update_product_fields,
)
from src.knowledge.refresh import notify_knowledge_changed
from src.storage.bot_settings import SLOT_KINDS, TARGET_KEYS, BotSettingsStore
from src.storage.users import UserStore
from src.ui import admin_keyboards as ak
from src.ui import keyboards, texts
from src.utils.chat_dest import validate_destination

logger = logging.getLogger(__name__)

router = Router(name="admin_settings")


class _SettingsButtonFilter(Filter):
    """Match built-in settings labels or runtime custom button labels.

    Do NOT match main-menu product labels here — those must reach the public menu
    router. Product rows in the Products hub are handled via session mode text.
    """

    def __init__(self, static: set[str] | frozenset[str]) -> None:
        self._static = frozenset(static)

    async def __call__(self, message: Message) -> bool:
        text = (message.text or "").strip()
        if not text:
            return False
        if text in self._static or text in ak.custom_button_labels():
            return True
        # Old keyboards / RTL may send "✅ ساخت کاتالوگ" or "ساخت کاتالوگ ✅".
        return ak.resolve_action(text) == "catalog_run"


async def _settings_kb(lang: str, store: BotSettingsStore):
    customs = await store.list_custom_buttons(menu="settings")
    generated: list = []
    try:
        from src.generated.buttons import list_generated_buttons

        generated = list_generated_buttons(menu="settings", refresh=True)
    except Exception:  # noqa: BLE001
        generated = []
    ak.refresh_custom_button_labels(list(customs) + list(generated))
    return ak.settings_hub_keyboard(
        lang, custom_buttons=customs, generated_buttons=generated
    )


def _product_button_labels(knowledge_root: Path, lang: str) -> list[str]:
    labels: list[str] = []
    for data in list_all_product_dicts(knowledge_root):
        pid = str(data.get("product_id") or "")
        title = (data.get("title") or {})
        name = str(title.get("fa") or title.get("en") or pid)
        emoji = str(data.get("menu_emoji") or "").strip()
        on = bool(data.get("enabled", True))
        prefix = "" if on else "⬜ "
        labels.append(f"{prefix}{emoji} {name}".strip() if emoji else f"{prefix}{name}".strip())
    return labels


def _match_product_id_from_button(knowledge_root: Path, text: str) -> str | None:
    needle = (text or "").strip()
    for prefix in ("⬜ ", "✅ "):
        if needle.startswith(prefix):
            needle = needle[len(prefix) :].strip()
            break
    for data in list_all_product_dicts(knowledge_root):
        pid = str(data.get("product_id") or "")
        title = data.get("title") or {}
        name = str(title.get("fa") or title.get("en") or pid)
        emoji = str(data.get("menu_emoji") or "").strip()
        label = f"{emoji} {name}".strip() if emoji else name
        if needle in {label, name, pid, f"⬜ {label}", f"✅ {label}"}:
            return pid
    hit = find_product_by_label(needle, lang="fa") or find_product_by_label(needle, lang="en")
    return hit.product_id if hit else None


async def _show_products_hub(message: Message, settings: Settings, lang: str) -> None:
    load_product_catalogs(settings.knowledge_root)
    labels = _product_button_labels(settings.knowledge_root, lang)
    ak.refresh_product_manage_labels(labels)
    body = ak.msg("products_hub_intro", lang)
    if not labels:
        body += "\n\n" + ak.msg("products_empty", lang)
    else:
        lines = []
        for data in list_all_product_dicts(settings.knowledge_root):
            pid = data.get("product_id")
            on = "روشن" if data.get("enabled", True) else "خاموش"
            if not (lang or "").startswith("fa"):
                on = "on" if data.get("enabled", True) else "off"
            lines.append(f"• `{pid}` — {on}")
        body += "\n\n" + "\n".join(lines)
    await message.answer(
        body[:3900],
        reply_markup=ak.products_hub_keyboard(lang, product_labels=labels),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


async def _show_product_detail(
    message: Message, settings: Settings, lang: str, product_id: str
) -> None:
    load_product_catalogs(settings.knowledge_root)
    data = None
    for item in list_all_product_dicts(settings.knowledge_root):
        if str(item.get("product_id")) == product_id:
            data = item
            break
    if not data:
        await _show_products_hub(message, settings, lang)
        return
    title = (data.get("title") or {})
    name = title.get("fa") or title.get("en") or product_id
    summary = (data.get("short_summary") or {}).get("fa") or (data.get("short_summary") or {}).get(
        "en"
    ) or "—"
    on = data.get("enabled", True)
    cat_on = data.get("catalog_enabled", True)
    body = (
        f"🏷 {data.get('menu_emoji') or ''} {name}\n"
        f"id: `{product_id}`\n"
        f"{'وضعیت منو' if (lang or '').startswith('fa') else 'Menu'}: "
        f"{'روشن' if on else 'خاموش' if (lang or '').startswith('fa') else ('on' if on else 'off')}\n"
        f"{'استفادهٔ AI از کاتالوگ' if (lang or '').startswith('fa') else 'AI catalog use'}: "
        f"{'🟢 Enabled' if cat_on else '🔴 Disabled'}\n\n"
        f"{summary}"
    )
    await message.answer(
        body[:3900],
        reply_markup=ak.product_detail_keyboard(lang),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )

_TARGET_BY_ACTION = {
    "msg_channel": "channel",
    "msg_group": "group",
    "msg_support": "support",
    "msg_account": "support",
    "msg_test": "test",
}

_SLOT_BY_ACTION = {"slot_1": 0, "slot_2": 1, "slot_3": 2}

_OWNER_FIELD_BY_ACTION = {
    "owner_bot_name": "bot_display_name",
    "owner_site": "site_url",
    "owner_channel": "channel",
    "owner_group": "group",
    "owner_support": "support_handle",
}

_ASK_OWNER = {
    "bot_display_name": "ask_owner_bot_name",
    "site_url": "ask_owner_site",
    "channel": "ask_owner_channel",
    "group": "ask_owner_group",
    "support_handle": "ask_owner_support",
}

_EDIT_FIELD_BY_ACTION = {
    "edit_dest": "chat_id",
    "edit_template": "message_template",
    "edit_schedule": "schedule_times",
    "edit_rules": "rules_prompt",
    "edit_slot_kind": "kind",
    "edit_panel_url": "base_url",
    "edit_panel_token": "api_token",
    "edit_panel_inbound": "inbound_ids",
}

_ASK_MSG = {
    "chat_id": "ask_dest",
    "message_template": "ask_template",
    "schedule_times": "ask_schedule",
    "rules_prompt": "ask_rules",
    "kind": "ask_slot_kind",
    "base_url": "ask_panel_url",
    "api_token": "ask_panel_token",
    "inbound_ids": "ask_panel_inbound",
}


def _uid(message: Message) -> int:
    return message.from_user.id if message.from_user else 0


def _fmt_current(lang: str, value: Any, *, secret: bool = False) -> str:
    fa = (lang or "").startswith("fa")
    empty = "—" if fa else "-"
    if secret:
        raw = str(value or "").strip()
        if not raw:
            shown = empty
        elif len(raw) <= 8:
            shown = "••••"
        else:
            shown = raw[:4] + "…" + raw[-2:]
    else:
        shown = str(value).strip() if value is not None and str(value).strip() else empty
        if len(shown) > 600:
            shown = shown[:600] + "…"
    label = "مقدار فعلی" if fa else "Current value"
    return f"{label}: {shown}"


def _ask_with_current(lang: str, ask_key: str, value: Any, *, secret: bool = False) -> str:
    return f"{_fmt_current(lang, value, secret=secret)}\n\n{ak.msg(ask_key, lang)}"


def _ask_dest_key(target_key: str) -> str:
    return {
        "channel": "ask_dest_channel",
        "group": "ask_dest_group",
        "support": "ask_dest_account",
    }.get(target_key, "ask_dest")


def _expect_for_target(target_key: str) -> str | None:
    return {
        "channel": "channel",
        "group": "group",
        "support": "account",
    }.get(target_key)


def _staging_dir(settings: Settings, admin_id: int, product_id: str = "") -> Path:
    pid = (product_id or "").strip()
    if pid:
        return product_media_dir(settings.project_root, pid)
    path = settings.data_dir / "catalog_staging" / str(admin_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


_CONFIRM_YES = frozenset(
    {"تایید", "تاييد", "تأیید", "تاکید", "confirm", "yes", "ok", "✅"}
)
_CONFIRM_NO = frozenset(
    {"عدم تایید", "عدم تاييد", "عدم تأیید", "decline", "no", "cancel"}
)


def _is_yes(text: str) -> bool:
    return (text or "").strip().lower() in {x.lower() for x in _CONFIRM_YES}


def _is_no(text: str) -> bool:
    return (text or "").strip().lower() in {x.lower() for x in _CONFIRM_NO}


def _enrich_notes_path(staging: Path) -> Path:
    return staging / "_enrich_notes.json"


def _load_enrich_notes(staging: Path) -> list[dict[str, Any]]:
    path = _enrich_notes_path(staging)
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return []
    return [x for x in data if isinstance(x, dict)] if isinstance(data, list) else []


def _save_enrich_notes(staging: Path, notes: list[dict[str, Any]]) -> None:
    staging.mkdir(parents=True, exist_ok=True)
    _enrich_notes_path(staging).write_text(
        json.dumps(notes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _source_record(raw: dict[str, Any] | None, key: str) -> dict[str, Any]:
    block = (raw or {}).get("catalog_sources")
    if not isinstance(block, dict):
        return {"value": "", "use": False}
    item = block.get(key)
    if isinstance(item, dict):
        return {
            "value": str(item.get("value") or "").strip(),
            "use": bool(item.get("use")),
        }
    if isinstance(item, bool):
        return {"value": "", "use": item}
    if isinstance(item, str):
        return {"value": item.strip(), "use": bool(item.strip())}
    return {"value": "", "use": False}


def _source_marks(raw: dict[str, Any] | None) -> dict[str, bool]:
    return {
        key: bool(_source_record(raw, key).get("use") and _source_record(raw, key).get("value"))
        for key in ("site", "channel", "group")
    }


def _write_guide_files(folder: Path, *, training: str, extras: str, notes: list[dict[str, Any]]) -> None:
    chunks: list[str] = []
    if training.strip():
        chunks.append("### OPERATOR TRAINING\n" + training.strip())
    if extras.strip():
        chunks.append("### CONFIRMED SOURCES\n" + extras.strip())
    for item in notes:
        kind = str(item.get("kind") or "")
        guide = str(item.get("ai_note") or "").strip()
        if kind == "text":
            chunks.append(
                "### OPERATOR TEXT\n"
                + str(item.get("text") or "").strip()
                + (f"\nAI_GUIDE: {guide}" if guide else "")
            )
        elif kind == "photo":
            chunks.append(
                "### PHOTO "
                + Path(str(item.get("path") or "")).name
                + (f"\nAI_GUIDE: {guide}" if guide else "")
            )
    if chunks:
        (folder / "ai_guide_notes.txt").write_text("\n\n".join(chunks) + "\n", encoding="utf-8")


async def _execute_catalog_build(
    *,
    message: Message,
    settings: Settings,
    bot_settings: BotSettingsStore,
    uid: int,
    lang: str,
    sess: dict[str, Any],
    ai: AIClient,
) -> None:
    hint = str(sess.get("product_hint") or sess.get("product_id") or "").strip()
    staging = Path(
        str(sess.get("catalog_staging") or _staging_dir(settings, uid, hint))
    )
    folder_path = str(sess.get("catalog_path") or "").strip()
    if not hint:
        hint = Path(folder_path).name if folder_path else "product"
    raw = load_product_raw(settings.knowledge_root, hint) or {}
    notes = _load_enrich_notes(staging)
    extras: list[str] = []
    for key, title in (("site", "Official site"), ("channel", "Official channel"), ("group", "Official group")):
        rec = _source_record(raw, key)
        if rec.get("use") and rec.get("value"):
            extras.append(f"{title}: {rec['value']}")
    await message.answer(ak.msg("catalog_building", lang))
    try:
        staging.mkdir(parents=True, exist_ok=True)
        (staging / "operator_seed.txt").write_text(
            f"product_id={hint}\n", encoding="utf-8"
        )
        has_staging = staging.is_dir() and any(
            p.is_file() for p in staging.rglob("*") if p.name != "_enrich_notes.json"
        )
        if not has_staging and not folder_path:
            from src.knowledge.product_catalogs import product_media_dir

            media_dir = product_media_dir(settings.project_root, hint)
            if media_dir.is_dir() and any(media_dir.iterdir()):
                folder_path = str(media_dir)
        folder = prepare_work_folder(
            knowledge_root=settings.knowledge_root,
            folder_path=folder_path or None,
            staging_dir=staging if has_staging else None,
            product_hint=hint,
        )
        training = str(raw.get("ai_training_text") or "")
        _write_guide_files(folder, training=training, extras="\n".join(extras), notes=notes)
        pid = await build_one_catalog(
            folder,
            ai.chat,
            knowledge_root=settings.knowledge_root,
            project_root=settings.project_root,
            extra_sources="\n".join(extras),
            reload_fn=notify_knowledge_changed,
            force_product_id=hint,
            enrich_notes=notes,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("catalog wizard failed: %s", exc)
        cause = str(exc)
        await message.answer(
            (
                "❌ روند ساخت کاتالوگ ناموفق بود.\n"
                f"علت: {cause}\n"
                "عکس/متن را دوباره بفرستید و دوباره «ساخت کاتالوگ» را بزنید."
            )
            if (lang or "").startswith("fa")
            else f"❌ Catalog build failed.\nCause: {cause}",
            reply_markup=ak.catalog_wizard_keyboard(lang, sources=_source_marks(raw)),
        )
        return

    from src.knowledge.catalog_media_ingest import IngestResult, reindex_product_media_with_ai

    try:
        idx = await reindex_product_media_with_ai(
            knowledge_root=settings.knowledge_root,
            project_root=settings.project_root,
            product_id=pid,
            ai=ai,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("catalog media reindex failed: %s", exc)
        idx = IngestResult(
            ok=False,
            product_id=pid,
            files_added=[],
            message_fa=f"ساخت کاتالوگ OK بود؛ ایندکس تصاویر ناموفق. علت: {exc}",
            message_en=f"Catalog built; media reindex failed: {exc}",
            detail=str(exc),
        )
    notify_knowledge_changed()
    done = ak.msg("catalog_done", lang).format(ids=pid)
    if (lang or "").startswith("fa"):
        done += "\n\nروند ارسال به AI و سرور با موفقیت انجام شد."
        done += f"\n{idx.message_fa}"
    else:
        done += "\n\nSend to AI and server completed successfully."
        done += f"\n{idx.message_en}"
    await message.answer(done, reply_markup=ak.product_detail_keyboard(lang))
    await bot_settings.set_session(
        uid,
        {"mode": "product_detail", "product_id": str(sess.get("product_id") or pid)},
    )


async def _lang(users: UserStore, message: Message) -> str:
    uid = _uid(message)
    code = await users.get_lang(
        uid, message.from_user.language_code if message.from_user else None
    )
    return ak.ui_lang(code)


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


async def _show_messages_hub(message: Message, lang: str) -> None:
    await message.answer(ak.msg("messages_hub", lang), reply_markup=ak.messages_hub_keyboard(lang))


async def _show_owner(message: Message, store: BotSettingsStore, lang: str) -> None:
    owner = await store.get_owner()
    await message.answer(
        store.format_owner_card(owner, lang=lang),
        reply_markup=ak.owner_info_keyboard(lang),
    )


async def _show_target(
    message: Message, store: BotSettingsStore, key: str, lang: str
) -> None:
    target = await store.get_target(key)
    note = ""
    if key == "support" and (lang or "").startswith("fa"):
        note = (
            "\n\nاین بخش فقط برای پیام به اکانت کاربر معمولی است "
            "(نه کانال/گروه). خبر و کانفیگ را در بخش کانال تنظیم کنید."
        )
    elif key == "support":
        note = (
            "\n\nThis section is for normal user-account messages only "
            "(not channel/group). Configure news/config under Channel."
        )
    elif key == "channel" and (lang or "").startswith("fa"):
        note = (
            "\n\nخبر و کانفیگ رایگان اینجا تنظیم می‌شود. "
            "ربات باید در کانال مدیر باشد."
        )
    elif key == "channel":
        note = "\n\nNews and free-config slots live here. Bot must be channel admin."
    elif key == "group" and (lang or "").startswith("fa"):
        note = "\n\nربات باید در گروه مدیر باشد."
    elif key == "group":
        note = "\n\nBot must be an admin in the group."
    await message.answer(
        (store.format_target_card(target, lang=lang) + note)[:3900],
        reply_markup=ak.target_edit_keyboard(lang),
    )


async def _show_slot(
    message: Message, store: BotSettingsStore, key: str, slot_index: int, lang: str
) -> None:
    target = await store.get_target(key)
    kb = ak.slot_edit_keyboard(lang)
    # Account section: message-to-user only (no kind switch needed)
    if key == "support":
        from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=ak.label("edit_dest", lang))],
                [KeyboardButton(text=ak.label("edit_template", lang))],
                [KeyboardButton(text=ak.label("edit_schedule", lang))],
                [KeyboardButton(text=ak.label("edit_rules", lang))],
                [KeyboardButton(text=ak.label("nav_back", lang))],
                [KeyboardButton(text=ak.label("settings_back", lang))],
            ],
            resize_keyboard=True,
            is_persistent=True,
        )
    await message.answer(
        store.format_slot_card(target, slot_index, lang=lang)[:3900],
        reply_markup=kb,
    )


async def _show_panel(message: Message, store: BotSettingsStore, lang: str) -> None:
    panel = await store.get_panel()
    await message.answer(
        store.format_panel_card(panel, lang=lang),
        reply_markup=ak.panel_edit_keyboard(lang),
    )


async def _show_catalog_wizard(
    message: Message,
    store: BotSettingsStore,
    uid: int,
    lang: str,
    *,
    settings: Settings,
) -> None:
    sess = await store.get_session(uid)
    pid = str(sess.get("product_id") or sess.get("product_hint") or "").strip()
    staging = Path(str(sess.get("catalog_staging") or _staging_dir(settings, uid)))
    raw = load_product_raw(settings.knowledge_root, pid) if pid else None
    if pid:
        ensure_product_asset_dirs(settings.project_root, settings.knowledge_root, pid)
        staging = product_media_dir(settings.project_root, pid)
    photos = count_product_photos(
        settings.knowledge_root,
        settings.project_root,
        pid,
        staging=None,
    )
    raw_title = ((raw or {}).get("title") or {})
    pname = str(raw_title.get("fa") or raw_title.get("en") or pid or "—")
    body = ak.msg("catalog_wizard_intro", lang).format(photo_count=photos, product=pname)
    marks = _source_marks(raw)
    sess_marks = sess.get("catalog_source_marks")
    if isinstance(sess_marks, dict):
        marks = {**marks, **{k: bool(v) for k, v in sess_marks.items()}}
    await message.answer(
        body,
        reply_markup=ak.catalog_wizard_keyboard(lang, sources=marks),
    )


async def _show_training_hub(
    message: Message,
    *,
    settings: Settings,
    bot_settings: BotSettingsStore,
    uid: int,
    lang: str,
    pid: str,
    from_wizard: bool,
) -> None:
    from src.knowledge.ai_memory import catalog_teaching_text

    saved = catalog_teaching_text(settings.knowledge_root, pid)
    if not saved:
        raw = load_product_raw(settings.knowledge_root, pid) or {}
        saved = str(raw.get("ai_training_text") or "").strip()
    if saved:
        status = ak.msg("products_training_status_ok", lang).format(n=len(saved))
    else:
        status = ak.msg("products_training_status_empty", lang)
    await bot_settings.set_session(
        uid,
        {
            "mode": "products_ai_training_hub",
            "product_id": pid,
            "from_catalog_wizard": from_wizard,
            "catalog_staging": str(_staging_dir(settings, uid, pid)),
            "product_hint": pid,
        },
    )
    await message.answer(
        ak.msg("products_training_hub", lang).format(status=status),
        reply_markup=ak.training_hub_keyboard(lang),
    )


async def _show_ai_chat_hub(
    message: Message,
    *,
    bot_settings: BotSettingsStore,
    uid: int,
    lang: str,
    product_id: str = "",
    from_product: bool = False,
) -> None:
    await bot_settings.set_session(
        uid,
        {
            "mode": "ai_chat_hub",
            "product_id": product_id,
            "from_product": from_product,
            "ai_chat_all": False,
            "ai_chat_task": "",
        },
    )
    await message.answer(
        ak.msg("bot_chat_start", lang),
        reply_markup=ak.ai_chat_hub_keyboard(lang),
    )


def setup_admin_settings_router(
    users: UserStore,
    *,
    settings: Settings,
    bot_settings: BotSettingsStore,
    audit: AuditLog,
    control: ControlService | None = None,
    ai: AIClient | None = None,
    access: AdminAccess | None = None,
) -> Router:
    access = access or AdminAccess(settings, bot_settings)

    async def _require_settings(message: Message) -> tuple[bool, str]:
        uid = _uid(message)
        lang = await _lang(users, message)
        if not uid or not await access.can_settings(uid):
            if uid and await access.can_stats(uid):
                await message.answer(ak.msg("settings_denied", lang))
            else:
                await message.answer(ak.msg("admin_only", lang))
            return False, lang
        return True, lang

    async def _admins_card(lang: str) -> str:
        env_ids = sorted(settings.bot_admin_ids)
        env_txt = "\n".join(f"• {i} (full/env)" for i in env_ids) or "—"
        extra = await bot_settings.list_extra_admins()
        extra_txt = (
            "\n".join(f"• {uid} ({role})" for uid, role in extra) if extra else "—"
        )
        return ak.msg("admins_card", lang).format(
            env_admins=env_txt,
            extra_admins=extra_txt,
        )

    async def _clear_control(uid: int) -> None:
        if control is not None:
            await control.registry.clear_session(uid)

    async def _save_dest(
        message: Message,
        *,
        uid: int,
        lang: str,
        target_key: str,
        slot_index: int | None,
        value: str,
    ) -> bool:
        expect = _expect_for_target(target_key)
        if expect and message.bot is not None:
            check = await validate_destination(message.bot, value, expect=expect)
            if not check.ok:
                detail = check.detail_fa if (lang or "").startswith("fa") else check.detail_en
                await message.answer(
                    ak.msg("dest_type_mismatch", lang).format(detail=detail),
                    reply_markup=ak.cancel_keyboard(lang),
                )
                if check.need_admin:
                    await message.answer(ak.msg("dest_need_admin", lang))
                return False
            value = check.chat_id or value
        if slot_index is None:
            await bot_settings.update_target(target_key, chat_id=value)
        else:
            await bot_settings.update_slot(target_key, slot_index, chat_id=value)
        return True

    @router.message(F.text.in_(set(texts.MENU_SETTINGS.values()) | ak.texts("settings_hub")))
    async def on_settings_entry(message: Message) -> None:
        ok, lang = await _require_settings(message)
        if not ok:
            return
        uid = _uid(message)
        await users.set_ask_ai(uid, False)
        await bot_settings.set_session(uid, {"mode": "settings"})
        await _clear_control(uid)
        await _show_settings_hub(message, lang, bot_settings)

    button_texts = (
        ak.texts("settings_messages")
        | ak.texts("settings_panel")
        | ak.texts("settings_back")
        | ak.texts("nav_back")
        | ak.texts("owner_info")
        | ak.texts("creator_contact")
        | ak.texts("bot_config_chat")
        | ak.texts("bot_config_chat_legacy")
        | ak.texts("ai_chat_core")
        | ak.texts("ai_chat_buttons")
        | ak.texts("ai_chat_teach_product")
        | ak.texts("ai_chat_teach_behavior")
        | ak.texts("ai_chat_all_products")
        | ak.texts("build_catalogs")
        | ak.texts("products_hub")
        | ak.texts("products_add")
        | ak.texts("products_edit_title")
        | ak.texts("products_edit_emoji")
        | ak.texts("products_edit_summary")
        | ak.texts("products_toggle")
        | ak.texts("products_catalog_ai")
        | ak.texts("products_delete")
        | ak.texts("products_build_catalog")
        | ak.texts("products_catalog_enrich")
        | ak.texts("products_ai_training")
        | ak.texts("products_ai_training_edit")
        | ak.texts("products_ai_training_delete")
        | ak.texts("products_product_chat")
        | ak.texts("products_product_chat_legacy")
        | ak.texts("products_back")
        | ak.texts("catalog_src_site")
        | ak.texts("catalog_src_channel")
        | ak.texts("catalog_src_group")
        | ak.texts("catalog_run")
        | {
            "✅ ساخت کاتالوگ",
            "ساخت کاتالوگ ✅",
            "ساخت کاتالوگ",
            "✅ Build Catalog",
            "Build Catalog ✅",
            "Build Catalog",
            "📦 ساخت کاتالوگ",
            "📦 Build Catalog",
        }
        | ak.texts("owner_bot_name")
        | ak.texts("owner_site")
        | ak.texts("owner_channel")
        | ak.texts("owner_group")
        | ak.texts("owner_support")
        | ak.texts("msg_channel")
        | ak.texts("msg_group")
        | ak.texts("msg_support")
        | ak.texts("msg_account")
        | ak.texts("msg_test")
        | ak.texts("slot_1")
        | ak.texts("slot_2")
        | ak.texts("slot_3")
        | ak.texts("edit_dest")
        | ak.texts("edit_dest_legacy")
        | ak.texts("edit_template")
        | ak.texts("edit_template_legacy")
        | ak.texts("edit_schedule")
        | ak.texts("edit_schedule_legacy")
        | ak.texts("edit_rules")
        | ak.texts("edit_rules_legacy")
        | ak.texts("edit_slot_kind")
        | ak.texts("toggle_slot_enabled")
        | ak.texts("edit_panel_url")
        | ak.texts("edit_panel_url_legacy")
        | ak.texts("edit_panel_token")
        | ak.texts("edit_panel_token_legacy")
        | ak.texts("edit_panel_inbound")
        | ak.texts("edit_panel_inbound_legacy")
        | ak.texts("backup_settings")
        | ak.texts("backup_export")
        | ak.texts("backup_import")
        | ak.texts("health_status")
        | ak.texts("health_toggle")
        | ak.texts("health_times")
        | ak.texts("health_chat")
        | ak.texts("manage_admins")
        | ak.texts("admin_role_full")
        | ak.texts("admin_role_stats")
        | ak.texts("admin_remove")
        | ak.texts("cancel")
    )
    # include toggle-prefixed labels
    for src in ("catalog_src_site", "catalog_src_channel", "catalog_src_group"):
        for v in ak.texts(src):
            button_texts |= {f"✅ {v}", f"⬜ {v}"}

    @router.message(_SettingsButtonFilter(button_texts))
    async def on_settings_button(message: Message) -> None:
        uid = _uid(message)
        lang = await _lang(users, message)
        action = ak.resolve_action(message.text)

        # Custom / generated buttons (must run before empty-action return).
        if not action:
            try:
                from src.generated.buttons import dispatch_generated, find_generated_by_label

                gen = find_generated_by_label(message.text or "")
            except Exception:  # noqa: BLE001
                gen = None
            if gen:
                # Stats-menu generated buttons are handled in admin_control (stats role).
                if str(gen.get("menu") or "settings") == "stats":
                    raise SkipHandler()
                ok, lang = await _require_settings(message)
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
            raw_btn = await bot_settings.find_custom_button_by_label(message.text or "")
            if raw_btn:
                ok, lang = await _require_settings(message)
                if not ok:
                    raise SkipHandler()
                btn = CustomButton.from_dict(raw_btn)
                if btn is None:
                    raise SkipHandler()
                await dispatch_custom_button(
                    message,
                    btn,
                    lang=lang,
                    settings=settings,
                    bot_settings=bot_settings,
                    show_owner=_show_owner,
                    show_messages_hub=_show_messages_hub,
                    show_panel=_show_panel,
                    show_slot=_show_slot,
                    show_settings_hub=_show_settings_hub,
                )
                return
            raise SkipHandler()

        # Health report is allowed for stats-only admins too.
        if action == "health_status":
            if not await access.can_stats(uid):
                await message.answer(ak.msg("admin_only", lang))
                return
            report = await build_health_report(settings, bot_settings, lang=lang)
            if await access.can_settings(uid):
                await bot_settings.set_session(uid, {"mode": "health"})
                await message.answer(report[:3900], reply_markup=ak.health_keyboard(lang))
            else:
                await message.answer(
                    report[:3900],
                    reply_markup=ak.stats_hub_keyboard(lang, show_news_report=False),
                )
            return

        # Contact Creator: public info. From Settings keep settings keyboard;
        # from main menu let the public menu router answer.
        if action == "creator_contact":
            sess = await bot_settings.get_session(uid)
            mode = str(sess.get("mode") or "")
            in_settings = mode in {
                "settings",
                "owner",
                "messages_hub",
                "panel",
                "backup",
                "health",
                "admins",
                "products_hub",
                "product_detail",
                "catalog_wizard",
                "bot_config_chat",
            }
            if await access.can_settings(uid) and in_settings:
                from src.branding import load_creator_contact

                await message.answer(
                    load_creator_contact(settings.knowledge_root).format_card(lang),
                    reply_markup=await _settings_kb(lang, bot_settings),
                )
                return
            raise SkipHandler()

        ok, lang = await _require_settings(message)
        if not ok:
            return
        uid = _uid(message)
        await users.set_ask_ai(uid, False)

        if action == "settings_back":
            await bot_settings.set_session(uid, {"mode": "settings"})
            await _clear_control(uid)
            await _show_settings_hub(message, lang, bot_settings)
            return

        if action == "backup_settings":
            await bot_settings.set_session(uid, {"mode": "backup"})
            await message.answer(
                "💾 " + ("پشتیبان تنظیمات" if lang == "fa" else "Settings backup"),
                reply_markup=ak.backup_keyboard(lang),
            )
            return

        if action == "backup_export":
            import json
            from datetime import datetime

            from aiogram.types import BufferedInputFile

            payload = await bot_settings.export_backup()
            raw = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
            name = f"smart-support-bot-settings-{datetime.utcnow().strftime('%Y%m%d-%H%M')}.json"
            await message.answer_document(
                BufferedInputFile(raw, filename=name),
                caption=ak.msg("backup_exported", lang),
                reply_markup=ak.backup_keyboard(lang),
            )
            await audit.write("export_settings_backup", admin_id=uid, detail=name)
            return

        if action == "backup_import":
            await bot_settings.set_session(uid, {"mode": "import_backup"})
            await message.answer(
                ak.msg("ask_backup_import", lang),
                reply_markup=ak.cancel_keyboard(lang),
            )
            return

        if action == "health_toggle":
            cfg = await bot_settings.get_health_settings()
            cfg = await bot_settings.update_health_settings(enabled=not cfg.get("enabled", True))
            state = ("روشن" if cfg.get("enabled") else "خاموش") if lang == "fa" else ("on" if cfg.get("enabled") else "off")
            await message.answer(
                f"{'گزارش روزانه' if lang == 'fa' else 'Daily report'}: {state}",
                reply_markup=ak.health_keyboard(lang),
            )
            return

        if action == "health_times":
            cfg = await bot_settings.get_health_settings()
            await bot_settings.set_session(uid, {"mode": "edit_health", "health_field": "times"})
            await message.answer(
                ak.msg("ask_health_times", lang) + "\n" + _fmt_current(lang, cfg.get("times")),
                reply_markup=ak.cancel_keyboard(lang),
            )
            return

        if action == "health_chat":
            cfg = await bot_settings.get_health_settings()
            await bot_settings.set_session(uid, {"mode": "edit_health", "health_field": "chat_id"})
            await message.answer(
                ak.msg("ask_health_chat", lang) + "\n" + _fmt_current(lang, cfg.get("chat_id") or "—"),
                reply_markup=ak.cancel_keyboard(lang),
            )
            return

        if action == "manage_admins":
            await bot_settings.set_session(uid, {"mode": "admins"})
            await message.answer(await _admins_card(lang), reply_markup=ak.admins_keyboard(lang))
            return

        if action in {"admin_role_full", "admin_role_stats", "admin_remove"}:
            await bot_settings.set_session(
                uid,
                {"mode": "edit_admin", "admin_action": action},
            )
            await message.answer(ak.msg("ask_admin_id", lang), reply_markup=ak.cancel_keyboard(lang))
            return

        if action == "nav_back":
            sess = await bot_settings.get_session(uid)
            mode = str(sess.get("mode") or "")
            target_key = str(sess.get("target_key") or "")
            slot_index = sess.get("slot_index")
            if mode in {"backup", "health", "admins", "catalog_wizard", "products_hub"}:
                await bot_settings.clear_session(uid)
                await _show_settings_hub(message, lang, bot_settings)
                return
            if mode in {
                "products_add_title",
                "products_add_emoji",
                "products_add_summary",
                "products_edit",
                "product_detail",
            }:
                await bot_settings.set_session(uid, {"mode": "products_hub"})
                await _show_products_hub(message, settings, lang)
                return
            if mode in {"edit_slot", "scoped_rules_ai"} and target_key in TARGET_KEYS and slot_index is not None:
                await bot_settings.set_session(
                    uid,
                    {"mode": "slot", "target_key": target_key, "slot_index": int(slot_index)},
                )
                await _show_slot(message, bot_settings, target_key, int(slot_index), lang)
                return
            if mode == "slot" and target_key in TARGET_KEYS:
                await bot_settings.set_session(uid, {"mode": "target", "target_key": target_key})
                await _show_target(message, bot_settings, target_key, lang)
                return
            if mode == "edit_target" and target_key in TARGET_KEYS:
                await bot_settings.set_session(uid, {"mode": "target", "target_key": target_key})
                await _show_target(message, bot_settings, target_key, lang)
                return
            if mode in {"edit_owner", "owner"}:
                await bot_settings.set_session(uid, {"mode": "owner"})
                await _show_owner(message, bot_settings, lang)
                return
            if mode == "edit_panel":
                await bot_settings.set_session(uid, {"mode": "panel"})
                await _show_panel(message, bot_settings, lang)
                return
            if mode == "target" and target_key in TARGET_KEYS:
                await bot_settings.set_session(uid, {"mode": "messages_hub"})
                await _show_messages_hub(message, lang)
                return
            if mode in {"panel", "messages_hub", "bot_config_chat", "owner"}:
                await bot_settings.clear_session(uid)
                await _show_settings_hub(message, lang, bot_settings)
                return
            raise SkipHandler()

        if action == "cancel":
            sess = await bot_settings.get_session(uid)
            if not sess or sess.get("mode") in {None, ""}:
                raise SkipHandler()
            target_key = str(sess.get("target_key") or "")
            slot_index = sess.get("slot_index")
            mode = str(sess.get("mode") or "")
            if mode == "catalog_wizard":
                await _show_catalog_wizard(message, bot_settings, uid, lang, settings=settings)
                return
            if mode in {
                "products_hub",
                "product_detail",
                "products_add_title",
                "products_add_emoji",
                "products_add_summary",
                "products_edit",
                "products_ai_training",
                "products_ai_training_append",
                "products_ai_training_replace",
                "products_ai_training_hub",
                "product_ai_chat",
                "ai_chat_hub",
                "ai_chat_pick_product",
                "ai_chat_teach_product",
                "ai_chat_teach_behavior",
                "catalog_enrich",
                "catalog_enrich_note",
                "catalog_source_wait",
                "catalog_source_confirm",
                "catalog_run_confirm",
            }:
                await bot_settings.set_session(uid, {"mode": "products_hub"})
                await _show_products_hub(message, settings, lang)
                return
            await bot_settings.clear_session(uid)
            if target_key in TARGET_KEYS and slot_index is not None:
                await bot_settings.set_session(
                    uid,
                    {"mode": "slot", "target_key": target_key, "slot_index": int(slot_index)},
                )
                await _show_slot(message, bot_settings, target_key, int(slot_index), lang)
            elif target_key in TARGET_KEYS:
                await bot_settings.set_session(uid, {"mode": "target", "target_key": target_key})
                await _show_target(message, bot_settings, target_key, lang)
            elif mode in {"panel", "edit_panel"}:
                await bot_settings.set_session(uid, {"mode": "panel"})
                await _show_panel(message, bot_settings, lang)
            elif mode in {"owner", "edit_owner"}:
                await bot_settings.set_session(uid, {"mode": "owner"})
                await _show_owner(message, bot_settings, lang)
            else:
                await _show_settings_hub(message, lang, bot_settings)
            return

        if action == "owner_info":
            await bot_settings.set_session(uid, {"mode": "owner"})
            await message.answer(ak.msg("owner_hub", lang))
            await _show_owner(message, bot_settings, lang)
            return

        if action == "bot_config_chat":
            sess = await bot_settings.get_session(uid)
            pid = str(sess.get("product_id") or "").strip()
            from_product = bool(pid) and str(sess.get("mode") or "") in {
                "product_detail",
                "catalog_wizard",
                "catalog_enrich",
                "product_ai_chat",
                "bot_config_chat",
                "ai_chat_hub",
                "products_ai_training_hub",
            }
            await _show_ai_chat_hub(
                message,
                bot_settings=bot_settings,
                uid=uid,
                lang=lang,
                product_id=pid if from_product else "",
                from_product=from_product,
            )
            return

        if action in {
            "ai_chat_core",
            "ai_chat_buttons",
            "ai_chat_teach_product",
            "ai_chat_teach_behavior",
            "ai_chat_all_products",
        }:
            sess = await bot_settings.get_session(uid)
            pid = str(sess.get("product_id") or "").strip()
            from_product = bool(sess.get("from_product"))
            if action == "ai_chat_all_products":
                task = str(sess.get("pending_task") or sess.get("ai_chat_task") or "")
                mode = (
                    "ai_chat_teach_behavior"
                    if task == "behavior"
                    else "ai_chat_teach_product"
                )
                await bot_settings.set_session(
                    uid,
                    {
                        **sess,
                        "mode": mode,
                        "ai_chat_all": True,
                        "product_id": "",
                        "from_product": from_product,
                    },
                )
                ask = (
                    "ai_chat_ask_behavior"
                    if mode == "ai_chat_teach_behavior"
                    else "ai_chat_ask_product_teach"
                )
                await message.answer(
                    ak.msg(ask, lang),
                    reply_markup=ak.ai_chat_hub_keyboard(lang),
                )
                return
            if action == "ai_chat_core":
                await bot_settings.set_session(
                    uid,
                    {
                        "mode": "bot_config_chat",
                        "product_id": pid,
                        "from_product": from_product,
                        "ai_chat_task": "core",
                        "history": [],
                    },
                )
                await message.answer(
                    (
                        "اطلاعات اصلی: نام، سایت، کانال، گروه، پشتیبانی، پیام‌ها، پنل، سلامت، ادمین یا ستون کیبورد را بگویید."
                        if (lang or "").startswith("fa")
                        else "Main settings: send the change for owner, messages, panel, health, admins, or keyboard."
                    ),
                    reply_markup=ak.ai_chat_hub_keyboard(lang),
                )
                return
            if action == "ai_chat_buttons":
                await bot_settings.set_session(
                    uid,
                    {
                        "mode": "bot_config_chat",
                        "product_id": pid,
                        "from_product": from_product,
                        "ai_chat_task": "buttons",
                        "history": [],
                    },
                )
                await message.answer(
                    (
                        "ساخت کلید: مثلاً بنویسید «کلید بساز: خلاصه وضعیت پنل»."
                        if (lang or "").startswith("fa")
                        else "Build button: e.g. send “create button: panel status”."
                    ),
                    reply_markup=ak.ai_chat_hub_keyboard(lang),
                )
                return
            task = "behavior" if action == "ai_chat_teach_behavior" else "product"
            if not pid:
                labels = _product_button_labels(settings.knowledge_root, lang)
                await bot_settings.set_session(
                    uid,
                    {
                        "mode": "ai_chat_pick_product",
                        "pending_task": task,
                        "from_product": from_product,
                        "product_id": "",
                        "ai_chat_all": False,
                    },
                )
                await message.answer(
                    ak.msg("ai_chat_ask_product", lang),
                    reply_markup=ak.ai_chat_product_pick_keyboard(labels, lang),
                )
                return
            mode = (
                "ai_chat_teach_behavior" if task == "behavior" else "ai_chat_teach_product"
            )
            await bot_settings.set_session(
                uid,
                {
                    "mode": mode,
                    "product_id": pid,
                    "from_product": from_product,
                    "ai_chat_all": False,
                    "pending_task": task,
                },
            )
            await message.answer(
                ak.msg(
                    "ai_chat_ask_behavior" if task == "behavior" else "ai_chat_ask_product_teach",
                    lang,
                ),
                reply_markup=ak.ai_chat_hub_keyboard(lang),
            )
            return

        if action == "products_hub":
            await bot_settings.set_session(uid, {"mode": "products_hub"})
            await _show_products_hub(message, settings, lang)
            return

        if action == "products_back":
            sess = await bot_settings.get_session(uid)
            mode_now = str(sess.get("mode") or "")
            pid_now = str(sess.get("product_id") or "").strip()
            if mode_now in {
                "ai_chat_hub",
                "ai_chat_pick_product",
                "ai_chat_teach_product",
                "ai_chat_teach_behavior",
                "bot_config_chat",
            }:
                if sess.get("from_product") and pid_now:
                    await bot_settings.set_session(
                        uid, {"mode": "product_detail", "product_id": pid_now}
                    )
                    await _show_product_detail(message, settings, lang, pid_now)
                    return
                await _show_settings_hub(message, lang, bot_settings)
                return
            if mode_now in {
                "products_ai_training_hub",
                "products_ai_training",
                "products_ai_training_append",
                "products_ai_training_replace",
            } and pid_now and sess.get("from_catalog_wizard"):
                sess["mode"] = "catalog_wizard"
                await bot_settings.set_session(uid, sess)
                await _show_catalog_wizard(
                    message, bot_settings, uid, lang, settings=settings
                )
                return
            await bot_settings.set_session(uid, {"mode": "products_hub"})
            await _show_products_hub(message, settings, lang)
            return

        if action in {"products_ai_training_edit", "products_ai_training_delete"}:
            sess = await bot_settings.get_session(uid)
            pid = str(sess.get("product_id") or "").strip()
            from_wizard = bool(sess.get("from_catalog_wizard"))
            if not pid:
                await bot_settings.set_session(uid, {"mode": "products_hub"})
                await _show_products_hub(message, settings, lang)
                return
            if action == "products_ai_training_delete":
                raw = load_product_raw(settings.knowledge_root, pid) or {}
                raw["ai_training_text"] = ""
                save_product_raw(settings.knowledge_root, pid, raw)
                from src.knowledge.ai_memory import set_catalog_teaching

                set_catalog_teaching(settings.knowledge_root, pid, "")
                notify_knowledge_changed()
                await audit.write("product_ai_training_delete", admin_id=uid, detail=pid)
                await message.answer(ak.msg("products_training_cleared", lang))
                await _show_training_hub(
                    message,
                    settings=settings,
                    bot_settings=bot_settings,
                    uid=uid,
                    lang=lang,
                    pid=pid,
                    from_wizard=from_wizard,
                )
                return
            from src.knowledge.ai_memory import catalog_teaching_text

            saved = catalog_teaching_text(settings.knowledge_root, pid)
            if not saved:
                raw = load_product_raw(settings.knowledge_root, pid) or {}
                saved = str(raw.get("ai_training_text") or "").strip()
            await bot_settings.set_session(
                uid,
                {
                    "mode": "products_ai_training_replace",
                    "product_id": pid,
                    "from_catalog_wizard": from_wizard,
                    "catalog_staging": str(_staging_dir(settings, uid, pid)),
                    "product_hint": pid,
                },
            )
            await message.answer(
                ak.msg("products_ask_training", lang).format(saved=saved or "—"),
                reply_markup=ak.training_hub_keyboard(lang),
            )
            return

        if action == "products_add":
            await bot_settings.set_session(uid, {"mode": "products_add_title"})
            await message.answer(
                ak.msg("products_ask_title", lang),
                reply_markup=ak.cancel_keyboard(lang),
            )
            return

        if action in {
            "products_edit_title",
            "products_edit_emoji",
            "products_edit_summary",
            "products_toggle",
            "products_catalog_ai",
            "products_delete",
            "products_build_catalog",
            "products_catalog_enrich",
            "products_ai_training",
            "products_product_chat",
        }:
            sess = await bot_settings.get_session(uid)
            pid = str(sess.get("product_id") or "").strip()
            if not pid:
                await bot_settings.set_session(uid, {"mode": "products_hub"})
                await _show_products_hub(message, settings, lang)
                return
            if action == "products_catalog_ai":
                data = next(
                    (
                        d
                        for d in list_all_product_dicts(settings.knowledge_root)
                        if str(d.get("product_id")) == pid
                    ),
                    None,
                )
                cur = bool((data or {}).get("catalog_enabled", True))
                update_product_fields(settings.knowledge_root, pid, catalog_enabled=not cur)
                await audit.write("product_catalog_ai", admin_id=uid, detail=f"{pid}:{not cur}")
                if (lang or "").startswith("fa"):
                    feedback = (
                        "استفادهٔ AI از این کاتالوگ روشن شد."
                        if not cur
                        else "استفادهٔ AI از این کاتالوگ خاموش شد."
                    )
                else:
                    feedback = (
                        "AI catalog use was enabled."
                        if not cur
                        else "AI catalog use was disabled."
                    )
                await message.answer(feedback)
                await bot_settings.set_session(
                    uid, {"mode": "product_detail", "product_id": pid}
                )
                await _show_product_detail(message, settings, lang, pid)
                return
            if action == "products_toggle":
                data = next(
                    (
                        d
                        for d in list_all_product_dicts(settings.knowledge_root)
                        if str(d.get("product_id")) == pid
                    ),
                    None,
                )
                cur = bool((data or {}).get("enabled", True))
                update_product_fields(settings.knowledge_root, pid, enabled=not cur)
                await audit.write("product_toggle", admin_id=uid, detail=f"{pid}:{not cur}")
                await bot_settings.set_session(
                    uid, {"mode": "product_detail", "product_id": pid}
                )
                await _show_product_detail(message, settings, lang, pid)
                return
            if action == "products_delete":
                delete_product(settings.knowledge_root, pid)
                await audit.write("product_delete", admin_id=uid, detail=pid)
                await bot_settings.set_session(uid, {"mode": "products_hub"})
                await message.answer(ak.msg("products_deleted", lang))
                await _show_products_hub(message, settings, lang)
                return
            if action == "products_product_chat":
                await _show_ai_chat_hub(
                    message,
                    bot_settings=bot_settings,
                    uid=uid,
                    lang=lang,
                    product_id=pid,
                    from_product=True,
                )
                return
            if action == "products_ai_training":
                sess_now = await bot_settings.get_session(uid)
                if str(sess_now.get("mode") or "") == "products_ai_training_hub":
                    await bot_settings.set_session(
                        uid,
                        {
                            "mode": "products_ai_training_append",
                            "product_id": pid,
                            "from_catalog_wizard": bool(sess_now.get("from_catalog_wizard")),
                            "catalog_staging": str(_staging_dir(settings, uid, pid)),
                            "product_hint": pid,
                        },
                    )
                    await message.answer(
                        ak.msg("products_ask_training_append", lang),
                        reply_markup=ak.training_hub_keyboard(lang),
                    )
                    return
                await _show_training_hub(
                    message,
                    settings=settings,
                    bot_settings=bot_settings,
                    uid=uid,
                    lang=lang,
                    pid=pid,
                    from_wizard=True,
                )
                return
            if action in {"products_build_catalog", "products_catalog_enrich"}:
                ensure_product_asset_dirs(
                    settings.project_root, settings.knowledge_root, pid
                )
                staging = _staging_dir(settings, uid, pid)
                staging.mkdir(parents=True, exist_ok=True)
                await bot_settings.set_session(
                    uid,
                    {
                        "mode": "catalog_wizard",
                        "catalog_path": "",
                        "catalog_staging": str(staging),
                        "product_id": pid,
                        "product_hint": pid,
                    },
                )
                await _show_catalog_wizard(
                    message, bot_settings, uid, lang, settings=settings
                )
                return
            field = {
                "products_edit_title": "title",
                "products_edit_emoji": "emoji",
                "products_edit_summary": "summary",
            }[action]
            await bot_settings.set_session(
                uid,
                {"mode": "products_edit", "product_id": pid, "product_field": field},
            )
            ask = {
                "title": "products_ask_edit_title",
                "emoji": "products_ask_edit_emoji",
                "summary": "products_ask_edit_summary",
            }[field]
            await message.answer(ak.msg(ask, lang), reply_markup=ak.cancel_keyboard(lang))
            return

        if action == "build_catalogs":
            await bot_settings.set_session(uid, {"mode": "products_hub"})
            tip = (
                "ساخت کاتالوگ از مسیر «محصولات» انجام می‌شود.\n"
                "محصول را انتخاب کنید و «ساخت/تکمیل کاتالوگ» را بزنید."
                if (lang or "").startswith("fa")
                else (
                    "Catalog build is under Products.\n"
                    "Select a product, then tap Build / Enrich Catalog."
                )
            )
            await message.answer(tip)
            await _show_products_hub(message, settings, lang)
            return

        if action in {"catalog_src_site", "catalog_src_channel", "catalog_src_group"}:
            sess = await bot_settings.get_session(uid)
            if sess.get("mode") not in {
                "catalog_wizard",
                "catalog_enrich",
                "catalog_source_wait",
                "catalog_source_confirm",
                "catalog_run_confirm",
            }:
                await _show_settings_hub(message, lang, bot_settings)
                return
            key = action.replace("catalog_src_", "")
            pid = str(sess.get("product_id") or "").strip()
            raw = load_product_raw(settings.knowledge_root, pid) or {}
            rec = _source_record(raw, key)
            owner = await bot_settings.get_owner()
            fallback = {
                "site": owner.site_url,
                "channel": owner.channel,
                "group": owner.group,
            }.get(key) or ""
            saved = rec.get("value") or fallback or "—"
            sess["mode"] = "catalog_source_wait"
            sess["catalog_source_key"] = key
            await bot_settings.set_session(uid, sess)
            await message.answer(
                ak.msg("catalog_ask_source", lang).format(saved=saved),
                reply_markup=ak.catalog_wizard_keyboard(lang, sources=_source_marks(raw)),
            )
            return

        if action == "catalog_run":
            sess = await bot_settings.get_session(uid)
            pid = str(sess.get("product_id") or sess.get("product_hint") or "").strip()
            staging = Path(str(sess.get("catalog_staging") or _staging_dir(settings, uid, pid)))
            if not pid:
                await message.answer(
                    "اول محصول را باز کنید، بعد ساخت کاتالوگ را بزنید."
                    if (lang or "").startswith("fa")
                    else "Open a product first, then tap Build Catalog.",
                    reply_markup=await _settings_kb(lang, bot_settings),
                )
                return
            raw = load_product_raw(settings.knowledge_root, pid) or {}
            photos = count_product_photos(
                settings.knowledge_root,
                settings.project_root,
                pid,
                staging=staging if staging.is_dir() else None,
            )
            notes = _load_enrich_notes(staging)
            sess["mode"] = "catalog_wizard"
            sess["catalog_staging"] = str(staging)
            sess["product_id"] = pid
            sess["product_hint"] = pid
            await bot_settings.set_session(uid, sess)

            def _shown(key: str) -> str:
                rec = _source_record(raw, key)
                if rec.get("use") and rec.get("value"):
                    return str(rec["value"])
                return "—"

            await message.answer(
                ak.msg("catalog_confirm_preview", lang).format(
                    photo_count=photos,
                    site=_shown("site"),
                    channel=_shown("channel"),
                    group=_shown("group"),
                    notes=len(notes),
                )
                + "\n\n"
                + ak.msg("catalog_building", lang),
                reply_markup=ak.catalog_wizard_keyboard(lang, sources=_source_marks(raw)),
            )
            if ai is None:
                await message.answer(
                    "❌ سرویس AI در دسترس نیست. ساخت کاتالوگ انجام نشد."
                    if (lang or "").startswith("fa")
                    else "❌ AI is unavailable. Catalog was not built.",
                    reply_markup=ak.catalog_wizard_keyboard(lang, sources=_source_marks(raw)),
                )
                return
            try:
                await _execute_catalog_build(
                    message=message,
                    settings=settings,
                    bot_settings=bot_settings,
                    uid=uid,
                    lang=lang,
                    sess=sess,
                    ai=ai,
                )
            except Exception as exc:  # noqa: BLE001
                logger.exception("catalog_run handler failed: %s", exc)
                await message.answer(
                    f"❌ روند ساخت کاتالوگ ناموفق بود.\nعلت: {exc}"
                    if (lang or "").startswith("fa")
                    else f"❌ Catalog build failed.\nCause: {exc}",
                    reply_markup=ak.catalog_wizard_keyboard(lang, sources=_source_marks(raw)),
                )
            return

        if action in _OWNER_FIELD_BY_ACTION:
            field = _OWNER_FIELD_BY_ACTION[action]
            owner = await bot_settings.get_owner()
            current = getattr(owner, field, "") or ""
            await bot_settings.set_session(uid, {"mode": "edit_owner", "owner_field": field})
            await message.answer(
                _ask_with_current(lang, _ASK_OWNER[field], current),
                reply_markup=ak.cancel_keyboard(lang),
            )
            return

        if action == "settings_messages":
            await bot_settings.set_session(uid, {"mode": "messages_hub"})
            await _show_messages_hub(message, lang)
            return

        if action == "settings_panel":
            await bot_settings.set_session(uid, {"mode": "panel"})
            await _show_panel(message, bot_settings, lang)
            return

        if action in _TARGET_BY_ACTION:
            key = _TARGET_BY_ACTION[action]
            # Account section: force static slots for user DMs
            if key == "support":
                target = await bot_settings.get_target(key)
                for i, s in enumerate(target.slots):
                    if s.kind != "static":
                        await bot_settings.update_slot(key, i, kind="static")
            await bot_settings.set_session(uid, {"mode": "target", "target_key": key})
            await _show_target(message, bot_settings, key, lang)
            return

        if action in _SLOT_BY_ACTION:
            sess = await bot_settings.get_session(uid)
            key = str(sess.get("target_key") or "")
            if key not in TARGET_KEYS:
                await _show_messages_hub(message, lang)
                return
            idx = _SLOT_BY_ACTION[action]
            await bot_settings.set_session(
                uid, {"mode": "slot", "target_key": key, "slot_index": idx}
            )
            await _show_slot(message, bot_settings, key, idx, lang)
            return

        if action == "toggle_slot_enabled":
            sess = await bot_settings.get_session(uid)
            target_key = str(sess.get("target_key") or "")
            slot_index = sess.get("slot_index")
            if target_key not in TARGET_KEYS or slot_index is None:
                await message.answer(
                    "اول یک اسلات را باز کنید." if lang == "fa" else "Open a slot first.",
                    reply_markup=ak.messages_hub_keyboard(lang),
                )
                return
            idx = int(slot_index)
            target = await bot_settings.get_target(target_key)
            slot = target.slot(idx)
            new_enabled = not bool(slot.enabled)
            await bot_settings.update_slot(target_key, idx, enabled=new_enabled)
            await audit.write(
                "toggle_slot_enabled",
                admin_id=uid,
                detail=f"{target_key}/{idx} -> {new_enabled}",
                meta={"target": target_key, "slot": idx, "enabled": new_enabled},
            )
            state = ("فعال" if new_enabled else "غیرفعال") if lang == "fa" else ("on" if new_enabled else "off")
            await message.answer(
                (f"اسلات {idx + 1}: {state}" if lang == "fa" else f"Slot {idx + 1}: {state}"),
            )
            await _show_slot(message, bot_settings, target_key, idx, lang)
            return

        if action in _EDIT_FIELD_BY_ACTION:
            field = _EDIT_FIELD_BY_ACTION[action]
            sess = await bot_settings.get_session(uid)
            if field in {"base_url", "api_token", "inbound_ids"}:
                panel = await bot_settings.get_panel()
                if field == "api_token":
                    ask_body = _ask_with_current(
                        lang, _ASK_MSG[field], bot_settings.mask_panel_token(panel)
                    )
                elif field == "base_url":
                    ask_body = _ask_with_current(lang, _ASK_MSG[field], panel.base_url)
                else:
                    ask_body = _ask_with_current(lang, _ASK_MSG[field], panel.inbound_ids)
                await bot_settings.set_session(
                    uid, {"mode": "edit_panel", "panel_field": field}
                )
                await message.answer(ask_body, reply_markup=ak.cancel_keyboard(lang))
                return
            target_key = str(sess.get("target_key") or "")
            slot_index = sess.get("slot_index")
            if target_key not in TARGET_KEYS:
                await _show_messages_hub(message, lang)
                return
            if sess.get("mode") == "target" and field == "chat_id":
                target = await bot_settings.get_target(target_key)
                await bot_settings.set_session(
                    uid,
                    {"mode": "edit_target", "target_key": target_key, "field": "chat_id"},
                )
                await message.answer(
                    _ask_with_current(lang, _ask_dest_key(target_key), target.chat_id),
                    reply_markup=ak.cancel_keyboard(lang),
                )
                return
            if slot_index is None and sess.get("mode") == "target":
                await message.answer(
                    "یک اسلات (۱/۲/۳) انتخاب کنید." if lang == "fa" else "Pick a slot (1/2/3).",
                    reply_markup=ak.target_edit_keyboard(lang),
                )
                return
            idx = int(slot_index if slot_index is not None else 0)
            target = await bot_settings.get_target(target_key)
            slot = target.slot(idx)
            if field == "rules_prompt":
                await bot_settings.set_session(
                    uid,
                    {
                        "mode": "scoped_rules_ai",
                        "target_key": target_key,
                        "slot_index": idx,
                        "history": [],
                    },
                )
                await message.answer(
                    _ask_with_current(lang, "scoped_rules_start", slot.rules_prompt),
                    reply_markup=ak.cancel_keyboard(lang),
                )
                await message.answer(
                    _ask_with_current(lang, "ask_rules", slot.rules_prompt),
                    reply_markup=ak.cancel_keyboard(lang),
                )
                return
            if field == "kind" and target_key == "support":
                await message.answer(
                    "این بخش فقط پیام به اکانت کاربر است (نوع ثابت)."
                    if lang == "fa"
                    else "Account section uses static user messages only.",
                )
                return
            current_map = {
                "chat_id": slot.chat_id or target.chat_id,
                "message_template": slot.message_template,
                "schedule_times": slot.schedule_times,
                "kind": slot.kind,
            }
            ask_key = _ask_dest_key(target_key) if field == "chat_id" else _ASK_MSG[field]
            await bot_settings.set_session(
                uid,
                {
                    "mode": "edit_slot",
                    "target_key": target_key,
                    "slot_index": idx,
                    "field": field,
                },
            )
            await message.answer(
                _ask_with_current(lang, ask_key, current_map.get(field, "")),
                reply_markup=ak.cancel_keyboard(lang),
            )
            return

    @router.message(F.chat.type == "private", F.text, ~F.text.startswith("/"))
    async def on_products_hub_pick(message: Message) -> None:
        """Admin product-row taps while in Products hub (before public menu router)."""
        uid = _uid(message)
        if not uid or not await access.can_settings(uid):
            raise SkipHandler()
        if await users.is_ask_ai(uid):
            raise SkipHandler()
        sess = await bot_settings.get_session(uid)
        mode = str(sess.get("mode") or "")
        if mode not in {"products_hub", "product_detail"}:
            raise SkipHandler()
        text = (message.text or "").strip()
        if not text:
            raise SkipHandler()
        # Let dedicated settings/product action buttons handle themselves.
        if ak.resolve_action(text):
            raise SkipHandler()
        if text in ak.texts("cancel"):
            raise SkipHandler()
        pid = _match_product_id_from_button(settings.knowledge_root, text)
        if not pid:
            raise SkipHandler()
        lang = await _lang(users, message)
        await users.set_ask_ai(uid, False)
        await bot_settings.set_session(uid, {"mode": "product_detail", "product_id": pid})
        await _show_product_detail(message, settings, lang, pid)

    @router.message(F.chat.type == "private", F.document | F.photo)
    async def on_catalog_upload(message: Message) -> None:
        uid = _uid(message)
        if not await access.can_settings(uid) or not message.bot:
            return
        sess = await bot_settings.get_session(uid)
        lang = await _lang(users, message)

        if sess.get("mode") == "import_backup":
            if not message.document:
                await message.answer(ak.msg("ask_backup_import", lang))
                return
            import json
            from io import BytesIO

            buf = BytesIO()
            await message.bot.download(message.document, destination=buf)
            try:
                payload = json.loads(buf.getvalue().decode("utf-8"))
                applied = await bot_settings.import_backup(payload)
            except Exception as exc:  # noqa: BLE001
                await message.answer(f"❌ {exc}", reply_markup=ak.backup_keyboard(lang))
                return
            apply_owner_info(await bot_settings.get_owner())
            await audit.write(
                "import_settings_backup",
                admin_id=uid,
                detail=",".join(applied),
            )
            await bot_settings.set_session(uid, {"mode": "backup"})
            await message.answer(
                ak.msg("backup_imported", lang).format(
                    sections=", ".join(applied) or "—"
                ),
                reply_markup=ak.backup_keyboard(lang),
            )
            return

        if sess.get("mode") == "product_detail" and (message.photo or message.document):
            await message.answer(
                "برای ارسال عکس و متن از کلید «تکمیل اطلاعات کاتالوگ» استفاده کنید."
                if lang.startswith("fa")
                else "Use Complete catalog info to send photos and text.",
                reply_markup=ak.product_detail_keyboard(lang),
            )
            return

        if sess.get("mode") == "bot_config_chat" and message.photo and message.bot:
            staging = settings.data_dir / "config_chat_images" / str(uid)
            staging.mkdir(parents=True, exist_ok=True)
            photo = message.photo[-1]
            dest = staging / f"photo_{photo.file_unique_id}.jpg"
            try:
                await message.bot.download(photo, destination=dest)
            except Exception as exc:  # noqa: BLE001
                await message.answer(f"❌ upload failed: {exc}")
                return
            imgs = list(sess.get("config_chat_images") or [])
            imgs.append(str(dest))
            sess["config_chat_images"] = imgs[-8:]
            await bot_settings.set_session(uid, sess)
            await message.answer(
                "✅ عکس ذخیره شد. در پیام بعدی بگویید با این عکس چه کاری انجام شود."
                if lang.startswith("fa")
                else "✅ Photo saved. In your next message say what to do with it.",
                reply_markup=ak.cancel_keyboard(lang),
            )
            return

        if sess.get("mode") not in {"catalog_wizard", "catalog_enrich"}:
            raise SkipHandler()
        pid = str(sess.get("product_id") or "").strip()
        staging = Path(str(sess.get("catalog_staging") or _staging_dir(settings, uid, pid)))
        staging.mkdir(parents=True, exist_ok=True)
        try:
            if message.document:
                dest = staging / (message.document.file_name or f"file_{message.document.file_id}")
                await message.bot.download(message.document, destination=dest)
            elif message.photo:
                photo = message.photo[-1]
                dest = staging / f"photo_{photo.file_unique_id}.jpg"
                await message.bot.download(photo, destination=dest)
            else:
                return
        except Exception as exc:  # noqa: BLE001
            await message.answer(f"❌ upload failed: {exc}")
            return
        raw = load_product_raw(settings.knowledge_root, pid) or {}
        sess["mode"] = "catalog_enrich_note"
        sess["pending_enrich"] = {"kind": "photo", "path": str(dest)}
        await bot_settings.set_session(uid, sess)
        await message.answer(
            ak.msg("catalog_enrich_ask_note", lang),
            reply_markup=ak.catalog_wizard_keyboard(lang, sources=_source_marks(raw)),
        )

    @router.message(
        F.chat.type == "private",
        F.text,
        ~F.text.startswith("/"),
        ~F.text.in_(ak.all_admin_control_texts()),
        ~F.text.in_(keyboards.all_menu_button_texts()),
        ~F.text.in_(keyboards.all_lang_button_texts()),
    )
    async def on_settings_text(message: Message) -> None:
        uid = _uid(message)
        if not await access.can_settings(uid):
            raise SkipHandler()
        # Public Ask AI must not be captured by settings wizards.
        if await users.is_ask_ai(uid):
            raise SkipHandler()
        lang = await _lang(users, message)
        sess = await bot_settings.get_session(uid)
        mode = sess.get("mode")
        if mode not in {
            "edit_target",
            "edit_panel",
            "edit_slot",
            "edit_owner",
            "edit_health",
            "edit_admin",
            "scoped_rules_ai",
            "bot_config_chat",
            "catalog_wizard",
            "catalog_enrich",
            "catalog_enrich_note",
            "catalog_source_wait",
            "catalog_source_confirm",
            "catalog_run_confirm",
            "products_add_title",
            "products_add_emoji",
            "products_add_summary",
            "products_edit",
            "products_ai_training",
            "products_ai_training_append",
            "products_ai_training_replace",
            "products_ai_training_hub",
            "product_ai_chat",
            "ai_chat_hub",
            "ai_chat_pick_product",
            "ai_chat_teach_product",
            "ai_chat_teach_behavior",
        }:
            raise SkipHandler()

        text = (message.text or "").strip()
        if not text:
            return

        if mode == "products_add_title":
            await bot_settings.set_session(
                uid, {"mode": "products_add_emoji", "new_product_title": text}
            )
            await message.answer(
                ak.msg("products_ask_emoji", lang),
                reply_markup=ak.cancel_keyboard(lang),
            )
            return
        if mode == "products_add_emoji":
            emoji = "📦" if text in {"—", "-", "–", "default"} else text.strip()[:8]
            sess["new_product_emoji"] = emoji
            sess["mode"] = "products_add_summary"
            await bot_settings.set_session(uid, sess)
            await message.answer(
                ak.msg("products_ask_summary", lang),
                reply_markup=ak.cancel_keyboard(lang),
            )
            return
        if mode == "products_add_summary":
            title = str(sess.get("new_product_title") or "").strip()
            emoji = str(sess.get("new_product_emoji") or "📦")
            try:
                created = create_product_stub(
                    settings.knowledge_root,
                    title=title or "Product",
                    emoji=emoji,
                    summary=text,
                )
            except Exception as exc:  # noqa: BLE001
                await message.answer(f"❌ {exc}", reply_markup=ak.cancel_keyboard(lang))
                return
            await audit.write("product_add", admin_id=uid, detail=created.product_id)
            await bot_settings.set_session(
                uid, {"mode": "product_detail", "product_id": created.product_id}
            )
            await message.answer(ak.msg("saved_ok", lang))
            await _show_product_detail(message, settings, lang, created.product_id)
            return
        if mode == "products_edit":
            pid = str(sess.get("product_id") or "").strip()
            field = str(sess.get("product_field") or "").strip()
            if not pid or field not in {"title", "emoji", "summary"}:
                await bot_settings.set_session(uid, {"mode": "products_hub"})
                await _show_products_hub(message, settings, lang)
                return
            try:
                if field == "title":
                    update_product_fields(settings.knowledge_root, pid, title=text)
                elif field == "emoji":
                    update_product_fields(
                        settings.knowledge_root,
                        pid,
                        emoji="📦" if text in {"—", "-", "–"} else text.strip()[:8],
                    )
                else:
                    update_product_fields(settings.knowledge_root, pid, summary=text)
            except Exception as exc:  # noqa: BLE001
                await message.answer(f"❌ {exc}", reply_markup=ak.cancel_keyboard(lang))
                return
            await audit.write("product_edit", admin_id=uid, detail=f"{pid}:{field}")
            await bot_settings.set_session(
                uid, {"mode": "product_detail", "product_id": pid}
            )
            await message.answer(ak.msg("saved_ok", lang))
            await _show_product_detail(message, settings, lang, pid)
            return

        if mode == "ai_chat_hub":
            await message.answer(
                ak.msg("bot_chat_start", lang),
                reply_markup=ak.ai_chat_hub_keyboard(lang),
            )
            return

        if mode == "ai_chat_pick_product":
            if ak.resolve_action(text) == "ai_chat_all_products" or text == ak.label(
                "ai_chat_all_products", lang
            ):
                task = str(sess.get("pending_task") or "product")
                mode_next = (
                    "ai_chat_teach_behavior" if task == "behavior" else "ai_chat_teach_product"
                )
                await bot_settings.set_session(
                    uid,
                    {
                        **sess,
                        "mode": mode_next,
                        "ai_chat_all": True,
                        "product_id": "",
                    },
                )
                await message.answer(
                    ak.msg(
                        "ai_chat_ask_behavior" if task == "behavior" else "ai_chat_ask_product_teach",
                        lang,
                    ),
                    reply_markup=ak.ai_chat_hub_keyboard(lang),
                )
                return
            picked = _match_product_id_from_button(settings.knowledge_root, text)
            if not picked:
                labels = _product_button_labels(settings.knowledge_root, lang)
                await message.answer(
                    ak.msg("ai_chat_ask_product", lang),
                    reply_markup=ak.ai_chat_product_pick_keyboard(labels, lang),
                )
                return
            task = str(sess.get("pending_task") or "product")
            mode_next = (
                "ai_chat_teach_behavior" if task == "behavior" else "ai_chat_teach_product"
            )
            await bot_settings.set_session(
                uid,
                {
                    **sess,
                    "mode": mode_next,
                    "product_id": picked,
                    "ai_chat_all": False,
                },
            )
            await message.answer(
                ak.msg(
                    "ai_chat_ask_behavior" if task == "behavior" else "ai_chat_ask_product_teach",
                    lang,
                ),
                reply_markup=ak.ai_chat_hub_keyboard(lang),
            )
            return

        if mode in {"ai_chat_teach_behavior", "ai_chat_teach_product"}:
            from src.knowledge.ai_memory import append_operator_teaching

            kind = "behavior" if mode == "ai_chat_teach_behavior" else "fact"
            all_products = bool(sess.get("ai_chat_all"))
            pid = str(sess.get("product_id") or "").strip()
            if not all_products and not pid:
                labels = _product_button_labels(settings.knowledge_root, lang)
                sess["mode"] = "ai_chat_pick_product"
                sess["pending_task"] = "behavior" if kind == "behavior" else "product"
                await bot_settings.set_session(uid, sess)
                await message.answer(
                    ak.msg("ai_chat_ask_product", lang),
                    reply_markup=ak.ai_chat_product_pick_keyboard(labels, lang),
                )
                return
            targets = append_operator_teaching(
                settings.knowledge_root,
                pid,
                text,
                kind=kind,
                all_products=all_products,
            )
            notify_knowledge_changed()
            await audit.write(
                "ai_chat_teach",
                admin_id=uid,
                detail=f"{kind}:{','.join(targets) or 'none'}",
            )
            await message.answer(
                ak.msg("ai_chat_saved_targets", lang).format(
                    targets=", ".join(targets) or "—"
                ),
                reply_markup=ak.ai_chat_hub_keyboard(lang),
            )
            await _show_ai_chat_hub(
                message,
                bot_settings=bot_settings,
                uid=uid,
                lang=lang,
                product_id=pid if not all_products else "",
                from_product=bool(sess.get("from_product")),
            )
            return

        if mode == "products_ai_training_hub":
            await message.answer(
                "برای افزودن متن، «ارسال متن آموزشی برای ai» و برای جایگزینی، «ویرایش متن آموزشی» را بزنید."
                if (lang or "").startswith("fa")
                else "Tap Send AI training text to append, or Edit to replace.",
                reply_markup=ak.training_hub_keyboard(lang),
            )
            return

        if mode in {"products_ai_training", "products_ai_training_append", "products_ai_training_replace"}:
            pid = str(sess.get("product_id") or "").strip()
            if not pid:
                await bot_settings.set_session(uid, {"mode": "products_hub"})
                await _show_products_hub(message, settings, lang)
                return
            from src.knowledge.ai_memory import append_catalog_training, replace_catalog_training

            if mode == "products_ai_training_replace":
                replace_catalog_training(settings.knowledge_root, pid, text)
            else:
                append_catalog_training(settings.knowledge_root, pid, text)
            notify_knowledge_changed()
            await audit.write("product_ai_training", admin_id=uid, detail=pid)
            back_wizard = bool(sess.get("from_catalog_wizard"))
            await bot_settings.set_session(
                uid,
                {
                    "mode": "catalog_wizard" if back_wizard else "product_detail",
                    "product_id": pid,
                    "catalog_staging": str(_staging_dir(settings, uid, pid)),
                    "product_hint": pid,
                },
            )
            await message.answer(ak.msg("saved_ok", lang))
            await _show_training_hub(
                message,
                settings=settings,
                bot_settings=bot_settings,
                uid=uid,
                lang=lang,
                pid=pid,
                from_wizard=back_wizard,
            )
            return

        if mode == "edit_health":
            field = str(sess.get("health_field") or "")
            if field == "times":
                await bot_settings.update_health_settings(times=text)
            elif field == "chat_id":
                await bot_settings.update_health_settings(chat_id=text)
            else:
                await bot_settings.clear_session(uid)
                await _show_settings_hub(message, lang, bot_settings)
                return
            await bot_settings.set_session(uid, {"mode": "health"})
            await message.answer(ak.msg("saved_ok", lang), reply_markup=ak.health_keyboard(lang))
            report = await build_health_report(settings, bot_settings, lang=lang)
            await message.answer(report[:3900], reply_markup=ak.health_keyboard(lang))
            return

        if mode == "edit_admin":
            action = str(sess.get("admin_action") or "")
            try:
                target_id = int(text.replace("@", "").strip())
            except ValueError:
                await message.answer(ak.msg("ask_admin_id", lang), reply_markup=ak.cancel_keyboard(lang))
                return
            if target_id in settings.bot_admin_ids and action == "admin_remove":
                await message.answer(
                    ("ادمین env را از BOT_ADMIN_IDS حذف کنید." if lang == "fa" else "Remove env admins from BOT_ADMIN_IDS."),
                    reply_markup=ak.admins_keyboard(lang),
                )
                return
            if action == "admin_role_full":
                await bot_settings.set_admin_role(target_id, "full")
            elif action == "admin_role_stats":
                await bot_settings.set_admin_role(target_id, "stats")
            elif action == "admin_remove":
                await bot_settings.remove_admin(target_id)
            else:
                await bot_settings.clear_session(uid)
                await _show_settings_hub(message, lang, bot_settings)
                return
            await audit.write(
                "update_admin_role",
                admin_id=uid,
                detail=f"{action}:{target_id}",
            )
            await bot_settings.set_session(uid, {"mode": "admins"})
            await message.answer(ak.msg("saved_ok", lang))
            await message.answer(await _admins_card(lang), reply_markup=ak.admins_keyboard(lang))
            return

        if mode == "catalog_source_wait":
            pid = str(sess.get("product_id") or "").strip()
            raw = load_product_raw(settings.knowledge_root, pid) or {}
            sess["mode"] = "catalog_source_confirm"
            sess["catalog_source_pending"] = text
            await bot_settings.set_session(uid, sess)
            await message.answer(
                _fmt_current(lang, text) + "\n\n" + ak.msg("catalog_ask_confirm", lang),
                reply_markup=ak.catalog_wizard_keyboard(lang, sources=_source_marks(raw)),
            )
            return

        if mode == "catalog_source_confirm":
            pid = str(sess.get("product_id") or "").strip()
            key = str(sess.get("catalog_source_key") or "")
            pending = str(sess.get("catalog_source_pending") or "").strip()
            raw = load_product_raw(settings.knowledge_root, pid) or {}
            sources = raw.get("catalog_sources") if isinstance(raw.get("catalog_sources"), dict) else {}
            if _is_yes(text) and key:
                sources[key] = {"value": pending, "use": True}
                raw["catalog_sources"] = sources
                save_product_raw(settings.knowledge_root, pid, raw)
                await message.answer(ak.msg("saved_ok", lang))
            elif _is_no(text):
                await message.answer(ak.msg("catalog_declined", lang))
            else:
                await message.answer(ak.msg("catalog_ask_confirm", lang))
                return
            sess["mode"] = "catalog_wizard"
            sess.pop("catalog_source_pending", None)
            sess.pop("catalog_source_key", None)
            await bot_settings.set_session(uid, sess)
            await _show_catalog_wizard(message, bot_settings, uid, lang, settings=settings)
            return

        if mode == "catalog_run_confirm":
            if _is_no(text):
                sess["mode"] = "catalog_wizard"
                await bot_settings.set_session(uid, sess)
                await message.answer(ak.msg("catalog_declined", lang))
                await _show_catalog_wizard(message, bot_settings, uid, lang, settings=settings)
                return
            if not _is_yes(text):
                await message.answer(ak.msg("catalog_ask_confirm", lang))
                return
            if ai is None:
                await message.answer("AI unavailable.")
                return
            await _execute_catalog_build(
                message=message,
                settings=settings,
                bot_settings=bot_settings,
                uid=uid,
                lang=lang,
                sess=sess,
                ai=ai,
            )
            return

        if mode == "catalog_enrich":
            pid = str(sess.get("product_id") or "").strip()
            raw = load_product_raw(settings.knowledge_root, pid) or {}
            staging = Path(str(sess.get("catalog_staging") or _staging_dir(settings, uid)))
            staging.mkdir(parents=True, exist_ok=True)
            sess["mode"] = "catalog_enrich_note"
            sess["pending_enrich"] = {"kind": "text", "text": text}
            await bot_settings.set_session(uid, sess)
            await message.answer(
                ak.msg("catalog_enrich_ask_note", lang),
                reply_markup=ak.catalog_wizard_keyboard(lang, sources=_source_marks(raw)),
            )
            return

        if mode == "catalog_enrich_note":
            pid = str(sess.get("product_id") or "").strip()
            raw = load_product_raw(settings.knowledge_root, pid) or {}
            staging = _staging_dir(settings, uid, pid)
            pending = dict(sess.get("pending_enrich") or {})
            pending["ai_note"] = text
            notes = _load_enrich_notes(staging)
            notes.append(pending)
            _save_enrich_notes(staging, notes)
            if pending.get("kind") == "photo" and pending.get("path"):
                from src.knowledge.catalog_media_ingest import ingest_files_to_product_catalog

                src = Path(str(pending["path"]))
                await message.answer(
                    "در حال تحلیل عکس این محصول…"
                    if (lang or "").startswith("fa")
                    else "Analyzing this product photo…",
                )
                result = await ingest_files_to_product_catalog(
                    knowledge_root=settings.knowledge_root,
                    project_root=settings.project_root,
                    product_id=pid,
                    source_files=[src] if src.is_file() else [],
                    ai=ai,
                    ai_guides={src.name.lower(): text},
                )
                body = result.message_fa if (lang or "").startswith("fa") else result.message_en
            else:
                mats = raw.get("operator_materials")
                if not isinstance(mats, list):
                    mats = []
                mats.append(
                    {
                        "text": str(pending.get("text") or "").strip(),
                        "ai_guide": text,
                    }
                )
                raw["operator_materials"] = mats[-40:]
                save_product_raw(settings.knowledge_root, pid, raw)
                body = ak.msg("saved_ok", lang)
            notify_knowledge_changed()
            sess["mode"] = "catalog_wizard"
            sess.pop("pending_enrich", None)
            sess["catalog_staging"] = str(staging)
            await bot_settings.set_session(uid, sess)
            await message.answer(body[:3900], reply_markup=ak.catalog_wizard_keyboard(lang, sources=_source_marks(load_product_raw(settings.knowledge_root, pid))))
            await _show_catalog_wizard(message, bot_settings, uid, lang, settings=settings)
            return

        if mode == "catalog_wizard":
            pid = str(sess.get("product_id") or "").strip()
            raw = load_product_raw(settings.knowledge_root, pid) or {}
            looks_path = ("/" in text or "\\" in text) and not text.startswith(("http://", "https://"))
            if looks_path:
                sess["catalog_path"] = text
                await bot_settings.set_session(uid, sess)
                await message.answer(
                    ("✅ مسیر ذخیره شد." if lang == "fa" else "✅ Path saved.")
                    + "\n"
                    + _fmt_current(lang, text),
                    reply_markup=ak.catalog_wizard_keyboard(lang, sources=_source_marks(raw)),
                )
                return
            sess["mode"] = "catalog_enrich_note"
            sess["pending_enrich"] = {"kind": "text", "text": text}
            await bot_settings.set_session(uid, sess)
            await message.answer(
                ak.msg("catalog_enrich_ask_note", lang),
                reply_markup=ak.catalog_wizard_keyboard(lang, sources=_source_marks(raw)),
            )
            return

        if mode == "edit_owner":
            field = str(sess.get("owner_field") or "")
            if field not in {
                "site_url",
                "channel",
                "group",
                "support_handle",
                "bot_display_name",
            }:
                await bot_settings.clear_session(uid)
                await _show_settings_hub(message, lang, bot_settings)
                return
            owner = await bot_settings.update_owner(**{field: text})
            apply_owner_info(owner)
            if field == "bot_display_name":
                from src.branding import sync_telegram_bot_name

                await sync_telegram_bot_name(message.bot, text)
            await audit.write(
                "update_owner_info",
                admin_id=uid,
                detail=f"Updated owner.{field}",
                meta={"field": field},
            )
            await bot_settings.set_session(uid, {"mode": "owner"})
            await message.answer(ak.msg("saved_ok", lang))
            await _show_owner(message, bot_settings, lang)
            return

        if mode == "edit_target":
            key = str(sess.get("target_key") or "")
            field = str(sess.get("field") or "")
            if key not in TARGET_KEYS or field != "chat_id":
                await bot_settings.clear_session(uid)
                await _show_messages_hub(message, lang)
                return
            ok = await _save_dest(
                message, uid=uid, lang=lang, target_key=key, slot_index=None, value=text
            )
            if not ok:
                return
            updated = await bot_settings.get_target(key)
            await audit.write(
                "update_message_target",
                admin_id=uid,
                detail=f"Updated chat_id for {key}",
                meta={"target": key, "field": "chat_id"},
            )
            await bot_settings.set_session(uid, {"mode": "target", "target_key": key})
            await message.answer(ak.msg("saved_ok", lang))
            await message.answer(
                bot_settings.format_target_card(updated, lang=lang)[:3900],
                reply_markup=ak.target_edit_keyboard(lang),
            )
            return

        if mode == "edit_slot":
            key = str(sess.get("target_key") or "")
            field = str(sess.get("field") or "")
            slot_index = int(sess.get("slot_index") or 0)
            if key not in TARGET_KEYS or field not in {
                "chat_id",
                "message_template",
                "schedule_times",
                "kind",
            }:
                await bot_settings.clear_session(uid)
                await _show_messages_hub(message, lang)
                return
            if field == "chat_id":
                ok = await _save_dest(
                    message,
                    uid=uid,
                    lang=lang,
                    target_key=key,
                    slot_index=slot_index,
                    value=text,
                )
                if not ok:
                    return
            else:
                value: Any = text
                if field == "kind":
                    kind = text.strip().lower()
                    if key == "support":
                        kind = "static"
                    if kind not in SLOT_KINDS:
                        await message.answer(
                            ak.msg("ask_slot_kind", lang),
                            reply_markup=ak.cancel_keyboard(lang),
                        )
                        return
                    value = kind
                await bot_settings.update_slot(key, slot_index, **{field: value})
            updated = await bot_settings.get_target(key)
            await audit.write(
                "update_message_slot",
                admin_id=uid,
                detail=f"Updated {field} for {key} slot {slot_index}",
                meta={"target": key, "slot": slot_index, "field": field},
            )
            await bot_settings.set_session(
                uid, {"mode": "slot", "target_key": key, "slot_index": slot_index}
            )
            await message.answer(ak.msg("saved_ok", lang))
            await _show_slot(message, bot_settings, key, slot_index, lang)
            return

        if mode == "scoped_rules_ai":
            key = str(sess.get("target_key") or "")
            slot_index = int(sess.get("slot_index") or 0)
            if key not in TARGET_KEYS or ai is None:
                await bot_settings.clear_session(uid)
                await _show_messages_hub(message, lang)
                return
            target = await bot_settings.get_target(key)
            slot = target.slot(slot_index)
            new_rules = text
            wants_ai = any(
                w in text.lower()
                for w in ("بساز", "عوض", "تغییر", "rewrite", "change", "update", "make")
            ) or len(text) < 200
            if wants_ai:
                prompt = (
                    f"You edit ONLY the rules_prompt for destination={key} slot={slot_index + 1} "
                    f"(kind={slot.kind}). Do not change creator contact or other bot sections.\n"
                    f"Current rules:\n{slot.rules_prompt or '(empty)'}\n\n"
                    f"Admin request:\n{text}\n\n"
                    "Return ONLY the new rules_prompt text (no markdown, no commentary)."
                )
                try:
                    answer = await ai.chat(
                        [
                            {
                                "role": "system",
                                "content": "You are a settings assistant. Output only the updated rules prompt.",
                            },
                            {"role": "user", "content": prompt},
                        ]
                    )
                    answer = strip_reasoning_leak(answer)
                    if answer and not looks_like_reasoning_leak(answer):
                        new_rules = answer.strip()
                except AIClientError as exc:
                    logger.exception("scoped rules AI failed: %s", exc)
            await bot_settings.update_slot(key, slot_index, rules_prompt=new_rules)
            await audit.write(
                "update_slot_rules_ai",
                admin_id=uid,
                detail=f"Rules updated via AI for {key}/{slot_index}",
                meta={"target": key, "slot": slot_index},
            )
            await bot_settings.set_session(
                uid, {"mode": "slot", "target_key": key, "slot_index": slot_index}
            )
            await message.answer(ak.msg("saved_ok", lang))
            await _show_slot(message, bot_settings, key, slot_index, lang)
            return

        if mode in {"bot_config_chat", "product_ai_chat"}:
            if ai is None:
                await message.answer("AI unavailable.")
                return
            lowered = text.lower()
            if any(k in lowered for k in ("سازنده", "creator_contact", "creator contact")):
                await message.answer(ak.msg("creator_locked", lang))
                return

            # Deterministic status card (readable; no raw dict dump / link preview).
            stripped = text.strip()
            wants_status = stripped.lower() in {
                "وضعیت",
                "status",
                "show status",
                "current status",
                "وضعیت فعلی",
                "نمایش وضعیت",
                "وضعیت تنظیمات",
            } or any(
                x in text
                for x in (
                    "نمایش وضعیت",
                    "وضعیت تنظیمات",
                    "show status",
                    "current status",
                )
            )
            if wants_status:
                from src.bot_config_apply import build_human_status

                body = await build_human_status(bot_settings, lang=lang)
                await message.answer(
                    body[:3900],
                    reply_markup=ak.cancel_keyboard(lang),
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
                )
                return

            # Deterministic UI layout requests (do not depend on model inventing menus).
            # Avoid treating "کلید بساز" as a layout request.
            is_button_mgmt = any(
                x in text
                for x in (
                    "کلید بساز",
                    "دکمه بساز",
                    "حذف کلید",
                    "پاک کردن کلید",
                    "برگرداندن کلید",
                    "بازگردانی کلید",
                    "لیست کلید",
                    "add button",
                    "create button",
                    "remove button",
                    "delete button",
                    "restore button",
                    "list button",
                )
            )
            wants_two_cols = (not is_button_mgmt) and (
                any(
                    x in text
                    for x in ("دو ردیف", "دو ستون", "2 ستون", "2 ردیف", "two row", "two column")
                )
                or (
                    any(x in text for x in ("کوچیک", "کوچک", "compact", "small"))
                    and any(
                        x in text
                        for x in ("کلید", "دکمه", "کیبورد", "تنظیمات", "button", "keyboard")
                    )
                )
            )
            wants_one_col = any(
                x in text for x in ("یک ردیف", "تک ستون", "1 ستون", "one column", "single column")
            )
            if wants_two_cols or wants_one_col:
                cols = 1 if wants_one_col and not wants_two_cols else 2
                ui = await bot_settings.update_ui_settings(settings_columns=cols)
                ak.set_settings_columns(int(ui["settings_columns"]))
                await audit.write(
                    "bot_config_chat_apply",
                    admin_id=uid,
                    detail=f"ui.settings_columns={ui['settings_columns']}",
                )
                await bot_settings.set_session(uid, {"mode": "settings"})
                msg = (
                    f"ظاهر کیبورد تنظیمات روی {ui['settings_columns']} ستون تنظیم شد.\n"
                    "اندازه دقیق دکمه‌ها را تلگرام مشخص می‌کند؛ با دو ستون معمولاً جمع‌وجورتر دیده می‌شوند."
                    if lang.startswith("fa")
                    else (
                        f"Settings keyboard set to {ui['settings_columns']} column(s).\n"
                        "Telegram controls exact button width; two columns usually look more compact."
                    )
                )
                await message.answer(msg, reply_markup=await _settings_kb(lang, bot_settings))
                return

            # Deterministic custom button add/remove/list (Persian + English cues).
            wants_list_buttons = any(
                x in text for x in ("لیست کلید", "کلیدهای سفارشی", "list button", "list custom")
            )
            wants_remove_button = any(
                x in text for x in ("حذف کلید", "پاک کردن کلید", "remove button", "delete button")
            )
            wants_add_button = any(
                x in text
                for x in ("کلید بساز", "دکمه بساز", "اضافه کردن کلید", "add button", "create button")
            )
            if wants_list_buttons:
                from src.generated.buttons import list_generated_buttons
                from src.ui.system_layout import list_system_buttons_brief

                gen_items = list_generated_buttons(menu="settings", refresh=True)
                cat_items = await bot_settings.list_custom_buttons(menu="settings")
                lines: list[str] = []
                lines.append(
                    "—— کلیدهای سیستم (قابل حذف با safe-change؛ 🔒 قفل) ——"
                    if lang.startswith("fa")
                    else "—— System buttons (safe-change; 🔒 locked) ——"
                )
                lines.append(list_system_buttons_brief(labels_table=ak._LABELS))
                if gen_items:
                    lines.append("—— کلیدهای کدنویسی‌شده (AI) ——" if lang.startswith("fa") else "—— AI-coded buttons ——")
                    for b in gen_items:
                        lines.append(
                            f"• {b.get('id')}: {b.get('label_fa') or b.get('label_en')} [generated]"
                        )
                if cat_items:
                    lines.append("—— کلیدهای کاتالوگ ——" if lang.startswith("fa") else "—— Catalog buttons ——")
                    for b in cat_items:
                        lines.append(
                            f"• {b.get('id')}: {b.get('label_fa') or b.get('label_en')} → {b.get('action')}"
                        )
                body = "\n".join(lines)
                await message.answer(body[:3900], reply_markup=ak.cancel_keyboard(lang))
                return
            if wants_remove_button:
                from src.button_codegen import queue_generated_button_remove
                from src.generated.buttons import list_generated_buttons
                from src.ui.system_layout import (
                    match_system_button,
                    queue_system_button_change,
                    resolve_menu_hint,
                )

                bid = ""
                label = ""
                for token in text.replace("،", " ").split():
                    if token.startswith("id=") or token.startswith("btn_") or token.startswith("cb_"):
                        bid = token.split("=", 1)[-1].strip()
                for cue in ("حذف کلید", "پاک کردن کلید", "remove button", "delete button"):
                    if cue in text:
                        label = text.split(cue, 1)[-1].strip(" :-")
                        break
                # Prefer generated registry removal via safe-change
                gen_hit = None
                for b in list_generated_buttons(menu=None, refresh=True):
                    labs = {str(b.get("label_fa") or "").strip(), str(b.get("label_en") or "").strip()}
                    if (bid and str(b.get("id") or "") == bid) or (label and label in labs):
                        gen_hit = b
                        break
                if gen_hit:
                    result = queue_generated_button_remove(
                        button_id=str(gen_hit.get("id") or ""),
                        label=str(gen_hit.get("label_fa") or ""),
                        description=f"Remove generated button {gen_hit.get('id')}",
                        admin_chat_id=uid,
                    )
                    if not result.get("ok"):
                        await message.answer(
                            f"❌ {result.get('error')}",
                            reply_markup=ak.cancel_keyboard(lang),
                        )
                        return
                    await audit.write(
                        "generated_button_remove_queued",
                        admin_id=uid,
                        detail=str(result.get("change_id")),
                    )
                    await message.answer(
                        (
                            "🛡 حذف کلید در صف safe-change قرار گرفت.\n"
                            f"change: `{result.get('change_id')}`\n"
                            "ربات ری‌استارت می‌شود؛ حدود ۱ دقیقه فرصت چک دارید، بعد پیام تأیید می‌آید."
                            if lang.startswith("fa")
                            else (
                                "🛡 Button removal queued via safe-change.\n"
                                f"change: `{result.get('change_id')}`\n"
                                "Bot will restart; ~1 minute observe, then confirm prompt."
                            )
                        ),
                        reply_markup=ak.cancel_keyboard(lang),
                    )
                    return
                removed = await bot_settings.remove_custom_button(button_id=bid, label=label)
                if removed:
                    await audit.write(
                        "custom_button_remove",
                        admin_id=uid,
                        detail=str(removed.get("id")),
                    )
                    await bot_settings.set_session(uid, {"mode": "settings"})
                    await message.answer(
                        ("✅ کلید حذف شد: " if lang.startswith("fa") else "✅ Removed: ")
                        + str(removed.get("label_fa") or removed.get("id")),
                        reply_markup=await _settings_kb(lang, bot_settings),
                    )
                    return
                # System / hardcoded buttons (e.g. وضعیت سلامت on آمار)
                menu_hint = resolve_menu_hint(text)
                sys_hit = match_system_button(
                    label=label,
                    button_id=bid,
                    menu=menu_hint,
                    labels_table=ak._LABELS,
                )
                if sys_hit:
                    action_id, menu = sys_hit
                    result = queue_system_button_change(
                        op="remove",
                        action=action_id,
                        menu=menu,
                        description=f"Remove system button {action_id} from {menu}",
                        admin_chat_id=uid,
                    )
                    if not result.get("ok"):
                        await message.answer(
                            f"❌ {result.get('error')}",
                            reply_markup=ak.cancel_keyboard(lang),
                        )
                        return
                    await audit.write(
                        "system_button_remove_queued",
                        admin_id=uid,
                        detail=f"{action_id}@{menu}:{result.get('change_id')}",
                    )
                    await message.answer(
                        (
                            f"🛡 حذف کلید سیستم `{action_id}` از منوی `{menu}` در صف safe-change است.\n"
                            f"change: `{result.get('change_id')}`\n"
                            "ربات ری‌استارت می‌شود؛ حدود ۱ دقیقه فرصت چک دارید، بعد پیام تأیید می‌آید.\n"
                            "اگر خراب شد و تأیید نکنید، خودکار برمی‌گردد."
                            if lang.startswith("fa")
                            else (
                                f"🛡 System button `{action_id}` removal from `{menu}` queued.\n"
                                f"change: `{result.get('change_id')}`\n"
                                "Bot restarts; ~1 min observe, then confirm. No confirm → rollback."
                            )
                        ),
                        reply_markup=ak.cancel_keyboard(lang),
                    )
                    return
                await message.answer(
                    "کلیدی پیدا نشد. id یا متن دکمه را بفرستید (مثلاً: حذف کلید وضعیت سلامت از آمار)."
                    if lang.startswith("fa")
                    else "Button not found. Send id or label (e.g. delete button Health Status from stats).",
                    reply_markup=ak.cancel_keyboard(lang),
                )
                return
            # Restore system button
            wants_restore_button = any(
                x in text
                for x in ("برگرداندن کلید", "بازگردانی کلید", "restore button", "undelete button")
            )
            if wants_restore_button:
                from src.ui.system_layout import (
                    match_system_button,
                    queue_system_button_change,
                    resolve_menu_hint,
                )

                label = ""
                for cue in (
                    "برگرداندن کلید",
                    "بازگردانی کلید",
                    "restore button",
                    "undelete button",
                ):
                    if cue in text:
                        label = text.split(cue, 1)[-1].strip(" :-")
                        break
                menu_hint = resolve_menu_hint(text)
                sys_hit = match_system_button(
                    label=label,
                    menu=menu_hint,
                    labels_table=ak._LABELS,
                )
                if not sys_hit:
                    await message.answer(
                        "کلید سیستم پیدا نشد."
                        if lang.startswith("fa")
                        else "System button not found.",
                        reply_markup=ak.cancel_keyboard(lang),
                    )
                    return
                action_id, menu = sys_hit
                result = queue_system_button_change(
                    op="restore",
                    action=action_id,
                    menu=menu,
                    description=f"Restore system button {action_id} on {menu}",
                    admin_chat_id=uid,
                )
                if not result.get("ok"):
                    await message.answer(
                        f"❌ {result.get('error')}",
                        reply_markup=ak.cancel_keyboard(lang),
                    )
                    return
                await message.answer(
                    (
                        f"🛡 بازگردانی `{action_id}` روی `{menu}` در صف safe-change است.\n"
                        f"change: `{result.get('change_id')}`"
                        if lang.startswith("fa")
                        else (
                            f"🛡 Restore `{action_id}` on `{menu}` queued.\n"
                            f"change: `{result.get('change_id')}`"
                        )
                    ),
                    reply_markup=ak.cancel_keyboard(lang),
                )
                return
            if wants_add_button:
                # Explicit catalog shortcut: action=run_health_now etc.
                has_catalog_action = "action=" in text
                if has_catalog_action:
                    label_fa = ""
                    action_name = "noop_confirm"
                    params: dict[str, Any] = {}
                    chunk = text
                    for cue in ("کلید بساز", "دکمه بساز", "اضافه کردن کلید", "add button", "create button"):
                        if cue in chunk:
                            chunk = chunk.split(cue, 1)[-1].strip(" :-")
                            break
                    parts = chunk.replace("—", " ").replace("–", " ").split()
                    label_bits: list[str] = []
                    for part in parts:
                        if part.startswith("action="):
                            action_name = part.split("=", 1)[1].strip()
                        elif "=" in part and part.split("=", 1)[0] in {
                            "target",
                            "slot",
                            "text",
                            "menu",
                        }:
                            k, v = part.split("=", 1)
                            params[k] = v
                        else:
                            label_bits.append(part)
                    label_fa = " ".join(label_bits).strip().strip("\"'«»")
                    if label_fa and action_name in ALLOWED_ACTIONS:
                        try:
                            created = await bot_settings.add_custom_button(
                                {
                                    "id": new_button_id(),
                                    "menu": str(params.pop("menu", "settings") or "settings"),
                                    "label_fa": label_fa,
                                    "label_en": label_fa,
                                    "enabled": True,
                                    "action": action_name,
                                    "params": params,
                                    "order": 50,
                                }
                            )
                        except ValueError as exc:
                            await message.answer(f"❌ {exc}", reply_markup=ak.cancel_keyboard(lang))
                            return
                        await audit.write(
                            "custom_button_add",
                            admin_id=uid,
                            detail=f"{created.get('id')}:{created.get('action')}",
                        )
                        await bot_settings.set_session(uid, {"mode": "settings"})
                        await message.answer(
                            (
                                "✅ کلید کاتالوگ ساخته شد:\n"
                                if lang.startswith("fa")
                                else "✅ Catalog button created:\n"
                            )
                            + f"{created.get('label_fa')} → {created.get('action')} ({created.get('id')})",
                            reply_markup=await _settings_kb(lang, bot_settings),
                        )
                        return

                # Default: AI writes real Python code → safe-change watchdog (~1 min).
                from src.button_codegen import (
                    build_codegen_user_prompt,
                    codegen_system_prompt,
                    extract_python_block,
                    guess_labels_from_request,
                    guess_menu_from_request,
                    new_generated_id,
                    queue_generated_button_add,
                    validate_generated_button_source,
                )

                if ai is None:
                    await message.answer("AI unavailable.", reply_markup=ak.cancel_keyboard(lang))
                    return
                button_id = new_generated_id()
                label_fa, label_en = guess_labels_from_request(text)
                menu_target = guess_menu_from_request(text)
                await message.answer(
                    "⏳ در حال کدنویسی کلید با AI…"
                    if lang.startswith("fa")
                    else "⏳ Generating button code with AI…"
                )
                vision_note = ""
                pending_imgs: list[bytes] = []
                for p in list(sess.get("config_chat_images") or [])[-4:]:
                    try:
                        pending_imgs.append(Path(p).read_bytes())
                    except OSError:
                        continue
                try:
                    sys_p = codegen_system_prompt()
                    user_p = build_codegen_user_prompt(
                        admin_request=text,
                        button_id=button_id,
                        label_fa=label_fa,
                        label_en=label_en,
                        lang=lang,
                    ) + f"\nTarget menu for this button: {menu_target}\n"
                    if pending_imgs:
                        answer = await ai.chat_with_images(
                            user_p
                            + "\nUse the attached screenshot(s) to understand UI context and implement the button accordingly.",
                            pending_imgs,
                            system=sys_p,
                            max_images=4,
                        )
                        vision_note = "+vision"
                    else:
                        answer = await ai.chat(
                            [
                                {"role": "system", "content": sys_p},
                                {"role": "user", "content": user_p},
                            ]
                        )
                except AIClientError as exc:
                    await message.answer(f"❌ {exc}", reply_markup=ak.cancel_keyboard(lang))
                    return
                source = extract_python_block(strip_reasoning_leak(answer or ""))
                ok_src, detail = validate_generated_button_source(source, button_id=button_id)
                if not ok_src:
                    await message.answer(
                        (
                            f"❌ کد تولیدشده معتبر نبود: {detail}\n"
                            "دوباره با توضیح واضح‌تر بخواهید. برای نام کوتاه بنویسید: به نام «لیست کاربران»"
                            if lang.startswith("fa")
                            else f"❌ Invalid generated code: {detail}"
                        ),
                        reply_markup=ak.cancel_keyboard(lang),
                    )
                    return
                result = queue_generated_button_add(
                    button_id=button_id,
                    label_fa=label_fa,
                    label_en=label_en,
                    source=source,
                    menu=menu_target,
                    description=f"AI button: {label_fa}@{menu_target}{vision_note}",
                    admin_chat_id=uid,
                )
                if not result.get("ok"):
                    await message.answer(
                        f"❌ {result.get('error')}",
                        reply_markup=ak.cancel_keyboard(lang),
                    )
                    return
                await audit.write(
                    "generated_button_add_queued",
                    admin_id=uid,
                    detail=f"{button_id}:{result.get('change_id')}",
                )
                if pending_imgs:
                    sess["config_chat_images"] = []
                    await bot_settings.set_session(uid, sess)
                await message.answer(
                    (
                        "🛡 کلید با کد AI در صف safe-change قرار گرفت.\n"
                        f"id: `{button_id}`\n"
                        f"change: `{result.get('change_id')}`\n"
                        f"برچسب: {label_fa}\n\n"
                        "ربات ری‌استارت می‌شود، حدود ۱ دقیقه فرصت تست دارید، "
                        "بعد پیام تأیید می‌آید. اگر تأیید نشود، خودکار برمی‌گردد."
                        if lang.startswith("fa")
                        else (
                            "🛡 AI-coded button queued via safe-change.\n"
                            f"id: `{button_id}`\n"
                            f"change: `{result.get('change_id')}`\n"
                            f"label: {label_fa}\n\n"
                            "Bot restarts, ~1 minute observe, then confirm. "
                            "No confirm → auto rollback."
                        )
                    ),
                    reply_markup=ak.cancel_keyboard(lang),
                )
                return

            from src.bot_config_apply import (
                apply_operator_lines,
                build_full_state_brief,
                operator_command_help,
                operator_system_prompt,
                strip_apply_lines,
            )

            state_brief = await build_full_state_brief(bot_settings)
            prompt = (
                f"{operator_system_prompt()}\n"
                f"CURRENT STATE:\n{state_brief}\n\n"
                f"{operator_command_help()}\n"
                f"Admin language hint: {lang}\n"
                f"Admin request: {text}"
            )
            pending_imgs: list[bytes] = []
            for p in list(sess.get("config_chat_images") or [])[-4:]:
                try:
                    pending_imgs.append(Path(p).read_bytes())
                except OSError:
                    continue
            try:
                sys_op = (
                    "Full settings operator. Edit any existing section via APPLY_*/OPEN_SECTION. "
                    "No fake menus. If screenshots are attached, use what you see in them."
                )
                if pending_imgs:
                    answer = await ai.chat_with_images(
                        prompt
                        + "\n\nUse the attached screenshot(s) as context for the admin request.",
                        pending_imgs,
                        system=sys_op,
                        max_images=4,
                    )
                    # Consume images after one successful vision turn.
                    sess["config_chat_images"] = []
                    await bot_settings.set_session(uid, sess)
                else:
                    answer = await ai.chat(
                        [
                            {"role": "system", "content": sys_op},
                            {"role": "user", "content": prompt},
                        ]
                    )
            except AIClientError as exc:
                await message.answer(f"❌ {exc}", reply_markup=ak.cancel_keyboard(lang))
                return
            answer = strip_reasoning_leak(answer)
            result = await apply_operator_lines(
                (answer or "").splitlines(),
                bot_settings=bot_settings,
                message_bot=message.bot,
                allowed_catalog_actions=ALLOWED_ACTIONS,
                lang=lang,
            )
            clean = strip_apply_lines(answer or "")
            if result.status_dump:
                # Drop model chatter when admin only asked for status.
                if not result.applied and not result.errors and not result.open_section:
                    clean = result.status_dump
                else:
                    clean = (
                        (clean + "\n\n" + result.status_dump)
                        if clean
                        else result.status_dump
                    )
            if result.applied:
                clean = (
                    clean
                    + (
                        "\n\n✅ اعمال شد: "
                        if lang.startswith("fa")
                        else "\n\n✅ Applied: "
                    )
                    + ", ".join(result.applied)
                ).strip()
                await audit.write(
                    "bot_config_chat_apply",
                    admin_id=uid,
                    detail=", ".join(result.applied)[:500],
                )
            if result.errors:
                clean = (
                    clean
                    + (
                        "\n⚠️ "
                        if lang.startswith("fa")
                        else "\n⚠ "
                    )
                    + "; ".join(result.errors)
                ).strip()

            if result.safe_change_queued and result.safe_change_queued.get("ok"):
                cid = result.safe_change_queued.get("change_id")
                clean = (
                    (
                        f"{clean}\n\n🛡 تغییر در صف safe-change است.\n"
                        f"change: `{cid}`\n"
                        "ربات ری‌استارت می‌شود؛ حدود ۱ دقیقه فرصت چک دارید."
                        if lang.startswith("fa")
                        else (
                            f"{clean}\n\n🛡 Change queued via safe-change.\n"
                            f"change: `{cid}`\n"
                            "Bot restarts; ~1 minute observe window."
                        )
                    )
                ).strip()
                await message.answer(clean[:3900] or "✅", reply_markup=ak.cancel_keyboard(lang))
                return

            # Navigate to requested section when possible.
            if result.open_section:
                sec = result.open_section
                await bot_settings.set_session(uid, {"mode": sec if sec != "account" else "target"})
                if sec == "settings":
                    await _show_settings_hub(message, lang, bot_settings)
                    return
                if sec == "owner":
                    await bot_settings.set_session(uid, {"mode": "owner"})
                    await _show_owner(message, bot_settings, lang)
                    return
                if sec == "messages":
                    await bot_settings.set_session(uid, {"mode": "messages_hub"})
                    await _show_messages_hub(message, lang)
                    return
                if sec == "panel":
                    await bot_settings.set_session(uid, {"mode": "panel"})
                    await _show_panel(message, bot_settings, lang)
                    return
                if sec == "health":
                    from src.health_report import build_health_report as _bhr

                    report = await _bhr(settings, bot_settings, lang=lang)
                    await bot_settings.set_session(uid, {"mode": "health"})
                    await message.answer(
                        ((clean + "\n\n") if clean else "") + report[:3500],
                        reply_markup=ak.health_keyboard(lang),
                    )
                    return
                if sec == "backup":
                    await bot_settings.set_session(uid, {"mode": "backup"})
                    await message.answer(
                        ((clean + "\n\n") if clean else "")
                        + ("💾 پشتیبان تنظیمات" if lang.startswith("fa") else "💾 Settings backup"),
                        reply_markup=ak.backup_keyboard(lang),
                    )
                    return
                if sec == "admins":
                    await bot_settings.set_session(uid, {"mode": "admins"})
                    await message.answer(
                        ((clean + "\n\n") if clean else "") + await _admins_card(lang),
                        reply_markup=ak.admins_keyboard(lang),
                    )
                    return
                if sec in {"channel", "group", "account", "test"}:
                    key = "support" if sec == "account" else sec
                    await bot_settings.set_session(uid, {"mode": "target", "target_key": key})
                    if clean:
                        await message.answer(clean[:3900])
                    await _show_target(message, bot_settings, key, lang)
                    return
                if sec == "creator":
                    creator = load_creator_contact(settings.knowledge_root)
                    await message.answer(
                        ((clean + "\n\n") if clean else "") + creator.format_card(lang),
                        reply_markup=await _settings_kb(lang, bot_settings),
                    )
                    return
                if sec == "control" and control is not None:
                    from src.handlers.admin_control import _show_control_home

                    await users.set_ask_ai(uid, False)
                    await control.registry.set_session(uid, {"mode": "control_home"})
                    if clean:
                        await message.answer(clean[:3900])
                    await _show_control_home(message, control, lang)
                    return

            if result.show_settings_keyboard:
                await bot_settings.set_session(uid, {"mode": "settings"})
                kb = await _settings_kb(lang, bot_settings)
            else:
                kb = ak.ai_chat_hub_keyboard(lang)
            await message.answer(
                (clean or ak.msg("saved_ok", lang))[:3900],
                reply_markup=kb,
                link_preview_options=LinkPreviewOptions(is_disabled=True),
            )
            return

        if mode == "edit_panel":
            field = str(sess.get("panel_field") or "")
            fields: dict[str, Any] = {}
            try:
                if field == "api_token":
                    fields["api_token"] = text
                elif field == "base_url":
                    fields["base_url"] = text
                elif field == "inbound_ids":
                    fields["inbound_ids"] = text
                else:
                    await message.answer(
                        "فیلد نامعتبر." if lang == "fa" else "Invalid field.",
                        reply_markup=ak.panel_edit_keyboard(lang),
                    )
                    return
            except ValueError:
                await message.answer(
                    (
                        "شناسه Inbound معتبر بفرستید (مثل 1 یا 1,2,5)."
                        if lang == "fa"
                        else "Send valid inbound ID(s), e.g. 1 or 1,2,5."
                    ),
                    reply_markup=ak.cancel_keyboard(lang),
                )
                return
            try:
                panel = await bot_settings.update_panel(**fields)
            except ValueError:
                await message.answer(
                    (
                        "شناسه Inbound معتبر بفرستید (مثل 1 یا 1,2,5)."
                        if lang == "fa"
                        else "Send valid inbound ID(s), e.g. 1 or 1,2,5."
                    ),
                    reply_markup=ak.cancel_keyboard(lang),
                )
                return
            await audit.write(
                "update_panel",
                admin_id=uid,
                detail=f"Updated panel.{field}",
                meta={"field": field},
            )
            await bot_settings.set_session(uid, {"mode": "panel"})
            await message.answer(ak.msg("saved_ok", lang))
            await message.answer(
                bot_settings.format_panel_card(panel, lang=lang),
                reply_markup=ak.panel_edit_keyboard(lang),
            )
            return

    return router
