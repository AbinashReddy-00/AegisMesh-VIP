# AegisMesh — Unified End-to-End Security Validation Suite (PowerShell)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  RUNNING AEGISMESH UNIFIED END-TO-END VALIDATION SUITE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

python testing/end-to-end/run_e2e_tests.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[+] All End-to-End Security Scenarios Passed!" -ForegroundColor Green
} else {
    Write-Host "`n[!] End-to-End Security Scenarios Failed." -ForegroundColor Red
}
