import asyncio
import httpx
from datetime import datetime, timezone
from typing import List, Optional
from loguru import logger
from data_sourcing.models import Post
from data_sourcing.scrapers.base_scraper import BaseScraper
from data_sourcing.core import RateLimiter, ProxyManager


class RedditScraper(BaseScraper):
    """Scrapes Reddit posts and comments using JSON endpoints"""
    
    REDDIT_JSON_URL = "https://www.reddit.com/r/{subreddit}.json"
    
    def __init__(
        self,
        rate_limiter: Optional[RateLimiter] = None,
        proxy_manager: Optional[ProxyManager] = None,
    ):
        super().__init__("reddit", rate_limiter, proxy_manager)
        self.client: Optional[httpx.AsyncClient] = None
    
    async def scrape(
        self,
        subreddits: List[str] = None,
        max_posts_per_subreddit: int = 50,
        include_comments: bool = True,
    ) -> List[Post]:
        """Scrape posts from specified subreddits"""
        if not subreddits:
            subreddits = ["Bitcoin", "CryptoCurrency", "Ethereum"]
        
        proxy = self.proxy_manager.get_next_proxy() if self.proxy_manager else None
        
        try:
            async with httpx.AsyncClient(
                headers=self._get_headers(),
                proxy=proxy,
                timeout=30,
            ) as client:
                self.client = client
                
                for subreddit in subreddits:
                    logger.info(f"Scraping r/{subreddit}...")
                    await self._scrape_subreddit(subreddit, max_posts_per_subreddit, include_comments)
        
        except Exception as e:
            logger.error(f"Reddit scraper error: {e}")
            if self.proxy_manager and proxy:
                self.proxy_manager.mark_failed(proxy)
        
        finally:
            self.client = None
        
        return self.posts
    
    async def _scrape_subreddit(
        self,
        subreddit: str,
        max_posts: int,
        include_comments: bool,
    ) -> None:
        """Scrape posts from a specific subreddit"""
        if not self.client:
            return
        
        url = self.REDDIT_JSON_URL.format(subreddit=subreddit)
        
        # Retry up to 3 times for Reddit
        for attempt in range(3):
            try:
                await self.random_delay(1, 3)  # Human-like delay
                # Fetch posts
                response = await self.client.get(url, params={"limit": max_posts})
                response.raise_for_status()
                data = response.json()
                break  # Success, exit retry loop
            
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 403 and attempt < 2:
                    logger.warning(f"Reddit 403 for r/{subreddit} (attempt {attempt + 1}/3), retrying...")
                    await self.random_delay(3, 6)
                    continue
                else:
                    logger.error(f"Error scraping r/{subreddit}: {e}")
                    return
            
            except Exception as e:
                if attempt < 2:
                    logger.debug(f"Retry {attempt + 1}/3 for r/{subreddit}")
                    await self.random_delay(2, 4)
                    continue
                else:
                    logger.error(f"Error scraping r/{subreddit}: {e}")
                    return
        
        try:
            data = response.json()
            
            posts = data.get("data", {}).get("children", [])
            
            for post_data in posts:
                try:
                    post_info = post_data.get("data", {})
                    
                    # Skip if not a text post or link post
                    if post_info.get("removed_by_category"):
                        continue
                    
                    title = post_info.get("title", "")
                    selftext = post_info.get("selftext", "")
                    content = f"{title}\n{selftext}".strip()
                    
                    if not content:
                        continue
                    
                    # Create post
                    post = Post(
                        platform="reddit",
                        content=content[:5000],  # Limit content length
                        author=post_info.get("author", "[deleted]"),
                        timestamp=datetime.fromtimestamp(
                            post_info.get("created_utc", 0),
                            tz=timezone.utc
                        ),
                        engagement={
                            "upvotes": post_info.get("score", 0),
                            "comments": post_info.get("num_comments", 0),
                            "awards": post_info.get("total_awards_received", 0),
                        },
                        url=f"https://reddit.com{post_info.get('permalink', '')}",
                        metadata={
                            "subreddit": subreddit,
                            "post_id": post_info.get("id"),
                            "upvote_ratio": post_info.get("upvote_ratio", 0),
                        }
                    )
                    
                    # Avoid duplicates
                    if not any(p.url == post.url for p in self.posts):
                        self.posts.append(post)
                    
                    # Optionally scrape top comments
                    if include_comments and post_info.get("num_comments", 0) > 0:
                        await self._scrape_comments(
                            subreddit,
                            post_info.get("id", ""),
                        )
                
                except Exception as e:
                    logger.debug(f"Error processing post: {e}")
                    continue
            
            await self.random_delay(2, 5)
        
        except Exception as e:
            logger.error(f"Error scraping r/{subreddit}: {e}")
    
    async def _scrape_comments(self, subreddit: str, post_id: str, max_comments: int = 10) -> None:
        """Scrape top comments from a specific post"""
        if not self.client:
            return
        
        url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json"
        
        try:
            response = await self.client.get(url, params={"limit": max_comments, "sort": "top"})
            response.raise_for_status()
            data = response.json()
            
            # data[1] contains comments
            if isinstance(data, list) and len(data) > 1:
                comments_data = data[1].get("data", {}).get("children", [])
                
                for comment_data in comments_data[:max_comments]:
                    try:
                        comment_info = comment_data.get("data", {})
                        
                        if comment_info.get("removed_by_category") or comment_info.get("type") != "t1":
                            continue
                        
                        content = comment_info.get("body", "")
                        if not content or len(content.strip()) < 10:
                            continue
                        
                        comment = Post(
                            platform="reddit_comment",
                            content=content[:2000],
                            author=comment_info.get("author", "[deleted]"),
                            timestamp=datetime.fromtimestamp(
                                comment_info.get("created_utc", 0),
                                tz=timezone.utc
                            ),
                            engagement={
                                "upvotes": comment_info.get("score", 0),
                            },
                            url=f"https://reddit.com{comment_info.get('permalink', '')}",
                            metadata={
                                "subreddit": subreddit,
                                "comment_id": comment_info.get("id"),
                            }
                        )
                        
                        if not any(p.url == comment.url for p in self.posts):
                            self.posts.append(comment)
                    
                    except Exception as e:
                        logger.debug(f"Error processing comment: {e}")
                        continue
        
        except Exception as e:
            logger.debug(f"Error scraping comments for {post_id}: {e}")
    
    def _get_headers(self) -> dict:
        """Get Reddit-friendly headers - required to bypass 403 blocking"""
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Referer": "https://www.reddit.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
