#!/bin/bash

# Run tests for the Mood Analysis API

set -e

echo "🧪 Running API Tests"
echo "===================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.example .env
fi

# Install test dependencies
echo "Installing test dependencies..."
pip install pytest pytest-asyncio httpx

# Run tests
echo ""
echo "Running tests..."
python -m pytest tests.py -v -s

echo ""
echo "✅ Tests completed!"
