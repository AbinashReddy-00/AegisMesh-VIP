# ==============================================================================
# LocalStack Terraform Runner — Reuses Production Modules from aws/terraform/
# ==============================================================================

# --- Module 1: 3-Tier Multi-AZ VPC ---
module "vpc" {
  source = "../../../aws/terraform/modules/vpc"

  name_prefix              = var.name_prefix
  vpc_cidr                 = var.vpc_cidr
  availability_zones       = var.availability_zones
  public_subnet_cidrs      = var.public_subnet_cidrs
  private_app_subnet_cidrs  = var.private_app_subnet_cidrs
  isolated_db_subnet_cidrs  = var.isolated_db_subnet_cidrs
  enable_nat_gateway       = var.enable_nat_gateway
  tags = {
    Environment = "localstack-simulation"
    ManagedBy   = "AegisMesh-Testing-Engine"
  }
}

# --- Module 2: Zero-Trust Security Groups ---
module "security_groups" {
  source = "../../../aws/terraform/modules/security-groups"

  name_prefix               = var.name_prefix
  vpc_id                    = module.vpc.vpc_id
  trusted_web_ingress_cidrs = var.trusted_web_ingress_cidrs
  enable_http               = var.enable_http
  app_port                  = var.app_port
  db_port                   = var.db_port
  tags = {
    Environment = "localstack-simulation"
    ManagedBy   = "AegisMesh-Testing-Engine"
  }
}
