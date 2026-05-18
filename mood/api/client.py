"""
Python client library for the Mood Analysis API.
Simplifies interaction with the API.
"""

import httpx
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime


class MoodAnalysisClient:
    """Client for Mood Analysis API."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: int = 300,
        api_key: Optional[str] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.api_key = api_key
        self.client = None

    async def __aenter__(self):
        """Enter context manager."""
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=headers,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        if self.client:
            await self.client.aclose()

    # ========== HEALTH & INFO ==========

    async def health_check(self) -> Dict[str, Any]:
        """Get API health status."""
        response = await self.client.get("/health")
        response.raise_for_status()
        return response.json()

    async def get_info(self) -> Dict[str, Any]:
        """Get API information."""
        response = await self.client.get("/info")
        response.raise_for_status()
        return response.json()

    # ========== SCRAPPER ==========

    async def get_available_platforms(self) -> List[str]:
        """Get available scraping platforms."""
        response = await self.client.get("/api/v1/scrapper/platforms")
        response.raise_for_status()
        return response.json()["platforms"]

    async def start_scraping(
        self,
        scrapper_type: str,
        platforms: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> str:
        """
        Start a scraping job.
        
        Returns:
            Job ID
        """
        payload = {
            "scrapper_type": scrapper_type,
            "platforms": platforms,
            "limit": limit,
        }
        
        response = await self.client.post("/api/v1/scrapper/run", json=payload)
        response.raise_for_status()
        return response.json()["id"]

    async def get_scraper_status(self, job_id: str) -> Dict[str, Any]:
        """Get scraper job status."""
        response = await self.client.get(f"/api/v1/scrapper/job/{job_id}")
        response.raise_for_status()
        return response.json()

    async def get_latest_scraped_data(self) -> Dict[str, Any]:
        """Get latest scraped data."""
        response = await self.client.get("/api/v1/scrapper/latest")
        response.raise_for_status()
        return response.json()

    async def cancel_scraper_job(self, job_id: str) -> bool:
        """Cancel scraper job."""
        response = await self.client.post(f"/api/v1/scrapper/job/{job_id}/cancel")
        response.raise_for_status()
        return True

    # ========== MOOD ANALYSIS ==========

    async def get_available_models(self) -> List[str]:
        """Get available LLM models."""
        response = await self.client.get("/api/v1/mood/models")
        response.raise_for_status()
        return response.json()["models"]

    async def start_mood_analysis(
        self,
        data_source: str = "scrapper",
        input_file: Optional[str] = None,
        models: Optional[List[str]] = None,
        batch_size: int = 5,
        resume: bool = False,
    ) -> str:
        """
        Start mood analysis job.
        
        Returns:
            Job ID
        """
        payload = {
            "data_source": data_source,
            "input_file": input_file,
            "models": models,
            "batch_size": batch_size,
            "resume": resume,
        }
        
        response = await self.client.post("/api/v1/mood/analyze", json=payload)
        response.raise_for_status()
        return response.json()["job_id"]

    async def get_analysis_status(self, job_id: str) -> Dict[str, Any]:
        """Get mood analysis job status."""
        response = await self.client.get(f"/api/v1/mood/job/{job_id}")
        response.raise_for_status()
        return response.json()

    async def get_latest_report(self) -> Dict[str, Any]:
        """Get latest mood analysis report."""
        response = await self.client.get("/api/v1/mood/latest-report")
        response.raise_for_status()
        return response.json()

    async def cancel_analysis_job(self, job_id: str) -> bool:
        """Cancel mood analysis job."""
        response = await self.client.post(f"/api/v1/mood/job/{job_id}/cancel")
        response.raise_for_status()
        return True

    async def analyze_from_scrapper(
        self,
        models: Optional[List[str]] = None,
        batch_size: int = 5,
    ) -> str:
        """
        Analyze latest scraped data directly.
        
        Returns:
            Job ID
        """
        params = {
            "models": models,
            "batch_size": batch_size,
        }
        
        response = await self.client.post(
            "/api/v1/mood/analyze-from-scrapper",
            json=params,
        )
        response.raise_for_status()
        return response.json()["job_id"]

    # ========== CONVENIENCE METHODS ==========

    async def wait_for_job(
        self,
        job_id: str,
        job_type: str = "scrapper",
        poll_interval: int = 5,
        timeout: int = 3600,
    ) -> Dict[str, Any]:
        """
        Wait for a job to complete.
        
        Args:
            job_id: Job ID to wait for
            job_type: Type of job (scrapper or mood)
            poll_interval: Polling interval in seconds
            timeout: Maximum wait time in seconds
            
        Returns:
            Final job status
        """
        elapsed = 0
        
        while elapsed < timeout:
            if job_type == "scrapper":
                status = await self.get_scraper_status(job_id)
            else:
                status = await self.get_analysis_status(job_id)
            
            if status["status"] in ["completed", "failed", "cancelled"]:
                return status
            
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        
        raise TimeoutError(f"Job {job_id} did not complete within {timeout} seconds")

    async def run_complete_pipeline(
        self,
        scrapper_type: str = "all",
        scrapper_limit: Optional[int] = None,
        analysis_models: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Run complete pipeline: scrape -> analyze.
        
        Returns:
            Final analysis report
        """
        # Start scraping
        print("Starting scraping...")
        scraper_job_id = await self.start_scraping(
            scrapper_type=scrapper_type,
            limit=scrapper_limit,
        )
        
        # Wait for scraping
        print(f"Waiting for scraping job {scraper_job_id}...")
        await self.wait_for_job(scraper_job_id, job_type="scrapper")
        print("Scraping completed!")
        
        # Start analysis
        print("Starting mood analysis...")
        analysis_job_id = await self.analyze_from_scrapper(
            models=analysis_models,
        )
        
        # Wait for analysis
        print(f"Waiting for analysis job {analysis_job_id}...")
        await self.wait_for_job(analysis_job_id, job_type="mood")
        print("Analysis completed!")
        
        # Get report
        report = await self.get_latest_report()
        return report


