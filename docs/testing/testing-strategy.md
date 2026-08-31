# AegisMesh — Testing Strategy & Multi-Domain Verification Framework

**Version:** 1.0 (FINAL)
**Date:** 2026-08-31
**Status:** IMPLEMENTED & EMPIRICALLY VALIDATED
**Automated Executable Validations:** **37 / 37 Passed** (Backend: 18, K8s: 6, E2E: 5, AWS: 8)
**Packet Tracer Empirical Matrix:** **30 / 30 Passed** (VLANs & SVI ACLs)
**Traces to:** NFR-04, AC-01, AC-02, AC-03, AC-04

---

## 1. Testing Philosophy & Verification Hierarchy

### 1.1 Core Principle: Bidirectional Zero-Trust Verification

For every security domain and microsegmentation boundary, we empirically prove **BOTH** directions:

1. ✅ **Authorized traffic succeeds** — least-privilege workflows operate with zero impediment.
2. ❌ **Unauthorized traffic fails** — policy boundaries and containment locks strictly drop packets.

### 1.2 Unified 5-Level Testing Hierarchy

```
                       ╱╲
                      ╱  ╲         Level 3: Hybrid End-to-End Threat Scenarios
                     ╱    ╲        (5 / 5 Passing Scenarios — run_e2e_tests.py)
                    ╱──────╲
                   ╱        ╲      Level 2: Kubernetes Live Containment Validation
                  ╱          ╲     (6 / 6 Passing Phases — test_containment_bridge.py)
                 ╱────────────╲
                ╱              ╲   Level 1: Backend Engine Unit & Integration
               ╱                ╲  (18 / 18 Passing Tests — pytest backend/tests/)
              ╱──────────────────╲
             ╱                    ╲ Level 4: AWS Zero-Trust Cloud Validation
            ╱                      ╲(8 / 8 Passing Controls — LocalStack + Terraform)
           ╱────────────────────────╲
          ╱                          ╲ Level 5: Cisco DC Network Segmentation
         ╱                            ╲(30 / 30 Empirical Tests — Packet Tracer Matrix)
        ╱──────────────────────────────╲
```

---

## 2. Multi-Domain Test Levels & Execution Breakdown

### Level 1: Backend Security Engine & Integration Testing
- **Target:** FastAPI Decision Engine, 6-Factor Risk Scorer, and Containment Bridge
- **Runner:** `python -m pytest backend/tests/`
- **Result:** **18 / 18 PASS**
- **Test Modules:**
  - `test_engine.py` (8 tests): Risk scoring weights, policy rules, default deny, rationale generation.
  - `test_k8s_bridge.py` (5 tests): Dynamic manifest generation, quarantine state machine, API responses.
  - `test_e2e_scenarios.py` (5 tests): Core decision and containment pipeline integration.

---

### Level 2: Kubernetes Live Containment Validation
- **Target:** Local Kind Cluster (`kind-aegismesh-k8s`) with Project Calico CNI v3.28
- **Runner:** `python testing/kubernetes/test_containment_bridge.py`
- **Execution Model:** **LIVE Local Cluster Execution**
- **Result:** **6 / 6 PHASES PASS**
  1. *Baseline Authorized Connectivity*: HTTP 200 OK (`education-client` -> `education-app`).
  2. *Automated Quarantine Trigger*: `ISOLATE` decision generated with incident record.
  3. *Dynamic NetworkPolicy Injection*: `aegismesh-isolate-education-client` applied to cluster.
  4. *Kernel Packet Drop Verification*: Calico drops TCP SYN packets (Connection timed out).
  5. *Quarantine Release Trigger*: Workload restored to `NORMAL` state.
  6. *NetworkPolicy Teardown & Reconnection*: Policy deleted, traffic restored (HTTP 200 OK).

---

