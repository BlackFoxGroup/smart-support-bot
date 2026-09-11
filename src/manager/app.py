"""Smart Support Manager — local HTTP UI. No secrets in source or HTML logs."""

from __future__ import annotations

import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

from src.config import DATA_DIR, KNOWLEDGE_ROOT, PROJECT_ROOT
from src.knowledge.source_catalog import service
from src.knowledge.source_catalog.analyze import analyze_and_send, analyze_media, apply_mapping_decision
from src.knowledge.source_catalog.catalog_edit import (
    add_catalog_feature,
    catalog_feature_ids,
    catalog_media_list,
    delete_catalog_media,
    lang_text,
    read_catalog,
    return_catalog_media_to_index,
    save_catalog_texts,
    set_catalog_media_feature,
)
from src.knowledge.source_catalog.queue import (
    cancel_job,
    ingest_files,
    ingest_loose_files,
    load_upload_state,
    process_waiting,
    retry_job,
    send_mapped_media_to_catalog,
)
from src.knowledge.source_catalog.sftp_conn import (
    connect_session,
    disconnect_session,
    load_sftp_settings,
    save_sftp_settings,
    session_status,
)
from src.knowledge.source_catalog.media import is_remote_server_item
from src.knowledge.source_catalog.queue import visible_queue_jobs
from src.knowledge.source_catalog.store import load_global_queue
from src.manager.ai_store import load_ai_settings, save_ai_settings
from src.manager.i18n import LABELS, LANGS, load_saved_lang, save_lang, t

HOST = "127.0.0.1"
PORT = int(os.getenv("MANAGER_PORT") or "8765")
APP_NAME = (os.getenv("MANAGER_NAME") or "Smart Support Manager").strip()
NAV_KEYS = (
    ("/", "nav_dash"),
    ("/products", "nav_products"),
    ("/catalog", "nav_catalog"),
    ("/catalog-photos", "nav_cat_photos"),
    ("/media", "nav_media"),
    ("/queue", "nav_queue"),
    ("/history", "nav_history"),
    ("/settings", "nav_settings"),
)


