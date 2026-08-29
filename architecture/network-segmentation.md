# AegisMesh — Cross-Domain Network Segmentation Strategy

**Version:** 1.0  
**Date:** 2026-08-29  
**Project:** AegisMesh — Cisco Virtual Internship 2026 Cyber Security  
**Traces to:** SR-01, SR-02, SR-03, SR-05  

---

## 1. Segmentation Philosophy

Network segmentation is the **foundational security control** of the AegisMesh architecture. Every workload is placed in a security zone with explicit, least-privilege access boundaries. The default posture across all three domains is **DENY ALL** — only authorized flows are explicitly permitted.

The architecture implements segmentation at three layers, each using the native primitives of its infrastructure domain:

| Layer | Domain | Segmentation Primitive | Granularity |
|---|---|---|---|
| **Layer 2/3** | Private Datacenter (Cisco) | VLANs + SVI Extended ACLs | Per-subnet / per-zone |
| **Layer 3** | AWS Cloud | VPC Isolation + Security Groups | Per-VPC / per-instance |
| **Layer 3/4** | Kubernetes | Namespace + NetworkPolicy | Per-namespace / per-pod |

---

## 2. Private Datacenter Segmentation

> **Status: IMPLEMENTED AND VALIDATED in Cisco Packet Tracer**

### 2.1 VLAN Zone Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PRIVATE DATACENTER ZONES                        │
│                                                                     │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐                        │
│   │ VLAN 10  │  │ VLAN 20  │  │ VLAN 30  │                        │
│   │ FACULTY  │  │ APP SRVR │  │ MGMT     │                        │
│   │ LOW      │  │ MEDIUM   │  │ HIGH     │                        │
│   │ 10.10.10 │  │ 10.10.20 │  │ 10.10.30 │                        │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘                        │
│        │              │              │                              │
│   ┌────┴──────────────┴──────────────┴────┐                        │
│   │         SW-CORE (Layer 3 Switch)      │                        │
│   │         SVI ACL Enforcement Point     │                        │
│   └────┬──────────────┬──────────────┬────┘                        │
│        │              │              │                              │
│   ┌────┴─────┐  ┌─────┴────┐  ┌─────┴────┐                        │
│   │ VLAN 40  │  │ VLAN 50  │  │ VLAN 60  │                        │
│   │ DATABASE │  │ SECURITY │  │ DMZ      │                        │
│   │ HIGH     │  │ HIGH     │  │ LOW      │                        │
│   │ 10.10.40 │  │ 10.10.50 │  │ 10.10.60 │                        │
│   └──────────┘  └──────────┘  └──────────┘                        │
│                                                                     │
│   Native VLAN 99 — Unused / Blackholed (Anti-VLAN-Hopping)         │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Inter-VLAN Access Policy

| Source Zone | Destination Zone | Policy | Enforcement |
|---|---|:---:|---|
| Faculty (VLAN 10) | App Servers (VLAN 20) | ✅ ALLOW | `FACULTY-ACCESS` Rule 1 |
| Faculty (VLAN 10) | DMZ (VLAN 60) | ✅ ALLOW | `FACULTY-ACCESS` Rule 2 |
| Faculty (VLAN 10) | Management (VLAN 30) | ❌ BLOCK | `FACULTY-ACCESS` Rule 3 |
| Faculty (VLAN 10) | Database (VLAN 40) | ❌ BLOCK | `FACULTY-ACCESS` Rule 4 |
| Faculty (VLAN 10) | Security (VLAN 50) | ❌ BLOCK | `FACULTY-ACCESS` Rule 5 |
| App Servers (VLAN 20) | Database (VLAN 40) | ✅ ALLOW | `APP-SERVER-ACCESS` Rule 1 |
| App Servers (VLAN 20) | Management (VLAN 30) | ❌ BLOCK | `APP-SERVER-ACCESS` Rule 5 |
| DMZ (VLAN 60) | App Servers (VLAN 20) | ✅ ALLOW | `DMZ-ACCESS` Rule 1 |
| DMZ (VLAN 60) | Database (VLAN 40) | ❌ BLOCK | `DMZ-ACCESS` Rule 4 |
| DMZ (VLAN 60) | Management (VLAN 30) | ❌ BLOCK | `DMZ-ACCESS` Rule 5 |
| Database (VLAN 40) | Faculty (VLAN 10) | ❌ BLOCK | `DB-ACCESS` Rule 4 |
| Security (VLAN 50) | Faculty (VLAN 10) | ❌ BLOCK | `SEC-ACCESS` Rule 4 |

