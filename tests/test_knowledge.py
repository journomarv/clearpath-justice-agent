"""Tests for the knowledge base structure and source registry."""
from app.knowledge import KNOWLEDGE_STRUCTURE, list_knowledge_for_relief_type
from app.knowledge.sources import SOURCE_REGISTRY, list_unverified_sources
from app.schemas.rules import ReliefType


def test_every_knowledge_item_cites_at_least_one_source():
    for item in KNOWLEDGE_STRUCTURE.values():
        assert item["source_ids"], f"{item['id']} has no source_ids"


def test_every_cited_source_id_exists_in_registry():
    for item in KNOWLEDGE_STRUCTURE.values():
        for source_id in item["source_ids"]:
            assert source_id in SOURCE_REGISTRY, f"missing source: {source_id}"


def test_cannabis_relief_type_has_knowledge_items():
    items = list_knowledge_for_relief_type(ReliefType.CANNABIS_EXPUNGEMENT)
    assert len(items) > 0


def test_general_relief_type_has_knowledge_items():
    items = list_knowledge_for_relief_type(ReliefType.CRIMINAL_RECORD_EXPUNGEMENT)
    assert len(items) > 0


def test_no_source_is_falsely_marked_verified_for_automation_yet():
    # v0.2 ships with zero sources cleared for automated eligibility logic.
    # This test should be updated (not deleted) once ClearPath legal signs
    # off on a specific source -- see app/knowledge/README.md.
    unverified = list_unverified_sources()
    assert len(unverified) == len(SOURCE_REGISTRY)
