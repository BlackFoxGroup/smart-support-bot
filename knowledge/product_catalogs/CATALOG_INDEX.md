# Catalog media index

This file is the source of truth for catalog files.
The Telegram bot can send these files with sendPhoto.
If a file is listed here, it exists. Never say the catalog has no photo.
Do not invent files that are not listed.
When the user asks to see or send a photo, the bot attaches the file;
the AI only describes it and must not claim it cannot send files.

## agent-bot — Smart Support Bot
photo_count: 9
folder: products/agent-bot/media/
- file: products/agent-bot/media/00-product-logo.png
  slot: product-logo
  topics: logo, brand, smart support bot, agent-bot
  note: لوگوی Smart Support Bot. وقتی لوگو یا ظاهر محصول را خواستند همین را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/agent-bot/media/01-manager-dashboard-overview.png
  slot: dashboard
  topics: dashboard, smart support manager, expert, manager
  note: داشبورد Manager — وضعیت Draft/In use و میانبر Catalog/Products.
  access: Telegram sendPhoto from this path on the bot server
- file: products/agent-bot/media/02-contact-suite-versions.png
  slot: contact
  topics: contact, version, smart support manager, expert
  note: صفحه Contact با نسخه Manager و Bot.
  access: Telegram sendPhoto from this path on the bot server
- file: products/agent-bot/media/03-catalog-editor.png
  slot: catalog-editor
  topics: catalog editor, howto, smart support manager
  note: ویرایشگر کاتالوگ و Use catalog in bot.
  access: Telegram sendPhoto from this path on the bot server
- file: products/agent-bot/media/04-products-mapping.png
  slot: products
  topics: products, paths, smart support manager
  note: صفحه Products با مسیر عکس و سرور.
  access: Telegram sendPhoto from this path on the bot server
- file: products/agent-bot/media/05-catalog-photos.png
  slot: catalog-photos
  topics: catalog photos, feature tags, smart support manager
  note: لیست عکس کاتالوگ با برچسب feature برای Ask AI.
  access: Telegram sendPhoto from this path on the bot server
- file: products/agent-bot/media/06-media-gallery.png
  slot: media
  topics: media gallery, send to catalog, smart support manager
  note: گالری Media: انتخاب عکس و Send to catalog.
  access: Telegram sendPhoto from this path on the bot server
- file: products/agent-bot/media/07-upload-queue.png
  slot: upload_queue
  topics: upload queue, batch, smart support manager
  note: صف آپلود برای پردازش دسته‌ای عکس.
  access: Telegram sendPhoto from this path on the bot server
- file: products/agent-bot/media/08-install-bot-and-expert.png
  slot: install_bot_expert
  topics: install, expert, bot, activate, smart support manager
  note: نصب ربات و Expert در سه مرحله.
  access: Telegram sendPhoto from this path on the bot server

