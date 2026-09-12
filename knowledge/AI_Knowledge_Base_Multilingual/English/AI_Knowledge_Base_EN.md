# Black Fox VPN Installer — AI Knowledge Base

> **Language pack:** English (`AI_Knowledge_Base_Multilingual/English/`)  
> **Siblings:** Persian / Russian / Chinese packs in the same multilingual tree.  
> **Companion (repo):** `Documentation/*`, `Screenshots/`  
> **Audience:** RAG / chatbot / Telegram Bot. Match the end-user’s language; retrieve from the matching language folder.  
> **Rule:** Prefer facts below. Never invent version numbers, prices, or hosting brands. Mark gaps as `NEED_MORE_REVIEW`.


> **Audience:** RAG / chatbot systems (BlackFox AI, support bots, docs agents).  
> **Language:** English (primary). Match the end-user’s UI language in replies.  
> **Rule:** Prefer facts below. Never invent version numbers, prices, or hosting brands. Mark gaps as `NEED_MORE_REVIEW`.

---

## 1. Product introduction

**Black Fox Vpn** is an **operations installer / automation toolkit**, not a consumer “connect-to-VPN” client.

| Surface | Stack | Role |
|--------|--------|------|
| Windows Installer | Fyne desktop app | SSH-driven deploy of **3X-UI (Sanaei)** + **WireGuard** on Linux VPS; mesh, DNS/CDN, Mirza bot, license, AI Assistant Pro |
| Android app | Flutter | Companion product (Config Builder / VPN Android variants per hub `version.json`); AI Assistant Pro available on Android with shared persona rules |

**What it automates:** saving central SSH credentials, installing WireGuard and the Sanaei/3X-UI panel on a central VPS, adding exit/tunnel/node servers, panel configure/test client, domains/DNS, CDN, mesh links, Telegram Mirza bot, move-central, deletes/resets — via the app’s built-in flows over SSH and hub APIs.

**What it is not:** a residential VPN app that only toggles a tunnel for end users; a fork of the 3X-UI web UI; a generic Linux control panel.

**Brand / hubs**

- Primary update hub: `http://blackfoxupdate.ir`
- Secondary hub: `https://foxnext.net`
- Contact / website: FoxNext (`www.foxnext.net`, `support@foxnext.net`)
- Support channels (from runtime contact config): `@HiBlackFoxVpn`, `@BlackFoxVpnn`, `@BlackFoxVpn_bot`, `@Black_Fox_Group`
- Public GitHub display (runtime-config): `github.com/balckfoxgroup/blackfox-vpn-installer` — spelling as published in hub config

**External technical references (engineers / AI grounding only — do not invent versions from them)**

- 3X-UI (Sanaei): https://github.com/MHSanaei/3x-ui
- Mirza Telegram sales bot: https://github.com/mahdiMGF2/botmirzapanel

---

## 2. Versioning (verified + drift)

| Source | Version | Build | Notes |
|--------|---------|-------|-------|
| Windows code `internal/buildinfo/buildinfo.go` | AppVersion **3.0.0** | AppBuild **211** | Authoritative for current Windows source tree |
| Hub `host-samples/version.json` (Windows) | 3.0.0 | **208** | Download Setup from foxnext.net |
| Hub `version.json` → `vpn_android` | 3.0.0 | **207** | Android release APK |
| Hub `version.json` → `config_builder` | 1.1.3 | **7** | Black Fox Config Builder APK |

**`NEED_MORE_REVIEW`:** Live hub vs local AppBuild drift (211 local vs 208 Windows / 207 Android on sample hub). Chatbots **must not invent** app/panel/Xray/bot versions. Product AI system prompt: never state or discuss version numbers; identity answer is only “BlackFox AI”.

Minimum supported (hub sample): Windows/Android minimum_supported_version **3.0.0**, builds **207**.

---

## 3. Architecture (actionable)

