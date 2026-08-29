# AegisMesh — Security Engine Design

**Version:** 1.0  
**Date:** 2026-08-28  
**Status:** DRAFT — Awaiting Approval  
**Stack:** Python 3.12 + FastAPI + PostgreSQL  
**Traces to:** FR-01 through FR-10, NFR-01 through NFR-07  

---

## 1. Design Scope

This document specifies the AegisMesh Security Engine — the custom application component that provides centralized policy evaluation, risk assessment, workload identity management, and blast-radius containment orchestration across all infrastructure domains.

AegisMesh is the **brain** of the architecture. While VLANs, Security Groups, and NetworkPolicies enforce access at the infrastructure layer, AegisMesh provides the **decision intelligence** — evaluating context, identity, intent, and risk to produce security decisions.

---

## 2. Module Architecture

```
aegismesh/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration management
│   ├── dependencies.py            # Dependency injection
│   │
│   ├── api/                       # REST API layer
│   │   ├── __init__.py
│   │   ├── router.py              # API router aggregation
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── evaluate.py        # POST /api/v1/evaluate
│   │   │   ├── policies.py        # CRUD /api/v1/policies
│   │   │   ├── workloads.py       # CRUD /api/v1/workloads
│   │   │   ├── incidents.py       # /api/v1/incidents
│   │   │   ├── risk.py            # /api/v1/risk
│   │   │   ├── isolation.py       # POST /api/v1/isolate
│   │   │   ├── events.py          # /api/v1/events
│   │   │   ├── topology.py        # /api/v1/topology
│   │   │   └── health.py          # /api/v1/health
│   │   └── middleware/
│   │       ├── __init__.py
│   │       ├── auth.py            # Authentication middleware
│   │       └── logging.py         # Request/response logging
│   │
│   ├── policy_engine/             # Policy evaluation logic
│   │   ├── __init__.py
│   │   ├── engine.py              # Core policy evaluation
│   │   ├── matcher.py             # Policy rule matching
│   │   └── models.py              # Policy domain models
│   │
│   ├── risk_engine/               # Risk scoring logic
│   │   ├── __init__.py
│   │   ├── engine.py              # Risk score computation
│   │   ├── factors.py             # Risk factor definitions
│   │   ├── scorer.py              # Individual factor scorers
│   │   └── models.py              # Risk domain models
│   │
│   ├── decision_engine/           # Final decision logic
│   │   ├── __init__.py
│   │   ├── engine.py              # Decision combiner
│   │   └── models.py              # Decision domain models
│   │
│   ├── workload_identity/         # Workload registry
│   │   ├── __init__.py
│   │   ├── registry.py            # Workload CRUD
│   │   ├── trust.py               # Trust level management
│   │   └── models.py              # Workload domain models
│   │
│   ├── containment/               # Blast-radius controller
│   │   ├── __init__.py
│   │   ├── controller.py          # Containment orchestration
│   │   ├── strategies.py          # Containment strategies
│   │   ├── actions.py             # Concrete containment actions
│   │   └── models.py              # Containment domain models
│   │
│   ├── detection/                 # Security event processing
│   │   ├── __init__.py
│   │   ├── processor.py           # Event ingestion and correlation
│   │   ├── analyzers.py           # Anomaly detection rules
│   │   └── models.py              # Detection domain models
│   │
│   ├── models/                    # Shared data models (SQLAlchemy + Pydantic)
│   │   ├── __init__.py
│   │   ├── database.py            # SQLAlchemy ORM models
│   │   ├── schemas.py             # Pydantic request/response schemas
│   │   └── enums.py               # Shared enumerations
│   │
│   └── database/                  # Database layer
│       ├── __init__.py
│       ├── session.py             # Database session management
│       ├── migrations/            # Alembic migrations
│       │   ├── env.py
│       │   ├── alembic.ini
│       │   └── versions/
│       └── seed.py                # Demo data seeding (labeled as SIMULATION)
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Test fixtures
│   ├── test_policy_engine.py
│   ├── test_risk_engine.py
│   ├── test_decision_engine.py
│   ├── test_containment.py
│   ├── test_api_evaluate.py
│   ├── test_api_policies.py
│   ├── test_api_workloads.py
│   └── test_api_incidents.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

---

## 3. Security Request Evaluation Pipeline

### 3.1 Request Structure

```python
class EvaluateRequest(BaseModel):
    source: WorkloadIdentifier        # Who/what is requesting
    destination: ResourceIdentifier   # What is being accessed
    action: ActionType                # What action (READ, WRITE, EXECUTE, CONNECT)
    context: RequestContext           # Additional context
    
