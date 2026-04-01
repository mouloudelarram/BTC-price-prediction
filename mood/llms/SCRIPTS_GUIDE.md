# Setup & Run Scripts Guide

Complete guide to using the `setup.sh` and `run.sh` scripts for easy deployment and execution of the Crypto Market Mood Analyzer.

## 📋 Overview

The project includes two convenience scripts:

| Script | Purpose | Usage |
|--------|---------|-------|
| **setup.sh** | Initialize environment, install dependencies | One-time setup |
| **run.sh** | Execute analyzer with various options | Regular execution |

Both scripts are **production-ready**, with comprehensive error handling, colored output, and detailed feedback.

---

## 🚀 Quick Start

### One-Command Setup

```bash
# Make scripts executable (one-time)
chmod +x setup.sh run.sh

# Run setup
bash setup.sh

# Run analyzer
bash run.sh
```

**That's it!** The scripts handle everything else.

---

## 📝 setup.sh - Environment Initialization

### Purpose

Prepares your system to run the analyzer by:
- ✅ Checking Python 3.8+ is installed
- ✅ Creating required directories
- ✅ Installing Python dependencies
- ✅ Validating configuration files
- ✅ Verifying Ollama connectivity
- ✅ Testing Ollama models availability

### Usage

```bash
# Standard setup (uses system Python)
bash setup.sh

# Setup with virtual environment
bash setup.sh --venv

# Skip Ollama connectivity check
bash setup.sh --no-checks

# Show help
bash setup.sh --help
```

### Setup Modes

#### Standard Setup (System Python)

```bash
bash setup.sh
```

**What it does:**
1. Checks Python version (requires 3.8+)
2. Creates directories: `checkpoints/`, `logs/`, `output/`, `test_data/`
3. Upgrades pip
4. Installs packages from `requirements.txt`
5. Validates `config.py`
6. Tests Ollama connectivity and lists available models

**Best for:** Most users, quick setup

#### Virtual Environment Setup

```bash
bash setup.sh --venv
```

**What it does:**
- Everything above, PLUS creates isolated Python environment in `venv/` directory
- Prevents dependency conflicts with other projects

**Best for:** Power users, multi-project environments, deployment

**Note:** After virtual environment setup, the `run.sh` script automatically detects and activates it.

#### Skip Checks

```bash
bash setup.sh --no-checks
```

