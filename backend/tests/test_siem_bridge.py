from backend.app.integrations.siem_client import SIEMClient
from backend.app.models.enums import Decision, RiskLevel


def test_allow_event_logged():
    siem = SIEMClient()
    event = siem.log_event(
        decision=Decision.ALLOW,
        risk_score=20,
        severity=RiskLevel.LOW,
        source_domain="kubernetes",
        source_workload="education-client",
        target="education-app",
    )
    assert event["decision"] == "ALLOW"


def test_block_event_logged():
    siem = SIEMClient()
    event = siem.log_event(
        decision=Decision.BLOCK,
        risk_score=77,
        severity=RiskLevel.HIGH,
        source_domain="private_dc",
        source_workload="faculty-pc",
        target="finance-db",
    )
    assert event["decision"] == "BLOCK"


def test_isolate_event_logged():
    siem = SIEMClient()
    event = siem.log_event(
        decision=Decision.ISOLATE,
        risk_score=90,
        severity=RiskLevel.CRITICAL,
        source_domain="kubernetes",
        source_workload="education-client",
        target="finance-db",
        containment_status="ACTIVE",
    )
    assert event["decision"] == "ISOLATE"
    assert event["containment_status"] == "ACTIVE"


def test_restore_event_logged():
    siem = SIEMClient()
    event = siem.log_event(
        decision=Decision.ALLOW,
        risk_score=15,
        severity=RiskLevel.LOW,
        source_domain="kubernetes",
        source_workload="education-client",
        target="education-app",
        containment_status="RESTORED",
        event_type="security_restore",
    )
    assert event["event_type"] == "security_restore"
    assert event["containment_status"] == "RESTORED"


def test_risk_score_stored():
    siem = SIEMClient()
    event = siem.log_event(
        decision=Decision.BLOCK,
        risk_score=82,
        severity=RiskLevel.CRITICAL,
        source_domain="kubernetes",
        source_workload="education-client",
        target="finance-db",
    )
    assert event["risk_score"] == 82


def test_severity_stored():
    siem = SIEMClient()
    event = siem.log_event(
        decision=Decision.ISOLATE,
        risk_score=95,
        severity=RiskLevel.CRITICAL,
        source_domain="kubernetes",
        source_workload="education-client",
        target="finance-db",
    )
    assert event["severity"] == "CRITICAL"


def test_timestamp_exists():
    siem = SIEMClient()
    event = siem.log_event(
        decision=Decision.ALLOW,
        risk_score=10,
        severity=RiskLevel.LOW,
        source_domain="kubernetes",
        source_workload="education-client",
        target="education-app",
    )
    assert event["timestamp"]
    assert event["event_id"]


def test_json_export_works():
    siem = SIEMClient()
    siem.log_event(
        decision=Decision.BLOCK,
        risk_score=70,
        severity=RiskLevel.HIGH,
        source_domain="private_dc",
        source_workload="faculty-pc",
        target="finance-db",
    )

    exported = siem.export_events()

    assert '"decision": "BLOCK"' in exported
    assert '"risk_score": 70' in exported
