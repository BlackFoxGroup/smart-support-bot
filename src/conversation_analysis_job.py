"""Analyze private chats and generate multilingual insight posts."""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from aiogram import Bot

from src.ai.client import AIClient
from src.config import Settings
from src.storage.bot_settings import BotSettingsStore

IRAN_TZ = ZoneInfo("Asia/Tehran")
log = logging.getLogger("blackfox-agent-bot.convo-analysis")


async def _resolve_test_chat(
    settings: Settings, bot_settings: BotSettingsStore | None
) -> str:
    if bot_settings is not None:
        return await bot_settings.effective_test_chat_id(settings)
    return settings.convo_analysis_chat_id


async def _resolve_test_times(
    settings: Settings, bot_settings: BotSettingsStore | None
) -> str:
    if bot_settings is not None:
        return await bot_settings.effective_test_times(settings)
    return settings.convo_analysis_times


@dataclass(slots=True)
class TopicInsight:
    topic: str
    occurrences: int
    users: int
    severity: str
    priority_score: int
    category: str
    sample_needs: list[str]


TOPIC_RULES: dict[str, tuple[str, ...]] = {
    "ssh_connectivity": ("ssh", "connect ssh", "authentication", "expired password"),
    "full_deploy": ("full deploy", "deploy", "setup central"),
    "exit_server": ("add exit", "exit server", "node"),
    "panel_3xui": ("3x-ui", "panel", "inbound", "outbound"),
    "license_activation": ("license", "registration", "activate", "ai pro", "pro mode"),
    "wireguard_link": ("wireguard", "config", "subscription", "qr"),
    "telegram_bot_usage": ("bot", "group", "topic", "announce", "map_topic"),
}

REQUIRED_SECTIONS = ("📌", "📅", "🔎", "❓", "✅", "🛠", "💡", "🆘")
FORBIDDEN_RECOMMENDATION_PHRASES = (
    "یک آموزش برای این موضوع ایجاد شود",
    "یک راهنمای مرحله‌ای پیشنهاد می‌شود",
    "بهتر است آموزش مربوط به این مشکل منتشر شود",
    "کاربران به راهنمایی بیشتری نیاز دارند",
    "این موضوع ارزش تولید محتوای آموزشی دارد",
    "publish a focused tutorial",
    "recommendation:",
)
FORBIDDEN_INTERNAL_ANALYSIS_PHRASES = (
    "occurrences",
    "users:",
    "severity",
    "threshold",
    "الگوریتم",
    "حدنصاب",
    "تعداد پیام",
    "تعداد کاربران",
)

AI_HANDLE = "@BlackFox_Agent_Bot"
SUPPORT_HANDLE = "@HiBlackFoxVpn"

TOPIC_CATEGORY: dict[str, str] = {
    "ssh_connectivity": "support",
    "full_deploy": "education",
    "exit_server": "education",
    "panel_3xui": "education",
    "license_activation": "education",
    "wireguard_link": "support",
    "telegram_bot_usage": "education",
}


def _parse_times(raw: str) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    for token in (raw or "").split(","):
        token = token.strip()
        if not token:
            continue
        parts = token.split(":")
        if len(parts) != 2:
            continue
        try:
            h = int(parts[0])
            m = int(parts[1])
        except ValueError:
            continue
        if 0 <= h <= 23 and 0 <= m <= 59:
            out.append((h, m))
    return out or [(12, 30)]


def _next_tick(now: datetime, hhmm: list[tuple[int, int]]) -> datetime:
    base = now.astimezone(IRAN_TZ)
    cands = []
    for h, m in hhmm:
        dt = base.replace(hour=h, minute=m, second=0, microsecond=0)
        if dt <= base:
            dt += timedelta(days=1)
        cands.append(dt)
    return min(cands)


def _normalize_text(text: str) -> str:
    return " ".join((text or "").lower().split())


def _severity(occ: int, users: int) -> str:
    score = occ + (users * 2)
    if score >= 18:
        return "critical"
    if score >= 10:
        return "high"
    if score >= 5:
        return "medium"
    return "low"


