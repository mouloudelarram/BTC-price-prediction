from typing import Optional, List
from loguru import logger


class ProxyManager:
    """Manages proxy rotation for anonymous scraping"""
    
    def __init__(self, proxies: Optional[List[str]] = None):
        self.proxies = proxies or []
        self.current_index = 0
        self.failed_proxies = set()
    
    def get_next_proxy(self) -> Optional[str]:
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
        
        available = [p for p in self.proxies if p not in self.failed_proxies]
        if not available:
            logger.warning("All proxies marked as failed, resetting...")
            self.failed_proxies.clear()
            available = self.proxies
        
        proxy = available[self.current_index % len(available)]
        self.current_index += 1
        return proxy
    
    def mark_failed(self, proxy: str) -> None:
        """Mark a proxy as failed after error"""
        self.failed_proxies.add(proxy)
        logger.warning(f"Proxy marked as failed: {proxy}")
    
    def reset(self) -> None:
        """Reset proxy rotation"""
        self.current_index = 0
        self.failed_proxies.clear()
