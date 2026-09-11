"""Social-media news watcher for filtering/internet updates."""

from __future__ import annotations

import asyncio
import html
import hashlib
import io
import json
import logging
import math
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx
import jdatetime
from aiogram import Bot
from aiogram.types import BufferedInputFile
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw

from src.ai.client import AIClient, AIClientError
from src.config import Settings
from src.storage.bot_settings import BotSettingsStore

IRAN_TZ = ZoneInfo("Asia/Tehran")
MAX_NEWS_AGE_HOURS = 48
KEYWORDS = (
    "filter",
    "filtering",
    "censor",
    "censorship",
    "internet",
    "internet shutdown",
    "internet outage",
    "vpn block",
    "telegram block",
    "اینترنت",
    "فیلترینگ",
    "اختلال اینترنت",
    "قطع اینترنت",
    "رفع فیلتر",
    "وی‌پی‌ان",
    "vpn",
)


@dataclass(slots=True)
class CandidateNews:
    title: str
    summary: str
    link: str
    source: str
    score: float
    reactions: int
    comments: int
    published: datetime | None
    image_url: str | None = None
    views: int = 0
    shares: int = 0
    importance: float = 0.0
    corroboration: int = 1
    growth: int = 0


# Up to 80 configured sources (Iran + world official / tech news).
DEFAULT_SOURCE_LIST: list[dict[str, str]] = [
    {"kind": "telegram", "name": "BBC فارسی", "url": "https://t.me/s/BBCPersian"},
    {"kind": "telegram", "name": "ایران اینترنشنال", "url": "https://t.me/s/iranintltv"},
    {"kind": "telegram", "name": "منوتو", "url": "https://t.me/s/Manototv"},
    {"kind": "telegram", "name": "صدای آمریکا فارسی", "url": "https://t.me/s/FarsiVOA"},
    {"kind": "telegram", "name": "دیجیاتو", "url": "https://t.me/s/Digiato"},
    {"kind": "telegram", "name": "زومیت", "url": "https://t.me/s/theZoomit"},
    {"kind": "telegram", "name": "پیوست", "url": "https://t.me/s/peivast"},
    {"kind": "telegram", "name": "رادیو فردا", "url": "https://t.me/s/radiofarda"},
    {"kind": "telegram", "name": "دویچه‌وله فارسی", "url": "https://t.me/s/dw_Farsi"},
    {"kind": "telegram", "name": "یورونیوز فارسی", "url": "https://t.me/s/euronewspe"},
    {"kind": "telegram", "name": "گزارش‌های اینترنت ایران", "url": "https://t.me/s/IRVIVPN"},
    {"kind": "telegram", "name": "اخبار فیلترینگ", "url": "https://t.me/s/filtereshekan"},
    {"kind": "reddit", "name": "Reddit r/iran", "url": "https://www.reddit.com/r/iran/new.json?limit=40"},
    {"kind": "reddit", "name": "Reddit r/NewIran", "url": "https://www.reddit.com/r/NewIran/new.json?limit=40"},
    {"kind": "hn", "name": "HN (Iran internet)", "url": "https://hn.algolia.com/api/v1/search?tags=story&query=Iran%20internet%20censorship"},
    {"kind": "hn", "name": "HN (Iran filtering)", "url": "https://hn.algolia.com/api/v1/search?tags=story&query=Iran%20filtering"},
    {"kind": "rss", "name": "Zoomit", "url": "https://www.zoomit.ir/feed/"},
    {"kind": "rss", "name": "Digiato", "url": "https://digiato.com/feed"},
    {"kind": "rss", "name": "ISNA Science", "url": "https://www.isna.ir/rss/tp/24"},
    {"kind": "rss", "name": "IRNA IT", "url": "https://www.irna.ir/rss/tp/14"},
]


def _contains_keywords(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in KEYWORDS)


def _is_iran_related(text: str) -> bool:
    t = text.lower()
    iran_terms = ("iran", "iranian", "ایران", "ایرانی", "tehran", "تهران")
    return any(k in t for k in iran_terms)


def _has_persian(text: str) -> bool:
    return any("\u0600" <= ch <= "\u06ff" for ch in (text or ""))


PROMPT_LEAK_PHRASES = (
    "# role",
    "# main objective",
    "impact score",
    "news selection algorithm",
    "telegram post format",
    "دقیقاً با این قالب",
    "فقط اطلاعات موجود در متن",
    "عنوان منبع:",
    "متن منبع:",
    # Reject / meta reasoning must never become a public caption
    "باید رد",
    "رد می‌کنم",
    "رد ميکنم",
    "این خبر اینترنت ایران نیست",
    "اینترنت ایران نیست",
    "طبق دستورالعمل",
    "طبق دستور العمل",
    "تأییدکننده",
    "تاییدکننده",
    "reasoning",
    "i must reject",
    "reject this news",
    "not iran internet",
    "family relationships",
    "روابط خانوادگی",
)

PRIORITY_TOPICS: tuple[tuple[tuple[str, ...], float], ...] = (
    (("قطع اینترنت", "اختلال گسترده", "internet shutdown", "internet outage"), 1.0),
    (("فیلترینگ", "رفع فیلتر", "سانسور", "filtering", "censorship"), 0.97),
    (("سیاست اینترنت", "اینترنت طبقاتی", "طرح اینترنت", "محدودیت اینترنت"), 0.93),
    (("vpn", "وی‌پی‌ان", "فیلترشکن", "محدودیت اتصال"), 0.88),
    (("dns", "دی‌ان‌اس", "شبکه ملی", "شبکه اطلاعات"), 0.84),
    (("حمله سایبری", "هک", "cyberattack"), 0.82),
    (("اپراتور", "دیتاسنتر", "مرکز داده"), 0.78),
)

NON_PRIMARY_SOURCES = {
    "گزارش‌های اینترنت ایران",
    "اخبار فیلترینگ",
    "Reddit r/iran",
    "Reddit r/NewIran",
    "HN (Iran internet)",
    "HN (Iran filtering)",
}

EVENT_STOPWORDS = {
    "ایران", "ایرانی", "اینترنت", "خبر", "گزارش", "درباره", "برای", "شده",
    "است", "شد", "های", "یک", "این", "آن", "با", "از", "در", "به", "و",
    "iran", "iranian", "internet", "the", "and", "for", "with", "from",
}


def _contains_prompt_leak(text: str) -> bool:
    normalized = (text or "").strip().lower()
    return any(phrase.lower() in normalized for phrase in PROMPT_LEAK_PHRASES)


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
    return out or [(10, 0), (17, 0)]


def _next_tick(now: datetime, hhmm: list[tuple[int, int]]) -> datetime:
    base = now.astimezone(IRAN_TZ)
    cands = []
    for h, m in hhmm:
        dt = base.replace(hour=h, minute=m, second=0, microsecond=0)
        if dt <= base:
            dt += timedelta(days=1)
        cands.append(dt)
    return min(cands)


def _published_today_after(settings: Settings, slot: datetime) -> bool:
    """True if any news was published at/after this Iran-local slot today."""
    slot_utc = slot.astimezone(ZoneInfo("UTC"))
    for item in _load_publication_state(settings):
        try:
            published_at = datetime.fromisoformat(
                str(item.get("published_at", "")).replace("Z", "+00:00")
            )
        except Exception:
            continue
        if published_at >= slot_utc:
            return True
    return False


