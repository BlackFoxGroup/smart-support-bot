<p align="center">
  <img src="1.png" alt="Black Fox Group Logo" width="96">
</p>

<h1 align="center"> Smart Support Bot and Manager</h1>

<p align="center">
  Features · Languages · Catalog · Setup · Deploy · Safety
</p>

<p align="center">
  <a href="https://foxnext.net">Website</a> •
  <a href="https://github.com/BlackFoxGroup/VPS to VPN">VPS to VPN</a> •
  <a href="https://github.com/BlackFoxGroup/blackfox-config-builder">Black Fox Config Builder</a> •
  <a href="https://t.me/blackFoxVPNN">Telegram</a>
</p>

<div dir="rtl">

  ربات و اکسپرت مدیریت **Smart Support Bot and Manager** به‌صورت رایگان و متن‌باز (**Open Source**) در اختیار عموم قرار گرفته است تا همه بتوانند آزادانه از آن استفاده کنند و در توسعه و بهبود آن مشارکت داشته باشند.

⭐ اگر این پروژه برای شما مفید است، لطفاً با **Star ⭐ در GitHub** از ادامه این مسیر و توسعه پروژه حمایت کنید. حمایت شما انگیزه‌ای برای ادامه و ساخت پروژه‌های بهتر است.

🦊 همچنین خوشحالیم که به خانواده **Black Fox** پیوسته‌اید. 💖
امیدواریم در کنار هم بتوانیم پروژه‌های کاربردی و متن‌باز بیشتری توسعه دهیم.

🚀 در کنار Smart Support Bot، می‌توانید از سایر پروژه‌های **Black Fox** نیز دیدن کنید و از آن‌ها استفاده کنید.

**از همراهی و حمایت شما سپاسگزاریم. 🙏**



</div>


Smart Support Bot is a Telegram support bot that answers product questions from an active catalog. Smart Support Manager 2.1 is the companion interface for creating, editing, publishing, and managing those catalogs with an OpenAI-compatible service.

Both programs use the same product directory on the server:

```text
/opt/smart-support/products/<product-id>/
├── catalog.json
└── media/
```

