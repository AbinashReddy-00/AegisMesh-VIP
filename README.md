# AegisMesh

<div align="center">

![AegisMesh](https://img.shields.io/badge/AegisMesh-Security%20Platform-0073E6?style=for-the-badge)
![CISCO VIP](https://img.shields.io/badge/CISCO-VIP%202026-FF6B1A?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-51.4%25-3776AB?style=for-the-badge)
![JavaScript](https://img.shields.io/badge/JavaScript-20.8%25-F7DF1E?style=for-the-badge)

</div>

> **Secure Hybrid Datacenter and Cloud Security Architecture & Decision Engine**  
> Cisco Virtual Internship 2026 — Cyber Security Project

---

## Executive Overview

An enterprise operates a hybrid infrastructure spanning a **private datacenter** and **public cloud (AWS)**. Workloads run as traditional server applications and Kubernetes-orchestrated microservices. The challenge: **how do we prevent lateral movement after compromise?**

> **Primary Security Objective:** If one application or workload is compromised, the compromise must not be able to spread laterally to unauthorized applications, VPCs, Kubernetes workloads, or the datacenter.

**AegisMesh** is the security control and decision architecture that enforces this objective across all infrastructure domains through **Zero-Trust policy evaluation**, **multi-factor risk scoring**, and **dynamic containment**.

---

## 📸 Interactive Cyber Command Center Dashboard

The AegisMesh platform includes an interactive, glassmorphic Cyber Command Center web dashboard (`http://localhost:8000/`) allowing evaluators to inspect the hybrid topology, run canned attack simulations, and observe real-time containment decisions.

| Command Center View | Architectural Coverage & Features |
|---|---|
| ![Dashboard Overview](docs/assets/dashboard-overview.png) | **Executive Command Center:** Real-time KPI stat bar, 1-click threat simulation suite, live packet flow terminal, and custom Zero-Trust decision traceability. |
| ![Private Datacenter Topology](docs/assets/topology-private-dc.png) | **Private Datacenter Domain:** Cisco Packet Tracer architecture model (VLANs 10–60, SVI routing, and extended ACL enforcement). |
| ![AWS Cloud Topology](docs/assets/topology-aws-cloud.png) | **AWS Public Cloud Domain:** Multi-VPC architecture (VPCs A–D), tiered subnets, and security group isolation boundaries. |
| ![Kubernetes Platform Topology](docs/assets/topology-kubernetes.png) | **Kubernetes Container Domain:** Namespace isolation (`education`, `research`, `finance`), RBAC, and Calico default-deny NetworkPolicies. |
| ![Blast-Radius Containment & Audit](docs/assets/containment-and-audit.png) | **Containment & Audit Stream:** Active incident quarantine management, 1-click remediation, and immutable security decision ledger. |

👉 **[View the Complete 2-3 Minute Demonstration Walkthrough Guide](docs/demonstration-guide.md)**

---

## Solution Architecture

AegisMesh implements a **three-domain security architecture** with defense-in-depth controls at every layer:

```
                         ┌─────────────────────┐
                         │   USERS / FACULTY    │
                         │  Campus + Remote VPN │
                         └──────────┬──────────┘
                                    │
                         ┌──────────┴──────────┐
                         │   IDENTITY / IAM     │
                         │   MFA + RBAC + Tokens│
                         └──────────┬──────────┘
                                    │
             ┌────────────────────────┼────────────────────────┐
             │                        │                        │
  ┌──────────┴──────────┐  ┌─────────┴─────────┐  ┌──────────┴────────┐
  │  PRIVATE DATACENTER │  │    AWS CLOUD       │  │  KUBERNETES CLUSTER │
  │                     │  │                    │  │                     │
  │  6 VLANs + ACLs     │  │  4 VPCs + SGs      │  │  5 Namespaces       │
  │  SVI Routing        │  │  IAM Policies      │  │  NetworkPolicies    │
  │  Trunk Hardening    │  │  NACLs             │  │  RBAC + PSS         │
  │  VTY Restriction    │  │  CloudTrail Logs   │  │  Resource Quotas    │
  │                     │  │                    │  │                     │
  │  ✅ IMPLEMENTED     │  │  ✅ TERRAFORM IaC  │  │  ✅ IMPLEMENTED     │
  │  ✅ VALIDATED (PT)  │  │  ✅ VALIDATED (IaC)│  │  ✅ VALIDATED (K8s) │
  └──────────┬──────────┘  └─────────┬──────────┘  └─────────┬──────────┘
             │                       │                        │
             └───────────────────────┼────────────────────────┘
                                    │
                         ┌──────────┴──────────┐
                         │   AEGISMESH ENGINE   │
                         │   Policy + Risk +    │
                         │   Containment        │
                         │   (FastAPI Backend)  │
                         └──────────┬──────────┘
                                    │
                         ┌──────────┴──────────┐
                         │  COMMAND DASHBOARD  │
                         │  Live SOC Telemetry │
                         └─────────────────────┘
```

---

## ⚡ Quickstart — Running the Platform Locally

AegisMesh is fully runnable with zero external database dependencies:

```powershell
# 1. Install lightweight Python dependencies
pip install -r requirements.txt

# 2. Launch the single-command runner
python run.py
```

- **Interactive Cyber Command Center:** [`http://127.0.0.1:8000/`](http://127.0.0.1:8000/) *(Opens automatically in your browser)*
- **OpenAPI / Swagger Documentation:** [`http://127.0.0.1:8000/api/docs`](http://127.0.0.1:8000/api/docs)
- **Run Automated Test Suite:**
  ```powershell
  python -m pytest backend/tests/test_engine.py
  ```

---

## Key Security Features

| # | Feature | Implementation |
|:---:|---|---|
| 1 | **Hybrid Connectivity** | IPsec VPN between Private DC and AWS VPC-D (architecturally designed) |
| 2 | **Cloud VPC Segmentation** | 4 isolated VPCs: Education, Research, Finance, Security/Management |
| 3 | **Public/Private Subnet Architecture** | Tiered subnets; Finance VPC has zero public subnets |
| 4 | **IAM/RBAC with Least Privilege & MFA** | Per-domain IAM roles with explicit cross-domain deny; MFA enforced |
| 5 | **Cloud Security Groups** | Per-instance SG rules; SG-to-SG references; default deny inbound |
| 6 | **Application Isolation** | VLANs (DC) + VPC boundaries (AWS) + NetworkPolicies (K8s) |
| 7 | **Lateral Movement Prevention** | ACLs, VPC isolation, default-deny NetworkPolicies at every boundary |
| 8 | **Kubernetes Security** | RBAC, Pod Security Standards, ResourceQuotas, ServiceAccount isolation |
| 9 | **Namespace Isolation** | Default-deny ingress/egress per namespace; no cross-namespace traffic |
| 10 | **Secure Faculty Remote Access** | VPN + MFA; same restrictions as on-campus; split tunnel disabled |
| 11 | **Zero Trust Architecture** | No implicit trust from network location; continuous evaluation |
| 12 | **Monitoring & Security Logging** | Dedicated Security VLAN 50, immutable decision audit ledger |
| 13 | **Incident Containment** | AegisMesh blast-radius controller; dynamic policy lockdown |

---

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Private Datacenter** | Cisco Packet Tracer 8.2+ | Enterprise network simulation with VLAN/ACL enforcement |
| **Security Decision Engine** | Python 3.12, FastAPI, Pydantic | Centralized zero-trust evaluation, 6-factor risk scoring, containment |
| **Cyber Dashboard** | Modern HTML5, Vanilla CSS Glassmorphism, ES6 | Interactive hybrid topology, live packet traces, risk gauges, incident management |
| **Cloud (Architecture)** | AWS + Terraform | Multi-VPC public cloud with IAM, Security Groups, and CloudTrail |
| **Containers (Architecture)** | Kubernetes (kind) + Calico CNI | Namespace isolation with real NetworkPolicy enforcement |
| **Verification & Testing** | Pytest, TestClient, Packet Tracer CLI | Automated regression testing and empirical network validation |

---

## Implementation Status

| Component | Status | Evidence |
|---|---|---|
| **Private Datacenter Network** | **IMPLEMENTED AND VALIDATED** | Cisco Packet Tracer topology (`packet-tracer/topology.pkt`) |
| **VLAN Segmentation (6 zones)** | **IMPLEMENTED AND VALIDATED** | `show vlan brief`, device configurations |
| **Extended ACL Enforcement** | **IMPLEMENTED AND VALIDATED** | `show access-lists` with verified match counters |
| **Trunk Hardening (DTP, Native VLAN 99)** | **IMPLEMENTED AND VALIDATED** | `show interfaces trunk` |
| **VTY Management Isolation** | **IMPLEMENTED AND VALIDATED** | `MGMT-VTY-ACCESS` ACL on VTY lines |
| **AegisMesh Security Engine** | **IMPLEMENTED AND RUNNABLE** | FastAPI backend with zero-trust policy, risk, decision, and containment engines |
| **Cyber Command Center Dashboard** | **IMPLEMENTED AND RUNNABLE** | Interactive web dashboard served live at `http://localhost:8000/` |
| **Kubernetes Security Lab** | **LOCALLY IMPLEMENTED & VALIDATED** | Kind cluster + Project Calico CNI + RBAC + NetworkPolicies (`testing/kubernetes/run-k8s-tests.ps1`) |
| **Dynamic Containment Bridge** | **LOCALLY IMPLEMENTED & VALIDATED** | AegisMesh $\to$ Kubernetes API $\to$ Calico Dynamic Isolation & Release (`testing/kubernetes/test_containment_bridge.py`) |
| **Automated End-to-End Test Suite** | **IMPLEMENTED & VALIDATED** | 5/5 Scenarios passing (`testing/end-to-end/run_e2e_tests.py`) |
| **AWS Cloud Infrastructure** | **Terraform Infrastructure Implemented & Locally Validated** | Production 3-Tier Multi-AZ Terraform modules + `terraform validate` passing (Not applied to live AWS) |

| **Threat Model (STRIDE)** | **COMPLETED & DOCUMENTED** | 21 threats, 11 trust boundaries, attack trees |
| **Threat Traceability** | **COMPLETED & DOCUMENTED** | 14-row authoritative threat matrix (`docs/threat-traceability.md`) |


---

## Repository Structure

```
AegisMesh/
├── README.md                                    # Project overview & documentation (this file)
├── requirements.txt                              # Lightweight Python dependencies
├── run.py                                        # Single-command launcher (FastAPI + Dashboard)
├── .gitignore                                   # Repository hygiene rules
│
├── backend/                                     # AegisMesh Security Decision Engine
│   ├── app/
│   │   ├── main.py                               # FastAPI entry point & static mounting
│   │   ├── models/                               # Domain enums & Pydantic request/response schemas
│   │   ├── database/                             # In-memory store & seed data engine
│   │   ├── policy_engine/                        # Zero-Trust policy matcher & default-deny rules
│   │   ├── risk_engine/                          # 6-factor composite risk scorer (0–100)
│   │   ├── decision_engine/                      # Decision matrix combiner & human rationale generator
│   │   ├── containment/                          # Blast-radius state machine (NORMAL → CONTAINED)
│   │   └── api/v1/                               # REST API endpoints (/evaluate, /simulate, /isolate)
│   └── tests/
│       └── test_engine.py                        # Automated pytest suite (8 passing tests)
│
├── frontend/                                    # Interactive Cyber Command Center Dashboard
│   ├── index.html                                # Executive dashboard single-page interface
│   ├── css/
│   │   └── dashboard.css                         # Dark glassmorphism, responsive grid, status badges
│   └── js/
│       ├── api.js                                # REST client for backend communication
│       ├── topology.js                           # Interactive SVG hybrid topology renderer
│       ├── simulator.js                          # Attack scenario simulator & packet flow animator
│       └── app.js                                # Main controller & live telemetry manager
│
├── architecture/                                # Professional Architecture Documents
│   ├── hybrid-architecture.md                   # Unified hybrid datacenter + cloud architecture
│   ├── network-segmentation.md                  # Cross-domain segmentation strategy
│   ├── iam-security-model.md                    # IAM, RBAC, MFA, Zero Trust, remote access
│   ├── kubernetes-security.md                   # K8s namespace isolation & security
│   └── threat-model-summary.md                  # Executive threat model with attack trees
│
├── docs/                                        # Detailed Specifications & Documentation
│   ├── demonstration-guide.md                   # 2-3 minute executive evaluation walkthrough
│   ├── architecture-overview.md                 # Quick evaluator orientation guide
│   ├── security-controls-summary.md             # Unified security controls catalog
│   ├── threat-traceability.md                   # Authoritative threat traceability matrix
│   ├── security-control-traceability.md         # Control-to-test mapping
│   ├── assets/                                  # Dashboard demonstration screenshots
│   └── architecture/                            # Per-Domain Design Specifications
│       ├── architecture.md                      # System architecture & component model
│       ├── network-design.md                    # Private DC VLAN/ACL design (385 lines)
│       ├── aws-design.md                        # AWS VPC/IAM/SG design (378 lines)
│       ├── kubernetes-design.md                 # K8s namespace/RBAC/NetworkPolicy (600 lines)
│       ├── aegismesh-design.md                  # Security engine API design (757 lines)
│       └── threat-model.md                      # Complete STRIDE analysis (239 lines)
│
└── packet-tracer/                               # Cisco Packet Tracer Implementation
    ├── topology.pkt                             # Packet Tracer binary topology file
    ├── handoff-package.md                       # Self-contained teammate execution guide
    ├── configs/
    │   └── SW-CORE-STAGE-A.txt                  # Stage A baseline (no ACL bindings)
    ├── configurations/                          # Stage B hardened device configurations
    │   ├── SW-CORE.txt                          # Core L3 switch (SVIs + ACLs)
    │   ├── R-EDGE.txt                           # Edge router
    │   ├── SW-ACCESS-1.txt                      # Access switch 1 (Faculty + DMZ)
    │   ├── SW-ACCESS-2.txt                      # Access switch 2 (App + DB)
    │   ├── SW-ACCESS-3.txt                      # Access switch 3 (Mgmt + Security)
    │   └── build-guide.md                       # Port/cabling reference
    ├── acl/                                     # ACL design documentation
    └── test-results/                            # Validation Results
        ├── validation-summary.md                # Empirical test results (VERIFIED)
        └── test-matrix.md                       # 30-test security matrix
```

---

## License & Evaluation Notice

This project is developed exclusively for the **Cisco Virtual Internship 2026 Cyber Security** program.

---

## Status

**Current Phase:** Phase 5 Complete — Private Datacenter Implemented & Validated, Hybrid Architecture Documented, Security Engine & Interactive Dashboard Runnable.
