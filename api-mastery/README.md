# 🔌 API Mastery
> Complete API development from absolute beginner to production-ready.
> Covers API fundamentals, REST, GraphQL, gRPC, **FastAPI mastery**, security, testing, deployment, and real-world architectures.

---

## 🎯 What This Covers

```
Theory + Practice combined:
  ✅ How APIs work (HTTP, request-response, status codes)
  ✅ REST design done right
  ✅ FastAPI — from first endpoint to production
  ✅ Authentication, security, rate limiting
  ✅ Testing, documentation, deployment
  ✅ Real-world: payment APIs, social feeds, ride-sharing
```

**Every stage has working Python/FastAPI code, not just theory.**

---

## 📂 Learning Path

### 🌐 Stage 1–6: API Fundamentals

| # | Topic | What You'll Learn |
|---|-------|-----------------|
| 01 | [What is an API?](./01_what_is_an_api/story.md) | HTTP, request-response, status codes, headers, first Python API call |
| 02 | [HTTP Deep Dive](./02_rest_fundamentals/rest_explained.md) | Roy Fielding's REST, 6 constraints, resources, idempotency, URL patterns |
| 03 | [API Design Principles](./03_rest_best_practices/patterns.md) | Naming, versioning, pagination, error formats, idempotency keys, caching |
| 04 | [Data Formats & Serialization](./04_data_formats/serialization_guide.md) | JSON types, Pydantic validation, XML, binary formats |
| 05 | [Authentication & Authorization](./05_authentication/securing_apis.md) | API keys, OAuth2, JWT, sessions, rate limiting, CORS |
| 06 | [Error Handling & Standards](./06_error_handling_standards/error_guide.md) | Error formats, pagination, filtering, sorting in FastAPI |

---

### ⚡ Stage 7: FastAPI Mastery (all in `07_fastapi/`)

All FastAPI topics are in one folder for easy navigation:

| File | What You'll Learn |
|------|-----------------|
| [FastAPI Fundamentals](./07_fastapi/why_fastapi.md) | ASGI vs WSGI, Starlette, Pydantic, event loop, request lifecycle |
| [FastAPI Basics](./07_fastapi/first_api.md) | First API, path params, query params, request bodies, response models |
| [FastAPI Core Concepts](./07_fastapi/core_guide.md) | Pydantic deep dive, dependency injection, middleware, routers, error handling |
| [FastAPI & Databases](./07_fastapi/database_guide.md) | SQLAlchemy, PostgreSQL, CRUD, Alembic migrations, async DB |
| [FastAPI Advanced](./07_fastapi/advanced_guide.md) | WebSockets, file uploads, streaming, Celery, Redis caching, rate limiting |

---

### 🔧 Stage 8–12: Production APIs

| # | Topic | What You'll Learn |
|---|-------|-----------------|
| 08 | [API Versioning](./08_versioning_standards/versioning_strategy.md) | Breaking vs non-breaking changes, URL vs header versioning, deprecation |
| 09 | [API Performance & Scaling](./09_api_performance_scaling/performance_guide.md) | Caching, N+1 queries, connection pools, horizontal scaling, key metrics |
| 10 | [Testing & Documentation](./10_testing_documentation/testing_apis.md) | Unit tests, FastAPI TestClient, contract testing, OpenAPI docs |
| 11 | [Security in Production](./11_api_security_production/security_hardening.md) | HTTPS, input validation, token security, security headers, audit logs |
| 12 | [Production Deployment](./12_production_deployment/deployment_guide.md) | Docker, Gunicorn/Uvicorn, Kubernetes, CI/CD, monitoring |

---

### 🧩 Stage 13–18: Advanced Protocols & Architecture

| # | Topic | What You'll Learn |
|---|-------|-----------------|
| 13 | [GraphQL](./13_graphql/graphql_story.md) | Schema, queries, mutations, subscriptions, N+1 problem, DataLoader |
| 14 | [gRPC](./14_grpc/grpc_guide.md) | Protocol Buffers, 4 streaming modes, Python client/server |
| 15 | [API Gateway](./15_api_gateway/gateway_patterns.md) | Routing, auth offload, rate limiting, BFF pattern |
| 16 | [API Design Patterns](./16_api_design_patterns/design_guide.md) | Idempotency keys, long-running ops, bulk operations, partial updates |
| 17 | [WebSockets](./17_websockets/realtime_apis.md) | Full-duplex, handshake, use cases, scaling WS connections |
| 18 | [Real-World API Architectures](./18_real_world_apis/architectures.md) | Payment, social media, ride-sharing, SaaS API design |

---

### 🎯 Practice

| # | Topic | Content |
|---|-------|---------|
| 99 | [Interview Master](./99_interview_master/api_questions.md) | Junior → Senior Q&A, API design problems, URL shortener, Stripe-style API |

---

## ⚡ Quick Reference

### HTTP Status Codes
```
200 OK               → success, has body
201 Created          → POST created a resource
204 No Content       → success, no body (DELETE)
400 Bad Request      → malformed request
401 Unauthorized     → not authenticated
403 Forbidden        → authenticated but not allowed
404 Not Found        → resource doesn't exist
409 Conflict         → duplicate, version conflict
422 Unprocessable    → validation error
429 Too Many Req.    → rate limited
500 Internal Error   → server bug
503 Unavailable      → server down/overloaded
```

### REST URL Patterns
```
GET    /users              → list
POST   /users              → create
GET    /users/42           → get one
PUT    /users/42           → replace
PATCH  /users/42           → partial update
DELETE /users/42           → delete
GET    /users/42/orders    → nested collection
GET    /orders?status=pending&page=2&limit=20  → filter + paginate
```

### REST vs GraphQL vs gRPC
```
                REST        GraphQL     gRPC
Protocol:       HTTP/1.1    HTTP        HTTP/2
Format:         JSON        JSON        Protobuf
Flexibility:    Fixed       Client-defined  Fixed (schema)
Browser:        Native      Native      gRPC-web only
Best for:       Public APIs Complex UIs Internal services
```

### FastAPI Quick Start
```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

app = FastAPI(title="My API")

class UserCreate(BaseModel):
    name: str
    email: str

@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    return {"id": 1, **user.dict()}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id > 100:
        raise HTTPException(404, "User not found")
    return {"id": user_id, "name": "Alice"}

# Run: uvicorn main:app --reload
# Docs: http://localhost:8000/docs
```

---

## 🔁 Navigation

| | |
|---|---|
| 🚀 Start | [01 — What is an API?](./01_what_is_an_api/story.md) |
| ⚡ FastAPI | [FastAPI Fundamentals](./07_fastapi/why_fastapi.md) |
| 🏭 Deploy | [12 — Production Deployment](./12_production_deployment/deployment_guide.md) |
| 🎯 Practice | [99 — Interview Master](./99_interview_master/api_questions.md) |
| 🏗️ System Design | [../system-design-mastery/](../system-design-mastery/) |
| 🐍 Python | [../python-complete-mastery/](../python-complete-mastery/) |
| 🏠 Root | [../Readme.md](../Readme.md) |
