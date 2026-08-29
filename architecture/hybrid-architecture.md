# AegisMesh — Secure Hybrid Datacenter Architecture

**Version:** 1.0  
**Date:** 2026-08-29  
**Project:** AegisMesh — Cisco Virtual Internship 2026 Cyber Security  
**Status:** Architecture Design Complete | Private Datacenter Implemented & Validated in Cisco Packet Tracer  

---

## 1. Executive Summary

AegisMesh is a **security control and decision architecture** that operates across three infrastructure domains to prevent lateral movement and enforce least-privilege access boundaries in a hybrid enterprise environment.

| Domain | Infrastructure | Security Enforcement | Implementation Status |
|---|---|---|---|
| **Private Datacenter** | Cisco Switches & Routers | VLANs, Extended ACLs, SVI Routing | **IMPLEMENTED AND VALIDATED** |
| **Public Cloud** | AWS (4 VPCs) | Security Groups, NACLs, IAM Policies | Architecture Design |
| **Container Platform** | Kubernetes (3 Namespaces) | NetworkPolicies, RBAC, Pod Security | Architecture Design |

> **Primary Security Objective:**  
> If one application or workload is compromised, the compromise must not be able to spread laterally to unauthorized applications, VPCs, Kubernetes workloads, or the private enterprise network.

---

## 2. Hybrid Architecture Topology

```
                                    ┌─────────────────────────────────┐
                                    │         USERS / FACULTY         │
                                    │   Campus + Remote (VPN + MFA)   │
                                    └───────────────┬─────────────────┘
                                                    │
                                        ┌───────────┴───────────┐
                                        │    IDENTITY / IAM     │
                                        │  Authentication Layer │
                                        │  (MFA, RBAC, Tokens)  │
                                        └───────────┬───────────┘
                                                    │
                        ┌───────────────────────────┼───────────────────────────┐
                        │                           │                           │
            ┌───────────┴───────────┐   ┌───────────┴───────────┐   ┌───────────┴───────────┐
            │   PRIVATE DATACENTER  │   │      AWS CLOUD        │   │  KUBERNETES CLUSTER   │
            │   ══════════════════  │   │  ══════════════════   │   │  ══════════════════   │
            │                       │   │                       │   │                       │
            │  ┌─────┐  ┌────────┐  │   │  ┌───────┐ ┌───────┐ │   │  ┌──────────────────┐ │
            │  │R-EDGE│→│SW-CORE │  │   │  │ VPC-A │ │ VPC-B │ │   │  │  education NS    │ │
            │  └─────┘  └───┬────┘  │   │  │ Edu   │ │ Res   │ │   │  │  research NS     │ │
            │       ┌───────┼─────┐ │   │  └───────┘ └───────┘ │   │  │  finance NS      │ │
            │  ┌────┴──┐ ┌──┴──┐  │ │   │  ┌───────┐ ┌───────┐ │   │  │  aegismesh-sys   │ │
            │  │SW-AC-1│ │AC-2 │  │ │   │  │ VPC-C │ │ VPC-D │ │   │  └──────────────────┘ │
            │  └───────┘ └─────┘  │ │   │  │ Fin   │ │ Sec   │ │   │                       │
            │         ┌──────┐    │ │   │  └───────┘ └───────┘ │   │  NetworkPolicies      │
            │         │AC-3  │    │ │   │                       │   │  RBAC + PSS            │
            │         └──────┘    │ │   │  Security Groups      │   │  Resource Quotas       │
            │                     │ │   │  NACLs + IAM          │   │                       │
            │  6 VLANs + ACLs     │ │   │  CloudTrail Logging   │   │  Calico CNI           │
            └─────────┬───────────┘ └───┴───────────┬───────────┘   └───────────┬───────────┘
                      │                             │                           │
                      │         ┌───────────────────┤                           │
                      │         │   VPN / DIRECT     │                           │
                      │         │   CONNECT TUNNEL   │                           │
                      └─────────┤   (Encrypted)      ├───────────────────────────┘
                                └───────────────────-┘
                                            │
                                ┌───────────┴───────────┐
                                │   AEGISMESH SECURITY   │
                                │    CONTROL PLANE       │
                                │                        │
                                │  Policy Engine         │
                                │  Risk Engine           │
                                │  Decision Engine       │
                                │  Containment Controller│
                                └───────────┬────────────┘
                                            │
                                ┌───────────┴───────────┐
                                │   MONITORING / SIEM    │
                                │   Wazuh + CloudWatch   │
                                │   VPC Flow Logs        │
                                └───────────┬────────────┘
                                            │
                                ┌───────────┴───────────┐
                                │   SECURITY DASHBOARD   │
                                │   Next.js + React Flow │
                                └────────────────────────┘
```

