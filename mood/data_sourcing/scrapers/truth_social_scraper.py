import asyncio
import re
from datetime import datetime
from typing import List, Optional
from playwright.async_api import BrowserContext
from loguru import logger
from data_sourcing.models import Post
from data_sourcing.scrapers.base_scraper import BaseScraper
from data_sourcing.core import BrowserManager, RateLimiter, ProxyManager


class TruthSocialScraper(BaseScraper):
    """Scrapes posts from Truth Social accounts using Playwright"""

    BASE_URL = "https://truthsocial.com/@{handle}"

    def __init__(
        self,
        rate_limiter: Optional[RateLimiter] = None,
        proxy_manager: Optional[ProxyManager] = None,
        browser_manager: Optional[BrowserManager] = None,
    ):
        super().__init__("truth_social", rate_limiter, proxy_manager)
        self.browser_manager = browser_manager

    async def scrape(
        self,
        accounts: List[dict] = None,
        max_posts_per_account: int = 20,
        headless: bool = True,
    ) -> List[Post]:
        """Scrape posts from specified Truth Social accounts"""
        if not accounts:
            accounts = [
                {
                    "handle": "realDonaldTrump",
                    "url": "https://truthsocial.com/@realDonaldTrump",
                    "priority": "very_high",
                    "type": "macro_signal",
                    "description": "Primary market-moving account; posts can directly influence crypto narratives, regulation expectations, and BTC sentiment"
                },
                {
                    "handle": "DonaldJTrumpJr",
                    "url": "https://truthsocial.com/@DonaldJTrumpJr",
                    "priority": "high",
                    "type": "narrative_signal",
                    "description": "Amplifies and sometimes pre-signals crypto-related initiatives and narratives"
                },
                {
                    "handle": "EricTrump",
                    "url": "https://truthsocial.com/@EricTrump",
                    "priority": "high",
                    "type": "narrative_signal",
                    "description": "Publicly crypto-friendly; may hint at upcoming moves or reinforce bullish sentiment"
                }
            ]

        proxy = self.proxy_manager.get_next_proxy() if self.proxy_manager else None
        browser_manager = self.browser_manager or BrowserManager(headless=headless, proxy=proxy)

        try:
            await browser_manager.launch()
            context = await browser_manager.create_context()

            for account in accounts:
                logger.info(f"Scraping Truth Social account: @{account['handle']}")
                await self._scrape_account(context, account, max_posts_per_account)

        except Exception as e:
            logger.error(f"Truth Social scraper error: {e}")
            if self.proxy_manager and proxy:
                self.proxy_manager.mark_failed(proxy)

        finally:
            await browser_manager.close()

        return self.posts

    async def _scrape_account(self, context: BrowserContext, account: dict, max_posts: int) -> None:
        """Scrape posts from a specific Truth Social account"""
        url = account['url']
        page = await context.new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=45000)
            await self.random_delay(3, 5)

            collected = 0
            last_height = await page.evaluate("() => document.body.scrollHeight")
            scroll_attempts = 0

            while collected < max_posts and scroll_attempts < 10:
                posts = await self._extract_posts_from_page(page, account)
                filtered_posts = self._filter_posts(posts, account)

                for post in filtered_posts:
                    if collected >= max_posts:
                        break
                    if not any(p.url == post.url for p in self.posts):
                        self.posts.append(post)
                        collected += 1

                if collected >= max_posts:
                    break

                await page.evaluate("window.scrollBy(0, window.innerHeight)")
                await self.random_delay(2, 4)

                new_height = await page.evaluate("() => document.body.scrollHeight")
                if new_height <= last_height:
                    scroll_attempts += 1
                    if scroll_attempts >= 3:
                        logger.debug("Reached end of feed")
                        break
                else:
                    last_height = new_height
                    scroll_attempts = 0

            logger.info(f"Account @{account['handle']}: collected {collected} posts")

        except Exception as e:
            logger.error(f"Error scraping account @{account['handle']}: {e}")

        finally:
            await page.close()

    def _filter_posts(self, posts: List[Post], account: dict) -> List[Post]:
        """Filter posts based on length (removed keyword filtering to get all posts)"""
        min_length = 20

        filtered = []
        for post in posts:
            if len(post.content) < min_length:
                continue
            filtered.append(post)

        return filtered

    async def _extract_posts_from_page(self, page, account: dict) -> List[Post]:
        """Extract post data from current page"""
        posts = []

        try:
            # Look for post containers (try multiple selectors)
            post_selectors = await page.query_selector_all('article, div.post, [data-testid*="post"], div[data-testid*="status"], div[class*="post"], div[class*="status"]')

            logger.debug(f"Found {len(post_selectors)} potential post elements")

            if not post_selectors:
                return posts

            for post_element in post_selectors[-10:]:  # last 10 to get recent
                try:
                    text = await post_element.inner_text()
                    text = text.strip()
                    if not text or len(text) < 10:  # Lower minimum length
                        continue

                    author = account['handle']

                    time_elem = await post_element.query_selector('time')
                    timestamp = datetime.now()
                    if time_elem:
                        datetime_attr = await time_elem.get_attribute('datetime')
                        if datetime_attr:
                            try:
                                timestamp = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                            except Exception:
                                timestamp = datetime.now()

                    # Try multiple URL patterns
                    url = ""
                    link_elem = await post_element.query_selector('a[href*="/posts/"], a[href*="/status/"], a[href*="truthsocial.com"]')
                    if link_elem:
                        link = await link_elem.get_attribute('href')
                        if link and link.startswith('/'):
                            url = f"https://truthsocial.com{link}"
                        elif link and link.startswith('http'):
                            url = link

                    # If no specific post URL, use account URL with timestamp
                    if not url:
                        url = f"{account['url']}?t={int(timestamp.timestamp())}"

                    engagement = await self._extract_engagement_metrics(post_element)

                    post = Post(
                        platform="truth_social",
                        content=text[:5000],
                        author=author,
                        timestamp=timestamp,
                        engagement=engagement,
                        url=url,
                        metadata={"account": account, "priority": account.get('priority', 'medium')},
                    )

                    posts.append(post)

                except Exception as e:
                    logger.debug(f"Error extracting individual post: {e}")
                    continue

        except Exception as e:
            logger.debug(f"Error extracting posts from page: {e}")

        return posts

    async def _extract_engagement_metrics(self, post_element) -> dict:
        """Extract likes, shares, etc. from post"""
        engagement = {"likes": 0, "shares": 0, "comments": 0}

        try:
            # Look for engagement buttons/text
            buttons = await post_element.query_selector_all('[role="button"]')
            for button in buttons:
                aria_label = await button.get_attribute('aria-label') or ""
                text = await button.inner_text() or ""

                if 'like' in aria_label.lower() or 'like' in text.lower():
                    nums = re.findall(r'\d+', text)
                    if nums:
                        engagement['likes'] = int(nums[0])
                elif 'share' in aria_label.lower() or 'share' in text.lower():
                    nums = re.findall(r'\d+', text)
                    if nums:
                        engagement['shares'] = int(nums[0])
                elif 'comment' in aria_label.lower() or 'reply' in text.lower():
                    nums = re.findall(r'\d+', text)
                    if nums:
                        engagement['comments'] = int(nums[0])

        except Exception as e:
            logger.debug(f"Error extracting engagement: {e}")

        return engagement