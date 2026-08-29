# AegisMesh — Packet Tracer Security Test Matrix

**Date:** 2026-08-29  
**Version:** 1.1  
**Platform:** Cisco Packet Tracer 8.2+  
**Traces to:** AC-01, testing-strategy.md Layer 1, docs/threat-traceability.md  
**Status:** **AUTHORITATIVE TEST SPECIFICATION — PENDING EXECUTION**  

---

## 1. Multi-Tier Verification Model

For each test executed in Packet Tracer, record observations across all four empirical verification tiers:

| Field | Meaning |
|---|---|
| **Expected Behavior** | Layer 3/4 policy mandate (**ALLOW** or **BLOCK**) |
| **Actual Connectivity** | Observed result (Echo Reply received, HTTP page 200 OK, Request Timed Out, Destination Host Unreachable) |
| **ACL Match Evidence** | Output of `show access-lists` showing non-zero hit counter on the corresponding permit/deny line |
| **Simulation Evidence** | Packet Tracer Simulation Mode visual trace showing packet arrival or specific drop point (e.g. `SW-CORE` SVI) |
| **Verification Status** | `VERIFIED` (all 3 evidence tiers match expected), `FAILED` (any tier contradicts expected), or `PENDING EXECUTION` |

---

## 2. Pre-ACL Fabric Connectivity Tests

Run these initial baseline tests **before** activating ACL filters to prove that Layer 2 switching, Layer 3 SVIs, and point-to-point links are up.

| Pre-Test ID | Source Host | Destination Gateway / Target | Protocol | Expected | Actual Connectivity | Verification Status | Verification Scope |
|---|---|---|---|---|---|---|---|
| **PRE-01** | `FAC-PC-01` (10.10.10.100) | `10.10.10.1` (Vlan10 SVI) | ICMP Echo | ALLOW | PENDING EXECUTION | PENDING EXECUTION | Faculty VLAN 10 SVI Gateway |
| **PRE-02** | `APP-SRV-01` (10.10.20.10) | `10.10.20.1` (Vlan20 SVI) | ICMP Echo | ALLOW | PENDING EXECUTION | PENDING EXECUTION | Application VLAN 20 SVI Gateway |
| **PRE-03** | `MGMT-SRV-01` (10.10.30.10)| `10.10.30.1` (Vlan30 SVI) | ICMP Echo | ALLOW | PENDING EXECUTION | PENDING EXECUTION | Management VLAN 30 SVI Gateway |
| **PRE-04** | `DB-SRV-01` (10.10.40.10)   | `10.10.40.1` (Vlan40 SVI) | ICMP Echo | ALLOW | PENDING EXECUTION | PENDING EXECUTION | Database VLAN 40 SVI Gateway |
| **PRE-05** | `SEC-SRV-01` (10.10.50.10)  | `10.10.50.1` (Vlan50 SVI) | ICMP Echo | ALLOW | PENDING EXECUTION | PENDING EXECUTION | Security VLAN 50 SVI Gateway |
| **PRE-06** | `DMZ-SRV-01` (10.10.60.10)  | `10.10.60.1` (Vlan60 SVI) | ICMP Echo | ALLOW | PENDING EXECUTION | PENDING EXECUTION | DMZ VLAN 60 SVI Gateway |
| **PRE-07** | `FAC-PC-01`                 | `SW-CORE` DHCP Pool           | DHCP Req  | ALLOW | PENDING EXECUTION | PENDING EXECUTION | Dynamic IP allocation (10.10.10.100-200) |

---

## 3. Post-ACL Security Test Matrix (30 Test Cases)

### 3.1 Authorized Functional Traffic Tests (Expected: ALLOW)

