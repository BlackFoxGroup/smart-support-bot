"""Full settings apply protocol for bot_config_chat (all existing sections)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.ai.persona import apply_owner_info
from src.storage.bot_settings import SLOT_KINDS, TARGET_KEYS, BotSettingsStore

OWNER_FIELDS = frozenset(
    {"site_url", "channel", "group", "support_handle", "bot_display_name"}
)
OPEN_SECTIONS = frozenset(
    {
        "settings",
        "owner",
        "messages",
        "panel",
        "health",
        "backup",
        "admins",
        "channel",
        "group",
        "account",
        "support",
        "test",
        "control",
    }
)


@dataclass
class ApplyResult:
    applied: list[str] = field(default_factory=list)
    open_section: str | None = None
    show_settings_keyboard: bool = False
    status_dump: str | None = None
    errors: list[str] = field(default_factory=list)
    safe_change_queued: dict[str, Any] | None = None


def parse_kv_tokens(body: str) -> dict[str, str]:
    """Parse key=value tokens; values may be double/single-quoted."""
    out: dict[str, str] = {}
    i = 0
    s = body.strip()
    n = len(s)
    while i < n:
        while i < n and s[i].isspace():
            i += 1
        if i >= n:
            break
        eq = s.find("=", i)
        if eq < 0:
            break
        key = s[i:eq].strip()
        i = eq + 1
        if i >= n:
            break
        if s[i] in {'"', "'"}:
            quote = s[i]
            i += 1
            end = s.find(quote, i)
            if end < 0:
                val = s[i:]
                i = n
            else:
                val = s[i:end]
                i = end + 1
        else:
            j = i
            while j < n and not s[j].isspace():
                j += 1
            val = s[i:j]
            i = j
        if key:
            out[key] = val.strip()
    return out


def _parse_bool(raw: str) -> bool:
    return str(raw).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
        "بله",
        "روشن",
        "فعال",
    }


def _clip(text: str, n: int = 48) -> str:
    raw = " ".join(str(text or "").split())
    if len(raw) <= n:
        return raw
    return raw[: max(0, n - 1)] + "…"


def _slot_brief(slots: list[Any]) -> str:
    bits = []
    for s in slots:
        tmpl = _clip(s.message_template or "", 40)
        rules = _clip(s.rules_prompt or "", 40)
        bits.append(
            "{"
            f"i={s.index + 1}, kind={s.kind}, enabled={s.enabled}, "
            f"chat_id={s.chat_id!r}, times={s.schedule_times!r}, "
            f"template={tmpl!r}, rules={rules!r}"
            "}"
        )
    return "[" + ", ".join(bits) + "]"


def _yn(value: bool, *, fa: bool) -> str:
    if fa:
        return "بله" if value else "خیر"
    return "yes" if value else "no"


def _dash(value: Any, *, fa: bool) -> str:
    s = str(value or "").strip()
    if s:
        return s
    return "—" if fa else "—"


async def build_full_state_brief(bot_settings: BotSettingsStore) -> str:
    """Compact machine brief for the AI operator prompt (not for end-user display)."""
    owner = await bot_settings.get_owner()
    ui = await bot_settings.get_ui_settings()
    health = await bot_settings.get_health_settings()
    panel = await bot_settings.get_panel()
    lines = [
        f"owner={owner.to_dict()}",
        f"ui={ui}",
        f"health={health}",
        (
            f"panel={{base_url={panel.base_url!r}, inbound_ids={panel.inbound_ids!r}, "
            f"token_set={bool(bot_settings.panel_token(panel))}}}"
        ),
    ]
    for key in TARGET_KEYS:
        t = await bot_settings.get_target(key)
        lines.append(
            f"{key}={{chat_id={t.chat_id!r}, enabled={t.enabled}, slots={_slot_brief(t.slots)}}}"
        )
    customs = await bot_settings.list_custom_buttons(menu="settings")
    lines.append(
        "catalog_buttons="
        + str([f"{b.get('id')}:{b.get('label_fa')}->{b.get('action')}" for b in customs])
    )
    try:
        from src.generated.buttons import list_generated_buttons

        gens = list_generated_buttons(menu="settings", refresh=True)
        lines.append(
            "generated_buttons="
            + str([f"{b.get('id')}:{b.get('label_fa')}" for b in gens])
        )
    except Exception:  # noqa: BLE001
        lines.append("generated_buttons=[]")
    extras = await bot_settings.list_extra_admins()
    lines.append("extra_admins=" + str(extras))
    return "\n".join(lines)


async def build_human_status(bot_settings: BotSettingsStore, *, lang: str = "fa") -> str:
    """Readable STATUS for admins in Telegram (no wall-of-dict, no long dumps)."""
    fa = str(lang or "").startswith("fa")
    owner = await bot_settings.get_owner()
    ui = await bot_settings.get_ui_settings()
    health = await bot_settings.get_health_settings()
    panel = await bot_settings.get_panel()
    token_set = bool(bot_settings.panel_token(panel))

    target_title = {
        "channel": ("📢 کانال", "📢 Channel"),
        "group": ("👥 گروه", "👥 Group"),
        "support": ("🛟 پشتیبانی", "🛟 Support"),
        "test": ("🧪 تست", "🧪 Test"),
    }

    lines: list[str] = [
        "📋 وضعیت تنظیمات" if fa else "📋 Settings status",
        "",
        "👤 مالک" if fa else "👤 Owner",
        f"• {'سایت' if fa else 'site'}: {_dash(owner.site_url, fa=fa)}",
        f"• {'کانال' if fa else 'channel'}: {_dash(owner.channel, fa=fa)}",
        f"• {'گروه' if fa else 'group'}: {_dash(owner.group, fa=fa)}",
        f"• {'پشتیبانی' if fa else 'support'}: {_dash(owner.support_handle, fa=fa)}",
        f"• {'نام ربات' if fa else 'bot name'}: {_dash(owner.bot_display_name, fa=fa)}",
        "",
        "🖥 UI",
        f"• {'ستون تنظیمات' if fa else 'settings columns'}: {ui.get('settings_columns', 2)}",
        "",
        "🩺 سلامت" if fa else "🩺 Health",
        f"• {'روشن' if fa else 'enabled'}: {_yn(bool(health.get('enabled')), fa=fa)}",
        f"• {'زمان' if fa else 'times'}: {_dash(health.get('times'), fa=fa)}",
        f"• {'مقصد' if fa else 'chat'}: {_dash(health.get('chat_id'), fa=fa)}",
        "",
        "🖧 پنل" if fa else "🖧 Panel",
        f"• {'آدرس' if fa else 'url'}: "
        + ("تنظیم‌شده" if fa else "set")
        + (f" | {'توکن' if fa else 'token'}: {_yn(token_set, fa=fa)}"),
        f"• inbound: {panel.inbound_ids or ('—' if fa else '-')}",
    ]

    for key in TARGET_KEYS:
        t = await bot_settings.get_target(key)
        title_fa, title_en = target_title.get(key, (key, key))
        lines.append("")
        lines.append(
            f"{title_fa if fa else title_en}  "
            f"({_dash(t.chat_id, fa=fa)})  "
            f"{'روشن' if t.enabled else 'خاموش' if fa else ('on' if t.enabled else 'off')}"
        )
        for s in t.slots:
            empty = not (
                str(s.chat_id or "").strip()
                or str(s.schedule_times or "").strip()
                or str(s.message_template or "").strip()
                or str(s.rules_prompt or "").strip()
            )
            on = "روشن" if s.enabled else "خاموش" if fa else ("on" if s.enabled else "off")
            if empty:
                lines.append(
                    f"  • {'اسلات' if fa else 'slot'} {s.index + 1}: "
                    f"{s.kind} | {on} | {'خالی' if fa else 'empty'}"
                )
                continue
            lines.append(
                f"  • {'اسلات' if fa else 'slot'} {s.index + 1}: "
                f"{s.kind} | {on} | {_dash(s.chat_id, fa=fa)} | "
                f"{_dash(s.schedule_times, fa=fa)}"
            )
            rules = _clip(s.rules_prompt or "", 70)
            tmpl = _clip(s.message_template or "", 70)
            if rules:
                lines.append(f"    {'قوانین' if fa else 'rules'}: {rules}")
            if tmpl:
                lines.append(f"    {'قالب' if fa else 'template'}: {tmpl}")

    customs = await bot_settings.list_custom_buttons(menu="settings")
    lines.append("")
    lines.append("🔘 کلیدهای کاتالوگ" if fa else "🔘 Catalog buttons")
    if not customs:
        lines.append("  • —")
    else:
        for b in customs:
            lines.append(
                f"  • {b.get('id')}: {b.get('label_fa') or b.get('label_en')} → {b.get('action')}"
            )

    try:
        from src.generated.buttons import list_generated_buttons

        gens = list_generated_buttons(menu="settings", refresh=True)
    except Exception:  # noqa: BLE001
        gens = []
    lines.append("🧬 کلیدهای AI" if fa else "🧬 AI buttons")
    if not gens:
        lines.append("  • —")
    else:
        for b in gens:
            lines.append(f"  • {b.get('id')}: {b.get('label_fa') or b.get('label_en')}")

    extras = await bot_settings.list_extra_admins()
    lines.append("👥 ادمین اضافه" if fa else "👥 Extra admins")
    lines.append("  • " + (", ".join(str(x) for x in extras) if extras else ("—" if fa else "—")))
    return "\n".join(lines)


def operator_system_prompt() -> str:
    return (
        "You are the full Smart Support Bot settings operator for an ADMIN.\n"
        "You can edit ALL existing settings sections via APPLY_* lines.\n"
        "Never invent fake Telegram UI panels. Be concise in the admin language.\n"
        "Creator contact is view-only (OPEN_SECTION creator is ok; never APPLY it).\n"
        "For brand-new button behavior that needs new code, tell admin to say "
        "'کلید بساز: …' (that path uses safe-change). For settings edits use APPLY_*.\n"
        "System (hardcoded) buttons can be removed/restored/renamed with "
        "APPLY_SYSTEM_BUTTON (safe-change + ~1 min rollback). Locked nav buttons "
        "cannot change: cancel, nav_back, settings_back, stats_back, bot_config_chat, "
        "creator_contact, settings, bot_stats.\n"
    )


def operator_command_help() -> str:
    return (
        "Commands (one per line at end of reply):\n"
        "APPLY_OWNER site_url=...|channel=...|group=...|support_handle=...|bot_display_name=...\n"
        "APPLY_TARGET key=channel|group|support|test chat_id=@name\n"
        "APPLY_SLOT target=channel slot=1 enabled=true schedule=10:00,17:00 "
        "chat_id=@x kind=news template=\"...\" rules=\"...\"\n"
        "APPLY_PANEL base_url=https://... inbound_ids=1,2\n"
        "APPLY_HEALTH enabled=true times=09:00 chat_id=@x_or_id\n"
        "APPLY_UI settings_columns=1|2\n"
        "APPLY_ADMIN action=add|remove|set_role user_id=123456 role=full|stats\n"
        "APPLY_BUTTON_ADD label_fa=... label_en=... action=run_health_now target=channel slot=1\n"
        "APPLY_BUTTON_REMOVE id=cb_xxx OR label=...\n"
        "APPLY_SYSTEM_BUTTON op=remove|restore|rename id=health_status menu=stats "
        "label_fa=... label_en=...\n"
        "OPEN_SECTION settings|owner|messages|panel|health|backup|admins|"
        "channel|group|account|test|control\n"
        "SHOW_STATUS\n"
        "SHOW_SETTINGS_KEYBOARD\n"
    )


async def apply_operator_lines(
    lines: list[str],
    *,
    bot_settings: BotSettingsStore,
    message_bot: Any = None,
    allowed_catalog_actions: frozenset[str] | None = None,
    lang: str = "fa",
) -> ApplyResult:
    from src.custom_buttons import ALLOWED_ACTIONS, new_button_id
    from src.ui import admin_keyboards as ak

    result = ApplyResult()
    catalog_actions = allowed_catalog_actions or ALLOWED_ACTIONS

    for raw in lines:
        line = (raw or "").strip()
        if not line:
            continue
        if line == "SHOW_SETTINGS_KEYBOARD":
            result.show_settings_keyboard = True
            continue
        if line == "SHOW_STATUS":
            result.status_dump = await build_human_status(bot_settings, lang=lang)
            continue
        if line.startswith("OPEN_SECTION "):
            sec = line[len("OPEN_SECTION ") :].strip().lower()
            if sec == "support":
                sec = "account"
            if sec in OPEN_SECTIONS or sec == "creator":
                result.open_section = sec
            continue

        if line.startswith("APPLY_OWNER "):
            fields = parse_kv_tokens(line[len("APPLY_OWNER ") :])
            # also support single key=value without parser edge cases
            if not fields and "=" in line:
                k, v = line[len("APPLY_OWNER ") :].split("=", 1)
                fields = {k.strip(): v.strip()}
            for k, v in fields.items():
                if k in OWNER_FIELDS and v:
                    owner = await bot_settings.update_owner(**{k: v})
                    apply_owner_info(owner)
                    if k == "bot_display_name" and message_bot is not None:
                        from src.branding import sync_telegram_bot_name

                        await sync_telegram_bot_name(message_bot, v)
                    result.applied.append(f"owner.{k}")
            continue

        if line.startswith("APPLY_TARGET "):
            fields = parse_kv_tokens(line[len("APPLY_TARGET ") :])
            key = fields.get("key", "").strip()
            if key == "account":
                key = "support"
            if key not in TARGET_KEYS:
                result.errors.append(f"bad target key: {key}")
                continue
            updates: dict[str, Any] = {}
            if "chat_id" in fields:
                updates["chat_id"] = fields["chat_id"]
            if "enabled" in fields:
                updates["enabled"] = _parse_bool(fields["enabled"])
            if updates:
                await bot_settings.update_target(key, **updates)
                result.applied.append(f"target.{key}")
            continue

        if line.startswith("APPLY_SLOT "):
            fields = parse_kv_tokens(line[len("APPLY_SLOT ") :])
            target = fields.get("target", "").strip()
            if target == "account":
                target = "support"
            if target not in TARGET_KEYS:
                result.errors.append(f"bad slot target: {target}")
                continue
            try:
                slot_no = int(fields.get("slot") or "0")
            except ValueError:
                result.errors.append("bad slot number")
                continue
            if not (1 <= slot_no <= 3):
                result.errors.append("slot must be 1..3")
                continue
            idx = slot_no - 1
            updates = {}
            if "enabled" in fields:
                updates["enabled"] = _parse_bool(fields["enabled"])
            if "schedule" in fields:
                updates["schedule_times"] = fields["schedule"]
            if "chat_id" in fields:
                updates["chat_id"] = fields["chat_id"]
            if "kind" in fields and fields["kind"] in SLOT_KINDS:
                updates["kind"] = "static" if target == "support" else fields["kind"]
            if "template" in fields:
                updates["message_template"] = fields["template"]
            if "rules" in fields:
                updates["rules_prompt"] = fields["rules"]
            if updates:
                await bot_settings.update_slot(target, idx, **updates)
                result.applied.append(f"slot.{target}.{slot_no}")
            continue

        if line.startswith("APPLY_PANEL "):
            fields = parse_kv_tokens(line[len("APPLY_PANEL ") :])
            try:
                if "base_url" in fields and fields["base_url"]:
                    await bot_settings.update_panel(base_url=fields["base_url"])
                    result.applied.append("panel.base_url")
                if "inbound_ids" in fields and fields["inbound_ids"]:
                    await bot_settings.update_panel(inbound_ids=fields["inbound_ids"])
                    result.applied.append("panel.inbound_ids")
                elif "inbound_id" in fields and fields["inbound_id"]:
                    await bot_settings.update_panel(inbound_ids=fields["inbound_id"])
                    result.applied.append("panel.inbound_ids")
                if "api_token" in fields:
                    result.errors.append("panel.api_token skipped (use Panel menu)")
                if "required_port" in fields and fields["required_port"]:
                    result.errors.append("panel.required_port removed (use inbound_ids)")
            except ValueError as exc:
                result.errors.append(str(exc))
            continue

        if line.startswith("APPLY_HEALTH "):
            fields = parse_kv_tokens(line[len("APPLY_HEALTH ") :])
            # single-field legacy
            if len(fields) == 0 and "=" in line:
                k, v = line[len("APPLY_HEALTH ") :].split("=", 1)
                fields = {k.strip(): v.strip()}
            payload: dict[str, Any] = {}
            if "enabled" in fields:
                payload["enabled"] = _parse_bool(fields["enabled"])
            if "times" in fields and fields["times"]:
                payload["times"] = fields["times"]
            if "chat_id" in fields:
                payload["chat_id"] = fields["chat_id"]
            if payload:
                await bot_settings.update_health_settings(**payload)
                result.applied.extend(f"health.{k}" for k in payload)
            continue

        if line.startswith("APPLY_UI "):
            fields = parse_kv_tokens(line[len("APPLY_UI ") :])
            if not fields and "=" in line:
                k, v = line[len("APPLY_UI ") :].split("=", 1)
                fields = {k.strip(): v.strip()}
            if "settings_columns" in fields:
                try:
                    cols = int(fields["settings_columns"])
                except ValueError:
                    cols = 2
                ui = await bot_settings.update_ui_settings(settings_columns=cols)
                ak.set_settings_columns(int(ui["settings_columns"]))
                result.applied.append(f"ui.settings_columns={ui['settings_columns']}")
                result.show_settings_keyboard = True
            continue

        if line.startswith("APPLY_ADMIN "):
            fields = parse_kv_tokens(line[len("APPLY_ADMIN ") :])
            action = fields.get("action", "").strip().lower()
            try:
                user_id = int(fields.get("user_id") or "0")
            except ValueError:
                user_id = 0
            role = (fields.get("role") or "full").strip().lower()
            if user_id <= 0:
                result.errors.append("admin user_id required")
                continue
            if action == "add" or action == "set_role":
                if role not in {"full", "stats"}:
                    role = "full"
                await bot_settings.set_admin_role(user_id, role)
                result.applied.append(f"admin.{action}:{user_id}:{role}")
            elif action == "remove":
                await bot_settings.remove_admin(user_id)
                result.applied.append(f"admin.remove:{user_id}")
            else:
                result.errors.append(f"bad admin action: {action}")
            continue

        if line.startswith("APPLY_BUTTON_ADD "):
            fields = parse_kv_tokens(line[len("APPLY_BUTTON_ADD ") :])
            action_name = fields.get("action", "").strip()
            label_fa = fields.get("label_fa", "").strip()
            if action_name not in catalog_actions or not label_fa:
                result.errors.append("button add needs valid action + label_fa")
                continue
            params: dict[str, Any] = {}
            for pk in ("target", "slot", "text"):
                if pk in fields:
                    params[pk] = fields[pk]
            try:
                created = await bot_settings.add_custom_button(
                    {
                        "id": new_button_id(),
                        "menu": fields.get("menu") or "settings",
                        "label_fa": label_fa,
                        "label_en": fields.get("label_en") or label_fa,
                        "enabled": True,
                        "action": action_name,
                        "params": params,
                        "order": 50,
                    }
                )
                result.applied.append(f"button.add:{created.get('id')}")
                result.show_settings_keyboard = True
            except ValueError as exc:
                result.errors.append(str(exc))
            continue

        if line.startswith("APPLY_BUTTON_REMOVE "):
            fields = parse_kv_tokens(line[len("APPLY_BUTTON_REMOVE ") :])
            removed = await bot_settings.remove_custom_button(
                button_id=fields.get("id", ""),
                label=fields.get("label", ""),
            )
            if removed:
                result.applied.append(f"button.remove:{removed.get('id')}")
                result.show_settings_keyboard = True
            else:
                # Fall back: system hardcoded button via safe-change layout
                from src.ui.system_layout import match_system_button, queue_system_button_change

                hit = match_system_button(
                    label=fields.get("label", ""),
                    button_id=fields.get("id", ""),
                    menu=(fields.get("menu") or "").strip() or None,
                    labels_table=ak._LABELS,
                )
                if hit:
                    action_id, menu = hit
                    queued = queue_system_button_change(
                        op="remove",
                        action=action_id,
                        menu=menu,
                        description=f"Remove system button {action_id} from {menu}",
                    )
                    if queued.get("ok"):
                        result.applied.append(f"system_button.remove:{action_id}@{menu}")
                        result.safe_change_queued = queued
                    else:
                        result.errors.append(str(queued.get("error") or "system button remove failed"))
                else:
                    result.errors.append("button not found")
            continue

        if line.startswith("APPLY_SYSTEM_BUTTON "):
            from src.ui.system_layout import match_system_button, queue_system_button_change

            fields = parse_kv_tokens(line[len("APPLY_SYSTEM_BUTTON ") :])
            op = (fields.get("op") or "remove").strip().lower()
            menu = (fields.get("menu") or "").strip()
            action_id = (fields.get("id") or "").strip()
            if not action_id and fields.get("label"):
                hit = match_system_button(
                    label=fields.get("label", ""),
                    menu=menu or None,
                    labels_table=ak._LABELS,
                )
                if hit:
                    action_id, menu = hit
            if not action_id or not menu:
                result.errors.append("APPLY_SYSTEM_BUTTON needs id+menu (or label+menu)")
                continue
            queued = queue_system_button_change(
                op=op,
                action=action_id,
                menu=menu,
                label_fa=fields.get("label_fa", ""),
                label_en=fields.get("label_en", ""),
            )
            if queued.get("ok"):
                result.applied.append(f"system_button.{op}:{action_id}@{menu}")
                result.safe_change_queued = queued
            else:
                result.errors.append(str(queued.get("error") or "system button change failed"))
            continue

    return result


def strip_apply_lines(answer: str) -> str:
    return "\n".join(
        ln
        for ln in (answer or "").splitlines()
        if not (
            ln.strip().startswith("APPLY_")
            or ln.strip().startswith("OPEN_SECTION ")
            or ln.strip() in {"SHOW_SETTINGS_KEYBOARD", "SHOW_STATUS"}
        )
    ).strip()
