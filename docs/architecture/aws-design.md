# AegisMesh — AWS Cloud Architecture Design

**Version:** 1.0  
**Date:** 2026-08-28  
**Status:** DRAFT — Awaiting Approval  
**Traces to:** SR-02, FR-01, AC-01  

---

## 1. Design Scope

This document specifies the AWS public cloud architecture for AegisMesh. The cloud layer represents the multi-tenant, multi-domain application infrastructure that runs alongside the private datacenter and Kubernetes cluster.

**AWS is the public cloud component** of the hybrid architecture. It hosts domain-specific workloads (Education, Research, Finance) in isolated VPCs, with a dedicated Security/Management VPC for centralized monitoring and control.

---

## 2. VPC Architecture

### 2.1 VPC Layout

| VPC | Name | CIDR | Domain | Purpose |
|---|---|---|---|---|
| VPC-A | education-vpc | 10.1.0.0/16 | Education | Student/faculty learning services |
| VPC-B | research-vpc | 10.2.0.0/16 | Research | Research computing and data |
| VPC-C | finance-vpc | 10.3.0.0/16 | Finance | Financial systems and records |
| VPC-D | security-vpc | 10.4.0.0/16 | Security/Management | Monitoring, AegisMesh, logging |

### 2.2 Network Diagram

```
                    ┌──────────────────────────────────────┐
                    │              AWS CLOUD                │
                    │                                      │
    ┌───────────────┴──────────────────────────────────────┴───────────┐
    │                                                                  │
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
    │  │   VPC-A      │  │   VPC-B      │  │   VPC-C      │           │
    │  │  EDUCATION   │  │  RESEARCH    │  │  FINANCE     │           │
    │  │  10.1.0.0/16 │  │  10.2.0.0/16 │  │  10.3.0.0/16 │           │
    │  │              │  │              │  │              │           │
    │  │ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │           │
    │  │ │Public    │ │  │ │Public    │ │  │ │Private   │ │           │
    │  │ │Subnet    │ │  │ │Subnet    │ │  │ │Subnet    │ │           │
    │  │ │10.1.1/24 │ │  │ │10.2.1/24 │ │  │ │10.3.2/24 │ │           │
    │  │ └──────────┘ │  │ └──────────┘ │  │ └──────────┘ │           │
    │  │ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │           │
    │  │ │Private   │ │  │ │Private   │ │  │ │Private   │ │           │
    │  │ │Subnet    │ │  │ │Subnet    │ │  │ │Subnet    │ │           │
    │  │ │10.1.2/24 │ │  │ │10.2.2/24 │ │  │ │10.3.3/24 │ │           │
    │  │ └──────────┘ │  │ └──────────┘ │  │ └──────────┘ │           │
    │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │
    │         │                 │                 │                    │
    │         │    DEFAULT: NO PEERING / NO TRANSIT                    │
    │         │    (Isolation by design)                               │
    │         │                 │                 │                    │
    │  ┌──────┴─────────────────┴─────────────────┴───────┐           │
    │  │                  VPC-D                            │           │
    │  │            SECURITY / MANAGEMENT                  │           │
    │  │              10.4.0.0/16                          │           │
    │  │                                                   │           │
    │  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  │           │
    │  │  │ AegisMesh  │  │  Wazuh     │  │ CloudTrail │  │           │
    │  │  │ Backend    │  │  Manager   │  │ Logs       │  │           │
    │  │  └────────────┘  └────────────┘  └────────────┘  │           │
    │  └──────────────────────────────────────────────────┘           │
    └──────────────────────────────────────────────────────────────────┘
```

---

## 3. Subnet Design

### 3.1 VPC-A: Education

| Subnet | CIDR | Type | AZ | Purpose |
|---|---|---|---|---|
| edu-public-1 | 10.1.1.0/24 | Public | us-east-1a | Load balancer, NAT gateway |
| edu-private-app-1 | 10.1.2.0/24 | Private | us-east-1a | Application servers |
| edu-private-db-1 | 10.1.3.0/24 | Private | us-east-1a | Database (RDS) |
| edu-private-app-2 | 10.1.4.0/24 | Private | us-east-1b | Application servers (HA) |
| edu-private-db-2 | 10.1.5.0/24 | Private | us-east-1b | Database (RDS standby) |