def _human(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, dict):
        name = value.get("filename") or value.get("feature_id") or value.get("name")
        extra = value.get("feature_id") if name and name != value.get("feature_id") else None
        if name and extra:
            return f"{name} ({extra})"
        if name:
            return str(name)
        return ""
    if isinstance(value, (list, tuple, set)):
        parts = [_human(x) for x in value]
        return "، ".join(p for p in parts if p)
    return ""


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
    if "v2" in APP_NAME.lower() and "v2" not in title.lower():
        title = f"{title} v2"
    direction = "rtl" if lang == "fa" else "ltr"
    links = []
    qn = ""
    try:
        qn = str(len(visible_queue_jobs(load_global_queue(DATA_DIR))))
    except Exception:
        qn = ""
    for href, key in NAV_KEYS:
        label = t(lang, key)
        if key == "nav_queue" and qn:
            label = f"{label} ({qn})"
        links.append(f'<a href="{href}">{_esc(label)}</a>')
    links = " ".join(links)
    langs = " ".join(
        f'<a href="/set-lang?lang={code}" class="{"on" if code==lang else ""}">{_esc(LABELS[code])}</a>'
        for code in LANGS
    )
    live = (
        ""
        if pick
        else (
            "<div class='live' id='uplive' aria-live='polite'>"
            "<span class='dot' id='updot' hidden></span>"
            f"<span class='live-txt' id='uptxt' data-up='{_esc(t(lang,'uploading'))}'>{_esc(t(lang,'idle'))}</span></div>"
        )
    )
    nav = "" if pick else f"<nav><div class='nav-main'>{links}</div>{live}<div class='langbar'>{langs}</div></nav>"
    page = f"""<!DOCTYPE html>
<html lang="{_esc(lang)}" dir="{direction}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fira+Sans:wght@400;500;600;700&family=Fira+Code:wght@400;500&family=Vazirmatn:wght@400;600;700&family=Noto+Sans+SC:wght@400;600&display=swap" rel="stylesheet">
<style>
:root{{--bg:#0F172A;--fg:#F8FAFC;--card:#1B2336;--card-fg:#F8FAFC;--muted:#272F42;--muted-fg:#94A3B8;--accent:#22C55E;--on-accent:#0F172A;--primary:#1E293B;--on-primary:#FFFFFF;--secondary:#334155;--border:#475569;--ring:#FFFFFF;--nav:#0B1220;--space:8px;--danger:#EF4444;--header-h:64px}}
*{{box-sizing:border-box}}
html{{scroll-padding-top:var(--header-h)}}
body{{font-family:Fira Sans,Vazirmatn,Noto Sans SC,Segoe UI,sans-serif;margin:0;background:var(--bg);color:var(--fg);line-height:1.5;font-size:16px}}
code,kbd,.stat{{font-family:Fira Code,Vazirmatn,monospace}}
a,button,input[type=submit],label,select,summary{{cursor:pointer}}
a,button,input,select,textarea{{transition:background .2s ease,border-color .2s ease,color .2s ease,opacity .2s ease}}
nav{{display:flex;flex-wrap:wrap;gap:var(--space);justify-content:space-between;align-items:center;background:var(--nav);padding:8px 16px;position:sticky;top:0;z-index:2;min-height:var(--header-h);border-bottom:1px solid var(--border)}}
.nav-main{{display:flex;flex-wrap:wrap;gap:4px}}
nav a{{color:#E2E8F0;padding:8px 10px;min-height:44px;min-width:44px;display:inline-flex;align-items:center;text-decoration:none;border-radius:4px}}
nav a:hover{{background:var(--muted)}}
nav a:focus-visible,button:focus-visible,a.btn:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible{{outline:2px solid var(--ring);outline-offset:2px}}
.langbar a{{border:1px solid var(--border);justify-content:center}}
.langbar a.on{{background:var(--accent);color:var(--on-accent);font-weight:600}}
.live{{display:inline-flex;align-items:center;gap:8px;min-height:44px;color:var(--muted-fg);font-size:14px}}
.dot{{width:10px;height:10px;border-radius:50%;background:var(--accent);flex:0 0 10px;animation:flash .8s ease-in-out infinite}}
@keyframes flash{{50%{{opacity:.2}}}}
main{{padding:16px 20px;max-width:1280px;margin:0 auto;overflow-x:auto}}
h1{{font-size:1.25rem;font-weight:600;margin:0 0 16px;padding-bottom:10px;border-bottom:1px solid var(--border);letter-spacing:.02em}}
h2{{font-size:1rem;margin:0 0 8px;font-weight:600}}
h3{{font-size:.95rem;margin:0 0 8px;color:var(--muted-fg);font-weight:600}}
table{{border-collapse:collapse;width:100%;min-width:560px}}
td,th{{border-bottom:1px solid var(--border);padding:10px 8px;text-align:start;font-size:14px;vertical-align:middle}}
th{{color:var(--muted-fg);font-weight:600;background:var(--muted);position:sticky;top:0}}
.card{{background:var(--card);color:var(--card-fg);padding:16px;margin:0 0 12px;border-radius:4px;border:1px solid var(--border)}}
.form-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;margin:12px 0}}
.field{{display:flex;flex-direction:column;gap:4px}}
.field label{{color:var(--muted-fg);font-size:14px;font-weight:600}}
.field input,.field select,.field textarea{{width:100%;margin:0}}
.span2{{grid-column:1/-1}}
button,input[type=submit],a.btn{{background:var(--accent);color:var(--on-accent);border:0;padding:10px 14px;min-height:44px;text-decoration:none;display:inline-flex;align-items:center;justify-content:center;font:inherit;border-radius:4px;font-weight:600}}
button.ghost,a.ghost{{background:var(--secondary);color:var(--on-primary)}}
button:hover,a.btn:hover{{filter:brightness(1.06)}}
.toolbar{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:12px 0}}
.warn{{color:#FCA5A5}} .ok{{color:#86EFAC}} .stat{{color:var(--muted-fg);font-size:13px}}
.drop{{border:1px dashed var(--border);padding:16px;margin:12px 0;border-radius:4px;background:var(--primary)}}
img.th{{max-height:64px;border-radius:2px;border:1px solid var(--border)}}
input,select,textarea{{background:var(--primary);color:var(--fg);border:1px solid var(--border);padding:8px 10px;border-radius:4px;min-height:44px;font:inherit}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px}}
.pair-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;align-items:start}}
@media (max-width:900px){{.pair-grid{{grid-template-columns:1fr}}}}
.guide{{color:var(--fg);max-width:70ch}}
.guide ol{{margin:8px 0 0;padding-inline-start:1.3rem}}
.pick{{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin-top:24px}}
.pick a.btn{{min-width:140px;justify-content:center}}
.pick-copy{{text-align:center;color:var(--muted-fg)}}
.prodcard .form-grid{{margin-top:8px}}
.fullwrap{{min-height:100vh;margin:0;background:#000;display:flex;align-items:center;justify-content:center}}
.fullwrap img{{max-width:100%;max-height:100vh;object-fit:contain}}
.spin{{width:22px;height:22px;border:3px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:spin .7s linear infinite;display:inline-block}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
#batchbox[hidden]{{display:none}}
@media (max-width:768px){{main{{padding:12px}} .toolbar a.btn,.toolbar button{{flex:1 1 auto;justify-content:center}}}}
@media (prefers-reduced-motion:reduce){{.dot,.spin{{animation:none;opacity:1}} *{{transition:none!important}}}}
</style></head><body>
{nav}
<main>
{"<h1>"+_esc(title)+"</h1>" if not pick else ""}
{body}
</main>
{"" if pick else '''<script>
(function(){
const dot=document.getElementById('updot'); const txt=document.getElementById('uptxt');
if(!dot||!txt)return;
const idle=txt.textContent;
function tick(){
fetch('/upload-state').then(r=>r.json()).then(s=>{
dot.hidden=!s.busy;
txt.textContent=s.busy?((s.filename||'')+' — '+(txt.dataset.up||'')):idle;
}).catch(()=>{});
}
tick(); setInterval(tick,1500);
})();
</script>'''}
</body></html>"""
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
        out = service.build_ai_catalog(PROJECT_ROOT, KNOWLEDGE_ROOT, DATA_DIR, pid)
        if not out.get("ok"):
            err = str(out.get("error") or "catalog failed")
            return "", err if err.startswith("err_") else err
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
        return _cookie_lang(self.headers.get("Cookie")) or load_saved_lang(DATA_DIR)

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
            save_lang(DATA_DIR, code)
            self.send_response(303)
            self.send_header("Set-Cookie", f"ssm_lang={code}; Path=/; Max-Age=31536000")
            self.send_header("Location", "/")
            self.end_headers()
            return
        if not lang and path not in {"/thumb"}:
            picks = "".join(f'<a class="btn" href="/set-lang?lang={c}">{_esc(LABELS[c])}</a>' for c in LANGS)
            copies = "".join(f"<p class='pick-copy'>{_esc(t(c, 'choose_lang'))}</p>" for c in LANGS)
            self._send(
                _html(
                    f"{copies}<div class='pick'>{picks}</div>",
                    lang="en",
                    pick=True,
                    title="Language",
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
            if action == "catalog":
                loc = "/catalog"
            if err:
                if action == "catalog":
                    loc = f"/catalog?err={quote(err)}"
                else:
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
                    f"<p class='stat'>{_esc(t(lang,'catalog_ai'))}: {_esc(p['catalog_status'])}<br>"
                    f"{_esc(t(lang,'version'))}: {_esc(p['catalog_version'])}<br>"
                    f"{_esc(t(lang,'queue_n'))}: {_esc(dash.get('queue_count'))} · "
                    f"{_esc(t(lang,'media_n'))}: {_esc(p['images'])}<br>"
                    f"{_esc(t(lang,'synced'))}: {_esc(p['synced'])} · {_esc(t(lang,'pending'))}: {_esc(p['pending'])} · "
                    f"{_esc(t(lang,'failed'))}: {_esc(p['failed'])} · {_esc(t(lang,'unmapped'))}: {_esc(p['unmapped'])}<br>"
                    f"{_esc(t(lang,'server'))}: {_esc(p['server'])}</p></div>"
                )
            steps = t(lang, "guide_body")
            parts = [p.strip(" .") for p in re.split(r"[\d۰-۹]+\s*[\)\.]?\s*", steps) if p.strip()]
            lis = "".join(f"<li>{_esc(p)}</li>" for p in parts)
            guide = (
                f"<div class='card'><h2>{_esc(t(lang, 'guide_title'))}</h2>"
                f"<div class='guide'><ol>{lis}</ol></div></div>"
            )
            self._page(guide + "<div class='grid'>" + "".join(cards) + "</div>")
            return
        if path == "/products":
            if pid:
                self._product(pid, q)
                return
            flash = ""
            msg_key = (q.get("msg") or [""])[0]
            err_key = (q.get("err") or [""])[0]
            if msg_key:
                flash += f"<p class='ok'>{_esc(t(lang, msg_key) if msg_key.startswith('ok_') else msg_key)}</p>"
            if err_key:
                flash += f"<p class='warn'>{_esc(t(lang, err_key) if err_key.startswith('err_') else err_key)}</p>"
            map_cards = []
            for m in dash.get("maps") or []:
                src = "" if m.get("source") == "Missing" else (m.get("source") or "")
                imgs = "" if m.get("images") == "Missing" else (m.get("images") or "")
                st = t(lang, "registered") if m.get("registered") else t(lang, "unregistered")
                map_cards.append(
                    f"<div class='card prodcard'><h2>{_esc(m.get('display') or m.get('product_id'))}</h2>"
                    f"<p class='stat'>{_esc(st)}</p>"
                    f"<form method='post' action='/api/paths'>"
                    f"<input type='hidden' name='id' value='{_esc(m.get('product_id'))}'>"
                    "<div class='form-grid'>"
                    f"<div class='field'><label>{t(lang,'col_id')}</label><input value='{_esc(m.get('product_id'))}' disabled></div>"
                    f"<div class='field'><label for='d-{_esc(m.get('product_id'))}'>{t(lang,'display')}</label>"
                    f"<input id='d-{_esc(m.get('product_id'))}' name='display' value='{_esc(m.get('display'))}'></div>"
                    f"<div class='field span2'><label for='s-{_esc(m.get('product_id'))}'>{t(lang,'col_source')}</label>"
                    f"<input id='s-{_esc(m.get('product_id'))}' name='source' value='{_esc(src)}'></div>"
                    f"<div class='field span2'><label for='i-{_esc(m.get('product_id'))}'>{t(lang,'col_images')}</label>"
                    f"<input id='i-{_esc(m.get('product_id'))}' name='images' value='{_esc(imgs)}'></div>"
                    f"<div class='field span2'><label for='r-{_esc(m.get('product_id'))}'>{t(lang,'server')}</label>"
                    f"<input id='r-{_esc(m.get('product_id'))}' name='server_media' value='{_esc(m.get('server_media'))}'></div>"
                    f"</div><div class='toolbar'><button>{t(lang,'edit_row')}</button>"
                    f"<a class='btn ghost' href='/products?id={_esc(m.get('product_id'))}'>{_esc(t(lang,'open'))}</a></div></form></div>"
                )
            save_card = (
                f"<div class='card'><h2>{t(lang,'save_map')}</h2>"
                f"<form method='post' action='/api/paths'>"
                "<div class='form-grid'>"
                f"<div class='field'><label for='newid'>{t(lang,'col_id')}</label><input id='newid' name='id'></div>"
                f"<div class='field'><label for='newdisp'>{t(lang,'display')}</label><input id='newdisp' name='display'></div>"
                f"<div class='field span2'><label for='newsrc'>{t(lang,'col_source')}</label><input id='newsrc' name='source'></div>"
                f"<div class='field span2'><label for='newimg'>{t(lang,'col_images')}</label><input id='newimg' name='images'></div>"
                f"<div class='field span2'><label for='newsrv'>{t(lang,'server')}</label><input id='newsrv' name='server_media'></div>"
                f"</div><button>{t(lang,'save_map')}</button></form></div>"
            )
            self._page(
                flash
                + f"<div class='card'><h2>{_esc(t(lang,'path_map'))}</h2>"
                f"<p class='guide'>{_esc(t(lang,'source_help'))}</p></div>"
                + f"<div class='pair-grid'>{''.join(map_cards)}{save_card}</div>",
                t(lang, "nav_products"),
            )
            return
        if path == "/catalog":
            rows = []
            for p in dash["products"]:
                rows.append(
                    f"<tr><td>{_esc(p['product_id'])}</td><td>{_esc(p['catalog_status'])}</td>"
                    f"<td>v{_esc(p['catalog_version'])}</td>"
                    f"<td><a class='btn' href='/run/catalog?id={_esc(p['product_id'])}'>{_esc(t(lang,'build'))}</a></td></tr>"
                )
            flash = ""
            msg_key = (q.get("msg") or [""])[0]
            err_key = (q.get("err") or [""])[0]
            if msg_key:
                flash += f"<p class='ok'>{_esc(t(lang, msg_key) if msg_key.startswith('ok_') else msg_key)}</p>"
            if err_key:
                flash += f"<p class='warn'>{_esc(t(lang, err_key) if err_key.startswith('err_') else err_key)}</p>"
            pid = pid or (dash["products"][0]["product_id"] if dash["products"] else "")
            cat_opts = "".join(
                f"<option value='{_esc(p['product_id'])}' {'selected' if p['product_id']==pid else ''}>"
                f"{_esc(p.get('title') or p['product_id'])}</option>"
                for p in dash.get("products") or []
            )
            cat = read_catalog(KNOWLEDGE_ROOT, pid) if pid else {}
            feat_blocks = []
            for feat in cat.get("features") or []:
                if not isinstance(feat, dict) or not feat.get("id"):
                    continue
                fid = str(feat.get("id"))
                feat_blocks.append(
                    f"<div class='card'><h3>{_esc(fid)}</h3><div class='form-grid'>"
                    f"<input type='hidden' name='feat_id' value='{_esc(fid)}'>"
                    f"<div class='field span2'><label>{_esc(t(lang,'feat_title'))}</label>"
                    f"<input name='feat_title_{_esc(fid)}' value='{_esc(lang_text(feat.get('title'), lang))}'></div>"
                    f"<div class='field span2'><label>{_esc(t(lang,'feat_sum'))}</label>"
                    f"<textarea name='feat_sum_{_esc(fid)}' rows='3'>{_esc(lang_text(feat.get('summary'), lang))}</textarea></div>"
                    f"</div></div>"
                )
            texts = ""
            if pid:
                texts = (
                    f"<div class='card'><h2>{_esc(t(lang,'cat_texts'))}</h2>"
                    f"<form method='get' action='/catalog' class='toolbar'>"
                    f"<label>{_esc(t(lang,'target_catalog'))}</label>"
                    f"<select name='id' onchange='this.form.submit()'>{cat_opts}</select></form>"
                    f"<form method='post' action='/api/catalog-text'>"
                    f"<input type='hidden' name='id' value='{_esc(pid)}'>"
                    f"<div class='form-grid'>"
                    f"<div class='field span2'><label>{_esc(t(lang,'title_label'))}</label>"
                    f"<input name='title' value='{_esc(lang_text(cat.get('title'), lang))}'></div>"
                    f"<div class='field span2'><label>{_esc(t(lang,'short_sum'))}</label>"
                    f"<textarea name='short_summary' rows='4'>{_esc(lang_text(cat.get('short_summary'), lang))}</textarea></div>"
                    f"<div class='field span2'><label>{_esc(t(lang,'long_sum'))}</label>"
                    f"<textarea name='long_summary' rows='8'>{_esc(lang_text(cat.get('long_summary'), lang))}</textarea></div>"
                    f"</div>"
                    + "".join(feat_blocks)
                    + f"<button>{_esc(t(lang,'save'))}</button></form></div>"
                    + f"<div class='card'><h2>{_esc(t(lang,'add_feat'))}</h2>"
                    f"<form method='post' action='/api/catalog-feat-add'>"
                    f"<input type='hidden' name='id' value='{_esc(pid)}'>"
                    f"<div class='form-grid'>"
                    f"<div class='field'><label>{_esc(t(lang,'feat_id'))}</label>"
                    f"<input name='feat_id' required placeholder='overview'></div>"
                    f"<div class='field span2'><label>{_esc(t(lang,'feat_title'))}</label>"
                    f"<input name='feat_title' required></div>"
                    f"<div class='field span2'><label>{_esc(t(lang,'feat_sum'))}</label>"
                    f"<textarea name='feat_sum' rows='3'></textarea></div>"
                    f"</div><button>{_esc(t(lang,'add_feat'))}</button></form></div>"
                )
            self._page(
                flash
                + f"<p class='guide'>{_esc(t(lang,'catalog_help'))}</p><table>"
                + "".join(rows)
                + "</table>"
                + texts
            )
            return
        if path == "/catalog-photos":
            pid = pid or (dash["products"][0]["product_id"] if dash["products"] else "")
            self._catalog_photos(pid, q)
            return
        if path == "/cmedia":
            rel = (q.get("p") or [""])[0].replace("\\", "/").lstrip("/")
            file = (PROJECT_ROOT / rel).resolve() if rel.startswith("media/catalogs/") else None
            root = (PROJECT_ROOT / "media" / "catalogs").resolve()
            if file is None or not file.is_file():
                self._send(b"missing", 404, "text/plain")
                return
            try:
                file.relative_to(root)
            except ValueError:
                self._send(b"missing", 404, "text/plain")
                return
            mime = "image/jpeg" if file.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
            self._send(file.read_bytes(), 200, mime)
            return
        if path == "/media":
            pid = pid or (dash["products"][0]["product_id"] if dash["products"] else "")
            self._media(pid, q)
            return
        if path == "/queue":
            rows = []
            for job in visible_queue_jobs(load_global_queue(DATA_DIR)):
                thumb = (
                    f"<img class='th' src='/thumb?id={_esc(job.get('product_id'))}&mid={_esc(job.get('media_id'))}' alt=''>"
                    if job.get("media_id")
                    else ""
                )
                rows.append(
                    "<tr>"
                    f"<td>{thumb}</td>"
                    f"<td>{_esc(job.get('filename'))}</td><td>{_esc(job.get('product_id'))}</td>"
                    f"<td>{_esc(job.get('feature'))}</td><td>{_esc(job.get('size'))}</td>"
                    f"<td>{_esc(job.get('status'))}</td><td>{_esc(job.get('progress'))}%</td>"
                    f"<td>{_esc(job.get('speed'))}</td><td class='warn'>{_esc(job.get('error'))}</td>"
                    f"<td><form method='post' action='/api/retry'><input type='hidden' name='job' value='{_esc(job.get('job_id'))}'>"
                    f"<button>{_esc(t(lang,'retry'))}</button></form>"
                    f"<form method='post' action='/api/cancel'><input type='hidden' name='job' value='{_esc(job.get('job_id'))}'>"
                    f"<button>{_esc(t(lang,'cancel'))}</button></form></td></tr>"
                )
            opts = "".join(
                f"<option value='{_esc(p['product_id'])}'>{_esc(p.get('title') or p['product_id'])}</option>"
                for p in dash.get("products") or []
            )
            flash = ""
            msg_key = (q.get("msg") or [""])[0]
            err_key = (q.get("err") or [""])[0]
            if msg_key:
                flash += f"<p class='ok'>{_esc(t(lang, msg_key) if msg_key.startswith('ok_') else msg_key)}</p>"
            if err_key:
                flash += f"<p class='warn'>{_esc(t(lang, err_key) if err_key.startswith('err_') else err_key)}</p>"
            body = (
                flash
                + f"<p class='stat'>{_esc(t(lang,'queue_n'))}: {len(visible_queue_jobs(load_global_queue(DATA_DIR)))}</p>"
                f"<form method='post' action='/api/process-queue'><button>{_esc(t(lang,'process_queue'))}</button></form>"
                f"<div class='card drop'><h2>{_esc(t(lang,'loose_title'))}</h2>"
                f"<p class='guide'>{_esc(t(lang,'loose_help'))}</p>"
                f"<form method='post' action='/api/ingest-loose' enctype='multipart/form-data'>"
                f"<div class='form-grid'><div class='field'><label>{_esc(t(lang,'product'))}</label>"
                f"<select name='id' required><option value=''>{_esc(t(lang,'choose_product'))}</option>{opts}</select></div>"
                f"<div class='field span2'><label>{_esc(t(lang,'select_files'))}</label>"
                f"<input type='file' name='files' multiple accept='image/*' required></div></div>"
                f"<button>{_esc(t(lang,'loose_send'))}</button></form></div>"
                f"<table><tr><th></th><th>{_esc(t(lang,'filename'))}</th><th>{_esc(t(lang,'product'))}</th>"
                f"<th>{_esc(t(lang,'feature'))}</th><th>{_esc(t(lang,'size'))}</th>"
                f"<th>{_esc(t(lang,'col_status'))}</th><th>{_esc(t(lang,'progress'))}</th>"
                f"<th>{_esc(t(lang,'speed'))}</th><th>{_esc(t(lang,'error'))}</th><th></th></tr>"
                + "".join(rows)
                + "</table>"
            )
            self._page(body, t(lang, "nav_queue"))
            return
        if path == "/upload-state":
            st = load_upload_state(DATA_DIR)
            self._send(json.dumps(st).encode("utf-8"), 200, "application/json")
            return
        if path == "/server":
            self._redir("/media")
            return
        if path == "/history":
            pid = pid or (dash["products"][0]["product_id"] if dash["products"] else "")
            page = service.product_page(PROJECT_ROOT, KNOWLEDGE_ROOT, DATA_DIR, pid) if pid else {"history": []}
            hist = "".join(
                f"<li>{_esc(h.get('timestamp'))} {_esc(_human(h.get('action')))} {_esc(_human(h.get('result')))} {_esc(_human(h.get('error')))}</li>"
                for h in page.get("history") or []
            )
            self._page(f"<p>{_esc(t(lang,'product'))} {_esc(pid)}</p><ul>{hist}</ul>", t(lang, "nav_history"))
            return
        if path == "/settings":
            s = load_sftp_settings(DATA_DIR)
            flash = ""
            msg_key = (q.get("msg") or [""])[0]
            err_key = (q.get("err") or [""])[0]
            if msg_key:
                flash = f"<p class='ok'>{_esc(t(lang, msg_key))}</p>"
            if err_key:
                flash += f"<p class='warn'>{_esc(t(lang, err_key))}</p>"
            ai = load_ai_settings(PROJECT_ROOT, DATA_DIR)
            body = f"""
{flash}
<div class="card">
<h2>{t(lang, 'server_conn')}</h2>
<p class="stat">{t(lang,'pass_note')}</p>
<form method="post" action="/api/sftp">
<div class="form-grid">
<div class="field"><label for="host">{t(lang,'host')}</label><input id="host" name="host" value="{_esc(s['host'])}"></div>
<div class="field"><label for="port">{t(lang,'port')}</label><input id="port" name="port" value="{_esc(s['port'])}"></div>
<div class="field"><label for="username">{t(lang,'username')}</label><input id="username" name="username" value="{_esc(s['username'])}"></div>
<div class="field"><label for="auth_method">{t(lang,'auth')}</label>
<select id="auth_method" name="auth_method">
<option value="key" {"selected" if s["auth_method"]=="key" else ""}>{t(lang,'auth_key')}</option>
<option value="password" {"selected" if s["auth_method"]=="password" else ""}>{t(lang,'auth_pass')}</option>
</select></div>
<div class="field span2"><label for="key_path">{t(lang,'key_path')}</label><input id="key_path" name="key_path" value="{_esc(s['key_path'])}"></div>
<div class="field"><label for="password">{t(lang,'password')}</label><input id="password" type="password" name="password" autocomplete="new-password"></div>
<div class="field span2"><label for="key_pem">{t(lang,'key_pem')}</label><textarea id="key_pem" name="key_pem" rows="4"></textarea></div>
<div class="field span2"><label for="remote_media_path">{t(lang,'remote_path')}</label><input id="remote_media_path" name="remote_media_path" value="{_esc(s['remote_media_path'])}"></div>
</div>
<div class="toolbar"><button>{t(lang,'save')}</button></div>
</form>
<p class="stat">{t(lang,'conn_state')}: {_esc(t(lang,'connected') if session_status().get('connected') else t(lang,'disconnected'))} {_esc(session_status().get('host') or '')}</p>
<div class="toolbar">
<form method="post" action="/api/connect"><button>{t(lang,'connect')}</button></form>
<form method="post" action="/api/disconnect"><button class="ghost" type="submit">{t(lang,'disconnect')}</button></form>
</div>
</div>
<div class="card">
<h2>{t(lang,'ai_box')}</h2>
<p class="guide">{t(lang,'ai_note')}</p>
<form method="post" action="/api/ai">
<div class="form-grid">
<div class="field span2"><label for="base_url">{t(lang,'ai_url')}</label><input id="base_url" name="base_url" value="{_esc(ai['base_url'])}"></div>
<div class="field"><label for="model">{t(lang,'ai_model')}</label><input id="model" name="model" value="{_esc(ai['model'])}"></div>
<div class="field"><label for="api_key">{t(lang,'ai_key')}</label><input id="api_key" type="password" name="api_key" autocomplete="new-password"></div>
</div>
<button>{t(lang,'save')}</button>
</form>
</div>
"""
            self._page(body, t(lang, "nav_settings"))
            return
        if path == "/analyze":
            mid = (q.get("mid") or [""])[0]
            force = (q.get("fresh") or [""])[0] == "1"
            result = analyze_media(KNOWLEDGE_ROOT, DATA_DIR, pid, mid, force=force)
            cands = "".join(
                f"<li>{_esc(c.get('feature_id'))} — {_esc(c.get('percent'))}%"
                f"<form method='post' action='/api/map-decide'><input type='hidden' name='id' value='{_esc(pid)}'>"
                f"<input type='hidden' name='mid' value='{_esc(mid)}'><input type='hidden' name='action' value='change'>"
                f"<input type='hidden' name='features' value='{_esc(c.get('feature_id'))}'><button>{_esc(t(lang,'accept'))}</button></form></li>"
                for c in result.get("candidates") or []
            )
            src = "from_ai" if result.get("source") == "ai" else "from_name"
            review = t(lang, "need_review") if result.get("needs_review") else ""
            errk = str(result.get("ai_error") or "")
            err_line = f"<p class='warn'>{_esc(t(lang, errk))}</p>" if errk and result.get("source") != "ai" else ""
            vis = _human(result.get("visible_ui"))
            keys = _human(result.get("keywords"))
            body = f"""
<div class="card">
<p class="stat">{_esc(t(lang, src))}</p>
<p class="stat">{_esc(t(lang,'filename'))}: {_esc(result.get('filename'))}</p>
{err_line}
<div class="form-grid">
<div class="field span2"><label>{_esc(t(lang,'desc'))}</label><p>{_esc(result.get('description'))}</p></div>
<div class="field"><label>{_esc(t(lang,'screen'))}</label><p>{_esc(result.get('likely_screen'))}</p></div>
<div class="field"><label>{_esc(t(lang,'vis_ui'))}</label><p>{_esc(vis)}</p></div>
<div class="field"><label>{_esc(t(lang,'features'))}</label><p>{_esc(result.get('likely_feature'))}</p></div>
<div class="field"><label>{_esc(t(lang,'keywords'))}</label><p>{_esc(keys)}</p></div>
<div class="field"><label>{_esc(t(lang,'confidence'))}</label><p>{_esc(result.get('confidence'))} {_esc(review)}</p></div>
</div>
<p>{_esc(t(lang,'ai_class_only'))}</p>
<h3>{_esc(t(lang,'candidates'))}</h3><ul>{cands}</ul>
<form method="post" action="/api/map-decide">
<input type="hidden" name="id" value="{_esc(pid)}"><input type="hidden" name="mid" value="{_esc(mid)}">
<label>{_esc(t(lang,'features'))}</label> <input name="features">
<button name="action" value="accept">{_esc(t(lang,'accept'))}</button>
<button name="action" value="change">{_esc(t(lang,'change'))}</button>
<a class="btn ghost" href="/media?id={_esc(pid)}">{_esc(t(lang,'cancel'))}</a>
</form>
<p><a href="/analyze?id={_esc(pid)}&mid={_esc(mid)}&fresh=1">{_esc(t(lang,'analyze_again'))}</a></p>
</div>"""
            self._page(body, t(lang, "analyze"))
            return
        if path == "/view":
            mid = (q.get("mid") or [""])[0]
            html = (
                "<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>"
                f"<title>{_esc(mid)}</title><style>body{{margin:0;background:#000}}.fullwrap{{min-height:100vh;display:flex;align-items:center;justify-content:center}}"
                "img{{max-width:100%;max-height:100vh;object-fit:contain}}</style></head>"
                f"<body class='fullwrap'><img src='/thumb?id={_esc(pid)}&mid={_esc(mid)}' alt=''></body></html>"
            )
            self._send(html.encode("utf-8"))
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
<p>ID {_esc(pid)} {_esc(t(lang,'nav_catalog'))} {_esc(p.get('catalog_status'))} v{_esc(p.get('catalog_version'))}
{_esc(t(lang,'catalog_ai'))} {'ON' if p.get('catalog_enabled') else 'OFF'}</p>
<p>{_esc(t(lang,'col_source'))}: {_esc(p.get('source'))}<br>{_esc(t(lang,'col_images'))}: {_esc(p.get('pic_dir'))}<br>{_esc(t(lang,'server'))}: {_esc(p.get('server_media'))}</p>
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
<h3>{t(lang, 'select_files')}</h3>
<form method="post" action="/api/ingest" enctype="multipart/form-data" id="up">
<input type="hidden" name="id" value="{_esc(pid)}">
<input type="file" name="files" id="files" multiple accept="image/*">
{_esc(t(lang,'feature'))} <select name="feature"><option value=""></option>{feats}</select>
<button type="submit">{_esc(t(lang,'upload_selected'))}</button>
<button type="button" onclick="document.getElementById('files').value=''">{_esc(t(lang,'cancel'))}</button>
</form>
<div id="preview"></div>
</div>
<script>
const input=document.getElementById('files'); const box=document.getElementById('drop'); const prev=document.getElementById('preview');
function show(){{prev.innerHTML='';[...input.files].forEach((f,i)=>{{const d=document.createElement('div');
d.innerHTML='<b>'+f.name+'</b> '+(f.size/1024).toFixed(1)+' KB <button type=button data-i="'+i+'">{t(lang,'remove')}</button>';
if(f.type.startsWith('image/')){{const img=document.createElement('img');img.className='th';img.src=URL.createObjectURL(f);d.prepend(img);}}
prev.appendChild(d);}});prev.querySelectorAll('button').forEach(b=>b.onclick=()=>{{const dt=new DataTransfer();[...input.files].forEach((f,i)=>{{if(i!=+b.dataset.i)dt.items.add(f);}});input.files=dt.files;show();}});}}
input.onchange=show; ['dragover','drop'].forEach(ev=>box.addEventListener(ev,e=>{{e.preventDefault(); if(ev==='drop'){{input.files=e.dataTransfer.files;show();}}}}));
</script>
<p><a href="/media?id={_esc(pid)}">{_esc(t(lang,'nav_media'))}</a> · <a href="/queue">{_esc(t(lang,'nav_queue'))}</a></p>
"""
        self._page(body, pid)

    def _media(self, pid: str, q) -> None:
        lang = self._lang() or "en"
        page = service.product_page(PROJECT_ROOT, KNOWLEDGE_ROOT, DATA_DIR, pid)
        qtext = (q.get("q") or [""])[0].lower()
        feats = catalog_feature_ids(KNOWLEDGE_ROOT, pid) or [str(f) for f in (page.get("features") or []) if str(f).strip()]
        feat_opts = "".join(f"<option value='{_esc(f)}'>{_esc(f)}</option>" for f in feats)
        rows = []
        batch_ids = []
        for m in page.get("media") or []:
            if not is_remote_server_item(m):
                continue
            if qtext and qtext not in str(m.get("filename") or "").lower():
                continue
            if not m.get("catalog_path"):
                batch_ids.append(str(m.get("media_id") or ""))
            mapped = _human(m.get("feature_ids") or [])
            current = str((m.get("feature_ids") or [""])[0] if m.get("feature_ids") else m.get("catalog_feature_id") or "")
            opts = "".join(
                f"<option value='{_esc(f)}' {'selected' if f == current else ''}>{_esc(f)}</option>"
                for f in feats
            )
            send = (
                f"<form method='post' action='/api/to-catalog' class='toolbar'>"
                f"<input type='hidden' name='id' value='{_esc(pid)}'>"
                f"<input type='hidden' name='catalog' value='{_esc(pid)}'>"
                f"<input type='hidden' name='mid' value='{_esc(m.get('media_id'))}'>"
                f"<label class='stat'>{_esc(t(lang,'feature'))}</label>"
                f"<select name='feature' required><option value=''>{_esc(t(lang,'choose_feature'))}</option>{opts or feat_opts}</select>"
                f"<button>{_esc(t(lang,'send_catalog'))}</button></form>"
            )
            rows.append(
                "<tr>"
                f"<td><a href='/view?id={_esc(pid)}&mid={_esc(m.get('media_id'))}' target='_blank' rel='noopener'>"
                f"<img class='th' src='/thumb?id={_esc(pid)}&mid={_esc(m.get('media_id'))}' alt=''></a></td>"
                f"<td>{_esc(m.get('filename'))}</td><td>{_esc(m.get('status'))}</td>"
                f"<td>{_esc(mapped)}</td>"
                f"<td>{_esc(m.get('size'))}</td>"
                f"<td><a href='/analyze?id={_esc(pid)}&mid={_esc(m.get('media_id'))}'>{_esc(t(lang,'analyze'))}</a></td>"
                f"<td>{send}</td>"
                f"<td><form method='post' action='/api/delete'><input type='hidden' name='id' value='{_esc(pid)}'>"
                f"<input type='hidden' name='mid' value='{_esc(m.get('media_id'))}'><button>{_esc(t(lang,'delete'))}</button></form></td>"
                "</tr>"
            )
        cons = page.get("consistency") or {}
        flash = ""
        msg_key = (q.get("msg") or [""])[0]
        err_key = (q.get("err") or [""])[0]
        if msg_key:
            flash += f"<p class='ok'>{_esc(t(lang, msg_key) if msg_key.startswith('ok_') else msg_key)}</p>"
        if err_key:
            flash += f"<p class='warn'>{_esc(t(lang, err_key) if err_key.startswith('err_') else err_key)}</p>"
        mapped_n = cons.get("mapped") if not isinstance(cons.get("mapped"), (list, dict)) else 0
        media_n = cons.get("media") if not isinstance(cons.get("media"), (list, dict)) else 0
        unmapped = _human(cons.get("unmapped"))
        orphans = _human(cons.get("orphaned_media"))
        missing = _human(cons.get("missing_local"))
        cons_line = (
            f"<p class='stat'>{_esc(t(lang,'consistency'))}: {_esc(mapped_n)} / {_esc(media_n)}"
            f"{(' — ' + _esc(t(lang,'unmapped')) + ': ' + _esc(unmapped)) if unmapped else ''}"
            f"{(' — ' + _esc(t(lang,'orphaned')) + ': ' + _esc(orphans)) if orphans else ''}"
            f"{(' — ' + _esc(t(lang,'missing')) + ': ' + _esc(missing)) if missing else ''}</p>"
        )
        cat_opts = "".join(
            f"<option value='{_esc(p['product_id'])}' {'selected' if p['product_id']==pid else ''}>"
            f"{_esc(p.get('title') or p['product_id'])}</option>"
            for p in (service.dashboard(PROJECT_ROOT, KNOWLEDGE_ROOT, DATA_DIR).get("products") or [])
        )
        self._page(
                flash
                + f"<p class='guide'>{_esc(t(lang,'media_help'))}</p>"
                + cons_line
                + f"<form method='get' action='/media' class='toolbar'>"
                f"<label>{_esc(t(lang,'target_catalog'))}</label>"
                f"<select name='id' onchange='this.form.submit()'>{cat_opts}</select>"
                f"</form>"
                f"<div class='toolbar'><button type='button' id='batchbtn'>{_esc(t(lang,'batch_analyze'))}</button>"
                f"<span id='batchbox' hidden><span class='spin' aria-hidden='true'></span> "
                f"<span id='batchtxt'>{_esc(t(lang,'batch_wait'))}</span></span></div>"
                f"<script>window.BATCH={{pid:{json.dumps(pid)},ids:{json.dumps([x for x in batch_ids if x])},label:{json.dumps(t(lang,'batch_wait'))}}};"
                """(function(){const b=document.getElementById('batchbtn');const box=document.getElementById('batchbox');const txt=document.getElementById('batchtxt');
if(!b||!window.BATCH)return;b.onclick=async()=>{b.disabled=true;box.hidden=false;const ids=window.BATCH.ids||[];let ok=0;
for(let i=0;i<ids.length;i++){txt.textContent=(window.BATCH.label||'')+' '+(i+1)+'/'+ids.length;try{const fd=new FormData();fd.append('id',window.BATCH.pid);fd.append('mid',ids[i]);fd.append('catalog',window.BATCH.pid);const r=await fetch('/api/analyze-send',{method:'POST',body:fd});const j=await r.json();if(j.ok)ok++;}catch(e){}}
txt.textContent=ok+'/'+ids.length;location.href='/catalog-photos?id='+encodeURIComponent(window.BATCH.pid)+'&msg=ok_batch';};})();</script>"""
                f"<table><tr><th></th><th>{_esc(t(lang,'filename'))}</th><th>{_esc(t(lang,'col_status'))}</th>"
                f"<th>{_esc(t(lang,'features'))}</th><th>{_esc(t(lang,'size'))}</th>"
                f"<th>{_esc(t(lang,'analyze'))}</th><th>{_esc(t(lang,'send_catalog'))}</th><th></th></tr>"
                + "".join(rows)
                + "</table>",
                t(self._lang() or "en", "nav_media"),
            )

    def _catalog_photos(self, pid: str, q) -> None:
        lang = self._lang() or "en"
        dash = service.dashboard(PROJECT_ROOT, KNOWLEDGE_ROOT, DATA_DIR)
        cat_opts = "".join(
            f"<option value='{_esc(p['product_id'])}' {'selected' if p['product_id']==pid else ''}>"
            f"{_esc(p.get('title') or p['product_id'])}</option>"
            for p in dash.get("products") or []
        )
        feats = catalog_feature_ids(KNOWLEDGE_ROOT, pid)
        rows = []
        for m in catalog_media_list(KNOWLEDGE_ROOT, pid):
            current = str(m.get("feature") or "")
            opts = "".join(
                f"<option value='{_esc(f)}' {'selected' if f == current else ''}>{_esc(f)}</option>"
                for f in feats
            )
            rel = str(m.get("path") or "")
            rows.append(
                "<tr>"
                f"<td><a href='/cmedia?p={_esc(rel)}' target='_blank' rel='noopener'>"
                f"<img class='th' src='/cmedia?p={_esc(rel)}' alt=''></a></td>"
                f"<td>{_esc(m.get('filename'))}</td>"
                f"<td>{_esc(current)}</td>"
                f"<td><form method='post' action='/api/cat-feat' class='toolbar'>"
                f"<input type='hidden' name='id' value='{_esc(pid)}'>"
                f"<input type='hidden' name='path' value='{_esc(rel)}'>"
                f"<select name='feature' required><option value=''>{_esc(t(lang,'choose_feature'))}</option>{opts}</select>"
                f"<button>{_esc(t(lang,'save_feat'))}</button></form></td>"
                f"<td><form method='post' action='/api/cat-return'>"
                f"<input type='hidden' name='id' value='{_esc(pid)}'>"
                f"<input type='hidden' name='path' value='{_esc(rel)}'>"
                f"<button class='ghost'>{_esc(t(lang,'return_media'))}</button></form></td>"
                f"<td><form method='post' action='/api/cat-delete'>"
                f"<input type='hidden' name='id' value='{_esc(pid)}'>"
                f"<input type='hidden' name='path' value='{_esc(rel)}'>"
                f"<button>{_esc(t(lang,'del_server'))}</button></form></td>"
                "</tr>"
            )
        flash = ""
        msg_key = (q.get("msg") or [""])[0]
        err_key = (q.get("err") or [""])[0]
        if msg_key:
            flash += f"<p class='ok'>{_esc(t(lang, msg_key) if msg_key.startswith('ok_') else msg_key)}</p>"
        if err_key:
            flash += f"<p class='warn'>{_esc(t(lang, err_key) if err_key.startswith('err_') else err_key)}</p>"
        self._page(
            flash
            + f"<p class='guide'>{_esc(t(lang,'cat_photos_help'))}</p>"
            + f"<form method='get' action='/catalog-photos' class='toolbar'>"
            f"<label>{_esc(t(lang,'target_catalog'))}</label>"
            f"<select name='id' onchange='this.form.submit()'>{cat_opts}</select></form>"
            f"<table><tr><th></th><th>{_esc(t(lang,'filename'))}</th><th>{_esc(t(lang,'feature'))}</th>"
            f"<th>{_esc(t(lang,'save_feat'))}</th><th></th><th></th></tr>"
            + "".join(rows)
            + "</table>",
            t(lang, "nav_cat_photos"),
        )

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        form, files = _form(raw, self.headers)
        pid = (form.get("id") or [""])[0]
        lang = self._lang() or "en"
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
                    self._page(f"<p class='warn'>{_esc(t(lang,'source_missing'))}</p>")
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
                if not session_status().get("connected"):
                    loc = "/queue?err=err_offline"
                else:
                    process_waiting(PROJECT_ROOT, DATA_DIR)
                    loc = "/queue?msg=ok_queue"
            elif u == "/api/ingest-loose":
                result = ingest_loose_files(PROJECT_ROOT, DATA_DIR, pid, files)
                loc = "/queue"
                if not result.get("ok"):
                    loc = "/queue?err=err_loose"
                else:
                    process_waiting(PROJECT_ROOT, DATA_DIR)
                    loc = "/queue?msg=ok_loose"
            elif u == "/api/analyze-send":
                mid = (form.get("mid") or [""])[0]
                cat_id = (form.get("catalog") or [pid])[0]
                out = analyze_and_send(PROJECT_ROOT, KNOWLEDGE_ROOT, DATA_DIR, pid, mid, catalog_id=cat_id)
                self._send(json.dumps(out).encode("utf-8"), 200, "application/json")
                return
            elif u == "/api/to-catalog":
                feat = (form.get("feature") or [""])[0].strip()
                mid = (form.get("mid") or [""])[0]
                loc = f"/media?id={pid}"
                if not feat:
                    loc = f"/media?id={pid}&err=err_no_feature"
                else:
                    cat_id = (form.get("catalog") or [pid])[0]
                    out = send_mapped_media_to_catalog(
                        PROJECT_ROOT, KNOWLEDGE_ROOT, DATA_DIR, pid, mid, feat, catalog_id=cat_id
                    )
                    err = "err_no_file" if out.get("error") == "local file missing" else "err_catalog_send"
                    loc = f"/media?id={pid}&msg=ok_catalog_send" if out.get("ok") else f"/media?id={pid}&err={err}"
            elif u == "/api/catalog-text":
                feats = []
                for fid in form.get("feat_id") or []:
                    feats.append(
                        {
                            "id": fid,
                            "title": (form.get(f"feat_title_{fid}") or [""])[0],
                            "summary": (form.get(f"feat_sum_{fid}") or [""])[0],
                        }
                    )
                out = save_catalog_texts(
                    KNOWLEDGE_ROOT,
                    pid,
                    lang=lang,
                    title=(form.get("title") or [""])[0],
                    short_summary=(form.get("short_summary") or [""])[0],
                    long_summary=(form.get("long_summary") or [""])[0],
                    features=feats,
                )
                loc = f"/catalog?id={pid}&msg=ok_text" if out.get("ok") else f"/catalog?id={pid}&err=err_catalog_send"
            elif u == "/api/catalog-feat-add":
                out = add_catalog_feature(
                    KNOWLEDGE_ROOT,
                    pid,
                    feature_id=(form.get("feat_id") or [""])[0],
                    title=(form.get("feat_title") or [""])[0],
                    summary=(form.get("feat_sum") or [""])[0],
                    lang=lang,
                )
                loc = f"/catalog?id={pid}&msg=ok_feat_add" if out.get("ok") else f"/catalog?id={pid}&err=err_feat_add"
            elif u == "/api/cat-feat":
                rel = (form.get("path") or [""])[0]
                feat = (form.get("feature") or [""])[0]
                out = set_catalog_media_feature(KNOWLEDGE_ROOT, DATA_DIR, pid, rel, feat)
                loc = f"/catalog-photos?id={pid}&msg=ok_feat" if out.get("ok") else f"/catalog-photos?id={pid}&err=err_no_feature"
            elif u == "/api/cat-return":
                rel = (form.get("path") or [""])[0]
                return_catalog_media_to_index(KNOWLEDGE_ROOT, DATA_DIR, pid, rel)
                loc = f"/catalog-photos?id={pid}&msg=ok_return"
            elif u == "/api/cat-delete":
                rel = (form.get("path") or [""])[0]
                delete_catalog_media(PROJECT_ROOT, KNOWLEDGE_ROOT, DATA_DIR, pid, rel, from_server=True)
                loc = f"/catalog-photos?id={pid}&msg=ok_del_cat"
            elif u == "/api/retry":
                retry_job(DATA_DIR, (form.get("job") or [""])[0])
                if not session_status().get("connected"):
                    loc = "/queue?err=err_offline"
                else:
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
                    key_pem=(form.get("key_pem") or [""])[0] or None,
                )
                loc = "/settings?msg=saved_ok"
            elif u == "/api/ai":
                save_ai_settings(
                    PROJECT_ROOT,
                    DATA_DIR,
                    base_url=(form.get("base_url") or [""])[0],
                    model=(form.get("model") or [""])[0],
                    api_key=(form.get("api_key") or [""])[0] or None,
                )
                loc = "/settings?msg=saved_ok"
            elif u == "/api/connect":
                result = connect_session(DATA_DIR)
                loc = "/settings?msg=ok_connect" if result.get("ok") else "/settings?err=err_connect"
            elif u == "/api/disconnect":
                disconnect_session()
                loc = "/settings?msg=ok_disconnect"
            elif u == "/api/paths":
                service.save_product_paths(
                    DATA_DIR,
                    pid,
                    (form.get("source") or [""])[0],
                    (form.get("images") or [""])[0],
                    (form.get("server_media") or [""])[0],
                    (form.get("display") or [""])[0],
                )
                loc = "/products?msg=saved_ok"
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
                        f"<p class='warn'>{_esc(t(lang,'linked_n'))} ({n})</p>"
                        f"<form method='post' action='/api/delete-force'><input type='hidden' name='id' value='{_esc(pid)}'>"
                        f"<input type='hidden' name='mid' value='{_esc(mid)}'><button>{_esc(t(lang,'delete'))}</button></form>"
                        f"<a href='/media?id={_esc(pid)}'>{_esc(t(lang,'cancel'))}</a>"
                    )
                    self._page(body)
                    return
                loc = f"/media?id={pid}"
            elif u == "/api/delete-force":
                service.delete_server_media(DATA_DIR, pid, [(form.get("mid") or [""])[0]], force=True)
                loc = f"/media?id={pid}"
            elif u == "/api/keep":
                service.keep_server_media(DATA_DIR, pid, (form.get("mid") or [""])[0])
                loc = f"/media?id={pid}"
        except Exception as exc:  # noqa: BLE001
            self._page(f"<p class='warn'>{_esc(exc)}</p>")
            return
        self._redir(loc)


def run(host: str = HOST, port: int = PORT) -> None:
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"{APP_NAME} http://{host}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
