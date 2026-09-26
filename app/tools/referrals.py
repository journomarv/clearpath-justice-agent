"""
Referral tool for matters requiring human review.

ClearPath does not currently persist or deliver referrals. This module
therefore creates a privacy-minimised referral object and returns a
truthful user-facing message. Future persistence or WhatsApp/Paige
handoff can be added without changing the referral object contract.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict

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
    Return verified referral-organisation information.

    The current knowledge base contains a placeholder until ClearPath
    establishes verified referral partners.
    """
    sources = get_sources_for_item("referral_organizations")

    return {
        "organizations": [],
        "sources": [source.model_dump(mode="json") for source in sources],
    }


def create_referral_object(
    reason: ReferralReason,
    description: str,
    contacts: Dict[str, Any],
) -> Dict[str, Any]:
    """Create a privacy-minimised referral object."""
    return {
        "reason": reason.value,
        "description": safe_for_logging(description),
        "contacts": contacts,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


async def create_referral(
    reason: ReferralReason,
    description: str,
) -> Dict[str, Any]:
    """
    Create a referral object for future human handoff.

    No persistence or delivery occurs yet. The caller must not tell the
    user that a human has been contacted or that a referral was submitted.
    """
    contacts = get_referral_contacts()
    referral = create_referral_object(
        reason,
        description,
        contacts,
    )

    return {
        "referral": referral,
        "message": (
            "This question needs human follow-up. ClearPath has prepared "
            "a privacy-minimised referral record, but it has not yet been "
            "sent to a human or partner organisation."
        ),
    }
