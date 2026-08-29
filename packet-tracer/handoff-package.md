# AegisMesh — Cisco Packet Tracer Teammate Handoff Package

**Project:** AegisMesh — Secure Hybrid Datacenter & Cloud Security Architecture  
**Document Type:** Turnkey Execution Guide for Network Modeling & Testing  
**Target Platform:** Cisco Packet Tracer 8.2+ (Desktop GUI)  
**Estimated Completion Time:** 45–60 minutes  
**Authoritative Baseline:** Audited & Frozen Architecture (Zero External Decisions Required)  

---

## 1. Mission Overview

Welcome! Your objective is to build, configure, test, and collect verification evidence for the **AegisMesh Private Enterprise Datacenter** in Cisco Packet Tracer.

This network represents the on-premises datacenter segment of a zero-trust enterprise security architecture, featuring:
- **6 Segmented VLANs** (Faculty, App Servers, Management, Database, Security/SIEM, DMZ).
- **802.1Q Hardened Trunks** with dedicated Native VLAN 99.
- **Inter-VLAN Routing** via Layer 3 Switch Virtual Interfaces (SVIs).
- **Ingress Stateless Extended Access Control Lists (ACLs)** enforcing least-privilege boundaries and lateral movement prevention.
- **Dedicated Management & Security Isolation** restricting infrastructure VTY administration and protecting centralized logging.

Follow the step-by-step instructions below in exact order. Everything you need is self-contained in this guide.

---

## 2. Device Inventory & Catalog Selection

Open a fresh Cisco Packet Tracer project. From the bottom-left device drawer, select and place **15 devices**:

| Role | Catalog Location | Exact PT Model | Hostname (Display Name) | Qty |
|---|---|---|---|:---:|
| **Edge Router** | Network Devices $\rightarrow$ Routers | **2911** | `R-EDGE` | 1 |
| **Core L3 Switch** | Network Devices $\rightarrow$ Switches | **3560-24PS** | `SW-CORE` | 1 |
| **Access Switch 1** | Network Devices $\rightarrow$ Switches | **2960-24TT** | `SW-ACCESS-1` | 1 |
| **Access Switch 2** | Network Devices $\rightarrow$ Switches | **2960-24TT** | `SW-ACCESS-2` | 1 |
| **Access Switch 3** | Network Devices $\rightarrow$ Switches | **2960-24TT** | `SW-ACCESS-3` | 1 |
| **Faculty Workstation 1** | End Devices $\rightarrow$ End Devices | **PC** | `FAC-PC-01` | 1 |
| **Faculty Workstation 2** | End Devices $\rightarrow$ End Devices | **PC** | `FAC-PC-02` | 1 |
| **Faculty Workstation 3** | End Devices $\rightarrow$ End Devices | **PC** | `FAC-PC-03` | 1 |
| **Application Server 1** | End Devices $\rightarrow$ End Devices | **Server** | `APP-SRV-01` | 1 |
| **Application Server 2** | End Devices $\rightarrow$ End Devices | **Server** | `APP-SRV-02` | 1 |
| **Database Server 1** | End Devices $\rightarrow$ End Devices | **Server** | `DB-SRV-01` | 1 |
| **Database Server 2** | End Devices $\rightarrow$ End Devices | **Server** | `DB-SRV-02` | 1 |
| **Management Server** | End Devices $\rightarrow$ End Devices | **Server** | `MGMT-SRV-01` | 1 |
| **Security / SIEM Server** | End Devices $\rightarrow$ End Devices | **Server** | `SEC-SRV-01` | 1 |
| **DMZ Web Server** | End Devices $\rightarrow$ End Devices | **Server** | `DMZ-SRV-01` | 1 |

> **Naming Tip:** Click each device $\rightarrow$ **Config** tab $\rightarrow$ set **Display Name** to match the Hostname in the table.

---

## 3. Physical Layout & Topology Diagram

Arrange the devices on your Packet Tracer canvas as shown below:

```
                              ┌─────────────────────────┐
                              │        R-EDGE           │
                              │     (Router 2911)       │
                              │  Gig0/1: 10.10.0.1/30   │
                              └────────────┬────────────┘
                                           │
                                    Gig0/1 │ Gig0/1
                                           │
                              ┌────────────┴────────────┐
                              │        SW-CORE          │
                              │  (3560-24PS L3 Switch)  │
                              │  Gig0/1: 10.10.0.2/30   │
                              │  SVIs: .1 on VLANs 10-60│
                              └───┬────────┬────────┬───┘
                                  │        │        │
                           Fa0/1  │  Fa0/2 │  Fa0/3 │ (802.1Q Trunks, Native 99)
                                  │        │        │
                      ┌───────────┴┐ ┌─────┴──────┐ ┌┴───────────┐
                      │SW-ACCESS-1 │ │SW-ACCESS-2 │ │SW-ACCESS-3 │
                      │(2960-24TT) │ │(2960-24TT) │ │(2960-24TT) │
                      │            │ │            │ │            │
                      │Fa0/1-3:V10 │ │Fa0/1-2:V20 │ │Fa0/1: V30  │
                      │Fa0/10: V60 │ │Fa0/3-4:V40 │ │Fa0/2: V50  │
                      └──┬───┬───┬─┘ └──┬───┬───┬─┘ └──┬─────┬───┘
                         │   │   │      │   │   │      │     │
                      ┌──┘   │   └──┐┌──┘   │   └──┐ ┌─┘     └──┐
                      │      │      ││      │      │ │          │
                   FAC-PC FAC-PC FAC-PCAPP APP DB  DBMGMT      SEC
                    -01    -02   -03 SRV-01-02 -01 -02-01      -01
                                 │
                            DMZ-SRV-01
```