def _missed_slot_today(now: datetime, hhmm: list[tuple[int, int]], settings: Settings) -> datetime | None:
    """If a scheduled slot today already passed with no post, return that slot for catch-up."""
    base = now.astimezone(IRAN_TZ)
    missed: datetime | None = None
    for h, m in sorted(hhmm):
        slot = base.replace(hour=h, minute=m, second=0, microsecond=0)
        if slot > base:
            continue
        # Only catch up within 12h of the slot to avoid very old double-posts.
        if base - slot > timedelta(hours=12):
            continue
        if not _published_today_after(settings, slot):
            missed = slot
    return missed


def _topic_importance(text: str) -> float:
    normalized = (text or "").lower()
    return max(
        (weight for terms, weight in PRIORITY_TOPICS if any(term in normalized for term in terms)),
        default=0.55,
    )


def _event_tokens(news: CandidateNews) -> set[str]:
    words = set(re.findall(r"[A-Za-z\u0600-\u06ff\u200c]{3,}", f"{news.title} {news.summary}".lower()))
    return {word for word in words if word not in EVENT_STOPWORDS}


def _same_event(left: CandidateNews, right: CandidateNews) -> bool:
    a, b = _event_tokens(left), _event_tokens(right)
    if not a or not b:
        return False
    overlap = len(a & b)
    similarity = overlap / max(1, min(len(a), len(b)))
    return (overlap >= 3 and similarity >= 0.25) or (overlap >= 2 and similarity >= 0.4)


def _log_ratio(value: int, maximum: int) -> float:
    if value <= 0 or maximum <= 0:
        return 0.0
    return math.log1p(value) / math.log1p(maximum)


def _is_primary_source_link(url: str) -> bool:
    blocked_social_hosts = (
        "t.me/", "telegram.", "youtube.com/", "youtu.be/", "instagram.com/",
        "x.com/", "twitter.com/", "facebook.com/", "fb.com/",
    )
    normalized = (url or "").lower()
    return normalized.startswith(("http://", "https://")) and not any(
        host in normalized for host in blocked_social_hosts
    )


def _is_fresh(news: CandidateNews) -> bool:
    if news.published is None:
        # Telegram/RSS scrapes sometimes omit datetime; allow if already age-gated at fetch.
        return True
    published = news.published
    if published.tzinfo is None:
        published = published.replace(tzinfo=ZoneInfo("UTC"))
    age = datetime.now(ZoneInfo("UTC")) - published.astimezone(ZoneInfo("UTC"))
    return timedelta(0) <= age <= timedelta(hours=MAX_NEWS_AGE_HOURS)


def _safe_int(v: object, default: int = 0) -> int:
    try:
        return int(v)  # type: ignore[arg-type]
    except Exception:
        return default


