"""
Eligibility tool: the only path the agent has to an eligibility result.

Wraps app.rules.eligibility so the agent never talks to the rules engine
directly — keeping a single, testable seam between "LLM decides to check
eligibility" and "deterministic rules engine computes the result".
"""
from typing import Any, Dict

from app.rules import assess_expungement_eligibility, identify_referral_need
from app.schemas.rules import ScreeningAnswers


async def check_eligibility(screening_answers: ScreeningAnswers) -> Dict[str, Any]:
    """
    Run an eligibility assessment and report whether a referral is needed.

    Returns a plain dict (not the pydantic model) so it can be dropped
    straight into an LLM context or an API response.
    """
    assessment = assess_expungement_eligibility(screening_answers)
    referral_reason = identify_referral_need(assessment)
    return {
        "status": assessment.status.value,
        "assessment": assessment.model_dump(mode="json"),
        "referral_needed": referral_reason is not None,
        "referral_reason": referral_reason,
    }
