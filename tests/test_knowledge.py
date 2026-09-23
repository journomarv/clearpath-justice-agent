from app.services.knowledge import KnowledgeService


def test_general_expungement_pathway():
    service = KnowledgeService()

    result = service.identify_pathway(
        "I want to understand expungement of my criminal record"
    )

    assert result == "general_expungement"


def test_parliament_source_detection():
    service = KnowledgeService()

    result = service.identify_source_categories(
        "What has Parliament said about expungement?"
    )

    assert "parliament" in result


def test_saflii_source_detection():
    service = KnowledgeService()

    result = service.identify_source_categories(
        "Are there SAFLII judgments about criminal record expungement?"
    )

    assert "case_law" in result


def test_dataset_detection_is_not_triggered_by_generic_message():
    service = KnowledgeService()

    result = service.identify_source_categories(
        "I have a criminal record and need help"
    )

    assert "datasets" not in result


def test_research_detection():
    service = KnowledgeService()

    result = service.identify_source_categories(
        "Are there academic research papers about criminal records and employment?"
    )

    assert "academic" in result


def test_safeguards_are_available():
    service = KnowledgeService()

    documents = service.retrieve(
        "I want to understand expungement"
    )

    sources = [document["source"] for document in documents]

    assert "knowledge/safeguards/ai_principles.md" in sources
    assert "knowledge/safeguards/uncertainty.md" in sources


def test_legal_framework_fallback_exists_for_unknown_pathway():
    service = KnowledgeService()

    documents = service.retrieve(
        "Can you explain the justice process?"
    )

    sources = [document["source"] for document in documents]

    assert "knowledge/legal_framework/criminal_record_relief.md" in sources
