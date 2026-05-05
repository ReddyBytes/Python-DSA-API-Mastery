# Capstone Projects

> Theory tells you how things work. Projects prove you can build them.

These projects are not exercises — they are real systems you would find in production codebases.
Each one is self-contained and deployable. By the end of the series you will have built
an auth system, a real-time chat server, a task queue, a rate limiter, a webhook receiver,
and a full e-commerce API — from scratch, without tutorials.

---

## How This Series Works

Every project has a **difficulty level** that controls how much guidance you get:

```
4 difficulty levels:

  Fully Guided     — Every step: concept → think → hint → answer
                     Use when: first time seeing this type of system

  Partially Guided — Every step: concept → think → answer (no hint)
                     Use when: you know the concept, need to apply it

  Minimal Hints    — Every step: requirements + one hint. Full solution at end.
                     Use when: you understand the domain, need to build confidence

  Build Yourself   — Spec + acceptance criteria only. Full solution at end.
                     Use when: proving to yourself you can do it independently
```

The series is arranged in **cycles of four**. Each cycle follows the same progression:

```
Each 4-project cycle follows the same progression:

  Project N+0  Fully Guided   — learn the pattern
  Project N+1  Partially      — apply with support
  Project N+2  Minimal Hints  — build with minimal help
  Project N+3  Build Yourself — prove independence
```

This is deliberate. The first project in a cycle holds your hand completely. By the fourth,
you are on your own. That gap — between guided and independent — is where confidence is built.

---

## The Learning Path

Projects are grouped by **track** (the domain they belong to) but the difficulty cycle cuts
across tracks. Pick a path below or follow the full sequence.

### Track 1 — Networking Fundamentals

| # | Project | Difficulty | Key Skills | Prerequisites |
|---|---------|------------|------------|---------------|
| 01 | [TCP Socket Chat Server](./01_TCP_Socket_Chat_Server/Project_Guide.md) | 🟢 Fully Guided | socket, threading, broadcast, client-server model | Python functions, threading basics |
| 02 | [WebSocket Real-Time Chat](./02_WebSocket_Realtime_Chat/Project_Guide.md) | 🟡 Partially Guided | websockets, asyncio, HTML client | Project 01, async/await basics |

### Track 2 — CLI & Data Tools

| # | Project | Difficulty | Key Skills | Prerequisites |
|---|---------|------------|------------|---------------|
| 03 | [Data Pipeline CLI](./03_Data_Pipeline_CLI/Project_Guide.md) | 🟠 Minimal Hints | requests, Pydantic, SQLAlchemy, pandas, packaging | File handling, logging, Pydantic |
| 04 | [CLI Tool — devtools](./04_CLI_Tool/Project_Guide.md) | 🟡 Partially Guided | argparse subcommands, configparser, pip packaging | argparse basics, modules |

### Track 3 — Auth & Security

| # | Project | Difficulty | Key Skills | Prerequisites |
|---|---------|------------|------------|---------------|
| 05 | [JWT Auth System](./05_JWT_Auth_System/Project_Guide.md) | 🟠 Minimal Hints | FastAPI, bcrypt, JWT, refresh tokens | FastAPI basics, Pydantic, SQLAlchemy |
| 06 | [Webhook Receiver](./06_Webhook_Receiver/Project_Guide.md) | 🟢 Fully Guided | HMAC signatures, FastAPI, idempotency | Project 05, requests |
| 10 | [OAuth Client — GitHub + Google](./10_OAuth_Client/Project_Guide.md) | 🟢 Fully Guided | OAuth2 Authorization Code Flow, OIDC | Project 05, FastAPI sessions |
| 11 | [OAuth Server](./11_OAuth_Server/Project_Guide.md) | 🟡 Partially Guided | OAuth2 provider, token endpoint, scopes | Project 10 |
| 12 | [Two-Factor Auth / TOTP](./12_2FA_TOTP/Project_Guide.md) | 🟠 Minimal Hints | pyotp, QR codes, TOTP verification | Projects 05 + 10 |
| 13 | [RBAC Permission System](./13_RBAC/Project_Guide.md) | 🔴 Build Yourself | roles, permissions, policy enforcement | All auth projects |

### Track 4 — Infrastructure & Reliability

| # | Project | Difficulty | Key Skills | Prerequisites |
|---|---------|------------|------------|---------------|
| 07 | [Config-Driven Scheduler](./07_Config_Driven_Scheduler/Project_Guide.md) | 🟠 Minimal Hints | APScheduler, PyYAML, signal handling | Functions, threading, logging |
| 08 | [Celery Task Queue](./08_Celery_Task_Queue/Project_Guide.md) | 🔴 Build Yourself | Celery, Redis, retries, task status | FastAPI, Docker, Redis basics |
| 09 | [Rate Limiter Middleware](./09_Rate_Limiter_Middleware/Project_Guide.md) | 🔴 Build Yourself | Redis sorted sets, sliding window, FastAPI middleware | Redis, FastAPI, Docker |

