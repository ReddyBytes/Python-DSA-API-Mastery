# 🎯 GraphQL — Interview Preparation

> This file prepares you to discuss GraphQL like a working engineer.
> Not just definitions — but real-world usage, trade-offs, and production scenarios.

---

# 🔹 Basic Level Questions (0–2 Years)

**Q1: What problem does GraphQL solve that REST does not handle well?**

<details>
<summary>💡 Show Answer</summary>

REST APIs return fixed shapes per endpoint. The server decides what data comes back. This causes two problems: over-fetching (you get 20 fields but need 3) and under-fetching (one endpoint does not have what you need, so you make a second request to another endpoint). A mobile app and a web app that display the same user data in different ways both get the same large JSON payload.

GraphQL lets the client declare exactly which fields it needs. A mobile app requests just name and avatar. A web dashboard requests name, email, role, and the last 5 orders with totals. Both send queries to the same endpoint (/graphql), and each gets precisely the data it asked for — nothing more, nothing less. This also reduces the need to version endpoints for different client needs, which is a major pain point for teams maintaining REST APIs across multiple clients with different requirements.

</details>

<br>

**Q2: What is a resolver in GraphQL and how does it relate to the schema?**

<details>
<summary>💡 Show Answer</summary>

The schema defines the data types and the shape of what can be queried — it is a contract. A resolver is the function that executes when a client queries a field — it is the implementation. Every field in a GraphQL schema has a resolver. The schema says "a User has an email field of type String." The resolver is the Python function that goes to the database and fetches that email value for a specific user.

In Strawberry (the Python library): the schema is defined with @strawberry.type decorated classes and @strawberry.field decorated methods. The method body is the resolver — it receives arguments (the ID, filters, etc.) and returns the typed value. The separation means you can redesign your data sources (switch from SQL to a microservice) without changing the schema contract that clients depend on, as long as the resolver returns the same shape.

</details>

<br>

**Q3: How does GraphQL handle errors differently from REST?**

<details>
<summary>💡 Show Answer</summary>

REST uses HTTP status codes to signal errors — 404 for not found, 400 for bad input, 500 for server error. GraphQL always returns 200 OK regardless of whether the operation succeeded. Errors are communicated in the response body in an "errors" array alongside the "data" field.

This means you cannot rely on HTTP status codes to detect GraphQL errors — you must inspect the response body. A partially successful response is possible: data.user might be null with an error in the errors array explaining why, while data.posts contains valid results because that part of the query succeeded. The error objects include message, path (which field failed), locations (line number in the query), and optionally an extensions object with a machine-readable code like NOT_FOUND or UNAUTHORIZED. In production tooling you need to check for the presence of an "errors" key, not just a non-200 status.

</details>

<br>

**Q4: What is the ! (non-null) modifier in a GraphQL schema and what does it mean for clients?**

<details>
<summary>💡 Show Answer</summary>

In GraphQL SDL, a type without ! can be null — the resolver may return null for that field. Adding ! makes the field non-nullable — the resolver must return a value, never null. For example: name: String can be null, while email: String! is guaranteed to have a value.

For list fields: [Post!]! means the list itself is never null (might be empty but always an array) and each item in the list is never null. [Post] means both the list and each item can be null.

