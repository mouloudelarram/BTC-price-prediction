"""
Health check and utility routes.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas import HealthCheckResponse
from app.core.config import settings
from app.core.logger import logger
import requests
from datetime import datetime

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health check",
    description="Check API and dependent services health status",
)
async def health_check() -> HealthCheckResponse:
    """Check health of API and dependent services."""
    try:
        services = {}
        status_code = "healthy"
        
        # Check Ollama service
        try:
            resp = requests.get(f"{settings.ollama_host}/api/tags", timeout=5)
            services["ollama"] = "healthy" if resp.status_code == 200 else "unhealthy"
            if resp.status_code != 200:
                status_code = "degraded"
        except Exception as e:
            logger.warning(f"Ollama health check failed: {str(e)}")
            services["ollama"] = "unhealthy"
            status_code = "degraded"
        
        # Check data directory
        try:
            if settings.data_dir.exists():
                services["data_storage"] = "healthy"
            else:
                services["data_storage"] = "unhealthy"
                status_code = "degraded"
        except Exception as e:
            logger.warning(f"Data storage check failed: {str(e)}")
            services["data_storage"] = "unhealthy"
            status_code = "degraded"
        
        # API itself is always up if we got here
        services["api"] = "healthy"
        
        return HealthCheckResponse(
            status=status_code,
            services=services,
            message="All systems operational" if status_code == "healthy" else "Some services degraded",
        )
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check failed"
        )


@router.get(
    "/info",
    summary="API information",
    description="Get API version and configuration information",
)
async def api_info():
    """Get API information."""
    return {
        "name": "Crypto Market Mood Analysis API",
        "version": "1.0.0",
        "environment": settings.api_environment,
        "debug": settings.debug,
        "endpoints": {
            "scrapper": "/api/v1/scrapper",
            "mood": "/api/v1/mood",
        },
    }


@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Crypto Market Mood Analysis API",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }
