provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project       = "AegisMesh"
      ManagedBy     = "Terraform"
      Environment   = var.environment
      SecurityModel = "Zero-Trust"
      Framework     = "Cisco-VIP-2026"
    }
  }
}
