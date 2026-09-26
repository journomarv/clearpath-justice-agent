"""
Public interface for the ClearPath rules engine.

The rules engine is deliberately conservative:
unverified relief types route to human review rather than producing
automated eligibility determinations.
"""

from app.rules.registry import (
    get_handler,
    is_supported,
    list_supported_relief_types,
    register,
)

# Import handler modules so their @register decorators execute.
from app.rules import cannabis_cppa as _cannabis_cppa  # noqa: F401,E402
from app.rules import criminal_record_expungement as _criminal_record_expungement  # noqa: F401,E402

from app.schemas.rules import (
    EligibilityAssessment,
    EligibilityStatus,
    ReliefType,
    ScreeningAnswers,
)


def assess_expungement_eligibility(
    answers: ScreeningAnswers,
) -> EligibilityAssessment:
    """
    Route an assessment to the registered handler.

    No handler means no automated determination.
    """
    relief_type = answers.relief_type or ReliefType.UNKNOWN

    handler = get_handler(relief_type)

    if handler is None:
        return EligibilityAssessment(
            relief_type=relief_type,
            status=EligibilityStatus.UNKNOWN,
            reasons=[
                "ClearPath does not currently have a verified rules handler "
                "for this relief type."
            ],
            next_steps=[
                "A human reviewer should assess the matter before any "
                "eligibility conclusion is given."
            ],
            requires_human_review=True,
            verified_rules_applied=False,
            source_ids=[],
        )

    return handler(answers)


def identify_referral_need(
    assessment: EligibilityAssessment,
) -> str | None:
    """
    Identify whether an assessment requires human review.

    This function never overrides an assessment or creates a legal
    determination.
    """
    if assessment.requires_human_review:
        return "UNCERTAIN_ELIGIBILITY"

    return None


__all__ = [
    "assess_expungement_eligibility",
    "get_handler",
    "identify_referral_need",
    "is_supported",
    "list_supported_relief_types",
    "register",
]
