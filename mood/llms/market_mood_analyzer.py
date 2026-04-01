"""
Crypto Market Mood Analyzer - Production Grade Implementation

A robust, asynchronous system for analyzing cryptocurrency market sentiment
from multiple sources using local Ollama LLM models. Features include:
- Async/concurrent processing with configurable concurrency limits
- Checkpointing and resumable processing
- Ensemble sentiment analysis (multiple models per entry)
- Weighted aggregation of platform sentiments
- Comprehensive error handling and logging
- State management with automatic recovery

Author: Senior Python Engineer
Date: 2024
"""

import asyncio
import json
import logging
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import time

import aiohttp

# Import configuration
import config

# ============================================================================
# TYPE DEFINITIONS & DATA CLASSES
# ============================================================================


class SentimentStatus(Enum):
    """Status of sentiment analysis for an entry."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class SentimentResult:
    """Result from a single model's sentiment analysis."""
    sentiment_score: float
    confidence: float
    reasoning: str
    model_name: str
    processing_time: float

    def is_valid(self) -> bool:
        """Validate that sentiment values are within acceptable ranges."""
        return (
            -1.0 <= self.sentiment_score <= 1.0
            and 0.0 <= self.confidence <= 1.0
            and len(self.reasoning) > 0
        )


@dataclass
class EntryAnalysis:
    """Complete analysis result for a single data entry."""
    entry_id: str
    platform: str
    text: str
    timestamp: str
    status: SentimentStatus
    individual_results: List[SentimentResult]
    aggregated_sentiment: float
    aggregated_confidence: float
    processing_time: float
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "entry_id": self.entry_id,
            "platform": self.platform,
            "text": self.text[:500],  # Truncate for output
            "timestamp": self.timestamp,
            "status": self.status.value,
            "individual_results": [
                {
                    "sentiment_score": r.sentiment_score,
                    "confidence": r.confidence,
                    "reasoning": r.reasoning,
                    "model_name": r.model_name,
                    "processing_time": r.processing_time,
                }
                for r in self.individual_results
            ],
            "aggregated_sentiment": self.aggregated_sentiment,
            "aggregated_confidence": self.aggregated_confidence,
            "processing_time": self.processing_time,
            "error_message": self.error_message,
        }


# ============================================================================
# LOGGING SETUP
# ============================================================================


def setup_logging() -> logging.Logger:
    """Configure logging with both file and console handlers."""
    config.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("MoodAnalyzer")
    logger.setLevel(logging.getLevelName(config.LOG_LEVEL))

    # File handler
    fh = logging.FileHandler(config.LOG_FILE)
    fh.setLevel(logging.DEBUG)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(config.LOG_FORMAT)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # Clear existing handlers to avoid duplicates
    logger.handlers = []
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


logger = setup_logging()

# ============================================================================
# CHECKPOINT & STATE MANAGEMENT
# ============================================================================


