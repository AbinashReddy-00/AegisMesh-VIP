# AegisMesh — AWS Cloud Infrastructure (Terraform IaC)

**Status:** IMPLEMENTED AS TERRAFORM IaC & LOCALLY VALIDATED  
**Deployment:** NOT YET APPLIED TO AWS (Zero-Cost Local Architecture & Validation Only)  
**Evidence:** Modular Terraform Codebase + `terraform validate` passing  

---

## 1. Directory Structure

```
aws/
├── terraform/
│   ├── providers.tf                  # AWS provider declaration & global tagging
│   ├── main.tf                       # Root module assembling VPC and Security Groups
│   ├── variables.tf                  # Input variables with strict type validation
│   ├── outputs.tf                    # VPC and Security Group resource ID outputs
│   ├── versions.tf                   # Required Terraform and AWS provider versions
│   ├── terraform.tfvars.example      # Sample variable configuration values
│   │
│   └── modules/
│       ├── vpc/
│       │   ├── main.tf               # 3-Tier Multi-AZ VPC, subnets, route tables, IGW
│       │   ├── variables.tf          # Subnet CIDRs, AZs, NAT gateway toggles
│       │   └── outputs.tf            # Subnet IDs and VPC attributes
│       │
│       └── security-groups/
│           ├── main.tf               # Web, App, and Database Zero-Trust Security Groups
│           ├── variables.tf          # Port configurations and trusted CIDRs
│           └── outputs.tf            # Security group IDs
│
├── architecture/
│   └── aws-zero-trust-architecture.md # Detailed Zero-Trust Cloud Architecture Design
│
└── README.md                         # This file
```

---

## 2. Local Validation Instructions

To validate this Terraform configuration locally without requiring AWS cloud credentials or an active AWS account:

```powershell
# 1. Navigate to the terraform directory
cd aws/terraform

# 2. Initialize provider plugins locally (offline mode)
terraform init -backend=false

# 3. Check format compliance
terraform fmt -check

# 4. Validate syntax and resource configuration
terraform validate
```

---

## 3. Key Architecture & Security Principles

1. **3-Tier Micro-Segmentation:** Clear separation of Public Web, Private Application, and Isolated Database subnets across multiple Availability Zones.
2. **Mutual Security Group Referencing:** Application tier accepts traffic *only* from the Web security group; Database tier accepts traffic *only* from the Application security group.
3. **Air-Gapped Database Tier:** Isolated database subnets possess no default route (`0.0.0.0/0`) to the Internet Gateway or NAT Gateway.
4. **Cost-Safe Defaults:** `enable_nat_gateway = false` by default to avoid cloud charges during academic or evaluation testing.
