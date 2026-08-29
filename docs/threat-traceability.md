# AegisMesh — Threat Traceability Matrix

**Date:** 2026-08-29  
**Version:** 1.4 (Authoritative Final)  
**Methodology:** STRIDE Model Cross-Mapping  
**Source of Truth:** `docs/architecture/threat-model.md`  
**Traces to:** `docs/requirements/requirements.md`, `packet-tracer/test-results/test-matrix.md`, `docs/security-control-traceability.md`  

---

## 1. Canonical Threat Identification

The threat traceability model uses `docs/architecture/threat-model.md` as the authoritative source for canonical threat identifiers.

Each threat must have exactly one canonical identifier. Duplicate numbering systems and combined identifiers are prohibited.

**Packet Tracer Scope Limitation:** Canonical threat `I-01` ("Compromised education app reads finance database") targets AWS VPC and Kubernetes trust boundaries (TB-6, TB-7) and is outside the scope of Cisco Packet Tracer network validation. It is not re-mapped or repurposed within this traceability matrix. Private datacenter scenarios that resemble I-01's data-access pattern are documented as architectural validation scenarios (`ARCH-SCENARIO-02`).

The traceability model distinguishes between different enforcement layers:

1. **VLAN Hopping (Layer 2):**
   Exploits trunk encapsulation, DTP auto-negotiation, or 802.1Q double-tagging to access unauthorized VLANs. Mitigated through trunk hardening, a dedicated unused native VLAN, explicit trunk VLAN restrictions, and DTP disabling.

2. **Cross-Zone Lateral Movement (Layer 3):**
   Attempts to exploit inter-VLAN routing paths to reach unauthorized security zones. Mitigated through SVI ingress extended ACLs using explicit least-privilege rules and restrictive default-deny behavior.

3. **Precise Network Control Scoping:**
   Network ACLs are documented strictly as Layer 3/4 packet filtering controls that restrict network reachability. They do not claim application-layer mitigations such as SQL injection prevention, credential compromise prevention, or cryptographic non-repudiation.

4. **Logging Infrastructure Protection Scope:**
   VLAN 50 isolation provides network-level segregation and controlled access paths to centralized logging infrastructure. It is not represented as independently providing immutable, tamper-proof, or cryptographically protected audit logs.

5. **Architectural Validation Scenarios:**
   Inter-VLAN security scenarios required by SR-05 but not explicitly assigned a canonical identifier in the base threat model are documented using the `ARCH-SCENARIO-XX` namespace. These scenarios are clearly identified as architectural validation scenarios rather than canonical STRIDE threats.


---

## 2. Authoritative Threat Traceability Matrix

