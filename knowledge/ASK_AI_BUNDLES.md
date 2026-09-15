# Ask AI / Catalog change bundles (2026-08-16)

Organized packages synced to GitHub `smart-support-bot` and VPS `/opt/Smart Support Bot`.

## 01 — Catalog (product facts)
- `knowledge/product_catalogs/vpn-installer.json`
- Free Domain: Pro=3, AI Pro=5; Configure auto-activate; Add Domain / Mesh howto
- Official name: **Black Fox VPN Installer & Android**

## 02 — Product guides (MD fallback)
- `knowledge/product_guides/*`
- Structure map + domain/mesh guide (FA/EN)

## 03 — Ask AI pipeline (code)
- Local answer memory (`src/storage/answer_memory.py` → `data/answer_memory.json`)
- Catalog RAG + loader product guides
- Chat path: catalog → memory → MD → LLM
- Persona product naming

## 04 — Service unit
- `deploy/smart-support-bot.service`
- WorkingDirectory `/opt/Smart Support Bot`
- ReadWritePaths: `data`, `media`, `knowledge/product_catalogs`

Runtime memory file is NOT committed (gitignore `data/*.json`).
