# AegisMesh — Requirements Specification

**Project:** AegisMesh — Secure Hybrid Datacenter and Cloud Security Architecture  
**Version:** 1.0  
**Date:** 2026-08-28  
**Status:** DRAFT — Awaiting Approval  

---

## 1. Problem Statement

An enterprise operates a **hybrid infrastructure** spanning a private datacenter and public cloud (AWS). Workloads are deployed as traditional server applications and Kubernetes-orchestrated microservices. Faculty, developers, and platform engineers access resources from campus and remote locations.

**Primary Security Objective:**

> If one application or workload is compromised, the compromise must not be able to spread laterally to unauthorized applications, VPCs, Kubernetes workloads, or the private enterprise network.

AegisMesh is the **security control and decision layer** that enforces this objective across all infrastructure domains.

---

## 2. Stakeholders

| Stakeholder | Role | Security Concern |
|---|---|---|
| Faculty | End users accessing applications from campus or remotely | Secure, uninterrupted access to authorized services |
| Developers | Build and deploy applications across cloud and Kubernetes | Least-privilege access; cannot reach production databases directly |
| Network Engineers | Manage private datacenter networking (Cisco infrastructure) | Segmented VLANs; ACL enforcement; no unauthorized inter-zone traffic |
| Kubernetes/Platform Engineers | Manage Kubernetes clusters, namespaces, workloads | RBAC enforcement; namespace isolation; NetworkPolicy compliance |
| Security Operations | Monitor, detect, respond to security incidents | Real-time visibility; containment capability; audit trail |

---

## 3. Functional Requirements

### FR-01: Security Policy Evaluation

The system shall accept security access requests and evaluate them against configured policies to produce a decision: **ALLOW**, **RESTRICT**, **BLOCK**, or **ISOLATE**.

### FR-02: Policy Management

The system shall support CRUD operations for security policies that define source, destination, action, and permitted result.

### FR-03: Risk Assessment

The system shall compute a normalized risk score (0–100) for each access request using deterministic, explainable rules based on identity, workload trust, destination sensitivity, requested action, network zone, and prior security events.

### FR-04: Workload Identity Management

The system shall maintain a registry of workloads with associated trust levels, network zones, dependencies, and security classifications.

### FR-05: Blast-Radius Containment

Upon detecting a suspicious or compromised workload, the system shall:
1. Create an incident record.
2. Identify the workload's authorized dependencies.
3. Apply containment rules (block unauthorized lateral movement).
4. Preserve required functionality where the policy allows.
5. Transition the workload through states: `NORMAL → SUSPICIOUS → CONTAINED → RECOVERED`.

### FR-06: Incident Management

The system shall create, track, and resolve security incidents with full audit trails including timestamps, affected workloads, actions taken, and outcomes.

### FR-07: Security Event Collection

The system shall ingest security events from application logs, Kubernetes audit logs, authentication systems, and cloud infrastructure logs.

### FR-08: Network Topology Visualization

The system shall provide an interactive visualization of the security topology showing users, IAM, AegisMesh, VPCs, Kubernetes namespaces, applications, and the private datacenter with real-time status indicators.

### FR-09: Security Dashboard

The system shall present a unified dashboard showing: protected workloads count, active incidents, blocked requests, risk distribution, isolated workloads, VPC status, Kubernetes namespace status, and recent security events.

### FR-10: Audit Logging

Every security-relevant action (policy evaluation, risk assessment, containment action, configuration change) shall be logged with actor identity, timestamp, action, target, and outcome.

---

## 4. Non-Functional Requirements

### NFR-01: Security

- All API endpoints shall require authentication.
- Authorization shall enforce least privilege.
- No secrets shall be stored in source code.
- All security decisions shall be enforced server-side.

### NFR-02: Scalability

- The policy engine shall evaluate requests with sub-second latency for up to 1,000 concurrent policy evaluations.
- The architecture shall support horizontal scaling of the backend.

### NFR-03: Maintainability

- Modules shall be loosely coupled with clear interface boundaries.
- Code shall follow consistent naming conventions and include documentation for complex security logic.

### NFR-04: Testability

- Every security boundary shall be testable in both directions: authorized traffic succeeds AND unauthorized traffic fails.
- Unit tests shall cover policy evaluation, risk scoring, and containment logic.
- Integration tests shall verify end-to-end security workflows.

