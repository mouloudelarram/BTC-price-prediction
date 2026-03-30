import json
from pathlib import Path
from typing import List, Set
from datetime import datetime
from loguru import logger
from data_sourcing.models import Post


class JSONWriter:
    """Handles JSON output with deduplication"""
    
    def __init__(self, output_dir: str = "data_sourcing/output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.seen_urls: Set[str] = set()
    
    def save(self, posts: List[Post], platform: str) -> None:
        """Save posts to JSON file with deduplication"""
        if not posts:
            logger.info(f"No posts to save for {platform}")
            return
        
        # Deduplicate by URL
        unique_posts = []
        for post in posts:
            if post.url not in self.seen_urls:
                unique_posts.append(post)
                self.seen_urls.add(post.url)
        
        if not unique_posts:
            logger.info(f"All posts from {platform} were duplicates")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"{platform}_{timestamp}.json"
        
        data = [post.dict() for post in unique_posts]
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Saved {len(unique_posts)} unique posts to {filename}")
