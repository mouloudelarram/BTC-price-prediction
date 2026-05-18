"""
API routes for mood analysis operations.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas import MoodAnalyzeRequest, MoodAnalyzeResult, MoodJobStatus, MoodReportSchema
from app.services.mood_service import MoodAnalyzerService
from app.core.logger import logger
from app.core.exceptions import LLMException, ProcessingError

router = APIRouter(prefix="/api/v1/mood", tags=["mood-analysis"])
mood_service = MoodAnalyzerService()


@router.post(
    "/analyze",
    response_model=MoodAnalyzeResult,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start mood analysis",
    description="Initiates a background mood analysis task",
)
async def start_mood_analysis(request: MoodAnalyzeRequest) -> MoodAnalyzeResult:
    """Start a new mood analysis job."""
    try:
        job_id = await mood_service.start_analysis(
            data_source=request.data_source,
            input_file=request.input_file,
            models=request.models,
            batch_size=request.batch_size,
            resume=request.resume,
        )
        
        job = await mood_service.get_job_status(job_id)
        
        return MoodAnalyzeResult(
            job_id=job["id"],
            status=job["status"],
            total_entries=job["total_entries"],
            started_at=job["started_at"],
        )
    except (LLMException, ProcessingError) as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get(
    "/job/{job_id}",
    response_model=MoodJobStatus,
    summary="Get mood analysis job status",
    description="Retrieve the current status of a mood analysis job",
)
async def get_mood_status(job_id: str) -> MoodJobStatus:
    """Get status of a mood analysis job."""
    try:
        job = await mood_service.get_job_status(job_id)
        
        return MoodJobStatus(
            job_id=job["id"],
            status=job["status"],
            entries_processed=job["entries_processed"],
            entries_failed=job.get("failed_entries", 0),
            error=job.get("error"),
            current_aggregated_sentiment=job.get("aggregated_sentiment"),
            created_at=job["started_at"],
            updated_at=job.get("completed_at") or job["started_at"],
        )
    except LLMException as e:
        logger.error(f"Job not found: {job_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post(
    "/job/{job_id}/cancel",
    summary="Cancel mood analysis job",
    description="Cancel a running mood analysis job",
)
async def cancel_mood_job(job_id: str):
    """Cancel a mood analysis job."""
    try:
        await mood_service.cancel_job(job_id)
        return {"message": f"Job {job_id} cancelled successfully"}
    except LLMException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get(
    "/latest-report",
    summary="Get latest mood report",
    description="Retrieve the most recent mood analysis report",
)
async def get_latest_report():
    """Get the latest mood analysis report."""
    try:
        report = await mood_service.get_latest_report()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No mood analysis report found"
            )
        
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving latest report: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get(
    "/models",
    summary="List available models",
    description="Get list of available LLM models for analysis",
)
async def get_available_models():
    """Get available LLM models."""
    try:
        models = await mood_service.get_available_models()
        return {"models": models}
    except Exception as e:
        logger.error(f"Error retrieving models: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post(
    "/analyze-from-scrapper",
    response_model=MoodAnalyzeResult,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Analyze latest scrapped data",
    description="Run mood analysis on the latest scraped data",
)
async def analyze_latest_scrapper_data(
    models: list = None,
    batch_size: int = 5,
):
    """Analyze the latest scraped data directly."""
    try:
        request = MoodAnalyzeRequest(
            data_source="scrapper",
            models=models,
            batch_size=batch_size,
            resume=False,
        )
        
        job_id = await mood_service.start_analysis(
            data_source=request.data_source,
            input_file=request.input_file,
            models=request.models,
            batch_size=request.batch_size,
            resume=request.resume,
        )
        
        job = await mood_service.get_job_status(job_id)
        
        return MoodAnalyzeResult(
            job_id=job["id"],
            status=job["status"],
            total_entries=job["total_entries"],
            started_at=job["started_at"],
        )
    except (LLMException, ProcessingError) as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
