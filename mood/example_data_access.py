"""
Example 4: Accessing Scraped Data - How to use the Post model
"""

import asyncio
import json
from pathlib import Path
from data_sourcing.models import Post
from data_sourcing.scrapers import RedditScraper
from data_sourcing.storage import JSONWriter

async def main():
    # Scrape some posts
    print("📊 Scraping Reddit posts...")
    scraper = RedditScraper()
    posts = await scraper.run(
        subreddits=["Bitcoin"],
        max_posts_per_subreddit=10,
        include_comments=False,
    )
    
    if not posts:
        print("No posts collected. Try checking your internet connection.")
        return
    
    # === ANALYZE POSTS ===
    print(f"\n✓ Collected {len(posts)} posts\n")
    print("="*70)
    
    for i, post in enumerate(posts[:3], 1):  # Show first 3
        print(f"\n📌 Post #{i}")
        print(f"Platform:    {post.platform}")
        print(f"Author:      {post.author}")
        print(f"Timestamp:   {post.timestamp}")
        print(f"URL:         {post.url}")
        print(f"Engagement:  {post.engagement}")
        print(f"Content:     {post.content[:150]}...")
        print("-"*70)
    
    # === SAVE TO FILE ===
    writer = JSONWriter("data_sourcing/output")
    writer.save(posts, "reddit")
    print(f"\n✓ Saved {len(posts)} posts to JSON")
    
    # === LOAD AND PARSE JSON ===
    output_files = list(Path("data_sourcing/output").glob("reddit_*.json"))
    if output_files:
        latest = sorted(output_files)[-1]
        print(f"\n📄 Latest output: {latest.name}")
        
        with open(latest) as f:
            data = json.load(f)
            print(f"✓ Loaded {len(data)} posts from JSON")
            print(f"\nFirst post from JSON:")
            print(json.dumps(data[0], indent=2)[:400] + "...")

if __name__ == "__main__":
    asyncio.run(main())
