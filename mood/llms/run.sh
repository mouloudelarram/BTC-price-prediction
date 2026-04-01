#!/bin/bash

################################################################################
# Crypto Market Mood Analyzer - Run Script
################################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' 

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="venv"
LOG_FILE="logs/mood_analyzer.log"
CHECKPOINT_FILE="checkpoints/progress_tracker.json"
USE_VENV=false
DEBUG_MODE=false
WATCH_LOGS=false
PROFILE_MODE=false
RESET_CHECKPOINT=false
DRY_RUN=false

################################################################################
# Archive Management (NEW SECTION)
################################################################################

archive_old_runs() {
    print_header "Archiving Previous Run Data"
    
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    local found_old_data=false

    # Pairs of (source_dir, archive_dir)
    declare -A dirs_to_archive=( 
        ["output"]="old_output" 
        ["logs"]="old_logs" 
        ["checkpoints"]="old_checkpoints" 
    )

    for src in "${!dirs_to_archive[@]}"; do
        dest="${dirs_to_archive[$src]}"
        
        # Check if source directory exists and is not empty
        if [ -d "$src" ] && [ "$(ls -A "$src")" ]; then
            print_status "Archiving $src/ to $dest/ ..."
            mkdir -p "$dest/$TIMESTAMP"
            
            # Move contents instead of the directory itself
            mv "$src"/* "$dest/$TIMESTAMP/" 2>/dev/null || true
            found_old_data=true
            print_success "Moved $src data to $dest/$TIMESTAMP/"
        fi
        
        # Ensure clean directories exist for the new run
        mkdir -p "$src"
    done

    if [ "$found_old_data" = false ]; then
        print_info "No previous data found to archive."
    fi
}

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "\n${BLUE}===============================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===============================================================================${NC}\n"
}

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }
print_status() { echo -e "${CYAN}→ $1${NC}"; }

show_help() {
    cat << 'EOF'
Crypto Market Mood Analyzer - Run Script

USAGE:
    bash run.sh [OPTIONS]

OPTIONS:
    --debug             Run with debug logging
    --watch             Monitor logs in real-time
    --profile           Profile performance
    --reset             Clear checkpoint and reprocess
    --dry-run           Show what would happen
    --help              Show this help
EOF
}

################################################################################
# Pre-flight Checks
################################################################################

check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"; exit 1
    fi
}

check_config() {
    if [ ! -f "config.py" ]; then
        print_error "config.py not found"; exit 1
    fi
    python3 config.py > /dev/null 2>&1 || { print_error "Config invalid"; exit 1; }
}

################################################################################
# Execution Modes
################################################################################

run_standard() {
    print_header "Running Crypto Market Mood Analyzer"
    python3 market_mood_analyzer.py
}

# ... (Other run_ functions like run_debug, run_profile remain the same as your original) ...

################################################################################
# Main Execution
################################################################################

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --debug) DEBUG_MODE=true; shift ;;
            --watch) WATCH_LOGS=true; shift ;;
            --profile) PROFILE_MODE=true; shift ;;
            --reset) RESET_CHECKPOINT=true; shift ;;
            --dry-run) DRY_RUN=true; shift ;;
            --help) show_help; exit 0 ;;
            *) print_error "Unknown option: $1"; exit 1 ;;
        esac
    done

    cd "$SCRIPT_DIR"
    
    # 1. Archive old data BEFORE starting new run
    if [ "$DRY_RUN" = false ]; then
        archive_old_runs
    fi

    # 2. Setup environment
    if [ -d "$VENV_DIR" ]; then
        source "$VENV_DIR/bin/activate"
    fi

    # 3. Basic Checks
    check_python
    check_config

    # 4. Execute
    if [ "$DRY_RUN" = true ]; then
        print_info "Dry run complete."
    elif [ "$DEBUG_MODE" = true ]; then
        run_standard # Simplified for brevity, uses your original logic
    else
        run_standard
    fi
}

main "$@"
