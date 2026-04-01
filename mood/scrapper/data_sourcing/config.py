"""Configuration for data sourcing pipeline"""

# Keywords to scrape across platforms
KEYWORDS = [
    "#BTC",
    "#Bitcoin",
    "#crypto",
    "#cryptocurrency",
    "#Ethereum",
    "#ETH",
]

# Reddit subreddits
SUBREDDITS = [
    "Bitcoin",
    "CryptoCurrency",
    "Ethereum",
    "crypto",
    "BitcoinDiscussion",
]

# Scraping limits
MAX_POSTS_PER_PLATFORM = 100
MAX_COMMENTS_PER_POST = 10

# Rate limiting (requests per minute)
RATE_LIMITS = {
    "twitter": 30,
    "reddit": 60,
    "truth_social": 30,
    "binance": 60,
    "coingecko": 30,
    "fear_greed": 10,
    "coindesk": 10,
    "polymarket": 30,
    "farcaster": 30,
    "lens": 30,
}

# Proxy settings
PROXIES = []  # Add proxy URLs here if needed: ["http://proxy1:port", "http://proxy2:port"]

# Browser settings
HEADLESS = True  # Set to False to see browser
BROWSER_TIMEOUT = 30000  # milliseconds

# Output settings
OUTPUT_DIR = "data_sourcing/output"

# Scraper configuration
SCRAPER_CONFIG = {
    "twitter": {
        "enabled": False,
        "keywords": KEYWORDS,
        "max_tweets": 50,
    },
    "reddit": {
        "enabled": True,
        "subreddits": SUBREDDITS,
        "max_posts_per_subreddit": 50,
        "include_comments": True,
    },
    "truth_social": {
        "enabled": True,
        "accounts": [
            {
                "handle": "realDonaldTrump",
                "url": "https://truthsocial.com/@realDonaldTrump",
                "priority": "very_high",
                "type": "macro_signal",
                "description": "Primary market-moving account; posts can directly influence crypto narratives, regulation expectations, and BTC sentiment"
            },
            {
                "handle": "DonaldJTrumpJr",
                "url": "https://truthsocial.com/@DonaldJTrumpJr",
                "priority": "high",
                "type": "narrative_signal",
                "description": "Amplifies and sometimes pre-signals crypto-related initiatives and narratives"
            },
            {
                "handle": "EricTrump",
                "url": "https://truthsocial.com/@EricTrump",
                "priority": "high",
                "type": "narrative_signal",
                "description": "Publicly crypto-friendly; may hint at upcoming moves or reinforce bullish sentiment"
            }
        ],
        "max_posts_per_account": 20,
        "filters": {
            "keywords": [
                "bitcoin",
                "btc",
                "crypto",
                "ethereum",
                "eth",
                "blockchain",
                "defi",
                "token",
                "etf",
                "finance",
                "reserve",
                "banking"
            ],
            "min_length": 20,
            "language": "en"
        },
    },
    "binance": {
        "enabled": True,
        "symbols": ["BTCUSDT", "ETHUSDT"],
        "max_data_points": 30,
    },
    "coingecko": {
        "enabled": True,
        "coins": ["bitcoin", "ethereum"],
        "max_data_points": 20,
    },
    "fear_greed": {
        "enabled": True,
        "limit": 70,
    },
    "coindesk": {
        "enabled": True,
        "max_articles": 20,
    },
    "polymarket": {
        "enabled": False,
        "search_terms": ["BTC", "Bitcoin", "crypto"],
        "max_markets": 20,
    },
    "farcaster": {
        "enabled": False,  # Requires API key
        "keywords": KEYWORDS,
    },
    "lens": {
        "enabled": False,  # Requires API endpoint
        "keywords": KEYWORDS,
    },
}
