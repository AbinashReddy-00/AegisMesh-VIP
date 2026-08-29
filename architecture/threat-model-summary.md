# AegisMesh — Threat Model Summary

**Version:** 1.0  
**Date:** 2026-08-29  
**Project:** AegisMesh — Cisco Virtual Internship 2026 Cyber Security  
**Methodology:** STRIDE + Attack Tree Analysis  
**Detailed Reference:** [docs/architecture/threat-model.md](../docs/architecture/threat-model.md)  
**Traces to:** SR-01 through SR-05, FR-05, AC-02  

---

## 1. Executive Summary

This document provides an evaluator-friendly summary of the AegisMesh threat model. The complete STRIDE analysis with attack trees and detailed mitigations is available in [threat-model.md](../docs/architecture/threat-model.md). The authoritative threat-to-control-to-test traceability matrix is maintained in [threat-traceability.md](../docs/threat-traceability.md).

---

## 2. Threat Actors

| Actor | Capability | Primary Target | Example Scenario |
|---|---|---|---|
| **External Attacker** | Moderate | Internet-facing DMZ services | Exploit DMZ web server, pivot to internal network |
| **Compromised Application** | High (has valid credentials) | Cross-domain lateral movement | Education app attempts Finance database access |
| **Malicious Insider** | High (legitimate access) | Data exfiltration | Faculty user bypasses application tier to reach database |
| **Compromised Container** | Moderate | K8s namespace escape | Pod in education namespace accesses finance secrets |
| **Supply Chain** | Low probability, high impact | Application dependencies | Backdoored library exfiltrates data |

---

## 3. STRIDE Threat Summary

### 3.1 Threats by Category

| Category | Count | Key Threats | Primary Defense |
|---|---|:---:|---|
| **Spoofing** | 4 | User impersonation, VLAN hopping, service account abuse | MFA, port security, unique ServiceAccounts |
| **Tampering** | 4 | ACL modification, NetworkPolicy alteration, SG rule changes | VTY isolation, RBAC, IAM least privilege |
| **Repudiation** | 2 | Denied actions, log deletion | Immutable audit logs, isolated VLAN 50 |
| **Information Disclosure** | 4 | Cross-domain data access, credential exposure, unencrypted tunnel | VPC isolation, secret management, VPN encryption |
| **Denial of Service** | 3 | API flood, K8s resource exhaustion, SYN flood | Rate limiting, ResourceQuotas, ACL filtering |
| **Elevation of Privilege** | 4 | Container escape, lateral movement, direct DB access | PSS, ACLs, SG rules, AegisMesh policy |

### 3.2 Packet Tracer Validated Threats

The following threats have been implemented and empirically validated in Cisco Packet Tracer:

| Threat ID | Threat | Validation Result |
|---|---|---|
| **S-03** | VLAN hopping via trunk misconfiguration | Mitigated: DTP disabled, Native VLAN 99, explicit trunk VLAN list |
| **T-02** | Unauthorized device administration | Mitigated: MGMT-VTY-ACCESS restricts SSH to VLAN 30 only |
| **R-02** | Interference with logging infrastructure | Mitigated: VLAN 50 isolated via SEC-ACCESS ACL |
| **D-03** | Cross-zone reconnaissance / flood traffic | Mitigated: SVI ACLs with explicit permit + default deny |
| **E-02** | App server → Management lateral movement | Mitigated: APP-SERVER-ACCESS blocks VLAN 20 → VLAN 30 |
| **E-04** | Faculty → Database direct access bypass | Mitigated: FACULTY-ACCESS blocks VLAN 10 → VLAN 40 |

---

## 4. Primary Attack Scenario — Lateral Movement

The **core threat** the entire AegisMesh architecture is designed to defeat:

> *A compromised workload in one domain (education) attempts to access resources in another domain (finance database).*

### 4.1 Attack Tree

```
Goal: Access Finance Database from Compromised Education Workload
│
├── Path 1: Direct Network Access
│   ├── Private DC: VLAN 10 → VLAN 40
│   │   └── ❌ BLOCKED by FACULTY-ACCESS ACL (E-04)
│   ├── AWS: VPC-A → VPC-C
│   │   └── ❌ BLOCKED by VPC isolation (no peering exists)
│   └── K8s: education NS → finance NS
│       └── ❌ BLOCKED by default-deny NetworkPolicy
│
├── Path 2: Kubernetes API Abuse
│   ├── List pods in finance namespace
│   │   └── ❌ BLOCKED by RBAC (education SA has no finance access)
│   ├── Read finance secrets
│   │   └── ❌ BLOCKED by RBAC (secrets scoped to namespace)
│   └── Create pod in finance namespace
│       └── ❌ BLOCKED by RBAC (no create binding)
│
├── Path 3: AWS IAM Abuse
│   ├── Assume FinanceAppRole
│   │   └── ❌ BLOCKED by IAM policy (explicit cross-domain deny)
│   └── Modify Finance Security Group
│       └── ❌ BLOCKED by IAM policy (SG modify limited to own VPC)
│
└── Path 4: Application-Level Exploit
    ├── API call to finance service
    │   └── ❌ BLOCKED by AegisMesh policy evaluation (FR-01)
    └── DNS resolution of finance endpoints
        └── ❌ BLOCKED by NetworkPolicy egress rules
```

### 4.2 Detection and Response Flow

```
1. Education API sends anomalous request → finance-db
2. AegisMesh Detection Module observes anomaly
3. Risk Engine scores: 85 (CRITICAL)
4. Policy Engine evaluates: education-api → finance-db = BLOCK
5. Containment Controller activates:
   a. Workload state: NORMAL → SUSPICIOUS → CONTAINED
   b. NetworkPolicy updated: deny all egress except education-db
   c. Security Group updated: restrict education-api instance
6. Incident created with full timeline
7. Dashboard displays incident in real-time
```

---

## 5. Trust Boundary Summary

| Boundary | Between | Domain | Enforcement |
|---|---|---|---|
| TB-1 | Internet ↔ DMZ | Private DC | R-EDGE ACL |
| TB-2 | DMZ ↔ Internal | Private DC | DMZ-ACCESS ACL |
| TB-3 | Faculty ↔ App | Private DC | FACULTY-ACCESS ACL |
| TB-4 | App ↔ Database | Private DC | APP-SERVER-ACCESS / DB-ACCESS ACLs |
| TB-5 | Any ↔ Management | Private DC | MGMT-ACCESS + VTY ACL |
| TB-6 | VPC ↔ VPC | AWS | VPC isolation (no peering between A/B/C) |
| TB-7 | Namespace ↔ Namespace | K8s | Default-deny NetworkPolicy |
| TB-8 | Pod ↔ K8s API | K8s | RBAC + ServiceAccount |
| TB-9 | Frontend ↔ Backend | Application | HTTPS + auth middleware |
| TB-10 | Backend ↔ Database | Application | TLS + credential management |
| TB-11 | Private DC ↔ AWS | Hybrid | IPsec VPN tunnel |

---

## 6. Residual Risks

| Risk | Impact | Accepted Because |
|---|---|---|
| Packet Tracer fidelity | PT does not perfectly replicate production Cisco hardware | Simulation environment; architecture principles remain valid |
| Local K8s limitations | kind/Minikube may not support all production CNI features | Calico CNI provides real NetworkPolicy enforcement |
| Single-region AWS | No multi-region disaster recovery | Development scope limitation |
| Deterministic risk scoring | Rule-based scoring may miss novel attack patterns | Appropriate for project scope; ML not claimed |
| VPN simulation | VPN between DC and AWS is architecturally documented, not physically implemented | PT operates as independent security zone |
