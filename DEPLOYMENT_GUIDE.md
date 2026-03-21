# Deployment Guide - Enterprise Service Management System

## 🚀 Complete Deployment Instructions

### System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                 PRODUCTION DEPLOYMENT                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Load Balancer / Reverse Proxy (Nginx / Apache)        │ │
│  │  - SSL/TLS Termination                                 │ │
│  │  - Load Distribution                                   │ │
│  └────────────────────────────────────────────────────────┘ │
│         ↓                                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Application Servers (Docker Containers)               │ │
│  │  - Flask API (Gunicorn)                                │ │
│  │  - React Web App                                       │ │
│  │  - Auto-scaling enabled                                │ │
│  └────────────────────────────────────────────────────────┘ │
│         ↓                                                    │
│  ┌────────────┬──────────────┬──────────────┬────────────┐ │
│  │ PostgreSQL │  Redis       │  S3 Storage  │  Backup    │ │
│  │ Database   │  Cache/Queue │  Files       │  Service   │ │
│  └────────────┴──────────────┴──────────────┴────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Monitoring & Logging                                  │ │
│  │  - Prometheus Metrics                                  │ │
│  │  - ELK Stack (Elasticsearch, Logstash, Kibana)         │ │
│  │  - Grafana Dashboards                                  │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Pre-Deployment Checklist

### Infrastructure Requirements
- [ ] Server with at least 4GB RAM and 20GB SSD
- [ ] PostgreSQL 12+ installed
- [ ] Redis 5+ installed
- [ ] Node.js 14+ installed
- [ ] Python 3.8+ installed
- [ ] Docker & Docker Compose (recommended)
- [ ] SSL certificate (Let's Encrypt)
- [ ] Domain name configured
- [ ] Firewall rules configured

### Credentials & API Keys
- [ ] Google Maps API key
- [ ] Stripe API keys (if using Stripe)
- [ ] Email service credentials
- [ ] JWT secret key
- [ ] Database credentials
- [ ] AWS/Cloud provider credentials (if cloud deployed)

### Code Preparation
- [ ] All tests passing
- [ ] Code linting passed
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] Build artifacts generated
- [ ] Git repository clean

---

## 🐳 Docker Deployment (Recommended)

### 1. Create Dockerfile for Backend

Create `Dockerfile.backend`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend_requirements.txt .
RUN pip install --no-cache-dir -r backend_requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')"

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", "wsgi:app"]
```

Create `Dockerfile.frontend`:

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY frontend_package.json package.json
COPY package-lock.json* ./

RUN npm ci

COPY . .

RUN npm run build

FROM nginx:alpine

COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=builder /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:13-alpine
    environment:
      POSTGRES_DB: service_management
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: service_api
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/service_management
      REDIS_URL: redis://redis:6379
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      FLASK_ENV: production
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    ports:
      - "5000:5000"
    restart: unless-stopped
    networks:
      - app-network

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: service_frontend
    ports:
      - "80:80"
    depends_on:
      - api
    restart: unless-stopped
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
```

### 3. Deploy with Docker Compose

```bash
# Create .env file
cp .env.example .env
# Edit .env with production values

# Start services
docker-compose up -d

# Run database migrations
docker-compose exec api flask db upgrade

# Create admin user
docker-compose exec api python -c "
from app import create_app, db
from models import User

app = create_app()
with app.app_context():
    admin = User(
        username='admin',
        email='admin@example.com',
        full_name='Administrator',
        role='admin',
        is_active=True
    )
    admin.set_password('strong_password_here')
    db.session.add(admin)
    db.session.commit()
    print('Admin user created')
"

# Check status
docker-compose ps
docker-compose logs -f api
```

---

## 🔐 SSL/TLS Configuration

### Using Let's Encrypt with Nginx

Create `nginx.conf`:

```nginx
upstream api {
    server api:5000;
}

server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # API
    location /api/ {
        proxy_pass http://api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # CORS headers
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
}
```

Obtain SSL certificate:

