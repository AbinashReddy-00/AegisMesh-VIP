output "vpc_id" {
  description = "The ID of the AegisMesh VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "The CIDR block of the AegisMesh VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "List of IDs of the public web tier subnets"
  value       = aws_subnet.public[*].id
}

output "private_app_subnet_ids" {
  description = "List of IDs of the private application tier subnets"
  value       = aws_subnet.private_app[*].id
}

output "isolated_db_subnet_ids" {
  description = "List of IDs of the isolated database tier subnets"
  value       = aws_subnet.isolated_db[*].id
}

output "db_subnet_group_name" {
  description = "Name of the RDS database subnet group"
  value       = aws_db_subnet_group.db_group.name
}

output "internet_gateway_id" {
  description = "The ID of the Internet Gateway"
  value       = aws_internet_gateway.igw.id
}

output "nat_gateway_id" {
  description = "The ID of the NAT Gateway (if enabled)"
  value       = var.enable_nat_gateway ? aws_nat_gateway.nat[0].id : null
}