This matters for client developers: a non-null field can be accessed without a null check. A nullable field requires defensive code. The schema contract is your API contract — making a currently non-null field nullable in a later version is a breaking change because clients without null checks will crash. Making a nullable field non-null is safe (stricter guarantee). Design non-nullability carefully — fields that might not exist in all contexts (a user's profile picture before they upload one) should be nullable.

</details>

<br>

**Q5: What is a GraphQL mutation and how does it differ from a query?**

<details>
<summary>💡 Show Answer</summary>

A query is a read operation — it should not change server state. A mutation is a write operation — it creates, updates, or deletes data. Syntactically they are similar, but mutations use the mutation keyword. The critical behavioral difference is execution order: queries can be executed in parallel by the server because they are read-only. Mutations in a single request are executed serially, in document order, to avoid race conditions between write operations.

Mutations return a selection set — you specify exactly which fields of the created or updated resource you want back. This eliminates the need for a separate GET request after a write, which is a common REST pattern. The return type is typically the modified object so the client can update its local state optimistically without a round-trip. A common mistake is returning only a success boolean from a mutation — this forces clients to re-fetch data they could have received in the mutation response.

</details>

<br>

---

# 🔹 Intermediate Level Questions (2–5 Years)

**Q6: What is the N+1 problem in GraphQL and how does DataLoader solve it?**

<details>
<summary>💡 Show Answer</summary>

In GraphQL, a query for 10 posts where each post has an author field triggers the post resolver once, then the author resolver 10 times — one per post. That is 11 database queries instead of 2. This is worse than REST because the client controls the query shape, and nested resolvers composing their own DB calls have no visibility into how many times they will be called.

DataLoader solves this by batching and caching. Instead of fetching each author immediately, the author resolver registers its request with the DataLoader: "I need user ID 42." The DataLoader collects all author requests during the current tick of the event loop, then fires a single batched query: SELECT * FROM users WHERE id IN (42, 7, 15, ...). It returns results to each waiting resolver in order. The batch function receives all requested keys at once and must return results in the same order. DataLoader must be scoped per request — a shared DataLoader across requests would serve one user's data to another.

</details>

<br>

**Q7: Why should you disable introspection in production and what are the security implications of leaving it enabled?**

<details>
<summary>💡 Show Answer</summary>

Introspection lets any client query the entire schema — all types, fields, mutations, and their argument names. It is essential during development for GraphQL clients, IDEs, and tooling. In production it gives attackers a complete map of your API surface: all available queries, all mutations, all input types, and field names that might reveal internal domain concepts.

With introspection enabled an attacker can automate discovery of every mutation (to find data modification operations), every query with ID arguments (potential BOLA targets), and field names that suggest sensitive data (ssn, credit_card_number, internal_admin_flag). Disable introspection in your GraphQL server configuration for production deployments. In Strawberry: schema = strawberry.Schema(query=Query, introspection=False). Maintain a separate introspection-enabled endpoint behind authentication for internal tooling if needed. Never expose your schema to the public internet — treat it as an internal asset.

</details>

<br>

**Q8: What are GraphQL fragments and when do you use them?**

<details>
<summary>💡 Show Answer</summary>

A fragment is a reusable selection set — a named set of fields on a specific type that can be spread into multiple queries with ...FragmentName syntax. They prevent repetition when multiple queries need the same set of fields.

The practical use case is client-side code organization: a React component that renders a User card defines a UserCardFields fragment with id, name, avatar, and role. Every query that fetches users for rendering in that component spreads ...UserCardFields. When the component needs a new field, you add it to the fragment once — all queries automatically include it. This is the principle behind the Relay framework's colocation pattern, where UI components own their data requirements as fragments. On the server side, fragments do not change how resolvers work — they are purely a query composition tool. The server sees the expanded field set after fragments are resolved.

</details>

<br>

**Q9: How does HTTP caching work (or not work) with GraphQL and what are the workarounds?**

<details>
<summary>💡 Show Answer</summary>

REST benefits from HTTP GET caching natively — CDNs and browser caches key on URL and headers. GraphQL typically uses a single POST endpoint (/graphql) for all operations including queries. POST requests are not cached by HTTP intermediaries, so every GraphQL query hits your origin server.

Workarounds: persisted queries — the client uploads query documents to the server once (by hash), and subsequent requests send only the hash as a GET parameter (GET /graphql?operationId=abc123). This enables CDN caching of common queries because they are now GET requests with stable URLs. Apollo Engine and Relay implement this pattern. A simpler approach: send read-only queries as GET requests with the query in the URL query parameter — this works for short queries and enables CDN caching without persisted query infrastructure. For field-level caching, use an in-memory or Redis cache within the resolver itself, keyed on the field arguments. At the response level you can cache entire operation results for frequently-run queries by hashing the query string and variables.

</details>

<br>

**Q10: What is the difference between GraphQL interfaces and unions and when do you use each?**

<details>
<summary>💡 Show Answer</summary>

An interface defines a set of fields that multiple types must implement. A union groups types together without requiring shared fields. Both enable queries that can return different concrete types.

Use an interface when the types share meaningful common fields that clients will always query. For example, an Identifiable interface with id: ID! and createdAt: String! — every Node in your system has these fields. Queries can then request interface fields without knowing the concrete type, and use inline fragments (...on User { email }) for type-specific fields.

Use a union when the types have nothing structurally in common but appear in the same context. A search endpoint that returns SearchResult — which can be a User, a Post, or a Product — has no shared fields beyond the fact that they are all search results. The union expresses "one of these types" without imposing any structure. In client code, unions require exhaustive inline fragments to access any fields because there are no guaranteed shared fields.

</details>

<br>

---

# 🔹 Advanced Level Questions (5+ Years)

**Q11: How would you design authorization in a GraphQL API where different users should see different fields on the same type?**

<details>
<summary>💡 Show Answer</summary>

Field-level authorization is more nuanced in GraphQL than in REST because a single query can request a mix of public and restricted fields. There are two main approaches.

Resolver-level checks: each resolver for a sensitive field (salary, ssn, internal_notes) calls a permission check before returning data. If the current user lacks permission, it returns null for nullable fields or raises a PermissionError for non-null fields. This is granular but requires discipline — every sensitive resolver must include the check, and there is no central enforcement point.

Schema directives: define a @auth(requires: ADMIN) directive and apply it to sensitive fields in the schema. A directive visitor intercepts resolver calls for decorated fields and performs the permission check before invoking the resolver. This centralizes authorization logic and makes it visible in the schema itself. Strawberry and Graphene both support directive-based authorization patterns.

A third approach — schema stitching or separate schemas per role — is more complex but provides hard isolation: admin clients get a schema that includes sensitive types; regular clients receive a schema that literally does not contain them. The schema itself becomes the access control boundary.

</details>

<br>

**Q12: What is Apollo Federation and when would you choose it over a monolithic GraphQL schema?**

<details>
<summary>💡 Show Answer</summary>

Apollo Federation is a specification for composing multiple GraphQL subgraphs into a single unified supergraph. Each team maintains their own GraphQL service (subgraph) with their domain types. The federation gateway combines them into a single endpoint that clients query as if it were one schema.

Choose federation when: you have multiple teams with separate deployment cycles who each own distinct domains (users team, orders team, catalog team), and you want them to iterate independently without coordinating schema changes. The gateway handles query planning — splitting a federated query across subgraphs and assembling the result. Entities are shared across subgraphs using the @key directive — the User type defined in the users subgraph can be extended by the orders subgraph to add an orders field without touching the users subgraph.

Avoid federation for small teams — the operational overhead of running a gateway, managing schema registry, and debugging distributed query plans is significant. A monolithic schema with a well-organized resolver directory is simpler and performs better for a single-team project. The break-even point is typically when you have 3+ teams with independent deployment needs.

</details>

<br>

**Q13: How do you implement pagination in GraphQL following the Relay cursor connection specification?**

<details>
<summary>💡 Show Answer</summary>

The Relay cursor connection spec defines a standard pagination shape that client libraries understand. Rather than returning a plain list, a paginated field returns a Connection object with edges (each containing a node and a cursor) and pageInfo (hasNextPage, hasPreviousPage, startCursor, endCursor).

The query uses four optional arguments: first (take N from the start), after (a cursor, start after this position), last (take N from the end), and before (a cursor, take from before this position). Forward pagination uses first + after; backward pagination uses last + before.

In implementation, the cursor encodes the position in the dataset — typically a base64-encoded id or (created_at, id) tuple. On each request the resolver decodes the cursor, converts it to a SQL WHERE clause (WHERE id > decoded_id ORDER BY id LIMIT first+1), fetches first+1 rows, sets hasNextPage=true if the extra row exists, and returns only first rows with their cursors. The +1 trick is the standard way to determine hasNextPage without a COUNT query. This gives O(log n) pagination performance through an index rather than the O(n) cost of offset-based pagination.

</details>

<br>

**Q14: How do you protect a GraphQL API from query complexity abuse and denial of service attacks?**

<details>
<summary>💡 Show Answer</summary>

GraphQL's flexibility is also its attack surface. A single query can request arbitrarily deeply nested fields or repeat expensive resolvers hundreds of times in one request. Without limits, a malicious query can consume all server resources with a single HTTP request.

The primary defenses are query complexity analysis and depth limiting. Assign a cost to each field (1 for scalars, higher for relations and list fields) and reject queries whose total cost exceeds a threshold before execution begins. Depth limiting rejects queries that nest beyond N levels — a depth limit of 10 prevents recursion attacks on types that reference themselves. Both are static checks that run before any resolver fires.

Persisted queries (allow only pre-registered query hashes) provide the strongest protection — arbitrary queries from unknown clients are rejected outright. This is practical for your own clients (web app, mobile app) but restricts third-party developers from using the API dynamically.

Rate limiting must account for query cost, not just request count — 10 expensive queries should count more than 100 cheap queries. Store per-client cost budgets in Redis and reject requests that exceed the budget in the current window. Timeout execution for any query that takes longer than a threshold (5–10 seconds) and return a timeout error rather than holding the connection indefinitely.

</details>

<br>