## vpn-installer — VPS to VPN — Black Fox Group
photo_count: 49
folder: products/vpn-installer/media/
- file: products/vpn-installer/media/01-product-logo.jpg
  slot: product-logo
  topics: product logo, vps to vpn, vpn installer
  note: لوگوی VPS to VPN. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/02-brand-logo.jpg
  slot: brand-logo
  topics: brand logo, vps to vpn, vpn installer
  note: لوگوی Black Fox Group. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/03-app-icon.png
  slot: app-icon
  topics: app icon, vps to vpn, vpn installer
  note: آیکون برنامه VPS to VPN. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/04-basic-mode.png
  slot: basic-mode
  topics: basic mode, vps to vpn, vpn installer
  note: مد Basic ویندوز. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/05-basic-mode-android.jpg
  slot: basic-mode-android
  topics: basic mode android, vps to vpn, vpn installer
  note: مد Basic اندروید. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/06-pro-mode.png
  slot: pro-mode
  topics: pro mode, vps to vpn, vpn installer
  note: مد Pro ویندوز. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/07-ai-pro-mode.png
  slot: ai-pro-mode
  topics: ai pro mode, vps to vpn, vpn installer
  note: مد AI Pro ویندوز. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/08-ai-pro-mode-android.jpg
  slot: ai-pro-mode-android
  topics: ai pro mode android, vps to vpn, vpn installer
  note: مد AI Pro اندروید. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/09-registration.png
  slot: registration
  topics: registration, vps to vpn, vpn installer
  note: ثبت لایسنس ویندوز. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/10-registration-android.jpg
  slot: registration-android
  topics: registration android, vps to vpn, vpn installer
  note: ثبت لایسنس اندروید. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/11-central-setup.png
  slot: central-setup
  topics: central setup, vps to vpn, vpn installer, سرور مرکزی, central server
  note: راه‌اندازی سرور مرکزی. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/12-full-deploy.png
  slot: full-deploy
  topics: full deploy, vps to vpn, vpn installer, دیپلوی کامل, fulldeploy
  note: دیپلوی کامل. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/13-add-exit.png
  slot: add-exit
  topics: add exit, vps to vpn, vpn installer, exit server, exit servers, سرور خروجی, خروجی, ثبت خروج
  note: اسکرین Add Exit / سرور خروجی. وقتی کاربر درباره ثبت Exit، سرور خروجی، Add Exit پرسید یا گفت عکس بفرست، همین فایل را بفرست. حداکثر ۶ Exit؛ نیاز به لایسنس مد کاری.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/14-add-node.png
  slot: add-node
  topics: add node, vps to vpn, vpn installer, نود, node server
  note: افزودن Node Server. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/15-add-tunnel.png
  slot: add-tunnel
  topics: add tunnel, vps to vpn, vpn installer, تونل, tunnel server
  note: افزودن Tunnel Server. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/16-mesh-servers.png
  slot: mesh-servers
  topics: mesh servers, vps to vpn, vpn installer
  note: مش سرورها. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/17-connection-manager.png
  slot: connection-manager
  topics: connection manager, vps to vpn, vpn installer
  note: مدیریت اتصال سرورها. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/18-move-central.png
  slot: move-central
  topics: move central, vps to vpn, vpn installer
  note: جابجایی سرور مرکزی. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/19-move-server.png
  slot: move-server
  topics: move server, vps to vpn, vpn installer
  note: انتقال به سرور جدید. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/20-delete-exit-node.png
  slot: delete-exit-node
  topics: delete exit node, vps to vpn, vpn installer, delete exit, حذف exit, حذف خروجی, delete node
  note: حذف Exit و Node. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/21-reset-servers.png
  slot: reset-servers
  topics: reset servers, vps to vpn, vpn installer
  note: ریست همه سرورها. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/22-check-system.png
  slot: check-system
  topics: check system, vps to vpn, vpn installer
  note: بررسی سیستم ویندوز. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/23-check-system-android.jpg
  slot: check-system-android
  topics: check system android, vps to vpn, vpn installer
  note: بررسی سیستم اندروید. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/24-panel-inbound-proto.png
  slot: panel-inbound-proto
  topics: panel inbound proto, vps to vpn, vpn installer
  note: پروتکل inbound پنل. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/25-panel-inbound-port.png
  slot: panel-inbound-port
  topics: panel inbound port, vps to vpn, vpn installer
  note: پورت inbound پنل. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/26-panel-outbound.png
  slot: panel-outbound
  topics: panel outbound, vps to vpn, vpn installer
  note: outbound سرورها در پنل. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/27-panel-manager.png
  slot: panel-manager
  topics: panel manager, vps to vpn, vpn installer, مدیریت پنل, update panel, backup panel, restore panel, factory reset
  note: اسکرین Panel manager / مدیریت پنل. وقتی کاربر مدیریت پنل، بکاپ پنل، آپدیت پنل یا ریست پنل خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/28-restore-panel.png
  slot: restore-panel
  topics: restore panel, vps to vpn, vpn installer
  note: بازیابی پنل. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/29-factory-reset-panel.png
  slot: factory-reset-panel
  topics: factory reset panel, vps to vpn, vpn installer
  note: ریست کارخانه‌ای پنل. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/30-domain-dns.png
  slot: domain-dns
  topics: domain dns, vps to vpn, vpn installer
  note: دامنه و DNS. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/31-free-domain.png
  slot: free-domain
  topics: free domain, vps to vpn, vpn installer
  note: دامنه رایگان. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/32-cdn-arvan.png
  slot: cdn-arvan
  topics: cdn arvan, vps to vpn, vpn installer
  note: CDN ابرآروان. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/33-cdn-cloudflare.png
  slot: cdn-cloudflare
  topics: cdn cloudflare, vps to vpn, vpn installer
  note: CDN کلودفلر. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/34-cdn-other.png
  slot: cdn-other
  topics: cdn other, vps to vpn, vpn installer
  note: CDN دیگر. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/35-ip-access.png
  slot: ip-access
  topics: ip access, vps to vpn, vpn installer
  note: محدودیت IP. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/36-ip-access-on.png
  slot: ip-access-on
  topics: ip access on, vps to vpn, vpn installer
  note: IP Access روشن. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/37-proxy.png
  slot: proxy
  topics: proxy, vps to vpn, vpn installer
  note: پروکسی. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/38-telegram-bot.png
  slot: telegram-bot
  topics: telegram bot, vps to vpn, vpn installer
  note: افزودن ربات تلگرام. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/39-mirza-bot.png
  slot: mirza-bot
  topics: mirza bot, vps to vpn, vpn installer
  note: میرزا بات. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/40-smart-support.png
  slot: smart-support
  topics: smart support, vps to vpn, vpn installer
  note: Smart Support Bot داخل اپ. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/41-settings.png
  slot: settings
  topics: settings, vps to vpn, vpn installer
  note: تنظیمات ویندوز. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/42-settings-android.jpg
  slot: settings-android
  topics: settings android, vps to vpn, vpn installer
  note: تنظیمات اندروید. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/43-view.png
  slot: view
  topics: view, vps to vpn, vpn installer
  note: نمای وضعیت ویندوز. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/44-view-android.jpg
  slot: view-android
  topics: view android, vps to vpn, vpn installer
  note: نمای وضعیت اندروید. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/45-contact.png
  slot: contact
  topics: contact, vps to vpn, vpn installer
  note: تماس ویندوز. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/46-contact-android.jpg
  slot: contact-android
  topics: contact android, vps to vpn, vpn installer
  note: تماس اندروید. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/47-delete-history.png
  slot: delete-history
  topics: delete history, vps to vpn, vpn installer
  note: حذف تاریخچه محلی. اگر کاربر همین بخش را خواست یا گفت عکس بفرست، همین فایل را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/21-add-exit-servers.png
  slot: add-exit-servers
  topics: add exit servers, exit servers list, سرور خروجی, لیست exit
  note: اسکرین مکمل Add Exit (لیست سرورهای خروجی). همراه add-exit برای سوال ثبت Exit بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/vpn-installer/media/23-delete-exit-node-chooser.png
  slot: delete-exit-node-chooser
  topics: delete exit chooser, حذف exit, حذف node
  note: اسکرین انتخاب Exit/Node قبل از حذف. همراه delete-exit-node بفرست.
  access: Telegram sendPhoto from this path on the bot server

