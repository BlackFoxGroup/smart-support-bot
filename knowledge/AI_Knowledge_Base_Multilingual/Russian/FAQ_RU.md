# Black Fox VPN — FAQ (русский)

> Для AI / Telegram Bot / поддержки. ID вопросов совпадают с EN.
> Ответы Q001–Q200 локализованы полностью (без английской обёртки).
> Точность: макс. 6 Exit; бесплатно в Basic = Setup Central + Connect SSH + Full Deploy; Pro ≠ AI Pro.


### Q001
**Question:** Что такое Black Fox VPN Installer?
**Answer:** Black Fox — Windows Installer, который по SSH автоматизирует WireGuard и панель 3X-UI (Sanaei) на вашем VPS для multi-location VPN. Это не потребительский VPN-клиент.
**Step by step solution:**
1. Скачайте Setup с foxnext.net.
2. Установите и выберите язык.
3. Сделайте: Choose Basic, Pro, or AI Assistant Pro on the View tab.
4. Сделайте: Save central SSH, Connect SSH, then Full Deploy.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q002
**Question:** Black Fox — это форк UI панели 3X-UI?
**Answer:** По текущему поведению Black Fox: No — it automates and manages the Sanaei / 3X-UI panel; it is not a panel UI fork. Black Fox installs and configures the real 3X-UI (Sanaei) panel on your central server and drives panel API tasks (inbounds, outbounds, nodes, clients). You still open the panel URL for advanced panel UI work when needed. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Complete Full Deploy.
2. Сделайте: Use Panel Login Info for URL/user/password.
3. Сделайте: Open the panel in a browser if you need the native 3X-UI UI.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q003
**Question:** Какие платформы поддерживает продукт?
**Answer:** По текущему поведению Black Fox: Windows Installer is the full ops app; Android has a companion app with chat/engine packaging differences. Primary product is the Windows desktop Installer (Setup and portable exe). Android builds exist (including a larger release APK that embeds the Go engine). Client WireGuard configs can be imported on Windows/Android/iOS WireGuard apps. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Use Windows for Full Deploy and mesh ops.
2. Сделайте: Use Android where you need mobile AI/chat or engine-backed features.
3. Сделайте: Import `.conf` into any WireGuard client for end-user VPN.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q004
**Question:** Где скачать официальный Installer?
**Answer:** По текущему поведению Black Fox: From foxnext.net (website download and update hosts). Official site is foxnext.net. Setup is typically `Black Fox Vpn-Installer-Setup.exe`. App updates also pull from foxnext.net / blackfoxupdate.ir style hosts configured in runtime. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Open http://foxnext.net/ (or /en/).
2. Сделайте: Use the download/setup page.
3. Сделайте: Prefer Setup.exe for first install.
4. Сделайте: For support, confirm you did not use an unofficial mirror.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q005
**Question:** Какие основные вкладки в приложении?
**Answer:** Вкладки: Operations, Check System, View, Settings, Registration, Contact. Add Domain и Mesh — оверлеи; отдельной вкладки Add нет.
**Step by step solution:**
1. Сделайте: Start on View to pick mode. 2. Use Registration to activate. 3. Use Operations for SSH/deploy. 4. Use Contact for support.
2. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q006
**Question:** Для чего вкладка View?
**Answer:** По текущему поведению Black Fox: Choose Basic / Pro / AI Pro and see topology when ready. View lets you pick the app mode and shows topology after Full Deploy (panel ready) or when links are deployed and a panel client exists. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Откройте вкладку View.
2. Сделайте: Select Basic, Pro, or AI Assistant Pro.
3. Сделайте: After deploy, open Topology when available.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q007
**Question:** Что такое режим Basic?
**Answer:** По текущему поведению Black Fox: Central SSH, WireGuard + Sanaei panel, up to 6 exits, inbound/outbound setup, client test. Basic covers central in Iran/China/Russia, panel on central, up to six exit servers, configure panel, client test. Keys like Initial Server Setup, Connect SSH, and Full Deploy in Basic are free operations (license still gates full paid feature set after free basics). Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Select Basic on View.
2. Сделайте: Save central (Iran/China/Russia).
3. Выполните Connect SSH.
4. Выполните Full Deploy.
5. Сделайте: Add Exit Server(s) as needed.
6. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q008
**Question:** Что такое режим Pro?
**Answer:** По текущему поведению Black Fox: All Basic plus multi-hop chain, tunnel relay, CDN, subscriptions, nodes (still max 6 exit slots). Pro unlocks multi-hop tunnel chain (Add Tunnel Servers), CDN, subscriptions, nodes, and other Pro ops. Exit capacity remains capped at 6 slots. Dialog text: “This feature requires Pro activation” when a Pro-only feature is locked. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Activate Pro on Registration / foxnext.net.
2. Сделайте: Switch View to Pro.
3. Сделайте: Use tunnel chain, CDN, subscription, and node buttons.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q009
**Question:** Что такое AI Assistant Pro?
**Answer:** По текущему поведению Black Fox: All Pro ops via smart chat, with simultaneous access to manual Pro. AI Assistant Pro (`ai_pro`) provides guided chat that can queue the same operations (Full Deploy, exits, mesh, CDN, diagnose, etc.) with confirmation. Manual Pro remains available. AI chat requires AI Pro unlock and AI quota credit on the hub. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Activate AI Assistant Pro.
2. Сделайте: Select AI Pro on View.
3. Сделайте: Use Tasks or free-form chat.
4. Сделайте: Confirm Yes/No when asked before execution.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q010
**Question:** Можно ли сменить режим после активации?
**Answer:** По текущему поведению Black Fox: Yes — View mode selection is separate from license unlock, but locked features still need the matching license. You can select Basic/Pro/AI Pro on View. Features still check unlock state (Basic Full / Pro / AI Pro). AI chat is blocked with “AI Assistant Pro activation required…” if not unlocked. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Откройте вкладку View.
2. Сделайте: Select the mode you want.
3. Сделайте: If a button says need activate / need Pro, open Registration.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q011
**Question:** Какие операции бесплатны в Basic?
**Answer:** Без License в Basic бесплатны только Setup Central, Connect SSH и Full Deploy.
**Step by step solution:**
1. Сделайте: Stay in Basic.
2. Сделайте: Configure central.
3. Выполните Connect SSH.
4. Сделайте: Run Full Deploy without paying for those three keys.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q012
**Question:** В Basic Central должен быть в определённых странах?
**Answer:** По текущему поведению Black Fox: Yes — Iran, China, or Russia. Dialog: “Basic mode: central server must be in Iran, China, or Russia.” Pro allows broader central placement (product Pro copy references worldwide/central flexibility vs Basic country rule). Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Choose a VPS in IR/CN/RU for Basic.
2. Сделайте: Save country correctly in the server form.
3. Сделайте: If rejected, use a Pro license or change location.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q013
**Question:** Сколько Exit Server можно в Basic?
**Answer:** По текущему поведению Black Fox: Up to 6 exit servers. Basic tooltip and mode description: up to 6 exit servers; Add Exit Server 2 covers slot 2 in Basic and slots 2–6 in Pro flows. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Full Deploy central.
2. Сделайте: Add Exit Server
3. Сделайте: 3. Add further exits via Add Exit Server 2 / slots up to 6.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q014
**Question:** Неограничены ли Exit в Pro?
**Answer:** Нет. Лимит Exit — 6 слотов (`MaxExitServers`).
**Step by step solution:**
1. Сделайте: Activate Pro.
2. Сделайте: Add exits as needed.
3. Сделайте: Configure Panel for selected exits/nodes.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q015
**Question:** Что такое Full Deploy?
**Answer:** Full Deploy — одношаговая установка WireGuard и панели 3X-UI на Central.
**Step by step solution:**
1. Сделайте: Save central credentials.
2. Сделайте: Connect SSH (OK).
3. Сделайте: Run Full Deploy.
4. Сделайте: Wait for terminal success.
5. Сделайте: Open Panel Login Info.
6. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q016
**Question:** Что сделать перед Full Deploy?
**Answer:** По текущему поведению Black Fox: Configure/save central server and verify SSH. Dialogs: “Configure central server first.” and Connect SSH to verify login. Without panel credentials after deploy, later ops say “Complete Full Deploy first.” Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Initial / Central Server Setup.
2. Выполните Connect SSH.
3. Сделайте: Fix auth errors if any.
4. Выполните Full Deploy.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q017
**Question:** Что такое Connect SSH?
**Answer:** По текущему поведению Black Fox: Test SSH login to the central server and verify connectivity. Validates username/password or key, host reachability, and stores trust state for host keys. Failures surface as SSH authentication / timeout / host key dialogs. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Save IP, port, user, password or PEM.
2. Сделайте: Click Connect SSH.
3. Сделайте: Accept host key only if you trust the VPS.
4. Сделайте: Proceed when status is OK.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q018
**Question:** Какие SSH-данные принимает приложение?
**Answer:** По текущему поведению Black Fox: Host/IP, port (usually 22), username (often root), password and/or private key (PEM). Server forms and Factory Reset accept password or private key. Invalid both key and password: “SSH authentication failed” with message that invalid credentials were not saved. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Prefer root or sudo-capable user.
2. Сделайте: Paste PEM if key auth.
3. Сделайте: Or password.
4. Сделайте: Connect SSH to validate.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q019
**Question:** Что такое Panel Login Info?
**Answer:** По текущему поведению Black Fox: Shows saved 3X-UI panel URL, username, and password. Shared across Basic / Pro / AI Pro after deploy. Use it to open the panel and copy credentials. Long values wrap; copy buttons available. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Finish Full Deploy.
2. Сделайте: Open Panel Login Info.
3. Сделайте: Copy URL/user/pass.
4. Сделайте: Log in via browser or continue in-app ops.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q020
**Question:** Что такое Configure Panel?
**Answer:** Configure Panel чинит inbound/outbound/SOCKS для существующего Exit/Node; это не установка панели на Central.
**Step by step solution:**
1. Сделайте: Have exits/nodes registered as needed.
2. Сделайте: Open Configure Panel.
3. Сделайте: Select targets and ports.
4. Сделайте: Apply and verify Test Client.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q021
**Question:** Что такое Test Client / WireGuard?
**Answer:** По текущему поведению Black Fox: Shows VLESS link, subscription URL, and WireGuard config for testing. After panel configuration, generate/test client links and `.conf` for import into WireGuard apps. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Configure Panel.
2. Сделайте: Open Test Client.
3. Сделайте: Copy VLESS/sub/WG.
4. Сделайте: Import `.conf` into WireGuard.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q022
**Question:** Что такое Add Exit Server?
**Answer:** По текущему поведению Black Fox: Deploy an exit location (WireGuard + SOCKS outbound) for egress. Exit servers carry traffic out. Slot 1 and additional slots (2–6 Basic, more in Pro). Requires central panel ready. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Full Deploy central.
2. Сделайте: Enter exit SSH details.
3. Сделайте: Run Add Exit Server.
4. Сделайте: Configure Panel to use the exit.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q023
**Question:** Что такое Add Tunnel Server?
**Answer:** По текущему поведению Black Fox: Pro chain hop relay between central and exits. Pro-only multi-hop: register tunnel hops; delete one hop also resets higher-sequence hops to keep the chain intact. Exits using those hops must be deleted first when removing tunnels. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Activate Pro.
2. Сделайте: Add Tunnel Server with hop sequence.
3. Сделайте: Link exits through the chain.
4. Сделайте: Deploy mesh/link type as guided.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q024
**Question:** Что такое Add Node?
**Answer:** По текущему поведению Black Fox: Register a node with the central 3X-UI panel. Nodes are panel nodes (not the same as exit egress). Needs central panel login; errors often cite stale panel path/token — re-run Full Deploy or Panel Login Info. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Ensure Full Deploy done.
2. Сделайте: Enter node SSH/details.
3. Сделайте: Add Node.
4. Сделайте: If login fails, refresh panel credentials.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q025
**Question:** Чем Exit отличается от Node?
**Answer:** По текущему поведению Black Fox: Exit = traffic egress VPS; Node = 3X-UI panel node registration. AI chat explicitly asks to confirm Exit vs Node when SSH details are ambiguous. Wrong choice mis-wires routing. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: For country egress use Exit.
2. Сделайте: For panel node scaling use Node.
3. Сделайте: Confirm in AI chat or wizard labels.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q026
**Question:** Что такое Add Domain?
**Answer:** По текущему поведению Black Fox: Connect Cloudflare or ArvanCloud and manage DNS from the app. DNS page supports Cloudflare (email + API token) and ArvanCloud (machine user + API key), import zones, create A records for central or bot webhook subdomain. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Open Add Domain / DNS.
2. Сделайте: Choose provider.
3. Сделайте: Connect & Import Zones.
4. Сделайте: Point A records to central/bot IP.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q027
**Question:** Что такое Configure CDN?
**Answer:** По текущему поведению Black Fox: Configure CDN for domain and panel route (Pro feature family). Monetized Add CDN capability; AI template collects provider, domain/zone, API token/key. Used with domain for panel access over CDN. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Activate Pro/access CDN unlock.
2. Сделайте: Have domain ready.
3. Сделайте: Configure CDN with provider details.
4. Сделайте: Verify panel via domain.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q028
**Question:** Что такое Add Subscription?
**Answer:** По текущему поведению Black Fox: Pro subscription setup for client subscription URLs. Feature `add_subscription` unlocks with Basic Full or Pro tiers per auth rules; used to publish subscription endpoints for clients. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Ensure license allows it.
2. Сделайте: Run Add Subscription after panel ready.
3. Сделайте: Share subscription URL from Test Client / panel.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q029
**Question:** Что такое Proxy Settings?
**Answer:** По текущему поведению Black Fox: Proxy for reaching the 3X-UI panel and the internet from restricted networks. SSH Proxy Settings with profiles: none, auto-detect, Iran profile, free country profile; SOCKS5 or HTTP. Save and Test Connection. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Open Proxy Settings.
2. Сделайте: Choose mode/type/host/port.
3. Сделайте: Test Connection.
4. Сделайте: Save.
5. Сделайте: Retry panel/AI/hub operations.
6. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q030
**Question:** Когда нужен Proxy?
**Answer:** По текущему поведению Black Fox: When Direct access to hub, panel, or SSH path fails on filtered networks. Product network pattern prefers Direct first, then program proxy. Iran profile vs free-country profile helps match local filtering. AI chat can guide proxy updates. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Try Direct.
2. Сделайте: If timeouts, open Proxy Settings.
3. Сделайте: Enable Iran or free profile as appropriate.
4. Сделайте: Retest.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q031
**Question:** Как активировать License?
**Answer:** Registration → скопируйте Device ID → вставьте код/claim и Activate (или TX-оплата на foxnext.net).
**Step by step solution:**
1. Откройте вкладку Registration.
2. Сделайте: Paste code or verify TX.
3. Сделайте: Wait for success.
4. Сделайте: Confirm Basic/Pro/AI status badges.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q032
**Question:** Что такое claim-код?
**Answer:** По текущему поведению Black Fox: Website-style code (`PREFIX-CLM-…`) with no Device ID until first unlock binds the PC. PAS help: claim codes match website Activation; Device ID binds on first use in the Windows app. Prefixes include BFXB (Basic), BFXP (Pro), BFXA (AI Pro), BFXQ (AI quota). Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Buy/generate claim code on foxnext.net / PAS.
2. Сделайте: Open app Registration.
3. Сделайте: Paste code once on the intended PC.
4. Сделайте: Do not share after binding.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q033
**Question:** Что такое machine-bound код?
**Answer:** По текущему поведению Black Fox: Code already tied to a Device ID / fingerprint for a specific PC. PAS can generate machine-bound AI Pro (and related) codes. Verify tool distinguishes claim vs machine-bound vs tier. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Copy Device ID from Registration.
2. Сделайте: Ask support/PAS for machine-bound code if needed.
3. Сделайте: Paste on that same PC only.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q034
**Question:** Что такое Reactivation?
**Answer:** По текущему поведению Black Fox: Restore this PC’s prior activation from the server without manually saving the code. Messages: checking previous activation; success; success with code loaded; not found; expired; failed (check internet). Does not invent a new purchase. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Open Registration on the same device.
2. Сделайте: Tap Reactivation.
3. Сделайте: If expired, renew purchase.
4. Сделайте: If not found, activate with code/TX.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q035
**Question:** Что такое Device ID / License ID?
**Answer:** По текущему поведению Black Fox: This PC’s license fingerprint for AI status checks and support. Registration page hint: Device ID is for AI status checks and support. Copy Device ID button available. Used when claiming binds, reactivation lookups, and AI quota checks. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Откройте вкладку Registration.
2. Скопируйте Device ID.
3. Сделайте: Send to support only when asked.
4. Сделайте: Keep consistent after OS reinstall unless hardware identity changes.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q036
**Question:** Почему My Code ещё недоступен?
**Answer:** По текущему поведению Black Fox: Activate once, or use Reactivation to load the code from the server. `reg.my_code_empty`: “Not available yet — activate once, or tap Reactivation to load from server.” Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Complete first activation.
2. Сделайте: Or tap Reactivation.
3. Сделайте: Then copy activation code if shown.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q037
**Question:** Какая платёжная сеть используется?
**Answer:** По текущему поведению Black Fox: USDT on BEP-20 (BSC). Registration tutorial: open wallet, select USDT BEP-20, send exact plan amount to the shown wallet, paste TX HASH / TX ID. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Use BEP-20 only (not TRC20/ERC20).
2. Сделайте: Send exact amount.
3. Сделайте: Wait for confirmation.
4. Сделайте: Paste TX and verify.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q038
**Question:** Сколько стоит Basic?
**Answer:** По текущему поведению Black Fox: Catalog anchors around 19 USDT for 18 months; duration pricing is host-editable. Default amount constant 19 USDT; `license-access.json` lists Basic prices by months (e.g. 12→13.5 … 18→19.0 … 30→30.0 USDT). Live pricing may come from hub — if missing, app asks contacting @HiBlackFoxVpn. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Check foxnext.net Activation for live price/months.
2. Сделайте: Pay exact amount BEP-20.
3. Сделайте: Activate in app.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q039
**Question:** Сколько стоит Pro?
**Answer:** По текущему поведению Black Fox: Catalog uses ~33 USDT at 21 months / ~28.5 at 18; anchor 45 at 30 months. Code default `AmountProFull = 33`. Host catalog: Pro 12→20 … 18→28.5, 21→33, 30→45 USDT. Prefer website/live hub pricing. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Confirm months on website.
2. Сделайте: Pay exact USDT BEP-20.
3. Сделайте: Activate Pro.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q040
**Question:** Сколько стоит AI Assistant Pro?
**Answer:** По текущему поведению Black Fox: Catalog ~35–40 USDT mid-duration; anchor 55 at 30 months; includes AI quota flag. Default `AmountAIProFull = 40`. Catalog ai_pro prices 12→24.5 … 18→35, 21→40, 30→55. `includes_ai_quota: true` for AI Pro mode. Не выдумывайте цены и версии; ориентируйтесь на UI.
**Step by step solution:**
1. Сделайте: Buy AI Pro on foxnext.net.
2. Сделайте: Activate in app.
3. Сделайте: Confirm AI quota active before chatting.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q041
**Question:** Что такое пополнение AI quota (BFXQ)?
**Answer:** Коды пополнения AI quota с префиксом `BFXQ` (часто claim вроде `BFXQ-CLM-…`) не меняют режим License. Каталог `ai_quota` отделён от лицензии. PAS может выдать claim пополнения; claim добавляет только квоту.
**Step by step solution:**
1. Сделайте: If quota exhausted, buy AI quota / get BFXQ code.
2. Сделайте: Paste in Registration unlock.
3. Сделайте: Recheck AI status.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q042
**Question:** На сколько выдаётся License?
**Answer:** Срок обычно 12–30 месяцев по каталогу хаба; если месяцы не указаны, часто применяется 18. Месяцы в `license-access.json`: 12,15,18,21,24,27,30. Истёкшая лицензия блокирует полный функционал.
**Step by step solution:**
1. Сделайте: Pick months at purchase.
2. Сделайте: Note expiry in Registration.
3. Сделайте: Renew before expiry for uninterrupted Pro/AI.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q043
**Question:** Можно ли одной покупкой закрыть несколько устройств?
**Answer:** Каталог поддерживает до 3 устройств со скидками (device2 ≈20%, device3 ≈30%). Каждый claim при первом Activate привязывается к Device ID — не используйте один claim на разных ПК.
**Step by step solution:**
1. Сделайте: Buy multi-device plan on website if offered.
2. Сделайте: Activate each PC with its assigned code.
3. Сделайте: Contact support if device transfer needed.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q044
**Question:** Что будет, если повторно использовать TX HASH?
**Answer:** Уже использованный TX отклоняется и локально, и на хабе (`tx_already_used` / `tx_already_claimed`). После claim повторный ввод TX обычно больше не показывает коды.
**Step by step solution:**
1. Сделайте: Do not reuse old TX.
2. Сделайте: If code already claimed, use Reactivation on bound PC.
3. При необходимости напишите @HiBlackFoxVpn с Device ID.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q045
**Question:** Что значит «claim already bound»?
**Answer:** Этот claim уже привязан к другому Device ID (`bound_other_device` / `claim_bound`). Тем же claim нельзя открыть второй несвязанный ПК.
**Step by step solution:**
1. Сделайте: Use the original PC + Reactivation.
2. Сделайте: Or purchase another device seat.
3. Сделайте: Support can help with Device ID evidence.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q046
**Question:** Invalid activation code — что делать?
**Answer:** «Invalid activation code» обычно из‑за опечатки, неверного префикса тарифа, обрезанной вставки или мусорного кода. Для machine-bound нужен тот же Device ID.
**Step by step solution:**
1. Сделайте: Copy code again carefully.
2. Сделайте: Confirm BFXB/BFXP/BFXA/BFXQ prefix.
3. Сделайте: Use correct PC.
4. Сделайте: Ask support to inspect code.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q047
**Question:** TX not found / pending / wrong amount?
**Answer:** Дождитесь подтверждения BEP-20; сумма и адрес получателя должны совпадать со страницей. Ошибки: TX не найден, failed, неверный получатель, мало суммы, не USDT BEP-20, pending.
**Step by step solution:**
1. Сделайте: Confirm BSC explorer shows success.
2. Сделайте: Exact USDT amount.
3. Сделайте: Correct wallet address.
4. Сделайте: Retry verify.
5. Сделайте: Contact support with TX if stuck.
6. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q048
**Question:** Что значит «Please activate via Registration tab first»?
**Answer:** Функция закрыта лицензией (`dialog.need_activate` / Limited Access). В Basic без лицензии свободны только Setup Central, Connect SSH и Full Deploy.
**Step by step solution:**
1. Откройте вкладку Registration.
2. Сделайте: Activate Basic/Pro/AI.
3. Сделайте: Retry the operation.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q049
**Question:** Что значит «This feature requires Pro activation»?
**Answer:** Функция только для Pro при Basic/locked (`dialog.need_pro`). Туннельная цепочка и часть CDN/Subscription/Node требуют Pro или AI Pro.
**Step by step solution:**
1. Сделайте: Activate Pro or AI Pro.
2. Сделайте: Switch View to Pro/AI Pro.
3. Повторите попытку.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q050
**Question:** License истёк — можно ли ещё пользоваться приложением?
**Answer:** Полный функционал лицензии блокируется до продления. Виден бейдж «License expired». Reactivation может вернуть expired.
**Step by step solution:**
1. Сделайте: Note Device ID.
2. Сделайте: Purchase renewal on foxnext.net.
3. Сделайте: Activate or Reactivation.
4. Сделайте: Confirm badge cleared.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q051
**Question:** Где задаются live-цены сайта?
**Answer:** Живые цены в `license-access.json` на хабе; правка без rebuild приложения. Если хаб недоступен — fallback на константы в коде.
**Step by step solution:**
1. Сделайте: Prefer foxnext.net displayed price.
2. Сделайте: If app says pricing not received, contact @HiBlackFoxVpn.
3. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q052
**Question:** Что такое Initial / Central Server Setup?
**Answer:** Central Server Setup сохраняет SSH центрального сервера локально (IP, auth, страна, черновик). Нужно до Deploy.
**Step by step solution:**
1. Сделайте: Open setup central.
2. Сделайте: Fill IP/port/user/auth/country.
3. Сделайте: Save.
4. Выполните Connect SSH.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q053
**Question:** Почему нельзя менять Host/IP при сохранении?
**Answer:** Сообщение продукта: при сохранении нельзя менять Host/IP; для другого IP — новый server flow. Так защищают inventory и номер chain.
**Step by step solution:**
1. Сделайте: Keep IP on edit of credentials.
2. Сделайте: For a new VPS, use Add/new server flow.
3. Сделайте: Align chain number with Pro hops.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q054
**Question:** Full Deploy завершён, панель недоступна — что дальше?
**Answer:** Проверьте Panel Login Info (URL/path), Proxy, файрвол и повторите panel-операции. Нет credentials → Full Deploy. Ошибка логина ноды часто из‑за устаревшего path/token.
**Step by step solution:**
1. Сделайте: Open Panel Login Info.
2. Сделайте: Try URL in browser.
3. Сделайте: Enable Proxy if filtered.
4. Сделайте: Re-run Full Deploy / install 3X-UI.
5. Сделайте: Run Diagnostic Center.
6. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q055
**Question:** Что такое отдельная установка WireGuard / 3X-UI?
**Answer:** Можно поставить только WireGuard или только панель Sanaei на Central — полезно при частичном Full Deploy. Settings → Check Update 3X-UI кэширует пакет.
**Step by step solution:**
1. Сделайте: Confirm SSH OK.
2. Сделайте: Run the needed install button.
3. Сделайте: Verify Panel Login Info.
4. Сделайте: Continue Configure Panel.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q056
**Question:** Что такое Diagnostic Center?
**Answer:** Diagnostic Center — только чтение здоровья SSH, WireGuard, панели, DNS, CDN и Exit. Смотрите OK/Warning/Error и экспортируйте для поддержки.
**Step by step solution:**
1. Сделайте: Open Check System.
2. Сделайте: Run Checks.
3. Сделайте: Fix reported items.
4. Сделайте: Export logs if contacting support.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q057
**Question:** Что такое Link Test?
**Answer:** Link Test измеряет связность и рекомендует WireGuard, GRE или Reverse Tunnel (Stealth-WSS). Применение — через Mesh или тип линка в Add Server.
**Step by step solution:**
1. Сделайте: Ensure servers registered.
2. Сделайте: Run Link Test (ops/AI).
3. Сделайте: Apply recommended link type.
4. Сделайте: Redeploy mesh agents if needed.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q058
**Question:** Что такое GRE fallback?
**Answer:** Если WireGuard падает, приложение предлагает GRE. Порядок failover mesh: WireGuard → GRE → Reverse Tunnel (Stealth-WSS) → backups.
**Step by step solution:**
1. Сделайте: When prompted, choose Yes for GRE if WG blocked.
2. Сделайте: Or set link type explicitly.
3. Сделайте: Verify with Link Test / mesh status.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q059
**Question:** Что такое Reverse Tunnel (Stealth-WSS)?
**Answer:** Защищённый reverse-туннель в стеке линков/mesh под именем Reverse Tunnel (Stealth-WSS). Когда прямые WG/GRE плохи; мониторит Link Monitor Agent.
**Step by step solution:**
1. Сделайте: Prefer after Link Test recommends it.
2. Сделайте: Deploy via Mesh / link type.
3. Сделайте: Keep agents running.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q060
**Question:** Что такое Mesh / Link Monitor Agent?
**Answer:** Постоянные агенты на Central/Tunnel/Exit/Node для здоровья пути и failover. Мастер Mesh ставит их; инструменты качаются с GitHub на каждый VPS при установке.
**Step by step solution:**
1. Сделайте: Register hosts.
2. Сделайте: Open Mesh / CDN & Mesh section.
3. Сделайте: Install agents.
4. Сделайте: Refresh Status (installed/running).
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q061
**Question:** Нужно ли держать Windows-приложение открытым для mesh-агентов?
**Answer:** Нет — агенты продолжают работать на серверах при закрытом Windows-приложении. Приложение нужно для установки/статуса/ремонта.
**Step by step solution:**
1. Сделайте: Deploy agents once.
2. Сделайте: Close app if desired.
3. Сделайте: Refresh Status later to verify.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q062
**Question:** Mesh-агенты missing/stopped — что делать?
**Answer:** Снова Deploy mesh и Refresh Status. Метки: installed/missing, Running/Stopped/unknown. Итог: «Mesh agents installed: X ok, Y failed».
**Step by step solution:**
1. Сделайте: Refresh Status.
2. Сделайте: Re-run mesh install on failed hosts.
3. Сделайте: Check SSH to those hosts.
4. Сделайте: Re-test links.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q063
**Question:** Что такое Mirza Bot?
**Answer:** Мастер Telegram-бота: ставит Mirza на выбранный хост и подставляет credentials панели. Варианты: Install Mirza, другой бот, Move. Нужны bot token и admin.
**Step by step solution:**
1. Сделайте: Have panel credentials.
2. Сделайте: Open Add Telegram Bot / Install Mirza.
3. Сделайте: Enter token/admin.
4. Сделайте: Install or update with backup.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q064
**Question:** Можно ли перенести Mirza на другой сервер?
**Answer:** Да — в chooser есть Move existing bot. Перед Update/Move рекомендуется backup.
**Step by step solution:**
1. Сделайте: Backup Mirza.
2. Сделайте: Choose move.
3. Сделайте: Enter destination SSH.
4. Сделайте: Verify webhook/DNS if used.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q065
**Question:** Какие языки поддерживает приложение?
**Answer:** Много языков UI: английский, фарси, русский, арабский, немецкий, французский, хинди, турецкий и др. Старт + Settings → Language. Персидский — RTL.
**Step by step solution:**
1. Сделайте: Settings → Language.
2. Сделайте: Apply.
3. Сделайте: Restart UI path if a tab looks stale. NEED_MORE_REVIEW for exact full language list beyond en.go keys if extras load dynamically.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q066
**Question:** Чем Setup.exe отличается от Portable exe?
**Answer:** Setup ставится в LocalAppData\Programs; Portable с `portable.txt` хранит данные рядом с exe. Клиентам обычно лучше Setup.exe.
**Step by step solution:**
1. Сделайте: Prefer Setup for normal users.
2. Сделайте: Use portable when you must avoid installer.
3. Сделайте: Do not mix data folders casually.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q067
**Question:** Что делает Delete History?
**Answer:** Чистит локальную историю (SSH, логи, deploy-статус, локальный CDN…) без изменения удалённых серверов; язык, режим и лицензия остаются.
**Step by step solution:**
1. Сделайте: Confirm you have remote access elsewhere.
2. Сделайте: Run Delete History.
3. Сделайте: Re-enter servers to continue ops.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q068
**Question:** Что делает Delete Exit Servers & Node?
**Answer:** С Exit снимает WireGuard/microsocks/файрвол и чистит связанные туннели на Central; SSH сохраняет. Можно все или один; Node по возможности unregister с панели.
**Step by step solution:**
1. Сделайте: Open delete wizard.
2. Сделайте: Choose Exit or Node.
3. Сделайте: All or one.
4. Сделайте: Confirm warning.
5. Сделайте: Re-add if needed.
6. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q069
**Question:** Что делает Delete Tunnel Servers?
**Answer:** Снимает hop’ы Pro-цепочки; удаление одного hop может сбросить старшие номера. Exit, которые ещё используют hop, нужно удалить сначала.
**Step by step solution:**
1. Сделайте: Delete dependent exits first.
2. Сделайте: Delete tunnels (all/one).
3. Сделайте: Rebuild chain if required.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q070
**Question:** Что делает DELETE — Reset All Servers?
**Answer:** Снимает WireGuard и панель со всех настроенных серверов и чистит локальные deploy-данные; SSH оставляет. Это не Factory Reset ОС.
**Step by step solution:**
1. Сделайте: Read confirm body carefully.
2. Сделайте: Confirm.
3. Сделайте: Wait for completion.
4. Сделайте: Full Deploy again to rebuild.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q071
**Question:** Что такое Factory Reset Server?
**Answer:** Разрушительный remote-сброс к «свежему» VPS; пароль этой операции не хранится. Цель — данные, сервисы, VPN-пакеты, туннели, файрвол, пользователи. Неподдерживаемая ОС падает.
**Step by step solution:**
1. Сделайте: Settings maintenance / Factory Reset.
2. Сделайте: Enter IP/user/password or PEM.
3. Сделайте: Confirm warning.
4. Сделайте: Only on disposable VPS.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q072
**Question:** Удаляет ли Delete History лицензию?
**Answer:** Нет — язык, режим и активация лицензии сохраняются. Но переустановка Windows может сменить Device ID → Reactivation.
**Step by step solution:**
1. Сделайте: Delete History if cleaning local inventory.
2. Сделайте: License should remain.
3. Сделайте: If license missing after Windows reinstall, Reactivation.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q073
**Question:** Как работают обновления приложения?
**Answer:** Settings → Update BlackFox & Wallet Address; при force старая версия блокируется — ставьте новый Setup с хаба/официального сайта.
**Step by step solution:**
1. Сделайте: When prompted, download latest Setup.
2. Сделайте: Install over.
3. Сделайте: Reopen app.
4. Сделайте: Reactivation if needed.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q074
**Question:** Что такое Check Update 3X-UI?
**Answer:** Качает свежий пакет панели Sanaei в локальный кэш для будущих установок; сам по себе живую панель не обновляет без install/update ops.
**Step by step solution:**
1. Сделайте: Settings → packages.
2. Сделайте: Download if newer.
3. Сделайте: Next panel install uses cache.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q075
**Question:** Чем Android отличается от Windows?
**Answer:** Windows — полная ops-поверхность Installer; Android — компаньон с иной упаковкой/движком и общей AI-персоной. Для Full Deploy/Mesh обычно Windows.
**Step by step solution:**
1. Сделайте: Use Windows for Full Deploy/mesh.
2. Сделайте: Install full Android APK for engine features.
3. Сделайте: Same foxnext.net licenses conceptually via Device ID rules on each platform. NEED_MORE_REVIEW for exact Android license parity edge cases.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q076
**Question:** Как связаться с поддержкой?
**Answer:** Telegram `@HiBlackFoxVpn`, сайт foxnext.net, email support@foxnext.net, канал `@BlackFoxVPN`. Смотрите живые значения на вкладке Contact.
**Step by step solution:**
1. Сделайте: Open Contact tab or t.me.
2. Сделайте: Send Device ID + short problem + screenshots/logs.
3. Сделайте: Do not send passwords in public groups.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q077
**Question:** Что указать в сообщении поддержке?
**Answer:** Device ID, режим приложения, имя операции, фрагмент terminal, тип TX/кода (не светите полный секрет в публичном чате). Полезен Diagnostic export.
**Step by step solution:**
1. Скопируйте Device ID.
2. Сделайте: Note version from Settings/update.
3. Сделайте: Attach Diagnostic summary.
4. Сделайте: Message @HiBlackFoxVpn.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q078
**Question:** Что такое BlackFox MCP?
**Answer:** Локальный MCP-мост: внешние AI-приложения используют инструменты Black Fox, пока приложение открыто. Activate MCP, скопируйте mcp.json в настройки клиента.
**Step by step solution:**
1. Сделайте: Open BlackFox MCP.
2. Сделайте: Activate.
3. Сделайте: Copy mcp.json.
4. Сделайте: Configure external AI.
5. Сделайте: Keep Installer running.
6. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q079
**Question:** AI пишет, что нужна активация AI Assistant Pro
**Answer:** Нужно разблокировать AI Pro в Registration (`view.ai_pro_locked`). Одного Basic/Pro для AI-чата недостаточно.
**Step by step solution:**
1. Сделайте: Buy/activate AI Pro.
2. Сделайте: Reselect AI Pro mode.
3. Сделайте: Retry chat.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q080
**Question:** AI quota исчерпан — что делать?
**Answer:** Квота исчерпана; пополните BFXQ или напишите в поддержку. Возможны `ai.quota.exhausted` / expired / not_found / disabled.
**Step by step solution:**
1. Скопируйте Device ID.
2. Сделайте: Buy AI quota (BFXQ) or message @HiBlackFoxVpn.
3. Сделайте: Activate recharge code.
4. Сделайте: Retry chat.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q081
**Question:** Какие лимиты вложений в AI-чате?
**Answer:** До 3 изображений и 5 текстовых файлов на сообщение. Лишнее отклоняется (`too_many_images` / `too_many_text_files`).
**Step by step solution:**
1. Сделайте: Reduce attachments.
2. Сделайте: Resend.
3. Сделайте: Prefer text SSH details when possible.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q082
**Question:** AI выполняет операции без подтверждения?
**Answer:** Нет — сначала анализ, затем подтверждение Yes/No, потом выполнение. Одна постановка в очередь без подтверждения не запускает.
**Step by step solution:**
1. Сделайте: Review proposed action.
2. Сделайте: Reply Yes to run.
3. Сделайте: Wait for “process finished” or failure.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q083
**Question:** AI сказал, что операция началась — сколько ждать?
**Answer:** Дождитесь завершения в terminal/статусе; не закрывайте busy-окно без нужды. Статусы: wait / done / failed.
**Step by step solution:**
1. Сделайте: Keep window open.
2. Сделайте: Watch terminal.
3. Сделайте: On failure, read error and retry or Diagnose.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q084
**Question:** Может ли AI добавить кастомные v2ray outbounds?
**Answer:** Да в AI Pro — вставьте outbound JSON; максимум 10 AI-outbound на панели. Удаление в UI панели не сбрасывает счётчик AI. Невалидный JSON отклоняется.
**Step by step solution:**
1. Сделайте: Paste one outbound per request.
2. Сделайте: Confirm apply.
3. Сделайте: Contact support if need more than 10.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q085
**Question:** Какие inbound-порты по умолчанию в Configure Panel?
**Answer:** Подсказка Configure Panel обычно: 443 VLESS, 80 Trojan, 8080 WireGuard; фактические порты сверьте в Panel Login Info / client test.
**Step by step solution:**
1. Сделайте: Prefer defaults unless you know you need others.
2. Сделайте: Open firewall for those ports.
3. Сделайте: Test Client.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q086
**Question:** Не найдены credentials центральной панели?
**Answer:** Сначала завершите Full Deploy, чтобы сохранились URL/логин/пароль/токен панели. Многие операции зависят от этих credentials.
**Step by step solution:**
1. Выполните Full Deploy.
2. Сделайте: Panel Login Info non-empty.
3. Сделайте: Retry Add Node / proxy panel ops.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q087
**Question:** SSH host key изменился — это безопасно?
**Answer:** Часто после переустановки VPS; Accept только если доверяете серверу. Диалог предупреждает о возможном MITM; Accept очищает ключ и делает retry.
**Step by step solution:**
1. Сделайте: Confirm you reinstalled the VPS or changed keys.
2. Сделайте: Accept if trusted.
3. Сделайте: If unexpected, stop and check provider console/IP.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q088
**Question:** SSH authentication failed (ключ и пароль)?
**Answer:** И пароль, и ключ неверны/истекли; неверное не сохраняется. Заголовок: SSH authentication failed.
**Step by step solution:**
1. Сделайте: Reset password in provider panel if needed.
2. Сделайте: Fix PEM formatting.
3. Сделайте: Confirm user is allowed SSH.
4. Сделайте: Connect SSH again.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q089
**Question:** Linux password expired во время SSH?
**Answer:** Приложение показывает Change Linux Password (текущий/новый/подтверждение). Успех или mismatch/required/failed.
**Step by step solution:**
1. Сделайте: Enter current and new password.
2. Сделайте: Confirm match.
3. Сделайте: Retry Connect SSH.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q090
**Question:** Каковы причины SSH timeout?
**Answer:** Фильтр сети, неверный IP/порт, файрвол провайдера или нужен Proxy. Не обязательно неверный пароль (`log.ssh_timeout`).
**Step by step solution:**
1. Сделайте: Ping/port-check from another network if possible.
2. Сделайте: Verify IP/port.
3. Попробуйте Proxy Settings.
4. Сделайте: Check VPS running in provider UI.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q091
**Question:** Что такое topology view?
**Answer:** Карта топологии появляется при готовой панели или задеплоенных линках + клиенте панели. Иначе `topology_not_ready`.
**Step by step solution:**
1. Выполните Full Deploy.
2. Сделайте: Add links/exits.
3. Сделайте: Ensure panel client exists.
4. Сделайте: Open Topology.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q092
**Question:** Что такое Add OutBounds?
**Answer:** Добавление outbound на панели (вручную или кастомный JSON в AI Pro) для Exit и маршрутизации.
**Step by step solution:**
1. Сделайте: Panel must be ready.
2. Сделайте: Use Configure Panel / Add OutBounds / AI outbound paste.
3. Сделайте: Test Client.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q093
**Question:** Может ли Basic везде использовать Cloudflare CDN?
**Answer:** CDN входит в набор Pro; Basic фокусируется на Central+Exit и не позиционирует CDN как Pro.
**Step by step solution:**
1. Сделайте: Activate Pro for CDN.
2. Сделайте: Add Domain.
3. Сделайте: Configure CDN.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q094
**Question:** Какие DNS-провайдеры поддерживаются в приложении?
**Answer:** Cloudflare (email + API token Zone:DNS:Edit) и ArvanCloud (machine user + API key). Опциональный bot webhook subdomain отдельно от панели.
**Step by step solution:**
1. Сделайте: Create API credentials at provider.
2. Сделайте: Connect & Import Zones.
3. Сделайте: Create A records.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q095
**Question:** Bot webhook DNS vs домен панели?
**Answer:** Опциональный subdomain для Telegram bot webhook; если не нужен — пропустите; это не домен панели.
**Step by step solution:**
1. Сделайте: Decide if Mirza needs webhook domain.
2. Сделайте: Fill bot subdomain + IP.
3. Сделайте: Create A → Bot.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q096
**Question:** Что такое Diagnose & Repair?
**Answer:** Более широкая проверка/починка (диск/трафик, ping/фильтр, mesh-линки, DNS/CDN, битые параметры). Как AI task/ops; спрашивает только если нужны новый IP или секрет.
**Step by step solution:**
1. Сделайте: Register servers first.
2. Сделайте: Run Diagnose & Repair.
3. Сделайте: Approve fixes.
4. Сделайте: Re-test clients.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q097
**Question:** Что значит busy-спиннер в status bar?
**Answer:** Идёт длинная операция; дождитесь завершения. Раннее закрытие предупреждает о незавершённой работе.
**Step by step solution:**
1. Подождите.
2. Сделайте: Watch terminal.
3. Сделайте: Keep Open if prompted.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q098
**Question:** Можно ли остановить текущую terminal-операцию?
**Answer:** Да — Terminal Stop с подтверждением; прерывает текущий процесс и помечает остановку пользователем.
**Step by step solution:**
1. Сделайте: Click Stop.
2. Сделайте: Confirm.
3. Сделайте: Re-run cleanly if needed.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q099
**Question:** Где хранятся локальные файлы (installed)?
**Answer:** В установленном режиме обычно `%LocalAppData%\Programs\Black Fox Vpn`. В Portable — рядом с exe (с marker).
**Step by step solution:**
1. Сделайте: Win+R → `%LocalAppData%\Programs`.
2. Сделайте: Find Black Fox Vpn.
3. Сделайте: Do not delete license-critical files casually.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q100
**Question:** Как скопировать Device ID / wallet / TX / код?
**Answer:** Отдельные кнопки Copy с тостом успеха буфера для Device ID, wallet, TX и кода активации.
**Step by step solution:**
1. Сделайте: Click the Copy control.
2. Сделайте: Paste into notepad/support chat.
3. Сделайте: Verify no truncation.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q101
**Question:** Что такое offline / record-offline активация?
**Answer:** API хаба могут записывать offline-коды/TX с флагами claim_pending. Не все offline-диалоги сверены — при сомнении NEED_MORE_REVIEW.
**Step by step solution:**
1. Сделайте: Prefer online verify.
2. Сделайте: If offline code issued, activate in app when online.
3. Сделайте: Support if claim_pending stuck.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q102
**Question:** Что значат префиксы BFXB / BFXP / BFXA / BFXQ?
**Answer:** BFXB=Basic, BFXP=Pro, BFXA=AI Pro, BFXQ=AI quota. Неверный префикс для целевой функции ломает unlock.
**Step by step solution:**
1. Сделайте: Match purchase to prefix.
2. Сделайте: Paste exact code.
3. Сделайте: For quota only use BFXQ.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q103
**Question:** Включает ли AI Pro ручные функции Pro?
**Answer:** Да — AI Pro даёт операции Pro через чат и одновременный ручной Pro; отдельный AI-gate всё равно нужен.
**Step by step solution:**
1. Сделайте: Activate AI Pro.
2. Сделайте: Use AI chat or switch to Pro-style manual ops as allowed.
3. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q104
**Question:** Даёт ли unlock Pro доступ к AI Assistant Pro?
**Answer:** Нет — обычный Pro unlock никогда не выдаёт AI Assistant Pro (`FeatureAIProFull`).
**Step by step solution:**
1. Сделайте: Buy AI Pro separately.
2. Сделайте: Or upgrade path on website if offered (`already_ai_pro` / upgrade reasons on API).
3. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q105
**Question:** Website Activation vs проверка TX в приложении?
**Answer:** Сайт выдаёт claim после оплаты; приложение может проверить TX или принять код. После claim TX больше не показывает коды. Привязка Device ID — в Registration.
**Step by step solution:**
1. Сделайте: Pay on foxnext.net.
2. Сделайте: Receive claim code.
3. Сделайте: Paste in Windows Registration.
4. Сделайте: Keep Device ID record.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q106
**Question:** Что такое PAS Generator?
**Answer:** Внутренний/админ-инструмент для выдачи claim и проверки TX / AI Device ID. Не клиентский путь; клиенты — foxnext.net + Registration.
**Step by step solution:**
1. Сделайте: Customers: use website/app only.
2. Сделайте: Support staff: PAS for generate/verify.
3. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q107
**Question:** Какие prerequisites для Add Exit?
**Answer:** Central с Full Deploy/готовой панелью, лицензия на add_exit и SSH на Exit VPS. Без панели Central outbound wiring падает. Страновое правило Basic — для Central, не обязательно для Exit.
**Step by step solution:**
1. Выполните Full Deploy.
2. Сделайте: Activate if locked.
3. Сделайте: Add Exit with correct SSH.
4. Сделайте: Configure Panel.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q108
**Question:** Почему exits нужно удалить до некоторых tunnel deletes?
**Answer:** Целостность цепочки — Exit, которые ещё используют hop, нужно удалить сначала; мастер удаления туннеля предупреждает.
**Step by step solution:**
1. Сделайте: Identify dependent exits.
2. Сделайте: Delete those exits.
3. Сделайте: Delete tunnel hops.
4. Сделайте: Rebuild.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q109
**Question:** Что такое chain number в Pro?
**Answer:** Порядковый номер hop в multi-hop Pro. Сохранение IP, уже лежащего под другим chain number, отклоняется. Удаление hop может сбросить старшие номера.
**Step by step solution:**
1. Сделайте: Assign consistent chain numbers.
2. Сделайте: Don’t reuse IP across conflicting chains.
3. Сделайте: Rebuild after mid-chain deletes.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q110
**Question:** Роль Microsocks на exits?
**Answer:** При deploy Exit microsocks — часть SOCKS outbound пути; при удалении Exit снимается вместе с WG/файрволом.
**Step by step solution:**
1. Сделайте: Let Add Exit install it.
2. Сделайте: Don’t manually break microsocks.
3. Сделайте: Use app delete/redeploy to fix.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q111
**Question:** Совет по импорту WireGuard-клиента?
**Answer:** Импортируйте `.conf` в приложение WireGuard на Windows/Android/iOS. Клиент появляется во вкладке Clients панели после ensure inbound.
**Step by step solution:**
1. Сделайте: Download/copy conf from Test Client.
2. Сделайте: Import.
3. Сделайте: Activate tunnel.
4. Сделайте: Test IP/egress.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q112
**Question:** Ссылки на порт панели по умолчанию?
**Answer:** Реальный порт — тот, что Full Deploy сохранил в Panel Login Info (в истории часто 2053). Устаревший path/token — частая причина сбоя Add Node.
**Step by step solution:**
1. Сделайте: Copy URL from Panel Login Info.
2. Сделайте: Don’t guess old ports.
3. Сделайте: Re-sync credentials after panel changes.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q113
**Question:** External Proxy и proxy панели?
**Answer:** Proxy Settings помогает приложению достучаться до панели/интернета/хаба; это не proxy внутри VPN-клиента пользователя. Профили вроде Iran / Free.
**Step by step solution:**
1. Сделайте: Configure Proxy Settings in app.
2. Сделайте: Test.
3. Сделайте: Retry Panel Login / AI hub.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q114
**Question:** Туториал Registration — как найти TX HASH?
**Answer:** Скопируйте TxID из истории Trust Wallet / MetaMask / Binance (как в туториале Registration).
**Step by step solution:**
1. Сделайте: Open wallet activity.
2. Сделайте: Open TX details.
3. Сделайте: Copy hash starting with 0x.
4. Сделайте: Paste in app.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q115
**Question:** Копирование System info на Windows?
**Answer:** Win+R → msinfo32 или кнопка copy system info в приложении (если есть) для отпечатка поддержки.
**Step by step solution:**
1. Сделайте: Prefer in-app Device ID.
2. Сделайте: Use msinfo32 only if support asks.
3. Сделайте: Don’t paste unrelated secrets.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q116
**Question:** Что если не удаётся получить цены с хаба?
**Answer:** Если live-сумма не загрузилась, UI может отправить к `@HiBlackFoxVpn`.
**Step by step solution:**
1. Проверьте интернет/Proxy.
2. Сделайте: Retry later.
3. При необходимости напишите @HiBlackFoxVpn с Device ID.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q117
**Question:** Связан ли blackfoxupdate.ir?
**Answer:** Хаб обновлений рядом с foxnext.net (сначала blackfoxupdate.ir, затем foxnext.net). Клиентские загрузки лучше с foxnext.net.
**Step by step solution:**
1. Сделайте: Allow app update check.
2. Сделайте: If update fails, try from foxnext.net manually.
3. Сделайте: NEED_MORE_REVIEW for end-user visible branding of blackfoxupdate.ir.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q118
**Question:** Что такое диалог Limited Access?
**Answer:** Заголовок ограничения доступа, когда нужны Activate или Pro; рядом с need_activate / need_pro.
**Step by step solution:**
1. Сделайте: Read body.
2. Откройте вкладку Registration.
3. Сделайте: Unlock required tier.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q119
**Question:** Можно ли запустить Full Deploy из AI-чата?
**Answer:** Да — шаблон «Full Deploy на Central» с SSH-деталями. AI ставит действие в очередь; подтвердите и ждите done/failed.
**Step by step solution:**
1. Сделайте: AI Pro mode.
2. Сделайте: Pick Full Deploy task or paste template.
3. Сделайте: Provide SSH.
4. Сделайте: Confirm Yes.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q120
**Question:** AI продолжает предыдущий чат?
**Answer:** При открытии может спросить Continue или New; сохранённый чат на устройстве.
**Step by step solution:**
1. Сделайте: Read prompt.
2. Сделайте: Reply Continue or New.
3. Сделайте: Proceed.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q121
**Question:** Что такое Move Central?
**Answer:** Перенос роли Central на новый VPS (шаблон AI/ops). Нужны SSH источника и назначения; высокий риск — сначала backup. Полные поля мастера: NEED_MORE_REVIEW.
**Step by step solution:**
1. Сделайте: Backup panel/configs.
2. Сделайте: Provide both SSH sets.
3. Сделайте: Run move flow.
4. Сделайте: Update DNS/CDN to new IP.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q122
**Question:** Subscription URL vs ссылка VLESS?
**Answer:** Test Client может показать оба; Subscription — для приложений, которые тянут обновляемый список. VLESS обычно одиночная inbound-ссылка.
**Step by step solution:**
1. Сделайте: Configure Panel.
2. Сделайте: Open Test Client.
3. Сделайте: Share sub URL to users who need auto-update.
4. Сделайте: Or share single VLESS for quick test.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q123
**Question:** Почему topology пустая после deploy?
**Answer:** Пока панель не готова или нет линков/клиента, топология пустая (`topology_not_ready`).
**Step by step solution:**
1. Сделайте: Confirm Full Deploy success.
2. Сделайте: Add at least one link/exit path.
3. Сделайте: Ensure panel client exists.
4. Сделайте: Refresh View.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q124
**Question:** Откуда качаются agent tools при mesh install?
**Answer:** Инструменты агента при установке Mesh качаются с GitHub на сам VPS. На фильтрованном VPS может понадобиться proxy/доступ к GitHub на сервере.
**Step by step solution:**
1. Сделайте: Ensure VPS can reach GitHub.
2. Сделайте: Retry mesh install.
3. Сделайте: NEED_MORE_REVIEW for exact repo URLs shown in logs.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q125
**Question:** Что такое Other CDN?
**Answer:** Опция CDN для провайдеров вне основного списка в AI Pro задачах. Diagnose & Repair — отдельная задача от настройки CDN.
**Step by step solution:**
1. Сделайте: Choose provider or Other CDN.
2. Сделайте: Supply API details as requested.
3. Сделайте: Verify domain.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q126
**Question:** Hysteria / особые порты?
**Answer:** Некоторые порты валидируются во флоу; подсказка Configure Panel для WG inbound упоминает 8080. Точные строки Hysteria: NEED_MORE_REVIEW.
**Step by step solution:**
1. Сделайте: Follow form validation.
2. Сделайте: Don’t force closed ports.
3. Сделайте: Check Diagnostic.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q127
**Question:** Можно ли SSH не от root?
**Answer:** Возможно, если есть sudo для установок; многие скрипты предполагают привилегии. Предпочтительнее root, если не знаете образ.
**Step by step solution:**
1. Сделайте: Prefer root.
2. Сделайте: If non-root, ensure passwordless sudo.
3. Сделайте: NEED_MORE_REVIEW for full non-root support matrix.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q128
**Question:** Пароль или ключ — что предпочтительнее?
**Answer:** Поддерживаются оба; если оба падают — диалог both_failed. На облаке чаще ключ; после сброса панели чаще пароль.
**Step by step solution:**
1. Сделайте: Use provider-recommended auth.
2. Сделайте: Paste full PEM including headers.
3. Сделайте: Test Connect SSH.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q129
**Question:** Что значит server draft saved?
**Answer:** Локально сохранены credentials/черновик без завершения Deploy (`server.draft_saved`). Удобно перед продолжением многостраничного мастера.
**Step by step solution:**
1. Сделайте: Save draft.
2. Сделайте: Continue later.
3. Сделайте: Connect SSH before Full Deploy.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q130
**Question:** Операция идёт — всё равно закрыть?
**Answer:** Лучше Keep Open; Close Anyway оставляет работу незавершённой (`dialog.close_busy_*`).
**Step by step solution:**
1. Сделайте: Choose Keep Open.
2. Сделайте: Wait for finish.
3. Сделайте: Only Close Anyway if stuck and you accept repair later.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q131
**Question:** Как сменить язык после установки?
**Answer:** Settings → Language → Apply на все вкладки. На первом запуске тоже есть выбор языка.
**Step by step solution:**
1. Сделайте: Open Settings.
2. Сделайте: Select language.
3. Сделайте: Apply.
4. Сделайте: Confirm labels updated.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q132
**Question:** Какие каналы показывает вкладка Contact?
**Answer:** Поддержка `@HiBlackFoxVpn`, канал `@BlackFoxVPN`, сайт foxnext.net, email support@foxnext.net. Смотрите живые значения Contact.
**Step by step solution:**
1. Сделайте: Open Contact.
2. Сделайте: Tap support for help.
3. Сделайте: Tap channel for announcements.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q133
**Question:** Email — основной канал поддержки?
**Answer:** Основной канал в продукте обычно Telegram поддержки; email тоже есть. Для скорости пришлите Device ID в Telegram.
**Step by step solution:**
1. Сделайте: Message @HiBlackFoxVpn.
2. Сделайте: Use email if Telegram unavailable.
3. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q134
**Question:** Что такое «Update BlackFox & Wallet Address»?
**Answer:** Действие Settings для обновления метаданных update и отображения payment wallet с хаба.
**Step by step solution:**
1. Сделайте: Settings → Updates.
2. Сделайте: Run update check.
3. Сделайте: Install if force/min version requires.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q135
**Question:** Force min version блокирует приложение — что делать?
**Answer:** Установите релиз не ниже минимума; старые сборки могут блокироваться (`remote.force_*` / MustForceUpdate).
**Step by step solution:**
1. Сделайте: Download latest Setup from foxnext.net.
2. Сделайте: Install.
3. Сделайте: Relaunch.
4. Сделайте: Reactivation if license UI resets.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q136
**Question:** Таймаут / сетевая ошибка AI-сервиса?
**Answer:** Повторите; проверьте интернет/Proxy. Сообщения: timeout / could not reach AI service.
**Step by step solution:**
1. Сделайте: Check connectivity.
2. Сделайте: Configure Proxy if needed.
3. Сделайте: Resend.
4. Сделайте: If persistent, support with Device ID.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q137
**Question:** AI временно недоступен?
**Answer:** `ai.disabled` — хаб отключил AI; это не обязательно локальная лицензия.
**Step by step solution:**
1. Сделайте: Wait and retry.
2. Сделайте: Check foxnext announcements.
3. Сделайте: Ask @HiBlackFoxVpn.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q138
**Question:** Quota not found for license?
**Answer:** Сначала активируйте AI Assistant Pro (`ai.quota.not_found`). Это не то же самое, что exhausted.
**Step by step solution:**
1. Сделайте: Activate AI Pro.
2. Сделайте: Or apply BFXQ if only quota missing after AI Pro.
3. Сделайте: Recheck status.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q139
**Question:** Delete All удаляет SSH-пароли с диска?
**Answer:** Нет — Reset All сохраняет SSH; Delete History чистит локальные credentials (лицензия остаётся). Не путайте.
**Step by step solution:**
1. Сделайте: Choose the delete that matches intent.
2. Сделайте: Read confirm body.
3. Сделайте: Proceed.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q140
**Question:** Factory Reset сохраняет данные панели?
**Answer:** Нет — цель приблизить VPS к исходному состоянию, необратимо. Отличается от Reset All (снятие пакетов с сохранением SSH).
**Step by step solution:**
1. Сделайте: Use only if you intend to wipe VPS.
2. Сделайте: Prefer Delete All for app-managed cleanup.
3. Сделайте: Re-provision after factory reset.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q141
**Question:** Как быстро проверить mesh failover?
**Answer:** Обновите статус агентов; восстановление пути обычно автоматическое за секунды. Порядок: WG→GRE→Stealth-WSS→backups.
**Step by step solution:**
1. Сделайте: Deploy agents.
2. Сделайте: Refresh Status.
3. Сделайте: Run Link Test.
4. Сделайте: Simulate path issue only on test beds.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q142
**Question:** Каков scope «Install always-on Link Monitor Agents»?
**Answer:** На хостах Central, Tunnel, Exit и Node.
**Step by step solution:**
1. Сделайте: Ensure each role has SSH saved.
2. Сделайте: Run mesh deploy.
3. Сделайте: Confirm each host Running.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q143
**Question:** Можно ли использовать приложение только как менеджер закладок панели?
**Answer:** Так не задумано — это operational deploy library; Panel Login Info лишь одна функция после Deploy.
**Step by step solution:**
1. Сделайте: Deploy central.
2. Сделайте: Then use panel info/clients.
3. Сделайте: Or open external panel manually if you already have one (limited integration without saved creds).
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q144
**Question:** Общее состояние Basic / Pro / AI Pro?
**Answer:** Одно общее локальное хранилище серверов/панели для Basic/Pro/AI Pro — без параллельного AI-only конфига.
**Step by step solution:**
1. Сделайте: Deploy once.
2. Сделайте: Switch modes freely for UI.
3. Сделайте: License still gates features.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q145
**Question:** Check System vs Diagnose & Repair?
**Answer:** Check System — только диагностика; Diagnose & Repair пытается чинить. Для доказательств поддержке сначала read-only.
**Step by step solution:**
1. Сделайте: Run Checks.
2. Сделайте: Export if needed.
3. Сделайте: Run Diagnose & Repair if appropriate.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q146
**Question:** Client test failed после add exit?
**Answer:** Снова Configure Panel, проверьте outbound/линк, SSH на Exit и Diagnostic. Частые причины: неполный Exit deploy, WG/GRE down, mismatch тега outbound, файрвол.
**Step by step solution:**
1. Сделайте: Confirm exit deploy success.
2. Сделайте: Configure Panel.
3. Сделайте: Link Test.
4. Сделайте: Test Client again.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q147
**Question:** Add Node fails central login?
**Answer:** Устаревший path/token панели — обновите Full Deploy или Panel Login Info (`node.err_central_login`).
**Step by step solution:**
1. Сделайте: Open Panel Login Info.
2. Сделайте: Refresh via Full Deploy / panel install.
3. Сделайте: Retry Add Node.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q148
**Question:** Риск потери данных в portable mode?
**Answer:** Высокий риск при переносе/удалении portable-папки; installed mode использует LocalAppData. Делайте backup папки.
**Step by step solution:**
1. Сделайте: Keep portable.exe + data together.
2. Сделайте: Don’t run two copies fighting the same inventory.
3. Сделайте: Prefer Setup for stability.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q149
**Question:** Как мультиязычные страницы сайта связаны с приложением?
**Answer:** У foxnext.net есть мультиязычные страницы; язык приложения отдельный и меняется в Settings.
**Step by step solution:**
1. Сделайте: Browse foxnext.net in your language.
2. Сделайте: Set app language separately.
3. Сделайте: Use same support contacts.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q150
**Question:** Что значит подзаголовок «Multi-Location VPN Manager»?
**Answer:** Означает управление Central плюс несколькими Exit/Tunnel/Node из одного Installer; ценность — автоматизация multi-location топологии, не один VPS.
**Step by step solution:**
1. Сделайте: Full Deploy central.
2. Сделайте: Add locations.
3. Сделайте: Configure Panel.
4. Сделайте: Optional mesh.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q151
**Question:** Сохраняются ли пароли при Factory Reset?
**Answer:** Нет — пароли Factory Reset только для этой операции и не сохраняются; в отличие от обычного Save сервера.
**Step by step solution:**
1. Сделайте: Enter creds for factory reset only.
2. Сделайте: They won’t be kept.
3. Сделайте: Re-save server normally if you continue using it.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q152
**Question:** Что значит «SSH connected but probe output unexpected»?
**Answer:** Auth прошёл, но вывод probe неожиданный (`log.ssh_probe_unexpected`). Возможны необычный shell/MOTD или блокировка команд. Точные детали: NEED_MORE_REVIEW.
**Step by step solution:**
1. Сделайте: Confirm distro is supported Linux.
2. Сделайте: Retry Connect SSH.
3. Сделайте: Check provider serial console.
4. Сделайте: Send log line to support.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q153
**Question:** Можно ли прикреплять скриншоты панелей к AI-чату?
**Answer:** Да — до 3 изображений; AI мультимодальный (текст+фото) для деталей сервера/бота и т.п.
**Step by step solution:**
1. Сделайте: Attach clear screenshots.
2. Сделайте: Add short text.
3. Сделайте: Confirm extracted details selection.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q154
**Question:** AI перепутал Exit и Node?
**Answer:** Отклоните и перешлите с уточнением; reject-путь просит прояснить цель или выбрать Task.
**Step by step solution:**
1. Сделайте: Reply No.
2. Сделайте: State Exit or Node clearly.
3. Сделайте: Resend details or use left-task buttons.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q155
**Question:** Что значит статус Apply Actions в AI-чате?
**Answer:** Приложение применяет поставленные в очередь действия из ответа AI (preparing… applying_actions… finalizing).
**Step by step solution:**
1. Подождите.
2. Сделайте: Confirm any Yes/No prompts.
3. Сделайте: Watch terminal for real deploy results.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q156
**Question:** Сумма USDT всегда 19/33/40?
**Answer:** 19/33/40 — распространённые якоря/fallback; live-каталог по месяцам отличается. Всегда платите сумму на экране foxnext.net / в приложении.
**Step by step solution:**
1. Сделайте: Read on-screen amount.
2. Сделайте: Pay exactly that on BEP-20.
3. Сделайте: Don’t assume old chat prices.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q157
**Question:** Reactivation пишет tier mismatch?
**Answer:** Запись на сервере есть, но не совпадает с запрошенным тарифом (`tier_mismatch`). Активируйте верный тариф или согласуйте с поддержкой.
**Step by step solution:**
1. Сделайте: Confirm which product you bought.
2. Сделайте: Try matching activate button.
3. Сделайте: Message support with Device ID.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q158
**Question:** Можно ли восстановить коды со старого TX после claim?
**Answer:** Обычно нет — после claim TX больше не показывает коды. На привязанном устройстве Reactivation или поддержка с Device ID.
**Step by step solution:**
1. Сделайте: Try Reactivation on original PC.
2. Сделайте: Provide Device ID + TX to @HiBlackFoxVpn.
3. Сделайте: Do not expect website to reprint claimed codes.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q159
**Question:** Рекомендуемый first-run путь для новичка?
**Answer:** Setup → язык → Basic → Central → Connect SSH → Full Deploy → Panel Info → при необходимости Exit после Activate. При фильтрации: Proxy. Если застряли: `@HiBlackFoxVpn`.
**Step by step solution:**
1. Сделайте: Setup.exe from foxnext.net.
2. Сделайте: Basic mode.
3. Сделайте: Central IR/CN/RU.
4. Выполните Connect SSH.
5. Выполните Full Deploy.
6. Сделайте: Test Client.
7. Сделайте: Activate Pro/AI when needed.
8. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q160
**Question:** Куда смотреть агенту поддержки за точными UI-строками?
**Answer:** Точные UI-строки — в `internal/i18n/en.go` / `locales/en.json` и `reason_code` API хаба. Неизвестный Linux stderr помечайте NEED_MORE_REVIEW.
**Step by step solution:**
1. Сделайте: Match screenshot to i18n.
2. Сделайте: Use Troubleshooting.md for error playbooks.
3. Сделайте: Escalate with Device ID + logs.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q161
**Question:** Смена режима View стирает серверы?
**Answer:** Нет — режимы делят одно локальное хранилище. Смена View меняет UI и гейты, но не стирает серверы.
**Step by step solution:**
1. Сделайте: Save work if a wizard is open.
2. Сделайте: Change mode on View.
3. Сделайте: Confirm servers still listed under Operations.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q162
**Question:** Configure Panel vs Full Deploy?
**Answer:** Full Deploy ставит WG+панель на Central; Configure Panel чинит routing существующего Exit/Node и не является повторной установкой панели Central.
**Step by step solution:**
1. Сделайте: Finish Full Deploy first.
2. Сделайте: Add Exit/Node as needed.
3. Сделайте: Run Configure Panel.
4. Сделайте: Use Panel Login Info only to view URL/creds.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q163
**Question:** Сколько Node можно добавить?
**Answer:** Максимум 6 Node (`MaxNodes`); та же слотовая логика, что у Exit в Pro.
**Step by step solution:**
1. Сделайте: Unlock Pro.
2. Сделайте: Open Add Node.
3. Сделайте: Fill SSH + XUI source.
4. Сделайте: Stop at six or replace a slot.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q164
**Question:** Какие XUI-источники у Full Deploy / Add Node?
**Answer:** Sanaei GitHub, BlackFox Hub или пакет Local PC. Выбор в Full Deploy и Add Node. Local — для офлайна/фильтрации.
**Step by step solution:**
1. Сделайте: Prefer Hub when online.
2. Сделайте: Use Local if you have a verified package.
3. Сделайте: GitHub when Hub is blocked (may be slower).
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q165
**Question:** Что сохраняет Delete History?
**Answer:** Чистит локальную историю; язык, режим и лицензия остаются. Отличается от Reset All (снятие WG/панели удалённо с сохранением SSH).
**Step by step solution:**
1. Сделайте: Open the delete/history control.
2. Сделайте: Confirm.
3. Сделайте: Re-check Registration still unlocked.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q166
**Question:** Что делает DELETE — Reset All Servers?
**Answer:** Снимает WG/панель с настроенных серверов; сохранённый SSH остаётся. Потом снова нужен Full Deploy.
**Step by step solution:**
1. Сделайте: Confirm inventory is correct.
2. Сделайте: Run Reset All Servers.
3. Выполните Connect SSH.
4. Сделайте: Full Deploy again.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q167
**Question:** Можно ли удалить только tunnel hops?
**Answer:** Да — Delete Tunnel Servers сбрасывает hop’ы Pro-цепочки и не обязательно трогает Exit/Central.
**Step by step solution:**
1. Сделайте: Pro mode.
2. Сделайте: Use Delete Tunnel Servers.
3. Сделайте: Re-add tunnels if still needed.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q168
**Question:** Какие профили Proxy есть?
**Answer:** Профили вроде None / Auto / Iran / Free в Proxy Settings. Политика: сначала Direct, при сбое — Program Proxy для SSH, HTTP хаба и Panel API.
**Step by step solution:**
1. Сделайте: Open Proxy Settings.
2. Сделайте: Try Auto if Direct fails.
3. Сделайте: Iran profile when in restricted networks.
4. Сделайте: Retry Connect SSH / updates.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q169
**Question:** Где смотреть URL панели после deploy?
**Answer:** Panel Login Info показывает сохранённые URL/логин/пароль после успешной установки/синхронизации панели.
**Step by step solution:**
1. Сделайте: Complete Full Deploy.
2. Сделайте: Open Panel Login Info.
3. Сделайте: Copy URL carefully (port + path).
4. Сделайте: Log in via browser if needed.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q170
**Question:** Для чего Test Client / WG?
**Answer:** Диалог теста клиента/WireGuard для проверки после Configure; не замена Full Deploy.
**Step by step solution:**
1. Сделайте: Ensure panel + exit path ready.
2. Сделайте: Open Test Client.
3. Сделайте: Import/test as prompted.
4. Сделайте: If fail, run Link Test / diagnostics.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q171
**Question:** Что такое Add Domain?
**Answer:** DNS-менеджер Pro для Cloudflare / ArvanCloud (зоны/записи; опциональный bot webhook). Это оверлей, не главная вкладка.
**Step by step solution:**
1. Сделайте: Unlock Pro.
2. Сделайте: Open Add Domain / DNS Manager.
3. Сделайте: Enter API credentials.
4. Сделайте: Create/update records.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q172
**Question:** Какие CDN-провайдеры в UI?
**Answer:** В UI обычно Arvan, Cloudflare и Other CDN. Если видите четвёртый бренд — NEED_MORE_REVIEW (внутренний ключ может не быть в UI).
**Step by step solution:**
1. Сделайте: Pro mode.
2. Сделайте: Open CDN modal.
3. Сделайте: Pick Arvan/Cloudflare/Other.
4. Сделайте: Save; apply via API when available.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q173
**Question:** Что такое Mesh Servers?
**Answer:** Pro-страница графа inventory, Deploy агентов Link Monitor и статуса линков; отдельно от сетки Operations.
**Step by step solution:**
1. Сделайте: Unlock Pro.
2. Сделайте: Open Mesh Servers.
3. Сделайте: Deploy agents when prompted.
4. Сделайте: Read link status; repair via ops if down.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q174
**Question:** Что такое Add Telegram Bot (Mirza)?
**Answer:** Pro-инструмент установки/переноса Mirza (или Other). Это не support-бот Black Fox; семейство sales-бота панели Mirza.
**Step by step solution:**
1. Сделайте: Pro unlock.
2. Сделайте: Open Add Telegram Bot.
3. Сделайте: Choose install / other / move.
4. Сделайте: Supply bot token when asked.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q175
**Question:** Что такое Move Central Server?
**Answer:** Перенос роли Central на другой VPS (Pro Tools). Высокое влияние — inventory и credentials панели должны остаться согласованными. Точные поля: NEED_MORE_REVIEW.
**Step by step solution:**
1. Сделайте: Backup panel/creds.
2. Сделайте: Unlock Pro.
3. Сделайте: Open Move Central.
4. Сделайте: Follow wizard; re-verify Panel Login Info.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q176
**Question:** Что такое BlackFox MCP в AI tasks?
**Answer:** Активирует MCP binary / mcp.json, чтобы внешние AI-инструменты вызывали действия Black Fox. Для обычного in-app чата не обязателен.
**Step by step solution:**
1. Сделайте: AI Pro unlocked.
2. Сделайте: Run BlackFox MCP task.
3. Сделайте: Confirm desktop MCP config.
4. Сделайте: Use only if integrating external agents.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q177
**Question:** Diagnose & Repair vs Check System?
**Answer:** Check System — локальная вкладка Diagnostics; Diagnose & Repair — AI Pro Task с подтверждением перед изменениями.
**Step by step solution:**
1. Сделайте: For quick local status → Check System.
2. Сделайте: For guided fix → AI Pro Diagnose & Repair.
3. Сделайте: Confirm Yes before apply.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q178
**Question:** Что такое Link Test (AI)?
**Answer:** AI Task-шаблон для теста линков топологии; дополняет Configure Panel и Test Client с подтверждением до выполнения.
**Step by step solution:**
1. Сделайте: AI Pro chat.
2. Сделайте: Choose Link Test.
3. Сделайте: Confirm.
4. Сделайте: Read terminal/status outcome.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q179
**Question:** Что такое Add OutBounds (AI)?
**Answer:** AI Task для настройки outbound панели; предпочтительно после появления Exit/Node и с подтверждением до Apply.
**Step by step solution:**
1. Сделайте: Ensure central panel ready.
2. Сделайте: AI task Add OutBounds.
3. Сделайте: Confirm extracted details.
4. Сделайте: Verify in panel if needed.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q180
**Question:** Factory Reset сохраняет введённый пароль?
**Answer:** Нет — введённые для Factory Reset пароли только для этой операции и потом не хранятся.
**Step by step solution:**
1. Сделайте: Enter creds when asked.
2. Сделайте: Complete reset.
3. Сделайте: Re-save SSH normally if you continue.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q181
**Question:** Где меняется язык?
**Answer:** Settings → применение языка (и выбор на первом запуске). Язык сайта foxnext.net отделён от i18n приложения.
**Step by step solution:**
1. Сделайте: Open Settings.
2. Сделайте: Choose language.
3. Сделайте: Apply.
4. Сделайте: Confirm labels update (RTL for FA).
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q182
**Question:** Что такое менеджер пакетов 3X-UI в Settings?
**Answer:** Раздел Tools для управления офлайн/хаб-пакетами 3X-UI для Deploy и Local PC. Точные UI-подписи сверьте с текущим Settings.
**Step by step solution:**
1. Сделайте: Settings → Tools / packages.
2. Сделайте: Refresh from hub if online.
3. Сделайте: Use Local path when offline.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q183
**Question:** Что вызывает force update?
**Answer:** Ниже минимальной поддерживаемой версии/билда или force-флаг с более новым remote. `version.json` хаба ведёт фиды; не выдумывайте номера.
**Step by step solution:**
1. Сделайте: Allow update dialog.
2. Сделайте: Download from official hub/site.
3. Сделайте: Reinstall Setup if portable is stale.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q184
**Question:** Что такое PAS Generator?
**Answer:** Отдельный админ-инструмент (`cmd/pas-generator`) для PAS-процессов. Не основной клиентский путь; клиенты — foxnext.net + Registration.
**Step by step solution:**
1. Сделайте: Operators only.
2. Сделайте: Do not ask customers to run PAS Generator unless support instructs.
3. Сделайте: Customers use Activate / claim codes.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q185
**Question:** Что такое Config Builder?
**Answer:** Отдельный APK в `version.json` → `config_builder`. Связанный продукт; исходников нет в этом Windows-репо; не путайте с основным Android VPN.
**Step by step solution:**
1. Сделайте: Download from official hub/site if offered.
2. Сделайте: Do not expect Installer tabs inside Config Builder.
3. Сделайте: Support Installer vs Config Builder separately.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q186
**Question:** Какие бесплатные страны Central в Basic?
**Answer:** Без Pro бесплатные страны Central: Иран, Китай, Россия (`IsFreeCentralCountry`). Другие страны обычно требуют Pro.
**Step by step solution:**
1. Сделайте: Basic mode.
2. Сделайте: Pick IR/CN/RU for free central path.
3. Сделайте: Activate Pro if another country is required.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q187
**Question:** Открывает ли Pro license AI-чат?
**Answer:** Нет — AI-чат требует отдельный unlock AI Pro и quota. Pro открывает только Pro-дашборд.
**Step by step solution:**
1. Сделайте: Activate AI Assistant Pro.
2. Сделайте: Select AI Pro on View.
3. Сделайте: Confirm quota.
4. Сделайте: Chat/tasks.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q188
**Question:** Какие префиксы кодов есть?
**Answer:** BFXB Basic, BFXP Pro, BFXA AI Pro, BFXQ quota, BFXT test; claim содержат `-CLM-`. Неверный префикс → неверный unlock или ошибка.
**Step by step solution:**
1. Сделайте: Copy full code.
2. Сделайте: Paste Activate.
3. Сделайте: If claim code, ensure unused TX.
4. Сделайте: Use Reactivation if rebound needed.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q189
**Question:** Что такое My Code на Registration?
**Answer:** После успешного unlock показывает сохранённый код; полезно для тикетов, но храните как секрет.
**Step by step solution:**
1. Сделайте: Activate successfully.
2. Сделайте: Open My Code.
3. Сделайте: Share with support only when asked.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q190
**Question:** Что такое System ID / Device ID?
**Answer:** Отпечаток машины для привязки лицензии; нужен для Activation сайта и Reactivation. Смена железа может сломать привязку.
**Step by step solution:**
1. Сделайте: Registration tab.
2. Скопируйте Device ID.
3. Сделайте: Use on foxnext.net Activation.
4. Сделайте: Keep for support.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q191
**Question:** Срок License по умолчанию, если месяцы не указаны?
**Answer:** Если месяцы не указаны, часто 18 в логике лицензии; live-каталог 12–30 и multi-device скидки. Ориентируйтесь на срок на экране.
**Step by step solution:**
1. Сделайте: Read purchase page months.
2. Сделайте: Pay matching amount.
3. Сделайте: Activate with issued code.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q192
**Question:** Какие хабы использует приложение?
**Answer:** Основной `blackfoxupdate.ir`, запасной `foxnext.net` для version, runtime-config, license-access, AI и пакетов; failover при блоке.
**Step by step solution:**
1. Сделайте: Keep internet.
2. Сделайте: If updates fail, try Proxy.
3. Сделайте: Confirm official site for downloads.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q193
**Question:** Контакты поддержки из product config?
**Answer:** Включает `@HiBlackFoxVpn`, `@BlackFoxVpnn`, `@BlackFoxVpn_bot`, `@Black_Fox_Group` из runtime contact. Предпочитайте живой список Contact.
**Step by step solution:**
1. Сделайте: Open Contact tab.
2. Сделайте: Use listed Telegram/email.
3. Сделайте: Include Device ID in tickets.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q194
**Question:** Намеренное написание public GitHub?
**Answer:** Хаб может показывать `github.com/balckfoxgroup/blackfox-vpn-installer` — используйте опубликованную строку и не «исправляйте» написание, если так в Contact.
**Step by step solution:**
1. Сделайте: Open Contact → GitHub.
2. Сделайте: Follow the in-app URL.
3. Сделайте: Don’t invent alternate orgs.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q195
**Question:** Android или Windows для Full Deploy?
**Answer:** Для Full Deploy и Mesh используйте Windows Installer; Android — компаньон, основной Deploy-workstation обычно Windows.
**Step by step solution:**
1. Сделайте: Deploy from Windows.
2. Сделайте: Use Android for mobile monitoring/AI where available.
3. Сделайте: Import WG client configs on any OS WireGuard app.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q196
**Question:** Безопасно ли двум portable копиям делить inventory?
**Answer:** Рискованно — предпочитайте одну portable-папку или Setup+LocalAppData. Две копии могут конфликтовать на одном inventory.
**Step by step solution:**
1. Сделайте: Use one working copy.
2. Сделайте: Backup portable folder.
3. Сделайте: Prefer Setup install for stability.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q197
**Question:** Что AI никогда не должен выдумывать?
**Answer:** Номера версий, цены, бренды хостеров и Linux stderr вне i18n. Идентичность: BlackFox AI; пробелы помечайте NEED_MORE_REVIEW.
**Step by step solution:**
1. Сделайте: Answer from KB.
2. Сделайте: If unknown, say so.
3. Сделайте: Ask for screenshot + Device ID.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q198
**Question:** Где скриншоты для обучения?
**Answer:** Папка `/Screenshots` с README; live-захват всех диалогов ещё неполон. Есть mode picker, дашборды Basic/Pro, Android и маркетинг.
**Step by step solution:**
1. Сделайте: Pick matching asset from README.
2. Сделайте: Do not claim a missing dialog screenshot exists.
3. Сделайте: Request user screenshot when needed.
4. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q199
**Question:** Как chatbot вести застрявший deploy?
**Answer:** Порядок: Proxy → Connect SSH → источник Full Deploy → Panel Login Info → Configure Panel → Diagnostic. Не прыгайте сразу в Delete/Reset. Отделите бесплатный Basic от лицензии.
**Step by step solution:**
1. Сделайте: Verify mode/license.
2. Сделайте: Proxy if network fails.
3. Выполните Connect SSH.
4. Выполните Full Deploy.
5. Сделайте: Check System / AI Diagnose.
6. Сделайте: Support if still blocked.
7. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.

### Q200
**Question:** Какой единый RAG entry-файл?
**Answer:** Главный RAG-файл: `Documentation/AI_Knowledge_Base.md` плюс гайды, FAQ, Troubleshooting и `Screenshots/README`. Для мультиязычного бота — `AI_Knowledge_Base_Multilingual` и `AI_BOT_DATABASE`.
**Step by step solution:**
1. Сделайте: Load AI_Knowledge_Base.md.
2. Сделайте: Retrieve FAQ/Troubleshooting for errors.
3. Сделайте: Cite Feature_List for gates.
4. Сделайте: Mark NEED_MORE_REVIEW honestly.
5. Если не помогло — Device ID в @HiBlackFoxVpn.
**Possible errors:** Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.
