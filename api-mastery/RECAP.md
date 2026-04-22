# API Mastery — Topic Recap

> One-line summary of every module. Use this to quickly find which module covers the concept you need.

---

## API Foundations

| Module | Topics Covered |
|--------|----------------|
| 01 — What is an API? | HTTP request/response cycle, client-server model, API types overview (REST/GraphQL/gRPC), HTTP methods and status codes |
| 02 — REST Fundamentals | Fielding's 6 REST constraints, statelessness, resource modeling (nouns not verbs), HTTP verb semantics, idempotency, HATEOAS |
| 03 — REST Best Practices | URL naming conventions (lowercase/hyphens/plural), pagination (offset vs cursor), filtering and sorting safety, caching headers (ETag/Cache-Control), idempotency keys |
| 04 — Data Formats & Serialization | JSON types and limitations, ISO 8601 dates, Decimal-as-string, Pydantic validation, Protocol Buffers, MessagePack, binary format trade-offs |

---

## Authentication & Security

| Module | Topics Covered |
|--------|----------------|
| 05 — Authentication | API keys, JWT structure/validation/refresh, OAuth2 flows (authorization code, client credentials), rate limiting algorithms, CORS, input validation (SQL injection/Pydantic), RS256 vs HS256 |
| 06 — Error Handling Standards | Consistent error envelope structure (code/message/details), HTTP status code selection, field-level validation errors, pagination patterns, filtering/sorting with whitelists, RFC 7807 ProblemDetails |
| 11 — API Security in Production | HTTPS/TLS enforcement and termination layers, token rotation and revocation, security headers (HSTS/CSP/X-Frame-Options), CORS origin validation, advanced rate limiting (per-user/per-endpoint), audit logging, file upload validation |

---

## FastAPI

| Module | Topics Covered |
|--------|----------------|
| 07a — Why FastAPI | FastAPI vs Flask vs Django REST comparison, automatic docs, Pydantic-driven validation, async-first design |
| 07b — FastAPI First API | Route definition, path/query parameters, request bodies, status codes, auto-generated OpenAPI docs at `/docs` |
| 07c — FastAPI Core Concepts | Pydantic models (Field/validators/nested), dependency injection, middleware, APIRouter (prefixes/tags), background tasks, custom exception handlers |
| 07d — FastAPI Advanced Features | WebSocket endpoints, file uploads/streaming responses, large-scale async patterns, background jobs, production-ready features |
| 07e — FastAPI + Database | SQLAlchemy integration, async sessions, yield-pattern dependency for DB connections |

---

## Advanced API Patterns

| Module | Topics Covered |
|--------|----------------|
| 08 — API Versioning | Breaking vs non-breaking change definitions, URL versioning (/v1/ /v2/), header versioning trade-offs, API lifecycle (alpha/beta/v1/deprecated/sunset), deprecation headers (RFC 8594) |
| 13 — GraphQL | Over-fetching/under-fetching problems, schema design (Query/Mutation/Subscription), DataLoader for N+1 fix, subscriptions via WebSocket, GraphQL Federation, when GraphQL vs REST |
| 14 — gRPC | Protobuf binary serialization, service contract definition (.proto files), HTTP/2 multiplexing, unary/streaming RPC types, when gRPC vs REST |
| 15 — API Gateway | Cross-cutting concerns consolidation, path-based routing, auth offload, BFF pattern, request aggregation, protocol translation (REST to gRPC), gateway tool comparison (AWS/Kong/Nginx/Envoy) |
| 16 — API Design Patterns | Idempotency keys (client-generated/Redis), async long-running operations (202 Accepted), soft vs hard delete, bulk operations (207 Multi-Status), PATCH (JSON Merge Patch), API contract evolution |
| 17 — WebSockets | WebSocket protocol, HTTP upgrade handshake, full-duplex communication, Redis pub/sub for multi-server scaling, WebSocket vs SSE vs long-polling, real-time use cases |

---

## Production & Observability

| Module | Topics Covered |
|--------|----------------|
| 09 — API Performance & Scaling | N+1 query detection and fix, database indexes, connection pooling, Redis cache-aside pattern, circuit breaker, horizontal scaling (stateless design), p50/p95/p99 latency metrics |
| 10 — Testing & Documentation | Unit/integration/contract test layers, TestClient usage, auth and error path testing, load testing (Locust/k6), mocking external APIs, OpenAPI 3.0 spec, Swagger UI/Redoc, changelogs |
| 12 — Production Deployment | Dockerfile best practices (non-root/layer caching/slim base), Gunicorn + UvicornWorker, health checks (/health/live/ready), Kubernetes (RollingUpdate/probes/resource limits), CI/CD pipeline (test→build→push→deploy) |
| 18 — Real-World API Architectures | Payment state machines, idempotency in financial APIs, social media fan-out/fan-in, presigned URLs for media, surge pricing, multi-tenancy patterns, RBAC implementation, real-time location (Redis GEO) |
| 19 — OpenTelemetry | Three pillars (traces/metrics/logs), distributed tracing (spans/trace context), auto-instrumentation, manual spans, custom metrics (counter/histogram/gauge), correlated logs, sampling strategies, OTEL Collector |

---

## Interview

| Module | Topics Covered |
|--------|----------------|
| 99 — Interview Master | REST definition and constraints, PUT vs PATCH, idempotency, status code semantics, auth vs authz, URL shortener design, pagination comparison, API versioning strategies, distributed rate limiting, GraphQL vs REST trade-offs |

---

*Total modules: 19 + interview · Last updated: 2026-04-21*
