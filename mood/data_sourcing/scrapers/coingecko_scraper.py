import asyncio
import httpx
from datetime import datetime
from typing import List, Optional
from loguru import logger
from data_sourcing.models import Post
from data_sourcing.scrapers.base_scraper import BaseScraper
from data_sourcing.core import RateLimiter, ProxyManager


class CoinGeckoScraper(BaseScraper):
    """Fetches market data from CoinGecko API"""

    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(
        self,
        rate_limiter: Optional[RateLimiter] = None,
        proxy_manager: Optional[ProxyManager] = None,
    ):
        super().__init__("coingecko", rate_limiter, proxy_manager)

    async def scrape(
        self,
        coins: List[str] = None,
        max_data_points: int = 10,
    ) -> List[Post]:
        """Fetch market data for coins"""
        if not coins:
            coins = ["bitcoin", "ethereum"]

        async with httpx.AsyncClient(timeout=30.0) as client:
            for coin in coins:
                logger.info(f"Fetching CoinGecko data for: {coin}")
                await self._fetch_coin_data(client, coin)

            # Fetch trending coins
            await self._fetch_trending(client)

        return self.posts

    async def _fetch_coin_data(self, client: httpx.AsyncClient, coin: str) -> None:
        """Fetch price and market data for a coin"""
        try:
            resp = await client.get(f"{self.BASE_URL}/coins/{coin}")
            if resp.status_code == 200:
                data = resp.json()
                market_data = data.get('market_data', {})
                content = f"{coin.upper()}: ${market_data.get('current_price', {}).get('usd', 'N/A'):.2f}, " \
                         f"Market Cap: ${market_data.get('market_cap', {}).get('usd', 0):,.0f}, " \
                         f"24h Change: {market_data.get('price_change_percentage_24h', 0):.2f}%"
                post = Post(
                    platform="coingecko",
                    content=content,
                    author="coingecko_api",
                    timestamp=datetime.now(),
                    engagement={},
                    url=f"https://www.coingecko.com/en/coins/{coin}",
                    metadata={"coin": coin, "type": "market_data", "data": market_data},
                )
                self.posts.append(post)
        except Exception as e:
            logger.error(f"Error fetching CoinGecko data for {coin}: {e}")

    async def _fetch_trending(self, client: httpx.AsyncClient) -> None:
        """Fetch trending coins"""
        try:
            resp = await client.get(f"{self.BASE_URL}/search/trending")
            if resp.status_code == 200:
                data = resp.json()
                for coin in data.get('coins', [])[:5]:
                    item = coin.get('item', {})
                    content = f"Trending: {item.get('name')} ({item.get('symbol')}) - " \
                             f"Market Cap Rank: {item.get('market_cap_rank')}"
                    post = Post(
                        platform="coingecko",
                        content=content,
                        author="coingecko_api",
                        timestamp=datetime.now(),
                        engagement={},
                        url=item.get('id', ''),
                        metadata={"type": "trending", "data": item},
                    )
                    self.posts.append(post)
        except Exception as e:
            logger.error(f"Error fetching trending coins: {e}")