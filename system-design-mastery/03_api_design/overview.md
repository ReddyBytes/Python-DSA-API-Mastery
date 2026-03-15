# API Design — A Rapid Orientation

> This is a short overview. APIs are a vast topic and deserve their own
> deep-dive. That lives in the **api-mastery** folder (coming soon).
> This file gives you enough context to understand what APIs are,
> why they exist, and how to tell REST from GraphQL from gRPC at a glance.

---

## 1. What Is an API?

Think of a restaurant. You sit down, look at the **menu**, and tell the waiter
what you want. You do not walk into the kitchen, operate the stove, or know
the supplier's delivery schedule. The menu is the contract: here is what you
can ask for, here is the format, here is what you will get back.

An **API (Application Programming Interface)** is that menu — for software.

```
WITHOUT an API:

  Your app ──── direct database query ────► Database
                (you know the schema,
                 the table names,
                 the internal structure)

WITH an API:

  Your app ──── HTTP request ────► API Server ──► Database
               "GET /users/42"      (hides internals,
                                     validates input,
                                     controls access)
```

APIs let systems talk to each other without knowing each other's internals.
They are the contracts that make large, multi-team software possible.

---

## 2. REST in 60 Seconds

**REST (Representational State Transfer)** treats everything as a **resource**
identified by a URL, and uses standard HTTP verbs to act on it.

```
Verb      Meaning                Example
──────────────────────────────────────────────────────
GET       Read a resource        GET  /users/42
POST      Create a resource      POST /users
PUT       Replace a resource     PUT  /users/42
PATCH     Partially update       PATCH /users/42
DELETE    Remove a resource      DELETE /users/42
──────────────────────────────────────────────────────
```

A quick example:

```
Request:
  GET /articles/7
  Accept: application/json

Response:
  HTTP 200 OK
  {
    "id": 7,
    "title": "Why Postgres Is Still Great",
    "author": "dana",
    "published": "2024-11-01"
  }
```

Common status codes to know:

```
200 OK          Request succeeded
201 Created     Resource was created
400 Bad Request Client sent invalid data
401 Unauthorized  No valid auth credentials
403 Forbidden   Authenticated but not allowed
404 Not Found   Resource does not exist
429 Too Many Requests  Rate limited
500 Internal Server Error  Server blew up
503 Service Unavailable  Temporarily down
```

REST is the default choice for public APIs and most web services.

---

## 3. GraphQL in 30 Seconds

With REST, the server decides what fields you get back. With **GraphQL**,
the *client* asks for exactly the fields it needs.

```
Request:
  POST /graphql
  {
    user(id: "42") {
      name
      email
    }
  }

Response:
  {
    "data": {
      "user": {
        "name": "Alex",
        "email": "alex@example.com"
      }
    }
  }
```

No over-fetching (getting 30 fields when you needed 2). No under-fetching
(needing to make 3 REST calls to assemble one screen's worth of data).

Best for: frontends (especially mobile) with complex, varied data needs.
Invented at Facebook. Used heavily by GitHub, Shopify, Twitter.

---

## 4. gRPC in 30 Seconds

**gRPC** uses a binary protocol (Protocol Buffers) instead of JSON text.
You define your service in a `.proto` file and generate client/server code.

```protobuf
// user.proto
service UserService {
  rpc GetUser (UserRequest) returns (UserResponse);
}

message UserRequest {
  int32 id = 1;
}

message UserResponse {
  string name = 1;
  string email = 2;
}
```

The client call ends up looking like a regular function call in your
language of choice. The transport is fast (binary, compressed, HTTP/2).

Best for: internal service-to-service communication where performance
matters and you control both ends of the wire.
Used by: Google internally, Kubernetes control plane, many microservices.

---

## 5. Quick Comparison

```
Feature          REST              GraphQL          gRPC
────────────────────────────────────────────────────────────────
Transport        HTTP/1.1+         HTTP             HTTP/2
Format           JSON (usually)    JSON             Binary (protobuf)
Schema           Implicit          Explicit         Explicit (.proto)
Flexibility      Fixed endpoints   Client-driven    Fixed methods
Performance      Good              Good             Excellent
Browser support  Native            Native           Limited (needs proxy)
Best for         Public APIs       Complex UIs      Internal services
Learning curve   Low               Medium           Medium-High
────────────────────────────────────────────────────────────────
```

**When to use which:**

- Building a public API that third parties will consume? **REST.**
- Building a mobile app that needs to query complex, nested data? **GraphQL.**
- Connecting microservices inside your own infrastructure? **gRPC.**

---

## 6. Key Concepts — One Line Each

**Idempotency** — Calling the same endpoint multiple times has the same
effect as calling it once. GET, PUT, DELETE should be idempotent. POST
usually is not.

**Pagination** — Never return 10 million records at once. Use cursor-based
or offset-based pagination to return data in pages.

**Versioning** — APIs change. Signal breaking changes via the URL
(`/v1/users`, `/v2/users`) or headers so clients do not break overnight.

**Rate Limiting** — Protect your service from being overwhelmed. Return
`429 Too Many Requests` when a client exceeds its quota.

**Authentication vs Authorisation** — Auth*n* proves who you are (API
keys, OAuth tokens). Auth*z* decides what you are allowed to do (RBAC,
scopes). Both matter.

---

## 7. For the Full Deep-Dive

This overview is intentionally brief. APIs deserve — and will get — a
dedicated repository covering:

```
api-mastery/  (coming soon)
├── REST in depth         — HATEOAS, OpenAPI/Swagger, versioning strategies
├── GraphQL in depth      — schemas, resolvers, subscriptions, N+1 problem
├── gRPC in depth         — streaming, interceptors, deadlines
├── API security          — OAuth2, JWT, API keys, HMAC signing
├── API design patterns   — idempotency keys, cursor pagination, webhooks
├── Rate limiting         — token bucket, leaky bucket, sliding window
└── Real-world examples   — Stripe, GitHub, Twilio API design decisions
```

Until then, the core idea is: **APIs are contracts between systems.
Design them for the humans (and programs) who will use them, not for
the internals they hide.**

---

## Navigation

| Direction | Link |
|-----------|------|
| Previous | [02 — System Fundamentals](../02_system_fundamentals/fundamentals.md) |
| Next | [04 — Backend Architecture](../04_backend_architecture/intro.md) |
| Home | [README.md](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← System Fundamentals — Interview Q&A](../02_system_fundamentals/interview.md) &nbsp;|&nbsp; **Next:** [Theory →](./theory.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
