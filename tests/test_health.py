async def test_health_returns_200(client):
    response = await client.get("/health")
    assert response.status_code == 200


async def test_health_response_structure(client):
    response = await client.get("/health")
    data = response.json()
    assert "data" in data
    assert data["data"]["status"] == "ok"


async def test_not_found_returns_404(client):
    response = await client.get("/nonexistent-path-xyz")
    assert response.status_code == 404


async def test_health_database_field_present(client):
    response = await client.get("/health")
    data = response.json()
    assert "database" in data["data"]
