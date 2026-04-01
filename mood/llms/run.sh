#!/bin/bash

################################################################################
# Crypto Market Mood Analyzer - Run Script
#
# This script provides convenient ways to run the mood analyzer with various
# options for monitoring, debugging, and configuration.
#
# Usage:
#   bash run.sh              # Standard run
#   bash run.sh --debug      # Run with debug logging
#   bash run.sh --watch      # Run with log monitoring
#   bash run.sh --profile    # Profile performance
#   bash run.sh --reset      # Reset checkpoints and run fresh
#   bash run.sh --help       # Show this help
#
################################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

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

print_status() {
    echo -e "${CYAN}→ $1${NC}"
}

show_help() {
    cat << 'EOF'
Crypto Market Mood Analyzer - Run Script

USAGE:
    bash run.sh [OPTIONS]

OPTIONS:
    --debug             Run with debug logging (very verbose)
    --watch             Monitor logs in real-time while running
    --profile           Profile execution time and performance
    --reset             Clear checkpoint and reprocess all data
    --dry-run           Show what would happen without running
    --no-ollama-check   Skip Ollama connectivity check
    --help              Show this help message

EXAMPLES:
    # Standard run (respects checkpoints)
    bash run.sh

    # Debug mode with verbose logging
    bash run.sh --debug

    # Watch logs while running
    bash run.sh --watch

    # Profile performance
    bash run.sh --profile

    # Start fresh (clear checkpoint)
    bash run.sh --reset

    # Combined: debug + watch logs
    bash run.sh --debug --watch

ENVIRONMENT:
    The script automatically detects if a virtual environment exists.
    If found, it will be activated before running.

STATUS CHECKS:
    Before running, the script verifies:
    • Python is available
    • Dependencies are installed
    • Configuration is valid
    • Ollama is running
    • Required directories exist

MONITORING:
    View logs while running:
        tail -f logs/mood_analyzer.log

    Check checkpoint status:
        cat checkpoints/progress_tracker.json | python -m json.tool

    View latest report:
        cat output/final_mood_report.json | python -m json.tool

TROUBLESHOOTING:
    If the script fails:
    1. Check logs/mood_analyzer.log for error messages
    2. Verify Ollama is running: curl http://localhost:11434/api/tags
    3. Ensure dependencies are installed: bash setup.sh
    4. Check configuration: python config.py

EOF
}

################################################################################
# Pre-flight Checks
################################################################################

check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    print_success "Python is available"
}

check_directories() {
    for dir in "checkpoints" "logs" "output"; do
        if [ ! -d "$dir" ]; then
            print_info "Creating directory: $dir/"
            mkdir -p "$dir"
        fi
    done
    print_success "Required directories exist"
}

check_config() {
    if [ ! -f "config.py" ]; then
        print_error "config.py not found"
        exit 1
    fi

    print_info "Validating configuration..."
    python3 config.py > /dev/null 2>&1 || {
        print_error "Configuration validation failed"
        python3 config.py
        exit 1
    }
    print_success "Configuration is valid"
}

check_dependencies() {
    print_info "Checking Python dependencies..."

    python3 << 'PYTHON_SCRIPT'
import sys
try:
    import aiohttp
    print("OK")
except ImportError as e:
    print(f"MISSING: {e}")
    sys.exit(1)
PYTHON_SCRIPT

    if [ $? -ne 0 ]; then
        print_error "Required packages not installed"
        print_info "Run setup first: bash setup.sh"
        exit 1
    fi

    print_success "All dependencies are installed"
}

check_ollama() {
    print_info "Checking Ollama connectivity..."

    if command -v curl &> /dev/null; then
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:11434/api/tags" 2>/dev/null || echo "000")

        if [ "$RESPONSE" = "200" ]; then
            print_success "Ollama is running"
            return 0
        else
            print_warning "Ollama is not responding (HTTP $RESPONSE)"
            return 1
        fi
    else
        print_warning "curl not available, skipping Ollama check"
        print_info "Manually verify with: curl http://localhost:11434/api/tags"
        return 1
    fi
}

check_data() {
    if [ ! -d "../scrapper/data_sourcing/output" ]; then
        print_warning "Data directory not found: ../scrapper/data_sourcing/output"
        print_info "The analyzer will create a test dataset if none exists"
        return 1
    else
        FILE_COUNT=$(find ../scrapper/data_sourcing/output -name "*.json" 2>/dev/null | wc -l || echo 0)
        if [ "$FILE_COUNT" -gt 0 ]; then
            print_success "Found $FILE_COUNT JSON files in data directory"
            return 0
        else
            print_warning "Data directory is empty"
            return 1
        fi
    fi
}