---

## 4. Port-to-Port Cabling Specification

Connect the network using **Copper Straight-Through** cables (solid black line icon in Connections):

| Cable # | From Device | From Port | To Device | To Port | Link Purpose |
|:---:|---|---|---|---|---|
| **1** | `R-EDGE` | `GigabitEthernet0/1` | `SW-CORE` | `GigabitEthernet0/1` | Routed point-to-point link (`10.10.0.0/30`) |
| **2** | `SW-CORE` | `FastEthernet0/1` | `SW-ACCESS-1` | `FastEthernet0/24` | 802.1Q Trunk (VLANs 10,20,30,40,50,60; Native 99) |
| **3** | `SW-CORE` | `FastEthernet0/2` | `SW-ACCESS-2` | `FastEthernet0/24` | 802.1Q Trunk (VLANs 10,20,30,40,50,60; Native 99) |
| **4** | `SW-CORE` | `FastEthernet0/3` | `SW-ACCESS-3` | `FastEthernet0/24` | 802.1Q Trunk (VLANs 10,20,30,40,50,60; Native 99) |
| **5** | `SW-ACCESS-1` | `FastEthernet0/1` | `FAC-PC-01` | `FastEthernet0` | Access Port $\rightarrow$ VLAN 10 (Faculty) |
| **6** | `SW-ACCESS-1` | `FastEthernet0/2` | `FAC-PC-02` | `FastEthernet0` | Access Port $\rightarrow$ VLAN 10 (Faculty) |
| **7** | `SW-ACCESS-1` | `FastEthernet0/3` | `FAC-PC-03` | `FastEthernet0` | Access Port $\rightarrow$ VLAN 10 (Faculty) |
| **8** | `SW-ACCESS-1` | `FastEthernet0/10` | `DMZ-SRV-01` | `FastEthernet0` | Access Port $\rightarrow$ VLAN 60 (DMZ) |
| **9** | `SW-ACCESS-2` | `FastEthernet0/1` | `APP-SRV-01` | `FastEthernet0` | Access Port $\rightarrow$ VLAN 20 (App Tier) |
| **10** | `SW-ACCESS-2` | `FastEthernet0/2` | `APP-SRV-02` | `FastEthernet0` | Access Port $\rightarrow$ VLAN 20 (App Tier) |
| **11** | `SW-ACCESS-2` | `FastEthernet0/3` | `DB-SRV-01` | `FastEthernet0` | Access Port $\rightarrow$ VLAN 40 (Database) |
| **12** | `SW-ACCESS-2` | `FastEthernet0/4` | `DB-SRV-02` | `FastEthernet0` | Access Port $\rightarrow$ VLAN 40 (Database) |
| **13** | `SW-ACCESS-3` | `FastEthernet0/1` | `MGMT-SRV-01` | `FastEthernet0` | Access Port $\rightarrow$ VLAN 30 (Management) |
| **14** | `SW-ACCESS-3` | `FastEthernet0/2` | `SEC-SRV-01` | `FastEthernet0` | Access Port $\rightarrow$ VLAN 50 (Security / SIEM) |

---

## 5. End-Device IP & Service Configuration

### 5.1 Faculty Workstations (DHCP Enabled)
For `FAC-PC-01`, `FAC-PC-02`, and `FAC-PC-03`:
1. Click PC $\rightarrow$ **Desktop** tab $\rightarrow$ **IP Configuration**.
2. Select **DHCP** (it will receive `10.10.10.100`+, mask `255.255.255.0`, gateway `10.10.10.1`, DNS `10.10.10.1`).

### 5.2 Server Endpoints (Static Configuration)
For each server, click device $\rightarrow$ **Desktop** tab $\rightarrow$ **IP Configuration** $\rightarrow$ select **Static**:

| Hostname | Role | VLAN | IP Address | Subnet Mask | Default Gateway |
|---|---|:---:|---|---|---|
| `APP-SRV-01` | Education App Server | 20 | `10.10.20.10` | `255.255.255.0` | `10.10.20.1` |
| `APP-SRV-02` | Research App Server | 20 | `10.10.20.11` | `255.255.255.0` | `10.10.20.1` |
| `MGMT-SRV-01` | Infrastructure Admin Server | 30 | `10.10.30.10` | `255.255.255.0` | `10.10.30.1` |
| `DB-SRV-01` | Primary Database Server | 40 | `10.10.40.10` | `255.255.255.0` | `10.10.40.1` |
| `DB-SRV-02` | Secondary Database Server | 40 | `10.10.40.11` | `255.255.255.0` | `10.10.40.1` |
| `SEC-SRV-01` | Wazuh SIEM / Logging Server | 50 | `10.10.50.10` | `255.255.255.0` | `10.10.50.1` |
| `DMZ-SRV-01` | Public Reverse Proxy / Web Server | 60 | `10.10.60.10` | `255.255.255.0` | `10.10.60.1` |

### 5.3 Enable HTTP Service
On `APP-SRV-01`, `APP-SRV-02`, and `DMZ-SRV-01`:
1. Click server $\rightarrow$ **Services** tab $\rightarrow$ **HTTP**.
2. Ensure HTTP is set to **ON**.

---

## 6. Copy-Paste Device Configurations

