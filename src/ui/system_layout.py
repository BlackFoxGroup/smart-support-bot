"""Editable system-button layout (remove/rename) applied via safe-change.

Buttons listed under ``removed[menu]`` are omitted from that menu's keyboard.
``renames[action]`` overrides FA/EN labels used by keyboards and resolve_action.
Locked actions cannot be removed or renamed via bot_config_chat.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

from src.safety.api import request_safe_change

logger = logging.getLogger(__name__)

_LAYOUT_PATH = Path(__file__).resolve().parent.parent / "generated" / "ui_layout.json"

# Never removable / renamable via chat (navigation + entry + config chat + creator).
LOCKED_ACTIONS: frozenset[str] = frozenset(
    {
        "cancel",
        "nav_back",
        "settings_back",
        "stats_back",
        "bot_config_chat",
        "creator_contact",
        # Main-menu entry points (labels live in ui/keyboards.py; reserved here).
        "settings",
        "bot_stats",
        "settings_hub",
    }
)

# action_id → menus where it appears as a system (hardcoded) button
SYSTEM_PLACEMENTS: dict[str, tuple[str, ...]] = {
    "owner_info": ("settings",),
    "bot_config_chat": ("settings",),
    "build_catalogs": ("settings",),
    "products_hub": ("settings",),
    "change_agent_api": ("settings",),
    "settings_messages": ("settings",),
    "settings_panel": ("settings",),
    "backup_settings": ("settings",),
    "health_status": ("settings", "stats", "health"),
    "manage_admins": ("settings",),
    "creator_contact": ("settings",),
    "stats_report": ("stats",),
    "users_list": ("stats",),
    "news_report": ("stats",),
    "stats_back": ("stats", "settings", "control"),
    "backup_export": ("backup",),
    "backup_import": ("backup",),
    "settings_back": ("backup", "health", "admins", "owner", "messages", "panel", "api"),
    "health_toggle": ("health",),
    "health_times": ("health",),
    "health_chat": ("health",),
    "admin_role_full": ("admins",),
    "admin_role_stats": ("admins",),
    "admin_remove": ("admins",),
    "owner_bot_name": ("owner",),
    "owner_site": ("owner",),
    "owner_channel": ("owner",),
    "owner_group": ("owner",),
    "owner_support": ("owner",),
    "msg_channel": ("messages",),
    "msg_group": ("messages",),
    "msg_account": ("messages",),
    "msg_test": ("messages",),
    "edit_panel_url": ("panel",),
    "edit_panel_token": ("panel",),
    "edit_panel_inbound": ("panel",),
}

MENU_ALIASES: dict[str, tuple[str, ...]] = {
    "stats": ("آمار", "stats", "statistics", "statistic"),
    "settings": ("تنظیمات", "settings", "setting"),
    "health": ("سلامت", "health"),
    "backup": ("پشتیبان", "backup"),
    "admins": ("ادمین", "admins", "admin"),
    "owner": ("اطلاعات اصلی", "مالک", "owner"),
    "messages": ("پیام", "messages", "message"),
    "panel": ("پنل", "panel"),
}

_cache: dict[str, Any] | None = None


def layout_path() -> Path:
    return _LAYOUT_PATH


def _empty() -> dict[str, Any]:
    return {"removed": {}, "renames": {}}


def load_layout(*, refresh: bool = False) -> dict[str, Any]:
    global _cache
    if not refresh and _cache is not None:
        return dict(_cache)
    data = _empty()
    if _LAYOUT_PATH.is_file():
        try:
            raw = json.loads(_LAYOUT_PATH.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                removed = raw.get("removed") if isinstance(raw.get("removed"), dict) else {}
                renames = raw.get("renames") if isinstance(raw.get("renames"), dict) else {}
                data = {
                    "removed": {
                        str(k): [str(x) for x in (v or []) if str(x).strip()]
                        for k, v in removed.items()
                        if isinstance(v, list)
                    },
                    "renames": {
                        str(k): {
                            "fa": str((v or {}).get("fa") or ""),
                            "en": str((v or {}).get("en") or ""),
                        }
                        for k, v in renames.items()
                        if isinstance(v, dict)
                    },
                }
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            logger.warning("ui_layout unreadable: %s", exc)
    _cache = data
    return dict(data)


def dump_layout(data: dict[str, Any]) -> str:
    clean = {
        "removed": {
            str(menu): sorted({str(a) for a in ids if str(a).strip()})
            for menu, ids in (data.get("removed") or {}).items()
            if isinstance(ids, list) and ids
        },
        "renames": {
            str(aid): {"fa": str(lab.get("fa") or ""), "en": str(lab.get("en") or "")}
            for aid, lab in (data.get("renames") or {}).items()
            if isinstance(lab, dict) and (lab.get("fa") or lab.get("en"))
        },
    }
    return json.dumps(clean, ensure_ascii=False, indent=2) + "\n"


def is_removed(action: str, menu: str) -> bool:
    data = load_layout()
    removed = data.get("removed") or {}
    ids = removed.get(menu) or []
    return action in ids


def filter_actions(menu: str, actions: list[str]) -> list[str]:
    return [a for a in actions if not is_removed(a, menu)]


def rename_for(action: str) -> dict[str, str] | None:
    data = load_layout()
    lab = (data.get("renames") or {}).get(action)
    if not isinstance(lab, dict):
        return None
    fa = str(lab.get("fa") or "").strip()
    en = str(lab.get("en") or "").strip()
    if not fa and not en:
        return None
    return {"fa": fa or en, "en": en or fa}


def is_locked(action: str) -> bool:
    return action in LOCKED_ACTIONS


def resolve_menu_hint(text: str) -> str | None:
    raw = text or ""
    low = raw.lower()
    # Explicit "از آمار" / "from stats" wins over words inside the button label.
    explicit = re.search(
        r"(?:از\s+منوی\s+|از\s+|from\s+|in\s+|on\s+)([^\s,،]+)",
        raw,
        flags=re.IGNORECASE,
    )
    if explicit:
        token = explicit.group(1).strip().lower()
        for menu, aliases in MENU_ALIASES.items():
            for alias in aliases:
                if token == alias.lower() or alias.lower() in token or token in alias.lower():
                    return menu
    for menu, aliases in MENU_ALIASES.items():
        for alias in aliases:
            if alias.lower() in low or alias in raw:
                return menu
    return None


def _strip_menu_phrase(chunk: str) -> str:
    out = (chunk or "").strip()
    out = re.sub(
        r"\s*(از\s+منوی\s+|از\s+|in\s+|from\s+|on\s+).*$",
        "",
        out,
        flags=re.IGNORECASE,
    ).strip()
    for menu, aliases in MENU_ALIASES.items():
        for alias in aliases:
            out = re.sub(
                rf"\b{re.escape(alias)}\b",
                "",
                out,
                flags=re.IGNORECASE,
            ).strip()
        _ = menu
    return out.strip(" :-،,")


def match_system_button(
    *,
    label: str = "",
    button_id: str = "",
    menu: str | None = None,
    labels_table: dict[str, dict[str, str]] | None = None,
) -> tuple[str, str] | None:
    """Return (action_id, menu) or None."""
    bid = (button_id or "").strip()
    lab = _strip_menu_phrase(label)
    needle = lab or bid
    if not needle:
        return None

    if bid and bid in SYSTEM_PLACEMENTS:
        menus = SYSTEM_PLACEMENTS[bid]
        pick = menu if menu in menus else (menus[0] if menus else (menu or "settings"))
        return bid, pick

    # Exact action id as free text
    if needle in SYSTEM_PLACEMENTS:
        menus = SYSTEM_PLACEMENTS[needle]
        pick = menu if menu in menus else menus[0]
        return needle, pick

    table = labels_table or {}
    hits: list[tuple[str, str]] = []
    for action, langs in table.items():
        if action not in SYSTEM_PLACEMENTS:
            continue
        values = [str(v) for v in langs.values()]
        rename = rename_for(action)
        if rename:
            values.extend([rename["fa"], rename["en"]])
        for v in values:
            vv = v.strip()
            if not vv:
                continue
            if needle == vv or needle in vv or vv in needle:
                menus = SYSTEM_PLACEMENTS[action]
                pick = menu if menu and menu in menus else menus[0]
                hits.append((action, pick))
                break
    if not hits:
        return None
    if menu:
        scoped = [h for h in hits if h[1] == menu or menu in SYSTEM_PLACEMENTS.get(h[0], ())]
        if scoped:
            # Prefer placement matching requested menu
            for action, _m in scoped:
                if menu in SYSTEM_PLACEMENTS.get(action, ()):
                    return action, menu
            return scoped[0]
    return hits[0]


def queue_system_button_change(
    *,
    op: str,
    action: str,
    menu: str,
    label_fa: str = "",
    label_en: str = "",
    description: str = "",
    admin_chat_id: str | int | None = None,
    all_menus: bool = False,
) -> dict[str, Any]:
    action = (action or "").strip()
    menu = (menu or "").strip()
    op = (op or "").strip().lower()
    if not action:
        return {"ok": False, "error": "action required"}
    if action not in SYSTEM_PLACEMENTS:
        return {"ok": False, "error": f"unknown system button: {action}"}
    menus = list(SYSTEM_PLACEMENTS[action]) if all_menus or not menu else [menu]
    if not menus:
        return {"ok": False, "error": "menu required"}
    for m in menus:
        if m not in SYSTEM_PLACEMENTS[action]:
            return {"ok": False, "error": f"{action} is not on menu {m}"}
    if is_locked(action) and op in {"remove", "rename"}:
        return {"ok": False, "error": f"locked system button: {action}"}

    data = load_layout(refresh=True)
    removed: dict[str, list[str]] = {
        str(k): list(v) for k, v in (data.get("removed") or {}).items()
    }
    renames: dict[str, dict[str, str]] = {
        str(k): dict(v) for k, v in (data.get("renames") or {}).items()
    }

    if op == "remove":
        for m in menus:
            cur = list(removed.get(m) or [])
            if action not in cur:
                cur.append(action)
            removed[m] = cur
        desc = description or f"Remove system button {action} from {','.join(menus)}"
    elif op == "restore":
        for m in menus:
            cur = [a for a in (removed.get(m) or []) if a != action]
            if cur:
                removed[m] = cur
            else:
                removed.pop(m, None)
        desc = description or f"Restore system button {action} on {','.join(menus)}"
    elif op == "rename":
        fa = (label_fa or "").strip()
        en = (label_en or "").strip() or fa
        if not fa:
            return {"ok": False, "error": "rename needs label_fa"}
        renames[action] = {"fa": fa, "en": en}
        desc = description or f"Rename system button {action}"
    else:
        return {"ok": False, "error": f"bad op: {op}"}

    payload = {"removed": removed, "renames": renames}
    files = {"src/generated/ui_layout.json": dump_layout(payload)}
    return request_safe_change(
        description=desc,
        files=files,
        admin_chat_id=admin_chat_id,
        observe_seconds=60,
        confirm_seconds=30,
    )


def list_system_buttons_brief(*, labels_table: dict[str, dict[str, str]] | None = None) -> str:
    layout = load_layout(refresh=True)
    removed = layout.get("removed") or {}
    lines: list[str] = []
    for action, menus in sorted(SYSTEM_PLACEMENTS.items()):
        lock = "🔒" if is_locked(action) else ""
        fa = ""
        if labels_table and action in labels_table:
            fa = labels_table[action].get("fa") or labels_table[action].get("en") or ""
        ren = rename_for(action)
        if ren:
            fa = ren.get("fa") or fa
        gone = [m for m in menus if action in (removed.get(m) or [])]
        status = f" removed={gone}" if gone else ""
        lines.append(f"• {action}{lock} menus={list(menus)} {fa}{status}".strip())
    return "\n".join(lines)
