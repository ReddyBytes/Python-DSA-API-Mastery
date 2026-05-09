<a id="top"></a>

# API Design for System Design

> Mahesh is a Telugu system architect. His company is building a new platform with a mobile app, a web dashboard, an internal analytics service, and a public developer API. Four consumers, four different needs. He cannot pick one API style blindly — he needs a framework for choosing the right tool for each boundary. This is that framework.

## Contents

- [1. What Is an API](#what-is-an-api)
- [2. The Restaurant Analogy](#restaurant-analogy)
- [3. REST — The Universal Menu](#rest)
  - [HTTP Verbs and Resources](#rest-verbs)
  - [Status Codes Every Engineer Must Know](#status-codes)
  - [REST Strengths and Weaknesses](#rest-strengths)
- [4. GraphQL — The Build-Your-Own-Plate Buffet](#graphql)
  - [How GraphQL Works](#graphql-how)
  - [The N+1 Problem](#graphql-n1)
  - [GraphQL Strengths and Weaknesses](#graphql-strengths)
- [5. gRPC — The Kitchen Intercom](#grpc)
  - [Protocol Buffers and Code Generation](#grpc-proto)
  - [Streaming Modes](#grpc-streaming)
  - [gRPC Strengths and Weaknesses](#grpc-strengths)
- [6. Head-to-Head Comparison Table](#comparison)
- [7. Decision Framework — When to Choose Which](#decision-framework)
  - [Mahesh's Decision Tree](#decision-tree)
  - [Real-World Mapping](#real-world-mapping)
- [8. Request Flow Diagrams](#request-flows)
- [9. API Contract Design](#contract-design)
  - [Versioning Strategies](#versioning)
  - [Backward Compatibility Rules](#backward-compat)
  - [Idempotency Keys](#idempotency)
- [10. API Gateway Patterns](#api-gateway)
  - [Gateway as Traffic Controller](#gateway-traffic)
  - [Backend-for-Frontend (BFF)](#bff)
- [11. Pagination Patterns](#pagination)
- [12. Rate Limiting at the API Layer](#rate-limiting)
- [13. Common Mistakes](#common-mistakes)
- [14. Interview Decision Scenarios](#interview-scenarios)
- [15. Summary](#summary)

[Back to Top](#top)

<a id="what-is-an-api"></a>

## 1. What Is an API

Think of a restaurant. You sit down, look at the **menu**, and tell the waiter what you want. You do not walk into the kitchen, operate the stove, or know the supplier's delivery schedule. The menu is the contract: here is what you can ask for, here is the format, here is what you will get back.

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

APIs let systems talk to each other without knowing each other's internals. They are the contracts that make large, multi-team software possible.

[Back to Top](#top)

<a id="restaurant-analogy"></a>

## 2. The Restaurant Analogy

Mahesh explains API styles to his team using a food analogy that sticks:

```
REST = A fixed menu restaurant
  - You pick from what they offer (fixed endpoints)
  - Each dish comes with a standard plate (fixed response shape)
  - Simple, universal, well-understood

GraphQL = A build-your-own-plate buffet
  - You specify exactly what you want on your plate
  - No wasted food (no over-fetching)
  - You can combine items from different stations in one trip

gRPC = The kitchen intercom
  - Chefs talking to each other in shorthand
  - Fast, compact, no pleasantries needed
  - Not customer-facing — internal efficiency
```

This analogy maps directly to how Mahesh designs boundaries in his system. The public API is the fixed menu (REST). The mobile app gets the buffet (GraphQL). The microservices use the intercom (gRPC).

[Back to Top](#top)

<a id="rest"></a>

## 3. REST — The Universal Menu

**REST (Representational State Transfer)** treats everything as a **resource** identified by a URL, and uses standard HTTP verbs to act on it. It was defined by Roy Fielding in 2000 and remains the dominant style for public APIs.

<a id="rest-verbs"></a>

**HTTP Verbs and Resources**

```
Verb      Meaning                Example               Idempotent?
──────────────────────────────────────────────────────────────────────
GET       Read a resource        GET  /users/42         Yes
POST      Create a resource      POST /users            No
PUT       Replace a resource     PUT  /users/42         Yes
PATCH     Partially update       PATCH /users/42        No*
DELETE    Remove a resource      DELETE /users/42       Yes
──────────────────────────────────────────────────────────────────────
* PATCH can be idempotent depending on implementation
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

<a id="status-codes"></a>

**Status Codes Every Engineer Must Know**

```
Code   Meaning                    When Mahesh Uses It
──────────────────────────────────────────────────────────────────────
200    OK                         Successful read or update
201    Created                    Resource was created (POST)
204    No Content                 Successful delete, nothing to return
400    Bad Request                Client sent invalid data
401    Unauthorized               No valid auth credentials
403    Forbidden                  Authenticated but not allowed
404    Not Found                  Resource does not exist
409    Conflict                   Duplicate creation attempt
422    Unprocessable Entity       Valid JSON but failed validation
429    Too Many Requests          Rate limited
500    Internal Server Error      Server blew up
502    Bad Gateway                Upstream service failed
503    Service Unavailable        Temporarily down (maintenance)
504    Gateway Timeout            Upstream timed out
──────────────────────────────────────────────────────────────────────
```

<a id="rest-strengths"></a>

**REST Strengths and Weaknesses**

```
STRENGTHS                              WEAKNESSES
─────────────────────────────────────  ─────────────────────────────────────
Universal — every language has HTTP    Over-fetching: GET /users returns 30
  client support                         fields when mobile needs 3

Cacheable — HTTP caching works         Under-fetching: need 3 calls to
  natively with GET requests             assemble one screen of data

Stateless — easy to scale              No standard for real-time (need
  horizontally                           WebSockets or SSE separately)

Tooling-rich — Swagger/OpenAPI,        Versioning is messy — no single
  Postman, curl all work                 standard, many competing approaches

Human-readable — JSON is debug-        N+1 call problem for nested
  friendly                               resources
─────────────────────────────────────  ─────────────────────────────────────
```

Mahesh's rule: "If you are building something that will be consumed by unknown third parties — developers you will never meet — REST is the default. They already know how it works."

[Back to Top](#top)

<a id="graphql"></a>

## 4. GraphQL — The Build-Your-Own-Plate Buffet

With REST, the server decides what fields you get back. With **GraphQL**, the *client* asks for exactly the fields it needs. Facebook invented it in 2012 to solve the mobile app problem: slow networks, limited bandwidth, screens that combine data from many sources.

<a id="graphql-how"></a>

**How GraphQL Works**

```
Request:
  POST /graphql
  {
    user(id: "42") {
      name
      email
      posts(limit: 5) {
        title
        createdAt
      }
    }
  }

Response:
  {
    "data": {
      "user": {
        "name": "Alex",
        "email": "alex@example.com",
        "posts": [
          {"title": "First Post", "createdAt": "2024-01-15"},
          {"title": "Second Post", "createdAt": "2024-02-20"}
        ]
      }
    }
  }
```

One request. Exactly the fields needed. No second round-trip for posts. This is why mobile teams love GraphQL — on a 3G connection, fewer round-trips means faster screens.

The schema is explicit and typed:

```graphql
type User {
  id: ID!
  name: String!
  email: String!
  posts(limit: Int): [Post!]!
}

type Post {
  id: ID!
  title: String!
  createdAt: DateTime!
  author: User!
}

type Query {
  user(id: ID!): User
  posts(authorId: ID!, limit: Int): [Post!]!
}

type Mutation {
  createPost(title: String!, body: String!): Post!
}
```

<a id="graphql-n1"></a>

**The N+1 Problem**

Mahesh's team hit this on day two. When a query asks for 50 users and their posts, a naive resolver does:

```
1 query to get 50 users
+ 50 queries to get each user's posts
= 51 database queries for one GraphQL request
```

Solution: **DataLoader** — batches and deduplicates database calls within a single request. Instead of 50 separate queries, DataLoader collects all user IDs and issues one `WHERE id IN (...)` query.

```
Without DataLoader:           With DataLoader:
  SELECT * FROM posts           SELECT * FROM posts
    WHERE user_id = 1;            WHERE user_id IN (1,2,3,...50);
  SELECT * FROM posts           -- ONE query, results distributed
    WHERE user_id = 2;             to each resolver
  ... (48 more times)
```

<a id="graphql-strengths"></a>

**GraphQL Strengths and Weaknesses**

```
STRENGTHS                              WEAKNESSES
─────────────────────────────────────  ─────────────────────────────────────
No over-fetching — client gets         HTTP caching is hard — everything
  exactly what it asks for               is POST to /graphql

No under-fetching — one request        Complexity shifts to server — need
  can traverse relationships             DataLoader, query cost analysis

Strongly typed schema doubles          File uploads are awkward — not
  as documentation                       natively supported

Schema evolution without versions —    N+1 problem requires explicit
  add fields, deprecate old ones         mitigation (DataLoader)

Excellent for mobile — fewer           Query complexity attacks — malicious
  round-trips on slow networks           clients can craft expensive queries

Introspection — clients can            Learning curve — resolvers, schema
  discover the API at runtime            stitching, federation are complex
─────────────────────────────────────  ─────────────────────────────────────
```

Mahesh's rule: "GraphQL shines when you have diverse clients with different data needs hitting the same backend. If everyone wants the same shape, REST is simpler."

[Back to Top](#top)

<a id="grpc"></a>

## 5. gRPC — The Kitchen Intercom

**gRPC** uses a binary protocol (Protocol Buffers) instead of JSON text. You define your service in a `.proto` file and generate client/server code in any language. Google built it for internal service communication where nanoseconds matter.

<a id="grpc-proto"></a>

**Protocol Buffers and Code Generation**

```protobuf
// user.proto
syntax = "proto3";

service UserService {
  rpc GetUser (UserRequest) returns (UserResponse);
  rpc ListUsers (ListUsersRequest) returns (stream UserResponse);
  rpc CreateUser (CreateUserRequest) returns (UserResponse);
}

message UserRequest {
  int32 id = 1;
}

message UserResponse {
  int32 id = 1;
  string name = 2;
  string email = 3;
  int64 created_at = 4;
}

message ListUsersRequest {
  int32 page_size = 1;
  string page_token = 2;
}

message CreateUserRequest {
  string name = 1;
  string email = 2;
}
```

From this single `.proto` file, `protoc` generates:
- Python client and server stubs
- Go client and server stubs
- Java, C++, Rust, Node.js — any supported language

The client call looks like a local function call:

```python
# Generated client code — feels like calling a local function
response = stub.GetUser(UserRequest(id=42))
print(response.name)  # "Alex"
```

<a id="grpc-streaming"></a>

**Streaming Modes**

gRPC supports four communication patterns:

```
Pattern              Flow                    Use Case
──────────────────────────────────────────────────────────────────────
Unary                Client ──► Server       Simple request/response
                     Client ◄── Server

Server streaming     Client ──► Server       Real-time feed, logs
                     Client ◄── Server       (server sends multiple
                     Client ◄── Server        responses)
                     Client ◄── Server

Client streaming     Client ──► Server       File upload, sensor data
                     Client ──► Server       (client sends chunks,
                     Client ──► Server        server responds once)
                     Client ◄── Server

Bidirectional        Client ◄──► Server      Chat, collaborative
                     Client ◄──► Server       editing, gaming
                     Client ◄──► Server
──────────────────────────────────────────────────────────────────────
```

<a id="grpc-strengths"></a>

**gRPC Strengths and Weaknesses**

```
STRENGTHS                              WEAKNESSES
─────────────────────────────────────  ─────────────────────────────────────
Binary format — 5-10x smaller than     No browser support without proxy
  JSON, faster serialization             (grpc-web adds complexity)

HTTP/2 multiplexing — multiple         Not human-readable — cannot curl
  requests on one TCP connection          or inspect with browser devtools

Streaming built-in — all four          Tighter coupling — both sides need
  patterns natively supported             the .proto file and generated code

Code generation — type-safe clients    Debugging is harder — binary
  in any language, no SDK to write        payloads need special tooling

Deadlines/timeouts — built into        Load balancing is harder — HTTP/2
  the protocol, not an afterthought       long-lived connections confuse L4

Interceptors — middleware pattern       Breaking changes require careful
  for auth, logging, metrics              proto evolution (field numbers)
─────────────────────────────────────  ─────────────────────────────────────
```

Mahesh's rule: "gRPC is for the kitchen — services talking to services where you control both ends, performance matters, and no browser will ever call this directly."

[Back to Top](#top)

<a id="comparison"></a>

## 6. Head-to-Head Comparison Table

```
Dimension            REST                 GraphQL              gRPC
──────────────────────────────────────────────────────────────────────────────
Transport            HTTP/1.1 or 2        HTTP/1.1 or 2        HTTP/2 required
Payload format       JSON (usually)       JSON                 Binary (protobuf)
Schema/Contract      Implicit (OpenAPI    Explicit (SDL)       Explicit (.proto)
                       optional)
Request model        Multiple endpoints   Single endpoint      RPC methods
Flexibility          Server-driven        Client-driven        Server-driven
Caching              Native HTTP cache    Custom (persisted    Not cacheable via
                       (ETags, CDN)         queries)             HTTP semantics
Real-time            Bolt-on (WS, SSE)    Subscriptions        Native streaming
Performance          Good                 Good                 Excellent
Browser support      Native               Native               grpc-web proxy
Error handling       HTTP status codes    200 + errors array   Status codes + details
Type safety          Weak (JSON)          Strong (schema)      Strong (protobuf)
Versioning           URL/header/media     Schema evolution     Proto field numbers
File uploads         Multipart native     Awkward              Streaming chunks
Learning curve       Low                  Medium               Medium-High
Tooling maturity     Excellent            Good                 Good
Best audience        External devs        Frontend teams       Internal services
──────────────────────────────────────────────────────────────────────────────
```

[Back to Top](#top)

<a id="decision-framework"></a>

## 7. Decision Framework — When to Choose Which

<a id="decision-tree"></a>

**Mahesh's Decision Tree**

When Mahesh's team proposes a new service boundary, he walks through this:

```
                    Who consumes this API?
                           |
            ┌──────────────┼──────────────┐
            |              |              |
      External devs   Our frontend   Our services
      (public API)    (web/mobile)   (internal)
            |              |              |
         REST           Ask:            Ask:
            |         "Do clients      "Is latency
            |          need varied      critical?"
            |          data shapes?"        |
            |              |          ┌────┴────┐
            |         ┌────┴────┐     |         |
            |         |         |    Yes        No
            |        Yes        No    |         |
            |         |         |   gRPC      REST
            |      GraphQL    REST    |      (simpler)
            |         |         |    |
            ▼         ▼         ▼    ▼
```

Additional considerations that override the basic tree:

```
Factor                          Choose...        Reason
──────────────────────────────────────────────────────────────────
Streaming data (logs, events)   gRPC             Native streaming
Browser-only consumers          REST/GraphQL     gRPC needs proxy
Team has no GraphQL experience  REST             Lowest risk
Bandwidth-constrained (IoT)     gRPC             Binary is smallest
Must support webhooks           REST             Standard pattern
Polyglot services (5+ langs)    gRPC             Code gen handles it
Rapid frontend iteration        GraphQL          No backend deploy
                                                   for new fields
──────────────────────────────────────────────────────────────────
```

<a id="real-world-mapping"></a>

**Real-World Mapping**

```
Company        Public API    Mobile App      Internal Services
───────────────────────────────────────────────────────────────
Stripe         REST          REST            ?
GitHub         REST+GraphQL  GraphQL         ?
Netflix        -             GraphQL(Falcor) gRPC
Google         REST          REST            gRPC (Stubby)
Uber           REST          GraphQL         gRPC + Thrift
Shopify        REST+GraphQL  GraphQL         gRPC
Slack          REST          REST            gRPC
───────────────────────────────────────────────────────────────
```

Mahesh notices the pattern: almost everyone uses REST for public, GraphQL for complex frontends, and gRPC (or similar) for internal. The difference is where they draw the boundary.

[Back to Top](#top)

<a id="request-flows"></a>

## 8. Request Flow Diagrams

**REST Request Flow**

```
  Mobile App                    API Gateway              User Service           Database
      |                             |                        |                     |
      |  GET /users/42              |                        |                     |
      |  Authorization: Bearer xyz  |                        |                     |
      |---------------------------->|                        |                     |
      |                             | Validate JWT           |                     |
      |                             | Check rate limit       |                     |
      |                             | Route to service       |                     |
      |                             |----------------------->|                     |
      |                             |                        | SELECT * FROM users  |
      |                             |                        |  WHERE id = 42       |
      |                             |                        |-------------------->|
      |                             |                        |                     |
      |                             |                        |<--------------------|
      |                             |                        |  {row data}          |
      |                             |<-----------------------|                     |
      |                             |  200 OK + JSON body    |                     |
      |<----------------------------|                        |                     |
      |  {"id":42,"name":"Mahesh"}  |                        |                     |
```

**GraphQL Request Flow**

```
  Mobile App                    GraphQL Gateway          User Resolver         Post Resolver
      |                             |                        |                     |
      |  POST /graphql              |                        |                     |
      |  { user(id:42) {            |                        |                     |
      |      name                   |                        |                     |
      |      posts { title }        |                        |                     |
      |  }}                         |                        |                     |
      |---------------------------->|                        |                     |
      |                             | Parse query            |                     |
      |                             | Validate against       |                     |
      |                             |   schema               |                     |
      |                             | Check query depth/cost |                     |
      |                             |----------------------->|                     |
      |                             |                        | fetch user 42       |
      |                             |                        |---> DB              |
      |                             |                        |<--- user data       |
      |                             |                        |                     |
      |                             |  user resolved         |                     |
      |                             |------------------------------------------>|
      |                             |                        |                     |
      |                             |                        |    fetch posts      |
      |                             |                        |    for user 42      |
      |                             |                        |    ---> DB          |
      |                             |                        |    <--- post data   |
      |                             |<------------------------------------------|
      |                             |                        |                     |
      |                             | Assemble response      |                     |
      |<----------------------------|                        |                     |
      |  {"data":{"user":{...}}}    |                        |                     |
```

**gRPC Request Flow**

```
  Order Service              Payment Service (gRPC Server)            Database
      |                             |                                     |
      | ChargeCard(                  |                                     |
      |   user_id=42,               |                                     |
      |   amount=9999,              |                                     |
      |   idempotency_key="abc"     |                                     |
      | )                           |                                     |
      |  [binary protobuf frame]    |                                     |
      |---------------------------->|                                     |
      |                             | Deserialize protobuf                |
      |                             | Validate fields                     |
      |                             | Check idempotency key               |
      |                             |----------------------------------->|
      |                             |                                     |
      |                             |<-----------------------------------|
      |                             |  {charge record}                    |
      |                             |                                     |
      |  ChargeResponse(            |                                     |
      |    status=SUCCESS,          |                                     |
      |    charge_id="ch_xyz"       |                                     |
      |  )                          |                                     |
      |  [binary protobuf frame]    |                                     |
      |<----------------------------|                                     |
```

[Back to Top](#top)

<a id="contract-design"></a>

## 9. API Contract Design

<a id="versioning"></a>

**Versioning Strategies**

APIs change. Mahesh needs a strategy that does not break existing consumers when the schema evolves.

```
Strategy          Example                     Pros                    Cons
──────────────────────────────────────────────────────────────────────────────────────
URL versioning    GET /v2/users/42            Simple, explicit,       URL pollution,
                                                 cacheable              routing complexity

Header version    X-API-Version: 2            Clean URLs,             Hidden from logs,
                                                 flexible               harder to test

Media type        Accept: application/        RESTful, granular       Complex content
                    vnd.myapi.v2+json                                    negotiation

Query param       GET /users/42?version=2     Easy to test            Caching issues,
                                                                        feels hacky
──────────────────────────────────────────────────────────────────────────────────────
```

Mahesh's choice: **URL versioning for public APIs** (Stripe, GitHub, Twitter all do this). Simplicity wins when thousands of unknown developers will consume your API.

For GraphQL: **No versioning needed** — add new fields, deprecate old ones with `@deprecated(reason: "Use nameV2 instead")`. The schema evolves without breaking clients.

For gRPC: **Field numbers are forever** — never reuse a deleted field number. Add new fields with new numbers. This is proto's built-in versioning.

<a id="backward-compat"></a>

**Backward Compatibility Rules**

Mahesh's team follows these rules to avoid breaking consumers:

```
SAFE CHANGES (non-breaking):            BREAKING CHANGES (need new version):
─────────────────────────────────────   ─────────────────────────────────────
Add a new field to response             Remove a field from response
Add a new optional query parameter      Rename a field
Add a new endpoint                      Change a field's type
Add a new enum value (if client         Make an optional field required
  handles unknowns gracefully)          Change URL structure
Relax a validation (accept more)        Tighten a validation (reject more)
Increase a rate limit                   Decrease a rate limit
Add a new error code                    Change the meaning of a status code
─────────────────────────────────────   ─────────────────────────────────────
```

<a id="idempotency"></a>

**Idempotency Keys**

Mahesh's payment service processes charges. If a network timeout occurs and the client retries, it must not double-charge. Solution: idempotency keys.

```
First attempt:
  POST /charges
  Idempotency-Key: "abc-123-def"
  {"amount": 5000, "currency": "USD"}

  Response: 201 Created {"id": "ch_1", "amount": 5000}
  Server stores: key "abc-123-def" -> response

Retry (network timeout, same key):
  POST /charges
  Idempotency-Key: "abc-123-def"
  {"amount": 5000, "currency": "USD"}

  Response: 201 Created {"id": "ch_1", "amount": 5000}  <-- same response
  Server sees key exists -> returns cached response, no new charge
```

Implementation pattern:

```
1. Client generates a unique key (UUID) before the first attempt
2. Server checks if key exists in idempotency store (Redis/DB)
3. If exists: return stored response (no side effects)
4. If not: process request, store response keyed by idempotency key
5. Keys expire after 24-48 hours (configurable)
```

[Back to Top](#top)

<a id="api-gateway"></a>

## 10. API Gateway Patterns

<a id="gateway-traffic"></a>

**Gateway as Traffic Controller**

An API gateway sits between clients and backend services. It handles cross-cutting concerns so services do not have to.

```
                          ┌─────────────────────────────────┐
                          |          API GATEWAY             |
  Mobile App ────────────>|                                 |
                          |  - Authentication (JWT verify)  |──► User Service
  Web Dashboard ─────────>|  - Rate limiting                |──► Order Service
                          |  - Request routing              |──► Payment Service
  External Devs ─────────>|  - TLS termination              |──► Notification Svc
                          |  - Request/response transform   |──► Analytics Service
  Internal Services ─────>|  - Logging and metrics          |
                          |  - Circuit breaking             |
                          └─────────────────────────────────┘
```

Popular gateways: Kong, AWS API Gateway, Nginx, Envoy, Traefik.

<a id="bff"></a>

**Backend-for-Frontend (BFF)**

Mahesh notices his mobile team and web team want different response shapes from the same data. Instead of one gateway trying to serve both, he creates dedicated backends:

```
  Mobile App ──────► Mobile BFF ──────┐
                     (slim responses,  |
                      aggregates 3     |──► Shared Microservices
                      calls into 1)    |      (User, Order, Payment)
                                       |
  Web Dashboard ───► Web BFF ─────────┘
                     (rich responses,
                      dashboard-optimized
                      aggregations)
```

BFF pattern works well when:
- Different clients need radically different response shapes
- You want to avoid GraphQL complexity
- Each frontend team wants to own their backend

BFF pattern is overkill when:
- All clients need roughly the same data
- You only have one frontend
- GraphQL already solves the flexibility problem

[Back to Top](#top)

<a id="pagination"></a>

## 11. Pagination Patterns

Never return 10 million records at once. Mahesh's team uses two patterns:

```
OFFSET-BASED                           CURSOR-BASED
──────────────────────────────────     ──────────────────────────────────────
GET /posts?page=3&limit=20             GET /posts?after=eyJpZCI6MTAwfQ&limit=20

Simple to implement                    Stable under writes (inserts/deletes)
Familiar to frontend devs              No skipped/duplicated items
"Jump to page 50" works                Scales to billions of rows

BUT: skips/duplicates if data          BUT: no "jump to page N"
  changes between pages                Cannot go backward easily
Slow on large offsets (DB scans        Cursor must be opaque to client
  skip N rows)

Best for: admin dashboards,            Best for: infinite scroll feeds,
  small datasets, internal tools         social timelines, large datasets
──────────────────────────────────     ──────────────────────────────────────
```

Cursor-based response shape:

```json
{
  "data": [...],
  "pagination": {
    "has_next": true,
    "next_cursor": "eyJpZCI6MTAwLCJjcmVhdGVkX2F0IjoiMjAyNC0wMS0xNSJ9",
    "has_previous": true,
    "previous_cursor": "eyJpZCI6ODEsImNyZWF0ZWRfYXQiOiIyMDI0LTAxLTE0In0="
  }
}
```

The cursor is a base64-encoded composite of the sort fields (e.g., `{"id": 100, "created_at": "2024-01-15"}`). This is opaque to the client but allows the server to efficiently query `WHERE (created_at, id) > (?, ?)`.

[Back to Top](#top)

<a id="rate-limiting"></a>

## 12. Rate Limiting at the API Layer

Mahesh protects his public API from abuse and ensures fair usage across tenants.

```
Algorithm            How It Works                         Best For
──────────────────────────────────────────────────────────────────────────
Token Bucket         Bucket fills at fixed rate.          Bursty traffic allowed
                     Each request takes a token.          (e.g., 100 req/min but
                     Empty bucket = rejected.             allow 20 in 1 second)

Leaky Bucket         Requests enter a queue.              Smooth output rate
                     Queue drains at fixed rate.          (e.g., video streaming)
                     Full queue = rejected.

Fixed Window         Count requests per time window.      Simple to implement
                     Reset count at window boundary.      (e.g., 1000/hour)
                     Edge case: burst at boundary.

Sliding Window Log   Track timestamp of each request.     Accurate but memory-
                     Count within sliding window.         heavy. Good for
                     Most accurate.                       critical limits.

Sliding Window       Weighted combination of current      Balance of accuracy
  Counter            and previous window counts.          and efficiency.
──────────────────────────────────────────────────────────────────────────
```

Rate limit headers Mahesh includes in every response:

```
X-RateLimit-Limit: 1000          # max requests per window
X-RateLimit-Remaining: 847       # requests left in window
X-RateLimit-Reset: 1704067200    # unix timestamp when window resets
Retry-After: 30                  # seconds to wait (on 429 only)
```

[Back to Top](#top)

<a id="common-mistakes"></a>

## 13. Common Mistakes

Mahesh has seen every mistake in his 15 years. Here are the ones that cost teams weeks:

**Mistake 1: Using GraphQL for everything**

A team used GraphQL for service-to-service calls. Result: query parsing overhead on every internal request, no HTTP caching, debugging nightmares. Fix: GraphQL is for client-server boundaries with diverse consumers. Internal services should use gRPC or simple REST.

**Mistake 2: No idempotency keys on state-changing endpoints**

A payment service without idempotency keys double-charged 200 users during a network partition. The client retried, the server processed again. Fix: every POST/PUT that causes side effects must accept an idempotency key.

**Mistake 3: Returning 200 for errors**

```json
HTTP 200 OK
{"success": false, "error": "User not found"}
```

This breaks HTTP caching, confuses monitoring tools, and violates the principle of least surprise. Fix: use appropriate 4xx/5xx status codes. The body can add detail, but the status code must be semantically correct.

**Mistake 4: Designing APIs around database tables**

```
Bad:  GET /user_profiles_table?columns=name,email
Good: GET /users/42
```

APIs represent business resources, not database schemas. If you rename a table, your API should not break.

**Mistake 5: No pagination on list endpoints**

A service returned all 2 million records on `GET /events`. One call consumed 4GB of memory and crashed the pod. Fix: every list endpoint must paginate. Default page size should be small (20-50). Maximum page size should be enforced (100-200).

**Mistake 6: Breaking changes without versioning**

A team renamed `user_name` to `username` in a response without incrementing the version. 47 integration partners broke overnight. Fix: follow the backward compatibility rules above. When in doubt, add a new field and deprecate the old one.

**Mistake 7: Exposing internal IDs**

Using auto-increment integer IDs (`/users/1`, `/users/2`) in public APIs leaks information (total user count, creation order) and enables enumeration attacks. Fix: use UUIDs or typed prefixes (`usr_a1b2c3d4`).

**Mistake 8: Ignoring content negotiation**

Returning JSON when the client sent `Accept: text/xml` without a proper 406 response. Fix: respect the `Accept` header. If you only support JSON, return `406 Not Acceptable` for other media types.

[Back to Top](#top)

<a id="interview-scenarios"></a>

## 14. Interview Decision Scenarios

Mahesh uses these scenarios to test API design thinking in interviews:

**Scenario 1: "Design the API for a ride-sharing app"**

```
Boundary                   Choice        Reasoning
─────────────────────────────────────────────────────────────────
Public driver API          REST          Third-party integrators
Rider mobile app           GraphQL       Complex screens, varied data
Driver location stream     gRPC          High-frequency, low-latency
Pricing <-> Trip service   gRPC          Internal, latency-critical
Trip <-> Notification      REST/async    Fire-and-forget via queue
Admin dashboard            REST          Simple CRUD, few users
```

**Scenario 2: "Your API has 10,000 partners. How do you deprecate a field?"**

```
1. Add new field alongside old one (non-breaking)
2. Mark old field as deprecated in docs/schema
3. Add deprecation sunset header: Sunset: Sat, 01 Mar 2025 00:00:00 GMT
4. Email partners with 6-month migration timeline
5. Monitor usage of deprecated field via API analytics
6. After sunset: return warning header for 1 month
7. Finally remove (this is a breaking change, new version)
```

**Scenario 3: "GraphQL vs REST for a mobile banking app?"**

Think through it:
- Banking app has strict, well-defined screens (not dynamic)
- Security auditing needs clear request/response logging
- Caching account balances is critical for performance
- Regulatory compliance requires predictable API behavior

Answer: **REST** — despite being a mobile app. The predictable nature of banking screens, need for HTTP caching, security auditing (every endpoint is auditable), and regulatory requirements all favor REST's simplicity. GraphQL's flexibility is a liability when you need strict control over data access patterns.

**Scenario 4: "How do you handle API versioning for 500 microservices?"**

```
Strategy:
- External APIs: URL versioning (v1, v2) — explicit, discoverable
- Internal APIs (gRPC): Proto field numbers — backward compatible by default
- Contract testing: Every service publishes its contract (proto or OpenAPI)
- Consumer-driven contracts: Downstream services define what they need
- Breaking change process:
    1. PR must tag "breaking-change" label
    2. Automated compatibility checker runs against consumer contracts
    3. If any consumer breaks -> PR is blocked until consumers update
    4. Canary deploy: route 1% of traffic to new version first
```

[Back to Top](#top)

<a id="summary"></a>

## 15. Summary

```
 ┌─────────────────────────────────────────────────────────────────────┐
 |                    API DESIGN DECISION SUMMARY                       |
 ├─────────────────────────────────────────────────────────────────────┤
 |                                                                     |
 |  REST:     Universal default. Public APIs. Simple CRUD. Cacheable.  |
 |            "When in doubt, REST."                                   |
 |                                                                     |
 |  GraphQL:  Diverse clients, complex data needs, mobile-first.       |
 |            "When frontends need flexibility without backend deploy." |
 |                                                                     |
 |  gRPC:     Internal services. High throughput. Streaming.           |
 |            "When machines talk to machines and speed matters."       |
 |                                                                     |
 ├─────────────────────────────────────────────────────────────────────┤
 |                                                                     |
 |  Contract design:  Version explicitly. Never break silently.        |
 |  Idempotency:      Every state-changing call needs a retry story.   |
 |  Gateway:          Centralize auth, rate limits, routing.           |
 |  Pagination:       Cursor-based for feeds. Offset for dashboards.   |
 |  Rate limiting:    Token bucket for bursty. Sliding window for      |
 |                      accuracy. Always return limit headers.         |
 |                                                                     |
 └─────────────────────────────────────────────────────────────────────┘
```

Mahesh's final wisdom: "The best API is boring to consume. No surprises, no cleverness, no magic. Just predictable contracts that let teams move independently."

[Back to Top](#top)

## Navigation

| | |
|---|---|
| Previous | [02 - System Fundamentals](../02_system_fundamentals/theory.md) |
| Next | [04 - Backend Architecture](../04_backend_architecture/theory.md) |
| Interview | [interview.md](./interview.md) |
| Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| Home | [README.md](../README.md) |

**[Back to README](../README.md)**

**Prev:** [System Fundamentals](../02_system_fundamentals/theory.md) | **Next:** [Backend Architecture](../04_backend_architecture/theory.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) | [Interview Q&A](./interview.md) | [Overview](./overview.md)
