"""Single Ask AI response safety pipeline. No secrets."""

from __future__ import annotations

import time

from src.ai.persona import (
    looks_incomplete_reply,
    looks_like_prompt_dump,
    looks_like_reasoning_leak,
    strip_internal_prompt_lines,
    strip_reasoning_leak,
)

ASK_AI_TIMEOUT_SECONDS = 20.0
ASK_AI_MAX_TOKENS = 2048


def bounded_ask_timeout(configured: float | int | None) -> float:
    return max(12.0, min(ASK_AI_TIMEOUT_SECONDS, float(configured or 30)))


def bounded_ask_tokens(configured: float | int | None) -> int:
    return max(768, min(ASK_AI_MAX_TOKENS, int(configured or ASK_AI_MAX_TOKENS)))


def is_transient_ai_error(exc: BaseException) -> bool:
    msg = str(exc or "").lower()
    return any(
        token in msg
        for token in (
            "timeout",
            "timed out",
            "temporar",
            "429",
            "502",
            "503",
            "504",
            "connect",
            "reset",
        )
    )


def prepare_user_reply(text: str) -> str:
    """Normalize and reject internal/prompt dumps. Empty means unsafe."""
    cleaned = strip_reasoning_leak(text or "")
    cleaned = strip_internal_prompt_lines(cleaned)
    if not cleaned:
        return ""
    if looks_like_prompt_dump(cleaned) or looks_like_reasoning_leak(cleaned):
        return ""
    if looks_incomplete_reply(cleaned) and looks_like_prompt_dump(text or ""):
        return ""
    return cleaned.strip()


def is_safe_to_persist(text: str) -> bool:
    ready = prepare_user_reply(text)
    return bool(ready) and not looks_like_prompt_dump(ready)


class ResponseBudget:
    def __init__(self, total_seconds: float) -> None:
        self.total = max(8.0, float(total_seconds))
        self.started = time.monotonic()

    def remaining(self) -> float:
        return self.total - (time.monotonic() - self.started)

    def can_retry(self, need_seconds: float = 14.0) -> bool:
        return self.remaining() >= max(8.0, float(need_seconds))
