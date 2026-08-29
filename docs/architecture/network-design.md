# AegisMesh — Private Datacenter Network Design

**Version:** 1.0  
**Date:** 2026-08-28  
**Status:** DRAFT — Awaiting Approval  
**Platform:** Cisco Packet Tracer  
**Traces to:** SR-01, AC-01  

---

## 1. Design Scope

This document specifies the private enterprise datacenter network modeled in Cisco Packet Tracer. The private datacenter represents the on-premises infrastructure of an enterprise that operates a hybrid architecture alongside AWS cloud and Kubernetes workloads.

**Packet Tracer is NOT the entire project.** It represents the network-security portion — specifically, VLAN-based segmentation, ACL enforcement, and inter-zone access control within the enterprise perimeter.

---

## 2. Network Topology

### 2.1 Physical Topology

```
                        ┌──────────────────┐
                        │    INTERNET      │
                        │   (simulated)    │
                        └────────┬─────────┘
                                 │
                        ┌────────┴─────────┐
                        │  EDGE ROUTER     │
                        │  (R-EDGE)        │
                        │  Gateway + NAT   │
                        │  ACL enforcement │
                        └────────┬─────────┘
                                 │
                        ┌────────┴─────────┐
                        │  CORE SWITCH     │
                        │  (SW-CORE)       │
                        │  L3 Switch       │
                        │  Inter-VLAN      │
                        │  Routing         │
                        └────────┬─────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
     ┌────────┴───────┐ ┌───────┴────────┐ ┌───────┴────────┐
     │ ACCESS SWITCH  │ │ ACCESS SWITCH  │ │ ACCESS SWITCH  │
     │  (SW-ACCESS-1) │ │  (SW-ACCESS-2) │ │  (SW-ACCESS-3) │
     │  Faculty +     │ │  App + DB      │ │  Mgmt + Sec    │
     │  DMZ           │ │  Servers       │ │  + Logging     │
     └───────┬────────┘ └───────┬────────┘ └───────┬────────┘
             │                  │                  │
        ┌────┴────┐       ┌────┴────┐        ┌────┴────┐
        │Faculty  │       │App Srv  │        │Mgmt Srv │
        │PCs (3)  │       │(2)      │        │(1)      │
        │         │       │         │        │         │
        │DMZ Srv  │       │DB Srv   │        │Log Srv  │
        │(1)      │       │(2)      │        │(1)      │
        └─────────┘       └─────────┘        └─────────┘
```

### 2.2 Device Inventory

| Device | Hostname | Type | Role |
|---|---|---|---|
| Edge Router | R-EDGE | Cisco 2911 Router | Internet gateway, NAT, inter-site routing, ACL enforcement |
| Core Switch | SW-CORE | Cisco 3560 Multilayer Switch | Inter-VLAN routing, trunk aggregation, core ACLs |
| Access Switch 1 | SW-ACCESS-1 | Cisco 2960 Switch | Faculty + DMZ access ports |
| Access Switch 2 | SW-ACCESS-2 | Cisco 2960 Switch | Application + Database server ports |
| Access Switch 3 | SW-ACCESS-3 | Cisco 2960 Switch | Management + Security/Logging ports |

### 2.3 End Devices

| Device | Hostname | VLAN | IP Address | Purpose |
|---|---|---|---|---|
| Faculty PC 1 | FAC-PC-01 | VLAN 10 | DHCP (10.10.10.x/24) | Faculty workstation |
| Faculty PC 2 | FAC-PC-02 | VLAN 10 | DHCP (10.10.10.x/24) | Faculty workstation |
| Faculty PC 3 | FAC-PC-03 | VLAN 10 | DHCP (10.10.10.x/24) | Faculty workstation |
| App Server 1 | APP-SRV-01 | VLAN 20 | 10.10.20.10/24 | Education application |
| App Server 2 | APP-SRV-02 | VLAN 20 | 10.10.20.11/24 | Research application |
| Management Server | MGMT-SRV-01 | VLAN 30 | 10.10.30.10/24 | Infrastructure management |
| Database Server 1 | DB-SRV-01 | VLAN 40 | 10.10.40.10/24 | Primary database |
| Database Server 2 | DB-SRV-02 | VLAN 40 | 10.10.40.11/24 | Secondary database |
| Security/Log Server | SEC-SRV-01 | VLAN 50 | 10.10.50.10/24 | Wazuh / SIEM |
| DMZ Server | DMZ-SRV-01 | VLAN 60 | 10.10.60.10/24 | Public-facing web server |

