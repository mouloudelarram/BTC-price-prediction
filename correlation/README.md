# BTC Correlation Engine

A production-grade microservice for analyzing Bitcoin price correlations with global financial indices and generating daily trading signals (BUY/SELL/HOLD).

## 📋 Overview

The Correlation Engine is part of the **BNMP (BTC Next Move Prediction)** system. It analyzes lagged correlations between Bitcoin and 100+ financial assets to identify predictive relationships and generate actionable trading signals.

### Key Features

- ✅ **Lagged Correlation Analysis** - Identify which indices lead/lag Bitcoin price movements
- ✅ **Daily Signal Generation** - Produce BUY/SELL/HOLD recommendations based on correlation strength
- ✅ **RESTful API** - FastAPI with automatic OpenAPI documentation
- ✅ **Backtesting** - Evaluate historical decisions against actual price data
- ✅ **Production-Ready** - Type-safe with Pydantic models, comprehensive logging, error handling
- ✅ **Modular Architecture** - Clean separation of concerns, easy to extend

### Assets Analyzed

- **Bitcoin (BTC)** - Primary asset
- **50+ Cryptocurrencies** - ETH, SOL, MATIC, LINK, etc.
- **20 Stock Indices** - S&P 500, Nikkei 225, DAX, etc.
- **28 ETFs & Sectors** - SPY, QQQ, XLY, XLE, etc.
- **International Assets** - FXI, EEM, VWO, etc.
- **Commodities & Bonds** - Gold, Silver, TLT, etc.

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start API Server

```bash
cd correlation/
python main.py
```

API will be available at:
- **http://localhost:8000** - API root
- **http://localhost:8000/docs** - Interactive API documentation
- **http://localhost:8000/redoc** - Alternative documentation

### 3. Run Daily Pipeline

```bash
# Dry-run (test without storing results)
python scripts/daily_job.py --dry-run

# Production execution
python scripts/daily_job.py
```

### 4. Run Unit Tests

```bash
python -m pytest tests/ -v
```

---

## 📡 API Endpoints

### Get Latest Signal
```bash
GET /api/v1/correlation/signal
```

**Response:**
```json
{
  "signal": "BUY",
  "confidence": "85.3%",
  "timestamp": "2026-05-17T12:34:56Z",
  "net_score": 2.45,
  "analyzed_count": 18,
  "top_contributors": [
    {
      "ticker": "^GSPC",
      "impact": 0.95,
      "period": "1mo",
      "move": "UP"
    }
  ]
}
```

### Get Correlation Summary
```bash
GET /api/v1/correlation/summary
```

Returns top correlated indices with correlation scores and best lags.

### Run Daily Pipeline
```bash
POST /api/v1/correlation/pipeline/run
```

Executes full correlation analysis and signal generation. Stores results.

### Dry-Run Pipeline
```bash
POST /api/v1/correlation/pipeline/dry-run
```

Test pipeline without storing results.

### Health Check
```bash
GET /health
GET /api/v1/correlation/health
```

---

## 🛠️ CLI Commands

### Daily Pipeline

```bash
# Dry-run execution
python scripts/daily_job.py --dry-run

# Production execution
python scripts/daily_job.py

# Save results to JSON
python scripts/daily_job.py --output result.json
```

### Backtesting

```bash
# Single decision evaluation
python scripts/backtest.py --date 2026-05-16 --decision BUY

# Batch evaluation from CSV
python scripts/backtest.py --file decisions.csv

# Save results
python scripts/backtest.py --file decisions.csv --output backtest.json
```

### Unit Tests

```bash
# Run all tests
python -m pytest tests/ -v

# With coverage report
python -m pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file in the `correlation/` directory:

```bash
# API Server
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=False

# Logging
LOG_LEVEL=INFO

# Pipeline
PIPELINE_ENABLED=False
PIPELINE_SCHEDULE_HOUR=0

# Cache
CACHE_TTL_SECONDS=3600

# YFinance SSL (optional)
YFINANCE_DISABLE_SSL_VERIFY=false
```

See `.env.example` for reference.

### Programmatic Configuration

Edit `config.py` to customize:

- **Correlation Periods** - Time windows for analysis (1mo, 3mo, 6mo, 1y, 2y, 3y)
- **Lag Days** - How many days to shift BTC returns (1-7 days)
- **Signal Thresholds** - BUY/SELL decision thresholds
- **Correlation Weights** - How to weight different periods
- **Asset Lists** - Which tickers to analyze

---

## 🏗️ Architecture

```
correlation/
├── app/                          # Application code
│   ├── api/routes.py            # FastAPI endpoints
│   ├── core/
│   │   ├── correlation.py       # Correlation analysis engine
│   │   └── signal_engine.py     # Signal generation logic
│   ├── data/loaders.py          # Binance data fetching
│   ├── pipeline/executor.py     # Daily pipeline orchestrator
│   ├── models/__init__.py       # Pydantic data models
│   └── utils/
│       ├── logger.py            # Logging setup
│       └── helpers.py           # Utility functions
├── scripts/
│   ├── daily_job.py             # CLI for daily execution
│   └── backtest.py              # Backtesting tool
├── tests/test_correlation.py    # Unit tests
├── main.py                      # FastAPI app entry point
├── config.py                    # Configuration
├── requirements.txt             # Dependencies
└── results/                     # Pipeline outputs (created at runtime)
```

---

## 📊 Data Flow

```
1. Daily Execution
   └─ python scripts/daily_job.py

2. Correlation Analysis
   ├─ Download OHLCV data (100+ assets)
   ├─ Calculate daily returns
   ├─ Compute lagged correlations
   └─ Save results → results/correlation_summary.txt