Apply these configurations in order by clicking each device $\rightarrow$ **CLI** tab $\rightarrow$ paste into terminal.

### 6.1 `SW-CORE` Configuration (STAGE A: BASELINE)
*This configuration enables Layer 2 switching, trunks, DHCP, inter-VLAN routing, and defines all ACLs in memory without activating them on SVIs yet. (Also saved at: `packet-tracer/configs/SW-CORE-STAGE-A.txt`)*

```cisco
enable
configure terminal

hostname SW-CORE
ip domain-name aegismesh.local

enable secret AegisMesh2026!
service password-encryption
no ip domain-lookup
banner motd # UNAUTHORIZED ACCESS PROHIBITED - AegisMesh Core Switch #

line console 0
 password ConsoleAccess2026!
 login
 logging synchronous
 exec-timeout 10 0
exit

username admin privilege 15 secret AdminSSH2026!
crypto key generate rsa general-keys modulus 1024
ip ssh version 2

line vty 0 15
 login local
 transport input ssh
 exec-timeout 10 0
 access-class MGMT-VTY-ACCESS in
exit

ip access-list standard MGMT-VTY-ACCESS
 permit 10.10.30.0 0.0.0.255
 deny any
exit

ip routing

vlan 10
 name FACULTY
exit
vlan 20
 name APP-SERVERS
exit
vlan 30
 name MANAGEMENT
exit
vlan 40
 name DATABASE
exit
vlan 50
 name SECURITY
exit
vlan 60
 name DMZ
exit
vlan 99
 name NATIVE-UNUSED
exit

interface Vlan10
 description FACULTY-GATEWAY
 ip address 10.10.10.1 255.255.255.0
 no shutdown
exit

interface Vlan20
 description APP-SERVERS-GATEWAY
 ip address 10.10.20.1 255.255.255.0
 no shutdown
exit

interface Vlan30
 description MANAGEMENT-GATEWAY
 ip address 10.10.30.1 255.255.255.0
 no shutdown
exit

interface Vlan40
 description DATABASE-GATEWAY
 ip address 10.10.40.1 255.255.255.0
 no shutdown
exit

interface Vlan50
 description SECURITY-LOGGING-GATEWAY
 ip address 10.10.50.1 255.255.255.0
 no shutdown
exit

interface Vlan60
 description DMZ-GATEWAY
 ip address 10.10.60.1 255.255.255.0
 no shutdown
exit

interface GigabitEthernet0/1
 description UPLINK-TO-R-EDGE
 no switchport
 ip address 10.10.0.2 255.255.255.252
 no shutdown
exit

interface FastEthernet0/1
 description TRUNK-TO-SW-ACCESS-1
 switchport mode trunk
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,30,40,50,60
 switchport nonegotiate
 no shutdown
exit

interface FastEthernet0/2
 description TRUNK-TO-SW-ACCESS-2
 switchport mode trunk
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,30,40,50,60
 switchport nonegotiate
 no shutdown
exit

interface FastEthernet0/3
 description TRUNK-TO-SW-ACCESS-3
 switchport mode trunk
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,30,40,50,60
 switchport nonegotiate
 no shutdown
exit

interface range FastEthernet0/4-24
 shutdown
exit

interface GigabitEthernet0/2
 shutdown
exit

ip dhcp excluded-address 10.10.10.1 10.10.10.99

ip dhcp pool FACULTY-POOL
 network 10.10.10.0 255.255.255.0
 default-router 10.10.10.1
 dns-server 10.10.10.1
exit

ip route 0.0.0.0 0.0.0.0 10.10.0.1

ip access-list extended FACULTY-ACCESS
 remark --- PERMIT: Faculty to App Servers (authorized access) ---
 permit ip 10.10.10.0 0.0.0.255 10.10.20.0 0.0.0.255
 remark --- PERMIT: Faculty to DMZ (authorized access) ---
 permit ip 10.10.10.0 0.0.0.255 10.10.60.0 0.0.0.255
 remark --- DENY: Faculty to Management (lateral movement prevention) ---
 deny ip 10.10.10.0 0.0.0.255 10.10.30.0 0.0.0.255
 remark --- DENY: Faculty to Database (must go through app layer) ---
 deny ip 10.10.10.0 0.0.0.255 10.10.40.0 0.0.0.255
 remark --- DENY: Faculty to Security/Logging (privileged zone) ---
 deny ip 10.10.10.0 0.0.0.255 10.10.50.0 0.0.0.255
 remark --- PERMIT: Faculty to Internet (via default route) ---
 permit ip 10.10.10.0 0.0.0.255 any
exit

ip access-list extended APP-SERVER-ACCESS
 remark --- PERMIT: App to Database (authorized data access) ---
 permit ip 10.10.20.0 0.0.0.255 10.10.40.0 0.0.0.255
 remark --- PERMIT: App to Security/Logging (log forwarding) ---
 permit ip 10.10.20.0 0.0.0.255 10.10.50.0 0.0.0.255
 remark --- PERMIT: App to Faculty (response traffic) ---
 permit ip 10.10.20.0 0.0.0.255 10.10.10.0 0.0.0.255
 remark --- PERMIT: App to DMZ (response traffic) ---
 permit ip 10.10.20.0 0.0.0.255 10.10.60.0 0.0.0.255
 remark --- DENY: App to Management (lateral movement prevention) ---
 deny ip 10.10.20.0 0.0.0.255 10.10.30.0 0.0.0.255
 remark --- DENY: App to all other (default deny) ---
 deny ip any any
exit

ip access-list extended DMZ-ACCESS
 remark --- PERMIT: DMZ to App Servers (reverse proxy path) ---
 permit ip 10.10.60.0 0.0.0.255 10.10.20.0 0.0.0.255
 remark --- PERMIT: DMZ to Security/Logging (log forwarding) ---
 permit ip 10.10.60.0 0.0.0.255 10.10.50.0 0.0.0.255
 remark --- PERMIT: DMZ to Faculty (stateless return traffic for Faculty-initiated requests) ---
 permit ip 10.10.60.0 0.0.0.255 10.10.10.0 0.0.0.255
 remark --- DENY: DMZ to Database (critical data protection) ---
 deny ip 10.10.60.0 0.0.0.255 10.10.40.0 0.0.0.255
 remark --- DENY: DMZ to Management (privilege escalation prevention) ---
 deny ip 10.10.60.0 0.0.0.255 10.10.30.0 0.0.0.255
 remark --- DENY: DMZ to all other (default deny) ---
 deny ip any any
exit

ip access-list extended MGMT-ACCESS
 remark --- PERMIT: Mgmt to App Servers (administration) ---
 permit ip 10.10.30.0 0.0.0.255 10.10.20.0 0.0.0.255
 remark --- PERMIT: Mgmt to Database (administration) ---
 permit ip 10.10.30.0 0.0.0.255 10.10.40.0 0.0.0.255
 remark --- PERMIT: Mgmt to Security/Logging (log review) ---
 permit ip 10.10.30.0 0.0.0.255 10.10.50.0 0.0.0.255
 remark --- DENY: Mgmt to all other (restricted zone) ---
 deny ip any any
exit

ip access-list extended DB-ACCESS
 remark --- PERMIT: DB to Security/Logging (log forwarding) ---
 permit ip 10.10.40.0 0.0.0.255 10.10.50.0 0.0.0.255
 remark --- PERMIT: DB to App Servers (response traffic) ---
 permit ip 10.10.40.0 0.0.0.255 10.10.20.0 0.0.0.255
 remark --- PERMIT: DB to Management (response traffic) ---
 permit ip 10.10.40.0 0.0.0.255 10.10.30.0 0.0.0.255
 remark --- DENY: DB to all other (default deny) ---
 deny ip any any
exit

ip access-list extended SEC-ACCESS
 remark --- PERMIT: SIEM/Monitoring to App Servers ---
 permit ip 10.10.50.0 0.0.0.255 10.10.20.0 0.0.0.255
 remark --- PERMIT: SIEM/Monitoring to Database Servers ---
 permit ip 10.10.50.0 0.0.0.255 10.10.40.0 0.0.0.255
 remark --- PERMIT: SIEM/Monitoring to DMZ Servers ---
 permit ip 10.10.50.0 0.0.0.255 10.10.60.0 0.0.0.255
 remark --- PERMIT: SIEM/Monitoring to Management VLAN ---
 permit ip 10.10.50.0 0.0.0.255 10.10.30.0 0.0.0.255
 remark --- DENY: SIEM to Faculty PCs ---
 deny ip 10.10.50.0 0.0.0.255 10.10.10.0 0.0.0.255
 remark --- DENY: SIEM to Internet (Exfiltration prevention) ---
 deny ip 10.10.50.0 0.0.0.255 any
 remark --- DENY: Default Deny ---
 deny ip any any
exit

logging 10.10.50.10

end
write memory
```

