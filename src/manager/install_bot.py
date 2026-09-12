"""Install any local Telegram bot folder onto a Linux server. Token is not logged."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

_SKIP = {".git", ".venv", "venv", "data", "__pycache__", ".pytest_cache", "node_modules"}


def install_telegram_bot(
    *,
    local_path: str,
    host: str,
    port: str,
    username: str,
    password: str,
    remote_dir: str,
    service_name: str,
    bot_token: str,
    start_cmd: str,
    extra_env: str = "",
    extra_pip: str = "",
    bot_label: str = "",
    ssh_key: str = "",
) -> dict[str, Any]:
    src = Path(local_path)
    if not src.is_dir():
        return {"ok": False, "error": "local folder missing"}
    host = host.strip()
    user = username.strip()
    requested_remote = remote_dir.strip().rstrip("/")
    remote = (
        "/opt/smart-support"
        if requested_remote in {"", "/opt/telegram-bot", "/opt/Smart Support Bot"}
        else requested_remote
    )
    svc = re.sub(r"[^a-zA-Z0-9_.-]", "-", (service_name or "telegram-bot").strip()) or "telegram-bot"
    token = (bot_token or "").strip()
    start = (start_cmd or "python3 -m src.main").strip()
    if not host or not user or not token:
        return {"ok": False, "error": "missing host/user/token"}
    try:
        import paramiko
    except ImportError:
        return {"ok": False, "error": "paramiko missing"}
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        kwargs: dict[str, Any] = {
            "hostname": host,
            "port": int(port or 22),
            "username": user,
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
                return {"ok": False, "error": "bad ssh key"}
            kwargs["pkey"] = pkey
        else:
            kwargs["look_for_keys"] = True
        client.connect(**kwargs)
        sftp = client.open_sftp()
        _mkdirs(sftp, remote)
        uploaded = 0
        for path in src.rglob("*"):
            if not path.is_file():
                continue
            if any(part in _SKIP for part in path.parts):
                continue
            if path.name == ".env":
                continue
            rel = path.relative_to(src).as_posix()
            dest = f"{remote}/{rel}"
            _mkdirs(sftp, dest.rsplit("/", 1)[0])
            sftp.put(str(path), dest)
            uploaded += 1
        updates = {"TELEGRAM_BOT_TOKEN": token}
        for line in (extra_env or "").splitlines():
            row = line.strip()
            if row and "=" in row and not row.startswith("#") and not row.upper().startswith("TELEGRAM_BOT_TOKEN="):
                key_name, value = row.split("=", 1)
                updates[key_name.strip()] = value
        try:
            with sftp.open(f"{remote}/.env", "r") as fh:
                existing = fh.read()
            if isinstance(existing, bytes):
                existing = existing.decode("utf-8", "replace")
        except FileNotFoundError:
            existing = ""
        env_lines = []
        seen: set[str] = set()
        for line in str(existing or "").splitlines():
            key_name = line.split("=", 1)[0] if "=" in line else ""
            if key_name in updates:
                env_lines.append(f"{key_name}={updates[key_name]}")
                seen.add(key_name)
            else:
                env_lines.append(line)
        for key_name, value in updates.items():
            if key_name not in seen:
                env_lines.append(f"{key_name}={value}")
        env_body = "\n".join(env_lines).rstrip() + "\n"
        with sftp.open(f"{remote}/.env", "w") as fh:
            fh.write(env_body)
        sftp.close()
        if start.startswith("python3 "):
            exec_start = f"{remote}/.venv/bin/python {start[8:]}"
        elif start.startswith("python "):
            exec_start = f"{remote}/.venv/bin/python {start[7:]}"
        else:
            exec_start = f"/bin/bash -lc 'cd {remote} && {start}'"
        label = (bot_label or svc).strip() or svc
        extra = " ".join((extra_pip or "").split())
        pip_extra = f".venv/bin/pip install {extra}; " if extra else ""
        unit = (
            f"[Unit]\nDescription={label}\nAfter=network-online.target\n\n"
            f"[Service]\nType=simple\nWorkingDirectory={remote}\nEnvironmentFile={remote}/.env\n"
            f"ExecStart={exec_start}\n"
            f"Restart=on-failure\nRestartSec=5\n\n[Install]\nWantedBy=multi-user.target\n"
        )
        cmd = (
            f"apt-get update -qq && apt-get install -y python3 python3-venv python3-pip >/dev/null; "
            f"cd {remote!s} && python3 -m venv .venv; "
            f".venv/bin/pip install -U pip >/dev/null; "
            f"if [ -f requirements.txt ]; then .venv/bin/pip install -r requirements.txt; fi; "
            f"{pip_extra}"
            f"cat > /etc/systemd/system/{svc}.service << 'EOF'\n{unit}EOF\n"
            f"systemctl daemon-reload && systemctl enable --now {svc}.service && systemctl is-active {svc}.service"
        )
        _stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
        code = stdout.channel.recv_exit_status()
        active = stdout.read().decode("utf-8", "replace").strip().splitlines()
        client.close()
        if code != 0:
            return {"ok": False, "error": "remote install failed", "uploaded": uploaded}
        return {"ok": True, "uploaded": uploaded, "active": active[-1] if active else ""}
    except Exception as exc:  # noqa: BLE001
        try:
            client.close()
        except Exception:
            pass
        return {"ok": False, "error": type(exc).__name__}


def _mkdirs(sftp, remote_dir: str) -> None:
    parts = [p for p in remote_dir.replace("\\", "/").strip("/").split("/") if p]
    cur = ""
    for part in parts:
        cur += "/" + part
        try:
            sftp.stat(cur)
        except FileNotFoundError:
            sftp.mkdir(cur)
