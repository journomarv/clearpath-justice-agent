"""
Agent orchestrator.

Flow (see ARCHITECTURE_GUIDE.md for the full diagram):
  1. Detect a relief-type hint from the message (simple keyword routing —
     NOT a legal determination, just conversational triage).
  2. Gather relevant knowledge-base context.
  3. If the message looks like an eligibility question, run the rules
     engine (via app.tools.eligibility) to get a structured assessment.
  4. Build a constrained system prompt and call DeepSeek for the
     natural-language reply.
  5. Determine next_action / requires_human / confidence for the caller.

The LLM never decides eligibility. It explains what the rules engine (or
the "not yet supported" fallback) already decided.
"""
import logging
from typing import List, Optional

from app.deepseek import DeepSeekClient, DeepSeekError
from app.knowledge import list_knowledge_for_relief_type
from app.privacy import safe_for_logging
from app.schemas.agent import ChatRequest, ChatResponse, SourceRef
from app.schemas.rules import ReliefType, ScreeningAnswers
from app.tools.eligibility import check_eligibility
from app.tools.referrals import ReferralReason, create_referral

logger = logging.getLogger("clearpath.agent")

SYSTEM_PROMPT = """You are the ClearPath Justice Agent, an assistant that helps people in \
South Africa understand criminal-record relief and expungement processes.

Core rule, never break it: AI assists; it does not adjudicate.
- You do NOT decide whether someone is legally eligible for expungement. \
That decision comes only from ClearPath's verified rules engine, whose \
result is given to you below as ASSESSMENT CONTEXT. Explain it faithfully; \
never contradict, soften, or go beyond it.
- You do NOT invent South African legal criteria, deadlines, fees, forms, \
or procedures. If information is not present in the KNOWLEDGE CONTEXT \
below, say plainly that it is not yet available and that a human follow-up \
is coming, rather than guessing.
- You do NOT ask for ID numbers, full case numbers, or other sensitive \
identifiers in chat.
- Keep responses clear, warm, and in plain language. Avoid legal jargon \
where possible, and avoid sounding like a form letter.
- If the user seems distressed or describes a vulnerable situation, \
acknowledge that gently and note that a human will follow up.
"""

# Very small, intentionally conservative keyword router. This is NOT a
# legal test of anything -- it only decides which relief type's
# information to look up, defaulting to "ask" when unsure.
_CANNABIS_KEYWORDS = ["cannabis", "dagga", "marijuana", "weed", "cppa"]
_GENERAL_KEYWORDS = [
    "criminal record",
    "expunge",
    "expungement",
    "conviction",
    "clear my record",
    "police clearance",
]


def detect_relief_type_hint(message: str) -> Optional[ReliefType]:
    """Best-effort, non-legal routing hint from free text."""
    lowered = message.lower()
    if any(kw in lowered for kw in _CANNABIS_KEYWORDS):
        return ReliefType.CANNABIS_EXPUNGEMENT
    if any(kw in lowered for kw in _GENERAL_KEYWORDS):
        return ReliefType.CRIMINAL_RECORD_EXPUNGEMENT
    return None


def _looks_like_eligibility_question(message: str) -> bool:
    lowered = message.lower()
    triggers = ["eligib", "qualify", "can i expunge", "am i able", "do i qualify"]
    return any(t in lowered for t in triggers)


def _sources_for(relief_type: ReliefType) -> List[SourceRef]:
    from app.knowledge.sources import get_source

    refs: List[SourceRef] = []
    for item in list_knowledge_for_relief_type(relief_type):
        for source_id in item["source_ids"]:
            source = get_source(source_id)
            if source and source.id not in {r.id for r in refs}:
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


async def process_message(
    request: ChatRequest, deepseek_client: Optional[DeepSeekClient] = None
) -> ChatResponse:
    """Process one chat message end-to-end and return a structured response."""
    client = deepseek_client or DeepSeekClient()

    relief_type = request.relief_type_hint or detect_relief_type_hint(request.message)
    logger.info(
        "chat message received (relief_type=%s): %s",
        relief_type.value if relief_type else None,
        safe_for_logging(request.message),
    )

    assessment_context = ""
    next_action = "continue_conversation"
    requires_human = False
    confidence = 0.6
    sources: List[SourceRef] = []

    if relief_type is not None:
        sources = _sources_for(relief_type)

        if _looks_like_eligibility_question(request.message):
            screening = ScreeningAnswers(relief_type=relief_type)
            result = await check_eligibility(screening)
            assessment = result["assessment"]
            assessment_context = (
                f"\n\nASSESSMENT CONTEXT (from ClearPath's rules engine, "
                f"authoritative — do not contradict):\n"
                f"- status: {assessment['status']}\n"
                f"- verified_rules_applied: {assessment['verified_rules_applied']}\n"
                f"- reasons: {assessment['reasons']}\n"
                f"- next_steps: {assessment['next_steps']}\n"
            )
            requires_human = bool(result["referral_needed"])
            next_action = "refer_to_human" if requires_human else "ask_screening_questions"
            confidence = 0.85 if assessment["verified_rules_applied"] else 0.5

            if requires_human:
                await create_referral(
                    ReferralReason(result["referral_reason"]),
                    description=request.message,
                )
        else:
            next_action = "ask_screening_questions"
    else:
        next_action = "clarify_relief_type"
        confidence = 0.4

    knowledge_context = ""
    if relief_type is not None:
        items = list_knowledge_for_relief_type(relief_type)
        if items:
            knowledge_context = "\n\nKNOWLEDGE CONTEXT (cite faithfully, do not extend beyond it):\n" + "\n".join(
                f"- {item['title']}: {item['content']}" for item in items
            )

    user_context = (
        f"User message: {request.message}"
        f"{assessment_context}"
        f"{knowledge_context}"
    )

    try:
        message_text = await client.generate_response(SYSTEM_PROMPT, user_context)
    except DeepSeekError as exc:
        logger.error("DeepSeek call failed: %s", exc)
        requires_human = True
        next_action = "refer_to_human"
        confidence = 0.2
        message_text = (
            "I'm having trouble generating a full response right now. "
            "I've flagged this for a ClearPath team member to follow up "
            "with you directly."
        )
        await create_referral(ReferralReason.TECHNICAL_FAILURE, description=request.message)

    return ChatResponse(
        message=message_text,
        next_action=next_action,
        requires_human=requires_human,
        confidence=confidence,
        sources=sources,
        relief_type=relief_type,
    )