```
[Windows Fyne / Android Flutter]
        │
        ├─ Local shared store (same across Basic / Pro / AI Pro)
        │     central SSH, panel URL/port/path/password, exits, tunnels,
        │     nodes, domains, CDN, op badges (opstate)
        │
        ├─ Operations UI / AI task actions
        │     → SSH client → Linux VPS scripts (WG, 3X-UI, mesh agents, …)
        │     → Panel API (Sanaei/3X-UI) for nodes, clients, outbounds
        │
        ├─ Network policy: try Direct once → on failure Program Proxy
        │     (SSH, hub HTTP, panel API)
        │
        └─ Dual remote hubs
              blackfoxupdate.ir (primary) → foxnext.net (fallback)
              version.json, runtime-config.json, license-access.json,
              AI proxy (/api/ai/chat|quota|usage), 3x-ui packages
```

**Shared-state invariant:** Basic, Pro, and AI Pro read/write **one** local configuration store. There is no parallel “AI-only” config. Panel credential changes synced into local store update **Panel Login Info** across modes.

**Role vocabulary (use consistently)**

| Role | Meaning |
|------|---------|
| Central | Main VPS: WireGuard + 3X-UI panel after Full Deploy |
| Exit | Egress location server (slots **1–6** max) |
| Tunnel hop | Pro chain server between central and exits |
| Node | Remote 3X-UI node registered on central panel |
| Mesh | Inter-server link management (WireGuard / GRE / Reverse Tunnel Stealth-WSS) |

**Configure Panel ≠ install panel on central.** `configure_panel` repairs Inbound/Outbound/SOCKS routing for an **existing** exit or node. Central panel install uses **Full Deploy**.

---

## 4. Modes & licensing gates

Modes: `basic` | `pro` | `ai_pro` (AI Assistant Pro).

### 4.1 Basic (free without license)

UI copy: *Initial Server Setup / Connect SSH / Full Deploy in Basic mode are free.*

| Op | License |
|----|---------|
| Setup Central (`setup_central`) | Free (wizard; no registration gate in ops builder) |
| Connect SSH | Free in Basic |
| Full Deploy | Free in Basic |
| Exit Server 1 / Exit Server 2 | **Basic license** required |
| Configure Panel and other gated tools | **Basic** (or higher) as applicable |
| Pro-only features | Locked |

### 4.2 Pro

Unlocked with Pro (or AI Pro) license. Includes Pro operator features such as:

- Add Tunnel Server (chain hops)
- Add Exit Servers (slots up to **6**)
- Add Node Servers
- Add Domain (DNS manager overlay)
- CDN (Arvan / Cloudflare / Other) + Mesh Servers
- Add Telegram Bot (Mirza)
- Move Central Server
- Factory Reset (Settings → Maintenance; Pro UI)
- Delete flows for exits/nodes/tunnels / reset all / delete history

**Pro alone does NOT grant AI Assistant Pro.**

### 4.3 AI Pro (`ai_pro`)

- Requires **separate AI Pro unlock** (`BFXA` / claim / TX path) **plus AI quota** (`BFXQ` recharges; quota is separate catalog item).
- Same Pro-class operations available via **AI chat + task buttons**, plus AI-only tasks (see §6.3).
- Switching to AI Pro mode without unlock shows lock messaging pointing to Registration.

### 4.4 Activation code families

| Prefix | Purpose |
|--------|---------|
| `BFXB` | Basic full activation (device-bound) |
| `BFXP` | Pro full activation |
| `BFXA` | AI Assistant Pro full activation |
| `BFXQ` | AI quota recharge (not a mode unlock by itself) |
| `*-CLM-*` (e.g. `BFXB-CLM-…`) | Website **claim** codes — bind Device ID on first unlock |

Also supported: TX/payment + password flows; **Reactivation** via hub for prior device activation.

**Device ID:** shown on Registration; used for AI status checks and support.

**Hubs for license/reactivation/updates:** `blackfoxupdate.ir` + `foxnext.net`.

---

## 5. Pricing

### 5.1 Hardcoded fallback amounts (code `internal/auth/tiers.go`)

Typical fallback when live pricing unavailable: **Basic 19 / Pro 33 / AI Pro 40 USDT** (historically tied to ~18‑month messaging in product).

### 5.2 Live catalog (`host-samples/license-access.json`, currency USDT)

Host-editable; Windows, PAS, and website read it — **no rebuild required** for price edits.

