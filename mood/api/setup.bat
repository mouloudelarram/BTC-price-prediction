@echo off
REM Setup and run the Mood Analysis API

echo 🚀 Setting up Mood Analysis API...

REM Check if .env file exists
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo ✓ .env file created. Please edit it with your configuration.
)

REM Create necessary directories
echo Creating directories...
if not exist logs mkdir logs
if not exist output mkdir output
if not exist checkpoints mkdir checkpoints

REM Install dependencies
echo Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo ✓ Setup complete!
echo.
echo To start the API, run:
echo   python run.py
echo.
echo Or with Docker:
echo   docker-compose up -d
echo.
echo API will be available at http://localhost:8000
echo Documentation at http://localhost:8000/docs