run_preflight_checks() {
    print_header "Pre-flight Checks"

    check_python
    check_directories
    check_config
    check_dependencies

    if [ "$NO_OLLAMA_CHECK" != "true" ]; then
        check_ollama || print_warning "Ollama check failed, but continuing..."
    fi

    check_data || print_warning "Data not found, but continuing..."

    print_success "All checks passed!"
}

################################################################################
# Virtual Environment Setup
################################################################################

setup_environment() {
    if [ -d "$VENV_DIR" ]; then
        print_info "Found virtual environment: $VENV_DIR"
        source "$VENV_DIR/bin/activate"
        USE_VENV=true
        print_success "Virtual environment activated"
    else
        print_info "No virtual environment found (using system Python)"
    fi
}

################################################################################
# Checkpoint Management
################################################################################

reset_checkpoint() {
    if [ -f "$CHECKPOINT_FILE" ]; then
        print_warning "Resetting checkpoint..."
        rm "$CHECKPOINT_FILE"
        print_success "Checkpoint cleared - all entries will be reprocessed"
    else
        print_info "No checkpoint found (starting fresh)"
    fi
}

show_checkpoint_status() {
    if [ -f "$CHECKPOINT_FILE" ]; then
        print_info "Current checkpoint status:"
        python3 << 'PYTHON_SCRIPT'
import json
try:
    with open('checkpoints/progress_tracker.json') as f:
        data = json.load(f)
        processed = len(data.get('processed_ids', []))
        failed = len(data.get('failed_ids', {}))
        print(f"  Processed entries: {processed}")
        print(f"  Failed entries: {failed}")
        print(f"  Total: {processed + failed}")
except:
    print("  Could not read checkpoint")
PYTHON_SCRIPT
    else
        print_info "No checkpoint found (starting fresh)"
    fi
}

################################################################################
# Execution Modes
################################################################################

run_standard() {
    print_header "Running Crypto Market Mood Analyzer"

    print_status "Starting analysis..."
    python3 market_mood_analyzer.py
    RESULT=$?

    return $RESULT
}

run_debug() {
    print_header "Running with Debug Logging"

    print_status "Starting analysis with DEBUG logging..."
    PYTHONUNBUFFERED=1 python3 << 'PYTHON_SCRIPT'
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

import config
config.LOG_LEVEL = "DEBUG"

import asyncio
from market_mood_analyzer import MoodAnalyzer

async def main():
    analyzer = MoodAnalyzer(config)
    result = await analyzer.run()
    return result

result = asyncio.run(main())
print(f"\nFinal Mood Score: {result}")
PYTHON_SCRIPT

    RESULT=$?
    return $RESULT
}

run_with_watch() {
    print_header "Running with Log Monitoring"

    # Start the analyzer in the background
    print_status "Starting analyzer in background..."
    python3 market_mood_analyzer.py > /dev/null 2>&1 &
    PID=$!
    print_success "Analyzer running (PID: $PID)"

    # Give it a moment to start
    sleep 2

    print_status "Monitoring logs (Ctrl+C to stop)..."
    echo ""

    # Watch the log file
    if command -v tail &> /dev/null; then
        tail -f "$LOG_FILE" &
        TAIL_PID=$!

        # Wait for analyzer to finish
        wait $PID
        RESULT=$?

        # Stop tail
        kill $TAIL_PID 2>/dev/null || true
    else
        # Fallback if tail is not available
        wait $PID
        RESULT=$?
    fi

    return $RESULT
}

run_profile() {
    print_header "Running with Performance Profiling"

    print_status "Starting profiled analysis..."
    python3 << 'PYTHON_SCRIPT'
import time
import asyncio
import config
from market_mood_analyzer import MoodAnalyzer

async def main():
    start_time = time.time()

    analyzer = MoodAnalyzer(config)
    mood = await analyzer.run()

    elapsed = time.time() - start_time

    # Calculate metrics
    completed = len([r for r in analyzer.results if r.status.value == "completed"])
    failed = len([r for r in analyzer.results if r.status.value == "failed"])
    total_models = sum(len(r.individual_results) for r in analyzer.results if r.status.value == "completed")

    print("\n" + "="*70)
    print("PERFORMANCE PROFILE")
    print("="*70)
    print(f"Total time:         {elapsed:.2f}s")
    print(f"Entries completed:  {completed}")
    print(f"Entries failed:     {failed}")
    print(f"Model inferences:   {total_models}")
    print(f"Throughput:         {completed/elapsed:.2f} entries/sec")
    print(f"Avg time/entry:     {elapsed/completed:.2f}s" if completed > 0 else "")
    print(f"Global mood score:  {mood:.4f}")
    print("="*70 + "\n")

asyncio.run(main())
PYTHON_SCRIPT

    RESULT=$?
    return $RESULT
}