---

## 3. Domain Architecture Detail

### 3.1 Private Datacenter — Cisco Packet Tracer

> **Status: IMPLEMENTED AND VALIDATED**

The private datacenter is fully modeled, configured, and empirically tested in Cisco Packet Tracer 8.2+.

| Component | Specification | Reference Document |
|---|---|---|
| **Topology** | 1 Edge Router (Cisco 2911), 1 Core L3 Switch (3560), 3 Access Switches (2960), 10 Endpoints | [network-design.md](../docs/architecture/network-design.md) |
| **Segmentation** | 6 VLANs (Faculty, App Servers, Management, Database, Security, DMZ) + Native VLAN 99 | [vlan-inventory.md](../packet-tracer/vlan/vlan-inventory.md) |
| **Access Control** | 6 SVI Ingress Extended ACLs + VTY Standard ACL | [acl-design.md](../packet-tracer/acl/acl-design.md) |
| **Trunk Hardening** | 802.1Q with DTP disabled, explicit VLAN allow lists, unused Native VLAN 99 | [SW-CORE.txt](../packet-tracer/configurations/SW-CORE.txt) |
| **Validation** | Stage A baseline + Stage B ACL enforcement verified | [validation-summary.md](../packet-tracer/test-results/validation-summary.md) |

**Verified Test Results:**
- Faculty → App Server (10.10.20.10): **ALLOWED ✅**
- Faculty → Database (10.10.40.10): **BLOCKED ✅**
- Faculty → Security VLAN (10.10.50.1): **BLOCKED ✅**
- `show access-lists` ACL match counters: **Non-zero ✅**

### 3.2 AWS Public Cloud

> **Status: ARCHITECTURE DESIGN / PROPOSED IMPLEMENTATION**

The AWS cloud layer provides domain-level workload isolation using VPC boundaries, Security Groups, and IAM policies.

| Component | Specification | Reference Document |
|---|---|---|
| **VPC Isolation** | 4 VPCs: Education (10.1.0.0/16), Research (10.2.0.0/16), Finance (10.3.0.0/16), Security (10.4.0.0/16) | [aws-design.md](../docs/architecture/aws-design.md) |
| **Subnet Architecture** | Public + Private subnets per VPC; Finance VPC has NO public subnets | [aws-design.md](../docs/architecture/aws-design.md) |
| **Inter-VPC Policy** | DEFAULT DENY ALL; only VPC-D (Security) has selective peering for monitoring | [aws-design.md](../docs/architecture/aws-design.md) |
| **Security Groups** | Per-instance least-privilege firewall rules; no broad 0.0.0.0/0 inbound except ALB | [aws-design.md](../docs/architecture/aws-design.md) |
| **IAM** | Per-domain roles with explicit cross-domain deny; MFA on admin roles | [aws-design.md](../docs/architecture/aws-design.md) |
| **Logging** | CloudTrail (all regions), VPC Flow Logs (accept + reject), CloudWatch Alarms | [aws-design.md](../docs/architecture/aws-design.md) |

### 3.3 Kubernetes Container Platform

> **Status: ARCHITECTURE DESIGN / PROPOSED IMPLEMENTATION**

The Kubernetes layer provides workload-level isolation using namespace boundaries, NetworkPolicies, and RBAC.

