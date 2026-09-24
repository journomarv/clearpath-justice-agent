"""Regression tests for matter and intent routing."""

from app.services.knowledge import KnowledgeService


def test_cannabis_documents_routes_to_matter_and_prep():
    service = KnowledgeService()
    message = "I was convicted of cannabis possession. What documents do I need?"
    assert service.identify_pathway(message) == "cannabis_related_relief"
    assert service.identify_intent(message) == "application_prep"


def test_cannabis_waiting_routes_to_matter_and_tracking():
    service = KnowledgeService()
    message = (
        "My cannabis conviction was in 2011. "
        "How long will the Department of Justice take to process my expungement?"
    )
    assert service.identify_pathway(message) == "cannabis_related_relief"
    assert service.identify_intent(message) == "tracking"


def test_theft_documents_routes_to_general_expungement_and_prep():
    service = KnowledgeService()
    message = "I have a theft conviction. What documents do I need to expunge it?"
    assert service.identify_pathway(message) == "general_expungement"
    assert service.identify_intent(message) == "application_prep"


def test_theft_waiting_routes_to_general_expungement_and_tracking():
    service = KnowledgeService()
    message = "I have a theft conviction. How long will my expungement application take?"
    assert service.identify_pathway(message) == "general_expungement"
    assert service.identify_intent(message) == "tracking"


def test_refused_application_routes_to_post_decision():
    service = KnowledgeService()
    message = "My cannabis application was refused. What happens next?"
    assert service.identify_pathway(message) == "cannabis_related_relief"
    assert service.identify_intent(message) == "post_decision"


def test_child_documents_routes_to_child_justice_and_prep():
    service = KnowledgeService()
    message = "I was convicted as a child. What documents do I need?"
    assert service.identify_pathway(message) == "child_justice"
    assert service.identify_intent(message) == "application_prep"
