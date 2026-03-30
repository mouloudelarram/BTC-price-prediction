import asyncio
import feedparser
from datetime import datetime
from typing import List, Optional
from loguru import logger
from data_sourcing.models import Post
from data_sourcing.scrapers.base_scraper import BaseScraper
from data_sourcing.core import RateLimiter, ProxyManager


class CoinDeskScraper(BaseScraper):
    """Fetches news from CoinDesk RSS feed"""

    RSS_URL = "https://www.coindesk.com/arc/outboundfeeds/rss/"

    def __init__(
        self,
        rate_limiter: Optional[RateLimiter] = None,
        proxy_manager: Optional[ProxyManager] = None,
    ):
        super().__init__("coindesk", rate_limiter, proxy_manager)

    async def scrape(
        self,
        max_articles: int = 20,
    ) -> List[Post]:
        """Fetch latest news articles"""
        await self._fetch_rss_feed(max_articles)
        return self.posts

    async def _fetch_rss_feed(self, max_articles: int) -> None:
        """Parse RSS feed and create posts"""
        try:
            feed = feedparser.parse(self.RSS_URL)
            for entry in feed.entries[:max_articles]:
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                link = entry.get('link', '')
                published = entry.get('published_parsed')
                timestamp = datetime.now()
                if published:
                    timestamp = datetime(*published[:6])

                content = f"{title}\n{summary}"
                post = Post(
                    platform="coindesk",
                    content=content[:5000],
                    author="coindesk",
                    timestamp=timestamp,
                    engagement={},
                    url=link,
                    metadata={"type": "news", "title": title, "summary": summary},
                )
                self.posts.append(post)
        except Exception as e:
            logger.error(f"Error fetching CoinDesk RSS: {e}")