| Component | Specification | Reference Document |
|---|---|---|
| **Cluster** | kind (K8s in Docker) with Calico CNI for real NetworkPolicy enforcement | [kubernetes-design.md](../docs/architecture/kubernetes-design.md) |
| **Namespaces** | `education`, `research`, `finance`, `aegismesh-system`, `monitoring` | [kubernetes-design.md](../docs/architecture/kubernetes-design.md) |
| **NetworkPolicies** | Default-deny ingress/egress per namespace; explicit allow for authorized flows only | [kubernetes-design.md](../docs/architecture/kubernetes-design.md) |
| **RBAC** | Per-namespace Roles and RoleBindings; no cross-namespace access | [kubernetes-design.md](../docs/architecture/kubernetes-design.md) |
| **Pod Security** | Restricted Pod Security Standards; no privileged containers | [kubernetes-design.md](../docs/architecture/kubernetes-design.md) |
| **Resource Controls** | ResourceQuotas and LimitRanges per namespace to prevent resource exhaustion | [kubernetes-design.md](../docs/architecture/kubernetes-design.md) |

---

## 4. Hybrid Connectivity Model

### 4.1 Private DC ↔ AWS Cloud

| Parameter | Design Decision |
|---|---|
| **Connection Type** | AWS Site-to-Site VPN (IPsec IKEv2) |
| **Endpoint (On-Premises)** | R-EDGE (Cisco 2911) — GigabitEthernet0/0 (Internet-facing) |
| **Endpoint (AWS)** | Virtual Private Gateway attached to VPC-D (Security VPC) |
| **Encryption** | AES-256-GCM with SHA-384 integrity |
| **Routing** | Static routes; Private DC traffic enters AWS only via VPC-D |
| **Failover** | Dual-tunnel VPN with automatic failover |
| **Monitoring** | VPN tunnel status monitored via CloudWatch metrics |

> **Note:** The VPN connection is architecturally documented. In the Packet Tracer simulation, the private datacenter operates as an independent security zone. The AegisMesh security engine treats the private DC as a logically connected domain.

### 4.2 AWS ↔ Kubernetes

| Parameter | Design Decision |
|---|---|
| **Hosting Model** | Kubernetes runs within VPC-D (Security VPC) on EC2 instances or as EKS |
| **Network Integration** | Pod CIDR (192.168.0.0/16) routes through VPC-D subnet |
| **Service Exposure** | ClusterIP for internal; NodePort/LoadBalancer for VPC-D ingress |
| **Security Boundary** | Kubernetes NetworkPolicies enforce pod-level isolation independent of VPC SGs |

### 4.3 Cross-Domain Traffic Matrix

| Source ↓ / Destination → | Private DC | VPC-A (Edu) | VPC-B (Res) | VPC-C (Fin) | VPC-D (Sec) | K8s (edu) | K8s (fin) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Private DC** | — | ❌ | ❌ | ❌ | ✅ VPN | ❌ | ❌ |
| **VPC-A (Education)** | ❌ | — | ❌ | ❌ | ✅ Peer | ❌ | ❌ |
| **VPC-B (Research)** | ❌ | ❌ | — | ❌ | ✅ Peer | ❌ | ❌ |
| **VPC-C (Finance)** | ❌ | ❌ | ❌ | — | ✅ Peer | ❌ | ❌ |
| **VPC-D (Security)** | ✅ VPN | ✅ Mgmt | ✅ Mgmt | ✅ Mgmt | — | ✅ | ✅ |
| **K8s (education)** | ❌ | ❌ | ❌ | ❌ | ✅ | — | ❌ |
| **K8s (finance)** | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | — |

**Legend:** ✅ = Authorized (controlled) | ❌ = BLOCKED (no route exists)

---

## 5. Trust Boundaries

