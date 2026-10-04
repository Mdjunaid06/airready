from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_fleet_returns_200_and_correct_shape():
    response = client.get("/fleet")
    assert response.status_code == 200
    data = response.json()
    assert "fleet_availability_pct" in data
    assert "engines" in data
    assert isinstance(data["engines"], list)


def test_fleet_counts_sum_to_total():
    response = client.get("/fleet")
    data = response.json()
    assert (
        data["healthy_count"] + data["watch_count"] + data["urgent_count"]
        == data["total_engines"]
    )


def test_fleet_engine_statuses_are_valid():
    response = client.get("/fleet")
    data = response.json()
    valid_statuses = {"healthy", "watch", "urgent"}
    for engine in data["engines"]:
        assert engine["status"] in valid_statuses
