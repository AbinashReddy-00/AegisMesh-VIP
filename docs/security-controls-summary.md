# AegisMesh — Security Controls Summary

**Version:** 1.0  
**Date:** 2026-08-29  
**Project:** AegisMesh — Cisco Virtual Internship 2026 Cyber Security  
**Traces to:** SR-01 through SR-05, FR-01 through FR-10  

---

## 1. Controls Overview

AegisMesh implements security controls across **eight independent layers**, using native primitives in each infrastructure domain. No single layer's compromise grants unauthorized access.

---

## 2. Network Layer Controls

### 2.1 Private Datacenter — ACL Enforcement

> **Status: IMPLEMENTED AND VALIDATED**

| Control | ACL Name | Enforcement Point | Key Rules | Threat Mitigated |
|---|---|---|---|---|
| Faculty Zone Boundary | `FACULTY-ACCESS` | SVI Vlan10 (ingress) | Allow → App, DMZ; Block → DB, Mgmt, Security | E-04, D-03 |
| App Server Boundary | `APP-SERVER-ACCESS` | SVI Vlan20 (ingress) | Allow → DB, Faculty return; Block → Mgmt | E-02, D-03 |
| Management Isolation | `MGMT-ACCESS` | SVI Vlan30 (ingress) | Allow → DB, App, Security; Block → unauthorized | T-02, D-03 |
| Database Protection | `DB-ACCESS` | SVI Vlan40 (ingress) | Allow → App return, Mgmt return; Block → Faculty, DMZ | ARCH-SCENARIO-01 |
| Security/Log Isolation | `SEC-ACCESS` | SVI Vlan50 (ingress) | Allow → App, DB monitoring; Block → Faculty | R-02, D-03 |
| DMZ Containment | `DMZ-ACCESS` | SVI Vlan60 (ingress) | Allow → App, Faculty return; Block → DB, Mgmt | ARCH-SCENARIO-02, D-03 |
| VTY Access Restriction | `MGMT-VTY-ACCESS` | VTY Lines 0–15 | Permit 10.10.30.0/24 only; deny any | T-02 |

### 2.2 AWS Cloud — Security Groups

> **Status: ARCHITECTURE DESIGN / PROPOSED IMPLEMENTATION**

| Control | Security Group | Applied To | Inbound | Outbound |
|---|---|---|---|---|
| Education ALB | `edu-alb-sg` | ALB | 80/443 from internet | App port to app SG |
| Education App | `edu-app-sg` | App instances | App port from ALB | DB port to db SG |
| Education DB | `edu-db-sg` | RDS | 5432 from app SG | None |
| Finance App | `fin-app-sg` | App instances | App port from VPC-D only | DB port to db SG |
| Finance DB | `fin-db-sg` | RDS | 5432 from app SG | None |
| Security Bastion | `sec-bastion-sg` | Bastion | 22 from admin CIDR | All internal |
| AegisMesh Backend | `sec-aegismesh-sg` | Backend | 8000 from frontend | PostgreSQL to db SG |

### 2.3 Kubernetes — NetworkPolicies

> **Status: ARCHITECTURE DESIGN / PROPOSED IMPLEMENTATION**

| Control | Policy Name | Namespace | Effect |
|---|---|---|---|
| Default Deny All | `default-deny-all` | All domain NS | Block all ingress + egress by default |
| Intra-Namespace Allow | `allow-intra-namespace` | All domain NS | Permit pod-to-pod within same NS |
| Monitoring Access | `allow-monitoring-ingress` | All domain NS | Permit monitoring NS to collect logs |
| AegisMesh API Access | `allow-aegismesh-egress` | All domain NS | Permit security reporting to aegismesh-system |

---

## 3. Identity & Access Controls

| Control | Domain | Implementation | Status |
|---|---|---|---|
| VTY SSH Restriction | Private DC | Standard ACL `MGMT-VTY-ACCESS` on VTY lines | **IMPLEMENTED** |
| IAM Role Per Domain | AWS | `EducationAppRole`, `ResearchAppRole`, `FinanceAppRole` | Architecture Design |
| Cross-Domain Deny | AWS | Explicit `Deny` statements in IAM policies | Architecture Design |
| MFA for Admin Access | AWS | `aws:MultiFactorAuthPresent` condition | Architecture Design |
| Namespace RBAC | Kubernetes | Per-namespace Roles and RoleBindings | Architecture Design |
| ServiceAccount Isolation | Kubernetes | Unique SA per pod; no cross-namespace bindings | Architecture Design |
| Pod Security Standards | Kubernetes | Restricted PSS on all domain namespaces | Architecture Design |

