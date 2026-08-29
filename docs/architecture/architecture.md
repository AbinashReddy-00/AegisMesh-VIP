# AegisMesh — System Architecture

**Version:** 1.0  
**Date:** 2026-08-28  
**Status:** DRAFT — Awaiting Approval  
**Traces to:** FR-01 through FR-10, NFR-01 through NFR-07, SR-01 through SR-05  

---

## 1. Architecture Overview

AegisMesh is a **security control and decision layer** that operates across three infrastructure domains:

1. **Private Datacenter** — Cisco-switched enterprise network with VLAN segmentation
2. **AWS Cloud** — Multi-VPC public cloud infrastructure with IAM and Security Groups
3. **Kubernetes** — Container-orchestrated microservices with namespace isolation

AegisMesh does **not** replace the native security controls in each domain (ACLs, Security Groups, NetworkPolicies). Instead, it provides a **unified policy evaluation, risk assessment, and containment orchestration layer** that coordinates security decisions across domains.

---

## 2. Architectural Principles

| Principle | Application |
|---|---|
| **Defense in Depth** | Security enforced at network, platform, and application layers independently |
| **Least Privilege** | Every access requires explicit authorization; default posture is DENY |
| **Zero Trust** | No implicit trust from network location; every request is evaluated |
| **Blast-Radius Reduction** | Compromise in one domain cannot propagate to others |
| **Fail Closed** | If AegisMesh is unreachable, default action is DENY |
| **Explainability** | Every decision includes human-readable justification |
| **Separation of Concerns** | Each component has one clearly defined responsibility |

---

## 3. High-Level Architecture

```
                        ┌─────────────────┐
                        │     USERS       │
                        │ Faculty / Devs  │
                        │ Net Engineers   │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   IDENTITY /    │
                        │     IAM         │
                        └────────┬────────┘
                                 │
                                 ▼
                ┌────────────────────────────────┐
                │          AEGISMESH             │
                │    Security Control Plane      │
                │                                │
                │  ┌──────────┐ ┌─────────────┐  │
                │  │ Policy   │ │    Risk      │  │
                │  │ Engine   │ │   Engine     │  │
                │  └──────────┘ └─────────────┘  │
                │  ┌──────────┐ ┌─────────────┐  │
                │  │Decision  │ │ Containment │  │
                │  │Engine    │ │ Controller  │  │
                │  └──────────┘ └─────────────┘  │
                │  ┌──────────┐ ┌─────────────┐  │
                │  │Workload  │ │  Detection  │  │
                │  │Identity  │ │   Module    │  │
                │  └──────────┘ └─────────────┘  │
                └───────────┬────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
    ┌──────────────┐ ┌────────────┐ ┌───────────┐
    │   PRIVATE    │ │   AWS      │ │KUBERNETES │
    │  DATACENTER  │ │   CLOUD    │ │  CLUSTER  │
    │              │ │            │ │           │
    │  VLANs       │ │  VPC-A     │ │education  │
    │  ACLs        │ │  VPC-B     │ │research   │
    │  Routing     │ │  VPC-C     │ │finance    │
    │  DMZ         │ │  VPC-D     │ │           │
    └──────────────┘ └────────────┘ └───────────┘
              │             │             │
              └─────────────┼─────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │   MONITORING    │
                   │  Wazuh / SIEM   │
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │   DASHBOARD     │
                   │   (Next.js)     │
                   └─────────────────┘
```

---

## 4. Component Responsibilities

### 4.1 AegisMesh Security Engine (Backend — FastAPI + PostgreSQL)

**Responsibility:** Centralized security policy evaluation, risk assessment, and containment orchestration.

| Sub-component | Responsibility | Traces to |
|---|---|---|
| **API Layer** | REST endpoints for policy evaluation, workload management, incident management | FR-01, FR-02, FR-06 |
| **Policy Engine** | Evaluates access requests against configured policies | FR-01, FR-02 |
| **Risk Engine** | Computes normalized risk score (0–100) from deterministic rules | FR-03 |
| **Decision Engine** | Combines policy result and risk score to produce final decision | FR-01 |
| **Workload Identity** | Manages workload registry with trust levels and classifications | FR-04 |
| **Containment Controller** | Orchestrates blast-radius containment workflow | FR-05 |
| **Detection Module** | Ingests and correlates security events to identify anomalies | FR-07 |
| **Database Layer** | PostgreSQL storage for policies, workloads, incidents, events, audit logs | FR-10 |

