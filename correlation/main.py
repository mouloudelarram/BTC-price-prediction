"""FastAPI application for Correlation Engine microservice."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.routes import router as correlation_router
from app.utils.logger import get_logger
from config import API_HOST, API_PORT, API_DEBUG

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="BTC Correlation Engine",
    description="Correlation Engine microservice for BNMP (BTC Next Move Prediction)",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(correlation_router)


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "BTC Correlation Engine",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "summary": "GET /api/v1/correlation/summary",
            "signal": "GET /api/v1/correlation/signal",
            "pipeline_run": "POST /api/v1/correlation/pipeline/run",
            "pipeline_dry_run": "POST /api/v1/correlation/pipeline/dry-run",
            "health": "GET /api/v1/correlation/health",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get("/health")
async def health():
    """Application health endpoint."""
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    logger.info(f"Starting Correlation Engine API on {API_HOST}:{API_PORT}")
    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_DEBUG,
        log_level="info"
    )