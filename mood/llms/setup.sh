#!/bin/bash

################################################################################
# Crypto Market Mood Analyzer - Setup Script
#
# This script initializes the project environment by:
# 1. Checking Python version
# 2. Creating necessary directories
# 3. Setting up virtual environment (optional)
# 4. Installing Python dependencies
# 5. Validating configuration
# 6. Checking Ollama connectivity
#
# Usage:
#   bash setup.sh              # Standard setup
#   bash setup.sh --venv       # Create virtual environment
#   bash setup.sh --help       # Show this help
#
################################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PYTHON_MIN_VERSION="3.8"
VENV_DIR="venv"
USE_VENV=false
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "\n${BLUE}===============================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===============================================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

show_help() {
    cat << 'EOF'
Crypto Market Mood Analyzer - Setup Script

USAGE:
    bash setup.sh [OPTIONS]

OPTIONS:
    --venv              Create and use a Python virtual environment
    --no-checks         Skip Ollama connectivity check
    --help              Show this help message

EXAMPLES:
    # Standard setup (uses system Python)
    bash setup.sh

    # Setup with virtual environment
    bash setup.sh --venv

    # Setup without Ollama check
    bash setup.sh --no-checks

DESCRIPTION:
    This script prepares the environment for running the Mood Analyzer by:
    • Verifying Python 3.8+ is available
    • Creating required directories
    • Installing Python dependencies from requirements.txt
    • Validating configuration files
    • Testing Ollama API connectivity

REQUIREMENTS:
    • Python 3.8 or later
    • pip package manager
    • Ollama (running locally or on accessible network)
    • Internet connection (for package downloads)

AFTER SETUP:
    Run the analyzer with:
        python market_mood_analyzer.py
    
    Or use the provided run script:
        bash run.sh

EOF
}

################################################################################
# Version Checking
################################################################################

check_python_version() {
    print_header "Checking Python Version"

    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        echo "Install Python 3.8+ from: https://www.python.org/downloads/"
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        print_error "Python 3.8+ is required (found: $PYTHON_VERSION)"
        exit 1
    fi

    print_success "Python $PYTHON_VERSION is installed"
}

################################################################################
# Dependency Installation
################################################################################

install_dependencies() {
    print_header "Installing Python Dependencies"

    if [ "$USE_VENV" = true ]; then
        if [ ! -d "$VENV_DIR" ]; then
            print_info "Creating virtual environment: $VENV_DIR"
            python3 -m venv "$VENV_DIR"
            print_success "Virtual environment created"
        else
            print_info "Virtual environment already exists"
        fi

        # Activate virtual environment
        source "$VENV_DIR/bin/activate"
        PYTHON_CMD="python"
        PIP_CMD="pip"
        print_success "Virtual environment activated"
    else
        PYTHON_CMD="python3"
        PIP_CMD="pip3"
        print_info "Using system Python (not using virtual environment)"
    fi

    # Upgrade pip
    print_info "Upgrading pip..."
    $PIP_CMD install --upgrade pip setuptools wheel > /dev/null 2>&1 || true
    print_success "pip upgraded"

    # Install requirements
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found in $SCRIPT_DIR"
        exit 1
    fi

    print_info "Installing packages from requirements.txt..."
    $PIP_CMD install -r requirements.txt

    print_success "All Python dependencies installed"
}

################################################################################
# Directory Setup
################################################################################

setup_directories() {
    print_header "Setting Up Directories"

    DIRS=("checkpoints" "logs" "output" "test_data")

    for dir in "${DIRS[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir/"
        else
            print_info "Directory already exists: $dir/"
        fi
    done

    # Ensure directories are writable
    for dir in "${DIRS[@]}"; do
        if [ ! -w "$dir" ]; then
            print_warning "Directory not writable: $dir/ (trying to fix...)"
            chmod u+w "$dir" 2>/dev/null || print_warning "Could not modify permissions for $dir/"
        fi
    done
}

