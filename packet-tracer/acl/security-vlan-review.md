# Security VLAN (VLAN 50) Access Review & Least-Privilege Proposal

**Date:** 2026-08-29  
**Scope:** SW-CORE Access Control List for VLAN 50 (Security / SIEM / Logging)  
**Traces to:** NFR-02 (Least Privilege), SR-01, threat-model.md Section 4 (STRIDE)

---

## 1. Context & Problem Statement

In the initial SW-CORE configuration, the ACL `SEC-ACCESS` applied to `interface Vlan50` was configured as:

```cisco
ip access-list extended SEC-ACCESS
 remark --- PERMIT: Security to all (monitoring requires visibility) ---
 permit ip 10.10.50.0 0.0.0.255 any
```

### Prompt Review Questions:
1. **Why does the Security VLAN need broad access?**
   - Active SIEM monitoring, syslog/agent polling, remote vulnerability scanning, and alert correlation traditionally communicate with managed hosts across all subnets.
2. **What monitoring traffic actually requires it?**
   - In a production SIEM/Wazuh setup: Syslog ingestion (UDP/TCP 514), Wazuh agent communication (TCP 1514/1515), SNMP polling (UDP 161), and API/SSH auditing.
3. **Does `permit ip any any` from VLAN 50 create an unnecessary lateral movement path?**
   - **YES.** If the Security server (`SEC-SRV-01`) is compromised, an attacker would have unrestricted IP access to:
     - Management VLAN 30 (`10.10.30.0/24`)
     - Database VLAN 40 (`10.10.40.0/24`)
     - Internet (`0.0.0.0/0`) for command & control (C2) / exfiltration
4. **Does it conflict with default-deny?**
   - Yes. A blanket `permit ip ... any` violates strict zero-trust least privilege.

---

## 2. Least-Privilege Alternative (Hardened Proposal)

Instead of unrestricted IP routing, we can restrict VLAN 50 outbound traffic to strictly monitoring-relevant subnets and block outbound internet from the Security server.

### Proposed Refined ACL: `SEC-ACCESS-STRICT`

```cisco
ip access-list extended SEC-ACCESS
 remark --- PERMIT: SIEM/Monitoring to App Servers (Agent & Log Queries) ---
 permit ip 10.10.50.0 0.0.0.255 10.10.20.0 0.0.0.255
 remark --- PERMIT: SIEM/Monitoring to Database Servers (Audit & DB Logs) ---
 permit ip 10.10.50.0 0.0.0.255 10.10.40.0 0.0.0.255
 remark --- PERMIT: SIEM/Monitoring to DMZ Servers (Agent & Web Logs) ---
 permit ip 10.10.50.0 0.0.0.255 10.10.60.0 0.0.0.255
 remark --- PERMIT: SIEM/Monitoring to Management VLAN (SIEM Console & Admin Access) ---
 permit ip 10.10.50.0 0.0.0.255 10.10.30.0 0.0.0.255
 remark --- DENY: Security to Faculty Workstations (No direct push to client workstations) ---
 deny ip 10.10.50.0 0.0.0.255 10.10.10.0 0.0.0.255 log
 remark --- DENY: Security to External Internet (Prevent C2 / Exfiltration from SIEM) ---
 deny ip 10.10.50.0 0.0.0.255 any log
 remark --- DENY: Default Deny ---
 deny ip any any
```

---

## 3. Comparison & Impact Assessment

| Dimension | Original `permit ip any` | Hardened `SEC-ACCESS` (Proposed) |
|---|---|---|
| **Monitoring Capability** | Unrestricted across all zones | Permits reachability to App, DB, DMZ, and Mgmt |
| **Faculty PC Protection** | Vulnerable if SIEM compromised | **Blocked** (Faculty clients do not receive inbound connections from SIEM) |
| **Exfiltration / C2 Risk** | SIEM can initiate outbound Internet traffic | **Blocked** (SIEM cannot initiate traffic to 0.0.0.0/0) |
| **Compliance with Least Privilege** | Low | High |

---

## 4. Recommendation

Adopt the hardened `SEC-ACCESS` definition on `SW-CORE` to maintain strict adherence to zero-trust principles without degrading log aggregation capabilities.
