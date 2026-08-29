# AegisMesh — Kubernetes Security Architecture

**Version:** 1.0  
**Date:** 2026-08-29  
**Project:** AegisMesh — Cisco Virtual Internship 2026 Cyber Security  
**Status:** Architecture Design / Proposed Implementation  
**Traces to:** SR-03, SR-04, SR-05, FR-04, FR-05  

---

## 1. Overview

The Kubernetes layer provides **workload-level isolation** for cloud-native microservices. Three domain namespaces (`education`, `research`, `finance`) host independent application stacks with strict cross-namespace isolation enforced through NetworkPolicies, RBAC, and Pod Security Standards.

> **Implementation Status:** This document describes the designed Kubernetes security architecture. The Kubernetes cluster has not been deployed. All specifications are architecture design artifacts aligned with the Cisco problem statement.

---

## 2. Cluster Topology

```
┌──────────────────────────────────────────────────────────────┐
│                 KUBERNETES CLUSTER (kind)                    │
│                 CNI: Calico (NetworkPolicy enforcement)      │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              CONTROL PLANE NODE                      │    │
│  │  kube-apiserver, etcd, controller-manager, scheduler │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────┐  ┌────────────────────┐             │
│  │    WORKER NODE 1   │  │    WORKER NODE 2   │             │
│  │                    │  │                    │             │
│  │  ┌──────────────┐  │  │  ┌──────────────┐  │             │
│  │  │  education   │  │  │  │  research    │  │             │
│  │  │  namespace   │  │  │  │  namespace   │  │             │
│  │  │  ┌────────┐  │  │  │  │  ┌────────┐  │  │             │
│  │  │  │api-pod │  │  │  │  │  │api-pod │  │  │             │
│  │  │  │db-pod  │  │  │  │  │  │db-pod  │  │  │             │
│  │  │  │worker  │  │  │  │  │  │worker  │  │  │             │
│  │  │  └────────┘  │  │  │  │  └────────┘  │  │             │
│  │  └──────────────┘  │  │  └──────────────┘  │             │
│  │                    │  │                    │             │
│  │  ┌──────────────┐  │  │  ┌──────────────┐  │             │
│  │  │  finance     │  │  │  │  monitoring  │  │             │
│  │  │  namespace   │  │  │  │  namespace   │  │             │
│  │  │  ┌────────┐  │  │  │  │  ┌────────┐  │  │             │
│  │  │  │api-pod │  │  │  │  │  │wazuh   │  │  │             │
│  │  │  │db-pod  │  │  │  │  │  │agent   │  │  │             │
│  │  │  │worker  │  │  │  │  │  └────────┘  │  │             │
│  │  │  └────────┘  │  │  │  └──────────────┘  │             │
│  │  └──────────────┘  │  │                    │             │
│  │                    │  │  ┌──────────────┐  │             │
│  │  ┌──────────────┐  │  │  │ aegismesh-   │  │             │
│  │  │ (available)  │  │  │  │ system       │  │             │
│  │  └──────────────┘  │  │  │  ┌────────┐  │  │             │
│  │                    │  │  │  │aegis-  │  │  │             │
│  │                    │  │  │  │mesh-api│  │  │             │
│  │                    │  │  │  └────────┘  │  │             │
│  │                    │  │  └──────────────┘  │             │
│  └────────────────────┘  └────────────────────┘             │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. Namespace Isolation Design

### 3.1 Default-Deny NetworkPolicy

Every domain namespace enforces a default-deny ingress and egress policy. No traffic is permitted unless explicitly allowed by an additional NetworkPolicy:

```yaml
# Applied to: education, research, finance namespaces
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: education   # repeated for each domain namespace
spec:
  podSelector: {}        # applies to ALL pods in namespace
  policyTypes:
    - Ingress
    - Egress
```

### 3.2 Authorized Intra-Namespace Communication

Within each domain namespace, pods are allowed to communicate with each other (API → DB, API → Worker):

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-intra-namespace
  namespace: education
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector: {}   # same namespace only
  egress:
    - to:
        - podSelector: {}   # same namespace only
```

### 3.3 Cross-Namespace Traffic Matrix

| Source Namespace | Destination Namespace | Policy | Reason |
|---|---|:---:|---|
| education | research | ❌ DENY | Domain isolation (SR-03) |
| education | finance | ❌ DENY | Domain isolation (SR-03) |
| research | finance | ❌ DENY | Domain isolation (SR-03) |
| education | aegismesh-system | ✅ ALLOW | Security reporting |
| research | aegismesh-system | ✅ ALLOW | Security reporting |
| finance | aegismesh-system | ✅ ALLOW | Security reporting |
| monitoring | all domains | ✅ ALLOW | Log collection |
| aegismesh-system | all domains | ✅ ALLOW | Policy enforcement |

