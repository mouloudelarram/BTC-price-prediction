# Crypto Sentiment Data Sourcing Pipeline

> 🚀 **Production-ready scraping system for crypto sentiment analysis** with Twitter and Reddit support, anti-bot protections, and async architecture.

## 📋 Features

✅ **Multi-Platform Scraping**
- Twitter/X searching by keywords and hashtags
- Reddit posts and top comments from defined subreddits
- Farcaster and Lens Protocol ready (API configs needed)

✅ **Anti-Bot Protection**
- Browser fingerprinting evasion (stealth mode)
- Random user agents and viewport sizes
- Human-like behavior simulation (random delays)
- Proxy rotation support
- Rate limiting with exponential backoff

✅ **Production-Ready Architecture**
- Async-first design for concurrent scraping
- Modular, extensible class hierarchy
- Structured data models using Pydantic
- Comprehensive logging with Loguru
- JSON deduplication and storage

✅ **Reliability**
- Automatic retries with exponential backoff
- Graceful error handling
- Platform-specific rate limiting
- Detailed logging for debugging

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# From workspace root
pip install -r data_sourcing_requirements.txt

# Install Playwright browsers (one-time setup)
playwright install chromium
```

### 2. (Optional) Configure Proxies

Edit [data_sourcing/config.py](data_sourcing/config.py):

```python
PROXIES = [
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
]
```

### 3. Run the Pipeline

```bash
python -m data_sourcing.main
```

Output will be saved to `data_sourcing/output/` with timestamps:
- `twitter_20260330_143022.json`
- `reddit_20260330_143022.json`

---

## 📖 Configuration

Edit [data_sourcing/config.py](data_sourcing/config.py) to customize:

```python
# Search keywords
KEYWORDS = ["#BTC", "#Bitcoin", "#crypto", ...]

# Target subreddits
SUBREDDITS = ["Bitcoin", "CryptoCurrency", "Ethereum", ...]

# Limits
MAX_POSTS_PER_PLATFORM = 100

# Rate limiting (requests/minute)
RATE_LIMITS = {
    "twitter": 30,
    "reddit": 60,
}

# Browser settings
HEADLESS = True  # Set False to see browser
BROWSER_TIMEOUT = 30000  # ms
```

---

## 📁 Project Structure

```
data_sourcing/
├── scrapers/
│   ├── base_scraper.py          # Base class with retry logic
│   ├── twitter_scraper.py       # X/Twitter scraper (Playwright)
│   ├── reddit_scraper.py        # Reddit scraper (JSON API)
│   ├── farcaster_scraper.py     # Farcaster (placeholder)
│   └── lens_scraper.py          # Lens Protocol (placeholder)
├── core/
│   ├── browser_manager.py       # Playwright + stealth setup
│   ├── proxy_manager.py         # Proxy rotation
│   └── rate_limiter.py          # Platform rate limiting
├── models/
│   └── post.py                  # Pydantic Post model
├── storage/
│   └── json_writer.py           # JSON output with deduplication
├── config.py                    # Configuration
├── main.py                      # Entry point
└── __init__.py
```

---

## 🔐 Anti-Bot Strategy

### Browser Fingerprinting
- ✅ Stealth mode enabled
- ✅ Random user agents (Chrome, Firefox, Safari)
- ✅ Random viewport sizes

### Human Behavior
- ✅ Random delays between actions (1-5 seconds)
- ✅ Simulated scrolling on infinite feeds
- ✅ Proper header injection

### IP Protection
- ✅ Proxy rotation support
- ✅ Auto-retry with new IP on failure

### Rate Limiting
- ✅ Platform-specific limits
- ✅ Exponential backoff: `delay = base * (2^attempt) + jitter`

---

## 📊 Data Model

All posts are normalized to a unified Pydantic model:

```python
class Post(BaseModel):
    platform: str                    # "twitter", "reddit", etc.
    content: str                     # Post body text
    author: str                      # Username
    timestamp: datetime              # Post creation time
    engagement: Dict[str, int]       # Likes, comments, scores
    url: str                         # Direct link
    metadata: Dict[str, Any]         # Platform-specific data
