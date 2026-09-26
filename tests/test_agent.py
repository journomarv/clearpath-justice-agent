"""Tests for ClearPath agent orchestration."""

from unittest.mock import AsyncMock

import pytest

from app.agent import process_message
from app.deepseek import DeepSeekClient, DeepSeekError
from app.knowledge.routing import route_message
from app.schemas.agent import ChatRequest


def _mock_client(
    response_text: str = "Here is some helpful guidance.",
) -> DeepSeekClient:
    client = AsyncMock(spec=DeepSeekClient)
    client.generate_response = AsyncMock(return_value=response_text)
    return client


def test_agent_routing_uses_shared_router():
    route = route_message("Can I expunge my cannabis conviction?")

    assert route.question_type == "personal_justice"
    assert route.pathway == "cannabis_related_relief"
    assert route.intent == "eligibility"


def test_agent_routing_handles_general_expungement():
    route = route_message("I want to clear my criminal record.")

    assert route.question_type == "personal_justice"
    assert route.pathway == "general_expungement"


def test_agent_routing_handles_unknown_message():
    route = route_message("What's the weather like today?")

    assert route.pathway == "unknown"


@pytest.mark.asyncio
async def test_process_message_returns_structured_response():
    request = ChatRequest(
        message="Can I expunge my cannabis conviction?"
    )

    response = await process_message(
        request,
        deepseek_client=_mock_client(),
    )

    assert response.message
    assert response.next_action in {
        "ask_screening_questions",
        "refer_to_human",
        "clarify_relief_type",
        "continue_conversation",
        "prepare_application",
        "track_application",
        "post_decision_support",
        "answer_research_question",
    }
    assert isinstance(response.requires_human, bool)
    assert 0.0 <= response.confidence <= 1.0


@pytest.mark.asyncio
async def test_eligibility_question_refers_to_human():
    request = ChatRequest(
        message="Am I eligible to expunge my cannabis conviction?"
    )

    response = await process_message(
        request,
        deepseek_client=_mock_client(),
    )

    # No verified eligibility rules are implemented yet, so the rules
    # engine must refer this question for human review.
    assert response.requires_human is True
    assert response.next_action == "refer_to_human"


@pytest.mark.asyncio
async def test_unclear_relief_type_asks_for_clarification():
    request = ChatRequest(message="Hi, I need some help")

    response = await process_message(
        request,
        deepseek_client=_mock_client(),
    )

    assert response.next_action == "clarify_relief_type"
    assert response.relief_type is None


@pytest.mark.asyncio
async def test_application_prep_uses_new_intent():
    request = ChatRequest(
        message="I have a theft conviction. What documents do I need?"
    )

    response = await process_message(
        request,
        deepseek_client=_mock_client(),
    )

    assert response.next_action == "prepare_application"
    assert response.relief_type is not None


@pytest.mark.asyncio
async def test_tracking_uses_new_intent():
    request = ChatRequest(
        message=(
            "I have a cannabis conviction. "
            "How long will my expungement application take?"
        )
    )

    response = await process_message(
        request,
        deepseek_client=_mock_client(),
    )

    assert response.next_action == "track_application"


@pytest.mark.asyncio
async def test_post_decision_uses_new_intent():
    request = ChatRequest(
        message="My expungement certificate arrived. What happens next?"
    )

    response = await process_message(
        request,
        deepseek_client=_mock_client(),
    )

    assert response.next_action == "post_decision_support"


@pytest.mark.asyncio
async def test_research_question_uses_research_action():
    request = ChatRequest(
        message="What has Parliament said about expungement?"
    )

    response = await process_message(
        request,
        deepseek_client=_mock_client(),
    )

    assert response.next_action == "answer_research_question"
    assert response.relief_type is not None
    assert response.sources


@pytest.mark.asyncio
async def test_deepseek_failure_fails_safe_to_human_referral():
    client = AsyncMock(spec=DeepSeekClient)
    client.generate_response = AsyncMock(
        side_effect=DeepSeekError("boom")
    )

    request = ChatRequest(
        message="Can I expunge my cannabis conviction?"
    )

    response = await process_message(
        request,
        deepseek_client=client,
    )

    assert response.requires_human is True
    assert response.next_action == "refer_to_human"
    assert (
        "trouble" in response.message.lower()
        or "team" in response.message.lower()
    )
