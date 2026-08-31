# AegisMesh — Final Demonstration Script

## 1. Purpose

This demonstration validates the AegisMesh hybrid security architecture across normal access, policy-based blocking, automated risk-based containment, quarantine restoration, and centralized SIEM monitoring.

The demonstration should be performed from the AegisMesh dashboard while observing the corresponding API responses, topology state, containment status, and SIEM security events.

---

## 2. Pre-Demo Checklist

Before starting:

1. Start the AegisMesh backend.
2. Start/open the AegisMesh dashboard.
3. Confirm the backend health endpoint reports `online`.
4. Confirm the Kubernetes integration is available if demonstrating real Kubernetes enforcement.
5. Open the dashboard sections for:
   - Security decisions
   - Incidents
   - Containment
   - Live Security Events / SIEM
6. Ensure the system starts from a clean or known state.

---

# Demo 1 — Normal Authorized Access

## Scenario

Faculty workstation accesses the authorized application server.

```text
FAC-PC-01
    |
    | Authorized connection
    v
APP-SRV-01
```

## Scenario ID

```text
PT-01
```

## Expected Flow

```text
Authorized Request
        ↓
Policy Evaluation
        ↓
Risk Evaluation
        ↓
Decision = ALLOW
        ↓
Request Permitted
        ↓
SIEM Security Event
```

## Demonstration

1. Select the baseline authorized scenario.
2. Execute the simulation.
3. Observe the decision returned by AegisMesh.
4. Verify that the final decision is `ALLOW`.
5. Show the source and destination workloads.
6. Show the risk score and risk level.
7. Open the SIEM events section.

## Expected Result

```text
Decision: ALLOW
Source: FAC-PC-01
Target: APP-SRV-01
Containment: NONE
```
The event should appear in the centralized SIEM event store.

---

# Demo 2 — Unauthorized Database Access

## Scenario
A faculty workstation attempts direct access to the protected database server.

```text
FAC-PC-01
    |
    | Unauthorized database access
    v
DB-SRV-01
```

## Scenario ID

```text
E-04
```

## Expected Flow

```text
Unauthorized Request
        ↓
Policy Evaluation
        ↓
Risk Evaluation
        ↓
Decision = BLOCK
        ↓
Request Denied
        ↓
SIEM Security Event
```

## Demonstration

1. Select scenario `E-04`.
2. Execute the simulation.
3. Observe the decision.
4. Show the policy/risk explanation.
5. Show the packet trace indicating that the request is blocked.
6. Open the SIEM event list.

## Expected Result

```text
Decision: BLOCK
Source: FAC-PC-01
Target: DB-SRV-01
Containment: NONE
```
The event should be recorded by the SIEM bridge with its risk score, severity, timestamp, source, target, and threat ID.

---

# Demo 3 — Kubernetes Lateral Movement and Dynamic Containment

## Scenario
A Kubernetes workload attempts unauthorized cross-domain/lateral movement toward a protected resource.

```text
Kubernetes Workload
        |
        | Suspicious lateral movement
        v
Protected Kubernetes Resource
```

## Scenario ID

```text
I-01
```

## Expected Flow

```text
Suspicious Request
        ↓
Risk Engine
        ↓
High/Critical Risk
        ↓
Decision = ISOLATE
        ↓
Containment Controller
        ↓
Kubernetes Dynamic NetworkPolicy
        ↓
Unauthorized Traffic Blocked
        ↓
SIEM ISOLATE Event
```

## Demonstration

1. Select the Kubernetes lateral-movement scenario.
2. Execute the scenario.
3. Show the calculated risk score and severity.
4. Show that the final decision is `ISOLATE`.
5. Show the containment status.
6. Open the Kubernetes containment status.
7. Show the dynamically applied NetworkPolicy when real Kubernetes enforcement is available.
8. Show that the affected workload transitions to `CONTAINED`.
9. Open the SIEM event list.

## Expected Result

