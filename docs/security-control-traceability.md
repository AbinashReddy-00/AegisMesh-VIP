# AegisMesh — Security Control Traceability Matrix

**Date:** 2026-08-29  
**Version:** 1.1 (Canonicalized)  
**Scope:** Private Enterprise Datacenter Security Controls  
**Source of Truth:** `docs/architecture/threat-model.md`  
**Traces to:** `docs/requirements/requirements.md`, `packet-tracer/acl/acl-design.md`, `packet-tracer/test-results/test-matrix.md`  

---

## 1. Control Framework Overview

This matrix maps each architectural security control in the private datacenter to the canonical threat it mitigates (from `docs/architecture/threat-model.md`), its exact implementation location, its verification method, and its current status under the standardized validation framework.

---

## 2. Security Control Traceability

| Control ID | Security Control | Threat Mitigated (Canonical STRIDE) | Implementation | Verification Method | Status |
|---|---|---|---|---|---|
| **SC-01** | **VLAN Segmentation & Trunk Hardening** | `S-03` (VLAN Hopping via trunk misconfiguration) | VLANs 10, 20, 30, 40, 50, 60 on `SW-CORE` and `SW-ACCESS-1..3`; Native VLAN 99 unused; unused ports assigned to VLAN 99 and disabled | `show vlan brief`, `show interfaces trunk`, intra-VLAN isolation tests (PRE-01..07) | IMPLEMENTED — VALIDATION PENDING |
| **SC-02** | **Faculty Ingress Access Control (`FACULTY-ACCESS`)** | `E-04` (Direct DB Access by users), `T-02` (Unauthorized device access), `R-02` (Log interference) | Extended ACL on SVI `Vlan10` of `SW-CORE`: Explicit permit to VLAN 20 & 60; Explicit deny to VLAN 30, 40, 50; Permit to internet | PT-01, PT-01b, PT-02, PT-03, PT-16, `show access-lists FACULTY-ACCESS` | IMPLEMENTED — VALIDATION PENDING |
| **SC-03** | **Application Tier Lateral Movement Control (`APP-SERVER-ACCESS`)** | `E-02` (App server compromise leading to Management pivot) | Extended ACL on SVI `Vlan20` of `SW-CORE`: Explicit permit to DB (40), Logging (50), return to Faculty (10) & DMZ (60); Explicit deny to Mgmt (30); Default deny any any | PT-04, PT-05, PT-13, PT-LM-01, PT-LM-02, `show access-lists APP-SERVER-ACCESS` | IMPLEMENTED — VALIDATION PENDING |
| **SC-04** | **DMZ Tier Isolation (`DMZ-ACCESS`)** | `ARCH-SCENARIO-02` (DMZ-to-Database unauthorized reachability), `E-02` (DMZ to Mgmt pivot) | Extended ACL on SVI `Vlan60` of `SW-CORE`: Explicit permit to App (20) reverse proxy, return to Faculty (10), & Logging (50); Explicit deny to DB (40), Mgmt (30); Default deny any any | PT-06, PT-07, PT-08, PT-18, PT-LM-03, PT-LM-04, `show access-lists DMZ-ACCESS` | IMPLEMENTED — VALIDATION PENDING |
| **SC-05** | **Management Zone Isolation & VTY Hardening (`MGMT-ACCESS`, `MGMT-VTY-ACCESS`)** | `T-02` (Router/Switch ACL and device configuration alteration) | Extended ACL on SVI `Vlan30` of `SW-CORE`: Permit to App (20), DB (40), Logging (50); Deny to all other. Standard ACL `MGMT-VTY-ACCESS` applied to VTY lines on all routers/switches (permit 10.10.30.0/24 only; SSH v2) | PT-11, PT-MGMT-01A, PT-MGMT-01B, `show running-config \| section line vty` | IMPLEMENTED — VALIDATION PENDING |
| **SC-06** | **Database Egress Isolation (`DB-ACCESS`)** | `ARCH-SCENARIO-01` (Database reverse pivot to user network), `ARCH-SCENARIO-02` (Outbound exfiltration prevention) | Extended ACL on SVI `Vlan40` of `SW-CORE`: Permit to Logging (50), return to App (20), return to Mgmt (30); Terminating with explicit `deny ip any any`. Strictly prohibits DB-initiated sessions to Faculty (10), DMZ (60), or Internet | PT-09, PT-12, PT-LM-05, `show access-lists DB-ACCESS` | IMPLEMENTED — VALIDATION PENDING |
| **SC-07** | **Security/SIEM Telemetry Isolation (`SEC-ACCESS`)** | `R-02` (Log interference), Lateral movement from compromised SIEM | Extended ACL on SVI `Vlan50` of `SW-CORE`: Permit polling to App (20), DB (40), DMZ (60), Mgmt (30); Explicit deny to Faculty (10); Explicit deny to Internet (any); Default deny any any | PT-14, PT-15, `show access-lists SEC-ACCESS` | IMPLEMENTED — VALIDATION PENDING |
| **SC-08** | **Device Physical & Port-Level Hardening** | `S-03` (VLAN hopping & unauthorized port access) | Spanning-tree portfast on access ports, unused switchports administratively disabled and mapped to blackhole VLAN 99, enable secret type 5 password hashing, console login timeouts | `show running-config`, `show interfaces status` across all switches | IMPLEMENTED — VALIDATION PENDING |

---

## 3. Control Implementation & Verification Summary

- **Total Security Controls:** 8 distinct controls spanning L2, L3, L4, and administrative boundaries.
- **Enforcement Mechanisms:** Cisco IOS Extended Access Control Lists, Switched Virtual Interfaces, Standard VTY ACLs, 802.1Q Native VLAN blackholing.
- **Current Verification Status:** All controls marked `IMPLEMENTED — VALIDATION PENDING` until empirical test execution in Cisco Packet Tracer.
