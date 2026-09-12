# Black Fox VPN — 常见问题（简体中文）

> 供 AI / Telegram Bot / 客服。问题编号与英文对齐。
> Q001–Q200 答案已完整本地化（无英文外壳）。
> 准确性：Exit 最多 6；Basic 免费 = Setup Central + Connect SSH + Full Deploy；Pro ≠ AI Pro.


### Q001
**Question:** Black Fox VPN Installer 是什么？
**Answer:** Black Fox 是 Windows Installer，通过 SSH 在您的 VPS 上自动部署 WireGuard 与 3X-UI (Sanaei) Panel，用于多地域 VPN 基建，不是消费级 VPN 客户端。
**Step by step solution:**
1. 从 foxnext.net 下载 Setup。
2. 安装并选择语言。
3. 请执行：Choose Basic, Pro, or AI Assistant Pro on the View tab.
4. 请执行：Save central SSH, Connect SSH, then Full Deploy.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q002
**Question:** Black Fox 是 3X-UI 面板界面的分支吗？
**Answer:** 根据当前 Black Fox 行为：No — it automates and manages the Sanaei / 3X-UI panel; it is not a panel UI fork. Black Fox installs and configures the real 3X-UI (Sanaei) panel on your central server and drives panel API tasks (inbounds, outbounds, nodes, clients). You still open the panel URL for advanced panel UI work when needed. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Complete Full Deploy.
2. 请执行：Use Panel Login Info for URL/user/password.
3. 请执行：Open the panel in a browser if you need the native 3X-UI UI.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q003
**Question:** 产品支持哪些平台？
**Answer:** 根据当前 Black Fox 行为：Windows Installer is the full ops app; Android has a companion app with chat/engine packaging differences. Primary product is the Windows desktop Installer (Setup and portable exe). Android builds exist (including a larger release APK that embeds the Go engine). Client WireGuard configs can be imported on Windows/Android/iOS WireGuard apps. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Use Windows for Full Deploy and mesh ops.
2. 请执行：Use Android where you need mobile AI/chat or engine-backed features.
3. 请执行：Import `.conf` into any WireGuard client for end-user VPN.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q004
**Question:** 官方 Installer 从哪里下载？
**Answer:** 根据当前 Black Fox 行为：From foxnext.net (website download and update hosts). Official site is foxnext.net. Setup is typically `Black Fox Vpn-Installer-Setup.exe`. App updates also pull from foxnext.net / blackfoxupdate.ir style hosts configured in runtime. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Open http://foxnext.net/ (or /en/).
2. 请执行：Use the download/setup page.
3. 请执行：Prefer Setup.exe for first install.
4. 请执行：For support, confirm you did not use an unofficial mirror.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q005
**Question:** 应用有哪些主标签页？
**Answer:** 标签页：Operations、Check System、View、Settings、Registration、Contact。Add Domain 与 Mesh 为叠加页；没有独立顶层 Add 标签。
**Step by step solution:**
1. 请执行：Start on View to pick mode. 2. Use Registration to activate. 3. Use Operations for SSH/deploy. 4. Use Contact for support.
2. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q006
**Question:** View 标签页有什么用？
**Answer:** 根据当前 Black Fox 行为：Choose Basic / Pro / AI Pro and see topology when ready. View lets you pick the app mode and shows topology after Full Deploy (panel ready) or when links are deployed and a panel client exists. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 打开 View 标签。
2. 请执行：Select Basic, Pro, or AI Assistant Pro.
3. 请执行：After deploy, open Topology when available.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q007
**Question:** 什么是 Basic 模式？
**Answer:** 根据当前 Black Fox 行为：Central SSH, WireGuard + Sanaei panel, up to 6 exits, inbound/outbound setup, client test. Basic covers central in Iran/China/Russia, panel on central, up to six exit servers, configure panel, client test. Keys like Initial Server Setup, Connect SSH, and Full Deploy in Basic are free operations (license still gates full paid feature set after free basics). 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Select Basic on View.
2. 请执行：Save central (Iran/China/Russia).
3. 执行 Connect SSH。
4. 执行 Full Deploy。
5. 请执行：Add Exit Server(s) as needed.
6. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q008
**Question:** 什么是 Pro 模式？
**Answer:** 根据当前 Black Fox 行为：All Basic plus multi-hop chain, tunnel relay, CDN, subscriptions, nodes (still max 6 exit slots). Pro unlocks multi-hop tunnel chain (Add Tunnel Servers), CDN, subscriptions, nodes, and other Pro ops. Exit capacity remains capped at 6 slots. Dialog text: “This feature requires Pro activation” when a Pro-only feature is locked. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Activate Pro on Registration / foxnext.net.
2. 请执行：Switch View to Pro.
3. 请执行：Use tunnel chain, CDN, subscription, and node buttons.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q009
**Question:** 什么是 AI Assistant Pro？
**Answer:** 根据当前 Black Fox 行为：All Pro ops via smart chat, with simultaneous access to manual Pro. AI Assistant Pro (`ai_pro`) provides guided chat that can queue the same operations (Full Deploy, exits, mesh, CDN, diagnose, etc.) with confirmation. Manual Pro remains available. AI chat requires AI Pro unlock and AI quota credit on the hub. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Activate AI Assistant Pro.
2. 请执行：Select AI Pro on View.
3. 请执行：Use Tasks or free-form chat.
4. 请执行：Confirm Yes/No when asked before execution.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q010
**Question:** 激活后还能切换模式吗？
**Answer:** 根据当前 Black Fox 行为：Yes — View mode selection is separate from license unlock, but locked features still need the matching license. You can select Basic/Pro/AI Pro on View. Features still check unlock state (Basic Full / Pro / AI Pro). AI chat is blocked with “AI Assistant Pro activation required…” if not unlocked. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 打开 View 标签。
2. 请执行：Select the mode you want.
3. 请执行：If a button says need activate / need Pro, open Registration.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q011
**Question:** Basic 里哪些操作免费？
**Answer:** Basic 无 License 时仅 Setup Central、Connect SSH、Full Deploy 免费。
**Step by step solution:**
1. 请执行：Stay in Basic.
2. 请执行：Configure central.
3. 执行 Connect SSH。
4. 请执行：Run Full Deploy without paying for those three keys.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q012
**Question:** Basic 的 Central 必须位于特定国家吗？
**Answer:** 根据当前 Black Fox 行为：Yes — Iran, China, or Russia. Dialog: “Basic mode: central server must be in Iran, China, or Russia.” Pro allows broader central placement (product Pro copy references worldwide/central flexibility vs Basic country rule). 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Choose a VPS in IR/CN/RU for Basic.
2. 请执行：Save country correctly in the server form.
3. 请执行：If rejected, use a Pro license or change location.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q013
**Question:** Basic 最多可用多少 Exit Server？
**Answer:** 根据当前 Black Fox 行为：Up to 6 exit servers. Basic tooltip and mode description: up to 6 exit servers; Add Exit Server 2 covers slot 2 in Basic and slots 2–6 in Pro flows. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Full Deploy central.
2. 请执行：Add Exit Server
3. 请执行：3. Add further exits via Add Exit Server 2 / slots up to 6.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q014
**Question:** Pro 的 Exit 是无限的吗？
**Answer:** 不是。Exit 上限为 6 个槽位（`MaxExitServers`）。
**Step by step solution:**
1. 请执行：Activate Pro.
2. 请执行：Add exits as needed.
3. 请执行：Configure Panel for selected exits/nodes.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q015
**Question:** 什么是 Full Deploy？
**Answer:** Full Deploy 是在 Central 上一键安装 WireGuard 与 3X-UI Panel。
**Step by step solution:**
1. 请执行：Save central credentials.
2. 请执行：Connect SSH (OK).
3. 请执行：Run Full Deploy.
4. 请执行：Wait for terminal success.
5. 请执行：Open Panel Login Info.
6. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q016
**Question:** Full Deploy 之前要做什么？
**Answer:** 根据当前 Black Fox 行为：Configure/save central server and verify SSH. Dialogs: “Configure central server first.” and Connect SSH to verify login. Without panel credentials after deploy, later ops say “Complete Full Deploy first.” 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Initial / Central Server Setup.
2. 执行 Connect SSH。
3. 请执行：Fix auth errors if any.
4. 执行 Full Deploy。
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q017
**Question:** 什么是 Connect SSH？
**Answer:** 根据当前 Black Fox 行为：Test SSH login to the central server and verify connectivity. Validates username/password or key, host reachability, and stores trust state for host keys. Failures surface as SSH authentication / timeout / host key dialogs. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Save IP, port, user, password or PEM.
2. 请执行：Click Connect SSH.
3. 请执行：Accept host key only if you trust the VPS.
4. 请执行：Proceed when status is OK.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q018
**Question:** 应用接受哪些 SSH 凭据？
**Answer:** 根据当前 Black Fox 行为：Host/IP, port (usually 22), username (often root), password and/or private key (PEM). Server forms and Factory Reset accept password or private key. Invalid both key and password: “SSH authentication failed” with message that invalid credentials were not saved. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Prefer root or sudo-capable user.
2. 请执行：Paste PEM if key auth.
3. 请执行：Or password.
4. 请执行：Connect SSH to validate.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q019
**Question:** 什么是 Panel Login Info？
**Answer:** 根据当前 Black Fox 行为：Shows saved 3X-UI panel URL, username, and password. Shared across Basic / Pro / AI Pro after deploy. Use it to open the panel and copy credentials. Long values wrap; copy buttons available. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Finish Full Deploy.
2. 请执行：Open Panel Login Info.
3. 请执行：Copy URL/user/pass.
4. 请执行：Log in via browser or continue in-app ops.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q020
**Question:** 什么是 Configure Panel？
**Answer:** Configure Panel 修复已有 Exit/Node 的 inbound/outbound/SOCKS，不是在 Central 安装面板。
**Step by step solution:**
1. 请执行：Have exits/nodes registered as needed.
2. 请执行：Open Configure Panel.
3. 请执行：Select targets and ports.
4. 请执行：Apply and verify Test Client.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q021
**Question:** 什么是 Test Client / WireGuard？
**Answer:** 根据当前 Black Fox 行为：Shows VLESS link, subscription URL, and WireGuard config for testing. After panel configuration, generate/test client links and `.conf` for import into WireGuard apps. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Configure Panel.
2. 请执行：Open Test Client.
3. 请执行：Copy VLESS/sub/WG.
4. 请执行：Import `.conf` into WireGuard.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q022
**Question:** 什么是 Add Exit Server？
**Answer:** 根据当前 Black Fox 行为：Deploy an exit location (WireGuard + SOCKS outbound) for egress. Exit servers carry traffic out. Slot 1 and additional slots (2–6 Basic, more in Pro). Requires central panel ready. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Full Deploy central.
2. 请执行：Enter exit SSH details.
3. 请执行：Run Add Exit Server.
4. 请执行：Configure Panel to use the exit.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q023
**Question:** 什么是 Add Tunnel Server？
**Answer:** 根据当前 Black Fox 行为：Pro chain hop relay between central and exits. Pro-only multi-hop: register tunnel hops; delete one hop also resets higher-sequence hops to keep the chain intact. Exits using those hops must be deleted first when removing tunnels. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Activate Pro.
2. 请执行：Add Tunnel Server with hop sequence.
3. 请执行：Link exits through the chain.
4. 请执行：Deploy mesh/link type as guided.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q024
**Question:** 什么是 Add Node？
**Answer:** 根据当前 Black Fox 行为：Register a node with the central 3X-UI panel. Nodes are panel nodes (not the same as exit egress). Needs central panel login; errors often cite stale panel path/token — re-run Full Deploy or Panel Login Info. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Ensure Full Deploy done.
2. 请执行：Enter node SSH/details.
3. 请执行：Add Node.
4. 请执行：If login fails, refresh panel credentials.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q025
**Question:** Exit 和 Node 有什么区别？
**Answer:** 根据当前 Black Fox 行为：Exit = traffic egress VPS; Node = 3X-UI panel node registration. AI chat explicitly asks to confirm Exit vs Node when SSH details are ambiguous. Wrong choice mis-wires routing. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：For country egress use Exit.
2. 请执行：For panel node scaling use Node.
3. 请执行：Confirm in AI chat or wizard labels.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q026
**Question:** 什么是 Add Domain？
**Answer:** 根据当前 Black Fox 行为：Connect Cloudflare or ArvanCloud and manage DNS from the app. DNS page supports Cloudflare (email + API token) and ArvanCloud (machine user + API key), import zones, create A records for central or bot webhook subdomain. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Open Add Domain / DNS.
2. 请执行：Choose provider.
3. 请执行：Connect & Import Zones.
4. 请执行：Point A records to central/bot IP.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q027
**Question:** 什么是 Configure CDN？
**Answer:** 根据当前 Black Fox 行为：Configure CDN for domain and panel route (Pro feature family). Monetized Add CDN capability; AI template collects provider, domain/zone, API token/key. Used with domain for panel access over CDN. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Activate Pro/access CDN unlock.
2. 请执行：Have domain ready.
3. 请执行：Configure CDN with provider details.
4. 请执行：Verify panel via domain.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q028
**Question:** 什么是 Add Subscription？
**Answer:** 根据当前 Black Fox 行为：Pro subscription setup for client subscription URLs. Feature `add_subscription` unlocks with Basic Full or Pro tiers per auth rules; used to publish subscription endpoints for clients. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Ensure license allows it.
2. 请执行：Run Add Subscription after panel ready.
3. 请执行：Share subscription URL from Test Client / panel.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q029
**Question:** 什么是 Proxy Settings？
**Answer:** 根据当前 Black Fox 行为：Proxy for reaching the 3X-UI panel and the internet from restricted networks. SSH Proxy Settings with profiles: none, auto-detect, Iran profile, free country profile; SOCKS5 or HTTP. Save and Test Connection. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Open Proxy Settings.
2. 请执行：Choose mode/type/host/port.
3. 请执行：Test Connection.
4. 请执行：Save.
5. 请执行：Retry panel/AI/hub operations.
6. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q030
**Question:** 什么时候需要 Proxy？
**Answer:** 根据当前 Black Fox 行为：When Direct access to hub, panel, or SSH path fails on filtered networks. Product network pattern prefers Direct first, then program proxy. Iran profile vs free-country profile helps match local filtering. AI chat can guide proxy updates. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Try Direct.
2. 请执行：If timeouts, open Proxy Settings.
3. 请执行：Enable Iran or free profile as appropriate.
4. 请执行：Retest.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q031
**Question:** 如何激活 License？
**Answer:** 打开 Registration → 复制 Device ID → 粘贴代码/claim 并 Activate（或走 foxnext.net 的 TX 支付流程）。
**Step by step solution:**
1. 打开 Registration 标签。
2. 请执行：Paste code or verify TX.
3. 请执行：Wait for success.
4. 请执行：Confirm Basic/Pro/AI status badges.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q032
**Question:** 什么是 claim 码？
**Answer:** 根据当前 Black Fox 行为：Website-style code (`PREFIX-CLM-…`) with no Device ID until first unlock binds the PC. PAS help: claim codes match website Activation; Device ID binds on first use in the Windows app. Prefixes include BFXB (Basic), BFXP (Pro), BFXA (AI Pro), BFXQ (AI quota). 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Buy/generate claim code on foxnext.net / PAS.
2. 请执行：Open app Registration.
3. 请执行：Paste code once on the intended PC.
4. 请执行：Do not share after binding.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q033
**Question:** 什么是设备绑定码？
**Answer:** 根据当前 Black Fox 行为：Code already tied to a Device ID / fingerprint for a specific PC. PAS can generate machine-bound AI Pro (and related) codes. Verify tool distinguishes claim vs machine-bound vs tier. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Copy Device ID from Registration.
2. 请执行：Ask support/PAS for machine-bound code if needed.
3. 请执行：Paste on that same PC only.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q034
**Question:** 什么是 Reactivation？
**Answer:** 根据当前 Black Fox 行为：Restore this PC’s prior activation from the server without manually saving the code. Messages: checking previous activation; success; success with code loaded; not found; expired; failed (check internet). Does not invent a new purchase. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Open Registration on the same device.
2. 请执行：Tap Reactivation.
3. 请执行：If expired, renew purchase.
4. 请执行：If not found, activate with code/TX.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q035
**Question:** 什么是 Device ID / License ID？
**Answer:** 根据当前 Black Fox 行为：This PC’s license fingerprint for AI status checks and support. Registration page hint: Device ID is for AI status checks and support. Copy Device ID button available. Used when claiming binds, reactivation lookups, and AI quota checks. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 打开 Registration 标签。
2. 复制 Device ID。
3. 请执行：Send to support only when asked.
4. 请执行：Keep consistent after OS reinstall unless hardware identity changes.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q036
**Question:** 为什么 My Code 还不可用？
**Answer:** 根据当前 Black Fox 行为：Activate once, or use Reactivation to load the code from the server. `reg.my_code_empty`: “Not available yet — activate once, or tap Reactivation to load from server.” 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Complete first activation.
2. 请执行：Or tap Reactivation.
3. 请执行：Then copy activation code if shown.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q037
**Question:** 使用什么支付网络？
**Answer:** 根据当前 Black Fox 行为：USDT on BEP-20 (BSC). Registration tutorial: open wallet, select USDT BEP-20, send exact plan amount to the shown wallet, paste TX HASH / TX ID. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Use BEP-20 only (not TRC20/ERC20).
2. 请执行：Send exact amount.
3. 请执行：Wait for confirmation.
4. 请执行：Paste TX and verify.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q038
**Question:** Basic 多少钱？
**Answer:** 根据当前 Black Fox 行为：Catalog anchors around 19 USDT for 18 months; duration pricing is host-editable. Default amount constant 19 USDT; `license-access.json` lists Basic prices by months (e.g. 12→13.5 … 18→19.0 … 30→30.0 USDT). Live pricing may come from hub — if missing, app asks contacting @HiBlackFoxVpn. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Check foxnext.net Activation for live price/months.
2. 请执行：Pay exact amount BEP-20.
3. 请执行：Activate in app.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q039
**Question:** Pro 多少钱？
**Answer:** 根据当前 Black Fox 行为：Catalog uses ~33 USDT at 21 months / ~28.5 at 18; anchor 45 at 30 months. Code default `AmountProFull = 33`. Host catalog: Pro 12→20 … 18→28.5, 21→33, 30→45 USDT. Prefer website/live hub pricing. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Confirm months on website.
2. 请执行：Pay exact USDT BEP-20.
3. 请执行：Activate Pro.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q040
**Question:** AI Assistant Pro 多少钱？
**Answer:** 根据当前 Black Fox 行为：Catalog ~35–40 USDT mid-duration; anchor 55 at 30 months; includes AI quota flag. Default `AmountAIProFull = 40`. Catalog ai_pro prices 12→24.5 … 18→35, 21→40, 30→55. `includes_ai_quota: true` for AI Pro mode. 不要编造价格或版本；以应用 UI 为准。
**Step by step solution:**
1. 请执行：Buy AI Pro on foxnext.net.
2. 请执行：Activate in app.
3. 请执行：Confirm AI quota active before chatting.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q041
**Question:** AI quota 充值（BFXQ）是什么？
**Answer:** `BFXQ` 前缀的 AI quota 充值码（常为 `BFXQ-CLM-…` 这类 claim）不会改变 License 模式。目录项 `ai_quota` 与许可证分离。PAS 可生成充值 claim；claim 只增加配额。
**Step by step solution:**
1. 请执行：If quota exhausted, buy AI quota / get BFXQ code.
2. 请执行：Paste in Registration unlock.
3. 请执行：Recheck AI status.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q042
**Question:** License 有效期多久？
**Answer:** 时长通常按 Hub 目录为 12–30 个月；未指定时常见默认 18 个月。`license-access.json` 月份：12、15、18、21、24、27、30。过期后完整功能会被锁定。
**Step by step solution:**
1. 请执行：Pick months at purchase.
2. 请执行：Note expiry in Registration.
3. 请执行：Renew before expiry for uninterrupted Pro/AI.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q043
**Question:** 一次购买能否覆盖多台设备？
**Answer:** 目录最多支持 3 台设备折扣（第2台约20%，第3台约30%）。每个 claim 在首次 Activate 时绑定该机 Device ID；不要把同一 claim 用在无关的多台电脑。
**Step by step solution:**
1. 请执行：Buy multi-device plan on website if offered.
2. 请执行：Activate each PC with its assigned code.
3. 请执行：Contact support if device transfer needed.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q044
**Question:** 重复使用 TX HASH 会怎样？
**Answer:** 已使用的 TX 在本地与 Hub 都会被拒绝（`tx_already_used` / `tx_already_claimed`）。claim 之后再次输入 TX 通常不再显示代码。
**Step by step solution:**
1. 请执行：Do not reuse old TX.
2. 请执行：If code already claimed, use Reactivation on bound PC.
3. 必要时将 Device ID 发给 @HiBlackFoxVpn。
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q045
**Question:** “claim already bound” 是什么意思？
**Answer:** 表示该 claim 已绑定到另一台设备的 Device ID（`bound_other_device` / `claim_bound`）。同一 claim 无法解锁第二台无关电脑。
**Step by step solution:**
1. 请执行：Use the original PC + Reactivation.
2. 请执行：Or purchase another device seat.
3. 请执行：Support can help with Device ID evidence.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q046
**Question:** 激活码无效——怎么办？
**Answer:** “Invalid activation code” 通常因拼写错误、层级前缀错误、粘贴不完整或无效代码。设备绑定码还要求 Device ID 为本机。
**Step by step solution:**
1. 请执行：Copy code again carefully.
2. 请执行：Confirm BFXB/BFXP/BFXA/BFXQ prefix.
3. 请执行：Use correct PC.
4. 请执行：Ask support to inspect code.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q047
**Question:** TX 未找到 / 待确认 / 金额错误？
**Answer:** 等待 BEP-20 确认；金额与收款地址须与页面完全一致。错误包括：TX 未找到、失败、收款错误、金额不足、非 USDT BEP-20、pending。
**Step by step solution:**
1. 请执行：Confirm BSC explorer shows success.
2. 请执行：Exact USDT amount.
3. 请执行：Correct wallet address.
4. 请执行：Retry verify.
5. 请执行：Contact support with TX if stuck.
6. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q048
**Question:** “Please activate via Registration tab first” 是什么意思？
**Answer:** 表示功能被 License 门控（`dialog.need_activate` / Limited Access）。Basic 无许可证时仅 Setup Central、Connect SSH、Full Deploy 免费。
**Step by step solution:**
1. 打开 Registration 标签。
2. 请执行：Activate Basic/Pro/AI.
3. 请执行：Retry the operation.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q049
**Question:** “This feature requires Pro activation” 是什么意思？
**Answer:** 在 Basic/锁定状态下使用了仅 Pro 功能（`dialog.need_pro`）。隧道链及部分 CDN/Subscription/Node 需要 Pro 或 AI Pro。
**Step by step solution:**
1. 请执行：Activate Pro or AI Pro.
2. 请执行：Switch View to Pro/AI Pro.
3. 重试。
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q050
**Question:** License 过期后还能用应用吗？
**Answer:** 完整许可功能会锁定直至续期。可见 “License expired”。Reactivation 也可能返回 expired。
**Step by step solution:**
1. 请执行：Note Device ID.
2. 请执行：Purchase renewal on foxnext.net.
3. 请执行：Activate or Reactivation.
4. 请执行：Confirm badge cleared.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q051
**Question:** 网站实时价格在哪里定义？
**Answer:** 实时价格在 Hub 的 `license-access.json`，改价无需重建应用。Hub 不可用时回退代码常量。
**Step by step solution:**
1. 请执行：Prefer foxnext.net displayed price.
2. 请执行：If app says pricing not received, contact @HiBlackFoxVpn.
3. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q052
**Question:** 什么是 Initial / Central Server Setup？
**Answer:** Central Server Setup 在本地保存中心服务器 SSH（IP、认证、国家、草稿）。Deploy 前必需。
**Step by step solution:**
1. 请执行：Open setup central.
2. 请执行：Fill IP/port/user/auth/country.
3. 请执行：Save.
4. 执行 Connect SSH。
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q053
**Question:** 保存时为什么不能改 Host/IP？
**Answer:** 产品提示：保存时不能改 Host/IP；换 IP 请走新建服务器流程。用于保护库存与 chain 编号完整性。
**Step by step solution:**
1. 请执行：Keep IP on edit of credentials.
2. 请执行：For a new VPS, use Add/new server flow.
3. 请执行：Align chain number with Pro hops.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q054
**Question:** Full Deploy 完成但面板打不开——下一步？
**Answer:** 检查 Panel Login Info（URL/path）、Proxy、防火墙并重跑面板相关操作。无凭据 → Full Deploy。节点登录失败常见于过期 path/token。
**Step by step solution:**
1. 请执行：Open Panel Login Info.
2. 请执行：Try URL in browser.
3. 请执行：Enable Proxy if filtered.
4. 请执行：Re-run Full Deploy / install 3X-UI.
5. 请执行：Run Diagnostic Center.
6. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q055
**Question:** 单独的 Install WireGuard / Install 3X-UI 是什么？
**Answer:** 可仅在 Central 安装/更新 WireGuard 或仅 Sanaei 面板——Full Deploy 部分成功时有用。Settings → Check Update 3X-UI 会缓存包供下次安装。
**Step by step solution:**
1. 请执行：Confirm SSH OK.
2. 请执行：Run the needed install button.
3. 请执行：Verify Panel Login Info.
4. 请执行：Continue Configure Panel.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q056
**Question:** 什么是 Diagnostic Center？
**Answer:** Diagnostic Center 只读检查 SSH、WireGuard、面板、DNS、CDN 与 Exit。查看 OK/Warning/Error，并可导出给支持。
**Step by step solution:**
1. 请执行：Open Check System.
2. 请执行：Run Checks.
3. 请执行：Fix reported items.
4. 请执行：Export logs if contacting support.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q057
**Question:** 什么是 Link Test？
**Answer:** Link Test 评估连通性并建议 WireGuard、GRE 或 Reverse Tunnel (Stealth-WSS)。最终应用通常经 Mesh 或 Add Server 的链路类型。
**Step by step solution:**
1. 请执行：Ensure servers registered.
2. 请执行：Run Link Test (ops/AI).
3. 请执行：Apply recommended link type.
4. 请执行：Redeploy mesh agents if needed.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q058
**Question:** 什么是 GRE fallback？
**Answer:** 若 WireGuard 隧道失败，应用会建议 GRE。Mesh 故障切换顺序：WireGuard → GRE → Reverse Tunnel (Stealth-WSS) → 备份。
**Step by step solution:**
1. 请执行：When prompted, choose Yes for GRE if WG blocked.
2. 请执行：Or set link type explicitly.
3. 请执行：Verify with Link Test / mesh status.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q059
**Question:** 什么是 Reverse Tunnel (Stealth-WSS)？
**Answer:** 链路/Mesh 栈中的受保护反向隧道，产品名 Reverse Tunnel (Stealth-WSS)。在直连 WG/GRE 不佳时使用，并由 Link Monitor Agent 监控。
**Step by step solution:**
1. 请执行：Prefer after Link Test recommends it.
2. 请执行：Deploy via Mesh / link type.
3. 请执行：Keep agents running.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q060
**Question:** 什么是 Mesh / Link Monitor Agent？
**Answer:** 运行在 Central/Tunnel/Exit/Node 上的常驻代理，用于路径健康与故障切换。Mesh 向导安装它们；安装时各 VPS 从 GitHub 下载工具。
**Step by step solution:**
1. 请执行：Register hosts.
2. 请执行：Open Mesh / CDN & Mesh section.
3. 请执行：Install agents.
4. 请执行：Refresh Status (installed/running).
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q061
**Question:** Mesh 代理是否需要 Windows 应用一直打开？
**Answer:** 不需要——Windows 应用关闭后代理仍在服务器运行。应用用于安装/状态/修复。
**Step by step solution:**
1. 请执行：Deploy agents once.
2. 请执行：Close app if desired.
3. 请执行：Refresh Status later to verify.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q062
**Question:** Mesh 代理显示 missing/stopped——怎么办？
**Answer:** 重新 Deploy Mesh 并 Refresh Status。标签：已安装/缺失、Running/Stopped/未知。结果形如 “Mesh agents installed: X ok, Y failed”。
**Step by step solution:**
1. 请执行：Refresh Status.
2. 请执行：Re-run mesh install on failed hosts.
3. 请执行：Check SSH to those hosts.
4. 请执行：Re-test links.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q063
**Question:** 什么是 Mirza Bot？
**Answer:** Telegram 机器人向导：在选定主机安装 Mirza 并预填面板凭据。选项：安装 Mirza、保存其他机器人或迁移。需要 bot token 与管理员。
**Step by step solution:**
1. 请执行：Have panel credentials.
2. 请执行：Open Add Telegram Bot / Install Mirza.
3. 请执行：Enter token/admin.
4. 请执行：Install or update with backup.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q064
**Question:** 可以把 Mirza 迁到另一台服务器吗？
**Answer:** 可以——选择器含 Move existing bot。Update/Move 前建议备份。
**Step by step solution:**
1. 请执行：Backup Mirza.
2. 请执行：Choose move.
3. 请执行：Enter destination SSH.
4. 请执行：Verify webhook/DNS if used.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q065
**Question:** 应用支持哪些语言？
**Answer:** 多语言 UI：英语、波斯语、俄语、阿拉伯语、德语、法语、印地语、土耳其语等。首次选择；Settings → Language 作用于全部标签。波斯语为 RTL。
**Step by step solution:**
1. 请执行：Settings → Language.
2. 请执行：Apply.
3. 请执行：Restart UI path if a tab looks stale. NEED_MORE_REVIEW for exact full language list beyond en.go keys if extras load dynamically.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q066
**Question:** Setup.exe 与 Portable exe 有何区别？
**Answer:** Setup 安装到 LocalAppData\Programs；Portable 凭 `portable.txt` 把数据放在 exe 旁。客户通常更推荐 Setup.exe。
**Step by step solution:**
1. 请执行：Prefer Setup for normal users.
2. 请执行：Use portable when you must avoid installer.
3. 请执行：Do not mix data folders casually.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q067
**Question:** Delete History 做什么？
**Answer:** 清除本地历史（SSH、日志、部署状态、本地 CDN 等），不改远程服务器；保留语言、模式与 License。
**Step by step solution:**
1. 请执行：Confirm you have remote access elsewhere.
2. 请执行：Run Delete History.
3. 请执行：Re-enter servers to continue ops.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q068
**Question:** Delete Exit Servers & Node 做什么？
**Answer:** 从 Exit 移除 WireGuard/microsocks/防火墙并清理 Central 对应隧道；保留 SSH。可删全部或单个；Node 尽可能从面板注销。
**Step by step solution:**
1. 请执行：Open delete wizard.
2. 请执行：Choose Exit or Node.
3. 请执行：All or one.
4. 请执行：Confirm warning.
5. 请执行：Re-add if needed.
6. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q069
**Question:** Delete Tunnel Servers 做什么？
**Answer:** 移除 Pro 链路 hop；删除一个 hop 可能重置更高序号。仍依赖该 hop 的 Exit 须先删除。
**Step by step solution:**
1. 请执行：Delete dependent exits first.
2. 请执行：Delete tunnels (all/one).
3. 请执行：Rebuild chain if required.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q070
**Question:** DELETE — Reset All Servers 做什么？
**Answer:** 从所有已配置服务器移除 WireGuard 与面板并清除本地部署数据；保留 SSH。不同于 OS 级 Factory Reset。
**Step by step solution:**
1. 请执行：Read confirm body carefully.
2. 请执行：Confirm.
3. 请执行：Wait for completion.
4. 请执行：Full Deploy again to rebuild.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q071
**Question:** 什么是 Factory Reset Server？
**Answer:** 破坏性远程重置趋向全新 VPS；此次操作的密码不保存。针对数据、服务、VPN 包、隧道、防火墙、用户与自定义设置。不支持的系统会失败。
**Step by step solution:**
1. 请执行：Settings maintenance / Factory Reset.
2. 请执行：Enter IP/user/password or PEM.
3. 请执行：Confirm warning.
4. 请执行：Only on disposable VPS.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q072
**Question:** Delete History 会删除 License 吗？
**Answer:** 不会——保留语言、模式与 License 激活。但重装 Windows 可能改变 Device ID → 使用 Reactivation。
**Step by step solution:**
1. 请执行：Delete History if cleaning local inventory.
2. 请执行：License should remain.
3. 请执行：If license missing after Windows reinstall, Reactivation.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q073
**Question:** 应用 Update 如何工作？
**Answer:** Settings → Update BlackFox & Wallet Address；强制更新时旧版会被挡住，需安装官网/Hub 的新 Setup。
**Step by step solution:**
1. 请执行：When prompted, download latest Setup.
2. 请执行：Install over.
3. 请执行：Reopen app.
4. 请执行：Reactivation if needed.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q074
**Question:** 什么是 Check Update 3X-UI？
**Answer:** 将最新 Sanaei 面板包下载到本地缓存供日后安装； alone 不会升级服务器上现网面板，除非再跑安装/更新操作。
**Step by step solution:**
1. 请执行：Settings → packages.
2. 请执行：Download if newer.
3. 请执行：Next panel install uses cache.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q075
**Question:** Android 与 Windows 有何不同？
**Answer:** Windows 是完整 Installer 运维面；Android 为配套应用（打包/引擎不同）并共享 AI 人设。Full Deploy/Mesh 通常优先 Windows。
**Step by step solution:**
1. 请执行：Use Windows for Full Deploy/mesh.
2. 请执行：Install full Android APK for engine features.
3. 请执行：Same foxnext.net licenses conceptually via Device ID rules on each platform. NEED_MORE_REVIEW for exact Android license parity edge cases.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q076
**Question:** 如何联系支持？
**Answer:** Telegram `@HiBlackFoxVpn`、网站 foxnext.net、邮箱 support@foxnext.net、频道 `@BlackFoxVPN`。以 Contact 标签实时值为准。
**Step by step solution:**
1. 请执行：Open Contact tab or t.me.
2. 请执行：Send Device ID + short problem + screenshots/logs.
3. 请执行：Do not send passwords in public groups.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q077
**Question:** 给支持发消息应包含什么？
**Answer:** 提供 Device ID、应用模式、操作名、终端片段、TX/代码类型（公开聊天勿贴完整密钥）。Diagnostic 导出很有用。
**Step by step solution:**
1. 复制 Device ID。
2. 请执行：Note version from Settings/update.
3. 请执行：Attach Diagnostic summary.
4. 请执行：Message @HiBlackFoxVpn.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q078
**Question:** 什么是 BlackFox MCP？
**Answer:** 本地 MCP 桥：外部 AI 应用在本程序保持打开时可调用 Black Fox 工具。Activate MCP，复制 mcp.json 到客户端 MCP 设置。
**Step by step solution:**
1. 请执行：Open BlackFox MCP.
2. 请执行：Activate.
3. 请执行：Copy mcp.json.
4. 请执行：Configure external AI.
5. 请执行：Keep Installer running.
6. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q079
**Question:** AI 提示需要激活 AI Assistant Pro
**Answer:** 须在 Registration 解锁 AI Pro（`view.ai_pro_locked`）。仅有 Basic/Pro 不足以使用 AI 聊天。
**Step by step solution:**
1. 请执行：Buy/activate AI Pro.
2. 请执行：Reselect AI Pro mode.
3. 请执行：Retry chat.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q080
**Question:** AI quota 用尽——怎么办？
**Answer:** 配额已用尽；用 BFXQ 充值或联系支持续期。也可能出现 `ai.quota.exhausted` / expired / not_found / disabled。
**Step by step solution:**
1. 复制 Device ID。
2. 请执行：Buy AI quota (BFXQ) or message @HiBlackFoxVpn.
3. 请执行：Activate recharge code.
4. 请执行：Retry chat.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q081
**Question:** AI 聊天附件有哪些限制？
**Answer:** 每条消息最多 3 张图、5 个文本文件。超出返回 `too_many_images` / `too_many_text_files`。
**Step by step solution:**
1. 请执行：Reduce attachments.
2. 请执行：Resend.
3. 请执行：Prefer text SSH details when possible.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q082
**Question:** AI 会在未确认时执行操作吗？
**Answer:** 不会——先分析，再 Yes/No 确认，然后执行。仅入队不等于执行。
**Step by step solution:**
1. 请执行：Review proposed action.
2. 请执行：Reply Yes to run.
3. 请执行：Wait for “process finished” or failure.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q083
**Question:** AI 说操作已开始——要等多久？
**Answer:** 等待终端/状态完成；勿随意关闭 busy 窗口。状态含 wait / done / failed。
**Step by step solution:**
1. 请执行：Keep window open.
2. 请执行：Watch terminal.
3. 请执行：On failure, read error and retry or Diagnose.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q084
**Question:** AI 能否添加自定义 v2ray outbound？
**Answer:** 可以（AI Pro）——粘贴 outbound JSON；面板上 AI outbound 最多 10 条。在面板 UI 删除不会重置 AI 计数器。无效 JSON 会被拒绝。
**Step by step solution:**
1. 请执行：Paste one outbound per request.
2. 请执行：Confirm apply.
3. 请执行：Contact support if need more than 10.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q085
**Question:** Configure Panel 默认 inbound 端口指引是什么？
**Answer:** Configure Panel 提示通常为 443 VLESS、80 Trojan、8080 WireGuard；以 Panel Login Info / 客户端测试的实际端口为准。
**Step by step solution:**
1. 请执行：Prefer defaults unless you know you need others.
2. 请执行：Open firewall for those ports.
3. 请执行：Test Client.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q086
**Question:** 找不到 Central 面板凭据？
**Answer:** 请先完成 Full Deploy 以保存面板 URL/用户/密码/令牌。许多操作依赖这些凭据。
**Step by step solution:**
1. 执行 Full Deploy。
2. 请执行：Panel Login Info non-empty.
3. 请执行：Retry Add Node / proxy panel ops.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q087
**Question:** SSH host key 变更——安全吗？
**Answer:** 常见于 VPS 重装后；仅在信任该服务器时 Accept。对话框也会提示可能 MITM；Accept 会清除已存密钥并重试。
**Step by step solution:**
1. 请执行：Confirm you reinstalled the VPS or changed keys.
2. 请执行：Accept if trusted.
3. 请执行：If unexpected, stop and check provider console/IP.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q088
**Question:** SSH 认证失败（密钥与密码）？
**Answer:** 密码与密钥均无效/过期；错误值不会保存。标题：SSH authentication failed。
**Step by step solution:**
1. 请执行：Reset password in provider panel if needed.
2. 请执行：Fix PEM formatting.
3. 请执行：Confirm user is allowed SSH.
4. 请执行：Connect SSH again.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q089
**Question:** SSH 时 Linux 密码过期？
**Answer:** 应用会进入 Change Linux Password（当前/新/确认）。结果为成功或 mismatch/required/failed。
**Step by step solution:**
1. 请执行：Enter current and new password.
2. 请执行：Confirm match.
3. 请执行：Retry Connect SSH.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q090
**Question:** SSH timeout 的原因？
**Answer:** 网络过滤、错误 IP/端口、商家防火墙或需要 Proxy。不一定是密码错误（`log.ssh_timeout`）。
**Step by step solution:**
1. 请执行：Ping/port-check from another network if possible.
2. 请执行：Verify IP/port.
3. 尝试 Proxy Settings。
4. 请执行：Check VPS running in provider UI.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q091
**Question:** 什么是 topology 视图？
**Answer:** 面板就绪，或链路已部署且存在面板客户端时显示拓扑；否则 `topology_not_ready`。
**Step by step solution:**
1. 执行 Full Deploy。
2. 请执行：Add links/exits.
3. 请执行：Ensure panel client exists.
4. 请执行：Open Topology.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q092
**Question:** 什么是 Add OutBounds？
**Answer:** 在面板添加 outbound（手动或在 AI Pro 粘贴自定义 JSON），用于 Exit 与路由。
**Step by step solution:**
1. 请执行：Panel must be ready.
2. 请执行：Use Configure Panel / Add OutBounds / AI outbound paste.
3. 请执行：Test Client.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q093
**Question:** Basic 能否到处使用 Cloudflare CDN？
**Answer:** CDN 属于 Pro 能力集；Basic 聚焦 Central+Exit，不会像 Pro 那样开放 CDN。
**Step by step solution:**
1. 请执行：Activate Pro for CDN.
2. 请执行：Add Domain.
3. 请执行：Configure CDN.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q094
**Question:** 应用内支持哪些 DNS 提供商？
**Answer:** Cloudflare（邮箱 + Zone:DNS:Edit 的 API token）与 ArvanCloud（机器用户 + API key）。可选 bot webhook 子域与面板域名分开。
**Step by step solution:**
1. 请执行：Create API credentials at provider.
2. 请执行：Connect & Import Zones.
3. 请执行：Create A records.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q095
**Question:** Bot webhook DNS 与面板域名有何不同？
**Answer:** 可选的 Telegram bot webhook 子域；不需要就跳过——不是面板域名。
**Step by step solution:**
1. 请执行：Decide if Mirza needs webhook domain.
2. 请执行：Fill bot subdomain + IP.
3. 请执行：Create A → Bot.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q096
**Question:** 什么是 Diagnose & Repair？
**Answer:** 更广的检查/修复（磁盘/流量、ping/过滤、Mesh 链路、域名/CDN、损坏参数）。作为 AI 任务/运维；仅在需要新 IP 或密钥时询问。
**Step by step solution:**
1. 请执行：Register servers first.
2. 请执行：Run Diagnose & Repair.
3. 请执行：Approve fixes.
4. 请执行：Re-test clients.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q097
**Question:** 状态栏 busy 转圈是什么意思？
**Answer:** 长操作进行中；请等待完成。过早关闭会提示工作未完成。
**Step by step solution:**
1. 等待。
2. 请执行：Watch terminal.
3. 请执行：Keep Open if prompted.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q098
**Question:** 可以停止正在运行的 terminal 操作吗？
**Answer:** 可以——终端 Stop 需确认；会中断当前进程并标记为用户停止。
**Step by step solution:**
1. 请执行：Click Stop.
2. 请执行：Confirm.
3. 请执行：Re-run cleanly if needed.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q099
**Question:** 已安装模式下本地文件存在哪里？
**Answer:** 已安装模式通常在 `%LocalAppData%\Programs\Black Fox Vpn`。Portable 则在 exe 旁（有 marker）。
**Step by step solution:**
1. 请执行：Win+R → `%LocalAppData%\Programs`.
2. 请执行：Find Black Fox Vpn.
3. 请执行：Do not delete license-critical files casually.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q100
**Question:** 如何复制 Device ID / wallet / TX / 激活码？
**Answer:** 专用 Copy 按钮，成功复制 Device ID、wallet、TX 与激活码时有提示。
**Step by step solution:**
1. 请执行：Click the Copy control.
2. 请执行：Paste into notepad/support chat.
3. 请执行：Verify no truncation.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q101
**Question:** 离线 / record-offline 激活路径是什么？
**Answer:** Hub API 可用 claim_pending 记录离线代码/TX。并非所有离线对话框都已逐字核对——存疑标 NEED_MORE_REVIEW。
**Step by step solution:**
1. 请执行：Prefer online verify.
2. 请执行：If offline code issued, activate in app when online.
3. 请执行：Support if claim_pending stuck.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q102
**Question:** BFXB / BFXP / BFXA / BFXQ 前缀含义？
**Answer:** BFXB=Basic，BFXP=Pro，BFXA=AI Pro，BFXQ=AI quota。目标功能前缀错误会导致解锁失败。
**Step by step solution:**
1. 请执行：Match purchase to prefix.
2. 请执行：Paste exact code.
3. 请执行：For quota only use BFXQ.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q103
**Question:** AI Pro 是否包含 Pro 的手动功能？
**Answer:** 是——AI Pro 可通过聊天执行 Pro 操作并同时保留手动 Pro；但 AI 专用门控仍独立。
**Step by step solution:**
1. 请执行：Activate AI Pro.
2. 请执行：Use AI chat or switch to Pro-style manual ops as allowed.
3. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q104
**Question:** 解锁 Pro 能获得 AI Assistant Pro 吗？
**Answer:** 不能——普通 Pro 解锁绝不会授予 AI Assistant Pro（`FeatureAIProFull`）。
**Step by step solution:**
1. 请执行：Buy AI Pro separately.
2. 请执行：Or upgrade path on website if offered (`already_ai_pro` / upgrade reasons on API).
3. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q105
**Question:** 网站 Activation 与应用内 TX 验证有何不同？
**Answer:** 网站付款后发 claim；应用也可验证 TX 或粘贴代码。claim 后 TX 不再显示代码。Device ID 绑定在 Registration。
**Step by step solution:**
1. 请执行：Pay on foxnext.net.
2. 请执行：Receive claim code.
3. 请执行：Paste in Windows Registration.
4. 请执行：Keep Device ID record.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q106
**Question:** 什么是 PAS Generator？
**Answer:** 内部/管理员工具，用于签发 claim 与检查 TX / AI Device ID。非客户主路径；客户用 foxnext.net + Registration。
**Step by step solution:**
1. 请执行：Customers: use website/app only.
2. 请执行：Support staff: PAS for generate/verify.
3. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q107
**Question:** Add Exit 需要哪些前提？
**Answer:** Central 已 Full Deploy/面板就绪、具备 add_exit 许可，并能 SSH 到 Exit VPS。无 Central 面板则 outbound 接线失败。Basic 国家规则针对 Central，不一定限制 Exit 国家。
**Step by step solution:**
1. 执行 Full Deploy。
2. 请执行：Activate if locked.
3. 请执行：Add Exit with correct SSH.
4. 请执行：Configure Panel.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q108
**Question:** 为何部分 Tunnel 删除前必须先删 Exit？
**Answer:** 链路完整性——仍使用该 hop 的 Exit 须先删除；删除隧道向导会明确警告。
**Step by step solution:**
1. 请执行：Identify dependent exits.
2. 请执行：Delete those exits.
3. 请执行：Delete tunnel hops.
4. 请执行：Rebuild.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q109
**Question:** Pro 中的 chain number 是什么？
**Answer:** Pro 多跳隧道中 hop 的序号。若 IP 已登记在其他 chain number 下则拒绝保存。删除 hop 可能重置更高序号。
**Step by step solution:**
1. 请执行：Assign consistent chain numbers.
2. 请执行：Don’t reuse IP across conflicting chains.
3. 请执行：Rebuild after mid-chain deletes.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q110
**Question:** Exit 上 Microsocks 的作用？
**Answer:** 部署 Exit 时 microsocks 是 SOCKS outbound 路径的一部分；删除 Exit 时与 WG/防火墙一并移除。
**Step by step solution:**
1. 请执行：Let Add Exit install it.
2. 请执行：Don’t manually break microsocks.
3. 请执行：Use app delete/redeploy to fix.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q111
**Question:** WireGuard 客户端导入提示？
**Answer:** 将 `.conf` 导入 Windows/Android/iOS 的 WireGuard 应用。ensure inbound 后可在面板 Clients 看到客户端。
**Step by step solution:**
1. 请执行：Download/copy conf from Test Client.
2. 请执行：Import.
3. 请执行：Activate tunnel.
4. 请执行：Test IP/egress.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q112
**Question:** 面板默认端口相关说明？
**Answer:** 实际端口以 Full Deploy 写入 Panel Login Info 的为准（历史常提到 2053）。过期 path/token 是 Add Node 失败常见原因。
**Step by step solution:**
1. 请执行：Copy URL from Panel Login Info.
2. 请执行：Don’t guess old ports.
3. 请执行：Re-sync credentials after panel changes.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q113
**Question:** External Proxy 与面板 proxy 的关系？
**Answer:** Proxy Settings 帮助应用访问面板/互联网/Hub；不是最终用户 VPN 客户端内部代理。含 Iran / Free 等配置。
**Step by step solution:**
1. 请执行：Configure Proxy Settings in app.
2. 请执行：Test.
3. 请执行：Retry Panel Login / AI hub.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q114
**Question:** Registration 教程——如何找 TX HASH？
**Answer:** 从 Trust Wallet / MetaMask / Binance 历史复制 TxID（见 Registration 教程）。
**Step by step solution:**
1. 请执行：Open wallet activity.
2. 请执行：Open TX details.
3. 请执行：Copy hash starting with 0x.
4. 请执行：Paste in app.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q115
**Question:** Windows 上如何复制 System info？
**Answer:** Win+R → msinfo32，或应用内复制 System Info（若有），用于支持指纹。
**Step by step solution:**
1. 请执行：Prefer in-app Device ID.
2. 请执行：Use msinfo32 only if support asks.
3. 请执行：Don’t paste unrelated secrets.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q116
**Question:** 无法获取 Hub 价格时怎么办？
**Answer:** 若无法获取实时金额，界面可能引导联系 `@HiBlackFoxVpn`。
**Step by step solution:**
1. 检查网络/Proxy。
2. 请执行：Retry later.
3. 必要时将 Device ID 发给 @HiBlackFoxVpn。
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q117
**Question:** blackfoxupdate.ir 相关吗？
**Answer:** 更新 Hub 与 foxnext.net 并用（先 blackfoxupdate.ir 再 foxnext.net）。客户下载仍优先 foxnext.net。
**Step by step solution:**
1. 请执行：Allow app update check.
2. 请执行：If update fails, try from foxnext.net manually.
3. 请执行：NEED_MORE_REVIEW for end-user visible branding of blackfoxupdate.ir.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q118
**Question:** 什么是 Limited Access 对话框？
**Answer:** 需要 Activate 或 Pro 时的访问限制标题；与 need_activate / need_pro 成对出现。
**Step by step solution:**
1. 请执行：Read body.
2. 打开 Registration 标签。
3. 请执行：Unlock required tier.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q119
**Question:** 能否从 AI 聊天执行 Full Deploy？
**Answer:** 可以——模板“在 Central 上 Full Deploy”并附 SSH 详情。AI 会入队；确认后等待 done/failed。
**Step by step solution:**
1. 请执行：AI Pro mode.
2. 请执行：Pick Full Deploy task or paste template.
3. 请执行：Provide SSH.
4. 请执行：Confirm Yes.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q120
**Question:** AI 会恢复之前的聊天吗？
**Answer:** 打开时可能询问 Continue 或 New；聊天保存在本机。
**Step by step solution:**
1. 请执行：Read prompt.
2. 请执行：Reply Continue or New.
3. 请执行：Proceed.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q121
**Question:** 什么是 Move Central？
**Answer:** 将 Central 角色迁到新 VPS（AI/运维模板）。需要源与目标 SSH；高风险——先备份。向导完整字段：NEED_MORE_REVIEW。
**Step by step solution:**
1. 请执行：Backup panel/configs.
2. 请执行：Provide both SSH sets.
3. 请执行：Run move flow.
4. 请执行：Update DNS/CDN to new IP.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q122
**Question:** Subscription URL 与 VLESS 链接有何不同？
**Answer:** Test Client 可显示两者；Subscription 供会拉取更新列表的客户端。VLESS 通常是单条 inbound 链接。
**Step by step solution:**
1. 请执行：Configure Panel.
2. 请执行：Open Test Client.
3. 请执行：Share sub URL to users who need auto-update.
4. 请执行：Or share single VLESS for quick test.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q123
**Question:** 部署后 topology 为什么是空的？
**Answer:** 面板未就绪或缺少链路/客户端时拓扑为空（`topology_not_ready`）。
**Step by step solution:**
1. 请执行：Confirm Full Deploy success.
2. 请执行：Add at least one link/exit path.
3. 请执行：Ensure panel client exists.
4. 请执行：Refresh View.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q124
**Question:** Mesh 安装时 agent 工具从哪里下载？
**Answer:** Mesh 安装时代理工具从 GitHub 下载到该 VPS。受限 VPS 可能需要服务器侧 Proxy/访问 GitHub。
**Step by step solution:**
1. 请执行：Ensure VPS can reach GitHub.
2. 请执行：Retry mesh install.
3. 请执行：NEED_MORE_REVIEW for exact repo URLs shown in logs.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q125
**Question:** 什么是 Other CDN？
**Answer:** AI Pro 任务中用于主列表之外提供商的 CDN 选项。Diagnose & Repair 与 CDN 配置是不同任务。
**Step by step solution:**
1. 请执行：Choose provider or Other CDN.
2. 请执行：Supply API details as requested.
3. 请执行：Verify domain.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q126
**Question:** Hysteria / 特殊端口？
**Answer:** 部分端口会在流程中校验；Configure Panel 对 WG inbound 提示提到 8080。Hysteria 精确文案：NEED_MORE_REVIEW。
**Step by step solution:**
1. 请执行：Follow form validation.
2. 请执行：Don’t force closed ports.
3. 请执行：Check Diagnostic.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q127
**Question:** 可以使用非 root 的 SSH 用户吗？
**Answer:** 若用户具备安装所需 sudo 则可能；多数脚本假定高权限。除非熟悉镜像，否则推荐 root。
**Step by step solution:**
1. 请执行：Prefer root.
2. 请执行：If non-root, ensure passwordless sudo.
3. 请执行：NEED_MORE_REVIEW for full non-root support matrix.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q128
**Question:** 密码与密钥更推荐哪个？
**Answer:** 两者都支持；若都失败会出现 both_failed。云镜像常用密钥；面板重置后常用密码。
**Step by step solution:**
1. 请执行：Use provider-recommended auth.
2. 请执行：Paste full PEM including headers.
3. 请执行：Test Connect SSH.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q129
**Question:** server draft saved 是什么意思？
**Answer:** 本地已保存凭据/草稿但尚未完成 Deploy（`server.draft_saved`）。便于继续多页向导。
**Step by step solution:**
1. 请执行：Save draft.
2. 请执行：Continue later.
3. 请执行：Connect SSH before Full Deploy.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q130
**Question:** 操作进行中——仍要关闭吗？
**Answer:** 建议 Keep Open；Close Anyway 会使工作未完成（`dialog.close_busy_*`）。
**Step by step solution:**
1. 请执行：Choose Keep Open.
2. 请执行：Wait for finish.
3. 请执行：Only Close Anyway if stuck and you accept repair later.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q131
**Question:** 安装后如何更改应用语言？
**Answer:** Settings → Language → Apply 作用于全部标签。首次运行也有语言选择。
**Step by step solution:**
1. 请执行：Open Settings.
2. 请执行：Select language.
3. 请执行：Apply.
4. 请执行：Confirm labels updated.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q132
**Question:** Contact 标签显示哪些渠道？
**Answer:** 支持 `@HiBlackFoxVpn`、频道 `@BlackFoxVPN`、网站 foxnext.net、邮箱 support@foxnext.net。以 Contact 实时值为准。
**Step by step solution:**
1. 请执行：Open Contact.
2. 请执行：Tap support for help.
3. 请执行：Tap channel for announcements.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q133
**Question:** 邮件是主要支持渠道吗？
**Answer:** 产品内主通道通常是支持 Telegram；也有邮箱。为求速度请在 Telegram 发送 Device ID。
**Step by step solution:**
1. 请执行：Message @HiBlackFoxVpn.
2. 请执行：Use email if Telegram unavailable.
3. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q134
**Question:** “Update BlackFox & Wallet Address” 是什么？
**Answer:** Settings 操作，用于从 Hub 刷新更新元数据与支付 wallet 显示。
**Step by step solution:**
1. 请执行：Settings → Updates.
2. 请执行：Run update check.
3. 请执行：Install if force/min version requires.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q135
**Question:** 强制最低版本挡住应用——怎么办？
**Answer:** 安装不低于最低支持版本的发布包；过旧构建可能被强制挡住（`remote.force_*` / MustForceUpdate）。
**Step by step solution:**
1. 请执行：Download latest Setup from foxnext.net.
2. 请执行：Install.
3. 请执行：Relaunch.
4. 请执行：Reactivation if license UI resets.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q136
**Question:** AI 服务超时 / 网络错误？
**Answer:** 请重试；检查网络/Proxy。提示包括 timeout / could not reach AI service。
**Step by step solution:**
1. 请执行：Check connectivity.
2. 请执行：Configure Proxy if needed.
3. 请执行：Resend.
4. 请执行：If persistent, support with Device ID.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q137
**Question:** AI 暂时不可用？
**Answer:** `ai.disabled` 表示 Hub 关闭了 AI 服务；不一定是本地 License 问题。
**Step by step solution:**
1. 请执行：Wait and retry.
2. 请执行：Check foxnext announcements.
3. 请执行：Ask @HiBlackFoxVpn.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q138
**Question:** License 找不到 quota？
**Answer:** 请先激活 AI Assistant Pro（`ai.quota.not_found`）。这与 exhausted（用尽）不同。
**Step by step solution:**
1. 请执行：Activate AI Pro.
2. 请执行：Or apply BFXQ if only quota missing after AI Pro.
3. 请执行：Recheck status.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q139
**Question:** Delete All 会从磁盘删除 SSH 密码吗？
**Answer:** 不会——Reset All 保留 SSH；Delete History 清除本地凭据（保留 License）。勿混淆。
**Step by step solution:**
1. 请执行：Choose the delete that matches intent.
2. 请执行：Read confirm body.
3. 请执行：Proceed.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q140
**Question:** Factory Reset 会保留面板数据吗？
**Answer:** 不会——目标是把 VPS 推向初始状态且不可逆。不同于 Reset All（清软件但保留 SSH）。
**Step by step solution:**
1. 请执行：Use only if you intend to wipe VPS.
2. 请执行：Prefer Delete All for app-managed cleanup.
3. 请执行：Re-provision after factory reset.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q141
**Question:** 如何快速验证 mesh 故障切换？
**Answer:** 刷新代理状态；路径恢复通常数秒内自动。顺序：WG→GRE→Stealth-WSS→备份。
**Step by step solution:**
1. 请执行：Deploy agents.
2. 请执行：Refresh Status.
3. 请执行：Run Link Test.
4. 请执行：Simulate path issue only on test beds.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q142
**Question:** “Install always-on Link Monitor Agents” 范围是什么？
**Answer:** 安装在 Central、Tunnel、Exit 与 Node 主机上。
**Step by step solution:**
1. 请执行：Ensure each role has SSH saved.
2. 请执行：Run mesh deploy.
3. 请执行：Confirm each host Running.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q143
**Question:** 能否只把应用当面板书签管理器用？
**Answer:** 并非设计目标——它是运维部署工具库；Panel Login Info 只是部署后的一项功能。
**Step by step solution:**
1. 请执行：Deploy central.
2. 请执行：Then use panel info/clients.
3. 请执行：Or open external panel manually if you already have one (limited integration without saved creds).
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q144
**Question:** Basic / Pro / AI Pro 是否共享状态？
**Answer:** Basic/Pro/AI Pro 共用同一本地服务器/面板存储——没有并行的仅 AI 配置。
**Step by step solution:**
1. 请执行：Deploy once.
2. 请执行：Switch modes freely for UI.
3. 请执行：License still gates features.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q145
**Question:** Check System 与 Diagnose & Repair 有何不同？
**Answer:** Check System 为只读诊断；Diagnose & Repair 尝试修复。给支持举证时先用只读。
**Step by step solution:**
1. 请执行：Run Checks.
2. 请执行：Export if needed.
3. 请执行：Run Diagnose & Repair if appropriate.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q146
**Question:** 添加 Exit 后客户端测试失败？
**Answer:** 重跑 Configure Panel，检查 outbound/链路、SSH 到 Exit 与 Diagnostic。常见原因：Exit 部署不完整、WG/GRE 未起、outbound 标签不匹配、防火墙。
**Step by step solution:**
1. 请执行：Confirm exit deploy success.
2. 请执行：Configure Panel.
3. 请执行：Link Test.
4. 请执行：Test Client again.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q147
**Question:** Add Node 登录 Central 失败？
**Answer:** 面板 path/令牌过期——重跑 Full Deploy 或刷新 Panel Login Info（`node.err_central_login`）。
**Step by step solution:**
1. 请执行：Open Panel Login Info.
2. 请执行：Refresh via Full Deploy / panel install.
3. 请执行：Retry Add Node.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q148
**Question:** Portable 模式有数据丢失风险吗？
**Answer:** 移动/删除 Portable 文件夹风险高；安装模式用 LocalAppData。请备份该文件夹。
**Step by step solution:**
1. 请执行：Keep portable.exe + data together.
2. 请执行：Don’t run two copies fighting the same inventory.
3. 请执行：Prefer Setup for stability.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q149
**Question:** 网站多语言页面与应用有何关系？
**Answer:** foxnext.net 有多语言页面；应用语言独立，在 Settings 中更改。
**Step by step solution:**
1. 请执行：Browse foxnext.net in your language.
2. 请执行：Set app language separately.
3. 请执行：Use same support contacts.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q150
**Question:** 副标题 “Multi-Location VPN Manager” 是什么意思？
**Answer:** 指用同一 Installer 管理 Central 与多个 Exit/Tunnel/Node；核心价值是多地域拓扑自动化，而非单台 VPS。
**Step by step solution:**
1. 请执行：Full Deploy central.
2. 请执行：Add locations.
3. 请执行：Configure Panel.
4. 请执行：Optional mesh.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q151
**Question:** Factory Reset 时会保存密码吗？
**Answer:** 不会——Factory Reset 密码仅用于该次操作且不保存；不同于普通服务器 Save。
**Step by step solution:**
1. 请执行：Enter creds for factory reset only.
2. 请执行：They won’t be kept.
3. 请执行：Re-save server normally if you continue using it.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q152
**Question:** “SSH connected but probe output unexpected” 是什么意思？
**Answer:** 认证成功但 probe 输出异常（`log.ssh_probe_unexpected`）。可能是异常 shell/MOTD 或命令被拦。精确细节：NEED_MORE_REVIEW。
**Step by step solution:**
1. 请执行：Confirm distro is supported Linux.
2. 请执行：Retry Connect SSH.
3. 请执行：Check provider serial console.
4. 请执行：Send log line to support.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q153
**Question:** 能否把服务器面板截图附加到 AI 聊天？
**Answer:** 可以——最多 3 张图；AI 多模态（文本+图像），用于服务器/机器人等信息。
**Step by step solution:**
1. 请执行：Attach clear screenshots.
2. 请执行：Add short text.
3. 请执行：Confirm extracted details selection.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q154
**Question:** AI 把 Exit 和 Node 认错了？
**Answer:** 拒绝并澄清后重发；拒绝路径会要求说明用途或改选 Task。
**Step by step solution:**
1. 请执行：Reply No.
2. 请执行：State Exit or Node clearly.
3. 请执行：Resend details or use left-task buttons.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q155
**Question:** AI 聊天中的 Apply Actions 状态是什么？
**Answer:** 应用正在落实 AI 回复中排队的动作（preparing… applying_actions… finalizing）。
**Step by step solution:**
1. 等待。
2. 请执行：Confirm any Yes/No prompts.
3. 请执行：Watch terminal for real deploy results.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q156
**Question:** USDT 金额永远是 19/33/40 吗？
**Answer:** 19/33/40 是常见锚点/回退；按月的实时目录可能不同。务必支付 foxnext.net/应用内显示金额。
**Step by step solution:**
1. 请执行：Read on-screen amount.
2. 请执行：Pay exactly that on BEP-20.
3. 请执行：Don’t assume old chat prices.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q157
**Question:** Reactivation 提示 tier mismatch 怎么办？
**Answer:** 服务器有记录但与请求层级不符（`tier_mismatch`）。激活正确层级或联系支持对齐。
**Step by step solution:**
1. 请执行：Confirm which product you bought.
2. 请执行：Try matching activate button.
3. 请执行：Message support with Device ID.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q158
**Question:** claim 之后还能从旧 TX 找回代码吗？
**Answer:** 通常不行——claim 后 TX 不再显示代码。在已绑定设备用 Reactivation，或带 Device ID 找支持。
**Step by step solution:**
1. 请执行：Try Reactivation on original PC.
2. 请执行：Provide Device ID + TX to @HiBlackFoxVpn.
3. 请执行：Do not expect website to reprint claimed codes.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q159
**Question:** 新用户推荐的首次运行路径？
**Answer:** Setup → 语言 → Basic → Central → Connect SSH → Full Deploy → Panel Info → 需要时 Activate 后再加 Exit。受限网络用 Proxy。卡住联系 `@HiBlackFoxVpn`。
**Step by step solution:**
1. 请执行：Setup.exe from foxnext.net.
2. 请执行：Basic mode.
3. 请执行：Central IR/CN/RU.
4. 执行 Connect SSH。
5. 执行 Full Deploy。
6. 请执行：Test Client.
7. 请执行：Activate Pro/AI when needed.
8. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q160
**Question:** 客服应到哪里核对精确 UI 文案？
**Answer:** 精确 UI 文案见 `internal/i18n/en.go` / `locales/en.json` 与 Hub API 的 `reason_code`。未知 Linux stderr 标 NEED_MORE_REVIEW。
**Step by step solution:**
1. 请执行：Match screenshot to i18n.
2. 请执行：Use Troubleshooting.md for error playbooks.
3. 请执行：Escalate with Device ID + logs.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q161
**Question:** 切换 View 模式会清空服务器吗？
**Answer:** 不会——各模式共享同一本地存储。切换 View 只改界面与门控，不清除服务器。
**Step by step solution:**
1. 请执行：Save work if a wizard is open.
2. 请执行：Change mode on View.
3. 请执行：Confirm servers still listed under Operations.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q162
**Question:** Configure Panel 与 Full Deploy 有何不同？
**Answer:** Full Deploy 在 Central 安装 WG+面板；Configure Panel 修复已有 Exit/Node 的路由，不是再次安装 Central 面板。
**Step by step solution:**
1. 请执行：Finish Full Deploy first.
2. 请执行：Add Exit/Node as needed.
3. 请执行：Run Configure Panel.
4. 请执行：Use Panel Login Info only to view URL/creds.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q163
**Question:** 最多可以添加多少 Node？
**Answer:** 最多 6 个 Node（`MaxNodes`）；与 Pro 下 Exit 槽位逻辑相同。
**Step by step solution:**
1. 请执行：Unlock Pro.
2. 请执行：Open Add Node.
3. 请执行：Fill SSH + XUI source.
4. 请执行：Stop at six or replace a slot.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q164
**Question:** Full Deploy / Add Node 可用哪些 XUI 来源？
**Answer:** Sanaei GitHub、BlackFox Hub 或 Local PC 包。在 Full Deploy 与 Add Node 中选择。Local 适合离线/受限网络。
**Step by step solution:**
1. 请执行：Prefer Hub when online.
2. 请执行：Use Local if you have a verified package.
3. 请执行：GitHub when Hub is blocked (may be slower).
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q165
**Question:** Delete History 会保留什么？
**Answer:** 清除本地历史；保留语言、模式与 License。不同于 Reset All（远程清 WG/面板但保留 SSH）。
**Step by step solution:**
1. 请执行：Open the delete/history control.
2. 请执行：Confirm.
3. 请执行：Re-check Registration still unlocked.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q166
**Question:** DELETE — Reset All Servers 做什么？
**Answer:** 从已配置服务器移除 WG/面板；保留已存 SSH。之后需再次 Full Deploy。
**Step by step solution:**
1. 请执行：Confirm inventory is correct.
2. 请执行：Run Reset All Servers.
3. 执行 Connect SSH。
4. 请执行：Full Deploy again.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q167
**Question:** 可以只删除 tunnel hops 吗？
**Answer:** 可以——Delete Tunnel Servers 只重置 Pro 链路 hop，不一定清除 Exit/Central。
**Step by step solution:**
1. 请执行：Pro mode.
2. 请执行：Use Delete Tunnel Servers.
3. 请执行：Re-add tunnels if still needed.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q168
**Question:** 有哪些 Proxy 配置？
**Answer:** Proxy Settings 含 None / Auto / Iran / Free 等。网络策略：先 Direct，失败再用 Program Proxy（SSH、Hub HTTP、面板 API）。
**Step by step solution:**
1. 请执行：Open Proxy Settings.
2. 请执行：Try Auto if Direct fails.
3. 请执行：Iran profile when in restricted networks.
4. 请执行：Retry Connect SSH / updates.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q169
**Question:** 部署后在哪里查看面板 URL？
**Answer:** Panel Login Info 在面板安装/同步成功后显示已保存的 URL/用户/密码。
**Step by step solution:**
1. 请执行：Complete Full Deploy.
2. 请执行：Open Panel Login Info.
3. 请执行：Copy URL carefully (port + path).
4. 请执行：Log in via browser if needed.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q170
**Question:** Test Client / WG 做什么用？
**Answer:** Configure 之后用于校验的客户端/WireGuard 测试对话框；不能替代 Full Deploy。
**Step by step solution:**
1. 请执行：Ensure panel + exit path ready.
2. 请执行：Open Test Client.
3. 请执行：Import/test as prompted.
4. 请执行：If fail, run Link Test / diagnostics.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q171
**Question:** 什么是 Add Domain？
**Answer:** Pro 的 DNS 管理（Cloudflare / ArvanCloud 区域/记录；可选 bot webhook）。是叠加页而非主标签。
**Step by step solution:**
1. 请执行：Unlock Pro.
2. 请执行：Open Add Domain / DNS Manager.
3. 请执行：Enter API credentials.
4. 请执行：Create/update records.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q172
**Question:** UI 里有哪些 CDN 提供商？
**Answer:** UI 通常有 Arvan、Cloudflare 与 Other CDN。若见到第四个品牌标 NEED_MORE_REVIEW（内部键未必进 UI）。
**Step by step solution:**
1. 请执行：Pro mode.
2. 请执行：Open CDN modal.
3. 请执行：Pick Arvan/Cloudflare/Other.
4. 请执行：Save; apply via API when available.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q173
**Question:** 什么是 Mesh Servers？
**Answer:** Pro 页面：库存图、部署 Link Monitor 代理与链路状态；独立于 Operations 网格。
**Step by step solution:**
1. 请执行：Unlock Pro.
2. 请执行：Open Mesh Servers.
3. 请执行：Deploy agents when prompted.
4. 请执行：Read link status; repair via ops if down.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q174
**Question:** 什么是 Add Telegram Bot (Mirza)？
**Answer:** Pro 工具，用于安装/迁移 Mirza（或其他路径）。不同于 Black Fox 支持机器人；属 Mirza 面板销售机器人族。
**Step by step solution:**
1. 请执行：Pro unlock.
2. 请执行：Open Add Telegram Bot.
3. 请执行：Choose install / other / move.
4. 请执行：Supply bot token when asked.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q175
**Question:** 什么是 Move Central Server？
**Answer:** 将 Central 角色迁到另一台 VPS（Pro 工具）。影响大——库存与面板凭据须保持一致。向导精确字段：NEED_MORE_REVIEW。
**Step by step solution:**
1. 请执行：Backup panel/creds.
2. 请执行：Unlock Pro.
3. 请执行：Open Move Central.
4. 请执行：Follow wizard; re-verify Panel Login Info.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q176
**Question:** AI 任务中的 BlackFox MCP 是什么？
**Answer:** 激活 MCP 二进制 / mcp.json，让外部 AI 工具调用 Black Fox 动作。普通应用内聊天不需要。
**Step by step solution:**
1. 请执行：AI Pro unlocked.
2. 请执行：Run BlackFox MCP task.
3. 请执行：Confirm desktop MCP config.
4. 请执行：Use only if integrating external agents.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q177
**Question:** Diagnose & Repair 与 Check System 有何不同？
**Answer:** Check System 是本地 Diagnostics 标签；Diagnose & Repair 是 AI Pro 任务路径，变更前需确认。
**Step by step solution:**
1. 请执行：For quick local status → Check System.
2. 请执行：For guided fix → AI Pro Diagnose & Repair.
3. 请执行：Confirm Yes before apply.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q178
**Question:** 什么是 Link Test（AI）？
**Answer:** 用于测试拓扑链路的 AI 任务模板；配合 Configure Panel 与 Test Client，执行前确认。
**Step by step solution:**
1. 请执行：AI Pro chat.
2. 请执行：Choose Link Test.
3. 请执行：Confirm.
4. 请执行：Read terminal/status outcome.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q179
**Question:** 什么是 Add OutBounds（AI）？
**Answer:** 用于配置面板 outbound 的 AI 任务；最好在已有 Exit/Node 后使用，Apply 前确认。
**Step by step solution:**
1. 请执行：Ensure central panel ready.
2. 请执行：AI task Add OutBounds.
3. 请执行：Confirm extracted details.
4. 请执行：Verify in panel if needed.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q180
**Question:** Factory Reset 会保存我输入的密码吗？
**Answer:** 不会——Factory Reset 输入的密码仅用于该次操作，之后不保存。
**Step by step solution:**
1. 请执行：Enter creds when asked.
2. 请执行：Complete reset.
3. 请执行：Re-save SSH normally if you continue.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q181
**Question:** 在哪里更改语言？
**Answer:** Settings → 应用语言（及首次运行选择器）。foxnext.net 网站语言与应用 i18n 目录相互独立。
**Step by step solution:**
1. 请执行：Open Settings.
2. 请执行：Choose language.
3. 请执行：Apply.
4. 请执行：Confirm labels update (RTL for FA).
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q182
**Question:** Settings 里的 3X-UI 包管理器是什么？
**Answer:** Tools 区域管理 Deploy/Local PC 所用的离线/Hub 3X-UI 包。精确 UI 文案以当前 Settings 为准。
**Step by step solution:**
1. 请执行：Settings → Tools / packages.
2. 请执行：Refresh from hub if online.
3. 请执行：Use Local path when offline.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q183
**Question:** 什么会触发强制更新？
**Answer:** 低于最低支持版本/构建，或带更新的远程 force 标志。Hub 的 `version.json` 驱动各产品线；不要编造版本号。
**Step by step solution:**
1. 请执行：Allow update dialog.
2. 请执行：Download from official hub/site.
3. 请执行：Reinstall Setup if portable is stale.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q184
**Question:** 什么是 PAS Generator？
**Answer:** 独立的管理员工具（`cmd/pas-generator`）用于 PAS 流程。非客户主路径；客户走 foxnext.net + Registration。
**Step by step solution:**
1. 请执行：Operators only.
2. 请执行：Do not ask customers to run PAS Generator unless support instructs.
3. 请执行：Customers use Activate / claim codes.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q185
**Question:** 什么是 Config Builder？
**Answer:** `version.json` → `config_builder` 的独立 APK。相关产品，源码不在本 Windows 仓库；勿与主 Android VPN 混淆。
**Step by step solution:**
1. 请执行：Download from official hub/site if offered.
2. 请执行：Do not expect Installer tabs inside Config Builder.
3. 请执行：Support Installer vs Config Builder separately.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q186
**Question:** Basic 免费 Central 国家有哪些？
**Answer:** 无 Pro 时 Central 免费国家：伊朗、中国、俄罗斯（`IsFreeCentralCountry`）。其他国家通常需要 Pro。
**Step by step solution:**
1. 请执行：Basic mode.
2. 请执行：Pick IR/CN/RU for free central path.
3. 请执行：Activate Pro if another country is required.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q187
**Question:** Pro License 能打开 AI 聊天吗？
**Answer:** 不能——AI 聊天需要单独的 AI Pro 解锁与 quota。Pro 只解锁 Pro 仪表盘。
**Step by step solution:**
1. 请执行：Activate AI Assistant Pro.
2. 请执行：Select AI Pro on View.
3. 请执行：Confirm quota.
4. 请执行：Chat/tasks.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q188
**Question:** 有哪些代码前缀？
**Answer:** BFXB Basic、BFXP Pro、BFXA AI Pro、BFXQ 配额、BFXT 测试；claim 含 `-CLM-`。前缀错误 → 解锁错误或失败。
**Step by step solution:**
1. 请执行：Copy full code.
2. 请执行：Paste Activate.
3. 请执行：If claim code, ensure unused TX.
4. 请执行：Use Reactivation if rebound needed.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q189
**Question:** Registration 上的 My Code 是什么？
**Answer:** 成功解锁后显示已存激活码；便于工单，但仍须当密钥保护。
**Step by step solution:**
1. 请执行：Activate successfully.
2. 请执行：Open My Code.
3. 请执行：Share with support only when asked.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q190
**Question:** 什么是 System ID / Device ID？
**Answer:** 用于绑定 License 的机器指纹；网站 Activation 与 Reactivation 需要。更换硬件可能破坏绑定。
**Step by step solution:**
1. 请执行：Registration tab.
2. 复制 Device ID。
3. 请执行：Use on foxnext.net Activation.
4. 请执行：Keep for support.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q191
**Question:** 未指定月数时默认 License 时长？
**Answer:** 未指定月数时许可逻辑常见 18 个月；实时目录为 12–30 个月并含多设备折扣。以页面显示时长为准。
**Step by step solution:**
1. 请执行：Read purchase page months.
2. 请执行：Pay matching amount.
3. 请执行：Activate with issued code.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q192
**Question:** 应用使用哪些 Hub？
**Answer:** 主 Hub `blackfoxupdate.ir`，备 `foxnext.net`，用于 version、runtime-config、license-access、AI 与包；主用被拦时故障转移。
**Step by step solution:**
1. 请执行：Keep internet.
2. 请执行：If updates fail, try Proxy.
3. 请执行：Confirm official site for downloads.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q193
**Question:** 产品配置中的支持联系方式？
**Answer:** 含 runtime contact 中的 `@HiBlackFoxVpn`、`@BlackFoxVpnn`、`@BlackFoxVpn_bot`、`@Black_Fox_Group`。优先看 Contact 实时列表。
**Step by step solution:**
1. 请执行：Open Contact tab.
2. 请执行：Use listed Telegram/email.
3. 请执行：Include Device ID in tickets.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q194
**Question:** 公开 GitHub 拼写是故意的吗？
**Answer:** Hub 可能显示 `github.com/balckfoxgroup/blackfox-vpn-installer`——若 Contact 链接如此，请使用已发布拼写，勿擅自“纠正”。
**Step by step solution:**
1. 请执行：Open Contact → GitHub.
2. 请执行：Follow the in-app URL.
3. 请执行：Don’t invent alternate orgs.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q195
**Question:** Full Deploy 用 Android 还是 Windows？
**Answer:** Full Deploy 与 Mesh 请用 Windows Installer；Android 为配套，主要部署工作站通常仍是 Windows。
**Step by step solution:**
1. 请执行：Deploy from Windows.
2. 请执行：Use Android for mobile monitoring/AI where available.
3. 请执行：Import WG client configs on any OS WireGuard app.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q196
**Question:** 两个 Portable 副本能安全共享同一套库存吗？
**Answer:** 有风险——优先单一 Portable 文件夹或 Setup+LocalAppData。两个副本可能争用同一库存。
**Step by step solution:**
1. 请执行：Use one working copy.
2. 请执行：Backup portable folder.
3. 请执行：Prefer Setup install for stability.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q197
**Question:** AI 绝不应该编造什么？
**Answer:** 版本号、价格、主机商品牌，以及不在 i18n 中的 Linux stderr。身份：BlackFox AI；缺口标 NEED_MORE_REVIEW。
**Step by step solution:**
1. 请执行：Answer from KB.
2. 请执行：If unknown, say so.
3. 请执行：Ask for screenshot + Device ID.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q198
**Question:** 教学截图在哪里？
**Answer:** `/Screenshots` 目录含 README；并非所有对话框都有实机截图。已有 mode picker、Basic/Pro 仪表盘、Android 与营销图。
**Step by step solution:**
1. 请执行：Pick matching asset from README.
2. 请执行：Do not claim a missing dialog screenshot exists.
3. 请执行：Request user screenshot when needed.
4. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q199
**Question:** 聊天机器人应如何引导卡住的部署？
**Answer:** 顺序：Proxy → Connect SSH → Full Deploy 来源 → Panel Login Info → Configure Panel → Diagnostic。不要先跳到 Delete/Reset。分清 Basic 免费项与 License 门控。
**Step by step solution:**
1. 请执行：Verify mode/license.
2. 请执行：Proxy if network fails.
3. 执行 Connect SSH。
4. 执行 Full Deploy。
5. 请执行：Check System / AI Diagnose.
6. 请执行：Support if still blocked.
7. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。

### Q200
**Question:** 唯一的 RAG 入口文件是什么？
**Answer:** 主 RAG 入口：`Documentation/AI_Knowledge_Base.md`，并配合指南、FAQ、Troubleshooting 与 `Screenshots/README`。多语言机器人用 `AI_Knowledge_Base_Multilingual` 与 `AI_BOT_DATABASE`。
**Step by step solution:**
1. 请执行：Load AI_Knowledge_Base.md.
2. 请执行：Retrieve FAQ/Troubleshooting for errors.
3. 请执行：Cite Feature_List for gates.
4. 请执行：Mark NEED_MORE_REVIEW honestly.
5. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。
**Possible errors:** 常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。
