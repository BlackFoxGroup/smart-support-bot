"""Centralized localized strings for Black Fox support bot UI."""

from __future__ import annotations

from typing import Final

from src.ai.persona import GROUP_URL, SITE_URL, SUPPORT_HANDLE
from src.branding import get_bot_display_name

Lang = str
SUPPORTED: Final[tuple[Lang, ...]] = ("fa", "en", "ru", "zh")

# ---------------------------------------------------------------------------
# Language picker
# ---------------------------------------------------------------------------

def language_prompt(lang: Lang) -> str:
    name = get_bot_display_name()
    table = {
        "fa": (
            f"به {name} خوش آمدید.\n\n"
            "لطفاً زبان خود را انتخاب کنید:\n"
            "🇮🇷 فارسی  |  🇬🇧 English  |  🇷🇺 Русский  |  🇨🇳 中文"
        ),
        "en": (
            f"Welcome to {name}.\n\n"
            "Please choose your language:\n"
            "🇮🇷 فارسی  |  🇬🇧 English  |  🇷🇺 Русский  |  🇨🇳 中文"
        ),
        "ru": (
            f"Добро пожаловать в {name}.\n\n"
            "Выберите язык:\n"
            "🇮🇷 فارسی  |  🇬🇧 English  |  🇷🇺 Русский  |  🇨🇳 中文"
        ),
        "zh": (
            f"欢迎使用 {name}。\n\n"
            "请选择语言：\n"
            "🇮🇷 فارسی  |  🇬🇧 English  |  🇷🇺 Русский  |  🇨🇳 中文"
        ),
    }
    return table.get(lang, table["en"])


# Backward-compatible mapping used by texts.t — rebuilt at call time via welcome helpers.
LANGUAGE_PROMPT: dict[Lang, str] = {
    "fa": "به ربات خوش آمدید.\n\nلطفاً زبان خود را انتخاب کنید:\n🇮🇷 فارسی  |  🇬🇧 English  |  🇷🇺 Русский  |  🇨🇳 中文",
    "en": "Welcome.\n\nPlease choose your language:\n🇮🇷 فارسی  |  🇬🇧 English  |  🇷🇺 Русский  |  🇨🇳 中文",
    "ru": "Добро пожаловать.\n\nВыберите язык:\n🇮🇷 فارسی  |  🇬🇧 English  |  🇷🇺 Русский  |  🇨🇳 中文",
    "zh": "欢迎。\n\n请选择语言：\n🇮🇷 فارسی  |  🇬🇧 English  |  🇷🇺 Русский  |  🇨🇳 中文",
}

LANGUAGE_SELECTED: dict[Lang, str] = {
    "fa": "✅ زبان روی فارسی تنظیم شد.",
    "en": "✅ Language set to English.",
    "ru": "✅ Язык установлен: русский.",
    "zh": "✅ 语言已设为中文。",
}


def welcome_after_lang(lang: Lang) -> str:
    name = get_bot_display_name()
    table = {
        "fa": (
            f"سلام! من دستیار {name} هستم.\n"
            "از منوی زیر کاتالوگ مورد نظر را انتخاب کنید."
        ),
        "en": (
            f"Hi! I'm the {name} assistant.\n"
            "Choose a catalog from the menu below."
        ),
        "ru": (
            f"Здравствуйте! Я помощник {name}.\n"
            "Выберите нужный каталог в меню ниже."
        ),
        "zh": (
            f"你好！我是 {name} 助手。\n"
            "请从下方菜单选择所需目录。"
        ),
    }
    return table.get(lang, table["en"])


WELCOME_AFTER_LANG: dict[Lang, str] = {
    "fa": "سلام! از منوی زیر موضوع را انتخاب کنید.",
    "en": "Hi! Pick a topic from the menu below.",
    "ru": "Здравствуйте! Выберите тему в меню.",
    "zh": "你好！请从下方菜单选择主题。",
}

NEED_LANGUAGE_FIRST: dict[Lang, str] = {
    "fa": "لطفاً ابتدا زبان خود را از دکمه‌های زیر انتخاب کنید.",
    "en": "Please choose your language using the buttons below first.",
    "ru": "Сначала выберите язык с помощью кнопок ниже.",
    "zh": "请先使用下方按钮选择语言。",
}

# ---------------------------------------------------------------------------
# Main menu
# ---------------------------------------------------------------------------

MAIN_MENU_TITLE: dict[Lang, str] = {
    "fa": "📋 منوی اصلی",
    "en": "📋 Main menu",
    "ru": "📋 Главное меню",
    "zh": "📋 主菜单",
}

MAIN_MENU_HINT: dict[Lang, str] = {
    "fa": "یک گزینه را از منو انتخاب کنید.",
    "en": "Choose an option from the menu.",
    "ru": "Выберите пункт меню.",
    "zh": "请从菜单中选择一项。",
}

MENU_ASK_AI: dict[Lang, str] = {
    "fa": "🤖 سوال از AI",
    "en": "🤖 Ask AI",
    "ru": "🤖 Спросить AI",
    "zh": "🤖 向 AI 提问",
}

MENU_PRODUCTS: dict[Lang, str] = {
    "fa": "📦 محصولات",
    "en": "📦 Products",
    "ru": "📦 Products",
    "zh": "📦 产品",
}

