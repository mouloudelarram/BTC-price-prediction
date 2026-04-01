"""
Example 2: Custom configuration - Scrape specific keywords and subreddits
"""

import asyncio
from data_sourcing.scrapers import TwitterScraper, RedditScraper
from data_sourcing.core import RateLimiter, BrowserManager
from data_sourcing.storage import JSONWriter

async def main():
    # Create output writer
    writer = JSONWriter("data_sourcing/output")
    
    # === TWITTER SCRAPER ===
    print("\n📱 Starting Twitter Scraper...")
    twitter_scraper = TwitterScraper()
    twitter_posts = await twitter_scraper.run(
        keywords=["#Bitcoin", "#BTC", "#crypto"],
        max_tweets=30,
        headless=True,
    )
    
    if twitter_posts:
        writer.save(twitter_posts, "twitter")
        print(f"✓ Collected {len(twitter_posts)} tweets")
    
    # === REDDIT SCRAPER ===
    print("\n🤖 Starting Reddit Scraper...")
    reddit_scraper = RedditScraper()
    reddit_posts = await reddit_scraper.run(
        subreddits=["Bitcoin", "CryptoCurrency"],
        max_posts_per_subreddit=25,
        include_comments=True,
    )
    
    if reddit_posts:
        writer.save(reddit_posts, "reddit")
        print(f"✓ Collected {len(reddit_posts)} Reddit posts")
    
    # === SUMMARY ===
    total = len(twitter_posts) + len(reddit_posts)
    print(f"\n{'='*50}")
    print(f"Total posts collected: {total}")
    print(f"Output saved to: data_sourcing/output/")
    print(f"{'='*50}")

if __name__ == "__main__":
    asyncio.run(main())
