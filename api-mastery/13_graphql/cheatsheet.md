# ⚡ Cheatsheet: GraphQL

---

## Learning Priority

**Must Learn** — foundation for any GraphQL work:
Schema definition language · query/mutation syntax · resolver pattern · REST vs GraphQL comparison

**Should Learn** — required for production GraphQL:
Variables · fragments · DataLoader pattern (N+1 fix) · error handling shape

**Good to Know** — advanced usage:
Subscriptions · introspection · schema directives · federation

**Reference** — look up when needed:
Apollo Federation spec · Relay cursor spec · persisted queries

---

## Schema Definition Language (SDL)

```graphql
# Scalar types
String    Int    Float    Boolean    ID

# Object type
type User {
  id: ID!              # ! = non-null
  email: String!
  name: String
  posts: [Post!]!      # non-null list of non-null Post objects
  createdAt: String!
}

type Post {
  id: ID!
  title: String!
  body: String!
  author: User!
  tags: [String!]
  published: Boolean!
}

# Input type (for mutations)
input CreatePostInput {
  title: String!
  body: String!
  tags: [String!]
}

# Enum
enum PostStatus {
  DRAFT
  PUBLISHED
  ARCHIVED
}

# Interface
interface Node {
  id: ID!
}

# Union
union SearchResult = User | Post

# Root types
type Query {
  user(id: ID!): User
  users(limit: Int = 10, offset: Int = 0): [User!]!
  post(id: ID!): Post
  search(query: String!): [SearchResult!]!
}

type Mutation {
  createPost(input: CreatePostInput!): Post!
  updatePost(id: ID!, input: CreatePostInput!): Post
  deletePost(id: ID!): Boolean!
}

type Subscription {
  postPublished: Post!
  userActivity(userId: ID!): ActivityEvent!
}
```

---

## Query Syntax

```graphql
# Basic query
query {
  user(id: "42") {
    id
    email
    name
  }
}

# Named query (best practice — easier to debug)
query GetUser {
  user(id: "42") {
    id
    email
    posts {
      id
      title
    }
  }
}

# Query with variables
query GetUser($userId: ID!) {
  user(id: $userId) {
    id
    email
    name
  }
}
# Variables (sent alongside the query as JSON):
# { "userId": "42" }

# Multiple fields in one request
query Dashboard {
  currentUser: user(id: "42") {
    name
    email
  }
  recentPosts: posts(limit: 5) {
    id
    title
    author {
      name
    }
  }
}
```

---

## Mutation Syntax

```graphql
# Basic mutation
mutation {
  createPost(input: { title: "Hello", body: "World" }) {
    id
    title
    author {
      name
    }
  }
}

# With variables (always use this in practice)
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    id
    title
    published
  }
}
# Variables: { "input": { "title": "Hello", "body": "World" } }
```

---

## Subscription Syntax

```graphql
# Client subscribes over WebSocket
subscription {
  postPublished {
    id
    title
    author {
      name
    }
  }
}

subscription WatchUser($userId: ID!) {
  userActivity(userId: $userId) {
    type
    timestamp
    metadata
  }
}
```

---

## Resolver Pattern (Python — Strawberry)

```python
import strawberry
from typing import Optional
from dataclasses import dataclass

@strawberry.type
class User:
    id: strawberry.ID
    email: str
    name: Optional[str] = None

@strawberry.type
class Post:
    id: strawberry.ID
    title: str
    body: str

@strawberry.input
class CreatePostInput:
    title: str
    body: str

@strawberry.type
class Query:
    @strawberry.field
    def user(self, id: strawberry.ID) -> Optional[User]:
        # Resolver — fetch from DB
        row = db.fetchone("SELECT * FROM users WHERE id = %s", (id,))
        if not row:
            return None
        return User(id=row["id"], email=row["email"], name=row["name"])

    @strawberry.field
    def users(self, limit: int = 10, offset: int = 0) -> list[User]:
        rows = db.fetchall("SELECT * FROM users LIMIT %s OFFSET %s", (limit, offset))
        return [User(**r) for r in rows]

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_post(self, input: CreatePostInput) -> Post:
        row = db.insert("posts", {"title": input.title, "body": input.body})
        return Post(id=row["id"], title=row["title"], body=row["body"])

schema = strawberry.Schema(query=Query, mutation=Mutation)
```

