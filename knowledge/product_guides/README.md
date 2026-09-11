# Product guides (MD)

فایل‌های این پوشه نقشهٔ محصول برای Ask AI هستند.

- مستقل از API مدل‌اند (با عوض شدن مدل از بین نمی‌روند).
- وقتی کاتالوگ جزئیات کافی ندهد، ربات از این MDها برای توضیح ساده استفاده می‌کند.
- **هر فایل فقط به یک محصول تعلق دارد** (از روی پیشوند نام فایل):
  - `vpn-installer-*.md` → VPS to VPN by Black Fox Group (Server Installer & Manager)
  - `config-builder-*.md` → Config Builder
  - `agent-bot-*.md` یا `smart-support-*.md` → Smart Support Bot
- در نشست Ask AI داخل یک محصول، فقط راهنمای همان محصول خوانده می‌شود.
- نام رسمی نصب‌کننده در پاسخ‌ها: برنامه **VPS to VPN** از **Black Fox Group** (Server Installer & Manager)
- نام ربات در منو: **Smart Support Bot**

بعد از افزودن فایل جدید، سرویس ربات را ری‌استارت کنید تا `KnowledgeLoader` دوباره بخواند.
