# 📋 Complete File Index

## 🚀 Quick Start Files (Run These First!)

| File | Purpose | How to Use |
|------|---------|-----------|
| **setup.bat** | Install dependencies one-click (Windows) | Double-click or `setup.bat` |
| **setup.ps1** | Install dependencies one-click (PowerShell) | `.\setup.ps1` |
| **run.bat** | Run scraper one-click (Windows) | Double-click or `run.bat` |
| **run.ps1** | Run scraper one-click (PowerShell) | `.\run.ps1` |
| **menu.bat** | Interactive menu for all operations | Double-click for menu |

---

## 📚 Documentation Files

| File | Content |
|------|---------|
| **STATUS.md** | ✅ System status & quick reference |
| **QUICKSTART.md** | 3-minute setup guide |
| **data_sourcing/README.md** | Complete technical documentation |
| **data_sourcing/config.py** | Configuration file (EDIT THIS!) |

---

## 💻 Core Scraper Module (`data_sourcing/`)

### Main Entry Point
- **`main.py`** - Runs Twitter + Reddit scrapers concurrently
- **`__init__.py`** - Module exports

### Configuration  
- **`config.py`** - All settings (keywords, limits, proxies, etc.)

### Scrapers (`data_sourcing/scrapers/`)
| File | Scrapes | Status |
|------|---------|--------|
| **`base_scraper.py`** | Base class for all scrapers | ✅ Core |
| **`twitter_scraper.py`** | X/Twitter tweets | ✅ Working |
| **`reddit_scraper.py`** | Reddit posts & comments | ✅ Working |
| **`farcaster_scraper.py`** | Farcaster casts | 🚧 Placeholder |
| **`lens_scraper.py`** | Lens Protocol posts | 🚧 Placeholder |
| **`__init__.py`** | Module exports | ✅ Core |

### Core Infrastructure (`data_sourcing/core/`)
| File | Purpose |
|------|---------|
| **`browser_manager.py`** | Playwright setup + stealth mode |
| **`proxy_manager.py`** | Proxy rotation |
| **`rate_limiter.py`** | Rate limiting + backoff |
| **`__init__.py`** | Module exports |

### Data Models (`data_sourcing/models/`)
| File | Purpose |
|------|---------|
| **`post.py`** | Unified Post model (Pydantic) |
| **`__init__.py`** | Module exports |

### Storage (`data_sourcing/storage/`)
| File | Purpose |
|------|---------|
| **`json_writer.py`** | JSON output + deduplication |
| **`__init__.py`** | Module exports |

### Output Directory
- **`data_sourcing/output/`** - Where results are saved
  - `twitter_*.json` - Tweet data
  - `reddit_*.json` - Reddit data
  - `scraper_*.log` - Execution logs

---

## 📖 Example Scripts

All examples run the scraper with different configurations:

| File | Example |
|------|---------|
| **`example_basic_run.py`** | Run default pipeline (all scrapers) |
| **`example_custom_config.py`** | Custom keywords & subreddits |
| **`example_with_proxies.py`** | Using proxy rotation |
| **`example_data_access.py`** | How to use collected data |

---

## 📦 Dependencies

- **`data_sourcing_requirements.txt`** - Python package requirements
  - loguru - Logging
  - pydantic - Data validation
  - tenacity - Retry logic
  - playwright - Browser automation
  - httpx - HTTP client
  - aiohttp - Async HTTP

---

## 🎯 How to Use Each File

### 1. **First Time Setup**

```bash
# Run one of these:
setup.bat              # Windows (batch)
.\setup.ps1            # Windows (PowerShell)
# This installs: pip packages + Playwright browsers
```

### 2. **Run the Scraper**

```bash
# Option A: Batch script
run.bat

# Option B: PowerShell
.\run.ps1

# Option C: Direct Python
python -m data_sourcing.main
```

### 3. **Use the Menu**

```bash
menu.bat
# Interactive menu with all options
```

### 4. **Quick Examples**

```bash
python example_basic_run.py           # Default run
python example_custom_config.py       # Custom keywords
python example_with_proxies.py        # With proxies
python example_data_access.py         # Parse results
```

### 5. **Customize Settings**

```bash
# Edit configuration
notepad data_sourcing\config.py

# Or via menu: menu.bat → option 5
```

---

## 📊 Typical Workflow

```
1. setup.bat           ← Install (one time)
   ↓
2. Optionally edit config.py
   ↓
3. run.bat or menu.bat ← Collect data
   ↓
4. Check data_sourcing/output/
   ↓
5. Analyze results
```

---

## 🔍 File Index Summary

**Total Files Created: 30+**

- 4 Quick-start scripts
- 3 Setup/run scripts  
- 4 Documentation files
- 1 Configuration file
- 6 Scraper modules
- 3 Core infrastructure modules
- 2 Data model modules
- 2 Storage modules
- 5 Example scripts
- 1 Requirements file
- Plus `__init__.py` files in each package

---

## ✨ Key Files to Know

| File | Importance | Why |
|------|-----------|-----|
| **setup.bat** | 🔴 Critical | Install first |
| **run.bat** | 🔴 Critical | Run scraper |
| **config.py** | 🟡 Important | Customize behavior |
| **main.py** | 🟡 Important | Main script entry point |
| **STATUS.md** | 🟢 Reference | Check status/help |
| **example_*.py** | 🟢 Reference | Learn how to use |

---

## 🎓 Learning Path

1. **Setup:** `setup.bat`
2. **Quick Run:** `run.bat`
3. **Understand:** Read `QUICKSTART.md`
4. **Learn:** Run `example_basic_run.py`
5. **Customize:** Edit `config.py`, run `python -m data_sourcing.main`
6. **Advanced:** Read `data_sourcing/README.md`, explore source code

---

## 💻 System Requirements

- ✅ Python 3.11+ (tested with 3.13.3)
- ✅ 1GB RAM
- ✅ 2GB free disk space
- ✅ Internet connection
- ✅ Windows/Linux/macOS

---

## ✅ Everything is Ready!

All files are created and tested. You can:
1. Run `setup.bat` to install
2. Run `run.bat` to start scraping
3. Check `data_sourcing/output/` for results

---

**Questions?**
- Check `STATUS.md` for quick help
- Read `QUICKSTART.md` for setup
- See `data_sourcing/README.md` for full docs
- Look at `example_*.py` for code examples
- Edit `config.py` to customize
