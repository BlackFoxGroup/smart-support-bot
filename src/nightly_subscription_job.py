"""Nightly 3x-ui account creator and Telegram notifier."""

from __future__ import annotations

import asyncio
import html
import io
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from aiogram import Bot
from aiogram.types import BufferedInputFile
import segno
import jdatetime
from PIL import Image, ImageDraw

from src.config import Settings
from src.panel_client import PanelAPIError, PanelClient
from src.storage.bot_settings import BotSettingsStore

IRAN_TZ = ZoneInfo("Asia/Tehran")
BOT_HANDLE = "@BlackFox_Agent_Bot"
GROUP_HANDLE = "@Black_Fox_Group/1"
SUPPORT_HANDLE = "@HiBlackFoxVpn"
BRAND_HANDLE = "@blackFoxVPNN"
TELEGRAM_QR_MAX_BYTES = 300 * 1024
TELEGRAM_QR_MIN_SIZE = 720


def _parse_hhmm_list(raw: str, fallback_hour: int = 21, fallback_minute: int = 0) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    for part in (raw or "").split(","):
        part = part.strip()
        if not part or ":" not in part:
            continue
        hh_s, mm_s = part.split(":", 1)
        try:
            hh, mm = int(hh_s), int(mm_s)
        except ValueError:
            continue
        if 0 <= hh <= 23 and 0 <= mm <= 59:
            out.append((hh, mm))
    if not out:
        out.append((fallback_hour, fallback_minute))
    return out


def _next_run_iran(
    settings: Settings,
    now: datetime | None = None,
    *,
    schedule_times: str | None = None,
) -> datetime:
    base = now.astimezone(IRAN_TZ) if now else datetime.now(IRAN_TZ)
    times = _parse_hhmm_list(
        schedule_times or settings.nightly_iran_time.strftime("%H:%M"),
        fallback_hour=settings.nightly_iran_time.hour,
        fallback_minute=settings.nightly_iran_time.minute,
    )
    # Nightly free config: use the first configured time (usually one slot).
    hh, mm = times[0]
    target = base.replace(hour=hh, minute=mm, second=0, microsecond=0)
    if target <= base:
        target += timedelta(days=1)
    return target


def _build_support_message(
    *,
    sub_link: str,
    template: str | None = None,
) -> str:
    shamsi_date = jdatetime.datetime.now().strftime("%Y/%m/%d")
    sub = html.escape(sub_link, quote=False)
    raw = (template or "").strip()
    if raw:
        # Prefer {sub}; keep {config} as alias for older templates.
        body = raw.replace("{sub}", f"<blockquote><code>{sub}</code></blockquote>")
        body = body.replace("{config}", f"<blockquote><code>{sub}</code></blockquote>")
        body = body.replace("{date}", shamsi_date)
        return body
    return (
        "🤖 سلام، من ربات هوش مصنوعی  Black Fox هستم 🦊\n\n"
        "🎁 به پاس قدردانی از همراهی شما عزیزان، یک اشتراک رایگان برای شما در کانال قرار داده‌ام.\n\n"
        "⏰ از این به بعد هر شب رأس ساعت ۹ شب همین‌جا منتظرتان هستم تا بتوانید از اشتراک رایگان Black Fox استفاده کنید.\n\n"
        "📢 لطفاً این پیام را با دوستان خود به اشتراک بگذارید تا آن‌ها هم بتوانند از این هدیه استفاده کنند.\n\n"
        "💡 همچنین خوشحال می‌شوم کاربران عزیز را برای استفاده از برنامهBlackFox Vpn Installer &amp; Android و امکانات آن راهنمایی کنم.\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "🔹 لینک Subscription:\n"
        "<blockquote><code>"
        f"{sub}"
        "</code></blockquote>\n\n"
        "📱 QR کد Subscription را در تصویر ببینید.\n\n"
        "━━━━━━━━━━━━━━\n\n"
        f"🤖 ربات: {BOT_HANDLE}\n"
        f"👥 گروه کاربران: {GROUP_HANDLE}\n"
        f"🛠 پشتیبانی: {SUPPORT_HANDLE}\n"
        f"📢 کانال رسمی: {BRAND_HANDLE}\n\n"
        "🦊 با Black Fox همیشه امن و متصل بمانید.\n\n"
        f"📅 تاریخ: {shamsi_date}"
    )


