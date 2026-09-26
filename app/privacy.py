"""
Privacy utilities for ClearPath Justice Agent.

Core principle: minimal collection, minimal retention. This module gives the
rest of the app small, well-tested helpers for keeping high-risk personal
identifiers (like South African ID numbers) out of logs, LLM prompts sent to
third parties, and anywhere else they are not strictly required.

This is a safety net, not a substitute for good design: the agent should
avoid *asking* for identifiers like ID numbers in the first place. Screening
questions should stick to the minimum needed to route someone correctly
(e.g. "which type of record?", "roughly how long ago?") rather than
collecting full case details up front.
"""
import re

# South African ID numbers are 13 consecutive digits (YYMMDDSSSSCAZ).
# This is intentionally a broad pattern: we would rather over-redact than
# risk an identifier leaking into a log line or an LLM prompt.
_SA_ID_NUMBER_PATTERN = re.compile(r"\b\d{13}\b")

# Loose pattern for common SA phone number formats, redacted out of an
# abundance of caution when free text is logged or forwarded to the LLM.
_PHONE_NUMBER_PATTERN = re.compile(r"\b(?:\+27|0)\d{9}\b")

REDACTION_TOKEN = "[REDACTED]"


def contains_pii(text: str) -> bool:
    """Return True if text appears to contain a high-risk identifier."""
    if not text:
        return False
    return bool(_SA_ID_NUMBER_PATTERN.search(text) or _PHONE_NUMBER_PATTERN.search(text))


def redact_pii(text: str) -> str:
    """Return a copy of text with likely ID/phone numbers replaced."""
    if not text:
        return text
    redacted = _SA_ID_NUMBER_PATTERN.sub(REDACTION_TOKEN, text)
    redacted = _PHONE_NUMBER_PATTERN.sub(REDACTION_TOKEN, redacted)
    return redacted


def safe_for_logging(text: str, max_length: int = 500) -> str:
    """
    Prepare user-supplied text for logging: redact likely identifiers and
    truncate. Use this everywhere user free text is written to logs.
    """
    redacted = redact_pii(text or "")
    if len(redacted) > max_length:
        redacted = redacted[:max_length] + "...[truncated]"
    return redacted