3. Signal Generation
   ├─ Parse correlation file
   ├─ Filter by thresholds
   ├─ Calculate weighted score
   ├─ Determine BUY/SELL/HOLD
   └─ Save results → results/latest_signal.json

4. API Consumption
   ├─ GET /api/v1/correlation/signal
   └─ Display in BNMP dashboard
```

---

## 🔍 How It Works

### Correlation Analysis

For each time period (1mo, 3mo, 6mo, 1y, 2y, 3y) and lag (1-7 days):

1. **Fetch Data** - Download OHLCV from yfinance
2. **Calculate Returns** - Daily % change for each asset
3. **Lag BTC** - Shift Bitcoin returns by N days
4. **Correlate** - Pearson correlation between lagged BTC and other assets
5. **Identify** - Top 20 most correlated assets

### Signal Generation

1. **Parse Summary** - Extract correlation data from analysis
2. **Filter** - Keep correlations above threshold (0.30 short-term, 0.20 long-term)
3. **Score** - Calculate weighted contribution:
   - Correlation strength × period weight × market direction
4. **Decide**:
   - Score ≥ 2.0 → **BUY**
   - Score ≤ -2.0 → **SELL**
   - Otherwise → **HOLD**
5. **Confidence** - (|score| / max_potential) × 100%

---

## 🐛 Troubleshooting

### SSL Certificate Errors

**Problem:** `SSL certificate problem: self signed certificate in certificate chain`

**Solution:** Set environment variable:
```bash
$env:YFINANCE_DISABLE_SSL_VERIFY='true'
python scripts/daily_job.py --dry-run
```

⚠️ Only for development/testing. Not recommended for production.

### Port Already in Use

**Problem:** `Address already in use 0.0.0.0:8000`

**Solution:** Use a different port:
```bash
export API_PORT=8001
python main.py
```

### Module Not Found

**Problem:** `ModuleNotFoundError: No module named 'app'`

**Solution:** Run from the correct directory:
```bash
cd correlation/
python scripts/daily_job.py --dry-run
```

Or use absolute path:
```bash
python correlation/scripts/daily_job.py --dry-run
```

### No Data Returned

**Problem:** Pipeline runs but no correlation data

**Possible causes:**
1. Network connectivity issues
2. yfinance API rate limiting
3. Ticker symbols are no longer available

**Solution:**
- Wait and retry (rate limiting resets after ~60 seconds)
- Check yfinance status
- Update ticker list in `config.py`

---

## 📈 Performance

- **Correlation Analysis** - 2-5 minutes (downloads ~100 assets, multiple time periods)
- **Signal Generation** - <1 second (analyzes correlations)
- **API Response** - <100ms (cached results)
- **Memory Usage** - ~500MB (full asset list, multiple periods)

---

## 📋 Output Files

### Correlation Summary
**Location:** `results/correlation_summary.txt`

Contains top 20 correlated assets for each period/lag combination.

### Latest Signal
**Location:** `results/latest_signal.json`

Current trading signal in JSON format.

### Pipeline Log
**Location:** `results/pipeline_log.json`

Historical execution log with timestamps and signals.

### Application Logs
**Location:** `logs/`

Detailed logs for debugging and monitoring.

---

## 🧪 Testing

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Specific Test
```bash
python -m pytest tests/test_correlation.py::TestSignalEngine::test_determine_signal_buy -v
```

### Test Coverage
```bash
python -m pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## 🔐 Production Deployment

### Docker (Optional)

```dockerfile
FROM python:3.14

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t correlation-engine .
docker run -p 8000:8000 correlation-engine
```

### Environment Variables (Production)

```bash
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=False
LOG_LEVEL=INFO
PIPELINE_ENABLED=True
PIPELINE_SCHEDULE_HOUR=0
CACHE_TTL_SECONDS=3600
```

### Monitoring

Check logs:
```bash
tail -f logs/*.log
```

Monitor API:
```bash
curl http://localhost:8000/health
```

---

## 📚 Documentation

- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Architecture refactoring overview
- [FILES_TO_DELETE.md](FILES_TO_DELETE.md) - Cleanup old monolithic files
- [config.py](config.py) - Configuration reference
- [app/models/__init__.py](app/models/__init__.py) - Data models

---

## 🤝 Integration

### With BNMP Dashboard

```python
import requests

# Get latest signal
response = requests.get("http://localhost:8000/api/v1/correlation/signal")
signal = response.json()

# Update dashboard
dashboard.update_btc_signal(
    signal=signal["signal"],
    confidence=signal["confidence"],
    contributors=signal["top_contributors"]
)
```

### With External Systems

All endpoints return JSON for easy integration:
- Python: `requests` library
- JavaScript: `fetch()` API
- Curl: Command-line
- Postman: REST client

---

## 📞 Support

### Common Issues

1. **Can't import 'app' module** → Run from correct directory
2. **SSL certificate errors** → Set `YFINANCE_DISABLE_SSL_VERIFY=true`
3. **Port in use** → Change `API_PORT` in `.env`
4. **No signal data** → Check network, wait for retry

### Logs Location

```
logs/
├── __main__.log
├── app.core.correlation.log
├── app.core.signal_engine.log
├── app.data.loaders.log
├── app.pipeline.executor.log
└── app.utils.logger.log
```

---

## 📄 License

Part of BNMP (BTC Next Move Prediction) system.

---

## ✨ Key Metrics

| Metric | Value |
|--------|-------|
| Assets Analyzed | 100+ |
| Time Periods | 6 (1mo-3y) |
| Lag Shifts | 7 days |
| API Endpoints | 5 |
| Test Coverage | 50%+ |
| Response Time | <100ms |
| Update Frequency | Daily |

---

**Last Updated:** May 17, 2026  
**Status:** ✅ Production Ready
