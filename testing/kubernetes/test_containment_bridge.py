"""
AegisMesh — Automated Real Dynamic Kubernetes Containment Bridge Verification
Empirically tests the complete Zero-Trust containment and release loop against Kind + Calico CNI.
"""
import sys
import os
import subprocess
import time
import json

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.containment.controller import containment_controller
from backend.app.integrations.kubernetes_client import k8s_client


def run_kubectl(cmd: str):
    p = subprocess.run(f"kubectl {cmd}", shell=True, text=True, capture_output=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def main():
    print("============================================================")
    print("  AEGISMESH — DYNAMIC KUBERNETES CONTAINMENT BRIDGE TEST")
    print("============================================================")

    # 0. Check Cluster Status & Clean Baseline
    status = k8s_client.get_cluster_status()
    print(f"[*] Cluster Status: {'CONNECTED' if status['connected'] else 'OFFLINE'}")
    print(f"[*] CNI Provider:   {status['cni']}")
    if not status["connected"]:
        print("[!] Local cluster offline. Aborting live test.")
        sys.exit(1)

    # Ensure baseline is clean
    k8s_client.release_isolation("education-client", namespace="education")
    k8s_client.release_isolation("education-app", namespace="education")
    time.sleep(1)

    # 1. Step 1: Baseline Authorized Access
    print("\n[STEP 1/6] Testing Baseline Authorized Connectivity (education-client -> education-app)...")
    rc, out, _ = run_kubectl("exec -n education education-client -- wget -T 4 -qO- http://education-app")
    if "Welcome to nginx!" in out:
        print(" -> STATUS: ALLOWED (HTTP 200 OK) [PASS]")
    else:
        print(f" -> STATUS: FAILED ({out})")
        sys.exit(1)

    # 2. Step 2: Trigger Containment via AegisMesh
    print("\n[STEP 2/6] Triggering AegisMesh Automated Quarantine on 'education-client'...")
    iso_res = containment_controller.isolate_workload(
        workload_id="education-client",
        reason="Lateral movement anomaly probe detected (Threat I-01)",
        threat_id="I-01",
        namespace="education",
    )
    print(f" -> Incident ID:   {iso_res.get('incident_id')}")
    print(f" -> Enforcement:   {iso_res.get('enforcement')}")
    print(f" -> Policy Name:   {iso_res.get('policy_name')}")
    print(f" -> State:         {iso_res.get('state')}")

    # 3. Step 3: Verify Dynamic NetworkPolicy in Kubernetes Cluster
    print("\n[STEP 3/6] Verifying NetworkPolicy in Kubernetes cluster...")
    rc, out, _ = run_kubectl("get networkpolicy -n education")
    print(out)
    if "aegismesh-isolate-education-client" in out:
        print(" -> Dynamic NetworkPolicy verified in cluster [PASS]")
    else:
        print(" -> Dynamic NetworkPolicy NOT found in cluster [FAIL]")
        sys.exit(1)

    # 4. Step 4: Test Real Traffic Block During Containment
    print("\n[STEP 4/6] Testing Real Traffic During Containment (education-client -> education-app)...")
    rc, out, err = run_kubectl("exec -n education education-client -- wget -T 4 -qO- http://education-app")
    if rc != 0 or "timed out" in err or "timed out" in out:
        print(" -> STATUS: BLOCKED BY CALICO CNI (Connection Timed Out) [PASS]")
    else:
        print(" -> STATUS: UNEXPECTED ALLOW [FAIL]")
        sys.exit(1)

    # 5. Step 5: Trigger Release Quarantine via AegisMesh
    print("\n[STEP 5/6] Triggering AegisMesh Release Quarantine on 'education-client'...")
    rel_res = containment_controller.restore_workload(
        workload_id="education-client",
        namespace="education",
    )
    print(f" -> Result:        {rel_res.get('message')}")
    print(f" -> Workload State: {rel_res.get('state')}")

    # 6. Step 6: Verify NetworkPolicy Removed and Connectivity Restored
    print("\n[STEP 6/6] Verifying NetworkPolicy Removal and Connectivity Restoration...")
    rc, out, _ = run_kubectl("get networkpolicy -n education")
    if "aegismesh-isolate-education-client" not in out:
        print(" -> Dynamic NetworkPolicy successfully removed from cluster [PASS]")
    else:
        print(" -> Dynamic NetworkPolicy still exists in cluster [FAIL]")
        sys.exit(1)

    rc, out, _ = run_kubectl("exec -n education education-client -- wget -T 4 -qO- http://education-app")
    if "Welcome to nginx!" in out:
        print(" -> Connectivity Restored: ALLOWED (HTTP 200 OK) [PASS]")
    else:
        print(f" -> Connectivity Restoration Failed ({out}) [FAIL]")
        sys.exit(1)

    print("\n============================================================")
    print("  ALL 6 PHASES PASSED — DYNAMIC CONTAINMENT LOOP EMPIRICALLY VERIFIED!")
    print("============================================================")


if __name__ == "__main__":
    main()
