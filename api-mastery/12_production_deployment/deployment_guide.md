# Production Deployment for FastAPI

## From "It Works on My Machine" to Production

Your FastAPI app runs perfectly with `uvicorn main:app --reload`. One worker, your
laptop's CPU, your local database, no real traffic. You ship it, someone posts it on
Reddit, ten thousand people hit it simultaneously, and it falls over.

This module is about the gap between "it works" and "it holds up." Production
deployment is not an afterthought. It's a set of decisions — containers, workers,
configuration, health checks, orchestration, monitoring — that determine whether your
API survives contact with real users.

---

## 1. Dockerizing FastAPI

Docker gives you a portable, reproducible runtime. The same container that runs on
your MacBook runs identically on a Linux server in AWS. No more "it worked in dev
but not in prod" caused by library version differences or OS-level quirks.

### The Dockerfile

```dockerfile
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy and install dependencies first — before copying source code.
# This is the layer caching trick: if your requirements.txt hasn't changed,
# Docker reuses the cached pip install layer. Only copy source when it changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Don't run as root — create a non-root user for security
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Gunicorn with uvicorn workers: the production-grade combination.
# gunicorn manages worker processes; uvicorn handles async I/O within each.
CMD ["gunicorn", "main:app", \
     "-w", "4", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--keepalive", "5", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

**Why `python:3.12-slim` and not `python:3.12`?**

The full image includes build tools, documentation, and other packages you don't need
at runtime. `slim` is ~50MB vs ~350MB. Smaller images pull faster in CI/CD, start
faster in Kubernetes, and have a smaller attack surface (fewer packages that could
have vulnerabilities).

**Why Gunicorn + UvicornWorker?**

`uvicorn main:app` runs a single async worker — fine for development, insufficient for
production. Gunicorn is a mature process manager that spawns and monitors multiple
worker processes. `UvicornWorker` tells Gunicorn to run each worker as an async uvicorn
process, giving you multi-process parallelism with async I/O inside each process.

### .dockerignore

Keep the image clean. Create a `.dockerignore` alongside your Dockerfile:

```
.git
.gitignore
__pycache__
*.pyc
*.pyo
.pytest_cache
.env
.env.*
*.egg-info
dist/
build/
.venv/
venv/
node_modules/
tests/
docs/
*.md
```

Never let `.env` files into the image — they contain secrets. Never include `.git` —
it bloats the image with your full commit history.

### Docker Compose for Local Development

For local development, you want the full stack: API, database, Redis. Docker Compose
manages all of it:

```yaml
# docker-compose.yml
version: "3.8"

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=false
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      # For development only: mount source code so changes reflect without rebuild
      - .:/app
    command: uvicorn main:app --reload --host 0.0.0.0 --port 8000

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

Notice the `depends_on` with `condition: service_healthy` — the API container won't
start until Postgres passes its health check. Without this, your API starts before the
database is ready, fails to connect, and crashes. The health check prevents this race
condition.

To bring the whole stack up: `docker compose up`. To rebuild after code changes:
`docker compose up --build`.

---

## 2. Environment Configuration with Pydantic Settings

Hard-coding configuration is how secrets end up in git. The correct pattern: read
all configuration from environment variables. Pydantic Settings makes this clean:

```python
# config.py
from pydantic_settings import BaseSettings  # pip install pydantic-settings
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    # Required — will raise an error at startup if not set
    database_url: str
    secret_key: str

    # Optional with defaults
    debug: bool = False
    log_level: str = "INFO"
    allowed_hosts: List[str] = ["*"]
    cors_origins: List[str] = []

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Token settings
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    # Performance
    max_connections: int = 10

    class Config:
        env_file = ".env"          # read from .env file in development
        env_file_encoding = "utf-8"
        case_sensitive = False     # DATABASE_URL and database_url are the same

# Cached singleton — Settings is expensive to create; only do it once
@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Usage throughout the app
settings = get_settings()
```

In your `.env` file (never committed to git):

```bash
# .env — local development only
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=true
LOG_LEVEL=DEBUG
```

In production, these are set as environment variables in your deployment platform —
not from a file. Docker Compose reads `${SECRET_KEY}` from your local shell
environment. Kubernetes uses Secrets. AWS uses SSM Parameter Store or Secrets Manager.

