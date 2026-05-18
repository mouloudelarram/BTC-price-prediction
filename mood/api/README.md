# 🚀 Crypto Market Mood Analysis API

A production-grade REST API for cryptocurrency market sentiment analysis using LLM models and web scrapping. This API provides endpoints to scrape crypto market sentiment from multiple sources and analyze them using advanced LLM models.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

### Scrapper Service
- **Multi-Platform Scraping**: Twitter, Reddit, Fear & Greed Index, CoinDesk, Binance, CoinGecko
- **Asynchronous Processing**: Non-blocking API for long-running scraping tasks
- **Job Management**: Track scraping jobs with status updates and progress tracking
- **Data Persistence**: Automatic storage of scraped data in JSON format
- **Error Handling**: Robust error handling with detailed error messages and retry logic

### Mood Analysis Service  
- **Multiple LLM Models**: Support for various Ollama models for ensemble analysis
- **Async Processing**: Concurrent processing with configurable limits
- **Checkpointing**: Resume capability for interrupted analysis
- **Weighted Aggregation**: Platform-specific weights for balanced sentiment scoring
- **Result Persistence**: Automatic storage of analysis results

### API Features
- **RESTful Design**: Standard REST API with JSON request/response
- **Asynchronous Jobs**: Long-running operations return job IDs for polling
- **Health Checks**: Built-in health check endpoints for monitoring
- **CORS Support**: Cross-origin requests enabled for frontend integration
- **Comprehensive Logging**: Structured logging for debugging and monitoring
- **Error Handling**: Standardized error responses with detailed messages
- **Auto Documentation**: Swagger/OpenAPI documentation at `/docs`

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Application                    │
│  ┌────────────────────────────────────────────────────┐  │
│  │  HTTP Routes Layer                                 │  │
│  │  - Scrapper Routes (/api/v1/scrapper)             │  │
│  │  - Mood Routes (/api/v1/mood)                     │  │
│  │  - Health Routes (/health, /info)                 │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Service Layer                                     │  │
│  │  - ScrapperService                                 │  │
│  │  - MoodAnalyzerService                             │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Core Layer                                        │  │
│  │  - Configuration Management                        │  │
│  │  - Logging                                         │  │
│  │  - Exception Handling                              │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
         ↓                           ↓
    ┌─────────────┐         ┌──────────────────┐
    │  Scrapper   │         │  LLM/Ollama      │
    │  Module     │         │  Service         │
    └─────────────┘         └──────────────────┘
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11+
- Ollama (for LLM models)
- Docker & Docker Compose (optional)

### 2. Installation

```bash
# Clone or navigate to the project
cd mood/api

# Run setup script
# Windows:
setup.bat
# Linux/Mac:
bash setup.sh

# Or manually install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Create `.env` file from template:
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```env
API_HOST=0.0.0.0
API_PORT=8000
OLLAMA_HOST=http://localhost:11434
LOG_LEVEL=INFO
```

### 4. Start the API

```bash
# Development mode
python run.py

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

API will be available at `http://localhost:8000`

---

## 📦 Installation

### Standard Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

