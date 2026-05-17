"""CLI script for daily pipeline execution."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import json
from datetime import datetime

from app.pipeline.executor import PipelineExecutor
from app.utils.logger import get_logger

logger = get_logger(__name__)


def run_daily_pipeline(dry_run: bool = False, output: Path = None):
    """Execute daily pipeline."""
    executor = PipelineExecutor()

    logger.info("Starting daily pipeline execution...")

    if dry_run:
        result = executor.execute_daily_pipeline_dry_run()
        logger.info(f"[DRY-RUN] Result: {result.status}")
    else:
        result = executor.execute_daily_pipeline()
        logger.info(f"Pipeline result: {result.status}")

    if output:
        with open(output, 'w') as f:
            json.dump(result.model_dump(), f, indent=2, default=str)
        logger.info(f"Results saved to {output}")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Execute Correlation Engine daily pipeline"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Execute without storing results"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Save execution result to JSON file"
    )

    args = parser.parse_args()

    result = run_daily_pipeline(dry_run=args.dry_run, output=args.output)

    print(f"\nPipeline Status: {result.status}")
    if result.signal:
        print(f"Signal: {result.signal.signal}")
        print(f"Confidence: {result.signal.confidence}")
    if result.error:
        print(f"Error: {result.error}")

    return 0 if result.status == "SUCCESS" else 1


if __name__ == "__main__":
    exit(main())
