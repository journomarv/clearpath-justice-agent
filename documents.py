"""
Documents tool: builds a checklist from the (currently placeholder)
requirements attached to an eligibility assessment, plus the knowledge
base's document-related items.
"""
from typing import Any, Dict, List

from app.knowledge import get_sources_for_item, list_knowledge_for_relief_type
from app.schemas.rules import EligibilityAssessment


def get_document_requirements(assessment: EligibilityAssessment) -> List[str]:
    """Return the documents_required list carried by an assessment."""
    return list(assessment.documents_required)


def format_checklist(requirements: List[str]) -> List[Dict[str, Any]]:
    """Turn a flat requirements list into a display-friendly checklist."""
    return [{"item": text, "checked": False} for text in requirements]


async def generate_document_checklist(assessment: EligibilityAssessment) -> Dict[str, Any]:
    """
    Called by the agent when a user asks what documents they need.

    Combines the assessment's own requirements with any relevant
    document-related knowledge-base items, so the checklist stays
    consistent even while the underlying rules content is still a
    placeholder.
    """
    requirements = get_document_requirements(assessment)
    knowledge_items = [
        item
        for item in list_knowledge_for_relief_type(assessment.relief_type)
        if item["id"] in ("document_checklist", "application_forms")
    ]
    sources = []
    for item in knowledge_items:
        sources.extend(s.model_dump(mode="json") for s in get_sources_for_item(item["id"]))

    return {
        "success": True,
        "checklist": format_checklist(requirements),
        "guidance": [item["content"] for item in knowledge_items],
        "sources": sources,
        "verified": assessment.verified_rules_applied,
    }
