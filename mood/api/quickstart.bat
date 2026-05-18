@echo off
REM Quick start script for the Mood Analysis API

echo 🚀 Mood Analysis API - Quick Start
echo ==================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.11 or higher.
    exit /b 1
)

echo ✓ Python is installed

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Setup environment
echo.
echo Setting up environment...
if not exist .env (
    copy .env.example .env
    echo ✓ Created .env file (edit with your settings)
)

if not exist logs mkdir logs
if not exist output mkdir output
if not exist checkpoints mkdir checkpoints

REM Display next steps
echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file with your configuration
echo 2. Start the API:
echo    python run.py
echo 3. Open in browser:
echo    http://localhost:8000/docs
echo.
echo Or use Docker:
echo    docker-compose up -d
