import random
from typing import Optional, List
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from loguru import logger


class BrowserManager:
    """Manages browser instances with stealth and anti-bot evasion"""
    
    STEALTH_USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
    ]
    
    def __init__(self, headless: bool = True, proxy: Optional[str] = None):
        self.headless = headless
        self.proxy = proxy
        self.playwright = None
        self.browser = None
    
    async def launch(self) -> Browser:
        """Launch browser with stealth settings"""
        if self.browser:
            return self.browser
        
        self.playwright = await async_playwright().start()
        
        launch_args = {
            "headless": self.headless,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-first-run",
                "--no-default-browser-check",
            ]
        }
        
        if self.proxy:
            launch_args["proxy"] = {"server": self.proxy}
        
        self.browser = await self.playwright.chromium.launch(**launch_args)
        logger.info(f"Browser launched (headless={self.headless})")
        return self.browser
    
    async def create_context(self) -> BrowserContext:
        """Create browser context with stealth headers"""
        if not self.browser:
            await self.launch()
        
        context = await self.browser.new_context(
            user_agent=random.choice(self.STEALTH_USER_AGENTS),
            viewport={"width": random.randint(1366, 1920), "height": random.randint(768, 1080)},
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
        )
        
        # Inject stealth script to hide automation
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
            });
        """)
        
        return context
    
    async def create_page(self, context: BrowserContext) -> Page:
        """Create page with random delays"""
        page = await context.new_page()
        
        # Random delays to simulate human behavior
        await page.evaluate("""
            () => {
                window.chrome = {
                    runtime: {}
                };
            }
        """)
        
        return page
    
    async def close(self) -> None:
        """Close browser and cleanup"""
        if self.browser:
            await self.browser.close()
            logger.info("Browser closed")
        
        if self.playwright:
            await self.playwright.stop()