run_dry_run() {
    print_header "Dry Run (No Processing)"

    print_info "Checking environment without running analysis..."

    echo ""
    print_status "Configuration:"
    python3 << 'PYTHON_SCRIPT'
import config
print(f"  Data directory: {config.DATA_DIR}")
print(f"  Models: {list(config.MODEL_MAPPING.keys())}")
print(f"  Concurrency limit: {config.CONCURRENCY_LIMIT}")
print(f"  Batch size: {config.BATCH_SIZE}")
print(f"  Enable checkpointing: {config.ENABLE_CHECKPOINTING}")
PYTHON_SCRIPT

    echo ""
    print_status "Checkpoint status:"
    show_checkpoint_status

    echo ""
    print_status "Required files:"
    [ -f "config.py" ] && print_success "config.py exists" || print_error "config.py missing"
    [ -f "market_mood_analyzer.py" ] && print_success "market_mood_analyzer.py exists" || print_error "market_mood_analyzer.py missing"
    [ -f "requirements.txt" ] && print_success "requirements.txt exists" || print_error "requirements.txt missing"

    echo ""
    print_info "Ready to run. Execute: bash run.sh"

    return 0
}

################################################################################
# Main Execution
################################################################################

main() {
    print_header "Crypto Market Mood Analyzer"

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --debug)
                DEBUG_MODE=true
                shift
                ;;
            --watch)
                WATCH_LOGS=true
                shift
                ;;
            --profile)
                PROFILE_MODE=true
                shift
                ;;
            --reset)
                RESET_CHECKPOINT=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --no-ollama-check)
                NO_OLLAMA_CHECK=true
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

    # Setup
    cd "$SCRIPT_DIR"
    setup_environment
    run_preflight_checks

    # Handle dry-run
    if [ "$DRY_RUN" = true ]; then
        run_dry_run
        exit $?
    fi

    # Handle checkpoint reset
    if [ "$RESET_CHECKPOINT" = true ]; then
        reset_checkpoint
    fi

    # Show checkpoint status
    echo ""
    show_checkpoint_status

    # Run analysis with selected mode
    echo ""
    if [ "$DEBUG_MODE" = true ]; then
        run_debug
        RESULT=$?
    elif [ "$WATCH_LOGS" = true ]; then
        run_with_watch
        RESULT=$?
    elif [ "$PROFILE_MODE" = true ]; then
        run_profile
        RESULT=$?
    else
        run_standard
        RESULT=$?
    fi

    # Print completion status
    if [ $RESULT -eq 0 ]; then
        print_header "Analysis Complete"
        print_success "Mood analyzer finished successfully"

        echo ""
        print_status "Results:"
        if [ -f "output/final_mood_report.json" ]; then
            python3 << 'PYTHON_SCRIPT'
import json
try:
    with open('output/final_mood_report.json') as f:
        report = json.load(f)
        mood = report.get('global_mood_score', 'N/A')
        interpretation = report.get('interpretation', 'N/A')
        entries = report.get('metadata', {}).get('total_entries_processed', 'N/A')
        print(f"  Global mood score: {mood}")
        print(f"  Interpretation: {interpretation}")
        print(f"  Entries processed: {entries}")
except:
    print("  (Could not parse report)")
PYTHON_SCRIPT
        fi

        echo ""
        print_status "Output files:"
        [ -f "output/final_mood_report.json" ] && echo "  ✓ output/final_mood_report.json"
        [ -f "logs/mood_analyzer.log" ] && echo "  ✓ logs/mood_analyzer.log"
        [ -f "checkpoints/progress_tracker.json" ] && echo "  ✓ checkpoints/progress_tracker.json"

        exit 0
    else
        print_header "Analysis Failed"
        print_error "An error occurred during execution"

        echo ""
        print_status "Troubleshooting:"
        echo "  1. Check logs: tail -100 logs/mood_analyzer.log"
        echo "  2. Verify Ollama: curl http://localhost:11434/api/tags"
        echo "  3. Validate config: python3 config.py"
        echo "  4. Check data: ls ../scrapper/data_sourcing/output/"

        exit $RESULT
    fi
}

# Run main function
main "$@"
