import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.knowledge.source_catalog.classify import classify_filename
from src.knowledge.source_catalog.consistency import validate_consistency
from src.knowledge.source_catalog.deploy import upload_media_files
from src.knowledge.source_catalog.media import pending_uploads
from src.knowledge.source_catalog.queue import cancel_job, enqueue_media, process_waiting, retry_job
from src.knowledge.source_catalog.sftp_conn import test_connection
from src.knowledge.source_catalog.store import load_global_queue, load_media_index, save_global_queue, save_media_index
from src.knowledge.source_catalog.versions import generate_version, load_active, rollback


class GapFixesTests(unittest.TestCase):
    def test_candidates_and_low_confidence(self):
        r = classify_filename("zzz.png", ["cdn_cloudflare", "setup_central"], threshold=0.7)
        self.assertTrue(r["needs_review"])
        self.assertFalse(r["auto_assigned"])
        r2 = classify_filename("domain-cloudflare.png", ["cdn_cloudflare", "dns_records"])
        self.assertTrue(r2.get("candidates"))
        r3 = classify_filename("01-operations-pro.png", ["deploy_exit_1", "operations_pro"])
        ids = [c["feature_id"] for c in (r3.get("candidates") or [])]
        self.assertNotIn("deploy_exit_1", ids)

    def test_sftp_test_not_fake(self):
        with tempfile.TemporaryDirectory() as raw:
            with patch.dict("os.environ", {"BOT_SSH_HOST": "", "BOT_SSH_USER": "", "BOT_SSH_PASS": ""}):
                out = test_connection(Path(raw) / "data")
            self.assertFalse(out["ok"])
            self.assertEqual(out["status"], "NOT CONFIGURED")

    def test_save_password_and_key(self):
        from src.knowledge.source_catalog.sftp_conn import load_sftp_settings, save_sftp_settings

        with tempfile.TemporaryDirectory() as raw:
            data = Path(raw) / "data"
            save_sftp_settings(
                data,
                {"host": "1.2.3.4", "username": "u", "auth_method": "password", "port": "22"},
                password="secret-pass",
            )
            s = load_sftp_settings(data)
            self.assertTrue(s["has_password"])
            self.assertEqual(s["host"], "1.2.3.4")
            save_sftp_settings(
                data,
                {"host": "1.2.3.4", "username": "u", "auth_method": "key"},
                key_pem="-----BEGIN OPENSSH PRIVATE KEY-----\nabc\n-----END OPENSSH PRIVATE KEY-----",
            )
            s2 = load_sftp_settings(data)
            self.assertTrue(Path(s2["key_path"]).is_file())

    def test_accept_maps_feature_on_server_item(self):
        from src.knowledge.source_catalog.analyze import apply_mapping_decision

        with tempfile.TemporaryDirectory() as raw:
            data = Path(raw)
            save_media_index(
                data,
                "p1",
                {
                    "items": [
                        {
                            "media_id": "m1",
                            "status": "SYNCED",
                            "server_path": "/opt/Smart Support Bot/media/catalogs/p1/m1.png",
                            "ai_likely_feature": "cdn_cloudflare",
                            "classify_candidates": [{"feature_id": "cdn_cloudflare", "confidence": 0.9}],
                        }
                    ]
                },
            )
            self.assertTrue(apply_mapping_decision(data, "p1", "m1", action="accept", feature_ids=["cdn_cloudflare"]))
            item = load_media_index(data, "p1")["items"][0]
            self.assertEqual(item["catalog_feature_id"], "cdn_cloudflare")
            self.assertEqual(item["status"], "SYNCED")

    def test_queue_retry_one_job(self):
        with tempfile.TemporaryDirectory() as raw:
            data = Path(raw)
            save_media_index(data, "p1", {"items": [{"media_id": "m1", "filename": "a.png", "path": "x", "hash": "h", "size": 1, "feature_ids": ["f"]}]})
            jobs = enqueue_media(data, "p1", ["m1"])
            q = load_global_queue(data)
            q[0]["status"] = "FAILED"
            save_global_queue(data, q)
            self.assertTrue(retry_job(data, jobs[0]["job_id"]))
            self.assertEqual(load_global_queue(data)[0]["status"], "WAITING")
            self.assertTrue(cancel_job(data, jobs[0]["job_id"]))

    def test_unmapped_is_pending(self):
        pending = pending_uploads({"items": [{"status": "UNMAPPED", "hash": "aa", "media_id": "m"}]})
        self.assertEqual(len(pending), 1)

    def test_local_queue_upload_without_sftp(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            src = root / "a.png"
            blob = b"\x89PNG\r\n\x1a\n" + b"x" * 20
            src.write_bytes(blob)
            data = root / "data"
            import hashlib

            digest = hashlib.sha256(blob).hexdigest()
            save_media_index(
                data,
                "p1",
                {
                    "items": [
                        {
                            "media_id": "m1",
                            "path": str(src),
                            "hash": digest,
                            "status": "UNMAPPED",
                            "filename": "a.png",
                            "size": len(blob),
                        }
                    ]
                },
            )
            enqueue_media(data, "p1", ["m1"])
            with patch("src.knowledge.source_catalog.queue.session_status", return_value={"connected": False}):
                results = process_waiting(root, data)
            self.assertEqual(results, [])
            leftover = load_global_queue(data)
            self.assertEqual(len(leftover), 1)
            self.assertFalse(leftover[0].get("on_server"))
            self.assertEqual(leftover[0].get("error"), "not connected")
            item = load_media_index(data, "p1")["items"][0]
            from src.knowledge.source_catalog.media import is_remote_server_item

            self.assertFalse(is_remote_server_item(item))

    def test_remote_upload_leaves_queue(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            src = root / "a.png"
            blob = b"\x89PNG\r\n\x1a\n" + b"x" * 20
            src.write_bytes(blob)
            data = root / "data"
            digest = hashlib.sha256(blob).hexdigest()
            save_media_index(
                data,
                "p1",
                {
                    "items": [
                        {
                            "media_id": "m1",
                            "path": str(src),
                            "hash": digest,
                            "status": "LOCAL_ONLY",
                            "filename": "a.png",
                            "size": len(blob),
                        }
                    ]
                },
            )
            enqueue_media(data, "p1", ["m1"])

            def _ok(*_a, **_k):
                return {"ok": True, "remote": "/opt/Smart Support Bot/media/catalogs/p1/m1.png"}

            with patch("src.knowledge.source_catalog.queue.session_status", return_value={"connected": True}):
                with patch("src.knowledge.source_catalog.queue.upload_and_verify", side_effect=_ok):
                    results = process_waiting(root, data)
            self.assertEqual(results[0]["status"], "SYNCED")
            self.assertEqual(load_global_queue(data), [])
            from src.knowledge.source_catalog.media import is_remote_server_item

            self.assertTrue(is_remote_server_item(load_media_index(data, "p1")["items"][0]))

    def test_source_file_counts_as_source(self):
        with tempfile.TemporaryDirectory() as raw:
            data = Path(raw) / "data"
            src = Path(raw) / "note.md"
            src.write_text("physical product notes", encoding="utf-8")
            from src.knowledge.source_catalog.service import save_product_paths, source_root_for

            save_product_paths(data, "p1", str(src), "", "/opt/media/p1/")
            got = source_root_for(data, "p1")
            self.assertIsNotNone(got)
            self.assertTrue(got.is_file())

    def test_queue_hides_hundred_percent_on_server(self):
        from src.knowledge.source_catalog.queue import visible_queue_jobs

        jobs = [
            {"status": "UPLOADING", "progress": 40, "on_server": False},
            {"status": "SYNCED", "progress": 100, "on_server": True},
        ]
        vis = visible_queue_jobs(jobs)
        self.assertEqual(len(vis), 1)
        self.assertEqual(vis[0]["progress"], 40)

    def test_fake_synced_stays_in_queue(self):
        from src.knowledge.source_catalog.queue import visible_queue_jobs

        jobs = [{"status": "SYNCED", "progress": 100, "on_server": False, "note": "local copy"}]
        self.assertEqual(len(visible_queue_jobs(jobs)), 1)

    def test_mapped_send_needs_feature(self):
        from src.knowledge.source_catalog.queue import send_mapped_media_to_catalog

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            src = root / "a.png"
            src.write_bytes(b"\x89PNG\r\n\x1a\n" + b"x" * 20)
            data = root / "data"
            kr = root / "knowledge" / "product_catalogs"
            kr.mkdir(parents=True)
            (kr / "p1.json").write_text('{"product_id":"p1","media":[]}', encoding="utf-8")
            save_media_index(
                data,
                "p1",
                {"items": [{"media_id": "m1", "path": str(src), "filename": "a.png"}]},
            )
            blocked = send_mapped_media_to_catalog(root, root / "knowledge", data, "p1", "m1", "")
            self.assertFalse(blocked.get("ok"))
            out = send_mapped_media_to_catalog(root, root / "knowledge", data, "p1", "m1", "overview")
            self.assertTrue(out.get("ok"))
            copied = list((root / "products" / "p1" / "media").glob("*"))
            self.assertTrue(copied)
            (kr / "p2.json").write_text('{"product_id":"p2","media":[]}', encoding="utf-8")
            dest = send_mapped_media_to_catalog(
                root, root / "knowledge", data, "p1", "m1", "overview", catalog_id="p2"
            )
            self.assertTrue(dest.get("ok"))
            self.assertTrue((root / "products" / "p2" / "media").exists())
            from src.knowledge.source_catalog.catalog_edit import catalog_media_list, delete_all_catalog_media

            self.assertTrue(catalog_media_list(root / "knowledge", "p2"))
            wiped = delete_all_catalog_media(root, root / "knowledge", data, "p2")
            self.assertTrue(wiped.get("ok"))
            self.assertFalse(catalog_media_list(root / "knowledge", "p2"))

    def test_checksum_not_synced(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            src = root / "a.png"
            src.write_bytes(b"abc")
            data = root / "data"
            save_media_index(
                data,
                "p1",
                {"items": [{"media_id": "m1", "path": str(src), "hash": "deadbeef", "status": "LOCAL_ONLY", "filename": "a.png"}]},
            )
            dest = root / "dest"
            out = upload_media_files(data_dir=data, product_id="p1", dest_media=dest, only_ids=["m1"])
            self.assertFalse(out["ok"])
            idx = load_media_index(data, "p1")
            self.assertEqual(idx["items"][0]["status"], "FAILED")

    def test_orphaned_media(self):
        with tempfile.TemporaryDirectory() as raw:
            kr = Path(raw) / "k"
            dd = Path(raw) / "d"
            save_media_index(dd, "no-such-product", {"items": [{"filename": "x.png", "feature_ids": ["gone"], "status": "LOCAL_ONLY", "path": str(kr / "x.png")}]})
            report = validate_consistency(kr, dd, "no-such-product")
            self.assertTrue(report["orphaned_media"] or report["unmapped"] is not None)

    def test_ingest_duplicate(self):
        from src.knowledge.source_catalog.queue import ingest_files
        from src.knowledge.source_catalog import products as prodmod

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            pic = root / "pic" / "P"
            pic.mkdir(parents=True)
            blob = b"\x89PNG\r\n\x1a\n" + b"x" * 30
            (pic / "a.png").write_bytes(blob)
            data = root / "data"
            orig = prodmod.pic_dir_for_product
            prodmod.pic_dir_for_product = lambda *_a, **_k: pic  # type: ignore
            import src.knowledge.source_catalog.media as mediamod
            import src.knowledge.source_catalog.queue as queuemod

            mediamod.pic_dir_for_product = lambda *_a, **_k: pic  # type: ignore
            queuemod.pic_dir_for_product = lambda *_a, **_k: pic  # type: ignore
            try:
                from src.knowledge.source_catalog.media import scan_local_media

                scan_local_media(root, data, "p1")
                r = ingest_files(root, data, "p1", [("a.png", blob)])
                self.assertTrue(r.get("duplicates"))
                self.assertEqual(r["duplicates"][0]["status"], "DUPLICATE")
            finally:
                prodmod.pic_dir_for_product = orig  # type: ignore

    def test_catalog_text_and_photo_return(self):
        from src.knowledge.source_catalog.catalog_edit import (
            catalog_media_list,
            return_catalog_media_to_index,
            save_catalog_texts,
        )

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            kn = root / "knowledge"
            cat = kn / "product_catalogs"
            cat.mkdir(parents=True)
            (cat / "p1.json").write_text(
                '{"product_id":"p1","title":{"en":"Old"},"short_summary":{"en":"s"},'
                '"long_summary":{"en":"l"},"features":[{"id":"f1","title":{"en":"A"},"summary":{"en":"B"}}],'
                '"media":[{"path":"media/catalogs/p1/x.png","slot":"f1"}]}',
                encoding="utf-8",
            )
            data = root / "data"
            save_media_index(data, "p1", {"items": [{"media_id": "m1", "catalog_path": "media/catalogs/p1/x.png"}]})
            out = save_catalog_texts(
                kn, "p1", lang="fa", title="عنوان", short_summary="کوتاه", long_summary="کامل",
                features=[{"id": "f1", "title": "ویژگی", "summary": "شرح"}],
            )
            self.assertTrue(out.get("ok"))
            self.assertEqual(len(catalog_media_list(kn, "p1")), 1)
            return_catalog_media_to_index(kn, data, "p1", "media/catalogs/p1/x.png")
            self.assertEqual(catalog_media_list(kn, "p1"), [])
            from src.knowledge.source_catalog.catalog_edit import add_catalog_feature, read_catalog

            added = add_catalog_feature(kn, "p1", feature_id="new-ui", title="جدید", summary="شرح", lang="fa")
            self.assertTrue(added.get("ok"))
            ids = [str(f.get("id")) for f in (read_catalog(kn, "p1").get("features") or []) if isinstance(f, dict)]
            self.assertIn("new-ui", ids)


if __name__ == "__main__":
    unittest.main()