---

## 3. VLAN Design

### 3.1 VLAN Assignments

| VLAN ID | Name | Subnet | Gateway | Purpose | Security Level |
|---|---|---|---|---|---|
| 10 | FACULTY | 10.10.10.0/24 | 10.10.10.1 | Faculty user access | LOW |
| 20 | APP-SERVERS | 10.10.20.0/24 | 10.10.20.1 | Application workloads | MEDIUM |
| 30 | MANAGEMENT | 10.10.30.0/24 | 10.10.30.1 | Infrastructure management | HIGH |
| 40 | DATABASE | 10.10.40.0/24 | 10.10.40.1 | Data storage | HIGH |
| 50 | SECURITY | 10.10.50.0/24 | 10.10.50.1 | SIEM, logging | HIGH |
| 60 | DMZ | 10.10.60.0/24 | 10.10.60.1 | Internet-facing services | LOW |
| 99 | NATIVE | — | — | Native VLAN (unused) | — |

### 3.2 Trunk Configuration

All inter-switch links use 802.1Q trunking:

- Native VLAN: 99 (unused, for security)
- Allowed VLANs: 10, 20, 30, 40, 50, 60
- DTP: Disabled (`switchport nonegotiate`)

### 3.3 Access Port Configuration

Each end device port is configured as:
- `switchport mode access`
- `switchport access vlan <VLAN_ID>`
- `switchport port-security` (where supported)
- `spanning-tree portfast`

---

## 4. IP Addressing Scheme

### 4.1 Summary

| Network | Range | Purpose |
|---|---|---|
| 10.10.10.0/24 | Faculty | DHCP pool: .100–.200 |
| 10.10.20.0/24 | Application Servers | Static: .10–.50 |
| 10.10.30.0/24 | Management | Static: .10–.50 |
| 10.10.40.0/24 | Database | Static: .10–.50 |
| 10.10.50.0/24 | Security/Logging | Static: .10–.50 |
| 10.10.60.0/24 | DMZ | Static: .10–.50 |
| 10.10.0.0/24 | Inter-router link | Point-to-point |

### 4.2 DHCP Configuration

DHCP server on SW-CORE for VLAN 10 (Faculty):

```
ip dhcp pool FACULTY
  network 10.10.10.0 255.255.255.0
  default-router 10.10.10.1
  dns-server 10.10.10.1
  
ip dhcp excluded-address 10.10.10.1 10.10.10.99
```

All other VLANs use static addressing for servers.

---

## 5. Routing Design

### 5.1 Inter-VLAN Routing

Performed on SW-CORE using SVIs (Switched Virtual Interfaces):

```
interface Vlan10
  ip address 10.10.10.1 255.255.255.0
  
interface Vlan20
  ip address 10.10.20.1 255.255.255.0
  
interface Vlan30
  ip address 10.10.30.1 255.255.255.0
  
interface Vlan40
  ip address 10.10.40.1 255.255.255.0
  
interface Vlan50
  ip address 10.10.50.1 255.255.255.0
  
interface Vlan60
  ip address 10.10.60.1 255.255.255.0
```

### 5.2 Default Route

SW-CORE has a default route to R-EDGE for internet-bound traffic:

```
ip route 0.0.0.0 0.0.0.0 10.10.0.1
```

R-EDGE has a route back to internal networks:

```
ip route 10.10.0.0 255.255.0.0 10.10.0.2
```

---

## 6. Access Control Lists (ACLs)

### 6.1 ACL Strategy

ACLs are applied on SW-CORE SVI interfaces to control inter-VLAN traffic. This provides centralized, auditable access control.