---

## 4. RBAC Design

### 4.1 Role Hierarchy

| Role Type | Role Name | Scope | Permissions |
|---|---|---|---|
| ClusterRole | `cluster-admin` | Cluster | Full access (break-glass only) |
| ClusterRole | `aegismesh-controller` | Cluster | CRUD on NetworkPolicies across namespaces |
| ClusterRole | `monitoring-reader` | Cluster | Read pods, logs, events across namespaces |
| Role | `education-developer` | education | Deploy, scale, view pods/services/configmaps |
| Role | `research-developer` | research | Deploy, scale, view pods/services/configmaps |
| Role | `finance-developer` | finance | Deploy, scale, view pods/services/configmaps |

### 4.2 Key RBAC Constraint

**No developer role grants cross-namespace access:**

```yaml
# education-developer can ONLY operate in education namespace
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: education-developer-binding
  namespace: education                   # scoped to education ONLY
subjects:
  - kind: User
    name: edu-dev-user
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: education-developer
  apiGroup: rbac.authorization.k8s.io
```

---

## 5. Pod Security Standards

| Namespace | PSS Level | Key Restrictions |
|---|---|---|
| education | Restricted | No privileged, no hostPath, no hostNetwork, no root |
| research | Restricted | No privileged, no hostPath, no hostNetwork, no root |
| finance | Restricted | No privileged, no hostPath, no hostNetwork, no root |
| aegismesh-system | Restricted | No privileged; limited hostPath for config only |
| monitoring | Baseline | Wazuh agent may need host-level log access |

---

## 6. Resource Controls

### 6.1 ResourceQuotas (Per Namespace)

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: domain-quota
  namespace: education
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "20"
    services: "10"
```

### 6.2 LimitRanges (Per Pod)

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: domain-limits
  namespace: education
spec:
  limits:
    - type: Container
      default:
        cpu: 500m
        memory: 512Mi
      defaultRequest:
        cpu: 100m
        memory: 128Mi
      max:
        cpu: "2"
        memory: 4Gi
```

**Security Purpose:** Resource controls prevent a compromised or runaway workload in one namespace from consuming cluster resources and causing denial of service to other namespaces (maps to threat D-02).

---

## 7. Integration with AegisMesh Security Engine

### 7.1 AegisMesh Kubernetes Agent

The AegisMesh backend running in `aegismesh-system` namespace acts as a security control plane:

```
Wazuh Agent (monitoring NS)
    │ collects pod logs, events
    ▼
AegisMesh Detection Module (aegismesh-system NS)
    │ correlates events, identifies anomalies
    ▼
AegisMesh Risk Engine
    │ computes risk score for affected workload
    ▼
AegisMesh Containment Controller
    │ if risk > threshold:
    │   1. Update NetworkPolicy → restrict pod egress
    │   2. Update pod labels → trigger isolation
    │   3. Create incident record
    ▼
Dashboard (aegismesh-system NS)
    displays containment status in real-time
```

### 7.2 Containment via NetworkPolicy

When AegisMesh detects a compromised pod, it dynamically updates the NetworkPolicy to restrict the pod's network access:

```yaml
# Containment policy: restrict compromised education API pod
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: contain-education-api
  namespace: education
spec:
  podSelector:
    matchLabels:
      app: education-api
      aegismesh.io/status: contained     # label applied by containment controller
  policyTypes:
    - Egress
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: education-db          # preserve authorized DB dependency
      ports:
        - port: 5432
    # ALL other egress is DENIED — blast radius contained
```

---

## 8. Alignment with Cisco Problem Statement

| Cisco Requirement | Kubernetes Implementation |
|---|---|
| Application isolation to prevent lateral movement | Default-deny NetworkPolicy per namespace |
| Network policies and namespace isolation | Calico-enforced NetworkPolicies + namespace separation |
| Kubernetes / microservices security | RBAC + PSS + ServiceAccount isolation |
| Incident containment and blast-radius reduction | Dynamic NetworkPolicy updates via AegisMesh |
| Scalability without unnecessary complexity | ResourceQuotas prevent noisy-neighbor DoS |
| IAM / RBAC with least privilege | Per-namespace Roles + per-pod ServiceAccounts |
