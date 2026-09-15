# Knowledge roots for the bot (relative to project)

## Always included (public package)

- `product_catalogs/` — mirrored product catalog JSON (canonical catalogs live under `products/<id>/catalog.json`)
- Small JSON helpers: `creator_contact.json`, `group_community.json`, `social_news_sources.json`
- Docs: `ASK_AI_BUNDLES.md`, `CATALOG_FEATURE_COPY.md`

## Per-product Ask AI (no Black Fox FAQ required)

Product-scoped Ask AI uses:

1. `products/<product_id>/catalog.json`
2. `products/<product_id>/ai_profile.json` (reply rules + aliases; auto-created by Manager)
3. Optional screenshots under `products/<product_id>/media/` (added via Expert/Manager)

It does **not** require `AI_BOT_DATABASE` or `AI_Knowledge_Base_Multilingual`.

## Optional Black Fox operator databases (live / private)

These folders power the operator’s own global intents/FAQ. They are **not** shipped in the public GitHub suite zip:

- `AI_Knowledge_Base_Multilingual/`
- `AI_BOT_DATABASE/`
- `Support_Decision_Tree/` (optional)

On a private deploy host that needs them, copy or symlink:

```bash
ln -s /path/to/AI_Knowledge_Base_Multilingual knowledge/AI_Knowledge_Base_Multilingual
ln -s /path/to/AI_BOT_DATABASE knowledge/AI_BOT_DATABASE
```
