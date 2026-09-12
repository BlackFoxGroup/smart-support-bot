# Smart Support Bot and Manager

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

## Easy Manager installation on Linux

Run this command as a user with `sudo` access:

```bash
curl -fsSL https://raw.githubusercontent.com/BlackFoxGroup/smart-support-bot/main/deploy/install-manager.sh | sudo bash
```

The installer places the project in `/opt/smart-support` and starts `smart-support-manager.service` on `127.0.0.1:8766`.

Open it through an SSH tunnel:

```bash
ssh -L 8766:127.0.0.1:8766 USER@SERVER
```

Then open:

```text
http://127.0.0.1:8766
```

## Installing the bot and Manager from the ZIP

1. Extract the ZIP.
2. Copy `.env.example` to `.env`.
3. Add `TELEGRAM_BOT_TOKEN`, `BOT_ADMIN_IDS`, and the AI settings you want to use.
4. Run the installer:

```bash
sudo bash deploy/install.sh
sudo bash deploy/install-manager.sh
```

If the Telegram token is still a placeholder, the installer prepares the bot service without starting it. After editing `/opt/smart-support/.env`, start the services:

```bash
sudo systemctl enable --now smart-support-bot.service
sudo systemctl enable --now smart-support-bot-watchdog.service
```

Check their status:

```bash
sudo systemctl status smart-support-bot.service --no-pager
sudo systemctl status smart-support-manager.service --no-pager
```

## Windows setup

Open PowerShell in the extracted folder:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env`, then start the bot:

```powershell
py -3 -m src.main
```

Start Manager with:

```text
Start-Smart-Support-Manager-v2.bat
```

Manager opens at `http://127.0.0.1:8766`.

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

## نصب آسان Manager روی لینوکس

این دستور را با کاربری اجرا کنید که به `sudo` دسترسی دارد:

```bash
curl -fsSL https://raw.githubusercontent.com/BlackFoxGroup/smart-support-bot/main/deploy/install-manager.sh | sudo bash
```

نصب‌کننده پروژه را در مسیر `/opt/smart-support` قرار می‌دهد. سرویس Manager روی `127.0.0.1:8766` اجرا می‌شود.

برای بازکردن صفحه Manager یک تونل SSH بسازید:

```bash
ssh -L 8766:127.0.0.1:8766 USER@SERVER
```

سپس این نشانی را باز کنید:

```text
http://127.0.0.1:8766
```

## نصب ربات و Manager از فایل ZIP

۱. فایل ZIP را استخراج کنید.
۲. فایل `.env.example` را با نام `.env` کپی کنید.
۳. مقادیر `TELEGRAM_BOT_TOKEN` و `BOT_ADMIN_IDS` و تنظیمات دلخواه AI را وارد کنید.
۴. دستورهای زیر را اجرا کنید:

```bash
sudo bash deploy/install.sh
sudo bash deploy/install-manager.sh
```

اگر توکن تلگرام هنوز نمونه باشد، نصب‌کننده سرویس ربات را آماده می‌کند ولی آن را روشن نمی‌کند. پس از ویرایش فایل `/opt/smart-support/.env` سرویس‌ها را اجرا کنید:

```bash
sudo systemctl enable --now smart-support-bot.service
sudo systemctl enable --now smart-support-bot-watchdog.service
```

برای بررسی وضعیت:

```bash
sudo systemctl status smart-support-bot.service --no-pager
sudo systemctl status smart-support-manager.service --no-pager
```

## نصب روی ویندوز

پنجره PowerShell را در پوشه استخراج‌شده باز کنید:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

فایل `.env` را تکمیل کنید و ربات را اجرا کنید:

```powershell
py -3 -m src.main
```

برای اجرای Manager روی فایل زیر دوبار کلیک کنید:

```text
Start-Smart-Support-Manager-v2.bat
```

صفحه Manager در `http://127.0.0.1:8766` باز می‌شود.

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
