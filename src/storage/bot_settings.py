"""Runtime bot settings: owner info, message targets (3 slots), panel."""

from __future__ import annotations

import asyncio
import json
import logging
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from src.config import Settings
from src.control.secrets import decrypt_secret, encrypt_secret, mask_api_key

logger = logging.getLogger(__name__)

TARGET_KEYS = ("channel", "group", "support", "test")
SLOT_COUNT = 3
SLOT_KINDS = ("news", "static", "config")

TARGET_TITLE_FA = {
    "channel": "کانال",
    "group": "گروه",
    "support": "اکانت",
    "test": "اکانت تست",
}

TARGET_TITLE_EN = {
    "channel": "Channel",
    "group": "Group",
    "support": "Account",
    "test": "Test Account",
}

SLOT_KIND_FA = {"news": "خبر", "static": "پیام ثابت", "config": "کانفیگ"}
SLOT_KIND_EN = {"news": "News", "static": "Static", "config": "Config"}

DEFAULT_NIGHTLY_TEMPLATE = (
    "🤖 سلام، من ربات هوش مصنوعی هستم.\n\n"
    "🎁 یک اشتراک رایگان برای شما قرار داده‌ام.\n\n"
    "🔹 کانفیگ رایگان:\n{config}\n\n"
    "📅 تاریخ: {date}"
)

DEFAULT_SOCIAL_RULES = (
    "تو ویراستار خبری کانال تلگرام Black Fox Group (محصول VPS to VPN) هستی. "
    "خبر را با تیتر، لید کوتاه و نکات کلیدی ایموجی‌دار (🔴⚖️📊⏳) بنویس. "
    "هر نکته جملهٔ کامل و مستقل باشد؛ تکرار تیتر در لید ممنوع است. "
    "جملهٔ ناقص، تگ سایت و ایموجی تزئینی مبدأ ممنوع. "
    "رسمی، خوانا و بدون نشت پرامپت باشد."
)


@dataclass
class MessageSlot:
    index: int
    kind: str = "static"
    chat_id: str = ""
    message_template: str = ""
    schedule_times: str = ""
    rules_prompt: str = ""
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, index: int, raw: dict[str, Any] | None) -> MessageSlot:
        raw = raw if isinstance(raw, dict) else {}
        kind = str(raw.get("kind") or SLOT_KINDS[min(index, len(SLOT_KINDS) - 1)])
        if kind not in SLOT_KINDS:
            kind = "static"
        return cls(
            index=index,
            kind=kind,
            chat_id=str(raw.get("chat_id") or ""),
            message_template=str(raw.get("message_template") or ""),
            schedule_times=str(raw.get("schedule_times") or ""),
            rules_prompt=str(raw.get("rules_prompt") or ""),
            enabled=bool(raw.get("enabled", True)),
        )


def _default_slots() -> list[MessageSlot]:
    return [
        MessageSlot(index=0, kind="news"),
        MessageSlot(index=1, kind="static"),
        MessageSlot(index=2, kind="config"),
    ]


@dataclass
class MessageTarget:
    key: str
    chat_id: str = ""
    message_template: str = ""
    schedule_times: str = ""
    rules_prompt: str = ""
    enabled: bool = True
    slots: list[MessageSlot] = field(default_factory=_default_slots)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, key: str, raw: dict[str, Any] | None) -> MessageTarget:
        raw = raw if isinstance(raw, dict) else {}
        slots_raw = raw.get("slots")
        slots: list[MessageSlot] = []
        if isinstance(slots_raw, list) and slots_raw:
            for i in range(SLOT_COUNT):
                item = slots_raw[i] if i < len(slots_raw) else None
                slots.append(MessageSlot.from_dict(i, item if isinstance(item, dict) else {}))
        else:
            # Migrate legacy single fields → slot 0; keep kinds for 1/2 empty
            slots = _default_slots()
            slots[0] = MessageSlot(
                index=0,
            kind="config" if key == "channel" else "static",
                chat_id=str(raw.get("chat_id") or ""),
                message_template=str(raw.get("message_template") or ""),
                schedule_times=str(raw.get("schedule_times") or ""),
                rules_prompt=str(raw.get("rules_prompt") or ""),
                enabled=bool(raw.get("enabled", True)),
            )
        return cls(
            key=key,
            chat_id=str(raw.get("chat_id") or ""),
            message_template=str(raw.get("message_template") or ""),
            schedule_times=str(raw.get("schedule_times") or ""),
            rules_prompt=str(raw.get("rules_prompt") or ""),
            enabled=bool(raw.get("enabled", True)),
            slots=slots,
        )

    def slot(self, index: int) -> MessageSlot:
        if 0 <= index < len(self.slots):
            return self.slots[index]
        return MessageSlot(index=index)

    def effective_chat_id(self, slot_index: int = 0) -> str:
        s = self.slot(slot_index)
        return (s.chat_id or self.chat_id or "").strip()


@dataclass
class OwnerInfo:
    """Admin-editable public contacts used by Ask AI answers."""

    site_url: str = ""
    channel: str = ""
    group: str = ""
    support_handle: str = ""
    bot_display_name: str = "Smart Support Bot"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None) -> OwnerInfo:
        raw = raw if isinstance(raw, dict) else {}
        return cls(
            site_url=str(raw.get("site_url") or "").strip(),
            channel=str(raw.get("channel") or "").strip(),
            group=str(raw.get("group") or "").strip(),
            support_handle=str(raw.get("support_handle") or "").strip(),
            bot_display_name=str(
                raw.get("bot_display_name") or "Smart Support Bot"
            ).strip()
            or "Smart Support Bot",
        )


