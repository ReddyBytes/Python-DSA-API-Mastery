# REST Fundamentals

> 📝 **Practice:** [Q22 · rest-vs-rpc](../api_practice_questions_100.md#q22--normal--rest-vs-rpc)

> 📝 **Practice:** [Q9 · rest-hateoas](../api_practice_questions_100.md#q9--thinking--rest-hateoas)

> 📝 **Practice:** [Q7 · rest-statelessness](../api_practice_questions_100.md#q7--normal--rest-statelessness)

> 📝 **Practice:** [Q76 · explain-rest-principles](../api_practice_questions_100.md#q76--interview--explain-rest-principles)

## A Guy Wrote a Dissertation and Changed How We Build Software

In the year 2000, Roy Fielding — one of the principal authors of the HTTP specification
itself — submitted his PhD dissertation at UC Irvine.

The title: *"Architectural Styles and the Design of Network-based Software Architectures."*

Catchy, right?

Chapter 5 of that dissertation described a set of architectural constraints he called
REST — Representational State Transfer. He wasn't inventing something new. He was
describing and formalizing the principles behind why the World Wide Web worked so well
at scale. Billions of requests per day. Millions of different clients and servers. All
of it working together because everyone agreed on a small set of rules.

The software industry read it and said "oh, we should build our APIs this way."

And so they did.

**The key insight first: REST is not a protocol. It's not a standard. It's not a
technology.** It's an architectural style — a set of constraints. If your API follows
those constraints, it's RESTful. If it doesn't, it isn't.

That's it. No REST police. No compliance certificate. Just principles.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
6 REST constraints · resource modeling (nouns not verbs) · HTTP verb semantics · idempotency

**Should Learn** — Important for real projects, comes up regularly:
HATEOAS · URL design patterns (collections/nested/actions) · statelessness

**Good to Know** — Useful in specific situations, not always tested:
Fielding dissertation concepts · cacheability constraint

**Reference** — Know it exists, look up syntax when needed:
strict REST vs pragmatic REST · HATEOAS in practice

---

## The 6 REST Constraints

Fielding defined six constraints. Follow all of them (or most of them) and you've got
a RESTful API. Let's go through each one like a real human being, not a textbook.

---

### Constraint 1: Client-Server

**The principle:** The client and server are separate. They don't need to know anything
about each other's internal implementation. They only need to agree on the interface —
the API contract.

**The coffee shop analogy again:** You don't need to know how the espresso machine
works to order a coffee. The barista doesn't need to know how your digestive system
works to hand you a cup. You just agree on the ordering interface.

**In practice:** Your React frontend doesn't care if the backend is written in Python,
Go, or COBOL. The iOS app doesn't care if the server is running on AWS or in someone's
garage. They communicate through the API, and that's all they need to know about each
other.

This separation means:
- Frontend teams can work independently from backend teams
- You can rewrite your entire backend without touching the frontend (as long as the
  API contract stays the same)
- You can have multiple clients (web, iOS, Android) all talking to the same API

```
React Web App  ─┐
iOS App        ─┼──── same API ────> Your Backend (Python/Go/whatever)
Android App    ─┘
```

---

### Constraint 2: Stateless

**The principle:** Each request from client to server must contain all the information
needed to understand the request. The server doesn't store any session state between
requests.

**The analogy:** Imagine a phone support line where every time you call, you get a
different agent who has zero memory of your previous calls. You have to identify
yourself and explain your problem every single time. That's stateless.

The alternative — stateful — would be the agent remembering you and picking up where
you left off. Sounds nicer, but it's a nightmare to scale.

**In practice:** Every API request must be self-contained:

```
Stateful (bad for APIs):
  Request 1: "I'm Alice"
  Server: "OK, I'll remember that"
  Request 2: "Give me my orders"
  Server: "Whose orders?" ... oh wait, Alice is on server 2,
          but this request went to server 1...  ← this breaks with multiple servers

Stateless (REST):
  Request 1: "I'm Alice (token: eyJhb...), give me my orders"
  Server: "Got it. Here are Alice's orders."
  Request 2: "I'm Alice (token: eyJhb...), give me order #42"
  Server: "Got it. Here's order #42."
```

**Why stateless is great for scaling:**
With stateless APIs, any server in your cluster can handle any request. You don't need
sticky sessions. You don't need to worry about "which server stored Alice's session?"
You just add more servers when load increases.

The token (like a JWT) carries all the identity information. The server verifies the
token on every request. No server-side session storage needed.

---

### Constraint 3: Cacheable

**The principle:** Responses must define themselves as cacheable or non-cacheable.
If a response is cacheable, clients and intermediaries can reuse that response for
equivalent requests.

**The analogy:** Your browser already does this with web pages. When you load a website,
images get cached. Next time you visit, those images load from cache — no network
request. The server told the browser "this image is valid for 30 days, feel free to
cache it."

**In practice:** REST responses use HTTP caching headers to tell clients how long the
response is valid:

```
Cache-Control: public, max-age=3600    ← cache this for 1 hour, anyone can cache it
Cache-Control: private, max-age=300    ← cache for 5 min, only the browser (not CDNs)
Cache-Control: no-store                ← never cache this (financial data, auth tokens)
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"  ← fingerprint of the response
```

**Why this matters for performance:** If 10,000 users ask for the same product listing,
and that data is cached at the CDN level, your servers only handle 1 request instead of
10,000. That's a 10,000x performance improvement for free.

---

### Constraint 4: Uniform Interface

**The principle:** The interface between clients and servers must be uniform. There are
four sub-constraints here:

1. **Resource identification in requests** — Resources are identified by URLs
   (`/users/42`). The representation returned (JSON) may differ from the internal
   storage (database rows).

2. **Resource manipulation through representations** — When you have a resource
   representation (the JSON you got back), you have enough information to modify or
   delete it (if you have permission).

3. **Self-descriptive messages** — Each message includes enough information to describe
   how to process it (Content-Type header, HTTP method, etc.).

4. **HATEOAS** — We'll come back to this. It's the weird one.

**In practice:** The uniform interface is why REST APIs feel familiar even when you've
never used a specific one before. If you know REST, you can make reasonable guesses:
- `GET /products` → probably returns all products
- `GET /products/42` → probably returns product 42
- `POST /products` → probably creates a product
- `DELETE /products/42` → probably deletes product 42

That predictability is a feature. Developers don't need to read docs to make educated
guesses about how an endpoint works.

---

### Constraint 5: Layered System

**The principle:** A client can't tell whether it's connected directly to the end server
or to an intermediary. There can be multiple layers: load balancers, CDNs, API gateways,
proxies. The client just sends its request and gets a response.

```
Your App
   |
   v
[ CDN ]  ← serves cached responses, client doesn't know
   |
   v
[ Load Balancer ]  ← distributes traffic, client doesn't know
   |
   v
[ API Gateway ]  ← handles auth, rate limiting, client doesn't know
   |
   v
[ App Server 1 ]  or  [ App Server 2 ]  or  [ App Server 3 ]
```

**Why this matters:** The operator of the API can change their infrastructure — swap
CDN providers, add a caching layer, change load balancers — and none of their API
clients notice. They just keep making the same requests to the same URL.

This is also why you should always use HTTPS with the actual domain of the API, never
hardcode a specific server IP. The IP might be a load balancer. The load balancer might
route to any of ten servers. That's fine — that's the layered system constraint working
exactly as intended.

---

### Constraint 6: Code on Demand (Optional)

**The principle:** Servers can optionally extend client functionality by transferring
executable code. The most common example: a web server sending JavaScript to a browser.

**This one is marked optional in Fielding's dissertation.** Most REST API discussions
skip it entirely, and most REST APIs don't implement it.

When you hit a REST API from your Python code, you're getting back data (JSON), not
executable code. This constraint is mostly relevant in the context of web browsers, where
the "client" runs JavaScript that the server delivered.

You don't need to worry about this one for the APIs you'll build. Just know it exists
and is optional.

---

## Resources — Thinking in Nouns, Not Verbs

This is the most practical concept in REST, and the one that trips up developers most
often when they're new.

**A REST API is a collection of resources.** Resources are things. Nouns. Not actions.

The HTTP methods (GET, POST, PUT, DELETE) are your verbs. The URLs are your nouns. You
combine them:

```
verb  +  noun  =  action

GET  /users/42       →  "get the user with ID 42"
POST /users          →  "create a new user"
PUT  /users/42       →  "replace user 42"
DELETE /users/42     →  "delete user 42"
```

The mistake beginners make is putting the verb in the URL:

```
WRONG (RPC-style, not REST):
  POST /getUser
  POST /createUser
  POST /updateUser
  POST /deleteUser
  POST /getUserOrders
  POST /sendWelcomeEmail

RIGHT (REST-style):
  GET    /users/42          ← get user
  POST   /users             ← create user
  PATCH  /users/42          ← update user
  DELETE /users/42          ← delete user
  GET    /users/42/orders   ← get user's orders
  POST   /users/42/welcome-email  ← (action on a resource, acceptable)
```

**Why does this matter?**

Because when you put verbs in URLs, every endpoint becomes unique. There's no pattern.
You have to document every single endpoint from scratch. Your API becomes unpredictable.

When you design around nouns and use HTTP methods as verbs, your API becomes predictable.
Developers can guess how it works. They can explore it. It's self-consistent.

---

## URL Design Patterns

Let's get into the real patterns you'll see (and use) constantly.

### Collections

```
GET /users          → all users (usually paginated)
GET /products       → all products
GET /orders         → all orders
```

A collection URL is always a plural noun. It returns a list.

### Single Items

```
GET /users/42       → user with ID 42
GET /products/abc   → product with ID "abc"
GET /orders/x9y7    → order with ID "x9y7"
```

The ID goes in the URL path. IDs can be integers, UUIDs, slugs — whatever your system
uses.

### Nested Resources

```
GET /users/42/orders           → all orders belonging to user 42
GET /users/42/orders/7         → order 7, belonging to user 42
GET /teams/engineering/members → all members of the engineering team
```

Nesting expresses a relationship. Order 7 belongs to user 42. Use nesting when the
relationship is important to the query.

**Rule of thumb: don't nest more than 2 levels deep.** Beyond that, URLs get unwieldy
and the relationships get confusing. If you need `GET /users/42/orders/7/items/3`, ask
yourself if `GET /order-items/3` (with the order ID returned in the item object) might
be cleaner.

### Actions (the Exception to Nouns-Only)

Sometimes you have operations that genuinely don't map to CRUD. That's OK:

```
POST /users/42/deactivate      → deactivate user 42
POST /invoices/9/send          → send invoice 9 to the customer
POST /payments/abc/refund      → refund payment abc
POST /cache/clear              → clear the cache
```

These are actions on resources, not resources themselves. The convention is to use a
verb as the last segment. Use these sparingly — if you find yourself adding many actions,
you might want to reconsider your resource design.

### Filtering

```
GET /users?role=admin
GET /users?role=admin&active=true
GET /products?category=electronics&min_price=100&max_price=500
GET /orders?status=pending&customer_id=42
```

Filtering goes in query parameters, not the URL path. The URL path identifies the
collection; query parameters narrow down what you want from it.

### Sorting

```
GET /users?sort=created_at
GET /users?sort=created_at&order=desc
GET /products?sort=price&order=asc
GET /orders?sort=total&order=desc
```

### Pagination

```
GET /users?page=2&limit=20         → offset-based: page 2, 20 per page
GET /users?after=eyJpZCI6NDJ9      → cursor-based: items after this cursor
GET /users?offset=40&limit=20      → raw offset: skip 40, take 20
```

More on pagination strategies in the next module.

### Sparse Fieldsets

```
GET /users?fields=id,name,email    → only return these fields, not everything
```

Useful for mobile clients that don't want to receive data they won't use.

---

## HTTP Verbs — Deep Dive

> 📝 **Practice:** [Q1 · http-methods-semantics](../api_practice_questions_100.md#q1--normal--http-methods-semantics)

You've seen the verbs. Let's go deeper on two important properties: **idempotency** and
**safety**.

```
Method    Safe?    Idempotent?    Has Body?
GET       yes      yes            no
POST      no       no             yes
PUT       no       yes            yes
PATCH     no       no*            yes
DELETE    no       yes            no
```

*PATCH technically can be idempotent but usually isn't treated as such.

**Safe** means the operation doesn't modify anything on the server. GET is safe — you
can call it a million times and nothing changes. POST is not safe — it creates things.

**Idempotent** means calling the operation N times has the same effect as calling it
once. More on this in the next section.

> 📝 **Practice:** [Q23 · http-methods-safe](../api_practice_questions_100.md#q23--normal--http-methods-safe)

### GET — The Getter

```
GET /users/42

Response 200:
{
  "id": 42,
  "name": "Alice",
  "email": "alice@example.com",
  "created_at": "2024-01-15T09:30:00Z"
}
```

GET requests have no body. Parameters go in the URL path (`/users/42`) or query string
(`/users?role=admin`). GET should never modify anything. If a GET request modifies
state, something is wrong.

### POST — The Creator

```
POST /users
Content-Type: application/json

{
  "name": "Bob",
  "email": "bob@example.com",
  "role": "viewer"
}

Response 201 Created:
Location: /users/99
{
  "id": 99,
  "name": "Bob",
  "email": "bob@example.com",
  "role": "viewer",
  "created_at": "2024-03-08T14:22:00Z"
}
```

POST creates a new resource. The server assigns the ID. The response includes a
`Location` header pointing to the new resource. Status code is 201, not 200.

> 📝 **Practice:** [Q2 · post-vs-put-vs-patch](../api_practice_questions_100.md#q2--thinking--post-vs-put-vs-patch)

### PUT — The Full Replacer

```
PUT /users/42
Content-Type: application/json

{
  "name": "Alice Johnson",
  "email": "alice.johnson@example.com",
  "role": "admin"
}

Response 200:
{
  "id": 42,
  "name": "Alice Johnson",
  "email": "alice.johnson@example.com",
  "role": "admin",
  "updated_at": "2024-03-08T14:25:00Z"
}
```

PUT replaces the entire resource. If you send a PUT with only `name` and forget to
include `email`, the email gets wiped. PUT is a full replacement. Send everything.

### PATCH — The Surgeon

```
PATCH /users/42
Content-Type: application/json

{
  "role": "admin"
}

Response 200:
{
  "id": 42,
  "name": "Alice",        ← unchanged
  "email": "alice@example.com",  ← unchanged
  "role": "admin",        ← updated
  "updated_at": "2024-03-08T14:25:00Z"
}
```

PATCH updates only what you send. Everything else stays the same. This is what you want
90% of the time when "updating" a resource.

**PUT vs PATCH — when to use which:**

Use PUT when you want to completely replace a resource and you have all the data.
Use PATCH when you want to change specific fields without affecting others.

In practice, PATCH is far more common. Most "edit" operations in real apps are partial
updates.

### DELETE — The Terminator

```
DELETE /users/42

Response 204 No Content
(empty body — there's nothing to return, the resource is gone)
```

204 with no body is the most common response for DELETE. Some APIs return 200 with the
deleted object (useful if you want to confirm what was deleted), but 204 is the standard.

---

## Idempotency — One of the Most Important Concepts

> 📝 **Practice:** [Q3 · idempotency-keys](../api_practice_questions_100.md#q3--critical--idempotency-keys)

Let's talk about this in depth because it matters more than most developers realize.

**Idempotent** means: calling the operation multiple times produces the same result as
calling it once.

```
Idempotent (GET):
  GET /users/42  → returns Alice
  GET /users/42  → returns Alice (same result)
  GET /users/42  → returns Alice (same result)
  No matter how many times you call it, same result.

Idempotent (DELETE):
  DELETE /users/42  → user 42 deleted, returns 204
  DELETE /users/42  → user 42 already gone, returns 404
  The state of the world after each call is the same: user 42 doesn't exist.

NOT idempotent (POST):
  POST /users body={"name": "Alice"}  → creates user 1, returns 201
  POST /users body={"name": "Alice"}  → creates user 2 (DUPLICATE), returns 201
  POST /users body={"name": "Alice"}  → creates user 3 (ANOTHER DUPLICATE), returns 201
  Every call creates a new resource. Not idempotent.

Idempotent (PUT):
  PUT /users/42 body={"name": "Alice", "email": "a@b.com"}  → user 42 updated
  PUT /users/42 body={"name": "Alice", "email": "a@b.com"}  → user 42 updated (same)
  PUT /users/42 body={"name": "Alice", "email": "a@b.com"}  → user 42 updated (same)
  Calling it three times with the same data = same result as calling it once.
```

**Why does idempotency matter?**

Networks are unreliable. Requests time out. Connections drop. Servers restart.

When a request fails, you don't always know if it succeeded on the server before the
failure, or failed before reaching the server.

With an idempotent operation, you can safely retry:

```
Client: "DELETE /users/42"
[connection drops — did it go through? don't know]

Client: "DELETE /users/42"  ← safe to retry
Server: "404 Not Found" or "204 No Content" — either way, user 42 is gone.
```

With a non-idempotent operation, retrying is dangerous:

```
Client: "POST /payments amount=1000"
[connection drops — did it go through? don't know]

Client: "POST /payments amount=1000"  ← DANGEROUS to retry
Server: "201 Created" — you may have just charged the customer twice!
```

This is why payment APIs like Stripe require you to send an **Idempotency Key** with
charge requests — so if you retry, Stripe returns the original response instead of
processing the charge again. More on this in the best practices module.

> 📝 **Practice:** [Q77 · explain-idempotency-analogy](../api_practice_questions_100.md#q77--interview--explain-idempotency-analogy)

---

## Request/Response Structure — Full Examples

Let's look at complete real-world examples.

### Creating a User — POST

**Request:**
```
POST /api/v1/users
Host: api.example.com
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
Accept: application/json

{
  "name": "Charlie Brown",
  "email": "charlie@example.com",
  "role": "viewer",
  "team_id": 5
}
```

**Success Response (201 Created):**
```
HTTP/1.1 201 Created
Content-Type: application/json
Location: /api/v1/users/128

{
  "data": {
    "id": 128,
    "name": "Charlie Brown",
    "email": "charlie@example.com",
    "role": "viewer",
    "team_id": 5,
    "created_at": "2024-03-08T09:15:00Z",
    "updated_at": "2024-03-08T09:15:00Z"
  }
}
```

### Fetching a User — GET

**Request:**
```
GET /api/v1/users/128
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
Accept: application/json
```

**Response (200 OK):**
```
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: private, max-age=300
ETag: "d3b07384d113edec49eaa6238ad5ff00"

{
  "data": {
    "id": 128,
    "name": "Charlie Brown",
    "email": "charlie@example.com",
    "role": "viewer",
    "team_id": 5,
    "created_at": "2024-03-08T09:15:00Z",
    "updated_at": "2024-03-08T09:15:00Z"
  }
}
```

### Validation Error — 400

**Request:**
```
POST /api/v1/users
Content-Type: application/json

{
  "name": "",
  "email": "not-an-email",
  "role": "superadmin"
}
```

**Response (400 Bad Request):**
```
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "name",
        "message": "Name is required and cannot be empty"
      },
      {
        "field": "email",
        "message": "must be a valid email address"
      },
      {
        "field": "role",
        "message": "must be one of: viewer, editor, admin"
      }
    ]
  }
}
```

### Paginated Collection Response

**Request:**
```
GET /api/v1/users?page=2&limit=20
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
```

**Response:**
```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "data": [
    {"id": 21, "name": "User 21", "email": "user21@example.com"},
    {"id": 22, "name": "User 22", "email": "user22@example.com"},
    ...
  ],
  "meta": {
    "total": 153,
    "page": 2,
    "limit": 20,
    "total_pages": 8,
    "has_next": true,
    "has_prev": true
  },
  "links": {
    "self": "/api/v1/users?page=2&limit=20",
    "next": "/api/v1/users?page=3&limit=20",
    "prev": "/api/v1/users?page=1&limit=20",
    "first": "/api/v1/users?page=1&limit=20",
    "last": "/api/v1/users?page=8&limit=20"
  }
}
```

---

## HATEOAS — The Constraint Nobody Uses (But You Should Know About)

HATEOAS stands for Hypermedia As The Engine Of Application State. Say it once, feel
fancy, then mostly forget about it in day-to-day work.

The idea: API responses should include links to related actions. The client discovers
what it can do next by reading the response, not from external documentation.

```json
{
  "id": 42,
  "name": "Alice",
  "status": "active",
  "_links": {
    "self": { "href": "/users/42" },
    "orders": { "href": "/users/42/orders" },
    "deactivate": { "href": "/users/42/deactivate", "method": "POST" },
    "update": { "href": "/users/42", "method": "PATCH" }
  }
}
```

**The theoretical benefit:** clients become more flexible. You can change your URL
structure and clients that follow links adapt automatically.

**The practical reality:** Almost no production APIs implement HATEOAS properly. The
benefits are real in theory but hard to realize in practice. Clients typically read
documentation, not hypermedia links, to understand what they can do.

You'll see HATEOAS mentioned in REST purity discussions. You'll rarely see it in actual
APIs. Don't stress about it. Know it exists. Move on.

---

## How RESTful Is "RESTful Enough"?

Here's a real talk moment: most APIs people call "REST" or "RESTful" don't actually
implement all six constraints. They implement Client-Server, Stateless, and Uniform
Interface. They partially implement Cacheable and Layered System. They ignore Code on
Demand and HATEOAS.

That's fine. The industry has converged on a pragmatic version of REST that gets you
90% of the benefits with 50% of the constraints. If you:

1. Design around resources (nouns) with HTTP methods (verbs)
2. Use status codes correctly
3. Keep requests stateless (token in every request)
4. Use consistent URL patterns

...then you're building a good API that most developers would call "RESTful," and that's
what matters.

Don't let perfect be the enemy of good. A pragmatic REST API that developers can
understand and use is worth a hundred technically-perfect APIs that are confusing.

---

## Summary

```
REST = 6 architectural constraints, not a protocol or standard

The 6 constraints:
  1. Client-Server    → separate concerns, independent evolution
  2. Stateless        → each request is self-contained
  3. Cacheable        → responses define their own caching rules
  4. Uniform Interface → consistent, predictable resource-based design
  5. Layered System   → client can't see what's behind the API
  6. Code on Demand   → optional, mostly for browsers

Resources:
  → things, not actions
  → nouns in URLs, verbs are HTTP methods

URL patterns:
  GET /resources          → list
  GET /resources/id       → single item
  POST /resources         → create
  PUT /resources/id       → replace
  PATCH /resources/id     → partial update
  DELETE /resources/id    → delete
  GET /resources/id/sub   → nested resource

Idempotency:
  → GET, PUT, DELETE = idempotent (safe to retry)
  → POST = NOT idempotent (danger: creates duplicates)
  → matters for: retries, network failures, reliability
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← What is an API?](../01_what_is_an_api/story.md) &nbsp;|&nbsp; **Next:** [REST Best Practices →](../03_rest_best_practices/patterns.md)

**Related Topics:** [REST Best Practices](../03_rest_best_practices/patterns.md) · [What is an API?](../01_what_is_an_api/story.md) · [Error Handling Standards](../06_error_handling_standards/error_guide.md) · [API Versioning](../08_versioning_standards/versioning_strategy.md)