The architecture defines 11 trust boundaries across three infrastructure domains:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        TRUST BOUNDARY MAP                              │
│                                                                        │
│   PRIVATE DATACENTER                                                   │
│   ┌──────────────────────────────────────────────────────┐             │
│   │  TB-1: Internet ↔ DMZ (VLAN 60)                      │             │
│   │  TB-2: DMZ ↔ Internal Network (VLANs 10–50)          │             │
│   │  TB-3: Faculty VLAN 10 ↔ Application VLAN 20         │             │
│   │  TB-4: Application VLAN 20 ↔ Database VLAN 40        │             │
│   │  TB-5: Any VLAN ↔ Management VLAN 30                 │             │
│   └──────────────────────────────────────────────────────┘             │
│                            │                                           │
│   TB-11: Private DC ↔ AWS Cloud (VPN Tunnel)                          │
│                            │                                           │
│   AWS CLOUD                │                                           │
│   ┌────────────────────────┴─────────────────────────────┐             │
│   │  TB-6: VPC-A ↔ VPC-B ↔ VPC-C ↔ VPC-D                │             │
│   └──────────────────────────────────────────────────────┘             │
│                            │                                           │
│   KUBERNETES               │                                           │
│   ┌────────────────────────┴─────────────────────────────┐             │
│   │  TB-7: Namespace ↔ Namespace                         │             │
│   │  TB-8: Pod ↔ Kubernetes API Server                   │             │
│   └──────────────────────────────────────────────────────┘             │
│                                                                        │
│   APPLICATION LAYER                                                    │
│   ┌──────────────────────────────────────────────────────┐             │
│   │  TB-9:  Frontend ↔ Backend API                       │             │
│   │  TB-10: Backend ↔ Database                           │             │
│   └──────────────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Security Control Equivalence Across Domains

A core strength of the AegisMesh architecture is that the same security principles are enforced consistently across all three domains, using each domain's native control primitives:

| Security Principle | Private Datacenter (Cisco) | AWS Cloud | Kubernetes |
|---|---|---|---|
| **Network Segmentation** | VLANs (L2) + SVIs (L3) | VPC Isolation (L3) | Namespace + NetworkPolicy (L3/L4) |
| **Access Control** | Extended ACLs on SVIs | Security Groups per instance | NetworkPolicy ingress/egress rules |
| **Default Deny** | ACL implicit deny | SG default deny inbound | Default-deny NetworkPolicy |
| **Management Isolation** | VLAN 30 + VTY ACL | Bastion Host + IAM MFA | aegismesh-system namespace + RBAC |
| **Monitoring Isolation** | VLAN 50 (Security/Logging) | VPC-D + CloudTrail + Flow Logs | monitoring namespace |
| **Identity & Authorization** | Port-based VLAN assignment | IAM Roles + Policies | RBAC + ServiceAccounts |
| **Blast-Radius Containment** | Per-VLAN ACL boundaries | Per-VPC SG + no cross-VPC peering | Per-namespace NetworkPolicy |
| **Trunk/Transit Hardening** | DTP disabled, Native VLAN 99 | No transit gateway (isolation) | Calico CNI with policy enforcement |

---

## 7. Faculty Remote Access Architecture

### 7.1 Design Approach

Faculty access follows a **Zero Trust** model — no implicit trust from network location:

```
Faculty (Remote)
    │
    ├── Step 1: VPN Client + MFA Authentication
    │   └── Cisco AnyConnect / AWS Client VPN
    │
    ├── Step 2: VPN Tunnel to Private DC or VPC-D
    │   └── IPsec IKEv2, AES-256-GCM
    │
    ├── Step 3: Identity verified by IAM / RADIUS
    │   └── Role-based group assignment
    │
    ├── Step 4: Placed into Faculty VLAN 10 (DC) or edu-private-app (AWS)
    │   └── Same ACL/SG restrictions apply as on-campus
    │
    └── Step 5: AegisMesh evaluates each access request
        └── Context: identity + zone + intent + risk = ALLOW/BLOCK
```

### 7.2 Key Controls
- **MFA is mandatory** for all remote access
- **Split tunneling is disabled** — all traffic routes through the enterprise security controls
- Remote users receive the **same access restrictions** as on-campus users
- VPN session tokens expire after configurable timeout
- All remote access attempts are logged to Wazuh SIEM

