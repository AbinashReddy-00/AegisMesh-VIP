"""
AegisMesh — Centralized SIEM Logging Bridge
"""

from datetime import datetime, timezone
import json
import uuid
from typing import Any, Dict, List, Optional

from ..models.enums import Decision, RiskLevel


class SIEMClient:
    """In-memory centralized security event store."""

    def __init__(self):
        self.events: List[Dict[str, Any]] = []

    def log_event(
        self,
        decision: Decision,
        risk_score: int,
        severity: RiskLevel,
        source_domain: str,
        source_workload: str,
        target: str,
        containment_status: str = "NONE",
        threat_id: Optional[str] = None,
        event_type: str = "security_decision",
    ) -> Dict[str, Any]:
        event = {
            "event_id": f"SIEM-{uuid.uuid4().hex[:12].upper()}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "AegisMesh",
            "event_type": event_type,
            "source_domain": source_domain,
            "source_workload": source_workload,
            "target": target,
            "risk_score": risk_score,
            "decision": decision.value,
            "severity": severity.value,
            "containment_status": containment_status,
            "threat_id": threat_id,
        }

        self.events.insert(0, event)
        return event

    def list_events(self) -> List[Dict[str, Any]]:
        return list(self.events)

    def export_events(self) -> str:
        return json.dumps(self.events, indent=2)

    def status(self) -> Dict[str, Any]:
        return {
            "status": "ACTIVE",
            "events_logged": len(self.events),
            "integration": "AegisMesh SIEM Bridge",
        }


siem_client = SIEMClient()