def _to_published(ts: int | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromtimestamp(ts, tz=ZoneInfo("UTC"))
    except Exception:
        return None


def _metric_value(raw: str) -> int:
    value = (raw or "").strip().upper().replace(",", "")
    m = re.search(r"([\d.]+)\s*([KMB]?)", value)
    if not m:
        return 0
    try:
        number = float(m.group(1))
    except ValueError:
        return 0
    multiplier = {"": 1, "K": 1_000, "M": 1_000_000, "B": 1_000_000_000}
    return int(number * multiplier.get(m.group(2), 1))


async def _fetch_telegram(client: httpx.AsyncClient, source: dict[str, str]) -> list[CandidateNews]:
    r = await client.get(source["url"], headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")
    out: list[CandidateNews] = []
    now_utc = datetime.now(ZoneInfo("UTC"))
    for wrap in soup.select(".tgme_widget_message_wrap"):
        message = wrap.select_one(".tgme_widget_message")
        text_node = wrap.select_one(".tgme_widget_message_text")
        if message is None or text_node is None:
            continue
        text = re.sub(r"\s+", " ", text_node.get_text(" ", strip=True)).strip()
        if len(text) < 80 or not _contains_keywords(text) or not _is_iran_related(text):
            continue
        post_id = str(message.get("data-post") or "").strip()
        if not post_id:
            continue
        post_link = f"https://t.me/{post_id}"
        source_link = post_link
        for anchor in text_node.select("a[href]"):
            href = str(anchor.get("href") or "").strip()
            if href.startswith("http") and "t.me/" not in href and "telegram." not in href:
                source_link = href
                break
        pub: datetime | None = None
        time_node = wrap.select_one("time[datetime]")
        if time_node:
            try:
                pub = datetime.fromisoformat(str(time_node.get("datetime")).replace("Z", "+00:00"))
            except Exception:
                pub = None
        freshness = 12.0
        if pub:
            freshness = max(0.0, (now_utc - pub.astimezone(ZoneInfo("UTC"))).total_seconds() / 3600.0)
            if freshness > MAX_NEWS_AGE_HOURS:
                continue

        views_node = wrap.select_one(".tgme_widget_message_views")
        views = _metric_value(views_node.get_text(" ", strip=True) if views_node else "")
        reactions = sum(
            _metric_value(node.get_text(" ", strip=True))
            for node in wrap.select(".tgme_widget_message_reaction_count")
        )
        replies_node = wrap.select_one(".tgme_widget_message_replies")
        comments = _metric_value(replies_node.get_text(" ", strip=True) if replies_node else "")

        image_url: str | None = None
        photo = wrap.select_one(".tgme_widget_message_photo_wrap")
        if photo:
            style = str(photo.get("style") or "")
            m = re.search(r"background-image:url\(['\"]?([^'\")]+)", style)
            if m:
                image_url = html.unescape(m.group(1))
        if not image_url:
            img = wrap.select_one(".tgme_widget_message_video_thumb img, .tgme_widget_message_photo img")
            if img and str(img.get("src") or "").startswith("http"):
                image_url = str(img.get("src"))

        title = text[:140]
        importance = _topic_importance(text)
        out.append(
            CandidateNews(
                title=title,
                summary=text[:4000],
                link=source_link,
                source=source["name"],
                score=0.0,
                reactions=reactions,
                comments=comments,
                published=pub,
                image_url=image_url,
                views=views,
                shares=0,
                importance=importance,
            )
        )
    return out


async def _fetch_reddit(client: httpx.AsyncClient, source: dict[str, str]) -> list[CandidateNews]:
    r = await client.get(source["url"], headers={"User-Agent": "BlackFoxNewsBot/1.0"})
    data = r.json()
    items = (((data or {}).get("data") or {}).get("children") or [])
    out: list[CandidateNews] = []
    for row in items:
        d = (row or {}).get("data") or {}
        title = str(d.get("title") or "").strip()
        summary = str(d.get("selftext") or "").strip()
        link = str(d.get("url") or "").strip()
        if not link:
            continue
        joined = f"{title} {summary} {link}"
        if not title or not _contains_keywords(joined):
            continue
        if not _is_iran_related(joined):
            continue
        reactions = _safe_int(d.get("score"))
        comments = _safe_int(d.get("num_comments"))
        pub = _to_published(_safe_int(d.get("created_utc")))
        freshness = 12.0
        if pub:
            freshness = max(0.0, (datetime.now(ZoneInfo("UTC")) - pub).total_seconds() / 3600.0)
            if freshness > MAX_NEWS_AGE_HOURS:
                continue
        img = str(d.get("thumbnail") or "").strip()
        if not img.startswith("http"):
            img = None
        out.append(
            CandidateNews(
                title=title,
                summary=summary[:220],
                link=link,
                source=source["name"],
                score=0.0,
                reactions=reactions,
                comments=comments,
                published=pub,
                image_url=img,
                views=0,
                shares=0,  # Reddit's public score is not a share count.
                importance=_topic_importance(joined),
            )
        )
    return out


async def _fetch_hn(client: httpx.AsyncClient, source: dict[str, str]) -> list[CandidateNews]:
    r = await client.get(source["url"], headers={"User-Agent": "BlackFoxNewsBot/1.0"})
    hits = (r.json() or {}).get("hits") or []
    out: list[CandidateNews] = []
    for h in hits:
        title = str(h.get("title") or "").strip()
        if not title:
            continue
        link = str(h.get("url") or "").strip()
        if not link:
            continue
        summary = str(h.get("story_text") or h.get("comment_text") or "").strip()
        joined = f"{title} {summary} {link}"
        if not _contains_keywords(joined) or not _is_iran_related(joined):
            continue
        reactions = _safe_int(h.get("points"))
        comments = _safe_int(h.get("num_comments"))
        pub = None
        created = str(h.get("created_at") or "")
        if created:
            try:
                pub = datetime.fromisoformat(created.replace("Z", "+00:00"))
            except Exception:
                pub = None
        freshness = 12.0
        if pub:
            freshness = max(0.0, (datetime.now(ZoneInfo("UTC")) - pub).total_seconds() / 3600.0)
            if freshness > MAX_NEWS_AGE_HOURS:
                continue
        out.append(
            CandidateNews(
                title=title,
                summary=summary[:220],
                link=link,
                source=source["name"],
                score=0.0,
                reactions=reactions,
                comments=comments,
                published=pub,
                views=0,
                shares=0,
                importance=_topic_importance(joined),
            )
        )
    return out


def _parse_rss_items(xml_text: str) -> list[tuple[str, str, str, datetime | None]]:
    items: list[tuple[str, str, str, datetime | None]] = []
    for m in re.finditer(r"<item>(.*?)</item>", xml_text, flags=re.S | re.I):
        chunk = m.group(1)
        t = re.search(r"<title><!\[CDATA\[(.*?)\]\]></title>|<title>(.*?)</title>", chunk, flags=re.S | re.I)
        l = re.search(r"<link>(.*?)</link>", chunk, flags=re.S | re.I)
        d = re.search(
            r"<description><!\[CDATA\[(.*?)\]\]></description>|<description>(.*?)</description>",
            chunk,
            flags=re.S | re.I,
        )
        p = re.search(r"<pubDate>(.*?)</pubDate>", chunk, flags=re.S | re.I)
        title = (t.group(1) if t and t.group(1) is not None else (t.group(2) if t else "")) or ""
        link = (l.group(1) if l else "") or ""
        desc = (d.group(1) if d and d.group(1) is not None else (d.group(2) if d else "")) or ""
        title = re.sub(r"\s+", " ", title).strip()
        link = link.strip()
        desc = re.sub(r"<[^>]+>", " ", desc)
        desc = re.sub(r"\s+", " ", desc).strip()
        published = None
        if p:
            try:
                published = parsedate_to_datetime(html.unescape(p.group(1).strip()))
            except Exception:
                published = None
        if title and link:
            items.append((title, link, desc, published))
    return items


async def _fetch_rss(client: httpx.AsyncClient, source: dict[str, str]) -> list[CandidateNews]:
    r = await client.get(source["url"], headers={"User-Agent": "BlackFoxNewsBot/1.0"})
    xml_text = r.text
    out: list[CandidateNews] = []
    for title, link, desc, published in _parse_rss_items(xml_text)[:30]:
        joined = f"{title} {desc} {link}"
        if not _contains_keywords(joined):
            continue
        if not _is_iran_related(joined):
            continue
        if published is None:
            continue
        if published.tzinfo is None:
            published = published.replace(tzinfo=ZoneInfo("UTC"))
        age_hours = (
            datetime.now(ZoneInfo("UTC")) - published.astimezone(ZoneInfo("UTC"))
        ).total_seconds() / 3600.0
        if age_hours < 0 or age_hours > MAX_NEWS_AGE_HOURS:
            continue
        out.append(
            CandidateNews(
                title=title,
                summary=desc[:220],
                link=link,
                source=source["name"],
                score=0.0,  # RSS has no native interaction counts.
                reactions=0,
                comments=0,
                published=published,
                importance=_topic_importance(joined),
            )
        )
    return out


async def _extract_og_image(url: str) -> str | None:
    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            r = await client.get(url, headers={"User-Agent": "BlackFoxNewsBot/1.0"})
        html = r.text
        m = re.search(r'property=["\']og:image["\']\s+content=["\']([^"\']+)["\']', html, flags=re.I)
        if m:
            v = m.group(1).strip()
            return v if v.startswith("http") else None
    except Exception:
        return None
    return None


async def _download_image(image_url: str) -> bytes | None:
    try:
        async with httpx.AsyncClient(timeout=25.0, follow_redirects=True) as client:
            response = await client.get(image_url, headers={"User-Agent": "Mozilla/5.0"})
        content_type = response.headers.get("content-type", "").lower()
        if response.status_code == 200 and content_type.startswith("image/") and response.content:
            if len(response.content) <= 10 * 1024 * 1024:
                return response.content
    except Exception:
        return None
    return None


def _build_concept_image(news: CandidateNews) -> bytes:
    """Create a neutral network illustration when the source has no usable image."""
    width, height = 1280, 720
    image = Image.new("RGB", (width, height), "#071525")
    draw = ImageDraw.Draw(image)
    for y in range(height):
        blend = y / height
        color = (
            int(7 + 7 * blend),
            int(21 + 20 * blend),
            int(37 + 30 * blend),
        )
        draw.line((0, y, width, y), fill=color)

    nodes = [
        (120, 170), (330, 105), (565, 210), (830, 115), (1110, 210),
        (205, 475), (470, 565), (760, 455), (1035, 545),
    ]
    links = ((0, 1), (0, 5), (1, 2), (2, 3), (2, 6), (2, 7), (3, 4), (3, 7),
             (4, 8), (5, 6), (6, 7), (7, 8))
    accent = "#27D3A2" if news.importance < 0.95 else "#FFB84D"
    for left, right in links:
        draw.line((*nodes[left], *nodes[right]), fill="#24506B", width=5)
    for x, y in nodes:
        draw.ellipse((x - 17, y - 17, x + 17, y + 17), fill=accent, outline="#D9FFF5", width=3)

    # A central shield makes the visual clearly conceptual rather than documentary.
    shield = [(640, 245), (735, 282), (720, 420), (640, 495), (560, 420), (545, 282)]
    draw.polygon(shield, fill="#102F46", outline=accent, width=8)
    draw.arc((590, 305, 690, 405), 205, 515, fill=accent, width=12)
    draw.ellipse((630, 350, 650, 370), fill=accent)

    output = io.BytesIO()
    image.save(output, format="JPEG", quality=88, optimize=True)
    return output.getvalue()


async def _translate_to_fa(text: str) -> str:
    src = (text or "").strip()
    if not src:
        return ""
    # Keep Persian text as-is.
    if any("\u0600" <= ch <= "\u06ff" for ch in src):
        return src
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            r = await client.get(
                "https://translate.googleapis.com/translate_a/single",
                params={
                    "client": "gtx",
                    "sl": "auto",
                    "tl": "fa",
                    "dt": "t",
                    "q": src,
                },
                headers={"User-Agent": "Mozilla/5.0"},
            )
        data = r.json()
        chunks = data[0] if isinstance(data, list) and data else []
        out = "".join(str(c[0]) for c in chunks if isinstance(c, list) and c and c[0])
        return out.strip() or src
    except Exception:
        return src


_JUNK_TEXT_MARKERS = (
    "کلمات کلیدی",
    "جستجو شده",
    "داغ‌ترین",
    "داغ ترین",
    "بیشتر بخوانید",
    "مطالب مرتبط",
    "پربازدید",
    "پیشنهاد سردبیر",
    "اشتراک‌گذاری",
    "دیدگاه شما",
    "نظرات کاربران",
    "آخرین کلمات",
    "related posts",
    "trending",
    "keywords",
    "tags:",
    "metaverse",
    "openai",
    "huawei",
    "bloomberg",
    "tim cook",
    "iphone fold",
)


def _latin_token_ratio(text: str) -> float:
    tokens = re.findall(r"[A-Za-z\u0600-\u06ff\u200c]{2,}", text or "")
    if not tokens:
        return 0.0
    latin = sum(1 for t in tokens if re.fullmatch(r"[A-Za-z]{2,}", t))
    return latin / max(1, len(tokens))


def _is_junk_news_text(text: str) -> bool:
    """Detect Digiato-style keyword salad / sidebar chrome mistaken for article body."""
    raw = (text or "").strip()
    if not raw:
        return True
    low = raw.lower()
    if any(m in low or m in raw for m in _JUNK_TEXT_MARKERS):
        # Short genuine mentions of a brand in a real sentence are OK;
        # long tag clouds almost always trip several markers + high Latin ratio.
        if _latin_token_ratio(raw) >= 0.25 or sum(1 for m in _JUNK_TEXT_MARKERS if m in low or m in raw) >= 2:
            return True
    if _latin_token_ratio(raw) >= 0.45:
        return True
    # Many tiny comma/pipe-separated tags
    if raw.count("،") + raw.count(",") >= 8 and len(raw) < 500:
        return True
    return False


def _clean_source_text(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", (text or "").strip())
    if not cleaned or _is_junk_news_text(cleaned):
        return ""
    return cleaned[:6000]


def _source_quality_score(text: str) -> int:
    raw = (text or "").strip()
    if not raw or _is_junk_news_text(raw):
        return 0
    score = 0
    if _has_persian(raw):
        score += 3
    if _is_iran_related(raw):
        score += 2
    if _contains_keywords(raw):
        score += 2
    # Prefer coherent length without being a tag dump.
    if 120 <= len(raw) <= 3500:
        score += 2
    score -= int(_latin_token_ratio(raw) * 6)
    return max(0, score)


async def _fetch_article_excerpt(url: str) -> str:
    """Fetch useful article text for factual AI summarization (skip tags/sidebars)."""
    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            r = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "noscript", "nav", "footer", "aside", "form"]):
            tag.decompose()
        for junk in soup.select(
            ".tags, .tag, .post-tags, .related, .related-posts, .sidebar, "
            ".share, .social, .breadcrumb, .comments, .comment, "
            "[class*='keyword'], [class*='related'], [id*='related']"
        ):
            junk.decompose()

        desc = ""
        og = soup.find("meta", attrs={"property": "og:description"})
        if og and og.get("content"):
            desc = re.sub(r"\s+", " ", html.unescape(str(og["content"]))).strip()
        if not desc:
            md = soup.find("meta", attrs={"name": "description"})
            if md and md.get("content"):
                desc = re.sub(r"\s+", " ", html.unescape(str(md["content"]))).strip()

        body = (
            soup.select_one("article")
            or soup.select_one(".entry-content, .post-content, .article-content, .content-body, .post-body")
            or soup.select_one("main")
            or soup.body
        )
        paras: list[str] = []
        root = body or soup
        for p in root.find_all(["p", "h2"]):
            txt = re.sub(r"\s+", " ", p.get_text(" ", strip=True)).strip()
            if len(txt) < 60 or _is_junk_news_text(txt):
                continue
            paras.append(txt)
            if len(paras) >= 8:
                break

        parts = []
        if desc and not _is_junk_news_text(desc):
            parts.append(desc)
        parts.extend(paras)
        combined = "\n".join(parts).strip()
        return _clean_source_text(combined)
    except Exception:
        return ""


def _is_meta_or_reject_text(text: str) -> bool:
    """True when model output is rejection/reasoning instead of news copy."""
    normalized = (text or "").strip().lower()
    if not normalized:
        return True
    if _contains_prompt_leak(normalized):
        return True
    if _is_junk_news_text(normalized):
        return True
    needles = (
        "رد می‌کنم",
        "رد ميکنم",
        "باید رد",
        "خبر اینترنت ایران نیست",
        "اینترنت ایران نیست",
        "روابط خانوادگی",
        "طبق دستورالعمل",
        "اگر بخواهم در قالب",
        "reject this",
        "must reject",
        "not iran internet",
        "family relationship",
    )
    return any(n in normalized for n in needles)


def _clean_news_title(title: str) -> str:
    text = _strip_telegram_chrome(title or "")
    text = re.sub(r"^[\W_🔋🌐📰📅🔗🎬🚨•\-–—]+", "", text).strip()
    text = re.sub(r"\s+", " ", text).strip()
    return " ".join(text.split()[:18])


_POINT_EMOJIS = ("🔴", "⚖️", "📊", "⏳", "📌", "🛡", "📡", "💡")
_BAD_START_TOKENS = (
    "کرد", "است", "شد", "شده", "می‌شود", "ميشود", "بود", "باشند", "هستند",
    "و", "که", "تا", "از", "به", "را", "در", "با", "برای", "نیز", "همچنین",
)
_BAD_END_TOKENS = (
    "و", "که", "تا", "از", "به", "را", "در", "با", "برای", "یا", "اگر", "چون",
)


def _strip_telegram_chrome(text: str) -> str:
    """Remove decorative channel emojis / separators that leak into captions."""
    cleaned = text or ""
    cleaned = re.sub(
        r"[🔺🔻🔹🔸▪️▫️●○•▶►◀◆◇★☆✅❌⚠️❗️❗‼️⁉️🟩🟥🟦]+",
        " ",
        cleaned,
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _first_token(text: str) -> str:
    m = re.match(r"[\u0600-\u06ff\u200cA-Za-z0-9]+", (text or "").strip())
    return m.group(0) if m else ""


def _last_token(text: str) -> str:
    parts = re.findall(r"[\u0600-\u06ff\u200cA-Za-z0-9]+", (text or "").strip())
    return parts[-1] if parts else ""


def _is_incomplete_sentence(text: str) -> bool:
    raw = _strip_telegram_chrome(text)
    if not raw or len(raw) < 25:
        return True
    if raw[-1] not in ".!؟…" and _last_token(raw) in _BAD_END_TOKENS:
        return True
    if _first_token(raw) in _BAD_START_TOKENS:
        return True
    if _last_token(raw.rstrip(".!؟…")) in _BAD_END_TOKENS:
        return True
    if re.match(r"^(کرد|است|شد|شده)\b", raw):
        return True
    return False


def _ensure_sentence_end(text: str) -> str:
    raw = _strip_telegram_chrome(text).strip()
    if not raw:
        return ""
    if raw[-1] not in ".!؟":
        raw += "."
    return raw


def _text_overlap_ratio(a: str, b: str) -> float:
    ta = set(re.findall(r"[\u0600-\u06ff\u200c]{3,}", (a or "").lower()))
    tb = set(re.findall(r"[\u0600-\u06ff\u200c]{3,}", (b or "").lower()))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(1, min(len(ta), len(tb)))


def _normalize_detail_lines(raw: str) -> list[str]:
    """Legacy plain-line normalizer (also used as quality fallback)."""
    lines: list[str] = []
    for line in (raw or "").splitlines():
        text = re.sub(r"^\s*(?:[-•*]|\d+[\.\)])\s*", "", line).strip()
        text = re.sub(r"^(?:SUMMARY|خلاصه|LEAD|POINTS)\s*:\s*", "", text, flags=re.I)
        text = re.sub(r"^[🔴⚖️📊⏳📌🛡📡💡]\s*", "", text)
        text = _strip_telegram_chrome(text)
        if not text or not _has_persian(text) or _contains_prompt_leak(text):
            continue
        if _is_meta_or_reject_text(text) or _is_junk_news_text(text):
            continue
        if _is_incomplete_sentence(text):
            continue
        text = _ensure_sentence_end(re.sub(r"\s+", " ", text))
        if len(text) < 28 or len(text) > 160:
            continue
        if text and text not in lines:
            lines.append(text)
    return lines[:12]


def _parse_editorial(summary: str) -> tuple[str, list[tuple[str, str, str]]]:
    """Return (lead, [(emoji, label, body), ...]) from stored editorial summary."""
    raw = (summary or "").strip()
    if not raw:
        return "", []
    lead = ""
    points: list[tuple[str, str, str]] = []
    lead_m = re.search(
        r"(?is)^\s*LEAD:\s*(.+?)(?=\n\s*POINTS:|\n\s*[🔴⚖️📊⏳📌🛡📡💡]|\Z)",
        raw,
    )
    if lead_m:
        lead = _ensure_sentence_end(_strip_telegram_chrome(lead_m.group(1)))
    points_blob = raw
    pm = re.search(r"(?im)^\s*POINTS:\s*$", raw)
    if pm:
        points_blob = raw[pm.end() :]
    elif lead_m:
        points_blob = raw[lead_m.end() :]
    for line in points_blob.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(
            r"^([🔴⚖️📊⏳📌🛡📡💡])\s*(?:\*\*)?([^:*\n]{2,40})(?:\*\*)?\s*[:：]\s*(.+)$",
            line,
        )
        if not m:
            plain = _ensure_sentence_end(
                _strip_telegram_chrome(re.sub(r"^\s*(?:[-•*]|\d+[\.\)])\s*", "", line))
            )
            if (
                _has_persian(plain)
                and not _is_junk_news_text(plain)
                and not _is_incomplete_sentence(plain)
                and len(plain) >= 28
            ):
                emoji = _POINT_EMOJIS[len(points) % len(_POINT_EMOJIS)]
                points.append((emoji, "نکته", plain[:140]))
            continue
        emoji = m.group(1)
        label = _strip_telegram_chrome(m.group(2)).strip()[:28]
        body = _ensure_sentence_end(_strip_telegram_chrome(m.group(3)))
        if (
            not _has_persian(label + body)
            or _is_junk_news_text(body)
            or _is_incomplete_sentence(body)
            or len(body) < 28
        ):
            continue
        if label in {"نکته", "نکته مهم", "جزئیات", "پیامد", "زمان‌بندی"}:
            label = "نکته"
        points.append((emoji, label, body[:150]))
        if len(points) >= 5:
            break
    if not lead:
        plain = _normalize_detail_lines(raw)
        if plain:
            lead = plain[0]
            if not points:
                for i, p in enumerate(plain[1:5]):
                    points.append((_POINT_EMOJIS[i % len(_POINT_EMOJIS)], "نکته", p))
    return lead, points


def _editorial_quality_ok(summary: str, *, title: str = "") -> bool:
    lead, points = _parse_editorial(summary)
    if _is_junk_news_text(lead) or _is_incomplete_sentence(lead) or len(lead) < 45:
        return False
    if title and _text_overlap_ratio(lead, title) >= 0.85:
        return False
    if len(points) < 3:
        return False
    for _, _label, body in points:
        if _is_incomplete_sentence(body) or _is_junk_news_text(body) or len(body) < 28:
            return False
    return True


def _fallback_detail_lines(raw: str) -> list[str]:
    """Split clean source text into complete Persian sentences."""
    text = _clean_source_text(_strip_telegram_chrome(raw))
    if not text or _source_quality_score(text) < 5:
        return []
    parts = [p.strip() for p in re.split(r"(?<=[.!?؟؛。])\s+", text) if p.strip()]
    out: list[str] = []
    for part in parts:
        part = _ensure_sentence_end(_strip_telegram_chrome(part))
        if _is_junk_news_text(part) or _is_incomplete_sentence(part):
            continue
        if len(part) < 28 or len(part) > 160:
            continue
        out.append(part)
    return out[:8]


def _build_editorial_fallback(raw: str, *, title: str = "", source: str = "") -> str:
    """Build LEAD + POINTS from complete sentences only (never mid-clause chops)."""
    lines = _fallback_detail_lines(raw)
    src = (source or "منبع خبر").strip()
    title_clean = _clean_news_title(title)
    if len(lines) < 3:
        if not title_clean or not _has_persian(title_clean):
            return ""
        lines = [
            _ensure_sentence_end(f"به گزارش {src}، {title_clean}"),
            _ensure_sentence_end(
                f"این خبر توسط {src} منتشر شده و به حوزه اینترنت و ارتباطات مربوط است"
            ),
            _ensure_sentence_end("جزئیات بیشتر در لینک منبع قابل مشاهده است"),
        ]
    lead = lines[0]
    if title_clean and _text_overlap_ratio(lead, title_clean) >= 0.85 and len(lines) > 1:
        lead = lines[1]
        point_bodies = [lines[0]] + lines[2:5]
    else:
        point_bodies = lines[1:5]
    while len(point_bodies) < 3 and len(lines) > len(point_bodies) + 1:
        point_bodies.append(lines[len(point_bodies) + 1])
    if len(point_bodies) < 3:
        return ""
    labels = ("اصل خبر", "جزئیات بیشتر", "حمایت و اقدام", "پیگیری", "جمع‌بندی")
    out = [f"LEAD: {lead}", "", "POINTS:"]
    for i, body in enumerate(point_bodies[:4]):
        out.append(f"{_POINT_EMOJIS[i % len(_POINT_EMOJIS)]} {labels[i % len(labels)]}: {body}")
    draft = "\n".join(out)
    return draft if _editorial_quality_ok(draft, title=title_clean) else ""


async def _prepare_news_content(
    settings: Settings,
    news: CandidateNews,
    *,
    rules_prompt: str | None = None,
) -> None:
    article = "" if "t.me/" in news.link else await _fetch_article_excerpt(news.link)
    original = _clean_source_text(_strip_telegram_chrome(news.summary or news.title))
    article_q = _source_quality_score(article)
    original_q = _source_quality_score(original)
    if article_q >= original_q and article_q > 0:
        source_text = article
    else:
        source_text = original or article
    if not source_text:
        news.summary = ""
        return

    system_prompt = (
        (rules_prompt or "").strip()
        or (
            "تو ویراستار خبری کانال تلگرام Black Fox Group (محصول VPS to VPN) هستی. "
            "خبر را برای مخاطب فارسی، رسمی و خوانا ادیت کن. "
            "فقط از اطلاعات موجود در متن منبع استفاده کن؛ ادعا اضافه نکن. "
            "هر نکته باید یک جملهٔ کامل و مستقل باشد؛ جملهٔ ناقص ممنوع است. "
            "تگ، ایموجی تزئینی کانال مبدأ، کلمات کلیدی جستجو و مطالب مرتبط را حذف کن."
        )
    )
    user_prompt = (
        "خبر را مثل پست ادیت‌شدهٔ حرفه‌ای تلگرام بنویس.\n"
        "خروجی دقیقاً با این قالب باشد:\n"
        "TITLE: تیتر فارسی کامل (حداکثر ۱۸ کلمه، بدون ایموجی)\n"
        "LEAD: یک پاراگراف ۲ جمله‌ای که اصل خبر را بگوید؛ تکرار عین تیتر ممنوع\n"
        "POINTS:\n"
        "🔴 برچسب کوتاه: یک جملهٔ کامل مستقل فارسی\n"
        "⚖️ برچسب کوتاه: یک جملهٔ کامل مستقل فارسی\n"
        "📊 برچسب کوتاه: یک جملهٔ کامل مستقل فارسی\n"
        "⏳ برچسب کوتاه: یک جملهٔ کامل مستقل فارسی\n"
        "قواعد سخت:\n"
        "- هر نکته فاعل+فعل کامل داشته باشد؛ با «کرد/است/شد/و/که» شروع نشود\n"
        "- هیچ جمله‌ای وسط حرف تمام نشود (آخرش و/که/تا/از ممنوع)\n"
        "- لید نباید کپی تیتر باشد\n"
        "- برچسب‌ها معنادار باشند (مثل بودجه، حمایت، زمان، اقدام)\n"
        "- بدون تگ و بدون لیست برند\n\n"
        f"منبع: {news.source}\n"
        f"عنوان اصلی: {news.title}\n"
        f"متن منبع:\n{source_text[:6000]}"
    )

    async def _ask_ai(extra: str = "") -> str:
        ai = AIClient(settings)
        try:
            return await ai.chat(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt + extra},
                ],
                temperature=0.15,
                max_tokens=1600,
            )
        except AIClientError:
            return ""
        finally:
            await ai.close()

    response = await _ask_ai()
    if _is_meta_or_reject_text(response):
        response = ""
    if not (response or "").strip():
        response = await _ask_ai(
            "\n\nپاسخ قبلی خالی بود. فقط همان قالب TITLE/LEAD/POINTS را با جمله‌های کامل بنویس."
        )
        if _is_meta_or_reject_text(response):
            response = ""

    title_match = re.search(r"(?im)^\s*\**TITLE:\**\s*(.+)$", response or "")
    if (
        title_match
        and _has_persian(title_match.group(1))
        and not _contains_prompt_leak(title_match.group(1))
        and not _is_junk_news_text(title_match.group(1))
    ):
        news.title = _clean_news_title(title_match.group(1))
    else:
        translated = await _translate_to_fa(_clean_news_title(news.title))
        news.title = _clean_news_title(translated)

    lead_m = re.search(
        r"(?is)^\s*\**LEAD:\**\s*(.+?)(?=\n\s*\**POINTS:\**|\n\s*[🔴⚖️📊⏳📌]|\Z)",
        response or "",
    )
    points_m = re.search(r"(?im)^\s*\**POINTS:\**\s*$", response or "")
    editorial = ""
    if lead_m and points_m:
        lead = _ensure_sentence_end(_strip_telegram_chrome(lead_m.group(1)))
        points_blob = (response or "")[points_m.end() :]
        rebuilt = [f"LEAD: {lead}", "", "POINTS:"]
        for line in points_blob.splitlines():
            line = line.strip()
            if re.match(r"^[🔴⚖️📊⏳📌🛡📡💡]", line):
                rebuilt.append(line)
        editorial = "\n".join(rebuilt)

    if not _editorial_quality_ok(editorial, title=news.title):
        editorial = _build_editorial_fallback(
            await _translate_to_fa(source_text),
            title=news.title,
            source=news.source,
        )
    if not _editorial_quality_ok(editorial, title=news.title):
        news.summary = ""
        return
    news.summary = editorial


