# AegisMesh

> **Secure Hybrid Datacenter and Cloud Security Architecture**  
> Cisco Virtual Internship 2026 — Cyber Security Project

---

## Overview

AegisMesh is a **security control and decision layer** that operates across a private enterprise datacenter, AWS public cloud, and Kubernetes container workloads. It evaluates access requests using identity, workload context, intent, and risk to produce security decisions: **ALLOW**, **RESTRICT**, **BLOCK**, or **ISOLATE**.

### Primary Security Objective

> If one application or workload is compromised, the compromise must not be able to spread laterally to unauthorized applications, VPCs, Kubernetes workloads, or the private enterprise network.

---

## Architecture

```
        USERS (Faculty / Developers / Engineers)
                       │
                       ▼
                Identity / IAM
                       │
                       ▼
              ┌─────────────────┐
              │   AEGISMESH     │
              │ Security Engine │
              └────────┬────────┘
                       │
            ┌──────────┼──────────┐
            ▼          ▼          ▼
     Private DC    AWS Cloud   Kubernetes
     (Cisco PT)   (4 VPCs)   (3 namespaces)
            │          │          │
            └──────────┼──────────┘
                       │
                  Monitoring
                  (Wazuh)
                       │
                  Dashboard
                  (Next.js)
```

---

## Project Structure

```
AegisMesh/
├── architecture/          # Architecture diagrams and design artifacts
├── packet-tracer/         # Cisco Packet Tracer topology and configs
├── infrastructure/        # AWS Terraform configurations
│   └── terraform/
├── kubernetes/            # Kubernetes manifests (RBAC, NetworkPolicies, etc.)
├── backend/               # AegisMesh FastAPI backend
│   ├── app/
│   └── tests/
├── frontend/              # Next.js security dashboard
├── monitoring/            # Wazuh / SIEM configuration
├── testing/               # Test scripts and results
└── docs/                  # Project documentation
    ├── requirements/
    ├── architecture/
    └── testing/
```

---

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Private DC | Cisco Packet Tracer | Enterprise network simulation |
| Cloud | AWS + Terraform | Public cloud infrastructure-as-code |
| Containers | Kubernetes (kind) + Calico | Workload orchestration and isolation |
| Backend | Python, FastAPI, PostgreSQL | Security policy engine, risk scoring, containment |
| Frontend | Next.js, TypeScript, Tailwind, React Flow | Security dashboard and topology visualization |
| Monitoring | Wazuh | Security event collection and alerting |

---

## Documentation

| Document | Description |
|---|---|
| [Requirements](docs/requirements/requirements.md) | Functional, non-functional, and security requirements |
| [Architecture](docs/architecture/architecture.md) | System architecture and component responsibilities |
| [Threat Model](docs/architecture/threat-model.md) | STRIDE analysis, attack trees, trust boundaries |
| [Network Design](docs/architecture/network-design.md) | Private datacenter VLAN and ACL design |
| [AWS Design](docs/architecture/aws-design.md) | AWS VPC, IAM, and Security Group architecture |
| [Kubernetes Design](docs/architecture/kubernetes-design.md) | Namespace isolation, RBAC, NetworkPolicies |
| [AegisMesh Design](docs/architecture/aegismesh-design.md) | Security engine module and API design |
| [Testing Strategy](docs/testing/testing-strategy.md) | Testing at every layer with bidirectional verification |
| [Technology Stack](docs/requirements/technology-stack.md) | Complete technology stack with justification |
| [Project Roadmap](docs/requirements/project-roadmap.md) | 19-phase development plan |

---

## Setup

*Setup instructions will be added as each component is implemented.*

---

## License

This project is developed for the Cisco Virtual Internship 2026 Cyber Security program.

---

## Status

**Current Phase:** 3 (Architecture Design) — Complete  
**Next Phase:** 4 (Packet Tracer Network) — Awaiting approval