INTRO_PRODUCTS: dict[Lang, str] = {
    "fa": "یکی از محصولات Black Fox را انتخاب کنید. جزئیات از کاتالوگ رسمی خوانده می‌شود.",
    "en": "Pick a Black Fox product. Details come from the official product catalogs.",
    "ru": "Выберите продукт Black Fox. Подробности берутся из официальных каталогов.",
    "zh": "请选择一个 Black Fox 产品。详情来自官方产品目录。",
}

MENU_BOT_STATS: dict[Lang, str] = {
    "fa": "📊 آمار ربات",
    "en": "📊 Bot Stats",
    "ru": "📊 Статистика бота",
    "zh": "📊 机器人统计",
}

MENU_SETTINGS: dict[Lang, str] = {
    "fa": "⚙️ تنظیمات",
    "en": "⚙️ Settings",
    "ru": "⚙️ Settings",
    "zh": "⚙️ Settings",
}

MENU_MODES: dict[Lang, str] = {
    "fa": "🎛️ مدها (Modes)",
    "en": "🎛️ Modes",
    "ru": "🎛️ Modes",
    "zh": "🎛️ Modes",
}

MENU_MODE_BASIC: dict[Lang, str] = {
    "fa": "🟢 مد Basic",
    "en": "🟢 Basic",
    "ru": "🟢 Basic",
    "zh": "🟢 Basic",
}

MENU_MODE_PRO: dict[Lang, str] = {
    "fa": "🔵 مد Pro",
    "en": "🔵 Pro",
    "ru": "🔵 Pro",
    "zh": "🔵 Pro",
}

MENU_MODE_AI_PRO: dict[Lang, str] = {
    "fa": "🟣 مد AI Pro",
    "en": "🟣 AI Pro",
    "ru": "🟣 AI Pro",
    "zh": "🟣 AI Pro",
}

ASK_AI_PROMPT: dict[Lang, str] = {
    "fa": (
        "حالت سوال از AI فعال شد.\n\n"
        "سؤال‌های مربوط به همین دسته محصولی که انتخاب کرده‌اید پاسخ داده می‌شود.\n"
        "برای بازگشت، دکمه محصول یا «بازگشت به منو» را بزنید."
    ),
    "en": (
        "Ask AI mode is on.\n\n"
        "Questions are answered for the product category you selected.\n"
        "To leave, tap the product button or “Back to menu”."
    ),
    "ru": (
        "Режим «Спросить AI» включён.\n\n"
        "Ответы даются по выбранной вами категории продукта.\n"
        "Чтобы выйти, нажмите кнопку продукта или «Назад в меню»."
    ),
    "zh": (
        "已进入「向 AI 提问」模式。\n\n"
        "将针对您所选的产品分类回答问题。\n"
        "退出请点产品按钮或「返回菜单」。"
    ),
}


def ask_ai_prompt_for_product(lang: Lang, product_title: str) -> str:
    title = (product_title or "").strip() or "Black Fox"
    table = {
        "fa": (
            f"حالت سوال از AI برای «{title}» فعال شد.\n\n"
            "سؤال‌های مربوط به همین دسته محصول پاسخ داده می‌شود.\n"
            "برای بازگشت، دکمه همین محصول یا «بازگشت به منو» را بزنید."
        ),
        "en": (
            f"Ask AI is on for “{title}”.\n\n"
            "Questions are answered for this product category only.\n"
            "To leave, tap this product or “Back to menu”."
        ),
        "ru": (
            f"Режим Ask AI для «{title}» включён.\n\n"
            "Ответы — только по этой категории продукта.\n"
            "Выход: кнопка продукта или «Назад в меню»."
        ),
        "zh": (
            f"已为「{title}」开启 Ask AI。\n\n"
            "仅回答该产品分类相关问题。\n"
            "退出请点该产品或「返回菜单」。"
        ),
    }
    return table.get(lang, table["en"])


USE_MENU_OR_ASK_AI: dict[Lang, str] = {
    "fa": (
        "الان حالت سوال از AI فعال نیست.\n"
        "اول یک کاتالوگ محصول را باز کنید، سپس «سوال از AI» را بزنید."
    ),
    "en": (
        "Ask AI mode is not active.\n"
        "Open a product catalog first, then tap “Ask AI”."
    ),
    "ru": (
        "Режим «Спросить AI» не активен.\n"
        "Сначала откройте каталог продукта, затем нажмите «Спросить AI»."
    ),
    "zh": (
        "尚未进入「向 AI 提问」模式。\n"
        "请先打开产品目录，再点「向 AI 提问」。"
    ),
}

BACK_TO_MENU: dict[Lang, str] = {
    "fa": "📋 بازگشت به منو",
    "en": "📋 Back to menu",
    "ru": "📋 Назад в меню",
    "zh": "📋 返回菜单",
}

MENU_ABOUT: dict[Lang, str] = {
    "fa": "🦊 درباره محصول",
    "en": "🦊 About product",
    "ru": "🦊 О продукте",
    "zh": "🦊 关于产品",
}

MENU_INSTALL: dict[Lang, str] = {
    "fa": "⚙️ نصب و راه‌اندازی",
    "en": "⚙️ Install & setup",
    "ru": "⚙️ Установка",
    "zh": "⚙️ 安装与设置",
}

MENU_LICENSE: dict[Lang, str] = {
    "fa": "🔑 لایسنس و فعال‌سازی",
    "en": "🔑 License & activation",
    "ru": "🔑 Лицензия",
    "zh": "🔑 许可证与激活",
}

