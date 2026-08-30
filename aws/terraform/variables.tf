# ==============================================================================
# AegisMesh Root Terraform Variables
# ==============================================================================

variable "aws_region" {
  description = "Target AWS Region for Infrastructure deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment name (e.g. dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "name_prefix" {
  description = "Resource naming prefix across all AegisMesh AWS resources"
  type        = string
  default     = "aegismesh"
}

variable "vpc_cidr" {
  description = "Base IPv4 CIDR block for the AegisMesh VPC"
  type        = string
  default     = "10.1.0.0/16"

  validation {
    condition     = can(cidrnetmask(var.vpc_cidr))
    error_message = "Must be a valid IPv4 CIDR block (e.g. 10.1.0.0/16)."
  }
}

variable "availability_zones" {
  description = "List of Availability Zones for Multi-AZ redundancy"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "public_subnet_cidrs" {
  description = "Public Web tier CIDR blocks"
  type        = list(string)
  default     = ["10.1.1.0/24", "10.1.4.0/24"]
}

variable "private_app_subnet_cidrs" {
  description = "Private Application tier CIDR blocks"
  type        = list(string)
  default     = ["10.1.2.0/24", "10.1.5.0/24"]
}

variable "isolated_db_subnet_cidrs" {
  description = "Isolated Database tier CIDR blocks"
  type        = list(string)
  default     = ["10.1.3.0/24", "10.1.6.0/24"]
}

variable "enable_nat_gateway" {
  description = "Enables NAT Gateway provisioning. Defaults to false to avoid unexpected AWS cloud charges."
  type        = bool
  default     = false
}

variable "trusted_web_ingress_cidrs" {
  description = "CIDRs permitted to reach public web tier on port 443"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "enable_http" {
  description = "Enables plain HTTP (port 80) on Web tier if true. Defaults to false."
  type        = bool
  default     = false
}

variable "app_port" {
  description = "TCP port on which application backend listens"
  type        = number
  default     = 8000
}

variable "db_port" {
  description = "TCP port for isolated database tier (e.g. 5432 for PostgreSQL)"
  type        = number
  default     = 5432
}

variable "tags" {
  description = "Custom metadata tags to merge into all resources"
  type        = map(string)
  default     = {}
}
