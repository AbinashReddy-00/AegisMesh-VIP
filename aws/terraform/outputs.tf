# ==============================================================================
# AegisMesh Root Outputs
# ==============================================================================

output "vpc_id" {
  description = "The ID of the AegisMesh Zero-Trust VPC"
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = "The CIDR block of the VPC"
  value       = module.vpc.vpc_cidr_block
}

output "public_subnet_ids" {
  description = "IDs of the public web tier subnets"
  value       = module.vpc.public_subnet_ids
}

output "private_app_subnet_ids" {
  description = "IDs of the private application tier subnets"
  value       = module.vpc.private_app_subnet_ids
}

output "isolated_db_subnet_ids" {
  description = "IDs of the isolated database tier subnets (Air-Gapped)"
  value       = module.vpc.isolated_db_subnet_ids
}

output "db_subnet_group_name" {
  description = "Name of the RDS database subnet group"
  value       = module.vpc.db_subnet_group_name
}

output "web_security_group_id" {
  description = "Security Group ID for Web Tier"
  value       = module.security_groups.web_security_group_id
}

output "app_security_group_id" {
  description = "Security Group ID for Application Tier"
  value       = module.security_groups.app_security_group_id
}

output "db_security_group_id" {
  description = "Security Group ID for Database Tier"
  value       = module.security_groups.db_security_group_id
}
