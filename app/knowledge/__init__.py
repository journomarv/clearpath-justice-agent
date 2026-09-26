"""
ClearPath knowledge layer.

Knowledge is deliberately separated from the rules engine.

A source can be useful for explanation and citation without being approved
for automated eligibility decisions.
"""

from typing import Any, Dict, List, Optional

from app.knowledge.sources import (
    SOURCE_REGISTRY,
    KnowledgeSource,
    SourceType,
)


# ---------------------------------------------------------------------------
# Knowledge items
# ---------------------------------------------------------------------------
#
# These are intentionally descriptive rather than legal determinations.
# The rules engine remains responsible for eligibility decisions.
#

KNOWLEDGE_STRUCTURE: Dict[str, Dict[str, Any]] = {
    "cannabis_expungement_overview": {
        "id": "cannabis_expungement_overview",
        "relief_type": "cannabis_expungement",
        "title": "Cannabis-related criminal-record relief",
        "content": (
            "ClearPath can provide general information about cannabis-related "
            "criminal-record relief and explain the available process. "
            "Eligibility is not automatically determined by Path until "
            "the relevant legal criteria have been verified and implemented."
        ),
        "source_ids": [
            source_id
            for source_id in (
                "cppa_act_7_2024",
                "doj_expungements_overview",
            )
            if source_id in SOURCE_REGISTRY
        ],
    },
    "general_expungement_overview": {
        "id": "general_expungement_overview",
        "relief_type": "criminal_record_expungement",
        "title": "General criminal-record expungement",
        "content": (
            "ClearPath can explain the general criminal-record expungement "
            "process using available official and research sources. "
            "Path does not make an automated eligibility determination "
            "until the applicable legal criteria have been verified."
        ),
        "source_ids": [
            source_id
            for source_id in (
                "cpa_1977_s271b",
                "doj_expungements_overview",
                "child_justice_act_s87",
            )
            if source_id in SOURCE_REGISTRY
        ],
    },
    "referral_organizations": {
        "id": "referral_organizations",
        "relief_type": "unknown",
        "title": "ClearPath referral organisations",
        "content": (
            "Referral contacts are maintained separately and will be "
            "populated as ClearPath establishes verified referral partners."
        ),
        "source_ids": [
            "clearpath_referrals"
        ] if "clearpath_referrals" in SOURCE_REGISTRY else [],
    },
}


def list_knowledge_for_relief_type(relief_type) -> List[Dict[str, Any]]:
    """Return knowledge items associated with a relief type."""
    value = getattr(relief_type, "value", relief_type)

    return [
        item
        for item in KNOWLEDGE_STRUCTURE.values()
        if item.get("relief_type") == value
    ]


def get_knowledge_item(item_id: str) -> Optional[Dict[str, Any]]:
    """Return one knowledge item by ID."""
    return KNOWLEDGE_STRUCTURE.get(item_id)


def get_source(source_id: str) -> Optional[KnowledgeSource]:
    """Return a registered source by ID."""
    return SOURCE_REGISTRY.get(source_id)


def get_sources_for_item(item_id: str) -> List[KnowledgeSource]:
    """Return registered sources cited by a knowledge item."""
    item = KNOWLEDGE_STRUCTURE.get(item_id)

    if not item:
        return []

    return [
        SOURCE_REGISTRY[source_id]
        for source_id in item.get("source_ids", [])
        if source_id in SOURCE_REGISTRY
    ]


def list_sources_for_relief_type(relief_type) -> List[KnowledgeSource]:
    """Return unique sources associated with a relief type."""
    sources: List[KnowledgeSource] = []
    seen = set()

    for item in list_knowledge_for_relief_type(relief_type):
        for source_id in item.get("source_ids", []):
            source = SOURCE_REGISTRY.get(source_id)

            if source and source.id not in seen:
                sources.append(source)
                seen.add(source.id)

    return sources


def list_unverified_sources() -> List[KnowledgeSource]:
    """
    Return sources not approved for automated eligibility decisions.
    """
    return [
        source
        for source in SOURCE_REGISTRY.values()
        if not source.content_verified_for_automation
    ]


__all__ = [
    "KNOWLEDGE_STRUCTURE",
    "KnowledgeSource",
    "SOURCE_REGISTRY",
    "SourceType",
    "get_knowledge_item",
    "get_source",
    "get_sources_for_item",
    "list_knowledge_for_relief_type",
    "list_sources_for_relief_type",
    "list_unverified_sources",
]