### Track 5 — Full System

| # | Project | Difficulty | Key Skills | Prerequisites |
|---|---------|------------|------------|---------------|
| 14 | [E-Commerce API](./14_Ecommerce_API_FastAPI/Project_Guide.md) | 🔴 Build Yourself | FastAPI, SQLAlchemy, JWT, transactions, pytest, Docker | All previous tracks |

---

## Start Here — Choose Your Path

You do not have to follow the full sequence. Start with the path that matches your goal.

**Path A: Complete Beginner** — start here if you are new to backend development

```
TCP Socket Chat (01)
  → WebSocket Chat (02)
  → Data Pipeline CLI (03)
  → JWT Auth System (05)
  → E-Commerce API (14)

Focus: understand how systems communicate before building them
```

**Path B: Interview Prep** — know Python, need system-building experience

```
JWT Auth System (05)
  → Webhook Receiver (06)
  → Celery Task Queue (08)
  → Rate Limiter Middleware (09)
  → E-Commerce API (14)

Focus: the systems that come up most in backend interviews
```

**Path C: Production Engineer** — want real patterns fast

```
Webhook Receiver (06)
  → Celery Task Queue (08)
  → Config-Driven Scheduler (07)
  → Rate Limiter Middleware (09)
  → OAuth Client (10)
  → E-Commerce API (14)

Focus: the infrastructure patterns used in every production backend
```

---

## Project Quick Reference

| # | Folder | Track | Difficulty | What You Build | Time |
|---|--------|-------|------------|----------------|------|
| 01 | [01_TCP_Socket_Chat_Server](./01_TCP_Socket_Chat_Server/Project_Guide.md) | Networking | 🟢 Guided | Multi-client chat server using raw TCP sockets | 2h |
| 02 | [02_WebSocket_Realtime_Chat](./02_WebSocket_Realtime_Chat/Project_Guide.md) | Networking | 🟡 Partial | Real-time browser chat with WebSockets and asyncio | 4h |
| 03 | [03_Data_Pipeline_CLI](./03_Data_Pipeline_CLI/Project_Guide.md) | CLI & Data | 🟠 Hints | CLI that fetches, validates, transforms, and stores data | 6h |
| 04 | [04_CLI_Tool](./04_CLI_Tool/Project_Guide.md) | CLI & Data | 🟡 Partial | Developer CLI tool with subcommands, config, pip packaging | 4h |
| 05 | [05_JWT_Auth_System](./05_JWT_Auth_System/Project_Guide.md) | Auth & Security | 🟠 Hints | Full JWT auth: register, login, access + refresh tokens | 6h |
| 06 | [06_Webhook_Receiver](./06_Webhook_Receiver/Project_Guide.md) | Auth & Security | 🟢 Guided | Webhook endpoint with HMAC validation and idempotency | 2h |
| 07 | [07_Config_Driven_Scheduler](./07_Config_Driven_Scheduler/Project_Guide.md) | Infrastructure | 🟠 Hints | YAML-configured job scheduler with signal handling | 6h |
| 08 | [08_Celery_Task_Queue](./08_Celery_Task_Queue/Project_Guide.md) | Infrastructure | 🔴 Self | Async task queue with Celery, Redis, retries, monitoring | 8h |
| 09 | [09_Rate_Limiter_Middleware](./09_Rate_Limiter_Middleware/Project_Guide.md) | Infrastructure | 🔴 Self | Sliding window rate limiter as FastAPI middleware via Redis | 8h |
| 10 | [10_OAuth_Client](./10_OAuth_Client/Project_Guide.md) | Auth & Security | 🟢 Guided | OAuth2 Authorization Code flow with GitHub and Google | 2h |
| 11 | [11_OAuth_Server](./11_OAuth_Server/Project_Guide.md) | Auth & Security | 🟡 Partial | Build your own OAuth2 provider with token endpoints | 4h |
| 12 | [12_2FA_TOTP](./12_2FA_TOTP/Project_Guide.md) | Auth & Security | 🟠 Hints | TOTP-based 2FA with QR code enrollment and verification | 6h |
| 13 | [13_RBAC](./13_RBAC/Project_Guide.md) | Auth & Security | 🔴 Self | Role-based access control with policy enforcement | 8h |
| 14 | [14_Ecommerce_API_FastAPI](./14_Ecommerce_API_FastAPI/Project_Guide.md) | Full System | 🔴 Self | Production REST API with auth, cart, orders, payments | 8h |

