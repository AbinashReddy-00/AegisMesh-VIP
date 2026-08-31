# AegisMesh — 2–3 Minute Executive Demonstration Guide

**Project:** AegisMesh — Secure Hybrid Datacenter & Cloud Decision Engine  
**Program:** Cisco Virtual Internship 2026 Cyber Security  
**Target Audience:** Evaluators, Technical Judges, and Network Security Engineers  

---

## Demonstration Overview

> **Core Objective:** Prove in under 3 minutes that AegisMesh enforces Zero-Trust access control, blocks lateral movement, computes deterministic risk scores, and dynamically contains compromised workloads across a hybrid enterprise topology.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               2-MINUTE DEMO NARRATIVE                                 │
│                                                                                        │
│  [1. Normal Access]  ──▶ [2. Threat Detection] ──▶ [3. Risk Calculation]               │
│  Faculty -> App          Faculty -> DB Bypass       6-Factor Decomposition             │
│  (Status: ALLOW)         (Threat: E-04)             (Score: 77/100 HIGH)               │
│                                                                                        │
│                                      │                                                 │
│                                      ▼                                                 │
│  [6. Audit & Recovery] ◀── [5. Auto-Quarantine] ◀── [4. Policy Enforcement]             │
│  Immutable Ledger        Workload -> CONTAINED      SVI ACL Line 4 Drops               │
│  1-Click Restore         Blast-Radius Contained     (Status: BLOCK / ISOLATE)          │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Demonstration Script

### Step 1: Launch the Command Center (15 seconds)
1. Run `python run.py` in your terminal.
2. The browser opens automatically to [`http://127.0.0.1:8000/`](http://127.0.0.1:8000/).
3. **Show the Evaluator:**
   - The **SIMULATION MODE** telemetry banner at the top.
   - The **Executive KPI bar** displaying 16 Monitored Assets across 3 Domains (`Private DC`, `AWS Cloud`, `Kubernetes`).
   - The **Hybrid Architecture Topology Canvas** and test switching between domain filter tabs (`🏢 Private DC`, `☁️ AWS Cloud`, `☸️ Kubernetes`).

---

### Step 2: Demonstrate Normal Authorized Access (30 seconds)
1. Click **`SCENARIO 1 (BASELINE ALLOWED)`** in the Threat Simulation suite.
2. **Explain to the Evaluator:**
   - *"Here, a faculty user on `FAC-PC-01` (VLAN 10) connects to the authorized academic web application on `APP-SRV-01` (VLAN 20)."*
3. **Show the Output:**
   - **Verdict:** **`ALLOW`** (Emerald badge).
   - **Risk Score:** **`18/100 (LOW)`** — Minimal destination sensitivity, standard academic workflow.
   - **Packet Trace:** Shows packet routed across SVI Vlan10 to Vlan20 via `FACULTY-ACCESS` Rule 1.

---

### Step 3: Demonstrate Attack Interception & Risk Calculation (45 seconds)
1. Click **`SCENARIO 2 (THREAT E-04: DIRECT DB BYPASS)`**.
2. **Explain to the Evaluator:**
   - *"Now, an attacker on the faculty subnet attempts to bypass the web tier and query the sensitive enterprise database `DB-SRV-01` (10.10.40.10) directly."*
3. **Show the Output:**
   - **Verdict:** **`BLOCK`** (Crimson badge).
   - **Risk Engine:** Computes risk at **`77/100 (HIGH)`**.
   - **6-Factor Breakdown Table:** Point out the elevated *Destination Sensitivity (95)* and *Cross-Zone Boundary Penalty (90)*.
   - **Enforcement Layer:** Cisco Core Switch SVI Ingress ACL (`FACULTY-ACCESS` Line 4 deny statement).
   - **Packet Trace:** Highlights the exact match rule and packet drop on `SW-CORE`.

---

### Step 4: Demonstrate Automated Blast-Radius Containment (45 seconds)
1. Click **`SCENARIO 5 (THREAT I-01: CROSS-DOMAIN LATERAL EXFILTRATION)`**.
2. **Explain to the Evaluator:**
   - *"In this scenario, a compromised container pod in the Kubernetes education namespace attempts cross-domain lateral exfiltration toward the restricted Finance Database."*
3. **Show the Output:**
   - **Verdict:** **`ISOLATE`** (Neon Pink badge).
   - **Risk Score:** **`82/100 (CRITICAL)`**.
   - **Automated Blast-Radius Containment:**
     - The node `k8s-edu-api` immediately turns **magenta** in the topology canvas with a `CONTAINED` status badge.
     - Top KPI bar updates: **`Quarantined Nodes: 1`**.
     - An active incident record appears in the **Blast-Radius Containment & Incidents** panel showing dynamic NetworkPolicy egress lockdown.

---

### Step 5: Incident Resolution & Audit Non-Repudiation (15 seconds)
1. In the **Blast-Radius Containment & Incidents** panel, click **`Lift Quarantine`**.
2. **Explain to the Evaluator:**
   - *"Once the security operations team reviews the containment actions, a single click restores the workload to `NORMAL` baseline trust."*
3. **Show the Audit Trail:**
   - Point to the **Live Decision Audit Trail** showing immutable timestamped records for every evaluated flow, risk score, quarantine, and restoration action.

---

## 🧪 Optional: Automated Multi-Domain CLI Demonstration (30 seconds)

For evaluators seeking automated terminal validation, demonstrate the multi-domain regression suites:

```powershell
# 1. Backend Security & Risk Engine Suite (18 tests)
python -m pytest backend/tests/

# 2. Live Kubernetes Calico Containment Suite (6 phases)
python testing/kubernetes/test_containment_bridge.py

# 3. Hybrid End-to-End Security Validation (5 scenarios)
python testing/end-to-end/run_e2e_tests.py

# 4. AWS Zero-Trust Local Simulation Suite (8 controls)
powershell -ExecutionPolicy Bypass -File .\testing\aws\deploy-localstack.ps1
```

> **Consolidated Validation Result:** **37 / 37 Automated Validations Passed (100% of implemented validation checks passed)**

---

## Key Talking Points for Evaluators

1. **Defense-in-Depth:** AegisMesh is not just static firewall rules; it is an intelligent decision plane that coordinates Cisco Packet Tracer network ACLs, AWS Security Groups, and Kubernetes NetworkPolicies.
2. **State Consistency:** When form inputs are modified, the evaluator flags previous results as stale, preventing invalid policy claims.
3. **Deterministic & Explainable:** Every risk score (0–100) is decomposed into 6 explainable factors with human-readable rationales.
4. **Transparent Validation:** Every domain is verified with empirical tests across live local Kubernetes, local AWS API simulation, and Cisco Packet Tracer network simulation.
