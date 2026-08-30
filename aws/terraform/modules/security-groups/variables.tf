variable "name_prefix" {
  description = "Prefix applied to all security group names"
  type        = string
  default     = "aegismesh"
}

variable "vpc_id" {
  description = "The ID of the VPC where security groups will be provisioned"
  type        = string
}

variable "trusted_web_ingress_cidrs" {
  description = "List of trusted CIDR blocks allowed to access the public Web tier over HTTPS (443)"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "enable_http" {
  description = "Allows insecure HTTP (port 80) ingress to Web tier if true. Defaults to false (HTTPS-only Zero Trust)."
  type        = bool
  default     = false
}

variable "app_port" {
  description = "TCP port on which application backend services listen (e.g. 8000 for FastAPI / 8080 for Microservices)"
  type        = number
  default     = 8000
}

variable "db_port" {
  description = "TCP port for isolated database tier (e.g. 5432 for PostgreSQL)"
  type        = number
  default     = 5432
}

variable "tags" {
  description = "Additional tags for security group resources"
  type        = map(string)
  default     = {}
}
