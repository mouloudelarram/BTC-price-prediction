#!/usr/bin/env bash
set -euo pipefail
# Usage: ./eval_wrapper.sh [YYYY-MM-DD|today] [decision|run_all]

DATE_ARG=${1:-today}
DECISION_ARG=${2:-run_all}

if [ "$DATE_ARG" = "today" ]; then
  DATE=$(date -u +%F)
else
  DATE="$DATE_ARG"
fi

if echo "$DECISION_ARG" | grep -qi "run_all"; then
  # suppress verbose prints from engines by redirecting stdout/stderr
  DECISION=$(python - <<'PY' 2>/dev/null
from pathlib import Path
from run_all_decision_engines import run_all, aggregate
res = run_all(Path('OutputLaggedCorrelationAnalysis/lagged_correlation_output_summary.txt'))
print(aggregate(res)['majority'])
PY
)
else
  DECISION="$DECISION_ARG"
fi

TMPFILE=$(mktemp)
# run evaluator, silence warnings and stderr to avoid noise
PYTHONWARNINGS=ignore python evaluate_signals.py --date "$DATE" --decision "$DECISION" --output "$TMPFILE" > /dev/null 2>&1 || true

python - <<PY
import json, sys
try:
  obj = json.load(open(r"$TMPFILE"))
except Exception:
  print('False')
  sys.exit(1)
rec = obj[0] if isinstance(obj, list) and obj else obj
res = bool(rec.get('correct', False)) if isinstance(rec, dict) else False
print('True' if res else 'False')
sys.exit(0 if res else 1)
PY

rm -f "$TMPFILE"
