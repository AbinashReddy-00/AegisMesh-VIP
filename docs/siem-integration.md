# AegisMesh SIEM Integration

## 1. Overview

AegisMesh records security decisions in a centralized in-memory SIEM bridge. The bridge is implemented as a lightweight event store for the demo environment and is exposed through the API layer for status checks, event retrieval, and JSON export.

```text
Decision Engine
      |
      v
Security Decision
      |
      +---- ALLOW
      +---- RESTRICT
      +---- BLOCK
      +---- ISOLATE
      |
      v
SIEMClient.log_event(...)
      |
      v
Centralized In-Memory Event Store
      |
      +---- /api/v1/siem/status
      +---- /api/v1/siem/events
      +---- /api/v1/siem/export
```

## 2. Event Flow

When AegisMesh generates a security decision, the decision engine calls the SIEM bridge to create a structured event record.

Each event stores the following fields:

- event_id
- timestamp
- source
- event_type
- source_domain
- source_workload
- target
- risk_score
- decision
- severity
- containment_status
- threat_id

## 3. Event Schema

Example event payload:

```json
{
  "event_id": "SIEM-123456789ABC",
  "timestamp": "2026-08-30T10:00:00+00:00",
  "source": "AegisMesh",
  "event_type": "security_decision",
  "source_domain": "kubernetes",
  "source_workload": "education-client",
  "target": "finance-db",
  "risk_score": 82,
  "decision": "ISOLATE",
  "severity": "CRITICAL",
  "containment_status": "ACTIVE",
  "threat_id": "I-01"
}
```

The actual implementation is defined in `backend/app/integrations/siem_client.py` and uses the project enums for `Decision` and `RiskLevel`.

## 4. Supported Security Decisions and Severity Levels

The current codebase supports the following decision values:

- ALLOW
- RESTRICT
- BLOCK
- ISOLATE

The severity values supported by the SIEM bridge are:

- LOW
- MEDIUM
- HIGH
- CRITICAL

A restoration flow is represented by a `security_restore` event type and a `containment_status` such as `RESTORED`, rather than a separate `RESTORE` decision value.

## 5. API Endpoints

### GET /api/v1/siem/status

Returns the bridge health and event count.

Example response:

```json
{
  "status": "ACTIVE",
  "events_logged": 25,
  "integration": "AegisMesh SIEM Bridge"
}
```

### GET /api/v1/siem/events

Returns the full list of stored security events.

### POST /api/v1/siem/export

Returns all recorded events in a structured JSON payload.

Example response:

```json
{
  "format": "json",
  "events": [],
  "event_count": 0
}
```

## 6. Implementation Details

The SIEM bridge is implemented in the following files:

- `backend/app/integrations/siem_client.py`
- `backend/app/api/v1/endpoints.py`
- `backend/tests/test_siem_bridge.py`

The implementation uses an in-memory list (`self.events`) and exposes a singleton instance named `siem_client` for centralized logging.

## 7. Testing Coverage

The backend test suite includes SIEM bridge validation for:

- ALLOW event logging
- BLOCK event logging
- ISOLATE event logging
- restoration event logging via `security_restore`
- risk score storage
- severity storage
- timestamp generation
- event ID generation
- JSON export behavior

Run the tests from the repository root:

```powershell
python -m pytest backend/tests/
```

## 8. Project Scope

The current implementation is intentionally limited to an in-memory event store suitable for the AegisMesh demonstration environment. It provides a clean integration interface that can later be connected to an external SIEM platform such as Wazuh, Elastic, or another centralized log collector.

The SIEM functionality remains isolated within the integrations layer and is intentionally separate from the decision engine and policy logic.