---

### 6.2 `R-EDGE` Configuration

```cisco
enable
configure terminal

hostname R-EDGE
ip domain-name aegismesh.local

enable secret AegisMesh2026!
service password-encryption
no ip domain-lookup
banner motd # UNAUTHORIZED ACCESS PROHIBITED - AegisMesh Private Datacenter #

line console 0
 password ConsoleAccess2026!
 login
 logging synchronous
 exec-timeout 10 0
exit

username admin privilege 15 secret AdminSSH2026!
crypto key generate rsa general-keys modulus 1024
ip ssh version 2

line vty 0 4
 login local
 transport input ssh
 exec-timeout 10 0
 access-class MGMT-VTY-ACCESS in
exit

ip access-list standard MGMT-VTY-ACCESS
 permit 10.10.30.0 0.0.0.255
 deny any
exit

interface GigabitEthernet0/1
 description LINK-TO-SW-CORE
 ip address 10.10.0.1 255.255.255.252
 no shutdown
exit

interface GigabitEthernet0/0
 description SIMULATED-INTERNET-UPLINK
 shutdown
exit

ip route 10.10.10.0 255.255.255.0 10.10.0.2
ip route 10.10.20.0 255.255.255.0 10.10.0.2
ip route 10.10.30.0 255.255.255.0 10.10.0.2
ip route 10.10.40.0 255.255.255.0 10.10.0.2
ip route 10.10.50.0 255.255.255.0 10.10.0.2
ip route 10.10.60.0 255.255.255.0 10.10.0.2

no ip http server
no ip http secure-server
no cdp run

logging 10.10.50.10

end
write memory
```

---

### 6.3 `SW-ACCESS-1` Configuration (Faculty + DMZ)

