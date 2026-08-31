# AegisMesh — Architecture Overview

**Version:** 1.0  
**Date:** 2026-08-29  
**Project:** AegisMesh — Cisco Virtual Internship 2026 Cyber Security  

---

## 1. Problem Statement

An enterprise operates a **hybrid infrastructure** spanning a private datacenter and public cloud (AWS). Workloads are deployed as traditional server applications and Kubernetes-orchestrated microservices. Faculty, developers, and platform engineers access resources from campus and remote locations.

> **Primary Security Objective:**  
> If one application or workload is compromised, the compromise must not be able to spread laterally to unauthorized applications, VPCs, Kubernetes workloads, or the private enterprise network.

---

## 2. Solution Architecture

AegisMesh addresses this objective through a **three-domain security architecture** with consistent security controls at every layer:

```
┌──────────────────────────────────────────────────────────────────┐
│                    AEGISMESH SECURITY ARCHITECTURE               │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐     │
│  │ PRIVATE        │  │ AWS PUBLIC     │  │ KUBERNETES     │     │
│  │ DATACENTER     │  │ CLOUD          │  │ CLUSTER        │     │
│  │                │  │                │  │                │     │
│  │ 6 VLANs        │  │ 3-Tier Multi-AZ│  │ 2 Workload NS  │     │
│  │ Extended ACLs  │  │ Security Groups│  │ NetworkPolicies│     │
│  │ SVI Routing    │  │ Route Tables   │  │ RBAC           │     │
│  │ VTY Hardening  │  │ Air-Gapped DB  │  │ Dynamic Isolate│     │
│  │                │  │                │  │                │     │
│  │ ✅ PT SIMULATED│  │ ✅ TERRAFORM IaC│  │ ✅ LIVE LOCAL K8S│     │
│  │ ✅ VALIDATED   │  │ ✅ LOCAL SIM   │  │ ✅ CALICO CNI  │     │
│  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘     │
│          │                   │                   │               │
│          └───────────────────┼───────────────────┘               │
│                              │                                   │
│                   ┌──────────┴──────────┐                        │
│                   │   AEGISMESH ENGINE  │                        │
│                   │   Policy + Risk +   │                        │
│                   │   Containment       │                        │
│                   │   (FastAPI Backend) │                        │
│                   └──────────┬──────────┘                        │
│                              │                                   │
│                   ┌──────────┴──────────┐                        │
│                   │  CYBER COMMAND      │                        │
│                   │  SOC DASHBOARD      │                        │
│                   │  (SIEM: Future Ext) │                        │
│                   └─────────────────────┘                        │
└──────────────────────────────────────────────────────────────────┘
```

---

## 3. Implementation Status

| Component | Status | Evidence |
|---|---|---|
| **AegisMesh Security Engine** | **IMPLEMENTED AND VALIDATED** | FastAPI decision, 6-factor risk, and containment engine (`backend/tests/`, 18/18 tests pass) |
| **Interactive Cyber Command Center** | **IMPLEMENTED AND VALIDATED** | Live single-page dashboard served at `http://localhost:8000/` |
| **Kubernetes Container Security** | **IMPLEMENTED AND EMPIRICALLY VALIDATED** | Live local Kind cluster with Project Calico CNI + dynamic NetworkPolicy containment bridge (6/6 phases pass) |
| **AWS Cloud Infrastructure** | **IMPLEMENTED AS IaC & LOCALLY VALIDATED** | Modular 3-Tier Multi-AZ Terraform code empirically validated against local AWS simulation (8/8 controls pass, $0 cost, not deployed to real AWS) |
| **Private Datacenter (Cisco Network)** | **IMPLEMENTED AS CISCO PACKET TRACER SIMULATION** | `topology.pkt` + `validation-summary.md` (30/30 empirical matrix verified) |
| VLAN Segmentation (6 zones) | **IMPLEMENTED (PT SIMULATION)** | `SW-CORE.txt`, `SW-ACCESS-1..3.txt` |
| Extended ACL Enforcement (6 SVIs) | **IMPLEMENTED (PT SIMULATION)** | `show access-lists` match counters verified |
| Trunk Hardening (DTP, Native VLAN 99) | **IMPLEMENTED (PT SIMULATION)** | `show interfaces trunk` configuration |
| VTY Management Isolation | **IMPLEMENTED (PT SIMULATION)** | `MGMT-VTY-ACCESS` ACL on VTY lines |
| **Threat Model (STRIDE)** | **COMPLETED & DOCUMENTED** | 21 threats across 6 STRIDE categories |
| **Threat Traceability** | **COMPLETED & DOCUMENTED** | 14-row authoritative threat matrix (`docs/threat-traceability.md`) |
| **SIEM Ingestion / Log Pipeline** | *FUTURE EXTENSION (NOT IMPLEMENTED)* | Centralized event correlation / Wazuh agent integration |

