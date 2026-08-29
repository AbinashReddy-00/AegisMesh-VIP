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
│  │ 6 VLANs       │  │ 4 VPCs         │  │ 5 Namespaces   │     │
│  │ Extended ACLs  │  │ Security Groups│  │ NetworkPolicies│     │
│  │ SVI Routing    │  │ IAM Policies   │  │ RBAC           │     │
│  │ VTY Hardening  │  │ NACLs          │  │ Pod Security   │     │
│  │                │  │                │  │                │     │
│  │ ✅ IMPLEMENTED │  │ 📐 DESIGNED   │  │ 📐 DESIGNED   │     │
│  │ ✅ VALIDATED   │  │                │  │                │     │
│  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘     │
│          │                   │                   │               │
│          └───────────────────┼───────────────────┘               │
│                              │                                   │
│                   ┌──────────┴──────────┐                        │
│                   │   AEGISMESH ENGINE  │                        │
│                   │   Policy + Risk +   │                        │
│                   │   Containment       │                        │
│                   └──────────┬──────────┘                        │
│                              │                                   │
│                   ┌──────────┴──────────┐                        │
│                   │   WAZUH SIEM +      │                        │
│                   │   SECURITY DASHBOARD│                        │
│                   └─────────────────────┘                        │
└──────────────────────────────────────────────────────────────────┘
```

---

## 3. Implementation Status

| Component | Status | Evidence |
|---|---|---|
| **Private Datacenter (Cisco Packet Tracer)** | **IMPLEMENTED AND VALIDATED** | `topology.pkt` + `validation-summary.md` |
| VLAN Segmentation (6 zones) | **IMPLEMENTED AND VALIDATED** | `SW-CORE.txt`, `SW-ACCESS-1..3.txt` |
| Extended ACL Enforcement (6 SVIs) | **IMPLEMENTED AND VALIDATED** | `show access-lists` match counters verified |
| Trunk Hardening (DTP, Native VLAN 99) | **IMPLEMENTED AND VALIDATED** | `show interfaces trunk` configuration |
| VTY Management Isolation | **IMPLEMENTED AND VALIDATED** | `MGMT-VTY-ACCESS` ACL on VTY lines |
| **AWS Cloud Architecture** | Architecture Design | `aws-design.md` (378 lines, 16.6 KB) |
| VPC Isolation (4 VPCs) | Architecture Design | Subnet, SG, NACL, and IAM fully specified |
| **Kubernetes Architecture** | Architecture Design | `kubernetes-design.md` (600 lines, 15.7 KB) |
| Namespace Isolation + RBAC | Architecture Design | NetworkPolicy, RBAC, PSS fully specified |
| **AegisMesh Security Engine** | Architecture Design | `aegismesh-design.md` (757 lines, 27.3 KB) |
| **Threat Model** | Complete | 21 threats across 6 STRIDE categories |
| **Threat Traceability** | Complete | 8 matrix rows (6 canonical + 2 architectural) |

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
