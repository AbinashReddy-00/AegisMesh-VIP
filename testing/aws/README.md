# AegisMesh — LocalStack AWS Security Validation Environment

This directory provides an **offline, zero-cost, locally executable AWS simulation environment** powered by [LocalStack](https://localstack.cloud/) and Docker Desktop. It allows evaluators and teammates to apply the 3-Tier Zero-Trust Terraform infrastructure and empirically assert its security controls without an AWS account or credentials.

---

## 1. Directory Structure

```
testing/aws/
├── docker-compose.yml              # LocalStack Community container definition (Port 4566)
├── deploy-localstack.ps1           # 1-click PowerShell runner: starts LocalStack, plans, applies, and validates
├── destroy-localstack.ps1          # 1-click PowerShell teardown: destroys Terraform and stops Docker
├── validate_aws_security.py        # Programmatic Zero-Trust compliance test suite (AWS-01 to AWS-08)
├── README.md                       # This documentation file
│
└── terraform-localstack/           # LocalStack-isolated Terraform runner
    ├── providers.tf                # Directs endpoints to http://localhost:4566 (Dummy credentials)
    ├── main.tf                     # Reuses production modules from ../../../aws/terraform/modules/
    ├── variables.tf                # Inherits standard parameters (enable_nat_gateway = false)
    ├── outputs.tf                  # Local resource outputs
    └── versions.tf                 # Terraform >= 1.5 & AWS Provider ~> 5.0
```

---

## 2. Quickstart Execution (PowerShell on Windows)

Make sure **Docker Desktop** is running, then execute:

```powershell
# Run the complete deployment, plan, apply, and security validation suite
powershell -File testing/aws/deploy-localstack.ps1
```

### Expected Output:
```
==================================================
AEGISMESH AWS ZERO-TRUST VALIDATION
==================================================

[AWS-01] Web Tier Architecture ........ PASS
[AWS-02] App Tier Private Isolation ... PASS
[AWS-03] DB Tier Isolation ............ PASS
[AWS-04] Web HTTPS Policy ............. PASS
[AWS-05] Web → App Policy ............. PASS
[AWS-06] App → DB Policy .............. PASS
[AWS-07] Web → DB Block ............... PASS
[AWS-08] DB Public Exposure Check ..... PASS

RESULT: 8/8 CONTROLS VALIDATED
==================================================
```

---

## 3. Teardown Instructions

When testing is complete, destroy the local simulated infrastructure and stop the Docker container:

```powershell
powershell -File testing/aws/destroy-localstack.ps1
```

---

## 4. Manual Step-by-Step Instructions (Alternative)

If you prefer executing the individual steps manually:

```powershell
# 1. Start LocalStack in background
docker compose -f testing/aws/docker-compose.yml up -d

# 2. Navigate to LocalStack Terraform directory
cd testing/aws/terraform-localstack

# 3. Initialize & Validate
terraform init
terraform validate
terraform plan
terraform apply -auto-approve

# 4. Run programmatic security verification
cd ../../..
python testing/aws/validate_aws_security.py

# 5. Clean up
cd testing/aws/terraform-localstack
terraform destroy -auto-approve
cd ../../..
docker compose -f testing/aws/docker-compose.yml down
```

---

## 5. Security & Safety Declarations

* **Local-Only:** Configured explicitly to communicate with `127.0.0.1:4566`.
* **Zero Cost:** No real AWS cloud resources are ever created or billed.
* **Separation of Concerns:** Does not modify or overwrite `aws/terraform/providers.tf` used for real cloud deployments.
