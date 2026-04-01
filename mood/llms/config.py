"""
Configuration module for Crypto Market Mood Analyzer.

This module centralizes all configuration settings, model mappings, weights,
concurrency controls, and system prompts. Modify settings here to adjust the
behavior of the mood analyzer without touching the main logic.

Author: Senior Python Engineer
Date: 2024
"""

from pathlib import Path
from typing import Dict, List

# ============================================================================
# DATA & I/O SETTINGS
# ============================================================================

# Base directory paths
DATA_DIR = Path("../scrapper/data_sourcing/output")
"""Path to the directory containing JSON source files."""

CHECKPOINT_DIR = Path("./checkpoints")
"""Directory for storing progress/checkpoint files."""

OUTPUT_DIR = Path("./output")
"""Directory for final reports and analysis results."""

CHECKPOINT_FILE = CHECKPOINT_DIR / "progress_tracker.json"
"""File tracking which entries have been processed."""

FINAL_REPORT_FILE = OUTPUT_DIR / "final_mood_report.json"
"""File where the final aggregated mood report is saved."""

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

# Available Ollama models in the local instance
AVAILABLE_MODELS = [
    "kimi-k2.5:cloud",
    "minimax-m2.5:cloud",
    "qwen2.5vl:latest",
    "mistral-large-3:675b-cloud",
    "llama3.1:latest",
    "deepseek-coder:latest",
]
"""List of available local Ollama models."""

# Platform-to-model mapping: which models analyze which data sources
MODEL_MAPPING: Dict[str, List[str]] = {
    "fear_greed": ["mistral-large-3:675b-cloud"],
    "coindesk": ["mistral-large-3:675b-cloud"],
    "reddit": ["mistral-large-3:675b-cloud"],
    "truth_social": ["mistral-large-3:675b-cloud"],
    "binance": ["mistral-large-3:675b-cloud"],
    "coingecko": ["mistral-large-3:675b-cloud"],
}
"""
Maps each data platform to a list of models for redundancy/ensemble analysis.
If multiple models are assigned, their sentiment scores are averaged.
"""

# ============================================================================
# SENTIMENT WEIGHTS & AGGREGATION
# ============================================================================

PLATFORM_WEIGHTS: Dict[str, float] = {
    "fear_greed": 0.30,      # Fear & Greed Index: most direct sentiment indicator
    "coindesk": 0.25,        # News articles: important for market narrative
    "reddit": 0.15,          # Community discussion: grassroots sentiment
    "truth_social": 0.10,    # Social posts: niche sentiment
    "binance": 0.10,         # Trading volume/price: on-chain behavior
    "coingecko": 0.10,       # Market data: aggregate market sentiment
}
"""
Weights for aggregating platform sentiments into global mood.
Higher weight = more influence on final score.
Sum does not need to be 1.0; will be normalized automatically.
"""

# ============================================================================
# CONCURRENCY & PERFORMANCE SETTINGS
# ============================================================================

CONCURRENCY_LIMIT = 3
"""
Maximum number of simultaneous Ollama API calls.
Lower values prevent VRAM crashes; higher values speed up processing.
Tune based on your GPU/CPU memory: start with 3, increase if stable.
"""

BATCH_SIZE = 5
"""Number of entries to process per batch."""

TIMEOUT_SECONDS = 60
"""Maximum seconds to wait for a single model inference."""

# ============================================================================
# RETRY & RESILIENCE SETTINGS
# ============================================================================

MAX_RETRIES = 3
"""Maximum retry attempts for failed sentiment analysis."""

INITIAL_BACKOFF = 2.0
"""Initial backoff delay in seconds (exponential backoff: 2, 4, 8, ...)."""

MAX_BACKOFF = 30.0
"""Maximum backoff delay to prevent excessively long waits."""

# ============================================================================
# SYSTEM PROMPTS FOR SENTIMENT ANALYSIS
# ============================================================================

SYSTEM_PROMPT_SENTIMENT = """You are a sentiment analysis expert for cryptocurrency markets. Analyze the given content and provide a sentiment score for Bitcoin/crypto market mood.

CRITICAL INSTRUCTIONS:
1. Your response MUST be ONLY a valid JSON object.
2. Do NOT include markdown code blocks, explanations, or any additional text.
3. Do NOT wrap your response in ```json``` tags or similar.
4. Return ONLY the JSON object on a single line or multiple lines.

Required JSON format (all fields mandatory):
{
  "sentiment_score": <float between -1.0 and 1.0>,
  "confidence": <float between 0.0 and 1.0>,
  "reasoning": "<brief explanation (max 50 words)>"
}

Sentiment score interpretation:
  -1.0: Extremely bearish (panic, crash expectations)
  -0.5: Moderately bearish (negative outlook)
   0.0: Neutral (no clear sentiment)
   0.5: Moderately bullish (positive outlook)
   1.0: Extremely bullish (euphoria, FOMO, surge expectations)

Confidence score interpretation:
  0.0: Completely uncertain
  0.5: Moderately confident
  1.0: Very confident in the assessment

EXAMPLE VALID RESPONSE:
{"sentiment_score": 0.45, "confidence": 0.82, "reasoning": "Positive adoption news balanced by regulatory concerns"}
"""

