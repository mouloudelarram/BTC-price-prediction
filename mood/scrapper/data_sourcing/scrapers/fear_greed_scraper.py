import asyncio
import httpx
from datetime import datetime
from typing import List, Optional
from loguru import logger
from data_sourcing.models import Post
from data_sourcing.scrapers.base_scraper import BaseScraper
from data_sourcing.core import RateLimiter, ProxyManager


class FearGreedScraper(BaseScraper):
    """Fetches Fear & Greed Index from Alternative.me"""

    BASE_URL = "https://api.alternative.me/fng/"

    def __init__(
        self,
        rate_limiter: Optional[RateLimiter] = None,
        proxy_manager: Optional[ProxyManager] = None,
    ):
        super().__init__("fear_greed", rate_limiter, proxy_manager)

    async def scrape(
        self,
        limit: int = 7,
    ) -> List[Post]:
        """Fetch Fear & Greed Index data"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            await self._fetch_fear_greed_data(client, limit)

        return self.posts

    async def _fetch_fear_greed_data(self, client: httpx.AsyncClient, limit: int) -> None:
        """Fetch current and historical Fear & Greed data"""
        try:
            resp = await client.get(f"{self.BASE_URL}?limit={limit}")
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get('data', []):
                    value = int(item['value'])
                    classification = item['value_classification']
                    content = f"Fear & Greed Index: {value}/100 ({classification})"
                    timestamp = datetime.fromtimestamp(int(item['timestamp']))
                    post = Post(
                        platform="fear_greed",
                        content=content,
                        author="alternative_me",
                        timestamp=timestamp,
                        engagement={},
                        url="https://alternative.me/crypto/fear-and-greed-index/",
                        metadata={"type": "sentiment_index", "data": item},
                    )
                    self.posts.append(post)
        except Exception as e:
            logger.error(f"Error fetching Fear & Greed data: {e}")