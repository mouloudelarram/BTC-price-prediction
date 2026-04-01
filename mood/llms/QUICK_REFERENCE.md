"""
QUICK REFERENCE GUIDE
Crypto Market Mood Analyzer

Common Commands, Configuration Changes, and Troubleshooting
"""

# ============================================================================
# INSTALLATION & SETUP
# ============================================================================

# 1. Install dependencies
pip install -r requirements.txt

# 2. Verify Ollama setup
curl http://localhost:11434/api/tags
ollama list

# 3. Pull required models
ollama pull llama3.1
ollama pull mistral-large-3:675b-cloud

# ============================================================================
# RUNNING THE ANALYZER
# ============================================================================

# Basic run (respects checkpoints)
python market_mood_analyzer.py

# Force reprocess all entries (ignore checkpoints)
# Edit market_mood_analyzer.py, line ~330:
#   global_mood = await analyzer.run(force_reprocess=True)

# Run examples/tests
python examples.py

# Run config validation only
python config.py

# ============================================================================
# CONFIGURATION QUICK CHANGES
# ============================================================================

# Increase speed (at cost of accuracy)
# In config.py:
CONCURRENCY_LIMIT = 5           # Increase parallelism
BATCH_SIZE = 20                 # Process more at once
# Use faster models:
MODEL_MAPPING = {
    "reddit": ["llama3.1:latest"],  # Smaller models
}

# Increase accuracy (at cost of speed)
# In config.py:
CONCURRENCY_LIMIT = 1           # Serialize execution
BATCH_SIZE = 3                  # Careful processing
TIMEOUT_SECONDS = 120           # More time per model

# Reduce memory usage
# In config.py:
CONCURRENCY_LIMIT = 1           # Single model at a time
# Use smaller models (8B instead of 70B)

# ============================================================================
# MONITORING & DEBUGGING
# ============================================================================

# Watch logs in real-time
tail -f logs/mood_analyzer.log

# Check last 50 log lines
tail -50 logs/mood_analyzer.log

# Filter logs by level
grep "ERROR" logs/mood_analyzer.log
grep "WARNING" logs/mood_analyzer.log

# Count processed entries
cat checkpoints/progress_tracker.json | python -m json.tool | grep processed_ids

# View final report
cat output/final_mood_report.json | python -m json.tool | head -50

# ============================================================================
# CHECKPOINT MANAGEMENT
# ============================================================================

# Check checkpoint status
cat checkpoints/progress_tracker.json

# Backup checkpoint (before reset)
cp checkpoints/progress_tracker.json checkpoints/progress_tracker.json.bak

# Reset checkpoint (start fresh)
rm checkpoints/progress_tracker.json

# See what entries failed
cat checkpoints/progress_tracker.json | python -c "
import json, sys
data = json.load(sys.stdin)
for entry_id, error_info in data['failed_ids'].items():
    print(f'{entry_id}: {error_info[\"error\"]}')"

# ============================================================================
# DATA MANAGEMENT
# ============================================================================

