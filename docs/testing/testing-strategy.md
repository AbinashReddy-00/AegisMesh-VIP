# AegisMesh — Testing Strategy

**Version:** 1.0  
**Date:** 2026-08-28  
**Status:** DRAFT — Awaiting Approval  
**Traces to:** NFR-04, AC-01, AC-02, AC-03  

---

## 1. Testing Philosophy

### Core Principle: Bidirectional Verification

For every security boundary, we prove **BOTH** directions:

1. ✅ **Authorized traffic succeeds** — the system does not break legitimate workflows.
2. ❌ **Unauthorized traffic fails** — the security boundary is enforced.

A test that only shows "it works" is incomplete. A test that only shows "it blocks" is incomplete. Both are required to demonstrate **least privilege**.

### Testing Pyramid

```
        ╱╲
       ╱  ╲         End-to-End Tests (Scenario)
      ╱    ╲         ~5 scenarios
     ╱──────╲
    ╱        ╲       Integration Tests (API + DB)
   ╱          ╲       ~30 tests
  ╱────────────╲
 ╱              ╲    Unit Tests (Engines + Logic)
╱                ╲    ~100+ tests
╱──────────────────╲
```

---

## 2. Test Layers

### Layer 1: Private Datacenter (Packet Tracer)

**Method:** Manual testing with Cisco Packet Tracer Simulation Mode  
**Evidence:** Screenshots + command outputs  

| Test ID | Source | Destination | Method | Expected | Security Principle |
|---|---|---|---|---|---|
| PT-01 | FAC-PC-01 (VLAN 10) | APP-SRV-01 (VLAN 20) | Ping + HTTP | ✅ ALLOW | Faculty can access applications |
| PT-02 | FAC-PC-01 (VLAN 10) | DB-SRV-01 (VLAN 40) | Ping | ❌ BLOCK | Faculty cannot access databases |
| PT-03 | FAC-PC-01 (VLAN 10) | MGMT-SRV-01 (VLAN 30) | Ping | ❌ BLOCK | Faculty cannot access management |
| PT-04 | APP-SRV-01 (VLAN 20) | DB-SRV-01 (VLAN 40) | Ping + TCP 3306 | ✅ ALLOW | Apps can access databases |
| PT-05 | APP-SRV-01 (VLAN 20) | MGMT-SRV-01 (VLAN 30) | Ping | ❌ BLOCK | Apps cannot access management |
| PT-06 | DMZ-SRV-01 (VLAN 60) | DB-SRV-01 (VLAN 40) | Ping | ❌ BLOCK | DMZ cannot access databases |
| PT-07 | DMZ-SRV-01 (VLAN 60) | MGMT-SRV-01 (VLAN 30) | Ping | ❌ BLOCK | DMZ cannot access management |
| PT-08 | DMZ-SRV-01 (VLAN 60) | APP-SRV-01 (VLAN 20) | Ping + HTTP | ✅ ALLOW | DMZ can reach app servers |
| PT-09 | DB-SRV-01 (VLAN 40) | FAC-PC-01 (VLAN 10) | Ping | ❌ BLOCK | Database cannot reach faculty |
| PT-10 | FAC-PC-01 (VLAN 10) | DHCP | DHCP Request | ✅ ALLOW | DHCP is functional |

**Verification commands:**
```
show vlan brief
show ip interface brief
show ip route
show access-lists
show running-config
show interfaces trunk
```

**Documentation:** Each test result will include:
- Screenshot of the test in Simulation Mode
- Command output confirming the configuration
- Pass/Fail determination

---

### Layer 2: AWS Cloud (Terraform)

**Method:** Terraform plan validation + AWS CLI verification  
**Evidence:** Terraform plan output + AWS CLI command results  

