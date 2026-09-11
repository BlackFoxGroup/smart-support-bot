"""SFTP connection for catalog media. Credentials are never stored in source."""

from __future__ import annotations

import json
import os
import socket
import threading
import time
from pathlib import Path
from typing import Any

from src.control.secrets import decrypt_secret, encrypt_secret
from src.knowledge.source_catalog.store import live_root

AUTH_FAILED = "AUTHENTICATION FAILED"
HOST_UNREACHABLE = "HOST UNREACHABLE"
TIMEOUT = "TIMEOUT"
PERMISSION_DENIED = "PERMISSION DENIED"
REMOTE_PATH_ERROR = "REMOTE PATH ERROR"
CONNECTED = "CONNECTED"


def _config_path(data_dir: Path) -> Path:
    return live_root(data_dir) / "sftp.json"


def _master_secret(data_dir: Path) -> str:
    env = (os.getenv("BOT_MASTER_SECRET") or os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
    if env:
        return env
    key_path = live_root(data_dir) / ".sftp_key"
    if key_path.is_file():
        return key_path.read_text(encoding="utf-8").strip()
    live_root(data_dir).mkdir(parents=True, exist_ok=True)
    raw = os.urandom(32).hex()
    key_path.write_text(raw, encoding="utf-8")
    try:
        os.chmod(key_path, 0o600)
    except OSError:
        pass
    return raw


def load_sftp_settings(data_dir: Path) -> dict[str, Any]:
    path = _config_path(data_dir)
    stored: dict[str, Any] = {}
    if path.is_file():
        try:
            stored = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            stored = {}
    if not isinstance(stored, dict):
        stored = {}
    host = str(stored.get("host") or os.getenv("BOT_SSH_HOST") or "").strip()
    user = str(stored.get("username") or os.getenv("BOT_SSH_USER") or "").strip()
    port = int(stored.get("port") or os.getenv("BOT_SSH_PORT") or 22)
    remote = str(
        stored.get("remote_media_path")
        or os.getenv("BOT_REMOTE_MEDIA")
        or ((os.getenv("BOT_REMOTE_ROOT") or "/opt/Smart Support Bot").rstrip("/") + "/media/catalogs")
    ).strip()
    auth = str(stored.get("auth_method") or ("password" if os.getenv("BOT_SSH_PASS") else "key")).strip() or "key"
    return {
        "host": host,
        "port": port,
        "username": user,
        "auth_method": auth,
        "key_path": str(stored.get("key_path") or os.getenv("BOT_SSH_KEY") or "").strip(),
        "has_password": bool(stored.get("password_enc") or os.getenv("BOT_SSH_PASS")),
        "remote_media_path": remote,
        "timeout": int(stored.get("timeout") or 20),
        "password_enc": str(stored.get("password_enc") or ""),
    }


def save_sftp_settings(
    data_dir: Path,
    fields: dict[str, Any],
    *,
    password: str | None = None,
    key_pem: str | None = None,
) -> None:
    current = load_sftp_settings(data_dir)
    password_enc = current.get("password_enc") or ""
    if password and password.strip():
        password_enc = encrypt_secret(password.strip(), _master_secret(data_dir))
    incoming = str(fields.get("key_path") or "").strip()
    key_path = incoming or str(current.get("key_path") or "")
    pem = (key_pem or "").strip()
    if pem and "BEGIN" in pem:
        dest = live_root(data_dir) / "sftp_user_key"
        dest.write_text(pem + "\n", encoding="utf-8")
        try:
            os.chmod(dest, 0o600)
        except OSError:
            pass
        key_path = str(dest)
    data = {
        "host": str(fields.get("host") or current["host"]).strip(),
        "port": int(fields.get("port") or current["port"] or 22),
        "username": str(fields.get("username") or current["username"]).strip(),
        "auth_method": str(fields.get("auth_method") or current["auth_method"]).strip(),
        "key_path": key_path,
        "remote_media_path": str(fields.get("remote_media_path") or current["remote_media_path"]).strip(),
        "timeout": int(fields.get("timeout") or current["timeout"] or 20),
        "password_enc": password_enc,
    }
    path = _config_path(data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _password(data_dir: Path, settings: dict[str, Any]) -> str:
    if settings.get("password_enc"):
        return decrypt_secret(str(settings["password_enc"]), _master_secret(data_dir))
    return (os.getenv("BOT_SSH_PASS") or "").strip()


_SESS_LOCK = threading.Lock()
_SESS: dict[str, Any] = {"client": None, "sftp": None, "host": ""}


def ssh_ready(data_dir: Path) -> bool:
    s = load_sftp_settings(data_dir)
    return bool(s["host"] and s["username"])


def session_status() -> dict[str, Any]:
    with _SESS_LOCK:
        client = _SESS.get("client")
        alive = False
        try:
            tr = client.get_transport() if client is not None else None
            alive = bool(tr and tr.is_active())
        except Exception:
            alive = False
        return {"connected": alive, "host": str(_SESS.get("host") or "")}


def connect_session(data_dir: Path) -> dict[str, Any]:
    s = load_sftp_settings(data_dir)
    if not s["host"] or not s["username"]:
        return {"ok": False, "status": "NOT CONFIGURED", "error": "host/username missing"}
    disconnect_session()
    try:
        client, settings = _client(data_dir)
        sftp = client.open_sftp()
        remote = settings["remote_media_path"]
        try:
            sftp.stat(remote)
        except FileNotFoundError:
            _mkdirs(sftp, remote.replace("\\", "/"))
        tr = client.get_transport()
        if tr is not None:
            tr.set_keepalive(30)
        with _SESS_LOCK:
            _SESS["client"] = client
            _SESS["sftp"] = sftp
            _SESS["host"] = settings["host"]
        return {"ok": True, "status": CONNECTED, "host": settings["host"]}
    except Exception as exc:  # noqa: BLE001
        disconnect_session()
        return {"ok": False, "status": _classify_error(exc), "error": str(exc)[:300]}


def disconnect_session() -> None:
    with _SESS_LOCK:
        sftp = _SESS.get("sftp")
        client = _SESS.get("client")
        _SESS["sftp"] = None
        _SESS["client"] = None
        _SESS["host"] = ""
    for obj in (sftp, client):
        if obj is None:
            continue
        try:
            obj.close()
        except Exception:
            pass


def _live_sftp(data_dir: Path):
    st = session_status()
    if not st.get("connected"):
        return None, load_sftp_settings(data_dir)
    with _SESS_LOCK:
        return _SESS.get("sftp"), load_sftp_settings(data_dir)


def _classify_error(exc: BaseException) -> str:
    name = type(exc).__name__
    text = str(exc).lower()
    if name in {"TimeoutError", "socket.timeout"} or "timed out" in text:
        return TIMEOUT
    if name in {"AuthenticationException", "PasswordRequiredException", "SSHException"} and (
        "auth" in text or "password" in text or name.startswith("Auth")
    ):
        return AUTH_FAILED
    if "auth" in text or "permission denied (publickey" in text:
        return AUTH_FAILED
    if "permission denied" in text:
        return PERMISSION_DENIED
    if name in {"gaierror", "ConnectionRefusedError", "NoValidConnectionsError"} or "unreachable" in text:
        return HOST_UNREACHABLE
    if "no such file" in text or "not a directory" in text:
        return REMOTE_PATH_ERROR
    return str(exc)[:300]


def _client(data_dir: Path):
    import paramiko

    s = load_sftp_settings(data_dir)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    kwargs: dict[str, Any] = {
        "hostname": s["host"],
        "port": int(s["port"]),
        "username": s["username"],
        "timeout": int(s["timeout"]),
        "allow_agent": False,
        "look_for_keys": False,
    }
    if s["auth_method"] == "password":
        kwargs["password"] = _password(data_dir, s)
    else:
        key_path = s.get("key_path") or ""
        if key_path:
            kwargs["key_filename"] = key_path
        else:
            kwargs["look_for_keys"] = True
            kwargs["allow_agent"] = True
        pwd = _password(data_dir, s)
        if pwd:
            kwargs["password"] = pwd
    client.connect(**kwargs)
    return client, s


def test_connection(data_dir: Path) -> dict[str, Any]:
    return connect_session(data_dir)


def _mkdirs(sftp, remote_dir: str) -> None:
    parts = [p for p in remote_dir.replace("\\", "/").strip("/").split("/") if p]
    cur = ""
    for part in parts:
        cur += "/" + part
        try:
            sftp.stat(cur)
        except FileNotFoundError:
            sftp.mkdir(cur)


def upload_and_verify(
    data_dir: Path,
    local_path: Path,
    remote_rel: str,
    expected_hash: str,
    expected_size: int,
    progress_cb=None,
) -> dict[str, Any]:
    s = load_sftp_settings(data_dir)
    if not s["host"] or not s["username"]:
        return {"ok": False, "status": "FAILED", "error": "SFTP not configured"}
    started = time.time()
    try:
        sftp, settings = _live_sftp(data_dir)
        if sftp is None:
            return {"ok": False, "status": "FAILED", "error": "not connected"}
        remote_root = str(settings["remote_media_path"]).rstrip("/").replace("\\", "/")
        remote = f"{remote_root}/{remote_rel.lstrip('/')}"
        parent = remote.rsplit("/", 1)[0]
        _mkdirs(sftp, parent)

        def _cb(transferred: int, total: int) -> None:
            if progress_cb:
                elapsed = max(0.001, time.time() - started)
                progress_cb(transferred, total, transferred / elapsed)

        sftp.put(str(local_path), remote, callback=_cb)
        st = sftp.stat(remote)
        if int(st.st_size or 0) != int(expected_size):
            return {
                "ok": False,
                "status": "FAILED",
                "error": f"remote size {st.st_size} != {expected_size}",
                "remote": remote,
            }
        with sftp.open(remote, "rb") as fh:
            import hashlib

            h = hashlib.sha256()
            while True:
                chunk = fh.read(1024 * 64)
                if not chunk:
                    break
                h.update(chunk)
            got = h.hexdigest()
        if expected_hash and got != expected_hash:
            return {"ok": False, "status": "FAILED", "error": "checksum mismatch", "remote": remote, "got": got}
        return {"ok": True, "status": "SYNCED", "remote": remote, "size": expected_size}
    except socket.timeout as exc:
        return {"ok": False, "status": "FAILED", "error": TIMEOUT, "detail": str(exc)}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "status": "FAILED", "error": _classify_error(exc), "detail": str(exc)[:300]}


def list_remote(data_dir: Path, product_id: str) -> dict[str, Any]:
    s = load_sftp_settings(data_dir)
    if not s["host"] or not s["username"]:
        return {"ok": False, "error": "SFTP not configured", "files": []}
    try:
        client, settings = _client(data_dir)
        sftp = client.open_sftp()
        remote = f"{settings['remote_media_path'].rstrip('/')}/{product_id}"
        try:
            names = sftp.listdir_attr(remote)
        except FileNotFoundError:
            sftp.close()
            client.close()
            return {"ok": True, "files": [], "path": remote}
        files = [{"filename": a.filename, "size": int(a.st_size or 0), "mtime": int(a.st_mtime or 0)} for a in names]
        sftp.close()
        client.close()
        return {"ok": True, "files": files, "path": remote}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": _classify_error(exc), "files": []}


def download_remote(data_dir: Path, remote_path: str, dest: Path) -> dict[str, Any]:
    if not remote_path or not str(remote_path).replace("\\", "/").startswith("/"):
        return {"ok": False, "error": "bad remote"}
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        sftp, _settings = _live_sftp(data_dir)
        if sftp is None:
            return {"ok": False, "error": "not connected"}
        sftp.get(remote_path, str(dest))
        return {"ok": dest.is_file()}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": _classify_error(exc)}


def delete_remote(data_dir: Path, remote_path: str) -> dict[str, Any]:
    if not remote_path:
        return {"ok": False, "error": "empty path"}
    try:
        client, _settings = _client(data_dir)
        sftp = client.open_sftp()
        sftp.remove(remote_path)
        sftp.close()
        client.close()
        return {"ok": True}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": _classify_error(exc)}
