"""Daily pipeline execution orchestrator."""

from pathlib import Path
from datetime import datetime
import json
from typing import Optional

from app.core.correlation import CorrelationEngine
from app.core.signal_engine import SignalEngine
from app.models import PipelineExecutionResult, SignalResponse
from app.utils.logger import get_logger
from app.utils.helpers import save_json, timestamp_now
from config import RESULTS_DIR

logger = get_logger(__name__)


class PipelineExecutor:
    """Orchestrate daily correlation and signal pipeline."""

    def __init__(self):
        self.correlation_engine = CorrelationEngine()
        self.signal_engine = SignalEngine()
        self.results_dir = RESULTS_DIR

    def execute_daily_pipeline(self) -> PipelineExecutionResult:
        """
        Execute full daily pipeline:
        1. Compute lagged correlations
        2. Generate trading signal
        3. Store results

        Returns:
            PipelineExecutionResult with status and outputs
        """
        logger.info("=== Starting Daily Pipeline Execution ===")
        exec_start = datetime.utcnow().isoformat()

        try:
            # Step 1: Correlation analysis
            logger.info("Step 1: Running correlation analysis...")
            summary_path, _ = self.correlation_engine.run_full_analysis()

            # Step 2: Signal generation
            logger.info("Step 2: Generating trading signal...")
            signal = self.signal_engine.generate_signal(summary_path)

            # Step 3: Store results
            logger.info("Step 3: Storing pipeline results...")
            self._store_results(signal, summary_path)

            result = PipelineExecutionResult(
                timestamp=exec_start,
                status="SUCCESS",
                correlation_summary_path=str(summary_path),
                signal=signal,
                error=None
            )

            logger.info(f"Pipeline execution completed successfully. Signal: {signal.signal}")
            return result

        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}", exc_info=True)
            return PipelineExecutionResult(
                timestamp=exec_start,
                status="FAILED",
                correlation_summary_path=None,
                signal=None,
                error=str(e)
            )

    def execute_daily_pipeline_dry_run(self) -> PipelineExecutionResult:
        """Execute pipeline without storing results (for testing)."""
        logger.info("=== Starting Dry-Run Pipeline Execution ===")
        
        try:
            summary_path, _ = self.correlation_engine.run_full_analysis()
            signal = self.signal_engine.generate_signal(summary_path)

            result = PipelineExecutionResult(
                timestamp=datetime.utcnow().isoformat(),
                status="SUCCESS",
                correlation_summary_path=str(summary_path),
                signal=signal,
                error=None
            )

            logger.info(f"Dry-run completed. Signal: {signal.signal}")
            return result

        except Exception as e:
            logger.error(f"Dry-run failed: {e}")
            return PipelineExecutionResult(
                timestamp=datetime.utcnow().isoformat(),
                status="FAILED",
                correlation_summary_path=None,
                signal=None,
                error=str(e)
            )

    def _store_results(
        self,
        signal: SignalResponse,
        correlation_summary_path: Path
    ) -> None:
        """Store pipeline results to files."""
        # Store signal as JSON
        signal_file = self.results_dir / "latest_signal.json"
        signal_data = json.loads(signal.model_dump_json())
        save_json(signal_data, signal_file)

        # Store execution log
        log_file = self.results_dir / "pipeline_log.json"
        log_entry = {
            "timestamp": timestamp_now(),
            "signal": signal.signal,
            "confidence": signal.confidence,
            "net_score": signal.net_score,
            "correlation_summary_path": str(correlation_summary_path),
        }

        # Append to log
        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logs = []

        logs.append(log_entry)
        save_json(logs, log_file)

        logger.info(f"Results stored: signal={signal_file}, log={log_file}")
