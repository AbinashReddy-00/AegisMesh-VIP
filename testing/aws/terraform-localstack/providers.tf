# ==============================================================================
# LocalStack Provider Configuration (Local Testing ONLY - Zero Cloud Cost)
# Explicitly directs all AWS API calls to the local LocalStack gateway (port 4566)
# ==============================================================================

provider "aws" {
  region                      = var.aws_region
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  s3_use_path_style           = true

  endpoints {
    ec2 = "http://localhost:4566"
    rds = "http://localhost:4566"
  }

  default_tags {
    tags = {
      Project       = "AegisMesh"
      Environment   = "localstack-simulation"
      SecurityModel = "Zero-Trust"
      TestingMode   = "Local-Empirical-Validation"
    }
  }
}
