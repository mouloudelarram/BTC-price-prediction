"""Crypto Sentiment Data Sourcing Pipeline"""

__version__ = "1.0.0"
__author__ = "AI Crypto Sentiment Team"

from data_sourcing.models import Post
from data_sourcing.scrapers import TwitterScraper, RedditScraper
from data_sourcing.core import BrowserManager, ProxyManager, RateLimiter
from data_sourcing.storage import JSONWriter

__all__ = [
    "Post",
    "TwitterScraper",
    "RedditScraper",
    "BrowserManager",
    "ProxyManager",
    "RateLimiter",
    "JSONWriter",
]