```cisco
enable
configure terminal

hostname SW-ACCESS-1
ip domain-name aegismesh.local

enable secret AegisMesh2026!
service password-encryption
no ip domain-lookup
banner motd # UNAUTHORIZED ACCESS PROHIBITED - AegisMesh Access Switch 1 #

line console 0
 password ConsoleAccess2026!
 login
 logging synchronous
 exec-timeout 10 0
exit

line vty 0 15
 password VTYAccess2026!
 login
 transport input ssh
 exec-timeout 10 0
exit

vlan 10
 name FACULTY
exit
vlan 20
 name APP-SERVERS
exit
vlan 30
 name MANAGEMENT
exit
vlan 40
 name DATABASE
exit
vlan 50
 name SECURITY
exit
vlan 60
 name DMZ
exit
vlan 99
 name NATIVE-UNUSED
exit

interface FastEthernet0/1
 description FAC-PC-01
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 no shutdown
exit

interface FastEthernet0/2
 description FAC-PC-02
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 no shutdown
exit

interface FastEthernet0/3
 description FAC-PC-03
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 no shutdown
exit

interface FastEthernet0/10
 description DMZ-SRV-01
 switchport mode access
 switchport access vlan 60
 spanning-tree portfast
 no shutdown
exit

interface FastEthernet0/24
 description TRUNK-TO-SW-CORE
 switchport mode trunk
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,30,40,50,60
 switchport nonegotiate
 no shutdown
exit

interface range FastEthernet0/4-9
 switchport mode access
 switchport access vlan 99
 shutdown
exit

interface range FastEthernet0/11-23
 switchport mode access
 switchport access vlan 99
 shutdown
exit

interface GigabitEthernet0/1
 shutdown
exit

interface GigabitEthernet0/2
 shutdown
exit

end
write memory
```

---

### 6.4 `SW-ACCESS-2` Configuration (App + DB Servers)

```cisco
enable
configure terminal

hostname SW-ACCESS-2
ip domain-name aegismesh.local

enable secret AegisMesh2026!
service password-encryption
no ip domain-lookup
banner motd # UNAUTHORIZED ACCESS PROHIBITED - AegisMesh Access Switch 2 #

line console 0
 password ConsoleAccess2026!
 login
 logging synchronous
 exec-timeout 10 0
exit

line vty 0 15
 password VTYAccess2026!
 login
 transport input ssh
 exec-timeout 10 0
exit

vlan 10
 name FACULTY
exit
vlan 20
 name APP-SERVERS
exit
vlan 30
 name MANAGEMENT
exit
vlan 40
 name DATABASE
exit
vlan 50
 name SECURITY
exit
vlan 60
 name DMZ
exit
vlan 99
 name NATIVE-UNUSED
exit

interface FastEthernet0/1
 description APP-SRV-01-EDUCATION
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
 no shutdown
exit

interface FastEthernet0/2
 description APP-SRV-02-RESEARCH
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
 no shutdown
exit

interface FastEthernet0/3
 description DB-SRV-01-PRIMARY
 switchport mode access
 switchport access vlan 40
 spanning-tree portfast
 no shutdown
exit

interface FastEthernet0/4
 description DB-SRV-02-SECONDARY
 switchport mode access
 switchport access vlan 40
 spanning-tree portfast
 no shutdown
exit

interface FastEthernet0/24
 description TRUNK-TO-SW-CORE
 switchport mode trunk
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,30,40,50,60
 switchport nonegotiate
 no shutdown
exit

interface range FastEthernet0/5-23
 switchport mode access
 switchport access vlan 99
 shutdown
exit

interface GigabitEthernet0/1
 shutdown
exit

interface GigabitEthernet0/2
 shutdown
exit

end
write memory
```

---

### 6.5 `SW-ACCESS-3` Configuration (Management + Security/SIEM)

```cisco
enable
configure terminal

hostname SW-ACCESS-3
ip domain-name aegismesh.local

enable secret AegisMesh2026!
service password-encryption
no ip domain-lookup
banner motd # UNAUTHORIZED ACCESS PROHIBITED - AegisMesh Access Switch 3 #

line console 0
 password ConsoleAccess2026!
 login
 logging synchronous
 exec-timeout 10 0
exit

line vty 0 15
 password VTYAccess2026!
 login
 transport input ssh
 exec-timeout 10 0
exit

vlan 10
 name FACULTY
exit
vlan 20
 name APP-SERVERS
exit
vlan 30
 name MANAGEMENT
exit
vlan 40
 name DATABASE
exit
vlan 50
 name SECURITY
exit
vlan 60
 name DMZ
exit
vlan 99
 name NATIVE-UNUSED
exit

interface FastEthernet0/1
 description MGMT-SRV-01
 switchport mode access
 switchport access vlan 30
 spanning-tree portfast
 no shutdown
exit

interface FastEthernet0/2
 description SEC-SRV-01-SIEM
 switchport mode access
 switchport access vlan 50
 spanning-tree portfast
 no shutdown
exit

interface FastEthernet0/24
 description TRUNK-TO-SW-CORE
 switchport mode trunk
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,30,40,50,60
 switchport nonegotiate
 no shutdown
exit

interface range FastEthernet0/3-23
 switchport mode access
 switchport access vlan 99
 shutdown
exit

interface GigabitEthernet0/1
 shutdown
exit

interface GigabitEthernet0/2
 shutdown
exit

end
write memory
```

---

## 7. Stage A: Baseline Verification Protocol

> **Objective:** Prove that Layer 2 switching, trunking, SVI gateways, and IP routing function 100% across the fabric before introducing ACL restrictions.  
> **Pass Rule:** ALL 14 tests must return **`Reply from <IP>`** or valid DHCP IP.

### 7.1 Gateway Reachability Tests (Intra-VLAN)

Open **Command Prompt** on each device and run:

