# AegisMesh — AWS Zero-Trust Cloud Architecture

**Status:** IMPLEMENTED AS TERRAFORM IaC & LOCALLY VALIDATED  
**Deployment Status:** ⚠️ **NOT DEPLOYED TO ACTIVE AWS ACCOUNT** (Local IaC Design & Validation Only)  
**IaC Framework:** HashiCorp Terraform `~> 1.5` / AWS Provider `~> 5.0`  

---

## 1. Executive Summary & Scope

The **AWS Cloud Domain** of AegisMesh provides a hardened, production-grade 3-Tier Zero-Trust Infrastructure as Code (IaC) implementation. It models the enterprise public cloud tier of our hybrid network alongside the Cisco Private Datacenter and Kubernetes Security Engine.

> [!IMPORTANT]
> **Safety & Cost Declaration:**  
> In accordance with project requirements, no live AWS infrastructure is provisioned or billed. All modules are designed, linted (`terraform fmt`), and syntax-validated (`terraform validate`) locally without requiring AWS cloud credentials or incurring cloud charges.

---

## 2. 3-Tier Zero-Trust Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               AEGISMESH AWS VPC (10.1.0.0/16)                          │
│                                                                                        │
│   [Public Internet]                                                                    │
│          │                                                                             │
│          ▼ HTTPS (443)                                                                 │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │ TIER 1: PUBLIC WEB TIER (10.1.1.0/24, 10.1.4.0/24)                             │   │
│   │                                                                                │   │
│   │  [Internet Gateway] ──▶ [aegismesh-web-sg] (Port 443 Ingress)                  │   │
│   │                         • No direct access to database tier                    │   │
│   │                         • Proxies traffic strictly to App Tier                 │   │
│   └────────────────────────────────────┬───────────────────────────────────────────┘   │
│                                        │                                               │
│                                        ▼ TCP (8000/8080) [SG-to-SG Ingress Only]       │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │ TIER 2: PRIVATE APPLICATION TIER (10.1.2.0/24, 10.1.5.0/24)                    │   │
│   │                                                                                │   │
│   │  [aegismesh-app-sg]                                                            │   │
│   │  • Ingress: Allowed ONLY from `aegismesh-web-sg`                               │   │
│   │  • No public IP exposure / No route to Internet Gateway                        │   │
│   │  • Egress: Allowed strictly to Database Tier on port 5432                      │   │
│   └────────────────────────────────────┬───────────────────────────────────────────┘   │
│                                        │                                               │
│                                        ▼ TCP (5432) [Mutual SG Ingress Only]           │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │ TIER 3: ISOLATED DATABASE TIER (10.1.3.0/24, 10.1.6.0/24)                      │   │
│   │                                                                                │   │
│   │  [aegismesh-db-sg] (PostgreSQL 5432)                                           │   │
│   │  • Ingress: Allowed ONLY from `aegismesh-app-sg`                               │   │
│   │  • STRICT DEFAULT-DENY: Zero direct Ingress from Web Tier or 0.0.0.0/0         │   │
│   │  • AIR-GAPPED: No Internet Gateway, No NAT Gateway, No Outbound Internet Route │   │
│   │  • RDS DB Subnet Group: Multi-AZ isolated storage                              │   │
│   └────────────────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Allowed Traffic Flow vs. Attack Scenarios

### Authorized Data Flow:
$$\text{Client (HTTPS:443)} \longrightarrow \text{Web SG} \longrightarrow \text{App SG (Port 8000)} \longrightarrow \text{DB SG (PostgreSQL:5432)}$$

* **Step 1:** External user initiates HTTPS connection to Web Tier (`aegismesh-web-sg`).
* **Step 2:** Web tier authenticates and forwards business logic requests to App Tier (`aegismesh-app-sg`).
* **Step 3:** App tier queries isolated database (`aegismesh-db-sg`) over authenticated PostgreSQL port 5432.

### Direct Database Bypass Interception (Threat E-04 / C-01):
$$\text{Compromised Web / External Node} \xlongrightarrow{\text{Direct Port 5432 Probe}} \text{Database SG} \quad \mathbf{[BLOCKED]}$$

* If an attacker compromises a Web Tier container or external client and attempts to query the database directly:
  1. **Network Layer:** The Database subnets have no route to the Internet Gateway.
  2. **Security Group Layer:** `aegismesh-db-sg` only permits ingress from the exact security group ID of `aegismesh-app-sg`. Packets from `aegismesh-web-sg` or external IPs are dropped statefully at the hypervisor layer.

---

## 4. Cross-Domain Policy Alignment

AegisMesh enforces identical Zero-Trust semantics across all three infrastructure domains:

| Zero-Trust Control | Cisco Datacenter (On-Premises) | Kubernetes Cluster (Containers) | AWS Cloud (Terraform) |
| :--- | :--- | :--- | :--- |
| **Edge / Web Ingress** | VLAN 10 (Faculty) SVI Ingress ACL Line 1 Permit | `allow-education-client` NetworkPolicy | `aegismesh-web-sg` (HTTPS 443) |
| **App-to-DB Tiering** | VLAN 30 $\to$ VLAN 40 Permit; VLAN 10 $\to$ VLAN 40 Deny | Namespace Isolation (`education` vs `finance`) | `aegismesh-app-sg` $\to$ `aegismesh-db-sg` SG Reference |
| **Default Deny** | Implicit Deny at end of Cisco SVI ACLs | `default-deny-all` NetworkPolicy | Default Deny on all AWS Security Groups |
| **Automated Quarantine** | AegisMesh Port / VLAN Quarantine | Dynamic `aegismesh-isolate-<workload>` Calico Policy | Security Group Ingress Revocation / Quarantine SG |

---

## 5. Cost Safety Decisions

* **NAT Gateway Disabled by Default:** In AWS, NAT Gateways incur ongoing hourly charges ($0.045/hr + data processing). The variable `enable_nat_gateway = false` ensures the configuration remains cost-free and safe for local development, academic review, and student portfolios.
* **Pure IaC Validation:** Designed for validation with `terraform init -backend=false` and `terraform validate`.
