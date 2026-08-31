# ==============================================================================
# AegisMesh — LocalStack Teardown Runner (PowerShell)
# Cleans up local simulated AWS resources and shuts down Docker container
# ==============================================================================

Write-Host '============================================================' -ForegroundColor Cyan
Write-Host '  AEGISMESH — LOCALSTACK TEARDOWN' -ForegroundColor Cyan
Write-Host '============================================================' -ForegroundColor Cyan

# 1. Destroy Terraform Resources in LocalStack
Write-Host ''
Write-Host '[STEP 1/2] Destroying LocalStack Terraform Resources...' -ForegroundColor Yellow
$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')

if (Test-Path "$PSScriptRoot/terraform-localstack") {
    Push-Location "$PSScriptRoot/terraform-localstack"
    if (Test-Path 'terraform.tfstate') {
        terraform destroy -auto-approve
    }
    if (Test-Path 'tfplan.local') {
        Remove-Item 'tfplan.local' -Force
    }
    Pop-Location
}

# 2. Stop LocalStack Container
Write-Host ''
Write-Host '[STEP 2/2] Stopping LocalStack Container...' -ForegroundColor Yellow
docker compose -f "$PSScriptRoot/docker-compose.yml" down

Write-Host ''
Write-Host '[+] LocalStack environment cleanly destroyed!' -ForegroundColor Green
