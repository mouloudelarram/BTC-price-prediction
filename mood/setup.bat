@echo off
REM Quick setup script for crypto sentiment scraper

echo.
echo =========================================================
echo   Crypto Sentiment Data Sourcing - Setup
echo =========================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.11+
    pause
    exit /b 1
)

echo [1/3] Installing Python dependencies...
pip install -r data_sourcing_requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/3] Installing Playwright browsers...
playwright install chromium
if errorlevel 1 (
    echo ERROR: Failed to install Playwright browsers
    pause
    exit /b 1
)

echo.
echo [3/3] Verifying installation...
python -c "import playwright; import pydantic; import loguru; import tenacity; import httpx; print('✓ All dependencies verified')"
if errorlevel 1 (
    echo ERROR: Dependency verification failed
    pause
    exit /b 1
)

echo.
echo =========================================================
echo   ✓ Setup Complete!
echo =========================================================
echo.
echo Next steps:
echo   1. Edit data_sourcing/config.py (optional)
echo   2. Run: python -m data_sourcing.main
echo.
pause
