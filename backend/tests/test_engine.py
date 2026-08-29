"""
AegisMesh — Automated Test Suite
Traces to: docs/testing/testing-strategy.md
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database.store import store
from backend.app.models.enums import (
    Decision,
    RiskLevel,
    SecurityZone,
    InfrastructureDomain,
    WorkloadState,
    SensitivityLevel,
    ActionType,
    ResourceType,
)
from backend.app.models.schemas import (
    EvaluateRequest,
    WorkloadIdentifier,
    ResourceIdentifier,
    RequestContext,
)
from backend.app.policy_engine.engine import policy_engine
from backend.app.risk_engine.engine import risk_engine
from backend.app.decision_engine.engine import decision_engine
from backend.app.containment.controller import containment_controller

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "SIMULATION MODE" in data["mode"]


def test_topology_endpoint():
    response = client.get("/api/v1/topology")
    assert response.status_code == 200
    data = response.json()
    assert len(data["nodes"]) >= 10
    assert "PRIVATE_DC" in data["domains"]
    assert "AWS_CLOUD" in data["domains"]
    assert "KUBERNETES" in data["domains"]


def test_policy_engine_faculty_to_app_allow():
    req = EvaluateRequest(
        source=WorkloadIdentifier(
            workload_id="FAC-PC-01",
            domain=InfrastructureDomain.PRIVATE_DC,
            zone=SecurityZone.FACULTY,
            ip_address="10.10.10.100",
        ),
        destination=ResourceIdentifier(
            resource_id="APP-SRV-01",
            resource_type=ResourceType.SERVICE,
            domain=InfrastructureDomain.PRIVATE_DC,
            zone=SecurityZone.APP,
            sensitivity=SensitivityLevel.INTERNAL,
            ip_address="10.10.20.10",
        ),
        action=ActionType.CONNECT,
    )
    decision, policy_id, explanation = policy_engine.evaluate(req)
    assert decision == Decision.ALLOW
    assert policy_id == "POL-01"


def test_policy_engine_faculty_to_db_block():
    req = EvaluateRequest(
        source=WorkloadIdentifier(
            workload_id="FAC-PC-01",
            domain=InfrastructureDomain.PRIVATE_DC,
            zone=SecurityZone.FACULTY,
            ip_address="10.10.10.100",
        ),
        destination=ResourceIdentifier(
            resource_id="DB-SRV-01",
            resource_type=ResourceType.DATABASE,
            domain=InfrastructureDomain.PRIVATE_DC,
            zone=SecurityZone.DATABASE,
            sensitivity=SensitivityLevel.RESTRICTED,
            ip_address="10.10.40.10",
        ),
        action=ActionType.CONNECT,
    )
    decision, policy_id, explanation = policy_engine.evaluate(req)
    assert decision == Decision.BLOCK
    assert policy_id == "POL-02"


def test_risk_engine_computation():
    req = EvaluateRequest(
        source=WorkloadIdentifier(
            workload_id="FAC-PC-01",
            domain=InfrastructureDomain.PRIVATE_DC,
            zone=SecurityZone.FACULTY,
            ip_address="10.10.10.100",
        ),
        destination=ResourceIdentifier(
            resource_id="DB-SRV-01",
            resource_type=ResourceType.DATABASE,
            domain=InfrastructureDomain.PRIVATE_DC,
            zone=SecurityZone.DATABASE,
            sensitivity=SensitivityLevel.RESTRICTED,
            ip_address="10.10.40.10",
        ),
        action=ActionType.CONNECT,
        context=RequestContext(
            source_zone=SecurityZone.FACULTY,
            is_anomaly=True,
        ),
    )
    risk = risk_engine.compute_risk(req)
    assert 0 <= risk.score <= 100
    assert len(risk.factors) == 6
    assert risk.level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]


def test_decision_engine_evaluation():
    req = EvaluateRequest(
        source=WorkloadIdentifier(
            workload_id="FAC-PC-01",
            domain=InfrastructureDomain.PRIVATE_DC,
            zone=SecurityZone.FACULTY,
            ip_address="10.10.10.100",
        ),
        destination=ResourceIdentifier(
            resource_id="APP-SRV-01",
            resource_type=ResourceType.SERVICE,
            domain=InfrastructureDomain.PRIVATE_DC,
            zone=SecurityZone.APP,
            sensitivity=SensitivityLevel.INTERNAL,
            ip_address="10.10.20.10",
        ),
        action=ActionType.CONNECT,
    )
    eval_res = decision_engine.evaluate_request(req)
    assert eval_res.decision == Decision.ALLOW
    assert eval_res.risk_score <= 40
    assert "FACULTY-ACCESS" in eval_res.enforcement_layer


def test_containment_quarantine_and_restoration():
    workload_id = "k8s-edu-api"

    # 1. Isolate
    iso_res = containment_controller.isolate_workload(
        workload_id=workload_id,
        reason="Automated test anomaly trigger",
        threat_id="TEST-I-01",
    )
    assert iso_res["status"] == "success"
    assert iso_res["state"] == "CONTAINED"

    node = store.get_workload(workload_id)
    assert node.state == WorkloadState.CONTAINED

    # 2. Test policy override during containment
    req_unauth = EvaluateRequest(
        source=WorkloadIdentifier(
            workload_id=workload_id,
            domain=InfrastructureDomain.KUBERNETES,
            zone=SecurityZone.K8S_EDU,
        ),
        destination=ResourceIdentifier(
            resource_id="k8s-fin-db",
            resource_type=ResourceType.DATABASE,
            domain=InfrastructureDomain.KUBERNETES,
            zone=SecurityZone.K8S_FIN,
            sensitivity=SensitivityLevel.RESTRICTED,
        ),
        action=ActionType.CONNECT,
    )
    dec, pol_id, expl = policy_engine.evaluate(req_unauth)
    assert dec == Decision.BLOCK
    assert "CONTAINED" in expl

    # 3. Restore
    res_res = containment_controller.restore_workload(workload_id)
    assert res_res["status"] == "success"
    assert node.state == WorkloadState.NORMAL


def test_simulation_endpoint_scenarios():
    # Test Scenario E-04
    resp_e04 = client.post("/api/v1/simulate", json={"scenario_id": "E-04"})
    assert resp_e04.status_code == 200
    data_e04 = resp_e04.json()
    assert data_e04["evaluation"]["decision"] == "BLOCK"
    assert "FACULTY-ACCESS" in str(data_e04["packet_trace"])

    # Test Scenario I-01
    resp_i01 = client.post("/api/v1/simulate", json={"scenario_id": "I-01"})
    assert resp_i01.status_code == 200
    data_i01 = resp_i01.json()
    assert data_i01["containment_triggered"] is True
    assert data_i01["evaluation"]["decision"] == "ISOLATE"