class WorkloadIdentifier(BaseModel):
    workload_id: str                  # e.g., "education-api"
    namespace: str | None             # Kubernetes namespace
    vpc_id: str | None                # AWS VPC
    vlan_id: int | None               # Private DC VLAN
    service_account: str | None       # K8s service account
    ip_address: str | None            # Source IP
    
class ResourceIdentifier(BaseModel):
    resource_id: str                  # e.g., "finance-db"
    resource_type: ResourceType       # DATABASE, API, SERVICE, STORAGE
    namespace: str | None
    vpc_id: str | None
    vlan_id: int | None
    sensitivity: SensitivityLevel     # PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED
    
class RequestContext(BaseModel):
    timestamp: datetime
    source_zone: SecurityZone         # FACULTY, APP, DATABASE, DMZ, CLOUD, K8S
    authentication_method: str | None
    session_id: str | None
    previous_actions: list[str]       # Recent action history
```

### 3.2 Evaluation Pipeline

```
┌──────────────────────────────────────────────────────────┐
│                  EVALUATION PIPELINE                      │
│                                                           │
│  1. IDENTITY EVALUATION                                   │
│     └─ Resolve source workload from registry              │
│     └─ Verify trust level                                 │
│     └─ Check authentication status                        │
│                                                           │
│  2. WORKLOAD EVALUATION                                   │
│     └─ Lookup destination resource                        │
│     └─ Verify resource exists and is active               │
│     └─ Determine resource sensitivity                     │
│                                                           │
│  3. CONTEXT EVALUATION                                    │
│     └─ Validate source zone                               │
│     └─ Check network path legitimacy                      │
│     └─ Evaluate time-of-day constraints                   │
│                                                           │
│  4. INTENT EVALUATION                                     │
│     └─ Classify requested action                          │
│     └─ Compare against workload's permitted actions       │
│     └─ Flag unusual action patterns                       │
│                                                           │
│  5. RISK EVALUATION (→ Risk Engine)                       │
│     └─ Compute normalized risk score (0–100)              │
│     └─ Decompose into contributing factors                │
│     └─ Return risk level (LOW/MEDIUM/HIGH/CRITICAL)       │
│                                                           │
│  6. POLICY EVALUATION (→ Policy Engine)                   │
│     └─ Match request against policy rules                 │
│     └─ Apply most specific matching rule                  │
│     └─ Return policy decision                             │
│                                                           │
│  7. DECISION (→ Decision Engine)                          │
│     └─ Combine risk score + policy result                 │
│     └─ Apply decision override rules                      │
│     └─ Produce final decision: ALLOW/RESTRICT/BLOCK/ISOLATE│
│     └─ Generate human-readable explanation                │
└──────────────────────────────────────────────────────────┘
```

### 3.3 Response Structure

```python
class EvaluateResponse(BaseModel):
    request_id: str                   # Unique evaluation ID
    decision: Decision                # ALLOW, RESTRICT, BLOCK, ISOLATE
    risk_score: int                   # 0–100
    risk_level: RiskLevel             # LOW, MEDIUM, HIGH, CRITICAL
    policy_matched: str | None        # ID of matched policy rule
    explanation: str                  # Human-readable decision explanation
    factors: list[RiskFactor]         # Contributing risk factors
    timestamp: datetime
    audit_id: str                     # Reference to audit log entry
```

---

## 4. Policy Engine Design

### 4.1 Policy Model

```python
class Policy(BaseModel):
    id: str
    name: str
    description: str
    priority: int                     # Lower number = higher priority
    enabled: bool
    rules: list[PolicyRule]
    
class PolicyRule(BaseModel):
    id: str
    source_selector: WorkloadSelector
    destination_selector: ResourceSelector
    actions: list[ActionType]         # What actions this rule covers
    decision: Decision                # ALLOW, RESTRICT, BLOCK
    conditions: list[Condition] | None  # Optional additional conditions
    