Website: [foxnext.net](https://foxnext.net)
Source: [github.com/BlackFoxGroup/smart-support-bot](https://github.com/BlackFoxGroup/smart-support-bot)

## Download

Download the public package:

[smart-support-suite-v2.1.zip](https://github.com/BlackFoxGroup/smart-support-bot/raw/main/downloads/smart-support-suite-v2.1.zip)

The package contains the raw source for the bot and Manager. It does not contain passwords, tokens, API keys, server addresses, usernames, user data, or Telegram session files.

## Requirements

- Python 3.11 or newer
- Windows 10/11 for the desktop launcher, or Ubuntu/Debian for server installation
- A Telegram bot token from `@BotFather`
- An OpenAI-compatible API endpoint and key when AI features are needed

## One-command setup (recommended)

Open PowerShell on Windows and run:

```powershell
irm https://raw.githubusercontent.com/BlackFoxGroup/smart-support-bot/main/deploy/install-suite.ps1 | iex
```

The installer asks for the Linux server login and Telegram token. It then:

1. saves a local Expert copy in `%LOCALAPPDATA%\SmartSupport`;
2. installs the bot and Expert together in `/opt/smart-support` on the server;
3. activates and verifies both services;
4. opens the local Expert in the browser.

Python 3.11 or newer must be installed on Windows. No other terminal command is required.
The local Expert runs without a console window and stops after its last browser page is closed.

## Installing the bot and Manager from the ZIP

1. Extract the ZIP.
2. Install Python 3.11 or newer on Windows.
3. Double-click `Start-Smart-Support-Manager-v2.bat`. The first run installs the required Python packages.
4. Open the Install bot page.
5. Select the local bot and Expert folder, then enter the server login and Telegram token.
6. Choose `Polling` for a simple installation, or `Webhook` when a public HTTPS reverse proxy is already configured.
7. Click Install bot, then Install Expert.
8. Click Activate bot and Expert.

The bot and Expert are stored together in `/opt/smart-support`. After the success message, open the bot in Telegram and send `/start`.

## Windows setup

Start Manager by double-clicking:

```text
Start-Smart-Support-Manager-v2.bat
```

Manager opens at `http://127.0.0.1:8766`. No terminal command is required after Python is installed.

## Catalog workflow

Manager is the main place for catalog work:

1. Add or select a product.
2. Connect Manager to the server and AI in Settings.
3. Build catalog text automatically from the product source.
4. Review and save the text.
5. Scan and map product images.
6. Send selected images directly to the catalog.
7. Activate the catalog.

After activation, the bot reads the same catalog and uses it when answering questions about that product. Catalogs can also be edited from the bot, but Manager has the complete editing workflow.

## Manager pages

- Dashboard: connection state and product summary
- Products: product source and fixed server storage path
- Automatic catalog: build, save, map, send images, activate, and roll back
- Catalog: edit titles, summaries, and features
- Catalog photos: change image features, return images to Media, or delete them
- Media: review server images and send them to a catalog
- Upload queue: upload files to the server with retry and removal controls
- Settings: server, Manager AI, bot AI, Expert connection, and Stop all
- Install bot: install a Telegram bot project on a Linux server

Clicking an image in Media, Catalog photos, or Upload queue opens it on the same page. Close it with `Esc`, the close button, or a click outside the image.

## Configuration

Use `.env.example` as the template. Important variables:

```dotenv
TELEGRAM_BOT_TOKEN=replace-with-botfather-token
BOT_ADMIN_IDS=replace-with-your-telegram-user-id
AI_BASE_URL=https://your-ai-provider.example/v1
AI_API_KEY=replace-with-your-api-key
AI_MODEL=replace-with-your-model
```

Manager stores settings locally after Save. New values replace old values. Keep `.env`, Manager settings, runtime JSON files, and Telegram sessions out of Git.

## Security

- Never publish `.env`.
- Never add `data/`, saved Manager credentials, or Telegram `.session` files to a release.
- Review a public archive before upload.
- Replace a token immediately if it was ever committed or shared.

## License and credit

Smart Support Bot and Manager are maintained by Black Fox Group.

---

# ربات و مدیر پشتیبانی هوشمند

ربات `Smart Support Bot` با استفاده از کاتالوگ فعال به پرسش‌های کاربران درباره محصول پاسخ می‌دهد. برنامه `Smart Support Manager 2.1` محیط ساخت، ویرایش و انتشار کاتالوگ است و می‌تواند برای این کار از سرویس‌های سازگار با OpenAI استفاده کند.

ربات و Manager از یک مسیر مشترک روی سرور استفاده می‌کنند:

```text
/opt/smart-support/products/<product-id>/
├── catalog.json
└── media/
```

وب‌سایت: [foxnext.net](https://foxnext.net)
سورس پروژه: [github.com/BlackFoxGroup/smart-support-bot](https://github.com/BlackFoxGroup/smart-support-bot)

## دانلود

بسته عمومی را از اینجا دریافت کنید:

[smart-support-suite-v2.1.zip](https://github.com/BlackFoxGroup/smart-support-bot/raw/main/downloads/smart-support-suite-v2.1.zip)

این بسته شامل سورس خام ربات و Manager است. هیچ رمز، توکن، کلید API، نشانی سرور، نام کاربری، اطلاعات کاربران یا فایل نشست تلگرام داخل آن قرار ندارد.

## پیش‌نیازها

- پایتون نسخه ۳.۱۱ یا جدیدتر
- ویندوز ۱۰ یا ۱۱ برای اجرای محلی، یا اوبونتو و دبیان برای نصب روی سرور
- توکن ربات تلگرام از `@BotFather`
- آدرس و کلید سرویس سازگار با OpenAI برای قابلیت‌های هوش مصنوعی

## نصب کامل با یک دستور

پنجره PowerShell را در ویندوز باز کنید و این دستور را اجرا کنید:

```powershell
irm https://raw.githubusercontent.com/BlackFoxGroup/smart-support-bot/main/deploy/install-suite.ps1 | iex
```

نصب‌کننده اطلاعات ورود سرور لینوکس و توکن تلگرام را می‌پرسد. سپس این کارها را خودکار انجام می‌دهد:

۱. یک نسخه محلی Expert را در `%LOCALAPPDATA%\SmartSupport` ذخیره می‌کند.
۲. ربات و Expert را در مسیر `/opt/smart-support` روی سرور نصب می‌کند.
۳. هر دو سرویس را فعال و بررسی می‌کند.
۴. Expert محلی را در مرورگر باز می‌کند.

پایتون نسخه ۳.۱۱ یا جدیدتر باید روی ویندوز نصب باشد. دستور دیگری لازم نیست.
برنامه Expert بدون پنجره ترمینال اجرا می‌شود و پس از بسته‌شدن آخرین صفحه مرورگر آن متوقف می‌شود.

## نصب ربات و Manager از فایل ZIP

۱. فایل ZIP را استخراج کنید.
۲. پایتون نسخه ۳.۱۱ یا جدیدتر را روی ویندوز نصب کنید.
۳. روی `Start-Smart-Support-Manager-v2.bat` دوبار کلیک کنید. برنامه در اولین اجرا بسته‌های لازم را نصب می‌کند.
۴. صفحه نصب ربات را باز کنید.
۵. مسیر پوشه محلی ربات و Expert را انتخاب کنید و اطلاعات ورود سرور و توکن تلگرام را وارد کنید.
۶. برای نصب ساده `Polling` را انتخاب کنید. حالت `Webhook` به دامنه عمومی HTTPS و پراکسی آماده نیاز دارد.
۷. ابتدا «نصب ربات» و بعد «نصب اکسپرت» را بزنید.
۸. کلید «فعال‌سازی ربات و اکسپرت» را بزنید.

ربات و اکسپرت در مسیر مشترک `/opt/smart-support` ذخیره می‌شوند. پس از نمایش پیام موفقیت، ربات را در تلگرام باز کنید و `/start` را بزنید.

## نصب روی ویندوز

برای اجرای Manager روی فایل زیر دوبار کلیک کنید:

```text
Start-Smart-Support-Manager-v2.bat
```

صفحه Manager در `http://127.0.0.1:8766` باز می‌شود. پس از نصب پایتون، نیازی به اجرای دستور ترمینال نیست.

## روند ساخت کاتالوگ

محل اصلی کار با کاتالوگ برنامه Manager است:

۱. محصول را اضافه یا انتخاب کنید.
۲. اتصال سرور و هوش مصنوعی را در تنظیمات برقرار کنید.
۳. متن کاتالوگ را از سورس محصول به‌صورت خودکار بسازید.
۴. متن را بررسی و ذخیره کنید.
۵. تصاویر محصول را اسکن و نگاشت کنید.
۶. تصاویر انتخابی را مستقیم به کاتالوگ بفرستید.
۷. کاتالوگ را فعال کنید.

ربات پس از فعال‌سازی، همان کاتالوگ را می‌خواند و برای پاسخ به پرسش‌های محصول استفاده می‌کند. ساخت و ویرایش کاتالوگ از داخل ربات هم ممکن است، اما امکانات کامل این کار در Manager قرار دارد.

## صفحه‌های Manager

- داشبورد: وضعیت اتصال‌ها و خلاصه محصولات
- محصولات: سورس محصول و مسیر ثابت ذخیره‌سازی روی سرور
- ساخت خودکار کاتالوگ: ساخت، ذخیره، نگاشت، ارسال عکس، فعال‌سازی و بازگشت نسخه
- کاتالوگ: ویرایش عنوان، خلاصه و ویژگی‌ها
- عکس‌های کاتالوگ: تغییر ویژگی، بازگرداندن عکس به رسانه یا حذف
- رسانه: بررسی عکس‌های سرور و ارسال آن‌ها به کاتالوگ
- صف آپلود: آپلود، تلاش دوباره و حذف فایل از صف
- تنظیمات: سرور، هوش مصنوعی Manager و ربات، اتصال Expert و توقف همه
- نصب ربات: نصب پروژه یک ربات تلگرام روی سرور لینوکس

کلیک روی عکس در رسانه، عکس‌های کاتالوگ یا صف آپلود، تصویر را در همان صفحه باز می‌کند. کلید `Esc`، علامت بستن و کلیک بیرون عکس آن را می‌بندند.

## تنظیمات

فایل `.env.example` الگوی تنظیمات است. متغیرهای اصلی:

```dotenv
TELEGRAM_BOT_TOKEN=replace-with-botfather-token
BOT_ADMIN_IDS=replace-with-your-telegram-user-id
AI_BASE_URL=https://your-ai-provider.example/v1
AI_API_KEY=replace-with-your-api-key
AI_MODEL=replace-with-your-model
```

اطلاعات ثبت‌شده در Manager پس از ذخیره روی همان رایانه باقی می‌ماند. اطلاعات جدید جای اطلاعات قبلی را می‌گیرد. فایل `.env`، تنظیمات Manager، فایل‌های اجرایی داخل `data/` و نشست تلگرام را در Git قرار ندهید.

## نکات امنیتی

- فایل `.env` را منتشر نکنید.
- پوشه `data/`، اطلاعات ذخیره‌شده Manager و فایل‌های `.session` را داخل نسخه عمومی نگذارید.
- فایل ZIP را پیش از انتشار بررسی کنید.
- توکنی را که قبلاً ثبت یا منتشر شده است فوراً عوض کنید.

## سازنده

توسعه و نگهداری پروژه برعهده Black Fox Group است.