## telegram-bot-expert-installer — Telegram Bot Expert Installer
photo_count: 7
folder: products/telegram-bot-expert-installer/media/
- file: products/telegram-bot-expert-installer/media/01-dashboard.png
  slot: dashboard
  topics: dashboard, telegram bot expert installer, expert installer
  note: اسکرین داشبورد Expert Installer — وقتی کاربر درباره این بخش پرسید همین عکس را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/telegram-bot-expert-installer/media/02-install-bot.png
  slot: install-bot
  topics: install bot, telegram bot expert installer, expert installer
  note: نصب ربات از Expert Installer — وقتی کاربر درباره این بخش پرسید همین عکس را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/telegram-bot-expert-installer/media/03-health-check.png
  slot: health-check
  topics: health check, telegram bot expert installer, expert installer
  note: بررسی سلامت ربات — وقتی کاربر درباره این بخش پرسید همین عکس را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/telegram-bot-expert-installer/media/04-backup.png
  slot: backup
  topics: backup, telegram bot expert installer, expert installer
  note: بکاپ ربات — وقتی کاربر درباره این بخش پرسید همین عکس را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/telegram-bot-expert-installer/media/05-logs.png
  slot: logs
  topics: logs, telegram bot expert installer, expert installer
  note: لاگ‌های ربات — وقتی کاربر درباره این بخش پرسید همین عکس را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/telegram-bot-expert-installer/media/06-uninstall.png
  slot: uninstall
  topics: uninstall, telegram bot expert installer, expert installer
  note: حذف نصب ربات — وقتی کاربر درباره این بخش پرسید همین عکس را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/telegram-bot-expert-installer/media/07-contact.png
  slot: contact
  topics: contact, telegram bot expert installer, expert installer
  note: صفحه تماس و پشتیبانی — وقتی کاربر درباره این بخش پرسید همین عکس را بفرست.
  access: Telegram sendPhoto from this path on the bot server

## config-builder — Config Builder
photo_count: 7
folder: products/config-builder/media/
- file: products/config-builder/media/00-product-logo.png
  slot: product-logo
  topics: logo, brand, config builder, config-builder
  note: لوگوی Config Builder. وقتی لوگو یا ظاهر محصول را خواستند همین را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/config-builder/media/01-connection.jpg
  slot: connection
  topics: connection, connect, panel, 3x-ui, config builder, اتصال, پنل
  note: اتصال به پنل 3X-UI — برای سوال همین بخش همین عکس را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/config-builder/media/02-single.jpg
  slot: single
  topics: single, single create, ساخت تکی, config builder, qr
  note: ساخت تکی کانفیگ — برای سوال همین بخش همین عکس را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/config-builder/media/03-bulk.jpg
  slot: bulk
  topics: bulk, bulk create, ساخت گروهی, config builder
  note: ساخت گروهی کانفیگ — برای سوال همین بخش همین عکس را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/config-builder/media/04-language.jpg
  slot: language
  topics: language, زبان, config builder
  note: انتخاب زبان برنامه — برای سوال همین بخش همین عکس را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/config-builder/media/05-settings.jpg
  slot: settings
  topics: settings, تنظیمات, config builder
  note: تنظیمات Config Builder — برای سوال همین بخش همین عکس را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/config-builder/media/06-contact.jpg
  slot: contact
  topics: contact, support, تماس, config builder
  note: تماس و پشتیبانی Config Builder — برای سوال همین بخش همین عکس را بفرست.
  access: Telegram sendPhoto from this path on the bot server
