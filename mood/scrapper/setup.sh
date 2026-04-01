#!/bin/bash
# Quick setup script for crypto sentiment scraper (Linux/macOS)

echo
echo "========================================================="
echo "  Crypto Sentiment Data Sourcing - Setup"
echo "========================================================="
echo

# Find Python
PYTHON_CMD=$(command -v python3 || command -v python)
if [[ -z "$PYTHON_CMD" ]]; then
    echo "ERROR: Python not found. Please install Python 3.11+"
    exit 1
fi

# Check Python version (accept pre-releases)
PY_VERSION=$($PYTHON_CMD -c 'import sys; v=sys.version_info; print(f"{v[0]}.{v[1]}")')
REQUIRED_MAJOR=3
REQUIRED_MINOR=11

PY_MAJOR=$(echo $PY_VERSION | cut -d. -f1)
PY_MINOR=$(echo $PY_VERSION | cut -d. -f2)

if (( PY_MAJOR < REQUIRED_MAJOR || (PY_MAJOR == REQUIRED_MAJOR && PY_MINOR < REQUIRED_MINOR) )); then
    echo "ERROR: Python 3.11+ required, found $PY_VERSION"
    exit 1
fi

echo "[1/3] Installing Python dependencies..."
if ! $PYTHON_CMD -m pip install --upgrade pip; then
    echo "ERROR: Failed to upgrade pip"
    exit 1
fi

if ! $PYTHON_CMD -m pip install -r data_sourcing_requirements.txt; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo "[2/3] Installing Playwright browsers..."
if ! $PYTHON_CMD -m playwright install chromium; then
    echo "ERROR: Failed to install Playwright browsers"
    exit 1
fi

echo "[3/3] Verifying installation..."
if ! $PYTHON_CMD -c "import playwright; import pydantic; import loguru; import tenacity; import httpx; print('✓ All dependencies verified')"; then
    echo "ERROR: Dependency verification failed"
    exit 1
fi

echo
echo "========================================================="
echo "  ✓ Setup Complete!"
echo "========================================================="
echo
echo "Next steps:"
echo "  1. Edit data_sourcing/config.py (optional)"
echo "  2. Run: $PYTHON_CMD -m data_sourcing.main"
echo

read -p "Press [Enter] to continue..."
