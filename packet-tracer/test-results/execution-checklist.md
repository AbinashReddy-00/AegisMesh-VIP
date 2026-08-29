# Phase 4 Validation — Execution Checklist

**Status:** IMPLEMENTATION COMPLETE — VALIDATION PENDING  
**Executor:** You (Packet Tracer is a GUI application — cannot be automated)  
**Estimated Time:** 30–45 minutes  

---

## Why This Must Be Done Manually

Cisco Packet Tracer is a native desktop GUI application with no CLI, API, or scripting interface. There is no way to automate:
- Device placement and cabling
- Configuration pasting
- Ping tests
- Simulation Mode capture
- Screenshot collection

This is a known limitation, not an implementation failure.

---

## Step-by-Step Execution Guide

### STEP 1: Build the Topology (10–15 min)

Follow [build-guide.md](file:///C:/Users/abhia/.gemini/antigravity-ide/scratch/AegisMesh/packet-tracer/configurations/build-guide.md) exactly.

1. Open Cisco Packet Tracer
2. Place devices:
   - 1× Router 2911 (name: R-EDGE)
   - 1× Switch 3560-24PS (name: SW-CORE)
   - 3× Switch 2960-24TT (names: SW-ACCESS-1, SW-ACCESS-2, SW-ACCESS-3)
   - 3× PC (names: FAC-PC-01, FAC-PC-02, FAC-PC-03)
   - 5× Server (names: APP-SRV-01, APP-SRV-02, DMZ-SRV-01, DB-SRV-01, DB-SRV-02)
   - 2× Server (names: MGMT-SRV-01, SEC-SRV-01)

3. Cable (all Copper Straight-Through):

   | From | Port | To | Port |
   |---|---|---|---|
   | R-EDGE | Gig0/1 | SW-CORE | Gig0/1 |
   | SW-CORE | Fa0/1 | SW-ACCESS-1 | Fa0/24 |
   | SW-CORE | Fa0/2 | SW-ACCESS-2 | Fa0/24 |
   | SW-CORE | Fa0/3 | SW-ACCESS-3 | Fa0/24 |
   | SW-ACCESS-1 | Fa0/1 | FAC-PC-01 | Fa0 |
   | SW-ACCESS-1 | Fa0/2 | FAC-PC-02 | Fa0 |
   | SW-ACCESS-1 | Fa0/3 | FAC-PC-03 | Fa0 |
   | SW-ACCESS-1 | Fa0/10 | DMZ-SRV-01 | Fa0 |
   | SW-ACCESS-2 | Fa0/1 | APP-SRV-01 | Fa0 |
   | SW-ACCESS-2 | Fa0/2 | APP-SRV-02 | Fa0 |
   | SW-ACCESS-2 | Fa0/3 | DB-SRV-01 | Fa0 |
   | SW-ACCESS-2 | Fa0/4 | DB-SRV-02 | Fa0 |
   | SW-ACCESS-3 | Fa0/1 | MGMT-SRV-01 | Fa0 |
   | SW-ACCESS-3 | Fa0/2 | SEC-SRV-01 | Fa0 |

### STEP 2: Apply Device Configurations (5–10 min)

For each device, click → CLI tab → type `enable` → paste the configuration.

Paste order matters — do SW-CORE first (it creates VLANs and ACLs):

1. **SW-CORE** — paste from [SW-CORE.txt](file:///C:/Users/abhia/.gemini/antigravity-ide/scratch/AegisMesh/packet-tracer/configurations/SW-CORE.txt)
2. **R-EDGE** — paste from [R-EDGE.txt](file:///C:/Users/abhia/.gemini/antigravity-ide/scratch/AegisMesh/packet-tracer/configurations/R-EDGE.txt)
3. **SW-ACCESS-1** — paste from [SW-ACCESS-1.txt](file:///C:/Users/abhia/.gemini/antigravity-ide/scratch/AegisMesh/packet-tracer/configurations/SW-ACCESS-1.txt)
4. **SW-ACCESS-2** — paste from [SW-ACCESS-2.txt](file:///C:/Users/abhia/.gemini/antigravity-ide/scratch/AegisMesh/packet-tracer/configurations/SW-ACCESS-2.txt)
5. **SW-ACCESS-3** — paste from [SW-ACCESS-3.txt](file:///C:/Users/abhia/.gemini/antigravity-ide/scratch/AegisMesh/packet-tracer/configurations/SW-ACCESS-3.txt)

> **⚠️ Important:** If you see errors during paste (e.g., `% Invalid input`), note the exact error and the command that failed. Some commands may not be supported in your PT version. This is expected for hardening commands like `switchport nonegotiate` or `no cdp run`.

### STEP 3: Configure End Device IPs (5 min)

**Faculty PCs** — Click → Desktop → IP Configuration → Select **DHCP**
- FAC-PC-01: Wait for IP (expect 10.10.10.100+)
- FAC-PC-02: Wait for IP
- FAC-PC-03: Wait for IP

**Servers** — Click → Desktop → IP Configuration → Select **Static**

| Device | IP | Mask | Gateway |
|---|---|---|---|
| APP-SRV-01 | 10.10.20.10 | 255.255.255.0 | 10.10.20.1 |
| APP-SRV-02 | 10.10.20.11 | 255.255.255.0 | 10.10.20.1 |
| DB-SRV-01 | 10.10.40.10 | 255.255.255.0 | 10.10.40.1 |
| DB-SRV-02 | 10.10.40.11 | 255.255.255.0 | 10.10.40.1 |
| MGMT-SRV-01 | 10.10.30.10 | 255.255.255.0 | 10.10.30.1 |
| SEC-SRV-01 | 10.10.50.10 | 255.255.255.0 | 10.10.50.1 |
| DMZ-SRV-01 | 10.10.60.10 | 255.255.255.0 | 10.10.60.1 |

**Enable HTTP** on APP-SRV-01, APP-SRV-02, DMZ-SRV-01:
- Click → Services → HTTP → Ensure ON

### STEP 4: Run Verification Commands (2 min)

On **SW-CORE** CLI, run and screenshot:
```
show vlan brief
show ip interface brief
show ip route
show interfaces trunk
show access-lists
```

On **R-EDGE** CLI, run:
```
show ip interface brief
show ip route
```

### STEP 5: Run Pre-ACL Connectivity Tests (3 min)

On each end device, open Command Prompt (Desktop → Command Prompt) and ping the gateway:

| Test | From | Command | Expected |
|---|---|---|---|
| PRE-01 | FAC-PC-01 | `ping 10.10.10.1` | Reply from 10.10.10.1 |
| PRE-02 | APP-SRV-01 | `ping 10.10.20.1` | Reply |
| PRE-03 | DB-SRV-01 | `ping 10.10.40.1` | Reply |
| PRE-04 | MGMT-SRV-01 | `ping 10.10.30.1` | Reply |
| PRE-05 | SEC-SRV-01 | `ping 10.10.50.1` | Reply |
| PRE-06 | DMZ-SRV-01 | `ping 10.10.60.1` | Reply |
| PRE-07 | FAC-PC-01 | Check IP config | IP is 10.10.10.1xx |

### STEP 6: Run Security Tests (10–15 min)

For each test, open Command Prompt on the SOURCE device and run the ping command. For HTTP tests, open Web Browser on the source device and enter the destination IP.

**ALLOW Tests (should succeed):**

| Test | From | Command / Action | Expected |
|---|---|---|---|
| PT-01 | FAC-PC-01 | `ping 10.10.20.10` | Reply ✅ |
| PT-01b | FAC-PC-01 | Web Browser → `http://10.10.20.10` | Page loads ✅ |
| PT-04 | APP-SRV-01 | `ping 10.10.40.10` | Reply ✅ |
| PT-08 | DMZ-SRV-01 | `ping 10.10.20.10` | Reply ✅ |
| PT-10 | FAC-PC-01 | DHCP (already done) | IP assigned ✅ |
| PT-18 | FAC-PC-01 | `ping 10.10.60.10` / Browser `http://10.10.60.10` | Reply / Page loads ✅ |
| PT-MGMT-01B | MGMT-SRV-01 | `ssh -l admin 10.10.30.1` (SW-CORE) | Password prompt (AdminSSH2026!) ✅ |

**BLOCK Tests (should fail — "Request timed out", "Destination unreachable", or connection refused):**

| Test | From | Command / Action | Expected |
|---|---|---|---|
| PT-02 | FAC-PC-01 | `ping 10.10.40.10` | Timed out ❌ |
| PT-03 | FAC-PC-01 | `ping 10.10.30.10` | Timed out ❌ |
| PT-05 | APP-SRV-01 | `ping 10.10.30.10` | Timed out ❌ |
| PT-06 | DMZ-SRV-01 | `ping 10.10.40.10` | Timed out ❌ |
| PT-07 | DMZ-SRV-01 | `ping 10.10.30.10` | Timed out ❌ |
| PT-09 | DB-SRV-01 | `ping 10.10.10.100` | Timed out ❌ |
| PT-MGMT-01A | FAC-PC-01 | `ssh -l admin 10.10.10.1` | Connection refused / dropped ❌ |

**Bidirectional & Zone Tests:**

| Test | From | Command | Expected |
|---|---|---|---|
| PT-11 | MGMT-SRV-01 | `ping 10.10.40.10` | Reply ✅ |
| PT-12 | DB-SRV-01 | `ping 10.10.60.10` | Timed out ❌ |
| PT-13 | APP-SRV-01 | `ping 10.10.10.100` | Reply ✅ |
| PT-14 | SEC-SRV-01 | `ping 10.10.20.10` | Reply ✅ |
| PT-15 | SEC-SRV-01 | `ping 10.10.40.10` | Reply ✅ |
| PT-16 | FAC-PC-01 | `ping 10.10.50.10` | Timed out ❌ |

**Lateral Movement Tests:**

| Test | From | Command | Expected |
|---|---|---|---|
| PT-LM-01 | APP-SRV-01 | `ping 10.10.40.10` | Reply ✅ |
| PT-LM-02 | APP-SRV-01 | `ping 10.10.30.10` | Timed out ❌ |
| PT-LM-03 | DMZ-SRV-01 | `ping 10.10.40.10` | Timed out ❌ |
| PT-LM-04 | DMZ-SRV-01 | `ping 10.10.30.10` | Timed out ❌ |
| PT-LM-05 | DB-SRV-01 | `ping 10.10.10.100` | Timed out ❌ |

### STEP 7: Simulation Mode Evidence (5 min)

1. Switch to **Simulation Mode** (bottom-right of PT window)
2. Run these specific tests and capture screenshots:

   a. **PT-01 in Simulation:** FAC-PC-01 → `ping 10.10.20.10`
      - Watch the PDU traverse: FAC-PC-01 → SW-ACCESS-1 → SW-CORE → SW-ACCESS-2 → APP-SRV-01
      - Screenshot the successful traversal

   b. **PT-02 in Simulation:** FAC-PC-01 → `ping 10.10.40.10`
      - Watch the PDU: FAC-PC-01 → SW-ACCESS-1 → SW-CORE (dropped!)
      - Screenshot the packet being dropped at SW-CORE

   c. **PT-05 in Simulation:** APP-SRV-01 → `ping 10.10.30.10`
      - Watch the PDU: APP-SRV-01 → SW-ACCESS-2 → SW-CORE (dropped!)
      - Screenshot

   d. **PT-06 in Simulation:** DMZ-SRV-01 → `ping 10.10.40.10`
      - Watch the PDU: DMZ-SRV-01 → SW-ACCESS-1 → SW-CORE (dropped!)
      - Screenshot

   e. **PT-07 in Simulation:** DMZ-SRV-01 → `ping 10.10.30.10`
      - Screenshot

3. Save screenshots to `packet-tracer/test-results/evidence/`

### STEP 8: Final Verification Commands (2 min)

On **SW-CORE**, run `show access-lists` again and screenshot the output. Look for non-zero match counts on both permit and deny rules.

### STEP 9: Save

Save the topology as `packet-tracer/topology.pkt`

---

## After Execution

Come back and tell me:
1. Which tests passed and which failed
2. Any configuration errors encountered
3. Any PT-version-specific issues
4. Paste the output of `show access-lists` from SW-CORE

I will then update all documentation with real results, handle any failures, complete the Security VLAN review, and produce the final Phase 4 validation report.
