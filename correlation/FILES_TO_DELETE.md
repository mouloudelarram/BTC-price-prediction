"""Files to delete after migration validation."""

# FILES TO DELETE - Production Refactoring Cleanup

**DO NOT DELETE UNTIL:**
1. ✅ New API server is running and tested
2. ✅ Daily pipeline executes successfully
3. ✅ Signals match or improve upon old implementation
4. ✅ All tests pass

---

## FILES TO DELETE

### 1. Legacy AI Decision Engines (SAFE TO DELETE)
These were experimental implementations from different LLMs that have been superseded by BTCAutoTraderV3 (now SignalEngine).

```
correlation/legacy/ChatGPTBTCLaggedCorrelationDecisionEngine.py
correlation/legacy/ClaudeBTCLaggedCorrelationDecisionEngine.py
correlation/legacy/CopilotBTCLaggedCorrelationDecisionEngine.py
correlation/legacy/GeminBTCLaggedCorrelationDecisionEngine.py
correlation/legacy/PerplexityBTCLaggedCorrelationDecisionEngine.py
correlation/legacy/run_all_decision_engines.py
```

**Reason:** Superseded by improved BTCAutoTraderV3 logic in `app/core/signal_engine.py`

---

### 2. Old Monolithic Python Files (SAFE TO DELETE)
These contain functionality now in `app/` modules.

```
correlation/decisionEngine.py
correlation/laggedCorrelationAnalysis.py
correlation/evaluate_signals.py
correlation/main.py (old monitor loop version)
```

**Reason:** Code has been refactored into:
- `app/core/correlation.py`
- `app/core/signal_engine.py`
- `scripts/backtest.py`
- `main.py` (new FastAPI version)

---

### 3. Shell Scripts (SAFE TO DELETE)
Bash/shell execution scripts replaced by Python CLI.

```
correlation/run_pipeline.sh
correlation/run.sh
correlation/script.sh
correlation/eval_wrapper.sh
```

**Reason:** Replaced by:
- `scripts/daily_job.py` - Daily pipeline CLI
- `scripts/backtest.py` - Backtesting CLI

---

### 4. Old Output Archives (SAFE TO DELETE)
Timestamped output files in the Old folder. Current summary is in `results/`.

```
correlation/OutputLaggedCorrelationAnalysis/Old/
    - lagged_correlation_output_summary_20260215_211637.txt
    - lagged_correlation_output_summary_20260216_202839.txt
    - lagged_correlation_output_summary_20260217_201118.txt
    - lagged_correlation_output_summary_20260218_220212.txt
    - lagged_correlation_output_summary_20260220_170958.txt
    - lagged_correlation_output_summary_20260221_220347.txt
    - lagged_correlation_output_summary_20260223_193547.txt
    - lagged_correlation_output_summary_20260225_235402.txt
```

**Reason:** Archive cleanup; new results stored in `results/` directory with rotation

---

### 5. Old CSV Output Files (OPTIONAL)
Legacy decision log that's being replaced by JSON logging.

```
correlation/decisions.csv
```

**Reason:** Historical decisions should be backed up. New format:
- `results/latest_signal.json` - Current signal
- `results/pipeline_log.json` - Execution history

**Action:** Backup to external storage before deleting.

---

### 6. Old OutputLaggedCorrelationAnalysis Directory (OPTIONAL)
The summary text file will be recreated in `results/`.

```
correlation/OutputLaggedCorrelationAnalysis/lagged_correlation_output_summary.txt
```

**Reason:** Replaced by structured JSON in `results/correlation_summary.json`

---

## DELETE STRATEGY

### Immediate Cleanup (Safe Now)
```bash
# Delete legacy decision engines
rm -r correlation/legacy/

# Delete shell scripts
rm correlation/run_pipeline.sh
rm correlation/run.sh
rm correlation/script.sh
rm correlation/eval_wrapper.sh

# Delete old Python files
rm correlation/decisionEngine.py
rm correlation/laggedCorrelationAnalysis.py
rm correlation/evaluate_signals.py
rm correlation/main.py.bak  # if exists
```

### Backup Before Deleting
```bash
# Backup decisions.csv
cp correlation/decisions.csv decisions.csv.backup

# Backup old analysis outputs
cp -r correlation/OutputLaggedCorrelationAnalysis/Old outputs_backup/
```

### After Backup
```bash
# Delete old outputs
rm -r correlation/OutputLaggedCorrelationAnalysis/Old/
rm correlation/decisions.csv
rm correlation/OutputLaggedCorrelationAnalysis/lagged_correlation_output_summary.txt
```

---

## WHAT TO KEEP

✅ These files should be preserved:

```
correlation/app/               # New modular architecture
correlation/scripts/           # New CLI tools
correlation/tests/             # Test suite
correlation/config.py          # Configuration
correlation/main.py            # New FastAPI app
correlation/requirements.txt   # Dependencies
correlation/.env.example       # Config template
correlation/MIGRATION_GUIDE.md # Documentation
correlation/results/           # Output directory
correlation/logs/              # Logs directory
```

---

## VERIFICATION CHECKLIST

Before deleting files, verify:

- [ ] API server starts: `python main.py`
- [ ] API docs accessible: `http://localhost:8000/docs`
- [ ] Daily job runs: `python scripts/daily_job.py --dry-run`
- [ ] New signal generation works
- [ ] Old and new signals produce similar results
- [ ] Unit tests pass: `pytest tests/ -v`
- [ ] All dependencies resolved

---

## RECOVERY

If something goes wrong after deletion:

1. **Git restore:** `git checkout <file>`
2. **From backup:** Restore from timestamped backups
3. **Rebuild:** Re-run correlation analysis

---

## Questions?

Refer to:
- `MIGRATION_GUIDE.md` - Overview of refactoring
- `config.py` - All configuration options
- `app/models/__init__.py` - Data models
- `tests/test_correlation.py` - Example usage
