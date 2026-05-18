"""
API routes for scrapper operations.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas import ScrapperRequest, ScrapperResult, ScrapperJobStatus
from app.services.scrapper_service import ScrapperService
from app.core.logger import logger
from app.core.exceptions import ScrapperException

router = APIRouter(prefix="/api/v1/scrapper", tags=["scrapper"])
scrapper_service = ScrapperService()


@router.post(
    "/run",
    response_model=ScrapperResult,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start a scraping job",
    description="Initiates a background scraping task",
)
async def start_scraping(request: ScrapperRequest) -> ScrapperResult:
    """Start a new scraping job."""
    try:
        job_id = await scrapper_service.start_scraping(
            scrapper_type=request.scrapper_type.value,
            platforms=request.platforms,
            limit=request.limit,
        )
        
        job = await scrapper_service.get_job_status(job_id)
        
        return ScrapperResult(
            id=job["id"],
            status=job["status"],
            platforms=job["platforms"],
            started_at=job["started_at"],
        )
    except ScrapperException as e:
        logger.error(f"Scrapper error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get(
    "/job/{job_id}",
    response_model=ScrapperJobStatus,
    summary="Get scrapping job status",
    description="Retrieve the current status of a scraping job",
)
async def get_scrapper_status(job_id: str) -> ScrapperJobStatus:
    """Get status of a scraping job."""
    try:
        job = await scrapper_service.get_job_status(job_id)
        
        return ScrapperJobStatus(
            job_id=job["id"],
            status=job["status"],
            entries_collected=job["entries_collected"],
            error=job.get("error"),
            created_at=job["started_at"],
            updated_at=job.get("completed_at") or job["started_at"],
        )
    except ScrapperException as e:
        logger.error(f"Job not found: {job_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post(
    "/job/{job_id}/cancel",
    summary="Cancel a scrapping job",
    description="Cancel a running scraping job",
)
async def cancel_scrapper_job(job_id: str):
    """Cancel a scraping job."""
    try:
        await scrapper_service.cancel_job(job_id)
        return {"message": f"Job {job_id} cancelled successfully"}
    except ScrapperException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get(
    "/latest",
    summary="Get latest scraped data",
    description="Retrieve the most recently scraped data",
)
async def get_latest_scrapped_data():
    """Get the latest scraped data."""
    try:
        data = await scrapper_service.get_latest_data()
        
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No scraped data found"
            )
        
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving latest data: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get(
    "/platforms",
    summary="List available platforms",
    description="Get list of available scraping platforms",
)
async def get_available_platforms():
    """Get available scraping platforms."""
    try:
        platforms = await scrapper_service.get_available_platforms()
        return {"platforms": platforms}
    except Exception as e:
        logger.error(f"Error retrieving platforms: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
