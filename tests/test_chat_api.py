"""API-level tests for the /chat contract."""

from unittest.mock import AsyncMock, patch

from app.schemas.agent import ChatResponse, SourceRef


def test_chat_response_contract(client):
    response_payload = ChatResponse(
        message="This question needs human review.",
        next_action="refer_to_human",
        requires_human=True,
        confidence=0.0,
        sources=[
            SourceRef(
                id="cppa_act_7_2024",
                title="Cannabis for Private Purposes Act 7 of 2024",
                source_type="official",
                verified_date=None,
                url=None,
            ),
            SourceRef(
                id="doj_expungements_overview",
                title="Department of Justice expungements overview",
                source_type="official",
                verified_date=None,
                url=None,
            ),
        ],
        relief_type="cannabis_expungement",
    )

    with patch(
        "app.main.process_message",
        new=AsyncMock(return_value=response_payload),
    ):
        response = client.post(
            "/chat",
            json={
                "message": "Am I eligible to expunge my cannabis conviction?"
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert set(data) == {
        "message",
        "next_action",
        "requires_human",
        "confidence",
        "sources",
        "relief_type",
    }

    assert data["message"]
    assert data["next_action"] == "refer_to_human"
    assert data["requires_human"] is True
    assert data["confidence"] == 0.0
    assert data["relief_type"] == "cannabis_expungement"

    assert len(data["sources"]) == 2

    source = data["sources"][0]

    assert set(source) == {
        "id",
        "title",
        "source_type",
        "verified_date",
        "url",
    }

    assert source["id"] == "cppa_act_7_2024"
    assert source["source_type"] == "official"