**Stateless ACL Design Consideration:** Packet Tracer ACLs are stateless — each packet direction is evaluated independently. For bidirectional communication (e.g., Faculty pings App Server), both the request AND the response must pass through their respective ACLs. Therefore, return traffic for authorized flows is explicitly permitted. This does NOT weaken security because unauthorized zone pairs (e.g., Faculty ✗ Database) are blocked in both directions.

### 6.2 ACL Rules

#### ACL: FACULTY-ACCESS (Applied to VLAN 10 SVI, inbound)

| Seq | Action | Source | Destination | Purpose |
|---|---|---|---|---|
| 10 | PERMIT | 10.10.10.0/24 | 10.10.20.0/24 | Faculty → App Servers |
| 20 | PERMIT | 10.10.10.0/24 | 10.10.60.0/24 | Faculty → DMZ |
| 30 | DENY | 10.10.10.0/24 | 10.10.30.0/24 | Faculty → Management BLOCKED |
| 40 | DENY | 10.10.10.0/24 | 10.10.40.0/24 | Faculty → Database BLOCKED |
| 50 | DENY | 10.10.10.0/24 | 10.10.50.0/24 | Faculty → Security BLOCKED |
| 100 | PERMIT | 10.10.10.0/24 | any | Faculty → Internet |

```
ip access-list extended FACULTY-ACCESS
  permit ip 10.10.10.0 0.0.0.255 10.10.20.0 0.0.0.255
  permit ip 10.10.10.0 0.0.0.255 10.10.60.0 0.0.0.255
  deny ip 10.10.10.0 0.0.0.255 10.10.30.0 0.0.0.255
  deny ip 10.10.10.0 0.0.0.255 10.10.40.0 0.0.0.255
  deny ip 10.10.10.0 0.0.0.255 10.10.50.0 0.0.0.255
  permit ip 10.10.10.0 0.0.0.255 any
```

#### ACL: APP-SERVER-ACCESS (Applied to VLAN 20 SVI, inbound)

| Seq | Action | Source | Destination | Purpose |
|---|---|---|---|---|
| 10 | PERMIT | 10.10.20.0/24 | 10.10.40.0/24 | App → Database |
| 20 | PERMIT | 10.10.20.0/24 | 10.10.50.0/24 | App → Logging |
| 30 | PERMIT | 10.10.20.0/24 | 10.10.10.0/24 | App → Faculty (return traffic) |
| 40 | PERMIT | 10.10.20.0/24 | 10.10.60.0/24 | App → DMZ (return traffic) |
| 50 | DENY | 10.10.20.0/24 | 10.10.30.0/24 | App → Management BLOCKED |
| 100 | DENY | any | any | Default deny |

```
ip access-list extended APP-SERVER-ACCESS
  permit ip 10.10.20.0 0.0.0.255 10.10.40.0 0.0.0.255
  permit ip 10.10.20.0 0.0.0.255 10.10.50.0 0.0.0.255
  permit ip 10.10.20.0 0.0.0.255 10.10.10.0 0.0.0.255
  permit ip 10.10.20.0 0.0.0.255 10.10.60.0 0.0.0.255
  deny ip 10.10.20.0 0.0.0.255 10.10.30.0 0.0.0.255
  deny ip any any
```

#### ACL: DMZ-ACCESS (Applied to VLAN 60 SVI, inbound)

| Seq | Action | Source | Destination | Purpose |
|---|---|---|---|---|
| 10 | PERMIT | 10.10.60.0/24 | 10.10.20.0/24 | DMZ → App (reverse proxy) |
| 20 | PERMIT | 10.10.60.0/24 | 10.10.50.0/24 | DMZ → Logging |
| 30 | PERMIT | 10.10.60.0/24 | 10.10.10.0/24 | DMZ → Faculty (stateless return traffic) |
| 40 | DENY | 10.10.60.0/24 | 10.10.40.0/24 | DMZ → Database BLOCKED |
| 50 | DENY | 10.10.60.0/24 | 10.10.30.0/24 | DMZ → Management BLOCKED |
| 100 | DENY | any | any | Default deny |

