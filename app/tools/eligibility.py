"""
Eligibility orchestration tool.

This module is deliberately thin. The actual assessment belongs to
app.rules. The LLM never determines eligibility.
"""

from typing import Any, Dict

from app.rules import assess_expungement_eligibility, identify_referral_need
from app.schemas.rules import ScreeningAnswers


async def check_eligibility(
    answers: ScreeningAnswers,
) -> Dict[str, Any]:
    """
    Run the deterministic ClearPath rules layer and return a serialisable
    assessment for the agent.
    """
    assessment = assess_expungement_eligibility(answers)

    referral_reason = identify_referral_need(assessment)

    return {
        "assessment": assessment.model_dump(),
        "referral_needed": assessment.requires_human_review,
        "referral_reason": referral_reason or "UNCERTAIN_ELIGIBILITY",
    }
