"""
Integration tests for the Mood Analysis API.
"""

import pytest
import httpx
import asyncio
from datetime import datetime

BASE_URL = "http://localhost:8000"


@pytest.fixture
async def client():
    """Create HTTP client."""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        yield client


class TestHealthEndpoints:
    """Test health check endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        assert "services" in data
        assert "api" in data["services"]

    @pytest.mark.asyncio
    async def test_api_info(self, client):
        """Test API info endpoint."""
        response = await client.get("/info")
        assert response.status_code == 200
        
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data


class TestScrapperEndpoints:
    """Test scrapper API endpoints."""

    @pytest.mark.asyncio
    async def test_available_platforms(self, client):
        """Test get available platforms."""
        response = await client.get("/api/v1/scrapper/platforms")
        assert response.status_code == 200
        
        data = response.json()
        assert "platforms" in data
        assert isinstance(data["platforms"], list)
        assert len(data["platforms"]) > 0

    @pytest.mark.asyncio
    async def test_start_scraping(self, client):
        """Test start scraping."""
        payload = {
            "scrapper_type": "twitter",
            "limit": 10,
        }
        
        response = await client.post("/api/v1/scrapper/run", json=payload)
        assert response.status_code == 202
        
        data = response.json()
        assert "id" in data
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_get_scrapper_status(self, client):
        """Test get scrapper job status."""
        # Start a job first
        payload = {"scrapper_type": "twitter", "limit": 10}
        start_response = await client.post("/api/v1/scrapper/run", json=payload)
        job_id = start_response.json()["id"]
        
        # Get status
        response = await client.get(f"/api/v1/scrapper/job/{job_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["job_id"] == job_id
        assert "status" in data


class TestMoodAnalysisEndpoints:
    """Test mood analysis API endpoints."""

    @pytest.mark.asyncio
    async def test_available_models(self, client):
        """Test get available models."""
        response = await client.get("/api/v1/mood/models")
        assert response.status_code == 200
        
        data = response.json()
        assert "models" in data
        assert isinstance(data["models"], list)

    @pytest.mark.asyncio
    async def test_start_analysis(self, client):
        """Test start mood analysis."""
        payload = {
            "data_source": "scrapper",
            "batch_size": 5,
        }
        
        response = await client.post("/api/v1/mood/analyze", json=payload)
        assert response.status_code == 202
        
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_get_analysis_status(self, client):
        """Test get mood analysis job status."""
        # Start a job first
        payload = {"data_source": "scrapper", "batch_size": 5}
        start_response = await client.post("/api/v1/mood/analyze", json=payload)
        job_id = start_response.json()["job_id"]
        
        # Get status
        response = await client.get(f"/api/v1/mood/job/{job_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["job_id"] == job_id
        assert "status" in data
        assert "entries_processed" in data


class TestErrorHandling:
    """Test error handling."""

    @pytest.mark.asyncio
    async def test_invalid_job_id(self, client):
        """Test invalid job ID returns 404."""
        response = await client.get("/api/v1/scrapper/job/invalid-id")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_invalid_scrapper_type(self, client):
        """Test invalid scrapper type."""
        payload = {
            "scrapper_type": "invalid_type",
            "limit": 10,
        }
        
        response = await client.post("/api/v1/scrapper/run", json=payload)
        # Should fail validation
        assert response.status_code >= 400


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