### 3.2 VPC-B: Research

| Subnet | CIDR | Type | AZ | Purpose |
|---|---|---|---|---|
| res-public-1 | 10.2.1.0/24 | Public | us-east-1a | Load balancer, NAT gateway |
| res-private-app-1 | 10.2.2.0/24 | Private | us-east-1a | Research compute |
| res-private-db-1 | 10.2.3.0/24 | Private | us-east-1a | Research data store |
| res-private-app-2 | 10.2.4.0/24 | Private | us-east-1b | Research compute (HA) |
| res-private-db-2 | 10.2.5.0/24 | Private | us-east-1b | Research data store (HA) |

### 3.3 VPC-C: Finance

| Subnet | CIDR | Type | AZ | Purpose |
|---|---|---|---|---|
| fin-private-app-1 | 10.3.1.0/24 | Private | us-east-1a | Financial application |
| fin-private-db-1 | 10.3.2.0/24 | Private | us-east-1a | Financial database |
| fin-private-app-2 | 10.3.3.0/24 | Private | us-east-1b | Financial application (HA) |
| fin-private-db-2 | 10.3.4.0/24 | Private | us-east-1b | Financial database (HA) |

**Note:** Finance VPC has NO public subnets. All access is through VPC-D (management) or VPN.

### 3.4 VPC-D: Security/Management

| Subnet | CIDR | Type | AZ | Purpose |
|---|---|---|---|---|
| sec-public-1 | 10.4.1.0/24 | Public | us-east-1a | Bastion host, NAT gateway |
| sec-private-mgmt-1 | 10.4.2.0/24 | Private | us-east-1a | AegisMesh backend, Wazuh |
| sec-private-db-1 | 10.4.3.0/24 | Private | us-east-1a | AegisMesh PostgreSQL |
| sec-private-mgmt-2 | 10.4.4.0/24 | Private | us-east-1b | Management (HA) |

---

## 4. Inter-VPC Connectivity

### 4.1 Default Policy: DENY ALL

By default, VPCs have **no connectivity** to each other. This is the AWS default — VPCs are isolated unless explicitly connected.

### 4.2 Controlled Connectivity via VPC-D

Only VPC-D (Security/Management) has selective peering to other VPCs for monitoring and management purposes:

| Peering | Direction | Purpose | Security |
|---|---|---|---|
| VPC-D ↔ VPC-A | Bidirectional | AegisMesh monitors Education workloads | Restricted SG rules |
| VPC-D ↔ VPC-B | Bidirectional | AegisMesh monitors Research workloads | Restricted SG rules |
| VPC-D ↔ VPC-C | Bidirectional | AegisMesh monitors Finance workloads | Restricted SG rules |
| VPC-A ↔ VPC-B | **NONE** | Education and Research are isolated | No peering exists |
| VPC-A ↔ VPC-C | **NONE** | Education and Finance are isolated | No peering exists |
| VPC-B ↔ VPC-C | **NONE** | Research and Finance are isolated | No peering exists |

### 4.3 Route Table Configuration

Each VPC's route table only contains:
- Local VPC CIDR (automatic)
- VPC peering route to VPC-D only (where applicable)
- Internet Gateway route (public subnets only)
- NAT Gateway route (private subnets, for outbound only)

**No routes exist between VPC-A, VPC-B, or VPC-C.**

---

## 5. Security Groups

### 5.1 Design Principle

Security Groups follow **least privilege** — only the minimum required ports and sources are allowed. Default: deny all inbound, allow all outbound (outbound restricted where needed).

### 5.2 VPC-A Security Groups

| SG Name | Attached To | Inbound Rules | Outbound Rules |
|---|---|---|---|
| edu-alb-sg | ALB | 80/443 from 0.0.0.0/0 | App SG on app port |
| edu-app-sg | App instances | App port from ALB SG | DB SG on 5432; HTTPS to VPC-D |
| edu-db-sg | RDS | 5432 from App SG only | None (default deny) |

### 5.3 VPC-B Security Groups

