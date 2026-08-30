# AegisMesh — Kubernetes Security Lab Validation & Empirical Test Report

**Environment:** Locally implemented and validated Kubernetes security model  
**Cluster Orchestrator:** Kind (Kubernetes in Docker) `v0.33.0` running Kubernetes `v1.37.0`  
**Host Runtime:** Docker Desktop Engine `v29.5.3` (WSL2 Linux Kernel `6.18.33`)  
**Container Network Interface (CNI):** Project Calico `v3.28.0` (Configured with `disableDefaultCNI: true` to enforce real packet-level `NetworkPolicy` dropping)  

---

## 1. Cluster Architecture & Configuration

```
┌────────────────────────────────────────────────────────────────────────┐
│                      KIND LOCAL CLUSTER (aegismesh-k8s)                │
│                                                                        │
│  [Calico CNI v3.28.0 Controller & Felix Node DaemonSet]                │
│                                                                        │
│  ┌───────────────────────────┐        ┌─────────────────────────────┐  │
│  │   Namespace: education    │        │     Namespace: finance      │  │
│  │                           │        │                             │  │
│  │  [education-client]       │  HTTP  │  [finance-db]               │  │
│  │         │                 │  80    │  (Default-Deny Policy)      │  │
│  │         ▼ (ALLOW)         │  XXX   │                             │  │
│  │  [education-app]          │  ──────┼──▶ 🛑 DROPPED BY CALICO     │  │
│  │  (allow-education-client) │        │                             │  │
│  └───────────────────────────┘        └─────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

* **Cluster Spec:** [`kubernetes/cluster/kind-config.yaml`](../cluster/kind-config.yaml)
  * `disableDefaultCNI: true`
  * `podSubnet: "192.168.0.0/16"`
* **CNI Deployment:** `Project Calico v3.28.0` (`calico-node` DaemonSet + `calico-kube-controllers`)

---

## 2. Test Execution & Empirical Results

### TEST 1 — Authorized Intra-Namespace Communication
* **Source:** `education-client` (`education` namespace)
* **Destination:** `education-app` (`education` namespace)
* **Applied Policy:** `allow-education-client` (Ingress on port 80 permitted from `app=education-client`)
* **Execution Command:**
  ```powershell
  kubectl exec -n education education-client -- wget -qO- http://education-app
  ```
* **Expected Result:** `ALLOW` (HTTP 200 / Nginx Welcome HTML)
* **Actual Output:**
  ```html
  <!DOCTYPE html>
  <html>
  <head><title>Welcome to nginx!</title></head>
  <body><h1>Welcome to nginx!</h1></body>
  </html>
  ```
* **Status:** 🟢 **PASS (ALLOWED)**

---

### TEST 2 — Unauthorized Cross-Namespace Lateral Movement
* **Source:** `education-client` (`education` namespace)
* **Destination:** `finance-db` (`finance` namespace — `http://finance-db.finance.svc.cluster.local`)
* **Applied Policy:** `default-deny-all` in `finance` namespace
* **Execution Command:**
  ```powershell
  kubectl exec -n education education-client -- wget -T 5 -qO- http://finance-db.finance.svc.cluster.local
  ```
* **Expected Result:** `BLOCK` (SYN packet dropped by Calico; connection timed out)
* **Actual Output:**
  ```text
  wget: download timed out
  command terminated with exit code 1
  ```
* **Status:** 🟢 **PASS (BLOCKED by NetworkPolicy)**

---

### TEST 3 — Default-Deny Security Perimeter
* **Source:** Unregistered workload in `research` namespace (`rogue-pod`)
* **Destination:** `finance-db` (`finance` namespace)
* **Applied Policy:** `default-deny-all` (`spec.podSelector: {}` with Ingress & Egress restricted)
* **Execution Command:**
  ```powershell
  kubectl exec -n research rogue-pod -- wget -T 5 -qO- http://finance-db.finance.svc.cluster.local
  ```
* **Expected Result:** `BLOCK`
* **Actual Output:**
  ```text
  wget: download timed out
  command terminated with exit code 1
  ```
* **Status:** 🟢 **PASS (BLOCKED by Default-Deny)**

---

### TEST 4 — Kubernetes RBAC Least-Privilege Verification
* **Subject:** `education-service-account` in `education` namespace
* **Assigned Role:** `education-reader` (`RoleBinding`: `education-reader-binding`)
* **Allowed Actions:** `get`, `list`, `watch` on `pods`, `services` in `education` namespace
* **Execution & Empirical Output:**

| Authorization Query Command | Expected | Actual Output | Status |
| :--- | :--- | :--- | :--- |
| `kubectl auth can-i list pods -n education --as=system:serviceaccount:education:education-service-account` | `yes` | `yes` | 🟢 **PASS** |
| `kubectl auth can-i delete pods -n education --as=system:serviceaccount:education:education-service-account` | `no` | `no` | 🟢 **PASS** |
| `kubectl auth can-i create secrets -n education --as=system:serviceaccount:education:education-service-account` | `no` | `no` | 🟢 **PASS** |
| `kubectl auth can-i list pods -n finance --as=system:serviceaccount:education:education-service-account` | `no` | `no` | 🟢 **PASS** |

* **Status:** 🟢 **PASS (RBAC Least Privilege Strictly Enforced)**

---

## 3. Automated Validation Script

To re-run the entire test suite in a single command at any time:

```powershell
powershell -File testing/kubernetes/run-k8s-tests.ps1
```

Or on Linux / macOS / WSL:
```bash
chmod +x testing/kubernetes/run-k8s-tests.sh
./testing/kubernetes/run-k8s-tests.sh
```

---

## 4. Scope & Technical Limitations

* **Local Environment:** This deployment is a **locally implemented and validated Kubernetes security model** running on Kind and Docker Desktop with Calico CNI.
* **Non-Cloud Scope:** It does not represent or claim a live cloud-managed provider deployment (such as AWS EKS or GCP GKE).
* **Simulated Bridge:** This real cluster provides the container validation foundation for AegisMesh, verifying Zero-Trust namespace isolation and ingress filtering under live kernel packet enforcement.