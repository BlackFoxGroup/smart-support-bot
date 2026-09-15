"""Install the bot and Manager together on a Linux server without logging secrets."""

from __future__ import annotations

import re
import secrets
from pathlib import Path
from typing import Any

from src.operation_control import raise_if_stopped

REMOTE_ROOT = "/opt/smart-support"
BOT_SERVICE = "smart-support-bot"
MANAGER_SERVICE = "smart-support-manager"
_SKIP = {
    ".git",
    ".venv",
    "venv",
    "data",
    "downloads",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
}


def _connect(
    *,
    host: str,
    port: str,
    username: str,
    password: str,
    ssh_key: str = "",
):
    try:
        import paramiko
    except ImportError as exc:
        raise RuntimeError("paramiko missing") from exc

    if not host.strip() or not username.strip():
        raise ValueError("missing host/user")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    kwargs: dict[str, Any] = {
        "hostname": host.strip(),
        "port": int(port or 22),
        "username": username.strip(),
        "timeout": 30,
        "allow_agent": False,
        "look_for_keys": False,
    }
    key = (ssh_key or "").strip()
    if password:
        kwargs["password"] = password
    elif key and "BEGIN" in key:
        from io import StringIO

        pkey = None
        for loader in (paramiko.RSAKey, paramiko.Ed25519Key, paramiko.ECDSAKey):
            try:
                pkey = loader.from_private_key(StringIO(key))
                break
            except Exception:
                continue
        if pkey is None:
            raise ValueError("bad ssh key")
        kwargs["pkey"] = pkey
    else:
        kwargs["look_for_keys"] = True
    client.connect(**kwargs)
    return client


def _mkdirs(sftp, remote_dir: str) -> None:
    parts = [part for part in remote_dir.replace("\\", "/").strip("/").split("/") if part]
    current = ""
    for part in parts:
        current += "/" + part
        try:
            sftp.stat(current)
        except FileNotFoundError:
            sftp.mkdir(current)


def _upload_suite(client, local_path: str) -> int:
    source = Path(local_path)
    if not source.is_dir():
        raise ValueError("local folder missing")
    if not (source / "src").is_dir() or not (source / "requirements.txt").is_file():
        raise ValueError("Smart Support package root required")
    sftp = client.open_sftp()
    try:
        _mkdirs(sftp, REMOTE_ROOT)
        uploaded = 0
        for path in source.rglob("*"):
            raise_if_stopped()
            if not path.is_file() or any(part in _SKIP for part in path.parts):
                continue
            if path.name == ".env" or path.suffix.lower() in {".session", ".pyc", ".pyo"}:
                continue
            relative = path.relative_to(source).as_posix()
            destination = f"{REMOTE_ROOT}/{relative}"
            _mkdirs(sftp, destination.rsplit("/", 1)[0])
            sftp.put(str(path), destination, callback=lambda _done, _total: raise_if_stopped())
            uploaded += 1
        return uploaded
    finally:
        sftp.close()


def _write_env(
    client,
    *,
    token: str,
    extra_env: str,
    bot_mode: str = "polling",
    webhook_url: str = "",
    webhook_port: str = "8080",
) -> None:
    updates: dict[str, str] = {"BOT_UPDATE_MODE": bot_mode}
    if token.strip():
        updates["TELEGRAM_BOT_TOKEN"] = token.strip()
    if bot_mode == "webhook":
        updates.update(
            {
                "BOT_WEBHOOK_URL": webhook_url.rstrip("/") + "/telegram/webhook",
                "BOT_WEBHOOK_PATH": "/telegram/webhook",
                "BOT_WEBHOOK_PORT": webhook_port,
                "BOT_WEBHOOK_SECRET": secrets.token_urlsafe(24),
            }
        )
    for line in (extra_env or "").splitlines():
        row = line.strip()
        if not row or row.startswith("#") or "=" not in row:
            continue
        key, value = row.split("=", 1)
        clean_key = key.strip()
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", clean_key):
            updates[clean_key] = value
    if not updates:
        return

    sftp = client.open_sftp()
    try:
        try:
            with sftp.open(f"{REMOTE_ROOT}/.env", "r") as handle:
                existing = handle.read()
            if isinstance(existing, bytes):
                existing = existing.decode("utf-8", "replace")
        except FileNotFoundError:
            existing = ""
        lines = []
        seen: set[str] = set()
        for line in str(existing or "").splitlines():
            key = line.split("=", 1)[0] if "=" in line else ""
            if key in updates:
                lines.append(f"{key}={updates[key]}")
                seen.add(key)
            else:
                lines.append(line)
        for key, value in updates.items():
            if key not in seen:
                lines.append(f"{key}={value}")
        with sftp.open(f"{REMOTE_ROOT}/.env", "w") as handle:
            handle.write("\n".join(lines).rstrip() + "\n")
    finally:
        sftp.close()


