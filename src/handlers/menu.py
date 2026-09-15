"""Main menu via reply-keyboard button presses (below the input field)."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Filter
from aiogram.types import Message

from src.access import AdminAccess
from src.config import Settings, is_bot_admin
from src.handlers.start import send_language_picker, send_main_menu
from src.knowledge.product_catalogs import (
    feature_body,
    get_product,
    parse_feature_action,
    parse_product_action,
)
from src.ui.keyboards import parse_section_action
from src.ui.media import menu_image_path
from src.knowledge.catalog_index import catalog_photos_for
from src.storage.metrics import MetricsStore
from src.storage.users import UserStore
from src.ui import keyboards, messaging, texts

router = Router(name="menu")

Lang = str


class IsMenuButton(Filter):
    async def __call__(self, message: Message) -> bool:
        return keyboards.is_reserved_menu_text(message.text)


_MENU_INTROS: dict[str, dict[Lang, str]] = {
    "about": texts.INTRO_ABOUT,
    "install": texts.INTRO_INSTALL,
    "license": texts.INTRO_LICENSE,
    "connection": texts.INTRO_CONNECTION,
    "update": texts.INTRO_UPDATE,
    "server": texts.INTRO_SERVER,
    "mesh": texts.INTRO_MESH,
    "domain_cdn": texts.INTRO_DOMAIN_CDN,
}

_MODE_DETAILS: dict[str, dict[Lang, str]] = {
    "mode_basic": texts.MODE_DETAIL_BASIC,
    "mode_pro": texts.MODE_DETAIL_PRO,
    "mode_ai_pro": texts.MODE_DETAIL_AI_PRO,
}

_MENU_STATIC: dict[str, dict[Lang, str]] = {
    "buy_license": texts.BUY_LICENSE_CTA,
    "buy_vps": texts.BUY_VPS_CTA,
    "contact": texts.CONTACT_CTA,
}


def _with_ai_footer(body: str, lang: Lang) -> str:
    footer = texts.t(texts.MENU_ASK_AI_FOOTER, lang)
    if footer in body:
        return body
    return f"{body.rstrip()}\n\n{footer}"


def setup_menu_router(
    users: UserStore,
    *,
    settings: Settings,
    metrics: MetricsStore,
    access: AdminAccess | None = None,
    bot_settings=None,
    control=None,
) -> Router:
    @router.message(F.chat.type == "private", IsMenuButton())
    async def on_menu_button(message: Message) -> None:
        user = message.from_user
        if not user or not message.text:
            return

        uid = user.id
        await users.touch_from_telegram_user(user)
        if not await users.has_lang(uid):
            await send_language_picker(message, users)
            return

        lang = await users.get_lang(uid, user.language_code)
        current_product = await users.get_current_product(uid)
        action = keyboards.resolve_menu_action(
            message.text, lang, current_product_id=current_product
        )
        if not action:
            # Not a resolvable menu label — let other routers (Ask AI / admin) handle it.
            from aiogram.dispatcher.event.bases import SkipHandler

            raise SkipHandler()

        # Sticky Ask AI: stay until user explicitly leaves via home/lang/contact
        # or a product hub key. Feature/section/installer labels typed as text
        # must go to Ask AI, not steal the session.
        if await users.is_ask_ai(uid):
            from aiogram.dispatcher.event.bases import SkipHandler

            if action == "ask_ai":
                pass  # re-prompt below
            elif action in {"lang", "home", "contact"} or parse_product_action(action):
                pass  # intentional leave — handle below
            else:
                raise SkipHandler()

        if action == "lang":
            await users.set_ask_ai(uid, False)
            await send_language_picker(message, users)
            return

        if action == "home":
            await users.set_current_product(uid, None)
            await send_main_menu(
                message,
                lang,
                users=users,
                user_id=uid,
                settings=settings,
                access=access,
            )
            return

        async def _menu_kb():
            if access is not None:
                return keyboards.main_menu_keyboard(
                    lang,
                    can_settings=await access.can_settings(uid),
                    can_stats=await access.can_stats(uid),
                )
            admin = is_bot_admin(settings, uid)
            return keyboards.main_menu_keyboard(lang, is_admin=admin)

        # bot_stats / settings are handled by admin routers.
        if action in {"bot_stats", "settings"}:
            from aiogram.dispatcher.event.bases import SkipHandler

            raise SkipHandler()

        if action == "ask_ai":
            product_id = (
                await users.get_current_product(uid)
                or await users.get_ask_ai_product(uid)
            )
            if not product_id:
                await users.set_ask_ai(uid, False)
                await message.answer(
                    texts.t(texts.USE_MENU_OR_ASK_AI, lang),
                    reply_markup=await _menu_kb(),
                )
                return
            await users.set_ask_ai(uid, True, product_id=product_id)
            # Leave admin wizards so free-text Ask AI is never swallowed.
            try:
                if bot_settings is not None:
                    await bot_settings.clear_session(uid)
                if control is not None:
                    await control.registry.clear_session(uid)
            except Exception:  # noqa: BLE001
                pass
            product = get_product(product_id)
            title = product.label(lang) if product else product_id
            await message.answer(
                texts.ask_ai_prompt_for_product(lang, title),
                reply_markup=keyboards.ask_ai_keyboard(lang, product_id=product_id),
            )
            return

        await users.set_ask_ai(uid, False)

        if action == "contact":
            from src.branding import load_creator_contact

            creator = load_creator_contact(settings.knowledge_root)
            await users.set_current_product(uid, None)
            await message.answer(
                creator.format_card(lang),
                reply_markup=await _menu_kb(),
            )
            return

        # Smart Support Bot section headers
        sec = parse_section_action(action)
        if sec:
            pid, section = sec
            await users.set_current_product(uid, pid)
            labels = keyboards.catalog_section_labels(lang)
            title = labels.get(section, section)
            if (lang or "").startswith("fa"):
                body = (
                    f"{title}\n\n"
                    "کلیدهای همین بخش را بزن تا راهنما و عکس همان قسمت بیاید. "
                    "اگر یک قابلیت روی ربات و Expert با هم اثر دارد، داخل متن همان کلید نوشته شده است."
                )
            else:
                body = (
                    f"{title}\n\n"
                    "Tap a key in this section for its guide and photo. "
                    "Keys that affect both Bot and Expert say so in their text."
                )
            body = _with_ai_footer(body, lang)
            await message.answer(
                body,
                reply_markup=keyboards.catalog_section_keyboard(lang, pid, section),
            )
            return

        # Product hubs
        product_id = parse_product_action(action)
        if product_id:
            await users.set_current_product(uid, product_id)
            product = get_product(product_id)
            body = _with_ai_footer(
                product.menu_body(lang) if product else texts.t(texts.MAIN_MENU_HINT, lang),
                lang,
            )
            # All products (including VPS to VPN) use catalog feature keys.
            await messaging.answer_with_media(
                message,
                body,
                images=catalog_photos_for(settings.project_root, product_id),
                reply_markup=keyboards.catalog_product_keyboard(lang, product_id),
            )
            return

        # Catalog feature detail (Config Builder / Agent Bot)
        feat = parse_feature_action(action)
        if feat:
            pid, fid = feat
            product = get_product(pid)
            if product:
                feature = next(
                    (f for f in product.features if str(f.get("id")) == fid),
                    None,
                )
                if feature:
                    body = _with_ai_footer(feature_body(product, feature, lang), lang)
                    media = catalog_photos_for(
                        settings.project_root,
                        pid,
                        feature_id=fid,
                        media_slot=str(feature.get("media_slot") or "").strip(),
                    )
                    if media:
                        await messaging.answer_with_media(
                            message,
                            body,
                            images=media,
                        )
                    else:
                        await message.answer(body)
                    return
            await message.answer(
                texts.t(texts.MAIN_MENU_HINT, lang),
                reply_markup=await _menu_kb(),
            )
            return

        if action == "modes":
            body = _with_ai_footer(texts.t(texts.INTRO_MODES, lang), lang)
            await message.answer(body, reply_markup=keyboards.modes_keyboard(lang))
            return

        if action in _MODE_DETAILS:
            body = _with_ai_footer(texts.t(_MODE_DETAILS[action], lang), lang)
            await message.answer(body, reply_markup=keyboards.modes_keyboard(lang))
            return

        if action in _MENU_STATIC:
            body = _with_ai_footer(texts.t(_MENU_STATIC[action], lang), lang)
        elif action in _MENU_INTROS:
            body = _with_ai_footer(texts.t(_MENU_INTROS[action], lang), lang)
        else:
            body = texts.t(texts.MAIN_MENU_HINT, lang)

        image = menu_image_path(action, lang)
        images = [image] if image is not None else []

        # Installer topics stay inside installer hub keyboard
        if keyboards.is_installer_topic(action):
            if images:
                await messaging.answer_with_media(
                    message,
                    body,
                    images=images,
                    reply_markup=keyboards.installer_keyboard(lang),
                )
            else:
                await message.answer(body, reply_markup=keyboards.installer_keyboard(lang))
            return

        if images:
            await messaging.answer_with_media(
                message,
                body,
                images=images,
                reply_markup=await _menu_kb(),
            )
        else:
            await message.answer(
                body,
                reply_markup=await _menu_kb(),
            )

    return router