| Test ID | Source Device | CLI Command | Expected Result | Screenshot Filename |
|:---:|---|---|---|---|
| **PRE-01 / BL-01** | `FAC-PC-01` | `ping 10.10.10.1` | Reply from 10.10.10.1 ✅ | `EV-BL-01_gateway-pings.png` |
| **PRE-02 / BL-02** | `APP-SRV-01` | `ping 10.10.20.1` | Reply from 10.10.20.1 ✅ | (Included in EV-BL-01) |
| **PRE-03 / BL-03** | `MGMT-SRV-01` | `ping 10.10.30.1` | Reply from 10.10.30.1 ✅ | (Included in EV-BL-01) |
| **PRE-04 / BL-04** | `DB-SRV-01` | `ping 10.10.40.1` | Reply from 10.10.40.1 ✅ | (Included in EV-BL-01) |
| **PRE-05 / BL-05** | `SEC-SRV-01` | `ping 10.10.50.1` | Reply from 10.10.50.1 ✅ | (Included in EV-BL-01) |
| **PRE-06 / BL-06** | `DMZ-SRV-01` | `ping 10.10.60.1` | Reply from 10.10.60.1 ✅ | (Included in EV-BL-01) |
| **PRE-07 / BL-07** | `FAC-PC-01` | `ipconfig` (or GUI IP check) | IP in `10.10.10.100`–`200` ✅ | `EV-BL-02_dhcp-assignment.png` |

### 7.2 Cross-VLAN Inter-Zone Routing Tests (Pre-ACL)

| Test ID | Source Device | CLI Command | Expected Pre-ACL Result | Screenshot Filename |
|:---:|---|---|---|---|
| **BL-08** | `FAC-PC-01` | `ping 10.10.20.10` | Reply from 10.10.20.10 ✅ | `EV-BL-03_cross-vlan-pings.png` |
| **BL-09** | `FAC-PC-01` | `ping 10.10.40.10` | Reply from 10.10.40.10 ✅ | (Included in EV-BL-03) |
| **BL-10** | `APP-SRV-01` | `ping 10.10.40.10` | Reply from 10.10.40.10 ✅ | (Included in EV-BL-03) |
| **BL-11** | `APP-SRV-01` | `ping 10.10.30.10` | Reply from 10.10.30.10 ✅ | (Included in EV-BL-03) |
| **BL-12** | `DMZ-SRV-01` | `ping 10.10.20.10` | Reply from 10.10.20.10 ✅ | (Included in EV-BL-03) |
| **BL-13** | `MGMT-SRV-01` | `ping 10.10.40.10` | Reply from 10.10.40.10 ✅ | (Included in EV-BL-03) |
| **BL-14** | `FAC-PC-01` | `ping 10.10.0.1` | Reply from 10.10.0.1 (R-EDGE) ✅ | `EV-BL-04_router-uplink.png` |

*Capture infrastructure CLI screenshots on `SW-CORE`: `show vlan brief` (`EV-INFRA-01`), `show interfaces trunk` (`EV-INFRA-02`), `show ip interface brief` (`EV-INFRA-03`), `show ip route` (`EV-INFRA-04`).*

---

## 8. Stage B: ACL Activation (Security Enforcement)

Once all Stage A baseline tests pass, paste this single activation block into `SW-CORE` CLI to bind all security ACLs to their respective SVIs:

```cisco
enable
configure terminal

interface Vlan10
 ip access-group FACULTY-ACCESS in
exit

interface Vlan20
 ip access-group APP-SERVER-ACCESS in
exit

interface Vlan30
 ip access-group MGMT-ACCESS in
exit

interface Vlan40
 ip access-group DB-ACCESS in
exit

interface Vlan50
 ip access-group SEC-ACCESS in
exit

interface Vlan60
 ip access-group DMZ-ACCESS in
exit

end
write memory
```

---

## 9. Stage B: Security & Lateral Movement Test Execution

Execute these tests in order. Open **Command Prompt** (for Ping/SSH) or **Web Browser** on the source device.

### 9.1 Authorized Functional Traffic (Expected: ALLOW)

| Test ID | Source | Target | Command / Protocol | Expected Result | Enforcing Security Rule |
|:---:|---|---|---|:---:|---|
| **PT-01** | `FAC-PC-01` | `APP-SRV-01` | `ping 10.10.20.10` | **Reply ✅** | `FACULTY-ACCESS` line 1 & `APP-SERVER-ACCESS` line 3 (return) |
| **PT-01b**| `FAC-PC-01` | `APP-SRV-01` | Browser $\rightarrow$ `http://10.10.20.10` | **Page Loads ✅** | `FACULTY-ACCESS` line 1 & `APP-SERVER-ACCESS` line 3 |
| **PT-04** | `APP-SRV-01` | `DB-SRV-01` | `ping 10.10.40.10` | **Reply ✅** | `APP-SERVER-ACCESS` line 1 & `DB-ACCESS` line 2 (return) |
| **PT-08** | `DMZ-SRV-01` | `APP-SRV-01` | `ping 10.10.20.10` | **Reply ✅** | `DMZ-ACCESS` line 1 & `APP-SERVER-ACCESS` line 4 (return) |
| **PT-10** | `FAC-PC-01` | DHCP Pool | DHCP Request | **IP Assigned ✅** | SVI broadcast / Intra-VLAN |
| **PT-11** | `MGMT-SRV-01`| `DB-SRV-01` | `ping 10.10.40.10` | **Reply ✅** | `MGMT-ACCESS` line 2 & `DB-ACCESS` line 3 (return) |
| **PT-13** | `APP-SRV-01` | `FAC-PC-01` | `ping 10.10.10.100` | **Reply ✅** | `APP-SERVER-ACCESS` line 3 (return path verification) |
| **PT-14** | `SEC-SRV-01` | `APP-SRV-01` | `ping 10.10.20.10` | **Reply ✅** | `SEC-ACCESS` line 1 (SIEM Telemetry polling) |
| **PT-15** | `SEC-SRV-01` | `DB-SRV-01` | `ping 10.10.40.10` | **Reply ✅** | `SEC-ACCESS` line 2 (Database audit polling) |
| **PT-18** | `FAC-PC-01` | `DMZ-SRV-01` | `ping 10.10.60.10` / HTTP | **Reply / Page ✅** | `FACULTY-ACCESS` line 2 & `DMZ-ACCESS` line 3 (return) |
| **PT-MGMT-01B**| `MGMT-SRV-01`| `SW-CORE` | `ssh -l admin 10.10.30.1` | **Password Prompt ✅** | `MGMT-VTY-ACCESS` (`permit 10.10.30.0/24`) on VTY |
| **PT-LM-01**| `APP-SRV-01` | `DB-SRV-01` | `ping 10.10.40.10` | **Reply ✅** | Authorized application dependency flow |