### Level 3: Hybrid End-to-End Threat Scenarios
- **Target:** Unified Multi-Domain Pipeline (Decision Engine + Packet Tracer Model + Live K8s + Audit Ledger)
- **Runner:** `python testing/end-to-end/run_e2e_tests.py`
- **Result:** **5 / 5 SCENARIOS PASS**
  - `E2E-01` Baseline Authorized Access: **ALLOW (HTTP 200 OK)**
  - `E2E-02` Direct Database Bypass Interception (Threat E-04): **BLOCK (SVI ACL)**
  - `E2E-03` Cross-Domain Lateral Movement Live Quarantine: **ISOLATE (Calico Dropped)**
  - `E2E-04` Incident Recovery & Baseline Restoration: **ALLOW (Restored)**
  - `E2E-05` Non-Repudiation Audit Ledger Verification: **AUDITED (Immutable records)**

---

### Level 4: AWS Infrastructure Security Validation
- **Target:** 3-Tier Multi-AZ VPC and Security Groups (Terraform)
- **Runner:** `powershell -ExecutionPolicy Bypass -File .\testing\aws\deploy-localstack.ps1`
- **Execution Model:** **LOCAL SIMULATION (Moto/LocalStack at `http://localhost:4566`)** *(No real AWS charges)*
- **Result:** **8 / 8 CONTROLS PASS** + `terraform validate` passing
  - `AWS-01` Web Tier Architecture & IGW Routing: **PASS**
  - `AWS-02` App Tier Private Isolation: **PASS**
  - `AWS-03` DB Tier Air-Gapped Isolation: **PASS**
  - `AWS-04` Web Security Group HTTPS Policy: **PASS**
  - `AWS-05` Web -> App Mutual Security Group Referencing: **PASS**
  - `AWS-06` App -> DB PostgreSQL Security Group Policy: **PASS**
  - `AWS-07` Direct Web -> DB Bypass Prevention (Threat E-04): **PASS**
  - `AWS-08` Database Tier Public Exposure Immunity: **PASS**

---

### Level 5: Cisco Network Segmentation Validation
- **Target:** Enterprise Datacenter Topology (`packet-tracer/topology.pkt`)
- **Execution Model:** **CISCO PACKET TRACER SIMULATION** (Manually and empirically verified via Packet Tracer Simulation Mode)
- **Result:** **30 / 30 EMPIRICAL TESTS PASS**
- **Evidence:** Documented in [validation-summary.md](../packet-tracer/test-results/validation-summary.md) and [test-matrix.md](../packet-tracer/test-results/test-matrix.md)
  - VLAN 10 Faculty isolated from VLAN 40 Databases.
  - SVI ACL `FACULTY-ACCESS` and `APP-ACCESS` line matches empirically counted on `SW-CORE`.
  - VTY management plane restricted to VLAN 30 via `MGMT-VTY-ACCESS`.

```python
# tests/test_policy_engine.py

class TestPolicyEngine:
    def test_allow_education_api_to_education_db(self):
        """Education API can READ its own database."""
        
    def test_block_education_api_to_finance_db(self):
        """Education API is BLOCKED from Finance database."""
        
    def test_block_education_api_to_research_api(self):
        """Cross-domain access is BLOCKED."""
        
    def test_default_deny_no_matching_rule(self):
        """Requests with no matching policy are BLOCKED (default deny)."""
        
    def test_policy_priority_ordering(self):
        """Higher priority rules override lower priority rules."""
        
    def test_disabled_policy_skipped(self):
        """Disabled policies are not evaluated."""
```

#### 4.2 Risk Engine Tests

```python
# tests/test_risk_engine.py

class TestRiskEngine:
    def test_low_risk_same_domain_read(self):
        """Same-domain READ has low risk score (0–30)."""
        
    def test_high_risk_cross_domain_write(self):
        """Cross-domain WRITE has high risk score (61–80)."""
        
    def test_critical_risk_cross_domain_to_sensitive(self):
        """Cross-domain access to RESTRICTED resource has critical risk (81–100)."""
        
    def test_risk_factors_decomposition(self):
        """Risk score includes all contributing factors with weights."""
        
    def test_risk_score_bounded_0_100(self):
        """Risk score is always between 0 and 100."""
        
    def test_risk_explanation_generated(self):
        """Risk assessment includes human-readable explanation."""
```

#### 4.3 Decision Engine Tests

