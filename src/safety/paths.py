"""Filesystem layout for safe-change backups and pending state.

Safety state lives outside the install tree (on VPS) so a restore cannot wipe
the watchdog's pending/confirm files. Local/dev falls back under data/.
"""

from __future__ import annotations

from pathlib import Path

# Bot package root = /opt/smart-support
INSTALL_ROOT = Path(__file__).resolve().parents[2]

_VPS_INSTALL_ROOTS = {
    Path("/opt/smart-support"),
    Path("/opt/Smart Support Bot"),
    Path("/opt/smart-support-bot"),
}

if INSTALL_ROOT in _VPS_INSTALL_ROOTS:
    # Keep safety store outside the install tree (stable path across renames).
    SAFETY_ROOT = Path("/opt/smart-support-bot-safety")
else:
    SAFETY_ROOT = INSTALL_ROOT / "data" / "bot-safety"

BACKUPS_DIR = SAFETY_ROOT / "backups"
STAGING_DIR = SAFETY_ROOT / "staging"
PENDING_PATH = SAFETY_ROOT / "pending.json"
WATCHDOG_LOG = SAFETY_ROOT / "watchdog.log"
LAST_GOOD_PATH = SAFETY_ROOT / "last_good.tar.gz"
LAST_GOOD_META = SAFETY_ROOT / "last_good.json"
CRASH_STATE_PATH = SAFETY_ROOT / "crash_guard.json"

# Bot-writable handshake files (inside install data/)
DATA_DIR = INSTALL_ROOT / "data"
HEARTBEAT_PATH = DATA_DIR / "heartbeat.json"
REQUEST_PATH = DATA_DIR / "safety_request.json"
DECISION_PATH = DATA_DIR / "safety_decision.json"

SERVICE_NAME = "smart-support-bot.service"
# After apply: wait this long so support can check the bot, then send confirm.
OBSERVE_SECONDS_DEFAULT = 60
# After confirm message is sent: wait this long for Yes/No before auto-restore.
CONFIRM_SECONDS_DEFAULT = 30
# Default support chat for confirm prompts (numeric id preferred).
# Set SAFETY_CONFIRM_CHAT_ID in .env — no default is injected, so confirm
# prompts are skipped (not misrouted) until the owner configures one.
DEFAULT_SUPPORT_CHAT_ID = ""

# Paths relative to INSTALL_ROOT that are included in backups
BACKUP_INCLUDE = (
    "src",
    "knowledge",
    "requirements.txt",
    "README.md",
    ".env",
    "deploy",
)

# Never restore over live runtime state that must survive rollback
BACKUP_EXCLUDE_PREFIXES = (
    "data/",
    ".venv/",
    "__pycache__/",
    ".git/",
)