- Duration months: **12, 15, 18, 21, 24, 27, 30**
- Multi-device: max **3** devices; discounts device2 **20%**, device3 **30%** (device1 full price; total = sum)

| Mode | 12 | 15 | 18 | 21 | 24 | 27 | 30 |
|------|----|----|----|----|----|----|-----|
| basic | 13.5 | 16.5 | **19.0** | 22.0 | 24.5 | 27.5 | 30.0 |
| pro | 20.0 | 24.5 | **28.5** | **33.0** | 37.0 | 41.0 | 45.0 |
| ai_pro | 24.5 | 30.0 | **35.0** | **40.0** | 45.0 | 50.0 | 55.0 |

**AI quota** (separate from license; `includes_ai_quota` on ai_pro plan; time expiry priority): 12→2.0 … 18→**3.0** … 30→5.0 USDT.

**Chatbot rule:** Prefer live hub/catalog prices when available; if citing fallbacks, say they are fallbacks. Do not invent other currencies or plans.

---

## 6. Features map

### 6.1 Core operations (Operations tab)

| Op ID / UI | Mode gate (summary) | Purpose |
|------------|---------------------|---------|
| `setup_central` | Free Basic | Save central SSH / initial server setup wizard |
| `connect_ssh` | Free Basic | Connect to registered central |
| `full_deploy` | Free Basic | Install WG + 3X-UI on central; choose install source |
| `add_tunnel_server` | Pro | Tunnel hop in chain |
| Exit 1 / Exit 2 (Basic) or `add_exit_servers` (Pro) | Basic license / Pro | Location egress; max **6** slots |
| `add_node` | Pro | Install remote panel, exchange tokens, register on central |
| `configure_panel` | Licensed | Fix routing for existing exit/node — **not** central install |
| `add_domain` | Pro | Opens DNS / Domains overlay |
| `proxy_settings` | Available tool | Program proxy for hub/SSH/panel fallback |
| `test_client` | Tool | Test client / WireGuard client path |
| CDN Arvan / Cloudflare / Other | Pro section | Save CDN provider configs |
| `mesh_servers` | Pro | Mesh Servers overlay / link repair |
| `add_bot_telegram` | Pro | Mirza Telegram bot install/move |
| `move_central_server` | Pro | Migrate central |
| Deletes | Pro-capable flows | History / exits&nodes / tunnels / reset all servers |

### 6.2 Full Deploy — 3X-UI install sources

User chooses one:

1. **Install from Sanaei GitHub**
2. **Install from BlackFox Hub** (hub package bases in runtime-config)
3. **Install from Local PC** (local cache)

Then WireGuard + panel are deployed on the **central** server.

`NEED_MORE_REVIEW`: Exact Linux script step list, default panel port/path generation, and failure codes — not field-verified in this KB snapshot.

### 6.3 AI Pro–only tasks (also in AI task list)

| Task | Op ID | Behavior summary |
|------|-------|------------------|
| BlackFox MCP | `blackfox_mcp` | Cursor MCP stdio connection helper |
| Add OutBounds | `add_outbounds` | Paste v2ray/xray outbound JSON; panel outbound + matching inbound/client; hard max **10** via server-side ledger |
| Diagnose & Repair | `diagnose_repair` | Checklist: resources, Iran filter/ping, WG/mesh links, DNS/CDN; prefer `run_on_server` recipes; confirm before mutate |
| Link Test | `link_test` | Assess links; recommend WireGuard (default), GRE fallback, or Reverse Tunnel (Stealth-WSS); finish in Mesh when needed |

### 6.4 Link types (product names only)

- **WireGuard** (default)
- **GRE** fallback
- **Reverse Tunnel (Stealth-WSS)** — anti-filter protected reverse path; may mention PROXY Protocol / real client IP when reverse is chosen  
Do **not** cite third-party project names in user-facing text.

### 6.5 Network & status UX

- Long ops should show busy/status feedback with spinner; prefer duration display when touching status UX.
- Internet ops: Direct first, then Program Proxy.

---

## 7. Pages / tabs / overlays

### 7.1 Startup sequence

