"""OpenAI-compatible chat completions client with Control Plane failover."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import aiohttp

from src.config import Settings

if TYPE_CHECKING:
    from src.control.service import ControlService

logger = logging.getLogger(__name__)


class AIClientError(RuntimeError):
    """Raised when the upstream AI API fails."""


@dataclass(slots=True)
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class AIClient:
    """Async client. Prefers ControlService registry; falls back to Settings env."""

    def __init__(self, settings: Settings, control: ControlService | None = None) -> None:
        self._settings = settings
        self._control = control
        self._session: aiohttp.ClientSession | None = None
        self.last_usage: TokenUsage = TokenUsage()
        self.last_agent_name: str = settings.ai_model

    def bind_control(self, control: ControlService) -> None:
        self._control = control

    async def start(self) -> None:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self._settings.ai_timeout_seconds)
            self._session = aiohttp.ClientSession(timeout=timeout)
        if self._control:
            await self._control.start()

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
        self._session = None
        if self._control:
            await self._control.close()

    def estimate_spend_usd(self, usage: TokenUsage | None = None) -> float:
        used = usage or self.last_usage
        rate = float(self._settings.ai_usd_per_million_tokens)
        return (max(0, used.total_tokens) / 1_000_000.0) * rate

    async def chat(
        self,
        messages: list[dict[str, Any]],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        retry_empty: bool = True,
    ) -> str:
        # Control Plane path — independent registry + automatic failover
        if self._control is not None:
            try:
                # Inject runtime overrides into a copy when temperature/max_tokens passed
                msgs: list[dict[str, Any]] = list(messages)
                # Reasoning models need headroom so content is not cut mid-sentence.
                token_cap = max_tokens
                if token_cap is None:
                    token_cap = max(4096, int(self._settings.ai_max_tokens or 4096))
                result = await self._control.chat_with_failover(
                    msgs,
                    allow_failover=True,
                    max_tokens_override=token_cap,
                )
                self.last_usage = TokenUsage(
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=result.usage_tokens,
                )
                self.last_agent_name = result.agent.name
                if result.failed_over:
                    logger.warning(
                        "AI failover → agent=%s model=%s",
                        result.agent.name,
                        result.agent.model,
                    )
                return result.text
            except Exception as exc:  # noqa: BLE001
                logger.error("Control Plane chat failed, trying env fallback: %s", type(exc).__name__)
                # Fall through to env Settings so support bot stays up if registry empty/corrupt

        return await self._chat_env(
            messages, temperature=temperature, max_tokens=max_tokens, _retry_empty=retry_empty
        )

    async def chat_with_images(
        self,
        prompt: str,
        image_jpeg_bytes: list[bytes],
        *,
        system: str | None = None,
        max_images: int = 6,
        max_tokens: int | None = None,
    ) -> str:
        """Vision-capable chat: send JPEG bytes as data-URL image_url parts."""
        import base64

        content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
        for raw in (image_jpeg_bytes or [])[: max(1, max_images)]:
            if not raw:
                continue
            b64 = base64.b64encode(raw).decode("ascii")
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                }
            )
        messages: list[dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": content})
        return await self.chat(messages, max_tokens=max_tokens or 400, retry_empty=False)

    async def _chat_env(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        _retry_empty: bool = True,
    ) -> str:
        await self.start()
        assert self._session is not None

        url = f"{self._settings.ai_base_url}/chat/completions"
        payload: dict[str, Any] = {
            "model": self._settings.ai_model,
            "messages": messages,
            "temperature": (
                self._settings.ai_temperature if temperature is None else temperature
            ),
            "max_tokens": (
                self._settings.ai_max_tokens if max_tokens is None else max_tokens
            ),
        }
        headers = {
            "Authorization": f"Bearer {self._settings.ai_api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with self._session.post(url, json=payload, headers=headers) as resp:
                body = await resp.json(content_type=None)
                if resp.status >= 400:
                    detail = body if isinstance(body, dict) else {"raw": body}
                    raise AIClientError(
                        f"AI API HTTP {resp.status}: {detail.get('error', detail)}"
                    )
        except aiohttp.ClientError as exc:
            raise AIClientError(f"AI API request failed: {exc}") from exc

        usage_raw = body.get("usage") if isinstance(body, dict) else None
        if isinstance(usage_raw, dict):
            prompt = int(usage_raw.get("prompt_tokens") or 0)
            completion = int(usage_raw.get("completion_tokens") or 0)
            total = int(usage_raw.get("total_tokens") or (prompt + completion))
            self.last_usage = TokenUsage(
                prompt_tokens=prompt,
                completion_tokens=completion,
                total_tokens=total,
            )
        else:
            self.last_usage = TokenUsage()

        self.last_agent_name = self._settings.ai_model

        try:
            message = body["choices"][0]["message"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AIClientError(f"Unexpected AI response shape: {body!r}") from exc

        content = message.get("content") if isinstance(message, dict) else None
        if isinstance(content, list):
            bits: list[str] = []
            for part in content:
                if isinstance(part, str) and part.strip():
                    bits.append(part.strip())
                elif isinstance(part, dict):
                    txt = part.get("text") or part.get("content")
                    if isinstance(txt, str) and txt.strip():
                        bits.append(txt.strip())
            content = "\n".join(bits)
        if isinstance(content, str) and content.strip():
            return content.strip()

        # Reasoning models may fill reasoning_content and leave content empty.
        # Never show raw chain-of-thought; salvage a final reply when possible.
        from src.ai.persona import salvage_reply_from_reasoning

        reasoning = None
        if isinstance(message, dict):
            reasoning = message.get("reasoning_content") or message.get("reasoning")
        has_reasoning = isinstance(reasoning, str) and bool(reasoning.strip())
        if has_reasoning:
            salvaged = salvage_reply_from_reasoning(reasoning)
            if salvaged:
                logger.warning(
                    "AI empty content; salvaged user-facing reply from reasoning (%s chars)",
                    len(salvaged),
                )
                return salvaged

        used_max = int(payload.get("max_tokens") or self._settings.ai_max_tokens)
        if has_reasoning and _retry_empty and used_max < 8192:
            bump = min(8192, max(used_max * 2, used_max + 2048))
            logger.warning(
                "AI empty content with reasoning_content; retrying max_tokens=%s",
                bump,
            )
            # Nudge the model to put the Telegram reply in `content`.
            retry_messages = list(messages) + [
                {
                    "role": "user",
                    "content": (
                        "IMPORTANT: Put the final Telegram reply in the content field only. "
                        "Do not leave content empty. No chain-of-thought."
                    ),
                }
            ]
            return await self._chat_env(
                retry_messages,
                temperature=temperature,
                max_tokens=bump,
                _retry_empty=False,
            )

        if has_reasoning:
            logger.error(
                "AI still empty content after retry; refusing to leak reasoning_content"
            )
        raise AIClientError(f"AI returned empty content: {body!r}")