################################################################################
# Configuration Validation
################################################################################

validate_config() {
    print_header "Validating Configuration"

    if [ ! -f "config.py" ]; then
        print_error "config.py not found"
        exit 1
    fi

    print_info "Validating config.py..."

    # Use Python to validate config
    python3 << 'PYTHON_SCRIPT'
import sys
try:
    import config
    if config.validate_config():
        print("Configuration validation: OK")
        sys.exit(0)
    else:
        print("Configuration validation: FAILED")
        sys.exit(1)
except Exception as e:
    print(f"Error validating configuration: {e}")
    sys.exit(1)
PYTHON_SCRIPT

    CONFIG_RESULT=$?
    if [ $CONFIG_RESULT -eq 0 ]; then
        print_success "Configuration is valid"
    else
        print_error "Configuration validation failed"
        exit 1
    fi
}

################################################################################
# Ollama Connectivity Check
################################################################################

check_ollama() {
    print_header "Checking Ollama Connectivity"

    OLLAMA_URL="http://localhost:11434"
    print_info "Checking Ollama at $OLLAMA_URL..."

    if command -v curl &> /dev/null; then
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$OLLAMA_URL/api/tags" 2>/dev/null || echo "000")

        if [ "$RESPONSE" = "200" ]; then
            print_success "Ollama is running and accessible"

            # List available models
            print_info "Available models:"
            curl -s "$OLLAMA_URL/api/tags" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if 'models' in data:
        for model in data['models']:
            print(f\"  • {model.get('name', 'unknown')}\")
    else:
        print('  No models found')
except:
    print('  (Could not parse model list)')
" || true

            return 0
        else
            print_warning "Ollama is not responding (HTTP $RESPONSE)"
            print_info "Make sure Ollama is running: ollama serve"
            return 1
        fi
    else
        print_warning "curl not found, skipping Ollama check"
        print_info "You can verify Ollama manually with: curl http://localhost:11434/api/tags"
        return 1
    fi
}

################################################################################
# Final Summary
################################################################################

print_summary() {
    print_header "Setup Complete"

    echo -e "${GREEN}Environment is ready!${NC}\n"

    echo "Next steps:"
    echo "  1. Verify your data is in: ../scrapper/data_sourcing/output/"
    echo "  2. Customize config.py if needed (MODEL_MAPPING, PLATFORM_WEIGHTS, etc.)"
    echo "  3. Run the analyzer:"
    echo ""

    if [ "$USE_VENV" = true ]; then
        echo "    source $VENV_DIR/bin/activate  # Activate virtual environment"
        echo "    python market_mood_analyzer.py  # Run analyzer"
        echo ""
        echo "  Or use the run script:"
        echo "    bash run.sh"
    else
        echo "    python3 market_mood_analyzer.py"
        echo ""
        echo "  Or use the run script:"
        echo "    bash run.sh"
    fi

    echo ""
    echo "For more information:"
    echo "  • README.md          - Full documentation"
    echo "  • QUICK_REFERENCE.md - Common tasks and commands"
    echo "  • config.py          - Configuration options"
    echo "  • examples.py        - Usage examples"
    echo ""
}

################################################################################
# Main Execution
################################################################################

main() {
    print_header "Crypto Market Mood Analyzer - Setup"

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --venv)
                USE_VENV=true
                shift
                ;;
            --no-checks)
                NO_CHECKS=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Execute setup steps
    check_python_version
    setup_directories
    install_dependencies
    validate_config

    # Check Ollama (unless disabled)
    if [ "$NO_CHECKS" != "true" ]; then
        check_ollama || print_warning "Ollama is not available. You can start it with: ollama serve"
    else
        print_info "Skipping Ollama check (--no-checks)"
    fi

    # Print summary
    print_summary

    print_success "Setup completed successfully!"
    exit 0
}

# Run main function
main "$@"