MENU_CONNECTION: dict[Lang, str] = {
    "fa": "🔗 اتصال (SSH/پنل/هاب)",
    "en": "🔗 Connection (SSH/panel/hub)",
    "ru": "🔗 Связь (SSH/панель/хаб)",
    "zh": "🔗 连接（SSH/面板/Hub）",
}

MENU_UPDATE: dict[Lang, str] = {
    "fa": "🔄 به‌روزرسانی",
    "en": "🔄 Updates",
    "ru": "🔄 Обновления",
    "zh": "🔄 更新",
}

MENU_SERVER: dict[Lang, str] = {
    "fa": "🖥️ سرور و Deploy",
    "en": "🖥️ Server & Deploy",
    "ru": "🖥️ Сервер и Deploy",
    "zh": "🖥️ 服务器与 Deploy",
}

MENU_MESH: dict[Lang, str] = {
    "fa": "🕸️ مانیتورینگ MESH",
    "en": "🕸️ MESH & Monitoring",
    "ru": "🕸️ MESH & мониторинг",
    "zh": "🕸️ MESH & 监控",
}

MENU_DOMAIN_CDN: dict[Lang, str] = {
    "fa": "🌐 دامنه و CDN",
    "en": "🌐 Domain & CDN",
    "ru": "🌐 Domain & CDN",
    "zh": "🌐 Domain & CDN",
}

MENU_BUY_LICENSE: dict[Lang, str] = {
    "fa": "🛒 خرید لایسنس",
    "en": "🛒 Buy license",
    "ru": "🛒 Купить лицензию",
    "zh": "🛒 购买许可证",
}

MENU_BUY_VPS: dict[Lang, str] = {
    "fa": "🖥 VPS (FoxNext Partners)",
    "en": "🖥 VPS (FoxNext Partners)",
    "ru": "🖥 VPS (FoxNext Partners)",
    "zh": "🖥 VPS (FoxNext Partners)",
}

MENU_CONTACT: dict[Lang, str] = {
    "fa": "🛠 تماس با سازنده",
    "en": "🛠 Contact Creator",
    "ru": "🛠 Связь с создателем",
    "zh": "🛠 联系开发者",
}

MENU_CHANGE_LANG: dict[Lang, str] = {
    "fa": "🌐 تغییر زبان",
    "en": "🌐 Change language",
    "ru": "🌐 Сменить язык",
    "zh": "🌐 更改语言",
}

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------

def help_text(lang: Lang) -> str:
    name = get_bot_display_name()
    table = {
        "fa": (
            f"من {name} هستم — پشتیبانی محصول VPS to VPN از Black Fox Group.\n\n"
            "• از منو کاتالوگ محصول را انتخاب کنید\n"
            "• داخل همان محصول، «سوال از AI» را بزنید (پاسخ‌ها برای همان دسته است)\n"
            "• برای منوی اصلی دستور /menu را بفرستید\n"
            "• برای تغییر زبان دستور /lang را بفرستید\n\n"
            f"وب‌سایت: {SITE_URL}\n"
            f"پشتیبانی: {SUPPORT_HANDLE}"
        ),
        "en": (
            f"I'm {name} — VPS to VPN product support by Black Fox Group.\n\n"
            "• Open a product catalog from the menu\n"
            "• Inside that product, tap Ask AI (answers stay in that category)\n"
            "• /menu — main menu\n"
            "• /lang — change language\n\n"
            f"Website: {SITE_URL}\n"
            f"Support: {SUPPORT_HANDLE}"
        ),
        "ru": (
            f"Я {name} — поддержка продукта VPS to VPN (Black Fox Group).\n\n"
            "• Откройте каталог продукта в меню\n"
            "• Внутри продукта нажмите «Спросить AI» (ответы по этой категории)\n"
            "• /menu — главное меню\n"
            "• /lang — сменить язык\n\n"
            f"Сайт: {SITE_URL}\n"
            f"Поддержка: {SUPPORT_HANDLE}"
        ),
        "zh": (
            f"我是 {name} — Black Fox Group 的 VPS to VPN 产品支持。\n\n"
            "• 从菜单打开产品目录\n"
            "• 在该产品内点「向 AI 提问」（仅回答该分类）\n"
            "• /menu — 主菜单\n"
            "• /lang — 更改语言\n\n"
            f"网站：{SITE_URL}\n"
            f"支持：{SUPPORT_HANDLE}"
        ),
    }
    return table.get(lang, table["en"])


# Backward-compatible alias (static snapshot; prefer help_text()).
HELP_TEXT: dict[Lang, str] = {
    "fa": help_text("fa"),
    "en": help_text("en"),
    "ru": help_text("ru"),
    "zh": help_text("zh"),
}

# ---------------------------------------------------------------------------
# Topic intros (menu help categories) — general overview only; no mode quotas
# ---------------------------------------------------------------------------

MENU_ASK_AI_FOOTER: dict[Lang, str] = {
    "fa": (
        "برای پرسش درباره همین دسته محصول، گزینه «سوال از AI» را بزنید؛ "
        "پاسخ‌ها مربوط به همین کاتالوگ خواهند بود."
    ),
    "en": (
        "To ask about this product category, tap “Ask AI”; "
        "answers stay scoped to this catalog."
    ),
    "ru": (
        "Чтобы спросить об этой категории продукта, нажмите «Спросить AI»; "
        "ответы относятся к этому каталогу."
    ),
    "zh": (
        "如需询问本产品分类，请点「向 AI 提问」；"
        "回答仅针对本目录。"
    ),
}

