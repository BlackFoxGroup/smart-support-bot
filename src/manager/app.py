"""Smart Support Manager — local HTTP UI. No secrets in source or HTML logs."""

from __future__ import annotations

import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

from src.config import DATA_DIR, KNOWLEDGE_ROOT, PROJECT_ROOT
from src.knowledge.source_catalog import service
from src.knowledge.source_catalog.analyze import analyze_media, apply_mapping_decision
from src.knowledge.source_catalog.queue import cancel_job, ingest_files, process_waiting, retry_job
from src.knowledge.source_catalog.sftp_conn import list_remote, load_sftp_settings, save_sftp_settings, test_connection
from src.knowledge.source_catalog.store import load_global_queue
from src.manager.i18n import LABELS, LANGS, t

HOST = "127.0.0.1"
PORT = 8765
NAV_KEYS = (
    ("/", "nav_dash"),
    ("/products", "nav_products"),
    ("/catalog", "nav_catalog"),
    ("/media", "nav_media"),
    ("/queue", "nav_queue"),
    ("/server", "nav_server"),
    ("/history", "nav_history"),
    ("/settings", "nav_settings"),
)


def _esc(text: object) -> str:
    return (
        str(text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _cookie_lang(header: str | None) -> str:
    for part in (header or "").split(";"):
        k, _, v = part.strip().partition("=")
        if k == "ssm_lang" and v in LANGS:
            return v
    return ""


def _html(body: str, *, lang: str = "en", title: str | None = None, pick: bool = False) -> bytes:
    title = title or t(lang, "title")
    direction = "rtl" if lang == "fa" else "ltr"
    links = " ".join(f'<a href="{href}">{_esc(t(lang, key))}</a>' for href, key in NAV_KEYS)
    langs = " ".join(f'<a href="/set-lang?lang={code}">{_esc(LABELS[code])}</a>' for code in LANGS)
    nav = "" if pick else f"<nav><div class='nav-main'>{links}</div><div class='langbar'>{langs}</div></nav>"
    page = f"""<!DOCTYPE html>
<html lang="{_esc(lang)}" dir="{direction}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{{--bg:#0F172A;--fg:#FFFFFF;--card:#192134;--muted:#94A3B8;--accent:#059669;--on-accent:#000;--border:rgba(255,255,255,.08);--ring:#FFFFFF;--danger:#DC2626}}
*{{box-sizing:border-box}}
body{{font-family:Inter,Segoe UI,sans-serif;margin:0;background:var(--bg);color:var(--fg);line-height:1.5;font-size:16px}}
nav{{display:flex;flex-wrap:wrap;gap:12px;justify-content:space-between;align-items:center;background:#10192E;padding:12px 20px;position:sticky;top:0;border-bottom:1px solid var(--border)}}
nav a{{color:#93C5FD;margin-inline-end:12px;text-decoration:none}}
nav a:focus{{outline:2px solid var(--ring);outline-offset:2px}}
main{{padding:20px 24px;max-width:1200px;margin:0 auto}}
h1{{font-size:1.4rem;font-weight:600;margin:0 0 16px}}
table{{border-collapse:collapse;width:100%}}
td,th{{border-bottom:1px solid var(--border);padding:8px;text-align:start;font-size:14px}}
.card{{background:var(--card);padding:16px;margin:12px 0;border-radius:10px;border:1px solid var(--border)}}
button,input[type=submit],a.btn{{background:var(--accent);color:var(--on-accent);border:0;padding:10px 14px;min-height:44px;cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;font:inherit;border-radius:8px}}
button:focus,a.btn:focus,input:focus{{outline:2px solid var(--ring);outline-offset:2px}}
.toolbar{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:12px 0}}
.warn{{color:#FCA5A5}} .ok{{color:#6EE7B7}}
.drop{{border:2px dashed var(--border);padding:24px;margin:12px 0;border-radius:10px}}
img.th{{max-height:72px}} input,select{{background:#10192E;color:var(--fg);border:1px solid var(--border);padding:8px;margin:4px;border-radius:6px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px}}
.guide{{color:var(--muted);max-width:65ch}}
.pick{{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin-top:32px}}
.pick a.btn{{min-width:140px;justify-content:center}}
@media (prefers-reduced-motion:reduce){{*{{transition:none!important}}}}
</style></head><body>
{nav}
<main>
{"<h1>"+_esc(title)+"</h1>" if not pick else ""}
{body}
</main></body></html>"""
    return page.encode("utf-8")


def _form(raw: bytes, headers) -> tuple[dict[str, list[str]], list[tuple[str, bytes]]]:
    ctype = headers.get("Content-Type") or ""
    if "multipart/form-data" in ctype:
        m = re.search(r"boundary=(.+)", ctype)
        if not m:
            return {}, []
        boundary = m.group(1).encode("ascii")
        fields: dict[str, list[str]] = {}
        files: list[tuple[str, bytes]] = []
        for part in raw.split(b"--" + boundary):
            if not part or part in {b"--\r\n", b"--"}:
                continue
            head, _, body = part.partition(b"\r\n\r\n")
            body = body.rstrip(b"\r\n")
            hm = re.search(br'name="([^"]+)"', head)
            if not hm:
                continue
            name = hm.group(1).decode("utf-8", "replace")
            fn = re.search(br'filename="([^"]*)"', head)
            if fn:
                fname = fn.group(1).decode("utf-8", "replace")
                if body.endswith(b"\r\n"):
                    body = body[:-2]
                if fname and body:
                    files.append((fname, body))
            else:
                fields.setdefault(name, []).append(body.decode("utf-8", "replace"))
        return fields, files
    text = raw.decode("utf-8") if raw else ""
    return parse_qs(text), []


def execute_action(name: str, pid: str) -> tuple[str, str]:
    """Returns (ok_key_or_empty, err_text)."""
    if name == "toggle":
        page = service.product_page(PROJECT_ROOT, KNOWLEDGE_ROOT, DATA_DIR, pid)
        cur = bool((page.get("product") or {}).get("catalog_enabled", True))
        service.set_catalog_enabled(KNOWLEDGE_ROOT, pid, not cur)
        return "ok_toggle", ""
    if name == "scan":
        from src.knowledge.source_catalog.media import scan_local_media

        scan_local_media(PROJECT_ROOT, DATA_DIR, pid)
        return "ok_scan", ""
    if name == "map":
        service.auto_map_media(PROJECT_ROOT, KNOWLEDGE_ROOT, DATA_DIR, pid)
        return "ok_map", ""
    if name == "catalog":
        src = service.source_root_for(DATA_DIR, pid)
        if not src:
            return "", "err_source"
        out = service.sync_catalog(
            source_root=src,
            knowledge_root=KNOWLEDGE_ROOT,
            data_dir=DATA_DIR,
            product_id=pid,
            force=False,
            activate=True,
        )
        if not out.get("ok"):
            return "", str(out.get("error") or "catalog failed")
        return "ok_catalog", ""
    if name == "upload-media":
        service.sync_media(PROJECT_ROOT, DATA_DIR, pid)
        return "ok_queue", ""
    if name == "rollback":
        from src.knowledge.source_catalog.versions import rollback

        out = rollback(KNOWLEDGE_ROOT, DATA_DIR, pid)
        if not out.get("ok"):
            return "", "err_rollback"
        return "ok_rollback", ""
    return "", "unknown action"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:  # noqa: A003
        return

    def _send(self, data: bytes, code: int = 200, ctype: str = "text/html; charset=utf-8") -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _redir(self, loc: str) -> None:
        self.send_response(303)
        self.send_header("Location", loc)
        self.end_headers()

    def _lang(self) -> str:
        return _cookie_lang(self.headers.get("Cookie"))

    def _page(self, body: str, title: str | None = None) -> None:
        self._send(_html(body, lang=self._lang() or "en", title=title))

    def do_GET(self) -> None:  # noqa: N802
        u = urlparse(self.path)
        path = unquote(u.path)
        q = parse_qs(u.query)
        pid = (q.get("id") or [""])[0]
        lang = self._lang()
        if path == "/set-lang":
            code = (q.get("lang") or ["en"])[0]
            if code not in LANGS:
                code = "en"
            self.send_response(303)
            self.send_header("Set-Cookie", f"ssm_lang={code}; Path=/; Max-Age=31536000")
            self.send_header("Location", "/")
            self.end_headers()
            return
        if not lang and path not in {"/thumb"}:
            picks = "".join(f'<a class="btn" href="/set-lang?lang={c}">{_esc(LABELS[c])}</a>' for c in LANGS)
            self._send(
                _html(
                    f"<p class='guide'>{_esc(t('en', 'choose_lang'))}</p><div class='pick'>{picks}</div>",
                    lang="en",
                    pick=True,
                    title=t("en", "choose_lang"),
                )
            )
            return
        if path.startswith("/run/"):
            action = path.split("/")[2]
            try:
                ok, err = execute_action(action, pid)
            except Exception as exc:  # noqa: BLE001
                loc = f"/products?id={quote(pid)}&err={quote(str(exc))}" if pid else f"/?err={quote(str(exc))}"
                self._redir(loc)
                return
            loc = "/queue" if action == "upload-media" else f"/products?id={pid}"
            if err:
                loc = f"/products?id={quote(pid)}&err={quote(err)}"
            elif ok:
                loc = f"{loc}&msg={ok}" if "?" in loc else f"{loc}?msg={ok}"
            self._redir(loc)
            return
        dash = service.dashboard(PROJECT_ROOT, KNOWLEDGE_ROOT, DATA_DIR)
        if path == "/":
            cards = []
            for p in dash["products"]:
                cards.append(
                    f"<div class='card'><h3><a href='/products?id={_esc(p['product_id'])}'>{_esc(p['title'])}</a></h3>"
                    f"<p>Catalog: {_esc(p['catalog_status'])}<br>Version: {_esc(p['catalog_version'])}<br>"
                    f"Features: {_esc(p['features'])}<br>Media: {_esc(p['images'])}<br>"
                    f"Synced: {_esc(p['synced'])} Pending: {_esc(p['pending'])} "
                    f"Failed: {_esc(p['failed'])} Unmapped: {_esc(p['unmapped'])}<br>"
                    f"Server: {_esc(p['server'])}</p></div>"
                )
            guide = (
                f"<div class='card'><h2>{_esc(t(lang, 'guide_title'))}</h2>"
                f"<p class='guide'>{_esc(t(lang, 'guide_body'))}</p></div>"
            )
            self._page(guide + "<div class='grid'>" + "".join(cards) + "</div>")
            return
        if path == "/products":
            if pid:
                self._product(pid, q)
                return
            rows = []
            for m in dash.get("maps") or []:
                st = "Registered" if m.get("registered") else "Unregistered"
                if m.get("source") == "Missing" or m.get("images") == "Missing":
                    st += " / Missing"
                rows.append(
                    "<tr>"
                    f"<td>{_esc(m.get('product_id'))}</td><td>{_esc(m.get('display'))}</td>"
                    f"<td>{_esc(m.get('source'))}</td><td>{_esc(m.get('images'))}</td>"
                    f"<td>{_esc(m.get('server_media'))}</td><td>{st}</td>"
                    f"<td><a href='/products?id={_esc(m.get('product_id'))}'>open</a></td></tr>"
                )
            self._page("<table><tr><th>Product ID</th><th>Display</th><th>Source</th>"
                             "<th>Images</th><th>Server media</th><th>Status</th><th></th></tr>"
                             + "".join(rows) + "</table>")
            return
        if path == "/catalog":
            rows = []
            for p in dash["products"]:
                rows.append(
                    f"<tr><td>{_esc(p['product_id'])}</td><td>{_esc(p['catalog_status'])}</td>"
                    f"<td>v{_esc(p['catalog_version'])}</td>"
                    f"<td><a class='btn' href='/run/catalog?id={_esc(p['product_id'])}'>Build</a></td></tr>"
                )
            self._page("<table>" + "".join(rows) + "</table>")
            return
        if path == "/media":
            pid = pid or (dash["products"][0]["product_id"] if dash["products"] else "")
            self._media(pid, q)
            return
        if path == "/queue":
            rows = []
            for job in load_global_queue(DATA_DIR):
                rows.append(
                    "<tr>"
                    f"<td>{_esc(job.get('filename'))}</td><td>{_esc(job.get('product_id'))}</td>"
                    f"<td>{_esc(job.get('feature'))}</td><td>{_esc(job.get('size'))}</td>"
                    f"<td>{_esc(job.get('status'))}</td><td>{_esc(job.get('progress'))}%</td>"
                    f"<td>{_esc(job.get('speed'))}</td><td class='warn'>{_esc(job.get('error'))}</td>"
                    f"<td><form method='post' action='/api/retry'><input type='hidden' name='job' value='{_esc(job.get('job_id'))}'>"
                    f"<button>Retry</button></form>"
                    f"<form method='post' action='/api/cancel'><input type='hidden' name='job' value='{_esc(job.get('job_id'))}'>"
                    f"<button>Cancel</button></form></td></tr>"
                )
            body = (
                "<form method='post' action='/api/process-queue'><button>Process waiting</button></form>"
                "<table><tr><th>Filename</th><th>Product</th><th>Feature</th><th>Size</th>"
                "<th>Status</th><th>Progress</th><th>Speed</th><th>Error</th><th></th></tr>"
                + "".join(rows)
                + "</table>"
            )
            self._page(body, t(lang, "nav_queue"))
            return
        if path == "/server":
            pid = pid or (dash["products"][0]["product_id"] if dash["products"] else "")
            remote = list_remote(DATA_DIR, pid) if pid else {"files": [], "error": ""}
            page = service.product_page(PROJECT_ROOT, KNOWLEDGE_ROOT, DATA_DIR, pid) if pid else {"media": []}
            qtext = (q.get("q") or [""])[0].lower()
            stf = (q.get("status") or [""])[0]
            rows = []
            for m in page.get("media") or []:
                if qtext and qtext not in str(m.get("filename") or "").lower():
                    continue
                if stf and m.get("status") != stf:
                    continue
                rows.append(
                    "<tr>"
                    f"<td>{_esc(m.get('filename'))}</td><td>{_esc(m.get('size'))}</td>"
                    f"<td>{_esc((m.get('hash') or '')[:12])}</td><td>{_esc(pid)}</td>"
                    f"<td>{_esc(', '.join(m.get('feature_ids') or []))}</td>"
                    f"<td>{_esc(m.get('status'))}</td><td>{_esc(m.get('uploaded_at'))}</td>"
                    f"<td><form method='post' action='/api/delete'><input type='hidden' name='id' value='{_esc(pid)}'>"
                    f"<input type='hidden' name='mid' value='{_esc(m.get('media_id'))}'><button>Delete</button></form>"
                    + (
                        "<form method='post' action='/api/keep'><input type='hidden' name='id' value='"
                        + _esc(pid)
                        + "'><input type='hidden' name='mid' value='"
                        + _esc(m.get("media_id"))
                        + "'><button>Keep On Server</button></form>"
                        if m.get("status") == "LOCAL_DELETED"
                        else ""
                    )
                    + "</td></tr>"
                )
            err = f"<p class='warn'>{_esc(remote.get('error'))}</p>" if remote.get("error") else ""
            rrows = "".join(
                f"<tr><td>{_esc(f.get('filename'))}</td><td>{_esc(f.get('size'))}</td></tr>"
                for f in remote.get("files") or []
            )
            self._page(
                    f"<form>Product <input name='id' value='{_esc(pid)}'> Search <input name='q' value='{_esc(qtext)}'> "
                    f"Status <input name='status' value='{_esc(stf)}'><button>Filter</button></form>"
                    f"{err}<h3>Index</h3><table>{''.join(rows)}</table>"
                    f"<h3>Remote listing</h3><table>{rrows}</table>",
                    t(lang, "nav_server"),
                )
            return
        if path == "/history":
            pid = pid or (dash["products"][0]["product_id"] if dash["products"] else "")
            page = service.product_page(PROJECT_ROOT, KNOWLEDGE_ROOT, DATA_DIR, pid) if pid else {"history": []}
            hist = "".join(
                f"<li>{_esc(h.get('timestamp'))} {_esc(h.get('action'))} {_esc(h.get('result'))} {_esc(h.get('error'))}</li>"
                for h in page.get("history") or []
            )
            self._page(f"<p>Product {_esc(pid)}</p><ul>{hist}</ul>", t(lang, "nav_history"))
            return
        if path == "/settings":
            s = load_sftp_settings(DATA_DIR)
            maps = "".join(
                "<tr>"
                f"<td>{_esc(m.get('product_id'))}</td><td>{_esc(m.get('display'))}</td>"
                f"<td>{_esc(m.get('source'))}</td><td>{_esc(m.get('images'))}</td></tr>"
                for m in dash.get("maps") or []
            )
            body = f"""
<div class="card">
<h2>Server Connection</h2>
<form method="post" action="/api/sftp">
Host <input name="host" value="{_esc(s['host'])}">
Port <input name="port" value="{_esc(s['port'])}">
Username <input name="username" value="{_esc(s['username'])}">
Auth
<select name="auth_method">
<option value="key" {"selected" if s["auth_method"]=="key" else ""}>Private key</option>
<option value="password" {"selected" if s["auth_method"]=="password" else ""}>Password</option>
</select>
Private key path <input name="key_path" value="{_esc(s['key_path'])}" size="40">
Password <input type="password" name="password" autocomplete="new-password">
Remote media path <input name="remote_media_path" value="{_esc(s['remote_media_path'])}" size="50">
<button>Save</button>
</form>
<form method="post" action="/api/test"><button>Test Connection</button></form>
<p>Password is stored encrypted. It is not written to catalogs or logs.</p>
</div>
<div class="card">
<h2>Product directory mapping</h2>
<table><tr><th>Product ID</th><th>Display</th><th>Source</th><th>Images</th></tr>{maps}</table>
<form method="post" action="/api/paths">
Product ID <input name="id"> Display <input name="display">
Source <input name="source" size="40"> Images <input name="images" size="40">
Server media <input name="server_media" size="40">
<button>Save mapping</button>
</form>
</div>
"""
            self._page(body, t(lang, "nav_settings"))
            return
        if path == "/analyze":
            mid = (q.get("mid") or [""])[0]
            result = analyze_media(KNOWLEDGE_ROOT, DATA_DIR, pid, mid)
            cands = "".join(
                f"<li>{_esc(c.get('feature_id'))} — {_esc(c.get('percent'))}%"
                f"<form method='post' action='/api/map-decide'><input type='hidden' name='id' value='{_esc(pid)}'>"
                f"<input type='hidden' name='mid' value='{_esc(mid)}'><input type='hidden' name='action' value='change'>"
                f"<input type='hidden' name='features' value='{_esc(c.get('feature_id'))}'><button>Accept this</button></form></li>"
                for c in result.get("candidates") or []
            )
            body = f"""
<div class="card">
<p>Description: {_esc(result.get('description'))}</p>
<p>Visible UI: {_esc(result.get('visible_ui'))}</p>
<p>Likely feature: {_esc(result.get('likely_feature'))}</p>
<p>Likely screen: {_esc(result.get('likely_screen'))}</p>
<p>Keywords: {_esc(result.get('keywords'))}</p>
<p>Confidence: {_esc(result.get('confidence'))} Review: {_esc(result.get('needs_review'))}</p>
<p>AI available: {_esc(result.get('ai_available'))} — AI is classification only.</p>
<h3>Candidate Features</h3><ul>{cands}</ul>
<form method="post" action="/api/map-decide">
<input type="hidden" name="id" value="{_esc(pid)}"><input type="hidden" name="mid" value="{_esc(mid)}">
Features (comma) <input name="features">
<button name="action" value="accept">Accept</button>
<button name="action" value="change">Change</button>
<button name="action" value="reject">Reject</button>
</form>
</div>"""
            self._page(body, "Analyze")
            return
        if path == "/thumb":
            mid = (q.get("mid") or [""])[0]
            page = service.product_page(PROJECT_ROOT, KNOWLEDGE_ROOT, DATA_DIR, pid)
            item = next((m for m in page.get("media") or [] if str(m.get("media_id")) == mid), None)
            file = Path(str((item or {}).get("path") or (item or {}).get("server_path") or ""))
            if not file.is_file():
                self._send(b"missing", 404, "text/plain")
                return
            self._send(file.read_bytes(), 200, str((item or {}).get("mime_type") or "image/png"))
            return
        self._send(b"not found", 404, "text/plain")

    def _product(self, pid: str, q: dict | None = None) -> None:
        q = q or {}
        lang = self._lang() or "en"
        page = service.product_page(PROJECT_ROOT, KNOWLEDGE_ROOT, DATA_DIR, pid)
        p = page.get("product") or {}
        feats = "".join(f"<option>{_esc(f)}</option>" for f in page.get("features") or [])
        msg_key = (q.get("msg") or [""])[0]
        err_key = (q.get("err") or [""])[0]
        flash = ""
        if msg_key:
            flash += f"<p class='ok'>{_esc(t(lang, msg_key) if msg_key.startswith('ok_') else msg_key)}</p>"
        if err_key:
            flash += f"<p class='warn'>{_esc(t(lang, err_key) if err_key.startswith('err_') else err_key)}</p>"
        body = f"""
<div class="card">
<h2>{_esc(p.get('title') or pid)}</h2>
<p>ID {_esc(pid)} Catalog {_esc(p.get('catalog_status'))} v{_esc(p.get('catalog_version'))}
AI {'ON' if p.get('catalog_enabled') else 'OFF'}</p>
<p>Source: {_esc(p.get('source'))}<br>Images: {_esc(p.get('pic_dir'))}<br>Server media: {_esc(p.get('server_media'))}</p>
{flash}
<div class="toolbar">
<a class="btn" href="/run/toggle?id={_esc(pid)}">{_esc(t(lang, 'toggle'))}</a>
<a class="btn" href="/run/scan?id={_esc(pid)}">{_esc(t(lang, 'scan'))}</a>
<a class="btn" href="/run/map?id={_esc(pid)}">{_esc(t(lang, 'map'))}</a>
<a class="btn" href="/run/catalog?id={_esc(pid)}">{_esc(t(lang, 'catalog'))}</a>
<a class="btn" href="/run/upload-media?id={_esc(pid)}">{_esc(t(lang, 'upload'))}</a>
<a class="btn" href="/run/rollback?id={_esc(pid)}">{_esc(t(lang, 'rollback'))}</a>
</div>
</div>
<div class="card drop" id="drop">
<h3>Select Files</h3>
<form method="post" action="/api/ingest" enctype="multipart/form-data" id="up">
<input type="hidden" name="id" value="{_esc(pid)}">
<input type="file" name="files" id="files" multiple accept="image/*">
Feature <select name="feature"><option value=""></option>{feats}</select>
<button type="submit">Upload selected</button>
<button type="button" onclick="document.getElementById('files').value=''">Cancel</button>
</form>
<div id="preview"></div>
</div>
<script>
const input=document.getElementById('files'); const box=document.getElementById('drop'); const prev=document.getElementById('preview');
function show(){{prev.innerHTML='';[...input.files].forEach((f,i)=>{{const d=document.createElement('div');
d.innerHTML='<b>'+f.name+'</b> '+(f.size/1024).toFixed(1)+' KB <button type=button data-i="'+i+'">remove</button>';
if(f.type.startsWith('image/')){{const img=document.createElement('img');img.className='th';img.src=URL.createObjectURL(f);d.prepend(img);}}
prev.appendChild(d);}});prev.querySelectorAll('button').forEach(b=>b.onclick=()=>{{const dt=new DataTransfer();[...input.files].forEach((f,i)=>{{if(i!=+b.dataset.i)dt.items.add(f);}});input.files=dt.files;show();}});}}
input.onchange=show; ['dragover','drop'].forEach(ev=>box.addEventListener(ev,e=>{{e.preventDefault(); if(ev==='drop'){{input.files=e.dataTransfer.files;show();}}}}));
</script>
<p><a href="/media?id={_esc(pid)}">Media</a> · <a href="/queue">Queue</a></p>
"""
        self._page(body, pid)

    def _media(self, pid: str, q) -> None:
        page = service.product_page(PROJECT_ROOT, KNOWLEDGE_ROOT, DATA_DIR, pid)
        qtext = (q.get("q") or [""])[0].lower()
        rows = []
        for m in page.get("media") or []:
            if qtext and qtext not in str(m.get("filename") or "").lower():
                continue
            rows.append(
                "<tr>"
                f"<td><img class='th' src='/thumb?id={_esc(pid)}&mid={_esc(m.get('media_id'))}'></td>"
                f"<td>{_esc(m.get('filename'))}</td><td>{_esc(m.get('status'))}</td>"
                f"<td>{_esc(', '.join(m.get('feature_ids') or []))}</td>"
                f"<td>{_esc(m.get('size'))}</td>"
                f"<td><a href='/analyze?id={_esc(pid)}&mid={_esc(m.get('media_id'))}'>AI analyze</a></td>"
                f"<td><form method='post' action='/api/delete'><input type='hidden' name='id' value='{_esc(pid)}'>"
                f"<input type='hidden' name='mid' value='{_esc(m.get('media_id'))}'><button>Delete</button></form></td>"
                "</tr>"
            )
        cons = page.get("consistency") or {}
        self._page(
                f"<p>Consistency mapped { _esc(cons.get('mapped')) } / {_esc(cons.get('media'))} "
                f"orphaned { _esc(cons.get('orphaned_media')) }</p>"
                f"<form>id <input name='id' value='{_esc(pid)}'> Search <input name='q'><button>Search</button></form>"
                "<table><tr><th></th><th>File</th><th>Status</th><th>Features</th><th>Size</th><th></th><th></th></tr>"
                + "".join(rows)
                + "</table>",
                t(self._lang() or "en", "nav_media"),
            )

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        form, files = _form(raw, self.headers)
        pid = (form.get("id") or [""])[0]
        u = urlparse(self.path).path
        loc = f"/products?id={pid}" if pid else "/"
        try:
            if u == "/api/toggle":
                page = service.product_page(PROJECT_ROOT, KNOWLEDGE_ROOT, DATA_DIR, pid)
                cur = bool((page.get("product") or {}).get("catalog_enabled", True))
                service.set_catalog_enabled(KNOWLEDGE_ROOT, pid, not cur)
            elif u == "/api/scan":
                from src.knowledge.source_catalog.media import scan_local_media

                scan_local_media(PROJECT_ROOT, DATA_DIR, pid)
            elif u == "/api/map":
                service.auto_map_media(PROJECT_ROOT, KNOWLEDGE_ROOT, DATA_DIR, pid)
            elif u == "/api/catalog":
                src = service.source_root_for(DATA_DIR, pid)
                if not src:
                    self._page("<p class='warn'>Source directory Missing</p>")
                    return
                service.sync_catalog(
                    source_root=src,
                    knowledge_root=KNOWLEDGE_ROOT,
                    data_dir=DATA_DIR,
                    product_id=pid,
                    force=False,
                    activate=True,
                )
            elif u == "/api/upload-media":
                service.sync_media(PROJECT_ROOT, DATA_DIR, pid)
                loc = "/queue"
            elif u == "/api/rollback":
                from src.knowledge.source_catalog.versions import rollback

                rollback(KNOWLEDGE_ROOT, DATA_DIR, pid)
            elif u == "/api/ingest":
                feat = (form.get("feature") or [""])[0]
                result = ingest_files(PROJECT_ROOT, DATA_DIR, pid, files, feature_id=feat)
                loc = "/queue"
                if not result.get("ok"):
                    self._page(f"<p class='warn'>{_esc(result.get('error'))}</p>")
                    return
                process_waiting(PROJECT_ROOT, DATA_DIR)
            elif u == "/api/process-queue":
                process_waiting(PROJECT_ROOT, DATA_DIR)
                loc = "/queue"
            elif u == "/api/retry":
                retry_job(DATA_DIR, (form.get("job") or [""])[0])
                process_waiting(PROJECT_ROOT, DATA_DIR, limit=1)
                loc = "/queue"
            elif u == "/api/cancel":
                cancel_job(DATA_DIR, (form.get("job") or [""])[0])
                loc = "/queue"
            elif u == "/api/sftp":
                save_sftp_settings(
                    DATA_DIR,
                    {
                        "host": (form.get("host") or [""])[0],
                        "port": (form.get("port") or ["22"])[0],
                        "username": (form.get("username") or [""])[0],
                        "auth_method": (form.get("auth_method") or ["key"])[0],
                        "key_path": (form.get("key_path") or [""])[0],
                        "remote_media_path": (form.get("remote_media_path") or [""])[0],
                    },
                    password=(form.get("password") or [""])[0] or None,
                )
                loc = "/settings"
            elif u == "/api/test":
                result = test_connection(DATA_DIR)
                self._page(f"<p class='{'ok' if result.get('ok') else 'warn'}'>{_esc(result.get('status'))} {_esc(result.get('error'))}</p><p><a href='/settings'>Back</a></p>")
                return
            elif u == "/api/paths":
                service.save_product_paths(
                    DATA_DIR,
                    pid,
                    (form.get("source") or [""])[0],
                    (form.get("images") or [""])[0],
                    (form.get("server_media") or [""])[0],
                    (form.get("display") or [""])[0],
                )
                loc = "/settings"
            elif u == "/api/map-decide":
                feats = [x.strip() for x in ((form.get("features") or [""])[0]).split(",") if x.strip()]
                apply_mapping_decision(
                    DATA_DIR,
                    pid,
                    (form.get("mid") or [""])[0],
                    action=(form.get("action") or ["accept"])[0],
                    feature_ids=feats,
                )
                loc = f"/media?id={pid}"
            elif u == "/api/delete":
                mid = (form.get("mid") or [""])[0]
                out = service.delete_server_media(DATA_DIR, pid, [mid], force=False)
                if not out.get("ok"):
                    w = (out.get("warnings") or [{}])[0]
                    n = len(w.get("features") or [])
                    body = (
                        f"<p class='warn'>This image is linked to {n} features.</p>"
                        f"<form method='post' action='/api/delete-force'><input type='hidden' name='id' value='{_esc(pid)}'>"
                        f"<input type='hidden' name='mid' value='{_esc(mid)}'><button>Delete</button></form>"
                        f"<a href='/server?id={_esc(pid)}'>Cancel</a>"
                    )
                    self._page(body)
                    return
                loc = f"/server?id={pid}"
            elif u == "/api/delete-force":
                service.delete_server_media(DATA_DIR, pid, [(form.get("mid") or [""])[0]], force=True)
                loc = f"/server?id={pid}"
            elif u == "/api/keep":
                service.keep_server_media(DATA_DIR, pid, (form.get("mid") or [""])[0])
                loc = f"/server?id={pid}"
        except Exception as exc:  # noqa: BLE001
            self._page(f"<p class='warn'>{_esc(exc)}</p>")
            return
        self._redir(loc)


def run(host: str = HOST, port: int = PORT) -> None:
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"Catalog Manager http://{host}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
