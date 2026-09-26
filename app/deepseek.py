"""
DeepSeek API client.

Thin, clean abstraction over the DeepSeek chat completions endpoint. This
is the ONLY place in the app that talks to the LLM over the network — the
agent builds context and prompts, this module just sends them.
"""
import logging
from typing import Optional

import httpx

from app.config import Settings, get_settings

logger = logging.getLogger("clearpath.deepseek")


class DeepSeekError(Exception):
    """Raised when the DeepSeek API call fails or is misconfigured."""


class DeepSeekClient:
    def __init__(self, settings: Optional[Settings] = None):
        self._settings = settings or get_settings()

    @property
    def is_configured(self) -> bool:
        return self._settings.deepseek_configured

    async def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        *,
        temperature: float = 0.3,
        max_tokens: int = 800,
    ) -> str:
        """
        Call DeepSeek's chat completions endpoint and return the assistant
        text. Raises DeepSeekError on any failure — callers should catch
        this and fail safe (e.g. refer to a human) rather than crash.
        """
        if not self.is_configured:
            raise DeepSeekError(
                "DeepSeek API key is not configured. Set DEEPSEEK_API_KEY."
            )

        url = f"{self._settings.deepseek_api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._settings.deepseek_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._settings.deepseek_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as exc:
            # Never include headers/payload (which contain the key) in the
            # error or logs.
            logger.error("DeepSeek API returned status %s", exc.response.status_code)
            raise DeepSeekError(
                f"DeepSeek API returned an error status ({exc.response.status_code})."
            ) from exc
        except httpx.RequestError as exc:
            logger.error("DeepSeek API request failed: %s", type(exc).__name__)
            raise DeepSeekError("Could not reach the DeepSeek API.") from exc
        except (KeyError, IndexError) as exc:
            logger.error("Unexpected DeepSeek response shape")
            raise DeepSeekError("Received an unexpected response from DeepSeek.") from exc
