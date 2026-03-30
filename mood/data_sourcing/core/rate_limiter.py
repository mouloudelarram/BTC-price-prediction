import asyncio
from datetime import datetime, timedelta
from typing import Dict
from loguru import logger


class RateLimiter:
    """Manages per-platform rate limiting with exponential backoff"""
    
    def __init__(self, platform: str, requests_per_minute: int = 30):
        self.platform = platform
        self.requests_per_minute = requests_per_minute
        self.min_delay = 60.0 / requests_per_minute
        self.last_request_time = None
        self.lock = asyncio.Lock()
    
    async def wait(self) -> None:
        """Wait if necessary to respect rate limits"""
        async with self.lock:
            if self.last_request_time:
                elapsed = (datetime.now() - self.last_request_time).total_seconds()
                if elapsed < self.min_delay:
                    wait_time = self.min_delay - elapsed
                    logger.debug(f"{self.platform}: Rate limit wait {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
            
            self.last_request_time = datetime.now()


class BackoffStrategy:
    """Exponential backoff for retries"""
    
    @staticmethod
    def get_delay(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
        """Calculate backoff delay using exponential strategy with jitter"""
        import random
        delay = min(base_delay * (2 ** attempt), max_delay)
        jitter = random.uniform(0, delay * 0.1)
        return delay + jitter
