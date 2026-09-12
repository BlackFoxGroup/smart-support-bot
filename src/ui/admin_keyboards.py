"""Admin Control Center reply keyboards — FA / EN with dedicated emojis."""

from __future__ import annotations

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

Lang = str

# Runtime UI preference (1 or 2 columns). Loaded from bot_settings on start / APPLY_UI.
_settings_columns: int = 2
_custom_button_labels: set[str] = set()
_product_manage_labels: set[str] = set()


def set_settings_columns(columns: int) -> int:
    global _settings_columns
    _settings_columns = 1 if int(columns) == 1 else 2
    return _settings_columns


def get_settings_columns() -> int:
    return 1 if _settings_columns == 1 else 2


def refresh_custom_button_labels(buttons: list[dict] | None) -> set[str]:
    """Keep filter cache in sync with stored custom + generated buttons."""
    global _custom_button_labels
    labels: set[str] = set()
    for item in buttons or []:
        if not isinstance(item, dict):
            continue
        for key in ("label_fa", "label_en"):
            val = str(item.get(key) or "").strip()
            if val:
                labels.add(val)
    try:
        from src.generated.buttons import all_generated_labels

        labels.update(all_generated_labels())
    except Exception:  # noqa: BLE001
        pass
    _custom_button_labels = labels
    return labels


def merge_settings_extra_buttons(
    *,
    lang: str | None,
    catalog_buttons: list[dict] | None = None,
    generated_buttons: list[dict] | None = None,
) -> list:
    """Build KeyboardButton list for extra settings entries."""
    from aiogram.types import KeyboardButton

    fa = (lang or "").startswith("fa")
    out = []
    seen: set[str] = set()
    for item in list(catalog_buttons or []) + list(generated_buttons or []):
        if not isinstance(item, dict) or not item.get("enabled", True):
            continue
        txt = str(item.get("label_fa") if fa else item.get("label_en") or "").strip()
        if not txt:
            txt = str(item.get("label_fa") or item.get("label_en") or "").strip()
        if not txt or txt in seen:
            continue
        seen.add(txt)
        out.append(KeyboardButton(text=txt))
    return out


def custom_button_labels() -> frozenset[str]:
    return frozenset(_custom_button_labels)


def refresh_product_manage_labels(labels: list[str] | None) -> set[str]:
    global _product_manage_labels
    _product_manage_labels = {str(x).strip() for x in (labels or []) if str(x).strip()}
    return _product_manage_labels


def product_manage_labels() -> frozenset[str]:
    return frozenset(_product_manage_labels)


def _chunk_rows(buttons: list[KeyboardButton], cols: int | None = None) -> list[list[KeyboardButton]]:
    n = get_settings_columns() if cols is None else (1 if cols == 1 else 2)
    if n <= 1:
        return [[b] for b in buttons]
    rows: list[list[KeyboardButton]] = []
    for i in range(0, len(buttons), n):
        rows.append(buttons[i : i + n])
    return rows