SYSTEM_PROMPT_FALLBACK = """Extract sentiment from the text. Return ONLY valid JSON:
{"sentiment_score": 0.0, "confidence": 0.5, "reasoning": "Unable to fully assess"}
"""

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = "INFO"
"""Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL."""

LOG_FILE = Path("./logs/mood_analyzer.log")
"""Path to the main application log file."""

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
"""Format string for log messages."""

# ============================================================================
# DATA VALIDATION & PREPROCESSING
# ============================================================================

REQUIRED_ENTRY_FIELDS = ["text", "timestamp", "platform"]
"""Fields that must be present in each data entry."""

TEXT_MIN_LENGTH = 10
"""Minimum character count for valid entry text."""

TEXT_MAX_LENGTH = 10000
"""Maximum character count to prevent token overflow."""

# ============================================================================
# QUALITY ASSURANCE
# ============================================================================

SENTIMENT_VALIDATION_ENABLED = True
"""Validate sentiment scores are within [-1.0, 1.0] range."""

CONFIDENCE_VALIDATION_ENABLED = True
"""Validate confidence scores are within [0.0, 1.0] range."""

DUPLICATE_DETECTION = True
"""Enable duplicate entry detection based on text hash."""

# ============================================================================
# REPORTING & ANALYSIS
# ============================================================================

INCLUDE_DETAILED_RESULTS = True
"""Include all individual entry results in the final report (can be large)."""

REPORT_SUMMARY_LIMIT = 100
"""Maximum number of top/bottom entries to include in summary."""

EXPORT_FORMAT = "json"
"""Output format for final report: 'json', 'csv', 'both'."""

# ============================================================================
# FEATURE FLAGS
# ============================================================================

ENABLE_CHECKPOINTING = True
"""Enable resumable processing with progress tracking."""

ENABLE_CACHING = True
"""Cache sentiment analysis results to avoid re-analyzing identical content."""

ENABLE_ENSEMBLE_MODE = True
"""
Use multiple models per entry and average results.
Disable to use only the first model in MODEL_MAPPING.
"""

ENABLE_DETAILED_LOGGING = False
"""Enable verbose logging for debugging (high verbosity)."""

# ============================================================================
# HELPER FUNCTIONS FOR CONFIG VALIDATION
# ============================================================================


def validate_config() -> bool:
    """
    Validates the configuration for consistency and correctness.
    
    Returns:
        bool: True if config is valid, False otherwise.
    """
    errors = []

    # Check weights sum reasonably
    total_weight = sum(PLATFORM_WEIGHTS.values())
    if total_weight == 0:
        errors.append("PLATFORM_WEIGHTS sum to zero")

    # Check all platforms in MODEL_MAPPING have weights
    for platform in MODEL_MAPPING:
        if platform not in PLATFORM_WEIGHTS:
            errors.append(f"Platform '{platform}' in MODEL_MAPPING but not in PLATFORM_WEIGHTS")

    # Check concurrency limits
    if CONCURRENCY_LIMIT < 1:
        errors.append("CONCURRENCY_LIMIT must be at least 1")

    if BATCH_SIZE < 1:
        errors.append("BATCH_SIZE must be at least 1")

    # Check timeout
    if TIMEOUT_SECONDS < 5:
        errors.append("TIMEOUT_SECONDS should be at least 5 seconds")

    # Check backoff settings
    if INITIAL_BACKOFF <= 0:
        errors.append("INITIAL_BACKOFF must be positive")

    if MAX_BACKOFF < INITIAL_BACKOFF:
        errors.append("MAX_BACKOFF must be >= INITIAL_BACKOFF")

    # Check text length constraints
    if TEXT_MIN_LENGTH > TEXT_MAX_LENGTH:
        errors.append("TEXT_MIN_LENGTH cannot exceed TEXT_MAX_LENGTH")

    if errors:
        for error in errors:
            print(f"CONFIG ERROR: {error}")
        return False

    return True


if __name__ == "__main__":
    # Simple validation when config.py is run directly
    print("Validating configuration...")
    if validate_config():
        print("✓ Configuration is valid!")
    else:
        print("✗ Configuration has errors")
        exit(1)
