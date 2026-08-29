# AegisMesh — Project Roadmap

**Version:** 1.0  
**Date:** 2026-08-28  
**Status:** DRAFT — Awaiting Approval  

---

## 1. Development Phases

This roadmap follows the strict 19-phase development order specified in the project requirements. Each phase has clear deliverables and acceptance criteria before moving to the next.

---

## 2. Phase Schedule

| Phase | Name | Duration | Dependencies | Key Deliverables |
|---|---|---|---|---|
| 1 | Requirements Analysis | ✅ Complete | None | `requirements.md` |
| 2 | Threat Model | ✅ Complete | Phase 1 | `threat-model.md` |
| 3 | Architecture Design | ✅ Complete | Phase 2 | `architecture.md`, `aegismesh-design.md` |
| 4 | Packet Tracer Network | 2–3 days | Phase 3 | `topology.pkt`, switch/router configs |
| 5 | Packet Tracer Testing | 1–2 days | Phase 4 | Test report with screenshots |
| 6 | Local Kubernetes Environment | 1–2 days | Phase 3 | kind cluster, Calico, namespaces |
| 7 | Kubernetes Security Controls | 2–3 days | Phase 6 | RBAC, NetworkPolicies, Pod Security |
| 8 | AWS Architecture | 1–2 days | Phase 3 | Terraform module design |
| 9 | Terraform Implementation | 2–3 days | Phase 8 | Working Terraform configs |
| 10 | AegisMesh Backend | 3–4 days | Phase 3 | FastAPI app, database, models |
| 11 | Policy Engine | 2–3 days | Phase 10 | Policy evaluation + unit tests |
| 12 | Risk Engine | 2–3 days | Phase 10 | Risk scoring + unit tests |
| 13 | Blast-Radius Controller | 2–3 days | Phase 11, 12 | Containment workflow + tests |
| 14 | Monitoring | 2–3 days | Phase 10 | Wazuh setup, event ingestion |
| 15 | Frontend Dashboard | 4–5 days | Phase 10 | Next.js dashboard, topology, incidents |
| 16 | Integration | 2–3 days | Phase 13, 14, 15 | Cross-component integration |
| 17 | End-to-End Testing | 2–3 days | Phase 16 | Complete scenario tests |
| 18 | Documentation | 2–3 days | Phase 17 | Final docs, README, presentation |
| 19 | Final Demonstration | 1–2 days | Phase 18 | Demo script, recording |

**Estimated total:** 30–45 days

---

## 3. Phase Details

### Phase 1: Requirements Analysis ✅

