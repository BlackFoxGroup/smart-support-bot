# Smart Support Bot — Ask AI / Catalog Audit

Date: 2026-08-22  
Phase: A diagnostic + B design. **No deploy in this document.**  
Constraint: future code changes **VPS only** (`/opt/smart-support-bot`), so Git/local stay a rollback source.  
No `.env`, tokens, or passwords in this file.

---

## 1. Executive Summary

Ask AI for a scoped product (e.g. Project Agent Hub) is a long private-chat pipeline in `src/handlers/chat.py` → `_handle_ask_ai_text`. It works, but knowledge is **multi-homed**, Edit **appends**, the model can still take **up to two full AI timeouts**, safety checks are **scattered**, media policy is **split** (RAG may flag attach; chat.py currently gates send), and **git HEAD is behind** the live VPS Ask AI patches.

Live VPS Ask AI files (`chat.py`, `persona.py`, `ai_memory.py`) **match** the GitHUB worktree and `D:\Smart Support Bot`. They are **not** in commit `05045b1`. History diagnostic on VPS: **1 of 14** stored chat messages still looks like an internal prompt dump.

Canonical training **should** be `product.ai_training_text`. Today the same text is also written to `{pid}-ai-memory.md` and `{pid}-catalog-training.md`, and `catalog_teaching_text()` **reads memory after a runtime seed**, not JSON first.

---

## 2. Root Causes

1. After product isolation, failed LLM replies had **no user-facing fallback** → `AI_ERROR`.
2. First fallback pasted **raw memory/prompt** (`memory_prompt_block` + markers).
3. Second fallback pasted **full catalog teaching** + RAG **auto-photo** (`wants_catalog_media` / educational).
4. Prompt still **duplicates** training (JSON snippet + RAG + compact retry teaching).
5. Admin **Edit** and **Append** share `append_catalog_training()` → Edit re-appends.
6. `seed_memory_from_product()` **mutates disk at read time**.
7. No `TOTAL_RESPONSE_BUDGET`; default `AI_TIMEOUT_SECONDS` is **60** and compact retry can run **another** full call.
8. Safety is not one pipeline; leak can still be **persisted** if it passes a later check (truncate 2000 chars in `append_chat`).
9. `ask_product` is a string on the user row; **not validated** against a live enabled catalog.

---

## 3. Architecture Conflicts

| Concern | Current |
|---|---|
| Training SoT | Intended JSON; runtime SoT is often **ai-memory.md catalog slot** |
| Behavior vs catalog teaching | Separate (`behavior` list vs `ai_training_text`) — OK if kept apart |
| Chat with AI vs Ask AI | Split (good); teaching product/behavior still writes md |
| RAG vs LLM | RAG is evidence; LLM is required even when teaching already answers |
| Media | RAG `attach_media` ≠ send permission; chat.py currently requires `wants_send_media` |
| Unscoped Ask AI | Still uses intents, FAQ, installer site catalog, answer memory |
| Scoped Ask AI | Skips intents/FAQ/answer-memory; still may load `vpn-installer` site/catalog if pid is that product |

---

## 4. Data Source Conflicts

Written/read today (verified in code):

| Store | Write | Read in Ask AI (scoped) |
|---|---|---|
| `{pid}.json` `ai_training_text` | `append_catalog_training`, delete, catalog build preserve | `ai_products_snippet` (full text), seed |
| `{pid}-ai-memory.md` `<!-- BEGIN CATALOG -->` | `set_catalog_teaching`, seed, learned Q&A | `catalog_teaching_text` **primary** |
| `{pid}-catalog-training.md` | `write_catalog_training_md` | `memory_prompt_block` (not used when scoped); KB loader can index as product-guide |
| `{pid}-AI_BEHAVIOR.md` | Chat with AI behavior | `behavior_rules_text` → system style |
| RAG units | catalog JSON features/media | `retrieve_catalog_context` |
| `answer_memory.json` | after reply | **skipped** when `ask_product` set |
| `users.json` `chat_history` | `append_chat` | last 8, dump-filtered in prompt only |

`catalog_teaching_text()` calls `seed_memory_from_product()` then returns **memory.catalog**, not JSON. If md catalog is non-empty and JSON later changes without going through `set_catalog_teaching`, **JSON is ignored**.

---

## 5. Prompt Flow Problems (live scoped path)

Built in `_handle_ask_ai_text`:

1. System: `build_system_prompt` + `behavior_rules_text` (may seed).
2. User prompt: product scope, history, question, RAG `query_expanded`, intent `(none)`, `kb_snip` (product-guide chunks only), `extra_sources`.
3. Scoped `extra_sources`: full catalog teaching (up to 4500) + `retrieval.prompt_block` + `ai_products_snippet` (body + features + **full training again**).
4. Compact retry: teaching again (3500) + question.

Duplicates: training ×2–3, catalog body vs RAG features, md guides vs JSON.

No validator that every block’s `product_id` equals `ask_product`.

---

## 6. Performance Bottlenecks

Measured in code, not live traces (no timing instrumentation yet):

| Stage | Typical cost | Note |
|---|---|---|
| Session / lang / ask flags | low | `users.json` lock |
| RAG `retrieve_catalog_context` | low–med | in-process, all units for one pid |
| `knowledge.retrieve` | low–med | scans FAQ index |
| `ai_products_snippet` | low | loads catalogs |
| Primary `ai.chat` | **high** | `ClientTimeout(total=ai_timeout_seconds)` default **60s** |
| Compact retry | **high** | second request, same client timeout |
| Fallback excerpt | low | CPU |
| Media / persist / send | low | |

Worst case: ~60s + ~60s + Telegram «در حال بررسی…». No shared budget. No skip-LLM path when excerpt confidence is high.

---

## 7. Retry / Fallback Problems

- Retry is **not** classified (timeout vs 4xx vs leak).
- Retry runs on **any** `AIClientError` and on leak/incomplete.
- Fallback after retry is deterministic excerpt (good) but intro still dumps up to 900 chars of teaching (can feel like a paste).
- Fallback is **not** a second model call except compact retry **is**.
- No remaining-time check.

---

## 8. Product Isolation Risks

**Guarded today (scoped):** intents off; faq_refs None; answer-memory off; `knowledge.retrieve(..., product_id=)`; RAG `product_id` filter; `ai_products_snippet(product_id=)`.

**Gaps:**

- `ask_product` not checked against `list_all_product` / enabled.
- `loader.product_id_from_guide_stem` only hard-knows `vpn-installer`, `config-builder`, `agent-bot` plus suffix rules; mis-stemmed files can get `chunk_pid=None` and be **dropped** when scoped (safer) or leak when unscoped.
- `ask_product == "vpn-installer"` still pulls installer `catalog_snippet` / site search.
- Unscoped Ask AI can still mix products (by design today).
- No assert on RAG unit `product_id`.
- Compact/fallback use `catalog_teach` for session pid only (good) if pid valid.

---

## 9. Media Policy Risks

| Path | Explicit request? | Can send? |
|---|---|---|
| `chat.py` Ask AI | `wants_send_media` | Yes if files exist |
| `chat.py` end | same `media_paths` | Only filled if explicit |
| `catalog_rag.attach_media` | educational / UI hints | Candidate only; chat ignores unless explicit |
| `menu.py` / `start.py` | product cards | **Yes** (not Ask AI) |
| `group.py` | — | No Ask AI / no catalog send found |
| social/nightly jobs | scheduled | Unrelated |

Risk: another handler calling `answer_with_media` with RAG `attach_media`. Policy is **not** one function. `wants_catalog_media` is still true for many educational questions (candidate).

---

## 10. History and Persistence Problems

- `append_chat(..., limit=8)`, content **[:2000]**.
- Prompt skips dump-like history; **disk still keeps** the dirty message.
- VPS preview (counts only): `users=21`, `history_msgs=14`, `dirty_history_msgs=1`.
- Learned answers: `append_learned_answer` if reply looks “solved”; dump check exists on `final`.
- Cleanup: **not implemented**. This report is the diagnostic; **do not delete history until approved**.

---

## 11. Git / Local / VPS Consistency

| Location | Ask AI trio (`chat` / `persona` / `ai_memory`) | Other src |
|---|---|---|
| Git **commit** `05045b1` | **Missing** leak/excerpt/compact/media-gate/seed-fix | training-in-catalog fallback of that commit |
| GitHUB **worktree** | Present (uncommitted) | extra `M` files; content vs HEAD mostly those 3 |
| `D:\Smart Support Bot` | Same hashes as GitHUB for the trio | `catalog_rag` / `product_catalogs` **hash ≠** GitHUB |
| VPS `/opt/smart-support-bot` | **Same hashes as GitHUB trio** | `catalog_rag`, `product_catalogs`, `catalog_builder`, `main.py` **≠** GitHUB worktree |

