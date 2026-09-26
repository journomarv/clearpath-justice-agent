"""
ClearPath agent orchestration.

The agent coordinates:
    1. conversational routing;
    2. bounded knowledge retrieval;
    3. deterministic rules evaluation for eligibility questions;
    4. DeepSeek response generation.

The LLM never determines legal eligibility.

Core principle:
    AI assists; it does not adjudicate.
"""

import logging
from typing import List, Optional

from app.deepseek import DeepSeekClient, DeepSeekError
from app.knowledge.retrieval import retrieve_knowledge
from app.knowledge.routing import Route, route_message
from app.privacy import safe_for_logging
from app.schemas.agent import ChatRequest, ChatResponse, SourceRef
from app.schemas.rules import ReliefType, ScreeningAnswers
from app.tools.eligibility import check_eligibility
from app.tools.referrals import ReferralReason, create_referral

logger = logging.getLogger("clearpath.agent")


SYSTEM_PROMPT = """You are Path, the ClearPath Justice AI-assisted digital
justice guide for South Africa.

Core rule: AI assists; it does not adjudicate.

You help people:
- understand justice information;
- identify potentially relevant pathways;
- prepare questions and documents;
- understand processes;
- identify possible next steps;
- locate authoritative sources and services.

You do NOT:
- determine legal eligibility yourself;
- determine guilt or innocence;
- guarantee expungement or record removal;
- claim that a government application has been checked unless a verified
  integration actually returned that information;
- invent South African legal criteria, deadlines, fees, forms, procedures,
  contacts, government records or case status;
- treat parliamentary discussion, academic research, advocacy or news as
  current law;
- request unnecessary identity numbers, full case numbers, passwords,
  banking information or other sensitive identifiers.

LEGAL ELIGIBILITY:
If ASSESSMENT CONTEXT is provided, it comes from ClearPath's deterministic
rules engine. Treat it as authoritative for the current implemented rules.
Explain it faithfully and do not contradict, extend or soften it.

KNOWLEDGE:
The KNOWLEDGE CONTEXT consists of ClearPath's retrieved evidence. Use only
that context for factual claims about the user's question. If the context
does not establish something, say that it needs verification rather than
guessing.

SOURCE DISCIPLINE:
Distinguish between:
- current law;
- official government information;
- court judgments;
- parliamentary material;
- law-reform material;
- academic research;
- datasets;
- civil-society information;
- news reporting.

A parliamentary proposal is not automatically law. Academic research is
not automatically legal authority. News reporting is not primary law.

UNCERTAINTY:
Use careful language such as "may", "generally", "based on the information
available", and "you may need to confirm" where appropriate.

STYLE:
Be calm, clear and conversational. Use plain language. Avoid unnecessary
legal jargon. Answer the user's question directly before giving additional
context.

PRIVACY:
Do not ask the user to paste sensitive identifiers. Where dates or other
details are needed, approximate dates and general descriptions are
preferable.
"""


def _route_to_relief_type(route: Route) -> Optional[ReliefType]:
    """Map a conversational pathway to the rules-engine relief type."""
    mapping = {
        "cannabis_related_relief": ReliefType.CANNABIS_EXPUNGEMENT,
        "general_expungement": ReliefType.CRIMINAL_RECORD_EXPUNGEMENT,
    }
    return mapping.get(route.pathway)


def _sources_from_ids(source_ids: List[str]) -> List[SourceRef]:
    """Convert retrieved source IDs into response source references."""
    from app.knowledge.sources import get_source

    refs: List[SourceRef] = []

    for source_id in source_ids:
        source = get_source(source_id)

        if source is None:
            continue

        refs.append(
            SourceRef(
                id=source.id,
                title=source.title,
                source_type=source.source_type.value,
                verified_date=source.verified_date,
                url=source.url,
            )
        )

    return refs


def _looks_like_eligibility_question(message: str) -> bool:
    """
    Identify whether the user is explicitly asking about eligibility.

    This is conversational triage only. It does not determine eligibility.
    """
    lowered = message.lower()

    triggers = [
        "eligib",
        "qualify",
        "can i expunge",
        "can i clear",
        "can my record be expunged",
        "can my record be cleared",
        "am i able",
        "do i qualify",
    ]

    return any(trigger in lowered for trigger in triggers)


