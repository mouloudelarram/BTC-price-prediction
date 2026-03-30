"""
Main entry point for crypto sentiment data sourcing pipeline
Runs Twitter and Reddit scrapers concurrently
"""

import asyncio
from loguru import logger
from data_sourcing.scrapers import (
    TwitterScraper, RedditScraper, TruthSocialScraper,
    BinanceScraper, CoinGeckoScraper, FearGreedScraper,
    CoinDeskScraper, PolymarketScraper
)
from data_sourcing.core import BrowserManager, ProxyManager, RateLimiter
from data_sourcing.storage import JSONWriter
from data_sourcing import config


logger.add(
    "data_sourcing/output/scraper_{time}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="INFO",
)


async def run_twitter_scraper():
    """Run Twitter scraper"""
    if not config.SCRAPER_CONFIG["twitter"]["enabled"]:
        logger.info("Twitter scraper disabled in config")
        return []
    
    try:
        proxy_manager = ProxyManager(config.PROXIES) if config.PROXIES else None
        rate_limiter = RateLimiter("twitter", config.RATE_LIMITS["twitter"])
        browser_manager = BrowserManager(headless=config.HEADLESS, proxy=proxy_manager.get_next_proxy() if proxy_manager else None)
        
        scraper = TwitterScraper(
            rate_limiter=rate_limiter,
            proxy_manager=proxy_manager,
            browser_manager=browser_manager,
        )
        
        posts = await scraper.run(
            keywords=config.SCRAPER_CONFIG["twitter"]["keywords"],
            max_tweets=config.SCRAPER_CONFIG["twitter"]["max_tweets"],
            headless=config.HEADLESS,
        )
        
        return posts
    
    except Exception as e:
        logger.error(f"Twitter scraper failed: {e}")
        return []


async def run_reddit_scraper():
    """Run Reddit scraper"""
    if not config.SCRAPER_CONFIG["reddit"]["enabled"]:
        logger.info("Reddit scraper disabled in config")
        return []
    
    try:
        proxy_manager = ProxyManager(config.PROXIES) if config.PROXIES else None
        rate_limiter = RateLimiter("reddit", config.RATE_LIMITS["reddit"])
        
        scraper = RedditScraper(
            rate_limiter=rate_limiter,
            proxy_manager=proxy_manager,
        )
        
        posts = await scraper.run(
            subreddits=config.SCRAPER_CONFIG["reddit"]["subreddits"],
            max_posts_per_subreddit=config.SCRAPER_CONFIG["reddit"]["max_posts_per_subreddit"],
            include_comments=config.SCRAPER_CONFIG["reddit"]["include_comments"],
        )
        
        return posts
    
    except Exception as e:
        logger.error(f"Reddit scraper failed: {e}")
        return []


async def run_truth_social_scraper():
    """Run Truth Social scraper"""
    if not config.SCRAPER_CONFIG["truth_social"]["enabled"]:
        logger.info("Truth Social scraper disabled in config")
        return []
    
    try:
        proxy_manager = ProxyManager(config.PROXIES) if config.PROXIES else None
        rate_limiter = RateLimiter("truth_social", config.RATE_LIMITS.get("truth_social", 30))
        browser_manager = BrowserManager(headless=config.HEADLESS, proxy=proxy_manager.get_next_proxy() if proxy_manager else None)
        
        scraper = TruthSocialScraper(
            rate_limiter=rate_limiter,
            proxy_manager=proxy_manager,
            browser_manager=browser_manager,
        )
        
        posts = await scraper.run(
            accounts=config.SCRAPER_CONFIG["truth_social"]["accounts"],
            max_posts_per_account=config.SCRAPER_CONFIG["truth_social"]["max_posts_per_account"],
            headless=config.HEADLESS,
        )
        
        return posts
    
    except Exception as e:
        logger.error(f"Truth Social scraper failed: {e}")
        return []


async def run_binance_scraper():
    """Run Binance scraper"""
    if not config.SCRAPER_CONFIG["binance"]["enabled"]:
        logger.info("Binance scraper disabled in config")
        return []
    
    try:
        proxy_manager = ProxyManager(config.PROXIES) if config.PROXIES else None
        rate_limiter = RateLimiter("binance", config.RATE_LIMITS["binance"])
        
        scraper = BinanceScraper(
            rate_limiter=rate_limiter,
            proxy_manager=proxy_manager,
        )
        
        posts = await scraper.run(
            symbols=config.SCRAPER_CONFIG["binance"]["symbols"],
            max_data_points=config.SCRAPER_CONFIG["binance"]["max_data_points"],
        )
        
        return posts
    
    except Exception as e:
        logger.error(f"Binance scraper failed: {e}")
        return []


async def run_coingecko_scraper():
    """Run CoinGecko scraper"""
    if not config.SCRAPER_CONFIG["coingecko"]["enabled"]:
        logger.info("CoinGecko scraper disabled in config")
        return []
    
    try:
        proxy_manager = ProxyManager(config.PROXIES) if config.PROXIES else None
        rate_limiter = RateLimiter("coingecko", config.RATE_LIMITS["coingecko"])
        
        scraper = CoinGeckoScraper(
            rate_limiter=rate_limiter,
            proxy_manager=proxy_manager,
        )
        
        posts = await scraper.run(
            coins=config.SCRAPER_CONFIG["coingecko"]["coins"],
            max_data_points=config.SCRAPER_CONFIG["coingecko"]["max_data_points"],
        )
        
        return posts
    
    except Exception as e:
        logger.error(f"CoinGecko scraper failed: {e}")
        return []


