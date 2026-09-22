"""
Rules module: general criminal-record expungement (not cannabis-specific).

Relief type: ReliefType.CRIMINAL_RECORD_EXPUNGEMENT
Relevant legislation (reference only, NOT yet encoded as logic below):
    Criminal Procedure Act 51 of 1977, Section 271B (as amended)
    Child Justice Act 75 of 2008, Section 87 (for records from childhood)

================================================================================
LEGAL VERIFICATION STATUS: NOT VERIFIED — PLACEHOLDER ONLY
================================================================================
Public DOJ material (see app/knowledge/sources.py, id
"doj_expungements_overview") describes general criteria in broad strokes —
e.g. a waiting period after conviction, limits on sentence type/value, and
exclusions for certain offence categories such as sexual offences against
children. This module deliberately does NOT translate that page into
automated logic. Two reasons:

  1. Public guidance pages are simplified and can lag behind the current
     regulations or omit exceptions that matter for a real case.
  2. ClearPath has not assigned a legal reviewer to confirm current wording,
     confirm which fields the agent may safely collect to test each
     criterion, and confirm how edge cases (e.g. multiple convictions,
     partially-served sentences, expunged-then-reinstated records) should
     be handled.

DO NOT add specific thresholds to this file without a section citation and
ClearPath legal sign-off (see app/rules/cannabis_cppa.py for the required
format). Until then, every assessment routes to human review.

TODO(legal-verification, ClearPath legal team):
  - Confirm current waiting-period and sentence-value thresholds under
    s271B (they are subject to amendment).
  - Confirm the full disqualification list (e.g. sexual offences register
    entries, offences against children).
  - Confirm whether/how Child Justice Act s87 cases should be routed
    differently (different form, different requesting authority).
  - Confirm the current required-document list and where to source the
    latest application form.
================================================================================
"""
from app.rules.registry import register
from app.schemas.rules import (
    EligibilityAssessment,
    EligibilityStatus,
    ReliefType,
    ScreeningAnswers,
)

_SOURCE_IDS = ["cpa_1977_s271b", "doj_expungements_overview", "child_justice_act_s87"]


@register(ReliefType.CRIMINAL_RECORD_EXPUNGEMENT)
def assess_general_criminal_record_expungement(
    answers: ScreeningAnswers,
) -> EligibilityAssessment:
    """
    Placeholder assessment for general (non-cannabis) criminal-record
    expungement under the Criminal Procedure Act / Child Justice Act.

    Always routes to human review until verified criteria are added.
    """
    return EligibilityAssessment(
        relief_type=ReliefType.CRIMINAL_RECORD_EXPUNGEMENT,
        status=EligibilityStatus.REQUIRES_HUMAN_REVIEW,
        reasons=[
            "Verified eligibility criteria for general criminal-record "
            "expungement have not yet been implemented in ClearPath's "
            "rules engine.",
            "Public guidance exists (see cited sources) but has not been "
            "legally verified for use in automated decisioning.",
        ],
        next_steps=[
            "A ClearPath team member or partner organisation will review "
            "your situation and advise on next steps.",
            "You can start by requesting a police clearance certificate "
            "from the SAPS Criminal Record Centre, which this process is "
            "very likely to require regardless of the final assessment.",
        ],
        documents_required=[
            "TODO(legal-verification): confirm the current official "
            "application form (Form A / J744, or the Child Justice Act "
            "Form 13, as applicable) and required attachments before "
            "surfacing this to users as authoritative.",
        ],
        requires_human_review=True,
        verified_rules_applied=False,
        source_ids=_SOURCE_IDS,
    )
