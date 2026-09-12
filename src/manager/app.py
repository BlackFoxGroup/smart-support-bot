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
    delete_all_catalog_media,
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
    publish_catalog_to_bot,
    push_catalog_json_to_bot,
    pull_remote_catalogs,
    save_sftp_settings,
    session_status,
    sync_remote_ai,
)
from src.knowledge.source_catalog.media import is_remote_server_item
from src.knowledge.source_catalog.queue import visible_queue_jobs
from src.knowledge.source_catalog.store import append_history, load_global_queue, read_all_history
from src.manager.ai_store import (
    load_ai_settings,
    save_ai_settings,
    set_ai_connection_state,
    test_ai_connection,
)
from src.manager.i18n import LABELS, LANGS, load_saved_lang, save_lang, t

HOST = "127.0.0.1"
PORT = int(os.getenv("MANAGER_PORT") or "8765")
APP_NAME = (os.getenv("MANAGER_NAME") or "Smart Support Manager").strip()
MANAGER_VERSION = (os.getenv("MANAGER_VERSION") or "2.1").strip()
BOT_VERSION = (os.getenv("BOT_VERSION") or "2.0").strip()
NAV_KEYS = (
    ("/", "nav_dash"),
    ("/products", "nav_products"),
    ("/catalog", "nav_catalog"),
    ("/catalog-photos", "nav_cat_photos"),
    ("/media", "nav_media"),
    ("/queue", "nav_queue"),
    ("/install", "nav_install"),
    ("/history", "nav_history"),
    ("/settings", "nav_settings"),
    ("/contact", "nav_contact"),
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


def _feat_posted(form: dict) -> tuple[str, str]:
    manual = str((form.get("feature_manual") or [""])[0] or "").strip()
    picked = str((form.get("feature") or [""])[0] or "").strip()
    return (manual or picked), manual


def _browse_local(raw: str) -> dict:
    import string

    text = (raw or "").strip()
    if not text:
        drives = [f"{d}:\\" for d in string.ascii_uppercase if Path(f"{d}:\\").exists()]
        return {"path": "", "parent": "", "dirs": drives, "files": []}
    cur = Path(text)
    if cur.is_file():
        cur = cur.parent
    if not cur.exists():
        return {"path": text, "parent": "", "dirs": [], "files": []}
    dirs = []
    files = []
    try:
        for child in sorted(cur.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
            if child.is_dir():
                dirs.append(str(child))
            else:
                files.append(str(child))
    except OSError:
        pass
    parent = str(cur.parent) if cur.parent != cur else ""
    return {"path": str(cur), "parent": parent, "dirs": dirs[:400], "files": files[:400]}


def _keys_list(lang: str, key: str) -> str:
    items = "".join(f"<li>{_esc(line.strip())}</li>" for line in t(lang, key).splitlines() if line.strip())
    return f"<ol class='guide keys'>{items}</ol>"


def _file_pick(name: str, iid: str, lang: str, *, multiple: bool = True, accept: str = "image/*", required: bool = False) -> str:
    multi = " multiple" if multiple else ""
    req = " required" if required else ""
    return (
        f"<label class='file-btn'>"
        f"<input class='sr-only' type='file' name='{name}' id='{iid}'{multi}{req} accept='{accept}'>"
        f"<span class='file-cta'>{_esc(t(lang, 'choose_files'))}</span>"
        f"<span class='file-name' data-empty='{_esc(t(lang, 'no_file'))}'>{_esc(t(lang, 'no_file'))}</span>"
        f"</label>"
    )


def _path_pick(name: str, value: str, iid: str, lang: str) -> str:
    return (
        f"<div class='path-pick'><input name='{name}' id='{iid}' value='{_esc(value)}' readonly>"
        f"<button type='button' class='browse-btn' data-for='{iid}'>{_esc(t(lang, 'choose_path'))}</button></div>"
    )


def _feat_fields(lang: str, mid: str, opts: str, current: str = "") -> str:
    return (
        f"<span class='feat-pair'>"
        f"<select name='feature' data-mid='{_esc(mid)}'>"
        f"<option value=''>{_esc(t(lang, 'choose_feature'))}</option>{opts}</select>"
        f"<input name='feature_manual' data-hint='{_esc(mid)}' value='{_esc(current)}' "
        f"placeholder='{_esc(t(lang, 'feat_manual'))}' autocomplete='off'>"
        f"</span>"
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
    server_connected = bool(session_status().get("connected"))
    ai_state = load_ai_settings(PROJECT_ROOT, DATA_DIR)
    ai_connected = bool(ai_state.get("connected"))
    bot_ai_connected = bool(server_connected and ai_connected and ai_state.get("bot_linked"))

    def _status_badge(label: str, connected: bool) -> str:
        state = t(lang, "connected") if connected else t(lang, "disconnected")
        css = "connected" if connected else "disconnected"
        return (
            f"<span class='conn-badge {css}' title='{_esc(label)}: {_esc(state)}'>"
            f"<span class='conn-dot' aria-hidden='true'></span>{_esc(label)}</span>"
        )

    connection_bar = (
        "<div class='connection-bar' aria-label='connection status'>"
        + _status_badge(t(lang, "status_server"), server_connected)
        + _status_badge(t(lang, "status_expert_ai"), ai_connected)
        + _status_badge(t(lang, "status_expert_bot_ai"), bot_ai_connected)
        + "</div>"
    )
    nav = "" if pick else f"<nav><div class='nav-main'>{links}</div>{connection_bar}{live}<div class='langbar'>{langs}</div></nav>"
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
a.ext{{color:#7DD3FC;text-decoration:underline}}
a.ext:hover,a.ext:focus-visible{{color:#BAE6FD}}
a,button,input,select,textarea{{transition:background .2s ease,border-color .2s ease,color .2s ease,opacity .2s ease}}
nav{{display:flex;flex-wrap:wrap;gap:var(--space);justify-content:space-between;align-items:center;background:var(--nav);padding:8px 16px;position:sticky;top:0;z-index:2;min-height:var(--header-h);border-bottom:1px solid var(--border)}}
.nav-main{{display:flex;flex-wrap:wrap;gap:4px}}
nav a{{color:#E2E8F0;padding:8px 10px;min-height:44px;min-width:44px;display:inline-flex;align-items:center;text-decoration:none;border-radius:4px}}
nav a:hover{{background:var(--muted)}}
nav a:focus-visible,button:focus-visible,a.btn:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible{{outline:2px solid var(--ring);outline-offset:2px}}
.langbar a{{border:1px solid var(--border);justify-content:center}}
.langbar a.on{{background:var(--accent);color:var(--on-accent);font-weight:600}}
.live{{display:inline-flex;align-items:center;gap:8px;min-height:44px;color:var(--muted-fg);font-size:14px}}
.connection-bar{{display:flex;align-items:center;gap:6px;flex-wrap:wrap}}
.conn-badge{{display:inline-flex;align-items:center;gap:5px;padding:4px 7px;border:1px solid var(--border);border-radius:999px;color:var(--muted-fg);font-size:11px;white-space:nowrap}}
.conn-dot{{width:8px;height:8px;border-radius:50%;background:var(--danger);box-shadow:0 0 0 2px #ef444426}}
.conn-badge.connected{{color:#BBF7D0;border-color:#166534}}
.conn-badge.connected .conn-dot{{background:var(--accent);box-shadow:0 0 0 2px #22c55e26}}
.catalog-state{{display:inline-flex;align-items:center;gap:6px;white-space:nowrap;color:#FCA5A5}}
.catalog-state.on{{color:#86EFAC}}
.catalog-state.on .conn-dot{{background:var(--accent)}}
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
.sr-only{{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);border:0}}
.file-btn{{display:inline-flex;align-items:center;gap:8px;flex-wrap:nowrap}}
.file-cta{{background:var(--accent);color:var(--on-accent);padding:8px 12px;min-height:36px;border-radius:4px;font-weight:600;display:inline-flex;align-items:center}}
.file-name{{color:var(--muted-fg);font-size:14px;min-width:15ch;max-width:28ch;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.upload-form{{display:flex;align-items:end;gap:10px;flex-wrap:nowrap}}
.upload-form .file-btn{{min-height:36px}}
.upload-feature{{display:flex;align-items:center;gap:6px;white-space:nowrap;color:var(--muted-fg);font-size:14px;font-weight:600}}
.upload-feature select{{width:180px;min-height:36px;padding:6px 10px;color:var(--fg);font-size:14px}}
.upload-form > button{{min-height:36px;padding:7px 12px}}
.guide.keys{{max-width:none;padding-inline-start:1.4rem;margin:8px 0 0}}
.guide.keys li{{margin:4px 0}}
button.ghost,a.ghost{{background:var(--secondary);color:var(--on-primary)}}
button.danger,a.danger{{background:var(--danger);color:#fff}}
button:hover,a.btn:hover{{filter:brightness(1.06)}}
.toolbar{{display:flex;flex-wrap:nowrap;gap:8px;align-items:center;margin:12px 0}}
.media-bar{{display:flex;align-items:center;justify-content:space-between;gap:16px;width:100%;box-sizing:border-box;margin:16px 0;padding-inline:24px}}
.media-bar form,.media-bar .bar-act{{margin:0;display:flex;align-items:center;gap:8px;flex:1 1 auto}}
.media-bar .bar-act{{justify-content:flex-end}}
.row-ops{{display:flex;flex-wrap:nowrap;align-items:center;gap:8px}}
.feat-pair{{display:inline-flex;flex:0 0 auto;flex-wrap:nowrap;align-items:center;gap:8px}}
.feat-pair select{{width:118px;flex:0 0 118px}}
.feat-pair input{{width:104px;flex:0 0 104px}}
.feat-pair select,.feat-pair input{{min-height:32px;padding:4px 8px;font-size:13px}}
.path-pick{{display:flex;gap:8px;align-items:center;width:100%}}
.path-pick input{{flex:1}}
.media-row{{display:grid;grid-template-columns:18px 44px minmax(140px,1fr) 110px 334px max-content;gap:8px;align-items:center;padding:6px 8px;border-bottom:1px solid var(--border);min-width:940px}}
.media-row.catalog-row{{grid-template-columns:18px 44px minmax(180px,260px) minmax(150px,1fr) 334px max-content}}
.media-row.queue-row{{grid-template-columns:18px 44px minmax(160px,1fr) 110px 90px 64px max-content;min-width:820px}}
.media-row > span,.media-row .name{{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.media-row .name{{font-size:12px;line-height:1.35}}
.media-row .feature-current{{overflow:visible;text-overflow:clip;font-size:12px}}
.media-row img.th{{max-height:36px;max-width:44px;width:44px;height:36px;object-fit:cover;display:block}}
.media-row input[type=checkbox]{{width:15px;height:15px;min-height:0;padding:0;margin:0;accent-color:var(--accent)}}
.media-row button,.media-row a.btn{{min-height:32px;min-width:auto;padding:5px 9px;font-size:12px;white-space:nowrap}}
.media-row > form.row-ops > button{{width:96px;flex:0 0 96px}}
.media-head{{color:var(--muted-fg);font-weight:600;background:var(--muted);font-size:12px}}
.feature-head{{display:grid!important;grid-template-columns:118px 104px 96px;gap:8px;align-items:center;overflow:visible!important}}
.feature-head span{{text-align:center;white-space:nowrap}}
#lightbox{{display:none;position:fixed;inset:0;background:#000c;z-index:60;align-items:center;justify-content:center;padding:24px}}
#lightbox.on{{display:flex!important}}
#lightbox img{{max-width:52vw;max-height:58vh;object-fit:contain;box-shadow:0 8px 40px #0008}}
#lightbox .x{{position:absolute;top:12px;inset-inline-end:12px;min-height:36px;min-width:36px;background:var(--danger);color:#fff}}
#lightbox .x:focus{{outline:2px solid var(--ring);outline-offset:2px}}
#browser{{display:none;position:fixed;inset:0;background:#000a;z-index:40;align-items:center;justify-content:center}}
#browser.on{{display:flex}}
#browser .box{{background:var(--card);width:min(760px,94vw);max-height:80vh;overflow:auto;padding:16px;border-radius:8px;border:1px solid var(--border)}}
#browser .item{{display:block;width:100%;text-align:start;background:transparent;color:var(--fg);margin:4px 0}}
#toast{{display:none;position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:var(--card);border:1px solid var(--border);padding:10px 16px;z-index:50;border-radius:4px}}
#toast.on{{display:block}}
.warn{{color:#FCA5A5}} .ok{{color:#86EFAC}} .stat{{color:var(--muted-fg);font-size:13px}}
.drop{{border:1px dashed var(--border);padding:16px;margin:12px 0;border-radius:4px;background:var(--primary)}}
img.th{{max-height:64px;border-radius:2px;border:1px solid var(--border)}}
input,select,textarea{{background:var(--primary);color:var(--fg);border:1px solid var(--border);padding:8px 10px;border-radius:4px;min-height:44px;font:inherit}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px}}
.pair-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;align-items:start}}
.stack{{display:flex;flex-direction:column;gap:12px}}
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
@media (max-width:768px){{main{{padding:12px}} .toolbar a.btn,.toolbar button{{flex:1 1 auto;justify-content:center}} .upload-form{{align-items:stretch;flex-wrap:wrap}}}}
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
function toast(m,ok){const el=document.getElementById('toast');if(!el)return;el.textContent=m;el.className=ok?'on ok':'on warn';setTimeout(()=>el.className='',2500);}
document.querySelectorAll('form.busy-form').forEach(form=>form.addEventListener('submit',()=>{
  const button=form.querySelector('button[type=submit]');if(!button)return;
  button.disabled=true;button.setAttribute('aria-busy','true');button.textContent=button.dataset.wait||'...';
}));
document.querySelectorAll('.send-one').forEach(btn=>btn.addEventListener('click',async()=>{
  if(btn.disabled)return;
  const form=btn.closest('form');if(!form)return;
  const old=btn.textContent;
  btn.disabled=true;btn.setAttribute('aria-busy','true');btn.textContent=btn.dataset.wait||'...';
  toast(btn.dataset.wait||'...',true);
  try{
    const response=await fetch('/api/to-catalog',{method:'POST',body:new FormData(form),headers:{'X-Stay':'1'}});
    if(!response.ok)throw new Error('HTTP '+response.status);
    const result=await response.json();
    toast(result.msg||(result.ok?'ok':'err'),!!result.ok);
    if(result.ok){const row=btn.closest('.media-row');if(row)row.remove();}
  }catch(error){
    toast(btn.dataset.fail||'fail',false);
  }finally{
    btn.disabled=false;btn.removeAttribute('aria-busy');btn.textContent=old;
  }
}));
let browseTarget=null;
document.querySelectorAll('.browse-btn').forEach(b=>b.addEventListener('click',()=>{browseTarget=b.getAttribute('data-for');openBrowse('');}));
async function openBrowse(p){const box=document.getElementById('browser');if(!box)return;box.className='on';const r=await fetch('/api/browse?path='+encodeURIComponent(p||''));const j=await r.json();const list=(j.dirs||[]).map(d=>'<button type=button class=item data-dir="'+d.replace(/"/g,'')+'">'+d+'</button>').join('')+(j.files||[]).map(f=>'<button type=button class=item data-file="'+f.replace(/"/g,'')+'">'+f+'</button>').join('');
box.innerHTML='<div class=box><p>'+(j.path||'')+'</p><div class=row-ops><button type=button id=bup>..</button><button type=button id=buse data-use="1">OK</button><button type=button id=bclose>X</button></div>'+list+'</div>';
box.querySelectorAll('[data-dir]').forEach(x=>x.onclick=()=>openBrowse(x.getAttribute('data-dir')));
box.querySelectorAll('[data-file]').forEach(x=>x.onclick=()=>{const el=document.getElementById(browseTarget);if(el)el.value=x.getAttribute('data-file');box.className='';});
const up=document.getElementById('bup');if(up)up.onclick=()=>openBrowse(j.parent||'');
const use=document.getElementById('buse');if(use)use.onclick=()=>{const el=document.getElementById(browseTarget);if(el)el.value=j.path||'';box.className='';};
const cl=document.getElementById('bclose');if(cl)cl.onclick=()=>box.className='';
}
document.querySelectorAll('.file-btn input').forEach(inp=>{
  const name=inp.parentElement.querySelector('.file-name');
  if(!name)return;
  const empty=name.getAttribute('data-empty')||'';
  inp.addEventListener('change',()=>{
    const n=inp.files.length;
    name.textContent=n===0?empty:(n===1?inp.files[0].name:(String(n)+' / '+empty));
    const form=inp.closest('form');
    if(form&&form.classList.contains('auto-queue')&&n){
      const sel=form.querySelector('select[name=id]');
      if(sel&&!sel.value){const o=[...sel.options].find(x=>x.value);if(o)sel.value=o.value;}
      if(form.requestSubmit)form.requestSubmit();else form.submit();
    }
  });
});
const lb=document.getElementById('lightbox');
const lbimg=document.getElementById('lbimg');
function closeLb(){if(!lb)return;lb.classList.remove('on');lb.hidden=true;if(lbimg)lbimg.removeAttribute('src');}
function openLb(src){if(!lb||!lbimg)return;lbimg.src=src;lb.hidden=false;lb.classList.add('on');const x=document.getElementById('lbx');if(x)x.focus();}
if(lb){lb.addEventListener('click',e=>{if(e.target!==lbimg)closeLb();});}
const lbx=document.getElementById('lbx');if(lbx)lbx.addEventListener('click',closeLb);
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeLb();});
document.addEventListener('click',e=>{
  const link=e.target.closest&&e.target.closest('a.zoom');
  if(!link)return;
  e.preventDefault();openLb(link.getAttribute('href'));
});
</script>'''}
<div id="browser"></div><div id="toast"></div>
<div id="lightbox" role="dialog" aria-modal="true" hidden>
<button type="button" class="x" id="lbx" aria-label="close">×</button>
<img id="lbimg" alt="">
</div>
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
        if path == "/api/browse":
            self._send(json.dumps(_browse_local((q.get("path") or [""])[0])).encode("utf-8"), 200, "application/json")
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
        if path in {"/catalog", "/catalog-photos", "/media"} and session_status().get("connected"):
            pull_remote_catalogs(DATA_DIR, KNOWLEDGE_ROOT)
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
                    f"{_path_pick('source', src, 's-'+str(m.get('product_id')), lang)}</div>"
                    f"<div class='field span2'><label for='i-{_esc(m.get('product_id'))}'>{t(lang,'col_images')}</label>"
                    f"{_path_pick('images', imgs, 'i-'+str(m.get('product_id')), lang)}</div>"
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
                f"<div class='field span2'><label for='newsrc'>{t(lang,'col_source')}</label>{_path_pick('source','','newsrc',lang)}</div>"
                f"<div class='field span2'><label for='newimg'>{t(lang,'col_images')}</label>{_path_pick('images','','newimg',lang)}</div>"
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
                catalog_on = bool(p.get("catalog_enabled"))
                state_label = t(lang, "catalog_in_use") if catalog_on else t(lang, "catalog_not_in_use")
                rows.append(
                    f"<tr><td>{_esc(p['product_id'])}</td><td>{_esc(p['catalog_status'])}</td>"
                    f"<td>v{_esc(p['catalog_version'])}</td><td><span class='catalog-state {'on' if catalog_on else 'off'}'>"
                    f"<span class='conn-dot' aria-hidden='true'></span>{_esc(state_label)}</span></td>"
                    f"<td><div class='row-ops'>"
                    f"<form class='busy-form' method='post' action='/api/catalog-build'><input type='hidden' name='id' value='{_esc(p['product_id'])}'>"
                    f"<button type='submit' data-wait='{_esc(t(lang,'building_catalog'))}' {'disabled' if not session_status().get('connected') else ''}>{_esc(t(lang,'build'))}</button></form>"
                    f"<form class='busy-form' method='post' action='/api/catalog-publish'><input type='hidden' name='id' value='{_esc(p['product_id'])}'>"
                    f"<button type='submit' data-wait='{_esc(t(lang,'publishing_catalog'))}' {'disabled' if not session_status().get('connected') else ''}>{_esc(t(lang,'publish_catalog'))}</button></form>"
                    f"<form class='busy-form' method='post' action='/api/catalog-disable'><input type='hidden' name='id' value='{_esc(p['product_id'])}'>"
                    f"<button class='danger' type='submit' data-wait='{_esc(t(lang,'disconnecting_catalog'))}' {'disabled' if not session_status().get('connected') or not catalog_on else ''}>{_esc(t(lang,'disable_catalog'))}</button></form>"
                    f"</div></td></tr>"
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
                jid = str(job.get("job_id") or "")
                qpid = str(job.get("product_id") or "")
                qmid = str(job.get("media_id") or "")
                thumb = (
                    f"<a class='zoom' href='/thumb?id={_esc(qpid)}&mid={_esc(qmid)}'>"
                    f"<img class='th' src='/thumb?id={_esc(qpid)}&mid={_esc(qmid)}' alt=''></a>"
                    if qmid
                    else "<span></span>"
                )
                rows.append(
                    "<div class='media-row queue-row'>"
                    f"<input type='checkbox' name='pick' value='{_esc(jid)}'>"
                    f"{thumb}"
                    f"<span class='name' title='{_esc(job.get('filename'))}'>{_esc(job.get('filename'))}</span>"
                    f"<span>{_esc(qpid)}</span>"
                    f"<span>{_esc(job.get('status'))}</span>"
                    f"<span>{_esc(job.get('progress'))}%</span>"
                    f"<span class='row-ops'>"
                    f"<form method='post' action='/api/retry' class='row-ops'><input type='hidden' name='job' value='{_esc(jid)}'>"
                    f"<button>{_esc(t(lang,'retry'))}</button></form>"
                    f"<form method='post' action='/api/cancel' class='row-ops'><input type='hidden' name='job' value='{_esc(jid)}'>"
                    f"<button class='danger'>{_esc(t(lang,'delete'))}</button></form></span>"
                    "</div>"
                )
            products = dash.get("products") or []
            first = str((products[0] or {}).get("product_id") or "") if products else ""
            opts = "".join(
                f"<option value='{_esc(p['product_id'])}' {'selected' if p['product_id']==first else ''}>"
                f"{_esc(p.get('title') or p['product_id'])}</option>"
                for p in products
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
                + f"<p class='guide'>{_esc(t(lang,'loose_auto'))}</p>"
                + f"<div class='media-bar'><p class='stat'>{_esc(t(lang,'queue_n'))}: {len(visible_queue_jobs(load_global_queue(DATA_DIR)))}</p>"
                f"<form method='post' action='/api/process-queue' class='bar-act'><button>{_esc(t(lang,'process_queue'))}</button></form></div>"
                f"<div class='card drop'><h2>{_esc(t(lang,'loose_title'))}</h2>"
                f"<form method='post' action='/api/ingest-loose' enctype='multipart/form-data' class='auto-queue'>"
                f"<div class='form-grid'><div class='field'><label>{_esc(t(lang,'product'))}</label>"
                f"<select name='id' required><option value=''>{_esc(t(lang,'choose_product'))}</option>{opts}</select></div>"
                f"<div class='field span2'><label>{_esc(t(lang,'select_files'))}</label>"
                f"{_file_pick('files', 'loose-files', lang, required=True)}</div></div></form></div>"
                f"<div class='media-row media-head queue-row'><input type='checkbox' onclick='document.querySelectorAll(\"input[name=pick]\").forEach(c=>c.checked=this.checked)'>"
                f"<span></span><span>{_esc(t(lang,'filename'))}</span><span>{_esc(t(lang,'product'))}</span>"
                f"<span>{_esc(t(lang,'col_status'))}</span><span>{_esc(t(lang,'progress'))}</span><span></span></div>"
                + "".join(rows)
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
            rows = []
            for h in read_all_history(DATA_DIR):
                obj = h.get("filename") or h.get("object") or ""
                rows.append(
                    f"<tr><td>{_esc(h.get('timestamp'))}</td><td>{_esc(_human(obj))}</td>"
                    f"<td>{_esc(_human(h.get('action')))}</td><td>{_esc(_human(h.get('source_section')))}</td>"
                    f"<td>{_esc(h.get('product_id'))}</td><td>{_esc(_human(h.get('server')))}</td>"
                    f"<td>{_esc(_human(h.get('result')) or _human(h.get('error')))}</td></tr>"
                )
            self._page(
                f"<table><tr><th>{_esc(t(lang,'history_time'))}</th><th>{_esc(t(lang,'history_object'))}</th>"
                f"<th>{_esc(t(lang,'history_action'))}</th><th>{_esc(t(lang,'history_section'))}</th>"
                f"<th>{_esc(t(lang,'product'))}</th><th>{_esc(t(lang,'server'))}</th>"
                f"<th>{_esc(t(lang,'col_status'))}</th></tr>{''.join(rows)}</table>",
                t(lang, "nav_history"),
            )
            return
        if path == "/contact":
            install_cmd = (
                "curl -fsSL https://raw.githubusercontent.com/BlackFoxGroup/"
                "smart-support-bot/main/deploy/install-manager.sh | sudo bash"
            )
            tunnel_cmd = "ssh -L 8766:127.0.0.1:8766 USER@SERVER"
            body = f"""
<div class="card">
<h2>{_esc(t(lang,'nav_contact'))}</h2>
<div class="form-grid">
<div class="field"><label>{_esc(t(lang,'website'))}</label><a class="ext" href="https://foxnex.net" target="_blank" rel="noopener">foxnex.net</a></div>
<div class="field"><label>{_esc(t(lang,'github_project'))}</label><a class="ext" href="https://github.com/BlackFoxGroup/smart-support-bot" target="_blank" rel="noopener">BlackFoxGroup/smart-support-bot</a></div>
<div class="field"><label>{_esc(t(lang,'expert_name'))}</label><span>Smart Support Manager</span></div>
<div class="field"><label>{_esc(t(lang,'bot_name'))}</label><span>Smart Support Bot</span></div>
<div class="field"><label>{_esc(t(lang,'expert_version'))}</label><span>{_esc(MANAGER_VERSION)}</span></div>
<div class="field"><label>{_esc(t(lang,'bot_version'))}</label><span>{_esc(BOT_VERSION)}</span></div>
<div class="field"><label>{_esc(t(lang,'creator'))}</label><span>Black Fox Group</span></div>
</div>
</div>
<div class="card">
<h2>{_esc(t(lang,'linux_install'))}</h2><p><code>{_esc(install_cmd)}</code></p>
<h3>{_esc(t(lang,'ssh_tunnel'))}</h3><p><code>{_esc(tunnel_cmd)}</code></p>
</div>
"""
            self._page(body, t(lang, "nav_contact"))
            return
        if path == "/install":
            flash = ""
            msg_key = (q.get("msg") or [""])[0]
            err_key = (q.get("err") or [""])[0]
            if msg_key:
                flash = f"<p class='ok'>{_esc(t(lang, msg_key))}</p>"
            if err_key:
                flash += f"<p class='warn'>{_esc(t(lang, err_key))}</p>"
            body = f"""
{flash}
<div class="card">
<h2>{_esc(t(lang,'nav_install'))}</h2>
<p class="guide">{_esc(t(lang,'install_help'))}</p>
<form method="post" action="/api/install-bot">
<div class="form-grid">
<div class="field span2"><label>{_esc(t(lang,'install_local'))}</label>{_path_pick('local_path','','local_path',lang)}</div>
<div class="field"><label>{_esc(t(lang,'host'))}</label><input name="host" required></div>
<div class="field"><label>{_esc(t(lang,'port'))}</label><input name="port" value="22"></div>
<div class="field"><label>{_esc(t(lang,'username'))}</label><input name="username" value="root" required></div>
<div class="field"><label>{_esc(t(lang,'password'))}</label><input name="password" type="password"></div>
<div class="field span2"><label>{_esc(t(lang,'install_ssh_key'))}</label><textarea name="ssh_key" rows="4"></textarea></div>
<div class="field span2"><label>{_esc(t(lang,'install_remote'))}</label><input name="remote_dir" value="/opt/smart-support" required></div>
<div class="field"><label>{_esc(t(lang,'install_service'))}</label><input name="service_name" value="smart-support-bot" required></div>
<div class="field"><label>{_esc(t(lang,'install_label'))}</label><input name="bot_label" value="Telegram bot"></div>
<div class="field"><label>{_esc(t(lang,'install_token'))}</label><input name="bot_token" type="password" required></div>
<div class="field span2"><label>{_esc(t(lang,'install_start'))}</label><input name="start_cmd" value="python3 -m src.main" required></div>
<div class="field span2"><label>{_esc(t(lang,'install_extra_env'))}</label><textarea name="extra_env" rows="4" placeholder="ADMIN_IDS=123&#10;TZ=UTC"></textarea></div>
<div class="field span2"><label>{_esc(t(lang,'install_extra_pip'))}</label><input name="extra_pip" placeholder="aiogram python-dotenv"></div>
</div>
<button type="submit">{_esc(t(lang,'install_run'))}</button>
</form>
</div>
"""
            self._page(body, t(lang, "nav_install"))
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
<div class="pair-grid">
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
<div class="field"><label for="password">{t(lang,'password')}</label><input id="password" type="password" name="password" autocomplete="new-password" placeholder="{"••••••••" if s["has_password"] else ""}"></div>
<div class="field span2"><label for="key_pem">{t(lang,'key_pem')}</label><textarea id="key_pem" name="key_pem" rows="4"></textarea></div>
</div>
<div class="toolbar"><button>{t(lang,'save')}</button></div>
</form>
<p class="stat">{t(lang,'conn_state')}: {_esc(t(lang,'connected') if session_status().get('connected') else t(lang,'disconnected'))} {_esc(session_status().get('host') or '')}</p>
<div class="toolbar">
<form method="post" action="/api/connect"><button>{t(lang,'connect')}</button></form>
<form method="post" action="/api/disconnect"><button class="danger" type="submit">{t(lang,'disconnect')}</button></form>
</div>
</div>
<div class="stack">
<div class="card">
<h2>{t(lang,'ai_box')}</h2>
<p class="stat">{_esc(t(lang,'conn_state'))}: <strong class="{'ok' if ai.get('connected') else 'warn'}">{_esc(t(lang,'connected') if ai.get('connected') else t(lang,'disconnected'))}</strong></p>
<p class="guide">{t(lang,'ai_note')}</p>
<form method="post" action="/api/ai">
<div class="form-grid">
<div class="field span2"><label for="base_url">{t(lang,'ai_url')}</label><input id="base_url" name="base_url" value="{_esc(ai['base_url'])}"></div>
<div class="field"><label for="model">{t(lang,'ai_model')}</label><input id="model" name="model" value="{_esc(ai['model'])}"></div>
<div class="field"><label for="api_key">{t(lang,'ai_key')}</label><input id="api_key" type="password" name="api_key" autocomplete="new-password" placeholder="{_esc(ai['key_mask'])}"></div>
</div>
<button>{t(lang,'save')}</button>
</form>
<div class="toolbar">
<form method="post" action="/api/ai-connect"><button type="submit">{_esc(t(lang,'ai_connect'))}</button></form>
<form method="post" action="/api/ai-disconnect"><button type="submit" class="danger">{_esc(t(lang,'ai_disconnect'))}</button></form>
</div>
</div>
<div class="card">
<h2>{_esc(t(lang,'expert_link_card'))}</h2>
<p class="guide">{_esc(t(lang,'link_bot_ai_note'))}</p>
<form method="post" action="/api/sftp">
<div class="form-grid">
<div class="field span2"><label for="remote_bot_root">{t(lang,'remote_bot_root')}</label><input id="remote_bot_root" name="remote_bot_root" value="{_esc(s['remote_bot_root'])}"></div>
<div class="field span2"><label for="remote_media_path">{t(lang,'remote_path')}</label><input id="remote_media_path" name="remote_media_path" value="{_esc(s['remote_media_path'])}"></div>
</div>
<div class="toolbar"><button>{t(lang,'save')}</button></div>
</form>
<form method="post" action="/api/link-bot-ai">
<button type="submit" {"disabled" if not session_status().get("connected") or not ai.get("connected") else ""}>{_esc(t(lang,'link_bot_ai'))}</button>
</form>
</div>
</div>
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
{_keys_list(lang, 'keys_help')}
</div>
<div class="card drop" id="drop">
<h3>{t(lang, 'select_files')}</h3>
<form method="post" action="/api/ingest" enctype="multipart/form-data" id="up" class="upload-form">
<input type="hidden" name="id" value="{_esc(pid)}">
{_file_pick('files', 'files', lang)}
<label class="upload-feature"><span>{_esc(t(lang,'feature'))}</span>
<select name="feature"><option value="">{_esc(t(lang,'choose_feature'))}</option>{feats}</select></label>
<button type="submit">{_esc(t(lang,'upload_selected'))}</button>
<button type="button" onclick="const f=document.getElementById('files');f.value='';f.dispatchEvent(new Event('change'))">{_esc(t(lang,'cancel'))}</button>
</form>
<div id="preview"></div>
</div>
<script>
const input=document.getElementById('files'); const box=document.getElementById('drop'); const prev=document.getElementById('preview');
function show(){{prev.innerHTML='';[...input.files].forEach((f,i)=>{{const d=document.createElement('div');
d.innerHTML='<b>'+f.name+'</b> '+(f.size/1024).toFixed(1)+' KB <button type=button data-i="'+i+'">{t(lang,'remove')}</button>';
if(f.type.startsWith('image/')){{const img=document.createElement('img');img.className='th';img.src=URL.createObjectURL(f);d.prepend(img);}}
prev.appendChild(d);}});prev.querySelectorAll('button').forEach(b=>b.onclick=()=>{{const dt=new DataTransfer();[...input.files].forEach((f,i)=>{{if(i!=+b.dataset.i)dt.items.add(f);}});input.files=dt.files;show();}});}}
input.onchange=()=>{{show();const name=input.parentElement&&input.parentElement.querySelector('.file-name');if(name)name.textContent=input.files.length?input.files[0].name:name.getAttribute('data-empty');}}; ['dragover','drop'].forEach(ev=>box.addEventListener(ev,e=>{{e.preventDefault(); if(ev==='drop'){{input.files=e.dataTransfer.files;input.onchange();}}}}));
</script>
<p><a href="/media?id={_esc(pid)}">{_esc(t(lang,'nav_media'))}</a> · <a href="/queue">{_esc(t(lang,'nav_queue'))}</a></p>
"""
        self._page(body, pid)

    def _media(self, pid: str, q) -> None:
        lang = self._lang() or "en"
        dest = str((q.get("catalog") or [pid])[0] or pid).strip() or pid
        page = service.product_page(PROJECT_ROOT, KNOWLEDGE_ROOT, DATA_DIR, pid)
        qtext = (q.get("q") or [""])[0].lower()
        feats = catalog_feature_ids(KNOWLEDGE_ROOT, dest) or catalog_feature_ids(KNOWLEDGE_ROOT, pid) or [
            str(f) for f in (page.get("features") or []) if str(f).strip()
        ]
        feat_opts = "".join(f"<option value='{_esc(f)}'>{_esc(f)}</option>" for f in feats)
        rows = []
        batch_ids = []
        for m in page.get("media") or []:
            if not is_remote_server_item(m):
                continue
            if m.get("catalog_path"):
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
            mid = str(m.get("media_id") or "")
            send = (
                f"<form class='row-ops'>"
                f"<input type='hidden' name='id' value='{_esc(pid)}'>"
                f"<input type='hidden' name='catalog' value='{_esc(dest)}'>"
                f"<input type='hidden' name='mid' value='{_esc(mid)}'>"
                f"{_feat_fields(lang, mid, opts or feat_opts)}"
                f"<button type='button' class='send-one' data-wait='{_esc(t(lang,'sending'))}' "
                f"data-fail='{_esc(t(lang,'err_catalog_send'))}'>{_esc(t(lang,'send_catalog'))}</button></form>"
            )
            rows.append(
                "<div class='media-row'>"
                f"<input type='checkbox' name='pick' value='{_esc(mid)}'>"
                f"<a class='zoom' href='/thumb?id={_esc(pid)}&mid={_esc(mid)}'>"
                f"<img class='th' src='/thumb?id={_esc(pid)}&mid={_esc(mid)}' alt=''></a>"
                f"<span class='name' title='{_esc(m.get('filename'))}'>{_esc(m.get('filename'))}</span><span>{_esc(m.get('status'))}</span>"
                f"{send}"
                f"<form method='post' action='/api/delete' class='row-ops'><input type='hidden' name='id' value='{_esc(pid)}'>"
                f"<input type='hidden' name='mid' value='{_esc(mid)}'><button class='danger'>{_esc(t(lang,'delete'))}</button></form>"
                "</div>"
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
            f"<p class='stat'>{_esc(t(lang,'consistency'))}: {_esc(mapped_n)} / {_esc(media_n)}</p>"
        )
        cat_opts = "".join(
            f"<option value='{_esc(p['product_id'])}' {'selected' if p['product_id']==dest else ''}>"
            f"{_esc(p.get('title') or p['product_id'])}</option>"
            for p in (service.dashboard(PROJECT_ROOT, KNOWLEDGE_ROOT, DATA_DIR).get("products") or [])
        )
        self._page(
                flash
                + f"<p class='guide'>{_esc(t(lang,'media_help'))}</p>"
                + cons_line
                + f"<div class='media-bar'>"
                f"<form method='get' action='/media'>"
                f"<input type='hidden' name='id' value='{_esc(pid)}'>"
                f"<label>{_esc(t(lang,'target_catalog'))}</label>"
                f"<select name='catalog' id='destcat' onchange='this.form.submit()'>{cat_opts}</select>"
                f"</form>"
                f"<div class='bar-act'><button type='button' id='batchbtn'>{_esc(t(lang,'batch_analyze'))}</button>"
                f"<span id='batchbox' hidden><span class='spin' aria-hidden='true'></span> "
                f"<span id='batchtxt'>{_esc(t(lang,'batch_wait'))}</span></span></div></div>"
                f"<script>window.BATCH={{pid:{json.dumps(pid)},dest:{json.dumps(dest)},ids:{json.dumps([x for x in batch_ids if x])},label:{json.dumps(t(lang,'batch_wait'))},need:{json.dumps(t(lang,'err_pick'))}}};"
                """(function(){const b=document.getElementById('batchbtn');const box=document.getElementById('batchbox');const txt=document.getElementById('batchtxt');
function picked(){return [...document.querySelectorAll('input[name=pick]:checked')].map(x=>x.value);}
function featOf(id){const man=document.querySelector('input[data-hint="'+id+'"]');const sel=document.querySelector('select[data-mid="'+id+'"]');return ((man&&man.value)||(sel&&sel.value)||'').trim();}
if(!b||!window.BATCH)return;b.onclick=async()=>{
const dest=(document.getElementById('destcat')||{}).value||window.BATCH.dest;
const ids=picked();if(!ids.length){toast(window.BATCH.need||'pick',false);return;}
b.disabled=true;b.setAttribute('aria-busy','true');box.hidden=false;
let ok=0,failed=0,done=0,next=0;const started=performance.now();
async function sendOne(id){
 const feat=featOf(id);const fd=new FormData();
 fd.append('id',window.BATCH.pid);fd.append('mid',id);fd.append('catalog',dest);
 if(feat){fd.append('feature',feat);fd.append('feature_manual',feat);}
 try{const r=await fetch('/api/analyze-send',{method:'POST',body:fd});const j=await r.json();if(r.ok&&j.ok){ok++;const pick=document.querySelector('input[name=pick][value="'+CSS.escape(id)+'"]');const row=pick&&pick.closest('.media-row');if(row)row.remove();}else failed++;}
 catch(e){failed++;}
 done++;txt.textContent=(window.BATCH.label||'')+' '+done+'/'+ids.length+'  ✓'+ok+'  ✕'+failed;
}
async function worker(){while(next<ids.length){const id=ids[next++];await sendOne(id);}}
await Promise.all(Array.from({length:1},worker));
const seconds=((performance.now()-started)/1000).toFixed(1);
txt.textContent=done+'/'+ids.length+'  ✓'+ok+'  ✕'+failed+'  '+seconds+'s';
b.disabled=false;b.removeAttribute('aria-busy');toast(txt.textContent,failed===0);
};})();</script>"""
                f"<div class='media-row media-head'><input type='checkbox' onclick='document.querySelectorAll(\"input[name=pick]\").forEach(c=>c.checked=this.checked)'>"
                f"<span></span><span>{_esc(t(lang,'filename'))}</span><span>{_esc(t(lang,'col_status'))}</span>"
                f"<span class='feature-head'><span>{_esc(t(lang,'feature'))}</span>"
                f"<span>{_esc(t(lang,'feat_manual'))}</span><span>{_esc(t(lang,'send_catalog'))}</span></span>"
                f"<span></span></div>"
                + "".join(rows),
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
                "<div class='media-row catalog-row'>"
                f"<input type='checkbox' name='pick' value='{_esc(rel)}'>"
                f"<a class='zoom' href='/cmedia?p={_esc(rel)}'>"
                f"<img class='th' src='/cmedia?p={_esc(rel)}' alt=''></a>"
                f"<span class='name' title='{_esc(m.get('filename'))}'>{_esc(m.get('filename'))}</span>"
                f"<span class='feature-current' title='{_esc(current)}'>{_esc(current)}</span>"
                f"<form method='post' action='/api/cat-feat' class='row-ops'>"
                f"<input type='hidden' name='id' value='{_esc(pid)}'>"
                f"<input type='hidden' name='path' value='{_esc(rel)}'>"
                f"{_feat_fields(lang, rel, opts, current)}"
                f"<button>{_esc(t(lang,'save_feat'))}</button></form>"
                f"<span class='row-ops'><form method='post' action='/api/cat-return' class='row-ops'>"
                f"<input type='hidden' name='id' value='{_esc(pid)}'>"
                f"<input type='hidden' name='path' value='{_esc(rel)}'>"
                f"<button class='ghost'>{_esc(t(lang,'return_media'))}</button></form>"
                f"<form method='post' action='/api/cat-delete' class='row-ops'>"
                f"<input type='hidden' name='id' value='{_esc(pid)}'>"
                f"<input type='hidden' name='path' value='{_esc(rel)}'>"
                f"<button class='danger'>{_esc(t(lang,'del_server'))}</button></form></span>"
                "</div>"
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
            + f"<div class='media-bar'>"
            f"<form method='get' action='/catalog-photos'>"
            f"<label>{_esc(t(lang,'target_catalog'))}</label>"
            f"<select name='id' onchange='this.form.submit()'>{cat_opts}</select></form>"
            f"<form method='post' action='/api/cat-delete-picked' class='bar-act' id='delpicked' onsubmit='var b=document.querySelectorAll(\"input[name=pick]:checked\");if(!b.length){{alert({json.dumps(t(lang,'err_pick'))});return false;}}b.forEach(x=>{{var i=document.createElement(\"input\");i.type=\"hidden\";i.name=\"path\";i.value=x.value;this.appendChild(i);}});return confirm({json.dumps(t(lang,'del_all_confirm'))})'>"
            f"<input type='hidden' name='id' value='{_esc(pid)}'>"
            f"<button type='submit' class='danger'>{_esc(t(lang,'del_all_photos'))}</button></form></div>"
            f"<div class='media-row media-head catalog-row'><input type='checkbox' onclick='document.querySelectorAll(\"input[name=pick]\").forEach(c=>c.checked=this.checked)'>"
            f"<span></span><span>{_esc(t(lang,'filename'))}</span><span>{_esc(t(lang,'feature'))}</span>"
            f"<span class='feature-head'><span>{_esc(t(lang,'feature'))}</span>"
            f"<span>{_esc(t(lang,'feat_manual'))}</span><span>{_esc(t(lang,'save_feat'))}</span></span>"
            f"<span></span></div>"
            + "".join(rows),
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
        catalog_mutations = {
            "/api/catalog-build",
            "/api/catalog-publish",
            "/api/catalog-disable",
            "/api/catalog-text",
            "/api/catalog-feat-add",
            "/api/cat-feat",
            "/api/cat-return",
            "/api/cat-delete",
            "/api/cat-delete-all",
            "/api/cat-delete-picked",
            "/api/to-catalog",
            "/api/analyze-send",
        }
        if u in catalog_mutations and not session_status().get("connected"):
            if (self.headers.get("X-Stay") or "") == "1":
                self._send(
                    json.dumps(
                        {"ok": False, "msg": t(lang, "err_offline"), "error": "not connected"}
                    ).encode("utf-8"),
                    200,
                    "application/json",
                )
                return
            self._redir(f"/catalog?id={quote(pid)}&err=err_offline")
            return
        if u in catalog_mutations and u not in {"/api/to-catalog", "/api/analyze-send"}:
            pulled = pull_remote_catalogs(DATA_DIR, KNOWLEDGE_ROOT)
            if not pulled.get("ok"):
                self._redir(f"/catalog?id={quote(pid)}&err=err_catalog_publish")
                return
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
            elif u == "/api/catalog-build":
                if not session_status().get("connected"):
                    loc = f"/catalog?id={quote(pid)}&err=err_offline"
                else:
                    was_enabled = bool(
                        read_catalog(KNOWLEDGE_ROOT, pid).get("catalog_enabled", False)
                    )
                    ok, err = execute_action("catalog", pid)
                    if ok:
                        service.set_catalog_enabled(KNOWLEDGE_ROOT, pid, was_enabled)
                        result = publish_catalog_to_bot(
                            DATA_DIR, PROJECT_ROOT, KNOWLEDGE_ROOT, pid
                        )
                        loc = (
                            f"/catalog?id={quote(pid)}&msg=ok_catalog"
                            if result.get("ok")
                            else f"/catalog?id={quote(pid)}&err=err_catalog_publish"
                        )
                    else:
                        loc = f"/catalog?id={quote(pid)}&err={quote(err or 'err_catalog_send')}"
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
                if not pid:
                    products = service.dashboard(PROJECT_ROOT, KNOWLEDGE_ROOT, DATA_DIR).get("products") or []
                    pid = str((products[0] or {}).get("product_id") or "") if products else ""
                result = ingest_loose_files(PROJECT_ROOT, DATA_DIR, pid, files)
                loc = "/queue"
                if not result.get("ok"):
                    loc = "/queue?err=err_loose"
                else:
                    loc = "/queue?msg=ok_loose"
            elif u == "/api/analyze-send":
                mid = (form.get("mid") or [""])[0]
                cat_id = (form.get("catalog") or [pid])[0]
                feat, hint = _feat_posted(form)
                out = analyze_and_send(
                    PROJECT_ROOT,
                    KNOWLEDGE_ROOT,
                    DATA_DIR,
                    pid,
                    mid,
                    catalog_id=cat_id,
                    feature_id=feat,
                )
                self._send(json.dumps(out).encode("utf-8"), 200, "application/json")
                return
            elif u == "/api/to-catalog":
                feat, hint = _feat_posted(form)
                mid = (form.get("mid") or [""])[0]
                cat_id = (form.get("catalog") or [pid])[0]
                loc = f"/media?id={pid}&catalog={quote(cat_id)}"
                if not feat:
                    loc = f"/media?id={pid}&catalog={quote(cat_id)}&err=err_no_feature"
                    if (self.headers.get("X-Stay") or "") == "1":
                        self._send(
                            json.dumps({"ok": False, "msg": t(lang, "err_no_feature")}).encode("utf-8"),
                            200,
                            "application/json",
                        )
                        return
                else:
                    out = send_mapped_media_to_catalog(
                        PROJECT_ROOT,
                        KNOWLEDGE_ROOT,
                        DATA_DIR,
                        pid,
                        mid,
                        feat,
                        catalog_id=cat_id,
                        ai_hint=hint,
                    )
                    err = {
                        "local file missing": "err_no_file",
                        "not connected": "err_offline",
                        "no_feature": "err_no_feature",
                    }.get(str(out.get("error") or ""), "err_catalog_send")
                    loc = (
                        f"/catalog-photos?id={quote(cat_id)}&msg=ok_catalog_send"
                        if out.get("ok")
                        else f"/media?id={pid}&catalog={quote(cat_id)}&err={err}"
                    )
                    if (self.headers.get("X-Stay") or "") == "1":
                        msg = t(lang, "ok_catalog_send" if out.get("ok") else err)
                        self._send(
                            json.dumps({"ok": bool(out.get("ok")), "msg": msg, "error": out.get("error")}).encode("utf-8"),
                            200,
                            "application/json",
                        )
                        return
            elif u == "/api/cat-delete-all":
                delete_all_catalog_media(PROJECT_ROOT, KNOWLEDGE_ROOT, DATA_DIR, pid)
                remote = push_catalog_json_to_bot(DATA_DIR, KNOWLEDGE_ROOT, pid)
                loc = (
                    f"/catalog-photos?id={pid}&msg=ok_del_all"
                    if remote.get("ok")
                    else f"/catalog-photos?id={pid}&err=err_catalog_publish"
                )
            elif u == "/api/cat-delete-picked":
                paths = form.get("path") or []
                if not paths:
                    loc = f"/catalog-photos?id={pid}&err=err_pick"
                else:
                    for rel in paths:
                        delete_catalog_media(PROJECT_ROOT, KNOWLEDGE_ROOT, DATA_DIR, pid, rel, from_server=True)
                    remote = push_catalog_json_to_bot(DATA_DIR, KNOWLEDGE_ROOT, pid)
                    loc = (
                        f"/catalog-photos?id={pid}&msg=ok_del_all"
                        if remote.get("ok")
                        else f"/catalog-photos?id={pid}&err=err_catalog_publish"
                    )
            elif u == "/api/catalog-publish":
                if session_status().get("connected"):
                    service.set_catalog_enabled(KNOWLEDGE_ROOT, pid, True)
                    result = publish_catalog_to_bot(
                        DATA_DIR, PROJECT_ROOT, KNOWLEDGE_ROOT, pid
                    )
                else:
                    result = {"ok": False, "error": "not connected"}
                append_history(
                    DATA_DIR,
                    pid,
                    {
                        "action": "publish_catalog_to_bot",
                        "result": "ok" if result.get("ok") else "FAILED",
                        "error": "" if result.get("ok") else result.get("error") or "",
                        "filename": f"{pid}.json",
                        "source_section": "catalog",
                        "server": session_status().get("host") or "",
                    },
                )
                loc = (
                    f"/catalog?id={quote(pid)}&msg=ok_catalog_publish"
                    if result.get("ok")
                    else f"/catalog?id={quote(pid)}&err=err_catalog_publish"
                )
            elif u == "/api/catalog-disable":
                if session_status().get("connected"):
                    service.set_catalog_enabled(KNOWLEDGE_ROOT, pid, False)
                    result = push_catalog_json_to_bot(
                        DATA_DIR, KNOWLEDGE_ROOT, pid, restart=True
                    )
                else:
                    result = {"ok": False, "error": "not connected"}
                append_history(
                    DATA_DIR,
                    pid,
                    {
                        "action": "disable_catalog_for_bot",
                        "result": "ok" if result.get("ok") else "FAILED",
                        "error": "" if result.get("ok") else result.get("error") or "",
                        "filename": f"{pid}.json",
                        "source_section": "catalog",
                        "server": session_status().get("host") or "",
                    },
                )
                loc = (
                    f"/catalog?id={quote(pid)}&msg=ok_catalog_disable"
                    if result.get("ok")
                    else f"/catalog?id={quote(pid)}&err=err_catalog_disable"
                )
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
                if out.get("ok"):
                    remote = push_catalog_json_to_bot(DATA_DIR, KNOWLEDGE_ROOT, pid)
                    if not remote.get("ok"):
                        out = remote
                append_history(
                    DATA_DIR,
                    pid,
                    {
                        "action": "save_catalog_text",
                        "result": "ok" if out.get("ok") else "FAILED",
                        "filename": f"{pid}.json",
                        "source_section": "catalog",
                        "server": session_status().get("host") or "",
                    },
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
                if out.get("ok"):
                    remote = push_catalog_json_to_bot(DATA_DIR, KNOWLEDGE_ROOT, pid)
                    if not remote.get("ok"):
                        out = remote
                append_history(
                    DATA_DIR,
                    pid,
                    {
                        "action": "add_catalog_feature",
                        "result": "ok" if out.get("ok") else "FAILED",
                        "object": (form.get("feat_id") or [""])[0],
                        "source_section": "catalog",
                    },
                )
                loc = f"/catalog?id={pid}&msg=ok_feat_add" if out.get("ok") else f"/catalog?id={pid}&err=err_feat_add"
            elif u == "/api/install-bot":
                from src.manager.install_bot import install_telegram_bot

                out = install_telegram_bot(
                    local_path=(form.get("local_path") or [""])[0],
                    host=(form.get("host") or [""])[0],
                    port=(form.get("port") or ["22"])[0],
                    username=(form.get("username") or [""])[0],
                    password=(form.get("password") or [""])[0],
                    remote_dir=(form.get("remote_dir") or [""])[0],
                    service_name=(form.get("service_name") or [""])[0],
                    bot_token=(form.get("bot_token") or [""])[0],
                    start_cmd=(form.get("start_cmd") or [""])[0],
                    extra_env=(form.get("extra_env") or [""])[0],
                    extra_pip=(form.get("extra_pip") or [""])[0],
                    bot_label=(form.get("bot_label") or [""])[0],
                    ssh_key=(form.get("ssh_key") or [""])[0],
                )
                loc = "/install?msg=ok_install" if out.get("ok") else "/install?err=err_install"
            elif u == "/api/cat-feat":
                rel = (form.get("path") or [""])[0]
                feat, _hint = _feat_posted(form)
                out = set_catalog_media_feature(KNOWLEDGE_ROOT, DATA_DIR, pid, rel, feat)
                if out.get("ok"):
                    remote = push_catalog_json_to_bot(DATA_DIR, KNOWLEDGE_ROOT, pid)
                    if not remote.get("ok"):
                        out = remote
                append_history(
                    DATA_DIR,
                    pid,
                    {
                        "action": "set_photo_feature",
                        "result": "ok" if out.get("ok") else "FAILED",
                        "filename": Path(rel).name,
                        "source_section": "catalog_photos",
                        "server": session_status().get("host") or "",
                    },
                )
                loc = f"/catalog-photos?id={pid}&msg=ok_feat" if out.get("ok") else f"/catalog-photos?id={pid}&err=err_no_feature"
            elif u == "/api/cat-return":
                rel = (form.get("path") or [""])[0]
                return_catalog_media_to_index(KNOWLEDGE_ROOT, DATA_DIR, pid, rel)
                remote = push_catalog_json_to_bot(DATA_DIR, KNOWLEDGE_ROOT, pid)
                append_history(
                    DATA_DIR,
                    pid,
                    {
                        "action": "return_to_media",
                        "result": "ok",
                        "filename": Path(rel).name,
                        "source_section": "catalog_photos",
                        "server": session_status().get("host") or "",
                    },
                )
                loc = (
                    f"/catalog-photos?id={pid}&msg=ok_return"
                    if remote.get("ok")
                    else f"/catalog-photos?id={pid}&err=err_catalog_publish"
                )
            elif u == "/api/cat-delete":
                rel = (form.get("path") or [""])[0]
                delete_catalog_media(PROJECT_ROOT, KNOWLEDGE_ROOT, DATA_DIR, pid, rel, from_server=True)
                remote = push_catalog_json_to_bot(DATA_DIR, KNOWLEDGE_ROOT, pid)
                append_history(
                    DATA_DIR,
                    pid,
                    {
                        "action": "delete_catalog_photo",
                        "result": "ok",
                        "filename": Path(rel).name,
                        "source_section": "catalog_photos",
                        "server": session_status().get("host") or "",
                    },
                )
                loc = (
                    f"/catalog-photos?id={pid}&msg=ok_del_cat"
                    if remote.get("ok")
                    else f"/catalog-photos?id={pid}&err=err_catalog_publish"
                )
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
                fields = {}
                for key in ("host", "port", "username", "auth_method", "key_path", "remote_media_path", "remote_bot_root"):
                    if key in form:
                        fields[key] = (form.get(key) or [""])[0]
                save_sftp_settings(
                    DATA_DIR,
                    fields,
                    password=(form.get("password") or [""])[0] or None,
                    key_pem=(form.get("key_pem") or [""])[0] or None,
                )
                append_history(
                    DATA_DIR,
                    "_manager",
                    {
                        "action": "save_server_settings",
                        "result": "ok",
                        "source_section": "settings",
                        "server": (form.get("host") or [""])[0],
                    },
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
                append_history(
                    DATA_DIR,
                    "_manager",
                    {
                        "action": "save_ai_settings",
                        "result": "ok",
                        "source_section": "settings",
                        "server": session_status().get("host") or "",
                    },
                )
                loc = "/settings?msg=saved_ok"
            elif u == "/api/ai-connect":
                result = test_ai_connection(PROJECT_ROOT, DATA_DIR)
                set_ai_connection_state(
                    PROJECT_ROOT,
                    DATA_DIR,
                    connected=bool(result.get("ok")),
                )
                append_history(
                    DATA_DIR,
                    "_manager",
                    {
                        "action": "connect_ai",
                        "result": "ok" if result.get("ok") else "FAILED",
                        "error": "" if result.get("ok") else result.get("error") or "",
                        "source_section": "settings",
                    },
                )
                loc = "/settings?msg=ok_ai_connect" if result.get("ok") else "/settings?err=err_ai_connect"
            elif u == "/api/ai-disconnect":
                set_ai_connection_state(PROJECT_ROOT, DATA_DIR, connected=False)
                append_history(
                    DATA_DIR,
                    "_manager",
                    {
                        "action": "disconnect_ai",
                        "result": "ok",
                        "source_section": "settings",
                    },
                )
                loc = "/settings?msg=ok_ai_disconnect"
            elif u == "/api/connect":
                result = connect_session(DATA_DIR)
                if result.get("ok"):
                    pulled = pull_remote_catalogs(DATA_DIR, KNOWLEDGE_ROOT)
                    append_history(
                        DATA_DIR,
                        "_manager",
                        {
                            "action": "connect_server",
                            "result": "ok",
                            "source_section": "settings",
                            "server": result.get("host") or "",
                        },
                    )
                    loc = "/settings?msg=ok_connect" if pulled.get("ok") else "/settings?msg=ok_connect"
                else:
                    loc = "/settings?err=err_connect"
            elif u == "/api/link-bot-ai":
                ai = load_ai_settings(PROJECT_ROOT, DATA_DIR)
                result = (
                    sync_remote_ai(
                        DATA_DIR,
                        base_url=str(ai.get("base_url") or ""),
                        model=str(ai.get("model") or ""),
                        api_key=str(ai.get("api_key") or ""),
                    )
                    if ai.get("connected")
                    else {"ok": False, "error": "AI is not connected"}
                )
                append_history(
                    DATA_DIR,
                    "_manager",
                    {
                        "action": "sync_bot_ai",
                        "result": "ok" if result.get("ok") else "FAILED",
                        "error": "" if result.get("ok") else result.get("error") or "",
                        "source_section": "settings",
                        "server": session_status().get("host") or "",
                    },
                )
                if result.get("ok"):
                    set_ai_connection_state(PROJECT_ROOT, DATA_DIR, bot_linked=True)
                loc = "/settings?msg=ok_link_ai" if result.get("ok") else "/settings?err=err_link_ai"
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
                append_history(
                    DATA_DIR,
                    pid,
                    {"action": "save_product_paths", "result": "ok", "source_section": "products"},
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
