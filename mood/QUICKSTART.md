# 🚀 Quick Start Guide

## 3-Minute Setup

### Step 1: Install Dependencies (2 minutes)

**Windows (Batch):**
```bash
setup.bat
```

**Windows (PowerShell):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\setup.ps1
```

**Linux/Mac:**
```bash
pip install -r data_sourcing_requirements.txt
playwright install chromium
```

### Step 2: Run the Pipeline (1 minute)

**Windows (Batch):**
```bash
run.bat
```

**Windows (PowerShell):**
```powershell
.\run.ps1
```

**Or direct Python:**
```bash
python -m data_sourcing.main
```

### Step 3: Check Output

Results are saved to: **`data_sourcing/output/`**

```
data_sourcing/output/
├── twitter_20260330_143022.json
├── reddit_20260330_143022.json
└── scraper_20260330_143022.log
```

---

## What's Included

✅ **Twitter/X Scraper** - Collects posts by keywords/hashtags  
✅ **Reddit Scraper** - Scrapes posts + top comments  
✅ **Anti-Bot Protection** - Stealth mode, proxy support, rate limiting  
✅ **Async Architecture** - Concurrent scraping for speed  
✅ **Production Ready** - Error handling, logging, retries  

---

## Customize It (5 minutes)

Edit **`data_sourcing/config.py`**:

```python
# Change search keywords
KEYWORDS = ["#YourHashtag", "#AnotherTag"]

# Change subreddits
SUBREDDITS = ["YourSubreddit", "AnotherSub"]

# Adjust limits
MAX_POSTS_PER_PLATFORM = 200

# Add proxies (optional)
PROXIES = ["http://proxy1:8080", "http://proxy2:8080"]

# Hide browser window (faster)
HEADLESS = True
```

Then run again: `python -m data_sourcing.main`

---

## Example: Run Twitter-Only

Create file: **`scrape_twitter_only.py`**

```python
import asyncio
from data_sourcing.scrapers import TwitterScraper
from data_sourcing.storage import JSONWriter

async def main():
    scraper = TwitterScraper()
    posts = await scraper.run(
        keywords=["#Bitcoin", "#Crypto"],
        max_tweets=100,
        headless=True
    )
    
    writer = JSONWriter()
    writer.save(posts, "twitter")
    print(f"✓ Collected {len(posts)} tweets!")

asyncio.run(main())
```

Run: `python scrape_twitter_only.py`

---

## Troubleshooting

### "Playwright not found"
```bash
playwright install chromium
```

### "Twitter scraper not working"
- Twitter updates selectors frequently
- Try running with `HEADLESS = False` in config to debug visually
- Check `data_sourcing/output/scraper_*.log` for errors

### "Reddit returns few results"
- Reddit is lenient; this is normal
- Add more subreddits to `SUBREDDITS` list in config
- Increase `MAX_POSTS_PER_PLATFORM` limit

### "Connection errors"
- Check internet connection
- Try adding proxies if you're rate-limited
- Reduce `MAX_POSTS_PER_PLATFORM` and retry

---

## Next Steps

1. ✅ Run `setup.bat` (or `setup.ps1`)
2. ✅ Run `run.bat` (or `python -m data_sourcing.main`)
3. ✅ Check `data_sourcing/output/` for JSON files
4. ✅ Edit `data_sourcing/config.py` to customize
5. ✅ Explore examples: `example_*.py`

---

## Project Structure

```
BTCPredict/
├── data_sourcing/              ← SCRAPER MODULE
│   ├── scrapers/               ← Platform scrapers
│   ├── core/                   ← Browser, proxy, rate limiting
│   ├── models/                 ← Post data model
│   ├── storage/                ← JSON output
│   ├── config.py               ← EDIT THIS
│   ├── main.py                 ← Entry point
│   ├── README.md               ← Full docs
│   └── output/                 ← Results saved here
├── setup.bat / setup.ps1       ← One-click setup
├── run.bat / run.ps1           ← One-click run
├── example_*.py                ← Usage examples
└── data_sourcing_requirements.txt
```

---

## Key Features at a Glance

| Feature | Status |
|---------|--------|
| Twitter scraper (Playwright) | ✅ Working |
| Reddit scraper (JSON API) | ✅ Working |
| Anti-bot (stealth mode) | ✅ Enabled |
| Proxy rotation | ✅ Supported |
| Rate limiting | ✅ Automatic |
| Error handling | ✅ Robust |
| Logging | ✅ Detailed |
| JSON output | ✅ Clean |
| Deduplication | ✅ Automatic |

---

## Commands Cheat Sheet

```bash
# Setup
setup.bat                              # Windows batch
.\setup.ps1                            # Windows PowerShell

# Run
run.bat                                # Windows batch
.\run.ps1                              # Windows PowerShell
python -m data_sourcing.main          # Direct Python

# Examples
python example_basic_run.py            # Basic run
python example_custom_config.py        # Custom keywords
python example_with_proxies.py         # Using proxies
python example_data_access.py          # Parse output

# Manual scraping
python -c "
import asyncio
from data_sourcing.scrapers import RedditScraper
scraper = RedditScraper()
asyncio.run(scraper.run(subreddits=['Bitcoin']))
"
```

---

**Ready?** Run `setup.bat` (or `setup.ps1` on PowerShell) and then `run.bat` to start scraping! 🚀

For full documentation, see [data_sourcing/README.md](data_sourcing/README.md)
