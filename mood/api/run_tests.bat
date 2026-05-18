@echo off
REM Run tests for the Mood Analysis API

echo 🧪 Running API Tests
echo ====================

REM Check if .env exists
if not exist .env (
    echo Creating .env from template...
    copy .env.example .env
)

REM Install test dependencies
echo Installing test dependencies...
python -m pip install pytest pytest-asyncio httpx

REM Run tests
echo.
echo Running tests...
python -m pytest tests.py -v -s

echo.
echo ✅ Tests completed!
