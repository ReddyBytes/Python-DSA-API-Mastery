<a id="top"></a>

# API Gateway Patterns

> 📝 **Practice:** [Q57 · api-gateway-pattern](../api_practice_questions_100.md#q57--normal--api-gateway-pattern)

> 📝 **Practice:** [Q84 · compare-gateway-vs-mesh](../api_practice_questions_100.md#q84--interview--compare-gateway-vs-mesh)

---

## Table of Contents

- [1. The Copy-Paste Problem](#copy-paste-problem)
- [2. Learning Priority](#learning-priority)
- [3. Cross-Cutting Concerns](#cross-cutting-concerns)
- [4. What an API Gateway Does](#what-gateway-does)
- [5. Key Gateway Patterns](#key-gateway-patterns)
  - [Path-Based Routing](#path-based-routing)
  - [Authentication Offload](#authentication-offload)
  - [Rate Limiting at the Edge](#rate-limiting-edge)
  - [Request Aggregation](#request-aggregation)
  - [Protocol Translation](#protocol-translation)
- [6. Backend for Frontend (BFF) Pattern](#bff-pattern)
- [7. Real Gateway Tools](#real-gateway-tools)
- [8. What NOT to Put in the Gateway](#what-not-gateway)
- [9. Summary](#summary)

---

<a id="copy-paste-problem"></a>

# 1. The Copy-Paste Problem

Ramesh manages API traffic for a growing e-commerce platform in Hyderabad. His team started with one microservice — a user service. Auth logic, rate limiting, logging, and SSL termination: done. Clean. He was proud of it.

Then the orders service came along. It needed auth. It needed rate limiting. It needed logging. He copied the code over and adapted it.

Then the products service. The notifications service. The inventory service. The payments service. The search service. The recommendations service. The reporting service. The admin service.

Ten services. Ten copies of the same auth middleware. Ten copies of the same rate limiter. Ten copies of the same logging setup.

Then a security researcher found a flaw in their JWT validation logic. Ramesh patched it in service one. He remembered to patch it in services two and three. He forgot it in services four through ten.

That's the problem that API Gateways solve. Ramesh learned this lesson the hard way — now he teaches every new engineer on his team: "If you're copying infrastructure logic between services, you need a gateway."

[Back to Top](#top)

<a id="learning-priority"></a>

# 2. Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
gateway routing · rate limiting · auth offloading

**Should Learn** — Important for real projects:
BFF pattern · circuit breaking

**Good to Know** — Useful in specific situations:
service mesh vs gateway

**Reference** — Know it exists, look up syntax when needed:
Kong plugins

[Back to Top](#top)

<a id="cross-cutting-concerns"></a>

# 3. Cross-Cutting Concerns

In software, a "cross-cutting concern" is something that almost every part of
your system needs, but doesn't belong in any single part. Authentication is the
canonical example.

Ramesh explains it to junior engineers like this: "Think of it as building security for an apartment complex. You could put a separate lock, camera, and guard at each apartment door — or you could secure the main entrance once and let everyone inside move freely."

```
Without a gateway — each service handles everything itself:

  Mobile App ──┬──> User Service     (auth + rate limit + log + SSL)
               ├──> Orders Service   (auth + rate limit + log + SSL)
               ├──> Products Service (auth + rate limit + log + SSL)
               ├──> Search Service   (auth + rate limit + log + SSL)
               └──> Payments Service (auth + rate limit + log + SSL)

  Problems:
    - Auth code duplicated 5 times (security vulnerability)
    - Mobile app needs to know about 5 service URLs
    - Mobile app makes 5 separate requests per screen
    - SSL certificates managed in 5 places
    - Rate limiting is per-service, not per-user globally
```

Cross-cutting concerns that belong in one place:

```
Authentication    → validate tokens once, not in every service
Authorization     → check permissions before reaching any service
Rate limiting     → per-user global limits, not per-service
Logging           → centralized request/response logging
Distributed tracing → correlate requests across services
SSL termination   → handle TLS in one place, internal traffic can use HTTP
Request routing   → route /users → user-service, /orders → order-service
Caching           → cache at the edge, reduce backend load
Request transformation → normalize headers, reshape payloads
```

[Back to Top](#top)

<a id="what-gateway-does"></a>

# 4. What an API Gateway Does

An API gateway is the front door of your system. Every client request goes through
it. No client talks to backend services directly.

Ramesh compares it to a hotel concierge: "Guests don't walk into the kitchen to order food or go to the maintenance room to request a towel. They talk to the concierge, who knows where everything is and handles the logistics."

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                       │
│                         CLIENTS                                       │
│          Mobile App    Web Browser    Partner API    Admin UI         │
│               │             │              │             │            │
└───────────────┼─────────────┼──────────────┼─────────────┼───────────┘
                │             │              │             │
                └──────────────┬─────────────┘             │
                               │                           │
                               ▼                           │
                ┌──────────────────────────┐               │
                │                          │               │
                │       API GATEWAY        │ <─────────────┘
                │                          │
                │  1. SSL Termination       │
                │  2. Authenticate token   │
                │  3. Check rate limits    │
                │  4. Log the request      │
                │  5. Route to service     │
                │  6. Transform response   │
                │                          │
                └──────────────────────────┘
                    │         │         │
          ┌─────────┤    ┌────┘    ┌────┘
          │         │    │         │
          ▼         ▼    ▼         ▼
     ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
     │  User   │ │  Orders  │ │ Products │ │Payments  │
     │ Service │ │ Service  │ │ Service  │ │ Service  │
     └─────────┘ └──────────┘ └──────────┘ └──────────┘
```

The gateway handles all cross-cutting concerns before the request ever reaches a
service. Backend services only see authenticated, rate-limited, logged requests.
They can focus entirely on their business logic.

[Back to Top](#top)

<a id="key-gateway-patterns"></a>

# 5. Key Gateway Patterns

<a id="path-based-routing"></a>

## Path-Based Routing

The gateway maps URL paths to backend services. Clients use one base URL.

```
Client request:
  GET https://api.myapp.com/users/42

Gateway routing rules:
  /users/*    → http://user-service:8001
  /orders/*   → http://order-service:8002
  /products/* → http://product-service:8003
  /search/*   → http://search-service:8004
  /payments/* → http://payment-service:8005

Gateway forwards:
  GET http://user-service:8001/users/42
```

The client doesn't know there's a user-service or what port it runs on. All it
knows is `api.myapp.com`. You can move, scale, or replace backend services without
changing any client code.

Routing config example (Kong/YAML style):

```yaml
routes:
  - name: users-route
    paths: ["/users"]
    service: user-service
    strip_path: false

  - name: orders-route
    paths: ["/orders"]
    service: order-service

  - name: payments-route
    paths: ["/payments"]
    service: payment-service
    plugins:
      - name: rate-limiting
        config:
          minute: 10    # stricter limits on payments
```

Ramesh's team uses path-based routing as the foundation of their gateway configuration. "Every new service gets a route on day one," he says. "The mobile team never needs to learn a new URL — they just hit `api.myapp.com` with a new path prefix."

<a id="authentication-offload"></a>

## Authentication Offload

The gateway validates the token. Backend services trust whoever the gateway
passes through, and receive the user's identity in a header.

```
Client request:
  GET /orders
  Authorization: Bearer eyJhbGci...

Gateway:
  1. Validates JWT signature
  2. Checks token not expired
  3. Looks up user permissions (or decodes from JWT claims)
  4. Adds headers:
       X-User-ID: 42
       X-User-Roles: user,premium
  5. Forwards to order-service WITHOUT the original Authorization header

Order service receives:
  GET /orders
  X-User-ID: 42
  X-User-Roles: user,premium
  (no Authorization header — the gateway consumed it)
```

The order service doesn't need JWT validation code at all. It just reads the
`X-User-ID` header and trusts it (because only the gateway can set it, and
internal traffic never comes from outside).

This is "authentication offload." The gateway is the only thing that ever needs
to know how JWTs work. All your backend services just read a header.

> Common mistake: Allowing services to be reached directly (bypassing the gateway) while trusting the `X-User-ID` header. If external traffic can reach the service, anyone can forge that header. Always ensure internal services are only reachable through the gateway via network policies or service mesh.

<a id="rate-limiting-edge"></a>

## Rate Limiting at the Edge

Rate limiting at the gateway means limits apply globally across all services.

```
Without gateway rate limiting:
  User makes 1000 requests
  100 to user-service   → hits user-service rate limit
  100 to orders-service → hits orders-service rate limit
  100 to products-service → not rate limited (forgot to add it)
  ... user can still hammer products-service

With gateway rate limiting:
  User has 1000 requests total across ALL services
  After 1000, they get 429 — regardless of which service they're hitting
```

Per-user global rate limits only make sense at a centralized entry point. A
per-service rate limiter can't see traffic going to other services.

You can also tier limits by endpoint:

```
Default:         1000 req/hour
/auth/login:       10 req/minute  (brute force protection)
/payments/charge:  60 req/hour    (expensive + high-stakes)
/search:          500 req/hour    (heavier compute)
```

Ramesh learned to tier limits after a bot scraped their entire product catalog in one night. "We had global rate limiting, but it was generous — 10,000 requests per hour. Enough for any normal user, but a scraper with patience could still drain us. Now we give `/search` a tighter budget because it's the most expensive endpoint."

<a id="request-aggregation"></a>

## Request Aggregation (API Composition)

The mobile client needs to render a user's profile page. It needs: the user's
details, their recent orders, and their preferences. Without aggregation, the
client makes three round trips:

```
Without aggregation:
  Mobile → GET /users/42          → User Service
  Mobile → GET /users/42/orders   → Orders Service
  Mobile → GET /users/42/prefs    → Prefs Service
  (3 round trips, each with latency)

With gateway aggregation:
  Mobile → GET /profile/42        → Gateway

  Gateway (in parallel):
    GET /users/42         → User Service
    GET /users/42/orders  → Orders Service
    GET /users/42/prefs   → Prefs Service

  Gateway assembles:
    {
      "user": {...},
      "recent_orders": [...],
      "preferences": {...}
    }

  Mobile ← single response (1 round trip)
```

This pattern is sometimes called "API composition" or "backend aggregation." It
reduces mobile latency significantly because mobile connections are slow and
round-trip latency is high.

Be careful with error handling here: if one upstream call fails, you need to
decide whether to fail the whole response or return partial data.

<a id="protocol-translation"></a>

## Protocol Translation

Internal services might speak gRPC for efficiency, but external clients speak
REST/JSON. The gateway handles translation.

```
External client:
  POST /users
  Content-Type: application/json
  {"name": "Alice", "email": "alice@example.com"}

Gateway translates to gRPC:
  service UserService {
    rpc CreateUser (CreateUserRequest) returns (User);
  }
  CreateUser({name: "Alice", email: "alice@example.com"})

gRPC response (protobuf binary) → Gateway translates back to JSON → client
```

External clients never need to know gRPC exists. Internal services benefit from
gRPC's performance. Both sides get what they want.

Ramesh's team migrated their internal services from REST to gRPC for the 30% latency improvement, but kept the gateway serving REST externally. "Our mobile app didn't change a single line of code," he says. "That's the power of the gateway as a translation layer."

[Back to Top](#top)

<a id="bff-pattern"></a>

# 6. Backend for Frontend (BFF) Pattern

Here's a real tension: your mobile app needs compact, battery-optimized responses.
Your web dashboard needs rich data for complex UI. Your partner API needs a stable,
well-documented interface. Your admin portal needs full access to everything.

They all have different needs. One gateway trying to serve all of them becomes a
mess of `if mobile then...` conditionals.

The BFF pattern: give each type of client its own gateway.

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Mobile App │  │  Web App    │  │  Partner    │  │  Admin UI   │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │                 │
       ▼                ▼                ▼                 ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Mobile    │  │    Web      │  │   Partner   │  │   Admin     │
│   Gateway   │  │   Gateway   │  │   Gateway   │  │   Gateway   │
│             │  │             │  │             │  │             │
│ - Compact   │  │ - Rich data │  │ - Versioned │  │ - Full      │
│   responses │  │ - Complex   │  │   stable    │  │   access    │
│ - Offline   │  │   queries   │  │   contract  │  │ - Audit     │
│   support   │  │ - WebSocket │  │ - Rate      │  │   logging   │
│ - Push      │  │   support   │  │   limited   │  │ - No rate   │
│   tokens    │  │             │  │             │  │   limits    │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       └────────────────┴──────────────────┴────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
              User Service   Order Service   Product Service
```

Each BFF is "owned" by the team that owns the client. The mobile team can evolve
the mobile gateway independently without affecting web or partners. Each BFF
aggregates and shapes data specifically for its client's needs.

This pattern becomes important at scale. If you have one team building both the
iOS app and maintaining the gateway that serves it, they can move fast without
coordinating with other client teams.

Ramesh adopted the BFF pattern when his single gateway grew to 4,000 lines of routing configuration with client-specific `if` branches everywhere. "We split into three gateways — mobile, web, and partner — and gave each team ownership. Deployment conflicts dropped to zero overnight."

[Back to Top](#top)

<a id="real-gateway-tools"></a>

# 7. Real Gateway Tools

You rarely build a gateway from scratch. The ecosystem has mature options:

```
AWS API Gateway  → managed, serverless, integrates with Lambda and IAM.
                   Great if you're AWS-native. Pay per request.

Kong             → open-source, Lua plugins, runs on Nginx. Battle-tested at
                   scale. Plugin ecosystem for everything.

Nginx            → not a "gateway" per se, but widely used as a reverse proxy
                   and load balancer with gateway capabilities. Fast, reliable.

Envoy            → high-performance proxy from Lyft. The data plane behind
                   Istio (service mesh). gRPC native. Complex to configure.

Traefik          → cloud-native, Docker and Kubernetes aware. Auto-discovers
                   services. Great developer experience, good for container
                   environments.
```

For a small startup: AWS API Gateway or Traefik. For a large platform with
complex routing needs: Kong or Envoy. For Kubernetes: Traefik or Envoy behind
Istio.

Ramesh's recommendation based on his experience: "Start with AWS API Gateway if you're on AWS and have fewer than 20 services. Move to Kong when you need custom plugin logic or multi-cloud. Move to Envoy when you need a service mesh and your traffic patterns are complex enough to justify the configuration overhead."

[Back to Top](#top)

<a id="what-not-gateway"></a>

# 8. What NOT to Put in the Gateway

The gateway is tempting. It's the one place every request passes through.
Developers start putting more and more logic there. Then it becomes a monolith
with a different name.

Ramesh calls this "gateway bloat" — the number one mistake he sees teams make after adopting a gateway. "They celebrate that services are lean, then they look at the gateway and it's 10,000 lines of business rules."

Do not put in the gateway:

```
Business logic         → "apply discount if user is premium and order > $100"
                          This belongs in the orders service.

Database queries       → The gateway should never talk to your application DB.
                          It can talk to a Redis cache for rate limit counters
                          or session data, but not your business data.

Complex transformations → Lightweight header manipulation: OK.
                           "Parse the order, look up the product details, compute
                           the tax rate for the user's jurisdiction": NOT OK.
                           Put this in a service.

Feature flags          → Maybe at the edge level (A/B routing). But complex
                          feature logic belongs in services.

Service-specific auth  → "Check if this user is allowed to see this specific
                          order" is authorization logic that needs access to
                          business data. The gateway checks authentication
                          (is the token valid?) and coarse permissions
                          (does this user have the 'orders:read' scope?).
                          Fine-grained checks belong in services.
```

The gateway should be thin and fast. It should handle the cross-cutting concerns
in milliseconds and get out of the way. The moment it starts making business
decisions, you've moved your complexity around instead of reducing it.

> Common mistake: Putting business-logic validation in the gateway. For example, checking "does this user have enough balance to make this purchase" at the gateway level. This requires database access and business rules — it belongs in the payments service. The gateway should only check "is this token valid?" and "does this user have the 'payments:write' scope?"

[Back to Top](#top)

<a id="summary"></a>

# 9. Summary

```
The problem:
  10 services × 5 cross-cutting concerns = 50 implementations of the same thing
  → bugs in 1 place affect 10 services
  → mobile client makes 5 round trips per screen

The solution: API Gateway
  - Single entry point for all clients
  - Handles auth, rate limiting, logging, SSL once, centrally
  - Routes requests to the right backend service
  - Clients know one URL: api.myapp.com

Key patterns:
  Path-based routing     → /users → user-service, /orders → order-service
  Auth offload           → gateway validates JWT, passes user_id in header
  Global rate limiting   → per-user limits across all services
  Request aggregation    → one client request → multiple backend calls → one response
  Protocol translation   → external REST ↔ internal gRPC

BFF Pattern:
  Different clients have different needs
  Give each client type its own gateway
  Mobile BFF, Web BFF, Partner BFF — each tailored to its consumer

What belongs in the gateway:
  Authentication, rate limiting, logging, routing, SSL, light transformation

What does NOT belong in the gateway:
  Business logic, DB queries, complex transformations, feature decisions
```

[Back to Top](#top)

---

**[Back to README](../README.md)**

**Prev:** [gRPC](../14_grpc/theory.md) | **Next:** [API Design Patterns](../16_api_design_patterns/theory.md)

**Related Topics:** [GraphQL](../13_graphql/theory.md) · [gRPC](../14_grpc/theory.md) · [Security in Production](../11_api_security_production/theory.md) · [API Design Patterns](../16_api_design_patterns/theory.md)
