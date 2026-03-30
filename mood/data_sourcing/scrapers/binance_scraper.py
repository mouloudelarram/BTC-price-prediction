import asyncio
import httpx
from datetime import datetime
from typing import List, Optional
from loguru import logger
from data_sourcing.models import Post
from data_sourcing.scrapers.base_scraper import BaseScraper
from data_sourcing.core import RateLimiter, ProxyManager


class BinanceScraper(BaseScraper):
    """Fetches market data from Binance Public API"""

    BASE_URL = "https://api.binance.com/api/v3"

    def __init__(
        self,
        rate_limiter: Optional[RateLimiter] = None,
        proxy_manager: Optional[ProxyManager] = None,
    ):
        super().__init__("binance", rate_limiter, proxy_manager)

    async def scrape(
        self,
        symbols: List[str] = None,
        max_data_points: int = 10,
    ) -> List[Post]:
        """Fetch market data for symbols"""
        if not symbols:
            symbols = ["BTCUSDT", "ETHUSDT"]

        async with httpx.AsyncClient(timeout=30.0) as client:
            for symbol in symbols:
                logger.info(f"Fetching Binance data for: {symbol}")
                await self._fetch_symbol_data(client, symbol, max_data_points)

        return self.posts

    async def _fetch_symbol_data(self, client: httpx.AsyncClient, symbol: str, max_points: int) -> None:
        """Fetch price, trades, etc. for a symbol"""
        try:
            # Get current price
            price_resp = await client.get(f"{self.BASE_URL}/ticker/price", params={"symbol": symbol})
            if price_resp.status_code == 200:
                price_data = price_resp.json()
                content = f"BTC Price: ${float(price_data['price']):.2f}"
                post = Post(
                    platform="binance",
                    content=content,
                    author="binance_api",
                    timestamp=datetime.now(),
                    engagement={},
                    url=f"https://www.binance.com/en/trade/{symbol}",
                    metadata={"symbol": symbol, "type": "price", "data": price_data},
                )
                self.posts.append(post)

            # Get recent trades
            trades_resp = await client.get(f"{self.BASE_URL}/trades", params={"symbol": symbol, "limit": 5})
            if trades_resp.status_code == 200:
                trades = trades_resp.json()
                for trade in trades[:max_points]:
                    content = f"Trade: {trade['qty']} @ ${float(trade['price']):.2f} ({'BUY' if trade['isBuyerMaker'] else 'SELL'})"
                    post = Post(
                        platform="binance",
                        content=content,
                        author="binance_api",
                        timestamp=datetime.fromtimestamp(trade['time'] / 1000),
                        engagement={},
                        url=f"https://www.binance.com/en/trade/{symbol}",
                        metadata={"symbol": symbol, "type": "trade", "data": trade},
                    )
                    self.posts.append(post)

        except Exception as e:
            logger.error(f"Error fetching Binance data for {symbol}: {e}")