# action → {fa, en} — every button has its own emoji
_LABELS: dict[str, dict[Lang, str]] = {
    "change_agent_api": {
        "fa": "📝 ثبت و ویرایش ایجنت و API",
        "en": "📝 Register & Edit Agent & API",
    },
    # Keep old labels resolvable so existing keyboards still work until refresh
    "change_agent_api_legacy": {
        "fa": "🔧 تغییر ایجنت و API",
        "en": "🔧 Change Agent & API",
    },
    "settings_hub": {
        "fa": "⚙️ تنظیمات",
        "en": "⚙️ Settings",
    },
    "backup_settings": {
        "fa": "💾 پشتیبان تنظیمات",
        "en": "💾 Settings Backup",
    },
    "backup_export": {
        "fa": "📤 خروجی پشتیبان",
        "en": "📤 Export Backup",
    },
    "backup_import": {
        "fa": "📥 درون‌ریزی پشتیبان",
        "en": "📥 Import Backup",
    },
    "health_status": {
        "fa": "🩺 وضعیت سلامت",
        "en": "🩺 Health Status",
    },
    "manage_admins": {
        "fa": "👥 مدیریت ادمین‌ها",
        "en": "👥 Manage Admins",
    },
    "admin_role_full": {
        "fa": "🔑 نقش کامل (تنظیمات)",
        "en": "🔑 Role: full (settings)",
    },
    "admin_role_stats": {
        "fa": "📊 نقش فقط آمار",
        "en": "📊 Role: stats only",
    },
    "admin_remove": {
        "fa": "🗑 حذف ادمین اضافی",
        "en": "🗑 Remove Extra Admin",
    },
    "health_toggle": {
        "fa": "⏱ روشن/خاموش گزارش روزانه",
        "en": "⏱ Toggle Daily Health Report",
    },
    "health_times": {
        "fa": "⏰ زمان گزارش سلامت",
        "en": "⏰ Health Report Times",
    },
    "health_chat": {
        "fa": "🎯 مقصد گزارش سلامت",
        "en": "🎯 Health Report Destination",
    },
    "owner_info": {
        "fa": "📋 اطلاعات اصلی",
        "en": "📋 Main Info",
    },
    "creator_contact": {
        "fa": "🛠 تماس با سازنده",
        "en": "🛠 Contact Creator",
    },
    "bot_config_chat": {
        "fa": "💬 گفتگو با AI",
        "en": "💬 Chat With AI",
    },
    "ai_chat_core": {
        "fa": "📋 اطلاعات اصلی",
        "en": "📋 Main settings",
    },
    "ai_chat_buttons": {
        "fa": "🛠 ساخت کلید",
        "en": "🛠 Build button",
    },
    "ai_chat_teach_product": {
        "fa": "📚 آموزش محصول",
        "en": "📚 Product teaching",
    },
    "ai_chat_teach_behavior": {
        "fa": "🎭 آموزش رفتار",
        "en": "🎭 Behavior teaching",
    },
    "ai_chat_all_products": {
        "fa": "🌐 همه محصولات",
        "en": "🌐 All products",
    },
    "bot_config_chat_legacy": {
        "fa": "💬 گفتگو با ربات",
        "en": "💬 Chat With Bot",
    },
    "build_catalogs": {
        "fa": "📦 ساخت کاتالوگ از پوشه",
        "en": "📦 Build Catalogs From Folder",
    },
    "products_hub": {
        "fa": "📦 محصولات",
        "en": "📦 Products",
    },
    "products_add": {
        "fa": "➕ افزودن محصول",
        "en": "➕ Add Product",
    },
    "products_edit_title": {
        "fa": "✏️ ویرایش نام",
        "en": "✏️ Edit Title",
    },
    "products_edit_emoji": {
        "fa": "😊 ویرایش ایموجی",
        "en": "😊 Edit Emoji",
    },
    "products_edit_summary": {
        "fa": "📝 ویرایش خلاصه",
        "en": "📝 Edit Summary",
    },
    "products_toggle": {
        "fa": "👁 روشن/خاموش در منو",
        "en": "👁 Toggle Menu Visibility",
    },
    "products_catalog_ai": {
        "fa": "📗 استفادهٔ AI از کاتالوگ",
        "en": "📗 Use catalog with AI",
    },
    "products_delete": {
        "fa": "🗑 حذف محصول",
        "en": "🗑 Delete Product",
    },
    "products_build_catalog": {
        "fa": "🗂 کاتالوگ محصول",
        "en": "🗂 Product catalog",
    },
    "products_product_chat": {
        "fa": "💬 گفتگو با AI",
        "en": "💬 Chat With AI",
    },
    "products_product_chat_legacy": {
        "fa": "💬 گفتگو با ربات",
        "en": "💬 Chat With Bot",
    },
    "products_ai_training": {
        "fa": "ارسال متن آموزشی برای ai",
        "en": "Send AI training text",
    },
    "products_ai_training_edit": {
        "fa": "✏️ ویرایش متن آموزشی",
        "en": "✏️ Edit training text",
    },
    "products_ai_training_delete": {
        "fa": "🗑 حذف متن آموزشی",
        "en": "🗑 Delete training text",
    },
    "products_catalog_enrich": {
        "fa": "📝 تکمیل اطلاعات کاتالوگ",
        "en": "📝 Complete catalog info",
    },
    "products_back": {
        "fa": "↩️ بازگشت به محصولات",
        "en": "↩️ Back to Products",
    },
    "catalog_src_site": {
        "fa": "🌐 منبع سایت",
        "en": "🌐 Site source",
    },
    "catalog_src_channel": {
        "fa": "📢 منبع کانال",
        "en": "📢 Channel source",
    },
    "catalog_src_group": {
        "fa": "👥 منبع گروه",
        "en": "👥 Group source",
    },
    "catalog_run": {
        "fa": "📦 ساخت کاتالوگ",
        "en": "📦 Build Catalog",
    },
    "settings_messages": {
        "fa": "📨 ثبت و ویرایش پیام‌های پیش‌فرض",
        "en": "📨 Register & Edit Default Messages",
    },
    "settings_panel": {
        "fa": "🖥 ثبت پنل و API",
        "en": "🖥 Register Panel & API",
    },
    "settings_back": {
        "fa": "⬅️ بازگشت به تنظیمات",
        "en": "⬅️ Back to Settings",
    },
    "msg_channel": {
        "fa": "📢 ثبت و ویرایش کانال",
        "en": "📢 Register & Edit Channel",
    },
    "msg_group": {
        "fa": "👥 ثبت و ویرایش گروه",
        "en": "👥 Register & Edit Group",
    },
    "msg_support": {
        "fa": "👤 ثبت و ویرایش اکانت",
        "en": "👤 Register & Edit Account",
    },
    "msg_account": {
        "fa": "👤 ثبت و ویرایش اکانت",
        "en": "👤 Register & Edit Account",
    },
    "msg_test": {
        "fa": "🧪 ثبت و ویرایش اکانت تست",
        "en": "🧪 Register & Edit Test Account",
    },
    "slot_1": {
        "fa": "1️⃣ اسلات ۱",
        "en": "1️⃣ Slot 1",
    },
    "slot_2": {
        "fa": "2️⃣ اسلات ۲",
        "en": "2️⃣ Slot 2",
    },
    "slot_3": {
        "fa": "3️⃣ اسلات ۳",
        "en": "3️⃣ Slot 3",
    },
    "edit_dest": {
        "fa": "🎯 اکانت مقصد",
        "en": "🎯 Destination Account",
    },
    "edit_dest_legacy": {
        "fa": "🎯 ویرایش مقصد",
        "en": "🎯 Edit Destination",
    },
    "edit_template": {
        "fa": "📝 متن پیام",
        "en": "📝 Message Text",
    },
    "edit_template_legacy": {
        "fa": "📝 ویرایش متن پیام",
        "en": "📝 Edit Message Text",
    },
    "edit_schedule": {
        "fa": "⏰ زمان ارسال",
        "en": "⏰ Schedule",
    },
    "edit_schedule_legacy": {
        "fa": "⏰ ویرایش زمان ارسال",
        "en": "⏰ Edit Schedule",
    },
    "edit_rules": {
        "fa": "📜 پرامپت قوانین و چت با AI",
        "en": "📜 Rules Prompt & AI Chat",
    },
    "edit_rules_legacy": {
        "fa": "📜 ویرایش پرامپت قوانین",
        "en": "📜 Edit Rules Prompt",
    },
    "edit_slot_kind": {
        "fa": "🏷 نوع اسلات (خبر/ثابت/کانفیگ)",
        "en": "🏷 Slot Kind (news/static/config)",
    },
    "toggle_slot_enabled": {
        "fa": "🔛 روشن/خاموش اسلات",
        "en": "🔛 Toggle Slot On/Off",
    },
    "owner_site": {
        "fa": "🌐 آدرس سایت",
        "en": "🌐 Site URL",
    },
    "owner_channel": {
        "fa": "📢 آدرس کانال",
        "en": "📢 Channel",
    },
    "owner_group": {
        "fa": "👥 آدرس گروه",
        "en": "👥 Group",
    },
    "owner_support": {
        "fa": "🛟 اکانت پشتیبانی مالک",
        "en": "🛟 Owner Support Account",
    },
    "owner_bot_name": {
        "fa": "🏷 نام ربات",
        "en": "🏷 Bot Name",
    },
    "nav_back": {
        "fa": "↩️ بازگشت",
        "en": "↩️ Back",
    },
    "edit_panel_url": {
        "fa": "🌐 آدرس پنل",
        "en": "🌐 Panel URL",
    },
    "edit_panel_url_legacy": {
        "fa": "🌐 ویرایش آدرس پنل",
        "en": "🌐 Edit Panel URL",
    },
    "edit_panel_token": {
        "fa": "🔑 API پنل",
        "en": "🔑 Panel API",
    },
    "edit_panel_token_legacy": {
        "fa": "🔑 ویرایش API پنل",
        "en": "🔑 Edit Panel API",
    },
    "edit_panel_inbound": {
        "fa": "📥 Inbound ID",
        "en": "📥 Inbound ID",
    },
    "edit_panel_inbound_legacy": {
        "fa": "📥 ویرایش Inbound ID",
        "en": "📥 Edit Inbound ID",
    },
    "stats_report": {
        "fa": "📈 گزارش عملکرد",
        "en": "📈 Performance Report",
    },
    "users_list": {
        "fa": "👥 لیست کاربران",
        "en": "👥 User List",
    },
    "news_report": {
        "fa": "📋 گزارش",
        "en": "📋 Report",
    },
    "stats_back": {
        "fa": "🏠 بازگشت به منو",
        "en": "🏠 Back to Menu",
    },
    "add_agent": {
        "fa": "➕ افزودن ایجنت جدید",
        "en": "➕ Add New Agent",
    },
    "list_agents": {
        "fa": "📋 فهرست ایجنت‌ها",
        "en": "📋 List Agents",
    },
    "set_active": {
        "fa": "✅ تنظیم به‌عنوان فعال",
        "en": "✅ Set as Active",
    },
    "test_agent": {
        "fa": "🧪 تست ایجنت",
        "en": "🧪 Test Agent",
    },
    "config_agent": {
        "fa": "⚙️ تنظیمات ایجنت",
        "en": "⚙️ Agent Configuration",
    },
    "support_agent": {
        "fa": "🛟 ایجنت پشتیبانی",
        "en": "🛟 Support Agent",
    },
    "api_mgmt": {
        "fa": "🔌 مدیریت API",
        "en": "🔌 API Management",
    },
    "chat_agent": {
        "fa": "💬 گفتگو با ایجنت",
        "en": "💬 Chat with Agent",
    },
    "failover": {
        "fa": "🔁 وضعیت جایگزینی خودکار",
        "en": "🔁 Failover Status",
    },
    "return_primary": {
        "fa": "↩️ بازگشت به ایجنت اصلی",
        "en": "↩️ Return to Primary",
    },
    "audit_log": {
        "fa": "📜 گزارش تغییرات",
        "en": "📜 Audit Log",
    },
    "token_monitor": {
        "fa": "💎 پایش اعتبار و توکن",
        "en": "💎 Token / Credit Monitor",
    },
    "control_home": {
        "fa": "🛠 خانه کنترل",
        "en": "🛠 Control Home",
    },
    "cancel": {
        "fa": "❌ انصراف",
        "en": "❌ Cancel",
    },
    "skip": {
        "fa": "⏭ رد کردن",
        "en": "⏭ Skip",
    },
    "clear_chat": {
        "fa": "🧹 پاک‌کردن مکالمه",
        "en": "🧹 Clear Conversation",
    },
    "end_chat": {
        "fa": "🚪 پایان گفتگو با ایجنت",
        "en": "🚪 End Chat with Agent",
    },
    "upload_hint": {
        "fa": "📎 ارسال فایل / تصویر / سند",
        "en": "📎 Send File / Image / Document",
    },
    "api_add": {
        "fa": "➕ افزودن API",
        "en": "➕ Add API",
    },
    "api_list": {
        "fa": "📋 فهرست APIها",
        "en": "📋 List APIs",
    },
    "api_test": {
        "fa": "🧪 تست API",
        "en": "🧪 Test API",
    },
    "api_delete": {
        "fa": "🗑 حذف API",
        "en": "🗑 Delete API",
    },
    "role_primary": {
        "fa": "👑 نقش اصلی (primary)",
        "en": "👑 Role: primary",
    },
    "role_secondary": {
        "fa": "🥈 نقش دوم (secondary)",
        "en": "🥈 Role: secondary",
    },
    "role_backup": {
        "fa": "🛟 نقش پشتیبان (backup)",
        "en": "🛟 Role: backup",
    },
    "role_support": {
        "fa": "🎧 نقش پشتیبانی (support)",
        "en": "🎧 Role: support",
    },
}

