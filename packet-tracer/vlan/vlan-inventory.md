# AegisMesh — VLAN Inventory

**Platform:** Cisco Packet Tracer  
**Device:** SW-CORE (3560-24PS) — authoritative VLAN source  
**Traces to:** SR-01, network-design.md Section 3  

---

## VLAN Assignments

| VLAN ID | Name | Subnet | Gateway | Purpose | Security Level | Assigned Interfaces |
|---|---|---|---|---|---|---|
| 10 | FACULTY | 10.10.10.0/24 | 10.10.10.1 | Faculty user workstations | LOW | SW-ACCESS-1: Fa0/1, Fa0/2, Fa0/3 |
| 20 | APP-SERVERS | 10.10.20.0/24 | 10.10.20.1 | Application servers (Education, Research) | MEDIUM | SW-ACCESS-2: Fa0/1, Fa0/2 |
| 30 | MANAGEMENT | 10.10.30.0/24 | 10.10.30.1 | Infrastructure management console | HIGH | SW-ACCESS-3: Fa0/1 |
| 40 | DATABASE | 10.10.40.0/24 | 10.10.40.1 | Database servers (primary, secondary) | HIGH | SW-ACCESS-2: Fa0/3, Fa0/4 |
| 50 | SECURITY | 10.10.50.0/24 | 10.10.50.1 | SIEM, security logging, Wazuh | HIGH | SW-ACCESS-3: Fa0/2 |
| 60 | DMZ | 10.10.60.0/24 | 10.10.60.1 | Internet-facing web services | LOW | SW-ACCESS-1: Fa0/10 |
| 99 | NATIVE-UNUSED | — | — | Trunk native VLAN (unused for security) | — | All trunk links |

---

## VLAN Security Classification

### LOW Security (VLANs 10, 60)

- **Faculty (10):** End-user workstations. Users can access application servers and DMZ. Cannot access management, database, or security zones.
- **DMZ (60):** Internet-facing services. Can reach application servers (reverse proxy pattern) and logging. Cannot access any internal high-security zone.

### MEDIUM Security (VLAN 20)

- **App Servers (20):** Application workloads. Can access databases (data queries) and logging. Can respond to Faculty and DMZ requests. Cannot access management zone.

### HIGH Security (VLANs 30, 40, 50)

- **Management (30):** Infrastructure admin access only. Can reach App Servers, Databases, and Logging for administration. Cannot be reached from Faculty, DMZ, or App zones.
- **Database (40):** Data storage. Only accepts connections from App Servers and Management. Cannot initiate outbound connections except to logging.
- **Security (50):** SIEM and log collection. Has broad access to all zones for monitoring purposes. This is by design — a SIEM must observe all zones to be effective.

---

## VLAN Verification

### Expected output: `show vlan brief` on SW-CORE

```
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    
10   FACULTY                          active    
20   APP-SERVERS                      active    
30   MANAGEMENT                       active    
40   DATABASE                         active    
50   SECURITY                         active    
60   DMZ                              active    
99   NATIVE-UNUSED                    active    
```

### Expected output: `show vlan brief` on SW-ACCESS-1

```
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    
10   FACULTY                          active    Fa0/1, Fa0/2, Fa0/3
20   APP-SERVERS                      active    
30   MANAGEMENT                       active    
40   DATABASE                         active    
50   SECURITY                         active    
60   DMZ                              active    Fa0/10
99   NATIVE-UNUSED                    active    Fa0/4-9, Fa0/11-23
```

### Expected output: `show vlan brief` on SW-ACCESS-2

```
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    
10   FACULTY                          active    
20   APP-SERVERS                      active    Fa0/1, Fa0/2
30   MANAGEMENT                       active    
40   DATABASE                         active    Fa0/3, Fa0/4
50   SECURITY                         active    
60   DMZ                              active    
99   NATIVE-UNUSED                    active    Fa0/5-23
```

### Expected output: `show vlan brief` on SW-ACCESS-3

```
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    
10   FACULTY                          active    
20   APP-SERVERS                      active    
30   MANAGEMENT                       active    Fa0/1
40   DATABASE                         active    
50   SECURITY                         active    Fa0/2
60   DMZ                              active    
99   NATIVE-UNUSED                    active    Fa0/3-23
```

---

## Trunk Verification

### Expected output: `show interfaces trunk` on SW-CORE

```
Port        Mode         Encapsulation  Status        Native vlan
Fa0/1       on           802.1q         trunking      99
Fa0/2       on           802.1q         trunking      99
Fa0/3       on           802.1q         trunking      99

Port        Vlans allowed on trunk
Fa0/1       10,20,30,40,50,60
Fa0/2       10,20,30,40,50,60
Fa0/3       10,20,30,40,50,60
```

---

## Security Design Rationale

| Security Principle | VLAN Implementation |
|---|---|
| **Network Segmentation** | 6 VLANs create logical security zones |
| **Least Privilege** | Each VLAN only permits explicitly authorized traffic via ACLs |
| **Defense in Depth** | VLAN isolation + ACL enforcement + trunk restrictions |
| **Management Isolation** | VLAN 30 is unreachable from VLANs 10, 20, 60 |
| **Database Protection** | VLAN 40 is accessible only from VLANs 20 (app) and 30 (admin) |
| **DMZ Isolation** | VLAN 60 can reach VLAN 20 (app tier) but not sensitive zones |
| **Native VLAN Security** | VLAN 99 is unused — prevents VLAN hopping via native VLAN |
| **Unused Port Security** | All unused ports assigned to VLAN 99 and shut down |