---

## How Projects Connect

The projects are not isolated. Each one builds vocabulary and muscle memory that the next one
assumes. The connections below show the explicit dependencies.

```
TCP Sockets (01) ──────────────────────► WebSocket Chat (02)
                                          "same idea, better protocol"


JWT Auth (05) ──────────────────────────► Webhook Receiver (06)
                                          "HMAC is JWT's cousin"
                    │
                    └───────────────────► OAuth Client (10)
                                          "OAuth gives out JWTs"
                    │
                    └───────────────────► E-Commerce API (14)
                                          "auth is one layer of many"


Celery Task Queue (08) ─────────────────► E-Commerce API (14)
                                          "background email task"


Rate Limiter (09) ──────────────────────► E-Commerce API (14)
                                          "login endpoint protection"


Config Scheduler (07) ──────────────────► Celery Task Queue (08)
                                          "scheduler triggers Celery tasks"


OAuth Client (10) ──────────────────────► OAuth Server (11)
                                          "understand both sides"


OAuth Server (11) + JWT Auth (05) ──────► Two-Factor Auth (12)
                                          "add a second factor on top"


JWT + OAuth + 2FA (05/10/12) ───────────► RBAC System (13)
                                          "permissions wrap every auth layer"
```

---

## What You Can Build After Each Track

**Track 1 complete** — You understand how every networked app communicates at the socket level.
When someone says "the WebSocket disconnected" or "the TCP buffer filled up" you know exactly what
happened and why.

**Track 2 complete** — You can build and ship professional CLI tools that others can `pip install`.
Data ingestion, transformation, and storage pipelines are no longer black boxes.

**Track 3 complete** — You can implement any auth system a company uses: JWT, OAuth2, 2FA, RBAC.
You understand the security guarantees each one provides and where each one breaks.

**Track 4 complete** — You can build the infrastructure layer: async task queues, cron-style
schedulers, and request rate limiting. These are the systems that keep production services alive
under load.

**Track 5 complete** — You can design and build a production-grade REST API from scratch: data
model, auth, background jobs, rate limiting, tests, and Docker deployment. No tutorial needed.

---

## Ground Rules

```
1. Try before opening the answer — the struggle is where learning happens

2. Build each project to completion before moving on — partial builds don't count

3. If you get stuck: read the theory module first, then the hint, then the answer

4. Extend at least 2 projects with the "Extend It" ideas — that's where real learning is

5. After completing a track, revisit the first project in that track — you will see it differently
```

The answer is always there when you need it. The goal is not to avoid looking — it is to build the
habit of attempting first. Every minute you spend stuck before looking at the answer is a minute
your brain is forming the pattern. That cannot happen if you skip straight to the solution.

---

## Navigation

| Project | Guide | Status |
|---------|-------|--------|
| 01 — TCP Socket Chat Server | [Project_Guide.md](./01_TCP_Socket_Chat_Server/Project_Guide.md) | Available |
| 02 — WebSocket Real-Time Chat | [Project_Guide.md](./02_WebSocket_Realtime_Chat/Project_Guide.md) | Available |
| 03 — Data Pipeline CLI | [Project_Guide.md](./03_Data_Pipeline_CLI/Project_Guide.md) | Available |
| 04 — CLI Tool (devtools) | [Project_Guide.md](./04_CLI_Tool/Project_Guide.md) | Available |
| 05 — JWT Auth System | [Project_Guide.md](./05_JWT_Auth_System/Project_Guide.md) | Available |
| 06 — Webhook Receiver | [Project_Guide.md](./06_Webhook_Receiver/Project_Guide.md) | Available |
| 07 — Config-Driven Scheduler | [Project_Guide.md](./07_Config_Driven_Scheduler/Project_Guide.md) | Available |
| 08 — Celery Task Queue | [Project_Guide.md](./08_Celery_Task_Queue/Project_Guide.md) | Available |
| 09 — Rate Limiter Middleware | [Project_Guide.md](./09_Rate_Limiter_Middleware/Project_Guide.md) | Available |
| 10 — OAuth Client | [Project_Guide.md](./10_OAuth_Client/Project_Guide.md) | Available |
| 11 — OAuth Server | [Project_Guide.md](./11_OAuth_Server/Project_Guide.md) | Available |
| 12 — Two-Factor Auth / TOTP | [Project_Guide.md](./12_2FA_TOTP/Project_Guide.md) | Available |
| 13 — RBAC Permission System | [Project_Guide.md](./13_RBAC/Project_Guide.md) | Available |
| 14 — E-Commerce API | [Project_Guide.md](./14_Ecommerce_API_FastAPI/Project_Guide.md) | Available |

---

Back to [Python-DSA-API-Mastery](../README.md)
