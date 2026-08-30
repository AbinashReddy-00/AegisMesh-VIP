# AegisMesh — Dynamic Kubernetes Containment Bridge

**Version:** 1.0  
**Status:** IMPLEMENTED & EMPIRICALLY VALIDATED  
**Cluster Target:** Local Kind Cluster (`aegismesh-k8s`) with Project Calico CNI  

---

## 1. Overview & Architecture

The **AegisMesh Dynamic Kubernetes Containment Bridge** establishes a live, closed-loop automated response between the AegisMesh Decision Engine and local Kubernetes container workloads. When anomalous cross-domain traversal or lateral movement is detected and evaluated as `ISOLATE`, AegisMesh dynamically programs real kernel-level Zero-Trust packet filters into the cluster via Calico CNI `NetworkPolicy` objects.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        AEGISMESH DYNAMIC CONTAINMENT LOOP                              │
│                                                                                        │
│   [Security Telemetry / API Flow]                                                      │
│                 │                                                                      │
│                 ▼                                                                      │
│   ┌───────────────────────────┐                                                        │
│   │    AegisMesh Risk Engine   │ ──▶ Multi-factor scoring (Score: 85-95 / CRITICAL)    │
│   └─────────────┬─────────────┘                                                        │
│                 ▼                                                                      │
│   ┌───────────────────────────┐                                                        │
│   │   AegisMesh Decision      │ ──▶ Verdict: ISOLATE                                   │
│   │   Engine Plane            │                                                        │
│   └─────────────┬─────────────┘                                                        │
│                 ▼                                                                      │
│   ┌───────────────────────────┐                                                        │
│   │   Containment Controller  │ ──▶ State: NORMAL ➔ CONTAINED                          │
│   └─────────────┬─────────────┘     Creates Immutable Audit Record                     │
│                 ▼                                                                      │
│   ┌───────────────────────────┐                                                        │
│   │   Kubernetes Integration  │ ──▶ Invokes `kubectl` / Kube API                       │
│   │   Client Module           │                                                        │
│   └─────────────┬─────────────┘                                                        │
│                 ▼                                                                      │
│   ┌───────────────────────────┐                                                        │
│   │ Dynamic NetworkPolicy     │ ──▶ Generated: `aegismesh-isolate-<workload>`          │
│   │ Applied in Namespace      │     Ingress & Lateral Egress locked down               │
│   └─────────────┬─────────────┘                                                        │
│                 ▼                                                                      │
│   ┌───────────────────────────┐                                                        │
│   │  Project Calico CNI Felix │ ──▶ Drops SYN packets at veth/iptables layer           │
│   │  Kernel Packet Filter     │                                                        │
│   └───────────────────────────┘                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Dynamic NetworkPolicy Specification

When a workload (such as `education-client` or `education-app`) is flagged for isolation, AegisMesh dynamically generates and applies the following targeted manifest:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: aegismesh-isolate-education-client
  namespace: education
  labels:
    app.kubernetes.io/managed-by: aegismesh
    aegismesh.security/enforcement: dynamic-containment
    aegismesh.security/target-workload: education-client
spec:
  podSelector:
    matchLabels:
      app: education-client
  policyTypes:
  - Ingress
  - Egress
  ingress: []
  egress:
  # Allows essential in-cluster DNS lookup to avoid hard crashing system resolvers,
  # but blocks ALL outbound TCP/UDP lateral communication across all subnets.
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
```

---

## 3. Endpoints & API Specifications

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/kubernetes/status` | Returns cluster health, Calico CNI status, node readiness, and active dynamic policies |
| `POST` | `/api/v1/containment/isolate` | Quarantines workload in AegisMesh state and applies dynamic Kubernetes NetworkPolicy |
| `POST` | `/api/v1/containment/release` | Removes dynamic NetworkPolicy and restores workload to `NORMAL` trust baseline |
| `GET` | `/api/v1/containment/status` | Returns active quarantined workloads and cluster-enforced policies |

