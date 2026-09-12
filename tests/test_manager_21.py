from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from src.knowledge.source_catalog import sftp_conn
from src.knowledge.source_catalog.sftp_conn import push_catalog_json_to_bot
from src.ai.safety import bounded_ask_timeout, bounded_ask_tokens
from src.config import KNOWLEDGE_ROOT
from src.manager.app import _html
from src.manager.ai_store import (
    load_ai_settings,
    save_ai_settings,
    set_ai_connection_state,
)
from src.knowledge.source_catalog.analyze import analyze_and_send
from src.knowledge.catalog_rag import build_catalog_units
from src.knowledge.product_catalogs import load_product_catalogs, update_product_fields


class _RemoteHandle:
    def __init__(self, files: dict[str, bytes], path: str, mode: str) -> None:
        self.files = files
        self.path = path
        self.mode = mode
        self.buffer = bytearray(files.get(path, b""))

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        if "w" in self.mode:
            self.files[self.path] = bytes(self.buffer)

    def read(self):
        return bytes(self.buffer)

    def write(self, value: bytes) -> None:
        self.buffer = bytearray(value)


class _Sftp:
    def __init__(self, files: dict[str, bytes]) -> None:
        self.files = files
        self.dirs = {"/", "/srv", "/srv/bot"}

    def open(self, path: str, mode: str):
        if "r" in mode and path not in self.files:
            raise FileNotFoundError(path)
        return _RemoteHandle(self.files, path, mode)

    def stat(self, path: str):
        if path not in self.dirs and path not in self.files:
            raise FileNotFoundError(path)
        return object()

    def mkdir(self, path: str) -> None:
        self.dirs.add(path)

    def put(self, local: str, remote: str, callback=None) -> None:
        payload = Path(local).read_bytes()
        self.files[remote] = payload
        if callback:
            callback(len(payload), len(payload))

    def posix_rename(self, source: str, target: str) -> None:
        self.files[target] = self.files.pop(source)


class _Channel:
    @staticmethod
    def recv_exit_status() -> int:
        return 0


class _Stream:
    channel = _Channel()

    def __init__(self, payload: bytes = b"") -> None:
        self.payload = payload

    def read(self) -> bytes:
        return self.payload


class _Client:
    def __init__(self) -> None:
        self.command = ""

    def exec_command(self, command: str, timeout: int = 0):
        self.command = command
        active = b"active\n" if "is-active" in command else b""
        return None, _Stream(active), _Stream()


