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
DEFAULT_BOT_ROOT = "/opt/smart-support"


def _local_bot_root() -> Path | None:
    enabled = (os.getenv("MANAGER_LOCAL_BOT") or "").strip().lower()
    if enabled not in {"1", "true", "yes", "on"}:
        return None
    root = Path(os.getenv("BOT_REMOTE_ROOT") or DEFAULT_BOT_ROOT).expanduser()
    return root if root.is_dir() else None


def _restart_local_bot() -> dict[str, Any]:
    import subprocess

    service = (os.getenv("BOT_SERVICE_NAME") or "smart-support-bot.service").strip()
    try:
        result = subprocess.run(
            ["systemctl", "restart", service],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if result.returncode:
            return {"ok": False, "error": (result.stderr or result.stdout).strip()[:300]}
        return {"ok": True}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": type(exc).__name__}


def settings_root(data_dir: Path) -> Path:
    configured = (os.getenv("MANAGER_CONFIG_DIR") or "").strip()
    return Path(configured).expanduser() if configured else live_root(data_dir)


def _config_path(data_dir: Path) -> Path:
    return settings_root(data_dir) / "sftp.json"


def _master_secret(data_dir: Path) -> str:
    env = (os.getenv("BOT_MASTER_SECRET") or os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
    if env:
        return env
    key_path = settings_root(data_dir) / ".sftp_key"
    if key_path.is_file():
        return key_path.read_text(encoding="utf-8").strip()
    legacy_key = live_root(data_dir) / ".sftp_key"
    if legacy_key.is_file() and legacy_key != key_path:
        raw = legacy_key.read_text(encoding="utf-8").strip()
        key_path.parent.mkdir(parents=True, exist_ok=True)
        key_path.write_text(raw, encoding="utf-8")
        try:
            os.chmod(key_path, 0o600)
        except OSError:
            pass
        return raw
    settings_root(data_dir).mkdir(parents=True, exist_ok=True)
    raw = os.urandom(32).hex()
    key_path.write_text(raw, encoding="utf-8")
    try:
        os.chmod(key_path, 0o600)
    except OSError:
        pass
    return raw


def load_sftp_settings(data_dir: Path) -> dict[str, Any]:
    path = _config_path(data_dir)
    legacy = live_root(data_dir) / "sftp.json"
    if not path.is_file() and legacy.is_file() and legacy != path:
        path = legacy
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
        or ((os.getenv("BOT_REMOTE_ROOT") or DEFAULT_BOT_ROOT).rstrip("/") + "/media/catalogs")
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
        "remote_bot_root": str(
            stored.get("remote_bot_root") or os.getenv("BOT_REMOTE_ROOT") or DEFAULT_BOT_ROOT
        ).strip().rstrip("/"),
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
        dest = settings_root(data_dir) / "sftp_user_key"
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
        "remote_bot_root": str(fields.get("remote_bot_root") or current["remote_bot_root"]).strip().rstrip("/"),
        "timeout": int(fields.get("timeout") or current["timeout"] or 20),
        "password_enc": password_enc,
    }
    path = _config_path(data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def _password(data_dir: Path, settings: dict[str, Any]) -> str:
    if settings.get("password_enc"):
        return decrypt_secret(str(settings["password_enc"]), _master_secret(data_dir))
    return (os.getenv("BOT_SSH_PASS") or "").strip()


_SESS_LOCK = threading.Lock()
_SFTP_IO_LOCK = threading.RLock()
_SESS: dict[str, Any] = {"client": None, "sftp": None, "host": ""}


def ssh_ready(data_dir: Path) -> bool:
    s = load_sftp_settings(data_dir)
    return bool(s["host"] and s["username"])


def session_status() -> dict[str, Any]:
    local = _local_bot_root()
    if local is not None:
        return {"connected": True, "host": "localhost", "local": True}
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
        out = {"ok": True, "status": CONNECTED, "host": settings["host"]}
        return out
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


def remote_install_root(data_dir: Path | None = None) -> str:
    if data_dir is not None:
        return str(load_sftp_settings(data_dir).get("remote_bot_root") or DEFAULT_BOT_ROOT).rstrip("/")
    return (os.getenv("BOT_REMOTE_ROOT") or DEFAULT_BOT_ROOT).rstrip("/")


def pull_remote_catalogs(data_dir: Path, knowledge_root: Path) -> dict[str, Any]:
    with _SFTP_IO_LOCK:
        return _pull_remote_catalogs_unlocked(data_dir, knowledge_root)


def _pull_remote_catalogs_unlocked(
    data_dir: Path, knowledge_root: Path
) -> dict[str, Any]:
    local_root = _local_bot_root()
    if local_root is not None:
        source = local_root / "knowledge" / "product_catalogs"
        if source.resolve() != (knowledge_root / "product_catalogs").resolve():
            import shutil

            destination = knowledge_root / "product_catalogs"
            destination.mkdir(parents=True, exist_ok=True)
            for file in source.glob("*.json"):
                shutil.copy2(file, destination / file.name)
        from src.knowledge.product_catalogs import load_product_catalogs

        loaded = load_product_catalogs(knowledge_root)
        return {"ok": True, "ids": [item.product_id for item in loaded], "local": True}
    sftp, _settings = _live_sftp(data_dir)
    if sftp is None:
        return {"ok": False, "error": "not connected", "ids": []}
    remote = f"{remote_install_root(data_dir)}/knowledge/product_catalogs"
    dest = knowledge_root / "product_catalogs"
    dest.mkdir(parents=True, exist_ok=True)
    ids: list[str] = []
    try:
        names = sftp.listdir(remote)
    except FileNotFoundError:
        return {"ok": False, "error": "remote catalogs missing", "ids": []}
    for name in names:
        if not name.endswith(".json"):
            continue
        local = dest / name
        temp = local.with_suffix(local.suffix + ".pulling")
        sftp.get(f"{remote}/{name}", str(temp))
        temp.replace(local)
        ids.append(name[:-5])
    from src.knowledge.product_catalogs import load_product_catalogs

    load_product_catalogs(knowledge_root)
    return {"ok": True, "ids": ids}


def push_catalog_json_to_bot(
    data_dir: Path,
    knowledge_root: Path,
    product_id: str,
    *,
    restart: bool = False,
) -> dict[str, Any]:
    with _SFTP_IO_LOCK:
        return _push_catalog_json_to_bot_unlocked(
            data_dir, knowledge_root, product_id, restart=restart
        )


def _push_catalog_json_to_bot_unlocked(
    data_dir: Path,
    knowledge_root: Path,
    product_id: str,
    *,
    restart: bool = False,
) -> dict[str, Any]:
    """Atomically replace one catalog JSON in the canonical bot directory."""
    from src.knowledge.product_catalogs import product_json_path

    pid = str(product_id or "").strip()
    catalog = product_json_path(knowledge_root, pid)
    if not pid or not catalog.is_file():
        return {"ok": False, "error": "catalog missing"}
    local_root = _local_bot_root()
    if local_root is not None:
        destination = local_root / "knowledge" / "product_catalogs" / catalog.name
        if destination.resolve() != catalog.resolve():
            destination.parent.mkdir(parents=True, exist_ok=True)
            temp = destination.with_suffix(destination.suffix + ".uploading")
            temp.write_bytes(catalog.read_bytes())
            temp.replace(destination)
        if restart:
            return {**_restart_local_bot(), "local": True}
        return {"ok": True, "local": True}
    sftp, _settings = _live_sftp(data_dir)
    with _SESS_LOCK:
        client = _SESS.get("client")
    if sftp is None or client is None:
        return {"ok": False, "error": "not connected"}
    remote = f"{remote_install_root(data_dir)}/knowledge/product_catalogs/{catalog.name}"
    temp = remote + ".uploading"
    try:
        _mkdirs(sftp, remote.rsplit("/", 1)[0])
        sftp.put(str(catalog), temp)
        try:
            sftp.posix_rename(temp, remote)
        except (AttributeError, OSError):
            try:
                sftp.remove(remote)
            except OSError:
                pass
            sftp.rename(temp, remote)
        if restart:
            _stdin, stdout, stderr = client.exec_command(
                "systemctl restart smart-support-bot.service && "
                "systemctl is-active smart-support-bot.service",
                timeout=30,
            )
            code = stdout.channel.recv_exit_status()
            state = stdout.read().decode("utf-8", "replace").strip()
            error = stderr.read().decode("utf-8", "replace").strip()
            if code != 0 or state != "active":
                return {"ok": False, "error": error or state or "bot restart failed"}
        return {"ok": True}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": _classify_error(exc)}


def push_catalog_photo_and_json(
    data_dir: Path,
    local_image: Path,
    dest_pid: str,
    local_json: Path,
) -> dict[str, Any]:
    with _SFTP_IO_LOCK:
        return _push_catalog_photo_and_json_unlocked(
            data_dir, local_image, dest_pid, local_json
        )


def _push_catalog_photo_and_json_unlocked(
    data_dir: Path,
    local_image: Path,
    dest_pid: str,
    local_json: Path,
) -> dict[str, Any]:
    local_root = _local_bot_root()
    if local_root is not None:
        import shutil

        image_dest = local_root / "media" / "catalogs" / dest_pid / local_image.name
        image_dest.parent.mkdir(parents=True, exist_ok=True)
        if image_dest.resolve() != local_image.resolve():
            shutil.copy2(local_image, image_dest)
        json_dest = local_root / "knowledge" / "product_catalogs" / local_json.name
        json_dest.parent.mkdir(parents=True, exist_ok=True)
        if local_json.is_file() and json_dest.resolve() != local_json.resolve():
            temp = json_dest.with_suffix(json_dest.suffix + ".uploading")
            temp.write_bytes(local_json.read_bytes())
            temp.replace(json_dest)
        return {"ok": True, "remote": str(image_dest), "local": True}
    sftp, _settings = _live_sftp(data_dir)
    if sftp is None:
        return {"ok": False, "error": "not connected"}
    # Catalog JSON stores media/catalogs/... paths relative to the bot root.
    # Publish to that exact location; remote_media_path is the source-media inbox.
    media_root = f"{remote_install_root(data_dir)}/media/catalogs"
    remote_img = f"{media_root}/{dest_pid}/{local_image.name}"
    remote_json = f"{remote_install_root(data_dir)}/knowledge/product_catalogs/{dest_pid}.json"
    try:
        _mkdirs(sftp, remote_img.rsplit("/", 1)[0])
        sftp.put(str(local_image), remote_img)
        if local_json.is_file():
            temp_json = remote_json + ".uploading"
            sftp.put(str(local_json), temp_json)
            try:
                sftp.posix_rename(temp_json, remote_json)
            except (AttributeError, OSError):
                try:
                    sftp.remove(remote_json)
                except OSError:
                    pass
                sftp.rename(temp_json, remote_json)
        return {"ok": True, "remote": remote_img}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": _classify_error(exc)}


def publish_catalog_to_bot(
    data_dir: Path,
    project_root: Path,
    knowledge_root: Path,
    product_id: str,
) -> dict[str, Any]:
    with _SFTP_IO_LOCK:
        return _publish_catalog_to_bot_unlocked(
            data_dir, project_root, knowledge_root, product_id
        )


def _publish_catalog_to_bot_unlocked(
    data_dir: Path,
    project_root: Path,
    knowledge_root: Path,
    product_id: str,
) -> dict[str, Any]:
    """Upload one complete catalog and its referenced media, then reload the bot."""
    import json

    from src.knowledge.product_catalogs import product_json_path

    pid = str(product_id or "").strip()
    catalog = product_json_path(knowledge_root, pid)
    if not pid or not catalog.is_file():
        return {"ok": False, "error": "catalog missing"}
    local_root = _local_bot_root()
    if local_root is not None:
        import shutil

        payload = json.loads(catalog.read_text(encoding="utf-8"))
        media = payload.get("media") if isinstance(payload, dict) else []
        uploaded = 0
        for item in media if isinstance(media, list) else []:
            if not isinstance(item, dict):
                continue
            rel = str(item.get("path") or "").replace("\\", "/").lstrip("/")
            source = (project_root / rel).resolve()
            destination = (local_root / rel).resolve()
            if source.is_file() and source != destination:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
            if source.is_file():
                uploaded += 1
        catalog_dest = local_root / "knowledge" / "product_catalogs" / catalog.name
        if catalog_dest.resolve() != catalog.resolve():
            catalog_dest.parent.mkdir(parents=True, exist_ok=True)
            temp = catalog_dest.with_suffix(catalog_dest.suffix + ".uploading")
            temp.write_bytes(catalog.read_bytes())
            temp.replace(catalog_dest)
        restarted = _restart_local_bot()
        return {**restarted, "uploaded": uploaded, "local": True}
    sftp, _settings = _live_sftp(data_dir)
    with _SESS_LOCK:
        client = _SESS.get("client")
    if sftp is None or client is None:
        return {"ok": False, "error": "not connected"}
    try:
        payload = json.loads(catalog.read_text(encoding="utf-8"))
        media = payload.get("media") if isinstance(payload, dict) else []
        uploaded = 0
        for item in media if isinstance(media, list) else []:
            if not isinstance(item, dict):
                continue
            rel = str(item.get("path") or "").replace("\\", "/").lstrip("/")
            local = (project_root / rel).resolve()
            try:
                local.relative_to(project_root.resolve())
            except ValueError:
                continue
            if not local.is_file():
                continue
            remote_image = f"{remote_install_root(data_dir)}/{rel}"
            _mkdirs(sftp, remote_image.rsplit("/", 1)[0])
            sftp.put(str(local), remote_image)
            uploaded += 1
        remote_catalog = f"{remote_install_root(data_dir)}/knowledge/product_catalogs/{catalog.name}"
        temp_catalog = remote_catalog + ".uploading"
        _mkdirs(sftp, remote_catalog.rsplit("/", 1)[0])
        sftp.put(str(catalog), temp_catalog)
        try:
            sftp.posix_rename(temp_catalog, remote_catalog)
        except (AttributeError, OSError):
            try:
                sftp.remove(remote_catalog)
            except OSError:
                pass
            sftp.rename(temp_catalog, remote_catalog)
        _stdin, stdout, stderr = client.exec_command(
            "systemctl restart smart-support-bot.service && "
            "systemctl is-active smart-support-bot.service",
            timeout=30,
        )
        code = stdout.channel.recv_exit_status()
        state = stdout.read().decode("utf-8", "replace").strip()
        error = stderr.read().decode("utf-8", "replace").strip()
        if code != 0 or state != "active":
            return {"ok": False, "error": error or state or "bot restart failed"}
        return {"ok": True, "uploaded": uploaded}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": _classify_error(exc)}


def sync_remote_ai(data_dir: Path, *, base_url: str, model: str, api_key: str) -> dict[str, Any]:
    """Merge AI settings into the remote bot .env and restart its service."""
    if not base_url.strip() or not model.strip() or not api_key.strip():
        return {"ok": False, "error": "AI endpoint, model, and API key are required"}
    updates = {
        "AI_BASE_URL": base_url.strip().rstrip("/"),
        "AI_MODEL": model.strip(),
        "AI_API_KEY": api_key.strip(),
    }
    local_root = _local_bot_root()
    if local_root is not None:
        env_path = local_root / ".env"
        lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.is_file() else []
        seen: set[str] = set()
        merged: list[str] = []
        for line in lines:
            key = line.split("=", 1)[0] if "=" in line else ""
            if key in updates:
                merged.append(f"{key}={updates[key]}")
                seen.add(key)
            else:
                merged.append(line)
        for key, value in updates.items():
            if key not in seen:
                merged.append(f"{key}={value}")
        temp = env_path.with_suffix(".env.uploading")
        temp.write_text("\n".join(merged).rstrip() + "\n", encoding="utf-8")
        temp.replace(env_path)
        restarted = _restart_local_bot()
        return {
            **restarted,
            "status": "AI_SYNCED" if restarted.get("ok") else "FAILED",
            "host": "localhost",
        }
    sftp, _settings = _live_sftp(data_dir)
    with _SESS_LOCK:
        client = _SESS.get("client")
    if sftp is None or client is None:
        return {"ok": False, "error": "not connected"}
    env_path = f"{remote_install_root(data_dir)}/.env"
    try:
        try:
            with sftp.open(env_path, "rb") as fh:
                raw = fh.read()
            text = raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)
        except FileNotFoundError:
            text = ""
        lines = text.splitlines()
        seen: set[str] = set()
        merged: list[str] = []
        for line in lines:
            key = line.split("=", 1)[0] if "=" in line else ""
            if key in updates:
                merged.append(f"{key}={updates[key]}")
                seen.add(key)
            else:
                merged.append(line)
        for key, value in updates.items():
            if key not in seen:
                merged.append(f"{key}={value}")
        payload = ("\n".join(merged).rstrip() + "\n").encode("utf-8")
        with sftp.open(env_path, "wb") as fh:
            fh.write(payload)
        _stdin, stdout, stderr = client.exec_command("systemctl restart smart-support-bot.service", timeout=30)
        code = int(stdout.channel.recv_exit_status())
        error = stderr.read()
        error_text = error.decode("utf-8", errors="replace") if isinstance(error, bytes) else str(error or "")
        if code:
            return {"ok": False, "error": error_text[:300] or f"systemctl exit {code}"}
        return {"ok": True, "status": "AI_SYNCED", "host": session_status().get("host") or ""}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": _classify_error(exc)}