@dataclass
class PanelSettings:
    base_url: str = ""
    api_token_enc: str = ""
    # Legacy field kept for older backups; UI no longer edits it.
    required_port: int = 443
    # Comma-separated inbound IDs, e.g. "1,2,5"
    inbound_ids: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def inbound_id_list(self) -> list[int]:
        return parse_inbound_ids(self.inbound_ids)

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None) -> PanelSettings:
        raw = raw if isinstance(raw, dict) else {}
        try:
            port = int(raw.get("required_port") or 443)
        except (TypeError, ValueError):
            port = 443
        ids_raw = raw.get("inbound_ids")
        if ids_raw is None or str(ids_raw).strip() == "":
            ids_raw = raw.get("inbound_id")
        try:
            inbound_ids = normalize_inbound_ids(ids_raw) if ids_raw not in (None, "") else ""
        except ValueError:
            inbound_ids = ""
        return cls(
            base_url=str(raw.get("base_url") or "").rstrip("/"),
            api_token_enc=str(raw.get("api_token_enc") or ""),
            required_port=port,
            inbound_ids=inbound_ids,
        )


def parse_inbound_ids(raw: Any) -> list[int]:
    """Parse inbound IDs from int/list/comma-separated string."""
    if raw is None or raw == "":
        return []
    if isinstance(raw, int):
        return [raw] if raw > 0 else []
    if isinstance(raw, (list, tuple)):
        out: list[int] = []
        for item in raw:
            try:
                n = int(item)
            except (TypeError, ValueError):
                continue
            if n > 0 and n not in out:
                out.append(n)
        return out
    text = str(raw).replace(";", ",")
    out = []
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            n = int(part)
        except ValueError:
            continue
        if n > 0 and n not in out:
            out.append(n)
    return out


def normalize_inbound_ids(raw: Any) -> str:
    ids = parse_inbound_ids(raw)
    if not ids:
        raise ValueError("no inbound ids")
    return ",".join(str(x) for x in ids)