| SG Name | Attached To | Inbound Rules | Outbound Rules |
|---|---|---|---|
| res-alb-sg | ALB | 80/443 from 0.0.0.0/0 | App SG on app port |
| res-app-sg | App instances | App port from ALB SG | DB SG on 5432; HTTPS to VPC-D |
| res-db-sg | RDS | 5432 from App SG only | None |

### 5.4 VPC-C Security Groups

| SG Name | Attached To | Inbound Rules | Outbound Rules |
|---|---|---|---|
| fin-app-sg | App instances | App port from VPC-D mgmt SG | DB SG on 5432; HTTPS to VPC-D |
| fin-db-sg | RDS | 5432 from App SG only | None |

### 5.5 VPC-D Security Groups

| SG Name | Attached To | Inbound Rules | Outbound Rules |
|---|---|---|---|
| sec-bastion-sg | Bastion host | 22 from admin CIDR | All internal |
| sec-aegismesh-sg | AegisMesh backend | 8000 from frontend; HTTPS from VPC-A/B/C | PostgreSQL to DB SG |
| sec-db-sg | PostgreSQL | 5432 from AegisMesh SG only | None |
| sec-wazuh-sg | Wazuh manager | 1514/1515 from agents; 443 from admin | None |

---

## 6. Network ACLs

Network ACLs provide **subnet-level** defense-in-depth on top of Security Groups.

### 6.1 Private Subnet NACL (All VPCs)

| Rule | Direction | Protocol | Port | Source/Dest | Action |
|---|---|---|---|---|---|
| 100 | Inbound | TCP | App port | VPC CIDR | ALLOW |
| 200 | Inbound | TCP | 1024-65535 | 0.0.0.0/0 | ALLOW (ephemeral) |
| * | Inbound | All | All | 0.0.0.0/0 | DENY |
| 100 | Outbound | TCP | 443 | 0.0.0.0/0 | ALLOW |
| 200 | Outbound | TCP | 5432 | VPC CIDR | ALLOW |
| 300 | Outbound | TCP | 1024-65535 | 0.0.0.0/0 | ALLOW (ephemeral) |
| * | Outbound | All | All | 0.0.0.0/0 | DENY |

### 6.2 Database Subnet NACL

| Rule | Direction | Protocol | Port | Source/Dest | Action |
|---|---|---|---|---|---|
| 100 | Inbound | TCP | 5432 | App subnet CIDR | ALLOW |
| 200 | Inbound | TCP | 1024-65535 | App subnet CIDR | ALLOW |
| * | Inbound | All | All | 0.0.0.0/0 | DENY |
| 100 | Outbound | TCP | 1024-65535 | App subnet CIDR | ALLOW |
| * | Outbound | All | All | 0.0.0.0/0 | DENY |

---

## 7. IAM Design

### 7.1 IAM Roles

| Role | Purpose | Permissions |
|---|---|---|
| AegisMeshServiceRole | AegisMesh backend execution | EC2 read, SG modify (own VPC only), CloudWatch write, CloudTrail read |
| EducationAppRole | Education application | S3 read (edu bucket), SQS (edu queue), CloudWatch write |
| ResearchAppRole | Research application | S3 read/write (research bucket), CloudWatch write |
| FinanceAppRole | Finance application | S3 read (finance bucket), KMS decrypt (finance key), CloudWatch write |
| MonitoringRole | Wazuh/monitoring | CloudWatch read, CloudTrail read, VPC Flow Logs read |
| AdminRole | Human administrators | Broad access with MFA requirement |

### 7.2 IAM Policies — Least Privilege Examples

