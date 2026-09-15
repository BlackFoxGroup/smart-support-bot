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
  topics: logo, brand, agent-bot
  note: لوگوی Smart Support Bot. وقتی لوگو یا ظاهر محصول را خواستند همین را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/agent-bot/media/01-manager-dashboard-overview.png
  slot: dashboard
  topics: dashboard, smart support manager, expert, manager
  note: Manager dashboard: Quick guide and product cards
  access: Telegram sendPhoto from this path on the bot server
- file: products/agent-bot/media/02-contact-suite-versions.png
  slot: contact
  topics: contact, smart support manager, expert, manager
  note: Contact page with Expert and Bot versions
  access: Telegram sendPhoto from this path on the bot server
- file: products/agent-bot/media/03-catalog-editor.png
  slot: catalog-editor
  topics: catalog editor, smart support manager, expert, manager
  note: Catalog text editor and Use catalog in bot
  access: Telegram sendPhoto from this path on the bot server
- file: products/agent-bot/media/04-products-mapping.png
  slot: products
  topics: products, smart support manager, expert, manager
  note: Products page with source and server paths
  access: Telegram sendPhoto from this path on the bot server
- file: products/agent-bot/media/05-catalog-photos.png
  slot: catalog-photos
  topics: catalog photos, smart support manager, expert, manager
  note: Catalog photos list with feature tags for AI
  access: Telegram sendPhoto from this path on the bot server
- file: products/agent-bot/media/06-media-gallery.png
  slot: media
  topics: media, smart support manager, expert, manager
  note: Media gallery: analyze and send photos to catalog
  access: Telegram sendPhoto from this path on the bot server
- file: products/agent-bot/media/07-upload-queue.png
  slot: upload_queue
  topics: upload queue, smart support manager, expert, manager
  note: Upload queue for batch photo processing
  access: Telegram sendPhoto from this path on the bot server
- file: products/agent-bot/media/08-install-bot-and-expert.png
  slot: install_bot_expert
  topics: install, smart support manager, expert, manager
  note: Install bot and Expert in three steps
  access: Telegram sendPhoto from this path on the bot server
