#!/bin/bash

# Setup and run the Mood Analysis API
set -e

echo "🚀 Setting up Mood Analysis API..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created. Please edit it with your configuration."
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p logs output checkpoints

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✓ Setup complete!"
echo ""
echo "To start the API, run:"
echo "  python run.py"
echo ""
echo "Or with Docker:"
echo "  docker-compose up -d"
echo ""
echo "API will be available at http://localhost:8000"
echo "Documentation at http://localhost:8000/docs"