1. **Splash** (uses **persisted language** so relaunch matches saved lang)
2. **Language** picker on **first run**
3. **Mode picker** (Basic / Pro / AI Pro art + SELECT)
4. **Main** window

### 7.2 Main tabs

| Tab key | EN label | Role |
|---------|----------|------|
| `tab.operations` | Operations | Primary action dashboard + terminal/status |
| `tab.diagnostics` | Check System | Diagnostic Center — read-only health checks; export log |
| `tab.view` | View | Switch mode; topology map (central / tunnels / exits) |
| `tab.settings` | Settings | Language, Updates, Packages, Factory Reset (Pro) |
| `tab.registration` | Registration | Activate / claim / Device ID / reactivation |
| `tab.contact` | Contact | Website, email, Telegram links from runtime-config |

### 7.3 Overlays / sections

- **Add Domain** / DNS Manager (Cloudflare & ArvanCloud auth; record management)
- **Mesh Servers** (Pro mesh / link-type workflows)

`NEED_MORE_REVIEW`: Complete field-by-field forms for every wizard (Setup Central pages, Add Node, Move Central, CDN Other providers like Bunny/KeyCDN/Gcore keys in i18n) — treat detailed field lists as incomplete unless confirmed live.

---

## 8. Settings

| Section | Contents |
|---------|----------|
| Language | Select UI language → Apply → rebuild tabs; persists for splash |
| Tools | **Updates** (remote update section) · **Packages** (3X-UI package / install-source modal) |
| Maintenance (Pro UI only) | **Factory Reset** — destructive remote wipe toward “fresh VPS”; credentials entered for that op are not stored; unsupported OS fails explicitly |

Factory Reset confirm meaning: removes data, services, VPN packages, tunnels, firewall rules, created users, custom settings — irreversible.

---

## 9. Beginner guide (happy path)

1. Install Windows Setup from FoxNext downloads (or hub).
2. Splash → choose language (first run) → pick **Basic**.
3. **Operations → Central Server Setup**: enter VPS IP, SSH user, password or key, port.
4. **Connect SSH** — confirm connectivity (free in Basic).
5. **Full Deploy** — pick 3X-UI source (Sanaei GitHub / BlackFox Hub / Local PC); wait for WG + panel.
6. Use **Panel Login Info** for URL/user/password; **Test Client** for a client/WG check.
7. To add exits: activate **Basic** (`BFXB` / claim / payment) then Exit 1 / Exit 2.
8. For tunnels, nodes, DNS/CDN, mesh, Mirza bot: activate **Pro** and switch mode in **View** (or start in Pro after unlock).
9. For chat automation: activate **AI Pro** + ensure **quota**; use task buttons; paste credentials in chat.
10. Buy VPS only via **FoxNext.net → Partners / همکاران** (AI must not invent hosters).

**Central panel without exit:** Full Deploy → Panel Info → Test Client. Do **not** force Configure Panel or require an exit.

---

## 10. Advanced guide

1. **Pro chain:** Central → optional tunnel hops → exits (slots 1–6); topology on View.
2. **Nodes:** Add Node installs remote 3X-UI, exchanges API tokens, registers on central; configure test client. Do not show node panel login unless user asks (AI Pro rule).
3. **Configure Panel:** only after exit/node exists — repairs inbound/outbound/SOCKS.
4. **DNS:** Add Domain with Cloudflare token or ArvanCloud API key + email/machine user as required; validate/point records in DNS Manager.
5. **CDN:** Arvan Cloud CDN / Cloudflare CDN / Other CDN forms; mesh can use protected link CDN scopes (`NEED_MORE_REVIEW` for each Other-provider API).
6. **Mesh / Link Test:** assess UDP/WG; fall back GRE; if filtered, Reverse Tunnel Stealth-WSS; change link type via Mesh / add flows.
7. **Mirza bot:** Add Telegram Bot with server + bot token; install/move via installer action.
8. **Move Central:** migrate with source/dest credentials; rebuild ops after success.
9. **Add OutBounds (AI):** paste outbound JSON; max 10 ledger-enforced.
10. **Diagnose & Repair (AI):** resources → filter/ping → WG/mesh → DNS/CDN → safe repairs with confirm.
11. **BlackFox MCP:** connect Cursor MCP stdio for agent tooling (`NEED_MORE_REVIEW`: exact user setup steps).
12. **Deletes:** Delete History (local only); Delete Exit/Node (wizard all/one); Delete Tunnels (higher seq resets for chain integrity); DELETE — Reset All Servers (remote WG+panel wipe, SSH creds kept).
13. **Proxy:** when Direct fails to hubs/SSH/panel, configure Program Proxy.
14. **Multi-device licenses:** pricing discounts up to 3 devices per catalog rules.
15. **Reactivation:** Registration → hub lookup by Device ID after reinstall/OS change.

