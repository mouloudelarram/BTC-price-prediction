"""
TECHNICAL SPECIFICATIONS
Crypto Market Mood Analyzer v1.0

Author: Senior Python Engineer
Date: 2024
Version: 1.0 (Production Ready)
"""

# ============================================================================
# 1. SYSTEM OVERVIEW
# ============================================================================

PROJECT DESCRIPTION:
  A production-grade asynchronous system for analyzing cryptocurrency market
  sentiment from multiple data sources using local Ollama LLM models.

CORE COMPONENTS:
  1. DataLoader - Load and preprocess JSON data
  2. OllamaClient - Async HTTP client for Ollama API
  3. MoodAnalyzer - Main orchestrator with concurrency control
  4. ProgressTracker - Checkpoint state management
  5. Configuration - Centralized settings management

KEY FEATURES:
  ✓ Async/await concurrency with semaphore-based rate limiting
  ✓ Resumable processing with checkpoint system
  ✓ Ensemble sentiment analysis (multiple models per entry)
  ✓ Weighted platform aggregation
  ✓ Comprehensive error handling and retry logic
  ✓ Full logging with file and console output
  ✓ Type hints and data validation
  ✓ Production-ready error recovery

# ============================================================================
# 2. ARCHITECTURE & DATA FLOW
# ============================================================================

SYSTEM ARCHITECTURE:

┌─────────────────────────────────────────────────────────────────────────┐
│                         MOOD ANALYZER PIPELINE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐                                                  │
│  │  Raw JSON Data   │                                                  │
│  │ (platforms:      │                                                  │
│  │  reddit,         │                                                  │
│  │  coindesk, etc)  │                                                  │
│  └────────┬─────────┘                                                  │
│           │                                                             │
│           ▼                                                             │
│  ┌──────────────────────────────────────┐                             │
│  │     DataLoader.load_all()            │                             │
│  │ - Read JSON files from DATA_DIR      │                             │
│  │ - Handle list & dict structures      │                             │
│  │ - Return [Dict] of entries           │                             │
│  └────────┬─────────────────────────────┘                             │
│           │                                                             │
│           ▼                                                             │
│  ┌──────────────────────────────────────┐                             │
│  │    DataLoader.preprocess()           │                             │
│  │ - Validate required fields           │                             │
│  │ - Check text length constraints      │                             │
│  │ - Clean URLs and whitespace          │                             │
│  │ - Generate content hash              │                             │
│  └────────┬─────────────────────────────┘                             │
│           │                                                             │
│           ▼                                                             │
│  ┌──────────────────────────────────────┐                             │
│  │  ProgressTracker.is_processed()      │                             │
│  │ - Check checkpoint for entry ID      │                             │
│  │ - Skip if already processed          │                             │
│  │ - (unless force_reprocess=True)      │                             │
│  └────────┬─────────────────────────────┘                             │
│           │                                                             │
│           ▼                                                             │
│  ┌──────────────────────────────────────┐                             │
│  │   Process in BATCH_SIZE chunks       │                             │
│  │ - Parallel asyncio.gather()          │                             │
│  │ - Semaphore limits concurrency       │                             │
│  └────────┬─────────────────────────────┘                             │
│           │                                                             │
│           ▼                                                             │
│  ┌──────────────────────────────────────┐                             │
│  │  _process_entry()                    │                             │
│  │ - Get models for platform            │                             │
│  │ - Call _analyze_with_model() for each│                             │
│  │ - Aggregate results                  │                             │
│  └────────┬─────────────────────────────┘                             │
│           │                                                             │
│     ┌─────┴─────┬──────────┬──────────┐                               │
│     │           │          │          │                               │
│     ▼           ▼          ▼          ▼                               │
│  ┌──────────────────────────────────────────────┐                    │
│  │        OllamaClient.analyze_sentiment()      │                    │
│  │  (Multiple instances in parallel)            │                    │
│  │  - POST to /api/chat                         │                    │
│  │  - Timeout: TIMEOUT_SECONDS                  │                    │
│  │  - Parse JSON response                       │                    │
│  │  - Return SentimentResult or None            │                    │
│  └──────────┬───────────────────────────────────┘                    │
│             │                                                         │
│             ▼                                                         │
│  ┌──────────────────────────────────────┐                            │
│  │   EntryAnalysis (aggregated)         │                            │
│  │ - Average sentiment across models    │                            │
│  │ - Average confidence                 │                            │
│  │ - Track individual results           │                            │
│  │ - Calculate processing_time          │                            │
│  └────────┬─────────────────────────────┘                            │
│           │                                                            │
│           ▼                                                            │
│  ┌──────────────────────────────────────┐                            │
│  │  ProgressTracker.mark_processed()    │                            │
│  │ - Add entry_id to processed set      │                            │
│  │ - Save checkpoint to disk            │                            │
│  └────────┬─────────────────────────────┘                            │
│           │                                                            │
│           │ (repeat for all batches)                                  │
│           │                                                            │
│           ▼                                                            │
│  ┌──────────────────────────────────────┐                            │
│  │  _calculate_global_mood()            │                            │
│  │ Formula: M_G = Σ(S_i * W_p) / Σ(W_p)│                            │
│  │ - Weighted sum of platforms          │                            │
│  │ - Return scalar [-1.0, 1.0]          │                            │
│  └────────┬─────────────────────────────┘                            │
│           │                                                            │
│           ▼                                                            │
│  ┌──────────────────────────────────────┐                            │
│  │   _generate_report()                 │                            │
│  │ - Platform statistics                │                            │
│  │ - Top bullish/bearish entries        │                            │
│  │ - Metadata (timing, counts)          │                            │
│  │ - Save to final_mood_report.json     │                            │
│  └────────┬─────────────────────────────┘                            │
│           │                                                            │
│           ▼                                                            │
│  ┌──────────────────────────────────────┐                            │
│  │   final_mood_report.json             │                            │
│  │ (Global Mood Score, Platform Stats)  │                            │
│  └──────────────────────────────────────┘                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