async def run_fear_greed_scraper():
    """Run Fear & Greed Index scraper"""
    if not config.SCRAPER_CONFIG["fear_greed"]["enabled"]:
        logger.info("Fear & Greed scraper disabled in config")
        return []
    
    try:
        proxy_manager = ProxyManager(config.PROXIES) if config.PROXIES else None
        rate_limiter = RateLimiter("fear_greed", config.RATE_LIMITS["fear_greed"])
        
        scraper = FearGreedScraper(
            rate_limiter=rate_limiter,
            proxy_manager=proxy_manager,
        )
        
        posts = await scraper.run(
            limit=config.SCRAPER_CONFIG["fear_greed"]["limit"],
        )
        
        return posts
    
    except Exception as e:
        logger.error(f"Fear & Greed scraper failed: {e}")
        return []


async def run_coindesk_scraper():
    """Run CoinDesk scraper"""
    if not config.SCRAPER_CONFIG["coindesk"]["enabled"]:
        logger.info("CoinDesk scraper disabled in config")
        return []
    
    try:
        proxy_manager = ProxyManager(config.PROXIES) if config.PROXIES else None
        rate_limiter = RateLimiter("coindesk", config.RATE_LIMITS["coindesk"])
        
        scraper = CoinDeskScraper(
            rate_limiter=rate_limiter,
            proxy_manager=proxy_manager,
        )
        
        posts = await scraper.run(
            max_articles=config.SCRAPER_CONFIG["coindesk"]["max_articles"],
        )
        
        return posts
    
    except Exception as e:
        logger.error(f"CoinDesk scraper failed: {e}")
        return []


async def run_polymarket_scraper():
    """Run Polymarket scraper"""
    if not config.SCRAPER_CONFIG["polymarket"]["enabled"]:
        logger.info("Polymarket scraper disabled in config")
        return []
    
    try:
        proxy_manager = ProxyManager(config.PROXIES) if config.PROXIES else None
        rate_limiter = RateLimiter("polymarket", config.RATE_LIMITS["polymarket"])
        browser_manager = BrowserManager(headless=config.HEADLESS, proxy=proxy_manager.get_next_proxy() if proxy_manager else None)
        
        scraper = PolymarketScraper(
            rate_limiter=rate_limiter,
            proxy_manager=proxy_manager,
            browser_manager=browser_manager,
        )
        
        posts = await scraper.run(
            search_terms=config.SCRAPER_CONFIG["polymarket"]["search_terms"],
            max_markets=config.SCRAPER_CONFIG["polymarket"]["max_markets"],
            headless=config.HEADLESS,
        )
        
        return posts
    
    except Exception as e:
        logger.error(f"Polymarket scraper failed: {e}")
        return []


async def main():
    """Run all enabled scrapers concurrently"""
    logger.info("=" * 60)
    logger.info("🚀 Starting Crypto Sentiment Data Sourcing Pipeline")
    logger.info("=" * 60)
    
    # Run scrapers concurrently
    results = await asyncio.gather(
        run_twitter_scraper(),
        run_reddit_scraper(),
        run_truth_social_scraper(),
        run_binance_scraper(),
        run_coingecko_scraper(),
        run_fear_greed_scraper(),
        run_coindesk_scraper(),
        run_polymarket_scraper(),
    )
    
    twitter_posts, reddit_posts, truth_social_posts, binance_posts, coingecko_posts, fear_greed_posts, coindesk_posts, polymarket_posts = results
    
    # Save results
    writer = JSONWriter(config.OUTPUT_DIR)
    
    if twitter_posts:
        writer.save(twitter_posts, "twitter")
    
    if reddit_posts:
        writer.save(reddit_posts, "reddit")
    
    if truth_social_posts:
        writer.save(truth_social_posts, "truth_social")
    
    if binance_posts:
        writer.save(binance_posts, "binance")
    
    if coingecko_posts:
        writer.save(coingecko_posts, "coingecko")
    
    if fear_greed_posts:
        writer.save(fear_greed_posts, "fear_greed")
    
    if coindesk_posts:
        writer.save(coindesk_posts, "coindesk")
    
    if polymarket_posts:
        writer.save(polymarket_posts, "polymarket")
    
    total_posts = (
        len(twitter_posts) + len(reddit_posts) + len(truth_social_posts) +
        len(binance_posts) + len(coingecko_posts) + len(fear_greed_posts) +
        len(coindesk_posts) + len(polymarket_posts)
    )
    
    logger.info("=" * 60)
    logger.info(f"✅ Pipeline Complete: {total_posts} total posts collected")
    logger.info(f"   - Twitter: {len(twitter_posts)} posts")
    logger.info(f"   - Reddit: {len(reddit_posts)} posts")
    logger.info(f"   - Truth Social: {len(truth_social_posts)} posts")
    logger.info(f"   - Binance: {len(binance_posts)} posts")
    logger.info(f"   - CoinGecko: {len(coingecko_posts)} posts")
    logger.info(f"   - Fear & Greed: {len(fear_greed_posts)} posts")
    logger.info(f"   - CoinDesk: {len(coindesk_posts)} posts")
    logger.info(f"   - Polymarket: {len(polymarket_posts)} posts")
    logger.info(f"   - Output: {config.OUTPUT_DIR}/")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
