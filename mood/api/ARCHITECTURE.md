# API Architecture & Technical Details

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        Client Applications                       │
│                  (Web Frontend / Mobile / CLI)                   │
└───────────────────┬──────────────────────────────────────────────┘
                    │
                    │ HTTPS/HTTP
                    ↓
┌──────────────────────────────────────────────────────────────────┐
│                      Nginx Reverse Proxy                         │
│  - Load Balancing                                                │
│  - SSL/TLS Termination                                           │
│  - Request Routing                                               │
│  - Compression                                                   │
└───────────────────┬──────────────────────────────────────────────┘
                    │
                    ↓
┌──────────────────────────────────────────────────────────────────┐
│                     FastAPI Application                          │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ API Routes Layer (Pydantic Validated Requests)            │ │
│  │                                                            │ │
│  │  ├─ GET   /health                                         │ │
│  │  ├─ GET   /info                                           │ │
│  │  │                                                        │ │
│  │  ├─ POST  /api/v1/scrapper/run                           │ │
│  │  ├─ GET   /api/v1/scrapper/job/{job_id}                 │ │
│  │  ├─ GET   /api/v1/scrapper/latest                        │ │
│  │  ├─ GET   /api/v1/scrapper/platforms                     │ │
│  │  │                                                        │ │
│  │  ├─ POST  /api/v1/mood/analyze                           │ │
│  │  ├─ GET   /api/v1/mood/job/{job_id}                     │ │
│  │  ├─ GET   /api/v1/mood/latest-report                     │ │
│  │  └─ GET   /api/v1/mood/models                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           │                                     │
│                           ↓                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Service Layer (Business Logic)                            │ │
│  │                                                            │ │
│  │  ├─ ScrapperService                                       │ │
│  │  │   ├─ start_scraping()                                  │ │
│  │  │   ├─ get_job_status()                                  │ │
│  │  │   ├─ get_latest_data()                                 │ │
│  │  │   └─ cancel_job()                                      │ │
│  │  │                                                        │ │
│  │  └─ MoodAnalyzerService                                   │ │
│  │      ├─ start_analysis()                                  │ │
│  │      ├─ get_job_status()                                  │ │
│  │      ├─ get_latest_report()                               │ │
│  │      └─ cancel_job()                                      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           │                                     │
│                           ↓                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Core Layer (Utilities)                                    │ │
│  │                                                            │ │
│  │  ├─ Configuration Management (config.py)                  │ │
│  │  ├─ Structured Logging (logger.py)                        │ │
│  │  ├─ Exception Handling (exceptions.py)                    │ │
│  │  └─ Data Validation (schemas/__init__.py)                 │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
         │                          │
         ├─ Async Tasks ────────────┤
         │                          │
         ↓                          ↓
    ┌─────────────┐           ┌─────────────────┐
    │  Scrapper   │           │  LLM/Ollama     │
    │  Module     │           │  Service        │
    │             │           │                 │
    │ - Twitter   │           │ - Multiple      │
    │ - Reddit    │           │   Models        │
    │ - Fear/Greed│           │ - Async         │
    │ - CoinDesk  │           │   Processing    │
    │ - Binance   │           │ - Checkpointing │
    │ - CoinGecko │           │ - Aggregation   │
    └──────┬──────┘           └────────┬────────┘
           │                          │
           ↓                          ↓
    ┌─────────────┐           ┌─────────────────┐
    │   JSON      │           │ Local Ollama    │
    │   Output    │           │ (Port 11434)    │
    │   Files     │           │                 │
    │             │           │ Runs LLM Models │
    │ Formatted:  │           │ on GPU/CPU      │
    │ - Platform  │           └─────────────────┘
    │ - Text      │
    │ - Metadata  │
    └─────────────┘
```

## Data Flow

### Scraping Flow
```
1. Client Request
   ↓
2. Validate Request (ScrapperRequest schema)
   ↓
3. Create Job in ScrapperService
   ↓
4. Return Job ID (202 Accepted)
   ↓
5. Async Execution:
   a. Import scraper module
   b. Execute platform-specific scraper
   c. Collect entries
   d. Save to JSON file
   e. Update job status
   ↓
6. Client Polls: GET /api/v1/scrapper/job/{job_id}
   ↓
7. Get Latest: GET /api/v1/scrapper/latest
```

### Analysis Flow
```
1. Client Request (data_source, models, etc.)
   ↓
2. Validate Request (MoodAnalyzeRequest schema)
   ↓
3. Create Job in MoodAnalyzerService
   ↓
