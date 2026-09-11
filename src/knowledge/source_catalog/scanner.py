"""Walk F:\\VPS to VPN and discover features from OpIDs, UI, packages, cmds."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from src.knowledge.source_catalog.schema import (
    STATUS_DEPRECATED,
    STATUS_LIVE,
    FeatureRecord,
)

SKIP_DIR_NAMES = {
    ".git",
    ".cursor",
    "vendor",
    "graphify-out",
    "node_modules",
    "__pycache__",
    ".venv",
    "VPS to VPN-Portable",
    "build",
}

# Path fragments that are artifacts, not product knowledge.
ARTIFACT_HINTS = ("-portable", "/vendor/", "\\vendor\\")

OP_RE = re.compile(r'(\w+)\s+OpID\s+=\s+"([^"]+)"')
FUNC_RE = re.compile(r"^func\s+(?:\([^)]+\)\s+)?([A-Za-z_][A-Za-z0-9_]*)", re.M)
HTTP_RE = re.compile(r"https?://[a-zA-Z0-9._~:/?#\[\]@!$&'()*+,;=%-]+")
PKG_RE = re.compile(r"^package\s+(\w+)", re.M)
TAB_RE = re.compile(r'tab\.(operations|diagnostics|view|settings|registration|contact)')
SHOW_RE = re.compile(r"\b(show[A-Z]\w+|build[A-Z]\w+|New[A-Z]\w+)\b")

# Logical groups: a file matching any needle is claimed. Counts are not hardcoded.
# Needles are path substrings (posix) or symbol prefixes.
GroupSpec = tuple[str, str, str, tuple[str, ...], tuple[str, ...], tuple[str, ...], str, str]

GROUP_SPECS: list[GroupSpec] = [
    ("first_run_splash", "Splash", "Getting Started", (), ("internal/ui/splash.go",), ("splash",), STATUS_LIVE, "windows"),
    ("first_run_language", "Language selection", "Getting Started", (), ("internal/ui/lang.go",), ("language",), STATUS_LIVE, "windows"),
    ("first_run_mode", "Mode selection", "Getting Started", (), ("internal/ui/mode.go",), ("mode",), STATUS_LIVE, "windows"),
    ("modes", "Basic / Pro / AI Pro", "Getting Started", (), ("internal/ui/view.go", "internal/ui/dashboard.go", "internal/ui/ops.go"), (), STATUS_LIVE, "windows"),
    ("view_topology", "View tab / Topology", "Advanced Features", (), ("internal/ui/topology.go", "internal/ui/topology_form.go", "internal/ui/topology_replace.go"), ("topology",), STATUS_LIVE, "windows"),
    ("tab_contact", "Contact tab", "Settings", (), ("internal/ui/contact.go",), (), STATUS_LIVE, "windows"),
    ("tab_settings", "Settings", "Settings", (), ("internal/ui/settings.go",), (), STATUS_LIVE, "windows"),
    ("locale_system", "Locale system (6 languages)", "Settings", (), ("internal/i18n/",), (), STATUS_LIVE, "windows"),
    ("locale_download", "Remote locale download", "Settings", (), ("internal/i18n/remote.go",), (), STATUS_LIVE, "windows"),
    ("app_update", "Forced update and news", "Updates", (), ("internal/ui/remote_update.go", "internal/remotehub/"), ("forceupdate", "news"), STATUS_LIVE, "windows"),
    ("xui_package_manager", "3X-UI package manager", "Updates", (), ("internal/ui/xui_package_manager.go", "internal/sanaei/xuipkg/"), (), STATUS_LIVE, "windows"),
    ("setup_central", "Setup Central", "Server Management", ("setup_central",), ("internal/ui/dialogs.go",), ("showSetupWizard",), STATUS_LIVE, "windows"),
    ("connect_ssh", "Connect SSH", "SSH", ("connect_ssh",), ("internal/ssh/",), (), STATUS_LIVE, "windows"),
    ("test_ssh", "Test SSH", "SSH", ("test_ssh",), (), ("OpTestSSH",), STATUS_LIVE, "windows"),
    ("ssh_host_key", "SSH host-key confirm", "SSH", (), ("internal/ui/hostkey_handler.go",), (), STATUS_LIVE, "windows"),
    ("ssh_password_expired", "Expired SSH password", "SSH", (), ("internal/ui/password_handler.go",), (), STATUS_LIVE, "windows"),
    ("ssh_key_ui", "SSH key UI", "SSH", (), ("internal/ui/ssh_key.go",), (), STATUS_LIVE, "windows"),
    ("proxy_settings", "Proxy Settings", "Proxy", ("proxy_settings",), ("internal/ui/dialogs.go", "internal/proxy/"), ("showProxySettings",), STATUS_LIVE, "windows"),
    ("install_wg", "Install WireGuard", "Server Management", ("install_wg",), (), ("OpInstallWG",), STATUS_LIVE, "windows"),
    ("install_sanaei", "Install Sanaei / 3X-UI", "Panel Configuration", ("install_sanaei",), ("internal/sanaei/",), ("OpInstallSanaei",), STATUS_LIVE, "windows"),
    ("full_deploy", "Full Deploy", "Server Management", ("full_deploy",), ("internal/deploy/", "internal/ui/full_deploy_source.go"), (), STATUS_LIVE, "windows"),
    ("full_deploy_source", "Full Deploy source selection", "Server Management", (), ("internal/ui/full_deploy_source.go",), (), STATUS_LIVE, "windows"),
    ("deploy_exit_1", "Deploy Exit 1 (Basic)", "Exit Server", ("deploy_location",), ("internal/ui/location_deploy.go",), ("OpDeployLocation",), STATUS_LIVE, "windows"),
    ("add_exit_servers", "Add Exit slots 1–6", "Exit Server", ("add_exit_server",), ("internal/ui/location_add_dialog.go",), (), STATUS_LIVE, "windows"),
    ("add_tunnel_servers", "Add Tunnel Servers", "Tunnel", ("add_tunnel_server",), ("internal/ui/tunnel_deploy.go",), (), STATUS_LIVE, "windows"),
    ("add_node_servers", "Add Node Servers", "Server Management", ("add_node",), ("internal/ui/add_node.go",), (), STATUS_LIVE, "windows"),
    ("deploy_chain_legacy", "Deploy Chain (legacy)", "Tunnel", ("deploy_chain",), (), ("OpDeployChain",), STATUS_DEPRECATED, "windows"),
    ("configure_panel", "Configure Panel 4-step wizard", "Panel Configuration", ("configure_panel",), ("internal/ui/configure_panel_wizard.go",), (), STATUS_LIVE, "windows"),
    ("configure_backup_memory", "Configure backup/inbound memory", "Panel Configuration", (), ("internal/ui/configure_backup_sources.go",), (), STATUS_LIVE, "windows"),
    ("configure_migration", "Configure migration inbound choice", "Panel Configuration", (), ("internal/ui/configure_panel_migration.go",), (), STATUS_LIVE, "windows"),
    ("configure_router_memory", "Configure router outbound memory", "Panel Configuration", (), ("internal/ui/configure_router_memory.go",), (), STATUS_LIVE, "windows"),
    ("panel_existing", "Existing panel on server", "Panel Configuration", (), ("internal/ui/panel_existing_modal.go",), (), STATUS_LIVE, "windows"),
    ("panel_login_info", "Panel Login Info", "Panel Configuration", ("panel_info",), ("internal/ui/panel_dialog.go", "internal/ui/panel_login_target.go"), (), STATUS_LIVE, "windows"),
    ("test_client", "Test Client", "Client Testing", ("test_client",), ("internal/ui/panel_dialog.go",), ("OpTestClient",), STATUS_LIVE, "windows"),
    ("add_subscription", "Add Subscription", "Client Testing", ("add_subscription",), (), ("OpAddSubscription",), STATUS_LIVE, "windows"),
    ("add_outbounds", "Add OutBounds", "Panel Configuration", ("add_outbounds",), (), ("OpAddOutbounds",), STATUS_LIVE, "windows"),
    ("add_domain_dns", "Add Domain DNS", "Domain", ("add_domain",), ("internal/ui/dns_manager_tab.go", "internal/dns/"), (), STATUS_LIVE, "windows"),
    ("get_certificate", "Get Certificate", "Domain", (), ("internal/ui/get_certificate.go",), (), STATUS_LIVE, "windows"),
    ("external_proxy", "Add Domain External Proxy", "Proxy", (), ("internal/ui/external_proxy_tab.go",), (), STATUS_LIVE, "windows"),
    ("free_domain", "Free Domain", "Domain", (), ("internal/ui/free_domain_tab.go", "internal/dns/freedomain"), (), STATUS_LIVE, "windows"),
    ("cdn_cloudflare", "Cloudflare", "Cloudflare", ("add_cdn",), ("internal/dns/cloudflare.go",), (), STATUS_LIVE, "windows"),
    ("cdn_arvancloud", "ArvanCloud", "Cloudflare", (), ("internal/dns/arvancloud.go",), (), STATUS_LIVE, "windows"),
    ("configure_cdn", "Configure CDN (Arvan/CF/Other)", "Cloudflare", (), ("internal/ui/cdn_dialog.go", "internal/config/cdn_providers.go"), (), STATUS_LIVE, "windows"),
    ("mesh_topology", "Mesh View Topology", "Tunnel", ("mesh_servers",), ("internal/ui/mesh_page.go", "internal/ui/mesh_graph.go", "internal/mesh/"), (), STATUS_LIVE, "windows"),
    ("mesh_watchdog", "Mesh watchdog / connection manager", "Tunnel", (), ("internal/ui/mesh_page.go",), ("watchdog",), STATUS_LIVE, "windows"),
    ("link_type_change", "Mesh link type change", "Tunnel", ("link_test",), ("internal/ui/link_type_picker.go", "internal/ui/link_type_form.go"), (), STATUS_LIVE, "windows"),
    ("link_recovery", "Link recovery", "Tunnel", (), ("internal/config/link_recovery.go",), (), STATUS_LIVE, "windows"),
    ("ip_access", "IP Access / reachability", "Server Management", (), ("internal/ui/mesh_reach_card.go",), (), STATUS_LIVE, "windows"),
    ("gre_fallback", "GRE fallback", "Tunnel", (), ("internal/gre/", "internal/ui/server_creds_dialog.go"), (), STATUS_LIVE, "windows"),
    ("netcheck", "Netcheck", "Troubleshooting", (), ("internal/netcheck/",), (), STATUS_LIVE, "windows"),
    ("diagnose_repair", "Diagnose & Repair", "Troubleshooting", ("diagnose_repair",), ("internal/ui/diagnostics.go", "internal/diagnostics/"), (), STATUS_LIVE, "windows"),
    ("check_system", "Check System / diagnostics export", "Troubleshooting", (), ("internal/ui/diagnostics.go",), (), STATUS_LIVE, "windows"),
    ("move_central", "Move Central", "Server Management", ("move_central_server",), ("internal/ui/move_central_dialog.go",), (), STATUS_LIVE, "windows"),
    ("move_central_path_a", "Move Central Path A", "Server Management", (), ("internal/ui/move_central_path_a.go",), (), STATUS_LIVE, "windows"),
    ("move_central_path_b", "Panel Manager Path B", "Server Management", (), ("internal/ui/move_central_path_b.go",), (), STATUS_LIVE, "windows"),
    ("move_central_path_b2", "Panel Manager Path B2 mapping", "Server Management", (), ("internal/ui/move_central_path_b2.go",), (), STATUS_LIVE, "windows"),
    ("move_central_domain_gate", "Need app domain before restore", "Domain", (), ("internal/ui/move_central_path_b.go",), ("NeedAppDomain", "need app domain"), STATUS_LIVE, "windows"),
    ("saved_workflow", "Saved workflow", "Advanced Features", (), ("internal/workflow/", "internal/ui/move_central_workflow.go"), (), STATUS_LIVE, "windows"),
    ("add_telegram_mirza", "Telegram bot Mirza", "Advanced Features", ("add_bot_telegram",), ("internal/ui/add_bot_telegram.go", "internal/mirza/"), (), STATUS_LIVE, "windows"),
    ("telegram_other_delete_vpn", "Telegram Other / Delete / VPN routing", "Advanced Features", (), ("internal/ui/add_bot_telegram.go",), (), STATUS_LIVE, "windows"),
    ("delete_tools", "Delete Exit / Tunnel / History / Reset All", "Settings", (), ("internal/ui/delete_wizard.go",), (), STATUS_LIVE, "windows"),
    ("factory_reset_ssh", "Factory reset over SSH", "Settings", (), ("internal/ui/factory_reset_dialog.go",), (), STATUS_LIVE, "windows"),
    ("registration", "License claim / Device ID", "License", (), ("internal/ui/register.go", "internal/auth/"), (), STATUS_LIVE, "windows"),
    ("license_reactivation", "License reactivation", "License", (), ("internal/remotehub/activation.go",), ("reactivat",), STATUS_LIVE, "windows"),
    ("license_offline", "Offline license", "License", (), ("internal/auth/",), ("offline",), STATUS_LIVE, "windows"),
    ("license_bsc", "BSC wallet license", "License", (), ("internal/auth/bsc.go", "internal/auth/bsc_config.go"), (), STATUS_LIVE, "windows"),
    ("ai_chatbox", "AI Assistant", "AI Assistant", (), ("internal/ui/ai_assistant_page.go", "internal/ai/", "internal/ui/ai_chat_view.go"), (), STATUS_LIVE, "windows"),
    ("ai_quota_lock", "AI quota / lock gate / recharge", "AI Assistant", (), ("internal/ui/ai_access.go", "internal/remotehub/ai_quota.go"), (), STATUS_LIVE, "windows"),
    ("ai_selection_confirm", "AI selection confirmation", "AI Assistant", (), ("internal/ui/ai_selection_dialog.go",), (), STATUS_LIVE, "windows"),
    ("blackfox_mcp", "BlackFox MCP", "AI Assistant", ("blackfox_mcp",), ("internal/mcp/", "cmd/blackfox-mcp/", "internal/ui/ai_mcp_task.go"), (), STATUS_LIVE, "windows"),
    ("terminal", "Terminal / activity log", "Settings", (), ("internal/ui/terminal_widget.go", "internal/terminal/"), (), STATUS_LIVE, "windows"),
    ("status_bar", "Status bar", "Settings", (), ("internal/ui/status_manager.go", "internal/ui/status_bar_label.go"), (), STATUS_LIVE, "windows"),
    ("vault", "Vault encryption", "Security", (), ("internal/vault/",), (), STATUS_LIVE, "windows"),
    ("json_store", "Local JSON store", "Settings", (), ("internal/config/",), (), STATUS_LIVE, "windows"),
    ("transaction_log", "Transaction log", "Settings", (), ("internal/transaction/",), (), STATUS_LIVE, "windows"),
    ("android_bind", "Android bind layer", "Advanced Features", (), ("Android-VPS to VPN/",), (), STATUS_LIVE, "android"),
    ("pas_generator", "PAS Generator", "License", (), ("cmd/pas-generator/",), (), STATUS_LIVE, "windows"),
    ("windows_setup", "Windows Setup", "Installation", (), ("cmd/setup/",), (), STATUS_LIVE, "windows"),
    ("uninstaller", "Uninstaller", "Installation", (), ("cmd/uninstall/",), (), STATUS_LIVE, "windows"),
    ("installer_entry", "Desktop app entry", "Installation", (), ("cmd/installer/", "internal/ui/app.go"), (), STATUS_LIVE, "windows"),
]


@dataclass
class FileFact:
    rel: str
    kind: str  # ui, cmd, android, internal, test, other, skip
    package: str = ""
    symbols: list[str] = field(default_factory=list)
    apis: list[str] = field(default_factory=list)
    op_ids: list[str] = field(default_factory=list)
    sha256: str = ""
    error: str = ""


@dataclass
class ScanRaw:
    root: str
    files: list[FileFact]
    file_index_hash: str
    scanned_at: str
    go_files: int
    ui_prod_files: int
    packages: list[str]


def _posix(rel: str) -> str:
    return rel.replace("\\", "/")


def classify_rel(rel: str) -> str:
    p = _posix(rel).lower()
    if "/vendor/" in f"/{p}/" or p.startswith("vendor/"):
        return "skip"
    name = Path(p).name
    if name.endswith("_test.go"):
        return "test"
    if p.startswith("internal/ui/"):
        return "ui"
    if p.startswith("cmd/"):
        return "cmd"
    if p.startswith("android-vps to vpn/") or p.startswith("android-"):
        return "android"
    if p.startswith("internal/"):
        return "internal"
    return "other"


def should_skip_dir(name: str) -> bool:
    return name in SKIP_DIR_NAMES or name.startswith(".")


def iter_go_files(root: Path) -> Iterable[Path]:
    import os

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not should_skip_dir(d)]
        for fn in filenames:
            if fn.endswith(".go"):
                yield Path(dirpath) / fn


def parse_go_file(path: Path, rel: str) -> FileFact:
    fact = FileFact(rel=_posix(rel), kind=classify_rel(rel))
    if fact.kind == "skip":
        return fact
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        fact.error = str(exc)
        return fact
    fact.sha256 = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()
    m = PKG_RE.search(text)
    if m:
        fact.package = m.group(1)
    fact.symbols = FUNC_RE.findall(text)[:80]
    fact.apis = [u.rstrip(").,;") for u in HTTP_RE.findall(text)[:40]]
    fact.op_ids = [g[1] for g in OP_RE.findall(text)]
    return fact


def scan_source_tree(root: Path) -> ScanRaw:
    root = root.resolve()
    facts: list[FileFact] = []
    packages: set[str] = set()
    ui_prod = 0
    go_n = 0
    h = hashlib.sha256()
    for path in sorted(iter_go_files(root), key=lambda p: str(p).lower()):
        rel = str(path.relative_to(root))
        kind = classify_rel(rel)
        if kind == "skip":
            continue
        go_n += 1
        fact = parse_go_file(path, rel)
        facts.append(fact)
        if fact.package:
            packages.add(fact.package)
        if fact.kind == "ui":
            ui_prod += 1
        h.update(fact.rel.encode())
        h.update(fact.sha256.encode())
        if fact.error:
            h.update(fact.error.encode())
    return ScanRaw(
        root=str(root),
        files=facts,
        file_index_hash=h.hexdigest(),
        scanned_at=datetime.now(timezone.utc).isoformat(),
        go_files=go_n,
        ui_prod_files=ui_prod,
        packages=sorted(packages),
    )


def _file_matches(rel: str, needles: tuple[str, ...]) -> bool:
    p = _posix(rel).lower()
    for n in needles:
        if n.lower() in p:
            return True
    return False


def _symbol_matches(fact: FileFact, needles: tuple[str, ...]) -> bool:
    blob = " ".join(fact.symbols + fact.op_ids).lower()
    text = _posix(fact.rel).lower() + " " + blob
    for n in needles:
        if n.lower() in text:
            return True
    return False


def discover_features(raw: ScanRaw) -> list[FeatureRecord]:
    claimed: set[str] = set()
    features: list[FeatureRecord] = []
    by_rel = {f.rel: f for f in raw.files}

    for spec in GROUP_SPECS:
        fid, name, cat, op_ids, path_needles, sym_needles, status, platform = spec
        matched: list[FileFact] = []
        for fact in raw.files:
            if fact.kind in {"skip", "test"}:
                continue
            hit = False
            if path_needles and _file_matches(fact.rel, path_needles):
                hit = True
            if not hit and op_ids and any(o in fact.op_ids for o in op_ids):
                hit = True
            if not hit and sym_needles and _symbol_matches(fact, sym_needles):
                hit = True
            if hit:
                matched.append(fact)
                claimed.add(fact.rel)
        if not matched and not op_ids:
            # Keep seed even if files renamed — SCAN_ERROR rather than drop.
            rec = FeatureRecord(
                id=fid,
                name=name,
                category=cat,
                status=status,
                platform=platform,
                purpose="UNKNOWN",
                scan_errors=["no matching source files in this scan"],
                last_scanned=raw.scanned_at,
                source_version=raw.file_index_hash[:12],
            )
            features.append(rec)
            continue
        if not matched and op_ids:
            rec = FeatureRecord(
                id=fid,
                name=name,
                category=cat,
                operation_ids=list(op_ids),
                status=status,
                platform=platform,
                purpose=f"Tracked OpID {', '.join(op_ids)}",
                last_scanned=raw.scanned_at,
                source_version=raw.file_index_hash[:12],
            )
            features.append(rec)
            continue
        symbols: list[str] = []
        apis: list[str] = []
        ops: list[str] = list(op_ids)
        ui_locs: list[str] = []
        files: list[str] = []
        errors: list[str] = []
        hasher = hashlib.sha256()
        for fact in matched:
            files.append(fact.rel)
            symbols.extend(fact.symbols[:12])
            apis.extend(fact.apis)
            ops.extend(fact.op_ids)
            if fact.kind == "ui":
                ui_locs.append(fact.rel)
            if fact.error:
                errors.append(f"{fact.rel}: {fact.error}")
            hasher.update(fact.sha256.encode())
        purpose = name
        if status == STATUS_DEPRECATED:
            purpose = f"LEGACY — do not recommend as current workflow. {name}"
        rec = FeatureRecord(
            id=fid,
            name=name,
            category=cat,
            source_files=sorted(set(files)),
            source_symbols=sorted(set(symbols))[:40],
            ui_locations=sorted(set(ui_locs)),
            operation_ids=sorted(set(ops)),
            purpose=purpose,
            api_calls=sorted(set(apis))[:30],
            platform=platform,
            status=status,
            source_hash=hasher.hexdigest(),
            source_version=raw.file_index_hash[:12],
            last_scanned=raw.scanned_at,
            scan_errors=errors,
            workflow=["UNKNOWN"] if not ui_locs and not ops else [],
            inputs=["UNKNOWN"],
            outputs=["UNKNOWN"],
            requirements=["UNKNOWN"],
            validation=["UNKNOWN"],
            success_states=["UNKNOWN"],
            error_states=["UNKNOWN"],
            troubleshooting=["UNKNOWN"],
        )
        # Extract slightly more than UNKNOWN from constructor names
        shows = [s for s in rec.source_symbols if s.startswith("show") or s.startswith("build")]
        if shows:
            rec.workflow = [f"UI entry via {s}" for s in shows[:8]]
        features.append(rec)

    # Leftover production files become their own records so MISSING can reach 0.
    for fact in raw.files:
        if fact.rel in claimed or fact.kind in {"skip", "test"}:
            continue
        if fact.kind == "other" and "website" in fact.rel.lower():
            continue
        fid = "src_" + re.sub(r"[^a-z0-9]+", "_", _posix(fact.rel).lower()).strip("_")[:80]
        cat = {
            "ui": "Settings",
            "cmd": "Advanced Features",
            "android": "Advanced Features",
            "internal": "Server Management",
        }.get(fact.kind, "Advanced Features")
        features.append(
            FeatureRecord(
                id=fid,
                name=Path(fact.rel).stem,
                category=cat,
                source_files=[fact.rel],
                source_symbols=fact.symbols[:20],
                ui_locations=[fact.rel] if fact.kind == "ui" else [],
                purpose="Discovered from source file; behavior details UNKNOWN unless grouped.",
                api_calls=fact.apis[:15],
                platform="android" if fact.kind == "android" else "windows",
                status=STATUS_LIVE,
                source_hash=fact.sha256,
                source_version=raw.file_index_hash[:12],
                last_scanned=raw.scanned_at,
                scan_errors=[fact.error] if fact.error else [],
                inputs=["UNKNOWN"],
                outputs=["UNKNOWN"],
                requirements=["UNKNOWN"],
                validation=["UNKNOWN"],
            )
        )

    # Dedup ids
    by_id: dict[str, FeatureRecord] = {}
    for rec in features:
        if rec.id in by_id:
            old = by_id[rec.id]
            old.source_files = sorted(set(old.source_files + rec.source_files))
            old.source_symbols = sorted(set(old.source_symbols + rec.source_symbols))[:50]
            continue
        by_id[rec.id] = rec
    return list(by_id.values())