class Manager21Tests(unittest.TestCase):
    def test_manager_script_is_valid_for_send_button(self) -> None:
        page = _html("<button class='send-one'>send</button>", lang="en").decode()
        self.assertIn("document.querySelectorAll('.send-one')", page)
        self.assertNotIn("let j={{}}", page)
        self.assertIn("e.target.closest('a.zoom')", page)
        self.assertIn("form.busy-form", page)

    def test_bot_ai_request_has_bounded_latency_and_output(self) -> None:
        settings = SimpleNamespace(ai_timeout_seconds=60, ai_max_tokens=4096)
        self.assertEqual(bounded_ask_timeout(settings.ai_timeout_seconds), 20.0)
        self.assertEqual(bounded_ask_tokens(settings.ai_max_tokens), 2048)

    def test_manual_feature_sends_without_slow_ai_analysis(self) -> None:
        with (
            patch(
                "src.knowledge.source_catalog.analyze.analyze_media",
                side_effect=AssertionError("AI analysis must be skipped"),
            ),
            patch(
                "src.knowledge.source_catalog.queue.send_mapped_media_to_catalog",
                return_value={"ok": True},
            ) as send,
        ):
            out = analyze_and_send(
                Path("project"),
                Path("knowledge"),
                Path("data"),
                "product",
                "media",
                feature_id="feature-1",
            )
        self.assertTrue(out["ok"])
        self.assertTrue(out["analysis_skipped"])
        send.assert_called_once()

    def test_catalog_json_is_atomically_published_and_bot_reloaded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            knowledge = root / "knowledge"
            catalog = knowledge / "product_catalogs" / "demo.json"
            catalog.parent.mkdir(parents=True)
            catalog.write_text('{"product_id":"demo","catalog_enabled":true}', encoding="utf-8")
            files: dict[str, bytes] = {}
            sftp = _Sftp(files)
            client = _Client()
            with (
                patch.object(sftp_conn, "_live_sftp", return_value=(sftp, {})),
                patch.object(sftp_conn, "remote_install_root", return_value="/srv/bot"),
                patch.dict(sftp_conn._SESS, {"client": client, "sftp": sftp}),
            ):
                out = push_catalog_json_to_bot(
                    root / "data", knowledge, "demo", restart=True
                )
            self.assertTrue(out["ok"])
            self.assertEqual(
                files["/srv/bot/knowledge/product_catalogs/demo.json"],
                catalog.read_bytes(),
            )
            self.assertNotIn(
                "/srv/bot/knowledge/product_catalogs/demo.json.uploading", files
            )
            self.assertIn("systemctl restart smart-support-bot.service", client.command)

    def test_unified_install_path_enables_local_catalog_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "smart-support"
            knowledge = root / "knowledge"
            catalog = knowledge / "product_catalogs" / "demo.json"
            catalog.parent.mkdir(parents=True)
            catalog.write_text('{"product_id":"demo"}', encoding="utf-8")
            with (
                patch.dict(
                    os.environ,
                    {
                        "MANAGER_LOCAL_BOT": "1",
                        "BOT_REMOTE_ROOT": str(root),
                        "MANAGER_CONFIG_DIR": str(root / "data"),
                    },
                ),
                patch.object(sftp_conn, "_restart_local_bot", return_value={"ok": True}),
            ):
                self.assertTrue(sftp_conn.session_status()["connected"])
                settings = sftp_conn.load_sftp_settings(root / "data")
                self.assertEqual(settings["remote_bot_root"], str(root))
                out = push_catalog_json_to_bot(
                    root / "data", knowledge, "demo", restart=True
                )
            self.assertTrue(out["ok"])
            self.assertTrue(out["local"])

    def test_linux_installer_uses_one_default_root(self) -> None:
        root = Path(__file__).resolve().parents[1]
        script = (root / "deploy" / "install-manager.sh").read_text(encoding="utf-8")
        installer = (root / "src" / "manager" / "install_bot.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('MANAGER_INSTALL_DIR:-/opt/smart-support', script)
        self.assertIn('Environment="MANAGER_LOCAL_BOT=1"', script)
        self.assertIn('or "/opt/smart-support"', installer)

    def test_ai_uses_only_enabled_product_catalogs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            knowledge = Path(tmp)
            folder = knowledge / "product_catalogs"
            folder.mkdir()
            (folder / "enabled.json").write_text(
                '{"product_id":"enabled","catalog_enabled":true,"title":{"en":"Enabled"}}',
                encoding="utf-8",
            )
            (folder / "disabled.json").write_text(
                '{"product_id":"disabled","catalog_enabled":false,"title":{"en":"Disabled"}}',
                encoding="utf-8",
            )
            load_product_catalogs(knowledge)
            ids = {
                unit.product_id
                for unit in build_catalog_units(lang="en")
                if unit.kind == "product"
            }
            self.assertIn("enabled", ids)
            self.assertNotIn("disabled", ids)
            update_product_fields(knowledge, "disabled", catalog_enabled=True)
            ids = {
                unit.product_id
                for unit in build_catalog_units(lang="en")
                if unit.kind == "product"
            }
            self.assertIn("disabled", ids)
        load_product_catalogs(KNOWLEDGE_ROOT)

    def test_ai_and_server_settings_persist_in_manager_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_dir = root / "manager-data"
            (root / "bot").mkdir()
            with patch.dict(os.environ, {"MANAGER_CONFIG_DIR": str(config_dir)}):
                sftp_conn.save_sftp_settings(
                    root / "bot-data",
                    {
                        "host": "server.test",
                        "port": 2222,
                        "username": "admin",
                        "auth_method": "password",
                        "key_path": "",
                        "remote_media_path": "/srv/media",
                        "remote_bot_root": "/srv/bot",
                    },
                    password="server-secret",
                )
                save_ai_settings(
                    root / "bot",
                    root / "bot-data",
                    base_url="https://ai.test/v1",
                    model="model-1",
                    api_key="api-secret",
                )
                server = sftp_conn.load_sftp_settings(root / "bot-data")
                ai = load_ai_settings(root / "bot", root / "bot-data")
                set_ai_connection_state(root / "bot", root / "bot-data", connected=True)
                connected_ai = load_ai_settings(root / "bot", root / "bot-data")
            self.assertEqual(server["host"], "server.test")
            self.assertEqual(server["remote_bot_root"], "/srv/bot")
            self.assertTrue(server["has_password"])
            self.assertEqual(ai["model"], "model-1")
            self.assertEqual(ai["api_key"], "api-secret")
            self.assertTrue(connected_ai["connected"])
            self.assertEqual(connected_ai["api_key"], "api-secret")
            self.assertTrue((config_dir / "sftp.json").is_file())
            self.assertTrue((config_dir / "ai.json").is_file())

    def test_remote_ai_merge_preserves_other_env_keys_and_restarts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            files = {"/srv/bot/.env": b"TELEGRAM_BOT_TOKEN=keep\nAI_MODEL=old\n"}
            client = _Client()
            with (
                patch.object(sftp_conn, "_live_sftp", return_value=(_Sftp(files), {})),
                patch.object(sftp_conn, "remote_install_root", return_value="/srv/bot"),
                patch.dict(sftp_conn._SESS, {"client": client, "sftp": object(), "host": "server.test"}),
            ):
                result = sftp_conn.sync_remote_ai(
                    data_dir,
                    base_url="https://ai.test/v1",
                    model="new-model",
                    api_key="new-key",
                )
            env_text = files["/srv/bot/.env"].decode()
            self.assertTrue(result["ok"])
            self.assertIn("TELEGRAM_BOT_TOKEN=keep", env_text)
            self.assertIn("AI_MODEL=new-model", env_text)
            self.assertIn("AI_API_KEY=new-key", env_text)
            self.assertEqual(client.command, "systemctl restart smart-support-bot.service")


if __name__ == "__main__":
    unittest.main()