---

## 11. Cross-feature relationships

| If you… | Then also… |
|---------|------------|
| Change panel port/path/user/password | Local store syncs → Panel Info updates in all modes |
| Full Deploy succeeds | Op badges for install/panel paths update; topology may appear when panel/client ready |
| Add Exit / Tunnel / Node | Mesh/Link Test / Configure Panel / deletes become relevant |
| Delete a tunnel hop | Higher-sequence hops must reset; exits using those hops must be removed first |
| Unlock Pro | AI still locked until BFXA + quota |
| Exhaust AI quota | Recharge via BFXQ / AI quota catalog — license alone may not refill usage |
| Set Program Proxy | Hub fetch, SSH failover, panel API benefit on Direct failure |
| Switch mode in View | Same servers/credentials; different buttons/AI shell |
| Factory Reset | Independent destructive remote op — not the same as Delete History |

---

## 12. Common problems & fixes

| Symptom | Likely cause | Action |
|---------|--------------|--------|
| Registration required on Exit | No Basic/Pro license | Activate on Registration |
| Pro features grey / dialog | No Pro unlock | `BFXP`/`BFXA` or payment |
| AI chat refused / locked | Not AI Pro or no quota | Unlock AI Pro + recharge |
| Hub/update unreachable | Network/filter | Enable Program Proxy; hubs try primary then secondary |
| SSH connect fails | Creds/port/firewall | Re-check Setup Central; proxy; seller IP change |
| Full Deploy hang/fail | Source/network/OS | Retry source; check terminal logs; Diagnose path |
| Panel login wrong | Local stale vs server changed | `panel_info_refresh` / reconnect sync |
| Configure Panel errors | No exit/node | Add exit/node first; or use Full Deploy for central |
| Node token / central panel errors | Panel not ready | Finish Full Deploy; verify panel_info |
| Topology empty | No deploy/client yet | Complete Full Deploy or deployed links + client |
| Mesh/WG fails Iran path | Filter | Link Test → GRE or Reverse Tunnel Stealth-WSS |
| DNS not resolving | Wrong records/CDN origin | DNS Manager + diag_dns_cdn style checks |
| Delete tunnel blocked | Exit still depends on hop | Delete dependent exits first |
| Version confusion | Hub vs local drift | Do not invent versions; point to About/hub if product UI shows them |

`NEED_MORE_REVIEW`: Exact user-visible error strings and Linux stderr mappings.

---

## 13. Errors & unlock messages (verified themes)

- Registration / need activate dialogs when license missing.
- AI Pro requires `BFXA`; Pro requires `BFXP` or `BFXA`.
- Reactivation: not found / expired / success / success with code loaded from server.
- Pricing fetch failure may tell user to contact support (e.g. `@HiBlackFoxVpn`) when live price unavailable.
- Factory Reset: invalid port, auth required, unsupported OS, failed (see logs).
- Delete wizards: no servers / no nodes messages when empty.
- Add OutBounds: max 10 enforced server-side.

Do not invent HTTP status codes or SSH errno lists here.

---

## 14. AI chatbot consumer rules (mandatory)

1. Answer **only** Black Fox installer / VPN-server-ops related questions; refuse unrelated topics briefly and steer back.
2. **Match user / UI language.**
3. **Never invent or discuss version numbers** (app, panel, bot, Xray, builds).
4. Identity: you are **BlackFox AI** only.
5. Where to buy VPS: **only** FoxNext.net → **Partners / همکاران** — no other hosters/prices/links.
6. Encourage license when user hits gated features.
7. Prefer built-in actions over inventing shell; confirm before mutating `run_on_server`.
8. Use APP STATE as ground truth for servers already saved.
9. Never claim deploy/SSH/mesh finished unless app state/chat confirms.
10. Passwords may be shown when state/user supplied them — never invent credentials.
11. Android variant of prompt adds: servers bought via Partners can be used as central, exit, or node inside the app.