_UI_MSGS: dict[str, dict[Lang, str]] = {
    "stats_hub": {
        "fa": "📊 آمار ربات\n\nگزارش مدیریتی عملکرد هوش مصنوعی.",
        "en": "📊 Bot Stats\n\nManagerial AI performance report.",
    },
    "settings_hub": {
        "fa": (
            "⚙️ تنظیمات\n\n"
            "• 📋 اطلاعات اصلی (سایت/کانال/گروه/پشتیبانی)\n"
            "• 💬 گفتگو با ربات (کل تنظیمات)\n"
            "• 📦 محصولات (افزودن/ویرایش/حذف و کاتالوگ)\n"
            "• 📝 ایجنت و API / 📨 پیام‌ها / 🖥 پنل\n"
            "• 🛠 تماس با سازنده (قفل)"
        ),
        "en": (
            "⚙️ Settings\n\n"
            "• 📋 Main Info (site/channel/group/support)\n"
            "• 💬 Chat With Bot (whole bot)\n"
            "• 🏷 Products (add/edit/delete and catalogs)\n"
            "• 📝 Agents & API / 📨 Messages / 🖥 Panel\n"
            "• 🛠 Contact Creator (locked)"
        ),
    },
    "products_hub_intro": {
        "fa": (
            "📦 محصولات\n\n"
            "منوی اصلی از کاتالوگ‌های این بخش ساخته می‌شود.\n"
            "محصول جدید بسازید، ویرایش/حذف کنید، یا برای تکمیل محتوا کاتالوگ بسازید.\n"
            "تعداد محصول محدودیت ندارد. نصب تازه پیش‌فرض خالی است."
        ),
        "en": (
            "📦 Products\n\n"
            "The main menu is built from catalogs here.\n"
            "Add, edit, or delete products, then enrich via catalog build.\n"
            "No product limit. Fresh installs start empty."
        ),
    },
    "products_ask_title": {
        "fa": "نام محصول را بفرستید (مثلاً Config Builder):",
        "en": "Send the product name (e.g. Config Builder):",
    },
    "products_ask_emoji": {
        "fa": "یک ایموجی برای کلید منو بفرستید (یا — برای پیش‌فرض 📦):",
        "en": "Send one emoji for the menu key (or — for default 📦):",
    },
    "products_ask_summary": {
        "fa": "یک خلاصهٔ کوتاه فارسی/انگلیسی برای معرفی محصول بفرستید:",
        "en": "Send a short summary for the product intro:",
    },
    "products_ask_edit_title": {
        "fa": "نام جدید محصول را بفرستید:",
        "en": "Send the new product title:",
    },
    "products_ask_edit_emoji": {
        "fa": "ایموجی جدید را بفرستید:",
        "en": "Send the new emoji:",
    },
    "products_ask_edit_summary": {
        "fa": "خلاصهٔ جدید را بفرستید:",
        "en": "Send the new summary:",
    },
    "products_empty": {
        "fa": "هنوز محصولی ندارید. «افزودن محصول» را بزنید.",
        "en": "No products yet. Tap Add Product.",
    },
    "products_deleted": {
        "fa": "✅ محصول حذف شد و از منوی اصلی برداشته شد.",
        "en": "✅ Product deleted and removed from the main menu.",
    },
    "messages_hub": {
        "fa": (
            "📨 پیام‌های پیش‌فرض\n\n"
            "• کانال: مقصد کانال\n"
            "• گروه: مقصد گروه\n"
            "• اکانت: اکانت کاربر معمولی\n"
            "• اکانت تست: خروجی‌های مدیریتی"
        ),
        "en": (
            "📨 Default Messages\n\n"
            "• Channel destination\n"
            "• Group destination\n"
            "• Account: normal user account\n"
            "• Test account: admin outputs"
        ),
    },
    "ask_dest_channel": {
        "fa": (
            "🎯 آدرس کانال را بفرستید (مثل @mychannel).\n"
            "⚠️ فقط کانال قبول می‌شود.\n"
            "ربات باید در کانال به‌عنوان مدیر عضو باشد."
        ),
        "en": (
            "🎯 Send channel (@mychannel).\n"
            "⚠️ Only a channel is accepted.\n"
            "Bot must be an admin in that channel."
        ),
    },
    "ask_dest_group": {
        "fa": (
            "🎯 آدرس گروه را بفرستید (مثل @mygroup یا chat id).\n"
            "⚠️ فقط گروه/سوپرگروه قبول می‌شود.\n"
            "ربات باید در گروه به‌عنوان مدیر عضو باشد."
        ),
        "en": (
            "🎯 Send group (@mygroup or chat id).\n"
            "⚠️ Only a group/supergroup is accepted.\n"
            "Bot must be an admin in that group."
        ),
    },
    "ask_dest_account": {
        "fa": (
            "🎯 آدرس اکانت کاربر معمولی را بفرستید (مثل @username یا chat id عددی).\n"
            "این بخش برای اکانت شخصی است؛ کانال و گروه بخش جدا دارند."
        ),
        "en": (
            "🎯 Send a normal user account (@username or numeric chat id).\n"
            "This section is for private accounts; channel/group have their own sections."
        ),
    },
    "dest_type_mismatch": {
        "fa": "❌ نوع مقصد با این بخش جور نیست. {detail}",
        "en": "❌ Destination type does not match this section. {detail}",
    },
    "dest_need_admin": {
        "fa": "⚠️ ربات را در کانال/گروه ادمین کنید و دوباره امتحان کنید.",
        "en": "⚠️ Make the bot an admin in the channel/group and try again.",
    },
    "catalog_wizard_intro": {
        "fa": (
            "کاتالوگ همین محصول ({product})\n"
            "تعداد عکس در پوشهٔ این محصول: {photo_count}\n\n"
            "عکس یا متن را همین‌جا بفرستید؛ برای آموزش کاتالوگ و نحوهٔ توضیح "
            "کاتالوگ به کاربر از کلید «ارسال متن آموزشی برای ai» استفاده کنید.\n"
            "برای ثبت نهایی کاتالوگ «ساخت کاتالوگ» را بزنید."
        ),
        "en": (
            "Catalog for this product ({product})\n"
            "Photos in this product folder: {photo_count}\n\n"
            "Send a photo or text here. Use Send AI training text only for catalog teaching.\n"
            "Tap Build Catalog when you want a full rebuild."
        ),
    },
    "products_product_chat_intro": {
        "fa": (
            "💬 گفتگو با AI — دسترسی کامل فعال شد.\n\n"
            "می‌توانم همهٔ بخش‌های موجود را ویرایش کنم:\n"
            "• اطلاعات اصلی (نام/سایت/کانال/گروه/پشتیبانی)\n"
            "• پیام‌ها: کانال، گروه، اکانت، اکانت تست (اسلات‌ها، زمان، متن، قوانین، روشن/خاموش)\n"
            "• پنل (آدرس/API/Inbound)\n"
            "• سلامت روزانه / ادمین‌ها / ستون کیبورد\n"
            "• ساخت کلید با کدنویسی AI (safe-change حدود ۱ دقیقه)\n"
            "• آموزش محصول، و به‌روز کردن دانش تمام محصولات\n"
            "• آموزش نحوهٔ رفتار پاسخ به کاربر (چند خط، ایموجی، لحن). "
            "این‌ها در فایل حافظه می‌ماند و Ask AI از آن‌ها استفاده می‌کند.\n\n"
            "آموزش مخصوص کاتالوگ را از «ارسال متن آموزشی برای ai» بفرستید."
        ),
        "en": (
            "💬 Chat With AI — full access is on.\n\n"
            "I can edit all existing sections:\n"
            "• Owner info (name/site/channel/group/support)\n"
            "• Messages: channel, group, account, test account\n"
            "• Panel / daily health / admins / keyboard columns\n"
            "• AI-coded buttons via safe-change (~1 min)\n"
            "• Product teaching and updating knowledge for all products\n"
            "• Reply behavior (multi-line, emojis, tone) stored for Ask AI\n\n"
            "Use Send AI training text only for catalog teaching."
        ),
    },
    "catalog_src_site": {
        "fa": "🌐 منبع سایت",
        "en": "🌐 Site source",
    },
    "catalog_src_channel": {
        "fa": "📢 منبع کانال",
        "en": "📢 Channel source",
    },
    "catalog_src_group": {
        "fa": "👥 منبع گروه",
        "en": "👥 Group source",
    },
    "catalog_ask_path": {
        "fa": "📁 مسیر پوشه روی سرور را بفرستید، یا همین‌جا عکس و متن همین محصول را بفرستید.",
        "en": "📁 Send a server folder path, or send this product's photos and text here.",
    },
    "catalog_ask_source": {
        "fa": (
            "مقدار ذخیره‌شده قبلی:\n{saved}\n\n"
            "مقدار جدید را بفرستید. بعد با نوشتن «تایید» یا «عدم تایید» مشخص کنید "
            "آیا در کاتالوگ استفاده شود."
        ),
        "en": (
            "Previously saved value:\n{saved}\n\n"
            "Send the new value. Then type Confirm or Decline to decide if the catalog should use it."
        ),
    },
    "catalog_ask_confirm": {
        "fa": "برای استفاده در کاتالوگ «تایید» و برای رد «عدم تایید» را بفرستید.",
        "en": "Type Confirm to use this in the catalog, or Decline to skip it.",
    },
    "catalog_confirm_preview": {
        "fa": (
            "آمادهٔ ارسال به AI و سرور.\n"
            "عکس‌ها: {photo_count}\n"
            "سایت: {site}\n"
            "کانال: {channel}\n"
            "گروه: {group}\n"
            "یادداشت‌های راهنما: {notes}"
        ),
        "en": (
            "Ready to send to AI and the server.\n"
            "Photos: {photo_count}\n"
            "Site: {site}\n"
            "Channel: {channel}\n"
            "Group: {group}\n"
            "Guide notes: {notes}"
        ),
    },
    "catalog_declined": {
        "fa": "ثبت نشد. اطلاعات قبلی همان‌طور ماند.",
        "en": "Not saved. Previous data was kept.",
    },
    "catalog_enrich_intro": {
        "fa": (
            "عکس یا متن کاتالوگ را بفرستید.\n"
            "بعد از هر مورد، یک توضیح کوتاه برای راهنمایی AI بنویسید.\n"
            "برای ثبت نهایی از کلید «ساخت کاتالوگ» استفاده کنید."
        ),
        "en": (
            "Send a catalog photo or text.\n"
            "After each item, write a short AI guide note.\n"
            "Tap Build Catalog when you want to register everything."
        ),
    },
    "catalog_enrich_ask_note": {
        "fa": "برای همین مورد، توضیح راهنمای AI را بفرستید (AI از این متن در پاسخ‌ها استفاده می‌کند).",
        "en": "Send the AI guide note for this item (used in later user answers).",
    },
    "products_ask_training": {
        "fa": (
            "ویرایش متن آموزشی کاتالوگ — ذخیره جایگزین متن قبلی می‌شود.\n"
            "متن فعلی:\n{saved}\n\n"
            "متن کامل جدید را بفرستید."
        ),
        "en": (
            "Edit catalog training text — saving replaces the previous text.\n"
            "Current text:\n{saved}\n\n"
            "Send the full new text."
        ),
    },
    "products_ask_training_append": {
        "fa": "متن آموزشی جدید را بفرستید. به ادامهٔ متن قبلی اضافه می‌شود.",
        "en": "Send the new training text. It will be appended to the previous text.",
    },
    "products_training_hub": {
        "fa": (
            "متن آموزشی کاتالوگ — فقط دربارهٔ همین کاتالوگ.\n\n"
            "وضعیت: {status}\n"
            "متن کامل فقط با «ویرایش متن آموزشی» دیده می‌شود."
        ),
        "en": (
            "Catalog training text — this catalog only.\n\n"
            "Status: {status}\n"
            "Full text is shown only when you tap Edit training text."
        ),
    },
    "products_training_status_empty": {
        "fa": "هنوز متنی ذخیره نشده.",
        "en": "No training text saved yet.",
    },
    "products_training_status_ok": {
        "fa": "ذخیره شده ({n} نویسه).",
        "en": "Saved ({n} characters).",
    },
    "products_training_cleared": {
        "fa": "متن آموزشی کاتالوگ حذف شد.",
        "en": "Catalog training text was deleted.",
    },
    "catalog_src_toggled": {
        "fa": "منبع‌ها: سایت={site} | کانال={channel} | گروه={group}",
        "en": "Sources: site={site} | channel={channel} | group={group}",
    },
    "owner_hub": {
        "fa": "📋 اطلاعات اصلی — یکی را برای ویرایش انتخاب کنید.",
        "en": "📋 Main Info — pick a field to edit.",
    },
    "creator_locked": {
        "fa": "🔒 تماس با سازنده قابل ویرایش از داخل ربات نیست.",
        "en": "🔒 Contact Creator cannot be edited inside the bot.",
    },
    "bot_chat_start": {
        "fa": (
            "💬 گفتگو با AI — یک گزینه را انتخاب کنید:\n\n"
            "📋 اطلاعات اصلی: نام/سایت/کانال/گروه/پشتیبانی، پیام‌ها، پنل، سلامت، ادمین، ستون کیبورد\n"
            "🛠 ساخت کلید: ساخت کلید با کدنویسی AI\n"
            "📚 آموزش محصول: دانش همان محصول (نه کاتالوگ محصول دیگر)\n"
            "🎭 آموزش رفتار: چند خط، ایموجی، لحن — فقط برای محصول انتخاب‌شده"
        ),
        "en": (
            "💬 Chat With AI — pick one option:\n\n"
            "📋 Main settings: owner, messages, panel, health, admins, keyboard\n"
            "🛠 Build button: AI-coded button\n"
            "📚 Product teaching: this product only\n"
            "🎭 Behavior teaching: multi-line / emoji / tone for the chosen product"
        ),
    },
    "ai_chat_ask_product": {
        "fa": "این آموزش برای کدام محصول است؟ یکی را بزنید، یا «همه محصولات».",
        "en": "Which product is this teaching for? Tap one, or All products.",
    },
    "ai_chat_ask_behavior": {
        "fa": "قانون رفتار همین محصول را بفرستید (مثلاً چند خط و ایموجی).",
        "en": "Send the behavior rule for this product (e.g. multi-line and emojis).",
    },
    "ai_chat_ask_product_teach": {
        "fa": "نکتهٔ آموزشی همین محصول را بفرستید. به کاتالوگ محصول دیگر ربط ندهید.",
        "en": "Send the teaching note for this product only.",
    },
    "ai_chat_saved_targets": {
        "fa": "✅ ذخیره شد در فایل همین محصول: {targets}",
        "en": "✅ Saved on this product file: {targets}",
    },
    "scoped_rules_start": {
        "fa": (
            "📜 پرامپت قوانین و چت با AI (فقط همین اسلات).\n"
            "خواسته‌تان را بنویسید تا قوانین همین بخش به‌روز شود."
        ),
        "en": (
            "📜 Rules prompt & AI chat (this slot only).\n"
            "Describe the change; only this section's rules will update."
        ),
    },
    "ask_slot_kind": {
        "fa": "🏷 نوع اسلات را بفرستید: news یا static یا config",
        "en": "🏷 Send slot kind: news or static or config",
    },
    "ask_owner_site": {
        "fa": "🌐 آدرس سایت را بفرستید (مثل https://example.com):",
        "en": "🌐 Send site URL:",
    },
    "ask_owner_channel": {
        "fa": "📢 آدرس کانال را بفرستید (مثل @mychannel):",
        "en": "📢 Send channel (@handle or id):",
    },
    "ask_owner_group": {
        "fa": "👥 آدرس گروه را بفرستید (مثل @mygroup):",
        "en": "👥 Send group (@handle or id):",
    },
    "ask_owner_support": {
        "fa": "🛟 اکانت پشتیبانی مالک را بفرستید (مثل @support):",
        "en": "🛟 Send owner support account:",
    },
    "ask_owner_bot_name": {
        "fa": "🏷 نام ربات را بفرستید (همان نام پروفایل تلگرام که کاربر می‌بیند):",
        "en": "🏷 Send the bot name (Telegram profile name users see):",
    },
    "ask_admin_id": {
        "fa": "شناسه عددی تلگرام ادمین را بفرستید:",
        "en": "Send the Telegram numeric user id for the admin:",
    },
    "ask_health_times": {
        "fa": "زمان گزارش سلامت را بفرستید (مثل 09:00 یا 09:00,21:00):",
        "en": "Send health report times (e.g. 09:00 or 09:00,21:00):",
    },
    "ask_health_chat": {
        "fa": "مقصد گزارش سلامت را بفرستید (آیدی عددی یا @username):",
        "en": "Send health report destination (numeric id or @username):",
    },
    "news_report_denied": {
        "fa": "این گزارش فقط برای مالک و میدان در دسترس است.",
        "en": "This report is only for the owner and Midan.",
    },
    "ask_backup_import": {
        "fa": "فایل JSON پشتیبان را به‌صورت Document بفرستید:",
        "en": "Send the backup JSON as a Document:",
    },
    "backup_exported": {
        "fa": "✅ فایل پشتیبان تنظیمات آماده است. در جای امن نگه دارید (توکن پنل داخلش هست).",
        "en": "✅ Settings backup file is ready. Keep it private (includes panel token).",
    },
    "backup_imported": {
        "fa": "✅ پشتیبان درون‌ریزی شد: {sections}",
        "en": "✅ Backup imported: {sections}",
    },
    "admins_card": {
        "fa": (
            "👥 مدیریت ادمین‌ها\n\n"
            "ادمین‌های env (همیشه کامل):\n{env_admins}\n\n"
            "ادمین‌های اضافی:\n{extra_admins}\n\n"
            "نقش کامل = تنظیمات + آمار\nنقش آمار = فقط آمار و سلامت"
        ),
        "en": (
            "👥 Manage Admins\n\n"
            "Env admins (always full):\n{env_admins}\n\n"
            "Extra admins:\n{extra_admins}\n\n"
            "full = settings + stats\nstats = stats/health only"
        ),
    },
    "settings_denied": {
        "fa": "دسترسی تنظیمات ندارید. نقش شما فقط آمار است.",
        "en": "No settings access. Your role is stats-only.",
    },
    "catalog_building": {
        "fa": "📦 در حال ساخت کاتالوگ از پوشه catalog_inbox …",
        "en": "📦 Building catalogs from catalog_inbox …",
    },
    "catalog_done": {
        "fa": "✅ کاتالوگ‌ها ساخته شد: {ids}",
        "en": "✅ Catalogs built: {ids}",
    },
    "catalog_empty": {
        "fa": "پوشه catalog_inbox خالی است. یک پوشه محصول با فایل متن/عکس بسازید.",
        "en": "catalog_inbox is empty. Add a product folder with text/photos.",
    },
    "admin_only": {
        "fa": "⛔ فقط برای مدیران.",
        "en": "⛔ Admin only.",
    },
    "no_agents": {
        "fa": "هیچ ایجنتی ثبت نشده است.",
        "en": "No agents registered.",
    },
    "no_apis": {
        "fa": "هیچ APIای ثبت نشده است.",
        "en": "No APIs registered.",
    },
    "add_agent_start": {
        "fa": "➕ افزودن ایجنت جدید\n\nگام ۱/۹ — نام ایجنت:",
        "en": "➕ Add New Agent\n\nStep 1/9 — Agent Name:",
    },
    "support_agent_start": {
        "fa": "🛟 راه‌اندازی ایجنت پشتیبانی\n\nگام ۱/۹ — نام ایجنت:",
        "en": "🛟 Support Agent setup\n\nStep 1/9 — Agent Name:",
    },
    "pick_set_active": {
        "fa": "✅ ایجنت موردنظر را برای فعال‌سازی انتخاب کنید (ابتدا تست اتصال اجرا می‌شود):",
        "en": "✅ Select agent to Set as Active (Test Mode runs first):",
    },
    "pick_test": {
        "fa": "🧪 ایجنت موردنظر را برای تست انتخاب کنید:",
        "en": "🧪 Select agent to Test:",
    },
    "pick_config": {
        "fa": "⚙️ ایجنت موردنظر را برای تنظیمات انتخاب کنید:",
        "en": "⚙️ Select agent to configure:",
    },
    "pick_chat": {
        "fa": "💬 گفتگو با ایجنت\nایجنت هدف را انتخاب کنید:",
        "en": "💬 Chat with Agent\nSelect target agent:",
    },
    "pick_api_delete": {
        "fa": "🗑 مورد API را برای حذف انتخاب کنید:",
        "en": "🗑 Select API to delete:",
    },
    "pick_api_test": {
        "fa": "🧪 مورد API را برای تست انتخاب کنید:",
        "en": "🧪 Select API to test:",
    },
    "api_mgmt_intro": {
        "fa": "🔌 مدیریت API\n\nافزودن، فهرست، تست یا حذف ارائه‌دهندگان API.",
        "en": "🔌 API Management\n\nAdd / List / Test / Delete API providers.",
    },
    "api_add_name": {
        "fa": "➕ افزودن API — نام ارائه‌دهنده:",
        "en": "➕ Add API — Provider Name:",
    },
    "chat_cleared": {
        "fa": "🧹 مکالمه پاک شد.",
        "en": "🧹 Conversation cleared.",
    },
    "not_in_chat": {
        "fa": "الان در حالت گفتگو با ایجنت نیستید.",
        "en": "Not in Chat with Agent mode.",
    },
    "upload_help": {
        "fa": (
            "📎 اکنون فایل، عکس یا سند را ارسال کنید.\n"
            "قبل از ارسال به ایجنت، نام، نوع و حجم نمایش داده می‌شود."
        ),
        "en": (
            "📎 Send a file / photo / document now.\n"
            "Name, type, and size will be shown before sending to the Agent."
        ),
    },
    "choose_role": {
        "fa": "نقش ایجنت را انتخاب کنید:",
        "en": "Choose Role:",
    },
    "cancel_done": {
        "fa": "❌ لغو شد.",
        "en": "❌ Cancelled.",
    },
    "testing_now": {
        "fa": "⏳ در حال تست اتصال… لطفاً چند لحظه صبر کنید.",
        "en": "⏳ Testing connection… please wait.",
    },
    "activating_now": {
        "fa": "⏳ در حال تست و فعال‌سازی ایجنت… لطفاً چند لحظه صبر کنید.",
        "en": "⏳ Testing and activating agent… please wait.",
    },
    "chatting_now": {
        "fa": "⏳ در حال دریافت پاسخ از ایجنت…",
        "en": "⏳ Waiting for agent reply…",
    },
    "ask_dest": {
        "fa": "🎯 شناسه یا آدرس مقصد را بفرستید (مثل @channel یا عدد chat id):",
        "en": "🎯 Send destination (@channel or numeric chat id):",
    },
    "ask_template": {
        "fa": (
            "📝 متن پیام را کامل بفرستید.\n"
            "برای کانفیگ شبانه می‌توانید از {config} و {date} استفاده کنید."
        ),
        "en": (
            "📝 Send the full message template.\n"
            "For nightly config you may use {config} and {date}."
        ),
    },
    "ask_schedule": {
        "fa": "⏰ زمان ارسال را بفرستید (مثل 21:00 یا 10:00,17:00):",
        "en": "⏰ Send schedule times (e.g. 21:00 or 10:00,17:00):",
    },
    "ask_rules": {
        "fa": (
            "📜 پرامپت قوانین و چت با AI — فقط برای همین اسلات.\n"
            "متن قوانین جدید را بفرستید، یا خواسته‌تان را به زبان ساده بنویسید تا AI قوانین را بسازد."
        ),
        "en": (
            "📜 Rules prompt & AI chat — this slot only.\n"
            "Send the new rules text, or describe the change in plain language for AI to rewrite rules."
        ),
    },
    "ask_panel_url": {
        "fa": "🌐 آدرس پنل را بفرستید (مثل https://panel.example.com:2053):",
        "en": "🌐 Send panel base URL:",
    },
    "ask_panel_token": {
        "fa": "🔑 توکن API پنل را بفرستید (رمزنگاری می‌شود):",
        "en": "🔑 Send panel API token (stored encrypted):",
    },
    "ask_panel_inbound": {
        "fa": "📥 شناسه Inbound را بفرستید (یک عدد یا چند عدد با کاما، مثل 1,2,5):",
        "en": "📥 Send inbound ID(s) — one number or comma-separated, e.g. 1,2,5:",
    },
    "saved_ok": {
        "fa": "✅ ذخیره شد.",
        "en": "✅ Saved.",
    },
}


