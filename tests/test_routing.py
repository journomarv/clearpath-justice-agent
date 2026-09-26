"""Regression tests for ClearPath conversational routing."""

from app.knowledge.routing import route_message


def test_cannabis_documents_routes_to_matter_and_prep():
    route = route_message(
        "I was convicted of cannabis possession. What documents do I need?"
    )
    assert route.question_type == "personal_justice"
    assert route.pathway == "cannabis_related_relief"
    assert route.intent == "application_prep"


def test_cannabis_waiting_routes_to_matter_and_tracking():
    route = route_message(
        "My cannabis conviction was in 2011. "
        "How long will the Department of Justice take to process my expungement?"
    )
    assert route.question_type == "personal_justice"
    assert route.pathway == "cannabis_related_relief"
    assert route.intent == "tracking"


def test_theft_documents_routes_to_general_expungement_and_prep():
    route = route_message(
        "I have a theft conviction. What documents do I need to expunge it?"
    )
    assert route.question_type == "personal_justice"
    assert route.pathway == "general_expungement"
    assert route.intent == "application_prep"


def test_theft_waiting_routes_to_general_expungement_and_tracking():
    route = route_message(
        "I have a theft conviction. How long will my expungement application take?"
    )
    assert route.question_type == "personal_justice"
    assert route.pathway == "general_expungement"
    assert route.intent == "tracking"


def test_refused_application_routes_to_post_decision():
    route = route_message(
        "My cannabis application was refused. What happens next?"
    )
    assert route.question_type == "personal_justice"
    assert route.pathway == "cannabis_related_relief"
    assert route.intent == "post_decision"


def test_child_documents_routes_to_child_justice_and_prep():
    route = route_message(
        "I was convicted as a child. What documents do I need?"
    )
    assert route.question_type == "personal_justice"
    assert route.pathway == "child_justice"
    assert route.intent == "application_prep"


def test_police_clearance_is_a_pathway_not_post_decision():
    route = route_message("I need a police clearance certificate.")
    assert route.pathway == "police_clearance"
    assert route.intent == "eligibility"


def test_parliament_question_routes_to_research_source():
    route = route_message("What has Parliament said about expungement?")
    assert route.question_type == "justice_research"
    assert route.pathway == "general_expungement"
    assert route.source_categories == ["parliament"]