```

JSON output example:
```json
{
  "platform": "twitter",
  "content": "Bitcoin just hit a new ATH! 🚀 #BTC",
  "author": "CryptoExpert",
  "timestamp": "2026-03-30T14:30:22+00:00",
  "engagement": {
    "likes": 1250,
    "retweets": 340,
    "replies": 89
  },
  "url": "https://twitter.com/CryptoExpert/status/1234567890",
  "metadata": {"keyword": "crypto"}
}
```

---

## 🧪 Advanced Usage

### Custom Scraper

```python
from data_sourcing.scrapers import BaseScraper
from data_sourcing.core import RateLimiter

class MyCustomScraper(BaseScraper):
    async def scrape(self, **kwargs):
        await self.rate_limiter.wait()
        # Your scraping logic here
        return self.posts
```

### Using Proxies

```python
from data_sourcing.core import ProxyManager, BrowserManager
from data_sourcing.scrapers import TwitterScraper

proxy_mgr = ProxyManager([
    "http://proxy1:8080",
    "http://proxy2:8080",
])

browser = BrowserManager(headless=True, proxy=proxy_mgr.get_next_proxy())
scraper = TwitterScraper(proxy_manager=proxy_mgr, browser_manager=browser)
posts = await scraper.run()
```

### Running Scrapers Individually

```python
import asyncio
from data_sourcing.scrapers import TwitterScraper

async def main():
    scraper = TwitterScraper()
    posts = await scraper.run(
        keywords=["#Bitcoin", "#Ethereum"],
        max_tweets=100,
        headless=True
    )
    print(f"Collected {len(posts)} tweets")

asyncio.run(main())
```

---

## 📝 Logging

All operations are logged to:
- **Console**: INFO level and above
- **File**: `data_sourcing/output/scraper_{timestamp}.log`

```
2026-03-30 14:30:22 | INFO     | main:main:45 - 🚀 Starting Crypto Sentiment Data Sourcing Pipeline
2026-03-30 14:30:25 | INFO     | twitter_scraper:_scrape_keyword:89 - Scraping tweets for: #Bitcoin
2026-03-30 14:30:45 | INFO     | json_writer:save:32 - Saved 48 unique posts to data_sourcing/output/twitter_20260330_143045.json
```

---

## ⚡ Performance Tips

1. **Reduce per-platform limits** in config if you have rate issues
2. **Increase `BROWSER_TIMEOUT`** if pages load slowly
3. **Use proxies** for large-scale collection
4. **Set `HEADLESS=True`** (default) to save memory
5. **Run during off-peak hours** for better success rates

---

## 🐛 Troubleshooting

### Twitter Scraper Fails
- Twitter frequently updates DOM selectors. Check browser console (run with `HEADLESS=False`)
- Instagram/TikTok have stricter protections; may need additional stealth measures

### Reddit Returns Few Posts
- Reddit is lenient; check `MAX_POSTS_PER_PLATFORM` in config
- Some subreddits may block automated requests; add more to SUBREDDITS list

### Proxy Errors
- Ensure proxy URL format: `http://ip:port` or `http://user:pass@ip:port`
- Test proxy connectivity before adding to config

### "Playwright not installed"
```bash
playwright install chromium
```

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `playwright` | Browser automation with stealth |
| `httpx` | Async HTTP client for Reddit API |
| `pydantic` | Data validation & serialization |
| `loguru` | Structured logging |
| `tenacity` | Retry logic with backoff |

---

## 🎯 Roadmap

- [x] Twitter/X scraper (Playwright)
- [x] Reddit scraper (JSON API)
- [ ] Farcaster scraper (API integration)
- [ ] Lens Protocol scraper (GraphQL)
- [ ] Discord webhook alerts
- [ ] Sentiment analysis pipeline
- [ ] Database storage (PostgreSQL)
- [ ] Distributed scraping (Celery)

---

## ⚙️ System Requirements

- Python 3.11+
- 1GB RAM (minimum)
- 2GB free disk space (for browser + output)
- Internet connection
- Windows / Linux / macOS

---

## 📄 License

MIT

---

**Questions?** Check [data_sourcing/config.py](data_sourcing/config.py) for all configuration options.