# Check data loading
ls -la ../scrapper/data_sourcing/output/*.json
wc -l ../scrapper/data_sourcing/output/*.json

# Generate test data
python -c "from examples import generate_test_data; generate_test_data(50)"

# Inspect data structure
python -c "
import json
with open('../scrapper/data_sourcing/output/data.json') as f:
    data = json.load(f)
    print(f'Total entries: {len(data)}')
    print(f'Sample keys: {data[0].keys() if data else \"empty\"}')
"

# ============================================================================
# PERFORMANCE OPTIMIZATION
# ============================================================================

# Benchmark current setup
time python market_mood_analyzer.py

# Profile with different concurrency
# Edit config.py CONCURRENCY_LIMIT to 1, 3, 5, etc.
# For each: time python market_mood_analyzer.py

# Find bottleneck (throughput per model)
# Look at processing_time in output/final_mood_report.json:
python -c "
import json
with open('output/final_mood_report.json') as f:
    report = json.load(f)
    times = [r['processing_time'] for r in report['detailed_results']]
    print(f'Avg time per entry: {sum(times)/len(times):.2f}s')
    print(f'Min: {min(times):.2f}s, Max: {max(times):.2f}s')
"

# ============================================================================
# COMMON ERRORS & FIXES
# ============================================================================

ERROR: "Connection refused" to Ollama
FIX:
  1. Check Ollama is running: curl http://localhost:11434/api/tags
  2. Start if needed: ollama serve
  3. Verify port 11434 is open: netstat -tuln | grep 11434

ERROR: "Data directory not found"
FIX:
  1. Check DATA_DIR in config.py
  2. Verify path exists: ls -la ../scrapper/data_sourcing/output/
  3. Update path if needed: DATA_DIR = Path("path/to/data")

ERROR: "All models failed to produce valid sentiment"
FIX:
  1. Verify models are installed: ollama list
  2. Check system prompt format (must be valid JSON)
  3. Increase TIMEOUT_SECONDS if models are slow
  4. Try different model: change MODEL_MAPPING

ERROR: "Out of memory" (OOM)
FIX:
  1. Reduce CONCURRENCY_LIMIT to 1
  2. Reduce BATCH_SIZE to 2-3
  3. Use smaller models (8B vs 70B)
  4. Increase TIMEOUT_SECONDS to give models time

ERROR: "JSON decode error"
FIX:
  1. Model not returning valid JSON
  2. Check logs: tail -f logs/mood_analyzer.log
  3. Try with llama3.1 (more reliable for JSON)
  4. Increase TIMEOUT_SECONDS

ERROR: "Checkpoint corrupted"
FIX:
  1. Backup: cp checkpoints/progress_tracker.json checkpoints/progress_tracker.json.bak
  2. Reset: rm checkpoints/progress_tracker.json
  3. Next run will start fresh

# ============================================================================
# INTEGRATION WITH OTHER SYSTEMS
# ============================================================================

# Save mood score to file
python -c "
import asyncio
from market_mood_analyzer import MoodAnalyzer
import config

async def save_mood():
    analyzer = MoodAnalyzer(config)
    mood = await analyzer.run()
    with open('mood.txt', 'w') as f:
        f.write(f'{mood:.4f}')

asyncio.run(save_mood())
"

# Send report via email (requires emaillib)
python -c "
import json
from pathlib import Path

report_file = Path('output/final_mood_report.json')
with open(report_file) as f:
    report = json.load(f)
    mood = report['global_mood_score']
    print(f'Current mood: {mood}')
    # Add email sending code here
"

# Store in database (example with sqlite)
python -c "
import json
import sqlite3
from datetime import datetime

conn = sqlite3.connect('mood_history.db')
c = conn.cursor()

# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS mood (
    timestamp TEXT, mood_score REAL
)''')

with open('output/final_mood_report.json') as f:
    report = json.load(f)
    mood = report['global_mood_score']
    c.execute('INSERT INTO mood VALUES (?, ?)',
              (datetime.now().isoformat(), mood))

conn.commit()
conn.close()
"

# ============================================================================
# AUTOMATION / CRON JOBS
# ============================================================================

# Run daily analysis (add to crontab)
# crontab -e

# Run daily at 2 AM
0 2 * * * cd /path/to/analyzer && python market_mood_analyzer.py

# Run every 6 hours
0 */6 * * * cd /path/to/analyzer && python market_mood_analyzer.py

# Run with logging
0 2 * * * cd /path/to/analyzer && python market_mood_analyzer.py >> cron.log 2>&1

# ============================================================================
# USEFUL PYTHON SNIPPETS
# ============================================================================

# Access results in Python
CODE:
from market_mood_analyzer import MoodAnalyzer
import asyncio, config

async def get_mood():
    analyzer = MoodAnalyzer(config)
    await analyzer.run()
    return analyzer.results

results = asyncio.run(get_mood())
print(f"Processed {len(results)} entries")

# Filter by platform
bullish_reddit = [r for r in results 
                  if r.platform == 'reddit' 
                  and r.aggregated_sentiment > 0.3]
print(f"Bullish Reddit posts: {len(bullish_reddit)}")

# Get top 5 bullish entries
top_bullish = sorted(results, 
                     key=lambda x: x.aggregated_sentiment, 
                     reverse=True)[:5]

# Export to CSV (requires pandas)
import pandas as pd
df = pd.DataFrame([{
    'platform': r.platform,
    'sentiment': r.aggregated_sentiment,
    'confidence': r.aggregated_confidence,
    'processing_time': r.processing_time
} for r in results])
df.to_csv('results.csv', index=False)

# ============================================================================
# FILE STRUCTURE
# ============================================================================

project/
├── config.py                    # Configuration
├── market_mood_analyzer.py      # Main analyzer
├── examples.py                  # Usage examples
├── requirements.txt             # Dependencies
├── README.md                    # Documentation
├── QUICK_REFERENCE.md           # This file
│
├── checkpoints/
│   └── progress_tracker.json    # Resume state
├── logs/
│   └── mood_analyzer.log        # Activity log
├── output/
│   └── final_mood_report.json   # Results
└── test_data/
    └── test_entries.json        # Test data

# ============================================================================
# SUPPORT RESOURCES
# ============================================================================

Official Documentation:
  - README.md: Full documentation
  - config.py: Configuration options with comments
  - market_mood_analyzer.py: Implementation details
  
Troubleshooting:
  - logs/mood_analyzer.log: Detailed error messages
  - checkpoints/progress_tracker.json: Processing state
  - output/final_mood_report.json: Detailed results

Community:
  - Ollama documentation: https://ollama.ai/
  - AsyncIO guide: https://docs.python.org/3/library/asyncio.html
  - aiohttp docs: https://docs.aiohttp.org/
