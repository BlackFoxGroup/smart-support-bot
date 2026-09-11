<p align="center">
  <img src="docs/assets/logo.png" alt="VPS to VPN — Black Fox Group" width="96">
</p>

<h1 align="center">Smart Support Bot</h1>

<p align="center">
  <strong>Telegram product support for VPS to VPN by Black Fox Group</strong><br>
  Features · Languages · Catalog · Setup · Deploy · Safety
</p>

<p align="center">
  <a href="https://foxnext.net">Website</a> •
  <a href="https://foxnext.net/downloads/Black-Fox-Config-Builder.apk">Black-Fox-Config-Builder.apk</a> •
  <a href="https://github.com/balckfoxgroup/blackfox-vpn-installer">VPS to VPN</a> •
  <a href="https://github.com/balckfoxgroup/blackfox-config-builder">Black Fox Config Builder</a> •
  <a href="https://t.me/blackFoxVPNN">Telegram</a>
</p>

<div dir="rtl">

ربات **Smart Support Bot** به‌صورت رایگان و متن‌باز (**Open Source**) در اختیار عموم قرار گرفته است تا همه بتوانند آزادانه از آن استفاده کنند و در توسعه و بهبود آن مشارکت داشته باشند.

⭐ اگر این پروژه برای شما مفید است، لطفاً با **Star ⭐ در GitHub** از ادامه این مسیر و توسعه پروژه حمایت کنید. حمایت شما انگیزه‌ای برای ادامه و ساخت پروژه‌های بهتر است.

🦊 همچنین خوشحالیم که به خانواده **Black Fox** پیوسته‌اید. 💖
امیدواریم در کنار هم بتوانیم پروژه‌های کاربردی و متن‌باز بیشتری توسعه دهیم.

🚀 در کنار Smart Support Bot، می‌توانید از سایر پروژه‌های **Black Fox** نیز دیدن کنید و از آن‌ها استفاده کنید.

**از همراهی و حمایت شما سپاسگزاریم. 🙏**

</div>

---

## Overview / معرفی

Async Telegram support bot for **VPS to VPN** by **Black Fox Group** (Server Installer & Manager) (ops toolkit).  
Long polling · **aiogram 3** · OpenAI-compatible chat API · local multilingual knowledge.

Not an image/video/codegen bot.

> Clean open-source release: no recorded user data, no secrets in the repo.  
> Only the **Contact Creator** card (`knowledge/creator_contact.json`) ships pre-filled.

