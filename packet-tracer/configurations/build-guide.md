# Cisco Packet Tracer — Build Guide

**Purpose:** Step-by-step instructions to construct the AegisMesh private datacenter topology in Cisco Packet Tracer.  
**Estimated Time:** 45–60 minutes  
**Packet Tracer Version:** 8.2+  

---

## Step 1: Place Network Devices

Open a new Packet Tracer project. Place the following devices from the device panel:

| Device | PT Model | Category | Hostname |
|---|---|---|---|
| Edge Router | 2911 | Network Devices → Routers | R-EDGE |
| Core Switch | 3560-24PS | Network Devices → Switches | SW-CORE |
| Access Switch 1 | 2960-24TT | Network Devices → Switches | SW-ACCESS-1 |
| Access Switch 2 | 2960-24TT | Network Devices → Switches | SW-ACCESS-2 |
| Access Switch 3 | 2960-24TT | Network Devices → Switches | SW-ACCESS-3 |

**Layout suggestion:**
```
                R-EDGE (top center)
                    |
               SW-CORE (center)
              /     |     \
    SW-ACCESS-1  SW-ACCESS-2  SW-ACCESS-3
    (left)       (center)     (right)
```

---

## Step 2: Place End Devices

From **End Devices**, place:

| Device | PT Type | Connect To | Hostname |
|---|---|---|---|
| Faculty PC 1 | PC | SW-ACCESS-1 Fa0/1 | FAC-PC-01 |
| Faculty PC 2 | PC | SW-ACCESS-1 Fa0/2 | FAC-PC-02 |
| Faculty PC 3 | PC | SW-ACCESS-1 Fa0/3 | FAC-PC-03 |
| DMZ Server | Server | SW-ACCESS-1 Fa0/10 | DMZ-SRV-01 |
| App Server 1 | Server | SW-ACCESS-2 Fa0/1 | APP-SRV-01 |
| App Server 2 | Server | SW-ACCESS-2 Fa0/2 | APP-SRV-02 |
| DB Server 1 | Server | SW-ACCESS-2 Fa0/3 | DB-SRV-01 |
| DB Server 2 | Server | SW-ACCESS-2 Fa0/4 | DB-SRV-02 |
| Mgmt Server | Server | SW-ACCESS-3 Fa0/1 | MGMT-SRV-01 |
| Sec/Log Server | Server | SW-ACCESS-3 Fa0/2 | SEC-SRV-01 |

---

## Step 3: Cable the Network

Use **Copper Straight-Through** cables for all connections:

| From Device | From Port | To Device | To Port | Link Type |
|---|---|---|---|---|
| R-EDGE | GigabitEthernet0/1 | SW-CORE | GigabitEthernet0/1 | Router ↔ Core |
| SW-CORE | FastEthernet0/1 | SW-ACCESS-1 | FastEthernet0/24 | Trunk |
| SW-CORE | FastEthernet0/2 | SW-ACCESS-2 | FastEthernet0/24 | Trunk |
| SW-CORE | FastEthernet0/3 | SW-ACCESS-3 | FastEthernet0/24 | Trunk |
| SW-ACCESS-1 | FastEthernet0/1 | FAC-PC-01 | FastEthernet0 | Access (VLAN 10) |
| SW-ACCESS-1 | FastEthernet0/2 | FAC-PC-02 | FastEthernet0 | Access (VLAN 10) |
| SW-ACCESS-1 | FastEthernet0/3 | FAC-PC-03 | FastEthernet0 | Access (VLAN 10) |
| SW-ACCESS-1 | FastEthernet0/10 | DMZ-SRV-01 | FastEthernet0 | Access (VLAN 60) |
| SW-ACCESS-2 | FastEthernet0/1 | APP-SRV-01 | FastEthernet0 | Access (VLAN 20) |
| SW-ACCESS-2 | FastEthernet0/2 | APP-SRV-02 | FastEthernet0 | Access (VLAN 20) |
| SW-ACCESS-2 | FastEthernet0/3 | DB-SRV-01 | FastEthernet0 | Access (VLAN 40) |
| SW-ACCESS-2 | FastEthernet0/4 | DB-SRV-02 | FastEthernet0 | Access (VLAN 40) |
| SW-ACCESS-3 | FastEthernet0/1 | MGMT-SRV-01 | FastEthernet0 | Access (VLAN 30) |
| SW-ACCESS-3 | FastEthernet0/2 | SEC-SRV-01 | FastEthernet0 | Access (VLAN 50) |

---

## Step 4: Configure Devices

Apply the configurations from the following files by entering CLI mode on each device (click device → CLI tab):

