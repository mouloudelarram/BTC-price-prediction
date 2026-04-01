# Crypto Market Mood Analyzer

A production-grade asynchronous system for analyzing cryptocurrency market sentiment from multiple data sources using local Ollama LLM models.

## 📋 Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Checkpointing & Resume](#checkpointing--resume)
7. [Mathematical Foundation](#mathematical-foundation)
8. [Troubleshooting](#troubleshooting)
9. [Performance Tuning](#performance-tuning)

---

## ✨ Features

- **Async/Concurrent Processing**: Multiple models run in parallel with configurable concurrency limits
- **Resumable Processing**: Checkpointing enables interruption and resume without data loss or duplication
- **Ensemble Analysis**: Multiple models per entry with automatic result averaging
- **Weighted Aggregation**: Platform-specific weights for balanced sentiment scoring
- **Robust Error Handling**: Detailed logging, graceful failure handling, and retry logic
- **State Management**: Automatic tracking of processed entries with SQLite-like JSON checkpoints
- **Flexible Configuration**: All settings in one `config.py` file
- **Production Ready**: Type hints, data validation, comprehensive logging

---

## 🏗️ Architecture

### Component Overview

```
market_mood_analyzer.py
├── MoodAnalyzer (main orchestrator)
│   ├── DataLoader (loads & preprocesses JSON data)
│   ├── OllamaClient (async Ollama API client)
│   ├── ProgressTracker (checkpoint management)
│   └── SentimentEngine (sentiment analysis coordination)
│
└── Supporting Classes
    ├── SentimentResult (single model output)
    ├── EntryAnalysis (aggregated entry result)
    └── SentimentStatus (enum for entry state)

config.py
└── All configuration settings, model mappings, weights, prompts
```

### Data Flow

```
Raw JSON Data
    ↓
DataLoader.load_all()
    ↓
DataLoader.preprocess()
    ↓
ProgressTracker.is_processed()
    ↓
MoodAnalyzer._process_entry()
    ├─ (parallel) OllamaClient.analyze_sentiment() [model 1]
    ├─ (parallel) OllamaClient.analyze_sentiment() [model 2]
    └─ (parallel) OllamaClient.analyze_sentiment() [model N]
    ↓
Aggregate sentiment scores
    ↓
MoodAnalyzer._calculate_global_mood()
    ↓
Generate Report & Update Checkpoint
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verify Ollama is Running

```bash
# Check if Ollama is accessible
curl http://localhost:11434/api/tags

# Expected output: list of available models
```

### 3. Run the Analyzer

```bash
# First run (processes all data)
python market_mood_analyzer.py

# Resume from checkpoint
python market_mood_analyzer.py

# Force reprocess all (ignore checkpoints)
# Modify main() to call: await analyzer.run(force_reprocess=True)
```

### 4. Check Results

```bash
# Final report
cat output/final_mood_report.json

# Log file
tail -f logs/mood_analyzer.log

# Checkpoint status
cat checkpoints/progress_tracker.json
```

---

## ⚙️ Configuration

### `config.py` Overview

All settings are in `config.py`. Key sections:

#### Data & I/O

```python
DATA_DIR = Path("../scrapper/data_sourcing/output")
CHECKPOINT_DIR = Path("./checkpoints")
OUTPUT_DIR = Path("./output")
```

#### Model Configuration

```python
MODEL_MAPPING = {
    "fear_greed": ["llama3.1:latest"],
    "coindesk": ["llama3.1:latest"],
    "reddit": ["mistral-large-3:675b-cloud"],
    "truth_social": ["mistral-large-3:675b-cloud"],
    "binance": ["llama3.1:latest"],
    "coingecko": ["llama3.1:latest"],
}
```

**Note**: Each platform can map to multiple models for ensemble analysis. Results are averaged.

#### Platform Weights

```python
PLATFORM_WEIGHTS = {
    "fear_greed": 0.30,      # Most direct sentiment indicator
    "coindesk": 0.25,        # News articles
    "reddit": 0.15,          # Community discussion
    "truth_social": 0.10,    # Social posts
    "binance": 0.10,         # Trading volume/price
    "coingecko": 0.10,       # Market data
}
```

**Weights don't need to sum to 1.0** — they're normalized automatically.

#### Concurrency & Performance

```python
CONCURRENCY_LIMIT = 3              # Max parallel Ollama calls
BATCH_SIZE = 5                     # Entries per batch
TIMEOUT_SECONDS = 60               # Model inference timeout
```

**Tuning Guide**:
- `CONCURRENCY_LIMIT=1`: Safe, slow (serialized processing)
- `CONCURRENCY_LIMIT=3`: Balanced (recommended for 6GB+ VRAM)
- `CONCURRENCY_LIMIT=5+`: Fast (requires 12GB+ VRAM)

#### Retry & Resilience

```python
MAX_RETRIES = 3                    # Retry failed inferences
INITIAL_BACKOFF = 2.0              # Start backoff: 2s
MAX_BACKOFF = 30.0                 # Cap backoff: 30s
```

Backoff uses exponential strategy: 2s → 4s → 8s → ...

#### Feature Flags

```python
ENABLE_CHECKPOINTING = True        # Resume capability
ENABLE_CACHING = True              # Cache results
ENABLE_ENSEMBLE_MODE = True        # Multiple models per entry
```

---

## 📖 Usage

### Basic Run

```python
from market_mood_analyzer import MoodAnalyzer
import asyncio
import config

async def main():
    analyzer = MoodAnalyzer(config)
    global_mood = await analyzer.run()
    print(f"Market Mood: {global_mood}")

asyncio.run(main())
```

### Resume from Checkpoint

The analyzer automatically checks `checkpoints/progress_tracker.json` and skips already-processed entries:

```bash
# First run: processes 100 entries, gets interrupted at entry 60
python market_mood_analyzer.py

# Second run: automatically resumes from entry 61
python market_mood_analyzer.py
```

### Force Reprocess All

```python
# In main() function
global_mood = await analyzer.run(force_reprocess=True)
```

### Access Results Programmatically

```python
analyzer = MoodAnalyzer(config)
await analyzer.run()

for result in analyzer.results:
    print(f"Entry {result.entry_id}:")
    print(f"  Platform: {result.platform}")
    print(f"  Sentiment: {result.aggregated_sentiment}")
    print(f"  Confidence: {result.aggregated_confidence}")
    print(f"  Status: {result.status}")
```

---

## 🔄 Checkpointing & Resume

### How It Works

1. **Before Processing**: Check if entry ID is in `progress_tracker.json`
2. **During Processing**: Mark entry as "in_progress"
3. **On Success**: Mark entry as "processed", update tracker
4. **On Failure**: Log error in tracker with timestamp
5. **On Interrupt**: Gracefully save state, allow resume

### Checkpoint File Structure

```json
{
  "processed_ids": ["abc123def456", "xyz789..."],
  "failed_ids": {
    "failed001": {
      "error": "All models failed",
      "timestamp": "2024-01-15T10:30:45.123456"
    }
  },
  "start_time": "2024-01-15T10:00:00.000000",
  "last_updated": "2024-01-15T10:30:50.654321"
}
```

### Manual Reset

```bash
# Clear checkpoint to reprocess all
rm checkpoints/progress_tracker.json

# Or set force_reprocess=True in code
```

---

## 📐 Mathematical Foundation

### Global Mood Score Formula

$$M_G = \frac{\sum_{i=1}^{n} (S_i \times W_p)}{\sum W_p}$$

Where:
- **$M_G$**: Global market mood score (-1.0 to 1.0)
- **$S_i$**: Aggregated sentiment for entry $i$
- **$W_p$**: Weight for platform $p$
- **$n$**: Total number of completed entries

### Sentiment Score Interpretation

| Score Range | Interpretation |
|-----------|-----------------|
| 1.0 | Extremely bullish (euphoria, FOMO) |
| 0.5 | Moderately bullish (positive outlook) |
| 0.0 | Neutral (no clear sentiment) |
| -0.5 | Moderately bearish (negative outlook) |
| -1.0 | Extremely bearish (panic, crash expectations) |

### Ensemble Aggregation

When multiple models analyze the same entry:

$$S_i = \frac{\sum_{m=1}^{k} \text{sentiment}_m}{k}$$

Where $k$ is the number of models for that platform.

### Confidence Aggregation

Similarly for confidence scores:

$$C_i = \frac{\sum_{m=1}^{k} \text{confidence}_m}{k}$$

---

## 🔧 Troubleshooting

### Issue: `Data directory not found`

**Solution**:
```python
# Check DATA_DIR path
import config
print(config.DATA_DIR)
print(config.DATA_DIR.exists())
```

### Issue: `Connection refused` to Ollama

**Solution**:
```bash
# Verify Ollama is running
curl http://localhost:11434/api/tags

# If not, start Ollama
ollama serve

# Check the base URL in code
# Default: http://localhost:11434
```

### Issue: `JSON decode error` from Ollama response

**Solution**: The model may be returning malformed JSON. Check:
1. SYSTEM_PROMPT is clear about JSON format
2. Model is capable (use llama3.1 or mistral, not ancient models)
3. Increase TIMEOUT_SECONDS if model is slow
4. Check logs: `tail -f logs/mood_analyzer.log`

### Issue: Out of Memory (OOM)

**Solution**:
```python
# Reduce concurrency
config.CONCURRENCY_LIMIT = 1  # Serialize execution
config.BATCH_SIZE = 2         # Smaller batches
config.TIMEOUT_SECONDS = 120  # Give more time
```

### Issue: Checkpoint corrupted

**Solution**:
```bash
# Backup and reset
cp checkpoints/progress_tracker.json checkpoints/progress_tracker.json.bak
rm checkpoints/progress_tracker.json

# Next run will start fresh
python market_mood_analyzer.py
```

### Issue: All entries marked as failed

**Check**:
1. Are models specified in MODEL_MAPPING installed in Ollama?
2. Is Ollama running and accessible?
3. Are models loaded in memory? (`ollama list`)
4. Check logs for specific error messages

```bash
# List available models
ollama list

# Load a model if not present
ollama pull llama3.1
```

---

## ⚡ Performance Tuning

### Measure Current Performance

The report includes timing information:

```json
{
  "metadata": {
    "analysis_duration_seconds": 145.67,
    "total_entries_processed": 150
  }
}
```

**Throughput**: 150 entries ÷ 145.67 sec ≈ **1.03 entries/sec**

### Optimization Strategies

#### 1. Increase Concurrency (if VRAM allows)

```python
# Before: CONCURRENCY_LIMIT = 3
# After: CONCURRENCY_LIMIT = 5
# Expected: ~1.5-2x speedup (if VRAM supports)
```

#### 2. Use Faster Models

```python
# Before: "mistral-large-3:675b-cloud"  # 675B params
# After: "llama3.1:latest"              # 8B params
# Expected: 2-3x speedup
```

#### 3. Batch Processing

```python
# Before: BATCH_SIZE = 5
# After: BATCH_SIZE = 20
# Effect: Reduces I/O overhead
```

#### 4. Async I/O Optimization

```python
# The analyzer already uses aiohttp for async HTTP
# Further optimization: implement connection pooling
# (already included in aiohttp.ClientSession)
```

### Benchmark Template

```python
import time
import asyncio
from market_mood_analyzer import MoodAnalyzer
import config

async def benchmark():
    start = time.time()
    analyzer = MoodAnalyzer(config)
    await analyzer.run()
    elapsed = time.time() - start
    
    entries = len(analyzer.results)
    throughput = entries / elapsed
    
    print(f"Time: {elapsed:.2f}s")
    print(f"Entries: {entries}")
    print(f"Throughput: {throughput:.2f} entries/sec")
```

---

## 📊 Output Files

### `output/final_mood_report.json`

Main report with:
- Global mood score
- Platform statistics
- Individual entry results
- Top bullish/bearish entries

### `logs/mood_analyzer.log`

Detailed activity log including:
- Data loading
- Model inference
- Errors and warnings
- Processing timeline

### `checkpoints/progress_tracker.json`

State management:
- Processed entry IDs
- Failed entries with errors
- Timestamps

---

## 🔐 Best Practices

1. **Backup Checkpoints**: `cp checkpoints/progress_tracker.json checkpoints/progress_tracker.json.backup`
2. **Monitor Logs**: `tail -f logs/mood_analyzer.log`
3. **Validate Models**: Verify all models in MODEL_MAPPING are installed
4. **Test System Prompt**: Ensure models return valid JSON with test data
5. **Version Control**: Track `config.py` changes for reproducibility
6. **Archive Reports**: Keep historical reports for trend analysis

---

## 📝 License

This project is provided as-is for cryptocurrency sentiment analysis.

---

## 🤝 Support

For issues:
1. Check logs: `logs/mood_analyzer.log`
2. Verify Ollama: `curl http://localhost:11434/api/tags`
3. Review checkpoint: `cat checkpoints/progress_tracker.json`
4. Check config validation: `python config.py`
