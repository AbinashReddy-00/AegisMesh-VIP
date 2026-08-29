"""
AegisMesh — Pydantic Schemas
Traces to: docs/architecture/aegismesh-design.md Section 3, 4, 5, 7
"""
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .enums import (
    Decision,
    RiskLevel,
    SecurityZone,
    InfrastructureDomain,
    WorkloadState,
    SensitivityLevel,
    ActionType,
    ResourceType,
)


class WorkloadIdentifier(BaseModel):
    workload_id: str = Field(..., example="FAC-PC-01")
    domain: InfrastructureDomain = Field(..., example=InfrastructureDomain.PRIVATE_DC)
    zone: SecurityZone = Field(..., example=SecurityZone.FACULTY)
    namespace: Optional[str] = None
    vpc_id: Optional[str] = None
    vlan_id: Optional[int] = None
    ip_address: Optional[str] = None
    service_account: Optional[str] = None


class ResourceIdentifier(BaseModel):
    resource_id: str = Field(..., example="DB-SRV-01")
    resource_type: ResourceType = Field(..., example=ResourceType.DATABASE)
    domain: InfrastructureDomain = Field(..., example=InfrastructureDomain.PRIVATE_DC)
    zone: SecurityZone = Field(..., example=SecurityZone.DATABASE)
    sensitivity: SensitivityLevel = Field(..., example=SensitivityLevel.RESTRICTED)
    namespace: Optional[str] = None
    vpc_id: Optional[str] = None
    vlan_id: Optional[int] = None
    ip_address: Optional[str] = None


class RequestContext(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_zone: SecurityZone
    authentication_method: Optional[str] = "MFA_SESSION_TOKEN"
    session_id: Optional[str] = "sess-live-01"
    is_anomaly: Optional[bool] = False
    threat_id: Optional[str] = None


class EvaluateRequest(BaseModel):
    source: WorkloadIdentifier
    destination: ResourceIdentifier
    action: ActionType = ActionType.CONNECT
    context: Optional[RequestContext] = None


class RiskFactorDetail(BaseModel):
    name: str
    score: int  # 0–100
    weight: float  # e.g., 0.20
    weighted_score: float
    description: str


class RiskAssessment(BaseModel):
    score: int  # 0–100
    level: RiskLevel
    factors: List[RiskFactorDetail]
    explanation: str


class EvaluateResponse(BaseModel):
    request_id: str
    decision: Decision
    policy_decision: Decision
    risk_override: bool
    risk_score: int
    risk_level: RiskLevel
    policy_matched: Optional[str] = None
    explanation: str
    factors: List[RiskFactorDetail]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    audit_id: str
    enforcement_layer: str
    threat_id: Optional[str] = None


class WorkloadNode(BaseModel):
    id: str
    name: str
    domain: InfrastructureDomain
    zone: SecurityZone
    domain_label: str
    state: WorkloadState = WorkloadState.NORMAL
    trust_score: int = 100  # 0–100 (100 = full trust)
    ip_address: Optional[str] = None
    vlan_or_vpc_or_ns: str
    allowed_dependencies: List[str] = []
    is_critical: bool = False


class NetworkEdge(BaseModel):
    source: str
    target: str
    label: str
    is_allowed: bool = True
    threat_id: Optional[str] = None


class TopologyResponse(BaseModel):
    nodes: List[WorkloadNode]
    edges: List[NetworkEdge]
    mode: str = "SIMULATION MODE (Demo Telemetry)"
    domains: Dict[str, str] = {
        "PRIVATE_DC": "Packet Tracer Architecture Model",
        "AWS_CLOUD": "Simulated Architecture Data",
        "KUBERNETES": "Simulated Architecture Data",
    }


class PolicyRuleSchema(BaseModel):
    id: str
    name: str
    source_zone: Optional[SecurityZone] = None
    source_workload_id: Optional[str] = None
    destination_zone: Optional[SecurityZone] = None
    destination_resource_id: Optional[str] = None
    actions: List[ActionType]
    decision: Decision
    threat_mitigated: Optional[str] = None
    priority: int = 100


class IncidentSchema(BaseModel):
    id: str
    workload_id: str
    workload_name: str
    domain: InfrastructureDomain
    zone: SecurityZone
    threat_id: str
    title: str
    severity: RiskLevel
    status: str  # "ACTIVE", "CONTAINED", "RESOLVED"
    created_at: datetime
    updated_at: datetime
    containment_actions: List[str]
    timeline: List[Dict[str, Any]]


class AuditLogSchema(BaseModel):
    id: str
    timestamp: datetime
    actor: str
    source_ip: Optional[str] = None
    target: str
    action: str
    decision: Decision
    risk_score: int
    threat_id: Optional[str] = None
    details: str


class SimulateRequest(BaseModel):
    scenario_id: str = Field(..., example="E-04")
    parameters: Optional[Dict[str, Any]] = None


class SimulateResponse(BaseModel):
    scenario_id: str
    scenario_title: str
    canonical_threat_id: str
    source: WorkloadIdentifier
    destination: ResourceIdentifier
    action: ActionType
    evaluation: EvaluateResponse
    containment_triggered: bool
    containment_details: Optional[Dict[str, Any]] = None
    packet_trace: List[str]
    mode: str = "SIMULATION MODE"


class IsolateRequest(BaseModel):
    workload_id: str
    reason: str = "Automated Anomaly Threshold Exceeded (Risk > 80)"
