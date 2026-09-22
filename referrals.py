"""
Referral tool: hands a case to a human when the agent shouldn't (or can't)
make a determination.

Referrals are the release valve for the whole "AI assists, does not
adjudicate" principle — anything uncertain, disputed, complex, or outside
the knowledge base ends up here rather than being guessed at.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from app.knowledge import get_sources_for_item
from app.privacy import safe_for_logging


class ReferralReason(str, Enum):
    UNCERTAIN_ELIGIBILITY = "UNCERTAIN_ELIGIBILITY"
    DISPUTED_RECORD = "DISPUTED_RECORD"
    COMPLEX_CIRCUMSTANCES = "COMPLEX_CIRCUMSTANCES"
    LEGAL_ADVICE_NEEDED = "LEGAL_ADVICE_NEEDED"
    VULNERABLE_USER = "VULNERABLE_USER"
    TECHNICAL_FAILURE = "TECHNICAL_FAILURE"
    OUTSIDE_KNOWLEDGE_BASE = "OUTSIDE_KNOWLEDGE_BASE"


def get_referral_contacts() -> Dict[str, Any]:
    """
    Return the current referral-organisation knowledge item (contacts are
    populated in app/knowledge, currently a TODO placeholder).
    """
    sources = get_sources_for_item("referral_organizations")
    return {
        "organizations": [],  # TODO(clearpath): populate from knowledge base
        "sources": [s.model_dump(mode="json") for s in sources],
    }


def create_referral_object(
    reason: ReferralReason, description: str, contacts: Dict[str, Any]
) -> Dict[str, Any]:
    return {
        "reason": reason.value,
        # Description is redacted before storage/transmission — see
        # app/privacy.py. ClearPath collects the minimum needed to route
        # a human follow-up, not a full case file, over this channel.
        "description": safe_for_logging(description),
        "contacts": contacts,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


async def create_referral(reason: ReferralReason, description: str) -> Dict[str, Any]:
    """
    Called by the agent when a matter requires human or legal review.

    Returns a referral object plus a user-facing message. Does not persist
    anywhere yet — v0.2 keeps this API-shaped so a database or a
    WhatsApp/Paige handoff can be wired in without changing this
    function's contract (see ARCHITECTURE_GUIDE.md, "Future Expansions").
    """
    contacts = get_referral_contacts()
    referral = create_referral_object(reason, description, contacts)
    return {
        "referral": referral,
        "message": (
            "Your question has been noted for follow-up by ClearPath's "
            "support team or a partner organisation. They'll be in touch "
            "about next steps."
        ),
    }