### Isolation Request Payload:
```json
{
  "workload": "education-client",
  "namespace": "education",
  "reason": "Lateral movement anomaly probe detected (Threat I-01)"
}
```

### Isolation Response Payload:
```json
{
  "status": "success",
  "workload_id": "education-client",
  "state": "CONTAINED",
  "incident_id": "INC-2026-A735",
  "enforcement": "REAL_KUBERNETES_NETWORKPOLICY",
  "enforcement_layer": "Calico CNI Dynamic Kernel Enforcement",
  "policy_name": "aegismesh-isolate-education-client",
  "actions_applied": [
    "Workload 'k8s: education-client' transitioned from NORMAL to CONTAINED.",
    "Egress restricted to authorized dependencies only: [].",
    "Dynamic policy override applied: All unauthorized lateral paths BLOCKED.",
    "REAL ENFORCEMENT: Applied Calico NetworkPolicy 'aegismesh-isolate-education-client' in namespace 'education'."
  ]
}
```

---

## 4. Empirical 6-Stage Validation Results

The end-to-end integration was executed and validated directly against the live cluster:

```
============================================================
  AEGISMESH — DYNAMIC KUBERNETES CONTAINMENT BRIDGE TEST
============================================================
[*] Cluster Status: CONNECTED
[*] CNI Provider:   Project Calico v3.28

[STEP 1/6] Testing Baseline Authorized Connectivity (education-client -> education-app)...
 -> STATUS: ALLOWED (HTTP 200 OK) [PASS]

[STEP 2/6] Triggering AegisMesh Automated Quarantine on 'education-client'...
 -> Incident ID:   INC-2026-A735
 -> Enforcement:   REAL_KUBERNETES_NETWORKPOLICY
 -> Policy Name:   aegismesh-isolate-education-client
 -> State:         CONTAINED

[STEP 3/6] Verifying NetworkPolicy in Kubernetes cluster...
NAME                                 POD-SELECTOR           AGE
aegismesh-isolate-education-client   app=education-client   0s
allow-education-client               app=education-app      11m
 -> Dynamic NetworkPolicy verified in cluster [PASS]

[STEP 4/6] Testing Real Traffic During Containment (education-client -> education-app)...
 -> STATUS: BLOCKED BY CALICO CNI (Connection Timed Out) [PASS]

[STEP 5/6] Triggering AegisMesh Release Quarantine on 'education-client'...
 -> Result:        Quarantine lifted. Workload returned to normal baseline.
 -> Workload State: NORMAL

[STEP 6/6] Verifying NetworkPolicy Removal and Connectivity Restoration...
 -> Dynamic NetworkPolicy successfully removed from cluster [PASS]
 -> Connectivity Restored: ALLOWED (HTTP 200 OK) [PASS]

============================================================
  ALL 6 PHASES PASSED — DYNAMIC CONTAINMENT LOOP EMPIRICALLY VERIFIED!
============================================================
```

---

## 5. Automated Test Suite

To run the automated integration tests:

* **Python Runner:**
  ```powershell
  python testing/kubernetes/test_containment_bridge.py
  ```
* **PowerShell Runner:**
  ```powershell
  powershell -File testing/kubernetes/test_containment_bridge.ps1
  ```
* **Unit Test Suite (with Mocking for Offline Testing):**
  ```powershell
  python -m pytest backend/tests/
  ```

---

## 6. Scope & Safety Declarations

* **Local Environment:** Operates against a **locally running Kind Kubernetes cluster** on Docker Desktop.
* **Graceful Degradation:** If the local Kubernetes cluster is offline or unreachable, AegisMesh logs the status clearly as `SIMULATED_CONTAINMENT_FALLBACK` and applies application-layer decision blocking without crashing the server.
* **Idempotent & Reversible:** Dynamic NetworkPolicies use explicit label tagging (`app.kubernetes.io/managed-by: aegismesh`), ensuring clean removal without disturbing base cluster policies.