def _render_news_caption(news: CandidateNews) -> str:
    """Editorial Telegram caption: headline + lead + emoji key points + source."""
    title_fa = _clean_news_title(news.title or "")
    if not _has_persian(title_fa) or _is_junk_news_text(title_fa):
        title_fa = "آخرین خبر مرتبط با اینترنت و ارتباطات ایران"

    lead, points = _parse_editorial(news.summary or "")
    lead = _ensure_sentence_end(_strip_telegram_chrome(lead))
    if not lead or _is_incomplete_sentence(lead):
        lead = _ensure_sentence_end(
            f"به گزارش {(news.source or 'منبع خبر').strip()}، {title_fa}"
        )
    clean_points: list[tuple[str, str, str]] = []
    for emoji, label, body in points:
        body = _ensure_sentence_end(_strip_telegram_chrome(body))
        label = _strip_telegram_chrome(label) or "نکته"
        if _is_incomplete_sentence(body) or len(body) < 28:
            continue
        clean_points.append((emoji, label[:28], body[:150]))
    if len(clean_points) < 3:
        for i, line in enumerate(_normalize_detail_lines(news.summary or "")[:4]):
            clean_points.append((_POINT_EMOJIS[i % len(_POINT_EMOJIS)], "نکته", line))

    ref = f'<a href="{html.escape(news.link, quote=True)}">مشاهده منبع</a>'
    source_name = (news.source or "").strip() or "منبع خبر"
    lines: list[str] = [
        f"🚨 <b>{html.escape(title_fa)}</b>",
        "",
        html.escape(lead),
        "",
        "⚙️ <b>نکات کلیدی:</b>",
        "",
    ]
    for emoji, label, body in clean_points[:4]:
        lines.append(f"{emoji} <b>{html.escape(label)}:</b> {html.escape(body)}")
    lines.extend(
        [
            "",
            f"🔗 منبع: {html.escape(source_name)} | {ref}",
            "",
            "🦊 Black Fox Group | VPS to VPN | @blackFoxVPNN",
        ]
    )
    caption = "\n".join(lines)
    if len(caption) > 1024:
        caption = caption[:1000].rsplit("\n", 1)[0] + "\n\n🔗 " + ref
    return caption


