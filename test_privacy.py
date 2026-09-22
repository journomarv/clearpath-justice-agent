"""Tests for privacy-conscious input handling."""
import pytest
from pydantic import ValidationError

from app.privacy import contains_pii, redact_pii, safe_for_logging
from app.schemas.agent import ChatRequest
from app.schemas.rules import ScreeningAnswers


def test_contains_pii_detects_13_digit_id_number():
    assert contains_pii("My ID number is 9001015009087, please help")


def test_contains_pii_detects_phone_number():
    assert contains_pii("call me on 0821234567")


def test_contains_pii_false_for_ordinary_message():
    assert not contains_pii("Can you tell me about expungement?")


def test_redact_pii_removes_id_number():
    redacted = redact_pii("ID: 9001015009087 thanks")
    assert "9001015009087" not in redacted
    assert "[REDACTED]" in redacted


def test_safe_for_logging_truncates_long_text():
    long_text = "a" * 1000
    result = safe_for_logging(long_text, max_length=50)
    assert len(result) <= 70  # 50 + truncation marker
    assert result.endswith("...[truncated]")


def test_chat_request_rejects_id_number_in_message():
    with pytest.raises(ValidationError):
        ChatRequest(message="My ID is 9001015009087, am I eligible?")


def test_chat_request_accepts_ordinary_message():
    request = ChatRequest(message="Can I expunge my cannabis conviction?")
    assert request.message


def test_screening_answers_rejects_id_number_in_free_text():
    with pytest.raises(ValidationError):
        ScreeningAnswers(free_text_context="9001015009087")


def test_screening_answers_accepts_ordinary_free_text():
    answers = ScreeningAnswers(free_text_context="Convicted about five years ago")
    assert answers.free_text_context