Using `@lru_cache()` means the settings object is created once at startup. If
`DATABASE_URL` is missing, the app fails immediately with a clear error — not three
requests in when the first DB query runs.

---

## 3. Production Uvicorn + Gunicorn Setup

### How Many Workers?

The rule of thumb: **2 × CPU cores + 1**

```bash
# Determine number of CPUs on the server
nproc

# Start with 2x + 1 workers
# e.g., 4 CPU cores → 9 workers
gunicorn main:app -w 9 -k uvicorn.workers.UvicornWorker
```

This formula accounts for the fact that async workers spend time waiting on I/O
(database queries, HTTP calls, file reads). While one coroutine waits, the worker
serves another request. The `+1` handles the edge case where all workers are CPU-bound.

For purely CPU-bound work (image processing, heavy computation), reduce workers and
consider offloading to a task queue (Celery, RQ) instead.

### Full Production Gunicorn Configuration

```python
# gunicorn.conf.py
import multiprocessing

# Worker count
workers = multiprocessing.cpu_count() * 2 + 1

# Async worker class
worker_class = "uvicorn.workers.UvicornWorker"

# Network
bind = "0.0.0.0:8000"

# Timeouts
timeout = 120          # worker timeout — kill worker if request takes > 2 min
keepalive = 5          # keep TCP connection alive for 5 seconds after response
graceful_timeout = 30  # seconds to wait for in-flight requests on shutdown

# Worker lifecycle — restart workers after N requests to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50  # randomize so workers don't all restart simultaneously

# Logging
accesslog = "-"         # log to stdout
errorlog = "-"          # log to stdout
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
```

Start gunicorn with the config file:

```bash
gunicorn main:app -c gunicorn.conf.py
```

### The Dockerfile CMD with the config file

```dockerfile
CMD ["gunicorn", "main:app", "-c", "gunicorn.conf.py"]
```

### Memory and CPU Limits in Docker

Set resource limits so a runaway process doesn't consume everything on the host:

```yaml
# docker-compose.yml (production variant)
services:
  api:
    build: .
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: "512M"
        reservations:
          cpus: "0.5"
          memory: "256M"
```

---

## 4. Health Checks

Every production deployment needs a health check endpoint. Load balancers use it to
decide whether to route traffic to a container. Kubernetes uses it to decide whether
to restart a pod. Monitoring systems use it to page you at 2am.

### Basic Health Check

```python
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

app = FastAPI()

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    health = {"status": "healthy", "checks": {}}

    # Check database connectivity
    try:
        db.execute(text("SELECT 1"))
        health["checks"]["database"] = "ok"
    except Exception as e:
        health["status"] = "unhealthy"
        health["checks"]["database"] = f"error: {str(e)}"

    # Check Redis if you use it
    try:
        import redis
        r = redis.from_url(settings.redis_url)
        r.ping()
        health["checks"]["redis"] = "ok"
    except Exception as e:
        health["status"] = "unhealthy"
        health["checks"]["redis"] = f"error: {str(e)}"

    status_code = 200 if health["status"] == "healthy" else 503
    return JSONResponse(status_code=status_code, content=health)

# Separate liveness endpoint — no DB check, just "am I running?"
# Kubernetes uses this to decide whether to restart the container.
@app.get("/health/live")
async def liveness():
    return {"status": "alive"}

# Readiness endpoint — "am I ready to serve traffic?"
# Kubernetes uses this to decide whether to send traffic.
@app.get("/health/ready")
async def readiness(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "not ready"})
```

**Liveness vs Readiness** — a common Kubernetes distinction:

- **Liveness**: Is the process alive and not deadlocked? If this fails, Kubernetes
  restarts the container. Keep it fast and simple — don't check external dependencies.