| Test ID | Source Device | Dest Device | Protocol / Service | Expected | Actual Connectivity | ACL Hit Evidence | Simulation Trace | Status | Relevant Security Rule |
|---|---|---|---|---|---|---|---|---|---|
| **PT-01** | `FAC-PC-01` (VLAN 10) | `APP-SRV-01` (VLAN 20) | ICMP (Ping) | **ALLOW** | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | `FACULTY-ACCESS` line 1 (permit 10→20) & `APP-SERVER-ACCESS` line 3 (permit 20→10 return) |
| **PT-01b**| `FAC-PC-01` (VLAN 10) | `APP-SRV-01` (VLAN 20) | HTTP (TCP 80) | **ALLOW** | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | `FACULTY-ACCESS` line 1 & `APP-SERVER-ACCESS` line 3 |
| **PT-04** | `APP-SRV-01` (VLAN 20) | `DB-SRV-01` (VLAN 40)  | ICMP / TCP DB | **ALLOW** | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | `APP-SERVER-ACCESS` line 1 (permit 20→40) & `DB-ACCESS` line 2 (permit 40→20 return) |
| **PT-08** | `DMZ-SRV-01` (VLAN 60) | `APP-SRV-01` (VLAN 20) | ICMP / HTTP | **ALLOW** | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | `DMZ-ACCESS` line 1 (permit 60→20) & `APP-SERVER-ACCESS` line 4 (permit 20→60 return) |
| **PT-10** | `FAC-PC-01` (VLAN 10) | DHCP Gateway | UDP 67/68 | **ALLOW** | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | SVI Intra-VLAN broadcast |
| **PT-11** | `MGMT-SRV-01` (VLAN 30)| `DB-SRV-01` (VLAN 40)  | ICMP / SSH Admin | **ALLOW** | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | `MGMT-ACCESS` line 2 (permit 30→40) & `DB-ACCESS` line 3 (permit 40→30 return) |
| **PT-13** | `APP-SRV-01` (VLAN 20) | `FAC-PC-01` (VLAN 10)  | ICMP (Response) | **ALLOW** | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | `APP-SERVER-ACCESS` line 3 (permit 20→10 return path) |
| **PT-14** | `SEC-SRV-01` (VLAN 50) | `APP-SRV-01` (VLAN 20) | ICMP / Agent Poll | **ALLOW** | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | `SEC-ACCESS` line 1 (permit 50→20) |
| **PT-15** | `SEC-SRV-01` (VLAN 50) | `DB-SRV-01` (VLAN 40)  | ICMP / DB Audit | **ALLOW** | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | `SEC-ACCESS` line 2 (permit 50→40) |
| **PT-18** | `FAC-PC-01` (VLAN 10) | `DMZ-SRV-01` (VLAN 60) | ICMP / HTTP (Web) | **ALLOW** | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | `FACULTY-ACCESS` line 2 (permit 10→60) & `DMZ-ACCESS` line 3 (permit 60→10 return) |
| **PT-MGMT-01B** | `MGMT-SRV-01` (VLAN 30) | `SW-CORE` (10.10.30.1) / `R-EDGE` (10.10.0.1) | SSH (TCP 22) Admin | **ALLOW** | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | `MGMT-VTY-ACCESS` (`permit 10.10.30.0 0.0.0.255`) on `line vty 0 15` |
| **PT-LM-01**| `APP-SRV-01` (VLAN 20)| `DB-SRV-01` (VLAN 40)  | ICMP Echo | **ALLOW** | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | Authorized dependency communication |

---

### 3.2 Unauthorized Boundary & Lateral Movement Tests (Expected: BLOCK)

