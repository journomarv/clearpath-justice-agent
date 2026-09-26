def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "clearpath-justice-agent"
    assert "checks" in body
    assert set(body["checks"].keys()) == {"api", "configuration", "deepseek_available"}


def test_health_never_exposes_api_key(client):
    response = client.get("/health")
    assert "test-key-not-real" not in response.text