def ui_lang(lang: str | None) -> Lang:
    """Control Center UI is FA/EN; other langs fall back to English."""
    return "fa" if (lang or "").startswith("fa") else "en"


def label(action: str, lang: str | None) -> str:
    from src.ui.system_layout import rename_for

    ren = rename_for(action)
    code = ui_lang(lang)
    if ren:
        return ren.get(code) or ren.get("en") or ren.get("fa") or ""
    table = _LABELS[action]
    return table.get(code) or table["en"]


def msg(key: str, lang: str | None) -> str:
    table = _UI_MSGS[key]
    code = ui_lang(lang)
    return table.get(code) or table["en"]


def texts(action: str) -> frozenset[str]:
    from src.ui.system_layout import rename_for

    table = _LABELS.get(action)
    if not table:
        return frozenset()
    out = set(table.values())
    ren = rename_for(action)
    if ren:
        out.update({ren.get("fa") or "", ren.get("en") or ""})
        out.discard("")
    return frozenset(out)


def _norm_button_text(text: str | None) -> str:
    """Strip Telegram RTL/check prefixes so '✅ ساخت کاتالوگ' still matches."""
    needle = (text or "").strip()
    for token in ("✅", "⬜"):
        needle = needle.replace(token, " ")
    return " ".join(needle.split())