def _execute(client, command: str, *, timeout: int = 300) -> tuple[bool, str]:
    raise_if_stopped()
    _stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    output = stdout.read().decode("utf-8", "replace").strip()
    error = stderr.read().decode("utf-8", "replace").strip()
    return code == 0, output or error


def _result_error(exc: Exception) -> dict[str, Any]:
    return {"ok": False, "error": str(exc) if isinstance(exc, ValueError) else type(exc).__name__}


def _safe_pip_packages(value: str) -> str:
    packages = (value or "").split()
    for package in packages:
        if not re.fullmatch(r"[A-Za-z0-9_.\-\[\],<>=!~]+", package):
            raise ValueError("invalid pip package")
    return " ".join(packages)


def install_telegram_bot(
    *,
    local_path: str,
    host: str,
    port: str,
    username: str,
    password: str,
    bot_token: str,
    extra_env: str = "",
    extra_pip: str = "",
    ssh_key: str = "",
    bot_mode: str = "polling",
    webhook_url: str = "",
    webhook_port: str = "8080",
    **_legacy: str,
) -> dict[str, Any]:
    """Upload the shared suite and prepare the bot service without starting it."""
    if not (bot_token or "").strip():
        return {"ok": False, "error": "missing bot token"}
    mode = (bot_mode or "polling").strip().lower()
    if mode not in {"polling", "webhook"}:
        return {"ok": False, "error": "invalid bot mode"}
    if mode == "webhook" and not (webhook_url or "").strip().lower().startswith("https://"):
        return {"ok": False, "error": "webhook requires HTTPS URL"}
    try:
        hook_port = str(int(webhook_port or "8080"))
        if not 1 <= int(hook_port) <= 65535:
            raise ValueError
    except ValueError:
        return {"ok": False, "error": "invalid webhook port"}
    client = None
    try:
        client = _connect(
            host=host,
            port=port,
            username=username,
            password=password,
            ssh_key=ssh_key,
        )
        uploaded = _upload_suite(client, local_path)
        _write_env(
            client,
            token=bot_token,
            extra_env=extra_env,
            bot_mode=mode,
            webhook_url=webhook_url.strip(),
            webhook_port=hook_port,
        )
        extra = _safe_pip_packages(extra_pip)
        pip_extra = f"{REMOTE_ROOT}/.venv/bin/pip install {extra}; " if extra else ""
        unit = (
            "[Unit]\nDescription=Smart Support Bot\nAfter=network-online.target\n"
            "Wants=network-online.target\n\n[Service]\nType=simple\n"
            f"WorkingDirectory={REMOTE_ROOT}\nEnvironmentFile={REMOTE_ROOT}/.env\n"
            f"ExecStart={REMOTE_ROOT}/.venv/bin/python -m src.main\n"
            "Restart=on-failure\nRestartSec=5\n\n[Install]\nWantedBy=multi-user.target\n"
        )
        command = (
            "apt-get update -qq && apt-get install -y python3 python3-venv python3-pip >/dev/null; "
            f"cd {REMOTE_ROOT} && python3 -m venv .venv; "
            f".venv/bin/pip install -U pip >/dev/null; "
            f".venv/bin/pip install -r requirements.txt; {pip_extra}"
            f"cat > /etc/systemd/system/{BOT_SERVICE}.service << 'EOF'\n{unit}EOF\n"
            "systemctl daemon-reload"
        )
        ok, output = _execute(client, command)
        return (
            {"ok": True, "uploaded": uploaded, "prepared": BOT_SERVICE}
            if ok
            else {"ok": False, "error": "remote bot install failed", "detail": output}
        )
    except Exception as exc:  # noqa: BLE001
        return _result_error(exc)
    finally:
        if client is not None:
            client.close()


