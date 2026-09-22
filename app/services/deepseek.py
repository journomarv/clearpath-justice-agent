import logging
from typing import Any

import httpx

from app.config import settings


logger = logging.getLogger(__name__)


class DeepSeekError(Exception):
    """Safe application-level DeepSeek error."""


class DeepSeekService:
    def __init__(self) -> None:
        self.api_key = settings.deepseek_api_key
        self.model = settings.deepseek_model
        self.base_url = settings.deepseek_api_base.rstrip("/")

    async def chat(
        self,
        message: str,
        knowledge_context: str,
        pathway: str | None = None,
    ) -> dict[str, Any]:

        if not self.api_key:
            raise DeepSeekError(
                "The AI service is not configured."
            )

        system_prompt = f"""
You are the ClearPath Justice Agent, an AI-assisted
digital justice navigation assistant for South Africa.

Core principle:
AI assists, not adjudicates.

You help people understand and navigate criminal-record
relief and expungement processes.

You must:
- use the supplied knowledge context;
- distinguish verified information from information requiring confirmation;
- never invent legislation, eligibility requirements, fees, forms,
  government procedures or deadlines;
- never claim that a person's record has been expunged;
- never claim to have contacted a government department;
- never fabricate case status;
- never make a final legal determination;
- recommend confirmation with the responsible authority or a qualified
  legal professional when the information is uncertain.

The user may be asking about:
{pathway or "an undetermined pathway"}

Knowledge context:
{knowledge_context}
""".strip()

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": message,
                },
            ],
            "temperature": 0.1,
        }

        timeout = httpx.Timeout(
            30.0,
            connect=10.0,
        )

        try:
            async with httpx.AsyncClient(
                timeout=timeout
            ) as client:

                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )

                response.raise_for_status()

                data = response.json()

        except httpx.TimeoutException:
            logger.warning("DeepSeek request timed out.")
            raise DeepSeekError(
                "The AI service timed out. Please try again."
            )

        except httpx.HTTPStatusError:
            logger.warning(
                "DeepSeek returned HTTP status %s.",
                response.status_code,
            )
            raise DeepSeekError(
                "The AI service returned an error."
            )

        except httpx.RequestError:
            logger.warning(
                "Unable to connect to DeepSeek."
            )
            raise DeepSeekError(
                "The AI service could not be reached."
            )

        except ValueError:
            logger.warning(
                "DeepSeek returned invalid JSON."
            )
            raise DeepSeekError(
                "The AI service returned an invalid response."
            )

        try:
            answer = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            logger.warning(
                "DeepSeek response did not contain expected content."
            )
            raise DeepSeekError(
                "The AI service returned an unexpected response."
            )

        return {
            "answer": answer,
            "pathway": pathway,
            "knowledge_sources": [],
            "uncertainty": (
                "This response is informational and does not constitute "
                "a final legal determination."
            ),
            "next_step": (
                "Confirm pathway-specific requirements with the "
                "responsible South African authority where necessary."
            ),
        }