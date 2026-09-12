"""Per-file upload queue. Retry re-sends one file only. Queue survives disconnect."""

from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Any

from src.knowledge.product_catalogs import product_media_dir
from src.knowledge.source_catalog.media import scan_local_media
from src.knowledge.source_catalog.sftp_conn import session_status, upload_and_verify
from src.knowledge.source_catalog.store import (
    append_history,
    live_root,
    load_global_queue,
    load_media_index,
    save_global_queue,
    save_media_index,
)
from src.operation_control import raise_if_stopped

WAITING = "WAITING"
UPLOADING = "UPLOADING"
VERIFYING = "VERIFYING"
SYNCED = "SYNCED"
FAILED = "FAILED"
CANCELLED = "CANCELLED"
DUPLICATE = "DUPLICATE"
PENDING_UPLOAD = "PENDING_UPLOAD"
CATALOG_ONLY = "CATALOG_ONLY"
QUEUE_DONE = {SYNCED, CATALOG_ONLY}


def _finished_on_server(job: dict[str, Any]) -> bool:
    if job.get("status") == CATALOG_ONLY:
        return True
    if job.get("on_server"):
        return True
    try:
        progress = int(job.get("progress") or 0)
    except (TypeError, ValueError):
        progress = 0
    return bool(job.get("on_server") and progress >= 100)


