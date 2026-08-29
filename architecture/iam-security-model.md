# AegisMesh — Identity & Access Management Security Model

**Version:** 1.0  
**Date:** 2026-08-29  
**Project:** AegisMesh — Cisco Virtual Internship 2026 Cyber Security  
**Traces to:** SR-04 (Zero Trust), SR-05 (Lateral Movement Prevention), NFR-01 (Security)  

---

## 1. IAM Design Philosophy

The AegisMesh IAM model enforces **Zero Trust** principles: no implicit trust from network location, every access request is explicitly authorized, and least privilege is enforced at every layer.

| Principle | Implementation |
|---|---|
| **Verify Explicitly** | Every request requires authentication; context (identity, device, location, risk) is evaluated |
| **Least Privilege** | Users and workloads receive only the minimum permissions required for their function |
| **Assume Breach** | Segmentation limits blast radius; containment activates automatically on anomaly detection |
| **MFA Everywhere** | Multi-factor authentication required for all human access paths |
| **Separation of Duties** | Administrative roles are separated from application roles across all domains |

---

## 2. Private Datacenter Identity Model

> **Status: IMPLEMENTED AND VALIDATED in Cisco Packet Tracer**

### 2.1 Zone-Based Access Control

In the private datacenter, identity is enforced through **VLAN zone assignment** and **VTY access restrictions**:

| Identity Layer | Mechanism | Implementation |
|---|---|---|
| **User Zone Assignment** | Physical port → VLAN mapping | Faculty PCs on VLAN 10 access ports |
| **Server Zone Assignment** | Static VLAN assignment per server role | App (VLAN 20), DB (VLAN 40), etc. |
| **Admin Authentication** | Local username/password + SSH v2 | `username admin privilege 15 secret` |
| **VTY Access Restriction** | Standard ACL on VTY lines | `MGMT-VTY-ACCESS`: permit 10.10.30.0/24 only |
| **Console Access** | Password-protected console with timeout | `line console 0` with login + exec-timeout |

### 2.2 Management Plane Isolation

Only the Management VLAN (30) can access network device administration:

```
VLAN 10 (Faculty)    ──→ SSH to SW-CORE ──→ ❌ BLOCKED (MGMT-VTY-ACCESS)
VLAN 20 (App)        ──→ SSH to SW-CORE ──→ ❌ BLOCKED (MGMT-VTY-ACCESS)
VLAN 30 (Management) ──→ SSH to SW-CORE ──→ ✅ ALLOWED (MGMT-VTY-ACCESS)
VLAN 40 (Database)   ──→ SSH to SW-CORE ──→ ❌ BLOCKED (MGMT-VTY-ACCESS)
VLAN 50 (Security)   ──→ SSH to SW-CORE ──→ ❌ BLOCKED (MGMT-VTY-ACCESS)
VLAN 60 (DMZ)        ──→ SSH to SW-CORE ──→ ❌ BLOCKED (MGMT-VTY-ACCESS)
```

---

## 3. AWS Cloud IAM Model

> **Status: ARCHITECTURE DESIGN / PROPOSED IMPLEMENTATION**

### 3.1 IAM Role Architecture

Each workload domain has a dedicated IAM role with explicit cross-domain deny:

| IAM Role | Attached To | Permitted Resources | Explicit Deny |
|---|---|---|---|
| `AegisMeshServiceRole` | AegisMesh backend (VPC-D) | EC2 read, SG modify (own VPC), CloudWatch write, CloudTrail read | — |
| `EducationAppRole` | Education app servers (VPC-A) | S3 read (edu bucket), SQS (edu queue) | `s3:*` on finance-*, research-* buckets |
| `ResearchAppRole` | Research compute (VPC-B) | S3 read/write (research bucket) | `s3:*` on finance-*, education-* buckets |
| `FinanceAppRole` | Finance application (VPC-C) | S3 read (finance bucket), KMS decrypt (finance key) | `s3:*` on education-*, research-* buckets |
| `MonitoringRole` | Wazuh manager (VPC-D) | CloudWatch read, CloudTrail read, VPC Flow Logs read | All write operations |
| `AdminRole` | Human administrators | Broad access | Requires MFA condition |

### 3.2 IAM Policy — Explicit Cross-Domain Deny