class ProgressTracker:
    """Manages checkpoint state for resumable processing."""

    def __init__(self, checkpoint_file: Path):
        self.checkpoint_file = checkpoint_file
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        self.state: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        """Load checkpoint state from disk."""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, "r") as f:
                    state = json.load(f)
                    logger.info(f"Loaded checkpoint with {len(state.get('processed_ids', []))} processed entries")
                    return state
            except Exception as e:
                logger.warning(f"Failed to load checkpoint: {e}. Starting fresh.")
        return {
            "processed_ids": set(),
            "failed_ids": {},
            "start_time": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
        }

    def is_processed(self, entry_id: str) -> bool:
        """Check if entry has already been processed."""
        # Convert to list for JSON serialization
        processed = self.state.get("processed_ids", [])
        return entry_id in processed

    def mark_processed(self, entry_id: str) -> None:
        """Mark entry as processed."""
        processed = self.state.get("processed_ids", [])
        if isinstance(processed, list):
            processed = set(processed)
        processed.add(entry_id)
        self.state["processed_ids"] = list(processed)
        self.state["last_updated"] = datetime.now().isoformat()
        self._save()

    def mark_failed(self, entry_id: str, error: str) -> None:
        """Mark entry as failed with error message."""
        failed = self.state.get("failed_ids", {})
        failed[entry_id] = {"error": error, "timestamp": datetime.now().isoformat()}
        self.state["failed_ids"] = failed
        self.state["last_updated"] = datetime.now().isoformat()
        self._save()

    def get_stats(self) -> Dict[str, Any]:
        """Get checkpoint statistics."""
        return {
            "total_processed": len(self.state.get("processed_ids", [])),
            "total_failed": len(self.state.get("failed_ids", {})),
            "start_time": self.state.get("start_time"),
            "last_updated": self.state.get("last_updated"),
        }

    def _save(self) -> None:
        """Save checkpoint state to disk."""
        try:
            # Ensure processed_ids is serializable
            state_copy = self.state.copy()
            state_copy["processed_ids"] = list(state_copy.get("processed_ids", []))
            with open(self.checkpoint_file, "w") as f:
                json.dump(state_copy, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")


# ============================================================================
# DATA LOADING & PREPROCESSING
# ============================================================================


class DataLoader:
    """Loads and preprocesses data from JSON files."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.logger = logger

    def load_all(self) -> List[Dict[str, Any]]:
        """Load all JSON files from data directory."""
        entries = []

        if not self.data_dir.exists():
            self.logger.error(f"Data directory not found: {self.data_dir}")
            return entries

        for json_file in self.data_dir.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        entries.extend(data)
                    elif isinstance(data, dict):
                        entries.append(data)
                    self.logger.info(f"Loaded {len(entries)} entries from {json_file.name}")
            except Exception as e:
                self.logger.error(f"Failed to load {json_file.name}: {e}")

        return entries

    @staticmethod
    def preprocess(entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Preprocess and validate a data entry."""
        # Check required fields
        if not all(field in entry for field in config.REQUIRED_ENTRY_FIELDS):
            return None

        # Handle both "text" and "content" field names
        text = entry.get("text") or entry.get("content")
        if not text or not isinstance(text, str):
            return None
        
        text = text.strip()

        # Validate text length
        if len(text) < config.TEXT_MIN_LENGTH or len(text) > config.TEXT_MAX_LENGTH:
            return None

        # Clean text
        text = re.sub(r"http\S+", "", text)  # Remove URLs
        text = re.sub(r"\s+", " ", text).strip()  # Normalize whitespace

        return {
            "text": text,
            "timestamp": entry.get("timestamp"),
            "platform": entry.get("platform"),
            "metadata": entry.get("metadata", {}),
        }

    @staticmethod
    def generate_entry_id(entry: Dict[str, Any]) -> str:
        """Generate unique ID for entry based on content hash."""
        text_to_hash = f"{entry['text']}-{entry['timestamp']}-{entry['platform']}"
        return hashlib.sha256(text_to_hash.encode()).hexdigest()[:12]


# ============================================================================
# SENTIMENT ANALYSIS ENGINE
# ============================================================================


class OllamaClient:
    """Async client for Ollama API."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.logger = logger

    async def analyze_sentiment(
        self,
        text: str,
        model: str,
        timeout: int = config.TIMEOUT_SECONDS,
    ) -> Optional[SentimentResult]:
        """
        Send text to Ollama for sentiment analysis.

        Args:
            text: The text to analyze
            model: Model name to use
            timeout: Timeout in seconds

        Returns:
            SentimentResult if successful, None otherwise
        """
        start_time = time.time()

        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": config.SYSTEM_PROMPT_SENTIMENT},
                        {"role": "user", "content": text},
                    ],
                    "stream": False,
                }

                async with session.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        self.logger.warning(
                            f"Ollama API error ({resp.status}) with model {model}: {error_text[:200]}"
                        )
                        return None

                    data = await resp.json()
                    response_text = data.get("message", {}).get("content", "").strip()

                    # Parse JSON response
                    try:
                        result_json = self._parse_json_response(response_text)
                        if not self._validate_sentiment_json(result_json):
                            self.logger.warning(f"Invalid sentiment structure from {model}")
                            return None

                        processing_time = time.time() - start_time
                        return SentimentResult(
                            sentiment_score=result_json["sentiment_score"],
                            confidence=result_json["confidence"],
                            reasoning=result_json["reasoning"],
                            model_name=model,
                            processing_time=processing_time,
                        )

                    except (json.JSONDecodeError, KeyError, ValueError) as e:
                        self.logger.warning(
                            f"Failed to parse sentiment JSON from {model}: {e}. Response: {response_text[:200]}"
                        )
                        return None

        except asyncio.TimeoutError:
            self.logger.warning(f"Timeout analyzing with model {model}")
            return None
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment with {model}: {e}")
            return None

    @staticmethod
    def _parse_json_response(text: str) -> Dict[str, Any]:
        """Extract JSON from response, handling markdown code blocks."""
        # Remove markdown code blocks if present
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"```\s*", "", text)
        text = text.strip()

        # Try to extract JSON object
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())

        return json.loads(text)

    @staticmethod
    def _validate_sentiment_json(data: Dict[str, Any]) -> bool:
        """Validate sentiment JSON structure."""
        required_keys = {"sentiment_score", "confidence", "reasoning"}
        if not required_keys.issubset(data.keys()):
            return False

        # Type checks
        if not isinstance(data["sentiment_score"], (int, float)):
            return False
        if not isinstance(data["confidence"], (int, float)):
            return False
        if not isinstance(data["reasoning"], str):
            return False

        # Range checks
        if not (-1.0 <= data["sentiment_score"] <= 1.0):
            return False
        if not (0.0 <= data["confidence"] <= 1.0):
            return False

        return True


# ============================================================================
# MAIN MOOD ANALYZER
# ============================================================================


class MoodAnalyzer:
    """Main orchestrator for sentiment analysis pipeline."""

    def __init__(self, config_obj=config):
        self.config = config_obj
        self.logger = logger
        self.data_loader = DataLoader(self.config.DATA_DIR)
        self.ollama_client = OllamaClient()
        self.progress_tracker = ProgressTracker(self.config.CHECKPOINT_FILE)
        self.semaphore = asyncio.Semaphore(self.config.CONCURRENCY_LIMIT)
        self.results: List[EntryAnalysis] = []

        # Validate config
        if not self.config.validate_config():
            raise ValueError("Configuration validation failed")

        self.logger.info("MoodAnalyzer initialized")

    async def run(self, force_reprocess: bool = False) -> float:
        """
        Execute the complete sentiment analysis pipeline.

        Args:
            force_reprocess: If True, ignore checkpoints and reprocess all entries

        Returns:
            Global market mood score
        """
        self.logger.info("=" * 70)
        self.logger.info("STARTING CRYPTO MARKET MOOD ANALYSIS")
        self.logger.info("=" * 70)

        start_time = time.time()

        # Load data
        raw_entries = self.data_loader.load_all()
        if not raw_entries:
            self.logger.warning("No data loaded. Check DATA_DIR configuration.")
            return 0.0

        # Preprocess data
        entries_to_process = []
        for entry in raw_entries:
            preprocessed = self.data_loader.preprocess(entry)
            if preprocessed:
                entry_id = self.data_loader.generate_entry_id(preprocessed)

                # Check if already processed (unless force_reprocess)
                if not force_reprocess and self.progress_tracker.is_processed(entry_id):
                    self.logger.debug(f"Skipping already-processed entry: {entry_id}")
                    continue

                entries_to_process.append((entry_id, preprocessed))

        self.logger.info(f"Loaded {len(raw_entries)} raw entries")
        self.logger.info(f"Processing {len(entries_to_process)} new/updated entries")
        self.logger.info(f"Resuming from checkpoint: {self.progress_tracker.get_stats()}")

        # Process entries in batches
        total_batches = (len(entries_to_process) + self.config.BATCH_SIZE - 1) // self.config.BATCH_SIZE
        for batch_idx in range(0, len(entries_to_process), self.config.BATCH_SIZE):
            batch = entries_to_process[batch_idx : batch_idx + self.config.BATCH_SIZE]
            batch_num = batch_idx // self.config.BATCH_SIZE + 1

            self.logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} entries)")

            # Process batch concurrently
            batch_results = await asyncio.gather(
                *[self._process_entry(entry_id, entry) for entry_id, entry in batch],
                return_exceptions=False,
            )

            self.results.extend(batch_results)

            # Update progress
            for result in batch_results:
                if result.status == SentimentStatus.COMPLETED:
                    self.progress_tracker.mark_processed(result.entry_id)
                elif result.status == SentimentStatus.FAILED:
                    self.progress_tracker.mark_failed(result.entry_id, result.error_message or "Unknown error")

        # Aggregate results
        global_mood = self._calculate_global_mood()

        # Generate report
        elapsed_time = time.time() - start_time
        self._generate_report(global_mood, elapsed_time)

        self.logger.info("=" * 70)
        self.logger.info("ANALYSIS COMPLETE")
        self.logger.info("=" * 70)

        return global_mood

    async def _process_entry(self, entry_id: str, entry: Dict[str, Any]) -> EntryAnalysis:
        """
        Process a single entry through sentiment analysis pipeline.

        Args:
            entry_id: Unique entry identifier
            entry: Entry data dict

        Returns:
            EntryAnalysis with results
        """
        start_time = time.time()
        platform = entry["platform"]

        try:
            # Get models for this platform
            models = self.config.MODEL_MAPPING.get(platform, ["llama3.1:latest"])

            # Analyze with all assigned models
            sentiment_results = await asyncio.gather(
                *[self._analyze_with_model(entry["text"], model) for model in models],
                return_exceptions=False,
            )

            # Filter out None results
            valid_results = [r for r in sentiment_results if r is not None]

            if not valid_results:
                processing_time = time.time() - start_time
                return EntryAnalysis(
                    entry_id=entry_id,
                    platform=platform,
                    text=entry["text"],
                    timestamp=entry["timestamp"],
                    status=SentimentStatus.FAILED,
                    individual_results=[],
                    aggregated_sentiment=0.0,
                    aggregated_confidence=0.0,
                    processing_time=processing_time,
                    error_message="All models failed to produce valid sentiment",
                )

            # Aggregate results
            avg_sentiment = sum(r.sentiment_score for r in valid_results) / len(valid_results)
            avg_confidence = sum(r.confidence for r in valid_results) / len(valid_results)

            processing_time = time.time() - start_time

            return EntryAnalysis(
                entry_id=entry_id,
                platform=platform,
                text=entry["text"],
                timestamp=entry["timestamp"],
                status=SentimentStatus.COMPLETED,
                individual_results=valid_results,
                aggregated_sentiment=avg_sentiment,
                aggregated_confidence=avg_confidence,
                processing_time=processing_time,
            )

        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"Error processing entry {entry_id}: {e}")
            return EntryAnalysis(
                entry_id=entry_id,
                platform=platform,
                text=entry["text"],
                timestamp=entry["timestamp"],
                status=SentimentStatus.FAILED,
                individual_results=[],
                aggregated_sentiment=0.0,
                aggregated_confidence=0.0,
                processing_time=processing_time,
                error_message=str(e),
            )

    async def _analyze_with_model(self, text: str, model: str) -> Optional[SentimentResult]:
        """Analyze sentiment with a specific model using semaphore for concurrency control."""
        async with self.semaphore:
            return await self.ollama_client.analyze_sentiment(text, model)

    def _calculate_global_mood(self) -> float:
        """
        Calculate global market mood using weighted aggregation.

        Formula: M_G = Σ(S_i * W_p) / Σ(W_p)
        where S_i is sentiment score and W_p is platform weight
        """
        weighted_sum = 0.0
        total_weight = 0.0

        for result in self.results:
            if result.status == SentimentStatus.COMPLETED:
                platform = result.platform
                sentiment = result.aggregated_sentiment
                weight = self.config.PLATFORM_WEIGHTS.get(platform, 0.1)

                weighted_sum += sentiment * weight
                total_weight += weight

        if total_weight == 0:
            self.logger.warning("No valid results to aggregate. Returning neutral mood.")
            return 0.0

        global_mood = weighted_sum / total_weight
        return round(global_mood, 4)

    def _generate_report(self, global_mood: float, elapsed_time: float) -> None:
        """Generate and save final analysis report."""
        # Create output directory
        self.config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        # Categorize results
        completed = [r for r in self.results if r.status == SentimentStatus.COMPLETED]
        failed = [r for r in self.results if r.status == SentimentStatus.FAILED]

        # Calculate statistics
        platform_stats = {}
        for result in completed:
            platform = result.platform
            if platform not in platform_stats:
                platform_stats[platform] = {"count": 0, "avg_sentiment": 0, "scores": []}
            platform_stats[platform]["count"] += 1
            platform_stats[platform]["scores"].append(result.aggregated_sentiment)

        for platform in platform_stats:
            scores = platform_stats[platform]["scores"]
            platform_stats[platform]["avg_sentiment"] = sum(scores) / len(scores)

        # Build report
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "analysis_duration_seconds": round(elapsed_time, 2),
                "total_entries_processed": len(completed),
                "total_entries_failed": len(failed),
                "unique_platforms": len(platform_stats),
            },
            "global_mood_score": global_mood,
            "interpretation": self._interpret_mood(global_mood),
            "platform_statistics": platform_stats,
            "weights_used": self.config.PLATFORM_WEIGHTS,
            "checkpoint_stats": self.progress_tracker.get_stats(),
            "detailed_results": [r.to_dict() for r in completed]
            if self.config.INCLUDE_DETAILED_RESULTS
            else [],
            "summary": {
                "top_bullish": [
                    r.to_dict()
                    for r in sorted(completed, key=lambda x: x.aggregated_sentiment, reverse=True)[
                        : self.config.REPORT_SUMMARY_LIMIT
                    ]
                ],
                "top_bearish": [
                    r.to_dict()
                    for r in sorted(completed, key=lambda x: x.aggregated_sentiment)[
                        : self.config.REPORT_SUMMARY_LIMIT
                    ]
                ],
            },
        }

        # Save report
        try:
            with open(self.config.FINAL_REPORT_FILE, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Report saved to: {self.config.FINAL_REPORT_FILE}")
        except Exception as e:
            self.logger.error(f"Failed to save report: {e}")

        # Console output
        self._print_summary(report, elapsed_time)

    @staticmethod
    def _interpret_mood(score: float) -> str:
        """Interpret mood score as human-readable text."""
        if score > 0.5:
            return "🚀 Extremely Bullish"
        elif score > 0.2:
            return "📈 Moderately Bullish"
        elif score > -0.2:
            return "➡️ Neutral"
        elif score > -0.5:
            return "📉 Moderately Bearish"
        else:
            return "🔴 Extremely Bearish"

    def _print_summary(self, report: Dict[str, Any], elapsed_time: float) -> None:
        """Print summary to console."""
        print("\n" + "=" * 70)
        print("CRYPTO MARKET MOOD ANALYSIS - FINAL REPORT")
        print("=" * 70)
        print(f"\nGlobal Market Mood Score: {report['global_mood_score']:.4f}")
        print(f"Interpretation: {report['interpretation']}")
        print(f"\nEntries Processed: {report['metadata']['total_entries_processed']}")
        print(f"Entries Failed: {report['metadata']['total_entries_failed']}")
        print(f"Analysis Time: {elapsed_time:.2f} seconds")

        print("\nPlatform Breakdown:")
        for platform, stats in report["platform_statistics"].items():
            print(
                f"  {platform:15} | Count: {stats['count']:3} | Avg Sentiment: {stats['avg_sentiment']:7.4f}"
            )

        print(f"\nReport saved to: {self.config.FINAL_REPORT_FILE}")
        print("=" * 70 + "\n")


# ============================================================================
# MAIN EXECUTION
# ============================================================================


async def main():
    """Main entry point."""
    try:
        analyzer = MoodAnalyzer(config)
        global_mood = await analyzer.run(force_reprocess=False)
        return global_mood
    except KeyboardInterrupt:
        logger.warning("Analysis interrupted by user. Checkpoint saved.")
        return None
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        return None


if __name__ == "__main__":
    # Validate config first
    if not config.validate_config():
        logger.error("Configuration validation failed. Exiting.")
        exit(1)

    # Run async main
    result = asyncio.run(main())

    if result is not None:
        print(f"\n✓ Analysis completed successfully")
        print(f"  Global Mood Score: {result}")
    else:
        print(f"\n✗ Analysis failed or was interrupted")