| Test ID | Source Device | Dest Device | Protocol / Attack Scenario | Expected | Actual Connectivity | ACL Hit Evidence | Simulation Trace | Status | Enforcing Security Rule |
|---|---|---|---|---|---|---|---|---|---|
| **PT-02** | `FAC-PC-01` (VLAN 10) | `DB-SRV-01` (VLAN 40)  | ICMP (Direct DB Access) | **BLOCK** | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | `FACULTY-ACCESS` line 4 (`deny ip 10.10.10.0 ... 10.10.40.0`) |
| **PT-03** | `FAC-PC-01` (VLAN 10) | `MGMT-SRV-01` (VLAN 30)| ICMP (Mgmt Recon) | **BLOCK** | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | `FACULTY-ACCESS` line 3 (`deny ip 10.10.10.0 ... 10.10.30.0`) |
| **PT-05** | `APP-SRV-01` (VLAN 20) | `MGMT-SRV-01` (VLAN 30)| ICMP (App→Mgmt Pivot) | **BLOCK** | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | `APP-SERVER-ACCESS` line 5 (`deny ip 10.10.20.0 ... 10.10.30.0`) |
| **PT-06** | `DMZ-SRV-01` (VLAN 60) | `DB-SRV-01` (VLAN 40)  | ICMP (DMZ→DB Breach) | **BLOCK** | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | `DMZ-ACCESS` line 4 (`deny ip 10.10.60.0 ... 10.10.40.0` - ARCH-SCENARIO-02) |
| **PT-07** | `DMZ-SRV-01` (VLAN 60) | `MGMT-SRV-01` (VLAN 30)| ICMP (DMZ→Mgmt Pivot) | **BLOCK** | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | `DMZ-ACCESS` line 5 (`deny ip 10.10.60.0 ... 10.10.30.0`) |
| **PT-09** | `DB-SRV-01` (VLAN 40)  | `FAC-PC-01` (VLAN 10)  | ICMP (DB Reverse Pivot)| **BLOCK** | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | `DB-ACCESS` line 4 (`deny ip any any` - ARCH-SCENARIO-01) |
| **PT-12** | `DB-SRV-01` (VLAN 40)  | `DMZ-SRV-01` (VLAN 60) | ICMP (DB→DMZ Outbound) | **BLOCK** | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | `DB-ACCESS` line 4 (`deny ip any any`) |
| **PT-16** | `FAC-PC-01` (VLAN 10) | `SEC-SRV-01` (VLAN 50) | ICMP (SIEM Tampering) | **BLOCK** | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | `FACULTY-ACCESS` line 5 (`deny ip 10.10.10.0 ... 10.10.50.0`) |
| **PT-MGMT-01A** | `FAC-PC-01` (VLAN 10) | `SW-CORE` (10.10.10.1) / `R-EDGE` (10.10.0.1) | SSH (TCP 22) Unauthorized | **BLOCK** | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | `MGMT-VTY-ACCESS` (`deny any` for non-VLAN 30 sources) on `line vty` |
| **PT-LM-02**| `APP-SRV-01` (VLAN 20)| `MGMT-SRV-01` (VLAN 30)| Lateral Movement Probe | **BLOCK** | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | `APP-SERVER-ACCESS` line 5 (`deny ip 10.10.20.0 ... 10.10.30.0`) |
| **PT-LM-03**| `DMZ-SRV-01` (VLAN 60)| `DB-SRV-01` (VLAN 40)  | Lateral Data Exfil | **BLOCK** | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | `DMZ-ACCESS` line 4 (ARCH-SCENARIO-02) |
| **PT-LM-04**| `DMZ-SRV-01` (VLAN 60)| `MGMT-SRV-01` (VLAN 30)| Admin Escalation Attempt| **BLOCK** | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | `DMZ-ACCESS` line 5 |
| **PT-LM-05**| `DB-SRV-01` (VLAN 40) | `FAC-PC-01` (VLAN 10)  | Reverse Workstation Pivot| **BLOCK**| PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | PENDING EXECUTION | `DB-ACCESS` line 4 (ARCH-SCENARIO-01) |

---

## 4. Cisco Packet Tracer Simulation Capture Protocol

When capturing evidence in Packet Tracer Simulation Mode:
1. Enable Simulation filter for `ICMP`, `HTTP`, `TCP`, `DNS`.
2. Generate packet from source terminal.
3. Observe PDU flow hop-by-hop across `SW-ACCESS-X` $\rightarrow$ `SW-CORE` $\rightarrow$ Target.
4. For **ALLOW** tests: Verify PDU arrives at target and return reply completes full round-trip.
5. For **BLOCK** tests: Identify that PDU is dropped at `SW-CORE` ingress SVI with a red indicator, confirming packet is destroyed at the security perimeter.
6. Capture screenshot showing Event List and PDU Details, and store in `packet-tracer/test-results/evidence/<Test-ID>.png`.
