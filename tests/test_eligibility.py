"""
Tests for the rules engine. These tests intentionally assert that no
relief type produces a fabricated ELIGIBLE / NOT_ELIGIBLE determination
yet -- every path must route to human review with
verified_rules_applied=False until legal criteria are implemented.
"""
import pytest

from app.rules import assess_expungement_eligibility, identify_referral_need
from app.schemas.rules import EligibilityStatus, ReliefType, ScreeningAnswers


@pytest.mark.parametrize(
    "relief_type",
    [ReliefType.CANNABIS_EXPUNGEMENT, ReliefType.CRIMINAL_RECORD_EXPUNGEMENT],
)
def test_supported_relief_types_route_to_human_review(relief_type):
    answers = ScreeningAnswers(relief_type=relief_type)
    assessment = assess_expungement_eligibility(answers)

    assert assessment.relief_type == relief_type
    assert assessment.status == EligibilityStatus.REQUIRES_HUMAN_REVIEW
    assert assessment.requires_human_review is True
    assert assessment.verified_rules_applied is False
    assert assessment.reasons  # never an empty explanation
    assert assessment.source_ids  # always traceable to a source


def test_unset_relief_type_returns_unknown():
    answers = ScreeningAnswers()
    assessment = assess_expungement_eligibility(answers)

    assert assessment.relief_type == ReliefType.UNKNOWN
    assert assessment.status == EligibilityStatus.UNKNOWN
    assert assessment.requires_human_review is True


def test_unsupported_relief_type_does_not_crash():
    # Simulate a relief type with no handler by constructing the enum
    # value directly is not possible (ReliefType is closed), so instead
    # verify the UNKNOWN fallback path, which shares the same code path
    # as any future unregistered type.
    answers = ScreeningAnswers(relief_type=ReliefType.UNKNOWN)
    assessment = assess_expungement_eligibility(answers)
    assert assessment.verified_rules_applied is False


@pytest.mark.parametrize(
    "relief_type",
    [ReliefType.CANNABIS_EXPUNGEMENT, ReliefType.CRIMINAL_RECORD_EXPUNGEMENT],
)
def test_referral_is_identified_for_unverified_assessments(relief_type):
    answers = ScreeningAnswers(relief_type=relief_type)
    assessment = assess_expungement_eligibility(answers)
    reason = identify_referral_need(assessment)
    assert reason == "UNCERTAIN_ELIGIBILITY"