---

## 15. FAQ starter (40+)

Format: **Q** → *Short* → Full.

### Product & identity

**Q1. What is Black Fox Vpn?**  
*Short:* Windows/Android toolkit that automates 3X-UI + WireGuard on your VPS.  
Full: It is an installer/operations app (Fyne on Windows, Flutter on Android companion). It connects over SSH to Linux VPS hosts and deploys WireGuard and the Sanaei/3X-UI panel, plus Pro mesh/DNS/CDN/bot workflows. It is not a consumer one-click VPN client for browsing only.

**Q2. Is this a VPN client like consumer apps?**  
*Short:* No — it builds and manages your server infrastructure.  
Full: End users still need clients/subscriptions from the panel you deploy. Black Fox automates the server side (central, exits, nodes, tunnels).

**Q3. What panel does it install?**  
*Short:* Sanaei **3X-UI**.  
Full: Full Deploy installs WireGuard and 3X-UI (Sanaei). Reference project: MHSanaei/3x-ui. Do not invent panel version numbers in chat.

**Q4. Windows and Android — same product?**  
*Short:* Same brand family; Windows is the full installer; Android is companion/AI-capable app.  
Full: Windows AppVersion 3.0.0 build 211 in current source; hub samples may list Windows 208 / Android 207 — treat drift as NEED_MORE_REVIEW; never invent builds in user chat.

**Q5. Who is BlackFox AI?**  
*Short:* In-app AI Assistant Pro helper.  
Full: Named BlackFox AI. Does not discuss model/app versions. Helps with installer workflows and can queue built-in actions.

### Modes & license

**Q6. What modes exist?**  
*Short:* Basic, Pro, AI Pro.  
Full: `basic`, `pro`, `ai_pro`. Switch in View (and mode picker at startup). Shared local store across modes.

**Q7. What is free in Basic?**  
*Short:* Setup Central, Connect SSH, Full Deploy.  
Full: Exit servers and Configure Panel need a Basic (or higher) license. Pro features need Pro/AI Pro unlock.

**Q8. Does Pro include AI?**  
*Short:* No.  
Full: AI Assistant Pro needs separate `BFXA` unlock and AI quota (`BFXQ` / quota catalog). Pro unlock alone is insufficient.

**Q9. Code prefixes?**  
*Short:* BFXB Basic, BFXP Pro, BFXA AI Pro, BFXQ AI quota; CLM = claim.  
Full: Claim codes look like `BFXP-CLM-18-…` and bind Device ID on first unlock. Full codes are device-bound for months encoded in issuance.

**Q10. What is Device ID?**  
*Short:* Machine/license id for activation and support.  
Full: Shown on Registration; used for AI status checks, claim binding, reactivation lookups.

**Q11. How do I reactivate after Windows reinstall?**  
*Short:* Registration → Reactivation via hub.  
Full: Hubs blackfoxupdate.ir / foxnext.net. Outcomes: success, not found, expired, or success with code restored.

**Q12. How much does it cost?**  
*Short:* Live USDT prices from license-access; fallbacks 19/33/40.  
Full: See §5 tables. Example live 18‑mo: Basic 19, Pro 28.5, AI Pro 35; 21‑mo Pro 33 / AI Pro 40. Multi-device discounts apply. Prefer live catalog.

**Q13. Is AI quota included?**  
*Short:* AI Pro plan includes quota flag; recharges are separate.  
Full: Catalog marks ai_pro `includes_ai_quota`; `ai_quota` item is `separate_from_license` with its own month prices. Time expiry priority noted in catalog.

### Startup & UI

**Q14. Startup order?**  
*Short:* Splash → language (first run) → mode picker → main.  
Full: Persisted language applies on splash so relaunch is not stuck on default FA.

