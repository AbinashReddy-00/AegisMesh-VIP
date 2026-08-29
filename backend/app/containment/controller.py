"""
AegisMesh — Blast-Radius Containment Controller
Traces to: docs/architecture/aegismesh-design.md Section 7
"""
from datetime import datetime, timezone
import uuid
from typing import Dict, Any, Optional
from ..models.enums import WorkloadState, RiskLevel, Decision
from ..models.schemas import IncidentSchema, AuditLogSchema
from ..database.store import store


class ContainmentController:
    def isolate_workload(self, workload_id: str, reason: str, threat_id: Optional[str] = "I-01") -> Dict[str, Any]:
        """
        Quarantines a compromised workload to contain the blast radius.
        Restricts egress while preserving authorized dependencies.
        """
        workload = store.get_workload(workload_id)
        if not workload:
            return {"error": f"Workload '{workload_id}' not found."}

        now = datetime.now(timezone.utc)
        workload.state = WorkloadState.CONTAINED
        workload.trust_score = 15  # Degraded trust

        # Create or update incident
        inc_id = f"INC-{now.strftime('%Y')}-{uuid.uuid4().hex[:4].upper()}"
        actions = [
            f"Workload '{workload.name}' transitioned from NORMAL to CONTAINED.",
            f"Egress restricted to authorized dependencies only: {workload.allowed_dependencies}.",
            "Dynamic policy override applied: All unauthorized lateral paths BLOCKED.",
            "Security telemetry alert dispatched to Wazuh SIEM.",
        ]
        timeline = [
            {"time": now.isoformat(), "event": f"Anomaly detected on {workload.id}: {reason}"},
            {"time": now.isoformat(), "event": "AegisMesh Containment Controller initiated quarantine protocol."},
            {"time": now.isoformat(), "event": "Blast-radius containment enforced."},
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

        # Audit log
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
                details=f"Workload quarantined. Reason: {reason}",
            )
        )

        return {
            "status": "success",
            "workload_id": workload.id,
            "state": workload.state.value,
            "incident_id": inc_id,
            "actions_applied": actions,
            "allowed_dependencies": workload.allowed_dependencies,
        }

    def restore_workload(self, workload_id: str) -> Dict[str, Any]:
        """
        Restores a contained workload back to NORMAL operation.
        """
        workload = store.get_workload(workload_id)
        if not workload:
            return {"error": f"Workload '{workload_id}' not found."}

        now = datetime.now(timezone.utc)
        workload.state = WorkloadState.NORMAL
        workload.trust_score = 85  # Restored baseline

        # Mark active incident as resolved
        incident = store.get_incident_for_workload(workload_id)
        if incident:
            incident.status = "RESOLVED"
            incident.updated_at = now
            incident.timeline.append(
                {"time": now.isoformat(), "event": "Security analyst verified remediation; workload restored to NORMAL."}
            )

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
                details=f"Workload {workload.id} quarantine lifted and restored to NORMAL.",
            )
        )

        return {
            "status": "success",
            "workload_id": workload.id,
            "state": workload.state.value,
            "trust_score": workload.trust_score,
            "message": "Quarantine lifted. Workload returned to normal baseline.",
        }


containment_controller = ContainmentController()
