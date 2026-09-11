"""Manager UI strings. fa / en / ru / zh."""

from __future__ import annotations

LANGS = ("fa", "en", "ru", "zh")
LABELS = {"fa": "فارسی", "en": "English", "ru": "Русский", "zh": "中文"}

T: dict[str, dict[str, str]] = {
    "title": {
        "fa": "مدیر پشتیبانی هوشمند",
        "en": "Smart Support Manager",
        "ru": "Менеджер Smart Support",
        "zh": "智能客服管理器",
    },
    "choose_lang": {
        "fa": "زبان را انتخاب کنید",
        "en": "Choose your language",
        "ru": "Выберите язык",
        "zh": "请选择语言",
    },
    "nav_dash": {"fa": "داشبورد", "en": "Dashboard", "ru": "Панель", "zh": "仪表盘"},
    "nav_products": {"fa": "محصولات", "en": "Products", "ru": "Продукты", "zh": "产品"},
    "nav_catalog": {"fa": "کاتالوگ", "en": "Catalog", "ru": "Каталог", "zh": "目录"},
    "nav_media": {"fa": "رسانه", "en": "Media", "ru": "Медиа", "zh": "媒体"},
    "nav_queue": {"fa": "صف آپلود", "en": "Upload Queue", "ru": "Очередь", "zh": "上传队列"},
    "nav_server": {"fa": "سرور", "en": "Server", "ru": "Сервер", "zh": "服务器"},
    "nav_history": {"fa": "تاریخچه", "en": "History", "ru": "История", "zh": "历史"},
    "nav_settings": {"fa": "تنظیمات", "en": "Settings", "ru": "Настройки", "zh": "设置"},
    "guide_title": {"fa": "راهنمای کوتاه", "en": "Quick guide", "ru": "Краткая справка", "zh": "简要说明"},
    "guide_body": {
        "fa": "۱) محصول را باز کنید. ۲) Scan تصاویر را بزنید. ۳) در صورت نیاز Auto-map یا نگاشت دستی. ۴) عکس جدید را انتخاب و Upload کنید. ۵) اگر سرور تنظیم باشد فایل با SFTP می‌رود؛ وگرنه کپی محلی. ۶) Build catalog فقط وقتی سورس محصول عوض شده. ۷) Rollback نسخه قبلی کاتالوگ را برمی‌گرداند.",
        "en": "1) Open a product. 2) Scan images. 3) Auto-map or map by hand. 4) Select files and Upload. 5) With SSH, files go by SFTP; otherwise a local copy. 6) Build catalog only after source changes. 7) Rollback restores the previous catalog.",
        "ru": "1) Откройте продукт. 2) Сканируйте изображения. 3) Auto-map или ручная привязка. 4) Выберите файлы и Upload. 5) При SSH файлы уходят по SFTP, иначе локальная копия. 6) Build catalog — только после изменения исходников. 7) Rollback вернёт предыдущий каталог.",
        "zh": "1）打开产品。2）扫描图片。3）自动或手动映射。4）选择文件并上传。5）已配置 SSH 时走 SFTP，否则本地复制。6）源码变更后再构建目录。7）回滚恢复上一版目录。",
    },
    "scan": {"fa": "اسکن تصاویر", "en": "Scan images", "ru": "Сканировать", "zh": "扫描图片"},
    "map": {"fa": "نگاشت خودکار", "en": "Auto-map", "ru": "Автопривязка", "zh": "自动映射"},
    "catalog": {"fa": "ساخت کاتالوگ", "en": "Build catalog", "ru": "Собрать каталог", "zh": "构建目录"},
    "upload": {"fa": "صف رسانه", "en": "Queue media", "ru": "В очередь", "zh": "加入队列"},
    "rollback": {"fa": "بازگشت نسخه", "en": "Rollback", "ru": "Откат", "zh": "回滚"},
    "toggle": {"fa": "کاتالوگ AI", "en": "Toggle Catalog AI", "ru": "Каталог ИИ", "zh": "开关目录 AI"},
    "ok_scan": {"fa": "اسکن انجام شد.", "en": "Scan finished.", "ru": "Сканирование готово.", "zh": "扫描完成。"},
    "ok_map": {"fa": "نگاشت انجام شد.", "en": "Mapping finished.", "ru": "Привязка готова.", "zh": "映射完成。"},
    "ok_catalog": {"fa": "کاتالوگ به‌روز شد.", "en": "Catalog updated.", "ru": "Каталог обновлён.", "zh": "目录已更新。"},
    "ok_rollback": {"fa": "بازگشت انجام شد.", "en": "Rollback done.", "ru": "Откат выполнен.", "zh": "已回滚。"},
    "ok_toggle": {"fa": "تنظیم کاتالوگ عوض شد.", "en": "Catalog AI toggled.", "ru": "Каталог ИИ переключён.", "zh": "目录 AI 已切换。"},
    "ok_queue": {"fa": "صف پردازش شد.", "en": "Queue processed.", "ru": "Очередь обработана.", "zh": "队列已处理。"},
    "err_source": {"fa": "پوشهٔ سورس پیدا نشد.", "en": "Source folder missing.", "ru": "Нет папки исходников.", "zh": "找不到源目录。"},
    "err_rollback": {"fa": "نسخهٔ قبلی نیست.", "en": "No previous version.", "ru": "Нет предыдущей версии.", "zh": "没有上一版本。"},
}


def t(lang: str, key: str) -> str:
    row = T.get(key) or {}
    code = lang if lang in LANGS else "en"
    return row.get(code) or row.get("en") or key