---

## 4. Key Design Decisions

| Decision | Rationale | Cisco Problem Statement Link |
|---|---|---|
| **VLANs for DC segmentation** | Industry-standard L2/L3 isolation; native to Cisco infrastructure | Network segmentation requirement |
| **VPC-per-domain isolation** | Default deny between VPCs; no accidental lateral paths | Cloud VPC segmentation |
| **Default-deny NetworkPolicies** | Pods isolated from first deployment; explicit allow required | Kubernetes namespace isolation |
| **Separate Security VPC/VLAN** | Management and monitoring infrastructure isolated from workloads | Monitoring and security logging |
| **Stateless ACLs in Packet Tracer** | PT does not support stateful inspection; architecture compensates with symmetric return rules | Application isolation |
| **AegisMesh as control plane** | Unified policy and risk evaluation across all three domains | Zero Trust approach |
| **MFA for all human access** | No implicit trust from network location | Secure faculty remote access |
| **Fail-closed default** | If AegisMesh unreachable, default action is DENY | Incident containment |

---

## 5. Document Map

For Cisco evaluators, the recommended reading order:

| Order | Document | Purpose | Location |
|:---:|---|---|---|
| 1 | **This document** | Quick orientation | `docs/architecture-overview.md` |
| 2 | [Hybrid Architecture](../architecture/hybrid-architecture.md) | Unified three-domain view | `architecture/hybrid-architecture.md` |
| 3 | [Network Segmentation](../architecture/network-segmentation.md) | Cross-domain segmentation strategy | `architecture/network-segmentation.md` |
| 4 | [Threat Model Summary](../architecture/threat-model-summary.md) | Attack scenarios and defenses | `architecture/threat-model-summary.md` |
| 5 | [IAM Security Model](../architecture/iam-security-model.md) | Identity, access, and Zero Trust | `architecture/iam-security-model.md` |
| 6 | [Kubernetes Security](../architecture/kubernetes-security.md) | Container platform security | `architecture/kubernetes-security.md` |
| 7 | [Security Controls](security-controls-summary.md) | Unified controls catalog | `docs/security-controls-summary.md` |
| 8 | [Validation Summary](../packet-tracer/test-results/validation-summary.md) | Empirical test results | `packet-tracer/test-results/validation-summary.md` |

For detailed per-domain specifications, see:
- [Network Design](architecture/network-design.md) — Private DC VLAN/ACL specification
- [AWS Design](architecture/aws-design.md) — Cloud VPC/IAM/SG specification
- [Kubernetes Design](architecture/kubernetes-design.md) — K8s namespace/RBAC/NetworkPolicy specification
- [AegisMesh Engine](architecture/aegismesh-design.md) — Security engine API and module design
- [Threat Model](architecture/threat-model.md) — Complete STRIDE analysis with attack trees
- [Requirements](requirements/requirements.md) — Functional, non-functional, and security requirements