```text
Decision: ISOLATE
Severity: CRITICAL
Containment: ACTIVE
Workload State: CONTAINED
```
For a real Kubernetes workload, the containment controller invokes the Kubernetes integration and applies the dynamic NetworkPolicy.

The SIEM event should contain:

```text
decision: ISOLATE
severity: CRITICAL
containment_status: ACTIVE
event_type: containment_action
```

---

# Demo 4 — Lift Quarantine and Restore Connectivity

## Scenario
After remediation, the security analyst restores the contained workload.

```text
Contained Workload
        ↓
Security Analyst Verification
        ↓
Lift Quarantine
        ↓
Dynamic NetworkPolicy Removed
        ↓
Workload = NORMAL
        ↓
Connectivity Restored
        ↓
SIEM Restore Event
```

## Demonstration

1. Identify the currently contained workload.
2. Trigger the restore/lift-quarantine action.
3. Show the workload state changing from `CONTAINED` to `NORMAL`.
4. Show the trust score returning to its baseline.
5. When real Kubernetes enforcement is active, show that the dynamic NetworkPolicy is removed.
6. Verify the containment incident becomes `RESOLVED`.
7. Open the SIEM event list.

## Expected Result

```text
State: NORMAL
Trust Score: 85
Containment Status: RESTORED
Event Type: containment_restore
Decision: ALLOW
```
AegisMesh represents the restore operation in the SIEM as an `ALLOW` decision with:

```text
event_type = containment_restore
containment_status = RESTORED
risk_score = 15
severity = LOW
```

---

# Demo 5 — Centralized SIEM Security Audit Trail

## Goal
Demonstrate that security decisions and containment actions are centrally recorded.

## Expected Flow

```text
Security Decision
      ↓
SIEM Logging Bridge
      ↓
Central Event Store
      ↓
GET /api/v1/siem/events
      ↓
Dashboard
```

## Demonstration
Open the Live Security Events section of the dashboard.

Verify that events contain:

```text
Timestamp
Event ID
Event Type
Decision
Risk Score
Severity
Source Domain
Source Workload
Target
Containment Status
Threat ID
```

## Example Event Sequence
A complete demonstration should produce events similar to:

```text
ALLOW
FAC-PC-01 → APP-SRV-01
Containment: NONE

BLOCK
FAC-PC-01 → DB-SRV-01
Containment: NONE

ISOLATE
Kubernetes workload → protected resource
Containment: ACTIVE

ALLOW / RESTORE
Contained workload → restored
Containment: RESTORED
```

## SIEM API Verification
Verify:

```text
GET /api/v1/siem/status
GET /api/v1/siem/events
POST /api/v1/siem/export
```
The SIEM status should report:

```json
{
  "status": "ACTIVE",
  "events_logged": "<number of recorded events>",
  "integration": "AegisMesh SIEM Bridge"
}
```
The events endpoint should return the centralized security event collection.

The export endpoint should return the events in structured JSON format.

---

# 3. Final Demonstration Narrative
The complete security lifecycle demonstrated by AegisMesh is:

```text
Normal Access
    ↓
ALLOW
    ↓
Centralized SIEM Logging

Unauthorized Access
    ↓
BLOCK
    ↓
Centralized SIEM Logging

Suspicious Kubernetes Lateral Movement
    ↓
Risk Detection
    ↓
ISOLATE
    ↓
Dynamic NetworkPolicy
    ↓
Traffic Contained
    ↓
SIEM Security Event

Security Analyst Verification
    ↓
Lift Quarantine
    ↓
NetworkPolicy Removed
    ↓
Workload Restored
    ↓
SIEM Restore Event

All Events
    ↓
Centralized Security Audit Trail
    ↓
Live Dashboard Monitoring
```

---

# 4. Key Message for the Demonstration
AegisMesh demonstrates a centralized security decision plane capable of evaluating requests, detecting elevated risk, enforcing policy decisions, dynamically containing Kubernetes workloads, restoring remediated workloads, and maintaining a centralized SIEM-compatible security audit trail.