def install_expert(
    *,
    local_path: str,
    host: str,
    port: str,
    username: str,
    password: str,
    ssh_key: str = "",
    **_unused: str,
) -> dict[str, Any]:
    """Upload the shared suite and prepare Manager without starting it."""
    source = Path(local_path)
    if not (source / "src" / "manager" / "app.py").is_file():
        return {"ok": False, "error": "Expert files missing"}
    client = None
    try:
        client = _connect(
            host=host,
            port=port,
            username=username,
            password=password,
            ssh_key=ssh_key,
        )
        uploaded = _upload_suite(client, local_path)
        unit = (
            "[Unit]\nDescription=Smart Support Manager\nAfter=network-online.target\n"
            "Wants=network-online.target\n\n[Service]\nType=simple\n"
            f"WorkingDirectory={REMOTE_ROOT}\nEnvironmentFile=-{REMOTE_ROOT}/.env\n"
            f'Environment="BOT_ROOT={REMOTE_ROOT}"\n'
            f'Environment="BOT_REMOTE_ROOT={REMOTE_ROOT}"\n'
            'Environment="BOT_SERVICE_NAME=smart-support-bot.service"\n'
            'Environment="MANAGER_LOCAL_BOT=1"\n'
            'Environment="MANAGER_NAME=Smart Support Manager"\n'
            'Environment="MANAGER_VERSION=2.3"\n'
            'Environment="BOT_VERSION=2.3"\n'
            'Environment="MANAGER_PORT=8766"\n'
            f'Environment="MANAGER_CONFIG_DIR={REMOTE_ROOT}/data"\n'
            f"ExecStart={REMOTE_ROOT}/.venv/bin/python -m src.manager\n"
            "Restart=on-failure\nRestartSec=5\nUMask=0077\n\n"
            "[Install]\nWantedBy=multi-user.target\n"
        )
        command = (
            "apt-get update -qq && apt-get install -y python3 python3-venv python3-pip >/dev/null; "
            f"cd {REMOTE_ROOT} && python3 -m venv .venv; "
            ".venv/bin/pip install -U pip >/dev/null; "
            ".venv/bin/pip install -r requirements.txt; "
            f"install -d -m 700 {REMOTE_ROOT}/data {REMOTE_ROOT}/products; "
            f"cat > /etc/systemd/system/{MANAGER_SERVICE}.service << 'EOF'\n{unit}EOF\n"
            "systemctl daemon-reload"
        )
        ok, output = _execute(client, command)
        return (
            {"ok": True, "uploaded": uploaded, "prepared": MANAGER_SERVICE}
            if ok
            else {"ok": False, "error": "remote Expert install failed", "detail": output}
        )
    except Exception as exc:  # noqa: BLE001
        return _result_error(exc)
    finally:
        if client is not None:
            client.close()


def activate_bot_and_expert(
    *,
    host: str,
    port: str,
    username: str,
    password: str,
    ssh_key: str = "",
    **_unused: str,
) -> dict[str, Any]:
    """Enable both prepared services and verify that both are active."""
    client = None
    try:
        client = _connect(
            host=host,
            port=port,
            username=username,
            password=password,
            ssh_key=ssh_key,
        )
        command = (
            f"test -f /etc/systemd/system/{BOT_SERVICE}.service; "
            f"test -f /etc/systemd/system/{MANAGER_SERVICE}.service; "
            f"test -s {REMOTE_ROOT}/.env; "
            "systemctl daemon-reload; "
            f"systemctl enable --now {BOT_SERVICE}.service {MANAGER_SERVICE}.service; "
            "sleep 3; "
            f"test \"$(systemctl is-active {BOT_SERVICE}.service)\" = active; "
            f"test \"$(systemctl is-active {MANAGER_SERVICE}.service)\" = active; "
            f"printf 'bot=%s\\nexpert=%s\\n' \"$(systemctl is-active {BOT_SERVICE}.service)\" "
            f"\"$(systemctl is-active {MANAGER_SERVICE}.service)\""
        )
        ok, output = _execute(client, command, timeout=90)
        return (
            {"ok": True, "bot": "active", "expert": "active"}
            if ok
            else {"ok": False, "error": "service activation failed", "detail": output}
        )
    except Exception as exc:  # noqa: BLE001
        return _result_error(exc)
    finally:
        if client is not None:
            client.close()