def _load_sources(project_root: Path) -> list[dict[str, str]]:
    path = project_root / "knowledge" / "social_news_sources.json"
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            out: list[dict[str, str]] = []
            for item in raw[:80]:
                if not isinstance(item, dict):
                    continue
                kind = str(item.get("kind") or "").strip()
                name = str(item.get("name") or "").strip()
                url = str(item.get("url") or "").strip()
                if kind and name and url:
                    out.append({"kind": kind, "name": name, "url": url})
            if len(out) >= 20:
                return out
    except Exception:
        pass
    return DEFAULT_SOURCE_LIST


def _state_path(settings: Settings) -> Path:
    return settings.data_dir / "social_news_state.json"


def _load_publication_state(settings: Settings) -> list[dict[str, str]]:
    try:
        raw = json.loads(_state_path(settings).read_text(encoding="utf-8"))
        posts = raw.get("posts", []) if isinstance(raw, dict) else []
        if isinstance(posts, list):
            return [item for item in posts if isinstance(item, dict)]
    except Exception:
        pass
    return []


def _publication_key(news: CandidateNews) -> str:
    normalized = re.sub(r"\W+", "", f"{news.link}|{news.title}".lower(), flags=re.UNICODE)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _was_published(news: CandidateNews, state: list[dict[str, str]]) -> bool:
    key = _publication_key(news)
    current_tokens = _event_tokens(news)
    cutoff = datetime.now(ZoneInfo("UTC")) - timedelta(days=7)
    for item in state:
        if item.get("key") == key or item.get("link") == news.link:
            return True
        try:
            published_at = datetime.fromisoformat(str(item.get("published_at", "")).replace("Z", "+00:00"))
        except Exception:
            continue
        if published_at < cutoff:
            continue
        old_title = str(item.get("title") or "")
        old_news = CandidateNews(old_title, "", "", "", 0.0, 0, 0, None)
        old_tokens = _event_tokens(old_news)
        if current_tokens and old_tokens:
            overlap = len(current_tokens & old_tokens) / max(1, min(len(current_tokens), len(old_tokens)))
            if len(current_tokens & old_tokens) >= 3 and overlap >= 0.4:
                return True
    return False