**Q15. Main tabs?**  
*Short:* Operations, Check System, View, Settings, Registration, Contact.  
Full: Overlays include Add Domain (DNS) and Mesh Servers.

**Q16. Where do I switch mode later?**  
*Short:* View tab.  
Full: View also shows topology after deploy/links/client readiness conditions.

### Deploy & servers

**Q17. Recommended first steps?**  
*Short:* Setup Central → Connect SSH → Full Deploy.  
Full: Then Panel Info / Test Client. License before exits.

**Q18. Full Deploy sources?**  
*Short:* Sanaei GitHub, BlackFox Hub, or Local PC.  
Full: Choice dialog before install; hub package URLs from runtime-config.

**Q19. Do I need an exit for panel on central?**  
*Short:* No.  
Full: Full Deploy + Panel Info + Test Client. Configure Panel is for existing exits/nodes only.

**Q20. What is Configure Panel?**  
*Short:* Repair routing on exit/node — not central install.  
Full: Fixes Inbound/Outbound/SOCKS for an existing exit or node.

**Q21. How many exits?**  
*Short:* Up to 6.  
Full: Basic UI emphasizes Exit 1 and Exit 2; Pro Add Exit Servers covers slots through 6 (`MaxExitServers = 6`).

**Q22. What is a tunnel server?**  
*Short:* Pro hop between central and exits.  
Full: Chain integrity matters when deleting: higher sequence hops reset; exits using hops must go first.

**Q23. What is Add Node?**  
*Short:* Remote 3X-UI registered on central.  
Full: Installs panel on remote VPS, exchanges API tokens, registers node, can configure test client. Hide node panel login unless asked.

**Q24. Mesh vs CDN?**  
*Short:* Mesh = server links; CDN = edge DNS/proxy providers.  
Full: CDN buttons: Arvan, Cloudflare, Other. Mesh is Pro overlay for link types including Stealth-WSS reverse.

**Q25. Link types?**  
*Short:* WireGuard, GRE, Reverse Tunnel Stealth-WSS.  
Full: Link Test recommends based on connectivity; finish changes in Mesh / add flows.

**Q26. Mirza bot?**  
*Short:* Add Telegram Bot (Pro).  
Full: Uses Mirza botmirzapanel concepts; provide server + bot token. Do not invent bot versions.

**Q27. Move Central?**  
*Short:* Pro migration of central role.  
Full: Collect source/dest; installer action `move_central_server`.

**Q28. Proxy Settings?**  
*Short:* Program Proxy when Direct fails.  
Full: Applies to SSH, hub HTTP, panel API failover pattern.

### AI Pro tasks

**Q29. What can AI do?**  
*Short:* Guide workflows and queue installer actions from chat.  
Full: Allowed actions include connect_ssh, full_deploy, add_*, configure_panel, mesh, bot, deletes, diagnose, run_on_server, open_section, etc. (see system prompt).

**Q30. Add OutBounds?**  
*Short:* Paste xray/v2ray outbound JSON; max 10.  
Full: Creates outbound + matching inbound/client; ledger enforces cap.

**Q31. Diagnose & Repair?**  
*Short:* Structured health + safe fixes.  
Full: Resources, Iran filter/ping, WG/mesh, DNS/CDN; confirm before mutating.

**Q32. Link Test?**  
*Short:* Pick best link method between servers.  
Full: Prefer WG; else GRE; else Reverse Tunnel Stealth-WSS.

**Q33. BlackFox MCP?**  
*Short:* Cursor MCP stdio integration task.  
Full: AI Pro op `blackfox_mcp`. Setup details NEED_MORE_REVIEW.

**Q34. Will AI run dangerous shell?**  
*Short:* No destructive recipes; confirm first.  
Full: Max short command lists; no rm -rf /, mass wipe, reboot, curl|sh, password resets in AI policy.

### Registration & purchase

**Q35. Where do I buy a VPS?**  
*Short:* FoxNext.net → Partners.  
Full: Only that path in AI answers. No competing hoster lists.

**Q36. Where do I buy a license?**  
*Short:* FoxNext / Activation flows; paste code in Registration.  
Full: Codes from website claim or PAS/payment; Device ID binding for claims.