**Status:** Complete  
**Deliverables:**
- [requirements.md](file:///C:/Users/abhia/.gemini/antigravity-ide/scratch/AegisMesh/docs/requirements/requirements.md) — Functional, non-functional, and security requirements  
- [technology-stack.md](file:///C:/Users/abhia/.gemini/antigravity-ide/scratch/AegisMesh/docs/requirements/technology-stack.md) — Complete technology stack with justification  

---

### Phase 2: Threat Model ✅

**Status:** Complete  
**Deliverables:**
- [threat-model.md](file:///C:/Users/abhia/.gemini/antigravity-ide/scratch/AegisMesh/docs/architecture/threat-model.md) — STRIDE analysis, attack trees, trust boundaries  

---

### Phase 3: Architecture Design ✅

**Status:** Complete  
**Deliverables:**
- [architecture.md](file:///C:/Users/abhia/.gemini/antigravity-ide/scratch/AegisMesh/docs/architecture/architecture.md) — System architecture  
- [network-design.md](file:///C:/Users/abhia/.gemini/antigravity-ide/scratch/AegisMesh/docs/architecture/network-design.md) — Private datacenter network design  
- [aws-design.md](file:///C:/Users/abhia/.gemini/antigravity-ide/scratch/AegisMesh/docs/architecture/aws-design.md) — AWS cloud architecture  
- [kubernetes-design.md](file:///C:/Users/abhia/.gemini/antigravity-ide/scratch/AegisMesh/docs/architecture/kubernetes-design.md) — Kubernetes security design  
- [aegismesh-design.md](file:///C:/Users/abhia/.gemini/antigravity-ide/scratch/AegisMesh/docs/architecture/aegismesh-design.md) — AegisMesh engine design  
- [testing-strategy.md](file:///C:/Users/abhia/.gemini/antigravity-ide/scratch/AegisMesh/docs/testing/testing-strategy.md) — Testing strategy  

---

### Phase 4: Packet Tracer Network

**Status:** Pending  
**Objective:** Build the private datacenter network in Cisco Packet Tracer.

**Deliverables:**
- `packet-tracer/topology.pkt` — Complete topology file
- `packet-tracer/configurations/*.txt` — Device running configurations
- 3 access switches, 1 core L3 switch, 1 edge router
- 6 VLANs configured
- Inter-VLAN routing on core switch
- DHCP for Faculty VLAN
- All access ports assigned to correct VLANs
- Trunk links configured between switches

**Acceptance:** All devices reachable within their VLAN; trunk links operational.

---

### Phase 5: Packet Tracer Security Testing

**Status:** Pending  
**Objective:** Implement ACLs and verify all 10 test cases.

**Deliverables:**
- ACLs applied on core switch SVIs
- `packet-tracer/test-results/test-report.md`
- Screenshots for each test (PT-01 through PT-10)
- Both ALLOW and BLOCK verified

**Acceptance:** All 10 tests pass with documented evidence.

---

### Phase 6: Local Kubernetes Environment

**Status:** Pending  
**Objective:** Set up kind cluster with Calico CNI.

**Deliverables:**
- `kubernetes/cluster/kind-config.yaml`
- Working kind cluster with 3 nodes
- Calico CNI installed
- 5 namespaces created (education, research, finance, aegismesh-system, monitoring)
- Namespace labels applied

**Acceptance:** `kubectl get nodes` shows 3 Ready nodes; `kubectl get ns` shows all namespaces.

---

### Phase 7: Kubernetes Security Controls

**Status:** Pending  
**Objective:** Implement RBAC, NetworkPolicies, and Pod Security.

**Deliverables:**
- `kubernetes/rbac/*.yaml`
- `kubernetes/network-policies/*.yaml`
- `kubernetes/deployments/*/*.yaml` — Sample workloads per namespace
- `kubernetes/resource-controls/*.yaml`
- Test script: `testing/kubernetes/run-tests.sh`

**Acceptance:** All 10 Kubernetes tests (K8S-01 through K8S-10) pass.

---

### Phase 8: AWS Architecture

**Status:** Pending  
**Objective:** Design Terraform module structure for AWS resources.

**Deliverables:**
- `infrastructure/terraform/` — Module structure
- `infrastructure/terraform/variables.tf` — All variables defined
- `infrastructure/terraform/terraform.tfvars.example`

**Acceptance:** Terraform structure reviewed; no AWS resources created yet.

---

### Phase 9: Terraform Implementation

**Status:** Pending  
**Objective:** Implement and validate Terraform configurations.

**Deliverables:**
- All Terraform modules implemented
- `terraform plan` succeeds without errors
- All AWS tests (AWS-01 through AWS-10) verified via plan output

**Acceptance:** `terraform plan` shows expected resources; no VPC peering between A/B/C.

---

### Phase 10: AegisMesh Backend

**Status:** Pending  
**Objective:** Build FastAPI application skeleton with database.

**Deliverables:**
- `backend/app/main.py` — FastAPI application
- `backend/app/models/` — SQLAlchemy models + Pydantic schemas
- `backend/app/database/` — Session management + Alembic migrations
- `backend/app/api/v1/` — All endpoint stubs
- `backend/docker-compose.yml` — Backend + PostgreSQL
- `backend/Dockerfile`
- Health check endpoint working

**Acceptance:** `POST /api/v1/health` returns 200; database migrations run successfully.

---

### Phase 11: Policy Engine

**Status:** Pending  
**Objective:** Implement policy evaluation logic.

**Deliverables:**
- `backend/app/policy_engine/` — Complete policy engine
- Policy CRUD endpoints working
- Policy evaluation logic with priority ordering and default deny
- Unit tests: `tests/test_policy_engine.py`
- Seed policies for education/research/finance domains

**Acceptance:** All policy engine unit tests pass; API endpoints return correct decisions.

---

### Phase 12: Risk Engine

**Status:** Pending  
**Objective:** Implement risk scoring logic.

**Deliverables:**
- `backend/app/risk_engine/` — Complete risk engine
- 6 risk factors implemented
- Weighted score computation (0–100)
- Risk level classification
- Factor decomposition in response
- Unit tests: `tests/test_risk_engine.py`

**Acceptance:** All risk engine unit tests pass; scores bounded 0–100; explanations generated.

---

### Phase 13: Blast-Radius Controller

**Status:** Pending  
**Objective:** Implement containment workflow.

**Deliverables:**
- `backend/app/containment/` — Complete controller
- Workload state machine (NORMAL → SUSPICIOUS → CONTAINED → RECOVERED)
- Containment action recording
- Incident creation on containment
- Integration with policy engine (override policies)
- Unit tests: `tests/test_containment.py`

**Acceptance:** Containment workflow transitions states correctly; actions recorded; incident created.

---

### Phase 14: Monitoring

**Status:** Pending  
**Objective:** Set up Wazuh and connect to AegisMesh.

**Deliverables:**
- `monitoring/wazuh/docker-compose.yml`
- Event ingestion endpoint working
- Security event processing
- Alert forwarding to AegisMesh

**Acceptance:** Wazuh running; events received and stored in AegisMesh database.

---

### Phase 15: Frontend Dashboard

**Status:** Pending  
**Objective:** Build the Next.js security dashboard.

**Deliverables:**
- Next.js application with App Router
- 8 pages: dashboard, topology, workloads, policies, incidents, risk, audit, settings
- React Flow topology visualization
- Recharts risk and metrics charts
- Real-time data from backend API
- Professional enterprise design

**Acceptance:** All pages render; data from API displayed; topology interactive.

---

### Phase 16: Integration

**Status:** Pending  
**Objective:** Connect all components end-to-end.

**Deliverables:**
- Backend connected to Kubernetes API (for NetworkPolicy management)
- Dashboard displaying live data from backend
- Event flow: detection → risk → policy → decision → containment → dashboard
- Cross-component communication verified

**Acceptance:** Full evaluation pipeline working; containment triggers NetworkPolicy updates.

---

### Phase 17: End-to-End Testing

**Status:** Pending  
**Objective:** Execute all 4 end-to-end scenarios.

**Deliverables:**
- `testing/end-to-end/` — Scenario scripts and results
- E2E-01: Normal operation verified
- E2E-02: Cross-domain block verified
- E2E-03: Lateral movement containment verified
- E2E-04: Recovery verified

**Acceptance:** All 4 scenarios documented with evidence.

---

### Phase 18: Documentation

**Status:** Pending  
**Objective:** Final documentation and presentation materials.

**Deliverables:**
- `README.md` — Project overview, setup, architecture
- `docs/implementation/` — Implementation details
- `docs/deployment/` — Deployment guide
- Presentation slides or script
- Architecture diagrams (final)

**Acceptance:** A reviewer can understand, deploy, and evaluate the project from documentation alone.

---

### Phase 19: Final Demonstration

**Status:** Pending  
**Objective:** Prepare and execute the final demonstration.

**Deliverables:**
- Demo script following the coherent story: Normal → Threat → Detection → Containment → Resolution
- Screen recording (if required)
- Live demo capability

**Acceptance:** Demo tells one coherent story with evidence at each stage.

---

## 4. Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Scope creep | HIGH | Delays | Strict phase gating; no phase skipping |
| AWS cost overrun | MEDIUM | Budget | Free-tier only; terraform destroy after testing |
| kind networking issues | MEDIUM | K8s tests fail | Use Calico CNI; test early |
| Packet Tracer limitations | LOW | Incomplete demo | Document limitations; architecture diagrams supplement |
| Single developer velocity | HIGH | Delays | Focus on core story (segmentation + containment); defer nice-to-haves |

---

## 5. Critical Path

The critical path through the project is:

```
Phase 3 (Architecture) →
  Phase 10 (Backend) →
    Phase 11 (Policy Engine) →
      Phase 12 (Risk Engine) →
        Phase 13 (Containment) →
          Phase 16 (Integration) →
            Phase 17 (E2E Testing)
```

Phases 4–9 (infrastructure) can proceed **in parallel** with Phases 10–13 (backend) since they have no code dependencies. The frontend (Phase 15) depends on Phase 10 (API endpoints) but can start UI scaffolding earlier.

---

## 6. Next Steps

**Immediate next action (Phase 4):**
1. Open Cisco Packet Tracer
2. Build the topology from `network-design.md`
3. Configure VLANs, trunking, SVIs, DHCP
4. Document device configurations
5. Proceed to Phase 5 (ACL implementation and testing)

**Or, if proceeding with backend first (Phase 10):**
1. Initialize FastAPI project structure
2. Set up Docker Compose with PostgreSQL
3. Create SQLAlchemy models
4. Run initial Alembic migration
5. Implement health check endpoint
