#!/bin/bash

# Quick start script for the Mood Analysis API

echo "🚀 Mood Analysis API - Quick Start"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 --version | cut -d' ' -f2)
echo "✓ Python version: $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Setup environment
echo ""
echo "Setting up environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env file (edit with your settings)"
fi

mkdir -p logs output checkpoints

# Display next steps
echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration:"
echo "   nano .env"
echo ""
echo "2. Start the API:"
echo "   python run.py"
echo ""
echo "3. Open in browser:"
echo "   http://localhost:8000/docs"
echo ""
echo "4. Run tests (optional):"
echo "   bash run_tests.sh"
echo ""
echo "Or use Docker:"
echo "   docker-compose up -d"