---

### 9.2 Unauthorized Boundary & Lateral Movement Tests (Expected: BLOCK)

| Test ID | Source | Target | Command / Protocol | Expected Result | Enforcing Security Rule |
|:---:|---|---|---|:---:|---|
| **PT-02** | `FAC-PC-01` | `DB-SRV-01` | `ping 10.10.40.10` | **Timed out ❌** | `FACULTY-ACCESS` line 4 (`deny ip 10.0 → 40.0`) |
| **PT-03** | `FAC-PC-01` | `MGMT-SRV-01`| `ping 10.10.30.10` | **Timed out ❌** | `FACULTY-ACCESS` line 3 (`deny ip 10.0 → 30.0`) |
| **PT-05** | `APP-SRV-01` | `MGMT-SRV-01`| `ping 10.10.30.10` | **Timed out ❌** | `APP-SERVER-ACCESS` line 5 (`deny ip 20.0 → 30.0` - E-02) |
| **PT-06** | `DMZ-SRV-01` | `DB-SRV-01` | `ping 10.10.40.10` | **Timed out ❌** | `DMZ-ACCESS` line 4 (`deny ip 60.0 → 40.0` - ARCH-SCENARIO-02) |
| **PT-07** | `DMZ-SRV-01` | `MGMT-SRV-01`| `ping 10.10.30.10` | **Timed out ❌** | `DMZ-ACCESS` line 5 (`deny ip 60.0 → 30.0`) |
| **PT-09** | `DB-SRV-01` | `FAC-PC-01` | `ping 10.10.10.100` | **Timed out ❌** | `DB-ACCESS` line 4 (`deny ip any any` - ARCH-SCENARIO-01) |
| **PT-12** | `DB-SRV-01` | `DMZ-SRV-01` | `ping 10.10.60.10` | **Timed out ❌** | `DB-ACCESS` line 4 (`deny ip any any`) |
| **PT-16** | `FAC-PC-01` | `SEC-SRV-01` | `ping 10.10.50.10` | **Timed out ❌** | `FACULTY-ACCESS` line 5 (`deny ip 10.0 → 50.0`) |
| **PT-MGMT-01A**| `FAC-PC-01` | `SW-CORE` | `ssh -l admin 10.10.10.1` | **Refused / Drop ❌** | `MGMT-VTY-ACCESS` (`deny any` for non-VLAN 30) |
| **PT-LM-02**| `APP-SRV-01` | `MGMT-SRV-01`| `ping 10.10.30.10` | **Timed out ❌** | `APP-SERVER-ACCESS` line 5 (E-02 lateral pivot) |
| **PT-LM-03**| `DMZ-SRV-01` | `DB-SRV-01` | `ping 10.10.40.10` | **Timed out ❌** | `DMZ-ACCESS` line 4 (ARCH-SCENARIO-02 data exfil) |
| **PT-LM-04**| `DMZ-SRV-01` | `MGMT-SRV-01`| `ping 10.10.30.10` | **Timed out ❌** | `DMZ-ACCESS` line 5 (DMZ $\rightarrow$ Mgmt escalation) |
| **PT-LM-05**| `DB-SRV-01` | `FAC-PC-01` | `ping 10.10.10.100` | **Timed out ❌** | `DB-ACCESS` line 4 (ARCH-SCENARIO-01 reverse pivot) |

---

## 10. Simulation Mode Visual Capture Protocol

Switch to **Simulation Mode** (bottom-right toggle in Packet Tracer, or `Shift+S`):
1. In Event List Filters, click **Show None**, then **Edit Filters** $\rightarrow$ select `ICMP`, `HTTP`, `TCP`.
2. Generate packets from source terminal. Click **Auto Capture / Play** or step forward.
3. Observe and capture:
   - **For ALLOW Tests (e.g., PT-01):** Packet travels source $\rightarrow$ Access Switch $\rightarrow$ SW-CORE $\rightarrow$ Access Switch $\rightarrow$ Target, and Echo Reply returns successfully.
   - **For BLOCK Tests (e.g., PT-02, PT-05, PT-06, PT-09):** Packet reaches `SW-CORE` ingress SVI and is **dropped with a red 'X' indicator**, proving destruction at the security boundary.