```
ip access-list extended DMZ-ACCESS
  permit ip 10.10.60.0 0.0.0.255 10.10.20.0 0.0.0.255
  permit ip 10.10.60.0 0.0.0.255 10.10.50.0 0.0.0.255
  permit ip 10.10.60.0 0.0.0.255 10.10.10.0 0.0.0.255
  deny ip 10.10.60.0 0.0.0.255 10.10.40.0 0.0.0.255
  deny ip 10.10.60.0 0.0.0.255 10.10.30.0 0.0.0.255
  deny ip any any
```

#### ACL: MGMT-ACCESS (Applied to VLAN 30 SVI, inbound)

| Seq | Action | Source | Destination | Purpose |
|---|---|---|---|---|
| 10 | PERMIT | 10.10.30.0/24 | 10.10.20.0/24 | Mgmt → App (administration) |
| 20 | PERMIT | 10.10.30.0/24 | 10.10.40.0/24 | Mgmt → Database (administration) |
| 30 | PERMIT | 10.10.30.0/24 | 10.10.50.0/24 | Mgmt → Logging |
| 100 | DENY | any | any | Mgmt → all other BLOCKED |

#### ACL: DB-ACCESS (Applied to VLAN 40 SVI, inbound)

| Seq | Action | Source | Destination | Purpose |
|---|---|---|---|---|
| 10 | PERMIT | 10.10.40.0/24 | 10.10.50.0/24 | DB → Logging |
| 20 | PERMIT | 10.10.40.0/24 | 10.10.20.0/24 | DB → App Servers (return traffic) |
| 30 | PERMIT | 10.10.40.0/24 | 10.10.30.0/24 | DB → Management (return traffic) |
| 100 | DENY | any | any | DB → all other BLOCKED |

#### ACL: SEC-ACCESS (Applied to VLAN 50 SVI, inbound)

| Seq | Action | Source | Destination | Purpose |
|---|---|---|---|---|
| 10 | PERMIT | 10.10.50.0/24 | 10.10.20.0/24 | Security → App Servers (telemetry/polling) |
| 20 | PERMIT | 10.10.50.0/24 | 10.10.40.0/24 | Security → Database Servers (audit/health checks) |
| 30 | PERMIT | 10.10.50.0/24 | 10.10.60.0/24 | Security → DMZ Servers (log collection) |
| 40 | PERMIT | 10.10.50.0/24 | 10.10.30.0/24 | Security → Management (alerts & console) |
| 50 | DENY | 10.10.50.0/24 | 10.10.10.0/24 | Security → Faculty PCs BLOCKED |
| 60 | DENY | 10.10.50.0/24 | any | Security → Internet BLOCKED |
| 100 | DENY | any | any | Default deny |

---

## 7. Security Hardening

### 7.1 Switch Hardening

- Disable unused ports: `shutdown`
- Set unused ports to VLAN 99 (blackhole)
- Enable port security on access ports
- Disable CDP on access ports
- Set native VLAN to 99 (unused)
- Disable DTP: `switchport nonegotiate`
- Enable BPDU guard on access ports
- Set console and VTY passwords
- Enable `enable secret` (type 5 hash)

### 7.2 Router Hardening

- Set `enable secret`
- Configure SSH (version 2) for remote management
- Disable Telnet on VTY lines
- Apply ACL to VTY lines (management VLAN only)
- Disable unused services: `no ip http server`, `no cdp run` on external interfaces
- Configure logging to Security VLAN

---

## 8. Inter-VLAN Traffic Matrix

| Source ↓ / Dest → | VLAN 10 | VLAN 20 | VLAN 30 | VLAN 40 | VLAN 50 | VLAN 60 |
|---|---|---|---|---|---|---|
| **VLAN 10 (Faculty)** | — | ✅ ALLOW | ❌ BLOCK | ❌ BLOCK | ❌ BLOCK | ✅ ALLOW |
| **VLAN 20 (App)** | ❌ BLOCK | — | ❌ BLOCK | ✅ ALLOW | ✅ ALLOW | ❌ BLOCK |
| **VLAN 30 (Mgmt)** | ❌ BLOCK | ⚠️ NOTE | — | ✅ ALLOW | ✅ ALLOW | ❌ BLOCK |
| **VLAN 40 (DB)** | ❌ BLOCK | ❌ BLOCK | ❌ BLOCK | — | ✅ ALLOW | ❌ BLOCK |
| **VLAN 50 (Security)** | ❌ BLOCK | ✅ ALLOW | ✅ ALLOW | ✅ ALLOW | — | ✅ ALLOW |
| **VLAN 60 (DMZ)** | ❌ BLOCK | ✅ ALLOW | ❌ BLOCK | ❌ BLOCK | ✅ ALLOW | — |