class WorkloadSelector(BaseModel):
    workload_ids: list[str] | None    # Specific workload IDs
    namespaces: list[str] | None      # Kubernetes namespaces
    vpc_ids: list[str] | None         # AWS VPCs
    vlan_ids: list[int] | None        # Private DC VLANs
    domains: list[str] | None         # Domain labels
    
class ResourceSelector(BaseModel):
    resource_ids: list[str] | None
    resource_types: list[ResourceType] | None
    sensitivity_levels: list[SensitivityLevel] | None
    namespaces: list[str] | None
    vpc_ids: list[str] | None
```

### 4.2 Policy Evaluation Order

1. Check for containment overrides (isolated workloads are always BLOCKED for unauthorized destinations).
2. Match request against rules in priority order (lowest number = highest priority).
3. First matching rule wins.
4. If no rule matches, apply **default deny** (BLOCK).

### 4.3 Example Policies

```json
{
  "name": "Education Domain Access",
  "priority": 10,
  "rules": [
    {
      "source_selector": {"domains": ["education"]},
      "destination_selector": {"resource_ids": ["education-db"]},
      "actions": ["READ", "WRITE"],
      "decision": "ALLOW"
    },
    {
      "source_selector": {"domains": ["education"]},
      "destination_selector": {"domains": ["finance"]},
      "actions": ["READ", "WRITE", "CONNECT"],
      "decision": "BLOCK"
    },
    {
      "source_selector": {"domains": ["education"]},
      "destination_selector": {"domains": ["research"]},
      "actions": ["READ", "WRITE", "CONNECT"],
      "decision": "BLOCK"
    }
  ]
}
```

---

## 5. Risk Engine Design

### 5.1 Risk Factors

| Factor | Weight | Range | Description |
|---|---|---|---|
| Source Trust | 20% | 0–100 | Trust level of the requesting workload |
| Destination Sensitivity | 25% | 0–100 | Sensitivity classification of target resource |
| Action Severity | 15% | 0–100 | How impactful the requested action is |
| Cross-Zone Penalty | 15% | 0–100 | Penalty for crossing security zone boundaries |
| Historical Anomaly | 15% | 0–100 | Whether this pattern is anomalous for the source |
| Time Context | 10% | 0–100 | Time-of-day risk modifier |

### 5.2 Risk Score Computation

```python
def compute_risk_score(request: EvaluateRequest) -> RiskAssessment:
    factors = []
    
    # Factor 1: Source Trust
    source_trust = get_workload_trust(request.source)
    trust_score = 100 - source_trust  # Lower trust = higher risk
    factors.append(RiskFactor("source_trust", trust_score, 0.20))
    
    # Factor 2: Destination Sensitivity
    dest_sensitivity = get_resource_sensitivity(request.destination)
    factors.append(RiskFactor("destination_sensitivity", dest_sensitivity, 0.25))
    
    # Factor 3: Action Severity
    action_score = ACTION_SEVERITY_MAP[request.action]
    factors.append(RiskFactor("action_severity", action_score, 0.15))
    
    # Factor 4: Cross-Zone Penalty
    zone_penalty = compute_zone_penalty(request.source, request.destination)
    factors.append(RiskFactor("cross_zone_penalty", zone_penalty, 0.15))
    
    # Factor 5: Historical Anomaly
    anomaly_score = check_historical_anomaly(request.source, request.destination, request.action)
    factors.append(RiskFactor("historical_anomaly", anomaly_score, 0.15))
    
    # Factor 6: Time Context
    time_score = compute_time_risk(request.context.timestamp)
    factors.append(RiskFactor("time_context", time_score, 0.10))
    
    # Weighted sum
    total = sum(f.score * f.weight for f in factors)
    risk_score = int(min(100, max(0, total)))
    
    return RiskAssessment(
        score=risk_score,
        level=classify_risk_level(risk_score),
        factors=factors,
        explanation=generate_risk_explanation(factors)
    )