1. [R-EDGE.txt](file:///C:/Users/abhia/.gemini/antigravity-ide/scratch/AegisMesh/packet-tracer/configurations/R-EDGE.txt)
2. [SW-CORE.txt](file:///C:/Users/abhia/.gemini/antigravity-ide/scratch/AegisMesh/packet-tracer/configurations/SW-CORE.txt)
3. [SW-ACCESS-1.txt](file:///C:/Users/abhia/.gemini/antigravity-ide/scratch/AegisMesh/packet-tracer/configurations/SW-ACCESS-1.txt)
4. [SW-ACCESS-2.txt](file:///C:/Users/abhia/.gemini/antigravity-ide/scratch/AegisMesh/packet-tracer/configurations/SW-ACCESS-2.txt)
5. [SW-ACCESS-3.txt](file:///C:/Users/abhia/.gemini/antigravity-ide/scratch/AegisMesh/packet-tracer/configurations/SW-ACCESS-3.txt)

**How to apply:** Copy each configuration block, enter `enable` mode on the device CLI, then paste the configuration commands.

---

## Step 5: Configure End Device IP Addresses

### Faculty PCs (DHCP)

For FAC-PC-01, FAC-PC-02, FAC-PC-03:
1. Click device → Desktop → IP Configuration
2. Select **DHCP**
3. Wait for IP assignment from pool 10.10.10.100–10.10.10.200
4. Verify gateway is 10.10.10.1

### Servers (Static IP)

| Device | IP Address | Subnet Mask | Default Gateway |
|---|---|---|---|
| APP-SRV-01 | 10.10.20.10 | 255.255.255.0 | 10.10.20.1 |
| APP-SRV-02 | 10.10.20.11 | 255.255.255.0 | 10.10.20.1 |
| MGMT-SRV-01 | 10.10.30.10 | 255.255.255.0 | 10.10.30.1 |
| DB-SRV-01 | 10.10.40.10 | 255.255.255.0 | 10.10.40.1 |
| DB-SRV-02 | 10.10.40.11 | 255.255.255.0 | 10.10.40.1 |
| SEC-SRV-01 | 10.10.50.10 | 255.255.255.0 | 10.10.50.1 |
| DMZ-SRV-01 | 10.10.60.10 | 255.255.255.0 | 10.10.60.1 |

For each server:
1. Click device → Desktop → IP Configuration
2. Select **Static**
3. Enter the IP address, subnet mask, and default gateway

### Enable HTTP on App Servers and DMZ Server

For APP-SRV-01, APP-SRV-02, DMZ-SRV-01:
1. Click device → Services → HTTP
2. Ensure HTTP service is **ON**
3. This allows testing web access in addition to ping

---

## Step 6: Verify Connectivity (Pre-ACL)

Before applying ACLs, verify basic routing works:

1. From FAC-PC-01: `ping 10.10.10.1` (default gateway) — should succeed
2. From FAC-PC-01: `ping 10.10.20.10` (APP-SRV-01) — should succeed
3. From APP-SRV-01: `ping 10.10.40.10` (DB-SRV-01) — should succeed
4. From FAC-PC-01: `ping 10.10.40.10` (DB-SRV-01) — should succeed (ACLs not applied yet)

If any fail, check:
- VLAN assignments: `show vlan brief` on switches
- Trunk links: `show interfaces trunk` on SW-CORE
- SVIs: `show ip interface brief` on SW-CORE
- Routing: `show ip route` on SW-CORE

---

## Step 7: Apply ACLs

The ACLs are already included in the SW-CORE configuration file. They are applied to SVI interfaces.

If you configured SW-CORE from the configuration file, ACLs are already active.

---

## Step 8: Run Security Tests

Execute the test matrix from [test-matrix.md](file:///C:/Users/abhia/.gemini/antigravity-ide/scratch/AegisMesh/packet-tracer/test-results/test-matrix.md).

Use Simulation Mode (bottom-right, switch from Realtime to Simulation) for detailed packet tracing.

---

## Step 9: Save

Save the topology as `topology.pkt` in the `packet-tracer/` directory.

---

## Troubleshooting

| Issue | Check |
|---|---|
| Trunk not working | `show interfaces trunk` — verify allowed VLANs |
| DHCP not assigning | `show ip dhcp pool` on SW-CORE — check excluded range |
| Ping fails everywhere | `show ip interface brief` on SW-CORE — all SVIs should be up/up |
| ACL blocking everything | `show access-lists` — check hit counts; verify correct interface/direction |
| Port not in correct VLAN | `show vlan brief` on the access switch — check port assignment |
