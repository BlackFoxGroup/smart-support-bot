# Per-product AI profile

Each product folder may include `ai_profile.json` next to `catalog.json`.

Canonical path: `products/<product_id>/ai_profile.json`

Ask AI (product-scoped) loads this file for reply rules and paraphrase aliases.
It does **not** require `knowledge/AI_BOT_DATABASE` or `knowledge/AI_Knowledge_Base_Multilingual`.

Minimal schema:

```json
{
  "schema_version": 1,
  "product_id": "vpn-installer",
  "reply_rules": {
    "stay_in_product": true,
    "use_howto": true,
    "attach_catalog_media": true,
    "language_from_question": true
  },
  "aliases": { "fa": [], "en": [] },
  "notes": "optional short support notes for AI"
}
```

Manager auto-creates a default profile when a catalog is created/saved/activated if the file is missing.
Media screenshots are optional and added via Expert/Manager (not required in the public source zip).