| Threat ID | Threat Scenario | Security Requirement | Security Control | Implementation Artifact | Test Cases | Evidence | Verification Status |
|---|---|---|---|---|---|---|---|
| **S-03** | **VLAN Hopping via Trunk Port Misconfiguration:** Threat actor attempts unauthorized VLAN access through trunk misconfiguration, DTP negotiation, or 802.1Q double-tagging. | SR-01 | Layer 2 Trunk Hardening & Dedicated Native VLAN Isolation | `SW-CORE.txt`, `SW-ACCESS-1..3.txt` (unused Native VLAN 99, `switchport nonegotiate`, explicit trunk allowed VLAN list) | `show interfaces trunk`, trunk configuration verification | PENDING EXECUTION | IMPLEMENTED — VALIDATION PENDING |
| **T-02** | **Unauthorized Network Device Administration / Configuration Alteration:** Threat actor from a non-management network attempts SSH or Telnet access to network infrastructure to modify security controls. | SR-01, SR-05 | Management Zone Isolation & VTY Access-Class Restriction | `R-EDGE.txt`, `SW-CORE.txt`, `SW-ACCESS-1..3.txt` (`access-class MGMT-VTY-ACCESS in`, SSH v2 only, Telnet disabled) | PT-MGMT-01A, PT-MGMT-01B, SSH access attempt from VLAN 10 vs VLAN 30 | PENDING EXECUTION | IMPLEMENTED — VALIDATION PENDING |
| **R-02** | **Unauthorized Network Interference with Centralized Logging Infrastructure:** Compromised workload attempts unauthorized network access or disruption against centralized logging infrastructure. | SR-01, NFR-03 | Dedicated Security/Logging VLAN Isolation & Controlled Log Forwarding | `SW-CORE.txt` (`SEC-ACCESS`; restricted log forwarding rules from authorized zones) | PT-14, PT-15, PT-16, logging configuration verification | PENDING EXECUTION | IMPLEMENTED — VALIDATION PENDING |
| **ARCH-SCENARIO-02** | **DMZ-to-Database Unauthorized Network Reachability:** Compromised public-facing DMZ workload attempts direct network connectivity or reconnaissance toward protected database resources. *(Note: This is an architectural private-datacenter network boundary validation scenario under SR-05. It is not the same scenario as canonical threat I-01 in threat-model.md, which targets AWS/Kubernetes cross-domain data access at TB-6/TB-7.)* | SR-01, SR-05 | DMZ Boundary Filtering via `DMZ-ACCESS` Extended ACL | `SW-CORE.txt` (restricted DMZ-to-Database access rules on SVI Vlan60) | PT-06, PT-LM-03 | PENDING EXECUTION | IMPLEMENTED — VALIDATION PENDING |
| **D-03** | **Unauthorized Cross-Zone Reconnaissance and Excessive Routed Traffic:** Rogue host attempts unauthorized subnet discovery, repeated connection attempts, or excessive routed traffic toward protected datacenter zones. | SR-01 | Restrictive SVI Ingress Filtering & Least-Privilege ACL Rules | `SW-CORE.txt` (SVI ACLs with explicit permitted flows and restrictive termination) | PT-12, PT-16, PT-17 | PENDING EXECUTION | IMPLEMENTED — VALIDATION PENDING |
| **E-02** | **Application Server Compromise Leading to Management Pivot:** Compromised application workload attempts lateral network traversal toward management servers or network administration interfaces. | SR-05 | Application Tier Lateral Movement Restriction via `APP-SERVER-ACCESS` | `SW-CORE.txt` (VLAN 20 → VLAN 30 restricted) | PT-05, PT-LM-02 | PENDING EXECUTION | IMPLEMENTED — VALIDATION PENDING |
| **E-04** | **Direct Database Access by Unauthorized End-Users:** Faculty workstation attempts direct database network connectivity, bypassing the intended application tier. | SR-01, SR-05 | Faculty Zone Boundary Filtering via `FACULTY-ACCESS` | `SW-CORE.txt` (VLAN 10 → VLAN 40 restricted) | PT-02, PT-09 | PENDING EXECUTION | IMPLEMENTED — VALIDATION PENDING |
| **ARCH-SCENARIO-01** | **Database Reverse Pivot Toward User Workstation Subnet:** Compromised database workload attempts to initiate unauthorized network connectivity toward the Faculty client zone. This is an architectural validation scenario under SR-05 and is a candidate for future formal inclusion in the threat model. | SR-05 | Database Tier Egress Boundary Restriction via `DB-ACCESS` | `SW-CORE.txt` (DB ACL permits only explicitly required flows and restricts unauthorized destinations) | PT-09, PT-LM-05 | PENDING EXECUTION | IMPLEMENTED — VALIDATION PENDING |

---

## 3. Threat Traceability Summary

- **Canonical Threat Scope:** 6 canonical threat-model scenarios (`S-03`, `T-02`, `R-02`, `D-03`, `E-02`, `E-04`) are mapped directly to security requirements, controls, implementation artifacts, and validation tests. Canonical threat `I-01` is outside Packet Tracer private datacenter scope (it targets AWS/Kubernetes trust boundaries TB-6/TB-7).
- **Architectural Validation Scope:** 2 architectural validation scenarios are documented: `ARCH-SCENARIO-01` (Database reverse pivot toward Faculty) and `ARCH-SCENARIO-02` (DMZ-to-Database unauthorized reachability).
- **Security Controls:** Layer 2 trunk hardening, six SVI ingress ACL boundaries, management-plane VTY restrictions, and dedicated Security/Logging zone isolation.
- **Enforcement Layers:** Cisco IOS Layer 2 switchport configuration, Layer 3 SVI extended ACL enforcement, and VTY management access restrictions.
- **Evidence Status:** All controls are currently `IMPLEMENTED — VALIDATION PENDING`.
- **Verification Rule:** No control is considered TESTED or VERIFIED until corresponding Packet Tracer execution evidence has been collected and recorded.
- **Control Scope:** Network controls are evaluated only against the network-layer security properties they actually enforce. Application-layer and software-level security claims are outside the scope of Packet Tracer ACL validation.
