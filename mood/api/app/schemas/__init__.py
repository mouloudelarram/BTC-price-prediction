"""
Request and Response schemas for the Mood Analysis API.
Using Pydantic for validation and serialization.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================


class SentimentStatusEnum(str, Enum):
    """Status of sentiment analysis."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ScrapperTypeEnum(str, Enum):
    """Type of scrapper to run."""
    TWITTER = "twitter"
    REDDIT = "reddit"
    FEAR_GREED = "fear_greed"
    COINDESK = "coindesk"
    ALL = "all"


# ============================================================================
# SCRAPPER SCHEMAS
# ============================================================================


class ScrapperRequest(BaseModel):
    """Request to run scrapper."""
    scrapper_type: ScrapperTypeEnum = Field(..., description="Type of scrapper to run")
    platforms: Optional[List[str]] = Field(None, description="Specific platforms to scrape")
    limit: Optional[int] = Field(default=100, description="Limit number of entries")
    output_format: Optional[str] = Field(default="json", description="Output format")


class ScrapperResult(BaseModel):
    """Result from scrapper."""
    id: str = Field(..., description="Job ID")
    status: str = Field(..., description="Job status")
    entries_collected: int = Field(default=0, description="Number of entries collected")
    platforms: List[str] = Field(default=[], description="Platforms scraped")
    output_file: Optional[str] = Field(None, description="Output file path")
    error: Optional[str] = Field(None, description="Error message if any")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None)


class ScrapperJobStatus(BaseModel):
    """Status of a scrapper job."""
    job_id: str = Field(..., description="Job ID")
    status: str = Field(..., description="Job status")
    entries_collected: int = Field(default=0)
    error: Optional[str] = Field(None)
    progress_percentage: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# LLM SCHEMAS
# ============================================================================


class SentimentResultSchema(BaseModel):
    """Result from a single model's sentiment analysis."""
    sentiment_score: float = Field(..., ge=-1.0, le=1.0, description="Sentiment score (-1 to 1)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0 to 1)")
    reasoning: str = Field(..., description="Model reasoning")
    model_name: str = Field(..., description="Model name")
    processing_time: float = Field(..., description="Processing time in seconds")


class EntryAnalysisSchema(BaseModel):
    """Complete analysis result for a single data entry."""
    entry_id: str = Field(..., description="Entry ID")
    platform: str = Field(..., description="Data platform")
    text: str = Field(..., description="Text being analyzed")
    timestamp: str = Field(..., description="Timestamp")
    status: SentimentStatusEnum = Field(..., description="Analysis status")
    individual_results: List[SentimentResultSchema] = Field(default=[])
    aggregated_sentiment: float = Field(..., ge=-1.0, le=1.0, description="Aggregated sentiment")
    aggregated_confidence: float = Field(..., ge=0.0, le=1.0, description="Aggregated confidence")
    processing_time: float = Field(..., description="Total processing time")
    error_message: Optional[str] = Field(None, description="Error message if any")


class MoodAnalyzeRequest(BaseModel):
    """Request to analyze mood."""
    data_source: Optional[str] = Field(default="scrapper", description="Data source: scrapper or file")
    input_file: Optional[str] = Field(None, description="Input file path if using file source")
    models: Optional[List[str]] = Field(None, description="Specific models to use")
    batch_size: Optional[int] = Field(default=5, description="Batch size for processing")
    resume: Optional[bool] = Field(default=False, description="Resume from checkpoint")


class MoodAnalyzeResult(BaseModel):
    """Result of mood analysis."""
    job_id: str = Field(..., description="Job ID")
    status: str = Field(..., description="Job status")
    total_entries: int = Field(default=0, description="Total entries analyzed")
    successful_entries: int = Field(default=0, description="Successful entries")
    failed_entries: int = Field(default=0, description="Failed entries")
    aggregated_sentiment: Optional[float] = Field(None, description="Overall sentiment")
    aggregated_confidence: Optional[float] = Field(None, description="Overall confidence")
    output_file: Optional[str] = Field(None, description="Output file path")
    error: Optional[str] = Field(None, description="Error message if any")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None)
    processing_time: Optional[float] = Field(None, description="Total processing time")


class MoodJobStatus(BaseModel):
    """Status of a mood analysis job."""
    job_id: str = Field(..., description="Job ID")
    status: str = Field(..., description="Job status")
    entries_processed: int = Field(default=0)
    entries_failed: int = Field(default=0)
    entries_skipped: int = Field(default=0)
    progress_percentage: float = Field(default=0.0)
    error: Optional[str] = Field(None)
    current_aggregated_sentiment: Optional[float] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MoodReportSchema(BaseModel):
    """Final mood report."""
    report_id: str = Field(..., description="Report ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    total_entries: int = Field(...)
    successful_entries: int = Field(...)
    failed_entries: int = Field(...)
    platform_breakdown: Dict[str, Dict[str, Any]] = Field(default={})
    overall_sentiment: float = Field(..., ge=-1.0, le=1.0)
    overall_confidence: float = Field(..., ge=0.0, le=1.0)
    entries: List[EntryAnalysisSchema] = Field(default=[])


# ============================================================================
# HEALTH CHECK SCHEMAS
# ============================================================================


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Health status: healthy, degraded, unhealthy")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    api_version: str = Field(default="1.0.0")
    services: Dict[str, str] = Field(default={})
    message: Optional[str] = Field(None)


# ============================================================================
# ERROR SCHEMAS
# ============================================================================


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
