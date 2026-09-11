"""/start /menu /help /lang — language picker via reply keyboard."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import BotCommand, Message

from src.access import AdminAccess
from src.config import Settings, is_bot_admin
from src.storage.metrics import MetricsStore
from src.storage.users import UserStore
from src.ui import keyboards, media, messaging, texts

router = Router(name="start")

BOT_COMMANDS: list[BotCommand] = [
    BotCommand(command="start", description="Start / choose language"),
    BotCommand(command="menu", description="Main menu"),
    BotCommand(command="help", description="Help"),
    BotCommand(command="lang", description="Change language"),
]

# Shown only to admin private chats (never in the public slash menu).
BOT_COMMANDS_ADMIN: list[BotCommand] = [
    BotCommand(command="agents", description="Admin: list agents"),
    BotCommand(command="active_agent", description="Admin: active agent"),
    BotCommand(command="failover", description="Admin: failover status"),
    BotCommand(command="safety_status", description="Admin: safe-change status"),
    BotCommand(command="catalog_scan", description="Admin: rescan VPS to VPN catalog"),

BOT_COMMANDS_FA: list[BotCommand] = [
    BotCommand(command="start", description="شروع / انتخاب زبان"),
    BotCommand(command="menu", description="منوی اصلی"),
    BotCommand(command="help", description="راهنما"),
    BotCommand(command="lang", description="تغییر زبان"),
]

BOT_COMMANDS_RU: list[BotCommand] = [
    BotCommand(command="start", description="Старт / выбор языка"),
    BotCommand(command="menu", description="Главное меню"),
    BotCommand(command="help", description="Справка"),
    BotCommand(command="lang", description="Сменить язык"),
]

BOT_COMMANDS_ZH: list[BotCommand] = [
    BotCommand(command="start", description="开始 / 选择语言"),
    BotCommand(command="menu", description="主菜单"),
    BotCommand(command="help", description="帮助"),
    BotCommand(command="lang", description="更改语言"),
]


def _uid(message: Message) -> int:
    return message.from_user.id if message.from_user else 0


def _telegram_lang(message: Message) -> str | None:
    return message.from_user.language_code if message.from_user else None


async def _picker_hint_lang(users: UserStore, message: Message) -> str:
    return await users.get_lang(_uid(message), _telegram_lang(message))


async def send_language_picker(message: Message, users: UserStore) -> None:
    hint = await _picker_hint_lang(users, message)
    await messaging.answer_with_media(
        message,
        texts.language_prompt(hint),
        image=media.language_picker_image(hint),
        reply_markup=keyboards.language_keyboard(),
    )


async def send_main_menu(
    message: Message,
    lang: str,
    *,
    users: UserStore | None = None,
    user_id: int = 0,
    settings: Settings | None = None,
    access: "AdminAccess | None" = None,
) -> None:
    if users is not None and user_id:
        await users.set_ask_ai(user_id, False)
    can_settings = False
    can_stats = False
    if access is not None and user_id:
        can_settings = await access.can_settings(user_id)
        can_stats = await access.can_stats(user_id)
    elif settings and user_id and is_bot_admin(settings, user_id):
        can_settings = True
        can_stats = True
    # No separate "Main menu / choose option" filler — welcome/catalog text is enough.
    await message.answer(
        texts.welcome_after_lang(lang),
        reply_markup=keyboards.main_menu_keyboard(
            lang,
            is_admin=can_settings or can_stats,
            can_settings=can_settings,
            can_stats=can_stats,
        ),
    )


async def send_welcome_flow(
    message: Message,
    lang: str,
    *,
    users: UserStore | None = None,
    user_id: int = 0,
    settings: Settings | None = None,
    access: AdminAccess | None = None,
) -> None:
    if users is not None and user_id:
        await users.set_ask_ai(user_id, False)
    can_settings = False
    can_stats = False
    if access is not None and user_id:
        can_settings = await access.can_settings(user_id)
        can_stats = await access.can_stats(user_id)
    elif settings and user_id and is_bot_admin(settings, user_id):
        can_settings = True
        can_stats = True
    await message.answer(
        texts.welcome_after_lang(lang),
        reply_markup=keyboards.main_menu_keyboard(
            lang,
            is_admin=can_settings or can_stats,
            can_settings=can_settings,
            can_stats=can_stats,
        ),
    )


def setup_start_router(
    users: UserStore,
    *,
    settings: Settings,
    metrics: MetricsStore,
    access: AdminAccess | None = None,
) -> Router:
    @router.message(CommandStart())
    async def cmd_start(message: Message) -> None:
        uid = _uid(message)
        await users.set_ask_ai(uid, False)
        await send_language_picker(message, users)

    @router.message(Command("menu"))
    async def cmd_menu(message: Message) -> None:
        uid = _uid(message)
        if not await users.has_lang(uid):
            await send_language_picker(message, users)
            return
        lang = await users.get_lang(uid, _telegram_lang(message))
        await send_main_menu(
            message,
            lang,
            users=users,
            user_id=uid,
            settings=settings,
            access=access,
        )

    @router.message(Command("help"))
    async def cmd_help(message: Message) -> None:
        uid = _uid(message)
        if not await users.has_lang(uid):
            await send_language_picker(message, users)
            return
        lang = await users.get_lang(uid, _telegram_lang(message))
        await message.answer(texts.help_text(lang))
        await send_main_menu(
            message,
            lang,
            users=users,
            user_id=uid,
            settings=settings,
            access=access,
        )

    @router.message(Command("lang"))
    async def cmd_lang(message: Message) -> None:
        await users.set_ask_ai(_uid(message), False)
        await send_language_picker(message, users)

    @router.message(F.text.in_(keyboards.all_lang_button_texts()))
    async def on_lang_button(message: Message) -> None:
        code = keyboards.resolve_lang_button(message.text)
        if not code or not message.from_user:
            return
        uid = message.from_user.id
        await users.touch_from_telegram_user(message.from_user)
        lang, is_new = await users.set_lang(uid, code)
        if is_new:
            await metrics.record_new_user()
        await users.set_ask_ai(uid, False)
        await message.answer(texts.t(texts.LANGUAGE_SELECTED, lang))
        await send_welcome_flow(
            message,
            lang,
            users=users,
            user_id=uid,
            settings=settings,
            access=access,
        )

    @router.message(Command("catalog_scan"))
    async def cmd_catalog_scan(message: Message) -> None:
        uid = _uid(message)
        if not uid or not is_bot_admin(settings, uid):
            await message.answer("Admin only.")
            return
        await message.answer("Scanning VPS to VPN source…")
        try:
            from src.knowledge.source_catalog.pipeline import run_sync

            payload = run_sync(
                settings.vps_to_vpn_source,
                settings.knowledge_root,
                settings.data_dir,
                force=True,
            )
        except Exception as exc:  # noqa: BLE001
            await message.answer(f"SCAN_ERROR: {exc}")
            return
        val = payload.get("validation") or {}
        st = payload.get("stats") or {}
        await message.answer(
            "Catalog scan done.\n"
            f"go_files={st.get('go_files')} ui={st.get('ui_prod_files')} "
            f"features={st.get('features')}\n"
            f"MISSING={val.get('missing')}\n"
            f"deprecated={val.get('deprecated')}\n"
            f"outdated={len(val.get('outdated') or [])}"
        )

    return router
