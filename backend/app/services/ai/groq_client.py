"""Groq API client — structured JSON reasoning layer.

Fully env-var driven. If GROQ_API_KEY is absent, `enabled` is False and every
caller degrades gracefully (returns None) instead of raising.
"""

import asyncio
import json
import logging

import httpx

from app.config import settings

logger = logging.getLogger("orbit.ai.groq")


class GroqClient:
    def __init__(self) -> None:
        self.api_key = settings.groq_api_key
        self.model = settings.groq_model
        self.base_url = settings.groq_base_url
        self.timeout = settings.groq_timeout
        self.calls_made = 0

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    async def json_completion(
        self,
        system: str,
        user: str,
        max_tokens: int = 1200,
        temperature: float = 0.1,
        retries: int = 3,
    ) -> dict | None:
        """Request a JSON object completion. Returns parsed dict or None."""
        if not self.enabled:
            return None

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {"type": "json_object"},
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        backoff = 1.5
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(
                        f"{self.base_url}/chat/completions", json=payload, headers=headers
                    )
                if resp.status_code == 429:
                    await asyncio.sleep(backoff * (2**attempt))
                    continue
                if resp.status_code >= 400:
                    logger.warning("Groq error %s: %s", resp.status_code, resp.text[:300])
                    if resp.status_code >= 500:
                        await asyncio.sleep(backoff * (2**attempt))
                        continue
                    return None
                self.calls_made += 1
                content = resp.json()["choices"][0]["message"]["content"]
                return json.loads(content)
            except (httpx.HTTPError, json.JSONDecodeError, KeyError, IndexError) as exc:
                logger.warning("Groq request failed (attempt %s): %s", attempt + 1, exc)
                await asyncio.sleep(backoff * (2**attempt))
        return None


groq_client = GroqClient()
