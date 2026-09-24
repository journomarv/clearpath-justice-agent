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

    async def generate_response(
        self,
        message: str,
        knowledge: list[dict[str, str]],
        pathway: str | None = None,
        intent: str | None = None,
        question_type: str | None = None,
    ) -> dict[str, Any]:

        if not self.api_key:
            raise DeepSeekError(
                "The AI service is not configured."
            )

        knowledge_context = "\n\n".join(
            f"Source: {item.get('source', 'unknown')}\n"
            f"{item.get('content', '')}"
            for item in knowledge
        )

        system_prompt = f"""
You are Path, the ClearPath Justice Agent.

You are an AI-assisted digital justice assistant focused on
South Africa.

Your role has two connected modes:

1. PERSONAL JUSTICE NAVIGATOR
Help a person understand and navigate issues such as:
- criminal-record expungement;
- criminal-record relief;
- cannabis-related record relief;
- child justice;
- police clearance;
- application preparation;
- application tracking;
- post-decision questions.

2. JUSTICE RESEARCH ASSISTANT
Help users research broader questions about South African justice,
including:
- Parliament;
- Hansard;
- parliamentary questions;
- committees;
- Bills;
- legislation;
- court judgments;
- case law;
- law reform;
- academic research;
- government reports;
- justice statistics;
- datasets;
- civil society research;
- justice policy.

CORE PRINCIPLE:

AI assists, not adjudicates.

QUESTION TYPE:

{question_type or "general_justice"}

MATTER/PATHWAY:

{pathway or "undetermined"}

INTENT:

{intent or "undetermined"}

GENERAL RULES:

- Use the supplied ClearPath knowledge context.
- Do not invent facts, legislation, cases, statistics, dates, fees,
  procedures, government actions or sources.
- Distinguish verified information from interpretation.
- If the supplied knowledge is insufficient, say so.
- Do not present a curated sample as an exhaustive dataset.
- Do not turn a number of indexed documents into a claim about the
  total number of parliamentary discussions.
- When answering "how many", explain what is being counted and the
  limits of the available evidence.
- Prefer wording such as "I found at least..." or "In the records
  currently indexed..." when the evidence is not exhaustive.
- Distinguish parliamentary discussion from a change in law.
- When discussing legislation, distinguish:
  proposed, introduced, passed, assented to, commenced and current law.
- Identify the source or document supporting important factual claims.
- Include dates where they are available.
- Do not fabricate citations or links.
- Do not claim to have searched a complete parliamentary database unless
  such a database was actually supplied to you.
- Do not claim that a person's criminal record has been expunged.
- Do not claim to have contacted a government department.
- Do not fabricate a person's case status.
- Do not make a final legal determination.
- For personal legal questions, identify missing facts and explain what
  should be confirmed with the responsible authority or qualified lawyer.
- For research questions, answer the research question directly before
  adding limitations.

RESEARCH COUNTING RULE:

If the user asks something like:

"How many times has Parliament dealt with expungements?"

do NOT simply count the number of files in the knowledge base.

Instead:

1. Explain what the available evidence actually covers.
2. Identify the indexed parliamentary records.
3. Explain whether the count represents documents, proceedings,
   legislative initiatives or individual mentions.
4. State that the indexed collection is not exhaustive unless it has
   been systematically searched and deduplicated.
5. Give an "at least" count only when justified by the supplied records.

SOURCE QUALITY:

Treat primary sources such as official Parliament material,
official government documents and court judgments as stronger evidence
than secondary commentary.

When secondary material conflicts with a primary source, identify the
conflict rather than silently choosing one.

ClearPath knowledge context:

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
            logger.warning(
                "DeepSeek request timed out."
            )
            raise DeepSeekError(
                "The AI service timed out. Please try again."
            ) from None

        except httpx.HTTPStatusError as exc:
            logger.warning(
                "DeepSeek returned HTTP status %s. Response: %s",
                exc.response.status_code,
                exc.response.text[:1000],
            )
            raise DeepSeekError(
                "The AI service returned an error."
            ) from None

        except httpx.RequestError as exc:
            logger.warning(
                "Unable to connect to DeepSeek: %s: %s",
                type(exc).__name__,
                str(exc),
            )
            raise DeepSeekError(
                "The AI service could not be reached."
            ) from None

        except ValueError:
            logger.warning(
                "DeepSeek returned invalid JSON."
            )
            raise DeepSeekError(
                "The AI service returned an invalid response."
            ) from None

        try:
            answer = data["choices"][0]["message"]["content"]

        except (KeyError, IndexError, TypeError):
            logger.warning(
                "DeepSeek response did not contain expected content."
            )
            raise DeepSeekError(
                "The AI service returned an unexpected response."
            ) from None

        return {
            "answer": answer,
            "pathway": pathway,
            "intent": intent,
            "question_type": question_type,
            "knowledge_sources": [
                item.get("source", "unknown")
                for item in knowledge
            ],
            "uncertainty": (
                "This response is informational. "
                "Research answers depend on the evidence currently indexed, "
                "and personal legal questions are not final legal determinations."
            ),
            "next_step": (
                "For research questions, verify important claims against "
                "the underlying primary source. For personal legal matters, "
                "confirm pathway-specific requirements with the responsible "
                "South African authority or a qualified legal professional."
            ),
        }