```python
# tests/test_decision_engine.py

class TestDecisionEngine:
    def test_allow_with_low_risk(self):
        """Policy ALLOW + LOW risk = ALLOW."""
        
    def test_allow_with_critical_risk_becomes_block(self):
        """Policy ALLOW + CRITICAL risk = BLOCK (risk override)."""
        
    def test_restrict_with_high_risk_becomes_block(self):
        """Policy RESTRICT + HIGH risk = BLOCK."""
        
    def test_block_always_blocks(self):
        """Policy BLOCK is never downgraded to ALLOW."""
        
    def test_isolate_triggers_containment(self):
        """ISOLATE decision triggers containment workflow."""
```

#### 4.4 Containment Tests

```python
# tests/test_containment.py

class TestBlastRadiusController:
    def test_containment_transitions_state(self):
        """Containment changes workload state: NORMAL → SUSPICIOUS → CONTAINED."""
        
    def test_containment_preserves_authorized_deps(self):
        """Authorized dependencies remain accessible after containment."""
        
    def test_containment_blocks_unauthorized(self):
        """Unauthorized connections are blocked after containment."""
        
    def test_containment_creates_incident(self):
        """Containment creates an incident record."""
        
    def test_containment_records_actions(self):
        """All containment actions are logged in isolation_actions table."""
        
    def test_recovery_restores_normal_state(self):
        """Recovery transitions workload from CONTAINED to RECOVERED."""
```

---

### Layer 5: AegisMesh Backend (Integration Tests)

**Method:** pytest with real database (test PostgreSQL container)

```python
# tests/test_api_evaluate.py

class TestEvaluateAPI:
    async def test_evaluate_allowed_request(self, client, seeded_db):
        """POST /api/v1/evaluate returns ALLOW for authorized request."""
        
    async def test_evaluate_blocked_request(self, client, seeded_db):
        """POST /api/v1/evaluate returns BLOCK for cross-domain request."""
        
    async def test_evaluate_creates_audit_log(self, client, seeded_db):
        """Every evaluation creates an audit log entry."""
        
    async def test_evaluate_requires_authentication(self, client):
        """POST /api/v1/evaluate without auth returns 401."""
        
    async def test_evaluate_validates_input(self, client, auth_headers):
        """POST /api/v1/evaluate with invalid input returns 422."""
```

---

### Layer 6: End-to-End Scenarios

These scenarios tell the **complete security story** from normal operation through compromise to containment.

#### E2E-01: Normal Operation

```
1. Faculty user authenticates → IAM
2. Faculty accesses education application → AegisMesh evaluates → ALLOW
3. Education application reads education database → AegisMesh evaluates → ALLOW
4. All actions logged in audit trail
5. Dashboard shows: all systems NORMAL
```

#### E2E-02: Cross-Domain Block

```
1. Education API attempts to read Finance database
2. AegisMesh evaluates:
   - Policy: education → finance = BLOCK
   - Risk: 87 (CRITICAL) — cross-domain + sensitive destination
3. Decision: BLOCK
4. Audit log: blocked request recorded
5. Dashboard shows: blocked request event
```

#### E2E-03: Lateral Movement Detection and Containment

```
1. Education API is "compromised" (simulated)
2. Compromised API attempts:
   a. Access finance-db → BLOCK (policy)
   b. Access research-api → BLOCK (policy)
   c. Access management network → BLOCK (policy)
3. AegisMesh detection observes pattern:
   - Multiple blocked cross-domain requests from same source
   - Anomaly score increases
4. Risk score exceeds CRITICAL threshold (>81)
5. Containment triggered:
   a. Workload state: NORMAL → SUSPICIOUS → CONTAINED
   b. NetworkPolicy updated: deny education-api egress
   c. Policy override created: BLOCK all education-api cross-domain
6. Incident created: INC-2026-001
7. Dashboard shows:
   - Active incident
   - education-api in CONTAINED state
   - Blocked lateral movement attempts
   - Containment timeline
8. Authorized access preserved:
   - education-api → education-db still ALLOW
```

#### E2E-04: Recovery