---

## 4. Monitoring & Logging Controls

| Control | Implementation | Coverage | Status |
|---|---|---|---|
| Dedicated Security VLAN | VLAN 50 with SEC-ACCESS ACL | Private DC | **IMPLEMENTED** |
| CloudTrail | Multi-region trail with log validation | AWS | Architecture Design |
| VPC Flow Logs | Accept + Reject on all 4 VPCs | AWS | Architecture Design |
| CloudWatch Alarms | Unauthorized API calls, SG modifications | AWS | Architecture Design |
| Wazuh SIEM | Agent-based log collection + correlation | All domains | Architecture Design |
| Audit Logging | Immutable audit_logs table in PostgreSQL | AegisMesh Engine | Architecture Design |

---

## 5. Containment Controls

| Control | Trigger | Action | Domain |
|---|---|---|---|
| ACL Boundary Enforcement | Per-VLAN ingress filtering | Block unauthorized cross-zone traffic | Private DC |
| Security Group Update | AegisMesh containment API | Restrict compromised instance egress | AWS |
| NetworkPolicy Update | AegisMesh containment controller | Restrict compromised pod to authorized dependencies only | Kubernetes |
| Workload State Transition | Risk score > 80 | NORMAL → SUSPICIOUS → CONTAINED | AegisMesh Engine |
| Incident Creation | Containment activation | Full audit trail with timeline | AegisMesh Engine |

---

## 6. Trunk & Transport Hardening

| Control | Implementation | Purpose | Status |
|---|---|---|---|
| DTP Disabled | `switchport nonegotiate` on all trunks | Prevent dynamic trunk negotiation | **IMPLEMENTED** |
| Native VLAN 99 | Dedicated unused VLAN on trunks | Prevent VLAN hopping / double-tagging | **IMPLEMENTED** |
| Explicit VLAN Lists | `switchport trunk allowed vlan` | Restrict trunk scope | **IMPLEMENTED** |
| Unused Ports Shutdown | VLAN 99 + `shutdown` | Prevent rogue device access | **IMPLEMENTED** |
| VPN Encryption | IPsec IKEv2 AES-256-GCM | Secure DC ↔ Cloud transit | Architecture Design |
| TLS for API | HTTPS with valid certificates | Secure frontend ↔ backend | Architecture Design |

---

## 7. Controls Mapping to Cisco Problem Statement

| Cisco Requirement | Control Categories | Key Artifacts |
|---|---|---|
| Hybrid connectivity | VPN tunnel, VPC peering, cross-domain traffic matrix | `hybrid-architecture.md` |
| Cloud VPC segmentation | 4 VPCs, default deny, controlled peering to VPC-D | `aws-design.md` |
| Public/private subnet architecture | Public (ALB/NAT), Private App, Private DB tiers | `aws-design.md` |
| IAM/RBAC with least privilege and MFA | Per-domain IAM roles, RBAC, MFA conditions | `iam-security-model.md` |
| Cloud Security Groups | Per-instance SG rules, SG-to-SG references | `aws-design.md` |
| Application isolation / lateral movement prevention | VLANs + ACLs, VPC isolation, NetworkPolicies | `network-segmentation.md` |
| Kubernetes / microservices security | RBAC, PSS, ResourceQuotas, ServiceAccount isolation | `kubernetes-security.md` |
| Network policies and namespace isolation | Default-deny NetworkPolicy, Calico CNI | `kubernetes-design.md` |
| Secure faculty remote access | VPN + MFA, same-as-on-campus restrictions | `iam-security-model.md` |
| Zero Trust / VPN access approach | No implicit trust, continuous evaluation, fail-closed | `iam-security-model.md` |
| Monitoring and security logging | Wazuh, CloudTrail, Flow Logs, VLAN 50 isolation | `security-controls-summary.md` |
| Incident containment / blast-radius reduction | AegisMesh containment controller, dynamic policy updates | `hybrid-architecture.md` |
| Scalability without complexity | Add VLANs/VPCs/namespaces with inherited default-deny | `hybrid-architecture.md` |
