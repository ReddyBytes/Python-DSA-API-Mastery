# GraphQL — When the Client Gets to Drive

> 📝 **Practice:** [Q81 · compare-rest-graphql](../api_practice_questions_100.md#q81--interview--compare-rest-graphql)

> 📝 **Practice:** [Q62 · graphql-n-plus-one](../api_practice_questions_100.md#q62--thinking--graphql-n-plus-one)

> 📝 **Practice:** [Q61 · graphql-vs-rest](../api_practice_questions_100.md#q61--interview--graphql-vs-rest)

> 📝 **Practice:** [Q97 · design-rest-vs-graphql](../api_practice_questions_100.md#q97--design--design-rest-vs-graphql)

## The Monday Morning Problem

It's Monday morning. You're building the mobile app for an e-commerce startup.
The designer hands you a new screen mockup: a profile card that shows the user's
name, their last three orders, and a badge showing how many unread notifications
they have.

You go to the backend team. They have a REST API.

"Great," they say. "Here are the endpoints you need:"

```
GET /users/42              -> returns 47 fields about the user
GET /users/42/orders       -> returns all orders (with 23 fields each)
GET /users/42/notifications?status=unread  -> returns all unread notifications
```

So to render one screen, your mobile app has to:
1. Make three separate HTTP requests
2. Download the full user object (47 fields, you need 3)
3. Download all orders (you need the last 3, you get all 200)
4. Download all unread notifications (you need a count, you get the full objects)

Your phone is on a slow 4G connection. Each round-trip is 150ms. You're downloading
kilobytes of data you immediately throw away.

This is the everyday reality that GraphQL was built to fix.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
schema definition · queries · mutations · resolvers

**Should Learn** — Important for real projects:
DataLoader · subscriptions

**Good to Know** — Useful in specific situations:
federation

**Reference** — Know it exists, look up syntax when needed:
Persisted queries

---

## The Two Problems REST Can't Shake

### Problem 1: Over-Fetching

You ask for a user, you get everything about the user.

```
GET /users/42

Response (47 fields, you needed 3):
{
  "id": 42,
  "name": "Alice Chen",            <- you wanted this
  "email": "alice@example.com",    <- you wanted this
  "avatar_url": "...",             <- you wanted this
  "phone": "+1-555-0100",
  "date_of_birth": "1990-05-15",
  "address_line_1": "123 Main St",
  "address_line_2": null,
  "city": "Austin",
  "state": "TX",
  "country": "US",
  "postal_code": "78701",
  "billing_address_id": 7,
  "shipping_address_id": 8,
  "created_at": "2021-03-12T10:05:00Z",
  "updated_at": "2024-01-08T14:22:00Z",
  "last_login": "2024-01-09T09:15:00Z",
  "timezone": "America/Chicago",
  "locale": "en-US",
  "is_verified": true,
  "is_active": true,
  "subscription_tier": "premium",
  "subscription_expires_at": "2024-12-31T00:00:00Z",
  ... 23 more fields ...
}
```

The server always returns the whole object. You wanted three fields. You got forty-seven.

On a mobile device with limited bandwidth and battery, this adds up fast.

### Problem 2: Under-Fetching (The N+1 Requests Problem)

The flip side: one endpoint doesn't give you enough, so you have to make more calls.

```
Screen needs: user name + last 3 orders + unread notification count

Call 1: GET /users/42
Call 2: GET /users/42/orders
Call 3: GET /users/42/notifications

Three round trips. 450ms minimum on a decent connection.
On mobile in a weak signal area: easily 2+ seconds.
```

And this is for a simple profile screen. Complex dashboards can require 10+ API calls
before the page can render anything meaningful. Users stare at loading spinners.

### Problem 3: Endpoint Explosion

The design team wants a mobile view and a desktop view. Same data, different shapes.

The mobile view needs: `name, avatar, order_count`
The desktop view needs: `name, email, avatar, orders[last5], stats, address`

With REST, you have options — none of them great:

- **Option A:** Make separate endpoints — `/users/42/mobile-summary` and
  `/users/42/desktop-profile`. Now you're writing custom endpoints for every UI view.
  The backend becomes a slave to the frontend.
- **Option B:** Over-fetch everywhere — always return everything, let the client
  pick what it needs. Wastes bandwidth. Gets slow on mobile.
- **Option C:** Query parameters — `GET /users/42?fields=name,email,orders`. Custom
  field selection logic the team has to build and maintain from scratch.

None of these scale well as your UI grows.

---

## Enter GraphQL

Facebook engineers were dealing with this exact problem in 2012. They were rebuilding
the Facebook mobile app. The REST API was returning massive payloads. The mobile app
was slow. Engineers were spending half their time writing new REST endpoints for every
slightly-different UI requirement.

So they built GraphQL internally. In 2015, they open-sourced it.

The core idea is elegant:

**The client describes exactly what data it wants. The server returns exactly that.**

```
GraphQL mental model:

Client: "Give me user 42's name, email, and their last 3 order IDs and totals."
Server: "Here is exactly that. Nothing more, nothing less."
```

A few key things make this possible:

**Single endpoint.** All GraphQL requests go to one place: `POST /graphql`.
No `/users`, no `/orders`, no `/products`. One URL. Everything goes through it.

**Query language.** The request body isn't JSON — it's a query written in GraphQL's
own language. The query describes the shape of the data you want.

**Typed schema.** The server publishes a schema — a complete description of every
type of data available and every operation you can perform. It's like documentation
that's also enforced by the runtime.

**The client is in control of the shape.** This is the key shift. REST says "here's
what we give you." GraphQL says "tell us what you want."

---

## The Schema — The Contract

Before writing any queries, you need to understand the schema. It's the backbone of
every GraphQL API — a typed description of all your data and all your operations.

```graphql
# Types — the data structures available
type User {
  id: ID!
  name: String!
  email: String!
  phone: String           # No ! means nullable (optional)
  orders: [Order!]!       # List of Order objects, never null
  notificationCount: Int!
}

type Order {
  id: ID!
  total: Float!
  status: String!
  createdAt: String!
  items: [OrderItem!]!
}

type OrderItem {
  id: ID!
  productName: String!
  quantity: Int!
  price: Float!
}

# Query type — defines what you can READ
type Query {
  user(id: ID!): User         # Get one user by ID
  users: [User!]!             # Get all users
  order(id: ID!): Order       # Get one order by ID
}

# Mutation type — defines what you can CREATE/UPDATE/DELETE
type Mutation {
  createUser(name: String!, email: String!): User!
  updateUser(id: ID!, name: String, email: String): User!
  deleteUser(id: ID!): Boolean!
  createOrder(userId: ID!, items: [OrderItemInput!]!): Order!
}

# Subscription type — defines real-time events you can LISTEN to
type Subscription {
  orderStatusUpdated(orderId: ID!): Order!
  newNotification(userId: ID!): Notification!
}
```

The `!` after a type means "non-null" — this field is always present and never null.
`[Order!]!` means the list itself is non-null, and every item in it is non-null.

This schema is published by the server. It's introspectable — clients can query the
schema itself to discover what's available. Tools like GraphiQL use this to give you
auto-complete as you type queries.

---

## Queries — Fetching Data

Now let's solve the Monday morning problem with a GraphQL query.

```graphql
query GetProfileScreen {
  user(id: "42") {
    name
    email
    avatarUrl
    orders {
      id
      total
      status
    }
    notificationCount
  }
}
```

That's one request. One HTTP call. The response contains exactly what you asked for:

```json
{
  "data": {
    "user": {
      "name": "Alice Chen",
      "email": "alice@example.com",
      "avatarUrl": "https://cdn.example.com/avatars/42.jpg",
      "orders": [
        {"id": "ord_101", "total": 89.99, "status": "delivered"},
        {"id": "ord_102", "total": 24.50, "status": "shipped"},
        {"id": "ord_103", "total": 156.00, "status": "processing"}
      ],
      "notificationCount": 3
    }
  }
}
```

No extra fields. No extra requests. The profile screen can render immediately.

Compare that to the REST approach:

```
REST: 3 separate HTTP calls
  GET /users/42              -> 150ms, 47 fields (3 needed)
  GET /users/42/orders       -> 150ms, 200 orders (3 needed), 23 fields each
  GET /users/42/notifications -> 150ms, full notification objects (count needed)

  Total: ~450ms minimum, downloading ~15KB, using ~1KB

GraphQL: 1 HTTP call
  POST /graphql              -> 150ms, exactly what you need
  Total: ~150ms, downloading ~1KB, using ~1KB
```

The difference gets more dramatic as screens get more complex.

### Variables — Making Queries Dynamic

Hardcoding `"42"` in your query is fine for exploration but impractical for a real
app. GraphQL supports variables:

```graphql
# Define variables in the query signature
query GetProfileScreen($userId: ID!) {
  user(id: $userId) {
    name
    email
    orders {
      id
      total
      status
    }
  }
}
```

You send the query and variables separately in the request body:

```json
{
  "query": "query GetProfileScreen($userId: ID!) { ... }",
  "variables": {
    "userId": "42"
  }
}
```

This is cleaner and safer than string interpolation. It also enables caching — the
query text stays the same, only the variables change.

### Aliases — Same Field, Different Arguments

What if you need to fetch two users at once? You can alias fields:

```graphql
query CompareTwoUsers {
  alice: user(id: "1") {
    name
    email
  }
  bob: user(id: "2") {
    name
    email
  }
}
```

Response:
```json
{
  "data": {
    "alice": {"name": "Alice", "email": "alice@example.com"},
    "bob":   {"name": "Bob",   "email": "bob@example.com"}
  }
}
```

---

## Mutations — Changing Data

Queries are for reading. Mutations are for writing — create, update, delete.

```graphql
mutation CreateNewUser {
  createUser(name: "David Kim", email: "david@example.com") {
    id
    name
    email
  }
}
```

Notice you also specify what you want back. After creating the user, you can
immediately ask for their server-generated ID and any computed fields. No need
for a follow-up GET request.

```json
{
  "data": {
    "createUser": {
      "id": "usr_8823",
      "name": "David Kim",
      "email": "david@example.com"
    }
  }
}
```

Updating with variables — the real-world pattern:

```graphql
mutation UpdateUserEmail($userId: ID!, $newEmail: String!) {
  updateUser(id: $userId, email: $newEmail) {
    id
    email
    updatedAt
  }
}
```

```json
{
  "query": "mutation UpdateUserEmail(...) { ... }",
  "variables": {
    "userId": "42",
    "newEmail": "alice.new@example.com"
  }
}
```

---

## Subscriptions — Real-Time Updates

Queries and mutations are request-response — you ask, you get an answer, connection
closes. Subscriptions are different. They open a persistent connection (usually via
WebSocket) and the server sends you data whenever something relevant happens.

```graphql
subscription WatchOrderStatus($orderId: ID!) {
  orderStatusUpdated(orderId: $orderId) {
    id
    status
    updatedAt
  }
}
```

Once subscribed, every time that order's status changes in the system, your client
receives a push notification — no polling, no repeated requests.

```
Client                              Server
  |                                   |
  |  subscribe: orderStatusUpdated    |
  |  ───────────────────────────>     |
  |                                   |  (processing...)
  |  {id: "101", status: "shipped"}   |
  |  <───────────────────────────     |
  |                                   |  (processing...)
  |  {id: "101", status: "delivered"} |
  |  <───────────────────────────     |
  |                                   |
```

Subscriptions are perfect for: order tracking, live scores, collaborative editing,
live auction bids, real-time dashboards.

---

## How Resolvers Work (and Why It Matters)

Here's something you need to understand before deploying GraphQL in production:
the execution model.

When GraphQL receives a query, it executes resolvers — functions you write that
know how to fetch each piece of data.

```python
# Simplified resolver example
class Query:
    def user(self, info, id):
        # Called once per query
        return db.query("SELECT * FROM users WHERE id = ?", id)

class User:
    def orders(self, info):
        # Called once per User object in the result
        user_id = self.id
        return db.query("SELECT * FROM orders WHERE user_id = ?", user_id)
```

For a single user query, this works fine. But here's where things get painful.

---

## The N+1 Problem — GraphQL's Biggest Gotcha

You build a query to get all users with their orders:

```graphql
query AllUsersWithOrders {
  users {
    name
    email
    orders {
      id
      total
    }
  }
}
```

The execution flow looks like this:

```
1. Resolve users:
   SELECT * FROM users
   -> returns 100 user rows

2. For user[0], resolve orders:
   SELECT * FROM orders WHERE user_id = 1

3. For user[1], resolve orders:
   SELECT * FROM orders WHERE user_id = 2

4. For user[2], resolve orders:
   SELECT * FROM orders WHERE user_id = 3

... keep going ...

101. For user[99], resolve orders:
     SELECT * FROM orders WHERE user_id = 100
```

**100 users + 1 query to get them = 101 database queries.**

That's the N+1 problem. You fetched N=100 users, then fired 1 query per user to get
their orders. This can destroy your database under any real load.

```
N users -> N+1 queries

  100 users  -> 101 DB queries
  1000 users -> 1001 DB queries
  10000 users -> 10001 DB queries   <- your DBA is crying
```

### The Fix: DataLoader

The solution is batching. Instead of running each resolver immediately, you collect
all the IDs you need and fire one query for all of them.

Facebook built DataLoader for exactly this purpose. It's now available in every
major GraphQL ecosystem.

```python
# Without DataLoader:           With DataLoader:

# 100 separate queries          # 1 batched query
SELECT * FROM orders            SELECT * FROM orders
WHERE user_id = 1               WHERE user_id IN (1,2,3,...,100)

SELECT * FROM orders
WHERE user_id = 2
...
```

How DataLoader works conceptually:

```
During one tick of the event loop, DataLoader collects all IDs requested.
At the end of the tick, it fires a single batch query.
It maps the results back to the original requesters.

Timeline:
  tick starts
    user[0].orders requested -> DataLoader: "noted, I'll batch this"
    user[1].orders requested -> DataLoader: "noted, I'll batch this"
    user[2].orders requested -> DataLoader: "noted, I'll batch this"
    ...
  tick ends
    DataLoader fires: SELECT * FROM orders WHERE user_id IN (1,2,3,...)
    DataLoader distributes results back to each resolver
```

```python
# Python example with Strawberry GraphQL + DataLoader

from strawberry.dataloader import DataLoader

async def load_orders_by_user_id(user_ids: list[str]) -> list[list[Order]]:
    # One query for ALL user IDs at once
    all_orders = await db.fetch_all(
        "SELECT * FROM orders WHERE user_id = ANY(:ids)",
        {"ids": user_ids}
    )
    # Group by user_id and return in the same order as user_ids
    orders_by_user = {uid: [] for uid in user_ids}
    for order in all_orders:
        orders_by_user[order.user_id].append(order)
    return [orders_by_user[uid] for uid in user_ids]

orders_loader = DataLoader(load_fn=load_orders_by_user_id)
```

**Bottom line:** Any time you write a resolver that fetches from a database based
on a parent object's ID, use DataLoader. Non-negotiable in production.

---

## A Python GraphQL Server (Strawberry)

Let's wire up a minimal working GraphQL server in Python. We'll use Strawberry —
the most Pythonic GraphQL library, built with type hints.

```bash
pip install strawberry-graphql fastapi uvicorn
```

```python
# server.py
import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from typing import Optional

# --- Type definitions ---

@strawberry.type
class Order:
    id: str
    total: float
    status: str

@strawberry.type
class User:
    id: str
    name: str
    email: str

    @strawberry.field
    def orders(self) -> list[Order]:
        # In production, use DataLoader here
        return fake_orders_db.get(self.id, [])


# --- Fake data ---

fake_users_db = {
    "1": User(id="1", name="Alice Chen", email="alice@example.com"),
    "2": User(id="2", name="Bob Smith", email="bob@example.com"),
}

fake_orders_db = {
    "1": [
        Order(id="ord_1", total=89.99, status="delivered"),
        Order(id="ord_2", total=24.50, status="shipped"),
    ],
    "2": [
        Order(id="ord_3", total=156.00, status="processing"),
    ],
}


# --- Resolvers ---

@strawberry.type
class Query:
    @strawberry.field
    def user(self, id: str) -> Optional[User]:
        return fake_users_db.get(id)

    @strawberry.field
    def users(self) -> list[User]:
        return list(fake_users_db.values())


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_user(self, name: str, email: str) -> User:
        new_id = str(len(fake_users_db) + 1)
        user = User(id=new_id, name=name, email=email)
        fake_users_db[new_id] = user
        return user


# --- App setup ---

schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")
```

Run it:
```bash
uvicorn server:app --reload
```

Now visit `http://localhost:8000/graphql` — you get GraphiQL, an interactive
in-browser IDE where you can explore the schema and run queries.

Try this query:
```graphql
query {
  user(id: "1") {
    name
    email
    orders {
      id
      total
      status
    }
  }
}
```

---

## When GraphQL Wins

GraphQL is a genuinely better solution in certain situations. Knowing when to reach
for it is just as important as knowing how to use it.

**Complex UIs with varied data requirements.**
You have a mobile app, a web app, and a desktop app. Each needs a different shape
of data from the same underlying models. GraphQL lets each client ask for exactly
what it needs — no custom endpoints, no over-fetching.

```
Mobile:   { name, avatar, orderCount }
Web:      { name, email, avatar, orders[last5], address }
Desktop:  { name, email, all orders, full stats, preferences }

Same GraphQL schema. Three different queries. Everyone's happy.
```

**Aggregation layer over multiple backend services.**
You have microservices: UserService, OrderService, InventoryService, NotificationService.
Your frontend needs data from all four for one screen. With REST, the frontend hits
four separate services. With GraphQL, you build one GraphQL gateway that federates
across all services — the frontend makes one request, the gateway fans out internally.

```
Client ──── POST /graphql ────> GraphQL Gateway
                                    |     |     |     |
                                    v     v     v     v
                                 Users Orders Inventory Notif
                                 Svc   Svc    Svc       Svc
```

**Rapid prototyping when data requirements change constantly.**
Early in a product's life, the frontend team is constantly changing what data they
need. With REST, every change requires a backend engineer to update an endpoint.
With GraphQL, the frontend team can often get new data combinations without touching
the backend at all — as long as the underlying types are already in the schema.

---

## When to Stick with REST

GraphQL is not a universal upgrade. There are real situations where REST is the
better choice.

**Simple CRUD APIs.**
If your API is basically a thin wrapper over a database — create a user, read a user,
update a user, delete a user — REST is simpler to build, simpler to understand, and
simpler to maintain. GraphQL's power-to-complexity ratio only favors GraphQL when you
actually need that flexibility.

**Public APIs.**
GraphQL's introspection feature — which lets clients query the schema itself — is
incredibly powerful for developers. It's also a potential information disclosure risk.
An attacker can use introspection to map your entire data model. You can disable
introspection in production, but then you lose one of GraphQL's best features.
Many public APIs (Stripe, Twilio, GitHub's REST API) stick with REST for this reason.

**File uploads.**
Sending binary data through GraphQL is awkward. You end up encoding files as base64
(which inflates size by ~33%) or using multipart form hacks. REST handles file uploads
naturally with `multipart/form-data`. Use REST for file uploads.

**HTTP caching.**
REST's cache story is simple: `GET /users/42` can be cached at the CDN, proxy, or
browser level using standard HTTP headers. GraphQL's queries are all `POST` requests
to the same URL — standard HTTP caches don't know how to cache them. GraphQL has
workarounds (persisted queries, query-specific caching), but none are as simple as
REST's built-in HTTP cache semantics. If cache hit rate is critical to your
performance strategy, REST is easier.

**Teams unfamiliar with GraphQL.**
This is real. A REST API that your team understands deeply is better than a GraphQL
API your team struggles with. Technology choices are team choices.

---

## The Mental Model

```
REST                          GraphQL
─────────────────────────     ──────────────────────────
Server defines shape          Client defines shape
Many endpoints                One endpoint
GET /users/42/orders          query { user(id:"42") { orders { ... } } }
Fixed response                Requested response
HTTP caching works            Caching is complex
Simple to build               More infrastructure needed
Good for: simple APIs         Good for: complex UIs, federation
         public APIs                   rapid product iteration
         file uploads                  mobile performance
```

---

## Summary

GraphQL solves a real problem: the mismatch between what REST gives you and what
your UI actually needs. It shifts control of the data shape from the server to the
client — a small change with big consequences for developer productivity and API
performance.

The core ideas to remember:

```
What it is:   A query language for APIs (not a database query language)
Single URL:   POST /graphql — everything goes through here
Schema:       Typed definition of every operation available
Queries:      Ask for exactly the fields you need
Mutations:    Create, update, delete — and get back what you want
Subscriptions: Real-time push via WebSocket
N+1 Problem:  The main performance trap — use DataLoader to solve it
```

You now understand GraphQL well enough to make an informed decision about when to
use it and — just as important — when not to. That's the senior engineering mindset.
Not "GraphQL is better than REST." It's "GraphQL is better for this problem, in this
context, with this team."

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Production Deployment](../12_production_deployment/deployment_guide.md) &nbsp;|&nbsp; **Next:** [gRPC →](../14_grpc/grpc_guide.md)

**Related Topics:** [gRPC](../14_grpc/grpc_guide.md) · [API Gateway Patterns](../15_api_gateway/gateway_patterns.md) · [REST Fundamentals](../02_rest_fundamentals/rest_explained.md) · [WebSockets & Real-Time APIs](../17_websockets/realtime_apis.md)
