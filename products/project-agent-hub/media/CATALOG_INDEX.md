# Catalog media index

This file is the source of truth for catalog files.
The Telegram bot can send these files with sendPhoto.
If a file is listed here, it exists. Never say the catalog has no photo.
Do not invent files that are not listed.
When the user asks to see or send a photo, the bot attaches the file;
the AI only describes it and must not claim it cannot send files.

## project-agent-hub — Project Agent Hub
photo_count: 1
folder: media/catalogs/project-agent-hub/
- file: media/catalogs/project-agent-hub/photo_AQADdA1rG31iSER--1787356044450898960.jpg
  slot: project-management-dashboard
  title: هاب عامل پروژه - داشبورد اصلی
  topics: dashboard, project-management, api-configuration, authentication, agent-execution
  note: این عکس مربوط به Project Agent Hub می باشد و صفحه اصلی آن هست
  access: Telegram sendPhoto from this path on the bot server