Example: Education application role cannot access Finance resources:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowEducationResources",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::aegismesh-education-*",
        "arn:aws:s3:::aegismesh-education-*/*"
      ]
    },
    {
      "Sid": "DenyFinanceResources",
      "Effect": "Deny",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::aegismesh-finance-*",
        "arn:aws:s3:::aegismesh-finance-*/*"
      ]
    },
    {
      "Sid": "DenyResearchResources",
      "Effect": "Deny",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::aegismesh-research-*",
        "arn:aws:s3:::aegismesh-research-*/*"
      ]
    }
  ]
}
```

### 3.3 MFA Enforcement

| Access Type | MFA Required | Implementation |
|---|---|---|
| AWS Console (human admin) | **Yes** | IAM policy condition: `aws:MultiFactorAuthPresent` |
| Bastion Host SSH | **Yes** | MFA-protected session token required before SSH |
| API programmatic access (service roles) | No | Instance profile provides temporary credentials |
| Emergency break-glass | **Yes** | Separate IAM user with MFA + CloudTrail alert |

### 3.4 Service Control Policies (SCP)

If using AWS Organizations, organization-level guardrails enforce:

| SCP | Effect | Purpose |
|---|---|---|
| Region Restriction | Deny all actions outside `us-east-1` | Cost control and compliance |
| Public S3 Prevention | Deny `s3:PutBucketPublicAccessBlock` changes | Prevent data exposure |
| Encryption Enforcement | Deny unencrypted S3 object uploads | Data-at-rest protection |

---

## 4. Kubernetes RBAC Model

> **Status: ARCHITECTURE DESIGN / PROPOSED IMPLEMENTATION**

### 4.1 RBAC Architecture

```
┌─────────────────────────────────────────────────────────┐
│                KUBERNETES RBAC MODEL                    │
│                                                         │
│   ClusterRoles (Cluster-Wide)                          │
│   ├── cluster-admin        → Full cluster access       │
│   ├── aegismesh-controller → NetworkPolicy CRUD        │
│   └── monitoring-reader    → Read pods/logs across NS  │
│                                                         │
│   Namespace Roles (Per-Namespace)                       │
│   ├── education-developer  → Deploy to education only  │
│   ├── research-developer   → Deploy to research only   │
│   ├── finance-developer    → Deploy to finance only    │
│   └── namespace-viewer     → Read-only within NS       │
│                                                         │
│   ServiceAccounts (Per-Pod)                             │
│   ├── education-api-sa     → education namespace only  │
│   ├── research-api-sa      → research namespace only   │
│   ├── finance-api-sa       → finance namespace only    │
│   └── aegismesh-sa         → aegismesh-system NS       │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Cross-Namespace Access Prevention

| Actor | Source Namespace | Can Access education | Can Access research | Can Access finance |
|---|---|:---:|:---:|:---:|
| `education-api-sa` | education | ✅ | ❌ | ❌ |
| `research-api-sa` | research | ❌ | ✅ | ❌ |
| `finance-api-sa` | finance | ❌ | ❌ | ✅ |
| `aegismesh-sa` | aegismesh-system | ✅ (monitor) | ✅ (monitor) | ✅ (monitor) |
| `education-developer` | N/A (human) | ✅ (deploy) | ❌ | ❌ |

### 4.3 Pod Security Standards

| Standard | Level | Enforcement |
|---|---|---|
| **Baseline** | All namespaces | Minimum pod security requirements |
| **Restricted** | finance, aegismesh-system | No privileged containers, no hostPath, no hostNetwork |

---

## 5. Faculty Remote Access — Zero Trust VPN

### 5.1 Access Flow

```
Faculty User (Remote / Off-Campus)
    │
    ├── 1. VPN Client Connection
    │       Cisco AnyConnect or AWS Client VPN
    │       Endpoint: R-EDGE (Private DC) or VPC-D (AWS)
    │
    ├── 2. Multi-Factor Authentication
    │       Username + Password + TOTP/Push MFA
    │       Backend: RADIUS server or AWS IAM Identity Center
    │
    ├── 3. Authorization & Group Assignment
    │       User mapped to role group (faculty, developer, admin)
    │       Group determines VLAN placement (DC) or IAM role (AWS)
    │
    ├── 4. Tunnel Establishment
    │       IPsec IKEv2, AES-256-GCM, SHA-384
    │       Split tunneling DISABLED (all traffic through enterprise)
    │
    ├── 5. Zone Placement
    │       Remote faculty → same restrictions as on-campus VLAN 10
    │       Same ACLs, same SG rules, same NetworkPolicies apply
    │
    └── 6. Continuous Evaluation
            AegisMesh evaluates each request: identity + zone + intent + risk
            Session tokens expire after configurable timeout
            All activity logged to Wazuh SIEM
```

### 5.2 Key Security Controls

| Control | Implementation | Cisco Problem Statement Mapping |
|---|---|---|
| MFA on all remote access | TOTP or push notification | Secure faculty remote access |
| No split tunneling | All traffic routes through enterprise | Zero Trust approach |
| Same-as-on-campus restrictions | VLAN ACLs / SG rules apply identically | Consistent security posture |
| Session timeout | Configurable expiry (default 8 hours) | Minimize credential exposure |
| Full audit logging | Every connection logged with identity | Monitoring and security logging |

---

## 6. IAM Cross-Domain Consistency

The following table shows how the same access control intent is enforced across all three domains:

| Access Control Intent | Private DC | AWS | Kubernetes |
|---|---|---|---|
| **Only admins access infrastructure** | MGMT-VTY-ACCESS ACL | AdminRole + MFA condition | cluster-admin ClusterRole |
| **Apps cannot reach management** | VLAN 20 → VLAN 30 BLOCK | App SG → no route to bastion | No RBAC binding to admin namespace |
| **Domain isolation** | Per-VLAN ACLs | Per-VPC IAM roles with cross-domain deny | Per-namespace RBAC + NetworkPolicy |
| **Monitoring can observe all** | VLAN 50 permitted to read | MonitoringRole: read-only | monitoring-reader ClusterRole |
| **Default deny** | ACL implicit deny all | SG deny all inbound by default | Default-deny NetworkPolicy |
