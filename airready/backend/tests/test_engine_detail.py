from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_known_engine_returns_200():
    response = client.get("/engine/engine_1")
    assert response.status_code == 200
    data = response.json()
    assert data["engine_id"] == "engine_1"
    assert "sensor_history" in data


def test_unknown_engine_returns_404():
    response = client.get("/engine/does_not_exist")
    assert response.status_code == 404