INTRO_ABOUT: dict[Lang, str] = {
    "fa": (
        "محصول Black Fox یک ابزار عملیاتی برای راه‌اندازی و مدیریت زیرساخت VPN روی VPS شماست "
        "(نه یک VPN مصرفی با دکمهٔ «وصل شو»).\n\n"
        "با آن می‌توانید پنل، اتصال سرورها، Mesh و خدمات مرتبط را از طریق نصب‌کننده ویندوز "
        "و اپ اندروید مدیریت کنید. مدهای کاری Basic و Pro و AI Pro در منوی مدها توضیح داده شده‌اند؛ "
        "برای آموزش گام‌به‌گام از AI بپرسید."
    ),
    "en": (
        "Black Fox is an operations toolkit for setting up and managing VPN infrastructure on your VPS "
        "(not a consumer “connect” VPN app).\n\n"
        "You can manage the panel, server links, mesh, and related services via the Windows installer "
        "and Android apps. Working modes Basic / Pro / AI Pro are summarized under Modes — "
        "ask AI for step-by-step guidance."
    ),
    "ru": (
        "Black Fox — операционный инструмент для развёртывания и управления VPN-инфраструктурой на вашем VPS "
        "(не бытовой VPN с кнопкой «подключить»).\n\n"
        "Через Windows Installer и Android можно управлять панелью, связью серверов, mesh и смежными сервисами. "
        "Режимы Basic / Pro / AI Pro кратко описаны в Modes — пошаговое обучение через AI."
    ),
    "zh": (
        "Black Fox 是用于在您的 VPS 上部署与管理 VPN 基础设施的操作工具"
        "（不是消费级“一键连接”VPN）。\n\n"
        "可通过 Windows 安装器与 Android 应用管理面板、服务器链路、Mesh 及相关服务。"
        "Basic / Pro / AI Pro 可在 Modes 中查看概述——分步教程请向 AI 提问。"
    ),
}

INTRO_INSTALL: dict[Lang, str] = {
    "fa": (
        "بخش نصب و راه‌اندازی برای شروع کار با برنامه است: "
        "انتخاب زبان/مد، ذخیره سرور مرکزی، اتصال SSH و اجرای نصب خودکار روی VPS."
    ),
    "en": (
        "Install & setup covers getting started: language/mode, saving the central server, "
        "Connect SSH, and automated install on your VPS."
    ),
    "ru": (
        "Установка и настройка — старт работы: язык/режим, сохранение центрального сервера, "
        "Connect SSH и автоматическая установка на VPS."
    ),
    "zh": (
        "安装与设置用于起步：语言/模式、保存中心服务器、Connect SSH，以及在 VPS 上自动安装。"
    ),
}

INTRO_LICENSE: dict[Lang, str] = {
    "fa": (
        "بخش لایسنس و فعال‌سازی برای ثبت کد و باز کردن امکانات برنامه است "
        "(از جمله سطوح Pro و AI Pro).\n\n"
        "قیمت و جزئیات خرید فقط از سایت و پشتیبانی اعلام می‌شود؛ اینجا قیمت نمی‌گوییم."
    ),
    "en": (
        "License & activation is where you register codes and unlock product features "
        "(including Pro and AI Pro tiers).\n\n"
        "Prices are only on the website / support — we don’t quote prices here."
    ),
    "ru": (
        "Лицензия и активация — регистрация кодов и открытие функций "
        "(включая уровни Pro и AI Pro).\n\n"
        "Цены только на сайте / в поддержке — здесь цены не называем."
    ),
    "zh": (
        "许可证与激活用于登记激活码并解锁功能（含 Pro / AI Pro）。\n\n"
        "价格仅以官网/支持账号为准，此处不报价。"
    ),
}

INTRO_CONNECTION: dict[Lang, str] = {
    "fa": (
        "بخش اتصال مربوط به دسترسی برنامه به سرور و سرویس‌هاست: "
        "اتصال SSH، پنل، هاب به‌روزرسانی و در صورت نیاز Proxy — "
        "نه دکمهٔ VPN مصرفی روی گوشی."
    ),
    "en": (
        "Connection covers how the app reaches your servers and services: "
        "SSH, panel, update hubs, and Proxy when needed — "
        "not a consumer VPN dial button."
    ),
    "ru": (
        "Связь — доступ приложения к серверам и сервисам: "
        "SSH, панель, хабы обновлений и при необходимости Proxy — "
        "не кнопка бытового VPN."
    ),
    "zh": (
        "连接部分涉及应用如何访问服务器与服务："
        "SSH、面板、更新 Hub，以及必要时的 Proxy——"
        "不是消费级 VPN 一键拨号。"
    ),
}

INTRO_UPDATE: dict[Lang, str] = {
    "fa": (
        "بخش به‌روزرسانی برای دریافت نسخهٔ جدید برنامه از هاب رسمی است "
        "تا امکانات و رفع اشکال‌ها اعمال شود."
    ),
    "en": (
        "Updates delivers new app builds from the official hub so fixes and features apply."
    ),
    "ru": (
        "Обновления — получение новых сборок с официального хаба."
    ),
    "zh": (
        "更新用于从官方 Hub 获取新版本以应用修复与功能。"
    ),
}

