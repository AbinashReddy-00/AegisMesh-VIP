"""
AegisMesh — In-Memory Seeded Store
Traces to: docs/architecture/aegismesh-design.md Section 4 & 9
"""
from datetime import datetime, timezone
import uuid
from typing import Dict, List, Optional
from ..models.enums import (
    Decision,
    RiskLevel,
    SecurityZone,
    InfrastructureDomain,
    WorkloadState,
    SensitivityLevel,
    ActionType,
    ResourceType,
)
from ..models.schemas import (
    WorkloadNode,
    NetworkEdge,
    PolicyRuleSchema,
    IncidentSchema,
    AuditLogSchema,
    WorkloadIdentifier,
    ResourceIdentifier,
)


class InMemoryStore:
    def __init__(self):
        self.workloads: Dict[str, WorkloadNode] = {}
        self.edges: List[NetworkEdge] = []
        self.policies: List[PolicyRuleSchema] = []
        self.incidents: List[IncidentSchema] = []
        self.audit_logs: List[AuditLogSchema] = []
        self.scenarios: Dict[str, dict] = {}
        self._seed_data()

    def _seed_data(self):
        # 1. Private Datacenter Workloads (Packet Tracer Model)
        self.workloads["FAC-PC-01"] = WorkloadNode(
            id="FAC-PC-01",
            name="Faculty Workstation 01",
            domain=InfrastructureDomain.PRIVATE_DC,
            zone=SecurityZone.FACULTY,
            domain_label="Private DC (Packet Tracer Architecture Model)",
            state=WorkloadState.NORMAL,
            trust_score=90,
            ip_address="10.10.10.100",
            vlan_or_vpc_or_ns="VLAN 10 (FACULTY)",
            allowed_dependencies=["APP-SRV-01", "DMZ-SRV-01"],
        )
        self.workloads["APP-SRV-01"] = WorkloadNode(
            id="APP-SRV-01",
            name="Application Server 01",
            domain=InfrastructureDomain.PRIVATE_DC,
            zone=SecurityZone.APP,
            domain_label="Private DC (Packet Tracer Architecture Model)",
            state=WorkloadState.NORMAL,
            trust_score=85,
            ip_address="10.10.20.10",
            vlan_or_vpc_or_ns="VLAN 20 (APP-SERVERS)",
            allowed_dependencies=["DB-SRV-01", "FAC-PC-01"],
        )
        self.workloads["MGMT-SRV-01"] = WorkloadNode(
            id="MGMT-SRV-01",
            name="Management Server",
            domain=InfrastructureDomain.PRIVATE_DC,
            zone=SecurityZone.MANAGEMENT,
            domain_label="Private DC (Packet Tracer Architecture Model)",
            state=WorkloadState.NORMAL,
            trust_score=100,
            ip_address="10.10.30.10",
            vlan_or_vpc_or_ns="VLAN 30 (MANAGEMENT)",
            allowed_dependencies=["SW-CORE", "DB-SRV-01", "APP-SRV-01"],
            is_critical=True,
        )
        self.workloads["DB-SRV-01"] = WorkloadNode(
            id="DB-SRV-01",
            name="Enterprise Database 01",
            domain=InfrastructureDomain.PRIVATE_DC,
            zone=SecurityZone.DATABASE,
            domain_label="Private DC (Packet Tracer Architecture Model)",
            state=WorkloadState.NORMAL,
            trust_score=95,
            ip_address="10.10.40.10",
            vlan_or_vpc_or_ns="VLAN 40 (DATABASE)",
            allowed_dependencies=["APP-SRV-01", "MGMT-SRV-01"],
            is_critical=True,
        )
        self.workloads["SEC-SRV-01"] = WorkloadNode(
            id="SEC-SRV-01",
            name="Wazuh SIEM / Logging",
            domain=InfrastructureDomain.PRIVATE_DC,
            zone=SecurityZone.SECURITY,
            domain_label="Private DC (Packet Tracer Architecture Model)",
            state=WorkloadState.NORMAL,
            trust_score=100,
            ip_address="10.10.50.10",
            vlan_or_vpc_or_ns="VLAN 50 (SECURITY)",
            allowed_dependencies=["APP-SRV-01", "DB-SRV-01"],
            is_critical=True,
        )
        self.workloads["DMZ-SRV-01"] = WorkloadNode(
            id="DMZ-SRV-01",
            name="Public Web Proxy",
            domain=InfrastructureDomain.PRIVATE_DC,
            zone=SecurityZone.DMZ,
            domain_label="Private DC (Packet Tracer Architecture Model)",
            state=WorkloadState.NORMAL,
            trust_score=60,
            ip_address="10.10.60.10",
            vlan_or_vpc_or_ns="VLAN 60 (DMZ)",
            allowed_dependencies=["APP-SRV-01", "FAC-PC-01"],
        )

        # 2. AWS Cloud Workloads (Simulated Architecture Data)
        self.workloads["aws-edu-app"] = WorkloadNode(
            id="aws-edu-app",
            name="AWS Education App",
            domain=InfrastructureDomain.AWS_CLOUD,
            zone=SecurityZone.CLOUD_EDU,
            domain_label="AWS Cloud (Simulated Architecture Data)",
            state=WorkloadState.NORMAL,
            trust_score=80,
            ip_address="10.1.2.15",
            vlan_or_vpc_or_ns="VPC-A (Education)",
            allowed_dependencies=["aws-edu-db", "aws-sec-mgmt"],
        )
        self.workloads["aws-edu-db"] = WorkloadNode(
            id="aws-edu-db",
            name="AWS Education RDS",
            domain=InfrastructureDomain.AWS_CLOUD,
            zone=SecurityZone.CLOUD_EDU,
            domain_label="AWS Cloud (Simulated Architecture Data)",
            state=WorkloadState.NORMAL,
            trust_score=95,
            ip_address="10.1.3.20",
            vlan_or_vpc_or_ns="VPC-A (Education DB)",
            allowed_dependencies=["aws-edu-app"],
            is_critical=True,
        )
        self.workloads["aws-fin-app"] = WorkloadNode(
            id="aws-fin-app",
            name="AWS Finance App",
            domain=InfrastructureDomain.AWS_CLOUD,
            zone=SecurityZone.CLOUD_FIN,
            domain_label="AWS Cloud (Simulated Architecture Data)",
            state=WorkloadState.NORMAL,
            trust_score=90,
            ip_address="10.3.1.10",
            vlan_or_vpc_or_ns="VPC-C (Finance)",
            allowed_dependencies=["aws-fin-db", "aws-sec-mgmt"],
            is_critical=True,
        )
        self.workloads["aws-fin-db"] = WorkloadNode(
            id="aws-fin-db",
            name="AWS Finance RDS (Restricted)",
            domain=InfrastructureDomain.AWS_CLOUD,
            zone=SecurityZone.CLOUD_FIN,
            domain_label="AWS Cloud (Simulated Architecture Data)",
            state=WorkloadState.NORMAL,
            trust_score=100,
            ip_address="10.3.2.50",
            vlan_or_vpc_or_ns="VPC-C (Finance DB)",
            allowed_dependencies=["aws-fin-app"],
            is_critical=True,
        )
        self.workloads["aws-sec-mgmt"] = WorkloadNode(
            id="aws-sec-mgmt",
            name="AWS Security Control Host",
            domain=InfrastructureDomain.AWS_CLOUD,
            zone=SecurityZone.CLOUD_SEC,
            domain_label="AWS Cloud (Simulated Architecture Data)",
            state=WorkloadState.NORMAL,
            trust_score=100,
            ip_address="10.4.2.5",
            vlan_or_vpc_or_ns="VPC-D (Security/Mgmt)",
            allowed_dependencies=["aws-edu-app", "aws-fin-app"],
            is_critical=True,
        )

        # 3. Kubernetes Workloads (Simulated Architecture Data)
        self.workloads["k8s-edu-api"] = WorkloadNode(
            id="k8s-edu-api",
            name="k8s: education-api-pod",
            domain=InfrastructureDomain.KUBERNETES,
            zone=SecurityZone.K8S_EDU,
            domain_label="Kubernetes (Simulated Architecture Data)",
            state=WorkloadState.NORMAL,
            trust_score=80,
            ip_address="192.168.1.12",
            vlan_or_vpc_or_ns="namespace: education",
            allowed_dependencies=["k8s-edu-db", "k8s-aegismesh-engine"],
        )
        self.workloads["k8s-edu-db"] = WorkloadNode(
            id="k8s-edu-db",
            name="k8s: education-db-pod",
            domain=InfrastructureDomain.KUBERNETES,
            zone=SecurityZone.K8S_EDU,
            domain_label="Kubernetes (Simulated Architecture Data)",
            state=WorkloadState.NORMAL,
            trust_score=95,
            ip_address="192.168.1.50",
            vlan_or_vpc_or_ns="namespace: education",
            allowed_dependencies=["k8s-edu-api"],
            is_critical=True,
        )
        self.workloads["k8s-fin-api"] = WorkloadNode(
            id="k8s-fin-api",
            name="k8s: finance-api-pod",
            domain=InfrastructureDomain.KUBERNETES,
            zone=SecurityZone.K8S_FIN,
            domain_label="Kubernetes (Simulated Architecture Data)",
            state=WorkloadState.NORMAL,
            trust_score=90,
            ip_address="192.168.3.10",
            vlan_or_vpc_or_ns="namespace: finance",
            allowed_dependencies=["k8s-fin-db", "k8s-aegismesh-engine"],
            is_critical=True,
        )
        self.workloads["k8s-fin-db"] = WorkloadNode(
            id="k8s-fin-db",
            name="k8s: finance-db-pod",
            domain=InfrastructureDomain.KUBERNETES,
            zone=SecurityZone.K8S_FIN,
            domain_label="Kubernetes (Simulated Architecture Data)",
            state=WorkloadState.NORMAL,
            trust_score=100,
            ip_address="192.168.3.40",
            vlan_or_vpc_or_ns="namespace: finance",
            allowed_dependencies=["k8s-fin-api"],
            is_critical=True,
        )
        self.workloads["k8s-aegismesh-engine"] = WorkloadNode(
            id="k8s-aegismesh-engine",
            name="k8s: aegismesh-control-plane",
            domain=InfrastructureDomain.KUBERNETES,
            zone=SecurityZone.K8S_SYS,
            domain_label="Kubernetes (Simulated Architecture Data)",
            state=WorkloadState.NORMAL,
            trust_score=100,
            ip_address="192.168.99.10",
            vlan_or_vpc_or_ns="namespace: aegismesh-system",
            allowed_dependencies=["k8s-edu-api", "k8s-fin-api", "SEC-SRV-01"],
            is_critical=True,
        )

        # 4. Hybrid Network Edges
        self.edges = [
            NetworkEdge(source="FAC-PC-01", target="APP-SRV-01", label="FACULTY-ACCESS Line 1", is_allowed=True),
            NetworkEdge(source="FAC-PC-01", target="DB-SRV-01", label="FACULTY-ACCESS Line 4 (BLOCK)", is_allowed=False, threat_id="E-04"),
            NetworkEdge(source="APP-SRV-01", target="DB-SRV-01", label="APP-SERVER-ACCESS Line 1", is_allowed=True),
            NetworkEdge(source="APP-SRV-01", target="MGMT-SRV-01", label="APP-SERVER-ACCESS Line 5 (BLOCK)", is_allowed=False, threat_id="E-02"),
            NetworkEdge(source="DMZ-SRV-01", target="DB-SRV-01", label="DMZ-ACCESS Line 4 (BLOCK)", is_allowed=False, threat_id="ARCH-SCENARIO-02"),
            NetworkEdge(source="DB-SRV-01", target="FAC-PC-01", label="DB-ACCESS Line 4 (BLOCK)", is_allowed=False, threat_id="ARCH-SCENARIO-01"),
            NetworkEdge(source="aws-edu-app", target="aws-edu-db", label="edu-app-sg -> edu-db-sg", is_allowed=True),
            NetworkEdge(source="aws-edu-app", target="aws-fin-db", label="No Peering / Cross-VPC Deny", is_allowed=False, threat_id="I-01"),
            NetworkEdge(source="k8s-edu-api", target="k8s-edu-db", label="Intra-Namespace NetworkPolicy", is_allowed=True),
            NetworkEdge(source="k8s-edu-api", target="k8s-fin-db", label="Default-Deny Cross-Namespace", is_allowed=False, threat_id="I-01"),
            NetworkEdge(source="SEC-SRV-01", target="k8s-aegismesh-engine", label="IPsec VPN Telemetry Sync", is_allowed=True),
        ]

        # 5. Policies
        self.policies = [
            PolicyRuleSchema(
                id="POL-01",
                name="Private DC: Faculty to App Server (Permit HTTP/App)",
                source_zone=SecurityZone.FACULTY,
                destination_zone=SecurityZone.APP,
                actions=[ActionType.CONNECT, ActionType.READ, ActionType.WRITE],
                decision=Decision.ALLOW,
                threat_mitigated="Normal Academic Workflow",
                priority=10,
            ),
            PolicyRuleSchema(
                id="POL-02",
                name="Private DC: Block Direct Faculty Access to Database",
                source_zone=SecurityZone.FACULTY,
                destination_zone=SecurityZone.DATABASE,
                actions=[ActionType.CONNECT, ActionType.READ, ActionType.WRITE],
                decision=Decision.BLOCK,
                threat_mitigated="E-04 (Direct Database Access Bypass)",
                priority=20,
            ),
            PolicyRuleSchema(
                id="POL-03",
                name="Private DC: Block App Server Lateral Traversal to Management",
                source_zone=SecurityZone.APP,
                destination_zone=SecurityZone.MANAGEMENT,
                actions=[ActionType.CONNECT, ActionType.ADMIN, ActionType.EXECUTE],
                decision=Decision.BLOCK,
                threat_mitigated="E-02 (App Compromise Leading to Mgmt Pivot)",
                priority=25,
            ),
            PolicyRuleSchema(
                id="POL-04",
                name="Private DC: Block Database Reverse Pivot toward Users",
                source_zone=SecurityZone.DATABASE,
                destination_zone=SecurityZone.FACULTY,
                actions=[ActionType.CONNECT],
                decision=Decision.BLOCK,
                threat_mitigated="ARCH-SCENARIO-01 (DB Reverse Pivot)",
                priority=30,
            ),
            PolicyRuleSchema(
                id="POL-05",
                name="Cloud/K8s: Block Cross-Domain Education to Finance DB",
                source_zone=SecurityZone.K8S_EDU,
                destination_zone=SecurityZone.K8S_FIN,
                actions=[ActionType.CONNECT, ActionType.READ, ActionType.WRITE],
                decision=Decision.BLOCK,
                threat_mitigated="I-01 (Compromised App Accesses Finance DB)",
                priority=15,
            ),
            PolicyRuleSchema(
                id="POL-06",
                name="Default Zero-Trust Deny All",
                actions=[ActionType.CONNECT, ActionType.READ, ActionType.WRITE, ActionType.ADMIN, ActionType.EXECUTE],
                decision=Decision.BLOCK,
                threat_mitigated="SR-04 (Zero-Trust Default Deny)",
                priority=999,
            ),
        ]

        # 6. Initial Seed Incident & Audit Logs
        now = datetime.now(timezone.utc)
        self.incidents.append(
            IncidentSchema(
                id="INC-2026-001",
                workload_id="k8s-edu-api",
                workload_name="k8s: education-api-pod",
                domain=InfrastructureDomain.KUBERNETES,
                zone=SecurityZone.K8S_EDU,
                threat_id="I-01",
                title="Cross-Domain Data Exfiltration Probe Detected",
                severity=RiskLevel.CRITICAL,
                status="ACTIVE",
                created_at=now,
                updated_at=now,
                containment_actions=[
                    "Dynamic NetworkPolicy egress lockdown applied",
                    "Egress restricted to authorized dependency: k8s-edu-db",
                    "Security telemetry alert dispatched to Wazuh SIEM",
                ],
                timeline=[
                    {"time": now.isoformat(), "event": "Anomalous connection attempt from k8s-edu-api toward k8s-fin-db:5432"},
                    {"time": now.isoformat(), "event": "Risk Engine computed score 85 (CRITICAL)"},
                    {"time": now.isoformat(), "event": "AegisMesh Decision: ISOLATE WORKLOAD"},
                ],
            )
        )

        self.audit_logs.append(
            AuditLogSchema(
                id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
                timestamp=now,
                actor="FAC-PC-01 (10.10.10.100)",
                source_ip="10.10.10.100",
                target="APP-SRV-01 (10.10.20.10:80)",
                action="HTTP_CONNECT",
                decision=Decision.ALLOW,
                risk_score=15,
                threat_id="PT-01",
                details="Permitted by policy POL-01 and SVI ACL FACULTY-ACCESS.",
            )
        )
        self.audit_logs.append(
            AuditLogSchema(
                id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
                timestamp=now,
                actor="FAC-PC-01 (10.10.10.100)",
                source_ip="10.10.10.100",
                target="DB-SRV-01 (10.10.40.10:5432)",
                action="DB_CONNECT",
                decision=Decision.BLOCK,
                risk_score=85,
                threat_id="E-04",
                details="Blocked by policy POL-02 and SVI ACL FACULTY-ACCESS (Rule 4).",
            )
        )

        # 7. Canned Attack Scenarios
        self.scenarios = {
            "PT-01": {
                "id": "PT-01",
                "title": "Baseline Authorized Flow: Faculty -> App Server",
                "threat_id": "PT-01",
                "source_id": "FAC-PC-01",
                "dest_id": "APP-SRV-01",
                "action": ActionType.CONNECT,
                "is_anomaly": False,
                "expected_decision": Decision.ALLOW,
                "packet_trace": [
                    "FAC-PC-01 (10.10.10.100) -> SW-ACCESS-1 (Port Fa0/1, VLAN 10)",
                    "SW-ACCESS-1 -> SW-CORE via Trunk Gi0/1 (802.1Q tagged VLAN 10)",
                    "SW-CORE evaluates SVI Vlan10 ingress ACL: FACULTY-ACCESS (Rule 1 PERMIT)",
                    "SW-CORE routes packet to SVI Vlan20 -> APP-SRV-01 (10.10.20.10) [REPLY ALLOWED]",
                ],
            },
            "E-04": {
                "id": "E-04",
                "title": "Direct Database Access Bypass: Faculty -> Database Server",
                "threat_id": "E-04",
                "source_id": "FAC-PC-01",
                "dest_id": "DB-SRV-01",
                "action": ActionType.CONNECT,
                "is_anomaly": True,
                "expected_decision": Decision.BLOCK,
                "packet_trace": [
                    "FAC-PC-01 (10.10.10.100) attempts direct connection to DB-SRV-01 (10.10.40.10)",
                    "SW-CORE receives packet on SVI Vlan10 -> Evaluates FACULTY-ACCESS",
                    "FACULTY-ACCESS Line 4 matched: 'deny ip 10.10.10.0 0.0.0.255 10.10.40.0 0.0.0.255'",
                    "SW-CORE drops packet -> Request Timed Out (Hit Counter Incremented) [BLOCKED]",
                ],
            },
            "E-02": {
                "id": "E-02",
                "title": "Lateral Movement Pivot: Compromised App -> Management Server",
                "threat_id": "E-02",
                "source_id": "APP-SRV-01",
                "dest_id": "MGMT-SRV-01",
                "action": ActionType.ADMIN,
                "is_anomaly": True,
                "expected_decision": Decision.BLOCK,
                "packet_trace": [
                    "APP-SRV-01 (10.10.20.10) initiates SSH / Admin probe toward MGMT-SRV-01 (10.10.30.10)",
                    "SW-CORE receives packet on SVI Vlan20 -> Evaluates APP-SERVER-ACCESS",
                    "APP-SERVER-ACCESS Line 5 matched: 'deny ip 10.10.20.0 0.0.0.255 10.10.30.0 0.0.0.255'",
                    "SW-CORE drops packet -> Lateral pivot halted [BLOCKED]",
                ],
            },
            "ARCH-SCENARIO-01": {
                "id": "ARCH-SCENARIO-01",
                "title": "Database Reverse Pivot: Compromised DB -> Faculty PC",
                "threat_id": "ARCH-SCENARIO-01",
                "source_id": "DB-SRV-01",
                "dest_id": "FAC-PC-01",
                "action": ActionType.CONNECT,
                "is_anomaly": True,
                "expected_decision": Decision.BLOCK,
                "packet_trace": [
                    "DB-SRV-01 (10.10.40.10) initiates reverse connection toward FAC-PC-01 (10.10.10.100)",
                    "SW-CORE receives packet on SVI Vlan40 -> Evaluates DB-ACCESS",
                    "DB-ACCESS Line 4 matched: 'deny ip 10.10.40.0 0.0.0.255 any'",
                    "Reverse C2 beacon dropped at database boundary [BLOCKED]",
                ],
            },
            "I-01": {
                "id": "I-01",
                "title": "Cross-Domain Cloud Lateral Access: Compromised K8s Pod -> Finance DB",
                "threat_id": "I-01",
                "source_id": "k8s-edu-api",
                "dest_id": "k8s-fin-db",
                "action": ActionType.WRITE,
                "is_anomaly": True,
                "expected_decision": Decision.ISOLATE,
                "packet_trace": [
                    "k8s-edu-api pod (education namespace) sends cross-domain probe toward k8s-fin-db",
                    "Calico CNI enforces default-deny NetworkPolicy on namespace boundary -> Packet dropped",
                    "AegisMesh Detection correlates anomalous cross-namespace probe -> Risk Score: 85 (CRITICAL)",
                    "Containment Controller triggers blast-radius containment: State -> CONTAINED",
                    "Dynamic NetworkPolicy updated to isolate pod while preserving k8s-edu-db dependency [ISOLATED]",
                ],
            },
        }

    # Store query & update methods
    def get_workload(self, workload_id: str) -> Optional[WorkloadNode]:
        return self.workloads.get(workload_id)

    def list_workloads(self) -> List[WorkloadNode]:
        return list(self.workloads.values())

    def update_workload_state(self, workload_id: str, state: WorkloadState, trust_score: Optional[int] = None):
        if workload_id in self.workloads:
            self.workloads[workload_id].state = state
            if trust_score is not None:
                self.workloads[workload_id].trust_score = trust_score

    def add_audit_log(self, log: AuditLogSchema):
        self.audit_logs.insert(0, log)
        if len(self.audit_logs) > 200:
            self.audit_logs.pop()

    def add_incident(self, incident: IncidentSchema):
        self.incidents.insert(0, incident)

    def get_incident_for_workload(self, workload_id: str) -> Optional[IncidentSchema]:
        for inc in self.incidents:
            if inc.workload_id == workload_id and inc.status != "RESOLVED":
                return inc
        return None


# Global singleton instance
store = InMemoryStore()
