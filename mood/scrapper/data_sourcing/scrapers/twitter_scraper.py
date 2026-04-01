import asyncio
import re
from datetime import datetime
from typing import List, Optional

import httpx
from playwright.async_api import BrowserContext
from loguru import logger
from data_sourcing.models import Post
from data_sourcing.scrapers.base_scraper import BaseScraper
from data_sourcing.core import BrowserManager, RateLimiter, ProxyManager


class TwitterScraper(BaseScraper):
    """Scrapes tweets from X/Twitter using Playwright"""
    
    SEARCH_URL = "https://twitter.com/search?q={query}&f=live"
    MOBILE_SEARCH_URL = "https://mobile.twitter.com/search?q={query}&f=live"
    NITTER_SEARCH_URL = "https://nitter.net/search?f=tweets&q={query}"

    TWITTER_API_BEARER = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAA..."  # public, may be rotated
    TWITTER_API_BASE = "https://api.twitter.com/2/search/adaptive.json"
    TWITTER_GUEST_TOKEN_URL = "https://api.twitter.com/1.1/guest/activate.json"
    
    def __init__(
        self,
        rate_limiter: Optional[RateLimiter] = None,
        proxy_manager: Optional[ProxyManager] = None,
        browser_manager: Optional[BrowserManager] = None,
    ):
        super().__init__("twitter", rate_limiter, proxy_manager)
        self.browser_manager = browser_manager
    
    async def scrape(
        self,
        keywords: List[str] = None,
        max_tweets: int = 50,
        headless: bool = True,
    ) -> List[Post]:
        """Scrape tweets for given keywords"""
        if not keywords:
            keywords = ["#BTC", "#Bitcoin", "#crypto"]
        
        proxy = self.proxy_manager.get_next_proxy() if self.proxy_manager else None
        browser_manager = self.browser_manager or BrowserManager(headless=headless, proxy=proxy)
        
        try:
            await browser_manager.launch()
            context = await browser_manager.create_context()
            
            for keyword in keywords:
                logger.info(f"Scraping tweets for: {keyword}")
                await self._scrape_keyword(context, keyword, max_tweets)
        
        except Exception as e:
            logger.error(f"Twitter scraper error: {e}")
            if self.proxy_manager and proxy:
                self.proxy_manager.mark_failed(proxy)
        
        finally:
            await browser_manager.close()
        
        return self.posts
    
    async def _scrape_keyword(self, context: BrowserContext, keyword: str, max_tweets: int) -> None:
        """Scrape tweets for a specific keyword"""
        url = self.SEARCH_URL.format(query=keyword.replace("#", "%23"))
        page = await context.new_page()
        
        try:
            # try regular/twitter mobile/nitter to avoid login wall restrictions
            endpoints = [self.SEARCH_URL, self.MOBILE_SEARCH_URL, self.NITTER_SEARCH_URL]
            success = False

            for endpoint in endpoints:
                url = endpoint.format(query=keyword.replace("#", "%23"))
                try:
                    await page.goto(url, wait_until="networkidle", timeout=45000)
                except Exception as e:
                    logger.warning(f"Twitter initial load timeout for keyword {keyword} @ {endpoint}; trying domcontentloaded ({e})")
                    await page.goto(url, wait_until="domcontentloaded", timeout=60000)

                await self.random_delay(3, 5)

                page_html = await page.content()
                if self._is_login_wall(page_html):
                    logger.warning(f"Twitter appears to require login at {endpoint} for keyword {keyword}; trying next endpoint")
                    continue

                articles = await page.query_selector_all('article')
                if not articles:
                    logger.warning(f"No tweets found at {endpoint} for keyword {keyword}; trying next endpoint")
                    continue

                success = True
                break

            if not success:
                logger.warning(f"No accessible tweets for keyword {keyword} after fallback endpoints; trying API fallback")
                api_posts = await self._scrape_keyword_via_api(keyword, max_tweets)
                for tweet in api_posts:
                    if len(self.posts) >= max_tweets:
                        break
                    if not any(p.url == tweet.url for p in self.posts):
                        self.posts.append(tweet)

                logger.info(f"Keyword {keyword} API fallback: collected {len(api_posts)} tweets")
                return

            await self.random_delay(2, 4)

            try:
                await page.wait_for_selector('article', timeout=15000)
            except Exception:
                logger.warning(f"No visible tweets for keyword {keyword}; likely login wall or no content")
                return

            collected = 0
            last_height = await page.evaluate("() => document.body.scrollHeight")
            scroll_attempts = 0
            
            while collected < max_tweets and scroll_attempts < 15:
                tweets = await self._extract_tweets_from_page(page, keyword)
                
                for tweet in tweets:
                    if collected >= max_tweets:
                        break
                    if not tweet.url:
                        continue
                    if not any(p.url == tweet.url for p in self.posts):
                        self.posts.append(tweet)
                        collected += 1
                
                if collected >= max_tweets:
                    break

                await page.evaluate("window.scrollBy(0, window.innerHeight)")
                await self.random_delay(2, 4)

                new_height = await page.evaluate("() => document.body.scrollHeight")
                if new_height <= last_height:
                    scroll_attempts += 1
                    if scroll_attempts >= 3:
                        logger.debug("Reached end of feed or no more scroll growth")
                        break
                else:
                    last_height = new_height
                    scroll_attempts = 0

            logger.info(f"Keyword {keyword}: collected {collected} tweets")

        except Exception as e:
            logger.error(f"Error scraping keyword {keyword}: {e}")
        
        finally:
            await page.close()

    def _is_login_wall(self, page_html: str) -> bool:
        lower_html = page_html.lower()
        checks = [
            'login to continue',
            'you must log in to view this content',
            'sign up',
            'log in',
            'redirecting to login',
            'get the twitter app',
        ]
        return any(check in lower_html for check in checks)

    async def _fetch_bearer_from_twitter_js(self, client: httpx.AsyncClient) -> Optional[str]:
        try:
            r = await client.get('https://twitter.com', headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code != 200:
                return None

            script_urls = re.findall(r'<script[^>]+src="([^"]*client-web[^"]*)"', r.text)
            for script in script_urls:
                if script.startswith('//'):
                    script = 'https:' + script
                elif script.startswith('/'):
                    script = 'https://twitter.com' + script

                js_res = await client.get(script, headers={'User-Agent': 'Mozilla/5.0'})
                if js_res.status_code != 200:
                    continue

                match = re.search(r'Bearer ([A-Za-z0-9%-]+)', js_res.text)
                if match:
                    bearer = match.group(1)
                    logger.info('Extracted twitter bearer token from JS')
                    return bearer

        except Exception as e:
            logger.debug(f"Failed to fetch bearer token from twitter.js: {e}")

        return None

    async def _scrape_keyword_via_api(self, keyword: str, max_tweets: int) -> List[Post]:
        cleaned = keyword.replace('#', '%23')
        posts = []

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    'Authorization': f'Bearer {self.TWITTER_API_BEARER}',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                }

                r = await client.post(self.TWITTER_GUEST_TOKEN_URL, headers=headers)
                if r.status_code == 401:
                    logger.warning("Guest token request returned 401; fetching fresh bearer token from twitter.com")
                    bearer = await self._fetch_bearer_from_twitter_js(client)
                    if not bearer:
                        return posts
                    self.TWITTER_API_BEARER = bearer
                    headers['Authorization'] = f'Bearer {bearer}'
                    r = await client.post(self.TWITTER_GUEST_TOKEN_URL, headers=headers)

                if r.status_code != 200:
                    logger.warning(f"Guest token request failed ({r.status_code})")
                    return posts

                guest_token = r.json().get('guest_token')
                if not guest_token:
                    logger.warning("No guest token received from Twitter API")
                    return posts

                headers['x-guest-token'] = guest_token
                params = {
                    'q': keyword,
                    'tweet_search_mode': 'live',
                    'count': max_tweets,
                }

                r = await client.get(self.TWITTER_API_BASE, headers=headers, params=params)
                if r.status_code != 200:
                    logger.warning(f"Twitter API search failed ({r.status_code})")
                    return posts

                data = r.json()
                tweets = data.get('globalObjects', {}).get('tweets', {})
                users = data.get('globalObjects', {}).get('users', {})

                for tweet_id, tweet in list(tweets.items())[:max_tweets]:
                    try:
                        text = tweet.get('full_text') or tweet.get('text', '')
                        author_id = tweet.get('user_id_str')
                        user = users.get(author_id, {})
                        author = user.get('screen_name', 'unknown')
                        created_at = tweet.get('created_at')
                        timestamp = datetime.now()
                        if created_at:
                            try:
                                timestamp = datetime.strptime(created_at, '%a %b %d %H:%M:%S %z %Y')
                            except Exception:
                                timestamp = datetime.now()

                        url = f"https://twitter.com/{author}/status/{tweet_id}"

                        engagement = {
                            'likes': int(tweet.get('favorite_count', 0)),
                            'retweets': int(tweet.get('retweet_count', 0)),
                            'replies': int(tweet.get('reply_count', 0)),
                        }

                        posts.append(Post(
                            platform='twitter',
                            content=text[:5000],
                            author=author,
                            timestamp=timestamp,
                            engagement=engagement,
                            url=url,
                            metadata={'keyword': keyword, 'source': 'api'},
                        ))

                    except Exception as e:
                        logger.debug(f"Error parsing Twitter API tweet {tweet_id}: {e}")

        except Exception as e:
            logger.error(f"Twitter API fallback error for {keyword}: {e}")

        return posts

    async def _extract_tweets_from_page(self, page, keyword: str) -> List[Post]:
        """Extract tweet data from current page"""
        tweets = []
        
        try:
            # Broad selector for desktop and mobile markup
            tweet_selectors = await page.query_selector_all('article, div.timeline-item')
            
            if not tweet_selectors:
                return tweets
            
            for tweet_element in tweet_selectors[-25:]:  # last 25 to avoid duplicates and get recent
                try:
                    text = ""
                    try:
                        text = await tweet_element.inner_text()
                    except Exception:
                        text = ""
                    text = text.strip()
                    if not text:
                        continue

                    author = "unknown"
                    author_elem = await tweet_element.query_selector('div[dir="auto"] > span')
                    if author_elem:
                        author = await author_elem.inner_text()

                    time_elem = await tweet_element.query_selector('time')
                    timestamp = datetime.now()
                    if time_elem:
                        timestamp_str = await time_elem.get_attribute('datetime')
                        if timestamp_str:
                            try:
                                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            except Exception:
                                timestamp = datetime.now()

                    url = ""
                    link_elem = await tweet_element.query_selector('a[href*="/status/"]')
                    if not link_elem:
                        link_elem = await tweet_element.query_selector('a[href*="/status/"][role="link"]')

                    if link_elem:
                        link = await link_elem.get_attribute('href')
                        if link:
                            if link.startswith('/'):
                                url = f"https://twitter.com{link}"
                            elif link.startswith('http'):
                                url = link
                            elif link.startswith('https'):
                                url = link

                    if not url and time_elem and author != 'unknown':
                        # fallback URL from author and timestamp if no status link
                        maybe_ts = await time_elem.get_attribute('datetime')
                        if maybe_ts:
                            url = f"https://twitter.com/{author}/status/{maybe_ts}"

                    engagement = await self._extract_engagement_metrics(tweet_element)

                    if url == "" and time_elem:
                        # fallback to building URL from author and time data
                        url = ""

                    if not url:
                        continue

                    post = Post(
                        platform="twitter",
                        content=text[:5000],
                        author=author.strip(),
                        timestamp=timestamp,
                        engagement=engagement,
                        url=url,
                        metadata={"keyword": keyword},
                    )

                    tweets.append(post)

                except Exception as e:
                    logger.debug(f"Error extracting individual tweet: {e}")
                    continue

        except Exception as e:
            logger.debug(f"Error extracting tweets from page: {e}")

        return tweets
    
    async def _extract_engagement_metrics(self, tweet_element) -> dict:
        """Extract likes, retweets, replies"""
        engagement = {"likes": 0, "retweets": 0, "replies": 0}
        
        try:
            # Look for engagement numbers in test IDs
            labels = await tweet_element.query_selector_all('[role="button"]')
            
            for label in labels:
                aria_label = await label.get_attribute('aria-label')
                if aria_label:
                    # Parse numbers from aria-labels like "123 Replies"
                    if 'replies' in aria_label.lower():
                        nums = re.findall(r'\d+', aria_label)
                        if nums:
                            engagement['replies'] = int(nums[0])
                    elif 'retweet' in aria_label.lower():
                        nums = re.findall(r'\d+', aria_label)
                        if nums:
                            engagement['retweets'] = int(nums[0])
                    elif 'like' in aria_label.lower():
                        nums = re.findall(r'\d+', aria_label)
                        if nums:
                            engagement['likes'] = int(nums[0])
        
        except Exception as e:
            logger.debug(f"Error extracting engagement: {e}")
        
        return engagement