### 2.3 Layer 2 Hardening

| Control | Implementation | Purpose |
|---|---|---|
| DTP Disabled | `switchport nonegotiate` on all trunk ports | Prevent dynamic trunk negotiation attacks |
| Native VLAN 99 | Dedicated unused VLAN on all trunks | Prevent native VLAN injection / double-tagging |
| Explicit Trunk VLANs | `switchport trunk allowed vlan 10,20,30,40,50,60,99` | Restrict VLAN scope on trunks |
| Unused Port Shutdown | All unused ports in VLAN 99, administratively down | Prevent rogue device connection |
| PortFast | Enabled on access ports | Prevent STP manipulation |

---

## 3. AWS Cloud Segmentation

> **Status: ARCHITECTURE DESIGN / PROPOSED IMPLEMENTATION**

### 3.1 VPC Zone Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                       AWS CLOUD ZONES                              │
│                                                                     │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│   │   VPC-A      │  │   VPC-B      │  │   VPC-C      │            │
│   │  EDUCATION   │  │  RESEARCH    │  │  FINANCE     │            │
│   │  10.1.0.0/16 │  │  10.2.0.0/16 │  │  10.3.0.0/16 │            │
│   │              │  │              │  │              │            │
│   │  Public +    │  │  Public +    │  │  Private     │            │
│   │  Private     │  │  Private     │  │  ONLY        │            │
│   │  Subnets     │  │  Subnets     │  │  (No IGW)    │            │
│   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘            │
│          │                 │                 │                      │
│          ╳ ─ ─ ─ ─ ─ ─ ─ ─╳─ ─ ─ ─ ─ ─ ─ ─╳                      │
│          │    NO PEERING BETWEEN A/B/C       │                      │
│          │                                   │                      │
│   ┌──────┴───────────────────────────────────┴──────┐              │
│   │                  VPC-D                           │              │
│   │           SECURITY / MANAGEMENT                  │              │
│   │             10.4.0.0/16                          │              │
│   │                                                  │              │
│   │  Peered to VPC-A, B, C for monitoring ONLY       │              │
│   │  Hosts: AegisMesh, Wazuh, Bastion               │              │
│   └──────────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Inter-VPC Access Policy

| Source VPC | Destination VPC | Policy | Mechanism |
|---|---|:---:|---|
| VPC-A (Education) | VPC-B (Research) | ❌ BLOCK | No peering exists |
| VPC-A (Education) | VPC-C (Finance) | ❌ BLOCK | No peering exists |
| VPC-B (Research) | VPC-C (Finance) | ❌ BLOCK | No peering exists |
| VPC-D (Security) | VPC-A, B, C | ✅ ALLOW (monitoring) | VPC Peering + restricted SG |
| VPC-A, B, C | VPC-D (Security) | ✅ ALLOW (reporting) | VPC Peering + restricted SG |

### 3.3 Subnet Security Tiers

| Tier | Subnet Type | Internet Access | Use Case |
|---|---|---|---|
| **Public** | Public subnet with IGW route | Inbound + Outbound | ALB, NAT Gateway, Bastion |
| **Private App** | Private subnet with NAT GW route | Outbound only (via NAT) | Application servers |
| **Private DB** | Private subnet, no NAT route | None | Database instances (RDS) |

---

## 4. Kubernetes Segmentation

> **Status: ARCHITECTURE DESIGN / PROPOSED IMPLEMENTATION**