def _record_publication(
    settings: Settings,
    news: CandidateNews,
    *,
    target: str | None = None,
) -> None:
    now = datetime.now(ZoneInfo("UTC")).isoformat()
    posts = _load_publication_state(settings)
    posts.append(
        {
            "key": _publication_key(news),
            "link": news.link,
            "title": news.title,
            "source": news.source,
            "impact_score": f"{news.score:.2f}",
            "corroboration": str(news.corroboration),
            "published_at": now,
            "target": (target or settings.social_news_chat_id or "").strip(),
        }
    )
    payload = {"posts": posts[-500:]}
    path = _state_path(settings)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)
    with (settings.data_dir / "social_news_publications.jsonl").open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(payload["posts"][-1], ensure_ascii=False) + "\n")


def _apply_and_store_metric_growth(settings: Settings, items: list[CandidateNews]) -> None:
    path = settings.data_dir / "social_news_metrics.json"
    try:
        previous = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(previous, dict):
            previous = {}
    except Exception:
        previous = {}
    now = datetime.now(ZoneInfo("UTC"))
    updated: dict[str, dict[str, object]] = {}
    for item in items:
        current = item.views + item.reactions + item.comments + item.shares
        old = previous.get(item.link, {})
        if isinstance(old, dict):
            try:
                old_time = datetime.fromisoformat(str(old.get("checked_at", "")).replace("Z", "+00:00"))
                old_value = int(old.get("interactions", 0))
                if now - old_time <= timedelta(hours=24):
                    item.growth = max(0, current - old_value)
            except Exception:
                item.growth = 0
        updated[item.link] = {
            "interactions": current,
            "checked_at": now.isoformat(),
        }
    path.write_text(
        json.dumps(dict(list(updated.items())[-2000:]), ensure_ascii=False),
        encoding="utf-8",
    )