**Notes:**

1. **Traffic Matrix Semantics:** This matrix represents authorized **initiated** communication flows, not individual stateless ACL rule directions. Where an initiated flow is authorized, corresponding return traffic may require an explicit reverse-direction ACL rule due to the stateless nature of Cisco Packet Tracer ACLs.

2. **Security VLAN (50):** Has selective monitoring access to App (20), DB (40), DMZ (60), and Management (30) for SIEM telemetry and log aggregation. Does NOT have access to Faculty (10) — the hardened SEC-ACCESS ACL explicitly denies Security→Faculty as a least-privilege control.

3. **Mgmt → App (⚠️ NOTE):** `MGMT-ACCESS` permits 30→20, but the corresponding return path (20→30) is blocked by `APP-SERVER-ACCESS` which explicitly denies App→Mgmt to enforce threat E-02 (lateral movement prevention). Since Packet Tracer ACLs are stateless and cannot distinguish initiated vs. return traffic, enabling the return path would also enable the attack path. **Design decision: E-02 security control is preserved; Mgmt→App bidirectional communication is a known stateless ACL limitation.** In a production environment with stateful ACLs, this flow would work correctly.

---

## 9. Packet Tracer Testing Plan

| Test ID | Source | Destination | Method | Expected | Verifies |
|---|---|---|---|---|---|
| PT-01 | FAC-PC-01 (VLAN 10) | APP-SRV-01 (VLAN 20) | Ping + HTTP | ✅ ALLOW | Faculty → App |
| PT-02 | FAC-PC-01 (VLAN 10) | DB-SRV-01 (VLAN 40) | Ping | ❌ BLOCK | Faculty ✗ Database |
| PT-03 | FAC-PC-01 (VLAN 10) | MGMT-SRV-01 (VLAN 30) | Ping | ❌ BLOCK | Faculty ✗ Management |
| PT-04 | APP-SRV-01 (VLAN 20) | DB-SRV-01 (VLAN 40) | Ping + TCP | ✅ ALLOW | App → Database |
| PT-05 | APP-SRV-01 (VLAN 20) | MGMT-SRV-01 (VLAN 30) | Ping | ❌ BLOCK | App ✗ Management |
| PT-06 | DMZ-SRV-01 (VLAN 60) | DB-SRV-01 (VLAN 40) | Ping | ❌ BLOCK | DMZ ✗ Database |
| PT-07 | DMZ-SRV-01 (VLAN 60) | MGMT-SRV-01 (VLAN 30) | Ping | ❌ BLOCK | DMZ ✗ Management |
| PT-08 | DMZ-SRV-01 (VLAN 60) | APP-SRV-01 (VLAN 20) | Ping + HTTP | ✅ ALLOW | DMZ → App |
| PT-09 | DB-SRV-01 (VLAN 40) | FAC-PC-01 (VLAN 10) | Ping | ❌ BLOCK | DB ✗ Faculty |
| PT-10 | FAC-PC-01 (VLAN 10) | DHCP | DHCP Request | ✅ ALLOW | DHCP functional |

### Verification Commands

```
show vlan brief
show ip interface brief
show ip route
show access-lists
show running-config
show interfaces trunk
show port-security
```

---

## 10. Packet Tracer File Deliverables

| File | Description |
|---|---|
| `topology.pkt` | Complete Packet Tracer topology with all devices configured |
| `configurations/R-EDGE.txt` | Edge router running configuration |
| `configurations/SW-CORE.txt` | Core switch running configuration |
| `configurations/SW-ACCESS-1.txt` | Access switch 1 running configuration |
| `configurations/SW-ACCESS-2.txt` | Access switch 2 running configuration |
| `configurations/SW-ACCESS-3.txt` | Access switch 3 running configuration |
| `test-results/test-report.md` | Documented test results with screenshots |
