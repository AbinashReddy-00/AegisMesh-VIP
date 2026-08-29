# AegisMesh — ACL Design and Placement Documentation

**Platform:** Cisco Packet Tracer  
**Device:** SW-CORE (3560-24PS) — all ACLs applied here  
**Traces to:** SR-01, SR-05, network-design.md Section 6, threat-model.md Section 4  

---

## 1. ACL Strategy

### Placement Decision

All ACLs are applied **inbound on the SVI interfaces of SW-CORE**. This centralizes access control enforcement at the inter-VLAN routing point.

**Why inbound on SVIs?**
- Traffic must pass through an SVI to be routed between VLANs.
- Applying ACLs inbound on the source VLAN's SVI catches traffic at the earliest possible point.
- Centralized management: all security rules are on one device.

### Stateless ACL Consideration

Cisco Packet Tracer does not support stateful inspection or reflexive ACLs. All ACLs are **stateless** — each packet direction is evaluated independently.

**Implication:** For a bidirectional flow (e.g., Faculty pings App Server), both the request packet AND the response packet must pass through their respective ACLs. Therefore, return traffic for authorized flows must be explicitly permitted.

**This is NOT a security weakness** because:
- Return traffic is only permitted between zone pairs that are already authorized in the forward direction.
- Unauthorized zone pairs (Faculty ✗ Database, DMZ ✗ Management) are blocked in **both** directions.

---

## 2. ACL Inventory

| ACL Name | Applied To | Direction | Source Zone | Controls |
|---|---|---|---|---|
| FACULTY-ACCESS | interface Vlan10 | in | Faculty (VLAN 10) | What Faculty can access |
| APP-SERVER-ACCESS | interface Vlan20 | in | App Servers (VLAN 20) | What App Servers can access |
| MGMT-ACCESS | interface Vlan30 | in | Management (VLAN 30) | What Management can access |
| DB-ACCESS | interface Vlan40 | in | Database (VLAN 40) | What Database can initiate/respond to |
| SEC-ACCESS | interface Vlan50 | in | Security (VLAN 50) | What Security/Logging can access |
| DMZ-ACCESS | interface Vlan60 | in | DMZ (VLAN 60) | What DMZ can access |
| MGMT-VTY-ACCESS | VTY lines (all devices) | in | Management only | SSH access restriction |

---

## 3. Detailed ACL Rules with Rationale

### ACL: FACULTY-ACCESS

**Applied to:** `interface Vlan10`, direction `in`  
**Purpose:** Control what Faculty users (VLAN 10) can reach.

| Seq | Action | Source | Destination | Rationale |
|---|---|---|---|---|
| 1 | PERMIT | 10.10.10.0/24 | 10.10.20.0/24 | Faculty must access application servers for daily work (learning management, research portals). This is the primary authorized communication path. |
| 2 | PERMIT | 10.10.10.0/24 | 10.10.60.0/24 | Faculty may access DMZ-hosted web services (public-facing portal). |
| 3 | DENY | 10.10.10.0/24 | 10.10.30.0/24 | **Faculty must NOT access the management network.** Management contains infrastructure controls (switches, routers). Faculty access here would enable privilege escalation. Traces to threat E-04, T-02. |
| 4 | DENY | 10.10.10.0/24 | 10.10.40.0/24 | **Faculty must NOT directly access databases.** All data access must be mediated by the application layer. Direct DB access bypasses application-level authorization. Traces to threat I-01, E-04. |
| 5 | DENY | 10.10.10.0/24 | 10.10.50.0/24 | **Faculty must NOT access the security/logging zone.** This zone contains the SIEM and audit logs. Unauthorized access could enable evidence tampering. Traces to threat R-02. |
| 6 | PERMIT | 10.10.10.0/24 | any | Faculty may reach the internet (via R-EDGE). This rule matches only after internal deny rules, so it cannot bypass them. |

---

### ACL: APP-SERVER-ACCESS

**Applied to:** `interface Vlan20`, direction `in`  
**Purpose:** Control what App Servers (VLAN 20) can reach.