class BotSettingsStore:
    """Persists admin-editable destinations/templates/panel under data/bot_settings.json."""

    def __init__(self, path: Path, *, master_secret: str) -> None:
        self.path = path
        self._master = master_secret
        self._lock = asyncio.Lock()
        self._data: dict[str, Any] = {
            "targets": {},
            "panel": {},
            "owner": {},
            "admins": {},
            "health": {
                "enabled": True,
                "times": "09:00",
                "chat_id": "",
            },
            "ui": {
                "settings_columns": 2,
            },
            "custom_buttons": [],
            "admin_sessions": {},
            "version": 3,
        }
        self._load()

    def _load(self) -> None:
        if not self.path.is_file():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._save_sync()
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                self._data.update(raw)
                self._data.setdefault("targets", {})
                self._data.setdefault("panel", {})
                self._data.setdefault("owner", {})
                self._data.setdefault("admins", {})
                self._data.setdefault(
                    "health",
                    {"enabled": True, "times": "09:00", "chat_id": ""},
                )
                self._data.setdefault("ui", {"settings_columns": 2})
                self._data.setdefault("custom_buttons", [])
                self._data.setdefault("admin_sessions", {})
                # One-time structural migrate for older installs
                if int(self._data.get("version") or 0) < 4:
                    self.migrate_news_to_channel()
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
            logger.warning("bot_settings.json unreadable (%s); starting fresh", exc)

    def _save_sync(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.path)

    def bootstrap_from_settings(self, settings: Settings) -> bool:
        """Seed defaults from env once if empty."""
        targets = self._data.get("targets") or {}
        panel = self._data.get("panel") or {}
        owner = self._data.get("owner") or {}
        seeded = False
        if not targets:
            hhmm = settings.nightly_iran_time.strftime("%H:%M")
            channel = MessageTarget(
                key="channel",
                chat_id=settings.social_news_chat_id or "@blackFoxVPNN",
                enabled=True,
            )
            channel.slots[0] = MessageSlot(
                index=0,
                kind="news",
                chat_id=settings.social_news_chat_id or "@blackFoxVPNN",
                schedule_times=settings.social_news_times or "10:00,17:00",
                rules_prompt=DEFAULT_SOCIAL_RULES,
                enabled=True,
            )
            channel.slots[2] = MessageSlot(
                index=2,
                kind="config",
                chat_id=settings.social_news_chat_id or "@blackFoxVPNN",
                message_template=DEFAULT_NIGHTLY_TEMPLATE,
                schedule_times=hhmm,
                rules_prompt="پیام کانفیگ رایگان زمان‌بندی‌شده برای کانال.",
                enabled=True,
            )
            support = MessageTarget(
                key="support",
                chat_id="",
                enabled=True,
            )
            support.slots[0] = MessageSlot(
                index=0,
                kind="static",
                chat_id="",
                schedule_times="",
                message_template="پیام زمان‌بندی‌شده برای کاربر.",
                rules_prompt="فقط پیام کوتاه و مودبانه برای اکانت کاربر بفرست.",
                enabled=False,
            )
            support.slots[1] = MessageSlot(index=1, kind="static", enabled=False)
            support.slots[2] = MessageSlot(index=2, kind="static", enabled=False)
            self._data["targets"] = {
                "channel": channel.to_dict(),
                "group": MessageTarget(key="group", chat_id="@Black_Fox_Group").to_dict(),
                "support": support.to_dict(),
                "test": MessageTarget(
                    key="test",
                    chat_id=settings.convo_analysis_chat_id,
                    schedule_times=settings.convo_analysis_times,
                    rules_prompt="خروجی تحلیل مکالمات برای اکانت تست/مدیر.",
                ).to_dict(),
            }
            seeded = True
        if not panel or not panel.get("base_url"):
            self._data["panel"] = PanelSettings(
                base_url=settings.panel_base_url,
                api_token_enc=encrypt_secret(settings.panel_api_token, self._master)
                if settings.panel_api_token
                else "",
                required_port=settings.panel_required_port,
                inbound_ids=settings.panel_inbound_ids,
            ).to_dict()
            seeded = True
        if not owner or not any(owner.values()):
            self._data["owner"] = OwnerInfo(
                site_url="https://foxnext.net",
                channel="@blackFoxVPNN",
                group="@Black_Fox_Group",
                support_handle="@HiBlackFoxVpn",
                bot_display_name="Smart Support Bot",
            ).to_dict()
            seeded = True
        if seeded:
            self._save_sync()
        # Always migrate legacy news-on-account → channel (idempotent).
        if self.migrate_news_to_channel():
            seeded = True
        return seeded

    def migrate_news_to_channel(self) -> bool:
        """Move news slots/rules from Account(support) into Channel; keep account static-only."""
        targets = self._data.setdefault("targets", {})
        changed = False

        channel = MessageTarget.from_dict(
            "channel",
            targets.get("channel") if isinstance(targets.get("channel"), dict) else {},
        )
        support = MessageTarget.from_dict(
            "support",
            targets.get("support") if isinstance(targets.get("support"), dict) else {},
        )
        owner = OwnerInfo.from_dict(self._data.get("owner"))

        def _looks_like_news(slot: MessageSlot) -> bool:
            if slot.kind == "news":
                return True
            rules = slot.rules_prompt or ""
            low = rules.lower()
            return (
                "خبر" in rules
                or "news" in low
                or "تحلیلگر اخبار" in rules
                or ("iran" in low and "vpn" in low)
                or "اینترنت ایران" in rules
            )

        # Collect news material from support (even if kind was wrongly left as static)
        news_from_support: MessageSlot | None = None
        for s in support.slots:
            if _looks_like_news(s) and (s.schedule_times or s.rules_prompt or s.chat_id):
                news_from_support = s
                break

        news_idx = next((i for i, s in enumerate(channel.slots) if s.kind == "news"), None)
        channel_has_useful_news = news_idx is not None and (
            channel.slots[news_idx].schedule_times or channel.slots[news_idx].rules_prompt
        )

        # Pick a channel slot for news: existing news slot, else first non-config empty, else slot 1
        if news_idx is None:
            for i, s in enumerate(channel.slots):
                if s.kind != "config" and not (s.schedule_times or s.message_template):
                    news_idx = i
                    break
            if news_idx is None:
                news_idx = 1 if len(channel.slots) > 1 else 0

        if news_from_support and not channel_has_useful_news:
            dest = (
                owner.channel
                or channel.chat_id
                or (news_from_support.chat_id if not str(news_from_support.chat_id or "").isdigit() else "")
                or "@blackFoxVPNN"
            )
            times = news_from_support.schedule_times or "10:00,17:00"
            # If support had no schedule, keep default news times
            if not news_from_support.schedule_times and "10:00" not in times:
                times = "10:00,17:00"
            channel.slots[news_idx] = MessageSlot(
                index=news_idx,
                kind="news",
                chat_id=dest if not str(dest).isdigit() else (owner.channel or "@blackFoxVPNN"),
                message_template="",
                schedule_times=times if times else "10:00,17:00",
                rules_prompt=news_from_support.rules_prompt or DEFAULT_SOCIAL_RULES,
                enabled=True,
            )
            if not channel.chat_id or str(channel.chat_id).strip().isdigit():
                channel.chat_id = owner.channel or "@blackFoxVPNN"
            changed = True
        elif news_idx is not None and channel.slots[news_idx].kind != "news" and not channel_has_useful_news:
            # Ensure a dedicated news slot exists on channel
            s = channel.slots[news_idx]
            channel.slots[news_idx] = MessageSlot(
                index=news_idx,
                kind="news",
                chat_id=s.chat_id or channel.chat_id or owner.channel or "@blackFoxVPNN",
                schedule_times=s.schedule_times or "10:00,17:00",
                rules_prompt=s.rules_prompt or DEFAULT_SOCIAL_RULES,
                enabled=True,
            )
            changed = True

        # Convert support news-like slots → clean static user messages
        for i, s in enumerate(support.slots):
            if _looks_like_news(s) or s.kind == "news":
                support.slots[i] = MessageSlot(
                    index=i,
                    kind="static",
                    chat_id=s.chat_id if str(s.chat_id or "").isdigit() else (s.chat_id or ""),
                    message_template="",
                    schedule_times="",
                    rules_prompt="فقط پیام کوتاه و مودبانه برای اکانت کاربر بفرست.",
                    enabled=False,
                )
                changed = True

        if changed:
            targets["channel"] = channel.to_dict()
            targets["support"] = support.to_dict()
            self._data["targets"] = targets
            self._data["version"] = max(int(self._data.get("version") or 0), 4)
            self._save_sync()
            logger.info("Migrated news settings from Account → Channel")
        return changed

    async def get_owner(self) -> OwnerInfo:
        async with self._lock:
            return OwnerInfo.from_dict(self._data.get("owner"))

    async def update_owner(self, **fields: Any) -> OwnerInfo:
        async with self._lock:
            cur = OwnerInfo.from_dict(self._data.get("owner"))
            for k, v in fields.items():
                if hasattr(cur, k):
                    setattr(cur, k, str(v or "").strip())
            self._data["owner"] = cur.to_dict()
            self._save_sync()
            return cur

    async def get_target(self, key: str) -> MessageTarget:
        async with self._lock:
            raw = (self._data.get("targets") or {}).get(key)
            return MessageTarget.from_dict(key, raw if isinstance(raw, dict) else {})

    async def list_targets(self) -> list[MessageTarget]:
        async with self._lock:
            out: list[MessageTarget] = []
            for key in TARGET_KEYS:
                raw = (self._data.get("targets") or {}).get(key)
                out.append(MessageTarget.from_dict(key, raw if isinstance(raw, dict) else {}))
            return out

    async def update_target(self, key: str, **fields: Any) -> MessageTarget:
        if key not in TARGET_KEYS:
            raise ValueError(f"unknown target key: {key}")
        async with self._lock:
            cur = MessageTarget.from_dict(
                key,
                (self._data.get("targets") or {}).get(key)
                if isinstance((self._data.get("targets") or {}).get(key), dict)
                else {},
            )
            for k, v in fields.items():
                if k == "slots" and isinstance(v, list):
                    cur.slots = v
                elif hasattr(cur, k) and k != "key":
                    setattr(cur, k, v)
            # Keep legacy top-level mirrors from slot 0 for older jobs
            s0 = cur.slot(0)
            if not fields.get("chat_id"):
                cur.chat_id = cur.chat_id or s0.chat_id
            if "message_template" not in fields and s0.message_template:
                cur.message_template = cur.message_template or s0.message_template
            if "schedule_times" not in fields and s0.schedule_times:
                cur.schedule_times = cur.schedule_times or s0.schedule_times
            if "rules_prompt" not in fields and s0.rules_prompt:
                cur.rules_prompt = cur.rules_prompt or s0.rules_prompt
            targets = self._data.setdefault("targets", {})
            targets[key] = cur.to_dict()
            self._save_sync()
            return cur

    async def update_slot(self, key: str, slot_index: int, **fields: Any) -> MessageTarget:
        if key not in TARGET_KEYS:
            raise ValueError(f"unknown target key: {key}")
        if not (0 <= slot_index < SLOT_COUNT):
            raise ValueError("slot_index must be 0..2")
        async with self._lock:
            cur = MessageTarget.from_dict(
                key,
                (self._data.get("targets") or {}).get(key)
                if isinstance((self._data.get("targets") or {}).get(key), dict)
                else {},
            )
            while len(cur.slots) < SLOT_COUNT:
                cur.slots.append(MessageSlot(index=len(cur.slots)))
            slot = cur.slots[slot_index]
            for k, v in fields.items():
                if hasattr(slot, k) and k != "index":
                    setattr(slot, k, v)
            cur.slots[slot_index] = slot
            # Mirror slot0 → legacy fields for job compatibility
            s0 = cur.slots[0]
            cur.chat_id = cur.chat_id or s0.chat_id
            if slot_index == 0:
                cur.message_template = s0.message_template
                cur.schedule_times = s0.schedule_times
                cur.rules_prompt = s0.rules_prompt
                if s0.chat_id:
                    cur.chat_id = s0.chat_id
            # Channel news/config mirrors for job helpers (enabled slots only)
            if key == "channel":
                for s in cur.slots:
                    if s.kind == "config" and s.enabled and s.schedule_times:
                        cur.schedule_times = s.schedule_times
                        if s.message_template:
                            cur.message_template = s.message_template
                        if s.chat_id:
                            cur.chat_id = s.chat_id
                    if s.kind == "news" and s.enabled and s.schedule_times:
                        if s.chat_id:
                            cur.chat_id = cur.chat_id or s.chat_id
            # Account section never stores news
            if key == "support":
                for i, s in enumerate(cur.slots):
                    if s.kind == "news":
                        cur.slots[i].kind = "static"
            targets = self._data.setdefault("targets", {})
            targets[key] = cur.to_dict()
            self._save_sync()
            return cur

    async def get_panel(self) -> PanelSettings:
        async with self._lock:
            return PanelSettings.from_dict(self._data.get("panel"))

    def panel_token(self, panel: PanelSettings) -> str:
        return decrypt_secret(panel.api_token_enc, self._master)

    def mask_panel_token(self, panel: PanelSettings) -> str:
        return mask_api_key(self.panel_token(panel))

    async def update_panel(self, **fields: Any) -> PanelSettings:
        async with self._lock:
            panel = PanelSettings.from_dict(self._data.get("panel"))
            if "api_token" in fields:
                token = str(fields.pop("api_token") or "").strip()
                if token:
                    panel.api_token_enc = encrypt_secret(token, self._master)
            if "inbound_ids" in fields or "inbound_id" in fields:
                raw_ids = fields.pop("inbound_ids", None)
                if raw_ids is None:
                    raw_ids = fields.pop("inbound_id", None)
                else:
                    fields.pop("inbound_id", None)
                panel.inbound_ids = normalize_inbound_ids(raw_ids)
            for k, v in fields.items():
                if hasattr(panel, k) and k != "api_token_enc":
                    setattr(panel, k, v)
            if panel.base_url:
                panel.base_url = panel.base_url.rstrip("/")
            self._data["panel"] = panel.to_dict()
            self._save_sync()
            return panel

    async def effective_nightly_chat_id(self, settings: Settings) -> str:
        """Destination only from an *enabled* config slot. Never inherit from a disabled slot."""
        t = await self.get_target("channel")
        config_slots = [s for s in t.slots if s.kind == "config"]
        active = [s for s in config_slots if s.enabled]
        if not active:
            # No enabled config slot → do not post (even if legacy target chat_id exists)
            return ""
        for s in active:
            cid = (s.chat_id or "").strip()
            if cid:
                return cid
        # Enabled slot(s) with empty per-slot chat → allow target-level chat_id only
        return (t.chat_id or "").strip()

    async def effective_nightly_times(self, settings: Settings) -> str:
        """Schedule only from an *enabled* config slot that has times. Never use disabled slot times."""
        t = await self.get_target("channel")
        config_slots = [s for s in t.slots if s.kind == "config"]
        active = [s for s in config_slots if s.enabled]
        if not active:
            return ""
        for s in active:
            if (s.schedule_times or "").strip():
                return s.schedule_times.strip()
        # Enabled but no schedule → do not fall back to disabled slots or env default
        return ""

    async def effective_nightly_template(self) -> str:
        """Template only from an *enabled* config slot. Empty means job uses built-in default only if posting."""
        t = await self.get_target("channel")
        for s in t.slots:
            if s.kind == "config" and s.enabled and s.message_template:
                return s.message_template.strip()
        # No enabled template → empty (caller must not post when slot inactive)
        return ""

    async def effective_social_chat_id(self, settings: Settings) -> str:
        """News posts always target Channel (never personal Account)."""
        channel = await self.get_target("channel")
        news_slots = [s for s in channel.slots if s.kind == "news"]
        for s in news_slots:
            if s.enabled and (s.chat_id or channel.chat_id):
                return (s.chat_id or channel.chat_id).strip()
        if news_slots:
            # News slot(s) exist but none enabled → do not post
            return ""
        if (channel.chat_id or "").strip():
            return channel.chat_id.strip()
        owner = await self.get_owner()
        return (
            owner.channel
            or settings.social_news_chat_id
            or ""
        ).strip()

    async def effective_social_times(self, settings: Settings) -> str:
        channel = await self.get_target("channel")
        news_slots = [s for s in channel.slots if s.kind == "news"]
        active = [s for s in news_slots if s.enabled]
        if not active:
            return ""
        for s in active:
            if (s.schedule_times or "").strip():
                return s.schedule_times.strip()
        # Enabled news slot(s) without times → do not use disabled slots or env defaults
        return ""

    async def effective_social_rules(self) -> str:
        channel = await self.get_target("channel")
        for s in channel.slots:
            if s.kind == "news" and s.enabled and s.rules_prompt:
                return s.rules_prompt.strip()
        # No enabled news rules → empty (do not reuse disabled-slot or default rules for a dead slot)
        return ""

    async def effective_test_chat_id(self, settings: Settings) -> str:
        t = await self.get_target("test")
        return (t.effective_chat_id(0) or settings.convo_analysis_chat_id).strip()

    async def effective_test_times(self, settings: Settings) -> str:
        t = await self.get_target("test")
        for s in t.slots:
            if s.schedule_times:
                return s.schedule_times.strip()
        return (t.schedule_times or settings.convo_analysis_times).strip()

    async def effective_group_chat_id(self) -> str:
        t = await self.get_target("group")
        return (t.effective_chat_id(0) or "").strip()

    async def effective_panel(self, settings: Settings) -> tuple[str, str, list[int]]:
        panel = await self.get_panel()
        base = panel.base_url or settings.panel_base_url
        token = self.panel_token(panel) or settings.panel_api_token
        inbound_ids = panel.inbound_id_list() or parse_inbound_ids(settings.panel_inbound_ids)
        return base.rstrip("/"), token, inbound_ids

    async def get_session(self, admin_id: int) -> dict[str, Any]:
        async with self._lock:
            sess = (self._data.get("admin_sessions") or {}).get(str(admin_id))
            return deepcopy(sess) if isinstance(sess, dict) else {}

    async def set_session(self, admin_id: int, session: dict[str, Any]) -> None:
        async with self._lock:
            sessions = self._data.setdefault("admin_sessions", {})
            sessions[str(admin_id)] = deepcopy(session)
            self._save_sync()

    async def clear_session(self, admin_id: int) -> None:
        async with self._lock:
            sessions = self._data.setdefault("admin_sessions", {})
            sessions.pop(str(admin_id), None)
            self._save_sync()

    async def get_admin_role(self, user_id: int) -> str:
        async with self._lock:
            raw = (self._data.get("admins") or {}).get(str(int(user_id)))
            if isinstance(raw, dict):
                role = str(raw.get("role") or "").strip().lower()
            else:
                role = str(raw or "").strip().lower()
            return role if role in {"full", "stats"} else ""

    async def list_extra_admins(self) -> list[tuple[int, str]]:
        async with self._lock:
            out: list[tuple[int, str]] = []
            for key, val in (self._data.get("admins") or {}).items():
                try:
                    uid = int(key)
                except (TypeError, ValueError):
                    continue
                if isinstance(val, dict):
                    role = str(val.get("role") or "").strip().lower()
                else:
                    role = str(val or "").strip().lower()
                if role in {"full", "stats"}:
                    out.append((uid, role))
            out.sort(key=lambda x: x[0])
            return out

    async def set_admin_role(self, user_id: int, role: str) -> None:
        role = (role or "").strip().lower()
        if role not in {"full", "stats"}:
            raise ValueError("role must be full or stats")
        async with self._lock:
            admins = self._data.setdefault("admins", {})
            admins[str(int(user_id))] = {"role": role}
            self._save_sync()

    async def remove_admin(self, user_id: int) -> bool:
        async with self._lock:
            admins = self._data.setdefault("admins", {})
            removed = admins.pop(str(int(user_id)), None) is not None
            if removed:
                self._save_sync()
            return removed

    async def get_health_settings(self) -> dict[str, Any]:
        async with self._lock:
            raw = self._data.get("health") if isinstance(self._data.get("health"), dict) else {}
            return {
                "enabled": bool(raw.get("enabled", True)),
                "times": str(raw.get("times") or "09:00").strip() or "09:00",
                "chat_id": str(raw.get("chat_id") or "").strip(),
            }

    async def update_health_settings(self, **fields: Any) -> dict[str, Any]:
        async with self._lock:
            cur = self._data.setdefault(
                "health",
                {"enabled": True, "times": "09:00", "chat_id": ""},
            )
            if not isinstance(cur, dict):
                cur = {"enabled": True, "times": "09:00", "chat_id": ""}
                self._data["health"] = cur
            if "enabled" in fields:
                cur["enabled"] = bool(fields["enabled"])
            if "times" in fields and fields["times"] is not None:
                cur["times"] = str(fields["times"]).strip() or "09:00"
            if "chat_id" in fields and fields["chat_id"] is not None:
                cur["chat_id"] = str(fields["chat_id"]).strip()
            self._save_sync()
            return dict(cur)

    async def get_ui_settings(self) -> dict[str, Any]:
        async with self._lock:
            raw = self._data.get("ui") if isinstance(self._data.get("ui"), dict) else {}
            cols = int(raw.get("settings_columns") or 2)
            return {"settings_columns": 1 if cols == 1 else 2}

    async def update_ui_settings(self, **fields: Any) -> dict[str, Any]:
        async with self._lock:
            cur = self._data.setdefault("ui", {"settings_columns": 2})
            if not isinstance(cur, dict):
                cur = {"settings_columns": 2}
                self._data["ui"] = cur
            if "settings_columns" in fields and fields["settings_columns"] is not None:
                cols = int(fields["settings_columns"])
                cur["settings_columns"] = 1 if cols == 1 else 2
            self._save_sync()
            return {
                "settings_columns": 1 if int(cur.get("settings_columns") or 2) == 1 else 2
            }

    async def list_custom_buttons(self, *, menu: str | None = "settings") -> list[dict[str, Any]]:
        from src.custom_buttons import CustomButton

        async with self._lock:
            raw = self._data.get("custom_buttons")
            items = raw if isinstance(raw, list) else []
            out: list[dict[str, Any]] = []
            for item in items:
                btn = CustomButton.from_dict(item if isinstance(item, dict) else None)
                if not btn or not btn.enabled:
                    continue
                if menu and btn.menu != menu:
                    continue
                out.append(btn.to_dict())
            out.sort(key=lambda b: (int(b.get("order") or 100), str(b.get("id") or "")))
            return out

    async def find_custom_button_by_label(self, label: str) -> dict[str, Any] | None:
        from src.custom_buttons import CustomButton

        needle = (label or "").strip()
        if not needle:
            return None
        async with self._lock:
            raw = self._data.get("custom_buttons")
            items = raw if isinstance(raw, list) else []
            for item in items:
                btn = CustomButton.from_dict(item if isinstance(item, dict) else None)
                if not btn or not btn.enabled:
                    continue
                if needle in btn.labels():
                    return btn.to_dict()
        return None

    async def add_custom_button(self, payload: dict[str, Any]) -> dict[str, Any]:
        from src.custom_buttons import ALLOWED_ACTIONS, ALLOWED_MENUS, CustomButton, new_button_id

        btn = CustomButton.from_dict(payload)
        if btn is None:
            raise ValueError("invalid custom button")
        if btn.action not in ALLOWED_ACTIONS:
            raise ValueError(f"action not allowed: {btn.action}")
        if btn.menu not in ALLOWED_MENUS:
            raise ValueError(f"menu not allowed: {btn.menu}")
        if not btn.id:
            btn.id = new_button_id()
        async with self._lock:
            cur = self._data.setdefault("custom_buttons", [])
            if not isinstance(cur, list):
                cur = []
                self._data["custom_buttons"] = cur
            # Replace same id or same label
            kept: list[Any] = []
            for item in cur:
                old = CustomButton.from_dict(item if isinstance(item, dict) else None)
                if not old:
                    continue
                if old.id == btn.id:
                    continue
                if old.labels() & btn.labels():
                    continue
                kept.append(old.to_dict())
            kept.append(btn.to_dict())
            self._data["custom_buttons"] = kept
            self._save_sync()
            return btn.to_dict()

    async def remove_custom_button(
        self, *, button_id: str = "", label: str = ""
    ) -> dict[str, Any] | None:
        from src.custom_buttons import CustomButton

        bid = (button_id or "").strip()
        lab = (label or "").strip()
        async with self._lock:
            cur = self._data.get("custom_buttons")
            items = cur if isinstance(cur, list) else []
            kept: list[Any] = []
            removed: dict[str, Any] | None = None
            for item in items:
                btn = CustomButton.from_dict(item if isinstance(item, dict) else None)
                if not btn:
                    continue
                hit = False
                if bid and btn.id == bid:
                    hit = True
                elif lab and lab in btn.labels():
                    hit = True
                if hit and removed is None:
                    removed = btn.to_dict()
                    continue
                kept.append(btn.to_dict())
            if removed is not None:
                self._data["custom_buttons"] = kept
                self._save_sync()
            return removed

    async def list_all_custom_buttons_raw(self) -> list[dict[str, Any]]:
        async with self._lock:
            raw = self._data.get("custom_buttons")
            return list(raw) if isinstance(raw, list) else []

    async def export_backup(self) -> dict[str, Any]:
        """Export settings (panel token decrypted). Sessions excluded."""
        from datetime import datetime, timezone

        async with self._lock:
            panel = PanelSettings.from_dict(self._data.get("panel"))
            token = self.panel_token(panel)
            admins_out: dict[str, str] = {}
            for k, v in (self._data.get("admins") or {}).items():
                if isinstance(v, dict):
                    role = str(v.get("role") or "")
                else:
                    role = str(v or "")
                if role in {"full", "stats"}:
                    admins_out[str(k)] = role
            health = self._data.get("health") if isinstance(self._data.get("health"), dict) else {}
            return {
                "format": "smart-support-bot-settings",
                "version": 1,
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "owner": deepcopy(self._data.get("owner") or {}),
                "targets": deepcopy(self._data.get("targets") or {}),
                "panel": {
                    "base_url": panel.base_url,
                    "api_token": token,
                    "inbound_ids": panel.inbound_ids,
                },
                "admins": admins_out,
                "health": {
                    "enabled": bool(health.get("enabled", True)),
                    "times": str(health.get("times") or "09:00"),
                    "chat_id": str(health.get("chat_id") or ""),
                },
                "ui": {
                    "settings_columns": 1
                    if int((self._data.get("ui") or {}).get("settings_columns") or 2) == 1
                    else 2
                },
                "custom_buttons": deepcopy(self._data.get("custom_buttons") or []),
            }

    async def import_backup(self, payload: dict[str, Any]) -> list[str]:
        """Import backup JSON. Returns list of applied section names."""
        if not isinstance(payload, dict):
            raise ValueError("invalid backup")
        fmt = str(payload.get("format") or "")
        if fmt and fmt != "smart-support-bot-settings":
            raise ValueError("unknown backup format")
        applied: list[str] = []
        async with self._lock:
            if isinstance(payload.get("owner"), dict):
                self._data["owner"] = OwnerInfo.from_dict(payload["owner"]).to_dict()
                applied.append("owner")
            if isinstance(payload.get("targets"), dict):
                targets: dict[str, Any] = {}
                for key in TARGET_KEYS:
                    raw = payload["targets"].get(key)
                    targets[key] = MessageTarget.from_dict(
                        key, raw if isinstance(raw, dict) else {}
                    ).to_dict()
                self._data["targets"] = targets
                applied.append("targets")
            if isinstance(payload.get("panel"), dict):
                p = payload["panel"]
                token = str(p.get("api_token") or "").strip()
                enc_in = str(p.get("api_token_enc") or "").strip()
                if token:
                    enc = encrypt_secret(token, self._master)
                elif enc_in:
                    # Already encrypted blob from same bot, or re-encrypt if decrypt works
                    plain = decrypt_secret(enc_in, self._master)
                    enc = enc_in if plain else encrypt_secret(enc_in, self._master)
                else:
                    enc = ""
                self._data["panel"] = PanelSettings(
                    base_url=str(p.get("base_url") or "").rstrip("/"),
                    api_token_enc=enc,
                    required_port=int(p.get("required_port") or 443),
                    inbound_ids=(
                        normalize_inbound_ids(p.get("inbound_ids") or p.get("inbound_id") or "")
                        if (p.get("inbound_ids") or p.get("inbound_id"))
                        else ""
                    ),
                ).to_dict()
                applied.append("panel")
            if isinstance(payload.get("admins"), dict):
                admins: dict[str, Any] = {}
                for k, v in payload["admins"].items():
                    role = str(v.get("role") if isinstance(v, dict) else v).strip().lower()
                    if role in {"full", "stats"}:
                        admins[str(k)] = {"role": role}
                self._data["admins"] = admins
                applied.append("admins")
            if isinstance(payload.get("health"), dict):
                h = payload["health"]
                self._data["health"] = {
                    "enabled": bool(h.get("enabled", True)),
                    "times": str(h.get("times") or "09:00").strip() or "09:00",
                    "chat_id": str(h.get("chat_id") or "").strip(),
                }
                applied.append("health")
            if isinstance(payload.get("ui"), dict):
                cols = int(payload["ui"].get("settings_columns") or 2)
                self._data["ui"] = {"settings_columns": 1 if cols == 1 else 2}
                applied.append("ui")
            if isinstance(payload.get("custom_buttons"), list):
                from src.custom_buttons import CustomButton

                cleaned: list[dict[str, Any]] = []
                for item in payload["custom_buttons"]:
                    btn = CustomButton.from_dict(item if isinstance(item, dict) else None)
                    if btn:
                        cleaned.append(btn.to_dict())
                self._data["custom_buttons"] = cleaned
                applied.append("custom_buttons")
            if applied:
                self._data["version"] = max(int(self._data.get("version") or 0), 3)
                self._save_sync()
        return applied

    def format_owner_card(self, owner: OwnerInfo, *, lang: str = "fa") -> str:
        fa = (lang or "").startswith("fa")
        if fa:
            return (
                "📋 اطلاعات اصلی\n\n"
                f"نام ربات: {owner.bot_display_name or '—'}\n"
                f"سایت: {owner.site_url or '—'}\n"
                f"کانال: {owner.channel or '—'}\n"
                f"گروه: {owner.group or '—'}\n"
                f"پشتیبانی مالک: {owner.support_handle or '—'}\n\n"
                "ربات و Ask AI از این اطلاعات در جواب‌ها استفاده می‌کنند."
            )
        return (
            "📋 Main Info\n\n"
            f"Bot name: {owner.bot_display_name or '-'}\n"
            f"Site: {owner.site_url or '-'}\n"
            f"Channel: {owner.channel or '-'}\n"
            f"Group: {owner.group or '-'}\n"
            f"Owner support: {owner.support_handle or '-'}\n\n"
            "Ask AI uses these contacts in answers."
        )

    def format_target_card(self, target: MessageTarget, *, lang: str = "fa") -> str:
        fa = (lang or "").startswith("fa")
        title = TARGET_TITLE_FA.get(target.key, target.key) if fa else TARGET_TITLE_EN.get(
            target.key, target.key
        )
        lines = [
            f"📨 {'تنظیمات' if fa else 'Settings'} {title}",
            f"{'مقصد پیش‌فرض' if fa else 'Default destination'}: {target.chat_id or ('—' if fa else '-')}",
            "",
        ]
        for s in target.slots:
            kind = SLOT_KIND_FA.get(s.kind, s.kind) if fa else SLOT_KIND_EN.get(s.kind, s.kind)
            on = ("بله" if s.enabled else "خیر") if fa else ("yes" if s.enabled else "no")
            lines.append(f"— {'اسلات' if fa else 'Slot'} {s.index + 1} ({kind})")
            lines.append(f"  {'مقصد' if fa else 'Dest'}: {s.chat_id or ('(پیش‌فرض)' if fa else '(default)')}")
            lines.append(f"  {'زمان' if fa else 'Time'}: {s.schedule_times or ('—' if fa else '-')}")
            lines.append(f"  {'فعال' if fa else 'On'}: {on}")
            rules = s.rules_prompt or ("—" if fa else "-")
            if len(rules) > 120:
                rules = rules[:120] + "…"
            lines.append(f"  {'قوانین' if fa else 'Rules'}: {rules}")
            lines.append("")
        return "\n".join(lines).strip()

    def format_slot_card(
        self, target: MessageTarget, slot_index: int, *, lang: str = "fa"
    ) -> str:
        fa = (lang or "").startswith("fa")
        s = target.slot(slot_index)
        kind = SLOT_KIND_FA.get(s.kind, s.kind) if fa else SLOT_KIND_EN.get(s.kind, s.kind)
        tmpl = s.message_template or ("—" if fa else "-")
        if len(tmpl) > 400:
            tmpl = tmpl[:400] + "…"
        rules = s.rules_prompt or ("—" if fa else "-")
        if len(rules) > 300:
            rules = rules[:300] + "…"
        if fa:
            return (
                f"✏️ اسلات {slot_index + 1} — {kind}\n"
                f"مقصد: {s.chat_id or target.chat_id or '—'}\n"
                f"زمان: {s.schedule_times or '—'}\n"
                f"فعال: {'بله' if s.enabled else 'خیر'}\n\n"
                f"متن پیام:\n{tmpl}\n\n"
                f"پرامپت قوانین و چت با AI:\n{rules}"
            )
        return (
            f"✏️ Slot {slot_index + 1} — {kind}\n"
            f"Dest: {s.chat_id or target.chat_id or '-'}\n"
            f"Time: {s.schedule_times or '-'}\n"
            f"Enabled: {'yes' if s.enabled else 'no'}\n\n"
            f"Message:\n{tmpl}\n\n"
            f"Rules prompt & AI chat:\n{rules}"
        )

    def format_panel_card(self, panel: PanelSettings, *, lang: str = "fa") -> str:
        fa = (lang or "").startswith("fa")
        masked = self.mask_panel_token(panel)
        inbound_disp = panel.inbound_ids or "—"
        if fa:
            return (
                "🖥 تنظیمات پنل و API\n"
                f"آدرس پنل: {panel.base_url or '—'}\n"
                f"وضعیت API: {masked}\n"
                f"شناسه Inbound: {inbound_disp}"
            )
        return (
            "🖥 Panel & API settings\n"
            f"Panel URL: {panel.base_url or '-'}\n"
            f"API status: {masked}\n"
            f"Inbound ID(s): {inbound_disp}"
        )
