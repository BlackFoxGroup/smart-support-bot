"""Reply keyboards (below the Telegram input field) for Black Fox support bot."""

from __future__ import annotations

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from src.knowledge.product_catalogs import (
    feature_action_id,
    feature_label,
    get_product,
    get_product_catalogs,
    parse_feature_action,
    parse_product_action,
    product_action_id,
)
from src.ui import texts

Lang = str

# Fixed language button labels (same in every UI chrome)
BTN_LANG_FA = "🇮🇷 فارسی"
BTN_LANG_EN = "🇬🇧 English"
BTN_LANG_RU = "🇷🇺 Русский"
BTN_LANG_ZH = "🇨🇳 中文"

LANG_BUTTON_TO_CODE: dict[str, Lang] = {
    BTN_LANG_FA: "fa",
    BTN_LANG_EN: "en",
    BTN_LANG_RU: "ru",
    BTN_LANG_ZH: "zh",
}

# Menu action → text table
_MENU_ACTION_TABLES: dict[str, dict[Lang, str]] = {
    "bot_stats": texts.MENU_BOT_STATS,
    "settings": texts.MENU_SETTINGS,
    "ask_ai": texts.MENU_ASK_AI,
    "modes": texts.MENU_MODES,
    "mode_basic": texts.MENU_MODE_BASIC,
    "mode_pro": texts.MENU_MODE_PRO,
    "mode_ai_pro": texts.MENU_MODE_AI_PRO,
    "about": texts.MENU_ABOUT,
    "install": texts.MENU_INSTALL,
    "license": texts.MENU_LICENSE,
    "connection": texts.MENU_CONNECTION,
    "update": texts.MENU_UPDATE,
    "server": texts.MENU_SERVER,
    "mesh": texts.MENU_MESH,
    "domain_cdn": texts.MENU_DOMAIN_CDN,
    "buy_license": texts.MENU_BUY_LICENSE,
    "buy_vps": texts.MENU_BUY_VPS,
    "contact": texts.MENU_CONTACT,
    "lang": texts.MENU_CHANGE_LANG,
    "home": texts.BACK_TO_MENU,
}

# Topics that live under VPN Installer (screenshots 2+3)
_INSTALLER_TOPIC_ACTIONS = (
    "modes",
    "about",
    "install",
    "license",
    "connection",
    "update",
    "server",
    "mesh",
    "domain_cdn",
    "buy_license",
    "buy_vps",
    "contact",
    "lang",
)


def _label(action: str, lang: Lang) -> str:
    return texts.t(_MENU_ACTION_TABLES[action], lang)


