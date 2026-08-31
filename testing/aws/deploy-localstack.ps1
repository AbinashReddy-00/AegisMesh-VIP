# ==============================================================================
# AegisMesh — LocalStack AWS Zero-Trust Deployment & Test Runner (PowerShell)
# Safe, local-only simulation. Incurs $0 cost. No AWS credentials needed.
# ==============================================================================

Write-Host '============================================================' -ForegroundColor Cyan
Write-Host '  AEGISMESH — LOCALSTACK ZERO-TRUST AWS DEPLOYMENT' -ForegroundColor Cyan
Write-Host '============================================================' -ForegroundColor Cyan

# 1. Start LocalStack
Write-Host ''
Write-Host '[STEP 1/6] Starting LocalStack / AWS Mock Container...' -ForegroundColor Yellow
docker compose -f "$PSScriptRoot/docker-compose.yml" up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host '[!] Failed to start Docker Compose. Is Docker Desktop running?' -ForegroundColor Red
    exit 1
}

# 2. Wait for LocalStack Health
Write-Host ''
Write-Host '[STEP 2/6] Waiting for LocalStack Gateway Health (http://localhost:4566)...' -ForegroundColor Yellow
$retries = 0
$healthy = $false
while ($retries -lt 20) {
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect('127.0.0.1', 4566)
        if ($tcp.Connected) {
            $tcp.Close()
            $healthy = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 1
        $retries++
    }
}

if (-not $healthy) {
    Write-Host '[!] LocalStack failed to become ready in time.' -ForegroundColor Red
    exit 1
}
Write-Host ' -> Local AWS Mock Gateway is ONLINE and healthy!' -ForegroundColor Green

# 3. Initialize Terraform for LocalStack
Write-Host ''
Write-Host '[STEP 3/6] Initializing Terraform for LocalStack...' -ForegroundColor Yellow
$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')
Push-Location "$PSScriptRoot/terraform-localstack"
terraform init -reconfigure

if ($LASTEXITCODE -ne 0) {
    Write-Host '[!] Terraform init failed.' -ForegroundColor Red
    Pop-Location
    exit 1
}

# 4. Validate and Plan
Write-Host ''
Write-Host '[STEP 4/6] Validating and Planning LocalStack Configuration...' -ForegroundColor Yellow
terraform validate
if ($LASTEXITCODE -ne 0) {
    Write-Host '[!] Terraform validation failed.' -ForegroundColor Red
    Pop-Location
    exit 1
}

terraform plan -out tfplan.local
if ($LASTEXITCODE -ne 0) {
    Write-Host '[!] Terraform plan failed.' -ForegroundColor Red
    Pop-Location
    exit 1
}

# 5. Apply strictly to LocalStack
Write-Host ''
Write-Host '[STEP 5/6] Applying 3-Tier Infrastructure to LocalStack...' -ForegroundColor Yellow
terraform apply -auto-approve tfplan.local
if ($LASTEXITCODE -ne 0) {
    Write-Host '[!] Terraform apply failed.' -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

# 6. Run Security Validation
Write-Host ''
Write-Host '[STEP 6/6] Executing AWS Zero-Trust Security Validation Suite...' -ForegroundColor Yellow
python "$PSScriptRoot/validate_aws_security.py"

if ($LASTEXITCODE -eq 0) {
    Write-Host ''
    Write-Host '[+] LocalStack AWS Infrastructure Deployed and 100% Validated!' -ForegroundColor Green
} else {
    Write-Host ''
    Write-Host '[!] Some Zero-Trust controls failed validation.' -ForegroundColor Red
}