### Docker Installation

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t mood-api:latest .
docker run -p 8000:8000 -e OLLAMA_HOST=http://host.docker.internal:11434 mood-api:latest
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_HOST` | `0.0.0.0` | API bind address |
| `API_PORT` | `8000` | API port |
| `API_ENVIRONMENT` | `development` | Environment (development/production) |
| `API_DEBUG` | `False` | Debug mode |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama service URL |
| `OLLAMA_MODEL` | `mistral-large-3:675b-cloud` | Default LLM model |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `DATA_DIR` | `../scrapper/data_sourcing/output` | Scrapper data directory |
| `CHECKPOINT_DIR` | `./checkpoints` | Checkpoint storage directory |
| `OUTPUT_DIR` | `./output` | Analysis output directory |
| `CONCURRENCY_LIMIT` | `3` | Max concurrent API calls |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed CORS origins |

### Platform Weights

Customize platform importance in sentiment analysis:

```env
FEAR_GREED_WEIGHT=0.30     # Fear & Greed Index
COINDESK_WEIGHT=0.25        # News articles
REDDIT_WEIGHT=0.15          # Community sentiment
TRUTH_SOCIAL_WEIGHT=0.10    # Social posts
BINANCE_WEIGHT=0.10         # Trading behavior
COINGECKO_WEIGHT=0.10       # Market data
```

---

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication
Not required by default. Enable in `.env` with `API_KEY_ENABLED=true`

### Response Format

All responses are JSON:

```json
{
  "job_id": "uuid",
  "status": "pending|running|completed|failed",
  "message": "string",
  "data": {}
}
```

### Error Response

```json
{
  "error": "ErrorType",
  "message": "Error description",
  "status_code": 400,
  "timestamp": "2024-01-01T12:00:00Z",
  "details": {}
}
```

---

## 🔌 Scrapper API Endpoints

### Start Scraping
**POST** `/api/v1/scrapper/run`

Start a new scraping job.

**Request:**
```json
{
  "scrapper_type": "all|twitter|reddit",
  "platforms": ["twitter", "reddit"],
  "limit": 100,
  "output_format": "json"
}
```

**Response (202 Accepted):**
```json
{
  "id": "job-uuid",
  "status": "pending",
  "entries_collected": 0,
  "platforms": ["twitter", "reddit"],
  "started_at": "2024-01-01T12:00:00Z"
}
```

### Get Scraping Status
**GET** `/api/v1/scrapper/job/{job_id}`

Get the status of a scraping job.

**Response:**
```json
{
  "job_id": "job-uuid",
  "status": "running",
  "entries_collected": 150,
  "error": null,
  "progress_percentage": 75.5,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:05:00Z"
}
```

### Get Latest Scraped Data
**GET** `/api/v1/scrapper/latest`

Retrieve the most recently scraped data.

**Response:**
```json
{
  "entries": [
    {
      "id": "entry-1",
      "platform": "twitter",
      "text": "Crypto sentiment...",
      "timestamp": "2024-01-01T12:00:00Z",
      "source": "url"
    }
  ],
  "total": 250,
  "scraped_at": "2024-01-01T12:05:00Z"
}
```

### List Available Platforms
**GET** `/api/v1/scrapper/platforms`

Get list of available scraping platforms.

**Response:**
```json
{
  "platforms": [
    "twitter",
    "reddit",
    "fear_greed",
    "coindesk",
    "binance",
    "coingecko"
  ]
}
```

### Cancel Scraping Job
**POST** `/api/v1/scrapper/job/{job_id}/cancel`

Cancel a running scraping job.

---

## 🧠 Mood Analysis API Endpoints

### Start Analysis
**POST** `/api/v1/mood/analyze`

Start a mood analysis job.

**Request:**
```json
{
  "data_source": "scrapper|file",
  "input_file": null,
  "models": ["mistral-large-3:675b-cloud"],
  "batch_size": 5,
  "resume": false
}
```

**Response (202 Accepted):**
```json
{
  "job_id": "job-uuid",
  "status": "pending",
  "total_entries": 150,
  "successful_entries": 0,
  "failed_entries": 0,
  "started_at": "2024-01-01T12:00:00Z"
}
```

### Get Analysis Status
**GET** `/api/v1/mood/job/{job_id}`

Get analysis progress.

**Response:**
```json
{
  "job_id": "job-uuid",
  "status": "running",
  "entries_processed": 75,
  "entries_failed": 2,
  "entries_skipped": 0,
  "progress_percentage": 50.0,
  "current_aggregated_sentiment": 0.35,
  "error": null,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:15:00Z"
}
```

### Get Latest Report
**GET** `/api/v1/mood/latest-report`

Get the most recent mood analysis report.

**Response:**
```json
{
  "entries": [
    {
      "entry_id": "entry-1",
      "platform": "twitter",
      "text": "Crypto text...",
      "status": "completed",
      "aggregated_sentiment": 0.42,
      "aggregated_confidence": 0.89,
      "individual_results": [
        {
          "sentiment_score": 0.42,
          "confidence": 0.89,
          "reasoning": "...",
          "model_name": "mistral-large-3",
          "processing_time": 2.34
        }
      ]
    }
  ],
  "overall_sentiment": 0.38,
  "overall_confidence": 0.87
}
```

### Analyze Latest Scraped Data
**POST** `/api/v1/mood/analyze-from-scrapper`

Directly analyze the latest scraped data.

**Response (202 Accepted):**
```json
{
  "job_id": "job-uuid",
  "status": "pending",
  "total_entries": 150,
  "started_at": "2024-01-01T12:00:00Z"
}
```

### List Available Models
**GET** `/api/v1/mood/models`

Get list of available LLM models.

**Response:**
```json
{
  "models": [
    "mistral-large-3:675b-cloud",
    "llama3.1:latest",
    "qwen2.5vl:latest"
  ]
}
```

---

## 🏥 Health & Info Endpoints

### Health Check
**GET** `/health`

**Response:**
```json
{
  "status": "healthy|degraded|unhealthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "api_version": "1.0.0",
  "services": {
    "api": "healthy",
    "ollama": "healthy",
    "data_storage": "healthy"
  }
}
```

### API Info
**GET** `/info`

Get API version and configuration info.

---

## 📖 Usage Examples

### Example 1: Complete Workflow

```bash
# 1. Start scraping
curl -X POST http://localhost:8000/api/v1/scrapper/run \
  -H "Content-Type: application/json" \
  -d '{
    "scrapper_type": "all",
    "limit": 100
  }'

