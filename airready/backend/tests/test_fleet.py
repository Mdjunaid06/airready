def test_fleet_returns_200_and_correct_shape(client):
    response = client.get("/fleet")
    assert response.status_code == 200
    data = response.json()
    assert "fleet_availability_pct" in data
    assert "engines" in data
    assert isinstance(data["engines"], list)


def test_fleet_counts_sum_to_total(client):
    response = client.get("/fleet")
    data = response.json()
    assert (
        data["healthy_count"] + data["watch_count"] + data["urgent_count"]
        == data["total_engines"]
    )


def test_fleet_engine_statuses_are_valid(client):
    response = client.get("/fleet")
    data = response.json()
    valid_statuses = {"healthy", "watch", "urgent"}
    for engine in data["engines"]:
        assert engine["status"] in valid_statuses


def test_alerts_returns_only_at_risk_engines(client):
    response = client.get("/alerts")
    assert response.status_code == 200
    alerts = response.json()["alerts"]
    assert all(alert["status"] in {"watch", "urgent"} for alert in alerts)
    assert [alert["predicted_rul_cycles"] for alert in alerts] == sorted(
        alert["predicted_rul_cycles"] for alert in alerts
    )


def test_spares_are_marked_illustrative(client):
    response = client.get("/spares")
    assert response.status_code == 200
    data = response.json()
    assert data["illustrative"] is True
    assert all({"part_id", "part_name", "stock_quantity", "lead_time_days"} <= part.keys()
               for part in data["parts"])


def test_comparison_uses_full_test_set(client):
    response = client.get("/comparison")
    assert response.status_code == 200
    data = response.json()
    assert set(data) == {
        "fixed_interval_missed_failures",
        "predictive_missed_failures",
        "fixed_interval_unnecessary_services",
        "predictive_unnecessary_services",
        "total_test_engines",
    }
    assert data["total_test_engines"] == 100
    assert data["fixed_interval_missed_failures"] == 39
    assert data["predictive_missed_failures"] == 2
    assert data["fixed_interval_unnecessary_services"] == 33
    assert data["predictive_unnecessary_services"] == 2
