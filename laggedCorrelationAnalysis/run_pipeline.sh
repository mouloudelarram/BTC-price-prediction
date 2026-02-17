#!/bin/bash

# Bash pipeline script for BTCPredict analysis
# Runs: laggedCorrelationAnalysis.py -> waits for output -> decisionEngine.py -> evaluate_signals.py
# Stores final results in a JSON report

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/OutputLaggedCorrelationAnalysis"
SUMMARY_FILE="${OUTPUT_DIR}/lagged_correlation_output_summary.txt"
REPORT_DIR="myfile"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="${REPORT_DIR}/report_${TIMESTAMP}.json"
TODAY=$(date +"%Y-%m-%d")

# Ensure report directory exists
mkdir -p "${REPORT_DIR}"
mkdir -p "${OUTPUT_DIR}"

echo "========================================="
echo "BTC Trading Pipeline Started"
echo "========================================="
echo "Timestamp: ${TIMESTAMP}"
echo "Today's Date: ${TODAY}"
echo ""

# Step 1: Run laggedCorrelationAnalysis.py
echo "[1/4] Running laggedCorrelationAnalysis.py..."
python "${SCRIPT_DIR}/laggedCorrelationAnalysis.py" || {
    echo "Error: laggedCorrelationAnalysis.py failed"
    exit 1
}

# Step 2: Wait for the output summary file to be created and has content
echo "[2/4] Waiting for output summary file to be generated..."
TIMEOUT=300  # 5 minutes timeout
ELAPSED=0
WAIT_INTERVAL=2

while [ $ELAPSED -lt $TIMEOUT ]; do
    if [ -f "${SUMMARY_FILE}" ] && [ -s "${SUMMARY_FILE}" ]; then
        echo "✓ Summary file ready: ${SUMMARY_FILE}"
        break
    fi
    sleep ${WAIT_INTERVAL}
    ELAPSED=$((ELAPSED + WAIT_INTERVAL))
done

if [ ! -f "${SUMMARY_FILE}" ] || [ ! -s "${SUMMARY_FILE}" ]; then
    echo "Error: Summary file not created or empty after ${TIMEOUT} seconds"
    exit 1
fi

# Small delay to ensure file is fully written
sleep 2

# Step 3: Run decisionEngine.py and capture the decision
echo "[3/4] Running decisionEngine.py to get trading decision..."
DECISION_OUTPUT=$(python "${SCRIPT_DIR}/decisionEngine.py")
echo "Decision Engine Output:"
echo "${DECISION_OUTPUT}"

# Extract the signal (BUY, SELL, or HOLD) from JSON output
SIGNAL=$(echo "${DECISION_OUTPUT}" | grep -o '"signal": "[^"]*"' | cut -d'"' -f4)

if [ -z "${SIGNAL}" ]; then
    echo "Error: Could not extract signal from decision engine"
    echo "Output was: ${DECISION_OUTPUT}"
    exit 1
fi

echo "✓ Signal extracted: ${SIGNAL}"

# Step 4: Run evaluate_signals.py with the extracted decision
echo "[4/4] Evaluating signal with evaluate_signals.py..."
EVAL_OUTPUT=$(python "${SCRIPT_DIR}/evaluate_signals.py" --date 2026-02-14 --decision "${SIGNAL}")
echo "Evaluation Output:"
echo "${EVAL_OUTPUT}"

# Combine results into a final report - using Python for proper JSON handling
python << PYSCRIPT
import json
import sys
from datetime import datetime

decision_output = '''${DECISION_OUTPUT}'''
eval_output = '''${EVAL_OUTPUT}'''

try:
    decision_data = json.loads(decision_output)
except json.JSONDecodeError:
    decision_data = {"signal": "UNKNOWN", "error": "Failed to parse decision output"}

# Find the last valid JSON line from evaluation output
eval_data = {}
for line in reversed(eval_output.split('\n')):
    if line.strip():
        try:
            eval_data = json.loads(line)
            break
        except:
            continue

report = {
    "timestamp": datetime.utcnow().isoformat() + 'Z',
    "date": "${TODAY}",
    "decision_signal": decision_data.get('signal', 'UNKNOWN'),
    "decision_confidence": decision_data.get('confidence', 'N/A'),
    "decision_engine": decision_data,
    "evaluation_result": eval_data
}

with open("${REPORT_FILE}", "w") as f:
    json.dump(report, f, indent=2)

print(json.dumps(report, indent=2))
PYSCRIPT

echo ""
echo "========================================="
echo "✓ Pipeline Completed Successfully"
echo "========================================="
echo "Report saved to: ${REPORT_FILE}"
cat "${REPORT_FILE}"