INTRO_SERVER: dict[Lang, str] = {
    "fa": (
        "بخش سرور و Deploy مربوط به نصب و پیکربندی روی VPS است؛ "
        "از جمله Deploy مرکزی و افزودن سرویس‌هایی مثل Exit، Node، تانل، دامنه و موارد مرتبط.\n\n"
        "این خدمات در محصول وجود دارند. برای جزئیات هر قابلیت یا مقایسهٔ مدها، از AI بپرسید."
    ),
    "en": (
        "Server & Deploy covers install and configuration on your VPS — "
        "including central Deploy and adding related services such as exits, nodes, tunnels, domains, and more.\n\n"
        "These capabilities exist in the product. For details or mode comparison, ask AI."
    ),
    "ru": (
        "Сервер и Deploy — установка и настройка на VPS: "
        "центральный Deploy и добавление связанных сервисов (exit, node, туннели, домены и др.).\n\n"
        "Эти возможности есть в продукте. Детали и сравнение режимов — спросите AI."
    ),
    "zh": (
        "服务器与 Deploy 用于在 VPS 上安装与配置，"
        "包括中心 Deploy 以及添加 Exit、Node、隧道、域名等相关服务。\n\n"
        "这些能力存在于产品中；细节或模式对比请向 AI 提问。"
    ),
}

INTRO_MESH: dict[Lang, str] = {
    "fa": (
        "بخش MESH و مانیتورینگ برای پایش سلامت مسیر بین سرورهاست "
        "(مثل Central، Tunnel، Exit و Node).\n\n"
        "ایجنت‌های Link Monitor روی میزبان‌ها نصب می‌شوند و وضعیت لینک‌ها را نگه می‌دارند "
        "حتی وقتی برنامهٔ ویندوز بسته باشد. جزئیات نصب و عیب‌یابی را از AI بپرسید."
    ),
    "en": (
        "MESH & Monitoring keeps path health between your servers "
        "(Central, Tunnel, Exit, Node, and related hosts).\n\n"
        "Link Monitor agents run on the hosts and watch links even when the Windows app is closed. "
        "Ask AI for install or troubleshooting steps."
    ),
    "ru": (
        "MESH и мониторинг следят за здоровьем путей между серверами "
        "(Central, Tunnel, Exit, Node и др.).\n\n"
        "Агенты Link Monitor работают на хостах и продолжают мониторинг, даже если Windows-приложение закрыто. "
        "Шаги установки и диагностики спросите у AI."
    ),
    "zh": (
        "MESH 与监控用于检查各服务器之间的链路健康"
        "（Central、Tunnel、Exit、Node 等）。\n\n"
        "Link Monitor 代理安装在主机上，即使关闭 Windows 程序也会持续监控。"
        "安装或排错步骤请向 AI 提问。"
    ),
}

INTRO_DOMAIN_CDN: dict[Lang, str] = {
    "fa": (
        "بخش Domain و CDN برای مدیریت دامنه/DNS و مسیرهای CDN مرتبط با پنل و سرویس‌هاست "
        "(مثل Cloudflare / ArvanCloud و گزینه‌های مرتبط در محصول).\n\n"
        "این قابلیت‌ها معمولاً در سطح Pro مطرح می‌شوند. برای آموزش گام‌به‌گام از AI بپرسید."
    ),
    "en": (
        "Domain & CDN covers domain/DNS management and CDN paths tied to the panel and services "
        "(such as Cloudflare / ArvanCloud and related product options).\n\n"
        "These are typically part of the Pro feature set. Ask AI for step-by-step guidance."
    ),
    "ru": (
        "Domain и CDN — управление доменом/DNS и CDN-путями для панели и сервисов "
        "(Cloudflare / ArvanCloud и связанные опции продукта).\n\n"
        "Обычно это набор Pro. Пошаговое обучение — через AI."
    ),
    "zh": (
        "Domain 与 CDN 用于管理与面板/服务相关的域名、DNS 与 CDN 路径"
        "（如 Cloudflare / ArvanCloud 及产品相关选项）。\n\n"
        "这些能力通常属于 Pro。分步教程请向 AI 提问。"
    ),
}

INTRO_MODES: dict[Lang, str] = {
    "fa": (
        "در Black Fox سه مد کاری دارید: Basic، Pro و AI Pro.\n\n"
        "همه روی یک تنظیمات مشترک کار می‌کنند؛ تفاوت در سطح امکانات و نحوهٔ کار است "
        "(در Basic و Pro بیشتر دستی، و در AI Pro امکان کار از طریق چت هوشمند هم هست).\n\n"
        "یکی از سه گزینهٔ زیر را انتخاب کنید تا امکانات همان مد را ببینید."
    ),
    "en": (
        "Black Fox has three working modes: Basic, Pro, and AI Pro.\n\n"
        "They share one local config store; the difference is feature access and workflow "
        "(manual ops in Basic/Pro, plus guided AI chat ops in AI Pro).\n\n"
        "Pick one option below to see that mode’s capabilities."
    ),
    "ru": (
        "В Black Fox три режима: Basic, Pro и AI Pro.\n\n"
        "Они используют одно общее локальное хранилище настроек; отличается доступ к функциям и способ работы "
        "(ручные операции в Basic/Pro, плюс умный чат в AI Pro).\n\n"
        "Выберите один пункт ниже, чтобы увидеть возможности режима."
    ),
    "zh": (
        "Black Fox 有三种工作模式：Basic、Pro、AI Pro。\n\n"
        "它们共用同一本地配置；差异在于功能权限与工作方式"
        "（Basic/Pro 偏手动操作，AI Pro 还可在智能对话中执行操作）。\n\n"
        "请选择下方某一项查看该模式能力。"
    ),
}