def resolve_action(text: str | None) -> str | None:
    if not text:
        return None
    raw = text.strip()
    needle = _norm_button_text(raw)
    from src.ui.system_layout import load_layout

    layout = load_layout()
    for action, lab in (layout.get("renames") or {}).items():
        if not isinstance(lab, dict):
            continue
        variants = {
            _norm_button_text(str(lab.get("fa") or "")),
            _norm_button_text(str(lab.get("en") or "")),
        }
        variants.discard("")
        if raw in {str(lab.get("fa") or "").strip(), str(lab.get("en") or "").strip()} or needle in variants:
            return str(action)
    for action, table in _LABELS.items():
        values = {str(v) for v in table.values()}
        norms = {_norm_button_text(v) for v in values}
        if raw in values or needle in norms:
            if action.endswith("_legacy"):
                return action[: -len("_legacy")]
            if action == "change_agent_api_legacy":
                return "change_agent_api"
            if action == "msg_support":
                return "msg_account"
            return action
    return None


def _kb_buttons(menu: str, actions: list[str], lang: str | None) -> list[KeyboardButton]:
    from src.ui.system_layout import filter_actions

    return [KeyboardButton(text=label(a, lang)) for a in filter_actions(menu, actions)]


def all_admin_control_texts() -> frozenset[str]:
    out: set[str] = set()
    for table in _LABELS.values():
        out.update(table.values())
        # Include toggle-prefixed catalog source labels
        for v in table.values():
            out.add("✅ " + v)
            out.add("⬜ " + v)
    out.update(_custom_button_labels)
    return frozenset(out)