**Q37. Contact support?**  
*Short:* foxnext.net / support@foxnext.net / Telegram support.  
Full: Runtime-config also lists channel, bot, group links — prefer live Contact tab values.

### Diagnostics & deletes

**Q38. Check System tab?**  
*Short:* Read-only Diagnostic Center.  
Full: SSH, WireGuard, panel, DNS, CDN, exits; export log for support.

**Q39. Delete History vs Reset All?**  
*Short:* History = local only; Reset All = remote wipe WG/panel.  
Full: History keeps language/mode/license; keeps remote unchanged. Reset All keeps SSH credentials but removes installs.

**Q40. Factory Reset?**  
*Short:* Pro Settings — wipe VPS toward fresh state.  
Full: Strong confirm; credentials not stored; unsupported OS fails.

**Q41. Why topology empty?**  
*Short:* Deploy/links/client not ready.  
Full: Appears after Full Deploy (panel ready) or when links deployed and a panel client exists.

**Q42. SSH worked yesterday, fails today?**  
*Short:* IP/password/firewall/proxy change.  
Full: Confirm seller IP; update Setup Central; try Program Proxy; Diagnose & Repair for filter clues.

**Q43. Panel opens but clients fail?**  
*Short:* Inbound/routing/exit path issue.  
Full: Test Client; Configure Panel on exit/node; Mesh/Link Test; check CDN/DNS if domain used.

**Q44. Can Basic and Pro share the same servers?**  
*Short:* Yes — one local store.  
Full: Mode only changes available buttons/AI; credentials persist.

**Q45. Multi-device discount?**  
*Short:* Up to 3 devices; 20%/30% off devices 2/3.  
Full: From license-access.json multi_device rules; totals are sums of discounted unit prices.

**Q46. What hubs does the app use?**  
*Short:* blackfoxupdate.ir then foxnext.net.  
Full: Updates, runtime-config, packages, license/AI APIs. Prefer Direct then Program Proxy.

**Q47. Local PC install source?**  
*Short:* Uses cached 3X-UI package on the PC.  
Full: Useful offline/restricted networks; configure via Packages / source dialog. Exact cache paths NEED_MORE_REVIEW.

**Q48. Does AI invent prices or versions?**  
*Short:* Must not.  
Full: Use catalog/hub facts; for versions, refuse numbers per system prompt.

**Q49. Android AI differences?**  
*Short:* Same persona; Android wording + Partners closing line.  
Full: Clarifies purchased Partners servers can be used as central/exit/node in the Android app.

**Q50. Config Builder APK?**  
*Short:* Separate Android tool (hub version 1.1.3 build 7).  
Full: Connection/Single/Bulk/List/Settings/Contact features per hub release notes — deep UI NEED_MORE_REVIEW relative to Windows installer.

---

## 16. RAG retrieval hints

**High-value keys:** `full_deploy`, `configure_panel`, `setup_central`, `BFXA`, `BFXQ`, `MaxExitServers`, `license-access`, `FoxNext.net Partners`, `Stealth-WSS`, `opstate`, `Direct→Program Proxy`, `shared store`, `claim CLM`.

**Disambiguation:**  
- “Install panel” → Full Deploy (central) vs Add Node (remote) vs Configure Panel (routing only).  
- “AI Pro” ≠ “Pro”.  
- “Delete History” ≠ “Factory Reset” ≠ “Reset All Servers”.

**Always escalate to NEED_MORE_REVIEW when asked for:** live form field lists not covered here; exact bash deployed on VPS; live production hub numbers if they diverge from this snapshot; unpaid third-party CDN API field matrices.

---

## 17. Document meta

| Field | Value |
|-------|-------|
| Product | Black Fox Vpn Installer (+ Android companion) |
| KB primary language | English |
| Fact cutoff basis | Repo sources cited above (buildinfo, license-access, version.json, auth/tiers, opstate, unlock, ops, settings, ai/prompt, runtime-config) |
| Explicit gaps | Marked `NEED_MORE_REVIEW` |
| Chatbot safety | No invented versions/prices/hosters; product-scope only |

*End of AI Knowledge Base.*