**Download ZIP:** [foxnext.net/downloads/smart-support-bot.zip](https://foxnext.net/downloads/smart-support-bot.zip)  
Archive root folder: `Smart Support Bot/`

<div dir="rtl">

ربات پشتیبانی تلگرام برای برنامه **VPS to VPN** از **Black Fox Group** (Server Installer & Manager) — اجرا به‌صورت async با **aiogram 3**، Long Polling، API سازگار با OpenAI و پایگاه دانش چندزبانهٔ محلی.

ربات تولید تصویر/ویدیو/کد عمومی نیست؛ تمرکز روی پشتیبانی محصول است.

> نسخهٔ متن‌باز تمیز است: دادهٔ کاربر و رمز در مخزن نیست.  
> فقط کارت **تماس با سازنده** (`knowledge/creator_contact.json`) از پیش پر شده است.

**دانلود ZIP:** [foxnext.net/downloads/smart-support-bot.zip](https://foxnext.net/downloads/smart-support-bot.zip)  
پوشهٔ ریشه داخل آرشیو: `Smart Support Bot/`

</div>

## Features / امکانات

- Languages: `fa`, `en`, `ru`, `zh` (Telegram `language_code` + `/lang`)
- Intent match from `AI_BOT_DATABASE` (keyword / sample overlap)
- Low confidence → clarifying question; high confidence → LLM with FAQ + KB snippets
- **Ask AI** scoped per product (catalog training + RAG; no internal prompt dumps to chat)
- Per-product catalogs, admin training hub (append-only), product-scoped operator chat
- Media send only when the user explicitly asks
- Sales nudge (FOMO, no fake prices) → https://foxnext.net · @HiBlackFoxVpn
- User language prefs in `data/users.json` (created on first run)
- Social news job (verified sources → captioned posts)
- Optional nightly free-config / conversation-analysis jobs
- **Safe-change watchdog**: backup → apply → observe → admin confirm → keep or auto-restore  
  (`/safety_drill`, `/safety_status`; `smart-support-bot-watchdog.service`)

<div dir="rtl">

- زبان‌ها: `fa`، `en`، `ru`، `zh` (بر اساس `language_code` تلگرام و دستور `/lang`)
- تشخیص نیت از `AI_BOT_DATABASE`
- اطمینان پایین → سؤال شفاف‌سازی؛ اطمینان بالا → پاسخ LLM با FAQ و قطعات دانش
- **سوال از AI** محدود به هر محصول (آموزش کاتالوگ + RAG؛ بدون نشت پرامپت داخلی به چت)
- کاتالوگ محصول، هاب آموزش ادمین (افزودن متن / append)، گفتگوی اپراتور به‌ازای محصول
- ارسال عکس فقط وقتی کاربر صریح درخواست کند
- پیام فروش بدون قیمت جعلی → سایت و @HiBlackFoxVpn
- ذخیرهٔ زبان کاربر در `data/users.json`
- ارسال خبرهای تأییدشدهٔ اینترنت
- جاب‌های اختیاری: کانفیگ شبانه و تحلیل گفتگو
- **نگهبان تغییر امن**: پشتیبان → اعمال → مشاهده → تأیید ادمین → نگه داشتن یا بازگردانی خودکار

</div>

## Layout / ساختار

VPS install path: `/opt/Smart Support Bot`  
Safety store (outside install tree): `/opt/smart-support-bot-safety`

```
Smart Support Bot/
├── src/
│   ├── main.py
│   ├── config.py
│   ├── ai/                 # client, persona, safety
│   ├── handlers/           # start, chat, menu, admin, group, safety
│   ├── knowledge/          # loader, intents, catalogs, RAG, Ask AI memory
│   ├── safety/             # watchdog, backup, paths
│   ├── control/            # agent registry & API keys
│   ├── ui/                 # keyboards & messaging
│   └── storage/            # users & runtime state helpers
├── knowledge/
│   ├── AI_Knowledge_Base_Multilingual/
│   ├── AI_BOT_DATABASE/
│   ├── Support_Decision_Tree/
│   ├── creator_contact.json
│   ├── social_news_sources.json
│   ├── product_catalogs/
│   └── product_guides/
├── data/.gitkeep
├── media/
├── docs/assets/logo.png
├── deploy/
│   ├── install.sh
│   ├── smart-support-bot.service
│   └── smart-support-bot-watchdog.service
├── src/manager/            # Smart Support Manager (local UI)
├── Start-Smart-Support-Manager.bat
├── requirements.txt
├── .env.example
└── README.md
```

<div dir="rtl">

مسیر نصب روی VPS: `/opt/Smart Support Bot`  
مسیر safety (خارج از پوشهٔ نصب): `/opt/smart-support-bot-safety`

</div>

## Setup / راه‌اندازی

### Windows (PowerShell)

```powershell
cd "Smart Support Bot"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env: TELEGRAM_BOT_TOKEN, AI_API_KEY, BOT_ADMIN_IDS
python -m src.main
```

### Linux / VPS

```bash
cd "/opt/Smart Support Bot"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env
python -m src.main
```

> **`BOT_ADMIN_IDS` is required** for admin / Statistics menus.  
> Find your numeric Telegram id via `@userinfobot`.

<div dir="rtl">

> برای منوی ادمین و آمار، تنظیم **`BOT_ADMIN_IDS`** لازم است.  
> شناسهٔ عددی تلگرام را از ربات‌هایی مثل `@userinfobot` بگیرید.

</div>

## Environment / متغیرهای محیطی

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `TELEGRAM_BOT_TOKEN` | yes | — | from @BotFather |
| `AI_API_KEY` | yes | — | OpenAI-compatible key |
| `AI_BASE_URL` | no | `https://ai.nube.sh/api/v1` | |
| `AI_MODEL` | no | `kimi-k2.5` | |
| `AI_TIMEOUT_SECONDS` | no | `60` | |
| `AI_MAX_TOKENS` | no | `4096` | |
| `AI_TEMPERATURE` | no | `0.4` | |
| `INTENT_CONFIDENCE_THRESHOLD` | no | `0.28` | |
| `KNOWLEDGE_SNIPPET_CHARS` | no | `12000` | |
| `LOG_LEVEL` | no | `INFO` | |
| `BOT_ADMIN_IDS` | recommended | — | comma-separated numeric ids |
| `AI_BUDGET_USD` | no | `50` | |
| `AI_USD_PER_MILLION_TOKENS` | no | `2.0` | |
| `NIGHTLY_ENABLED` | no | `false` | free config to channel |
| `NIGHTLY_IRAN_TIME` | no | `21:00` | |
| `NIGHTLY_SUPPORT_CHAT_ID` | no | `@HiBlackFoxVpn` | |
| `PANEL_BASE_URL` | when nightly on | — | 3x-ui panel |
| `PANEL_API_TOKEN` | when nightly on | — | |
| `PANEL_INBOUND_ID` | when nightly on | `1` | |
| `PANEL_REQUIRED_PORT` | no | `443` | |
| `SOCIAL_NEWS_ENABLED` | no | `true` | |
| `SOCIAL_NEWS_CHAT_ID` | no | `@HiBlackFoxVPN` | |
| `SOCIAL_NEWS_TIMES` | no | `10:00,17:00` | |
| `CONVO_ANALYSIS_ENABLED` | no | `false` | |
| `CONVO_ANALYSIS_TIMES` | no | `12:30` | |
| `CONVO_ANALYSIS_CHAT_ID` | when convo on | — | numeric id |
| `CONVO_ANALYSIS_TEST_MODE` | no | `true` | |
| `SAFETY_CONFIRM_CHAT_ID` | for safety drills | — | numeric id |
| `NEWS_REPORT_ADMIN_IDS` | no | — | extra Stats → Report ids |

Full template: `.env.example`

<div dir="rtl">

جدول بالا همهٔ متغیرهای مهم را نشان می‌دهد. الگوی کامل در `.env.example` است.  
کلیدها و توکن‌ها را هرگز در Git commit نکنید.

</div>

## systemd / استقرار سرویس

```bash
sudo cp "/opt/Smart Support Bot/deploy/smart-support-bot.service" /etc/systemd/system/
sudo cp "/opt/Smart Support Bot/deploy/smart-support-bot-watchdog.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now smart-support-bot
sudo systemctl enable --now smart-support-bot-watchdog
```

Or:

```bash
sudo bash "/opt/Smart Support Bot/deploy/install.sh"
```

<div dir="rtl">

واحدهای systemd مسیر کاری را روی `/opt/Smart Support Bot` تنظیم می‌کنند.  
می‌توانید از `deploy/install.sh` برای نصب یک‌مرحله‌ای استفاده کنید.

</div>

## Commands / دستورات

| Command | Description |
|---------|-------------|
| `/start` | Greeting / شروع |
| `/help` | Short help / راهنمای کوتاه |
| `/lang fa\|en\|ru\|zh` | Persist language / ذخیره زبان |
| `/safety_drill` | Admin: run safe-change drill |
| `/safety_status` | Admin: watchdog status |

<div dir="rtl">

دستورات `/safety_*` فقط برای ادمین (شناسه‌های `BOT_ADMIN_IDS`) فعال‌اند.

</div>

## Ask AI & Catalog / سوال از AI و کاتالوگ

- Admin can store **catalog training text** per product (hub shows status only; Edit shows full text; new text is appended).
- User **Ask AI** answers from that product’s training + catalog RAG.
- Failures fall back to a short teaching excerpt — not the full internal prompt.
- Photos are sent only on explicit request (e.g. «عکسش را بفرست»).

<div dir="rtl">

- ادمین می‌تواند **متن آموزشی کاتالوگ** را برای هر محصول ذخیره کند (هاب فقط وضعیت؛ ویرایش متن کامل؛ متن جدید به ادامه اضافه می‌شود).
- **سوال از AI** کاربر از آموزش همان محصول و RAG کاتالوگ پاسخ می‌دهد.
- در خطا، خلاصهٔ کوتاه آموزشی برمی‌گردد — نه کل پرامپت داخلی.
- عکس فقط با درخواست صریح کاربر ارسال می‌شود.

</div>

## Safety / product rules / قوانین ایمنی

- No invented versions or prices
- VPS only via FoxNext Partners on foxnext.net
- License sales: scarcity framing without fake numbers; link site + @HiBlackFoxVpn
- Never commit `.env`, runtime `data/*.json`, or Telegram sessions

<div dir="rtl">

- نسخه یا قیمت جعلی نسازید
- VPS فقط از طریق شرکای FoxNext در foxnext.net
- فروش لایسنس بدون عدد ساختگی؛ لینک سایت و @HiBlackFoxVpn
- هرگز `.env`، فایل‌های runtime در `data/` یا session تلگرام را commit نکنید

</div>

## Recent changes / تغییرات اخیر

- Live product catalog from the desktop app source (scan → validate → version → activate). Previous ACTIVE catalog stays if upload fails.
- Catalog AI can be turned OFF per product in Telegram Settings; RAG and catalog images are skipped, data is kept.
- Incremental media: hash, duplicate skip, queue with retry of one file, LOCAL DELETED does not auto-delete the server file.
- **Smart Support Manager** desktop UI for catalog, media, SFTP settings, and upload queue.

<div dir="rtl">

- کاتالوگ زنده از سورس برنامه دسکتاپ (اسکن تا فعال‌سازی). اگر آپلود شکست بخورد نسخهٔ ACTIVE قبلی می‌ماند.
- کاتالوگ AI را می‌توان برای هر محصول خاموش کرد؛ داده پاک نمی‌شود.
- رسانهٔ افزایشی: اثرانگشت، جلوگیری از تکراری، صف با Retry تک‌فایل. حذف محلی فایل سرور را خودکار پاک نمی‌کند.
- برنامهٔ **Smart Support Manager** برای کاتالوگ، عکس، تنظیم SFTP و صف آپلود.

</div>

## Smart Support Manager / اسکریپت مدیر

Windows: double-click `Start-Smart-Support-Manager.bat` in the project root. It starts the local server and opens `http://127.0.0.1:8765`.

First screen: choose **فارسی / English / Русский / 中文**.  
Dashboard shows a short usage guide. Product actions (Scan, Auto-map, Build catalog, Queue, Rollback) sit in one row.

```powershell
py -3 -m src.manager
```

Needs `py -3` (Python 3). Secrets stay in `.env` / Manager Settings — never in Git.

<div dir="rtl">

در ویندوز روی `Start-Smart-Support-Manager.bat` در ریشهٔ پروژه دوبار کلیک کنید. سرور محلی بالا می‌آید و مرورگر باز می‌شود.

ابتدا زبان را انتخاب کنید. داشبورد راهنمای کوتاه دارد. دکمه‌های محصول در یک ردیف‌اند.

رمزها فقط در `.env` یا تنظیمات Manager؛ در گیت‌هاب نیستند.

</div>

## License & credit / مجوز و اعتبار

Released free and open source. If it helps you, ⭐ the repo.  
🦊 Built by **Black Fox** — https://foxnext.net · @HiBlackFoxVpn

<div dir="rtl">

منتشرشده به‌صورت رایگان و متن‌باز. اگر مفید بود، به مخزن ⭐ بدهید.  
🦊 ساختهٔ **Black Fox** — https://foxnext.net · @HiBlackFoxVpn

</div>