async def _source_link_is_live(url: str) -> bool:
    """Accept primary article URLs; also allow public Telegram post links as soft sources."""
    normalized = (url or "").strip()
    if not normalized.startswith(("http://", "https://")):
        return False
    lower = normalized.lower()
    allow_telegram = "t.me/" in lower
    if not allow_telegram and not _is_primary_source_link(normalized):
        return False
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            async with client.stream("GET", normalized, headers={"User-Agent": "Mozilla/5.0"}) as response:
                if not (200 <= response.status_code < 400):
                    # Soft-accept known-good shapes when host blocks bots.
                    return allow_telegram or _is_primary_source_link(normalized)
                final = str(response.url)
                if allow_telegram:
                    return "t.me/" in final.lower()
                return _is_primary_source_link(final)
    except Exception:
        return allow_telegram or _is_primary_source_link(normalized)


def _soft_single_source_ok(item: CandidateNews) -> bool:
    """On low-news days allow a strong single source instead of requiring 2+ outlets."""
    engagement = int(item.reactions) + int(item.comments) + int(item.shares) + int(item.growth)
    views = int(item.views)
    if _is_primary_source_link(item.link):
        return item.importance >= 0.40 or engagement >= 10 or views >= 80
    # Telegram / aggregator: topic strength still required, but not extreme.
    if item.source in NON_PRIMARY_SOURCES:
        return item.importance >= 0.70
    return item.importance >= 0.60 or (
        item.importance >= 0.50 and (views >= 400 or engagement >= 25)
    )


async def run_social_news_job(
    settings: Settings,
    bot: Bot,
    bot_settings: BotSettingsStore | None = None,
) -> None:
    log = logging.getLogger("blackfox-agent-bot.social-news")
    sources = _load_sources(settings.project_root)
    catchup_done = False

    while True:
        times_raw = settings.social_news_times
        chat_id = settings.social_news_chat_id
        rules = None
        if bot_settings is not None:
            times_raw = await bot_settings.effective_social_times(settings)
            chat_id = await bot_settings.effective_social_chat_id(settings)
            rules = await bot_settings.effective_social_rules()
        hhmm = _parse_times(times_raw)
        log.info("Social news scheduler active (times=%s sources=%d)", hhmm, len(sources))
        now = datetime.now(IRAN_TZ)
        # After restart, catch up a missed morning/evening slot instead of jumping to the next one.
        if not catchup_done:
            missed = _missed_slot_today(now, hhmm, settings)
            catchup_done = True
            if missed is not None:
                log.info("Catch-up social news for missed slot %s", missed.isoformat())
                wait_seconds = 1
            else:
                nxt = _next_tick(now, hhmm)
                wait_seconds = max(1, int((nxt - datetime.now(IRAN_TZ)).total_seconds()))
                log.info("Next social news check at %s (in %ss)", nxt.isoformat(), wait_seconds)
        else:
            nxt = _next_tick(datetime.now(IRAN_TZ), hhmm)
            wait_seconds = max(1, int((nxt - datetime.now(IRAN_TZ)).total_seconds()))
            log.info("Next social news check at %s (in %ss)", nxt.isoformat(), wait_seconds)
        await asyncio.sleep(wait_seconds)
        try:
            if bot_settings is not None:
                chat_id = await bot_settings.effective_social_chat_id(settings)
                rules = await bot_settings.effective_social_rules()
            if not str(chat_id or "").strip():
                log.info("Social news skipped: news slot disabled or no destination")
                from src.job_status import record_job
                from src.social_news_attempts import record_news_attempt

                record_job(settings.data_dir, "social_news", ok=False, detail="slot disabled or no chat")
                record_news_attempt(
                    settings.data_dir,
                    ok=False,
                    reason="slot disabled or no chat",
                    target=str(chat_id or ""),
                )
                continue
            news = await _pick_publishable_news(settings, sources, rules_prompt=rules)
            if news is None:
                log.info("No publishable social news after soft single-source + multi-source filters")
                from src.job_status import record_job
                from src.social_news_attempts import record_news_attempt

                record_job(settings.data_dir, "social_news", ok=False, detail="nothing publishable")
                record_news_attempt(
                    settings.data_dir,
                    ok=False,
                    reason="nothing publishable",
                    target=str(chat_id or ""),
                )
                continue
            if not news.image_url:
                news.image_url = await _extract_og_image(news.link)
            caption = _render_news_caption(news)
            image_bytes = await _download_image(news.image_url) if news.image_url else None
            if not image_bytes:
                image_bytes = _build_concept_image(news)
            await bot.send_photo(
                chat_id=chat_id,
                photo=BufferedInputFile(image_bytes, filename="blackfox-social-news.jpg"),
                caption=caption,
                parse_mode="HTML",
            )
            _record_publication(settings, news, target=str(chat_id))
            log.info("Social news posted to %s: %s", chat_id, news.link)
            from src.job_status import record_job
            from src.social_news_attempts import record_news_attempt

            record_job(settings.data_dir, "social_news", ok=True, detail=news.link[:120])
            record_news_attempt(
                settings.data_dir,
                ok=True,
                reason="published",
                title=news.title,
                link=news.link,
                target=str(chat_id),
                source=news.source,
            )
        except Exception as exc:  # noqa: BLE001
            log.exception("Social news publish failed: %s", exc)
            from src.job_status import record_job
            from src.social_news_attempts import record_news_attempt

            record_job(settings.data_dir, "social_news", ok=False, detail=str(exc)[:200])
            record_news_attempt(
                settings.data_dir,
                ok=False,
                reason=f"error: {exc}"[:400],
                target=str(chat_id or ""),
            )


