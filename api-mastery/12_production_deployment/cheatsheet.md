# ⚡ Cheatsheet: API Production Deployment

---

## Learning Priority

**Must Learn** — needed for any real deployment:
Dockerfile for FastAPI · Gunicorn + Uvicorn workers · environment variable management · health check endpoint

**Should Learn** — comes up in backend interviews and infra roles:
docker-compose for local dev · K8s deployment skeleton · readiness vs liveness probes

**Good to Know** — useful when you own the infra:
Multi-stage Docker builds · resource limits in K8s · rolling update strategy

**Reference** — look up syntax when needed:
Helm chart structure · K8s HPA config · Nginx ingress annotations

---

## Dockerfile for FastAPI

```dockerfile
# Multi-stage build — keeps final image lean
FROM python:3.11-slim AS builder

WORKDIR /app

# Copy and install dependencies first (layer cache optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# --- Final stage ---
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["gunicorn", "main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "60", \
     "--access-logfile", "-"]
```

---

## Gunicorn + Uvicorn Command Flags

```bash
gunicorn main:app \
  --workers 4 \                    # CPU cores * 2 + 1 is a common starting point
  --worker-class uvicorn.workers.UvicornWorker \  # async workers for FastAPI
  --bind 0.0.0.0:8000 \           # bind to all interfaces inside container
  --timeout 60 \                   # worker timeout seconds (kill if no response)
  --graceful-timeout 30 \          # seconds to wait for workers to finish on shutdown
  --keep-alive 5 \                 # seconds to wait for next request on keep-alive
  --max-requests 1000 \            # restart worker after N requests (prevents memory leaks)
  --max-requests-jitter 100 \      # randomize restart to avoid thundering herd
  --access-logfile - \             # log to stdout
  --error-logfile - \              # log errors to stdout
  --log-level info
```

| Flag | Purpose | Production Default |
|------|---------|-------------------|
| `--workers` | Parallel worker processes | `(2 * CPU) + 1` |
| `--worker-class` | Worker type | `uvicorn.workers.UvicornWorker` for async |
| `--timeout` | Kill unresponsive worker | 60–120s |
| `--max-requests` | Recycle worker to prevent leaks | 500–2000 |
| `--preload` | Load app before forking workers | Saves memory, breaks some async code |

---

## docker-compose (Local Dev + Testing)

```yaml
version: "3.9"

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/appdb
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}          # loaded from .env file
      - ENVIRONMENT=development
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - .:/app                            # mount code for hot reload in dev
    command: uvicorn main:app --reload --host 0.0.0.0 --port 8000

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: appdb
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d appdb"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  pgdata:
```

---

## Kubernetes Deployment Skeleton

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: production
  labels:
    app: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1          # allow 1 extra pod during rollout
      maxUnavailable: 0    # never take a pod down before a new one is ready
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: your-registry/api:v1.2.3   # always pin a version tag, never 'latest'
          ports:
            - containerPort: 8000
          envFrom:
            - secretRef:
                name: api-secrets           # K8s Secret for sensitive values
            - configMapRef:
                name: api-config            # K8s ConfigMap for non-sensitive config
          resources:
            requests:
              cpu: "250m"
              memory: "256Mi"
            limits:
              cpu: "1000m"
              memory: "512Mi"
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
            failureThreshold: 3
          livenessProbe:
            httpGet:
              path: /health/live
              port: 8000
            initialDelaySeconds: 15
            periodSeconds: 30
            failureThreshold: 3
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 5"]  # drain connections before shutdown
      terminationGracePeriodSeconds: 60
```

---

## Health Check Endpoint Pattern

```python
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
import asyncpg
import redis.asyncio as aioredis
import time

app = FastAPI()
START_TIME = time.time()

@app.get("/health/live", status_code=200)
async def liveness():
    """K8s liveness — is the process alive? Never check dependencies here."""
    return {"status": "alive"}

@app.get("/health/ready", status_code=200)
async def readiness():
    """K8s readiness — can the pod accept traffic? Check all dependencies."""
    checks = {}
    ok = True

    # Check DB
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.fetchval("SELECT 1")
        await conn.close()
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"
        ok = False

    # Check Redis
    try:
        r = await aioredis.from_url(REDIS_URL)
        await r.ping()
        await r.close()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {e}"
        ok = False

    status_code = status.HTTP_200_OK if ok else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=status_code, content={"status": "ready" if ok else "degraded", "checks": checks})

@app.get("/health/info")
async def info():
    """Optional: version and uptime info."""
    return {
        "version": "1.2.3",
        "uptime_seconds": int(time.time() - START_TIME),
        "environment": ENVIRONMENT
    }
```

---

## Environment Variable Management

```python
# settings.py — Pydantic BaseSettings
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Required — will raise at startup if missing
    database_url: str
    secret_key: str

    # Optional with defaults
    environment: str = "development"
    debug: bool = False
    log_level: str = "info"
    cors_origins: list[str] = ["http://localhost:3000"]
    max_upload_size_mb: int = 10

    class Config:
        env_file = ".env"           # load from .env in development
        env_file_encoding = "utf-8"
        case_sensitive = False      # DATABASE_URL and database_url both work

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Usage
from fastapi import Depends

@app.get("/config-test")
async def test(settings: Settings = Depends(get_settings)):
    return {"env": settings.environment}
```

```bash
# .env (development only — never commit to git)
DATABASE_URL=postgresql://user:pass@localhost:5432/appdb
SECRET_KEY=dev-secret-key-change-in-production
ENVIRONMENT=development

# Production: inject via K8s Secrets or cloud secrets manager
# Never hardcode secrets in Dockerfile or docker-compose.yaml
```

---

## When to Use / Avoid

| Pattern | Use When | Avoid When |
|---------|----------|------------|
| Gunicorn + Uvicorn workers | CPU-bound + async mixed workload | Pure async with no CPU-bound work (Uvicorn alone is fine) |
| Multi-stage Docker build | Production images (keep them small) | Quick local dev iteration |
| Readiness probe (K8s) | All services — controls traffic routing | Never skip — causes 502s during deploys |
| Liveness probe (K8s) | Detecting deadlocks / hung processes | Don't check DB — K8s will restart healthy pods |
| `--preload` in Gunicorn | Shared model loading, memory saving | Apps using `asyncio.run()` at module level |
| K8s ConfigMap | Non-sensitive config (feature flags, log level) | Secrets (DB passwords, API keys — use K8s Secret) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← API Security](../11_api_security_production/cheatsheet.md) &nbsp;|&nbsp; **Next:** [GraphQL →](../13_graphql/cheatsheet.md)

**Related Topics:** [API Security](../11_api_security_production/) · [API Gateway](../15_api_gateway/) · [OpenTelemetry](../19_opentelemetry/)
