"""Independent watchdog: apply queued changes, ask confirm, auto-restore.

Runs as a separate systemd unit so a broken bot process cannot prevent rollback.
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import time
from pathlib import Path

# Allow `python -m src.safety.watchdog_main` from install root
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv

from src.safety.backup import create_backup, restore_backup, restore_last_good, save_last_good
from src.safety.paths import (
    CONFIRM_SECONDS_DEFAULT,
    CRASH_STATE_PATH,
    DATA_DIR,
    DEFAULT_SUPPORT_CHAT_ID,
    INSTALL_ROOT,
    LAST_GOOD_PATH,
    OBSERVE_SECONDS_DEFAULT,
    SERVICE_NAME,
)
from src.safety.state import (
    PendingChange,
    clear_decision,
    clear_pending,
    clear_request,
    ensure_safety_dirs,
    heartbeat_age_seconds,
    load_pending,
    read_decision,
    read_request,
    save_pending,
)
from src.safety.telegram_notify import (
    confirm_keyboard,
    edit_message_text,
    get_me,
    send_message,
)

log = logging.getLogger("blackfox-bot-watchdog")

POLL_SECONDS = 3
HEARTBEAT_STALE_SECONDS = 45
POST_RESTART_GRACE = 25
HEALTH_TRIES = 8
HEALTH_INTERVAL = 5
# Crash-loop auto-recovery (independent of safe-change pending flow)
CRASH_FAIL_STREAK = 8  # ~24s of consecutive unhealthy polls
HEALTHY_FOR_LAST_GOOD = 120  # seconds stable before refreshing last_good
CRASH_COOLDOWN = 180  # seconds between automatic last_good restores


def _token() -> str:
    return (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()


def _systemctl(*args: str) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["systemctl", *args],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except Exception as exc:  # noqa: BLE001
        return 1, str(exc)
    out = ((proc.stdout or "") + (proc.stderr or "")).strip()
    return int(proc.returncode), out


def service_active() -> bool:
    code, out = _systemctl("is-active", SERVICE_NAME)
    return code == 0 and out.strip() == "active"


def restart_bot() -> tuple[bool, str]:
    code, out = _systemctl("restart", SERVICE_NAME)
    return code == 0, out


def bot_healthy(token: str) -> tuple[bool, str]:
    if not service_active():
        return False, "systemd not active"
    age = heartbeat_age_seconds()
    if age is None:
        # Heartbeat may not exist yet right after first boot of this feature.
        pass
    elif age > HEARTBEAT_STALE_SECONDS:
        return False, f"heartbeat stale ({age:.0f}s)"
    me = get_me(token)
    if not me.get("ok"):
        return False, f"telegram getMe failed: {me.get('description')}"
    return True, "ok"


def wait_healthy(token: str) -> tuple[bool, str]:
    time.sleep(POST_RESTART_GRACE)
    last = "not checked"
    for _ in range(HEALTH_TRIES):
        ok, last = bot_healthy(token)
        if ok:
            return True, last
        time.sleep(HEALTH_INTERVAL)
    return False, last


def _apply_files(files: dict[str, str]) -> None:
    for rel, content in files.items():
        rel_norm = rel.replace("\\", "/").lstrip("/")
        if ".." in rel_norm.split("/"):
            raise ValueError(f"Invalid path: {rel}")
        # Refuse writing outside allowed trees
        if not (
            rel_norm.startswith("src/")
            or rel_norm.startswith("knowledge/")
            or rel_norm.startswith("deploy/")
            or rel_norm in {"requirements.txt", "README.md", ".env"}
        ):
            raise ValueError(f"Path not allowed for safe apply: {rel_norm}")
        dest = INSTALL_ROOT / rel_norm
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")


def _apply_marker(change_id: str) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / f"safety_drill_{change_id}.flag"
    path.write_text(f"drill ok at {time.time()}\n", encoding="utf-8")
    return path


def _notify(token: str, chat_id: str, text: str, *, markup: dict | None = None) -> dict:
    return send_message(token, chat_id, text, reply_markup=markup, disable_notification=True)


def _do_restore(pending: PendingChange, token: str, reason: str) -> None:
    log.warning("Restoring change %s (%s)", pending.change_id, reason)
    pending.status = "restoring"
    pending.last_error = reason
    save_pending(pending)
    try:
        if pending.backup_path and not pending.marker_only:
            restore_backup(Path(pending.backup_path))
        if pending.marker_only:
            flag = DATA_DIR / f"safety_drill_{pending.change_id}.flag"
            flag.unlink(missing_ok=True)
        ok, out = restart_bot()
        healthy, detail = wait_healthy(token) if ok else (False, out)
        msg = (
            f"⏪ Rollback انجام شد.\n"
            f"change: `{pending.change_id}`\n"
            f"دلیل: {reason}\n"
            f"سرویس: {'OK' if healthy else 'مشکل'}\n"
            f"{detail}"
        )
        _notify(token, pending.admin_chat_id, msg)
    except Exception as exc:  # noqa: BLE001
        log.exception("Restore failed")
        _notify(
            token,
            pending.admin_chat_id,
            f"❌ Rollback شکست خورد برای {pending.change_id}: {exc}",
        )
    finally:
        clear_decision()
        clear_request()
        clear_pending()


def _finalize_confirm(pending: PendingChange, token: str) -> None:
    log.info("Change %s confirmed — keeping", pending.change_id)
    if pending.confirm_message_id:
        edit_message_text(
            token,
            pending.admin_chat_id,
            pending.confirm_message_id,
            f"✅ تغییرات تأیید شد و نگه داشته شد.\nchange: {pending.change_id}",
        )
    else:
        _notify(
            token,
            pending.admin_chat_id,
            f"✅ تغییرات تأیید شد و نگه داشته شد.\nchange: {pending.change_id}",
        )
    clear_decision()
    clear_request()
    clear_pending()


def _handle_queued_request(token: str) -> None:
    req = read_request()
    if not req or req.get("status") != "queued":
        return
    pending_now = load_pending()
    if pending_now:
        return

    change_id = str(req.get("change_id") or "")
    admin_chat_id = str(req.get("admin_chat_id") or "")
    description = str(req.get("description") or "safe change")
    files = req.get("files") if isinstance(req.get("files"), dict) else {}
    marker_only = bool(req.get("marker_only"))
    confirm_seconds = int(req.get("confirm_seconds") or CONFIRM_SECONDS_DEFAULT)
    observe_seconds = int(req.get("observe_seconds") or OBSERVE_SECONDS_DEFAULT)

    if not change_id or not admin_chat_id:
        clear_request()
        return

    log.info("Applying queued change %s", change_id)
    _notify(
        token,
        admin_chat_id,
        (
            f"🛡 شروع Safe Change\n"
            f"change: {change_id}\n"
            f"{description}\n"
            f"در حال بک‌آپ…\n"
            f"بعد از اعمال، {observe_seconds} ثانیه برای چک ربات صبر می‌کنم؛ "
            f"سپس پیام تأیید می‌فرستم (مهلت پاسخ {confirm_seconds} ثانیه)."
        ),
    )

    try:
        backup = create_backup(change_id=change_id)
    except Exception as exc:  # noqa: BLE001
        _notify(token, admin_chat_id, f"❌ بک‌آپ شکست خورد: {exc}")
        clear_request()
        return

    pending = PendingChange(
        change_id=change_id,
        description=description,
        admin_chat_id=admin_chat_id,
        backup_path=str(backup),
        status="applying",
        created_at=time.time(),
        files={str(k): str(v) for k, v in files.items()} if files else None,
        marker_only=marker_only,
        confirm_seconds=confirm_seconds,
        observe_seconds=observe_seconds,
    )
    save_pending(pending)
    # Mark request consumed
    req["status"] = "consumed"
    from src.safety.state import write_request

    write_request(req)

    try:
        if marker_only:
            _apply_marker(change_id)
        if files:
            _apply_files({str(k): str(v) for k, v in files.items()})
        ok, out = restart_bot()
        if not ok:
            raise RuntimeError(f"restart failed: {out}")
        healthy, detail = wait_healthy(token)
        if not healthy:
            raise RuntimeError(f"health check failed: {detail}")
    except Exception as exc:  # noqa: BLE001
        log.exception("Apply failed")
        _do_restore(pending, token, f"apply/health failed: {exc}")
        return

    # Observation window: support checks the bot for observe_seconds, then confirm is sent.
    pending.status = "observing"
    pending.observe_until = time.time() + observe_seconds
    save_pending(pending)
    _notify(
        token,
        admin_chat_id,
        (
            f"✅ تغییرات اعمال شد و ربات فعلاً سالم است.\n"
            f"change: `{change_id}`\n"
            f"لطفاً تا {observe_seconds} ثانیه ربات را چک کنید.\n"
            f"بعد از این زمان پیام تأیید ارسال می‌شود "
            f"(مهلت پاسخ: {confirm_seconds} ثانیه)."
        ),
    )
    log.info(
        "Observing change %s until %s then ask confirm",
        change_id,
        pending.observe_until,
    )


def _send_confirm_prompt(pending: PendingChange, token: str) -> None:
    confirm_seconds = int(pending.confirm_seconds or CONFIRM_SECONDS_DEFAULT)
    deadline = time.time() + confirm_seconds
    pending.status = "awaiting_confirm"
    pending.confirm_deadline = deadline
    text = (
        f"🛡 زمان تأیید Safe Change\n\n"
        f"change: `{pending.change_id}`\n"
        f"{pending.description}\n\n"
        f"ربات به مدت ۱ دقیقه پس از اعمال در دسترس بود.\n"
        f"آیا تغییرات مورد تأیید است؟\n"
        f"اگر تا {confirm_seconds} ثانیه پاسخ ندهید، خودکار به آخرین بک‌آپ برمی‌گردم."
    )
    resp = _notify(
        token,
        pending.admin_chat_id,
        text,
        markup=confirm_keyboard(pending.change_id),
    )
    if resp.get("ok"):
        try:
            pending.confirm_message_id = int(resp["result"]["message_id"])
        except Exception:  # noqa: BLE001
            pending.confirm_message_id = None
        save_pending(pending)
        log.info("Awaiting confirm for %s until %s", pending.change_id, deadline)
        return
    _do_restore(
        pending,
        token,
        f"confirm message failed: {resp.get('description')}",
    )


def _handle_pending(token: str) -> None:
    pending = load_pending()
    if not pending:
        return

    if pending.status == "observing":
        ok, detail = bot_healthy(token)
        if not ok:
            _do_restore(
                pending,
                token,
                f"became unhealthy during observe window: {detail}",
            )
            return
        if pending.observe_until and time.time() >= float(pending.observe_until):
            _send_confirm_prompt(pending, token)
        return

    if pending.status == "awaiting_confirm":
        decision = read_decision()
        if decision and str(decision.get("change_id")) == pending.change_id:
            dec = str(decision.get("decision") or "").lower()
            if dec == "confirm":
                _finalize_confirm(pending, token)
                return
            if dec == "reject":
                _do_restore(pending, token, "support rejected")
                return

        # Timeout
        if pending.confirm_deadline and time.time() >= float(pending.confirm_deadline):
            _do_restore(pending, token, "no confirmation within timeout")
            return

        # Health collapse while waiting
        ok, detail = bot_healthy(token)
        if not ok:
            _do_restore(
                pending,
                token,
                f"became unhealthy while awaiting confirm: {detail}",
            )
            return


def _support_chat() -> str:
    return (
        (os.getenv("SAFETY_CONFIRM_CHAT_ID") or "").strip()
        or (os.getenv("CONVO_ANALYSIS_CHAT_ID") or "").strip()
        or DEFAULT_SUPPORT_CHAT_ID
    )


def _read_crash_state() -> dict:
    if not CRASH_STATE_PATH.is_file():
        return {"fail_streak": 0, "healthy_since": None, "last_restore_at": 0}
    try:
        import json

        raw = json.loads(CRASH_STATE_PATH.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {"fail_streak": 0, "healthy_since": None, "last_restore_at": 0}
    except Exception:  # noqa: BLE001
        return {"fail_streak": 0, "healthy_since": None, "last_restore_at": 0}


def _write_crash_state(state: dict) -> None:
    import json

    ensure_safety_dirs()
    CRASH_STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _handle_crash_guard(token: str) -> None:
    """If the bot crash-loops with no pending safe-change, restore last_good automatically."""
    pending = load_pending()
    if pending and pending.status in {
        "ready_to_apply",
        "applying",
        "observing",
        "awaiting_confirm",
        "restoring",
    }:
        return

    state = _read_crash_state()
    ok, detail = bot_healthy(token)
    now = time.time()
    if ok:
        fail_streak = 0
        healthy_since = state.get("healthy_since")
        if not healthy_since:
            healthy_since = now
        state["fail_streak"] = 0
        state["healthy_since"] = healthy_since
        _write_crash_state(state)
        # After the bot stays healthy long enough, refresh last_good snapshot.
        if float(healthy_since) and (now - float(healthy_since)) >= HEALTHY_FOR_LAST_GOOD:
            try:
                # Refresh at most every healthy window (avoid rewriting every poll).
                meta_age = now - LAST_GOOD_PATH.stat().st_mtime if LAST_GOOD_PATH.is_file() else 10**9
            except OSError:
                meta_age = 10**9
            if meta_age >= HEALTHY_FOR_LAST_GOOD:
                try:
                    save_last_good(reason="stable-healthy")
                except Exception:  # noqa: BLE001
                    log.exception("save_last_good failed")
        return

    fail_streak = int(state.get("fail_streak") or 0) + 1
    state["fail_streak"] = fail_streak
    state["healthy_since"] = None
    state["last_detail"] = detail
    _write_crash_state(state)
    log.warning("Crash-guard unhealthy streak=%s detail=%s", fail_streak, detail)

    if fail_streak < CRASH_FAIL_STREAK:
        return
    last_restore = float(state.get("last_restore_at") or 0)
    if now - last_restore < CRASH_COOLDOWN:
        return
    if not LAST_GOOD_PATH.is_file():
        log.error("Crash-loop detected but last_good.tar.gz is missing")
        _notify(
            token,
            _support_chat(),
            f"🚨 ربات در کرش‌لوپ است ولی last_good موجود نیست.\n{detail}",
        )
        state["fail_streak"] = 0
        state["last_restore_at"] = now
        _write_crash_state(state)
        return

    log.warning("Crash-loop detected — restoring last_good")
    try:
        restore_last_good()
        ok_restart, out = restart_bot()
        healthy, hdetail = wait_healthy(token) if ok_restart else (False, out)
        msg = (
            "⏪ Crash-guard: last_good بازگردانی شد.\n"
            f"دلیل: {detail}\n"
            f"سرویس: {'OK' if healthy else 'مشکل'}\n"
            f"{hdetail}"
        )
        _notify(token, _support_chat(), msg)
    except Exception as exc:  # noqa: BLE001
        log.exception("last_good restore failed")
        _notify(token, _support_chat(), f"❌ Crash-guard restore شکست خورد: {exc}")
    state["fail_streak"] = 0
    state["last_restore_at"] = now
    state["healthy_since"] = None
    _write_crash_state(state)


def run_forever() -> None:
    load_dotenv(INSTALL_ROOT / ".env")
    ensure_safety_dirs()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    token = _token()
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN missing")
    log.info("Watchdog started (install=%s)", INSTALL_ROOT)
    # Bootstrap last_good once if missing and current tree imports cleanly later via healthy path.
    while True:
        try:
            _handle_queued_request(token)
            _handle_pending(token)
            _handle_crash_guard(token)
        except Exception:  # noqa: BLE001
            log.exception("Watchdog loop error")
        time.sleep(POLL_SECONDS)


def main() -> None:
    run_forever()


if __name__ == "__main__":
    main()
