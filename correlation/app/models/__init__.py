"""Data models for Correlation Engine."""

from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class CorrelationResult(BaseModel):
    """Result from correlation analysis."""
    ticker: str
    correlation: float
    period: str
    shift_days: int


class Contributor(BaseModel):
    """Contributor to signal decision."""
    ticker: str
    impact: float
    period: str
    move: str


class SignalResponse(BaseModel):
    """Trading signal response."""
    timestamp: str
    signal: str  # BUY, SELL, HOLD
    confidence: str
    net_score: float
    analyzed_count: int
    top_contributors: List[Contributor]


class CorrelationSummary(BaseModel):
    """Summary of correlation analysis."""
    timestamp: str
    period: str
    shift_days: int
    top_assets: List[CorrelationResult]


class CorrelationSummaryReport(BaseModel):
    """Complete correlation summary report."""
    timestamp: str
    analyses: List[CorrelationSummary]
    total_assets_analyzed: int


class PipelineExecutionResult(BaseModel):
    """Result from daily pipeline execution."""
    timestamp: str
    status: str  # SUCCESS, FAILED, PARTIAL
    correlation_summary_path: Optional[str]
    signal: Optional[SignalResponse]
    error: Optional[str]


class BacktestResult(BaseModel):
    """Single decision backtesting result."""
    decision_date: str
    decision: str
    price_then: float
    price_next: float
    next_date: Optional[str]
    return_pct: float
    correct: bool
    error: Optional[str] = None


class BacktestSummary(BaseModel):
    """Aggregate backtesting statistics."""
    total: int
    valid: int
    errors: int
    correct: int
    accuracy_pct: float
    avg_return_pct: float
    cumulative_pnl: float