### 4.1 Namespace Zone Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    KUBERNETES ZONES                                 │
│                                                                     │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│   │  education   │  │  research    │  │  finance     │            │
│   │  MEDIUM      │  │  MEDIUM      │  │  HIGH        │            │
│   │              │  │              │  │              │            │
│   │  api pod     │  │  api pod     │  │  api pod     │            │
│   │  db pod      │  │  db pod      │  │  db pod      │            │
│   │  worker pod  │  │  worker pod  │  │  worker pod  │            │
│   └──────────────┘  └──────────────┘  └──────────────┘            │
│          ╳ ─ ─ ─ ─ ─ ─ ─ ─╳─ ─ ─ ─ ─ ─ ─ ─╳                      │
│          │    DEFAULT-DENY NetworkPolicy      │                     │
│          │    No cross-namespace traffic      │                     │
│                                                                     │
│   ┌──────────────┐  ┌──────────────┐                               │
│   │ aegismesh-   │  │ monitoring   │                               │
│   │ system       │  │              │                               │
│   │ HIGH         │  │ HIGH         │                               │
│   │              │  │              │                               │
│   │ aegismesh    │  │ wazuh-agent  │                               │
│   │ backend pod  │  │ log-shipper  │                               │
│   └──────────────┘  └──────────────┘                               │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 NetworkPolicy Model

Each domain namespace enforces a **default-deny** policy with explicit allow rules:

| Source Namespace | Destination Namespace | Policy | NetworkPolicy Rule |
|---|---|:---:|---|
| education | research | ❌ DENY | Default-deny (no allow rule) |
| education | finance | ❌ DENY | Default-deny (no allow rule) |
| research | finance | ❌ DENY | Default-deny (no allow rule) |
| education | aegismesh-system | ✅ ALLOW | Explicit allow for API reporting |
| monitoring | education, research, finance | ✅ ALLOW | Explicit allow for log collection |

---

## 5. Segmentation Equivalence Map

The following table shows how the same logical security zone is implemented across all three domains:

| Logical Zone | Private DC (VLAN) | AWS (VPC/Subnet) | Kubernetes (Namespace) |
|---|---|---|---|
| **Education / Faculty** | VLAN 10 (10.10.10.0/24) | VPC-A (10.1.0.0/16) | `education` |
| **Application Services** | VLAN 20 (10.10.20.0/24) | Private app subnets per VPC | Per-namespace API pods |
| **Management** | VLAN 30 (10.10.30.0/24) | VPC-D sec-private-mgmt (10.4.2.0/24) | `aegismesh-system` |
| **Database** | VLAN 40 (10.10.40.0/24) | Private DB subnets per VPC | Per-namespace DB pods |
| **Security / Logging** | VLAN 50 (10.10.50.0/24) | VPC-D (10.4.0.0/16) | `monitoring` |
| **DMZ / Public** | VLAN 60 (10.10.60.0/24) | Public subnets (ALB) | N/A (no public pods) |
| **Research** | N/A (DC does not host research) | VPC-B (10.2.0.0/16) | `research` |
| **Finance** | N/A (DC does not host finance) | VPC-C (10.3.0.0/16) | `finance` |

---

## 6. Defense-in-Depth Layering

Security is enforced at multiple independent layers. Compromise of any single layer does not grant unauthorized access:

```
Layer 1: Physical / Port Security
    │   Unused ports shutdown, PortFast, BPDU Guard
    ▼
Layer 2: VLAN Segmentation (L2)
    │   802.1Q trunks, Native VLAN 99, DTP disabled
    ▼
Layer 3: Network Access Control (L3/L4)
    │   SVI ACLs (DC), Security Groups (AWS), NetworkPolicies (K8s)
    ▼
Layer 4: Identity & Authorization
    │   IAM Roles (AWS), RBAC (K8s), VTY ACL (DC)
    ▼
Layer 5: Application Policy
    │   AegisMesh Policy Engine (ALLOW / RESTRICT / BLOCK / ISOLATE)
    ▼
Layer 6: Risk Assessment
    │   AegisMesh Risk Engine (contextual risk scoring 0–100)
    ▼
Layer 7: Detection & Response
    │   Wazuh SIEM + AegisMesh Detection Module
    ▼
Layer 8: Containment
        AegisMesh Containment Controller (blast-radius reduction)
```