| Test ID | Test | Method | Expected |
|---|---|---|---|
| AWS-01 | No VPC peering between Education and Research | `terraform plan` + `aws ec2 describe-vpc-peering-connections` | No peering exists |
| AWS-02 | No VPC peering between Education and Finance | `terraform plan` | No peering exists |
| AWS-03 | No VPC peering between Research and Finance | `terraform plan` | No peering exists |
| AWS-04 | Education app SG allows only app-port from ALB | `aws ec2 describe-security-groups` | Only ALB SG source |
| AWS-05 | Education DB SG allows only 5432 from app SG | `aws ec2 describe-security-groups` | Only app SG source |
| AWS-06 | Finance VPC has no public subnets | `aws ec2 describe-subnets` | No IGW route |
| AWS-07 | Education IAM role cannot access Finance S3 | `aws iam simulate-principal-policy` | ❌ AccessDenied |
| AWS-08 | CloudTrail is enabled | `aws cloudtrail describe-trails` | Trail active |
| AWS-09 | VPC Flow Logs are enabled | `aws ec2 describe-flow-logs` | Logs active |
| AWS-10 | Security VPC can reach Education VPC | Route table inspection | Peering route exists |

---

### Layer 3: Kubernetes

**Method:** kubectl commands + automated test scripts  
**Evidence:** Command outputs  

| Test ID | Test | Method | Expected |
|---|---|---|---|
| K8S-01 | education-api → education-db (5432) | `kubectl exec` + `nc -zv` | ✅ ALLOW |
| K8S-02 | education-api → research-api (8080) | `kubectl exec` + `nc -zv` | ❌ TIMEOUT |
| K8S-03 | education-api → finance-db (5432) | `kubectl exec` + `nc -zv` | ❌ TIMEOUT |
| K8S-04 | research-api → education-db (5432) | `kubectl exec` + `nc -zv` | ❌ TIMEOUT |
| K8S-05 | finance-api → finance-db (5432) | `kubectl exec` + `nc -zv` | ✅ ALLOW |
| K8S-06 | education SA cannot list pods in finance | `kubectl auth can-i` | ❌ no |
| K8S-07 | education SA cannot read finance secrets | `kubectl auth can-i` | ❌ no |
| K8S-08 | Pods run as non-root | `kubectl get pod -o yaml` | `runAsNonRoot: true` |
| K8S-09 | Resource quotas enforced | `kubectl describe quota` | Quotas set |
| K8S-10 | Post-containment: education-api isolated | `kubectl exec` + `nc -zv` | ❌ All blocked |

**Automated test script:**
```bash
#!/bin/bash
# kubernetes/test-network-policies.sh

echo "=== K8S Network Policy Tests ==="

echo "[K8S-01] education-api → education-db:5432"
kubectl exec -n education deploy/education-api -- nc -zv -w 3 education-db 5432
echo "Expected: ALLOW"

echo "[K8S-02] education-api → research-api:8080"
kubectl exec -n education deploy/education-api -- nc -zv -w 3 research-api.research.svc.cluster.local 8080
echo "Expected: BLOCK (timeout)"

echo "[K8S-03] education-api → finance-db:5432"
kubectl exec -n education deploy/education-api -- nc -zv -w 3 finance-db.finance.svc.cluster.local 5432
echo "Expected: BLOCK (timeout)"
```

---

### Layer 4: AegisMesh Backend (Unit Tests)

**Framework:** pytest + pytest-asyncio  
**Coverage target:** >80% for security-critical modules  

#### 4.1 Policy Engine Tests

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

## 4. Test Reporting

### 4.1 Format

Each test layer produces a report documenting:

1. **Test ID** and description
2. **Input** (what was tested)
3. **Expected outcome**
4. **Actual outcome**
5. **Evidence** (screenshot, command output, or test log)
6. **Pass/Fail**

### 4.2 Test Summary Table (Template)

| Layer | Total | Pass | Fail | Coverage |
|---|---|---|---|---|
| Packet Tracer | 10 | — | — | — |
| AWS | 10 | — | — | — |
| Kubernetes | 10 | — | — | — |
| Unit Tests | ~100 | — | — | >80% |
| Integration Tests | ~30 | — | — | — |
| End-to-End | 4 | — | — | — |

---

## 5. Continuous Testing

### 5.1 Development Workflow

```
Code change → Unit tests (local) → Integration tests (Docker) → PR review → Deploy
```

### 5.2 CI Commands

```bash
# Unit tests
pytest tests/ -v --cov=app --cov-report=html

# Integration tests (requires Docker)
docker-compose -f docker-compose.test.yml up -d
pytest tests/integration/ -v
docker-compose -f docker-compose.test.yml down

# Kubernetes tests (requires kind cluster)
./testing/kubernetes/run-tests.sh
```
