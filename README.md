# AegisMesh

> **Secure Hybrid Datacenter and Cloud Security Architecture**  
> Cisco Virtual Internship 2026 — Cyber Security Project

---

## Problem Statement

An enterprise operates a hybrid infrastructure spanning a **private datacenter** and **public cloud (AWS)**. Workloads run as traditional server applications and Kubernetes-orchestrated microservices. Faculty, developers, and engineers access resources from campus and remote locations.

> **Security Objective:** If one application or workload is compromised, the compromise must not be able to spread laterally to unauthorized applications, VPCs, Kubernetes workloads, or the private enterprise network.

AegisMesh is the security control and decision architecture that enforces this objective across all infrastructure domains.

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
┌──────────┴──────────┐  ┌─────────┴─────────┐  ┌──────────┴──────────┐
│  PRIVATE DATACENTER │  │    AWS CLOUD       │  │  KUBERNETES CLUSTER │
│                     │  │                    │  │                     │
│  6 VLANs + ACLs     │  │  4 VPCs + SGs      │  │  5 Namespaces       │
│  SVI Routing        │  │  IAM Policies      │  │  NetworkPolicies    │
│  Trunk Hardening    │  │  NACLs             │  │  RBAC + PSS         │
│  VTY Restriction    │  │  CloudTrail Logs   │  │  Resource Quotas    │
│                     │  │                    │  │                     │
│  ✅ IMPLEMENTED     │  │  📐 DESIGNED       │  │  📐 DESIGNED        │
│  ✅ VALIDATED       │  │                    │  │                     │
└──────────┬──────────┘  └─────────┬──────────┘  └──────────┬──────────┘
           │                       │                        │
           └───────────────────────┼────────────────────────┘
                                   │
                        ┌──────────┴──────────┐
                        │   AEGISMESH ENGINE   │
                        │   Policy + Risk +    │
                        │   Containment        │
                        └──────────┬──────────┘
                                   │
                        ┌──────────┴──────────┐
                        │   WAZUH SIEM +       │
                        │   SECURITY DASHBOARD │
                        └─────────────────────┘
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
| 12 | **Monitoring & Security Logging** | Wazuh SIEM, CloudTrail, VPC Flow Logs, dedicated Security VLAN |
| 13 | **Incident Containment** | AegisMesh blast-radius controller; dynamic policy enforcement |

---

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Private Datacenter | Cisco Packet Tracer 8.2+ | Enterprise network simulation with VLAN/ACL enforcement |
| Cloud | AWS + Terraform | Multi-VPC public cloud with IAM, SGs, and CloudTrail |
| Containers | Kubernetes (kind) + Calico CNI | Namespace isolation with real NetworkPolicy enforcement |
| Security Engine | Python 3.12, FastAPI, PostgreSQL | Centralized policy evaluation, risk scoring, containment |
| Dashboard | Next.js, TypeScript, React Flow | Interactive security topology and incident visualization |
| Monitoring | Wazuh (SIEM) | Agent-based log collection, correlation, and alerting |
| Infrastructure-as-Code | Terraform (HCL) | Declarative, reproducible AWS infrastructure provisioning |

---

## Implementation Status

| Component | Status | Evidence |
|---|---|---|
| Private Datacenter Network | **IMPLEMENTED AND VALIDATED** | Cisco Packet Tracer topology (`topology.pkt`) |
| VLAN Segmentation (6 zones) | **IMPLEMENTED AND VALIDATED** | `show vlan brief`, device configurations |
| Extended ACL Enforcement | **IMPLEMENTED AND VALIDATED** | `show access-lists` with non-zero match counters |
| Trunk Hardening (DTP, Native VLAN 99) | **IMPLEMENTED AND VALIDATED** | `show interfaces trunk` |
| VTY Management Isolation | **IMPLEMENTED AND VALIDATED** | MGMT-VTY-ACCESS ACL on VTY lines |
| AWS Cloud Architecture | Architecture Design | 378-line specification in `aws-design.md` |
| Kubernetes Architecture | Architecture Design | 600-line specification in `kubernetes-design.md` |
| AegisMesh Security Engine | Architecture Design | 757-line specification in `aegismesh-design.md` |
| Threat Model (STRIDE) | Complete | 21 threats, 11 trust boundaries, attack trees |
| Threat Traceability | Complete | 8-row matrix (6 canonical + 2 architectural) |

---

## Validation Summary

The private datacenter implementation has been empirically validated in Cisco Packet Tracer:

| Test | Source | Destination | Expected | Result |
|---|---|---|:---:|:---:|
| Faculty → App Server | FAC-PC-01 | APP-SRV-01 (10.10.20.10) | ALLOW | ✅ Verified |
| Faculty → Database | FAC-PC-01 | DB-SRV-01 (10.10.40.10) | BLOCK | ✅ Verified |
| Faculty → Security VLAN | FAC-PC-01 | SEC-SRV-01 (10.10.50.1) | BLOCK | ✅ Verified |
| ACL Match Counters | SW-CORE | `show access-lists` | Non-zero | ✅ Verified |
| Baseline Connectivity | All endpoints | Default gateways | ALLOW | ✅ Verified |

Full validation results: [`packet-tracer/test-results/validation-summary.md`](packet-tracer/test-results/validation-summary.md)

---

## Repository Structure

```
AegisMesh/
├── README.md                                    # Project overview (this file)
├── .gitignore                                   # Repository hygiene rules
│
├── architecture/                                # Professional Architecture Documents
│   ├── hybrid-architecture.md                   # Unified hybrid datacenter + cloud architecture
│   ├── network-segmentation.md                  # Cross-domain segmentation strategy
│   ├── iam-security-model.md                    # IAM, RBAC, MFA, Zero Trust, remote access
│   ├── kubernetes-security.md                   # K8s namespace isolation & security
│   ├── threat-model-summary.md                  # Executive threat model with attack trees
│   ├── data-flow/                               # Data flow diagrams
│   ├── network-topology/                        # Network topology diagrams
│   ├── system-design/                           # System design diagrams
│   ├── threat-model/                            # Threat model diagrams
│   └── trust-boundaries/                        # Trust boundary diagrams
│
├── docs/                                        # Detailed Specifications & Documentation
│   ├── architecture-overview.md                 # Quick evaluator orientation guide
│   ├── security-controls-summary.md             # Unified security controls catalog
│   ├── threat-traceability.md                   # Authoritative threat traceability matrix
│   ├── security-control-traceability.md         # Control-to-test mapping
│   ├── architecture/                            # Per-Domain Design Specifications
│   │   ├── architecture.md                      # System architecture & component model
│   │   ├── network-design.md                    # Private DC VLAN/ACL design (385 lines)
│   │   ├── aws-design.md                        # AWS VPC/IAM/SG design (378 lines)
│   │   ├── kubernetes-design.md                 # K8s namespace/RBAC/NetworkPolicy (600 lines)
│   │   ├── aegismesh-design.md                  # Security engine API design (757 lines)
│   │   └── threat-model.md                      # Complete STRIDE analysis (239 lines)
│   ├── requirements/                            # Project Requirements
│   │   ├── requirements.md                      # FR, NFR, SR specifications
│   │   ├── technology-stack.md                   # Technology selection & justification
│   │   └── project-roadmap.md                   # Development phase roadmap
│   └── testing/
│       └── testing-strategy.md                  # Multi-tier verification strategy
│
├── packet-tracer/                               # Cisco Packet Tracer Implementation
│   ├── topology.pkt                             # Packet Tracer binary topology file
│   ├── handoff-package.md                       # Self-contained teammate execution guide
│   ├── configs/
│   │   └── SW-CORE-STAGE-A.txt                  # Stage A baseline (no ACL bindings)
│   ├── configurations/                          # Stage B hardened device configurations
│   │   ├── SW-CORE.txt                          # Core L3 switch (SVIs + ACLs)
│   │   ├── R-EDGE.txt                           # Edge router
│   │   ├── SW-ACCESS-1.txt                      # Access switch 1 (Faculty + DMZ)
│   │   ├── SW-ACCESS-2.txt                      # Access switch 2 (App + DB)
│   │   ├── SW-ACCESS-3.txt                      # Access switch 3 (Mgmt + Security)
│   │   └── build-guide.md                       # Port/cabling reference
│   ├── acl/                                     # ACL design documentation
│   │   ├── acl-design.md                        # Stateless ACL logic & return paths
│   │   └── security-vlan-review.md              # VLAN 50 hardening analysis
│   ├── vlan/
│   │   └── vlan-inventory.md                    # Subnet/gateway/port mapping
│   └── test-results/                            # Validation Results
│       ├── validation-summary.md                # Empirical test results (VERIFIED)
│       ├── test-matrix.md                       # 30-test security matrix
│       ├── execution-checklist.md               # Test execution checklist
│       ├── requirement-traceability.md          # SR-to-test mapping
│       ├── phase4-validation-report.md          # Pre-validation review
│       └── evidence/                            # Screenshot evidence directory
│
├── infrastructure/                              # AWS Cloud (Terraform modules)
│   └── terraform/
│       ├── vpc/                                 # VPC, subnets, IGW, NAT, routes
│       ├── security-groups/                     # Security Group definitions
│       ├── iam/                                 # IAM roles and policies
│       ├── routing/                             # VPC peering, route tables
│       └── logging/                             # CloudTrail, CloudWatch, Flow Logs
│
├── kubernetes/                                  # Kubernetes Manifests
│   ├── cluster/                                 # kind cluster configuration
│   ├── namespaces/                              # Namespace definitions
│   ├── deployments/                             # Workload deployments
│   ├── services/                                # Service definitions
│   ├── network-policies/                        # NetworkPolicy manifests
│   ├── rbac/                                    # RBAC roles and bindings
│   ├── resource-controls/                       # ResourceQuotas, LimitRanges
│   └── secrets/                                 # Secret management
│
├── backend/                                     # AegisMesh Security Engine
│   ├── app/
│   │   ├── api/                                 # FastAPI REST endpoints
│   │   ├── policy_engine/                       # Policy evaluation
│   │   ├── risk_engine/                         # Risk scoring
│   │   ├── decision_engine/                     # Decision arbiter
│   │   ├── detection/                           # Anomaly detection
│   │   ├── containment/                         # Blast-radius controller
│   │   ├── workload_identity/                   # Identity verification
│   │   ├── models/                              # Data models
│   │   └── database/                            # PostgreSQL migrations
│   └── tests/                                   # Test suites
│
├── frontend/                                    # Security Dashboard
│   ├── app/                                     # Next.js pages
│   └── components/                              # React Flow topology, alerts
│
├── monitoring/                                  # SIEM & Telemetry
│   ├── wazuh/                                   # Wazuh rules and decoders
│   └── grafana/                                 # Dashboards
│
└── testing/                                     # Cross-Domain Testing
    ├── packet-tracer/                           # PT test scripts
    ├── aws/                                     # Cloud validation
    ├── kubernetes/                              # NetworkPolicy tests
    └── end-to-end/                              # Full-chain attack simulation
```

