#!/usr/bin/env pwsh
# Quick run script for crypto sentiment scraper (Windows PowerShell)

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Crypto Sentiment Data Sourcing - Pipeline Running" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

python -m data_sourcing.main

Write-Host ""
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Pipeline failed - check logs in data_sourcing/output/" -ForegroundColor Red
} else {
    Write-Host "✓ Pipeline complete! Check data_sourcing/output/ for results." -ForegroundColor Green
}
Write-Host ""
Read-Host "Press Enter to exit"
