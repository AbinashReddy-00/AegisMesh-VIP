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

## 2. Static Terraform Validation Instructions

To validate the syntax and structure of this Terraform configuration locally:

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

## 3. Local Zero-Trust Automated Security Validation

AegisMesh includes an automated, empirical security validation suite in `testing/aws/` that deploys the Terraform modules against a local AWS API simulation (Moto / LocalStack) and programmatically asserts Zero-Trust security rules without requiring AWS credentials or incurring any cloud costs.

### Execution Command:
```powershell
# From project root
powershell -ExecutionPolicy Bypass -File .\testing\aws\deploy-localstack.ps1
```

### What This Suite Does:
1. **Starts Local AWS API Simulator:** Launches a local mock container mapping AWS EC2/VPC APIs to `http://localhost:4566`.
2. **Initializes Terraform:** Configures provider endpoints to target the local simulator.
3. **Plans Infrastructure:** Validates state transitions against simulated AWS APIs.
4. **Applies Infrastructure:** Creates live virtual VPCs, subnets, route tables, and security groups in memory.
5. **Executes Empirical Security Validation:** Runs `validate_aws_security.py` to assert the 8 Zero-Trust controls below.

### The 8 Zero-Trust Controls Validated (8 / 8 PASS):

| Control ID | Control Name | Zero-Trust Verification Check | Result |
| :--- | :--- | :--- | :---: |
| **AWS-01** | Web Tier Architecture | Verifies 2 public subnets attach to the Internet Gateway with `0.0.0.0/0` routing. | **[PASS]** |
| **AWS-02** | App Tier Private Isolation | Asserts private application subnets have `MapPublicIpOnLaunch=False` and no IGW routes. | **[PASS]** |
| **AWS-03** | Database Tier Isolation | Verifies database subnets are air-gapped with no default `0.0.0.0/0` egress routes. | **[PASS]** |
| **AWS-04** | Web HTTPS Policy | Asserts Web Security Group restricts public ingress strictly to TCP port 443. | **[PASS]** |
| **AWS-05** | Web → App Policy | Verifies Application Security Group ingress allows traffic *only* from the Web SG ID. | **[PASS]** |
| **AWS-06** | App → DB Policy | Verifies Database Security Group ingress allows PostgreSQL port 5432 *only* from the App SG ID. | **[PASS]** |
| **AWS-07** | Web → DB Bypass Prevention | Asserts that Web tier cannot bypass the App tier to query the Database directly (Threat E-04). | **[PASS]** |
| **AWS-08** | Database Public Exposure Check | Strictly verifies zero direct internet (`0.0.0.0/0`) ingress rules exist on the Database SG. | **[PASS]** |

> **Cloud Deployment Clarification:**
> This validation runs **strictly against a local AWS API simulation**. It does **NOT** provision resources in a real AWS account, incurs **$0.00 cost**, and requires zero cloud credentials.

---

## 4. Key Architecture & Security Principles

1. **3-Tier Micro-Segmentation:** Clear separation of Public Web, Private Application, and Isolated Database subnets across multiple Availability Zones.
2. **Mutual Security Group Referencing:** Application tier accepts traffic *only* from the Web security group; Database tier accepts traffic *only* from the Application security group.
3. **Air-Gapped Database Tier:** Isolated database subnets possess no default route (`0.0.0.0/0`) to the Internet Gateway or NAT Gateway.
4. **Cost-Safe Defaults:** `enable_nat_gateway = false` by default to avoid cloud charges during academic or evaluation testing.