- **Readiness**: Is the container ready to serve traffic? If this fails, Kubernetes
  stops routing requests to it (but doesn't restart it). Check DB connectivity here.

A container that's alive but not ready (e.g., still running database migrations) won't
receive traffic until it reports ready. This prevents 503 errors during rolling deploys.

---

## 5. Kubernetes Deployment

For large-scale deployments, Kubernetes manages your containers across a cluster of
servers — scaling them, restarting failed pods, rolling out updates with zero downtime.

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
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
      maxSurge: 1        # one extra pod during updates
      maxUnavailable: 0  # never take a pod down before a new one is ready
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: my-api:latest
          ports:
            - containerPort: 8000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: api-secrets
                  key: database-url
            - name: SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: api-secrets
                  key: secret-key
          # Liveness: restart if unhealthy
          livenessProbe:
            httpGet:
              path: /health/live
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 10
            failureThreshold: 3
          # Readiness: stop traffic if not ready
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
            failureThreshold: 3
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: api
spec:
  selector:
    app: api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: ClusterIP
```

The `RollingUpdate` strategy with `maxUnavailable: 0` means Kubernetes starts a new
pod and waits for its readiness probe to pass before terminating an old pod. Your
users experience zero downtime during deployments.

---

## 6. CI/CD Pipeline with GitHub Actions

Automate the full path from code push to production:

```yaml
# .github/workflows/deploy.yml
name: Deploy API

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: testdb
          POSTGRES_USER: user
          POSTGRES_PASSWORD: pass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest --cov=. --cov-report=xml
        env:
          DATABASE_URL: postgresql://user:pass@localhost:5432/testdb
          SECRET_KEY: test-secret-key
      - uses: codecov/codecov-action@v4

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Log in to container registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:${{ github.sha }}
            ghcr.io/${{ github.repository }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Set kubeconfig
        run: echo "${{ secrets.KUBECONFIG }}" > kubeconfig.yml

      - name: Deploy to Kubernetes
        run: |
          kubectl --kubeconfig kubeconfig.yml set image \
            deployment/api \
            api=ghcr.io/${{ github.repository }}:${{ github.sha }}
          kubectl --kubeconfig kubeconfig.yml rollout status deployment/api
```

Three jobs, in sequence:

1. **test** — Run the test suite against a real Postgres instance. If tests fail, nothing
   deploys.
2. **build-and-push** — Build the Docker image, push to the container registry with the
   commit SHA as the tag. The SHA tag makes every image uniquely traceable to the exact
   commit.
3. **deploy** — Update the Kubernetes deployment to use the new image. `rollout status`
   waits until the deployment completes successfully before the pipeline marks as green.

If any job fails, the pipeline stops and the previous version keeps running.

---

## 7. Monitoring in Production

Shipping is not the end. You need to know whether your API is healthy, fast, and
handling errors correctly — not from users complaining, but from your own instrumentation.

### Prometheus Metrics

`prometheus-fastapi-instrumentator` adds metrics to your API with three lines:

```python
# main.py
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Expose Prometheus metrics at /metrics
Instrumentator().instrument(app).expose(app)
```

This automatically tracks:
- `http_requests_total` — request count by method, path, and status code
- `http_request_duration_seconds` — response time histogram
- `http_requests_in_progress` — concurrent requests in flight

Prometheus scrapes your `/metrics` endpoint on a schedule (typically every 15s). You
can then query these metrics in Grafana to build dashboards showing requests per second,
p99 latency, and error rates.

### Structured JSON Logging

Plain text logs don't scale. When you're searching through millions of log lines for
a specific request ID, you want structured data you can query. Use `structlog` or
configure Python's `logging` to output JSON:

```python
# logging_config.py
import logging
import json
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        # Include any extra fields passed to the logger
        for key, value in record.__dict__.items():
            if key not in ("args", "exc_info", "exc_text", "msg",
                           "message", "levelname", "name", "created",
                           "filename", "funcName", "levelno", "lineno",
                           "module", "msecs", "pathname", "process",
                           "processName", "relativeCreated", "stack_info",
                           "thread", "threadName"):
                log_entry[key] = value
        return json.dumps(log_entry)

def setup_logging(log_level: str = "INFO"):
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logging.basicConfig(level=getattr(logging, log_level), handlers=[handler])
```

With JSON logging, a single log line looks like:

```json
{"timestamp": "2024-03-08T14:30:00Z", "level": "ERROR", "logger": "app.api",
 "message": "Database connection failed", "request_id": "abc123", "user_id": 42}
```

This is queryable in Datadog, CloudWatch, Elasticsearch, or any log aggregation system.
You can filter by `user_id`, group by `request_id`, alert on `level=ERROR`.

### Request ID Middleware

Add a unique ID to every request so you can trace a single request through all your
logs:

```python
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

app.add_middleware(RequestIDMiddleware)
```

Pass `request.state.request_id` into every log call. Now when a user reports an issue
and gives you the `X-Request-ID` from their response headers, you can find every log
line for that exact request.

### Error Tracking with Sentry

Sentry catches unhandled exceptions, groups them by type, and alerts you:

```python
# main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn=settings.sentry_dsn,  # from environment variable
    integrations=[
        FastApiIntegration(),
        SqlalchemyIntegration(),
    ],
    traces_sample_rate=0.1,   # sample 10% of requests for performance tracing
    environment=settings.environment,  # "production", "staging"
    release=settings.git_sha,  # tag errors to exact code version
)
```

Add `sentry_dsn: str | None = None` to your `Settings` class. In production, set it.
In development, leave it unset — Sentry only activates when the DSN is provided.

---

## Production Deployment Checklist

Before you ship:

```
Docker:
  [ ] Dockerfile uses slim base image
  [ ] Non-root user in Dockerfile (not running as root)
  [ ] .dockerignore excludes .env, .git, test files
  [ ] Layer ordering: dependencies before source code
  [ ] No secrets baked into the image

Configuration:
  [ ] All config from environment variables, not hard-coded
  [ ] pydantic-settings validates required vars at startup
  [ ] .env file exists locally, never committed to git
  [ ] Secrets managed via Kubernetes Secrets or secret manager

Workers:
  [ ] Gunicorn + UvicornWorker (not bare uvicorn) in production
  [ ] Worker count = 2 × CPU + 1
  [ ] max_requests set to prevent memory leaks
  [ ] Timeout configured

Health Checks:
  [ ] /health endpoint returns 200 when healthy, 503 when not
  [ ] Separate /health/live and /health/ready for Kubernetes
  [ ] Health check tests DB and Redis connectivity

Kubernetes:
  [ ] RollingUpdate with maxUnavailable: 0 for zero-downtime deploys
  [ ] Liveness and readiness probes configured
  [ ] Resource requests and limits set
  [ ] Secrets stored in Kubernetes Secrets, not ConfigMaps

CI/CD:
  [ ] Tests run before every deploy
  [ ] Docker image tagged with git SHA (not just "latest")
  [ ] Deploy step waits for rollout completion
  [ ] Secrets in GitHub Actions secrets, not in workflow file

Monitoring:
  [ ] Prometheus metrics exposed
  [ ] Structured JSON logging
  [ ] Request IDs on all responses
  [ ] Sentry (or equivalent) for error tracking
  [ ] Alerts configured for error rate and p99 latency
```

---

## Summary

```
Docker:
  python:3.12-slim  →  small, production-appropriate base image
  Gunicorn + UvicornWorker  →  multi-process + async per process
  Non-root user, .dockerignore, layer caching for requirements.txt

Configuration:
  pydantic-settings reads from env vars + .env file
  Required vars missing at startup → fail fast with clear error
  Never bake secrets into images

Workers:
  Count = 2 × CPU cores + 1
  gunicorn.conf.py: timeout, keepalive, max_requests, log to stdout
  max_requests + jitter prevents coordinated worker restarts

Health Checks:
  /health/live → liveness (no DB check) → restart if failing
  /health/ready → readiness (with DB check) → stop traffic if failing
  503 when unhealthy, 200 when healthy

Kubernetes:
  RollingUpdate strategy, maxUnavailable: 0 = zero-downtime deploys
  livenessProbe + readinessProbe on /health/live and /health/ready

CI/CD:
  test → build + push (SHA tag) → deploy → wait for rollout
  Image tag = git SHA = every deploy traceable to exact commit

Monitoring:
  prometheus-fastapi-instrumentator: request count, latency, errors
  JSON structured logging: queryable in any log system
  Request ID middleware: trace one request through all logs
  Sentry: unhandled exception tracking and alerting
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Security in Production](../11_api_security_production/security_hardening.md) &nbsp;|&nbsp; **Next:** [GraphQL →](../13_graphql/graphql_story.md)

**Related Topics:** [Security in Production](../11_api_security_production/security_hardening.md) · [API Performance & Scaling](../09_api_performance_scaling/performance_guide.md) · [OpenTelemetry](../19_opentelemetry/opentelemetry_guide.md) · [GraphQL](../13_graphql/graphql_story.md)