def visible_queue_jobs(queue: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Jobs still waiting for a real server upload."""
    return [job for job in queue if not _finished_on_server(job)]


def _drop_finished_server_jobs(queue: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [job for job in queue if not _finished_on_server(job)]


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
    kept = [job for job in queue if str(job.get("job_id") or "") != str(job_id or "")]
    if len(kept) == len(queue):
        return False
    save_global_queue(data_dir, kept)
    return True


def retry_job(data_dir: Path, job_id: str) -> bool:
    queue = load_global_queue(data_dir)
    found = False
    for job in queue:
        if job.get("job_id") == job_id and (
            job.get("status") in {FAILED, CANCELLED, PENDING_UPLOAD, WAITING}
            or (job.get("status") == SYNCED and not job.get("on_server"))
        ):
            job["status"] = WAITING
            job["error"] = ""
            job["progress"] = 0
            found = True
    save_global_queue(data_dir, queue)
    return found


def upload_state_path(data_dir: Path) -> Path:
    return live_root(data_dir) / "upload_state.json"


def set_upload_state(data_dir: Path, *, busy: bool, filename: str = "") -> None:
    import json

    path = upload_state_path(data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"busy": bool(busy), "filename": filename, "at": time.time()}),
        encoding="utf-8",
    )


def load_upload_state(data_dir: Path) -> dict[str, Any]:
    import json

    path = upload_state_path(data_dir)
    if not path.is_file():
        return {"busy": False, "filename": ""}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"busy": False, "filename": ""}
    return {
        "busy": bool(data.get("busy")),
        "filename": str(data.get("filename") or ""),
    }


def cancel_active_uploads(data_dir: Path) -> int:
    """Cancel persisted in-flight jobs and clear their stale media status."""
    queue = load_global_queue(data_dir)
    cancelled = 0
    touched: set[str] = set()
    for job in queue:
        if str(job.get("status") or "") not in {UPLOADING, VERIFYING, WAITING}:
            continue
        job["status"] = CANCELLED
        job["error"] = "stopped by user"
        job["progress"] = 0
        cancelled += 1
        pid = str(job.get("product_id") or "")
        if pid:
            touched.add(pid)
    save_global_queue(data_dir, queue)
    for pid in touched:
        index = load_media_index(data_dir, pid)
        for item in index.get("items") or []:
            if str(item.get("status") or "") in {UPLOADING, VERIFYING}:
                item["status"] = "LOCAL_ONLY"
        save_media_index(data_dir, pid, index)
    set_upload_state(data_dir, busy=False, filename="")
    return cancelled


def _needs_server(job: dict[str, Any]) -> bool:
    if job.get("on_server"):
        return False
    st = str(job.get("status") or "")
    if st in {WAITING, PENDING_UPLOAD, FAILED}:
        return True
    if st == SYNCED and not job.get("on_server"):
        return True
    return False


def process_waiting(project_root: Path, data_dir: Path, *, limit: int | None = None) -> list[dict[str, Any]]:
    queue = load_global_queue(data_dir)
    if not session_status().get("connected"):
        for job in queue:
            if _needs_server(job) and not job.get("error"):
                job["error"] = "not connected"
        save_global_queue(data_dir, queue)
        return []
    for job in queue:
        if _needs_server(job):
            job["status"] = WAITING
            job["error"] = ""
            job["progress"] = 0
    waiting = [job for job in queue if job.get("status") == WAITING]
    if limit is not None:
        waiting = waiting[:limit]
    results = []
    try:
        for job in waiting:
            raise_if_stopped()
            set_upload_state(data_dir, busy=True, filename=str(job.get("filename") or ""))
            save_global_queue(data_dir, queue)
            results.append(_run_job(project_root, data_dir, job))
            queue = _drop_finished_server_jobs(queue)
            save_global_queue(data_dir, queue)
    finally:
        set_upload_state(data_dir, busy=False, filename="")
    save_global_queue(data_dir, _drop_finished_server_jobs(queue))
    return results


def send_mapped_media_to_catalog(
    project_root: Path,
    knowledge_root: Path,
    data_dir: Path,
    product_id: str,
    media_id: str,
    feature_id: str,
    catalog_id: str = "",
    ai_hint: str = "",
) -> dict[str, Any]:
    """Copy one mapped photo into the product catalog. Feature or manual hint is required."""
    import json
    import shutil

    hint = str(ai_hint or "").strip()
    feat = str(feature_id or hint or "").strip()
    if not feat:
        return {"ok": False, "error": "no_feature"}
    pid = str(product_id or "").strip()
    dest_pid = str(catalog_id or product_id or "").strip() or pid
    mid = str(media_id or "").strip()
    index = load_media_index(data_dir, pid)
    item = next((i for i in index.get("items") or [] if str(i.get("media_id")) == mid), None)
    if not item:
        return {"ok": False, "error": "media not found"}
    from src.knowledge.source_catalog.analyze import _resolve_image

    src = _resolve_image(project_root, data_dir, pid, item)
    if src is None or not src.is_file():
        return {"ok": False, "error": "local file missing"}
    dest_dir = product_media_dir(project_root, dest_pid)
    dest = dest_dir / f"{mid}{src.suffix.lower() or Path(str(item.get('filename') or 'img.png')).suffix.lower() or '.png'}"
    shutil.copy2(src, dest)
    rel = str(dest.relative_to(project_root)).replace("\\", "/")
    item["catalog_path"] = rel
    item["catalog_feature_id"] = feat
    if hint:
        item["ai_hint"] = hint
    fids = [str(x) for x in (item.get("feature_ids") or []) if str(x).strip()]
    if feat not in fids:
        fids.append(feat)
    item["feature_ids"] = fids
    save_media_index(data_dir, pid, index)
    from src.knowledge.product_catalogs import product_json_path
    from src.knowledge.source_catalog.sftp_conn import (
        pull_remote_catalogs,
        push_catalog_photo_and_json,
        session_status,
    )

    cat = product_json_path(knowledge_root, dest_pid)
    # Catalogs are pulled when the SSH session connects. Avoid a full remote
    # directory round-trip for every photo unless this catalog is missing.
    if session_status().get("connected") and not cat.is_file():
        pull_remote_catalogs(data_dir, knowledge_root)
    data: dict[str, Any] = {}
    if cat.is_file():
        try:
            loaded = json.loads(cat.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data = loaded
        except (OSError, json.JSONDecodeError):
            data = {}
    media = list(data.get("media") or []) if isinstance(data.get("media"), list) else []
    media = [m for m in media if not (isinstance(m, dict) and m.get("path") == rel)]
    media.append(
        {
            "role": "catalog",
            "slot": feat,
            "feature_ids": [feat],
            "path": rel,
            "note": hint or src.name,
            "ai_hint": hint,
        }
    )
    data["media"] = media
    if not data.get("product_id"):
        data["product_id"] = dest_pid
    cat.parent.mkdir(parents=True, exist_ok=True)
    cat.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    from src.knowledge.product_catalogs import load_product_catalogs

    load_product_catalogs(knowledge_root)
    remote = {"ok": False, "error": "not connected"}
    if session_status().get("connected"):
        remote = push_catalog_photo_and_json(data_dir, dest, dest_pid, cat)
    append_history(
        data_dir,
        pid,
        {
            "action": "send_to_catalog",
            "result": "ok",
            "filename": str(item.get("filename") or src.name),
            "object": mid,
            "source_section": "media",
            "server": session_status().get("host") or "",
        },
    )
    return {"ok": True, "path": rel, "feature_id": feat, "on_server": bool(remote.get("ok"))}


def _run_job(project_root: Path, data_dir: Path, job: dict[str, Any]) -> dict[str, Any]:
    raise_if_stopped()
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

    remote_rel = f"{pid}/media/{mid}{src.suffix.lower()}"
    if not session_status().get("connected"):
        job["status"] = PENDING_UPLOAD
        job["on_server"] = False
        job["error"] = "not connected"
        save_media_index(data_dir, pid, index)
        return job
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
        append_history(
            data_dir,
            pid,
            {
                "action": "sftp_upload",
                "result": "FAILED",
                "filename": str(job.get("filename") or src.name),
                "object": mid,
                "error": job["error"],
                "source_section": "queue",
                "server": session_status().get("host") or "",
            },
        )
        return job
    item["status"] = SYNCED
    item["server_path"] = out.get("remote") or ""
    item["uploaded_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    job["status"] = SYNCED
    job["on_server"] = True
    job["progress"] = 100
    job["error"] = ""
    save_media_index(data_dir, pid, index)
    append_history(
        data_dir,
        pid,
        {
            "action": "sftp_upload",
            "result": "ok",
            "filename": str(job.get("filename") or src.name),
            "object": mid,
            "source_section": "queue",
            "server": session_status().get("host") or "",
        },
    )
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


def ingest_loose_files(
    project_root: Path,
    data_dir: Path,
    product_id: str,
    files: list[tuple[str, bytes]],
) -> dict[str, Any]:
    """Import photos from any disk path into inbox, then queue for server upload."""
    import hashlib
    import re

    if not product_id or not files:
        return {"ok": False, "error": "no files"}
    folder = live_root(data_dir) / "inbox" / product_id
    folder.mkdir(parents=True, exist_ok=True)
    scan_local_media(project_root, data_dir, product_id)
    index = load_media_index(data_dir, product_id)
    hashes = {str(i.get("hash")) for i in index.get("items") or [] if isinstance(i, dict)}
    imported: list[str] = []
    duplicates: list[dict[str, Any]] = []
    for name, blob in files:
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
    resolved = {str(Path(p).resolve()) for p in imported}
    new_ids = []
    for item in index.get("items") or []:
        raw = str(item.get("path") or "")
        if not raw:
            continue
        try:
            same = str(Path(raw).resolve()) in resolved
        except OSError:
            same = raw in imported
        if same:
            new_ids.append(str(item.get("media_id")))
    if not new_ids and imported:
        new_ids = [str(i.get("media_id")) for i in (index.get("items") or []) if str(i.get("path") or "") in imported]
    dup_hashes = {str(d.get("hash") or "") for d in duplicates}
    for item in index.get("items") or []:
        if str(item.get("hash") or "") in dup_hashes:
            mid = str(item.get("media_id") or "")
            if mid and mid not in new_ids:
                new_ids.append(mid)
    save_media_index(data_dir, product_id, index)
    jobs = enqueue_media(data_dir, product_id, new_ids) if new_ids else []
    if imported and not jobs:
        return {"ok": False, "error": "queue add failed", "duplicates": duplicates}
    return {"ok": True, "imported": new_ids, "duplicates": duplicates, "jobs": [j["job_id"] for j in jobs]}
