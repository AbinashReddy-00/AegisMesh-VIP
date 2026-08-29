# AegisMesh — Technology Stack

**Version:** 1.0  
**Date:** 2026-08-28  
**Status:** DRAFT — Awaiting Approval  

---

## 1. Technology Selection Criteria

Every technology in this stack was selected based on:

1. **Does it solve a Cisco requirement?** — Each technology maps to a specific project requirement.
2. **Is it the simplest adequate choice?** — No technology is added for popularity alone.
3. **Is it production-grade?** — Tools must be suitable for enterprise security contexts.
4. **Is it well-documented?** — Judges and reviewers must be able to verify our choices.

---

## 2. Complete Technology Stack

### 2.1 Infrastructure Layer

| Technology | Version | Purpose | Traces to | Justification |
|---|---|---|---|---|
| **Cisco Packet Tracer** | 8.2+ | Private datacenter network simulation | SR-01 | Industry-standard Cisco network modeling tool; required for Cisco internship context |
| **AWS** | Current | Public cloud infrastructure | SR-02 | Dominant public cloud with real VPC/SG/IAM primitives |
| **Terraform** | 1.6+ | Infrastructure-as-code for AWS | SR-02 | Declarative, reproducible, auditable IaC; industry standard |
| **kind** | 0.20+ | Local Kubernetes cluster | SR-03 | Lightweight multi-node K8s cluster; runs in Docker |
| **Calico** | 3.27+ | Kubernetes CNI with NetworkPolicy enforcement | SR-03 | Real NetworkPolicy enforcement (kind's default CNI has limited support) |

### 2.2 Backend Layer

| Technology | Version | Purpose | Traces to | Justification |
|---|---|---|---|---|
| **Python** | 3.12+ | Backend programming language | FR-01 | Excellent for security tooling; rich ecosystem; readable |
| **FastAPI** | 0.110+ | REST API framework | FR-01, FR-02 | High-performance async; automatic OpenAPI docs; Pydantic validation |
| **Pydantic** | 2.0+ | Data validation and serialization | NFR-01 | Type-safe request/response models; automatic validation |
| **SQLAlchemy** | 2.0+ | ORM for database access | FR-10 | Mature, production-grade ORM; async support |
| **Alembic** | 1.13+ | Database migrations | FR-10 | Companion to SQLAlchemy; versioned, reversible migrations |
| **PostgreSQL** | 16+ | Primary database | FR-10 | ACID-compliant; JSONB support for flexible schemas; production-grade |
| **Uvicorn** | 0.27+ | ASGI server | NFR-02 | High-performance async server for FastAPI |
| **python-jose** | 3.3+ | JWT token handling | NFR-01 | Standard JWT library for Python |
| **passlib** | 1.7+ | Password hashing | NFR-01 | Secure password hashing with bcrypt |
| **structlog** | 24.0+ | Structured logging | FR-10 | JSON-formatted, structured log output |

### 2.3 Frontend Layer

| Technology | Version | Purpose | Traces to | Justification |
|---|---|---|---|---|
| **Next.js** | 14+ | React framework | FR-08, FR-09 | App Router; SSR; production-grade React framework |
| **TypeScript** | 5.0+ | Type-safe JavaScript | NFR-03 | Type safety for complex dashboard state |
| **Tailwind CSS** | 3.4+ | Utility-first CSS framework | FR-09 | Rapid UI development; consistent design system (user-specified) |
| **shadcn/ui** | Latest | UI component library | FR-09 | High-quality, accessible components; Tailwind-based (user-specified) |
| **React Flow** | 11+ | Interactive node-graph visualization | FR-08 | Purpose-built for topology diagrams with interactive nodes/edges |
| **Recharts** | 2.10+ | React charting library | FR-09 | Declarative charts; clean API; React-native |
| **Axios** / **fetch** | — | HTTP client | FR-09 | API communication with the backend |

### 2.4 Monitoring Layer

| Technology | Version | Purpose | Traces to | Justification |
|---|---|---|---|---|
| **Wazuh** | 4.7+ | SIEM / Security monitoring | FR-07 | Open-source; agent-based collection; real security event correlation |
| **Docker** (Wazuh) | — | Wazuh deployment container | FR-07 | Simplified deployment for development |

### 2.5 Development and Testing

| Technology | Version | Purpose | Justification |
|---|---|---|---|
| **Docker** | 24+ | Container runtime | Standard containerization for all services |
| **Docker Compose** | 2.20+ | Multi-container orchestration | Development environment orchestration |
| **pytest** | 8.0+ | Python test framework | Standard Python testing; rich plugin ecosystem |
| **pytest-asyncio** | 0.23+ | Async test support | Required for testing FastAPI async endpoints |
| **pytest-cov** | 4.0+ | Coverage reporting | Code coverage metrics |
| **httpx** | 0.27+ | Async HTTP test client | Test client for FastAPI (replaces requests for async) |
| **Git** | — | Version control | Standard |
| **GitHub** | — | Repository hosting | Standard |

---

## 3. Architecture Diagram with Technologies

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER LAYER                               │
│                                                                   │
│  Faculty / Developers / Network Engineers / Platform Engineers    │
│                                                                   │
│  Browser → Next.js Dashboard (TypeScript, Tailwind, shadcn/ui)   │
│            React Flow (topology) + Recharts (metrics)            │
└────────────────────────────┬──────────────────────────────────────┘
                             │ HTTPS (REST API)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                            │
│                                                                   │
│  FastAPI (Python 3.12)                                           │
│  ├── Policy Engine                                               │
│  ├── Risk Engine                                                 │
│  ├── Decision Engine                                             │
│  ├── Containment Controller                                      │
│  ├── Detection Module                                            │
│  └── Workload Identity Registry                                  │
│                                                                   │
│  Pydantic (validation) + SQLAlchemy (ORM) + structlog (logging) │
│  PostgreSQL 16 (database) + Alembic (migrations)                │
└────────┬──────────────────┬──────────────────┬──────────────────┘
         │                  │                  │
         ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  PRIVATE DC  │   │  AWS CLOUD   │   │  KUBERNETES  │
│              │   │              │   │              │
│ Cisco PT     │   │ Terraform    │   │ kind         │
│ VLANs/ACLs   │   │ VPC/SG/IAM   │   │ Calico CNI   │
│ L3 Switch    │   │ CloudTrail   │   │ NetworkPolicy│
│ Router       │   │ CloudWatch   │   │ RBAC         │
└──────────────┘   └──────────────┘   └──────────────┘
         │                  │                  │
         └──────────────────┼──────────────────┘
                            │
                            ▼
                   ┌──────────────┐
                   │  MONITORING  │
                   │              │
                   │  Wazuh 4.7+  │
                   │  (Docker)    │
                   └──────────────┘
```

---

## 4. Dependency Management

### 4.1 Backend Dependencies

```
# requirements.txt (core)
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
sqlalchemy[asyncio]>=2.0.0
asyncpg>=0.29.0
alembic>=1.13.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.0
structlog>=24.0.0
httpx>=0.27.0
python-dotenv>=1.0.0
```

```
# requirements-dev.txt
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=4.0.0
httpx>=0.27.0
factory-boy>=3.3.0
```

### 4.2 Frontend Dependencies

```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "reactflow": "^11.0.0",
    "recharts": "^2.10.0",
    "axios": "^1.6.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "@types/react": "^18.0.0",
    "@types/node": "^20.0.0"
  }
}
```

### 4.3 Infrastructure Dependencies

```
# Terraform providers
hashicorp/aws ~> 5.0
```

---

## 5. Development Environment Setup

### 5.1 Prerequisites

| Tool | Purpose | Installation |
|---|---|---|
| Python 3.12+ | Backend runtime | python.org or pyenv |
| Node.js 20+ | Frontend runtime | nodejs.org or nvm |
| Docker Desktop | Containerization | docker.com |
| kind | Local Kubernetes | `go install sigs.k8s.io/kind@latest` or binary |
| kubectl | Kubernetes CLI | kubernetes.io |
| Terraform | AWS IaC | terraform.io |
| Cisco Packet Tracer | Network simulation | Cisco NetAcad |
| Git | Version control | git-scm.com |
| AWS CLI | AWS management | aws.amazon.com/cli |

### 5.2 Quick Start

```bash
# 1. Clone repository
git clone <repo-url>
cd AegisMesh

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
# Edit .env with your settings