4. Return Job ID (202 Accepted)
   ↓
5. Async Execution:
   a. Load data (from scrapper or file)
   b. Initialize MoodAnalyzer
   c. Process in batches:
      - Split entries into batches
      - For each batch:
        * Call LLM models (in parallel)
        * Aggregate results
        * Save checkpoints
   d. Calculate platform weights
   e. Generate final report
   ↓
6. Client Polls: GET /api/v1/mood/job/{job_id}
   ↓
7. Get Report: GET /api/v1/mood/latest-report
```

## Request/Response Lifecycle

### Example: Complete Workflow

```
1. START SCRAPING
   POST /api/v1/scrapper/run
   Request:  {scrapper_type: "all", limit: 100}
   Response: {id: "job-123", status: "pending"}
   Status:   202 Accepted

2. POLL SCRAPER STATUS
   GET /api/v1/scrapper/job/job-123
   Response: {status: "running", entries_collected: 45}
   Status:   200 OK
   
   (repeat until status == "completed")

3. GET SCRAPED DATA
   GET /api/v1/scrapper/latest
   Response: {entries: [...], total: 100}
   Status:   200 OK

4. START ANALYSIS
   POST /api/v1/mood/analyze
   Request:  {data_source: "scrapper", batch_size: 5}
   Response: {job_id: "mood-456", status: "pending"}
   Status:   202 Accepted

5. POLL ANALYSIS STATUS
   GET /api/v1/mood/job/mood-456
   Response: {status: "running", entries_processed: 25}
   Status:   200 OK
   
   (repeat until status == "completed")

6. GET FINAL REPORT
   GET /api/v1/mood/latest-report
   Response: {
     overall_sentiment: 0.35,
     entries: [...],
     platform_breakdown: {...}
   }
   Status:   200 OK
```

## Configuration Hierarchy

```
1. Environment Variables (highest priority)
   (from .env or system environment)
   
2. .env File (from current directory)
   
3. Default Values (from config.py)
   (lowest priority)
```

## Error Handling Strategy

```
Client Error (4xx)
├─ 400 Bad Request: Invalid input
├─ 401 Unauthorized: Missing/invalid API key
├─ 404 Not Found: Resource doesn't exist
└─ 422 Unprocessable Entity: Validation error

Server Error (5xx)
├─ 500 Internal Server Error: Unexpected failure
└─ 503 Service Unavailable: Ollama/Service down

Error Response Format:
{
  "error": "ErrorType",
  "message": "Human-readable error message",
  "status_code": 400,
  "timestamp": "2024-01-01T12:00:00Z",
  "details": {...}
}
```

## Concurrency & Performance

### Async Processing
- All I/O operations are async
- Multiple jobs can run simultaneously
- Non-blocking requests using `asyncio`

### Batch Processing
- Configurable batch size for analysis
- Reduces memory footprint
- Improves throughput

### Checkpointing
- Saves progress after each batch
- Allows resuming interrupted analysis
- Prevents duplicate processing

### Resource Limits
```
Concurrency Limit: 3 (configurable)
Timeout: 60 seconds per inference
Batch Size: 5 entries (configurable)
Max Request Size: 100MB
```

## Security Measures

1. **Input Validation**: Pydantic schemas validate all inputs
2. **Error Messages**: Detailed errors in dev, generic in production
3. **CORS**: Configurable allowed origins
4. **API Keys**: Optional authentication via headers
5. **HTTPS**: Nginx handles SSL/TLS termination
6. **Rate Limiting**: Can be added via Nginx
7. **Logging**: All requests/responses logged
8. **Environment Variables**: Sensitive data in .env

## Monitoring & Observability

### Health Checks
- GET /health: Overall system health
- Checks: API, Ollama, data storage

### Logging
- Structured logging to file and console
- Rotating file handler (10MB per file, 5 backups)
- Configurable log level

### Metrics (Future)
- Request count, latency, error rate
- Job success/failure rates
- Sentiment distribution
- Model performance

## Deployment Tiers

### Development
```
API_ENVIRONMENT=development
API_DEBUG=true
Single process
Auto-reload
Verbose logging
```

### Staging
```
API_ENVIRONMENT=staging
API_DEBUG=false
Multiple processes
Health monitoring
Moderate logging
```

### Production
```
API_ENVIRONMENT=production
API_DEBUG=false
Multiple replicas (Kubernetes)
Load balancing
Minimal logging
Full monitoring
Backup & recovery
```

---

Last Updated: May 2026