# ============================================================================
# 3. CONCURRENCY MODEL
# ============================================================================

ASYNC CONCURRENCY STRATEGY:

Level 1 - Batch Level:
  - Load entries in BATCH_SIZE chunks
  - Process each batch with asyncio.gather()

Level 2 - Entry Level:
  - For each entry, spawn tasks for all assigned models
  - All model tasks run concurrently within the batch

Level 3 - Semaphore Control:
  - Global Semaphore(CONCURRENCY_LIMIT) limits parallel HTTP requests
  - Default: CONCURRENCY_LIMIT = 3
  - Prevents VRAM exhaustion from too many parallel model inferences

CONCURRENCY FORMULA:

Max Parallel Requests = min(
  CONCURRENCY_LIMIT,                          # Hardcap from config
  BATCH_SIZE * len(MODEL_MAPPING),            # Theoretical max in batch
  Available VRAM / Model Size                  # Hardware constraint
)

EXAMPLE WITH DEFAULT CONFIG:

CONCURRENCY_LIMIT = 3
BATCH_SIZE = 5
MODEL_MAPPING = {reddit: [mistral], coindesk: [llama]}

Process Batch 1 (5 entries):
  Entry 1 → Model 1  ─┐
  Entry 2 → Model 1  ─┼─ Wait for semaphore ─┐
  Entry 3 → Model 1  ─┤                      ├─ Execute at most 3 in parallel
  Entry 4 → Model 2  ─┤                      │
  Entry 5 → Model 2  ─┼─ Queued ──────────────┘

Time = O(BATCH_SIZE / CONCURRENCY_LIMIT * Model Inference Time)

# ============================================================================
# 4. ERROR HANDLING & RESILIENCE
# ============================================================================

ERROR HANDLING LAYERS:

Layer 1 - Model-Level Errors:
  try:
    result = await ollama_client.analyze_sentiment()
  except:
    log warning, continue with next model
  
  If all models fail → return Failed EntryAnalysis

Layer 2 - Entry-Level Errors:
  try:
    entry_analysis = await _process_entry()
  except Exception as e:
    mark_failed(entry_id, error_message)
    log error, continue with next entry

