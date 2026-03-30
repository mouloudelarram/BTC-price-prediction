import asyncio
import random
from abc import ABC, abstractmethod
from typing import List, Optional
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from data_sourcing.models import Post
from data_sourcing.core import RateLimiter, ProxyManager


class BaseScraper(ABC):
    """Abstract base class for all platform scrapers"""
    
    def __init__(
        self,
        platform: str,
        rate_limiter: Optional[RateLimiter] = None,
        proxy_manager: Optional[ProxyManager] = None,
    ):
        self.platform = platform
        self.rate_limiter = rate_limiter or RateLimiter(platform)
        self.proxy_manager = proxy_manager
        self.posts: List[Post] = []
    
    async def random_delay(self, min_sec: float = 1, max_sec: float = 5) -> None:
        """Random delay to simulate human behavior"""
        delay = random.uniform(min_sec, max_sec)
        await asyncio.sleep(delay)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def fetch_with_retry(self, func, *args, **kwargs):
        """Generic retry wrapper for failed requests"""
        await self.rate_limiter.wait()
        return await func(*args, **kwargs)
    
    @abstractmethod
    async def scrape(self, **kwargs) -> List[Post]:
        """Scrape posts from platform. Must be implemented by subclasses."""
        pass
    
    async def run(self, **kwargs) -> List[Post]:
        """Entry point for scraping"""
        try:
            logger.info(f"Starting {self.platform} scraper...")
            self.posts = await self.scrape(**kwargs)
            logger.info(f"{self.platform}: Collected {len(self.posts)} posts")
            return self.posts
        except Exception as e:
            logger.error(f"{self.platform} scraping failed: {e}")
            return []