MODE_DETAIL_BASIC: dict[Lang, str] = {
    "fa": (
        "مد Basic برای شروع کار و هستهٔ Deploy مرکزی است.\n\n"
        "امکانات شاخص:\n"
        "• ذخیره سرور مرکزی، اتصال SSH و Full Deploy (هستهٔ رایگان Basic)\n"
        "• نصب WireGuard و پنل 3X-UI روی سرور مرکزی\n"
        "• مشاهدهٔ اطلاعات ورود پنل پس از Deploy موفق\n"
        "• مسیر رایگان کشور مرکزی معمولاً ایران، چین یا روسیه\n"
        "• افزودن Exit و امکانات پیشرفته‌تر نیاز به فعال‌سازی لایسنس دارد\n\n"
        "مدهای Pro و AI Pro جدا هستند؛ برای مقایسه یا آموزش نصب از AI بپرسید."
    ),
    "en": (
        "Basic mode — getting started and the central Deploy core.\n\n"
        "Key capabilities:\n"
        "• Setup Central, Connect SSH, and Full Deploy (Basic free core)\n"
        "• Install WireGuard + 3X-UI on the central server\n"
        "• Panel Login Info after a successful Deploy\n"
        "• Free central country path is typically IR / CN / RU\n"
        "• Adding exits and advanced ops needs license activation\n\n"
        "Pro and AI Pro are separate. Ask AI to compare modes or for install guidance."
    ),
    "ru": (
        "Режим Basic — старт и ядро центрального Deploy.\n\n"
        "Ключевые возможности:\n"
        "• Setup Central, Connect SSH и Full Deploy (бесплатное ядро Basic)\n"
        "• Установка WireGuard + 3X-UI на центральный сервер\n"
        "• Panel Login Info после успешного Deploy\n"
        "• Бесплатный путь страны Central обычно IR / CN / RU\n"
        "• Exit и расширенные операции требуют активации лицензии\n\n"
        "Pro и AI Pro — отдельно. Сравнение и обучение — через AI."
    ),
    "zh": (
        "Basic 模式 — 起步与中心 Deploy 核心。\n\n"
        "主要能力：\n"
        "• Setup Central、Connect SSH、Full Deploy（Basic 免费核心）\n"
        "• 在中心服务器安装 WireGuard + 3X-UI\n"
        "• Deploy 成功后可查看 Panel Login Info\n"
        "• 免费中心国家路径通常为 IR / CN / RU\n"
        "• 添加 Exit 与高级操作需要激活许可证\n\n"
        "Pro 与 AI Pro 不同。对比或安装教程请向 AI 提问。"
    ),
}

MODE_DETAIL_PRO: dict[Lang, str] = {
    "fa": (
        "مد Pro برای عملیات دستی کامل‌تر روی چند موقعیت است.\n\n"
        "امکانات شاخص:\n"
        "• ادامهٔ کار روی سرور مرکزی به‌همراه افزودن Exit و Tunnel و Node\n"
        "• پیکربندی پنل (Configure Panel) و ابزارهای مرتبط مسیریابی\n"
        "• مدیریت دامنه، DNS و CDN\n"
        "• MESH و مانیتورینگ لینک‌ها\n"
        "• سقف عملیاتی رایج: تا ۶ Exit و ۶ Node\n"
        "• کار از طریق دکمه‌ها و ویزاردهای Operations (جایگزین AI Pro نیست)\n\n"
        "مد Pro با AI Pro یکی نیست. جزئیات هر دکمه را از AI بپرسید."
    ),
    "en": (
        "Pro mode — fuller manual multi-location operations.\n\n"
        "Key capabilities:\n"
        "• Build on Central plus Exit / Tunnel / Node flows\n"
        "• Configure Panel and related routing tools\n"
        "• Domain / DNS and CDN\n"
        "• MESH and link monitoring\n"
        "• Common operational cap: up to 6 exits and 6 nodes\n"
        "• Work via Operations buttons/wizards (Pro ≠ AI Pro)\n\n"
        "Ask AI for details on any specific button or flow."
    ),
    "ru": (
        "Режим Pro — более полный ручной мультилокационный набор.\n\n"
        "Ключевые возможности:\n"
        "• Central + потоки Exit / Tunnel / Node\n"
        "• Configure Panel и связанные инструменты маршрутизации\n"
        "• Domain / DNS и CDN\n"
        "• MESH и мониторинг линков\n"
        "• Обычный лимит: до 6 Exit и 6 Node\n"
        "• Работа через кнопки/визарды Operations (Pro ≠ AI Pro)\n\n"
        "Детали конкретной кнопки — у AI."
    ),
    "zh": (
        "Pro 模式 — 更完整的手动多节点运维。\n\n"
        "主要能力：\n"
        "• 在 Central 基础上进行 Exit / Tunnel / Node\n"
        "• Configure Panel 及相关路由工具\n"
        "• Domain / DNS 与 CDN\n"
        "• MESH 与链路监控\n"
        "• 常见上限：最多 6 个 Exit 与 6 个 Node\n"
        "• 通过 Operations 按钮/向导操作（Pro ≠ AI Pro）\n\n"
        "具体按钮说明请向 AI 提问。"
    ),
}

