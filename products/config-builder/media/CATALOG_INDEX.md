# Catalog media index

This file is the source of truth for catalog files.
The Telegram bot can send these files with sendPhoto.
If a file is listed here, it exists. Never say the catalog has no photo.
Do not invent files that are not listed.
When the user asks to see or send a photo, the bot attaches the file;
the AI only describes it and must not claim it cannot send files.

## config-builder — Config Builder
photo_count: 7
folder: products/config-builder/media/
- file: products/config-builder/media/00-product-logo.png
  slot: product-logo
  topics: logo, brand, config-builder
  note: لوگوی Config Builder. وقتی لوگو یا ظاهر محصول را خواستند همین را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/config-builder/media/01-connection.jpg
  slot: connection
  topics: connection, config builder, 3x-ui, کانفیگ
  note: اتصال به پنل 3X-UI — برای سوال همین بخش همین عکس را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/config-builder/media/02-single.jpg
  slot: single
  topics: single, config builder, 3x-ui, کانفیگ
  note: ساخت تکی کانفیگ — برای سوال همین بخش همین عکس را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/config-builder/media/03-bulk.jpg
  slot: bulk
  topics: bulk, config builder, 3x-ui, کانفیگ
  note: ساخت گروهی کانفیگ — برای سوال همین بخش همین عکس را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/config-builder/media/04-language.jpg
  slot: language
  topics: language, config builder, 3x-ui, کانفیگ
  note: انتخاب زبان برنامه — برای سوال همین بخش همین عکس را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/config-builder/media/05-settings.jpg
  slot: settings
  topics: settings, config builder, 3x-ui, کانفیگ
  note: تنظیمات Config Builder — برای سوال همین بخش همین عکس را بفرست.
  access: Telegram sendPhoto from this path on the bot server
- file: products/config-builder/media/06-contact.jpg
  slot: contact
  topics: contact, config builder, 3x-ui, کانفیگ
  note: تماس و پشتیبانی Config Builder — برای سوال همین بخش همین عکس را بفرست.
  access: Telegram sendPhoto from this path on the bot server