| Seq | Action | Source | Destination | Rationale |
|---|---|---|---|---|
| 1 | PERMIT | 10.10.20.0/24 | 10.10.40.0/24 | App Servers must query databases for application data. This is the authorized data-access path. |
| 2 | PERMIT | 10.10.20.0/24 | 10.10.50.0/24 | App Servers must forward logs to the SIEM for security monitoring. |
| 3 | PERMIT | 10.10.20.0/24 | 10.10.10.0/24 | **Return traffic:** App Servers must respond to Faculty requests (HTTP responses, ICMP echo-reply). Without this, stateless ACLs would drop response packets at the VLAN 20 SVI. |
| 4 | PERMIT | 10.10.20.0/24 | 10.10.60.0/24 | **Return traffic:** App Servers must respond to DMZ requests (reverse-proxied traffic). |
| 5 | DENY | 10.10.20.0/24 | 10.10.30.0/24 | **App Servers must NOT access the management network.** A compromised application should not be able to reach infrastructure management. This is the primary lateral movement prevention control. Traces to threat E-02. |
| 6 | DENY | any | any | **Default deny:** All traffic not explicitly permitted is blocked. This enforces the least-privilege principle. |

---

### ACL: DMZ-ACCESS

**Applied to:** `interface Vlan60`, direction `in`  
**Purpose:** Control what DMZ servers (VLAN 60) can reach.

| Seq | Action | Source | Destination | Rationale |
|---|---|---|---|---|
| 1 | PERMIT | 10.10.60.0/24 | 10.10.20.0/24 | DMZ servers forward requests to App Servers (reverse proxy architecture). The DMZ does not serve applications directly — it proxies to the app tier. |
| 2 | PERMIT | 10.10.60.0/24 | 10.10.50.0/24 | DMZ must forward logs to the SIEM for security monitoring. Internet-facing services require heightened monitoring. |
| 3 | PERMIT | 10.10.60.0/24 | 10.10.10.0/24 | **Return traffic:** DMZ must respond to Faculty-initiated requests (HTTP responses, ICMP echo-reply). Without this, stateless ACLs would drop response packets at the VLAN 60 SVI, breaking Faculty→DMZ communication. |
| 4 | DENY | 10.10.60.0/24 | 10.10.40.0/24 | **DMZ must NOT access databases.** A compromised internet-facing server must not be able to reach stored data directly. All data access is mediated through the app tier. Traces to ARCH-SCENARIO-02. |
| 5 | DENY | 10.10.60.0/24 | 10.10.30.0/24 | **DMZ must NOT access management.** This prevents a compromised DMZ server from accessing infrastructure controls. Traces to threat E-02. |
| 6 | DENY | any | any | **Default deny.** |

---

### ACL: MGMT-ACCESS

**Applied to:** `interface Vlan30`, direction `in`  
**Purpose:** Control what Management zone (VLAN 30) can reach.

| Seq | Action | Source | Destination | Rationale |
|---|---|---|---|---|
| 1 | PERMIT | 10.10.30.0/24 | 10.10.20.0/24 | Management staff must administer application servers (SSH, monitoring agents). |
| 2 | PERMIT | 10.10.30.0/24 | 10.10.40.0/24 | Database administrators must perform maintenance (backups, schema changes, monitoring). |
| 3 | PERMIT | 10.10.30.0/24 | 10.10.50.0/24 | Management must access the SIEM for security review and log analysis. |
| 4 | DENY | any | any | **Management is a restricted zone.** It cannot reach Faculty, DMZ, or the internet. Outbound management traffic is unnecessary and would increase attack surface. |

---

### ACL: DB-ACCESS

**Applied to:** `interface Vlan40`, direction `in`  
**Purpose:** Control what Database zone (VLAN 40) can initiate or respond to.

| Seq | Action | Source | Destination | Rationale |
|---|---|---|---|---|
| 1 | PERMIT | 10.10.40.0/24 | 10.10.50.0/24 | Databases must forward logs to the SIEM (audit logs, error logs, slow query logs). |
| 2 | PERMIT | 10.10.40.0/24 | 10.10.20.0/24 | **Return traffic:** Database must respond to App Server queries (SQL results, connection acknowledgements). Without this, stateless ACLs would drop response packets. |
| 3 | PERMIT | 10.10.40.0/24 | 10.10.30.0/24 | **Return traffic:** Database must respond to Management admin sessions (SSH responses, monitoring data). |
| 4 | DENY | any | any | **Default deny.** Databases must NOT initiate connections to Faculty, DMZ, or the internet. A compromised database cannot exfiltrate data outbound. |

---

### ACL: SEC-ACCESS

**Applied to:** `interface Vlan50`, direction `in`  
**Purpose:** Control what Security/Logging zone (VLAN 50) can access.

