"""Tests for agent orchestration. The DeepSeek client is always mocked."""
from unittest.mock import AsyncMock

import pytest

from app.agent import detect_relief_type_hint, process_message
from app.deepseek import DeepSeekClient, DeepSeekError
from app.schemas.agent import ChatRequest
from app.schemas.rules import ReliefType


def _mock_client(response_text: str = "Here is some helpful guidance.") -> DeepSeekClient:
    client = AsyncMock(spec=DeepSeekClient)
    client.generate_response = AsyncMock(return_value=response_text)
    return client


@pytest.mark.parametrize(
    "message,expected",
    [
        ("Can I expunge my cannabis conviction?", ReliefType.CANNABIS_EXPUNGEMENT),
        ("I want to clear my criminal record", ReliefType.CRIMINAL_RECORD_EXPUNGEMENT),
        ("What's the weather like today?", None),
    ],
)
def test_detect_relief_type_hint(message, expected):
    assert detect_relief_type_hint(message) == expected


@pytest.mark.asyncio
async def test_process_message_returns_structured_response():
    request = ChatRequest(message="Can I expunge my cannabis conviction?")
    response = await process_message(request, deepseek_client=_mock_client())

    assert response.message
    assert response.next_action in {
        "ask_screening_questions",
        "refer_to_human",
        "clarify_relief_type",
        "continue_conversation",
    }
    assert isinstance(response.requires_human, bool)
    assert 0.0 <= response.confidence <= 1.0


@pytest.mark.asyncio
async def test_eligibility_question_refers_to_human():
    request = ChatRequest(message="Am I eligible to expunge my cannabis conviction?")
    response = await process_message(request, deepseek_client=_mock_client())

    # v0.2 has no verified rules yet, so every eligibility question must
    # be referred, never answered as a determination.
    assert response.requires_human is True
    assert response.next_action == "refer_to_human"


@pytest.mark.asyncio
async def test_unclear_relief_type_asks_for_clarification():
    request = ChatRequest(message="Hi, I need some help")
    response = await process_message(request, deepseek_client=_mock_client())

    assert response.next_action == "clarify_relief_type"
    assert response.relief_type is None


@pytest.mark.asyncio
async def test_deepseek_failure_fails_safe_to_human_referral():
    client = AsyncMock(spec=DeepSeekClient)
    client.generate_response = AsyncMock(side_effect=DeepSeekError("boom"))

    request = ChatRequest(message="Can I expunge my cannabis conviction?")
    response = await process_message(request, deepseek_client=client)

    assert response.requires_human is True
    assert response.next_action == "refer_to_human"
    assert "trouble" in response.message.lower() or "team" in response.message.lower()
