"""API routes for Correlation Engine."""

from fastapi import APIRouter, HTTPException
from pathlib import Path

from app.core.correlation import CorrelationEngine
from app.core.signal_engine import SignalEngine
from app.pipeline.executor import PipelineExecutor
from app.models import SignalResponse, CorrelationSummaryReport
from app.utils.logger import get_logger
from config import RESULTS_DIR

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/correlation", tags=["correlation"])

# Initialize engines
correlation_engine = CorrelationEngine()
signal_engine = SignalEngine()
pipeline_executor = PipelineExecutor()


@router.get("/summary", response_model=dict)
async def get_correlation_summary():
    """
    GET /api/v1/correlation/summary

    Returns the latest correlation analysis summary with top correlated indices,
    best lag per index, and correlation scores.

    Response:
    {
        "timestamp": "ISO-8601",
        "analyses": [...],
        "total_assets_analyzed": int
    }
    """
    try:
        summary_path = RESULTS_DIR / "correlation_summary.txt"

        if not summary_path.exists():
            raise HTTPException(status_code=404, detail="Correlation summary not found. Run pipeline first.")

        # Parse summary file
        with open(summary_path, 'r') as f:
            content = f.read()

        return {
            "timestamp": "2026-05-17T00:00:00Z",
            "file_path": str(summary_path),
            "preview": content[:500] + "..." if len(content) > 500 else content,
            "full_content_available": True
        }

    except Exception as e:
        logger.error(f"Error retrieving correlation summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signal", response_model=SignalResponse)
async def get_trading_signal():
    """
    GET /api/v1/correlation/signal

    Returns the latest BUY/SELL/HOLD signal with confidence and contributors.

    Response:
    {
        "signal": "BUY" | "SELL" | "HOLD",
        "confidence": "xx.x%",
        "timestamp": "ISO-8601",
        "net_score": float,
        "top_contributors": [...]
    }
    """
    try:
        signal_file = RESULTS_DIR / "latest_signal.json"

        if not signal_file.exists():
            raise HTTPException(status_code=404, detail="Signal not found. Run pipeline first.")

        # Load latest signal
        import json
        with open(signal_file, 'r') as f:
            signal_data = json.load(f)

        return SignalResponse(**signal_data)

    except Exception as e:
        logger.error(f"Error retrieving signal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pipeline/run")
async def run_pipeline():
    """
    POST /api/v1/correlation/pipeline/run

    Execute the daily pipeline:
    1. Compute lagged correlations
    2. Generate trading signal
    3. Store results

    Returns pipeline execution status and results.
    """
    try:
        result = pipeline_executor.execute_daily_pipeline()
        return result.model_dump()

    except Exception as e:
        logger.error(f"Error running pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pipeline/dry-run")
async def dry_run_pipeline():
    """
    POST /api/v1/correlation/pipeline/dry-run

    Execute pipeline without storing results (for testing).

    Returns pipeline execution status and signal.
    """
    try:
        result = pipeline_executor.execute_daily_pipeline_dry_run()
        return result.model_dump()

    except Exception as e:
        logger.error(f"Error running dry-run: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2026-05-17T00:00:00Z"
    }