```

### 5.3 Risk Levels

| Score Range | Level | Implication |
|---|---|---|
| 0–30 | LOW | Normal operation; proceed with policy evaluation |
| 31–60 | MEDIUM | Elevated monitoring; proceed with policy evaluation |
| 61–80 | HIGH | Additional scrutiny; may downgrade ALLOW to RESTRICT |
| 81–100 | CRITICAL | Automatic escalation; may trigger ISOLATE regardless of policy |

### 5.4 Cross-Zone Penalty Matrix

| Source Zone ↓ / Dest Zone → | Same Domain | Different Domain | Management | Database (other) |
|---|---|---|---|---|
| Any | 0 | 60 | 80 | 90 |

---

## 6. Decision Engine Design

### 6.1 Decision Matrix

The decision engine combines the **policy result** and the **risk level** to produce a final decision:

| Policy Result | Risk: LOW | Risk: MEDIUM | Risk: HIGH | Risk: CRITICAL |
|---|---|---|---|---|
| **ALLOW** | ALLOW | ALLOW | RESTRICT | BLOCK |
| **RESTRICT** | RESTRICT | RESTRICT | BLOCK | ISOLATE |
| **BLOCK** | BLOCK | BLOCK | BLOCK | ISOLATE |

### 6.2 Decision Output

```python
class SecurityDecision(BaseModel):
    decision: Decision              # ALLOW, RESTRICT, BLOCK, ISOLATE
    policy_decision: Decision       # What the policy said
    risk_override: bool             # Whether risk engine overrode the policy
    explanation: str                # "Blocked because education-api attempted 
                                    #  cross-domain access to finance-db 
                                    #  (risk score: 87, CRITICAL)"
```

---

## 7. Blast-Radius Controller Design

### 7.1 Workload States

```
NORMAL ──→ SUSPICIOUS ──→ CONTAINED ──→ RECOVERED
  ↑             │              │            │
  └─────────────┘              │            │
  (cleared)                    └────────────┘
                               (remediated)
```

### 7.2 Containment Workflow

```python
class ContainmentWorkflow:
    def execute(self, workload_id: str, incident: Incident):
        # Step 1: Mark workload as SUSPICIOUS
        self.update_workload_state(workload_id, WorkloadState.SUSPICIOUS)
        
        # Step 2: Identify authorized dependencies
        authorized_deps = self.get_authorized_dependencies(workload_id)
        
        # Step 3: Identify all current connections
        current_connections = self.get_current_connections(workload_id)
        
        # Step 4: Determine unauthorized connections
        unauthorized = current_connections - authorized_deps
        
        # Step 5: Apply containment actions
        actions = []
        for conn in unauthorized:
            action = self.block_connection(workload_id, conn)
            actions.append(action)
        
        # Step 6: Mark workload as CONTAINED
        self.update_workload_state(workload_id, WorkloadState.CONTAINED)
        
        # Step 7: Record all actions
        self.record_containment(incident, actions)
        
        # Step 8: Notify dashboard
        self.emit_event(ContainmentEvent(
            incident_id=incident.id,
            workload_id=workload_id,
            actions_taken=actions,
            preserved_connections=list(authorized_deps),
            blocked_connections=list(unauthorized)
        ))
```

### 7.3 Containment Actions

| Action Type | Target | Mechanism |
|---|---|---|
| K8S_NETWORK_POLICY | Kubernetes pod | Create/update NetworkPolicy to deny egress |
| AWS_SECURITY_GROUP | AWS instance | Modify SG to remove unauthorized ingress/egress |
| POLICY_OVERRIDE | AegisMesh | Create high-priority BLOCK policy for workload |
| ALERT | Dashboard | Emit real-time incident notification |

### 7.4 Example Containment Scenario

**Trigger:** education-api sends anomalous request to finance-db

```
BEFORE CONTAINMENT:
  education-api → education-db      ALLOW
  education-api → education-frontend ALLOW (ingress)
  education-api → aegismesh          ALLOW

CONTAINMENT ACTIONS:
  1. Create NetworkPolicy: deny education-api egress to finance namespace
  2. Create policy override: BLOCK education-api → any non-education resource
  3. Preserve: education-api → education-db (authorized dependency)
  4. Create incident INC-2026-001

AFTER CONTAINMENT:
  education-api → education-db       ALLOW (preserved)
  education-api → aegismesh          ALLOW (monitoring)
  education-api → finance-db         BLOCK (contained)
  education-api → research-api       BLOCK (contained)
  education-api → private-dc         BLOCK (contained)
