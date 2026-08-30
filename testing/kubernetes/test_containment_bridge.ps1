# AegisMesh — Dynamic Kubernetes Containment Bridge Test (PowerShell)
# Tests the full end-to-end loop: Decision ISOLATE -> K8s NetworkPolicy -> Calico Dropping -> Release

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  AEGISMESH — DYNAMIC KUBERNETES CONTAINMENT BRIDGE TEST" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

python testing/kubernetes/test_containment_bridge.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[+] Integration Test Suite Completed Successfully!" -ForegroundColor Green
} else {
    Write-Host "`n[!] Integration Test Suite Failed." -ForegroundColor Red
}
