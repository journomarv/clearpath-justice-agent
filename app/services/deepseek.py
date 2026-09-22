import os
from typing import Any

import httpx


class DeepSeekService:
    API_URL = "https://api.deepseek.com/chat/completions"

    def __init__(self) -> None:
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    async def generate_response(
        self,
        message: str,
        knowledge: list[dict[str, Any]],
        pathway: str | None = None,
    ) -> dict[str, Any]:

        if not self.api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY is not configured."
            )

        knowledge_text = "\n\n".join(
            f"Source: {item.get('source', 'Unknown')}\n"
            f"{item.get('content', '')}"
            for item in knowledge
        )

        system_prompt = f"""
You are the ClearPath Justice Agent.

ClearPath Justice is a South African digital justice navigation
service that helps people understand and navigate legally recognised
criminal-record relief pathways.

Core principle:

AI assists, not adjudicates.

You must:

1. Use the supplied knowledge material as your primary factual basis.
2. Do not invent laws, requirements, forms, government procedures,
   fees, timelines or eligibility criteria.
3. Do not make a final legal determination.
4. Do not guarantee that an application will succeed.
5. Do not claim that a criminal record has been expunged or removed.
6. Clearly identify information that requires confirmation.
7. If important information is missing, say what is missing.
8. Distinguish between legal rules, administrative information,
   ClearPath information and information requiring confirmation.
9. Do not pretend to communicate with government departments.
10. Do not claim to be a lawyer or provide legal representation.
11. Keep the response practical and understandable.

The user's pathway, if known, is:

{pathway or "not yet determined"}

Knowledge available:

{knowledge_text}
"""

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
            "stream": False,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        timeout = httpx.Timeout(30.0, connect=10.0)

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                self.API_URL,
                headers=headers,
                json=payload,
            )

        if response.status_code != 200:
            raise ValueError(
                f"DeepSeek API returned HTTP {response.status_code}."
            )

        data = response.json()

        try:
            answer = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError(
                "DeepSeek returned an invalid response."
            ) from exc

        return {
            "answer": answer,
            "pathway": pathway,
            "knowledge_sources": [
                item.get("source", "Unknown")
                for item in knowledge
            ],
            "uncertainty": (
                "Confirm current legal and administrative requirements "
                "with the relevant authority where indicated."
            ),
            "next_step": (
                "Review the information provided and identify any "
                "missing documents or information."
            ),
        }