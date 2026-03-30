@echo off
REM Quick run script for crypto sentiment scraper

echo.
echo =========================================================
echo   Crypto Sentiment Data Sourcing - Pipeline Running
echo =========================================================
echo.


python -m data_sourcing.main

echo.
if errorlevel 1 (
    echo ✗ Pipeline failed - check logs in data_sourcing/output/
) else (
    echo ✓ Pipeline complete! Check data_sourcing/output/ for results.
)
echo.
pause
