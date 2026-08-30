# AegisMesh Kubernetes Security Validation

## Test 1 — Education → Education App

Command:

kubectl exec -n education education-client -- wget -qO- http://education-app

Expected: ALLOW

Result: PASS

The education client successfully reached the education application.


## Test 2 — Education → Finance DB

Command:

kubectl exec -n education education-client -- wget -T 5 -qO- http://finance-db.finance.svc.cluster.local

Expected: BLOCK

Result: PASS

The request timed out, proving that traffic from the education namespace to the finance database is blocked by NetworkPolicy.


## Network Policies

### Finance Default Deny

- Namespace: finance
- Policy: default-deny-all
- Blocks ingress and egress traffic.

### Education Application Policy

- Namespace: education
- Policy: allow-education-client
- Allows education-client to access education-app on TCP port 80.


## Kubernetes Environment

Cluster: aegismesh

Control Plane: Ready

Kubernetes Version: v1.37.0