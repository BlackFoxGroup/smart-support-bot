"""Per-file upload queue. Retry re-sends one file only. Queue survives disconnect."""

from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Any

from src.knowledge.source_catalog.deploy import upload_media_files
from src.knowledge.source_catalog.media import scan_local_media
from src.knowledge.source_catalog.sftp_conn import ssh_ready, upload_and_verify
from src.knowledge.source_catalog.store import (
    append_history,
    load_global_queue,
    load_media_index,
    save_global_queue,
    save_media_index,
)

WAITING = "WAITING"
UPLOADING = "UPLOADING"
VERIFYING = "VERIFYING"
SYNCED = "SYNCED"
FAILED = "FAILED"
CANCELLED = "CANCELLED"
DUPLICATE = "DUPLICATE"


def enqueue_media(data_dir: Path, product_id: str, media_ids: list[str]) -> list[dict[str, Any]]:
    index = load_media_index(data_dir, product_id)
    by_id = {str(i.get("media_id")): i for i in index.get("items") or [] if isinstance(i, dict)}
    queue = load_global_queue(data_dir)
    added = []
    for mid in media_ids:
        item = by_id.get(mid)
        if not item:
            continue
        job = {
            "job_id": uuid.uuid4().hex[:12],
            "product_id": product_id,
            "media_id": mid,
            "filename": item.get("filename") or "",
            "feature": ",".join(item.get("feature_ids") or []) or (item.get("catalog_feature_id") or ""),
            "size": item.get("size") or 0,
            "status": WAITING,
            "progress": 0,
            "speed": 0,
            "error": "",
            "local_path": item.get("path") or "",
            "hash": item.get("hash") or "",
        }
        queue.append(job)
        added.append(job)
    save_global_queue(data_dir, queue)
    return added


def cancel_job(data_dir: Path, job_id: str) -> bool:
    queue = load_global_queue(data_dir)
    found = False
    for job in queue:
        if job.get("job_id") == job_id and job.get("status") in {WAITING, FAILED, UPLOADING}:
            job["status"] = CANCELLED
            found = True
    save_global_queue(data_dir, queue)
    return found


def retry_job(data_dir: Path, job_id: str) -> bool:
    queue = load_global_queue(data_dir)
    found = False
    for job in queue:
        if job.get("job_id") == job_id and job.get("status") in {FAILED, CANCELLED}:
            job["status"] = WAITING
            job["error"] = ""
            job["progress"] = 0
            found = True
    save_global_queue(data_dir, queue)
    return found


def process_waiting(project_root: Path, data_dir: Path, *, limit: int = 8) -> list[dict[str, Any]]:
    queue = load_global_queue(data_dir)
    results = []
    n = 0
    for job in queue:
        if job.get("status") != WAITING:
            continue
        if n >= limit:
            break
        results.append(_run_job(project_root, data_dir, job))
        n += 1
    save_global_queue(data_dir, queue)
    return results


def _run_job(project_root: Path, data_dir: Path, job: dict[str, Any]) -> dict[str, Any]:
    pid = str(job.get("product_id") or "")
    mid = str(job.get("media_id") or "")
    index = load_media_index(data_dir, pid)
    item = next((i for i in index.get("items") or [] if str(i.get("media_id")) == mid), None)
    if not item:
        job["status"] = FAILED
        job["error"] = "media record missing"
        return job
    src = Path(str(item.get("path") or job.get("local_path") or ""))
    if not src.is_file():
        job["status"] = FAILED
        job["error"] = "local file missing"
        item["status"] = FAILED
        save_media_index(data_dir, pid, index)
        return job

    def _progress(done: int, total: int, speed: float) -> None:
        job["progress"] = int(100 * done / max(1, total))
        job["speed"] = int(speed)

    remote_rel = f"{pid}/{mid}{src.suffix.lower()}"
    if ssh_ready(data_dir):
        job["status"] = UPLOADING
        item["status"] = UPLOADING
        save_media_index(data_dir, pid, index)
        job["status"] = VERIFYING
        out = upload_and_verify(
            data_dir,
            src,
            remote_rel,
            str(item.get("hash") or ""),
            int(item.get("size") or src.stat().st_size),
            progress_cb=_progress,
        )
        if not out.get("ok"):
            job["status"] = FAILED
            job["error"] = str(out.get("error") or "upload failed")
            item["status"] = FAILED
            save_media_index(data_dir, pid, index)
            append_history(data_dir, pid, {"action": "sftp_upload", "result": "FAILED", "object": mid, "error": job["error"]})
            return job
        item["status"] = SYNCED
        item["server_path"] = out.get("remote") or ""
        item["uploaded_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        job["status"] = SYNCED
        job["progress"] = 100
        save_media_index(data_dir, pid, index)
        append_history(data_dir, pid, {"action": "sftp_upload", "result": "ok", "object": mid})
        return job

    dest = project_root / "media" / "catalogs" / pid
    job["status"] = UPLOADING
    local = upload_media_files(data_dir=data_dir, product_id=pid, dest_media=dest, only_ids=[mid])
    if local.get("ok") and mid in (local.get("uploaded") or []):
        job["status"] = SYNCED
        job["progress"] = 100
        job["error"] = ""
        job["note"] = "local copy (SFTP not configured)"
    else:
        job["status"] = FAILED
        fails = local.get("failed") or []
        job["error"] = str(fails[0] if fails else "local upload failed")
    return job


def ingest_files(
    project_root: Path,
    data_dir: Path,
    product_id: str,
    files: list[tuple[str, bytes]],
    *,
    feature_id: str = "",
) -> dict[str, Any]:
    from src.knowledge.source_catalog.products import pic_dir_for_product

    folder = pic_dir_for_product(project_root, product_id, data_dir)
    if folder is None:
        return {"ok": False, "error": "image directory Missing"}
    folder.mkdir(parents=True, exist_ok=True)
    scan_local_media(project_root, data_dir, product_id)
    index = load_media_index(data_dir, product_id)
    hashes = {str(i.get("hash")) for i in index.get("items") or [] if isinstance(i, dict)}
    imported = []
    duplicates = []
    for name, blob in files:
        import hashlib
        import re

        safe = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(name).name) or "image.bin"
        digest = hashlib.sha256(blob).hexdigest()
        if digest in hashes:
            duplicates.append({"filename": safe, "status": DUPLICATE, "hash": digest})
            continue
        dest = folder / safe
        n = 1
        while dest.exists():
            dest = folder / f"{dest.stem}_{n}{dest.suffix}"
            n += 1
        dest.write_bytes(blob)
        imported.append(str(dest))
        hashes.add(digest)
    scan_local_media(project_root, data_dir, product_id)
    index = load_media_index(data_dir, product_id)
    new_ids = []
    for path in imported:
        p = Path(path)
        for item in index.get("items") or []:
            if str(item.get("path")) == str(p):
                if feature_id:
                    fids = list(item.get("feature_ids") or [])
                    if feature_id not in fids:
                        fids.append(feature_id)
                    item["feature_ids"] = fids
                    item["catalog_feature_id"] = fids[0]
                    if item.get("status") == "UNMAPPED":
                        item["status"] = "LOCAL_ONLY"
                new_ids.append(str(item.get("media_id")))
    save_media_index(data_dir, product_id, index)
    jobs = enqueue_media(data_dir, product_id, new_ids) if new_ids else []
    return {"ok": True, "imported": new_ids, "duplicates": duplicates, "jobs": [j["job_id"] for j in jobs]}
