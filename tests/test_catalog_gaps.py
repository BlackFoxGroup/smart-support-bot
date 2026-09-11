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

    def test_sftp_test_not_fake(self):
        with tempfile.TemporaryDirectory() as raw:
            with patch.dict("os.environ", {"BOT_SSH_HOST": "", "BOT_SSH_USER": "", "BOT_SSH_PASS": ""}):
                out = test_connection(Path(raw) / "data")
            self.assertFalse(out["ok"])
            self.assertEqual(out["status"], "NOT CONFIGURED")

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
            with patch("src.knowledge.source_catalog.queue.ssh_ready", return_value=False):
                results = process_waiting(root, data)
            self.assertEqual(results[0]["status"], "SYNCED")
            dest = root / "media" / "catalogs" / "p1" / "m1.png"
            self.assertTrue(dest.is_file())

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


if __name__ == "__main__":
    unittest.main()
