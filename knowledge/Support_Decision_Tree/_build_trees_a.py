# -*- coding: utf-8 -*-
"""Build Support Decision Tree JSON packs (FA/EN/RU/ZH)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def T(fa, en, ru, zh):
    return {"fa": fa, "en": en, "ru": ru, "zh": zh}


def E(fa, en, ru, zh):
    return {"fa": fa, "en": en, "ru": ru, "zh": zh}


def ans(next_id, fa, en, ru, zh):
    return {"next": next_id, "label": T(fa, en, ru, zh)}


def question(text, answers):
    return {"type": "question", "text": text, "answers": answers}


def action(step, action_t, solution_t, nxt, if_unresolved="ask_more"):
    return {
        "type": "action",
        "step": step,
        "action": action_t,
        "solution": solution_t,
        "next": nxt,
        "if_unresolved": if_unresolved,
    }


def escalate(ask_for, final_solution, related_intents=None):
    return {
        "type": "escalate",
        "ask_for": ask_for,
        "final_solution": final_solution,
        "related_intents": related_intents or [],
    }


def end_ok(final_solution):
    return {"type": "resolved", "final_solution": final_solution}


META = {
    "product": "Black Fox VPN Installer",
    "schema_version": "1.0.0",
    "languages": ["fa", "en", "ru", "zh"],
    "intent_db": "AI_BOT_DATABASE/",
    "notes": [
        "Black Fox is an ops Installer (SSH/WireGuard/3X-UI), not a consumer browse VPN client.",
        "Connection trees focus on SSH, hubs, Proxy, panel reachability — not 'VPN connect button'.",
        "Never invent versions/prices/hosters. VPS only via FoxNext.net → Partners.",
    ],
}


# ---------------------------------------------------------------------------
# Installation
# ---------------------------------------------------------------------------
INSTALLATION = {
    "meta": {**META, "file": "Installation_Troubleshooting.json"},
    "trees": [
        {
            "id": "installation_failed",
            "category": "Installation",
            "priority": "critical",
            "related_intents": ["download_installer", "install_setup", "setup_vs_portable"],
            "title": T("نصب نشدن برنامه", "Installer will not install", "Программа не устанавливается", "程序无法安装"),
            "user_problem_examples": E(
                ["نصب نمیشه", "Setup ارور میده", "فایل باز نمیشه", "آنتی‌ویروس حذف کرد", "دسترسی ادمین میخواد"],
                ["won't install", "Setup error", "blocked by antivirus", "need administrator", "corrupt download"],
                ["не устанавливается", "ошибка Setup", "антивирус блокирует", "нужен Administrator", "битый файл"],
                ["安装不了", "Setup报错", "杀毒拦截", "需要管理员", "文件损坏"],
            ),
            "entry_node": "q_admin",
            "nodes": {
                "q_admin": question(
                    T("آیا Setup را با Run as administrator اجرا کردید؟",
                      "Did you run Setup as Administrator?",
                      "Запускали Setup от имени администратора?",
                      "是否以管理员身份运行了 Setup？"),
                    {
                        "yes": ans("q_av", "بله", "Yes", "Да", "是"),
                        "no": ans("a_admin", "خیر", "No", "Нет", "否"),
                    },
                ),
                "a_admin": action(
                    1,
                    T("اجرا با Administrator", "Run as Administrator", "Запуск от администратора", "以管理员运行"),
                    T("روی Setup راست‌کلیک → Run as administrator. اگر UAC آمد Confirm کنید.",
                      "Right-click Setup → Run as administrator. Confirm UAC.",
                      "ПКМ по Setup → Запуск от имени администратора. Подтвердите UAC.",
                      "右键 Setup → 以管理员身份运行，并确认 UAC。"),
                    "q_av",
                ),
                "q_av": question(
                    T("آیا آنتی‌ویروس / Windows Defender فایل را قرنطینه یا حذف کرده؟",
                      "Did antivirus / Windows Defender quarantine or delete the file?",
                      "Антивирус / Windows Defender поместил файл в карантин или удалил?",
                      "杀毒 / Windows Defender 是否隔离或删除了文件？"),
                    {
                        "yes": ans("a_av", "بله / مشکوکم", "Yes / maybe", "Да / возможно", "是 / 可能"),
                        "no": ans("q_file", "خیر", "No", "Нет", "否"),
                    },
                ),
                "a_av": action(
                    2,
                    T("استثنای Defender/آنتی‌ویروس", "Allow in Defender/antivirus", "Исключение в Defender/антивирусе", "杀毒放行"),
                    T("فایل را Restore کنید، برای Setup و پوشه نصب Exclusion بگذارید، دوباره از foxnext.net دانلود کنید.",
                      "Restore the file, add Exclusion for Setup and install folder, re-download from foxnext.net.",
                      "Восстановите файл, добавьте Exclusion для Setup и папки установки, скачайте снова с foxnext.net.",
                      "恢复文件，为 Setup 与安装目录添加排除项，并从 foxnext.net 重新下载。"),
                    "q_file",
                ),
                "q_file": question(
                    T("حجم/هش فایل با صفحه دانلود رسمی یکی است؟ دانلود کامل شد؟",
                      "Does file size match the official download page? Download complete?",
                      "Размер файла совпадает с официальной страницей? Загрузка завершена?",
                      "文件大小是否与官网一致？下载是否完整？"),
                    {
                        "yes": ans("q_net", "بله کامل است", "Yes complete", "Да, полный", "完整"),
                        "no": ans("a_redl", "ناقص / مطمئن نیستم", "Corrupt / unsure", "Битый / не уверен", "不完整 / 不确定"),
                    },
                ),
                "a_redl": action(
                    3,
                    T("دانلود مجدد رسمی", "Official re-download", "Повторная официальная загрузка", "官网重新下载"),
                    T("فقط از foxnext.net دوباره Setup را بگیرید؛ از mirror/تلگرام ناشناس پرهیز کنید.",
                      "Re-download Setup only from foxnext.net; avoid unknown mirrors/Telegram files.",
                      "Скачайте Setup только с foxnext.net; избегайте неизвестных зеркал/Telegram.",
                      "仅从 foxnext.net 重新下载 Setup；避免不明镜像/Telegram 文件。"),
                    "q_net",
                ),
                "q_net": question(
                    T("هنگام نصب اینترنت لازم/پایدار دارید؟ (برخی چک‌های اولیه به هاب وصل می‌شوند)",
                      "Do you have stable internet during install? (some checks may reach hubs)",
                      "Интернет стабилен во время установки? (часть проверок может ходить на хабы)",
                      "安装时网络是否稳定？（部分检查可能访问 Hub）"),
                    {
                        "yes": ans("a_retry", "بله", "Yes", "Да", "是"),
                        "no": ans("a_net", "خیر / قطع است", "No / unstable", "Нет / нестабилен", "否 / 不稳定"),
                    },
                ),
                "a_net": action(
                    4,
                    T("پایدار کردن اینترنت", "Stabilize internet", "Стабилизировать интернет", "稳定网络"),
                    T("شبکه پایدار یا هات‌اسپات امتحان کنید؛ بعد از نصب در صورت فیلتر از Proxy Settings داخل برنامه استفاده کنید.",
                      "Use a stable network/hotspot; after install use in-app Proxy Settings if filtered.",
                      "Используйте стабильную сеть/хотспот; после установки при фильтрации — Proxy Settings.",
                      "使用稳定网络/热点；安装后若被过滤，使用应用内 Proxy Settings。"),
                    "a_retry",
                ),
                "a_retry": action(
                    5,
                    T("تلاش نصب مجدد", "Retry install", "Повтор установки", "重试安装"),
                    T("Setup را دوباره با Administrator اجرا کنید. اگر باز هم شکست، متن خطای دقیق را ذخیره کنید.",
                      "Run Setup again as Administrator. If it still fails, save the exact error text.",
                      "Снова запустите Setup от администратора. Если снова ошибка — сохраните точный текст.",
                      "再次以管理员运行 Setup。若仍失败，保存确切错误原文。"),
                    "ask_more",
                    "ask_more",
                ),
                "ask_more": escalate(
                    [
                        T("متن کامل خطای Setup / اسکرین‌شات", "Full Setup error text / screenshot", "Полный текст ошибки Setup / скриншот", "Setup 完整错误原文/截图"),
                        T("نسخه Windows", "Windows version", "Версия Windows", "Windows 版本"),
                        T("نام آنتی‌ویروس", "Antivirus name", "Название антивируса", "杀毒软件名称"),
                    ],
                    T("اگر با Administrator + Exclusion + دانلود رسمی حل نشد، اسکرین خطا را به @HiBlackFoxVpn بفرستید.",
                      "If Administrator + Exclusion + official download still fail, send the error screenshot to @HiBlackFoxVpn.",
                      "Если Administrator + Exclusion + официальная загрузка не помогли — отправьте скрин в @HiBlackFoxVpn.",
                      "若管理员 + 排除项 + 官网下载仍失败，将错误截图发给 @HiBlackFoxVpn。"),
                    ["download_installer", "contact_support"],
                ),
            },
            "final_solution": T(
                "مسیر استاندارد نصب: دانلود رسمی → Administrator → Exclusion آنتی‌ویروس → Setup کامل.",
                "Standard install path: official download → Administrator → AV exclusion → complete Setup.",
                "Стандарт: официальная загрузка → Administrator → исключение AV → полный Setup.",
                "标准安装路径：官网下载 → 管理员 → 杀毒排除 → 完成 Setup。",
            ),
        },
        {
            "id": "app_wont_start",
            "category": "Installation",
            "priority": "high",
            "related_intents": ["install_setup", "force_update", "contact_support"],
            "title": T("اجرا نشدن برنامه", "App will not start", "Приложение не запускается", "程序无法启动"),
            "user_problem_examples": E(
                ["باز نمیشه", "کریش میکنه", "Startup error", "Permission", "همون لحظه بسته میشه"],
                ["won't open", "crash on start", "startup error", "permission denied", "closes immediately"],
                ["не открывается", "краш при старте", "ошибка запуска", "нет прав", "сразу закрывается"],
                ["打不开", "启动崩溃", "启动错误", "权限不足", "立刻退出"],
            ),
            "entry_node": "q_open",
            "nodes": {
                "q_open": question(
                    T("آیا پنجره Splash/برنامه لحظه‌ای ظاهر می‌شود یا هیچ‌چیز نمی‌آید؟",
                      "Does Splash/app flash briefly, or nothing appears at all?",
                      "Splash/окно мелькает или вообще ничего не появляется?",
                      "是闪一下 Splash/窗口，还是完全没有界面？"),
                    {
                        "flash": ans("a_dep", "چشمک می‌زند/کریش", "Flashes / crashes", "Мелькает / краш", "闪一下/崩溃"),
                        "nothing": ans("a_perm", "هیچی نمیاد", "Nothing appears", "Ничего нет", "完全没有"),
                    },
                ),
                "a_perm": action(
                    1,
                    T("مجوز و مسیر نصب", "Permissions and install path", "Права и путь установки", "权限与安装路径"),
                    T("از منوی Start با راست‌کلیک Run as administrator. مسیر نصب را در پوشه حفاظت‌شده عجیب نگذارید. SmartScreen را Allow کنید.",
                      "Start menu → Run as administrator. Avoid odd protected paths. Allow SmartScreen.",
                      "Пуск → от администратора. Не ставьте в странные защищённые пути. Разрешите SmartScreen.",
                      "开始菜单右键以管理员运行。避免异常受保护路径。允许 SmartScreen。"),
                    "a_reinstall",
                ),
                "a_dep": action(
                    1,
                    T("بررسی وابستگی / نسخه", "Check dependency / build", "Проверка зависимостей / сборки", "检查依赖/版本"),
                    T("اگر force update می‌آید اول Update کنید. Portable را از پوشه فقط‌خواندنی جابه‌جا نکنید. آنتی‌ویروس را موقتاً Exclusion بدهید.",
                      "If force-update appears, update first. Don't run Portable from a read-only folder. Add AV exclusion.",
                      "Если force update — сначала обновите. Не запускайте Portable из read-only. Добавьте Exclusion AV.",
                      "若出现强制更新先更新。不要从只读目录运行 Portable。添加杀毒排除。"),
                    "a_reinstall",
                ),
                "a_reinstall": action(
                    2,
                    T("نصب مجدد Setup", "Reinstall via Setup", "Переустановка через Setup", "通过 Setup 重装"),
                    T("Setup رسمی را دوباره نصب کنید (ترجیحاً غیر Portable برای پایداری).",
                      "Reinstall official Setup (prefer Setup over Portable for stability).",
                      "Переустановите официальный Setup (лучше Setup, не Portable).",
                      "重新安装官方 Setup（稳定性上优先 Setup 而非 Portable）。"),
                    "ask_more",
                ),
                "ask_more": escalate(
                    [
                        T("اسکرین/متن Startup error", "Startup error screenshot/text", "Скрин/текст ошибки запуска", "启动错误截图/原文"),
                        T("Setup یا Portable؟", "Setup or Portable?", "Setup или Portable?", "Setup 还是 Portable？"),
                        T("آیا دیالوگ Update اجباری می‌آید؟", "Any force-update dialog?", "Есть ли force-update диалог?", "是否有强制更新对话框？"),
                    ],
                    T("بدون لاگ Startup حدس نزنید؛ اسکرین را به پشتیبانی بفرستید.",
                      "Don't guess without startup log; send screenshot to support.",
                      "Без лога запуска не угадывайте; отправьте скрин в поддержку.",
                      "没有启动日志不要猜测；把截图发给支持。"),
                    ["force_update", "setup_vs_portable", "contact_support"],
                ),
            },
            "final_solution": T(
                "اجرا: Administrator + Exclusion + Setup رسمی؛ اگر Update اجباری است اول Update.",
                "Start path: Administrator + exclusion + official Setup; if force-update, update first.",
                "Запуск: Administrator + exclusion + официальный Setup; при force-update сначала обновите.",
                "启动路径：管理员 + 排除 + 官方 Setup；若强制更新则先更新。",
            ),
        },
    ],
}


# ---------------------------------------------------------------------------
# License
# ---------------------------------------------------------------------------
LICENSE = {
    "meta": {**META, "file": "License_Troubleshooting.json"},
    "trees": [
        {
            "id": "license_activation_failed",
            "category": "License",
            "priority": "critical",
            "related_intents": ["activate_license", "device_id", "claim_code", "reactivation", "need_activate"],
            "title": T("فعال‌سازی License ناموفق", "License activation failed", "Ошибка активации License", "License 激活失败"),
            "user_problem_examples": E(
                ["لایسنس فعال نمیشه", "کد نامعتبر", "Activation Failed", "claim already bound", "Device ID عوض شده"],
                ["license won't activate", "invalid code", "activation failed", "claim already bound", "device id changed"],
                ["лицензия не активируется", "неверный код", "activation failed", "claim already bound", "сменился device id"],
                ["License激活不了", "无效代码", "activation failed", "claim already bound", "Device ID变了"],
            ),
            "entry_node": "q_symptom",
            "nodes": {
                "q_symptom": question(
                    T("کدام پیام را می‌بینید؟",
                      "Which message do you see?",
                      "Какое сообщение видите?",
                      "你看到哪条提示？"),
                    {
                        "invalid": ans("a_invalid", "کد نامعتبر / Invalid", "Invalid code", "Неверный код", "无效代码"),
                        "bound": ans("a_bound", "claim already bound", "claim already bound", "claim already bound", "claim already bound"),
                        "hub": ans("a_hub", "به سرور فعال‌سازی وصل نمیشه", "Can't reach activation server", "Не достучаться до сервера активации", "连不上激活服务器"),
                        "device": ans("a_device", "Device ID عوض شده / بعد از فرمت", "Device ID changed / after reinstall", "Device ID сменился / после переустановки", "Device ID变更/重装后"),
                        "tier": ans("a_tier", "tier mismatch / سطح اشتباه", "tier mismatch / wrong tier", "tier mismatch / неверный тариф", "tier mismatch / 层级不对"),
                    },
                ),
                "a_invalid": action(
                    1,
                    T("کد کامل و سطح درست", "Full code + correct tier", "Полный код + верный тариф", "完整代码 + 正确层级"),
                    T("کد را کامل کپی کنید (BFXB/BFXP/BFXA/BFXQ). فاصله اضافه نگذارید. دکمه Activate همان سطح باشد.",
                      "Paste the full code (BFXB/BFXP/BFXA/BFXQ). No extra spaces. Use matching Activate tier button.",
                      "Вставьте полный код (BFXB/BFXP/BFXA/BFXQ). Без лишних пробелов. Кнопка Activate того же тарифа.",
                      "粘贴完整代码（BFXB/BFXP/BFXA/BFXQ），勿多余空格，Activate 按钮层级须匹配。"),
                    "q_retry_ok",
                ),
                "a_bound": action(
                    1,
                    T("claim قبلاً bind شده", "Claim already bound", "Claim уже привязан", "Claim 已绑定"),
                    T("روی همان دستگاه Reactivation را بزنید. اگر PC عوض شده با Device ID به پشتیبانی بروید؛ انتظار چاپ دوباره کد از TX نداشته باشید.",
                      "Use Reactivation on the same device. If PC changed, contact support with Device ID; TX usually won't reprint codes.",
                      "На том же устройстве — Reactivation. Если ПК другой — поддержка с Device ID; TX обычно не печатает коды снова.",
                      "在同一设备使用 Reactivation。若换了电脑，带 Device ID 找支持；TX 通常不会再次显示代码。"),
                    "q_retry_ok",
                ),
                "a_hub": action(
                    1,
                    T("دسترسی به هاب فعال‌سازی", "Reach activation hubs", "Доступ к хабам активации", "打通激活 Hub"),
                    T("اینترنت را چک کنید، Proxy Settings (Auto/Iran) را امتحان کنید. هاب‌ها: blackfoxupdate.ir و foxnext.net.",
                      "Check internet, try Proxy Settings (Auto/Iran). Hubs: blackfoxupdate.ir and foxnext.net.",
                      "Проверьте интернет, Proxy Settings (Auto/Iran). Хабы: blackfoxupdate.ir и foxnext.net.",
                      "检查网络，尝试 Proxy Settings（Auto/Iran）。Hub：blackfoxupdate.ir 与 foxnext.net。"),
                    "q_retry_ok",
                ),
                "a_device": action(
                    1,
                    T("بازیابی با Reactivation", "Restore via Reactivation", "Восстановление через Reactivation", "通过 Reactivation 恢复"),
                    T("Registration → Reactivation. اگر not found/expired شد Device ID + توضیح را برای پشتیبانی بفرستید.",
                      "Registration → Reactivation. If not found/expired, send Device ID + details to support.",
                      "Registration → Reactivation. Если not found/expired — Device ID + детали в поддержку.",
                      "Registration → Reactivation。若 not found/expired，将 Device ID + 说明发给支持。"),
                    "q_retry_ok",
                ),
                "a_tier": action(
                    1,
                    T("هم‌ترازی سطح", "Align tier", "Согласовать тариф", "对齐层级"),
                    T("کد Basic را روی Pro نزنید و برعکس. AI Pro جدا از Pro است (BFXA + quota).",
                      "Don't use a Basic code on Pro Activate (and vice versa). AI Pro is separate (BFXA + quota).",
                      "Не активируйте Basic-код кнопкой Pro (и наоборот). AI Pro отдельно (BFXA + quota).",
                      "不要用 Basic 码点 Pro Activate（反之亦然）。AI Pro 单独（BFXA + quota）。"),
                    "q_retry_ok",
                ),
                "q_retry_ok": question(
                    T("بعد از این کارها Activate موفق شد؟",
                      "Did Activate succeed after these steps?",
                      "После этих шагов Activate успешен?",
                      "按上述步骤后 Activate 成功了吗？"),
                    {
                        "yes": ans("ok", "بله", "Yes", "Да", "是"),
                        "no": ans("ask_more", "خیر", "No", "Нет", "否"),
                    },
                ),
                "ok": end_ok(T(
                    "لایسنس فعال شد. در صورت نیاز View را روی Basic/Pro/AI Pro بگذارید و عملیات را دوباره بزنید.",
                    "License active. Switch View to Basic/Pro/AI Pro if needed and retry the operation.",
                    "Лицензия активна. При необходимости переключите View на Basic/Pro/AI Pro и повторите операцию.",
                    "License 已激活。必要时将 View 切到 Basic/Pro/AI Pro 并重试操作。",
                )),
                "ask_more": escalate(
                    [
                        T("Device ID", "Device ID", "Device ID", "Device ID"),
                        T("متن دقیق خطا", "Exact error text", "Точный текст ошибки", "确切错误原文"),
                        T("پیشوند کد (بدون افشای کامل کد در چت عمومی)", "Code prefix only (don't paste full secret in public chats)", "Только префикс кода (не весь секрет в публичный чат)", "仅代码前缀（勿在公开聊天贴完整密钥）"),
                    ],
                    T("با Device ID + متن خطا به @HiBlackFoxVpn پیام دهید.",
                      "Message @HiBlackFoxVpn with Device ID + error text.",
                      "Напишите @HiBlackFoxVpn с Device ID + текстом ошибки.",
                      "将 Device ID + 错误原文发给 @HiBlackFoxVpn。"),
                    ["activate_license", "reactivation", "contact_support"],
                ),
            },
            "final_solution": T(
                "Activate درست = کد کامل + سطح درست + Device ID + دسترسی هاب (در صورت نیاز Proxy).",
                "Successful Activate = full code + matching tier + Device ID + hub reachability (Proxy if needed).",
                "Успешный Activate = полный код + нужный тариф + Device ID + доступ к хабу (при необходимости Proxy).",
                "成功 Activate = 完整代码 + 匹配层级 + Device ID + Hub 可达（必要时 Proxy）。",
            ),
        }
    ],
}


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------
UPDATE = {
    "meta": {**META, "file": "Update_Troubleshooting.json"},
    "trees": [
        {
            "id": "update_failed",
            "category": "Update",
            "priority": "high",
            "related_intents": ["force_update", "proxy_settings", "download_installer"],
            "title": T("مشکل Update", "Update problem", "Проблема Update", "Update 问题"),
            "user_problem_examples": E(
                ["آپدیت دانلود نمیشه", "force update", "نسخه قدیمی", "Update Server error", "چک آپدیت گیر کرده"],
                ["update won't download", "force update", "old version", "update server error", "check update stuck"],
                ["обновление не качается", "force update", "старая версия", "ошибка update server", "check update завис"],
                ["更新下不了", "强制更新", "版本太旧", "update server错误", "检查更新卡住"],
            ),
            "entry_node": "q_force",
            "nodes": {
                "q_force": question(
                    T("آیا برنامه با دیالوگ اجباری Update قفل شده (min version)؟",
                      "Is the app blocked by a force Update / minimum version dialog?",
                      "Приложение заблокировано диалогом force Update / min version?",
                      "是否被强制 Update / 最低版本对话框挡住？"),
                    {
                        "yes": ans("a_force", "بله قفل است", "Yes blocked", "Да, заблокировано", "是，被挡住"),
                        "no": ans("q_dl", "خیر فقط آپدیت دستی/شکست", "No, manual/failed update", "Нет, ручное/сбой", "否，只是手动/失败"),
                    },
                ),
                "a_force": action(
                    1,
                    T("Update اجباری", "Force update path", "Путь force update", "强制更新路径"),
                    T("از لینک رسمی داخل دیالوگ یا foxnext.net Setup جدید را بگیرید و نصب کنید. شماره نسخه را در چت اختراع نکنید.",
                      "Use the official link in the dialog or foxnext.net Setup, then install. Do not invent version numbers in chat.",
                      "Скачайте официальный Setup из диалога или foxnext.net и установите. Не выдумывайте номера версий.",
                      "通过对话框官方链接或 foxnext.net 下载新 Setup 并安装。聊天中不要编造版本号。"),
                    "q_after",
                ),
                "q_dl": question(
                    T("دانلود آپدیت fail می‌شود یا فقط چک آپدیت خطا می‌دهد؟",
                      "Does download fail, or only the update check fails?",
                      "Падает загрузка или только проверка обновлений?",
                      "是下载失败，还是仅检查更新失败？"),
                    {
                        "download": ans("a_proxy", "دانلود fail", "Download fails", "Падает загрузка", "下载失败"),
                        "check": ans("a_proxy", "چک/سرور آپدیت", "Check / update server", "Проверка / сервер", "检查/更新服务器"),
                    },
                ),
                "a_proxy": action(
                    2,
                    T("شبکه و Proxy به هاب", "Network + Proxy to hubs", "Сеть + Proxy к хабам", "网络 + Proxy 到 Hub"),
                    T("Proxy Settings را Auto/Iran کنید. هاب‌ها blackfoxupdate.ir و foxnext.net را در دسترس کنید. سپس Settings → Updates را دوباره بزنید.",
                      "Set Proxy Settings to Auto/Iran. Ensure hubs blackfoxupdate.ir / foxnext.net are reachable. Retry Settings → Updates.",
                      "Proxy Settings → Auto/Iran. Обеспечьте доступ к хабам. Повторите Settings → Updates.",
                      "将 Proxy Settings 设为 Auto/Iran，确保 Hub 可达，然后重试 Settings → Updates。"),
                    "q_after",
                ),
                "q_after": question(
                    T("بعد از نصب/تلاش مجدد، برنامه دیگر قفل Update نیست؟",
                      "After install/retry, is the app no longer update-blocked?",
                      "После установки/повтора приложение больше не заблокировано обновлением?",
                      "安装/重试后，是否已不再被更新挡住？"),
                    {
                        "yes": ans("ok", "بله", "Yes", "Да", "是"),
                        "no": ans("ask_more", "خیر", "No", "Нет", "否"),
                    },
                ),
                "ok": end_ok(T(
                    "Update انجام شد. در صورت نیاز برنامه را کامل ببندید و دوباره باز کنید.",
                    "Update completed. Fully quit and relaunch if needed.",
                    "Обновление выполнено. При необходимости полностью закройте и откройте снова.",
                    "更新完成。必要时完全退出后重开。",
                )),
                "ask_more": escalate(
                    [
                        T("متن دیالوگ Update", "Update dialog text", "Текст диалога Update", "Update 对话框原文"),
                        T("آیا Proxy را امتحان کردید؟", "Did you try Proxy?", "Пробовали Proxy?", "是否试过 Proxy？"),
                        T("Setup را از سایت رسمی گرفتید؟", "Downloaded Setup from official site?", "Setup с официального сайта?", "是否从官网下载 Setup？"),
                    ],
                    T("اسکرین دیالوگ Update + وضعیت Proxy را به پشتیبانی بفرستید.",
                      "Send Update dialog screenshot + Proxy status to support.",
                      "Отправьте скрин диалога Update + статус Proxy в поддержку.",
                      "将 Update 对话框截图 + Proxy 状态发给支持。"),
                    ["force_update", "proxy_settings", "contact_support"],
                ),
            },
            "final_solution": T(
                "Update = Setup رسمی + دسترسی هاب (Proxy در صورت فیلتر).",
                "Update = official Setup + hub reachability (Proxy if filtered).",
                "Update = официальный Setup + доступ к хабу (Proxy при фильтрации).",
                "Update = 官方 Setup + Hub 可达（被过滤时用 Proxy）。",
            ),
        }
    ],
}


def write(name, obj):
    path = ROOT / name
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", name, path.stat().st_size)


if __name__ == "__main__":
    write("Installation_Troubleshooting.json", INSTALLATION)
    write("License_Troubleshooting.json", LICENSE)
    write("Update_Troubleshooting.json", UPDATE)
    print("part A done")
