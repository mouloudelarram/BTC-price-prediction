# Quick Reference Guide

## 🚀 Getting Started (5 minutes)

### Step 1: Setup
```bash
cd mood/api
bash quickstart.sh        # Linux/Mac
# or
quickstart.bat            # Windows
```

### Step 2: Start API
```bash
python run.py
# API runs at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Step 3: Make Your First Request
```bash
curl http://localhost:8000/health
```

---

## 📋 Common Tasks

### Health Check
```bash
curl http://localhost:8000/health
```

### Start Scraping (All Platforms)
```bash
curl -X POST http://localhost:8000/api/v1/scrapper/run \
  -H "Content-Type: application/json" \
  -d '{
    "scrapper_type": "all",
    "limit": 100
  }'
# Returns: {"id": "job-uuid", "status": "pending"}
```

### Check Scraping Status
```bash
curl http://localhost:8000/api/v1/scrapper/job/{job_id}
```

### Get Latest Scraped Data
```bash
curl http://localhost:8000/api/v1/scrapper/latest
```

### Start Mood Analysis
```bash
curl -X POST http://localhost:8000/api/v1/mood/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "data_source": "scrapper",
    "batch_size": 5
  }'
# Returns: {"job_id": "mood-uuid", "status": "pending"}
```

### Check Analysis Status
```bash
curl http://localhost:8000/api/v1/mood/job/{job_id}
```

### Get Analysis Report
```bash
curl http://localhost:8000/api/v1/mood/latest-report
```

---

## 🐳 Docker Commands

### Start All Services
```bash
docker-compose up -d
```

### Check Status
```bash
docker-compose ps
```

### View Logs
```bash
docker-compose logs -f mood-api
docker-compose logs -f ollama
```

### Stop Services
```bash
docker-compose down
```

### Clean Everything
```bash
docker-compose down -v
```

---

## 🔧 Configuration

### Environment File
```bash
cp .env.example .env
nano .env  # Edit settings
```

### Key Settings
```env
API_HOST=0.0.0.0              # Listen address
API_PORT=8000                 # API port
OLLAMA_HOST=http://localhost:11434  # Ollama service
LOG_LEVEL=INFO                # Logging level
CONCURRENCY_LIMIT=3           # LLM concurrency
```

---

## 🧪 Testing

### Run Integration Tests
```bash
bash run_tests.sh
```

### Test Specific Endpoint
```bash
python -m pytest tests.py::TestScrapperEndpoints -v
```

### Manual Testing with Postman
```bash
python postman_collection.py
# Import postman_collection.json into Postman
```

---

## 📊 Python Client Usage

### Quick Example (Async)
```python
from client import MoodAnalysisClient
import asyncio

async def main():
    async with MoodAnalysisClient() as client:
        # Start scraping
        job_id = await client.start_scraping("all", limit=50)
        
        # Wait for completion
        await client.wait_for_job(job_id, "scrapper")
        
        # Analyze data
        analysis_id = await client.analyze_from_scrapper()
        
        # Get report
        report = await client.get_latest_report()
        print(report)

asyncio.run(main())
```

### Quick Example (Sync)
```python
from client import MoodAnalysisClientSync

client = MoodAnalysisClientSync()
report = client.run_pipeline()
print(f"Sentiment: {report['overall_sentiment']}")
```

---

## 🔍 Debugging

### Check API Status
```bash
curl http://localhost:8000/health
```

### View API Logs
```bash
tail -f logs/api.log
```

### Check Running Jobs
```bash
# Via API
curl http://localhost:8000/api/v1/scrapper/job/{job_id}
curl http://localhost:8000/api/v1/mood/job/{job_id}
```

### Enable Debug Mode
```env
API_DEBUG=true
LOG_LEVEL=DEBUG
```

### Check Ollama Status
```bash
curl http://localhost:11434/api/tags
```

---

## 🚢 Deployment

### Option 1: Docker (Recommended)
```bash
docker-compose up -d
```

### Option 2: Python (Development)
```bash
python run.py
```

### Option 3: Production Server
```bash
bash setup.sh
# Configure and start with process manager
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| README.md | Complete API documentation |
| ARCHITECTURE.md | System design & data flow |
| DEPLOYMENT.md | Production strategies |
| PROJECT_SUMMARY.md | Project overview |
| client.py | Python SDK |
| examples.py | Usage examples |

---

## 🔗 API Endpoints Reference

### Scrapper API
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/scrapper/run` | Start scraping |
| GET | `/api/v1/scrapper/job/{id}` | Get status |
| GET | `/api/v1/scrapper/latest` | Get data |
| GET | `/api/v1/scrapper/platforms` | List platforms |

### Analysis API
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/mood/analyze` | Start analysis |
| GET | `/api/v1/mood/job/{id}` | Get status |
| GET | `/api/v1/mood/latest-report` | Get report |
| GET | `/api/v1/mood/models` | List models |

### Health & Info
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| GET | `/info` | API info |
| GET | `/docs` | Swagger docs |

---

## ⚡ Performance Tips

1. **Increase Concurrency** (if machine can handle)
   ```env
   CONCURRENCY_LIMIT=5
   ```

2. **Adjust Batch Size** (for memory)
   ```env
   # Smaller = less memory, more time
   BATCH_SIZE=3
   ```

3. **Tune Timeouts** (for slow machines)
   ```env
   LLM_TIMEOUT=600
   ```

4. **Use Docker** for isolation

---

## 🆘 Common Issues

### Issue: Port 8000 already in use
**Solution:** Change port in .env
```env
API_PORT=8001
```

### Issue: Can't connect to Ollama
**Solution:** Check Ollama is running
```bash
curl http://localhost:11434/api/tags
```

### Issue: Out of memory
**Solution:** Reduce concurrency
```env
CONCURRENCY_LIMIT=1
```

### Issue: API won't start
**Solution:** Check logs
```bash
python run.py 2>&1 | tail -20
```

---

## 📞 Support

### Check Health
```bash
curl http://localhost:8000/health
```

### View Documentation
```
http://localhost:8000/docs
```

### Check Logs
```bash
tail -f logs/api.log
```

### Run Tests
```bash
bash run_tests.sh
```

---

## 🎯 Typical Workflow

```
1. API Running
   └─ python run.py

2. Start Scraping
   └─ POST /api/v1/scrapper/run

3. Wait for Completion
   └─ GET /api/v1/scrapper/job/{id}

4. Start Analysis
   └─ POST /api/v1/mood/analyze

5. Monitor Progress
   └─ GET /api/v1/mood/job/{id}

6. Get Results
   └─ GET /api/v1/mood/latest-report
```

---

## 📋 Useful Commands

```bash
# Setup
bash quickstart.sh

# Start
python run.py

# Test
bash run_tests.sh

# Docker
docker-compose up -d

# View logs
tail -f logs/api.log

# Health check
curl http://localhost:8000/health

# API Docs
open http://localhost:8000/docs

# Stop Docker
docker-compose down
```

---

**Last Updated**: May 2026  
**Quick Start Time**: ~5 minutes  
**Full Setup Time**: ~15 minutes