### 4.2 Private Datacenter (Cisco Packet Tracer)

**Responsibility:** Network-level segmentation and access control for the enterprise on-premises environment.

- VLAN segmentation (6 zones)
- Inter-VLAN routing with ACL enforcement
- DHCP services
- DMZ isolation
- Management network isolation

**Traces to:** SR-01

### 4.3 AWS Cloud (Terraform)

**Responsibility:** Public cloud infrastructure with VPC-level isolation and IAM access control.

- 4 VPCs (Education, Research, Finance, Security/Management)
- Subnet design (public/private per VPC)
- Security Groups (per-instance firewall)
- Network ACLs (subnet-level firewall)
- IAM roles and policies (least-privilege)
- CloudTrail (API audit logging)
- CloudWatch (metrics and alarms)

**Traces to:** SR-02

### 4.4 Kubernetes Cluster (kind/Minikube)

**Responsibility:** Container orchestration with namespace-level workload isolation.

- 3 namespaces (education, research, finance)
- RBAC (role-based access control)
- NetworkPolicies (pod-level network segmentation)
- Service Accounts (workload identity)
- Resource Quotas and Limits
- Pod Security Standards

**Traces to:** SR-03

### 4.5 Monitoring (Wazuh)

**Responsibility:** Security telemetry collection, correlation, and alerting.

- Agent-based log collection
- Security event correlation
- Alert generation
- Integration with AegisMesh detection module

**Traces to:** FR-07

### 4.6 Dashboard (Next.js)

**Responsibility:** Security visualization and operational interface.

- Real-time security status
- Interactive topology visualization (React Flow)
- Incident management UI
- Policy management UI
- Risk visualization (Recharts)
- Audit log viewer

**Traces to:** FR-08, FR-09

---

## 5. Security Request Evaluation Flow

```
                    ┌──────────────┐
                    │   REQUEST    │
                    │  (source,    │
                    │  destination,│
                    │  action)     │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  IDENTITY    │
                    │ EVALUATION   │
                    │ (who is the  │
                    │  requester?) │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  WORKLOAD    │
                    │ EVALUATION   │
                    │ (what is the │
                    │  workload?)  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   CONTEXT    │
                    │ EVALUATION   │
                    │ (from where? │
                    │  what zone?) │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   INTENT     │
                    │ EVALUATION   │
                    │ (what action │
                    │  requested?) │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    RISK      │
                    │ EVALUATION   │
                    │ (risk score  │
                    │   0–100)     │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   POLICY     │
                    │ EVALUATION   │
                    │ (match rules)│
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  DECISION    │
                    │              │
                    │ ALLOW        │
                    │ RESTRICT     │
                    │ BLOCK        │
                    │ ISOLATE      │
                    └──────────────┘
```

---

## 6. Data Flow

### 6.1 Normal Access Flow

```
Faculty → IAM Authentication → AegisMesh Evaluate → ALLOW → Application Server → Database
```

### 6.2 Unauthorized Access Attempt

```
Faculty → IAM Authentication → AegisMesh Evaluate → BLOCK → Access Denied → Audit Log
```

### 6.3 Compromised Workload Flow

```
Anomaly Detected → Detection Module → Risk Engine (score > 80) → Containment Controller
    → ISOLATE workload
    → Block lateral connections
    → Create Incident
    → Notify Dashboard
    → Preserve authorized dependencies
```

---

## 7. Integration Model

AegisMesh integrates with infrastructure domains through **observation and orchestration**, not by replacing native controls:

| Domain | Native Controls | AegisMesh Role |
|---|---|---|
| Private DC | VLANs, ACLs | Observes network zone; informs containment decisions |
| AWS | Security Groups, NACLs, IAM | Evaluates cloud access policies; triggers SG updates via API |
| Kubernetes | NetworkPolicies, RBAC | Evaluates namespace access; triggers NetworkPolicy changes |
| Monitoring | Wazuh alerts | Ingests alerts as security events for risk scoring |