---

## 11. Evidence Screenshot Checklist & Repository Path

Save all screenshots to: `packet-tracer/test-results/evidence/`

| Filename | Content to Capture |
|---|---|
| `EV-INFRA-01_vlan-brief.png` | `show vlan brief` on `SW-CORE` |
| `EV-INFRA-02_trunk-status.png` | `show interfaces trunk` on `SW-CORE` |
| `EV-INFRA-03_svi-status.png` | `show ip interface brief` on `SW-CORE` |
| `EV-INFRA-04_routing-table.png` | `show ip route` on `SW-CORE` |
| `EV-BL-01_gateway-pings.png` | Gateway pings (BL-01 through BL-06) |
| `EV-BL-02_dhcp-assignment.png` | `FAC-PC-01` IP Configuration showing DHCP assignment |
| `EV-BL-03_cross-vlan-pings.png` | Pre-ACL cross-VLAN pings (BL-08 through BL-13) |
| `EV-SEC-01_faculty-app-allow.png` | `PT-01` (Ping) & `PT-01b` (HTTP Browser) success |
| `EV-SEC-02_faculty-db-block.png` | `PT-02` Ping Request Timed Out |
| `EV-SEC-03_faculty-mgmt-block.png`| `PT-03` Ping Request Timed Out |
| `EV-SEC-04_app-db-allow.png` | `PT-04` App $\rightarrow$ DB Ping Reply |
| `EV-SEC-05_app-mgmt-block.png` | `PT-05` App $\rightarrow$ Mgmt Ping Timed Out (E-02) |
| `EV-SEC-06_dmz-db-block.png` | `PT-06` DMZ $\rightarrow$ DB Ping Timed Out (ARCH-SCENARIO-02) |
| `EV-SEC-07_dmz-mgmt-block.png` | `PT-07` DMZ $\rightarrow$ Mgmt Ping Timed Out |
| `EV-SEC-08_dmz-app-allow.png` | `PT-08` DMZ $\rightarrow$ App Ping Reply |
| `EV-SEC-09_db-faculty-block.png` | `PT-09` DB $\rightarrow$ Faculty Reverse Pivot Timed Out (ARCH-SCENARIO-01) |
| `EV-SEC-10_mgmt-db-allow.png` | `PT-11` Mgmt $\rightarrow$ DB Ping Reply |
| `EV-SEC-11_security-monitoring.png`| `PT-14` & `PT-15` Security SIEM Polling Replies |
| `EV-SEC-12_faculty-security-block.png` | `PT-16` Faculty $\rightarrow$ Security Timed Out |
| `EV-SEC-13_faculty-dmz-allow.png`| `PT-18` Faculty $\rightarrow$ DMZ Ping / HTTP Reply |
| `EV-SEC-14_vty-mgmt-ssh.png` | `PT-MGMT-01A` (Faculty SSH dropped) vs `PT-MGMT-01B` (Mgmt SSH login prompt) |
| `EV-SEC-15_lateral-movement-blocks.png`| `PT-LM-02` through `PT-LM-05` command prompt timed out captures |
| `EV-SEC-16_acl-hit-counters.png` | `show access-lists` on `SW-CORE` showing non-zero match counters |
| `EV-SIM-01_allow-faculty-app.png`| Simulation trace of `PT-01` (Green PDU path) |
| `EV-SIM-02_block-faculty-db.png` | Simulation drop of `PT-02` at `SW-CORE` SVI Vlan10 (Red 'X') |
| `EV-SIM-03_block-app-mgmt.png` | Simulation drop of `PT-05` at `SW-CORE` SVI Vlan20 (Red 'X') |
| `EV-SIM-04_block-dmz-db.png` | Simulation drop of `PT-06` at `SW-CORE` SVI Vlan60 (Red 'X') |
| `EV-SIM-05_block-db-faculty.png` | Simulation drop of `PT-09` at `SW-CORE` SVI Vlan40 (Red 'X') |

---

## 12. Troubleshooting & FAQ

| Problem | Cause | Quick Fix |
|---|---|---|
| Link lights are Amber / Orange | Spanning Tree Protocol (STP) listening/learning state (takes ~30s). | Click **Fast Forward Time** button (`Alt+F` or bottom toolbar double-arrow) to skip forward. |
| Faculty PC receives `169.254.x.x` (APIPA) | DHCP request timed out before switchport converged. | In PC IP Config, toggle from **Static** to **DHCP** again, or click **Fast Forward Time**. |
| First ping packet drops (`Request timed out`, then 3 replies) | Normal ARP resolution on first contact. | Run the ping command a second time — all 4 replies will succeed. |
| SSH connection says "Connection refused" | SSH v2 crypto keys not generated, or host blocked by VTY access-class. | Normal for `PT-MGMT-01A` (BLOCK). For `MGMT-SRV-01`, verify target IP is `10.10.30.1` and username is `admin`. |
| `% Invalid input detected` during config paste | Minor IOS syntax differences in older PT versions (e.g., `nonegotiate`). | Non-critical; ignore and proceed. The core VLAN, SVI, and ACL rules will function normally. |

---

## 13. Completion & Handback

When you finish running the tests:
1. Save your completed Packet Tracer topology as **`packet-tracer/topology.pkt`**.
2. Place all captured screenshots in **`packet-tracer/test-results/evidence/`**.
3. Hand back the evidence to the Antigravity Lead Architect to compile the final empirical verification report and update project traceability to **`VERIFIED`**.
