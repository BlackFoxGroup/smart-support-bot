"""Application configuration loaded from environment."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import time
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(
    (os.getenv("BOT_ROOT") or "").strip() or Path(__file__).resolve().parent.parent
).expanduser().resolve()
KNOWLEDGE_ROOT = PROJECT_ROOT / "knowledge"
DATA_DIR = PROJECT_ROOT / "data"
USERS_DB_PATH = DATA_DIR / "users.json"

SUPPORTED_LANGS = ("fa", "en", "ru", "zh")
DEFAULT_LANG = "en"

# Telegram language_code → bot language
LANG_ALIASES: dict[str, str] = {
    "fa": "fa",
    "fas": "fa",
    "per": "fa",
    "en": "en",
    "ru": "ru",
    "zh": "zh",
    "zh-hans": "zh",
    "zh-cn": "zh",
    "zh-hant": "zh",
    "zh-tw": "zh",
}


@dataclass(frozen=True, slots=True)
class Settings:
    telegram_bot_token: str
    ai_base_url: str
    ai_api_key: str
    ai_model: str
    ai_timeout_seconds: float
    ai_max_tokens: int
    ai_temperature: float
    intent_confidence_threshold: float
    knowledge_snippet_chars: int
    log_level: str
    project_root: Path
    knowledge_root: Path
    data_dir: Path
    users_db_path: Path
    panel_base_url: str
    panel_api_token: str
    panel_inbound_ids: str
    panel_required_port: int  # legacy; unused by panel create flow
    nightly_enabled: bool
    nightly_iran_time: time
    nightly_support_chat_id: str
    social_news_enabled: bool
    social_news_chat_id: str
    social_news_times: str
    convo_analysis_enabled: bool
    convo_analysis_times: str
    convo_analysis_chat_id: str
    convo_analysis_test_mode: bool
    convo_min_occurrences: int
    convo_min_users: int
    convo_priority_threshold: int
    bot_admin_ids: frozenset[int]
    news_report_admin_ids: frozenset[int]
    ai_budget_usd: float
    ai_usd_per_million_tokens: float
    vps_to_vpn_source: Path
    source_catalog_sync_on_start: bool

    @property
    def kb_multilingual_dir(self) -> Path:
        return self.knowledge_root / "AI_Knowledge_Base_Multilingual"

    @property
    def intents_dir(self) -> Path:
        return self.knowledge_root / "AI_BOT_DATABASE"

    @property
    def decision_tree_dir(self) -> Path:
        return self.knowledge_root / "Support_Decision_Tree"


def _require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _as_bool(raw: str | None, default: bool) -> bool:
    if raw is None:
        return default
    val = raw.strip().lower()
    if val in {"1", "true", "yes", "on"}:
        return True
    if val in {"0", "false", "no", "off"}:
        return False
    return default


def _parse_hhmm(raw: str, default_hour: int = 21) -> time:
    value = (raw or "").strip()
    if not value:
        return time(hour=default_hour, minute=0)
    parts = value.split(":")
    if len(parts) != 2:
        raise RuntimeError("NIGHTLY_IRAN_TIME must be HH:MM (example 21:00)")
    try:
        hh = int(parts[0])
        mm = int(parts[1])
    except ValueError as exc:
        raise RuntimeError("NIGHTLY_IRAN_TIME must be numeric HH:MM") from exc
    if hh < 0 or hh > 23 or mm < 0 or mm > 59:
        raise RuntimeError("NIGHTLY_IRAN_TIME is out of range")
    return time(hour=hh, minute=mm)


def _parse_id_set(raw: str | None) -> frozenset[int]:
    ids: set[int] = set()
    for token in (raw or "").split(","):
        token = token.strip()
        if not token:
            continue
        try:
            ids.add(int(token))
        except ValueError:
            continue
    return frozenset(ids)


def _parse_admin_ids(raw: str | None) -> frozenset[int]:
    # Owner sets their own Telegram user IDs in BOT_ADMIN_IDS (.env).
    # No default is injected — until set, admin-only menus are simply inaccessible.
    return _parse_id_set(raw)


def load_settings(env_file: Path | None = None) -> Settings:
    """Load `.env` then build immutable settings."""
    load_dotenv(env_file or (PROJECT_ROOT / ".env"))

    data_dir = DATA_DIR
    data_dir.mkdir(parents=True, exist_ok=True)

    return Settings(
        telegram_bot_token=_require("TELEGRAM_BOT_TOKEN"),
        ai_base_url=os.getenv("AI_BASE_URL", "https://ai.nube.sh/api/v1").rstrip("/"),
        ai_api_key=_require("AI_API_KEY"),
        ai_model=os.getenv("AI_MODEL", "kimi-k2.5").strip() or "kimi-k2.5",
        ai_timeout_seconds=float(os.getenv("AI_TIMEOUT_SECONDS", "60")),
        # Kimi K2.5 uses reasoning tokens; keep headroom so content is not truncated to null
        ai_max_tokens=int(os.getenv("AI_MAX_TOKENS", "4096")),
        ai_temperature=float(os.getenv("AI_TEMPERATURE", "0.4")),
        intent_confidence_threshold=float(
            os.getenv("INTENT_CONFIDENCE_THRESHOLD", "0.28")
        ),
        knowledge_snippet_chars=int(os.getenv("KNOWLEDGE_SNIPPET_CHARS", "12000")),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        project_root=PROJECT_ROOT,
        knowledge_root=KNOWLEDGE_ROOT,
        data_dir=data_dir,
        users_db_path=USERS_DB_PATH,
        panel_base_url=os.getenv("PANEL_BASE_URL", "").rstrip("/"),
        panel_api_token=os.getenv("PANEL_API_TOKEN", "").strip(),
        panel_inbound_ids=(os.getenv("PANEL_INBOUND_ID", "0") or "0").strip(),
        panel_required_port=int(os.getenv("PANEL_REQUIRED_PORT", "443")),
        nightly_enabled=_as_bool(os.getenv("NIGHTLY_ENABLED"), False),
        nightly_iran_time=_parse_hhmm(os.getenv("NIGHTLY_IRAN_TIME", "21:00")),
        nightly_support_chat_id=os.getenv("NIGHTLY_SUPPORT_CHAT_ID", "@HiBlackFoxVpn").strip()
        or "@HiBlackFoxVpn",
        social_news_enabled=_as_bool(os.getenv("SOCIAL_NEWS_ENABLED"), True),
        social_news_chat_id=os.getenv("SOCIAL_NEWS_CHAT_ID", "@blackFoxVPNN").strip()
        or "@blackFoxVPNN",
        social_news_times=os.getenv("SOCIAL_NEWS_TIMES", "10:00,17:00").strip() or "10:00,17:00",
        convo_analysis_enabled=_as_bool(os.getenv("CONVO_ANALYSIS_ENABLED"), False),
        convo_analysis_times=os.getenv("CONVO_ANALYSIS_TIMES", "12:30").strip() or "12:30",
        convo_analysis_chat_id=os.getenv("CONVO_ANALYSIS_CHAT_ID", "").strip(),
        convo_analysis_test_mode=_as_bool(os.getenv("CONVO_ANALYSIS_TEST_MODE"), True),
        convo_min_occurrences=int(os.getenv("CONVO_MIN_OCCURRENCES", "3")),
        convo_min_users=int(os.getenv("CONVO_MIN_USERS", "1")),
        convo_priority_threshold=int(os.getenv("CONVO_PRIORITY_THRESHOLD", "55")),
        bot_admin_ids=_parse_admin_ids(os.getenv("BOT_ADMIN_IDS")),
        # Extra IDs for Stats → Report (news). Owner (BOT_ADMIN_IDS) is always included.
        news_report_admin_ids=_parse_id_set(os.getenv("NEWS_REPORT_ADMIN_IDS")),
        ai_budget_usd=float(os.getenv("AI_BUDGET_USD", "50")),
        ai_usd_per_million_tokens=float(os.getenv("AI_USD_PER_MILLION_TOKENS", "2.0")),
        vps_to_vpn_source=Path(os.getenv("VPS_TO_VPN_SOURCE", r"F:\VPS to VPN")),
        source_catalog_sync_on_start=_as_bool(os.getenv("SOURCE_CATALOG_SYNC_ON_START"), False),
    )


def is_bot_admin(settings: Settings, user_id: int) -> bool:
    return int(user_id) in settings.bot_admin_ids


def normalize_lang(code: str | None) -> str:
    """Map Telegram / user language codes to fa|en|ru|zh."""
    if not code:
        return DEFAULT_LANG
    raw = code.strip().lower().replace("_", "-")
    if raw in LANG_ALIASES:
        return LANG_ALIASES[raw]
    primary = raw.split("-", 1)[0]
    return LANG_ALIASES.get(primary, DEFAULT_LANG)
