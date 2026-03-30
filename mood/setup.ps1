#!/usr/bin/env pwsh
# Quick setup script for crypto sentiment scraper (Windows PowerShell)

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Crypto Sentiment Data Sourcing - Setup" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found. Please install Python 3.11+" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[1/3] Installing Python dependencies..." -ForegroundColor Yellow
pip install -r data_sourcing_requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[2/3] Installing Playwright browsers..." -ForegroundColor Yellow
playwright install chromium
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install Playwright browsers" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[3/3] Verifying installation..." -ForegroundColor Yellow
python -c "import playwright; import pydantic; import loguru; import tenacity; import httpx; print('✓ All dependencies verified')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Dependency verification failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   ✓ Setup Complete!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Green
Write-Host "   1. Edit data_sourcing/config.py (optional)" -ForegroundColor White
Write-Host "   2. Run: python -m data_sourcing.main" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"