```

---

## 8. API Design

### 8.1 Endpoints

| Method | Path | Purpose | Auth Required |
|---|---|---|---|
| POST | `/api/v1/evaluate` | Evaluate a security access request | Yes |
| GET | `/api/v1/policies` | List all policies | Yes |
| POST | `/api/v1/policies` | Create a new policy | Yes (admin) |
| GET | `/api/v1/policies/{id}` | Get policy by ID | Yes |
| PUT | `/api/v1/policies/{id}` | Update a policy | Yes (admin) |
| DELETE | `/api/v1/policies/{id}` | Delete a policy | Yes (admin) |
| GET | `/api/v1/workloads` | List all registered workloads | Yes |
| POST | `/api/v1/workloads` | Register a workload | Yes (admin) |
| GET | `/api/v1/workloads/{id}` | Get workload by ID | Yes |
| PUT | `/api/v1/workloads/{id}` | Update workload | Yes (admin) |
| GET | `/api/v1/incidents` | List incidents | Yes |
| POST | `/api/v1/incidents` | Create an incident | Yes |
| GET | `/api/v1/incidents/{id}` | Get incident by ID | Yes |
| PUT | `/api/v1/incidents/{id}` | Update incident | Yes |
| GET | `/api/v1/risk` | Get current risk overview | Yes |
| POST | `/api/v1/isolate` | Trigger containment of a workload | Yes (admin) |
| GET | `/api/v1/events` | List security events | Yes |
| POST | `/api/v1/events` | Ingest a security event | Yes |
| GET | `/api/v1/topology` | Get network topology | Yes |
| GET | `/api/v1/health` | Health check (no auth) | No |

### 8.2 Authentication

- API key-based authentication for service-to-service calls.
- JWT token-based authentication for dashboard users.
- API key passed via `X-API-Key` header.
- JWT passed via `Authorization: Bearer <token>` header.

### 8.3 Error Handling

```python
class APIError(BaseModel):
    error: str
    message: str
    detail: str | None
    request_id: str
    timestamp: datetime