### NFR-05: Explainability

- Every security decision shall include a human-readable explanation of why it was made.
- Risk scores shall decompose into contributing factors with individual weights.

### NFR-06: Auditability

- All state transitions, policy changes, and security actions shall produce immutable audit records.

### NFR-07: Availability

- The system shall degrade gracefully: if AegisMesh is unreachable, the default posture shall be DENY (fail-closed).

---

## 5. Security Requirements

### SR-01: Network Segmentation (Private Datacenter)

The private datacenter shall enforce VLAN-based segmentation:

| VLAN | Zone | Purpose |
|---|---|---|
| VLAN 10 | Faculty | End-user access |
| VLAN 20 | Application Servers | Application workloads |
| VLAN 30 | Management | Infrastructure management |
| VLAN 40 | Database | Data storage |
| VLAN 50 | Security/Logging | SIEM, log collection |
| VLAN 60 | DMZ | Internet-facing services |

**Inter-VLAN access control:**

| Source | Destination | Expected |
|---|---|---|
| Faculty (VLAN 10) | Application (VLAN 20) | ALLOW |
| Faculty (VLAN 10) | Database (VLAN 40) | BLOCK |
| Faculty (VLAN 10) | Management (VLAN 30) | BLOCK |
| Application (VLAN 20) | Database (VLAN 40) | ALLOW |
| Application (VLAN 20) | Management (VLAN 30) | BLOCK |
| DMZ (VLAN 60) | Database (VLAN 40) | BLOCK |
| DMZ (VLAN 60) | Management (VLAN 30) | BLOCK |

### SR-02: Cloud Segmentation (AWS)

VPCs shall be isolated by security domain:

| VPC | Domain | Purpose |
|---|---|---|
| VPC-A | Education | Student/faculty learning services |
| VPC-B | Research | Research computing and data |
| VPC-C | Finance | Financial systems and records |
| VPC-D | Security/Management | Security tooling, monitoring, management |

**Default inter-VPC policy: DENY ALL.** Only explicitly authorized flows shall be permitted.

### SR-03: Kubernetes Workload Isolation

Namespaces (`education`, `research`, `finance`) shall be isolated by default using NetworkPolicies. Cross-namespace communication shall be denied unless an explicit policy exists.

### SR-04: Zero-Trust Principles

- No implicit trust based on network location.
- Every access request shall be explicitly authorized.
- Least-privilege access shall be enforced at every layer.

### SR-05: Lateral Movement Prevention

The architecture shall prevent a compromised workload in one domain from accessing resources in another domain. This shall be enforced at the network layer (ACLs, Security Groups, NetworkPolicies) AND the application layer (AegisMesh policy engine).

---

## 6. Constraints

| Constraint | Description |
|---|---|
| C-01 | Packet Tracer is used for private datacenter modeling only; it does not represent the entire project |
| C-02 | AWS infrastructure is defined via Terraform (infrastructure-as-code) |
| C-03 | Kubernetes uses local clusters (kind or Minikube) for development |
| C-04 | No Cisco-provided topology file exists; we design our own |
| C-05 | Demo data must be clearly labeled as SIMULATION / DEMONSTRATION DATA |
| C-06 | No ML/AI claims without validated models and datasets |
| C-07 | All implementation must be original work |

---

## 7. Acceptance Criteria

### AC-01: Segmentation Proof

For every security boundary, demonstrate:
1. Authorized traffic succeeds.
2. Unauthorized traffic is blocked.

### AC-02: Blast-Radius Containment Proof

Demonstrate that a compromised workload:
1. Cannot access unauthorized databases.
2. Cannot access other VPCs.
3. Cannot access the private enterprise network.
4. Continues to serve its authorized function (where policy allows).

### AC-03: End-to-End Story

Demonstrate the complete lifecycle:
```
NORMAL STATE → COMPROMISE → DETECTION → RISK EVALUATION → POLICY DECISION → CONTAINMENT → INCIDENT VISIBILITY
```

### AC-04: Dashboard Visibility

All security state changes, incidents, and containment actions shall be visible on the dashboard within 5 seconds of occurrence.

---

## 8. Traceability

Every design decision and implementation artifact shall trace back to a requirement in this document using the identifiers above (FR-XX, NFR-XX, SR-XX, C-XX, AC-XX).