---

## 8. Incident Containment and Blast-Radius Reduction

### 8.1 Containment Architecture

When a workload compromise is detected, containment operates at multiple layers simultaneously:

```
Detection (Wazuh alert / anomaly)
    │
    ▼
AegisMesh Risk Engine (score > 80 = CRITICAL)
    │
    ▼
AegisMesh Containment Controller
    │
    ├── Private DC: ACL rules restrict compromised VLAN's outbound paths
    ├── AWS: Security Group updated to deny egress to unauthorized VPCs
    ├── Kubernetes: NetworkPolicy updated to deny all egress except dependencies
    │
    ▼
Workload State: NORMAL → SUSPICIOUS → CONTAINED
    │
    ▼
Incident Created → Dashboard Notification → Audit Trail
```

### 8.2 Blast-Radius Boundaries

| Compromise Scenario | Blast Radius Limit | Enforcement Mechanism |
|---|---|---|
| Faculty PC compromised | VLAN 10 only; cannot reach DB (VLAN 40) or Mgmt (VLAN 30) | `FACULTY-ACCESS` ACL |
| App Server compromised | VLAN 20 only; cannot reach Mgmt (VLAN 30) | `APP-SERVER-ACCESS` ACL |
| DMZ server compromised | VLAN 60 only; cannot reach DB (VLAN 40) | `DMZ-ACCESS` ACL |
| Education VPC workload compromised | VPC-A only; no peering to VPC-B or VPC-C | VPC isolation + SG |
| K8s education pod compromised | education namespace only; no cross-namespace traffic | NetworkPolicy default-deny |
| Database server compromised | VLAN 40 only; cannot initiate toward Faculty (VLAN 10) | `DB-ACCESS` ACL |

---

## 9. Scalability Considerations

The architecture supports horizontal and vertical scaling without compromising security boundaries:

| Dimension | Scaling Approach | Security Implication |
|---|---|---|
| **More VLANs** | Add VLANs to SW-CORE with new SVI + ACL | New zone automatically inherits default-deny |
| **More VPCs** | Add VPC with Terraform; only peer to VPC-D if needed | Isolation by default; no lateral movement risk |
| **More Namespaces** | Add namespace with default-deny NetworkPolicy | Pod isolation from first deployment |
| **More Endpoints** | Add endpoints to existing VLANs | Inherit existing ACL boundaries |
| **Multi-Region** | Replicate VPC architecture in additional AWS regions | Cross-region isolation maintained |
| **Backend Scaling** | Horizontal scaling of AegisMesh FastAPI behind ALB | Stateless evaluation; PostgreSQL handles state |

---

## 10. Document Cross-References

| Document | Location | Purpose |
|---|---|---|
| System Architecture | [docs/architecture/architecture.md](../docs/architecture/architecture.md) | Component responsibilities and integration model |
| Network Design | [docs/architecture/network-design.md](../docs/architecture/network-design.md) | Private datacenter VLAN/ACL specification |
| AWS Design | [docs/architecture/aws-design.md](../docs/architecture/aws-design.md) | Cloud VPC, IAM, Security Group specification |
| Kubernetes Design | [docs/architecture/kubernetes-design.md](../docs/architecture/kubernetes-design.md) | Namespace, RBAC, NetworkPolicy specification |
| AegisMesh Engine | [docs/architecture/aegismesh-design.md](../docs/architecture/aegismesh-design.md) | Security engine API and module design |
| Threat Model | [docs/architecture/threat-model.md](../docs/architecture/threat-model.md) | STRIDE analysis with attack trees |
| Threat Traceability | [docs/threat-traceability.md](../docs/threat-traceability.md) | Threat-to-control-to-test mapping |
| Requirements | [docs/requirements/requirements.md](../docs/requirements/requirements.md) | Functional, non-functional, and security requirements |
| Validation Results | [packet-tracer/test-results/validation-summary.md](../packet-tracer/test-results/validation-summary.md) | Empirical Packet Tracer test results |