```

Standard HTTP status codes:
- `200` Success
- `201` Created
- `400` Bad Request (validation failure)
- `401` Unauthorized
- `403` Forbidden
- `404` Not Found
- `409` Conflict
- `422` Unprocessable Entity
- `500` Internal Server Error

---

## 9. Database Design

### 9.1 Entity-Relationship Overview

```
users ──< roles
workloads ──< workload_dependencies
policies ──< policy_rules
workloads ──< risk_assessments
workloads ──< incidents ──< isolation_actions
security_events ──< incidents
audit_logs (standalone)
```

### 9.2 Core Tables

#### `users`
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK |
| username | VARCHAR(100) | UNIQUE, NOT NULL |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| hashed_password | VARCHAR(255) | NOT NULL |
| role_id | UUID | FK → roles |
| is_active | BOOLEAN | DEFAULT true |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

#### `roles`
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK |
| name | VARCHAR(50) | UNIQUE, NOT NULL |
| permissions | JSONB | NOT NULL |

#### `workloads`
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK |
| workload_id | VARCHAR(100) | UNIQUE, NOT NULL |
| name | VARCHAR(200) | NOT NULL |
| domain | VARCHAR(50) | NOT NULL |
| namespace | VARCHAR(100) | |
| vpc_id | VARCHAR(100) | |
| vlan_id | INTEGER | |
| trust_level | INTEGER | NOT NULL (0–100) |
| sensitivity | VARCHAR(20) | NOT NULL |
| state | VARCHAR(20) | NOT NULL (NORMAL/SUSPICIOUS/CONTAINED/RECOVERED) |
| dependencies | JSONB | Authorized dependency list |
| metadata | JSONB | Additional workload metadata |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

#### `policies`
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK |
| name | VARCHAR(200) | NOT NULL |
| description | TEXT | |
| priority | INTEGER | NOT NULL |
| enabled | BOOLEAN | DEFAULT true |
| created_by | UUID | FK → users |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

#### `policy_rules`
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK |
| policy_id | UUID | FK → policies |
| source_selector | JSONB | NOT NULL |
| destination_selector | JSONB | NOT NULL |
| actions | JSONB | NOT NULL |
| decision | VARCHAR(20) | NOT NULL |
| conditions | JSONB | |

#### `risk_assessments`
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK |
| request_id | VARCHAR(100) | NOT NULL |
| source_workload_id | UUID | FK → workloads |
| destination_resource_id | VARCHAR(100) | NOT NULL |
| score | INTEGER | NOT NULL (0–100) |
| level | VARCHAR(20) | NOT NULL |
| factors | JSONB | NOT NULL |
| explanation | TEXT | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |

#### `incidents`
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK |
| incident_id | VARCHAR(100) | UNIQUE, NOT NULL |
| title | VARCHAR(300) | NOT NULL |
| description | TEXT | |
| severity | VARCHAR(20) | NOT NULL |
| status | VARCHAR(20) | NOT NULL (OPEN/INVESTIGATING/CONTAINED/RESOLVED) |
| affected_workload_id | UUID | FK → workloads |
| risk_assessment_id | UUID | FK → risk_assessments |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |
| resolved_at | TIMESTAMP | |

#### `isolation_actions`
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK |
| incident_id | UUID | FK → incidents |
| workload_id | UUID | FK → workloads |
| action_type | VARCHAR(50) | NOT NULL |
| target | VARCHAR(200) | NOT NULL |
| detail | JSONB | NOT NULL |
| executed_at | TIMESTAMP | NOT NULL |
| reverted_at | TIMESTAMP | |

#### `security_events`
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK |
| event_type | VARCHAR(50) | NOT NULL |
| source | VARCHAR(200) | NOT NULL |
| severity | VARCHAR(20) | NOT NULL |
| description | TEXT | NOT NULL |
| raw_data | JSONB | |
| workload_id | UUID | FK → workloads (nullable) |
| incident_id | UUID | FK → incidents (nullable) |
| created_at | TIMESTAMP | NOT NULL |

#### `audit_logs`
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK |
| actor | VARCHAR(200) | NOT NULL |
| action | VARCHAR(100) | NOT NULL |
| target | VARCHAR(200) | NOT NULL |
| outcome | VARCHAR(20) | NOT NULL |
| detail | JSONB | |
| ip_address | VARCHAR(45) | |
| created_at | TIMESTAMP | NOT NULL |

### 9.3 Migration Strategy

- Use **Alembic** for database migrations.
- Every schema change is a versioned migration.
- Migrations are reversible where possible.
- Seed data is clearly labeled as `SIMULATION / DEMONSTRATION DATA`.

---

## 10. Configuration Management

```python
# config.py
class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    API_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 60
    
    # Application
    APP_NAME: str = "AegisMesh"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Risk Engine
    RISK_HIGH_THRESHOLD: int = 61
    RISK_CRITICAL_THRESHOLD: int = 81
    
    # Containment
    AUTO_CONTAIN_THRESHOLD: int = 81
    
    model_config = SettingsConfigDict(env_file=".env")
```

`.env.example`:
```
DATABASE_URL=postgresql://aegismesh:changeme@localhost:5432/aegismesh
SECRET_KEY=changeme-generate-a-real-secret
API_KEY=changeme-generate-a-real-api-key
DEBUG=false
LOG_LEVEL=INFO
```

---

## 11. Logging Architecture

### 11.1 Structured Logging

All logs use structured JSON format:

```json
{
  "timestamp": "2026-08-28T12:00:00Z",
  "level": "INFO",
  "module": "policy_engine",
  "action": "evaluate",
  "request_id": "req-abc-123",
  "source": "education-api",
  "destination": "finance-db",
  "decision": "BLOCK",
  "risk_score": 87,
  "message": "Cross-domain access blocked: education → finance"
}
```

### 11.2 Security-Relevant Log Events

| Event | Level | Trigger |
|---|---|---|
| Policy evaluation | INFO | Every evaluation |
| Access blocked | WARNING | BLOCK decision |
| Containment triggered | CRITICAL | ISOLATE decision |
| Policy modified | WARNING | Admin action |
| Authentication failure | WARNING | Failed login |
| Risk threshold exceeded | WARNING | Score > 80 |
