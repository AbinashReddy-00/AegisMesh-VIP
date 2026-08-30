variable "name_prefix" {
  description = "Prefix applied to all resource names for consistent identification"
  type        = string
  default     = "aegismesh"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.1.0.0/16"

  validation {
    condition     = can(cidrnetmask(var.vpc_cidr))
    error_message = "The vpc_cidr value must be a valid CIDR block (e.g., 10.1.0.0/16)."
  }
}

variable "availability_zones" {
  description = "List of AWS availability zones for Multi-AZ redundancy"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]

  validation {
    condition     = length(var.availability_zones) >= 2
    error_message = "At least 2 availability zones must be specified for Multi-AZ resilience."
  }
}

variable "public_subnet_cidrs" {
  description = "List of CIDR blocks for public web tier subnets"
  type        = list(string)
  default     = ["10.1.1.0/24", "10.1.4.0/24"]
}

variable "private_app_subnet_cidrs" {
  description = "List of CIDR blocks for private application tier subnets"
  type        = list(string)
  default     = ["10.1.2.0/24", "10.1.5.0/24"]
}

variable "isolated_db_subnet_cidrs" {
  description = "List of CIDR blocks for isolated database tier subnets"
  type        = list(string)
  default     = ["10.1.3.0/24", "10.1.6.0/24"]
}

variable "enable_nat_gateway" {
  description = "Controls NAT Gateway provisioning for private subnets. Defaults to false for cost safety."
  type        = bool
  default     = false
}

variable "tags" {
  description = "Additional tags for VPC resources"
  type        = map(string)
  default     = {}
}
