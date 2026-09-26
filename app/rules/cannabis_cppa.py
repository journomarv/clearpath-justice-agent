"""
Rules module: cannabis conviction expungement.

Relief type: ReliefType.CANNABIS_EXPUNGEMENT
Relevant legislation (reference only, NOT yet encoded as logic below):
    Cannabis for Private Purposes Act 7 of 2024 ("CPPA")

================================================================================
LEGAL VERIFICATION STATUS: NOT VERIFIED — PLACEHOLDER ONLY
================================================================================
This module intentionally does NOT implement eligibility criteria. ClearPath
has not yet provided legally verified rules for which cannabis-related
convictions qualify for expungement, what temporal/date cutoffs apply, what
counts as a disqualifying factor, or what documents are strictly required.

DO NOT add specific thresholds (dates, quantities, sentence lengths, etc.)
to this file without:
  1. A citation to the specific CPPA section.
  2. Sign-off from a ClearPath legal reviewer (name + date).
  3. A corresponding entry in app/knowledge/sources.py marked
     content_verified_for_automation=True.

Until then, every assessment routes to human review. This is the correct
and safe behaviour for v0.1 and v0.2 — see ARCHITECTURE_GUIDE.md, "Key
Principle: The Hierarchy".

TODO(legal-verification, ClearPath legal team):
  - Which offences/convictions qualify under the CPPA?
  - What is the relevant effective-date cutoff, if any?
  - Are there quantity or intent thresholds (private use vs. dealing)?
  - What disqualifies an applicant (e.g. unrelated serious convictions)?
  - What documents does DOJ/SAPS require for a CPPA-based application?
================================================================================
"""
from app.rules.registry import register
from app.schemas.rules import (
    EligibilityAssessment,
    EligibilityStatus,
    ReliefType,
    ScreeningAnswers,
)

# Knowledge source IDs (see app/knowledge/sources.py) that back this relief
# type. These are reference sources only — see status flags there.
_SOURCE_IDS = ["cppa_act_7_2024", "doj_expungements_overview"]


@register(ReliefType.CANNABIS_EXPUNGEMENT)
def assess_cannabis_expungement(answers: ScreeningAnswers) -> EligibilityAssessment:
    """
    Placeholder assessment for cannabis-conviction expungement.

    Always routes to human review until verified CPPA criteria are added.
    Never fabricates a determination.
    """
    return EligibilityAssessment(
        relief_type=ReliefType.CANNABIS_EXPUNGEMENT,
        status=EligibilityStatus.REQUIRES_HUMAN_REVIEW,
        reasons=[
            "Verified eligibility criteria for the Cannabis for Private "
            "Purposes Act 7 of 2024 have not yet been implemented in "
            "ClearPath's rules engine.",
            "ClearPath does not determine eligibility from unverified "
            "information; a human reviewer is needed for this case type "
            "until legal verification is complete.",
        ],
        next_steps=[
            "A ClearPath team member or partner organisation will review "
            "your situation and advise on next steps.",
            "In the meantime, you can request a police clearance "
            "certificate from the SAPS Criminal Record Centre, which most "
            "expungement routes will eventually require.",
        ],
        documents_required=[
            "TODO(legal-verification): confirm the exact document list "
            "for a CPPA-based application before surfacing this to users "
            "as authoritative.",
        ],
        requires_human_review=True,
        verified_rules_applied=False,
        source_ids=_SOURCE_IDS,
    )