def language_keyboard() -> ReplyKeyboardMarkup:
    """Language picker under the input field."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=BTN_LANG_FA),
                KeyboardButton(text=BTN_LANG_EN),
            ],
            [
                KeyboardButton(text=BTN_LANG_RU),
                KeyboardButton(text=BTN_LANG_ZH),
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True,
        input_field_placeholder="Language / زبان",
    )


def main_menu_keyboard(
    lang: Lang,
    *,
    is_admin: bool = False,
    can_settings: bool | None = None,
    can_stats: bool | None = None,
) -> ReplyKeyboardMarkup:
    """Product catalogs on the main menu (Ask AI lives inside each product hub)."""
    rows: list[list[KeyboardButton]] = []
    for product in get_product_catalogs():
        rows.append([KeyboardButton(text=product.label(lang))])
    rows.append([KeyboardButton(text=_label("contact", lang))])
    show_settings = can_settings if can_settings is not None else is_admin
    show_stats = can_stats if can_stats is not None else is_admin
    if show_settings and show_stats:
        rows.append(
            [
                KeyboardButton(text=_label("bot_stats", lang)),
                KeyboardButton(text=_label("settings", lang)),
            ]
        )
    elif show_settings:
        rows.append([KeyboardButton(text=_label("settings", lang))])
    elif show_stats:
        rows.append([KeyboardButton(text=_label("bot_stats", lang))])
    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True,
        input_field_placeholder=texts.t(texts.MAIN_MENU_HINT, lang),
    )


def installer_keyboard(lang: Lang) -> ReplyKeyboardMarkup:
    """VPN Installer hub — Ask AI first, then topic buttons."""
    rows: list[list[KeyboardButton]] = [
        [KeyboardButton(text=_label("ask_ai", lang))],
        [KeyboardButton(text=_label("modes", lang))],
        [
            KeyboardButton(text=_label("about", lang)),
            KeyboardButton(text=_label("install", lang)),
        ],
        [
            KeyboardButton(text=_label("license", lang)),
            KeyboardButton(text=_label("connection", lang)),
        ],
        [
            KeyboardButton(text=_label("update", lang)),
            KeyboardButton(text=_label("server", lang)),
        ],
        [
            KeyboardButton(text=_label("mesh", lang)),
            KeyboardButton(text=_label("domain_cdn", lang)),
        ],
        [
            KeyboardButton(text=_label("buy_license", lang)),
            KeyboardButton(text=_label("buy_vps", lang)),
        ],
        [KeyboardButton(text=_label("home", lang))],
    ]
    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True,
        input_field_placeholder="VPN Installer",
    )


def _pair_feature_rows(product, feats: list, lang: Lang) -> list[list[KeyboardButton]]:
    rows: list[list[KeyboardButton]] = []
    i = 0
    while i < len(feats):
        left = feats[i]
        left_label = feature_label(product, left, lang)
        if i + 1 < len(feats):
            right = feats[i + 1]
            right_label = feature_label(product, right, lang)
            rows.append(
                [
                    KeyboardButton(text=left_label),
                    KeyboardButton(text=right_label),
                ]
            )
            i += 2
        else:
            rows.append([KeyboardButton(text=left_label)])
            i += 1
    return rows


def section_action_id(product_id: str, section: str) -> str:
    return f"psec:{product_id}:{section}"


def parse_section_action(action: str | None) -> tuple[str, str] | None:
    raw = (action or "").strip()
    if not raw.startswith("psec:"):
        return None
    parts = raw.split(":", 2)
    if len(parts) != 3:
        return None
    _, product_id, section = parts
    product_id = product_id.strip()
    section = section.strip()
    if not product_id or not section:
        return None
    return product_id, section


def catalog_section_labels(lang: Lang) -> dict[str, str]:
    if (lang or "").startswith("fa"):
        return {
            "bot": "📘 کاتالوگ ربات",
            "expert": "🧰 کاتالوگ Expert",
            "shared": "🔗 مشترک ربات و Expert",
        }
    return {
        "bot": "📘 Bot catalog",
        "expert": "🧰 Expert catalog",
        "shared": "🔗 Shared bot + Expert",
    }


def catalog_product_keyboard(lang: Lang, product_id: str) -> ReplyKeyboardMarkup:
    """Product hub root keyboard.

    Smart Support Bot shows only 4 main keys (Ask AI + 3 section hubs).
    Other products list Ask AI + all feature keys.
    """
    product = get_product(product_id)
    if product_id == "agent-bot":
        labels = catalog_section_labels(lang)
        rows: list[list[KeyboardButton]] = [
            [KeyboardButton(text=_label("ask_ai", lang))],
            [KeyboardButton(text=labels["bot"])],
            [KeyboardButton(text=labels["expert"])],
            [KeyboardButton(text=labels["shared"])],
            [KeyboardButton(text=_label("home", lang))],
        ]
        return ReplyKeyboardMarkup(
            keyboard=rows,
            resize_keyboard=True,
            one_time_keyboard=False,
            is_persistent=True,
            input_field_placeholder=product.label(lang) if product else "Product",
        )

    rows = [[KeyboardButton(text=_label("ask_ai", lang))]]
    if product:
        rows.extend(_pair_feature_rows(product, list(product.features or []), lang))
    rows.append([KeyboardButton(text=_label("home", lang))])
    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True,
        input_field_placeholder=product.label(lang) if product else "Product",
    )


def catalog_section_keyboard(lang: Lang, product_id: str, section: str) -> ReplyKeyboardMarkup:
    """Submenu for one Smart Support Bot section; back returns to product root (4 keys)."""
    product = get_product(product_id)
    labels = catalog_section_labels(lang)
    back = product.label(lang) if product else _label("home", lang)
    rows: list[list[KeyboardButton]] = [
        [KeyboardButton(text=_label("ask_ai", lang))],
    ]
    if product:
        feats = [
            f
            for f in (product.features or [])
            if isinstance(f, dict) and str(f.get("section") or "bot").strip() == section
        ]
        rows.extend(_pair_feature_rows(product, feats, lang))
    rows.append([KeyboardButton(text=back)])
    rows.append([KeyboardButton(text=_label("home", lang))])
    title = labels.get(section, section)
    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True,
        input_field_placeholder=title,
    )



def modes_keyboard(lang: Lang) -> ReplyKeyboardMarkup:
    """Modes submenu: Basic / Pro / AI Pro + back to Installer hub."""
    back = get_product("vpn-installer")
    back_label = back.label(lang) if back else _label("home", lang)
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=_label("mode_basic", lang))],
            [KeyboardButton(text=_label("mode_pro", lang))],
            [KeyboardButton(text=_label("mode_ai_pro", lang))],
            [KeyboardButton(text=back_label)],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True,
        input_field_placeholder=texts.t(texts.MENU_MODES, lang),
    )


def ask_ai_keyboard(
    lang: Lang,
    *,
    product_id: str | None = None,
) -> ReplyKeyboardMarkup:
    """While in Ask AI mode: Ask AI + optional product hub + back to main."""
    rows: list[list[KeyboardButton]] = [
        [KeyboardButton(text=_label("ask_ai", lang))],
    ]
    if product_id:
        product = get_product(product_id)
        if product:
            rows.append([KeyboardButton(text=product.label(lang))])
    rows.append([KeyboardButton(text=_label("home", lang))])
    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True,
        input_field_placeholder="Ask Black Fox…",
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


def resolve_lang_button(text: str | None) -> Lang | None:
    if not text:
        return None
    return LANG_BUTTON_TO_CODE.get(text.strip())


def resolve_menu_action(
    text: str | None,
    lang: Lang,
    *,
    current_product_id: str | None = None,
) -> str | None:
    """Map a reply-keyboard press to menu action for the user's language.

    When the user is inside a product hub, that product's feature labels win
    over same-looking global menu labels and other product catalogs.
    """
    if not text:
        return None
    needle = text.strip()
    current = (current_product_id or "").strip()

    # Section headers inside Smart Support Bot
    for code in texts.SUPPORTED:
        labels = catalog_section_labels(code)
        for section, title in labels.items():
            if title == needle:
                pid = current or "agent-bot"
                return section_action_id(pid, section)

    def _match_product_features(product) -> str | None:
        for feat in product.features or []:
            fid = str(feat.get("id") or "").strip()
            if not fid:
                continue
            for code in texts.SUPPORTED:
                if feature_label(product, feat, code) == needle:
                    return feature_action_id(product.product_id, fid)
        return None

    # 1) Prefer the open product hub (prevents Config Builder «تماس/تنظیمات» → VPS)
    if current:
        product = get_product(current)
        if product:
            hit = _match_product_features(product)
            if hit:
                return hit
            for code in texts.SUPPORTED:
                if product.label(code) == needle:
                    return product_action_id(product.product_id)

    # 2) Global menu labels (Ask AI / Home / installer topics / …)
    for action, table in _MENU_ACTION_TABLES.items():
        if texts.t(table, lang) == needle:
            return action
    for action, table in _MENU_ACTION_TABLES.items():
        for code in texts.SUPPORTED:
            if texts.t(table, code) == needle:
                return action

    # 3) Other product hubs + features
    for product in get_product_catalogs():
        if current and product.product_id == current:
            continue
        for code in texts.SUPPORTED:
            if product.label(code) == needle:
                return product_action_id(product.product_id)
        hit = _match_product_features(product)
        if hit:
            return hit
    return None


def all_lang_button_texts() -> frozenset[str]:
    return frozenset(LANG_BUTTON_TO_CODE.keys())


def all_menu_button_texts() -> frozenset[str]:
    labels: set[str] = set()
    for table in _MENU_ACTION_TABLES.values():
        for code in texts.SUPPORTED:
            labels.add(texts.t(table, code))
    for product in get_product_catalogs():
        for code in texts.SUPPORTED:
            labels.add(product.label(code))
            for feat in product.features or []:
                labels.add(feature_label(product, feat, code))
    return frozenset(labels)


def is_reserved_menu_text(text: str | None) -> bool:
    if not text:
        return False
    needle = text.strip()
    return needle in all_lang_button_texts() or needle in all_menu_button_texts()


def is_installer_topic(action: str | None) -> bool:
    return action in _INSTALLER_TOPIC_ACTIONS


__all__ = [
    "BTN_LANG_EN",
    "BTN_LANG_FA",
    "BTN_LANG_RU",
    "BTN_LANG_ZH",
    "LANG_BUTTON_TO_CODE",
    "all_lang_button_texts",
    "all_menu_button_texts",
    "ask_ai_keyboard",
    "catalog_product_keyboard",
    "installer_keyboard",
    "is_installer_topic",
    "is_reserved_menu_text",
    "language_keyboard",
    "main_menu_keyboard",
    "modes_keyboard",
    "parse_feature_action",
    "parse_product_action",
    "parse_section_action",
    "section_action_id",
    "catalog_section_labels",
    "catalog_section_keyboard",
    "remove_keyboard",
    "resolve_lang_button",
    "resolve_menu_action",
]