async def run_social_news_once(
    settings: Settings,
    bot: Bot,
    bot_settings: BotSettingsStore | None = None,
) -> bool:
    """One-shot publish attempt (manual/ops). Returns True if a post was sent."""
    log = logging.getLogger("blackfox-agent-bot.social-news")
    sources = _load_sources(settings.project_root)
    chat_id = settings.social_news_chat_id
    rules = None
    if bot_settings is not None:
        chat_id = await bot_settings.effective_social_chat_id(settings)
        rules = await bot_settings.effective_social_rules()
    if not str(chat_id or "").strip():
        log.info("One-shot social news: news slot disabled or no destination")
        from src.social_news_attempts import record_news_attempt

        record_news_attempt(
            settings.data_dir,
            ok=False,
            reason="slot disabled or no chat",
            target=str(chat_id or ""),
        )
        return False
    news = await _pick_publishable_news(settings, sources, rules_prompt=rules)
    if news is None:
        log.info("One-shot social news: nothing publishable")
        from src.social_news_attempts import record_news_attempt

        record_news_attempt(
            settings.data_dir,
            ok=False,
            reason="nothing publishable",
            target=str(chat_id or ""),
        )
        return False
    if not news.image_url:
        news.image_url = await _extract_og_image(news.link)
    caption = _render_news_caption(news)
    image_bytes = await _download_image(news.image_url) if news.image_url else None
    if not image_bytes:
        image_bytes = _build_concept_image(news)
    await bot.send_photo(
        chat_id=chat_id,
        photo=BufferedInputFile(image_bytes, filename="blackfox-social-news.jpg"),
        caption=caption,
        parse_mode="HTML",
    )
    _record_publication(settings, news, target=str(chat_id))
    log.info("One-shot social news posted to %s: %s", chat_id, news.link)
    from src.social_news_attempts import record_news_attempt

    record_news_attempt(
        settings.data_dir,
        ok=True,
        reason="published",
        title=news.title,
        link=news.link,
        target=str(chat_id),
        source=news.source,
    )
    return True


async def _pick_best_news_from_sources(sources: list[dict[str, str]]) -> CandidateNews | None:
    ranked = await _rank_news_from_sources(sources)
    return ranked[0] if ranked else None


async def _rank_news_from_sources(
    sources: list[dict[str, str]],
    settings: Settings | None = None,
) -> list[CandidateNews]:
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        async def fetch_source(src: dict[str, str]) -> list[CandidateNews]:
            if src["kind"] == "telegram":
                return await _fetch_telegram(client, src)
            if src["kind"] == "reddit":
                return await _fetch_reddit(client, src)
            if src["kind"] == "hn":
                return await _fetch_hn(client, src)
            return await _fetch_rss(client, src)

        batches = await asyncio.gather(
            *(fetch_source(src) for src in sources[:80]),
            return_exceptions=True,
        )
        all_items = [
            item
            for batch in batches
            if isinstance(batch, list)
            for item in batch
        ]
    if settings is not None:
        _apply_and_store_metric_growth(settings, all_items)
    clusters: list[list[CandidateNews]] = []
    for item in all_items:
        matching = next((cluster for cluster in clusters if _same_event(item, cluster[0])), None)
        if matching is None:
            clusters.append([item])
        else:
            matching.append(item)

    verified: list[CandidateNews] = []
    for cluster in clusters:
        source_count = len({item.source for item in cluster})
        eligible = [
            item
            for item in cluster
            if item.source not in NON_PRIMARY_SOURCES and _is_primary_source_link(item.link)
        ]
        primary: CandidateNews | None = None
        if source_count >= 2 and eligible:
            primary = max(
                eligible,
                key=lambda item: (item.importance, item.reactions + item.comments, item.views),
            )
            primary.corroboration = source_count
            primary.importance = min(1.0, primary.importance + 0.04 * (source_count - 2))
        elif eligible:
            # Soft path: strong single primary source is enough on quiet days.
            candidate = max(
                eligible,
                key=lambda item: (item.importance, item.reactions + item.comments, item.views),
            )
            if _soft_single_source_ok(candidate):
                primary = candidate
                primary.corroboration = 1
        else:
            # Last resort: prefer real outlets; aggregators only if topic-importance is very high.
            soft_pool = [
                item
                for item in cluster
                if item.source not in NON_PRIMARY_SOURCES or item.importance >= 0.70
            ]
            if soft_pool:
                candidate = max(
                    soft_pool,
                    key=lambda item: (item.importance, item.reactions + item.comments, item.views),
                )
                if _soft_single_source_ok(candidate):
                    primary = candidate
                    primary.corroboration = 1
        if primary is None:
            continue
        primary.reactions = sum(item.reactions for item in cluster)
        primary.comments = sum(item.comments for item in cluster)
        primary.shares = sum(item.shares for item in cluster)
        primary.growth = sum(item.growth for item in cluster)
        primary.views = max((item.views for item in cluster), default=0)
        verified.append(primary)

    max_engagement = max((item.reactions + item.comments + item.growth for item in verified), default=0)
    max_views = max((item.views for item in verified), default=0)
    max_shares = max((item.shares for item in verified), default=0)
    for item in verified:
        engagement = _log_ratio(item.reactions + item.comments + item.growth, max_engagement)
        views = _log_ratio(item.views, max_views)
        shares = _log_ratio(item.shares, max_shares)
        # Prefer multi-source slightly so soft singles don't always dominate.
        corr_bonus = 8 if item.corroboration >= 2 else 0
        item.score = 40 * engagement + 25 * views + 20 * shares + 15 * item.importance + corr_bonus
    verified.sort(key=lambda item: item.score, reverse=True)
    return verified


async def _pick_publishable_news(
    settings: Settings,
    sources: list[dict[str, str]],
    *,
    rules_prompt: str | None = None,
    min_detail_lines: int = 4,
) -> CandidateNews | None:
    state = _load_publication_state(settings)
    ranked = await _rank_news_from_sources(sources, settings)
    fallback: CandidateNews | None = None
    for news in ranked[:15]:
        if (
            not _is_fresh(news)
            or _was_published(news, state)
            or not await _source_link_is_live(news.link)
        ):
            continue
        await _prepare_news_content(settings, news, rules_prompt=rules_prompt)
        if not _editorial_quality_ok(news.summary or "", title=news.title or ""):
            continue
        lead, points = _parse_editorial(news.summary or "")
        if len(points) >= max(3, min_detail_lines - 1):
            return news
        if fallback is None and len(points) >= 3 and len(lead) >= 45 and not _is_incomplete_sentence(lead):
            fallback = news
    # Quiet-day / catch-up: accept a shorter but still usable caption.
    return fallback