def _priority_score(topic: str, occ: int, users: int, sample_needs: list[str]) -> int:
    # Weighted scoring: repetition, affected users, educational demand, business impact.
    usage_impact_topics = {"ssh_connectivity", "wireguard_link", "license_activation", "full_deploy"}
    demand_hits = sum(1 for s in sample_needs if any(k in _normalize_text(s) for k in ("how", "چطور", "راهنما", "guide", "help")))
    score = min(40, occ * 6) + min(30, users * 8) + min(15, demand_hits * 5)
    if topic in usage_impact_topics:
        score += 15
    return min(100, score)


def _read_user_messages(path: Path) -> list[tuple[str, str]]:
    if not path.is_file():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    users = (raw or {}).get("users") or {}
    out: list[tuple[str, str]] = []
    for user_id, row in users.items():
        if not isinstance(row, dict):
            continue
        anon = hashlib.sha256(str(user_id).encode("utf-8")).hexdigest()[:10]
        for item in row.get("chat_history") or []:
            if not isinstance(item, dict):
                continue
            if str(item.get("role", "")).lower() != "user":
                continue
            txt = str(item.get("content", "")).strip()
            if txt:
                out.append((anon, txt[:1200]))
    return out


def _load_topic_map(settings: Settings) -> tuple[int | None, dict[str, int]]:
    """Read forum topic mapping from knowledge/group_community.json."""
    path = settings.knowledge_root / "group_community.json"
    if not path.is_file():
        return None, {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None, {}
    chat_id_raw = (raw or {}).get("group_chat_id")
    chat_id: int | None
    try:
        chat_id = int(chat_id_raw) if chat_id_raw is not None else None
    except (TypeError, ValueError):
        chat_id = None
    topic_map_raw = (raw or {}).get("forum_topics") or {}
    out: dict[str, int] = {}
    if isinstance(topic_map_raw, dict):
        for lang in ("fa", "en", "ru", "zh"):
            try:
                tid = int(topic_map_raw.get(lang))
            except (TypeError, ValueError):
                continue
            out[lang] = tid
    return chat_id, out


def _memory_path(settings: Settings) -> Path:
    return settings.data_dir / "convo_resolution_memory.json"


def _store_resolution_memory(
    settings: Settings,
    insight: TopicInsight,
    posts: dict[str, str],
    *,
    result: str,
    success: bool,
) -> None:
    path = _memory_path(settings)
    try:
        raw = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {"items": []}
    except Exception:
        raw = {"items": []}
    items = raw.get("items") if isinstance(raw, dict) else []
    if not isinstance(items, list):
        items = []
    items.append(
        {
            "at": datetime.now(IRAN_TZ).isoformat(),
            "title": posts.get("fa", "").splitlines()[0] if posts.get("fa") else insight.topic,
            "category": insight.category,
            "topic": insight.topic,
            "cause": "workflow-prerequisite-or-step-order",
            "solution": "official-flow-with-prerequisites",
            "steps": "private-chat-start->feature-menu->prerequisites->run->verify->support-if-needed",
            "result": result,
            "success": bool(success),
        }
    )
    path.write_text(json.dumps({"items": items[-500:]}, ensure_ascii=False, indent=2), encoding="utf-8")


def _build_insights(messages: list[tuple[str, str]]) -> list[TopicInsight]:
    bucket: dict[str, dict[str, object]] = {}
    for user, text in messages:
        n = _normalize_text(text)
        for topic, keys in TOPIC_RULES.items():
            if not any(k in n for k in keys):
                continue
            row = bucket.setdefault(topic, {"occ": 0, "users": set(), "samples": []})
            row["occ"] = int(row["occ"]) + 1
            cast_users = row["users"]
            if isinstance(cast_users, set):
                cast_users.add(user)
            cast_samples = row["samples"]
            if isinstance(cast_samples, list) and len(cast_samples) < 5:
                cast_samples.append(text)
    out: list[TopicInsight] = []
    for topic, row in bucket.items():
        occ = int(row["occ"])
        users = len(row["users"]) if isinstance(row["users"], set) else 0
        samples = row["samples"] if isinstance(row["samples"], list) else []
        priority = _priority_score(topic, occ, users, [str(s) for s in samples[:3]])
        out.append(
            TopicInsight(
                topic=topic,
                occurrences=occ,
                users=users,
                severity=_severity(occ, users),
                priority_score=priority,
                category=TOPIC_CATEGORY.get(topic, "education"),
                sample_needs=[str(s) for s in samples[:3]],
            )
        )
    out.sort(key=lambda x: x.priority_score, reverse=True)
    return out


def _language_ratio(text: str, lang: str) -> float:
    if not text:
        return 0.0
    if lang == "fa":
        hits = re.findall(r"[\u0600-\u06FF]", text)
    elif lang == "ru":
        hits = re.findall(r"[\u0400-\u04FF]", text)
    elif lang == "zh":
        hits = re.findall(r"[\u4E00-\u9FFF]", text)
    else:  # en
        hits = re.findall(r"[A-Za-z]", text)
    letters = re.findall(r"[A-Za-z\u0400-\u04FF\u0600-\u06FF\u4E00-\u9FFF]", text)
    return len(hits) / max(1, len(letters))


def _is_complete_post(text: str) -> bool:
    if not text or len(text.strip()) < 220:
        return False
    if not all(section in text for section in REQUIRED_SECTIONS):
        return False
    # Step-by-step content must be concrete and executable.
    step_markers = re.findall(r"(?:^|\n)\s*(?:\d+[\.\)]|-\s)", text)
    if len(step_markers) < 3:
        return False
    lowered = text.lower()
    if any(p.lower() in lowered for p in FORBIDDEN_RECOMMENDATION_PHRASES):
        return False
    if any(p.lower() in lowered for p in FORBIDDEN_INTERNAL_ANALYSIS_PHRASES):
        return False
    return True


def _validate_multilingual_posts(posts: dict[str, str]) -> bool:
    if not all(posts.get(k, "").strip() for k in ("fa", "en", "ru", "zh")):
        return False
    for lang in ("fa", "en", "ru", "zh"):
        body = posts[lang]
        if not _is_complete_post(body):
            return False
        ratio = _language_ratio(body, lang)
        if ratio < 0.45:
            return False
    return True


async def _generate_multilingual_post(ai: AIClient, insight: TopicInsight) -> dict[str, str]:
    _ = ai
    day = datetime.now(IRAN_TZ).strftime("%Y-%m-%d")
    topic_title_fa = {
        "ssh_connectivity": "رفع مشکل عدم اتصال ربات به سرور (SSH)",
        "full_deploy": "حل خطاهای رایج Full Deploy",
        "exit_server": "آموزش صحیح افزودن Exit Server",
        "panel_3xui": "رفع ابهام تنظیمات پنل 3X-UI",
        "license_activation": "آموزش فعال‌سازی صحیح License",
        "wireguard_link": "رفع مشکل لینک اشتراک و WireGuard",
        "telegram_bot_usage": "آموزش استفاده صحیح از ربات تلگرام",
    }.get(insight.topic, "آموزش رفع مشکل پرتکرار کاربران")

    fa = (
        f"📌 **{topic_title_fa}**\n\n"
        "🔎 مشکل چیست؟\n"
        "کاربر در مسیر اجرای این بخش به خطا می‌رسد یا نتیجه مورد انتظار را دریافت نمی‌کند.\n\n"
        "❓ دلیل ایجاد مشکل:\n"
        "معمولاً به‌خاطر جا افتادن پیش‌نیاز، انتخاب مسیر نادرست منو، یا اجرای مراحل خارج از ترتیب صحیح رخ می‌دهد.\n\n"
        "✅ راه‌حل:\n"
        "> مسیر رسمی همان قابلیت را از چت خصوصی ربات اجرا کنید، پیش‌نیازها را کامل کنید و سپس عملیات اصلی را دوباره انجام دهید.\n\n"
        "🛠 آموزش مرحله‌به‌مرحله:\n"
        "1. وارد چت خصوصی ربات شوید و `/start` را بزنید.\n"
        "2. زبان را انتخاب کنید و فقط از منوی مرتبط با همان مشکل وارد شوید.\n"
        "3. پیش‌نیازها را کامل کنید (اتصال، دسترسی، اطلاعات لازم).\n"
        "4. عملیات اصلی را اجرا کنید و پیام موفقیت را بررسی کنید.\n"
        "5. اگر خطا باقی بود، متن دقیق خطا + اسکرین‌شات را کپی کنید.\n\n"
        "💡 نکته مهم:\n"
        "از جابه‌جایی بین منوها در میانه عملیات خودداری کنید تا وضعیت مرحله‌ها به‌هم نخورد.\n\n"
        "🆘 اگر مشکل حل نشد:\n"
        "ابتدا سوال خود را در چت خصوصی AI ارسال کنید تا راهنمایی و آموزش لازم را دریافت کنید.\n"
        "اگر پس از دریافت راهنمایی AI مشکل همچنان باقی بود، برای بررسی بیشتر با اکانت پشتیبانی ارتباط بگیرید.\n\n"
        f"🤖 AI Assistant:\n{AI_HANDLE}\n\n"
        f"🛠 Support:\n{SUPPORT_HANDLE}\n\n"
        f"📅 تاریخ: {day}"
    )
    en = (
        "📌 **Fixing a Common User Workflow Failure**\n\n"
        "🔎 What is the problem?\n"
        "The user reaches an error or does not get the expected result while running this workflow.\n\n"
        "❓ Why does it happen?\n"
        "Typical causes are missing prerequisites, wrong menu path, or incorrect step order.\n\n"
        "✅ Solution:\n"
        "> Run the official flow for this feature in the bot private chat, complete prerequisites, then retry the main action.\n\n"
        "🛠 Step-by-step guide:\n"
        "1. Open private chat with the bot and send `/start`.\n"
        "2. Select your language and enter only the menu related to this issue.\n"
        "3. Complete prerequisites (connection, permissions, required inputs).\n"
        "4. Execute the main operation and check the success output.\n"
        "5. If it still fails, copy exact error text and screenshot.\n\n"
        "💡 Important tip:\n"
        "Avoid switching between unrelated menus while an operation is in progress.\n\n"
        "🆘 If not resolved:\n"
        "First ask AI in private chat and follow the guidance.\n"
        "If the issue still remains after AI guidance, contact support.\n\n"
        f"🤖 AI Assistant:\n{AI_HANDLE}\n\n"
        f"🛠 Support:\n{SUPPORT_HANDLE}\n\n"
        f"📅 تاریخ: {day}"
    )
    ru = (
        "📌 **Исправление частой проблемы в рабочем процессе**\n\n"
        "🔎 В чем проблема?\n"
        "Пользователь получает ошибку или не видит ожидаемый результат при выполнении этого сценария.\n\n"
        "❓ Почему это происходит?\n"
        "Чаще всего из-за пропущенных предусловий, неверного раздела меню или нарушенного порядка шагов.\n\n"
        "✅ Решение:\n"
        "> Выполните официальный сценарий функции в личном чате бота, завершите все предусловия и повторите основное действие.\n\n"
        "🛠 Пошаговая инструкция:\n"
        "1. Откройте личный чат с ботом и отправьте `/start`.\n"
        "2. Выберите язык и войдите только в раздел, связанный с проблемой.\n"
        "3. Проверьте предусловия (подключение, права, данные).\n"
        "4. Выполните основную операцию и проверьте сообщение об успехе.\n"
        "5. Если ошибка осталась, отправьте точный текст ошибки и скриншот.\n\n"
        "💡 Важный совет:\n"
        "Не переключайтесь между разными меню во время активного процесса.\n\n"
        "🆘 Если не решилось:\n"
        "Сначала обратитесь к AI в личном чате и выполните рекомендации.\n"
        "Если проблема остается после рекомендаций AI, свяжитесь с поддержкой.\n\n"
        f"🤖 AI Assistant:\n{AI_HANDLE}\n\n"
        f"🛠 Support:\n{SUPPORT_HANDLE}\n\n"
        f"📅 تاریخ: {day}"
    )
    zh = (
        "📌 **高频流程问题修复教程**\n\n"
        "🔎 问题是什么？\n"
        "用户在执行该流程时出现报错，或没有得到预期结果。\n\n"
        "❓ 为什么会发生？\n"
        "常见原因是前置条件未完成、菜单路径错误、或步骤顺序不正确。\n\n"
        "✅ 解决方案：\n"
        "> 在机器人私聊中按该功能的官方流程执行，先完成前置条件，再重试主操作。\n\n"
        "🛠 分步操作：\n"
        "1. 打开与机器人的私聊并发送 `/start`。\n"
        "2. 选择语言后，只进入与该问题相关的菜单。\n"
        "3. 完成前置条件（连接、权限、必要输入）。\n"
        "4. 执行主操作并检查成功提示。\n"
        "5. 若仍失败，请提交原始报错文本与截图。\n\n"
        "💡 重要提示：\n"
        "操作进行中不要在不同菜单之间来回切换。\n\n"
        "🆘 如果问题仍未解决：\n"
        "请先在私聊向 AI 提问并按指导操作。\n"
        "如果按照 AI 指导后问题仍存在，再联系支持。\n\n"
        f"🤖 AI Assistant:\n{AI_HANDLE}\n\n"
        f"🛠 Support:\n{SUPPORT_HANDLE}\n\n"
        f"📅 تاریخ: {day}"
    )
    posts = {"fa": fa, "en": en, "ru": ru, "zh": zh}
    return posts if _validate_multilingual_posts(posts) else {"fa": "", "en": "", "ru": "", "zh": ""}


async def run_conversation_analysis_job(
    settings: Settings,
    bot: Bot,
    bot_settings: BotSettingsStore | None = None,
) -> None:
    ai = AIClient(settings)
    await ai.start()
    try:
        while True:
            times_raw = await _resolve_test_times(settings, bot_settings)
            hhmm = _parse_times(times_raw)
            nxt = _next_tick(datetime.now(IRAN_TZ), hhmm)
            wait_seconds = max(1, int((nxt - datetime.now(IRAN_TZ)).total_seconds()))
            log.info("Conversation analysis next run %s (in %ss)", nxt.isoformat(), wait_seconds)
            await asyncio.sleep(wait_seconds)
            await run_conversation_analysis_once(
                settings, bot, ai=ai, bot_settings=bot_settings
            )
    finally:
        await ai.close()


async def run_conversation_analysis_once(
    settings: Settings,
    bot: Bot,
    ai: AIClient | None = None,
    bot_settings: BotSettingsStore | None = None,
) -> bool:
    chat_id = await _resolve_test_chat(settings, bot_settings)
    messages = _read_user_messages(settings.users_db_path)
    if not messages:
        await bot.send_message(
            chat_id=chat_id,
            text="🧪 [Test 3] No private-chat data yet for conversation analysis.",
            disable_notification=True,
        )
        return False
    insights = _build_insights(messages)
    if not insights:
        await bot.send_message(
            chat_id=chat_id,
            text="🧪 [Test 3] No significant recurring topics found yet.",
            disable_notification=True,
        )
        return False

    target = insights[0]
    from src.knowledge.source_catalog.questions import fingerprint, is_duplicate_post, record_post

    qfp = fingerprint(target.topic + " ".join(target.sample_needs[:2]))
    if is_duplicate_post(settings.data_dir, qfp, qfp):
        await bot.send_message(
            chat_id=chat_id,
            text="🧪 Repeated topic already published (fingerprint match). Skipped duplicate.",
            disable_notification=True,
        )
        return False

    from src.knowledge.product_catalogs import get_product, load_product_catalogs

    load_product_catalogs(settings.knowledge_root)
    inst = get_product("vpn-installer")
    if inst is not None and not inst.catalog_enabled:
        await bot.send_message(
            chat_id=chat_id,
            text="Product Catalog AI is disabled for vpn-installer. Educational generation skipped.",
            disable_notification=True,
        )
        return False
    if (
        target.occurrences < settings.convo_min_occurrences
        or target.users < settings.convo_min_users
        or target.priority_score < settings.convo_priority_threshold
    ):
        await bot.send_message(
            chat_id=chat_id,
            text=(
                "🧪 [تست ۳] موضوع هنوز به حدنصاب نرسیده است.\n"
                f"- occurrences: {target.occurrences} (min={settings.convo_min_occurrences})\n"
                f"- users: {target.users} (min={settings.convo_min_users})\n"
                f"- priority: {target.priority_score} (min={settings.convo_priority_threshold})"
            ),
            disable_notification=True,
        )
        return False
    local_ai = ai
    created_local_ai = False
    if local_ai is None:
        local_ai = AIClient(settings)
        await local_ai.start()
        created_local_ai = True
    try:
        posts = await _generate_multilingual_post(local_ai, target)
    finally:
        if created_local_ai:
            await local_ai.close()

    if not _validate_multilingual_posts(posts):
        await bot.send_message(
            chat_id=chat_id,
            text=(
                "🧪 [تست ۳] اطلاعات برای تولید آموزش قطعی کافی نبود یا کیفیت ۴ زبان کامل تأیید نشد.\n"
                "این موضوع برای بررسی بیشتر علامت‌گذاری شد و به عنوان آموزش نهایی منتشر نشد."
            ),
            disable_notification=True,
        )
        _store_resolution_memory(
            settings,
            target,
            posts,
            result="insufficient_or_invalid",
            success=False,
        )
        return False

    record_post(settings.data_dir, question_fp=qfp, content_fp=qfp, langs=["fa", "en", "ru", "zh"])

    summary = (
        "🧪 [تست ۳] خلاصه تحلیل مکالمات کاربران\n\n"
        f"- موضوع: {target.topic}\n"
        f"- تعداد تکرار: {target.occurrences}\n"
        f"- تعداد کاربران درگیر: {target.users}\n"
        f"- سطح اهمیت: {target.severity}\n"
        "- خروجی تولیدشده: fa/en/ru/zh"
    )
    await bot.send_message(chat_id=chat_id, text=summary, disable_notification=True)
    if settings.convo_analysis_test_mode:
        await bot.send_message(chat_id=chat_id, text="🇮🇷\n" + posts["fa"][:3900], disable_notification=True)
        await bot.send_message(chat_id=chat_id, text="🇬🇧\n" + posts["en"][:3900], disable_notification=True)
        await bot.send_message(chat_id=chat_id, text="🇷🇺\n" + posts["ru"][:3900], disable_notification=True)
        await bot.send_message(chat_id=chat_id, text="🇨🇳\n" + posts["zh"][:3900], disable_notification=True)
        _store_resolution_memory(
            settings,
            target,
            posts,
            result="test_sent_to_support",
            success=True,
        )
    else:
        sent = await publish_analysis_to_group_topics(settings, bot, posts)
        await bot.send_message(
            chat_id=chat_id,
            text=f"✅ Published analysis post to {sent} mapped topics.",
            disable_notification=True,
        )
        _store_resolution_memory(
            settings,
            target,
            posts,
            result=f"published_to_topics:{sent}",
            success=sent > 0,
        )
    from src.job_status import record_job

    record_job(settings.data_dir, "convo_analysis", ok=True, detail=target.topic[:120])
    return True


async def publish_analysis_to_group_topics(settings: Settings, bot: Bot, posts: dict[str, str]) -> int:
    """Send each language to its own mapped forum topic."""
    chat_id, topic_map = _load_topic_map(settings)
    if chat_id is None or not topic_map:
        return 0
    sent = 0
    for lang in ("fa", "en", "ru", "zh"):
        tid = topic_map.get(lang)
        body = posts.get(lang, "").strip()
        if not tid or not body:
            continue
        await bot.send_message(
            chat_id=chat_id,
            message_thread_id=tid,
            text=body[:3900],
            disable_notification=(lang in {"ru", "zh"}),
        )
        sent += 1
    return sent

