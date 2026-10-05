def test_known_engine_returns_200(client):
    response = client.get("/engine/engine_1")
    assert response.status_code == 200
    data = response.json()
    assert data["engine_id"] == "engine_1"
    assert data["sensor_history"]
    assert {"cycle", "sensor_2", "sensor_3"} <= data["sensor_history"][0].keys()


def test_unknown_engine_returns_404(client):
    response = client.get("/engine/does_not_exist")
    assert response.status_code == 404