Patches vs `05045b1`:

| Patch | In commit? | In worktree? | On VPS? |
|---|---|---|---|
| Prompt leak prevention | no | yes | yes |
| `excerpt_teaching_for_query` | no | yes | yes |
| `_compact_retry` | no | yes | yes |
| Automatic media prevention (chat gate) | no | yes | yes |
| `seed_memory_from_product` empty-catalog-only | no (HEAD still old early-return) | yes | yes |
| Catalog training JSON + hub UX | yes (`05045b1`) | yes | yes (via later uploads) |

**Rollback of VPS Ask AI:** restore the three (or six) files from `05045b1` or from a tarball taken **before** the next deploy. Do not `git reset` VPS blindly; VPS is not a git checkout of HEAD.

---

## 12. Proposed Architecture

```text
ask_ai && valid enabled product_id
  → load JSON catalog once
  → SoT training = raw.ai_training_text
  → RAG(product_id) retrieve relevant slices only
  → validate all unit.product_id == ask_product
  → prompt = system + identity + retrieved slices + short history + question
  → AI with remaining budget
  → if transient error AND budget left → one compact retry
  → else deterministic excerpt / AI_ERROR
  → safety_pipeline(answer)
  → persist only if safe
  → send media only if wants_send_media AND policy(allow)
```

Markdown files: **export/cache only**, filled by explicit write after JSON save, never the read SoT.

---

## 13. Files That Must Change (Phase C, VPS copies)

| File | Why |
|---|---|
| `src/knowledge/ai_memory.py` | SoT read from JSON; `replace_catalog_training`; seed not on every read |
| `src/handlers/admin_settings.py` | Append vs Replace |
| `src/handlers/chat.py` | isolation validation, prompt slim, budget, pipeline, media policy, no persist leak |
| `src/ai/persona.py` | unify safety pipeline |
| `src/knowledge/product_catalogs.py` | snippet without full training dump (or training omitted; RAG excerpt instead) |
| `src/knowledge/catalog_rag.py` | attach is candidate only; never imply send |
| `src/knowledge/loader.py` | safer pid mapping; no dual memory boost if JSON is SoT |
| `src/ui/messaging.py` | optional: require `media_allowed` flag |
| `src/storage/users.py` | history sanitise API (preview first) |
| new `src/ai/safety.py` | pipeline + budget helper |
| new `tests/test_ask_ai_regression.py` | run locally; copy tests to VPS only if desired |

---

## 14. Files That Must Not Change

- `.env` and any token/password file  
- Telegram bot identity  
- `data/users.json` until history cleanup is approved  
- `data/agent_registry.json`  
- Black Fox Fyne installer repo  
- Unrelated jobs: `social_news_job.py`, `nightly_subscription_job.py` (photo sends are not Ask AI)  
- Do **not** blindly overwrite VPS `catalog_rag.py` / `product_catalogs.py` / `main.py` / `catalog_builder.py` from GitHUB worktree (hash mismatch)

---

## 15. Step-by-Step Implementation Plan

Order (low risk first), **VPS only** after a `src` tarball backup:

1. Snapshot `/opt/smart-support-bot/src` → `/opt/smart-support-bot/backups/src-YYYYMMDD-HHMM.tgz`  
2. SoT: `get_catalog_training()` reads JSON; md write-through only  
3. `replace_catalog_training()`; admin Edit uses replace; new-text button uses append  
4. `assert_product_scope(pid, units, snippets)`  
5. Slim prompt: no full training; retrieved excerpt only  
6. `prepare_user_reply()` single pipeline  
7. `media_send_allowed(text)` only explicit hints  
8. `ResponseBudget` from `ai_timeout_seconds` (e.g. 0.7 primary / 0.25 retry / rest fallback)  
9. History cleanup **preview** JSON counts; apply only after approval  
10. Tests on a machine with pytest; optional copy to VPS  

**Essential:** 2, 3, 4, 5, 6, 7, 8  
**Optional:** skip-LLM when excerpt score high; loader alias cleanup  
**Breaking:** changing Edit from append to replace (correct, but operators who relied on Edit=append will see replace)

---

## 16. Automated Test Plan

Add tests (no network):

1. Scope filter drops other `product_id` units  
2. `looks_like_prompt_dump` / pipeline rejects `<!-- BEGIN`  
3. Pipeline output never contains those markers  
4. Excerpt length << full teaching  
5. `wants_send_media("عکسش را بفرست")` true  
6. `wants_send_media("اسکریپت چه جوری کار میکنه؟")` false  
7. append = prev + new  
8. replace = new only  
9. missing/disabled pid → no foreign catalog  
10–11. budget: remaining < threshold skips retry  
12. fallback has no `Operator AI memory`  
13. dump history excluded from context builder  
14. RAG units all match pid  

---

## 17. Manual Verification Plan

Admin: send training (status only) → Edit shows full → save **replaces** → second send **appends**.

User Ask AI Agent Hub: «اسکریپت چه جوری کار میکنه؟» → short related answer; no markers; no full file; no photo.

«عکسش را بفرست» → photo only if files exist.

Other product question in Agent Hub mode → do not know / no SSH-PEM-seller panel.

---

## 18. Deployment Checklist (when Phase C starts)

- [ ] Backup tarball on VPS  
- [ ] Diff only intended files  
- [ ] Do not upload `.env`  
- [ ] Do not upload GitHUB `catalog_rag.py` unless hash-checked against current VPS  
- [ ] Restart `smart-support-bot.service`  
- [ ] `is-active`  
- [ ] One Ask AI smoke test  
- [ ] Keep tarball until confirmed  

---

## 19. Rollback Plan

```text
tar -C /opt/smart-support-bot -xzf /opt/smart-support-bot/backups/src-YYYYMMDD-HHMM.tgz
# or copy backed-up files over /opt/smart-support-bot/src/...
systemctl restart smart-support-bot.service
```

Git `05045b1` is **older** than current VPS Ask AI (would reintroduce AI_ERROR / raw fallback). Rollback target is the **tarball of current VPS**, not necessarily git HEAD.

---

## Ask AI path map (verified)

```text
Message (private text)
  src/handlers/chat.py  on_text
    → users.touch_from_telegram_user
    → _handle_ask_ai_text
Session
    users.has_lang / get_lang / is_ask_ai
    if not ask_ai → USE_MENU_OR_ASK_AI
ask_product
    users.get_ask_ai_product  (ask_ai_product_id)
    set in menu.py set_ask_ai(..., product_id=)
    NO enabled/exists check
Product resolution
    none beyond string id
Knowledge
    behavior_rules_text
    catalog_teaching_text → seed + memory.catalog
    ai_products_snippet(product_id)
    knowledge.retrieve(product_id)  loader.py
RAG
    retrieve_catalog_context(..., product_id)  catalog_rag.py
Prompt
    build_system_prompt  persona.py
    user_prompt string in chat.py
AI
    AIClient.chat  client.py  timeout settings.ai_timeout_seconds
Retry
    _compact_retry  same AIClient
Fallback
    _user_facing_fallback  excerpt_teaching_for_query
Safety
    strip_reasoning_leak, looks_like_reasoning_leak,
    looks_like_prompt_dump, looks_incomplete_reply
    (scattered)
Media
    wants_send_media → listed_image_paths / retrieval.media_paths
    messaging.answer_with_media
Persist
    users.append_chat
    metrics.record_*
    append_learned_answer
    AnswerMemoryStore.remember
Send
    wait.edit_text or answer_with_media
```

Latency / dup / bypass notes are in sections 5–9.

---

## Phase B — Design table

| Item | Problem | Root cause | Proposed | Risk | Perf |
|---|---|---|---|---|---|
| SoT | Triple write | historical md + JSON | Read JSON only | md stale until rewrite | faster reads |
| Edit/Append | Edit appends | one function | replace API | operators notice | none |
| Isolation | invalid pid | no check | validate or re-pick | extra message | none |
| Prompt | duplicate training | snippet+teach+RAG | retrieve only | weaker if RAG misses | smaller prompt, faster model |
| Safety | leak persist | late checks | one pipeline | none | none |
| Media | candidate≠policy | two functions | one `allow_send_media` | photos only on ask | none |
| Retry | 2×60s | no budget | shared budget | more fallbacks | much better |
| History | 1 dirty msg | persist leak | preview then sanitize | need approval | none |

---

*End of Phase A/B. Phase C starts only after operator confirmation; VPS backup first; no git commit unless asked.*
