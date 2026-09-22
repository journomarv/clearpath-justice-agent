"""
Schemas for the rules engine: relief types, screening answers, and
eligibility assessments.

ClearPath is designed to be modular across relief types, not
cannabis-only. New relief types are added by:
  1. Adding a value to ReliefType below.
  2. Adding a handler module under app/rules/ (see app/rules/registry.py).
  3. Registering the handler in app/rules/__init__.py.

No relief type in this file implies any eligibility outcome. Outcomes are
computed by the modules in app/rules/, which route to
REQUIRES_HUMAN_REVIEW / UNKNOWN until ClearPath's legal team verifies and
supplies the actual criteria.
"""
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from app.privacy import contains_pii


class ReliefType(str, Enum):
    """Supported categories of criminal-record relief."""

    CANNABIS_EXPUNGEMENT = "cannabis_expungement"
    CRIMINAL_RECORD_EXPUNGEMENT = "criminal_record_expungement"
    UNKNOWN = "unknown"


class EligibilityStatus(str, Enum):
    """Possible outcomes of an eligibility assessment."""

    ELIGIBLE = "eligible"
    NOT_ELIGIBLE = "not_eligible"
    NEEDS_MORE_INFO = "needs_more_info"
    REQUIRES_HUMAN_REVIEW = "requires_human_review"
    UNKNOWN = "unknown"


class ScreeningAnswers(BaseModel):
    """
    Structured answers from the screening flow.

    Design principle: minimal collection. `answers` should hold only the
    small set of fields a given relief type's rules module actually needs
    (e.g. offence category, approximate conviction year, sentence type) —
    never full names, ID numbers, or case numbers unless a later, explicit
    step requires it for a human referral.
    """

    relief_type: Optional[ReliefType] = None
    answers: Dict[str, Any] = Field(default_factory=dict)
    free_text_context: Optional[str] = None

    @field_validator("free_text_context")
    @classmethod
    def _reject_identifiers_in_free_text(cls, value: Optional[str]) -> Optional[str]:
        if value and contains_pii(value):
            raise ValueError(
                "free_text_context appears to contain an ID or phone number. "
                "Please remove identifying numbers; ClearPath collects only "
                "what is needed to route your question."
            )
        return value


class EligibilityAssessment(BaseModel):
    """Structured output of a rules-engine eligibility check."""

    relief_type: ReliefType
    status: EligibilityStatus
    reasons: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    documents_required: List[str] = Field(default_factory=list)
    requires_human_review: bool = True
    # False until ClearPath legal verifies and implements real criteria for
    # this relief type. Always surface this to the caller so the agent and
    # any downstream UI can visibly flag "not yet a verified determination".
    verified_rules_applied: bool = False
    # IDs referencing entries in app/knowledge/sources.py
    source_ids: List[str] = Field(default_factory=list)
