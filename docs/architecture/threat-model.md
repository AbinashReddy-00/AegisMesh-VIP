# AegisMesh — Threat Model

**Version:** 1.0  
**Date:** 2026-08-28  
**Status:** DRAFT — Awaiting Approval  
**Methodology:** STRIDE + Attack Tree Analysis  
**Traces to:** SR-01 through SR-05, FR-05, AC-02  

---

## 1. Scope

This threat model covers the AegisMesh hybrid security architecture across:

- Private datacenter (Cisco Packet Tracer network)
- AWS cloud infrastructure (4 VPCs)
- Kubernetes cluster (3 namespaces)
- AegisMesh security engine (FastAPI backend)
- Dashboard (Next.js frontend)

---

## 2. Threat Actors

| Actor | Capability | Motivation | Access Level |
|---|---|---|---|
| **External Attacker** | Moderate; uses known exploits, phishing | Data theft, disruption | Internet-facing services (DMZ) |
| **Compromised Application** | High; has valid credentials for its own domain | Lateral movement post-compromise | Internal network of its own VLAN/VPC/namespace |
| **Malicious Insider** | High; has legitimate credentials | Data exfiltration, sabotage | Authenticated access per role |
| **Compromised Container** | Moderate; Kubernetes pod with service account | Escape namespace, access secrets | Pod-level network and API access |
| **Supply Chain Compromise** | Low probability, high impact | Backdoor in dependencies | Runs within application context |

---

## 3. Trust Boundaries

```
Trust Boundary 1: Internet ↔ DMZ (VLAN 60)
Trust Boundary 2: DMZ ↔ Internal Network (VLANs 10–50)
Trust Boundary 3: Faculty VLAN ↔ Application VLAN
Trust Boundary 4: Application VLAN ↔ Database VLAN
Trust Boundary 5: Any VLAN ↔ Management VLAN
Trust Boundary 6: VPC-A ↔ VPC-B ↔ VPC-C ↔ VPC-D
Trust Boundary 7: Kubernetes namespace ↔ namespace
Trust Boundary 8: Kubernetes pod ↔ Kubernetes API server
Trust Boundary 9: Frontend ↔ Backend API
Trust Boundary 10: Backend ↔ Database
Trust Boundary 11: Private Datacenter ↔ AWS Cloud
```

---

## 4. STRIDE Analysis

### 4.1 Spoofing

| Threat ID | Threat | Target | Trust Boundary |
|---|---|---|---|
| S-01 | Attacker impersonates faculty user | IAM / Authentication | TB-9 |
| S-02 | Compromised pod uses another pod's service account | Kubernetes API | TB-8 |
| S-03 | VLAN hopping via trunk port misconfiguration | Private DC switch | TB-3 |
| S-04 | Spoofed source IP in cross-VPC request | AWS VPC routing | TB-6 |

**Mitigations:**

| Threat | Mitigation | Implementation |
|---|---|---|
| S-01 | Multi-factor authentication; session tokens with expiry | IAM layer + AegisMesh identity evaluation |
| S-02 | Unique service accounts per pod; RBAC bindings per namespace | Kubernetes RBAC + ServiceAccount isolation |
| S-03 | Disable DTP; configure access ports explicitly; enable port security | Packet Tracer switch configuration |
| S-04 | Security Groups do not allow source IP spoofing; VPC flow logs | AWS Security Groups + CloudTrail |

### 4.2 Tampering

| Threat ID | Threat | Target | Trust Boundary |
|---|---|---|---|
| T-01 | Modify security policy to allow unauthorized access | AegisMesh policy store | TB-10 |
| T-02 | Alter ACL on Cisco router | Private DC | TB-2 |
| T-03 | Modify Kubernetes NetworkPolicy to open cross-namespace access | K8s cluster | TB-7 |
| T-04 | Modify Security Group rules via compromised IAM credentials | AWS VPC | TB-6 |

**Mitigations:**

| Threat | Mitigation | Implementation |
|---|---|---|
| T-01 | Policy changes require authenticated admin; all changes audited | AegisMesh RBAC + audit logging (FR-10) |
| T-02 | Management VLAN (30) isolated; SSH access restricted | VLAN ACLs + management isolation |
| T-03 | RBAC denies NetworkPolicy modification to non-admin roles | Kubernetes ClusterRole restrictions |
| T-04 | IAM least privilege; MFA on admin roles; CloudTrail alerts | AWS IAM policies + CloudWatch alarms |

### 4.3 Repudiation

| Threat ID | Threat | Target | Trust Boundary |
|---|---|---|---|
| R-01 | User denies performing security-relevant action | All layers | All |
| R-02 | Attacker deletes logs to cover tracks | Logging infrastructure | TB-5 |

**Mitigations:**

| Threat | Mitigation | Implementation |
|---|---|---|
| R-01 | Immutable audit logs with actor identity, timestamp, action | AegisMesh audit_logs table (FR-10) |
| R-02 | Centralized logging to Security VLAN (50); separate log storage | Wazuh + dedicated logging VLAN |

### 4.4 Information Disclosure

| Threat ID | Threat | Target | Trust Boundary |
|---|---|---|---|
| I-01 | Compromised education app reads finance database | Cross-domain data | TB-6, TB-7 |
| I-02 | Database credentials exposed in source code or environment | Database | TB-10 |
| I-03 | Kubernetes secrets accessible from unauthorized namespace | K8s secrets | TB-7 |
| I-04 | Unencrypted traffic between private DC and AWS | VPN tunnel | TB-11 |

**Mitigations:**