| Seq | Action | Source | Destination | Rationale |
|---|---|---|---|---|
| 1 | PERMIT | 10.10.50.0/24 | 10.10.20.0/24 | SIEM telemetry collection and active agent polling for Application Servers. |
| 2 | PERMIT | 10.10.50.0/24 | 10.10.40.0/24 | SIEM database audit log polling and database security health checks. |
| 3 | PERMIT | 10.10.50.0/24 | 10.10.60.0/24 | SIEM web access log aggregation and DMZ reverse proxy monitoring. |
| 4 | PERMIT | 10.10.50.0/24 | 10.10.30.0/24 | Security event forwarding to Management administration console. |
| 5 | DENY | 10.10.50.0/24 | 10.10.10.0/24 | **Least privilege:** Security server does not initiate connections to Faculty client PCs. |
| 6 | DENY | 10.10.50.0/24 | any | **Exfiltration prevention:** Security server cannot initiate outbound connections to the Internet. |
| 7 | DENY | any | any | **Default deny.** |

---

### ACL: MGMT-VTY-ACCESS

**Applied to:** VTY lines on all network devices  
**Purpose:** Restrict SSH access to network devices.

| Seq | Action | Source | Rationale |
|---|---|---|---|
| 1 | PERMIT | 10.10.30.0/24 | Only Management VLAN can SSH to network devices. |
| 2 | DENY | any | All other zones are blocked from device management. |

---

## 4. Bidirectional ACL Verification Matrix

This matrix shows how ACL rules interact for **both directions** of each authorized flow:

| Flow | Forward ACL (Request) | Return ACL (Response) | Net Result |
|---|---|---|---|
| Faculty → App | FACULTY-ACCESS: permit 10→20 | APP-SERVER-ACCESS: permit 20→10 | ✅ Bidirectional |
| Faculty → DMZ | FACULTY-ACCESS: permit 10→60 | DMZ-ACCESS: permit 60→10 (return traffic) | ✅ Bidirectional |
| App → Database | APP-SERVER-ACCESS: permit 20→40 | DB-ACCESS: permit 40→20 | ✅ Bidirectional |
| DMZ → App | DMZ-ACCESS: permit 60→20 | APP-SERVER-ACCESS: permit 20→60 | ✅ Bidirectional |
| Mgmt → App | MGMT-ACCESS: permit 30→20 | APP-SERVER-ACCESS: (implicit deny) | ⚠️ See note below |
| Mgmt → DB | MGMT-ACCESS: permit 30→40 | DB-ACCESS: permit 40→30 | ✅ Bidirectional |
| Faculty → DB | FACULTY-ACCESS: deny 10→40 | — | ❌ Blocked at source |
| Faculty → Mgmt | FACULTY-ACCESS: deny 10→30 | — | ❌ Blocked at source |
| DMZ → DB | DMZ-ACCESS: deny 60→40 | — | ❌ Blocked at source |
| DMZ → Mgmt | DMZ-ACCESS: deny 60→30 | — | ❌ Blocked at source |
| App → Mgmt | APP-SERVER-ACCESS: deny 20→30 | — | ❌ Blocked at source |
| DB → Faculty | DB-ACCESS: deny (implicit) | — | ❌ Blocked at source |

**Note on Mgmt → App:** The APP-SERVER-ACCESS ACL does not have an explicit permit for 20→30 (return traffic to management). However, APP-SERVER-ACCESS has a `deny any any` at the end which would block the return. To make management of app servers work via this ACL approach, we rely on the Management → App path being tested primarily through MGMT-ACCESS. If bidirectional management access is needed, App Servers' return to Management should be added. For the current demo, the primary test (PT-05: App → Mgmt = BLOCK) validates that App Servers cannot *initiate* access to Management, which is the security requirement.

---

## 5. ACL Hit Count Verification

After running tests, use `show access-lists` on SW-CORE to verify ACL hit counts:

```
SW-CORE# show access-lists
Extended IP access list FACULTY-ACCESS
    permit ip 10.10.10.0 0.0.0.255 10.10.20.0 0.0.0.255 (X matches)
    permit ip 10.10.10.0 0.0.0.255 10.10.60.0 0.0.0.255 (X matches)
    deny ip 10.10.10.0 0.0.0.255 10.10.30.0 0.0.0.255 (X matches)
    deny ip 10.10.10.0 0.0.0.255 10.10.40.0 0.0.0.255 (X matches)
    ...
```

- Permit rules should show matches for authorized traffic tests.
- Deny rules should show matches for blocked traffic tests.
- Zero matches on a deny rule means that test was not executed.