def settings_hub_keyboard(
    lang: str | None = "en",
    *,
    custom_buttons: list[dict] | None = None,
    generated_buttons: list[dict] | None = None,
) -> ReplyKeyboardMarkup:
    buttons = _kb_buttons(
        "settings",
        [
            "owner_info",
            "bot_config_chat",
            "products_hub",
            "change_agent_api",
            "settings_messages",
            "settings_panel",
            "backup_settings",
            "health_status",
            "manage_admins",
            "creator_contact",
        ],
        lang,
    )
    buttons.extend(
        merge_settings_extra_buttons(
            lang=lang,
            catalog_buttons=custom_buttons,
            generated_buttons=generated_buttons,
        )
    )
    buttons.extend(_kb_buttons("settings", ["stats_back"], lang))
    refresh_custom_button_labels(list(custom_buttons or []) + list(generated_buttons or []))
    return ReplyKeyboardMarkup(
        keyboard=_chunk_rows(buttons),
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Settings / تنظیمات",
    )


def backup_keyboard(lang: str | None = "en") -> ReplyKeyboardMarkup:
    buttons = _kb_buttons(
        "backup",
        ["backup_export", "backup_import", "settings_back"],
        lang,
    )
    return ReplyKeyboardMarkup(
        keyboard=_chunk_rows(buttons),
        resize_keyboard=True,
        is_persistent=True,
    )