# 3. Start database
docker-compose up -d db

# 4. Run migrations
alembic upgrade head

# 5. Seed demo data
python -m app.database.seed

# 6. Start backend
uvicorn app.main:app --reload --port 8000

# 7. Frontend setup (new terminal)
cd ../frontend
npm install
npm run dev

# 8. Kubernetes setup (new terminal)
kind create cluster --config kubernetes/cluster/kind-config.yaml
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.27.0/manifests/calico.yaml
kubectl apply -f kubernetes/namespaces/
kubectl apply -f kubernetes/network-policies/
```

---

## 6. Technologies NOT Used (and Why)

| Technology | Why NOT | What We Use Instead |
|---|---|---|
| Redis | Not needed for MVP; PostgreSQL handles our query patterns | PostgreSQL |
| Kafka / RabbitMQ | Event volume does not justify message broker complexity | Direct API calls + PostgreSQL |
| GraphQL | REST is simpler and sufficient for our API surface | FastAPI REST |
| MongoDB | ACID compliance needed for security audit data | PostgreSQL |
| Prometheus/Grafana | Wazuh provides security monitoring; Prometheus adds operational complexity | Wazuh + custom dashboard |
| Machine Learning | No validated ML model or dataset; would be dishonest to claim ML accuracy | Deterministic rule-based scoring |
| Ansible | Not managing real infrastructure; Terraform handles AWS; PT is manual | Terraform (for AWS) |
| Istio / Service Mesh | Over-engineering for a kind cluster; NetworkPolicies are sufficient | Calico NetworkPolicies |
