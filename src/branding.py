"""Open-source bot branding + locked creator contact (not admin-editable)."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

# Runtime display name — overridable via Owner Info (اطلاعات اصلی)
BOT_DISPLAY_NAME = "Smart Support Bot"
AI_ASSISTANT_NAME = "Smart Support Bot"

_DEFAULT_CREATOR = {
    "title_fa": "تماس با سازنده",
    "title_en": "Contact Creator",
    "name": "Black Fox",
    "support": "@HiBlackFoxVpn",
    "site": "https://foxnext.net",
    "channel": "@blackFoxVPNN",
    "group": "@Black_Fox_Group",
    "github": "https://github.com/BlackFoxGroup",
    "footer_fa": "",
}


@dataclass(slots=True)
class CreatorContact:
    title_fa: str
    title_en: str
    name: str
    support: str
    site: str
    channel: str
    group: str
    github: str = ""
    footer_fa: str = ""

    def format_card(self, lang: str = "fa") -> str:
        fa = (lang or "").startswith("fa")
        if fa:
            lines = [
                f"🛠 {self.title_fa}",
                "",
                f"سازنده: {self.name}",
                f"پشتیبانی: {self.support}",
                f"سایت: {self.site}",
                f"کانال: {self.channel}",
                f"گروه: {self.group}",
            ]
            if self.github:
                lines.append(f"گیت‌هاب: {self.github}")
            if self.footer_fa.strip():
                lines.append("")
                lines.append(self.footer_fa.strip())
            return "\n".join(lines)
        lines = [
            f"🛠 {self.title_en}",
            "",
            f"Creator: {self.name}",
            f"Support: {self.support}",
            f"Site: {self.site}",
            f"Channel: {self.channel}",
            f"Group: {self.group}",
        ]
        if self.github:
            lines.append(f"GitHub: {self.github}")
        if self.footer_fa.strip():
            lines.append("")
            lines.append(self.footer_fa.strip())
        return "\n".join(lines)


def get_bot_display_name() -> str:
    return (BOT_DISPLAY_NAME or "Smart Support Bot").strip()


def set_bot_display_name(name: str | None) -> None:
    global BOT_DISPLAY_NAME, AI_ASSISTANT_NAME
    cleaned = (name or "").strip()
    if cleaned:
        BOT_DISPLAY_NAME = cleaned
        AI_ASSISTANT_NAME = cleaned


async def sync_telegram_bot_name(bot, name: str | None = None) -> bool:
    """Set Telegram profile name (what users see in chats/header), not only in-app copy."""
    cleaned = (name or get_bot_display_name()).strip()
    if not cleaned:
        return False
    try:
        await bot.set_my_name(name=cleaned)
        logger.info("Telegram bot name set to %r", cleaned)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not set Telegram bot name to %r: %s", cleaned, exc)
        return False


def load_creator_contact(knowledge_root: Path | None = None) -> CreatorContact:
    data = dict(_DEFAULT_CREATOR)
    if knowledge_root is not None:
        path = knowledge_root / "creator_contact.json"
        if path.is_file():
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    for k in data:
                        if k in raw and raw[k] is not None:
                            data[k] = str(raw[k])
            except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
                logger.warning("creator_contact.json unreadable: %s", exc)
    return CreatorContact(**data)