---

## DataLoader — Solving N+1

```python
# N+1 problem: fetching 10 posts triggers 10 separate author queries
# DataLoader batches those 10 queries into 1

from strawberry.dataloader import DataLoader
from typing import List

async def load_users(keys: List[strawberry.ID]) -> List[Optional[User]]:
    """Called once with ALL requested user IDs — returns list in same order."""
    rows = await db.fetchall(
        "SELECT * FROM users WHERE id = ANY(%s)", (list(keys),)
    )
    user_map = {str(r["id"]): User(**r) for r in rows}
    return [user_map.get(str(k)) for k in keys]  # preserve order of keys

# Register at request level (new DataLoader per request)
@strawberry.type
class Post:
    id: strawberry.ID
    title: str
    author_id: strawberry.ID

    @strawberry.field
    async def author(self, info: strawberry.types.Info) -> Optional[User]:
        return await info.context["user_loader"].load(self.author_id)

# In app setup
async def get_context():
    return {
        "user_loader": DataLoader(load_fn=load_users)
    }
```

---

## Fragments

```graphql
# Define reusable field sets
fragment UserFields on User {
  id
  email
  name
}

fragment PostSummary on Post {
  id
  title
  author {
    ...UserFields
  }
}

# Use in queries
query Feed {
  recentPosts: posts(limit: 10) {
    ...PostSummary
  }
}
```

---

## Introspection Query

```graphql
# Discover what types and fields are available
{
  __schema {
    types {
      name
      kind
      fields {
        name
        type {
          name
          kind
        }
      }
    }
  }
}

# Get specific type info
{
  __type(name: "User") {
    name
    fields {
      name
      type {
        name
        ofType {
          name
        }
      }
    }
  }
}
```

**Disable introspection in production** — it exposes your entire schema to attackers.

---

## GraphQL Error Shape

```json
{
  "data": {
    "user": null
  },
  "errors": [
    {
      "message": "User not found",
      "locations": [{"line": 2, "column": 3}],
      "path": ["user"],
      "extensions": {
        "code": "NOT_FOUND",
        "http_status": 404
      }
    }
  ]
}
```

GraphQL always returns `200 OK` — errors are in the response body, not HTTP status codes.

---

## REST vs GraphQL Comparison

| Dimension | REST | GraphQL |
|-----------|------|---------|
| Data fetching | Fixed shape per endpoint | Client specifies exact fields |
| Multiple resources | Multiple round trips | Single query |
| Over-fetching | Common (extra fields you don't need) | Eliminated |
| Under-fetching | Common (need another request) | Eliminated |
| HTTP caching | Native (GET is cacheable) | Hard (most queries use POST) |
| Schema contract | Implicit (OpenAPI optional) | Explicit and strongly typed |
| Error format | HTTP status codes | Always 200, errors in body |
| File uploads | Simple multipart | Requires spec extension |
| Real-time | Webhooks / SSE / polling | Subscriptions (WebSocket) |
| Learning curve | Low | Medium-high |
| Best for | Simple CRUD, public APIs | Complex domains, multiple clients |

---

## When to Use / Avoid

| Scenario | Use GraphQL | Use REST |
|----------|-------------|----------|
| Mobile + web with different data needs | Yes | No |
| Complex entity relationships (social graph, CMS) | Yes | No |
| Simple CRUD with uniform clients | No | Yes |
| Public developer API | No | Yes (more universal) |
| File upload as core feature | No | Yes |
| HTTP cache is critical | No | Yes |
| Team unfamiliar with GraphQL | No | Yes |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Production Deployment](../12_production_deployment/cheatsheet.md) &nbsp;|&nbsp; **Next:** [gRPC →](../14_grpc/cheatsheet.md)

**Related Topics:** [REST Best Practices](../03_rest_best_practices/) · [gRPC](../14_grpc/) · [API Design Patterns](../16_api_design_patterns/)