| Threat | Mitigation | Implementation |
|---|---|---|
| I-01 | NetworkPolicies + Security Groups + AegisMesh policy: BLOCK | SR-02, SR-03, FR-01 |
| I-02 | Environment variables; secret management; never in source | NFR-01, C-06 |
| I-03 | Secrets scoped to namespace; RBAC restricts cross-namespace reads | Kubernetes RBAC |
| I-04 | VPN with encryption (simulated in architecture) | VPN configuration |

### 4.5 Denial of Service

| Threat ID | Threat | Target | Trust Boundary |
|---|---|---|---|
| D-01 | Flood AegisMesh API to prevent policy evaluation | AegisMesh backend | TB-9 |
| D-02 | Resource exhaustion in Kubernetes namespace | K8s cluster | TB-7 |
| D-03 | SYN flood on DMZ services | Private DC DMZ | TB-1 |

**Mitigations:**

| Threat | Mitigation | Implementation |
|---|---|---|
| D-01 | Rate limiting; fail-closed default (DENY if unreachable) | NFR-07 |
| D-02 | Resource Quotas and LimitRanges per namespace | Kubernetes resource controls |
| D-03 | ACL rate limiting on router; DMZ firewall rules | Packet Tracer ACLs |

### 4.6 Elevation of Privilege

| Threat ID | Threat | Target | Trust Boundary |
|---|---|---|---|
| E-01 | Container escape to host | K8s node | TB-8 |
| E-02 | Lateral movement from compromised app to management VLAN | Private DC | TB-5 |
| E-03 | Compromised education workload accesses finance VPC | AWS cloud | TB-6 |
| E-04 | Faculty user accesses database directly | Private DC | TB-4 |

**Mitigations:**

| Threat | Mitigation | Implementation |
|---|---|---|
| E-01 | Pod Security Standards (restricted); no privileged containers | Kubernetes pod security |
| E-02 | ACLs block VLAN 20→30; AegisMesh detects and contains | SR-01 + FR-05 |
| E-03 | No VPC peering between Education and Finance; SG DENY | SR-02 |
| E-04 | ACL blocks VLAN 10→40; AegisMesh policy: BLOCK | SR-01 + FR-01 |

---

## 5. Primary Attack Scenario: Lateral Movement

This is the **core threat** the project must defend against.

### Attack Tree

```
Goal: Access Finance Database from Compromised Education API
│
├── Path 1: Direct network access
│   ├── Attempt cross-namespace K8s traffic
│   │   └── BLOCKED by NetworkPolicy (SR-03)
│   ├── Attempt cross-VPC traffic
│   │   └── BLOCKED by Security Group + no VPC peering (SR-02)
│   └── Attempt private DC access
│       └── BLOCKED by ACL (SR-01)
│
├── Path 2: Abuse Kubernetes API
│   ├── List pods in finance namespace
│   │   └── BLOCKED by RBAC (SR-03)
│   ├── Read finance secrets
│   │   └── BLOCKED by RBAC (SR-03)
│   └── Create pod in finance namespace
│       └── BLOCKED by RBAC (SR-03)
│
├── Path 3: Abuse AWS IAM
│   ├── Assume role for finance VPC
│   │   └── BLOCKED by IAM policy (SR-02)
│   └── Modify Security Group
│       └── BLOCKED by IAM policy (SR-02)
│
└── Path 4: Application-level exploit
    ├── API call to finance service
    │   └── BLOCKED by AegisMesh policy (FR-01)
    └── DNS resolution of finance endpoints
        └── BLOCKED by NetworkPolicy egress rules (SR-03)
```

### Detection and Response

```
1. Education API sends anomalous request → finance-db
2. AegisMesh detection module observes anomaly (FR-07)
3. Risk engine scores: 85 (CRITICAL) (FR-03)
4. Policy engine evaluates: education-api → finance-db = BLOCK (FR-01)
5. Containment controller activates (FR-05):
   a. Workload state: NORMAL → SUSPICIOUS → CONTAINED
   b. NetworkPolicy updated: deny all egress except education-db
   c. Security Group updated: restrict education-api instance
6. Incident created with full timeline (FR-06)
7. Dashboard displays incident in real-time (FR-09)
```

---

## 6. Security Controls Summary

| Layer | Control | Purpose |
|---|---|---|
| **Network (Private DC)** | VLANs + ACLs | Zone-based segmentation |
| **Network (AWS)** | VPC isolation + Security Groups + NACLs | Cloud network segmentation |
| **Network (K8s)** | NetworkPolicies | Pod-level network segmentation |
| **Identity** | IAM + RBAC + Service Accounts | Authentication and authorization |
| **Application** | AegisMesh Policy Engine | Centralized policy evaluation |
| **Risk** | AegisMesh Risk Engine | Contextual risk assessment |
| **Containment** | AegisMesh Blast-Radius Controller | Automated compromise response |
| **Detection** | Wazuh + AegisMesh Detection | Security event monitoring |
| **Audit** | CloudTrail + Audit Logs + Wazuh | Non-repudiation and forensics |
| **Visualization** | Next.js Dashboard | Operational awareness |

---

## 7. Residual Risks

| Risk | Description | Accepted Because |
|---|---|---|
| Packet Tracer fidelity | PT does not perfectly replicate production Cisco hardware | Simulation environment; architecture principles remain valid |
| Local K8s limitations | kind/Minikube may not support all production CNI features | Calico CNI provides real NetworkPolicy enforcement |
| Single-region AWS | No multi-region disaster recovery | Development scope limitation |
| Deterministic risk scoring | Rule-based scoring may miss novel attack patterns | Appropriate for project scope; ML not claimed |
