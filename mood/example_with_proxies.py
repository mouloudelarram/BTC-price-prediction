"""
Example 3: Using Proxies - Route requests through proxies
"""

import asyncio
from data_sourcing.scrapers import TwitterScraper, RedditScraper
from data_sourcing.core import ProxyManager, RateLimiter, BrowserManager
from data_sourcing.storage import JSONWriter

async def main():
    # Setup proxy rotation
    proxies = [
        "http://proxy1.example.com:8080",
        "http://proxy2.example.com:8080",
        # Add your own proxies here
    ]
    proxy_manager = ProxyManager(proxies)
    writer = JSONWriter("data_sourcing/output")
    
    if not proxies or proxies[0].startswith("http://proxy"):
        print("⚠️  No real proxies configured. Using direct connection.")
        proxy_manager = ProxyManager([])
    
    # === REDDIT WITH PROXIES ===
    print("\n🤖 Starting Reddit Scraper (with proxy rotation)...")
    reddit_scraper = RedditScraper(proxy_manager=proxy_manager)
    reddit_posts = await reddit_scraper.run(
        subreddits=["Bitcoin"],
        max_posts_per_subreddit=20,
    )
    
    if reddit_posts:
        writer.save(reddit_posts, "reddit")
        print(f"✓ Collected {len(reddit_posts)} posts")
    
    print("\n✓ Scraping complete with proxy rotation!")

if __name__ == "__main__":
    asyncio.run(main())