def health_keyboard(lang: str | None = "en") -> ReplyKeyboardMarkup:
    buttons = _kb_buttons(
        "health",
        ["health_status", "health_toggle", "health_times", "health_chat", "settings_back"],
        lang,
    )
    return ReplyKeyboardMarkup(
        keyboard=_chunk_rows(buttons),
        resize_keyboard=True,
        is_persistent=True,
    )


def admins_keyboard(lang: str | None = "en") -> ReplyKeyboardMarkup:
    buttons = _kb_buttons(
        "admins",
        ["admin_role_full", "admin_role_stats", "admin_remove", "settings_back"],
        lang,
    )
    return ReplyKeyboardMarkup(
        keyboard=_chunk_rows(buttons),
        resize_keyboard=True,
        is_persistent=True,
    )


def stats_hub_keyboard(
    lang: str | None = "en",
    *,
    generated_buttons: list[dict] | None = None,
    show_news_report: bool = False,
) -> ReplyKeyboardMarkup:
    actions = ["stats_report", "users_list"]
    if show_news_report:
        actions.append("news_report")
    actions.append("stats_back")
    buttons = _kb_buttons("stats", actions, lang)
    # Generated buttons targeted at stats menu
    for item in list(generated_buttons or []):
        if not item.get("enabled", True):
            continue
        if str(item.get("menu") or "settings") != "stats":
            continue
        lab = str(item.get("label_fa") or item.get("label_en") or "").strip()
        if lab:
            buttons.insert(-1, KeyboardButton(text=lab))
    refresh_custom_button_labels(list(generated_buttons or []))
    return ReplyKeyboardMarkup(
        keyboard=_chunk_rows(buttons),
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Statistics / آمار",
    )


def owner_info_keyboard(lang: str | None = "en") -> ReplyKeyboardMarkup:
    buttons = _kb_buttons(
        "owner",
        [
            "owner_bot_name",
            "owner_site",
            "owner_channel",
            "owner_group",
            "owner_support",
            "settings_back",
        ],
        lang,
    )
    return ReplyKeyboardMarkup(
        keyboard=_chunk_rows(buttons),
        resize_keyboard=True,
        is_persistent=True,
    )


def messages_hub_keyboard(lang: str | None = "en") -> ReplyKeyboardMarkup:
    buttons = _kb_buttons(
        "messages",
        ["msg_channel", "msg_group", "msg_account", "msg_test", "settings_back"],
        lang,
    )
    return ReplyKeyboardMarkup(
        keyboard=_chunk_rows(buttons),
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Default messages",
    )


def products_hub_keyboard(
    lang: str | None = "en",
    *,
    product_labels: list[str] | None = None,
) -> ReplyKeyboardMarkup:
    buttons: list[KeyboardButton] = []
    for lab in product_labels or []:
        if lab:
            buttons.append(KeyboardButton(text=lab))
    buttons.extend(
        [
            KeyboardButton(text=label("products_add", lang)),
            KeyboardButton(text=label("settings_back", lang)),
        ]
    )
    return ReplyKeyboardMarkup(
        keyboard=_chunk_rows(buttons),
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Products / محصولات",
    )


def product_detail_keyboard(lang: str | None = "en") -> ReplyKeyboardMarkup:
    buttons = _kb_buttons(
        "products",
        [
            "products_edit_title",
            "products_edit_emoji",
            "products_edit_summary",
            "products_toggle",
            "products_catalog_ai",
            "products_build_catalog",
            "products_product_chat",
            "products_delete",
            "products_back",
            "settings_back",
        ],
        lang,
    )
    return ReplyKeyboardMarkup(
        keyboard=_chunk_rows(buttons),
        resize_keyboard=True,
        is_persistent=True,
    )


def ai_chat_hub_keyboard(lang: str | None = "en") -> ReplyKeyboardMarkup:
    buttons = [
        KeyboardButton(text=label("ai_chat_core", lang)),
        KeyboardButton(text=label("ai_chat_buttons", lang)),
        KeyboardButton(text=label("ai_chat_teach_product", lang)),
        KeyboardButton(text=label("ai_chat_teach_behavior", lang)),
        KeyboardButton(text=label("products_back", lang)),
        KeyboardButton(text=label("settings_back", lang)),
    ]
    return ReplyKeyboardMarkup(
        keyboard=_chunk_rows(buttons),
        resize_keyboard=True,
        is_persistent=True,
    )


def ai_chat_product_pick_keyboard(
    labels: list[str], lang: str | None = "en"
) -> ReplyKeyboardMarkup:
    buttons = [KeyboardButton(text=x) for x in labels if x]
    buttons.append(KeyboardButton(text=label("ai_chat_all_products", lang)))
    buttons.append(KeyboardButton(text=label("products_back", lang)))
    return ReplyKeyboardMarkup(
        keyboard=_chunk_rows(buttons),
        resize_keyboard=True,
        is_persistent=True,
    )


def training_hub_keyboard(lang: str | None = "en") -> ReplyKeyboardMarkup:
    buttons = [
        KeyboardButton(text=label("products_ai_training", lang)),
        KeyboardButton(text=label("products_ai_training_edit", lang)),
        KeyboardButton(text=label("products_ai_training_delete", lang)),
        KeyboardButton(text=label("products_back", lang)),
        KeyboardButton(text=label("settings_back", lang)),
    ]
    return ReplyKeyboardMarkup(
        keyboard=_chunk_rows(buttons),
        resize_keyboard=True,
        is_persistent=True,
    )


def catalog_wizard_keyboard(lang: str | None = "en", *, sources: dict[str, bool] | None = None) -> ReplyKeyboardMarkup:
    sources = sources or {"site": False, "channel": False, "group": False}

    def mark(on: bool, key: str) -> str:
        base = label(key, lang)
        return (("✅ " if on else "⬜ ") + base)

    buttons = [
        KeyboardButton(text=mark(bool(sources.get("site")), "catalog_src_site")),
        KeyboardButton(text=mark(bool(sources.get("channel")), "catalog_src_channel")),
        KeyboardButton(text=mark(bool(sources.get("group")), "catalog_src_group")),
        KeyboardButton(text=label("products_ai_training", lang)),
        KeyboardButton(text=label("catalog_run", lang)),
        KeyboardButton(text=label("products_back", lang)),
        KeyboardButton(text=label("settings_back", lang)),
    ]
    return ReplyKeyboardMarkup(
        keyboard=_chunk_rows(buttons),
        resize_keyboard=True,
        is_persistent=True,
    )


