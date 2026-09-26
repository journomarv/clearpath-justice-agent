"""
Relief-type registry: makes the rules engine modular.

Each relief type (cannabis expungement, general criminal-record
expungement, future types) registers a handler function here. The agent
and tools never import a specific relief-type module directly — they go
through this registry, so adding a new relief type never requires
touching the orchestration code in app/agent.py or app/tools/.

Handler contract:
    def handler(answers: ScreeningAnswers) -> EligibilityAssessment

Handlers MUST NOT invent or assume legal criteria. Until a relief type's
module is verified by ClearPath's legal team, its handler should return
EligibilityStatus.REQUIRES_HUMAN_REVIEW or UNKNOWN with
verified_rules_applied=False. See app/rules/cannabis_cppa.py and
app/rules/criminal_record_expungement.py for the current placeholders.
"""
from typing import Callable, Dict, List, Optional

from app.schemas.rules import EligibilityAssessment, ReliefType, ScreeningAnswers

HandlerFn = Callable[[ScreeningAnswers], EligibilityAssessment]

_REGISTRY: Dict[ReliefType, HandlerFn] = {}


def register(relief_type: ReliefType):
    """Decorator: register a handler function for a relief type."""

    def _decorator(fn: HandlerFn) -> HandlerFn:
        _REGISTRY[relief_type] = fn
        return fn

    return _decorator


def get_handler(relief_type: ReliefType) -> Optional[HandlerFn]:
    """Return the handler for a relief type, or None if unsupported."""
    return _REGISTRY.get(relief_type)


def list_supported_relief_types() -> List[ReliefType]:
    """Return all relief types that currently have a registered handler."""
    return list(_REGISTRY.keys())


def is_supported(relief_type: ReliefType) -> bool:
    return relief_type in _REGISTRY