MODE_DETAIL_AI_PRO: dict[Lang, str] = {
    "fa": (
        "مد AI Pro همان عملیات محصول را با راهنمایی چت هوشمند در دسترس می‌گذارد.\n\n"
        "امکانات شاخص:\n"
        "• دسترسی به عملیات سطح Pro از مسیر چت AI (با تأیید کاربر)\n"
        "• همزمان امکان استفادهٔ دستی از ابزارهای Pro باقی می‌ماند\n"
        "• مناسب برای Deploy، Exit، Mesh، CDN، تشخیص و تعمیر و کارهای مشابه\n"
        "• برای چت AI معمولاً فعال‌سازی AI Pro و سهمیهٔ AI لازم است\n"
        "• مد Pro به‌تنهایی جایگزین AI Pro نمی‌شود\n\n"
        "برای آموزش فعال‌سازی یا نمونهٔ دستور در چت، از بخش سوال از AI بپرسید."
    ),
    "en": (
        "AI Pro mode — the same product operations with guided AI chat.\n\n"
        "Key capabilities:\n"
        "• Run Pro-level ops from AI chat (with user confirmation)\n"
        "• Manual Pro tools remain available at the same time\n"
        "• Useful for Deploy, Exit, Mesh, CDN, diagnose/repair, and similar tasks\n"
        "• AI chat usually needs AI Pro unlock plus AI quota\n"
        "• Pro alone is not AI Pro\n\n"
        "Ask AI for activation guidance or example chat prompts."
    ),
    "ru": (
        "Режим AI Pro — те же операции продукта через умный чат.\n\n"
        "Ключевые возможности:\n"
        "• Операции уровня Pro из AI-чата (с подтверждением)\n"
        "• Ручные инструменты Pro остаются доступны\n"
        "• Удобно для Deploy, Exit, Mesh, CDN, diagnose/repair и похожих задач\n"
        "• Для чата обычно нужны AI Pro и AI-квота\n"
        "• Один Pro не заменяет AI Pro\n\n"
        "Активацию и примеры запросов спросите у AI."
    ),
    "zh": (
        "AI Pro 模式 — 通过智能对话执行同类产品操作。\n\n"
        "主要能力：\n"
        "• 在 AI 对话中执行 Pro 级操作（需确认）\n"
        "• 同时仍可使用手动 Pro 工具\n"
        "• 适用于 Deploy、Exit、Mesh、CDN、诊断修复等\n"
        "• AI 对话通常需要解锁 AI Pro 并具备 AI 额度\n"
        "• 仅有 Pro 不等于 AI Pro\n\n"
        "激活说明或示例提问请向 AI 询问。"
    ),
}

# ---------------------------------------------------------------------------
# Sales / contact CTAs
# ---------------------------------------------------------------------------

BUY_LICENSE_CTA: dict[Lang, str] = {
    "fa": (
        "از این بخش می‌توانید برای تهیه و فعال‌سازی لایسنس اقدام کنید "
        "تا امکانات بیشتر برنامه در دسترس باشد.\n\n"
        "قیمت و شرایط فقط روی سایت به‌روز است — اینجا قیمت اعلام نمی‌کنیم.\n\n"
        f"👉 {SITE_URL}\n"
        f"💬 پشتیبانی خرید: {SUPPORT_HANDLE}"
    ),
    "en": (
        "Use this to purchase and activate a license so more product features unlock.\n\n"
        "Live pricing is only on the website — we don’t quote prices here.\n\n"
        f"👉 {SITE_URL}\n"
        f"💬 Purchase help: {SUPPORT_HANDLE}"
    ),
    "ru": (
        "Здесь можно оформить и активировать лицензию для расширения возможностей.\n\n"
        "Актуальные цены только на сайте — здесь цены не называем.\n\n"
        f"👉 {SITE_URL}\n"
        f"💬 Помощь с покупкой: {SUPPORT_HANDLE}"
    ),
    "zh": (
        "可由此购买并激活许可证以解锁更多功能。\n\n"
        "实时价格仅以官网为准，此处不报价。\n\n"
        f"👉 {SITE_URL}\n"
        f"💬 购买协助：{SUPPORT_HANDLE}"
    ),
}

BUY_VPS_CTA: dict[Lang, str] = {
    "fa": (
        "برای اجرای Black Fox به VPS لینوکس نیاز دارید. "
        "تهیه سرور را فقط از بخش Partners در سایت رسمی انجام دهید؛ "
        "فروشندهٔ متفرقه پیشنهاد نمی‌کنیم.\n\n"
        f"👉 {SITE_URL} (Partners)\n"
        f"💬 راهنمایی: {SUPPORT_HANDLE}"
    ),
    "en": (
        "Black Fox runs on a Linux VPS. "
        "Get servers only via Partners on the official site — we don’t recommend random sellers.\n\n"
        f"👉 {SITE_URL} (Partners)\n"
        f"💬 Guidance: {SUPPORT_HANDLE}"
    ),
    "ru": (
        "Для Black Fox нужен Linux VPS. "
        "Берите сервер только через Partners на официальном сайте — случайных продавцов не рекомендуем.\n\n"
        f"👉 {SITE_URL} (Partners)\n"
        f"💬 Помощь: {SUPPORT_HANDLE}"
    ),
    "zh": (
        "运行 Black Fox 需要 Linux VPS。"
        "请仅通过官网 Partners 采购，不推荐随机卖家。\n\n"
        f"👉 {SITE_URL}（Partners）\n"
        f"💬 咨询：{SUPPORT_HANDLE}"
    ),
}

