"""
AegisMesh — Unit Tests for Kubernetes Integration Bridge
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.app.main import app
from backend.app.integrations.kubernetes_client import KubernetesClient, Tuple_Result
from backend.app.models.enums import WorkloadState

client = TestClient(app)


def test_kubernetes_status_endpoint():
    response = client.get("/api/v1/kubernetes/status")
    assert response.status_code == 200
    data = response.json()
    assert "available" in data
    assert "connected" in data
    assert "cni" in data
    assert "namespaces" in data


def test_resolve_workload_target():
    k8s = KubernetesClient()
    edu_target = k8s.resolve_workload_target("education-app")
    assert edu_target["namespace"] == "education"
    assert edu_target["app_label"] == "education-app"

    fin_target = k8s.resolve_workload_target("finance-db")
    assert fin_target["namespace"] == "finance"
    assert fin_target["app_label"] == "finance-db"


def test_apply_isolation_mocked():
    k8s = KubernetesClient()
    with patch.object(k8s, "_run_kubectl", return_value=Tuple_Result(0, "networkpolicy.networking.k8s.io/aegismesh-isolate-education-app created", "")):
        result = k8s.apply_isolation(
            workload_id="education-app",
            reason="Test lateral movement detected",
            namespace="education",
        )
        assert result["success"] is True
        assert result["enforcement"] == "REAL_KUBERNETES_NETWORKPOLICY"
        assert result["policy_name"] == "aegismesh-isolate-education-app"
        assert result["status"] == "CONTAINED"


def test_release_isolation_mocked():
    k8s = KubernetesClient()
    with patch.object(k8s, "_run_kubectl", return_value=Tuple_Result(0, "networkpolicy.networking.k8s.io \"aegismesh-isolate-education-app\" deleted", "")):
        result = k8s.release_isolation(
            workload_id="education-app",
            namespace="education",
        )
        assert result["success"] is True
        assert result["enforcement"] == "REAL_KUBERNETES_NETWORKPOLICY"
        assert result["status"] == "RELEASED"


def test_api_containment_isolate_and_release_flow():
    # 1. Isolate
    iso_res = client.post(
        "/api/v1/containment/isolate",
        json={"workload": "education-app", "namespace": "education", "reason": "Test Anomaly Probe"},
    )
    assert iso_res.status_code == 200
    iso_data = iso_res.json()
    assert iso_data["status"] == "success"
    assert iso_data["state"] == "CONTAINED"

    # 2. Check Containment Status
    status_res = client.get("/api/v1/containment/status")
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["total_contained"] >= 1

    # 3. Release
    rel_res = client.post(
        "/api/v1/containment/release",
        params={"workload_id": "education-app", "namespace": "education"},
    )
    assert rel_res.status_code == 200
    rel_data = rel_res.json()
    assert rel_data["status"] == "success"
    assert rel_data["state"] == "NORMAL"