**Education App — Cannot access Finance S3:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::aegismesh-education-*",
        "arn:aws:s3:::aegismesh-education-*/*"
      ]
    },
    {
      "Effect": "Deny",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::aegismesh-finance-*",
        "arn:aws:s3:::aegismesh-finance-*/*"
      ]
    }
  ]
}
```

### 7.3 Service Control Policies (SCP)

If using AWS Organizations:
- Deny all actions outside `us-east-1` (cost control)
- Deny public S3 bucket creation
- Require encryption on all S3 objects

---

## 8. Logging and Monitoring

### 8.1 CloudTrail

- Enabled in all regions
- Multi-region trail
- Log file validation enabled
- Logs stored in dedicated S3 bucket in VPC-D account
- CloudWatch integration for real-time alerting

### 8.2 VPC Flow Logs

- Enabled on all VPCs
- Capture ACCEPT and REJECT traffic
- Stored in CloudWatch Log Groups
- Retention: 30 days

### 8.3 CloudWatch Alarms

| Alarm | Condition | Action |
|---|---|---|
| Unauthorized API Call | CloudTrail: AccessDenied count > 5 in 5 min | SNS → AegisMesh webhook |
| SG Modification | CloudTrail: AuthorizeSecurityGroupIngress | SNS → AegisMesh webhook |
| Cross-VPC Traffic Spike | Flow Logs: rejected traffic > threshold | SNS → AegisMesh webhook |

---

## 9. Hybrid Connectivity

### 9.1 Private DC ↔ AWS

In production, this would use **AWS Site-to-Site VPN** or **Direct Connect**.

For the project demonstration:
- The connection is **architecturally documented** but not physically implemented.
- AegisMesh models the private DC as a separate security zone.
- The Packet Tracer network and AWS VPCs are treated as logically connected via a secure tunnel.

### 9.2 Simulated Hybrid Flow

```
Private DC (VLAN 20: App Server)
    → VPN Tunnel (encrypted)
    → VPC-D (Security VPC)
    → VPC Peering
    → VPC-A (Education VPC, private subnet)
```

---

## 10. Inter-VPC Traffic Matrix

| Source ↓ / Dest → | VPC-A (Edu) | VPC-B (Res) | VPC-C (Fin) | VPC-D (Sec) |
|---|---|---|---|---|
| **VPC-A (Education)** | — | ❌ BLOCK | ❌ BLOCK | ✅ ALLOW (monitoring) |
| **VPC-B (Research)** | ❌ BLOCK | — | ❌ BLOCK | ✅ ALLOW (monitoring) |
| **VPC-C (Finance)** | ❌ BLOCK | ❌ BLOCK | — | ✅ ALLOW (monitoring) |
| **VPC-D (Security)** | ✅ ALLOW (mgmt) | ✅ ALLOW (mgmt) | ✅ ALLOW (mgmt) | — |

---

## 11. Terraform Structure

```
infrastructure/terraform/
├── main.tf                    # Root module
├── variables.tf               # Global variables
├── outputs.tf                 # Global outputs
├── terraform.tfvars.example   # Example variable values (no secrets)
├── backend.tf                 # State backend configuration
│
├── vpc/
│   ├── main.tf                # VPC, subnets, IGW, NAT, route tables
│   ├── variables.tf
│   └── outputs.tf
│
├── security-groups/
│   ├── main.tf                # All Security Group definitions
│   ├── variables.tf
│   └── outputs.tf
│
├── iam/
│   ├── main.tf                # IAM roles, policies
│   ├── variables.tf
│   └── outputs.tf
│
├── routing/
│   ├── main.tf                # VPC peering, route table entries
│   ├── variables.tf
│   └── outputs.tf
│
└── logging/
    ├── main.tf                # CloudTrail, CloudWatch, Flow Logs
    ├── variables.tf
    └── outputs.tf
```

---

## 12. AWS Testing Plan

| Test ID | Test | Method | Expected |
|---|---|---|---|
| AWS-01 | Education app cannot reach Finance DB | SG verification; connectivity test | ❌ BLOCK |
| AWS-02 | Education app can reach its own DB | Connectivity test | ✅ ALLOW |
| AWS-03 | No VPC peering between VPC-A and VPC-B | AWS Console / Terraform plan | No peering exists |
| AWS-04 | No VPC peering between VPC-A and VPC-C | AWS Console / Terraform plan | No peering exists |
| AWS-05 | VPC-D can reach VPC-A for monitoring | Connectivity test | ✅ ALLOW |
| AWS-06 | Education IAM role cannot access Finance S3 | IAM policy simulation | ❌ AccessDenied |
| AWS-07 | CloudTrail captures API calls | CloudTrail event history | Events logged |
| AWS-08 | VPC Flow Logs capture rejected traffic | CloudWatch Logs | Rejected flows logged |
| AWS-09 | Finance VPC has no public subnets | Terraform plan / AWS Console | No IGW route |
| AWS-10 | Security Groups deny all by default | SG inspection | No 0.0.0.0/0 inbound (except ALB) |