# Response: {"id": "job-123", "status": "pending"}

# 2. Check scraping status
curl http://localhost:8000/api/v1/scrapper/job/job-123

# 3. Once scraping is done, start mood analysis
curl -X POST http://localhost:8000/api/v1/mood/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "data_source": "scrapper",
    "batch_size": 5
  }'

# Response: {"job_id": "mood-456", "status": "pending"}

# 4. Check analysis status
curl http://localhost:8000/api/v1/mood/job/mood-456

# 5. Get final report
curl http://localhost:8000/api/v1/mood/latest-report
```

### Example 2: Python Client

```python
import httpx
import asyncio

BASE_URL = "http://localhost:8000"

async def analyze_crypto_sentiment():
    async with httpx.AsyncClient() as client:
        # Start scraping
        scrape_response = await client.post(
            f"{BASE_URL}/api/v1/scrapper/run",
            json={"scrapper_type": "all", "limit": 100}
        )
        job_id = scrape_response.json()["id"]
        
        # Wait for scraping
        while True:
            status = await client.get(f"{BASE_URL}/api/v1/scrapper/job/{job_id}")
            if status.json()["status"] == "completed":
                break
            await asyncio.sleep(5)
        
        # Start analysis
        analyze_response = await client.post(
            f"{BASE_URL}/api/v1/mood/analyze",
            json={"data_source": "scrapper"}
        )
        mood_job_id = analyze_response.json()["job_id"]
        
        # Wait for analysis
        while True:
            status = await client.get(f"{BASE_URL}/api/v1/mood/job/{mood_job_id}")
            if status.json()["status"] == "completed":
                break
            await asyncio.sleep(5)
        
        # Get report
        report = await client.get(f"{BASE_URL}/api/v1/mood/latest-report")
        return report.json()

# Run
result = asyncio.run(analyze_crypto_sentiment())
print(result)
```

---

## 🐳 Docker Deployment

### Quick Start with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f mood-api

# Stop services
docker-compose down

# Clean up volumes
docker-compose down -v
```

### Access Services

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Ollama**: http://localhost:11434
- **Nginx**: http://localhost:80

### Customize Docker

Edit `.env` before running:
```bash
cp .env.example .env
# Edit .env with your settings
docker-compose up -d
```

---

## 🚢 Production Deployment

### Best Practices

1. **Use Environment Variables**: Configure via `.env` file
2. **Enable Security**:
   ```env
   API_ENVIRONMENT=production
   API_DEBUG=false
   API_KEY_ENABLED=true
   API_KEY=your-secret-key-here
   ```

3. **Set Proper Logging**:
   ```env
   LOG_LEVEL=INFO
   LOG_FILE=./logs/api.log
   ```

4. **Configure CORS**:
   ```env
   CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
   ```

5. **Use Reverse Proxy** (Nginx):
   - Docker Compose includes Nginx configuration
   - Update `nginx.conf` as needed

6. **Monitor Health**:
   ```bash
   curl http://localhost:8000/health
   ```

### Kubernetes Deployment

Example `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mood-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mood-api
  template:
    metadata:
      labels:
        app: mood-api
    spec:
      containers:
      - name: mood-api
        image: mood-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: OLLAMA_HOST
          value: http://ollama:11434
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

---

## 🔧 Troubleshooting

### API Won't Start

```bash
# Check Python version
python --version  # Should be 3.11+

# Check port is available
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Ollama Connection Issues

```bash
# Verify Ollama is running
curl http://localhost:11434/api/tags

# Check Ollama host in .env
OLLAMA_HOST=http://localhost:11434

# For Docker, use service name:
OLLAMA_HOST=http://ollama:11434
```

### High Memory Usage

Reduce concurrency:
```env
CONCURRENCY_LIMIT=1  # Start with 1, increase gradually
```

### Job Takes Too Long

Adjust timeout:
```env
LLM_TIMEOUT=300  # Seconds
```

### Scrapper Data Not Found

```bash
# Check data directory exists
ls ../scrapper/data_sourcing/output/

# Update path in .env if needed
DATA_DIR=/path/to/scrapper/output
```

---

## 📞 Support & Issues

For issues or questions:

1. Check logs:
   ```bash
   tail -f logs/api.log
   ```

2. Visit API documentation:
   ```
   http://localhost:8000/docs
   ```

3. Check health status:
   ```bash
   curl http://localhost:8000/health
   ```

---

## 📜 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Please ensure:
- Code follows PEP 8 style guide
- Tests pass
- Documentation is updated
- Commit messages are clear

---

**Last Updated**: May 2026  
**Version**: 1.0.0
