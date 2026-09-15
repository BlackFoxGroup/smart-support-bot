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