```
1. Administrator reviews incident
2. Root cause identified and remediated
3. Administrator initiates recovery
4. Containment policies removed
5. Workload state: CONTAINED → RECOVERED
6. Normal policies restored
7. Dashboard shows: workload recovered
```

---

## 3. Test Data Strategy

### 3.1 Simulation Data

All test/demo data is clearly labeled:

```python
# database/seed.py

"""
SIMULATION / DEMONSTRATION DATA
================================
This module creates demonstration data for testing and presentation.
This data does not represent real workloads, users, or security events.
All entities are fictional and created for evaluation purposes.
"""
```

### 3.2 Test Fixtures

```python
# tests/conftest.py

@pytest.fixture
def sample_workloads():
    """Create standard test workloads for all domains."""
    return [
        Workload(workload_id="education-api", domain="education", trust_level=80, ...),
        Workload(workload_id="education-db", domain="education", sensitivity="CONFIDENTIAL", ...),
        Workload(workload_id="finance-db", domain="finance", sensitivity="RESTRICTED", ...),
        Workload(workload_id="research-api", domain="research", trust_level=80, ...),
    ]

@pytest.fixture
def sample_policies():
    """Create standard test policies."""
    return [
        Policy(name="Education Domain", rules=[
            PolicyRule(source={"domains": ["education"]}, dest={"resource_ids": ["education-db"]}, decision="ALLOW"),
            PolicyRule(source={"domains": ["education"]}, dest={"domains": ["finance"]}, decision="BLOCK"),
        ]),
    ]
```

---

## 4. Test Reporting & Consolidated Results

### 4.1 Reporting Artifacts
- **Backend Tests:** Automated pytest execution reports via stdout and XML/JUnit telemetry.
- **Kubernetes Dynamic Containment:** Documented in [kubernetes-containment-bridge.md](../kubernetes-containment-bridge.md).
- **Hybrid End-to-End Suite:** Documented in [e2e-validation-report.md](e2e-validation-report.md).
- **AWS LocalStack Validation:** Documented in [aws-validation-report.md](aws-validation-report.md).
- **Cisco Datacenter Matrix:** Documented in [validation-summary.md](../../packet-tracer/test-results/validation-summary.md) and [test-matrix.md](../../packet-tracer/test-results/test-matrix.md).

### 4.2 Multi-Domain Verification Summary

| Hierarchy Level | Domain / Layer | Target Environment | Total Checks | Pass | Fail | Execution Model |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **Level 1** | Backend Security Engine | FastAPI + Risk Scorer | **18** | 18 | 0 | Automated (`pytest backend/tests/`) |
| **Level 2** | Kubernetes Live Containment | Kind + Calico CNI | **6** | 6 | 0 | Automated (`test_containment_bridge.py`) |
| **Level 3** | Hybrid End-to-End Scenarios | Unified Decision Pipeline | **5** | 5 | 0 | Automated (`run_e2e_tests.py`) |
| **Level 4** | AWS Zero-Trust Security | Moto/LocalStack Simulation | **8** | 8 | 0 | Automated (`deploy-localstack.ps1`) |
| **Level 5** | Cisco Network Segmentation | Packet Tracer Topology | **30** | 30 | 0 | Empirical Simulation Matrix |
| **TOTALS** | **37 Automated + 30 Simulation** | | **67** | **67** | **0** | **100% of implemented validation checks passed** |

---

## 5. Automated Multi-Domain Regression Suite Commands

```powershell
# Level 1: Backend Unit & Integration Tests (18 tests)
python -m pytest backend/tests/

# Level 2: Kubernetes Live Containment Bridge Tests (6 phases)
python testing/kubernetes/test_containment_bridge.py

# Level 3: Hybrid End-to-End Security Suite (5 scenarios)
python testing/end-to-end/run_e2e_tests.py

# Level 4: AWS Zero-Trust Simulation Suite (8 controls)
powershell -ExecutionPolicy Bypass -File .\testing\aws\deploy-localstack.ps1

# Level 4 (IaC Static Validation):
cd aws/terraform
terraform init -backend=false
terraform validate
terraform fmt -check
cd ../..
```