def target_edit_keyboard(lang: str | None = "en") -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text=label("edit_dest", lang))],
        [
            KeyboardButton(text=label("slot_1", lang)),
            KeyboardButton(text=label("slot_2", lang)),
            KeyboardButton(text=label("slot_3", lang)),
        ],
    ]
    rows.extend(
        _chunk_rows(
            [
                KeyboardButton(text=label("nav_back", lang)),
                KeyboardButton(text=label("settings_back", lang)),
            ]
        )
    )
    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        is_persistent=True,
    )


def slot_edit_keyboard(lang: str | None = "en") -> ReplyKeyboardMarkup:
    buttons = [
        KeyboardButton(text=label("toggle_slot_enabled", lang)),
        KeyboardButton(text=label("edit_dest", lang)),
        KeyboardButton(text=label("edit_template", lang)),
        KeyboardButton(text=label("edit_schedule", lang)),
        KeyboardButton(text=label("edit_rules", lang)),
        KeyboardButton(text=label("edit_slot_kind", lang)),
        KeyboardButton(text=label("nav_back", lang)),
        KeyboardButton(text=label("settings_back", lang)),
    ]
    return ReplyKeyboardMarkup(
        keyboard=_chunk_rows(buttons),
        resize_keyboard=True,
        is_persistent=True,
    )


def panel_edit_keyboard(lang: str | None = "en") -> ReplyKeyboardMarkup:
    buttons = _kb_buttons(
        "panel",
        [
            "edit_panel_url",
            "edit_panel_token",
            "edit_panel_inbound",
            "settings_back",
        ],
        lang,
    )
    return ReplyKeyboardMarkup(
        keyboard=_chunk_rows(buttons),
        resize_keyboard=True,
        is_persistent=True,
    )


def control_home_keyboard(lang: str | None = "en") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=label("list_agents", lang)),
                KeyboardButton(text=label("add_agent", lang)),
            ],
            [
                KeyboardButton(text=label("set_active", lang)),
                KeyboardButton(text=label("test_agent", lang)),
            ],
            [
                KeyboardButton(text=label("config_agent", lang)),
                KeyboardButton(text=label("support_agent", lang)),
            ],
            [
                KeyboardButton(text=label("api_mgmt", lang)),
                KeyboardButton(text=label("chat_agent", lang)),
            ],
            [
                KeyboardButton(text=label("failover", lang)),
                KeyboardButton(text=label("return_primary", lang)),
            ],
            [
                KeyboardButton(text=label("token_monitor", lang)),
                KeyboardButton(text=label("audit_log", lang)),
            ],
            [
                KeyboardButton(text=label("settings_back", lang)),
                KeyboardButton(text=label("stats_back", lang)),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Agent & API",
    )


def cancel_keyboard(lang: str | None = "en") -> ReplyKeyboardMarkup:
    """Keyboard for admin value-input steps."""
    buttons = [
        KeyboardButton(text=label("cancel", lang)),
        KeyboardButton(text=label("nav_back", lang)),
        KeyboardButton(text=label("settings_back", lang)),
    ]
    return ReplyKeyboardMarkup(
        keyboard=_chunk_rows(buttons),
        resize_keyboard=True,
        is_persistent=True,
    )


def skip_keyboard(lang: str | None = "en") -> ReplyKeyboardMarkup:
    buttons = [
        KeyboardButton(text=label("skip", lang)),
        KeyboardButton(text=label("cancel", lang)),
        KeyboardButton(text=label("nav_back", lang)),
        KeyboardButton(text=label("settings_back", lang)),
    ]
    return ReplyKeyboardMarkup(
        keyboard=_chunk_rows(buttons),
        resize_keyboard=True,
        is_persistent=True,
    )


def role_keyboard(lang: str | None = "en") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=label("role_primary", lang)),
                KeyboardButton(text=label("role_secondary", lang)),
            ],
            [
                KeyboardButton(text=label("role_backup", lang)),
                KeyboardButton(text=label("role_support", lang)),
            ],
            [KeyboardButton(text=label("cancel", lang))],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def agent_pick_keyboard(labels: list[str], lang: str | None = "en") -> ReplyKeyboardMarkup:
    rows: list[list[KeyboardButton]] = [[KeyboardButton(text=lab)] for lab in labels[:20]]
    rows.append([KeyboardButton(text=label("control_home", lang))])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)


def chat_with_agent_keyboard(lang: str | None = "en") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=label("upload_hint", lang))],
            [
                KeyboardButton(text=label("clear_chat", lang)),
                KeyboardButton(text=label("end_chat", lang)),
            ],
            [KeyboardButton(text=label("control_home", lang))],
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="💬 Message Agent…",
    )


def api_mgmt_keyboard(lang: str | None = "en") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=label("api_add", lang)),
                KeyboardButton(text=label("api_list", lang)),
            ],
            [
                KeyboardButton(text=label("api_test", lang)),
                KeyboardButton(text=label("api_delete", lang)),
            ],
            [KeyboardButton(text=label("control_home", lang))],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


# Backward-compatible aliases (English) for any leftover imports
BTN_CHANGE_AGENT_API = _LABELS["change_agent_api"]["en"]
BTN_STATS_REPORT = _LABELS["stats_report"]["en"]
BTN_STATS_BACK = _LABELS["stats_back"]["en"]
BTN_ADD_AGENT = _LABELS["add_agent"]["en"]
BTN_LIST_AGENTS = _LABELS["list_agents"]["en"]
BTN_SET_ACTIVE = _LABELS["set_active"]["en"]
BTN_TEST_AGENT = _LABELS["test_agent"]["en"]
BTN_CONFIG_AGENT = _LABELS["config_agent"]["en"]
BTN_SUPPORT_AGENT = _LABELS["support_agent"]["en"]
BTN_API_MGMT = _LABELS["api_mgmt"]["en"]
BTN_CHAT_AGENT = _LABELS["chat_agent"]["en"]
BTN_FAILOVER = _LABELS["failover"]["en"]
BTN_RETURN_PRIMARY = _LABELS["return_primary"]["en"]
BTN_AUDIT_LOG = _LABELS["audit_log"]["en"]
BTN_TOKEN_MONITOR = _LABELS["token_monitor"]["en"]
BTN_CONTROL_HOME = _LABELS["control_home"]["en"]
BTN_CANCEL = _LABELS["cancel"]["en"]
BTN_SKIP = _LABELS["skip"]["en"]
BTN_CLEAR_CHAT = _LABELS["clear_chat"]["en"]
BTN_END_CHAT = _LABELS["end_chat"]["en"]
BTN_UPLOAD_HINT = _LABELS["upload_hint"]["en"]
BTN_API_ADD = _LABELS["api_add"]["en"]
BTN_API_LIST = _LABELS["api_list"]["en"]
BTN_API_TEST = _LABELS["api_test"]["en"]
BTN_API_DELETE = _LABELS["api_delete"]["en"]
BTN_ROLE_PRIMARY = _LABELS["role_primary"]["en"]
BTN_ROLE_SECONDARY = _LABELS["role_secondary"]["en"]
BTN_ROLE_BACKUP = _LABELS["role_backup"]["en"]
BTN_ROLE_SUPPORT = _LABELS["role_support"]["en"]
