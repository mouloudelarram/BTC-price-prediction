import asyncio
import re
from datetime import datetime
from typing import List, Optional
from playwright.async_api import BrowserContext
from loguru import logger
from data_sourcing.models import Post
from data_sourcing.scrapers.base_scraper import BaseScraper
from data_sourcing.core import BrowserManager, RateLimiter, ProxyManager


class PolymarketScraper(BaseScraper):
    """Scrapes prediction market data from Polymarket"""

    BASE_URL = "https://polymarket.com"

    def __init__(
        self,
        rate_limiter: Optional[RateLimiter] = None,
        proxy_manager: Optional[ProxyManager] = None,
        browser_manager: Optional[BrowserManager] = None,
    ):
        super().__init__("polymarket", rate_limiter, proxy_manager)
        self.browser_manager = browser_manager

    async def scrape(
        self,
        search_terms: List[str] = None,
        max_markets: int = 10,
        headless: bool = True,
    ) -> List[Post]:
        """Scrape prediction markets"""
        if not search_terms:
            search_terms = ["BTC", "Bitcoin"]

        proxy = self.proxy_manager.get_next_proxy() if self.proxy_manager else None
        browser_manager = self.browser_manager or BrowserManager(headless=headless, proxy=proxy)

        try:
            await browser_manager.launch()
            context = await browser_manager.create_context()

            for term in search_terms:
                logger.info(f"Searching Polymarket for: {term}")
                await self._search_markets(context, term, max_markets)

        except Exception as e:
            logger.error(f"Polymarket scraper error: {e}")
            if self.proxy_manager and proxy:
                self.proxy_manager.mark_failed(proxy)

        finally:
            await browser_manager.close()

        return self.posts

    async def _search_markets(self, context: BrowserContext, term: str, max_markets: int) -> None:
        """Search for markets containing the term"""
        page = await context.new_page()

        try:
            search_url = f"{self.BASE_URL}/search?q={term}"
            await page.goto(search_url, wait_until="networkidle", timeout=45000)
            await self.random_delay(3, 5)

            # Look for market cards
            market_selectors = await page.query_selector_all('[data-testid="market-card"], .market-card')

            for selector in market_selectors[:max_markets]:
                try:
                    title_elem = await selector.query_selector('h3, .market-title')
                    title = await title_elem.inner_text() if title_elem else "Unknown Market"

                    prob_elem = await selector.query_selector('[data-testid="market-probability"], .probability')
                    probability = await prob_elem.inner_text() if prob_elem else "N/A"

                    volume_elem = await selector.query_selector('[data-testid="market-volume"], .volume')
                    volume = await volume_elem.inner_text() if volume_elem else "N/A"

                    link_elem = await selector.query_selector('a')
                    url = await link_elem.get_attribute('href') if link_elem else ""
                    if url and not url.startswith('http'):
                        url = f"{self.BASE_URL}{url}"

                    content = f"Market: {title}\nProbability: {probability}\nVolume: {volume}"

                    post = Post(
                        platform="polymarket",
                        content=content,
                        author="polymarket",
                        timestamp=datetime.now(),
                        engagement={},
                        url=url,
                        metadata={"search_term": term, "probability": probability, "volume": volume},
                    )
                    self.posts.append(post)

                except Exception as e:
                    logger.debug(f"Error extracting market: {e}")

        except Exception as e:
            logger.error(f"Error searching markets for {term}: {e}")

        finally:
            await page.close()