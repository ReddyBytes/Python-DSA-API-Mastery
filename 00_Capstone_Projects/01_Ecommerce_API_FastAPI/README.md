# Project 01: E-Commerce API in FastAPI

A production-grade REST API for an e-commerce platform — users, products, orders, JWT authentication, background tasks, and Docker deployment.

---

## What You Will Build

A fully functional backend API that a real frontend could connect to:

- User registration and login with hashed passwords and JWT tokens
- Product catalogue with pagination and filtering
- Order placement with inventory checks and transactional writes
- Background task for email confirmation (simulated)
- Full test suite with pytest and TestClient
- Dockerized app + PostgreSQL via docker-compose

---

## Skills Exercised

| Skill | Where it appears |
|-------|-----------------|
| Python OOP | SQLAlchemy models, service layer classes |
| FastAPI routing | All endpoints, dependency injection |
| Pydantic v2 | Request bodies, response schemas, validation |
| SQLAlchemy ORM | Models, sessions, transactions |
| JWT authentication | Login, protected routes via `Depends()` |
| Background tasks | Post-order email simulation |
| pytest + TestClient | Unit tests, integration tests, fixture setup |
| Docker + Compose | Multi-container app with PostgreSQL |
| Logging | Structured request/error logging |
| Rate limiting | SlowAPI integration on sensitive endpoints |

---

## Prerequisites

Before starting, make sure you have covered:

- `python-complete-mastery/05_oops` — classes, inheritance, dunder methods
- `python-complete-mastery/14_type_hints_and_pydantic` — Pydantic models and validators
- `api-mastery/07_fastapi/first_api.md` — first endpoint, path/query params
- `api-mastery/07_fastapi/database_guide.md` — SQLAlchemy with FastAPI
- `api-mastery/05_authentication` — JWT concepts
- `python-complete-mastery/17_testing` — pytest basics

---

## Project Structure

```
01_Ecommerce_API_FastAPI/
├── README.md               ← this file
├── Project_Guide.md        ← step-by-step build instructions
├── Architecture.md         ← system design, ER diagram, API table
└── starter_code/
    └── main.py             ← runnable skeleton to start from
```

---

## Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Language |
| FastAPI | 0.111+ | Web framework |
| SQLAlchemy | 2.0+ | ORM |
| Pydantic | 2.x | Validation |
| python-jose | 3.x | JWT tokens |
| passlib | 1.x | Password hashing |
| PostgreSQL | 15 | Database (via Docker) |
| pytest | 7+ | Testing |
| SlowAPI | latest | Rate limiting |
| Docker + Compose | latest | Containerisation |

---

## How to Run (Finished App)

```bash
# Clone and enter the project
cd 01_Ecommerce_API_FastAPI

# Install dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose passlib pytest httpx slowapi

# Start PostgreSQL + app
docker-compose up --build

# API docs auto-generated at:
# http://localhost:8000/docs   (Swagger)
# http://localhost:8000/redoc  (ReDoc)
```

---

## How to Run (Starter Skeleton)

```bash
cd starter_code
pip install fastapi uvicorn sqlalchemy pydantic python-jose passlib
uvicorn main:app --reload

# Visit http://localhost:8000/docs
```

---

## Build Order

Follow `Project_Guide.md` step by step. Each step is independently runnable — you can commit after each one.

```
Step 1  →  Project layout and pyproject.toml
Step 2  →  SQLAlchemy models
Step 3  →  Pydantic schemas
Step 4  →  Auth (JWT + hashing)
Step 5  →  Product CRUD routes
Step 6  →  Order placement
Step 7  →  Background tasks
Step 8  →  Test suite
Step 9  →  Docker + Compose
Step 10 →  Logging, error handling, rate limiting
```

---

## Navigation

| | |
|---|---|
| Back | [Capstone Projects](../README.md) |
| Build Guide | [Project_Guide.md](./Project_Guide.md) |
| Architecture | [Architecture.md](./Architecture.md) |
| Starter Code | [starter_code/main.py](./starter_code/main.py) |
| Next Project | [02 — Data Pipeline CLI](../02_Data_Pipeline_CLI/README.md) |