---

## 8. Communication Architecture

### 8.1 Internal Communication

| From | To | Protocol | Purpose |
|---|---|---|---|
| Frontend | Backend API | HTTPS (REST) | Dashboard data, policy management |
| Backend | PostgreSQL | TCP/5432 (TLS) | Data persistence |
| Monitoring Agent | Wazuh Manager | TCP/1514 (TLS) | Security event forwarding |
| Wazuh Manager | Backend API | HTTPS (webhook) | Alert ingestion |

### 8.2 Cross-Domain Communication

| From | To | Mechanism | Security |
|---|---|---|---|
| Private DC | AWS | VPN / Direct Connect (simulated) | Encrypted tunnel |
| AWS VPCs | Inter-VPC | Transit Gateway or Peering (controlled) | Security Groups + NACLs |
| Kubernetes | Backend API | ClusterIP / NodePort | NetworkPolicy + RBAC |

---

## 9. Deployment Architecture

### Development Environment

```
Developer Machine
├── Packet Tracer (GUI) ─── Private DC simulation
├── Docker Compose
│   ├── aegismesh-backend (FastAPI)
│   ├── aegismesh-db (PostgreSQL)
│   ├── aegismesh-frontend (Next.js)
│   └── wazuh (optional)
├── kind / Minikube ─── Kubernetes cluster
└── Terraform (plan/apply) ─── AWS infrastructure
```

### Production Concept

```
                    ┌───────────────┐
                    │   CloudFront  │
                    └───────┬───────┘
                            │
                    ┌───────┴───────┐
                    │   Next.js     │
                    │  (Vercel/ECS) │
                    └───────┬───────┘
                            │
                    ┌───────┴───────┐
                    │   FastAPI     │
                    │  (ECS/EKS)   │
                    └───────┬───────┘
                            │
                    ┌───────┴───────┐
                    │  PostgreSQL   │
                    │    (RDS)      │
                    └───────────────┘
```

---

## 10. Technology Justification

| Technology | Why | What it replaces |
|---|---|---|
| **Cisco Packet Tracer** | Industry-standard network simulation; models enterprise DC as required by Cisco internship | Physical network lab |
| **AWS** | Dominant public cloud; real-world VPC/IAM/SG primitives | Generic "cloud" hand-waving |
| **Terraform** | Declarative IaC; reproducible; auditable | Manual AWS console configuration |
| **Kubernetes (kind)** | Production-grade container orchestration; real NetworkPolicies | Docker-only deployment |
| **FastAPI** | High-performance async Python; automatic OpenAPI docs; Pydantic validation | Flask/Django (heavier) |
| **PostgreSQL** | ACID-compliant; robust for security audit data; production-grade | SQLite (not production-ready) |
| **Next.js** | React-based; SSR; App Router; production-grade | Plain React SPA |
| **Wazuh** | Open-source SIEM; real agent-based collection | Custom log aggregation |
| **React Flow** | Purpose-built for interactive node-graph visualization | Static diagrams |
| **Recharts** | React-native charting; clean API | Heavy BI tools |

---

## 11. Assumptions

1. The private datacenter is **simulated** in Packet Tracer; there is no physical hardware.
2. AWS resources will be provisioned in a single region for cost control.
3. Kubernetes uses a local cluster (kind or Minikube) during development.
4. AegisMesh backend runs as a containerized application.
5. No Cisco-provided Packet Tracer topology exists; we design our own.
6. Demonstration data is clearly labeled as simulation data.
7. The project targets a **technical evaluation** audience (Cisco judges).

---

## 12. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| AWS costs exceed budget | Cannot demonstrate cloud component | Use free-tier resources; Terraform destroy after testing |
| Packet Tracer limitations | Cannot model all enterprise features | Document limitations; supplement with architecture diagrams |
| kind/Minikube networking differences from production K8s | NetworkPolicies may behave differently | Use Calico CNI for realistic NetworkPolicy support |
| Scope creep from monitoring integration | Delays core development | Implement monitoring as last infrastructure component |
| Single developer bandwidth | Cannot complete all 19 phases | Prioritize core security story (segmentation + containment) |