CONTACT_CTA: dict[Lang, str] = {
    "fa": (
        "از اینجا می‌توانید با اکانت پشتیبانی و گروه رسمی در ارتباط باشید.\n\n"
        f"اکانت پشتیبانی: {SUPPORT_HANDLE}\n"
        f"گروه: {GROUP_URL}\n"
        f"سایت: {SITE_URL}"
    ),
    "en": (
        "Reach support and the official community group here.\n\n"
        f"Support account: {SUPPORT_HANDLE}\n"
        f"Group: {GROUP_URL}\n"
        f"Website: {SITE_URL}"
    ),
    "ru": (
        "Здесь — аккаунт поддержки и официальная группа.\n\n"
        f"Поддержка: {SUPPORT_HANDLE}\n"
        f"Группа: {GROUP_URL}\n"
        f"Сайт: {SITE_URL}"
    ),
    "zh": (
        "可在此联系支持账号与官方群组。\n\n"
        f"支持账号：{SUPPORT_HANDLE}\n"
        f"群组：{GROUP_URL}\n"
        f"网站：{SITE_URL}"
    ),
}

# ---------------------------------------------------------------------------
# Chat / AI status
# ---------------------------------------------------------------------------

THINKING: dict[Lang, str] = {
    "fa": "در حال بررسی…",
    "en": "Looking that up…",
    "ru": "Проверяю…",
    "zh": "正在查找…",
}

def bot_intro(lang: Lang) -> str:
    name = get_bot_display_name()
    table = {
        "fa": (
            f"من {name} هستم — دستیار پشتیبانی محصول VPS to VPN در تلگرام.\n"
            "اکانت من: @BlackFox_Agent_Bot\n\n"
            "محصول VPS to VPN از Black Fox Group یک نصب‌کننده عملیاتی برای راه‌اندازی و مدیریت WireGuard و پنل 3X-UI "
            "روی VPS شماست (نه VPN مصرفی با دکمهٔ وصل شو).\n\n"
            "هر سؤالی دارید از من بپرسید؛ از منوی پایین هم می‌توانید موضوع را انتخاب کنید."
        ),
        "en": (
            f"I'm {name} — the Telegram product support assistant for VPS to VPN.\n"
            "My account: @BlackFox_Agent_Bot\n\n"
            "VPS to VPN by Black Fox Group is an operations installer for WireGuard and the 3X-UI panel on your VPS "
            "(not a consumer “connect” VPN app).\n\n"
            "Ask me anything — or pick a menu topic below."
        ),
        "ru": (
            f"Я {name} — помощник поддержки VPS to VPN в Telegram.\n"
            "Мой аккаунт: @BlackFox_Agent_Bot\n\n"
            "VPS to VPN (Black Fox Group) — операционный установщик WireGuard и панели 3X-UI на вашем VPS "
            "(не бытовой VPN).\n\n"
            "Спрашивайте меня о чём угодно — или выберите тему в меню."
        ),
        "zh": (
            f"我是 {name} — VPS to VPN 的 Telegram 产品支持助手。\n"
            "我的账号：@BlackFox_Agent_Bot\n\n"
            "VPS to VPN（Black Fox Group）是用于在您的 VPS 上部署管理 WireGuard 与 3X-UI 面板的操作安装器"
            "（不是消费级一键 VPN）。\n\n"
            "有问题尽管问我，也可从下方菜单选择主题。"
        ),
    }
    return table.get(lang, table["en"])


BOT_INTRO: dict[Lang, str] = {
    "fa": bot_intro("fa"),
    "en": bot_intro("en"),
    "ru": bot_intro("ru"),
    "zh": bot_intro("zh"),
}

GROUP_INVITE: dict[Lang, str] = {
    "fa": (
        "برای اخبار، آموزش و گفتگو به گروه رسمی بپیوندید:\n"
        f"{GROUP_URL}\n"
        f"اکانت پشتیبانی: {SUPPORT_HANDLE}"
    ),
    "en": (
        "Join the official group for news, guides, and discussion:\n"
        f"{GROUP_URL}\n"
        f"Support account: {SUPPORT_HANDLE}"
    ),
    "ru": (
        "Присоединяйтесь к официальной группе:\n"
        f"{GROUP_URL}\n"
        f"Поддержка: {SUPPORT_HANDLE}"
    ),
    "zh": (
        "请加入官方群组获取资讯与讨论：\n"
        f"{GROUP_URL}\n"
        f"支持账号：{SUPPORT_HANDLE}"
    ),
}

AI_ERROR: dict[Lang, str] = {
    "fa": f"الان پاسخ AI در دسترس نیست. لطفاً دوباره تلاش کنید یا به {SUPPORT_HANDLE} پیام دهید.",
    "en": f"AI is temporarily unavailable. Please retry or message {SUPPORT_HANDLE}.",
    "ru": f"AI временно недоступен. Повторите позже или напишите {SUPPORT_HANDLE}.",
    "zh": f"AI 暂时不可用。请稍后重试或联系 {SUPPORT_HANDLE}。",
}


def t(table: dict[Lang, str], lang: Lang, *, fallback: Lang = "en") -> str:
    """Look up a localized string with English fallback."""
    return table.get(lang, table[fallback])
