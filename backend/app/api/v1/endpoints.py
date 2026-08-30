"""
AegisMesh — REST API v1 Endpoints
Traces to: docs/architecture/aegismesh-design.md Section 2 & 3
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from ...models.schemas import (
    TopologyResponse,
    EvaluateRequest,
    EvaluateResponse,
    SimulateRequest,
    SimulateResponse,
    IsolateRequest,
    PolicyRuleSchema,
    IncidentSchema,
    AuditLogSchema,
    WorkloadIdentifier,
    ResourceIdentifier,
    RequestContext,
)
from ...models.enums import ResourceType, SensitivityLevel, ActionType, Decision
from ...database.store import store
from ...decision_engine.engine import decision_engine
from ...containment.controller import containment_controller

router = APIRouter(prefix="/api/v1", tags=["AegisMesh v1"])


@router.get("/health")
def get_health():
    return {
        "status": "online",
        "service": "AegisMesh Security Decision Engine",
        "version": "1.0.0",
        "mode": "SIMULATION MODE (Demonstration Telemetry)",
        "domains_monitored": ["PRIVATE_DC", "AWS_CLOUD", "KUBERNETES"],
    }


@router.get("/topology", response_model=TopologyResponse)
def get_topology():
    return TopologyResponse(
        nodes=store.list_workloads(),
        edges=store.edges,
        mode="SIMULATION MODE (Demo Telemetry)",
        domains={
            "PRIVATE_DC": "Packet Tracer Architecture Model",
            "AWS_CLOUD": "Simulated Architecture Data",
            "KUBERNETES": "Simulated Architecture Data",
        },
    )


@router.post("/evaluate", response_model=EvaluateResponse)
def evaluate_access(request: EvaluateRequest):
    return decision_engine.evaluate_request(request)


@router.get("/scenarios")
def list_scenarios():
    return list(store.scenarios.values())


@router.post("/simulate", response_model=SimulateResponse)
def simulate_scenario(req: SimulateRequest):
    scenario = store.scenarios.get(req.scenario_id)
    if not scenario:
        raise HTTPException(
            status_code=404,
            detail=f"Scenario '{req.scenario_id}' not found. Valid IDs: {list(store.scenarios.keys())}",
        )

    src_node = store.get_workload(scenario["source_id"])
    dst_node = store.get_workload(scenario["dest_id"])

    if not src_node or not dst_node:
        raise HTTPException(status_code=400, detail="Scenario source or destination workload missing from topology.")

    src_ident = WorkloadIdentifier(
        workload_id=src_node.id,
        domain=src_node.domain,
        zone=src_node.zone,
        ip_address=src_node.ip_address,
    )

    dst_ident = ResourceIdentifier(
        resource_id=dst_node.id,
        resource_type=ResourceType.DATABASE if "DB" in dst_node.id else ResourceType.SERVICE,
        domain=dst_node.domain,
        zone=dst_node.zone,
        sensitivity=SensitivityLevel.RESTRICTED if dst_node.is_critical else SensitivityLevel.INTERNAL,
        ip_address=dst_node.ip_address,
    )

    context = RequestContext(
        source_zone=src_node.zone,
        is_anomaly=scenario["is_anomaly"],
        threat_id=scenario["threat_id"],
    )

    eval_req = EvaluateRequest(
        source=src_ident,
        destination=dst_ident,
        action=scenario["action"],
        context=context,
    )

    evaluation = decision_engine.evaluate_request(eval_req)

    # If decision is ISOLATE or scenario targets cross-domain containment, trigger containment automatically
    containment_triggered = False
    containment_details = None
    if evaluation.decision == Decision.ISOLATE or scenario.get("threat_id") == "I-01":
        containment_triggered = True
        containment_details = containment_controller.isolate_workload(
            workload_id=src_node.id,
            reason=f"Automated Anomaly Defense triggered by Scenario {scenario['id']} (Threat: {scenario['threat_id']})",
            threat_id=scenario["threat_id"],
        )

    return SimulateResponse(
        scenario_id=scenario["id"],
        scenario_title=scenario["title"],
        canonical_threat_id=scenario["threat_id"],
        source=src_ident,
        destination=dst_ident,
        action=scenario["action"],
        evaluation=evaluation,
        containment_triggered=containment_triggered,
        containment_details=containment_details,
        packet_trace=scenario["packet_trace"],
        mode="SIMULATION MODE (Demonstration Telemetry)",
    )


@router.get("/kubernetes/status")
def get_kubernetes_status():
    from ...integrations.kubernetes_client import k8s_client
    return k8s_client.get_cluster_status()


@router.post("/containment/isolate")
@router.post("/isolate")
def isolate_workload(req: IsolateRequest):
    target_id = req.get_target_id()
    result = containment_controller.isolate_workload(
        workload_id=target_id,
        reason=req.reason,
        namespace=req.namespace,
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/containment/release")
@router.post("/containment/lift")
@router.post("/restore")
def restore_workload(workload_id: Optional[str] = None, workload: Optional[str] = None, namespace: Optional[str] = None):
    target_id = workload_id or workload
    if not target_id:
        raise HTTPException(status_code=400, detail="workload_id parameter required.")
    result = containment_controller.restore_workload(target_id, namespace=namespace)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/containment/status")
def get_containment_status():
    from ...integrations.kubernetes_client import k8s_client
    active_k8s = k8s_client.list_active_isolations()
    contained_workloads = [w for w in store.list_workloads() if w.state.value == "CONTAINED"]
    return {
        "total_contained": len(contained_workloads),
        "contained_workloads": [
            {
                "id": w.id,
                "name": w.name,
                "domain": w.domain.value,
                "zone": w.zone.value,
                "trust_score": w.trust_score,
            }
            for w in contained_workloads
        ],
        "active_k8s_dynamic_policies": active_k8s,
    }


@router.get("/policies", response_model=List[PolicyRuleSchema])
def list_policies():
    return store.policies


@router.get("/incidents", response_model=List[IncidentSchema])
def list_incidents():
    return store.incidents


@router.get("/audit", response_model=List[AuditLogSchema])
def list_audit_logs():
    return store.audit_logs

from ...integrations.siem_client import siem_client
from ...models.enums import RiskLevel


@router.get("/siem/status")
def get_siem_status():
    return siem_client.status()


@router.get("/siem/events")
def get_siem_events():
    return siem_client.list_events()


@router.post("/siem/export")
def export_siem_events():
    return {
        "format": "json",
        "events": siem_client.list_events(),
        "event_count": len(siem_client.list_events()),
    }
