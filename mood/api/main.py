"""
Main FastAPI application for Crypto Market Mood Analysis API.
Production-ready REST API for scrapper and mood analyzer services.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time

from app.core.config import settings
from app.core.logger import logger
from app.core.exceptions import MoodAnalyzerException
from app.routes import scrapper, mood, health
from app.schemas import ErrorResponse


# Create FastAPI application
app = FastAPI(
    title="Crypto Market Mood Analysis API",
    description="Production-grade API for cryptocurrency sentiment analysis",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom exception handler
@app.exception_handler(MoodAnalyzerException)
async def mood_analyzer_exception_handler(request: Request, exc: MoodAnalyzerException):
    """Handle MoodAnalyzerException."""
    logger.error(f"Application error: {str(exc)}", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": exc.__class__.__name__,
            "message": str(exc),
            "status_code": status.HTTP_400_BAD_REQUEST,
        },
    )


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred" if not settings.debug else str(exc),
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        },
    )


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and responses."""
    start_time = time.time()
    
    # Log request
    logger.info(f"{request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        raise
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - Duration: {process_time:.3f}s"
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Include routers
app.include_router(health.router)
app.include_router(scrapper.router)
app.include_router(mood.router)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting Crypto Market Mood Analysis API")
    logger.info(f"Environment: {settings.api_environment}")
    logger.info(f"Debug: {settings.debug}")
    logger.info(f"Ollama Host: {settings.ollama_host}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Crypto Market Mood Analysis API")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
