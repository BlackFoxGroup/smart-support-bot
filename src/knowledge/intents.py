"""Intent matching from AI_BOT_DATABASE JSON (keyword / sample overlap)."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.config import Settings
from src.knowledge.loader import tokenize

logger = logging.getLogger(__name__)

_WS_RE = re.compile(r"\s+")


@dataclass(slots=True)
class IntentRecord:
    intent: str
    language: str
    category: str
    keywords: list[str]
    sample_questions: list[str]
    short_answer: str
    full_answer: str
    clarifying_questions: list[str]
    faq_refs: list[str]
    related_intents: list[str]
    priority: str
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @property
    def searchable_blob(self) -> str:
        parts = [
            self.intent.replace("_", " "),
            " ".join(self.keywords),
            " ".join(self.sample_questions),
        ]
        return " ".join(parts)


@dataclass(slots=True)
class IntentMatch:
    record: IntentRecord | None
    score: float
    low_confidence: bool
    clarifying_question: str | None = None


class IntentMatcher:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._by_lang: dict[str, list[IntentRecord]] = {}
        self.facts: dict[str, Any] = {}

    def load(self) -> None:
        root = self.settings.intents_dir
        intents_dir = root / "intents"
        loaded = 0
        for lang in ("fa", "en", "ru", "zh"):
            path = intents_dir / f"intents_{lang}.json"
            records = self._load_file(path, lang)
            if not records:
                # Fallback: filter from master / all_languages
                records = self._load_from_flat(root, lang)
            self._by_lang[lang] = records
            loaded += len(records)
            if records and not self.facts:
                # facts already handled in knowledge loader; keep optional mirror
                pass
        logger.info("Intents loaded: %s records across %s langs", loaded, len(self._by_lang))

    def _load_file(self, path: Path, lang: str) -> list[IntentRecord]:
        if not path.is_file():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Cannot load intents %s: %s", path, exc)
            return []
        if isinstance(data.get("meta"), dict) and isinstance(data["meta"].get("facts"), dict):
            self.facts = data["meta"]["facts"]
        items = data.get("intents") if isinstance(data, dict) else None
        if not isinstance(items, list):
            return []
        return [r for item in items if (r := self._parse_record(item, lang))]

    def _load_from_flat(self, root: Path, lang: str) -> list[IntentRecord]:
        for name in ("all_languages_database.json", "intents_master_multilingual.json"):
            path = root / name
            if not path.is_file():
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            records: list[IntentRecord] = []
            # Flat list with language field
            if isinstance(data, dict) and isinstance(data.get("intents"), list):
                for item in data["intents"]:
                    if not isinstance(item, dict):
                        continue
                    item_lang = str(item.get("language") or "").lower()
                    if item_lang and item_lang != lang:
                        continue
                    rec = self._parse_record(item, lang)
                    if rec:
                        records.append(rec)
            if records:
                return records
        return []

    def _parse_record(self, item: dict[str, Any], lang: str) -> IntentRecord | None:
        intent = str(item.get("intent") or "").strip()
        if not intent:
            return None
        return IntentRecord(
            intent=intent,
            language=str(item.get("language") or lang),
            category=str(item.get("category") or ""),
            keywords=[str(k) for k in (item.get("keywords") or []) if k],
            sample_questions=[str(q) for q in (item.get("sample_questions") or []) if q],
            short_answer=str(item.get("short_answer") or ""),
            full_answer=str(item.get("full_answer") or ""),
            clarifying_questions=[
                str(q) for q in (item.get("clarifying_questions") or []) if q
            ],
            faq_refs=[str(r) for r in (item.get("faq_refs") or []) if r],
            related_intents=[str(r) for r in (item.get("related_intents") or []) if r],
            priority=str(item.get("priority") or "medium"),
            raw=item,
        )

    def match(
        self, text: str, lang: str, *, prior_blob: str = ""
    ) -> IntentMatch:
        query = _WS_RE.sub(" ", (text or "").strip())
        if not query:
            return IntentMatch(record=None, score=0.0, low_confidence=True)

        combined = f"{prior_blob}\n{query}".lower() if prior_blob else query.lower()

        # Bot / product introduction — never route to troubleshooting stage menu
        if _looks_identity(query):
            intro = self._find_by_name("product_what_is", lang)
            return IntentMatch(
                record=intro,
                score=0.95,
                low_confidence=False,
                clarifying_question=None,
            )

        # Ambiguous “doesn’t work” patterns → force clarifying intent when present
        if _looks_ambiguous(query):
            amb = self._find_by_name("ambiguous_app_broken", lang)
            if amb and amb.clarifying_questions:
                return IntentMatch(
                    record=amb,
                    score=0.5,
                    low_confidence=True,
                    clarifying_question=amb.clarifying_questions[0],
                )

        # Vague “install” without Central/Exit/Node → ask which target
        if _looks_vague_install(query) and not _has_exit_signal(combined) and not _has_central_signal(combined):
            return IntentMatch(
                record=self._find_by_name("full_deploy", lang),
                score=0.35,
                low_confidence=True,
                clarifying_question=_install_clarify(lang),
            )

        candidates = list(self._by_lang.get(lang) or [])
        if lang != "en":
            candidates.extend(self._by_lang.get("en") or [])

        q_tokens = tokenize(query)
        q_lower = query.lower()
        best: IntentRecord | None = None
        best_score = 0.0
        exit_signal = _has_exit_signal(combined)
        central_signal = _has_central_signal(combined)

        for rec in candidates:
            score = self._score(q_lower, q_tokens, rec)
            name = rec.intent.lower()
            if exit_signal:
                if name in {"add_exit", "exit_limit", "delete_exit"}:
                    score += 0.55
                if name in {"full_deploy", "setup_central", "connect_ssh"}:
                    score *= 0.35
            elif central_signal and name in {"full_deploy", "setup_central"}:
                score += 0.25
            if score > best_score:
                best_score = score
                best = rec

        # Hard preference: Exit context must not answer as Central Full Deploy
        if exit_signal:
            exit_rec = self._find_by_name("add_exit", lang)
            if exit_rec and (
                best is None
                or best.intent.lower() in {"full_deploy", "setup_central", "connect_ssh"}
                or best_score < 0.45
            ):
                best = exit_rec
                best_score = max(best_score, 0.72)

        threshold = self.settings.intent_confidence_threshold
        low = best is None or best_score < threshold
        # Only auto-clarify for true problem reports — never dump stage menu on unknown Qs
        clarifying: str | None = None
        if low and best and best.intent == "ambiguous_app_broken" and best.clarifying_questions:
            clarifying = best.clarifying_questions[0]

        return IntentMatch(
            record=best,
            score=best_score,
            low_confidence=low,
            clarifying_question=clarifying,
        )

    def _find_by_name(self, intent: str, lang: str) -> IntentRecord | None:
        for rec in self._by_lang.get(lang) or []:
            if rec.intent == intent:
                return rec
        for rec in self._by_lang.get("en") or []:
            if rec.intent == intent:
                return rec
        return None

    def _score(self, q_lower: str, q_tokens: set[str], rec: IntentRecord) -> float:
        score = 0.0
        # Keyword hits (cap so long keyword lists cannot drown a better intent)
        kw_score = 0.0
        for kw in rec.keywords:
            k = kw.lower().strip()
            if not k:
                continue
            if k in q_lower:
                kw_score += 0.18
            elif set(tokenize(k)) <= q_tokens:
                kw_score += 0.12
        score += min(kw_score, 0.54)

        # Sample question overlap — take the best sample, do not sum all of them
        best_sample = 0.0
        for sample in rec.sample_questions:
            s = sample.lower().strip()
            if not s:
                continue
            sample_score = 0.0
            if s == q_lower or s in q_lower or q_lower in s:
                sample_score = 0.55
            else:
                s_tokens = tokenize(s)
                if s_tokens:
                    inter = q_tokens & s_tokens
                    if inter:
                        sample_score = 0.35 * (len(inter) / max(len(s_tokens), 1))
            if sample_score > best_sample:
                best_sample = sample_score
        score += best_sample

        # Strong phrase boost for exact feature names in the query
        intent_phrases = {
            "add_exit": ("add exit server", "add exit", "exit server"),
            "add_tunnel": ("add tunnel server", "add tunnel", "tunnel server"),
            "add_node": ("add node",),
            "full_deploy": ("full deploy",),
            "setup_central": ("setup central", "central server"),
        }
        for phrase in intent_phrases.get(rec.intent.lower(), ()):
            if phrase in q_lower:
                score += 0.75
                break

        # Intent id token overlap
        id_tokens = tokenize(rec.intent.replace("_", " "))
        if id_tokens & q_tokens:
            score += 0.08 * len(id_tokens & q_tokens)

        # Soft priority boost
        if rec.priority == "critical":
            score *= 1.05
        elif rec.priority == "high":
            score *= 1.02
        return score


def looks_identity(text: str) -> bool:
    return _looks_identity(text)


def looks_creator(text: str) -> bool:
    """True when the user asks about Black Fox / the product creator."""
    t = (text or "").lower().strip()
    markers = (
        "سازنده",
        "کی ساخته",
        "چه کسی ساخته",
        "کیه ساخته",
        "black fox group",
        "بلک فاکس",
        "blackfox",
        "درباره سازنده",
        "تیم سازنده",
        "who made",
        "who created",
        "who built",
        "creator",
        "about the creator",
        "кто создал",
        "создатель",
        "谁做的",
        "创作者",
    )
    return any(m in t for m in markers)



def looks_usage_howto(text: str) -> bool:
    """True when the user asks how to use / operate a product section (any phrasing)."""
    t = (text or "").lower().strip()
    markers = (
        "چطور",
        "چگونه",
        "چه جوری",
        "چهجوری",
        "نحوه",
        "آموزش",
        "اموزش",
        "استفاده",
        "چیکار کنم",
        "چی کار کنم",
        "چکار کنم",
        "مراحل",
        "قدم به قدم",
        "گام به گام",
        "راهنما",
        "کمکم کن",
        "کمک کن",
        "نمیدونم",
        "نمی‌دونم",
        "نمیتونم",
        "نمی‌تونم",
        "کار نمیکنه",
        "کار نمی‌کنه",
        "گیر کردم",
        "از کجا",
        "کجا بزنم",
        "کدام دکمه",
        "کدوم دکمه",
        "how to",
        "howto",
        "how do i",
        "how can i",
        "how does",
        "tutorial",
        "steps",
        "usage",
        "use the",
        "help me",
        "where do i",
        "which button",
        "как ",
        "как пользоваться",
        "обучение",
        "помоги",
        "怎么用",
        "如何使用",
        "教程",
        "怎么办",
    )
    return any(m in t for m in markers)



def detect_reply_lang(text: str, fallback: str = "en") -> str:
    """Infer reply language from the question text (not profile preference)."""
    raw = text or ""
    fb = (fallback or "en").strip().lower()[:2] or "en"
    if re.search(r"[\u0600-\u06FF]", raw):
        return "fa"
    if re.search(r"[\u0400-\u04FF]", raw):
        return "ru"
    if re.search(r"[\u4E00-\u9FFF]", raw):
        return "zh"
    # Latin / English question
    if re.search(r"[A-Za-z]", raw):
        return "en"
    return fb if fb in {"fa", "en", "ru", "zh"} else "en"


def _looks_identity(text: str) -> bool:
    t = (text or "").lower().strip()
    markers = (
        "خودت معرفی",
        "خودتو معرفی",
        "معرفی کن",
        "معرفی خودت",
        "کی هستی",
        "کیستی",
        "تو کی هستی",
        "اسمت چیه",
        "who are you",
        "introduce yourself",
        "what are you",
        "your name",
        "кто ты",
        "представься",
        "你是谁",
        "介绍一下你",
        "自我介绍",
    )
    return any(m in t for m in markers)


def _looks_ambiguous(text: str) -> bool:
    t = text.lower().strip()
    patterns = (
        "doesn't work",
        "does not work",
        "not working",
        "broken",
        "کار نمیکنه",
        "کار نمی‌کنه",
        "کار نمیکند",
        "کار نمی‌کند",
        "خراب",
        "не работает",
        "не працює",
        "坏了",
        "不能用",
        "不行",
    )
    if len(t) <= 40 and any(p in t for p in patterns):
        return True
    return False


def _has_exit_signal(text: str) -> bool:
    t = (text or "").lower()
    markers = (
        "exit",
        "egress",
        "خروجی",
        "سرور خروجی",
        "add exit",
        "выход",
        "出口",
    )
    return any(m in t for m in markers)


def _has_central_signal(text: str) -> bool:
    t = (text or "").lower()
    markers = (
        "central",
        "مرکزی",
        "full deploy",
        "setup central",
        "پنل مرکزی",
        "центральн",
        "中心",
    )
    return any(m in t for m in markers)


def _looks_vague_install(text: str) -> bool:
    t = text.lower().strip()
    if len(t) > 48:
        return False
    vague = (
        "نصب کنم",
        "نصب کن",
        "نصب",
        "install",
        "how to install",
        "راهنمای نصب",
        "چطور نصب",
        "установ",
        "安装",
    )
    return any(v == t or t.startswith(v) or v in t for v in vague) and not any(
        x in t for x in ("exit", "خروجی", "central", "مرکزی", "node", "نود", "tunnel", "تونل", "panel", "پنل")
    )


def _install_clarify(lang: str) -> str:
    messages = {
        "fa": (
            "برای راهنمای درست بگویید کدام را می‌خواهید نصب کنید؟\n"
            "۱) سرور مرکزی (Central / Full Deploy)\n"
            "۲) سرور خروجی (Exit / Add Exit Server)\n"
            "۳) Node یا Tunnel"
        ),
        "en": (
            "To give the right steps, which do you want to install?\n"
            "1) Central Server (Full Deploy)\n"
            "2) Exit Server (Add Exit Server)\n"
            "3) Node or Tunnel"
        ),
        "ru": (
            "Уточните, что устанавливаете:\n"
            "1) Central (Full Deploy)\n"
            "2) Exit (Add Exit Server)\n"
            "3) Node или Tunnel"
        ),
        "zh": (
            "请说明要安装哪一类：\n"
            "1) 中心服务器 Central（Full Deploy）\n"
            "2) 出口服务器 Exit（Add Exit Server）\n"
            "3) Node 或 Tunnel"
        ),
    }
    return messages.get(lang, messages["en"])
