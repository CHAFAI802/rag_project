# 🐳 Docker Deployment Guide

Complete guide for running RAG Document Search API in Docker.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Docker Compose](#docker-compose)
- [Docker Commands](#docker-commands)
- [Volumes & Persistence](#volumes--persistence)
- [Environment Variables](#environment-variables)
- [Networking](#networking)
- [Resource Limits](#resource-limits)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)

---

## Prerequisites

### Install Docker

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose-plugin

# Add user to docker group (optional)
sudo usermod -aG docker $USER
newgrp docker
```

**macOS:**
```bash
# Install via Homebrew
brew install docker
brew install docker-compose

# Or use Docker Desktop: https://www.docker.com/products/docker-desktop
```

**Windows:**
- Download [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Install and follow setup instructions

### Verify Installation

```bash
docker --version
docker-compose --version
docker run hello-world
```

---

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/CHAFAI802/rag_project.git
cd rag_project
```

### 2. Create Environment File

```bash
cp .env.example .env
# Edit .env and add your HF_TOKEN
```

### 3. Run with Docker Compose

```bash
# Start container
docker-compose up

# Or run in background
docker-compose up -d

# View logs
docker-compose logs -f rag-api

# Stop container
docker-compose down
```

### 4. Test API

```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs

# Ingest document
curl -X POST http://localhost:8000/api/ingest \
  -F "file=@sample.txt"

# Query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Your question?"}'
```

---

## Docker Compose

### File Structure

**docker-compose.yml** defines:
- Container image (built from Dockerfile)
- Port mappings (8000:8000)
- Environment variables
- Volume mounts
- Health checks
- Resource limits
- Restart policy

### Usage

```bash
# Build image
docker-compose build

# Start services
docker-compose up

# Background mode
docker-compose up -d

# View logs
docker-compose logs -f

# List running containers
docker-compose ps

# Stop services
docker-compose stop

# Remove containers
docker-compose down

# Remove everything including volumes
docker-compose down -v

# Rebuild and restart
docker-compose up --build -d
```

### Service Name

The service is named `rag-api`. Access it:
- From host: `http://localhost:8000`
- Between containers: `http://rag-api:8000`

---

## Docker Commands

### Build Image

```bash
# Using docker-compose (recommended)
docker-compose build

# Using docker directly
docker build -t rag-api:latest .

# Build without cache
docker build --no-cache -t rag-api:latest .
```

### Run Container

**Using docker-compose (recommended):**
```bash
docker-compose up -d
```

**Using docker directly:**
```bash
docker run -d \
  --name rag-api \
  -p 8000:8000 \
  -e HF_TOKEN=your_token_here \
  -v $(pwd)/data:/app/data \
  rag-api:latest
```

### Container Management

```bash
# List running containers
docker ps

# List all containers
docker ps -a

# View logs
docker logs -f rag-api

# Execute command in container
docker exec -it rag-api bash

# Inspect container
docker inspect rag-api

# Stop container
docker stop rag-api

# Start container
docker start rag-api

# Remove container
docker rm rag-api

# View resource usage
docker stats rag-api
```

### Image Management

```bash
# List images
docker images

# Tag image
docker tag rag-api:latest myregistry/rag-api:1.0

# Push to registry
docker push myregistry/rag-api:1.0

# Remove image
docker rmi rag-api:latest
```

---

## Volumes & Persistence

### Data Volume

The `./data` directory contains:
- `raw_docs/` - Uploaded documents
- `faiss_index/` - Vector indices

### Volume Mounts in docker-compose.yml

```yaml
volumes:
  - ./data:/app/data           # Persist data
  - ./app:/app/app             # Mount source (dev only)
```

### Manual Volume Management

```bash
# Create named volume
docker volume create rag-data

# List volumes
docker volume ls

# Inspect volume
docker volume inspect rag-data

# Remove volume
docker volume rm rag-data

# Remove unused volumes
docker volume prune
```

### Backup Data

```bash
# Backup data directory
tar -czf backup-data.tar.gz data/

# Restore data
tar -xzf backup-data.tar.gz

# Copy from container
docker cp rag-api:/app/data ./data-backup
```

---

## Environment Variables

### Set in docker-compose.yml

```yaml
environment:
  - HF_TOKEN=${HF_TOKEN}
  - CHUNK_SIZE=500
  - CHUNK_OVERLAP=100
  - VECTOR_DIMENSION=384
  - EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
```

### Using .env File

Create `.env` file:
```env
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx
CHUNK_SIZE=500
CHUNK_OVERLAP=100
```

Load from file:
```bash
docker-compose up --env-file .env
```

### Override at Runtime

```bash
docker-compose run -e HF_TOKEN=new_token rag-api
```

---

## Networking

### Port Mapping

Default: `8000:8000` (container:host)

Change in docker-compose.yml:
```yaml
ports:
  - "9000:8000"  # Host:8000 → Container:9000
```

### Custom Network

```bash
# Create network
docker network create rag-network

# Connect container
docker run --network rag-network ...

# List networks
docker network ls

# Inspect network
docker network inspect rag-network
```

### DNS Resolution

**Within network:**
- Service name: `rag-api`
- Hostname: `rag-api:8000`

**From host:**
- Localhost: `http://localhost:8000`

---

## Resource Limits

### In docker-compose.yml

```yaml
deploy:
  resources:
    limits:
      cpus: "2"
      memory: 4G
    reservations:
      cpus: "1"
      memory: 2G
```

### Monitor Usage

```bash
# Real-time stats
docker stats rag-api

# Historical data
docker stats --no-stream
```

### Performance Tuning

- **CPU:** Increase for faster LLM inference
- **Memory:** Minimum 2GB, recommended 4GB+
- **Disk:** At least 5GB for models + indices

---

## Troubleshooting

### Container Won't Start

```bash
# View logs
docker logs rag-api

# Check container status
docker ps -a

# Inspect container
docker inspect rag-api

# Rebuild
docker-compose build --no-cache
docker-compose up
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
docker-compose -f docker-compose.yml -p 8001:8000 up
```

### No Space Left on Device

```bash
# Clean up unused images
docker image prune

# Clean up unused containers
docker container prune

# Clean up everything
docker system prune

# Show disk usage
docker system df
```

### HF_TOKEN Not Found

```bash
# Verify environment variable
docker-compose exec rag-api env | grep HF_TOKEN

# Check .env file
cat .env

# Pass directly
HF_TOKEN=your_token docker-compose up
```

### Slow Performance

```bash
# Check resource allocation
docker stats rag-api

# Increase limits in docker-compose.yml
deploy:
  resources:
    limits:
      cpus: "4"
      memory: 8G

# Rebuild and restart
docker-compose up --build -d
```

### Data Not Persisting

```bash
# Verify volume mount
docker inspect rag-api | grep -A 5 Mounts

# Check data directory
ls -la data/

# Verify path is correct in docker-compose.yml
volumes:
  - ./data:/app/data
```

---

## Production Deployment

### Image Size Optimization

Current: ~1.2GB (Python slim + dependencies)

Reduce with:
- Alpine base image (but slower with numpy/pytorch)
- Multi-stage build (already implemented)
- Remove build dependencies

### Registry Deployment

```bash
# Build and tag
docker build -t myregistry/rag-api:1.0 .

# Push to registry
docker login myregistry
docker push myregistry/rag-api:1.0

# Pull and run
docker run myregistry/rag-api:1.0
```

### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy service
docker service create \
  --name rag-api \
  -p 8000:8000 \
  --constraint node.role==manager \
  rag-api:latest
```

### Kubernetes (Helm)

Create `helm-values.yaml`:
```yaml
image:
  repository: rag-api
  tag: latest
replicaCount: 3
resources:
  limits:
    memory: 4Gi
    cpu: "2"
```

Deploy:
```bash
helm install rag-api ./chart -f helm-values.yaml
```

### Health Checks

```bash
# Docker built-in health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Kubernetes liveness probe
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 40
  periodSeconds: 30
```

### Logging

**Docker logging drivers:**
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

**Centralized logging:**
```bash
# Send logs to syslog
docker logs --driver syslog rag-api

# Stream to file
docker logs rag-api > app.log 2>&1
```

### Scaling

**Multiple instances with load balancer:**
```yaml
version: '3.8'
services:
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf

  rag-api-1:
    build: .
    environment:
      - HF_TOKEN=${HF_TOKEN}

  rag-api-2:
    build: .
    environment:
      - HF_TOKEN=${HF_TOKEN}

  rag-api-3:
    build: .
    environment:
      - HF_TOKEN=${HF_TOKEN}
```

---

## Best Practices

1. ✅ Use `.dockerignore` to exclude unnecessary files
2. ✅ Use multi-stage builds for smaller images
3. ✅ Set resource limits
4. ✅ Use health checks
5. ✅ Mount volumes for persistence
6. ✅ Use specific versions (not latest)
7. ✅ Keep images lean and secure
8. ✅ Don't run as root (consider USER directive)
9. ✅ Use docker-compose for local development
10. ✅ Use secrets manager for sensitive data in production

---

## References

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Hub](https://hub.docker.com/)

---

Last updated: January 19, 2026
