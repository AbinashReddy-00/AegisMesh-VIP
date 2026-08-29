# AegisMesh — Kubernetes Security Design

**Version:** 1.0  
**Date:** 2026-08-28  
**Status:** DRAFT — Awaiting Approval  
**Platform:** kind (Kubernetes in Docker) with Calico CNI  
**Traces to:** SR-03, FR-01, FR-04, AC-01  

---

## 1. Design Scope

This document specifies the Kubernetes security architecture for AegisMesh. The Kubernetes cluster hosts modern cloud-native microservices organized by domain (education, research, finance) with strict namespace isolation, RBAC, and NetworkPolicies.

**Kubernetes is the container orchestration layer** of the hybrid architecture. It enforces workload isolation at the pod and namespace level, complementing the network-layer controls (ACLs) in the private datacenter and the VPC-level controls in AWS.

---

## 2. Cluster Architecture

### 2.1 Local Development Cluster

| Component | Choice | Justification |
|---|---|---|
| Distribution | kind (Kubernetes in Docker) | Lightweight; runs on developer machines; supports multiple nodes |
| CNI | Calico | Real NetworkPolicy enforcement (kind default CNI has limited NetworkPolicy support) |
| Nodes | 1 control-plane + 2 workers | Realistic multi-node scheduling |

### 2.2 kind Cluster Configuration

```yaml
# kind-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: aegismesh
networking:
  disableDefaultCNI: true   # We'll install Calico
  podSubnet: "192.168.0.0/16"
nodes:
  - role: control-plane
  - role: worker
  - role: worker
```

---

## 3. Namespace Design

### 3.1 Namespace Layout

| Namespace | Domain | Purpose | Security Level |
|---|---|---|---|
| `education` | Education | Learning management services | MEDIUM |
| `research` | Research | Research computing and data | MEDIUM |
| `finance` | Finance | Financial systems | HIGH |
| `aegismesh-system` | Security | AegisMesh backend + monitoring agents | HIGH |
| `monitoring` | Operations | Wazuh agent, logging sidecar | HIGH |

### 3.2 Namespace Labels

Each namespace carries labels used by NetworkPolicies for selector-based access control:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: education
  labels:
    domain: education
    security-level: medium
    aegismesh.io/managed: "true"
---
apiVersion: v1
kind: Namespace
metadata:
  name: research
  labels:
    domain: research
    security-level: medium
    aegismesh.io/managed: "true"
---
apiVersion: v1
kind: Namespace
metadata:
  name: finance
  labels:
    domain: finance
    security-level: high
    aegismesh.io/managed: "true"
```

---

## 4. Workload Design

### 4.1 Per-Namespace Workloads

Each domain namespace contains a standard 3-tier application:

```
Namespace: education
├── education-frontend    (Deployment, 2 replicas)
├── education-api         (Deployment, 2 replicas)
└── education-db          (StatefulSet, 1 replica, PostgreSQL)

Namespace: research
├── research-frontend     (Deployment, 2 replicas)
├── research-api          (Deployment, 2 replicas)
└── research-db           (StatefulSet, 1 replica, PostgreSQL)

Namespace: finance
├── finance-frontend      (Deployment, 2 replicas)
├── finance-api           (Deployment, 2 replicas)
└── finance-db            (StatefulSet, 1 replica, PostgreSQL)
```

### 4.2 Workload Labels

All pods carry consistent labels for NetworkPolicy and AegisMesh identification:

```yaml
labels:
  app: education-api
  tier: backend
  domain: education
  aegismesh.io/workload-id: "edu-api-001"
```

---

## 5. RBAC Design

### 5.1 Principle

Each namespace has its own ServiceAccount, Role, and RoleBinding. No ClusterRole grants are given to application workloads. Cross-namespace access to the Kubernetes API is denied.

### 5.2 ServiceAccounts

| ServiceAccount | Namespace | Purpose |
|---|---|---|
| education-api-sa | education | Education API pod identity |
| education-frontend-sa | education | Education frontend pod identity |
| education-db-sa | education | Education database pod identity |
| research-api-sa | research | Research API pod identity |
| research-frontend-sa | research | Research frontend pod identity |
| research-db-sa | research | Research database pod identity |
| finance-api-sa | finance | Finance API pod identity |
| finance-frontend-sa | finance | Finance frontend pod identity |
| finance-db-sa | finance | Finance database pod identity |
| aegismesh-sa | aegismesh-system | AegisMesh backend (broader read access) |

### 5.3 Role Definitions

#### Application Roles (per namespace)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: app-workload-role
  namespace: education
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get", "list"]
  - apiGroups: [""]
    resources: ["secrets"]
    resourceNames: ["education-db-credentials"]
    verbs: ["get"]
```

