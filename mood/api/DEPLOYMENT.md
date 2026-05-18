# API Deployment Guide

## Production Deployment Strategies

### 1. Docker Compose (Recommended for Single-Server)

```bash
# Setup
docker-compose up -d

# Access
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Nginx: http://localhost:80

# Logs
docker-compose logs -f mood-api

# Scale workers
docker-compose up -d --scale mood-api=3
```

### 2. Kubernetes Deployment

```bash
# Apply manifests
kubectl apply -f k8s/

# Check status
kubectl get pods
kubectl logs -f deployment/mood-api

# Scale
kubectl scale deployment mood-api --replicas=3
```

**k8s/deployment.yaml**:
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
      - name: api
        image: mood-api:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: API_ENVIRONMENT
          value: production
        - name: OLLAMA_HOST
          value: http://ollama-svc:11434
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
```

### 3. Traditional Server (Ubuntu/Debian)

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y python3.11 python3-pip python3-venv nginx supervisor

# Create app directory
sudo mkdir -p /opt/mood-api
cd /opt/mood-api

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup Supervisor for process management
sudo cp supervisord.conf /etc/supervisor/conf.d/mood-api.conf
sudo systemctl restart supervisor

# Setup Nginx as reverse proxy
sudo cp nginx.conf /etc/nginx/sites-available/mood-api
sudo ln -s /etc/nginx/sites-available/mood-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. AWS ECS Deployment

```bash
# Create ECS task definition
aws ecs register-task-definition --cli-input-json file://task-def.json

# Create ECS service
aws ecs create-service \
  --cluster mood-cluster \
  --service-name mood-api \
  --task-definition mood-api:1 \
  --desired-count 3 \
  --load-balancers targetGroupArn=arn:aws:...,containerName=mood-api,containerPort=8000
```

## Security Checklist

- [ ] Enable API key authentication
- [ ] Use HTTPS/TLS for all connections
- [ ] Set proper CORS origins
- [ ] Rotate secrets regularly
- [ ] Enable logging and monitoring
- [ ] Set resource limits
- [ ] Use rate limiting
- [ ] Enable authentication
- [ ] Regular security updates
- [ ] Monitor API logs

## Performance Tuning

### Settings

```env
# Increase workers (2-4x CPU cores)
WORKERS=8

# Tune concurrency
CONCURRENCY_LIMIT=5

# Adjust timeouts
LLM_TIMEOUT=300
SCRAPPER_TIMEOUT=600

# Cache settings
CACHE_ENABLED=true
CACHE_TTL=7200
```

### Monitoring

```bash
# Check metrics
curl http://localhost:8000/metrics

# Monitor processes
watch -n 1 'ps aux | grep python'

# Check logs
tail -f logs/api.log
```

## Backup & Disaster Recovery

```bash
# Backup checkpoints and output
tar -czf backup-$(date +%Y%m%d).tar.gz checkpoints/ output/

# Backup to S3
aws s3 sync ./output s3://my-bucket/mood-api/output/

# Restore from backup
tar -xzf backup-20240101.tar.gz
```

## Monitoring & Alerting

### Health Check Endpoint

```bash
curl http://localhost:8000/health
```

### Logging

```bash
# Check recent logs
tail -n 100 logs/api.log

# Search for errors
grep ERROR logs/api.log

# Monitor in real-time
tail -f logs/api.log | grep -E "ERROR|WARNING"
```

### Metrics to Monitor

- API response time
- Job success rate
- Error rate
- Memory usage
- CPU usage
- Disk space
- Ollama service availability

## Troubleshooting

### High Memory Usage

```bash
# Check memory
free -h

# Reduce concurrency
CONCURRENCY_LIMIT=1

# Restart services
docker-compose restart
```

### Slow Responses

```bash
# Check Ollama
curl http://localhost:11434/api/tags

# Increase timeout
LLM_TIMEOUT=600

# Check resources
docker stats
```

### Service Unavailable

```bash
# Check logs
docker-compose logs mood-api

# Restart
docker-compose restart mood-api

# Full reset
docker-compose down
docker-compose up -d
```

## Updates & Maintenance

### Updating the API

```bash
# Pull latest code
git pull origin main

# Rebuild image
docker-compose build --no-cache

# Restart service
docker-compose up -d
```

### Database Cleanup

```bash
# Clear old checkpoints
rm -f checkpoints/progress_tracker_*.json

# Clear old output
find output/ -mtime +30 -delete
```

---

Last Updated: May 2026
