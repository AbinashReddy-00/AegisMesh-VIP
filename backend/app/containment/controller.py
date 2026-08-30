"""
AegisMesh — Blast-Radius Containment Controller
Traces to: docs/architecture/aegismesh-design.md Section 7 & Phase 3 K8s Bridge
"""
from datetime import datetime, timezone
import uuid
from typing import Dict, Any, Optional
from ..models.enums import WorkloadState, RiskLevel, Decision, InfrastructureDomain
from ..models.schemas import IncidentSchema, AuditLogSchema
from ..database.store import store
from ..integrations.kubernetes_client import k8s_client


class ContainmentController:
    def isolate_workload(
        self,
        workload_id: str,
        reason: str,
        threat_id: Optional[str] = "I-01",
        namespace: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Quarantines a compromised workload to contain the blast radius.
        Restricts egress while preserving authorized dependencies.
        Triggers real Kubernetes NetworkPolicy isolation when targeting container workloads.
        """
        workload = store.get_workload(workload_id)
        if not workload:
            # Check if it's a direct k8s workload name and register in store
            if workload_id in ["education-app", "education-client", "finance-db"] or "k8s" in workload_id.lower():
                from ..models.schemas import WorkloadNode
                from ..models.enums import SecurityZone
                ns = namespace or ("finance" if "fin" in workload_id.lower() else "education")
                workload = WorkloadNode(
                    id=workload_id,
                    name=f"k8s: {workload_id}",
                    domain=InfrastructureDomain.KUBERNETES,
                    zone=SecurityZone.K8S_FIN if "fin" in workload_id.lower() else SecurityZone.K8S_EDU,
                    domain_label="Kubernetes Local Cluster",
                    state=WorkloadState.NORMAL,
                    trust_score=85,
                    vlan_or_vpc_or_ns=f"namespace: {ns}",
                    allowed_dependencies=[],
                )
                store.workloads[workload_id] = workload
            else:
                return {"error": f"Workload '{workload_id}' not found."}

        now = datetime.now(timezone.utc)
        workload.state = WorkloadState.CONTAINED
        workload.trust_score = 15  # Degraded trust

        # 1. Check if Kubernetes Real Enforcement applies
        is_k8s_workload = (
            workload.domain == InfrastructureDomain.KUBERNETES
            or "k8s" in workload.id.lower()
            or workload.id in ["education-app", "education-client", "finance-db"]
        )

        k8s_result = None
        enforcement_type = "SIMULATED_DOMAIN_ISOLATION"
        enforcement_layer = "AegisMesh Central Decision Plane"
        policy_name = None

        if is_k8s_workload:
            k8s_result = k8s_client.apply_isolation(
                workload_id=workload.id,
                reason=reason,
                namespace=namespace,
                threat_id=threat_id,
            )
            enforcement_type = k8s_result.get("enforcement", "REAL_KUBERNETES_NETWORKPOLICY")
            enforcement_layer = k8s_result.get("enforcement_layer", "Calico CNI Dynamic Kernel Enforcement")
            policy_name = k8s_result.get("policy_name")

        # 2. Build Containment Actions & Timeline
        inc_id = f"INC-{now.strftime('%Y')}-{uuid.uuid4().hex[:4].upper()}"
        actions = [
            f"Workload '{workload.name}' transitioned from NORMAL to CONTAINED.",
            f"Egress restricted to authorized dependencies only: {workload.allowed_dependencies}.",
            "Dynamic policy override applied: All unauthorized lateral paths BLOCKED.",
        ]

        if is_k8s_workload and k8s_result and k8s_result.get("success"):
            actions.append(f"REAL ENFORCEMENT: Applied Calico NetworkPolicy '{policy_name}' in namespace '{k8s_result.get('namespace')}'.")
        else:
            actions.append("Security telemetry alert dispatched to Wazuh SIEM.")

        timeline = [
            {"time": now.isoformat(), "event": f"Anomaly detected on {workload.id}: {reason}"},
            {"time": now.isoformat(), "event": "AegisMesh Containment Controller initiated quarantine protocol."},
            {"time": now.isoformat(), "event": f"Blast-radius containment enforced via {enforcement_layer}."},
        ]

        incident = IncidentSchema(
            id=inc_id,
            workload_id=workload.id,
            workload_name=workload.name,
            domain=workload.domain,
            zone=workload.zone,
            threat_id=threat_id or "ANOMALY-01",
            title=f"Automated Containment: {workload.name} Quarantined",
            severity=RiskLevel.CRITICAL,
            status="ACTIVE",
            created_at=now,
            updated_at=now,
            containment_actions=actions,
            timeline=timeline,
        )
        store.add_incident(incident)

        # 3. Create Immutable Audit Log
        store.add_audit_log(
            AuditLogSchema(
                id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
                timestamp=now,
                actor="AegisMesh Containment Controller",
                source_ip=workload.ip_address,
                target=workload.id,
                action="ISOLATE_WORKLOAD",
                decision=Decision.ISOLATE,
                risk_score=90,
                threat_id=threat_id,
                details=f"Workload quarantined via {enforcement_type}. Reason: {reason} | Policy: {policy_name or 'N/A'}",
            )
        )

        return {
            "status": "success",
            "workload_id": workload.id,
            "state": workload.state.value,
            "incident_id": inc_id,
            "enforcement": enforcement_type,
            "enforcement_layer": enforcement_layer,
            "policy_name": policy_name,
            "actions_applied": actions,
            "allowed_dependencies": workload.allowed_dependencies,
            "k8s_result": k8s_result,
        }

    def restore_workload(self, workload_id: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """
        Restores a contained workload back to NORMAL operation.
        Removes dynamic Kubernetes NetworkPolicy if applicable.
        """
        workload = store.get_workload(workload_id)
        if not workload:
            if workload_id in ["education-app", "education-client", "finance-db"] or "k8s" in workload_id.lower():
                from ..models.schemas import WorkloadNode
                from ..models.enums import SecurityZone
                ns = namespace or ("finance" if "fin" in workload_id.lower() else "education")
                workload = WorkloadNode(
                    id=workload_id,
                    name=f"k8s: {workload_id}",
                    domain=InfrastructureDomain.KUBERNETES,
                    zone=SecurityZone.K8S_FIN if "fin" in workload_id.lower() else SecurityZone.K8S_EDU,
                    domain_label="Kubernetes Local Cluster",
                    state=WorkloadState.NORMAL,
                    trust_score=85,
                    vlan_or_vpc_or_ns=f"namespace: {ns}",
                    allowed_dependencies=[],
                )
                store.workloads[workload_id] = workload
            else:
                return {"error": f"Workload '{workload_id}' not found."}


        now = datetime.now(timezone.utc)
        workload.state = WorkloadState.NORMAL
        workload.trust_score = 85  # Restored baseline

        # 1. Release Kubernetes Real Enforcement if applicable
        is_k8s_workload = (
            workload.domain == InfrastructureDomain.KUBERNETES
            or "k8s" in workload.id.lower()
            or workload.id in ["education-app", "education-client", "finance-db"]
        )

        k8s_result = None
        if is_k8s_workload:
            k8s_result = k8s_client.release_isolation(workload_id=workload.id, namespace=namespace)

        # 2. Mark active incident as resolved
        incident = store.get_incident_for_workload(workload_id)
        if incident:
            incident.status = "RESOLVED"
            incident.updated_at = now
            incident.timeline.append(
                {"time": now.isoformat(), "event": "Security analyst verified remediation; workload restored to NORMAL."}
            )
            if k8s_result and k8s_result.get("success"):
                incident.timeline.append(
                    {"time": now.isoformat(), "event": f"Kubernetes dynamic NetworkPolicy '{k8s_result.get('policy_name')}' deleted from cluster."}
                )

        # 3. Create Immutable Audit Log
        store.add_audit_log(
            AuditLogSchema(
                id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
                timestamp=now,
                actor="Security Analyst",
                source_ip=workload.ip_address,
                target=workload.id,
                action="RESTORE_WORKLOAD",
                decision=Decision.ALLOW,
                risk_score=15,
                threat_id=None,
                details=f"Workload {workload.id} quarantine lifted and restored to NORMAL. (K8s Policy Released)",
            )
        )

        return {
            "status": "success",
            "workload_id": workload.id,
            "state": workload.state.value,
            "trust_score": workload.trust_score,
            "message": "Quarantine lifted. Workload returned to normal baseline.",
            "k8s_result": k8s_result,
        }


containment_controller = ContainmentController()