---

## Scalability

The architecture supports growth without compromising security:

| Scenario | Action | Security Guarantee |
|---|---|---|
| Add new department | Create VLAN (DC) + VPC (AWS) + Namespace (K8s) | Default-deny inherited automatically |
| Add new server | Place in appropriate VLAN/subnet | Existing ACL/SG boundaries apply |
| Scale application | Horizontal scaling behind ALB | Stateless policy evaluation |
| Multi-region expansion | Replicate VPC architecture per region | Cross-region isolation maintained |
| New microservice | Deploy to correct namespace | NetworkPolicy + RBAC enforce isolation |

---

## Documentation

| Document | Description |
|---|---|
| [Architecture Overview](docs/architecture-overview.md) | Quick evaluator orientation |
| [Hybrid Architecture](architecture/hybrid-architecture.md) | Unified three-domain security view |
| [Network Segmentation](architecture/network-segmentation.md) | Cross-domain segmentation strategy |
| [IAM Security Model](architecture/iam-security-model.md) | Identity, access, Zero Trust, remote access |
| [Kubernetes Security](architecture/kubernetes-security.md) | Container platform security |
| [Threat Model Summary](architecture/threat-model-summary.md) | Attack scenarios and defense layers |
| [Security Controls](docs/security-controls-summary.md) | Unified controls catalog |
| [Requirements](docs/requirements/requirements.md) | Functional and security requirements |
| [Network Design](docs/architecture/network-design.md) | Private DC VLAN/ACL specification |
| [AWS Design](docs/architecture/aws-design.md) | Cloud VPC/IAM/SG specification |
| [Kubernetes Design](docs/architecture/kubernetes-design.md) | K8s namespace/RBAC/NetworkPolicy |
| [AegisMesh Design](docs/architecture/aegismesh-design.md) | Security engine API design |
| [Threat Model](docs/architecture/threat-model.md) | Complete STRIDE analysis |
| [Threat Traceability](docs/threat-traceability.md) | Threat-to-control-to-test matrix |
| [Technology Stack](docs/requirements/technology-stack.md) | Technology justification |
| [Validation Summary](packet-tracer/test-results/validation-summary.md) | Empirical test results |
| [Handoff Package](packet-tracer/handoff-package.md) | Teammate Packet Tracer execution guide |

---

## License

This project is developed for the **Cisco Virtual Internship 2026 Cyber Security** program.

---

## Status

**Current Phase:** Phase 4 Complete — Private Datacenter Implemented and Validated  
**Architecture Design:** Complete for all three domains (Private DC, AWS, Kubernetes)  
**Next Phase:** Phase 5 — AWS Cloud Infrastructure Provisioning (Terraform)
