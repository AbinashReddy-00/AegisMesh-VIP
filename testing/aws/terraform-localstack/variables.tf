# ==============================================================================
# LocalStack Terraform Variables (Inherits from core architecture)
# ==============================================================================

variable "aws_region" {
  description = "Target region for local LocalStack simulation"
  type        = string
  default     = "us-east-1"
}

variable "name_prefix" {
  description = "Resource naming prefix"
  type        = string
  default     = "aegismesh"
}

variable "vpc_cidr" {
  description = "CIDR block for the local simulated VPC"
  type        = string
  default     = "10.1.0.0/16"
}

variable "availability_zones" {
  description = "List of simulated Availability Zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public web tier subnets"
  type        = list(string)
  default     = ["10.1.1.0/24", "10.1.4.0/24"]
}

variable "private_app_subnet_cidrs" {
  description = "CIDR blocks for private application tier subnets"
  type        = list(string)
  default     = ["10.1.2.0/24", "10.1.5.0/24"]
}

variable "isolated_db_subnet_cidrs" {
  description = "CIDR blocks for isolated database tier subnets"
  type        = list(string)
  default     = ["10.1.3.0/24", "10.1.6.0/24"]
}

variable "enable_nat_gateway" {
  description = "NAT Gateway toggle. Kept false for local simplicity and zero cost."
  type        = bool
  default     = false
}

variable "trusted_web_ingress_cidrs" {
  description = "CIDRs permitted to reach web tier on port 443"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "enable_http" {
  description = "Enables plain HTTP on web tier if true. Defaults to false (HTTPS-only Zero Trust)."
  type        = bool
  default     = false
}

variable "app_port" {
  description = "Application tier listening port"
  type        = number
  default     = 8000
}

variable "db_port" {
  description = "Database tier listening port"
  type        = number
  default     = 5432
}