**Key restrictions:**
- Cannot list/create pods in other namespaces
- Cannot modify NetworkPolicies
- Cannot access secrets outside their own namespace
- Cannot create/modify RBAC resources

#### AegisMesh System Role (ClusterRole)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: aegismesh-controller
rules:
  - apiGroups: [""]
    resources: ["namespaces", "pods", "services"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["networking.k8s.io"]
    resources: ["networkpolicies"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
  - apiGroups: [""]
    resources: ["events"]
    verbs: ["get", "list", "watch"]
```

**AegisMesh needs:** read access to pods/namespaces + write access to NetworkPolicies (for containment).

### 5.4 Preventing Privilege Escalation

```yaml
# Deny default SA usage — force explicit SA binding
automountServiceAccountToken: false  # Set on pods that don't need API access
```

---

## 6. NetworkPolicy Design

### 6.1 Strategy: Default Deny + Explicit Allow

Every namespace starts with a **default deny** policy. Then, only explicitly required flows are permitted.

### 6.2 Default Deny (All Namespaces)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: education  # Applied to each namespace
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

### 6.3 Education Namespace Policies

#### Allow: frontend → api (within namespace)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-api
  namespace: education
spec:
  podSelector:
    matchLabels:
      app: education-api
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: education-frontend
      ports:
        - port: 8080
          protocol: TCP
```

#### Allow: api → db (within namespace)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-api-to-db
  namespace: education
spec:
  podSelector:
    matchLabels:
      app: education-db
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: education-api
      ports:
        - port: 5432
          protocol: TCP
```

#### Allow: DNS resolution (all pods)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: education
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress:
    - to: []
      ports:
        - port: 53
          protocol: UDP
        - port: 53
          protocol: TCP
```

#### Allow: api → AegisMesh (cross-namespace, for policy evaluation)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-api-to-aegismesh
  namespace: education
spec:
  podSelector:
    matchLabels:
      app: education-api
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              domain: security
        - podSelector:
            matchLabels:
              app: aegismesh-backend
      ports:
        - port: 8000
          protocol: TCP
```

### 6.4 Cross-Namespace Denial (Implicit)

Because of the default-deny policy, no cross-namespace traffic is allowed unless an explicit NetworkPolicy exists. This means:

| Source | Destination | Result | Reason |
|---|---|---|---|
| education-api | education-db | ✅ ALLOW | Explicit ingress policy on education-db |
| education-api | research-api | ❌ BLOCK | No egress policy to research namespace |
| education-api | finance-db | ❌ BLOCK | No egress policy to finance namespace |
| education-api | kube-system | ❌ BLOCK | No egress policy (except DNS) |

---

## 7. Secrets Management

### 7.1 Kubernetes Secrets

Database credentials and API keys are stored as Kubernetes Secrets, scoped to their namespace:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: education-db-credentials
  namespace: education
type: Opaque
data:
  POSTGRES_USER: <base64>
  POSTGRES_PASSWORD: <base64>
  POSTGRES_DB: <base64>
```

### 7.2 Secret Access Control

- Secrets are accessible only via RBAC (RoleBindings scoped to the namespace).
- Application pods mount only their own namespace's secrets.
- `automountServiceAccountToken: false` on pods that don't need API access.

### 7.3 Secret Rotation

For production: use external secret managers (AWS Secrets Manager, HashiCorp Vault).  
For development: Kubernetes Secrets with documented rotation procedure.

---

## 8. Pod Security

### 8.1 Pod Security Standards

Apply `restricted` Pod Security Standard to all application namespaces:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: education
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### 8.2 Security Context (All Pods)

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
  seccompProfile:
    type: RuntimeDefault
```

---

## 9. Resource Controls

### 9.1 Resource Quotas (Per Namespace)

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: education
spec:
  hard:
    requests.cpu: "4"
    requests.memory: "8Gi"
    limits.cpu: "8"
    limits.memory: "16Gi"
    pods: "20"
    services: "10"
```

### 9.2 LimitRanges (Per Namespace)

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: education
spec:
  limits:
    - default:
        cpu: "500m"
        memory: "512Mi"
      defaultRequest:
        cpu: "100m"
        memory: "128Mi"
      type: Container
```

---

## 10. Cross-Namespace Traffic Matrix

| Source ↓ / Dest → | education | research | finance | aegismesh-system | monitoring |
|---|---|---|---|---|---|
| **education** | ✅ (internal) | ❌ BLOCK | ❌ BLOCK | ✅ (policy eval) | ✅ (logging) |
| **research** | ❌ BLOCK | ✅ (internal) | ❌ BLOCK | ✅ (policy eval) | ✅ (logging) |
| **finance** | ❌ BLOCK | ❌ BLOCK | ✅ (internal) | ✅ (policy eval) | ✅ (logging) |
| **aegismesh-system** | ✅ (monitor) | ✅ (monitor) | ✅ (monitor) | ✅ (internal) | ✅ (logging) |
| **monitoring** | ✅ (collect) | ✅ (collect) | ✅ (collect) | ✅ (collect) | ✅ (internal) |

---

## 11. AegisMesh Containment via NetworkPolicy

When AegisMesh detects a compromised workload, it dynamically creates/updates NetworkPolicies to contain the blast radius.

### 11.1 Example: Contain education-api

**Before containment** — education-api can reach:
- education-db (port 5432) ✅
- education-frontend (ingress) ✅
- aegismesh-system (port 8000) ✅

**After containment** — education-api is restricted to:
- Only aegismesh-system (for status reporting)
- All other egress/ingress DENIED

```yaml
# Containment policy — replaces normal policies
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: containment-education-api
  namespace: education
  labels:
    aegismesh.io/containment: "true"
    aegismesh.io/incident-id: "INC-2026-001"
spec:
  podSelector:
    matchLabels:
      app: education-api
  policyTypes:
    - Ingress
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              domain: security
      ports:
        - port: 8000
          protocol: TCP
    - to: []
      ports:
        - port: 53
          protocol: UDP
  ingress: []  # No inbound traffic allowed
```

---

## 12. Kubernetes Testing Plan

| Test ID | Test | Method | Expected |
|---|---|---|---|
| K8S-01 | education-api → education-db | `kubectl exec` + `nc -zv` | ✅ ALLOW |
| K8S-02 | education-api → research-api | `kubectl exec` + `nc -zv` | ❌ BLOCK (timeout) |
| K8S-03 | education-api → finance-db | `kubectl exec` + `nc -zv` | ❌ BLOCK (timeout) |
| K8S-04 | research-api → education-db | `kubectl exec` + `nc -zv` | ❌ BLOCK (timeout) |
| K8S-05 | finance-api → finance-db | `kubectl exec` + `nc -zv` | ✅ ALLOW |
| K8S-06 | education-api → aegismesh (policy eval) | `kubectl exec` + `curl` | ✅ ALLOW |
| K8S-07 | Default SA cannot list pods in other namespace | `kubectl auth can-i` | ❌ DENIED |
| K8S-08 | education-api SA cannot read finance secrets | `kubectl auth can-i` | ❌ DENIED |
| K8S-09 | Application pods run as non-root | `kubectl get pod -o yaml` | `runAsNonRoot: true` |
| K8S-10 | After containment: education-api → education-db | `kubectl exec` + `nc -zv` | ❌ BLOCK (contained) |

### Verification Commands

```bash
# Check NetworkPolicies
kubectl get networkpolicies -n education
kubectl describe networkpolicy default-deny-all -n education

# Test connectivity
kubectl exec -n education deploy/education-api -- nc -zv education-db 5432
kubectl exec -n education deploy/education-api -- nc -zv research-api.research.svc.cluster.local 8080

# Check RBAC
kubectl auth can-i list pods --as=system:serviceaccount:education:education-api-sa -n finance
kubectl auth can-i get secrets --as=system:serviceaccount:education:education-api-sa -n finance

# Check pod security
kubectl get pods -n education -o jsonpath='{.items[*].spec.securityContext}'
```

---

## 13. Kubernetes File Deliverables

```
kubernetes/
├── cluster/
│   ├── kind-config.yaml           # kind cluster configuration
│   └── calico-install.yaml        # Calico CNI installation
│
├── namespaces/
│   ├── education.yaml
│   ├── research.yaml
│   ├── finance.yaml
│   ├── aegismesh-system.yaml
│   └── monitoring.yaml
│
├── deployments/
│   ├── education/
│   │   ├── frontend.yaml
│   │   ├── api.yaml
│   │   └── db.yaml
│   ├── research/
│   │   ├── frontend.yaml
│   │   ├── api.yaml
│   │   └── db.yaml
│   └── finance/
│       ├── frontend.yaml
│       ├── api.yaml
│       └── db.yaml
│
├── services/
│   ├── education/
│   ├── research/
│   └── finance/
│
├── rbac/
│   ├── education-rbac.yaml
│   ├── research-rbac.yaml
│   ├── finance-rbac.yaml
│   └── aegismesh-rbac.yaml
│
├── network-policies/
│   ├── default-deny-all.yaml
│   ├── education-policies.yaml
│   ├── research-policies.yaml
│   ├── finance-policies.yaml
│   └── aegismesh-policies.yaml
│
├── secrets/
│   ├── education-secrets.yaml.example
│   ├── research-secrets.yaml.example
│   └── finance-secrets.yaml.example
│
└── resource-controls/
    ├── quotas.yaml
    └── limit-ranges.yaml
```