Skips Ollama connectivity check (useful if Ollama isn't running yet).

### What Gets Created

```
project/
├── venv/                          # (if --venv used)
│   ├── bin/
│   ├── lib/
│   └── ...
├── checkpoints/                   # Progress tracking
│   └── progress_tracker.json
├── logs/                          # Activity logs
│   └── mood_analyzer.log
├── output/                        # Results
│   └── final_mood_report.json
└── test_data/                     # Test data storage
    └── test_entries.json
```

### Troubleshooting setup.sh

| Problem | Solution |
|---------|----------|
| "Python 3 is not installed" | Install Python 3.8+ from https://www.python.org |
| "pip installation fails" | Check internet connection, update pip: `python3 -m pip install --upgrade pip` |
| "Ollama is not responding" | Start Ollama: `ollama serve` |
| "Permission denied" | Make script executable: `chmod +x setup.sh` |
| "config.py validation failed" | Check config.py syntax, or run: `python3 config.py` |

### Environment Variables

You can customize setup behavior with:

```bash
# Use specific Python version
PATH=/usr/bin/python3.11:$PATH bash setup.sh

# Custom virtual environment location
VENV_DIR=myenv bash setup.sh --venv
```

---

## ▶️ run.sh - Analyzer Execution

### Purpose

Executes the mood analyzer with:
- ✅ Pre-flight checks (config, dependencies, Ollama)
- ✅ Automatic virtual environment detection & activation
- ✅ Checkpoint status display
- ✅ Real-time monitoring options
- ✅ Performance profiling
- ✅ Debug mode with verbose logging
- ✅ Detailed result reporting

### Usage

```bash
# Standard run (respects existing checkpoints)
bash run.sh

# Run with debug logging
bash run.sh --debug

# Monitor logs in real-time
bash run.sh --watch

# Profile performance
bash run.sh --profile

# Start fresh (reset checkpoint)
bash run.sh --reset

# Dry run (check environment without processing)
bash run.sh --dry-run

# Show help
bash run.sh --help
```

### Execution Modes

#### Standard Run

```bash
bash run.sh
```

**Default behavior:**
- Runs preflight checks
- Respects checkpoint (skips already-processed entries)
- Normal logging (INFO level)
- Single execution, prints summary

**Output:**
```
✓ Python is available
✓ Required directories exist
✓ Configuration is valid
✓ All dependencies are installed
✓ Ollama is running

→ Current checkpoint status:
  Processed entries: 150
  Failed entries: 3
  Total: 153

→ Starting analysis...
[processing...]

===============================================================================
ANALYSIS COMPLETE
===============================================================================
✓ Global Mood Score: 0.3742
  Interpretation: 📈 Moderately Bullish
  Entries Processed: 47
  Results:
  • output/final_mood_report.json
  • logs/mood_analyzer.log
  • checkpoints/progress_tracker.json
```

#### Debug Mode

```bash
bash run.sh --debug
```

**What it does:**
- Enables DEBUG logging (all internal details)
- Very verbose output to console
- Shows every API call, model inference, data processing step

**Best for:** Troubleshooting, understanding flow, development

**Output:** Extensive logs like:
```
2024-01-15 10:30:45,123 - MoodAnalyzer - DEBUG - Loaded 1000 entries from data directory
2024-01-15 10:30:46,456 - MoodAnalyzer - DEBUG - Preprocessing entry abc123...
2024-01-15 10:30:47,789 - OllamaClient - DEBUG - POST to http://localhost:11434/api/chat
...
```

#### Watch Logs (Real-time Monitoring)

```bash
bash run.sh --watch
```

**What it does:**
- Starts analyzer in background
- Opens real-time log stream (like `tail -f`)
- Shows live progress as it happens
- Press Ctrl+C to stop monitoring (analysis continues)

**Best for:** Monitoring long runs, watching progress

**Output:**
```
→ Starting analyzer in background...
✓ Analyzer running (PID: 12345)
→ Monitoring logs (Ctrl+C to stop)

2024-01-15 10:30:45,123 - Starting sentiment analysis...
2024-01-15 10:30:46,456 - Processing batch 1/20...
2024-01-15 10:30:47,789 - Entry 1: Sentiment 0.45, Confidence 0.82
...
```

#### Profile Mode

```bash
bash run.sh --profile
```

**What it does:**
- Runs analyzer normally
- Measures and displays performance metrics
- Shows throughput, time per entry, model efficiency

**Best for:** Performance optimization, benchmarking

**Output:**
```
======================================================================
PERFORMANCE PROFILE
======================================================================
Total time:         145.67s
Entries completed:  150
Entries failed:     3
Model inferences:   180
Throughput:         1.03 entries/sec
Avg time/entry:     0.97s
Global mood score:  0.3742
======================================================================
```

#### Reset Checkpoint

```bash
bash run.sh --reset
```

**What it does:**
- Deletes `checkpoints/progress_tracker.json`
- Next run will reprocess ALL entries (not just new ones)
- Useful for reanalyzing entire dataset or recovering from corruption

**Warning:** This erases resume history!

**Safe reset:**
```bash
# Backup first
cp checkpoints/progress_tracker.json checkpoints/progress_tracker.json.bak

# Then reset
bash run.sh --reset
```

#### Dry Run (Environment Check)

```bash
bash run.sh --dry-run
```

**What it does:**
- Runs all preflight checks
- Shows configuration
- Displays checkpoint status
- Lists required files
- **Does NOT run analysis**

**Best for:** Verifying setup before running, troubleshooting

**Output:**
```
===============================================================================
Dry Run (No Processing)
===============================================================================
→ Configuration:
  Data directory: ../scrapper/data_sourcing/output
  Models: ['fear_greed', 'coindesk', 'reddit', ...]
  Concurrency limit: 3
  Batch size: 5
  Enable checkpointing: True

→ Checkpoint status:
  Processed entries: 150
  Failed entries: 3
  Total: 153

→ Required files:
✓ config.py exists
✓ market_mood_analyzer.py exists
✓ requirements.txt exists

Ready to run. Execute: bash run.sh
```

#### Combined Options

You can combine options:

```bash
# Debug + Watch (debug logging with real-time monitoring)
bash run.sh --debug --watch

# Reset + Profile (fresh start with performance metrics)
bash run.sh --reset --profile

# Debug without Ollama check
bash run.sh --debug --no-ollama-check
```

### Preflight Checks

Every execution includes automatic checks for:

1. **Python**: Version 3.8+
2. **Directories**: checkpoints/, logs/, output/
3. **Configuration**: config.py validates successfully
4. **Dependencies**: aiohttp and other packages installed
5. **Ollama**: Responds to API calls (skipped with `--no-ollama-check`)
6. **Data**: JSON files exist in data directory

If any check fails, the script shows:
- ❌ What failed
- 💡 How to fix it
- 🔧 Suggested commands to run

### Automatic Features

#### Virtual Environment Detection

If you ran `setup.sh --venv`, the `run.sh` script:
- Automatically detects the `venv/` directory
- Activates it before running
- No manual activation needed

#### Checkpoint Display

Before running, shows:
```
→ Current checkpoint status:
  Processed entries: 150
  Failed entries: 3
  Total: 153
```

Helps you understand what data will be reprocessed.

#### Results Summary

After completion, displays:
```
→ Results:
  Global mood score: 0.3742
  Interpretation: 📈 Moderately Bullish
  Entries processed: 150

→ Output files:
  ✓ output/final_mood_report.json
  ✓ logs/mood_analyzer.log
  ✓ checkpoints/progress_tracker.json
```

### Troubleshooting run.sh

| Problem | Solution |
|---------|----------|
| "Config validation failed" | Run: `python3 config.py` to see errors |
| "Ollama is not responding" | Start Ollama: `ollama serve` |
| "Python dependencies not installed" | Run setup: `bash setup.sh` |
| "No data found" | Check path: `ls ../scrapper/data_sourcing/output/` |
| "Permission denied" | Make executable: `chmod +x run.sh` |
| "Out of memory" | Reduce CONCURRENCY_LIMIT in config.py |

---

## 📊 Practical Examples

### Scenario 1: First-Time User

```bash
# 1. Initial setup
bash setup.sh

# 2. Verify everything works
bash run.sh --dry-run

# 3. Run analyzer
bash run.sh
```

### Scenario 2: Development / Debugging

```bash
# Run with verbose logging to see everything
bash run.sh --debug

# Or monitor in real-time
bash run.sh --watch

# Check logs manually
tail -f logs/mood_analyzer.log
```

### Scenario 3: Performance Testing

```bash
# Test current setup
bash run.sh --profile

# Optimize config.py, then test again
bash run.sh --reset --profile

# Compare results
cat output/final_mood_report.json
```

### Scenario 4: Reprocessing All Data

```bash
# Backup current progress
cp checkpoints/progress_tracker.json checkpoints/progress_tracker.json.backup

# Clear checkpoint and reprocess
bash run.sh --reset

# Monitor progress
bash run.sh --watch
```

### Scenario 5: Scheduled/Automated Runs

```bash
# Add to crontab for daily runs at 2 AM
# crontab -e
0 2 * * * cd /path/to/project && bash run.sh >> logs/cron.log 2>&1

# Monitor completion
bash run.sh --dry-run
tail logs/cron.log
```

### Scenario 6: Multi-Step Workflow

```bash
# Step 1: Fresh environment setup
bash setup.sh --venv

# Step 2: Verify configuration
bash run.sh --dry-run

# Step 3: Performance baseline
bash run.sh --profile

# Step 4: Optimize config.py (reduce CONCURRENCY_LIMIT, etc.)
nano config.py

# Step 5: Test optimizations
bash run.sh --reset --profile

# Step 6: Monitor one more run
bash run.sh --watch
```

---

## 🔧 Advanced Usage

### Custom Python Interpreter

```bash
# Use specific Python version
/usr/bin/python3.11/bin/python3 setup.sh
/usr/bin/python3.11/bin/python3 run.sh
```

### Custom Virtual Environment Location

```bash
VENV_DIR=/path/to/custom/venv bash setup.sh --venv
```

### Quiet Mode (No Colors)

```bash
# Remove color codes for CI/CD systems
bash setup.sh 2>&1 | sed 's/\x1b\[[0-9;]*m//g'
```

### Logging to File

```bash
# Capture full output
bash run.sh 2>&1 | tee execution_$(date +%s).log
```

### Running Multiple Instances

```bash
# (Carefully! May cause checkpoint conflicts)
bash run.sh &  # Background
bash run.sh    # Foreground
```

---

## 📈 File Structure After Setup

```
project/
├── setup.sh                       # Setup script
├── run.sh                         # Run script
├── config.py                      # Configuration
├── market_mood_analyzer.py        # Main analyzer
├── examples.py                    # Examples
├── requirements.txt               # Dependencies
├── README.md                      # Documentation
│
├── venv/                          # (created by setup.sh --venv)
│   ├── bin/
│   ├── lib/
│   └── pyvenv.cfg
│
├── checkpoints/                   # Created by setup.sh
│   └── progress_tracker.json      # Generated on first run
│
├── logs/                          # Created by setup.sh
│   └── mood_analyzer.log          # Generated on first run
│
├── output/                        # Created by setup.sh
│   └── final_mood_report.json     # Generated by analyzer
│
└── test_data/                     # Created by setup.sh
    └── (optional test data)
```

---

## 🆘 Common Issues & Solutions

### Issue: "No such file or directory" when running scripts

**Cause:** Scripts are in a different directory

**Solution:**
```bash
# Navigate to project directory first
cd /path/to/mood-analyzer

# Then run
bash setup.sh
bash run.sh
```

### Issue: Scripts don't execute even with `chmod +x`

**Cause:** Bash interpreter not found

**Solution:**
```bash
# Use explicit bash invocation
bash setup.sh
bash run.sh

# Or verify bash location
which bash
```

### Issue: Virtual environment not activating

**Cause:** Different shell or path issues

**Solution:**
```bash
# Verify venv exists
ls -la venv/

# Manually activate if needed
source venv/bin/activate

# Verify it's active
which python
```

### Issue: Ollama check fails but Ollama is running

**Cause:** Ollama on different host/port

**Solution:**
```bash
# Skip check
bash run.sh --no-ollama-check

# Or update config.py if Ollama is on different host
# Edit config.py: OLLAMA_BASE_URL = "http://other-host:11434"
```

---

## 📚 Quick Reference

### setup.sh Commands

```bash
bash setup.sh                 # Standard setup
bash setup.sh --venv          # With virtual environment
bash setup.sh --no-checks     # Skip Ollama check
bash setup.sh --help          # Show help
```

### run.sh Commands

```bash
bash run.sh                   # Standard run
bash run.sh --debug           # Debug logging
bash run.sh --watch           # Real-time monitoring
bash run.sh --profile         # Performance metrics
bash run.sh --reset           # Clear checkpoint
bash run.sh --dry-run         # Environment check only
bash run.sh --help            # Show help
```

### Useful Manual Commands

```bash
# View logs
tail -f logs/mood_analyzer.log
tail -100 logs/mood_analyzer.log

# Check checkpoint
cat checkpoints/progress_tracker.json | python3 -m json.tool

# View report
cat output/final_mood_report.json | python3 -m json.tool

# Verify Ollama
curl http://localhost:11434/api/tags

# Activate venv manually
source venv/bin/activate

# Deactivate venv
deactivate
```

---

## ✅ Best Practices

1. **Always run `setup.sh` first** - Ensures environment is ready
2. **Use `--dry-run`** before important runs - Verify everything works
3. **Backup checkpoint before `--reset`** - Safety first
4. **Use `--watch` for long runs** - Monitor progress
5. **Check logs on errors** - First troubleshooting step
6. **Use virtual environment for production** - Avoid conflicts

---

## 📞 Getting Help

If scripts fail:

1. **Check logs:** `tail -100 logs/mood_analyzer.log`
2. **Run validation:** `python3 config.py`
3. **Try dry run:** `bash run.sh --dry-run`
4. **Check Ollama:** `curl http://localhost:11434/api/tags`
5. **Read README.md** for full documentation

---

**Happy analyzing!** 🚀
