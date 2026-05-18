"""
Service for managing scrapper operations through API.
Abstracts scrapper functionality for API consumption.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from app.core.logger import logger
from app.core.config import settings
from app.core.exceptions import ScrapperException, TimeoutError


class ScrapperService:
    """Service for scrapper operations."""

    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.base_url = settings.scrapper_base_url

    async def start_scraping(
        self,
        scrapper_type: str,
        platforms: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> str:
        """
        Start a scraping job.
        
        Args:
            scrapper_type: Type of scrapper to use
            platforms: Specific platforms to scrape
            limit: Limit on number of entries
            
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        
        self.jobs[job_id] = {
            "id": job_id,
            "status": "pending",
            "scrapper_type": scrapper_type,
            "platforms": platforms or [],
            "limit": limit,
            "entries_collected": 0,
            "output_file": None,
            "error": None,
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
        }
        
        # Start scraping in background
        asyncio.create_task(
            self._execute_scraping(job_id, scrapper_type, platforms, limit)
        )
        
        logger.info(f"Started scraping job {job_id}")
        return job_id

    async def _execute_scraping(
        self,
        job_id: str,
        scrapper_type: str,
        platforms: Optional[List[str]],
        limit: Optional[int],
    ):
        """Execute scraping job."""
        try:
            self.jobs[job_id]["status"] = "running"
            
            # Import scrapper module dynamically
            if scrapper_type == "twitter":
                from scrapper.data_sourcing.twitter_scraper import TwitterScraper
                scraper = TwitterScraper()
            elif scrapper_type == "reddit":
                from scrapper.data_sourcing.reddit_scraper import RedditScraper
                scraper = RedditScraper()
            elif scrapper_type == "all":
                from scrapper.data_sourcing.main import run_all_scrapers
                result = await run_all_scrapers(platforms=platforms, limit=limit)
                self.jobs[job_id]["status"] = "completed"
                self.jobs[job_id]["entries_collected"] = result.get("total_entries", 0)
                self.jobs[job_id]["output_file"] = result.get("output_file")
                self.jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()
                logger.info(f"Scraping job {job_id} completed")
                return
            else:
                raise ScrapperException(f"Unknown scrapper type: {scrapper_type}")
            
            # Execute scraper
            result = await scraper.run(limit=limit)
            
            self.jobs[job_id]["status"] = "completed"
            self.jobs[job_id]["entries_collected"] = len(result.get("entries", []))
            self.jobs[job_id]["output_file"] = result.get("output_file")
            self.jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Scraping job {job_id} completed successfully")
            
        except Exception as e:
            self.jobs[job_id]["status"] = "failed"
            self.jobs[job_id]["error"] = str(e)
            self.jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()
            logger.error(f"Scraping job {job_id} failed: {str(e)}")

    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a scraping job."""
        if job_id not in self.jobs:
            raise ScrapperException(f"Job {job_id} not found")
        return self.jobs[job_id]

    async def get_latest_data(self) -> Optional[Dict[str, Any]]:
        """
        Get the latest scraped data from the scrapper output directory.
        
        Returns:
            Parsed JSON data or None if not found
        """
        try:
            output_dir = settings.data_dir
            
            if not output_dir.exists():
                logger.warning(f"Data directory {output_dir} does not exist")
                return None
            
            # Find the latest JSON file
            json_files = list(output_dir.glob("*.json"))
            
            if not json_files:
                logger.warning(f"No JSON files found in {output_dir}")
                return None
            
            latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
            
            with open(latest_file, "r") as f:
                data = json.load(f)
            
            logger.info(f"Loaded latest data from {latest_file}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading latest data: {str(e)}")
            raise ScrapperException(f"Failed to load latest data: {str(e)}")

    async def get_available_platforms(self) -> List[str]:
        """Get list of available platforms."""
        return ["twitter", "reddit", "fear_greed", "coindesk", "binance", "coingecko"]

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a scraping job."""
        if job_id not in self.jobs:
            raise ScrapperException(f"Job {job_id} not found")
        
        if self.jobs[job_id]["status"] in ["completed", "failed"]:
            raise ScrapperException(f"Cannot cancel job with status {self.jobs[job_id]['status']}")
        
        self.jobs[job_id]["status"] = "cancelled"
        logger.info(f"Cancelled job {job_id}")
        return True
