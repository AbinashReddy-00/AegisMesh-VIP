"""
AegisMesh — Unit Test Suite for End-to-End Scenarios
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.models.enums import Decision

client = TestClient(app)


def test_e2e_01_baseline_scenario_endpoint():
    res = client.post("/api/v1/simulate", json={"scenario_id": "PT-01"})
    assert res.status_code == 200
    data = res.json()
    assert data["evaluation"]["decision"] == Decision.ALLOW
    assert data["evaluation"]["risk_score"] <= 30
    assert len(data["packet_trace"]) > 0



def test_e2e_02_database_bypass_scenario_endpoint():
    res = client.post("/api/v1/simulate", json={"scenario_id": "E-04"})
    assert res.status_code == 200
    data = res.json()
    assert data["evaluation"]["decision"] == Decision.BLOCK
    assert data["evaluation"]["risk_score"] >= 70
    assert "FACULTY-ACCESS" in data["evaluation"]["enforcement_layer"]


def test_e2e_03_lateral_movement_containment_scenario_endpoint():
    res = client.post("/api/v1/simulate", json={"scenario_id": "I-01"})
    assert res.status_code == 200
    data = res.json()
    assert data["evaluation"]["decision"] == Decision.ISOLATE
    assert data["evaluation"]["risk_score"] >= 80
    assert data["containment_triggered"] is True


def test_e2e_04_recovery_scenario_endpoint():
    # Trigger restore
    res = client.post("/api/v1/containment/release", params={"workload_id": "k8s-edu-api"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["state"] == "NORMAL"


def test_e2e_05_audit_ledger_endpoint():
    res = client.get("/api/v1/audit")
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) >= 4
    decisions = [l["decision"] for l in logs]
    assert "ALLOW" in decisions
    assert "BLOCK" in decisions