def _build_qr_png(data: str) -> bytes:
    qr = segno.make(data, error="m")
    # Build a rectangular card so Telegram preview is less visually dominant.
    card_w, card_h = 1280, 460
    card = Image.new("RGB", (card_w, card_h), "#1F2B22")
    draw = ImageDraw.Draw(card)

    # Soft horizontal gradient background (dark green shades).
    for y in range(card_h):
        blend = y / card_h
        color = (
            int(25 + 18 * blend),
            int(38 + 34 * blend),
            int(30 + 20 * blend),
        )
        draw.line((0, y, card_w, y), fill=color)

    # Subtle frame.
    draw.rounded_rectangle((16, 16, card_w - 16, card_h - 16), radius=20, outline="#DDE7DD", width=2)

    # Render a crisp square QR, then place it smaller at center.
    qr_raw = io.BytesIO()
    qr.save(qr_raw, kind="png", scale=8, border=2, dark="#101010", light="#FFFFFF")
    qr_img = Image.open(io.BytesIO(qr_raw.getvalue())).convert("RGB")

    target_side = card_h - 64
    qr_img = qr_img.resize((target_side, target_side), Image.Resampling.NEAREST)

    pad = 10
    plate = Image.new("RGB", (target_side + pad * 2, target_side + pad * 2), "#FFFFFF")
    plate.paste(qr_img, (pad, pad))
    px = (card_w - plate.width) // 2
    py = max(0, (card_h - plate.height) // 2)
    card.paste(plate, (px, py))

    out = io.BytesIO()
    card.save(out, format="PNG", optimize=True)
    payload = out.getvalue()
    if len(payload) <= TELEGRAM_QR_MAX_BYTES:
        return payload

    # Compress fallback
    out = io.BytesIO()
    card.save(out, format="JPEG", quality=86, optimize=True)
    return out.getvalue()


async def run_nightly_subscription_job(
    settings: Settings,
    bot: Bot,
    bot_settings: BotSettingsStore | None = None,
) -> None:
    """Forever loop: run once per day at configured Iran local time."""
    log = logging.getLogger("smart-support-bot.nightly")

    while True:
        schedule = None
        if bot_settings is not None:
            schedule = await bot_settings.effective_nightly_times(settings)
        nxt = _next_run_iran(settings, schedule_times=schedule)
        wait_seconds = max(1, int((nxt - datetime.now(IRAN_TZ)).total_seconds()))
        log.info("Nightly subscription job scheduled for %s (in %ss)", nxt.isoformat(), wait_seconds)
        await asyncio.sleep(wait_seconds)

        try:
            if bot_settings is not None:
                base, token, inbound_ids = await bot_settings.effective_panel(settings)
                chat_id = await bot_settings.effective_nightly_chat_id(settings)
                template = await bot_settings.effective_nightly_template()
            else:
                from src.storage.bot_settings import parse_inbound_ids

                base = settings.panel_base_url
                token = settings.panel_api_token
                inbound_ids = parse_inbound_ids(settings.panel_inbound_ids)
                chat_id = settings.nightly_support_chat_id
                template = None

            panel = PanelClient(base_url=base, api_token=token)
            created = await panel.add_client_10gb(inbound_ids=inbound_ids)
            text = _build_support_message(
                sub_link=created.sub_link,
                template=template,
            )
            qr_bytes = _build_qr_png(created.sub_link)
            await bot.send_photo(
                chat_id=chat_id,
                photo=BufferedInputFile(qr_bytes, filename="blackfox-subscription-qr.png"),
                caption=text,
                parse_mode="HTML",
            )
            log.info("Nightly subscription created and sent to %s", chat_id)
            from src.job_status import record_job

            record_job(settings.data_dir, "nightly_config", ok=True, detail=f"sent to {chat_id}")
        except (PanelAPIError, Exception) as exc:  # noqa: BLE001
            log.exception("Nightly subscription job failed: %s", exc)
            from src.job_status import record_job

            record_job(settings.data_dir, "nightly_config", ok=False, detail=str(exc)[:200])
            # Avoid tight retry loops; next run remains next day.