# Synchronous wrapper
class MoodAnalysisClientSync:
    """Synchronous wrapper for MoodAnalysisClient."""

    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 300):
        self.base_url = base_url
        self.timeout = timeout

    def _run_async(self, coro):
        """Run async coroutine."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    def health_check(self) -> Dict[str, Any]:
        """Get API health status."""
        async def _health():
            async with MoodAnalysisClient(self.base_url, self.timeout) as client:
                return await client.health_check()
        return self._run_async(_health())

    def start_scraping(self, scrapper_type: str, limit: Optional[int] = None) -> str:
        """Start scraping job."""
        async def _scrape():
            async with MoodAnalysisClient(self.base_url, self.timeout) as client:
                return await client.start_scraping(scrapper_type, limit=limit)
        return self._run_async(_scrape())

    def start_analysis(self, data_source: str = "scrapper") -> str:
        """Start mood analysis."""
        async def _analyze():
            async with MoodAnalysisClient(self.base_url, self.timeout) as client:
                return await client.start_mood_analysis(data_source=data_source)
        return self._run_async(_analyze())

    def get_latest_report(self) -> Dict[str, Any]:
        """Get latest report."""
        async def _report():
            async with MoodAnalysisClient(self.base_url, self.timeout) as client:
                return await client.get_latest_report()
        return self._run_async(_report())

    def run_pipeline(self, scrapper_type: str = "all") -> Dict[str, Any]:
        """Run complete pipeline."""
        async def _pipeline():
            async with MoodAnalysisClient(self.base_url, self.timeout) as client:
                return await client.run_complete_pipeline(scrapper_type=scrapper_type)
        return self._run_async(_pipeline())


if __name__ == "__main__":
    # Example usage
    async def main():
        async with MoodAnalysisClient("http://localhost:8000") as client:
            # Check health
            health = await client.health_check()
            print(f"API Health: {health['status']}")
            
            # Get available platforms
            platforms = await client.get_available_platforms()
            print(f"Available platforms: {platforms}")
            
            # Run pipeline
            report = await client.run_complete_pipeline(scrapper_type="all")
            print(f"Overall sentiment: {report.get('overall_sentiment')}")

    asyncio.run(main())