def _build_assessment_context(assessment: dict) -> str:
    """Build tightly bounded context from the rules engine result."""
    return (
        "\n\n===== ASSESSMENT CONTEXT =====\n"
        "This information was produced by ClearPath's deterministic "
        "rules engine. Do not contradict or extend it.\n"
        f"- status: {assessment['status']}\n"
        f"- verified_rules_applied: {assessment['verified_rules_applied']}\n"
        f"- reasons: {assessment['reasons']}\n"
        f"- next_steps: {assessment['next_steps']}\n"
    )


def _build_user_context(
    request: ChatRequest,
    route: Route,
    knowledge_context: str,
    assessment_context: str = "",
) -> str:
    """Build the bounded context supplied to the language model."""
    return (
        f"===== ROUTE =====\n"
        f"question_type: {route.question_type}\n"
        f"pathway: {route.pathway}\n"
        f"intent: {route.intent}\n"
        f"source_categories: {route.source_categories}\n\n"
        f"===== USER MESSAGE =====\n"
        f"{request.message}\n"
        f"{assessment_context}\n"
        f"\n===== KNOWLEDGE CONTEXT =====\n"
        f"{knowledge_context}"
    )


async def process_message(
    request: ChatRequest,
    deepseek_client: Optional[DeepSeekClient] = None,
) -> ChatResponse:
    """Process one Path conversation turn."""
    client = deepseek_client or DeepSeekClient()

    route = route_message(request.message)

    logger.info(
        "chat message received (pathway=%s intent=%s question_type=%s): %s",
        route.pathway,
        route.intent,
        route.question_type,
        safe_for_logging(request.message),
    )

    knowledge = retrieve_knowledge(route)
    sources = _sources_from_ids(knowledge.source_ids)

    relief_type = _route_to_relief_type(route)

    next_action = "continue_conversation"
    requires_human = False
    confidence = 0.6
    assessment_context = ""

    # Only an explicitly identified eligibility question enters the
    # deterministic rules engine.
    if (
        route.question_type == "personal_justice"
        and relief_type is not None
        and _looks_like_eligibility_question(request.message)
    ):
        screening = ScreeningAnswers(relief_type=relief_type)

        result = await check_eligibility(screening)
        assessment = result["assessment"]

        assessment_context = _build_assessment_context(assessment)

        requires_human = bool(result["referral_needed"])
        next_action = (
            "refer_to_human"
            if requires_human
            else "ask_screening_questions"
        )
        confidence = (
            0.85
            if assessment["verified_rules_applied"]
            else 0.5
        )

        if requires_human:
            await create_referral(
                ReferralReason(result["referral_reason"]),
                description=request.message,
            )

    elif route.pathway == "unknown":
        next_action = "clarify_relief_type"
        confidence = 0.4

    elif route.intent == "application_prep":
        next_action = "prepare_application"

    elif route.intent == "tracking":
        next_action = "track_application"

    elif route.intent == "post_decision":
        next_action = "post_decision_support"

    elif route.question_type == "justice_research":
        next_action = "answer_research_question"

    else:
        next_action = "continue_conversation"

    user_context = _build_user_context(
        request,
        route,
        knowledge.context,
        assessment_context,
    )

    try:
        message_text = await client.generate_response(
            SYSTEM_PROMPT,
            user_context,
        )
    except DeepSeekError as exc:
        logger.error("DeepSeek call failed: %s", exc)

        requires_human = True
        next_action = "refer_to_human"
        confidence = 0.2

        message_text = (
            "I'm having trouble generating a full response right now. "
            "This question needs human follow-up, but ClearPath's current "
            "prototype does not yet send referrals automatically."
        )

        await create_referral(
            ReferralReason.TECHNICAL_FAILURE,
            description=request.message,
        )

    return ChatResponse(
        message=message_text,
        next_action=next_action,
        requires_human=requires_human,
        confidence=confidence,
        sources=sources,
        relief_type=relief_type,
    )