```bash
docker run --rm -v /etc/letsencrypt:/etc/letsencrypt \
    certbot/certbot certonly --standalone \
    -d your-domain.com \
    --email your-email@example.com \
    --agree-tos
```

---

## 📊 Monitoring & Logging

### Prometheus Metrics

Create `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'flask-api'
    static_configs:
      - targets: ['localhost:5000']
    metrics_path: '/metrics'
```

### ELK Stack Setup

```bash
# Start Elasticsearch
docker run -d --name elasticsearch \
    -e discovery.type=single-node \
    docker.elastic.co/elasticsearch/elasticsearch:8.0.0

# Start Kibana
docker run -d --name kibana \
    -e ELASTICSEARCH_HOSTS=http://elasticsearch:9200 \
    docker.elastic.co/kibana/kibana:8.0.0

# Configure Flask logging to ELK
# Update app.py with ELKHandler
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Run Tests
        run: |
          pip install -r backend_requirements.txt
          pytest

      - name: Build Docker Images
        run: docker-compose build

      - name: Push to Registry
        run: |
          docker login -u ${{ secrets.DOCKER_USER }} -p ${{ secrets.DOCKER_PASS }}
          docker push your-registry/service-api:latest
          docker push your-registry/service-frontend:latest

      - name: Deploy to Production
        run: |
          ssh -i ${{ secrets.DEPLOY_KEY }} user@server
          docker-compose pull && docker-compose up -d
```

---

## 🔧 Post-Deployment

### Initialize Database

```bash
# Run migrations
flask db upgrade

# Seed initial data
python -c "
from app import create_app, db
from models import *

app = create_app('production')
with app.app_context():
    db.create_all()
    # Add default data
"
```

### Backup Strategy

```bash
# Automated daily backup
0 2 * * * pg_dump -U $DB_USER $DB_NAME | gzip > /backups/db-$(date +%Y%m%d).sql.gz

# S3 backup
aws s3 sync /backups s3://your-backup-bucket/daily/
```

### Performance Tuning

- Configure PostgreSQL for production
- Enable Redis caching
- Configure CDN for static files
- Enable database connection pooling
- Set appropriate worker processes

---

## 🚨 Security Hardening

### Application Security

```python
# In app.py
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
```

### Network Security

- Enable firewall
- Restrict SSH access
- Use VPN for admin access
- Enable DDoS protection
- Configure rate limiting

```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=get_remote_address)
limiter.limit("200 per day, 50 per hour")(auth_bp)
```

---

## 📈 Scaling

### Horizontal Scaling

```yaml
# Load balance across multiple API servers
api:
  deploy:
    replicas: 3
  rolling_update_policy:
    max_surge: 1
    max_unavailable: 0
```

### Database Optimization

- Add read replicas
- Implement caching layer
- Use connection pooling
- Optimize slow queries
- Create indexes strategically

### CDN Configuration

```python
# Serve static files from CDN
app.config['CDN_URL'] = 'https://cdn.example.com'

@app.context_processor
def cdn_processor():
    return dict(cdn_url=app.config['CDN_URL'])
```

---

## 🔍 Troubleshooting

### Common Issues

**Database Connection Error**
```bash
docker-compose logs postgres
docker-compose restart postgres
```

**API Not Responding**
```bash
docker-compose logs api
docker-compose restart api
```

**Frontend Blank Page**
```bash
# Check browser console for errors
# Verify API URL in .env
docker-compose restart frontend
```

**High Memory Usage**
```bash
# Increase container memory limits
# Optimize database queries
# Implement caching
```

---

## 📞 Support & Maintenance

### Regular Maintenance

- Monthly security updates
- Weekly database optimization
- Daily monitoring reviews
- Monthly backups verification
- Quarterly performance audits

### Update Procedure

```bash
# Test updates in staging
git pull origin main
pip install -r backend_requirements.txt
npm install
npm run build

# Deploy to production
docker-compose pull
docker-compose up -d --force-recreate
```

---

**Last Updated:** March 2026
**Version:** 1.0.0