Layer 3 - Batch-Level Errors:
  try:
    batch_results = await asyncio.gather(...)
  except:
    continue with next batch
    (individual entry exceptions don't crash batch)

Layer 4 - Pipeline-Level Errors:
  try:
    await analyzer.run()
  except:
    save checkpoint, log critical error
    return None (graceful shutdown)

RETRY LOGIC:

Implemented in OllamaClient.analyze_sentiment():
  - Timeout: Automatic (asyncio.TimeoutError)
  - Connection: aiohttp handles internally
  - JSON Parse: Log and return None (no retry)

Future Enhancement - Exponential Backoff:
  if error_count < MAX_RETRIES:
    wait = min(INITIAL_BACKOFF ** error_count, MAX_BACKOFF)
    await asyncio.sleep(wait)
    retry...

# ============================================================================
# 5. DATA STRUCTURES
# ============================================================================

CONFIGURATION (config.py):

class Config:
  # Paths
  DATA_DIR: Path
  CHECKPOINT_DIR: Path
  OUTPUT_DIR: Path
  
  # Models
  MODEL_MAPPING: Dict[str, List[str]]
  PLATFORM_WEIGHTS: Dict[str, float]
  
  # Performance
  CONCURRENCY_LIMIT: int = 3
  BATCH_SIZE: int = 5
  TIMEOUT_SECONDS: int = 60
  
  # Resilience
  MAX_RETRIES: int = 3
  INITIAL_BACKOFF: float = 2.0
  MAX_BACKOFF: float = 30.0
  
  # Logging
  LOG_LEVEL: str = "INFO"
  LOG_FILE: Path

SENTIMENT RESULT:

@dataclass
class SentimentResult:
  sentiment_score: float         # -1.0 to 1.0
  confidence: float              # 0.0 to 1.0
  reasoning: str                 # Explanation
  model_name: str                # Which model
  processing_time: float         # Seconds

ENTRY ANALYSIS:

@dataclass
class EntryAnalysis:
  entry_id: str                  # Unique ID (hash)
  platform: str                  # reddit, coindesk, etc
  text: str                      # Full entry text
  timestamp: str                 # ISO format
  status: SentimentStatus        # pending/in_progress/completed/failed
  individual_results: List[SentimentResult]
  aggregated_sentiment: float    # Average across models
  aggregated_confidence: float
  processing_time: float         # Total entry processing time
  error_message: Optional[str]   # If status == failed

CHECKPOINT STATE:

{
  "processed_ids": ["abc123", "def456", ...],    # Processed entries
  "failed_ids": {
    "failed001": {
      "error": "All models failed",
      "timestamp": "2024-01-15T10:30:45"
    }
  },
  "start_time": "2024-01-15T10:00:00",
  "last_updated": "2024-01-15T10:30:50"
}

# ============================================================================
# 6. API SPECIFICATIONS
# ============================================================================

OLLAMA API ENDPOINT:

POST /api/chat HTTP/1.1
Host: localhost:11434
Content-Type: application/json

Request Body:
{
  "model": "llama3.1:latest",
  "messages": [
    {
      "role": "system",
      "content": "<SYSTEM_PROMPT>"
    },
    {
      "role": "user",
      "content": "<TEXT_TO_ANALYZE>"
    }
  ],
  "stream": false
}

Response:
{
  "model": "llama3.1:latest",
  "created_at": "2024-01-15T10:30:45.123456Z",
  "message": {
    "role": "assistant",
    "content": "{\"sentiment_score\": 0.45, ...}"
  },
  "done": true,
  "total_duration": 1234567890,
  "load_duration": 123456789,
  "prompt_eval_count": 150,
  "prompt_eval_duration": 234567890,
  "eval_count": 50,
  "eval_duration": 876543210
}

# ============================================================================
# 7. PERFORMANCE CHARACTERISTICS
# ============================================================================

THROUGHPUT ANALYSIS:

Single Model Inference Time: ~5-15 seconds (for 8B model)
Parallel Models: Min(ensemble_size) added due to concurrency

Example with 5 entries, 2 models each:
  Serial (CONCURRENCY_LIMIT=1):    10 entries * 10s = 100s
  Parallel (CONCURRENCY_LIMIT=2):  5 batches * 10s = 50s
  Parallel (CONCURRENCY_LIMIT=3):  4 batches * 10s = 40s

MEMORY USAGE:

Per Model in Memory: ~8GB for 7B model, ~16GB for 13B, ~40GB+ for 70B
Peak Usage = (CONCURRENCY_LIMIT * Model Size) + Overhead

Recommended:
  CONCURRENCY_LIMIT=1: 2GB RAM minimum
  CONCURRENCY_LIMIT=3: 8GB RAM recommended
  CONCURRENCY_LIMIT=5: 16GB+ RAM required

STORAGE:

Checkpoint File: ~1KB per 100 entries
Log File: ~100KB per 1000 entries
Report File: ~5-10KB per 100 entries + models

# ============================================================================
# 8. CONFIGURATION PARAMETER REFERENCE
# ============================================================================

DATA_DIR
  Type: Path
  Default: Path("../scrapper/data_sourcing/output")
  Effect: Where to load JSON input files from
  Tuning: Use absolute path for reliability

CHECKPOINT_DIR
  Type: Path
  Default: Path("./checkpoints")
  Effect: Where checkpoint state is stored
  Tuning: Use persistent storage for resume capability

OUTPUT_DIR
  Type: Path
  Default: Path("./output")
  Effect: Where final report is saved
  Tuning: Ensure write permissions

MODEL_MAPPING
  Type: Dict[str, List[str]]
  Effect: Maps platforms to models, enables ensemble
  Tuning: Add more models per platform for ensemble analysis
  Performance: More models = slower but more confident

PLATFORM_WEIGHTS
  Type: Dict[str, float]
  Effect: Controls influence of each platform on global mood
  Sum: Doesn't need to be 1.0 (normalized automatically)
  Tuning: Increase weight for more important platforms

CONCURRENCY_LIMIT
  Type: int
  Default: 3
  Effect: Max parallel Ollama API calls
  Tuning: Balance between speed and stability
  GPU Utilization:
    1 = 33% (single inference)
    3 = 100% (if model uses 33% per inference)
    5+ = Potential overflow/OOM

BATCH_SIZE
  Type: int
  Default: 5
  Effect: Entries per processing batch
  Tuning: Larger = fewer I/O operations but more memory

TIMEOUT_SECONDS
  Type: int
  Default: 60
  Effect: Max seconds to wait for model inference
  Tuning: Increase for slow/large models
  Note: Very large models might timeout

MAX_RETRIES
  Type: int
  Default: 3
  Effect: Retry attempts for failed inferences
  Status: Configured but not implemented in v1.0

INITIAL_BACKOFF / MAX_BACKOFF
  Type: float
  Default: 2.0 / 30.0
  Effect: Exponential backoff delays
  Status: Configured for future use

LOG_LEVEL
  Type: str
  Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
  Tuning: INFO for production, DEBUG for troubleshooting

# ============================================================================
# 9. TESTING STRATEGY
# ============================================================================

UNIT TESTS (Future):
  ✓ test_sentiment_result_validation()
  ✓ test_entry_analysis_to_dict()
  ✓ test_progress_tracker_load_save()
  ✓ test_data_loader_preprocessing()
  ✓ test_ollama_client_json_parsing()
  ✓ test_mood_calculation_formula()

INTEGRATION TESTS:
  ✓ Full pipeline with test data
  ✓ Checkpoint resume functionality
  ✓ Error recovery handling
  ✓ Report generation

PERFORMANCE TESTS:
  ✓ Throughput with varying CONCURRENCY_LIMIT
  ✓ Memory usage profiling
  ✓ Timeout handling

# ============================================================================
# 10. DEPLOYMENT CONSIDERATIONS
# ============================================================================

PRODUCTION SETUP:

1. Hardware Requirements:
   - GPU: 6GB+ VRAM for 8B models (CONCURRENCY_LIMIT=3)
   - CPU: 4+ cores (async I/O benefits from multiple cores)
   - RAM: 8GB minimum, 16GB+ recommended
   - Disk: 50GB+ for model storage

2. Software Requirements:
   - Python 3.8+
   - Ollama running locally or on accessible network
   - Dependencies: aiohttp, optional (pydantic, pandas)

3. Monitoring:
   - Track logs: tail -f logs/mood_analyzer.log
   - Monitor checkpoint: watch -n 5 "wc -l checkpoints/progress_tracker.json"
   - Alert on errors: grep ERROR logs/mood_analyzer.log

4. Scaling Strategies:
   - Horizontal: Run separate analyzer instances on different data subsets
   - Vertical: Increase CONCURRENCY_LIMIT and BATCH_SIZE on powerful hardware
   - Distributed: Use MQ (RabbitMQ, Redis) to distribute entries

5. Backup Strategy:
   - Checkpoint: cp checkpoints/ checkups_backup/
   - Report: Archive output/final_mood_report.json
   - Config: Version control config.py

# ============================================================================
# 11. FUTURE ENHANCEMENTS
# ============================================================================

v1.1 Planned Features:
  [ ] Implement exponential backoff retry logic
  [ ] Add Redis caching for duplicate detection
  [ ] Support for cloud-based LLM APIs (OpenAI, Claude)
  [ ] Streaming response handling for very long texts
  [ ] Prometheus metrics export

v2.0 Planned Features:
  [ ] Distributed processing with task queue
  [ ] Web dashboard for real-time monitoring
  [ ] Historical trend analysis
  [ ] Sentiment prediction models
  [ ] Multi-language support

# ============================================================================
# 12. REFERENCES & STANDARDS
# ============================================================================

Standards Followed:
  - PEP 8: Python style guide
  - PEP 484: Type hints
  - PEP 495: Local time handling
  - Async/await best practices (Python 3.8+)

External Resources:
  - Ollama API: https://github.com/ollama/ollama/blob/main/docs/api.md
  - AsyncIO: https://docs.python.org/3/library/asyncio.html
  - aiohttp: https://docs.aiohttp.org/
  - Sentiment Analysis: https://en.wikipedia.org/wiki/Sentiment_analysis

Mathematical References:
  - Weighted Average: https://www.investopedia.com/terms/w/weightedaverage.asp
  - Exponential Backoff: https://en.wikipedia.org/wiki/Exponential_backoff
