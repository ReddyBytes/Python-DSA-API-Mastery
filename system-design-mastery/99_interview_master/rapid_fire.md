# Rapid Fire — System Design Flash Questions
> High-velocity Q&A to drill core concepts before your interview.
> Read these the morning of. If you can answer every question cold, you are ready.

---

## Contents

```
1.  Fundamentals
2.  Databases
3.  Caching
4.  Message Queues
5.  Load Balancing
6.  Scalability
7.  Distributed Systems
8.  API Design
9.  Security
```

---

## 1. Fundamentals

**Q: What does the CAP theorem state?**
A: A distributed system can guarantee at most two of three properties: Consistency (every read returns the most recent write), Availability (every request gets a non-error response), and Partition Tolerance (the system keeps operating when network partitions occur). In practice, partition tolerance is non-negotiable in any distributed system, so the real trade-off is between CP (consistent, may reject requests during a partition) and AP (available, may return stale data).

---

**Q: What is the difference between strong and eventual consistency?**
A: Strong consistency guarantees that every read reflects the most recently committed write — every node converges before the next read is served. Eventual consistency allows reads to return stale data temporarily but guarantees all replicas will converge given no new writes. Strong consistency requires coordination overhead and adds latency; eventual consistency is faster and more available but requires clients to tolerate stale reads.

---

**Q: What is an SLO and how does it differ from an SLA?**
A: An SLO (Service Level Objective) is an internal reliability target — "p99 latency under 200ms." An SLA (Service Level Agreement) is a contractual commitment to customers with financial consequences for breach. SLOs are intentionally set tighter than SLAs so the team catches degradation before a breach. An SLI (Service Level Indicator) is the actual measured value — the number you compare against your SLO.

---

**Q: What is p99 latency and why does it matter more than average latency?**
A: p99 latency is the 99th percentile — the response time under which 99% of requests complete. At 10,000 requests/second, p99 represents 100 requests/second experiencing that worst-case latency. Average latency hides the long tail: a system averaging 20ms with p99 at 2,000ms is inflicting serious pain on real users. Senior engineers report p99 and p999, not averages.

---

**Q: What are the key latency numbers every engineer should know?**
A: L1 cache ~0.5ns. RAM ~100ns. SSD random read ~150µs. Same-datacenter network round trip ~500µs. HDD seek ~10ms. Cross-continent round trip ~150ms. The practical implication: one synchronous database call to another region costs as much as 300,000 RAM accesses. Every remote synchronous call in a hot path must be justified.

---

**Q: What is the difference between throughput and latency?**
A: Latency is how long a single request takes end-to-end. Throughput is how many requests the system handles per unit of time. They are related but not the same — batching increases throughput but also increases per-item latency. Reducing work per request lowers latency but may not improve throughput if concurrency is the bottleneck. Optimizing for one often trades off the other; understand which the system needs.

---

**Q: What does "nines of availability" mean in practice?**
A: 99% availability = ~87.6 hours downtime/year. 99.9% (three nines) = ~8.7 hours/year. 99.99% (four nines) = ~52 minutes/year. 99.999% (five nines) = ~5 minutes/year. Each additional nine is roughly 10x harder and more expensive to achieve. Most consumer SaaS targets 99.9%–99.99%; payment-critical systems often target 99.99%+.

---

**Q: What is a single point of failure?**
A: A SPOF is any component whose failure alone brings down the entire system. Examples: a primary database with no replica, a single load balancer, a single availability zone. Identifying and eliminating SPOFs requires redundancy — multiple instances, replicas across failure domains, or graceful degradation. A system design that introduces a SPOF is incomplete regardless of how sophisticated the rest of it is.

---

**Q: What is the difference between fault tolerance and high availability?**
A: High availability means the system remains accessible through failures by using redundant components that fail over automatically — users may notice a brief disruption during failover. Fault tolerance means the system continues operating correctly during active failures with no interruption at all. Fault tolerance is a superset of high availability, harder to achieve, and significantly more expensive to build and operate.

---

## 2. Databases

**Q: When would you choose SQL over NoSQL?**
A: Choose SQL when you need ACID transactions across multiple entities, your data is relational with well-defined schemas, you need complex queries (joins, aggregations, ad-hoc reporting), or your write volume fits on a single primary (under ~10,000 writes/second for most workloads). SQL databases excel at correctness guarantees and query flexibility. When in doubt, start with SQL.

---

**Q: When would you choose NoSQL over SQL?**
A: Choose NoSQL when you need horizontal write scalability beyond what a single SQL primary can handle, when your access patterns are fixed and simple (key-value lookups, time-series ranges), when your schema evolves rapidly and upfront definition is not feasible, or when you need to store document or graph-structured data efficiently. The trade-off is giving up joins, transactions, and ad-hoc queries.

---

**Q: What are the four ACID properties?**
A: Atomicity — a transaction either fully commits or fully rolls back; no partial application. Consistency — a transaction moves the database from one valid state to another, enforcing all defined constraints. Isolation — concurrent transactions do not interfere; their interleaving produces results equivalent to some serial execution. Durability — once committed, a transaction survives crashes, power loss, and restarts. ACID is why relational databases are the default choice for financial and inventory systems.

---

**Q: What is an index and what is the cost of adding one?**
A: An index is a separate data structure (typically a B-tree) that lets the database locate rows without scanning the full table. Without an index, a query on a non-keyed column is O(n); with a B-tree index, it is O(log n). The cost: every write (INSERT, UPDATE, DELETE) must update all relevant indexes, adding write latency and I/O. Indexes consume disk space. A table with ten indexes can have write throughput 5–10x lower than a table with one. Add indexes for columns you query, not columns you store.

---

**Q: What is the N+1 query problem?**
A: The N+1 problem occurs when code fetches N records in one query, then executes N additional queries to fetch related data for each record. For 100 users, that is 101 queries instead of 2. The fix is eager loading — either a JOIN or a second query with an IN clause fetching all related data at once. N+1 is one of the most common performance bugs in ORM-heavy applications and can turn a <10ms endpoint into a >1,000ms endpoint at modest scale.

---

**Q: What is the difference between primary key and secondary index?**
A: A primary key uniquely identifies each row and typically determines the physical row order in clustered storage (InnoDB, for example). A secondary index is an additional lookup structure on a non-primary column. Lookups via secondary index typically require two steps: find the primary key in the secondary index, then fetch the full row using that primary key. This "double lookup" adds overhead — covering indexes (where all needed columns are in the index itself) eliminate the second step.

---

**Q: What is the difference between synchronous and asynchronous replication?**
A: Synchronous replication waits for the replica to confirm the write before acknowledging the client — guarantees zero data loss on primary failure but adds latency proportional to replica lag. Asynchronous replication acknowledges the write immediately and replicates in the background — lower write latency but risks losing a small window of commits if the primary crashes before replication completes. Most RDBMS systems use async replication for performance, with at least one sync replica for durability.

---

**Q: What is database sharding and what problems does it create?**
A: Sharding horizontally partitions data across multiple database nodes, each holding a subset. A routing layer directs writes and reads to the correct shard based on a shard key. Sharding enables horizontal write scalability beyond a single node. The problems: cross-shard queries (joins, aggregations) become expensive or impossible; rebalancing shards when adding nodes requires data movement; the shard key choice is critical and hard to change later; transactions spanning shards lose ACID guarantees without additional coordination.

---

**Q: What is write-ahead logging (WAL) and why does it matter?**
A: WAL is a durability mechanism where every change is appended to a sequential log on disk before being applied to the main data files. On crash, the database replays the WAL to recover committed state. WAL ensures durability without requiring every write to immediately update the data file (which would be slow random I/O). WAL also enables streaming replication — the replica applies the same log entries the primary wrote.

---

**Q: What is a database connection pool and why is it necessary?**
A: A connection pool maintains a set of pre-opened, pre-authenticated database connections that application threads borrow and return. Opening a new TCP connection and authenticating costs ~10ms. Without pooling, a service handling 5,000 req/s would spend the majority of its latency budget on connection setup. Pools like PgBouncer (Postgres) and HikariCP (JVM) are standard. Pool exhaustion — all connections in use — is one of the most common causes of database-related outages.

---

## 3. Caching

**Q: What is cache-aside (lazy loading) and when is it used?**
A: In cache-aside, the application checks the cache first. On a hit, it returns the cached value immediately. On a miss, it fetches from the database, writes the result to cache, then returns it. The cache is only populated on actual cache misses, so it naturally holds only data that has been requested. Cache-aside is the most common pattern — it is simple, self-healing (expired entries are refreshed on next access), and works well for read-heavy workloads.

---

**Q: What is the difference between write-through and write-behind caching?**
A: Write-through updates both the cache and the database synchronously on every write — the write is not acknowledged until both are updated. The cache stays consistent but writes are slower. Write-behind (write-back) updates the cache immediately and flushes to the database asynchronously — lower write latency, higher throughput, but risks data loss if the cache node fails before flushing. Write-through is the safe default; write-behind is used for high-write, loss-tolerant use cases.

---

**Q: What are the Redis eviction policies and when would you use each?**
A: `allkeys-lru` evicts the least recently used key across all keys — best general-purpose cache policy. `volatile-lru` evicts the LRU key that has a TTL set — useful when some keys must never be evicted (set them without a TTL). `allkeys-lfu` evicts the least frequently used — better for workloads with highly skewed access patterns where some items are far more popular. `noeviction` returns an error when memory is full — used for session stores or data that must not be lost. Use `allkeys-lru` as the default.

---

**Q: What is a cache stampede and how do you prevent it?**
A: A cache stampede (thundering herd) occurs when a popular cached item expires and many concurrent requests simultaneously see a miss, triggering a flood of identical database queries before any can repopulate the cache. This can crash databases during traffic spikes. Prevention: (1) mutex locking — only one process fetches from the DB, others wait on the lock; (2) probabilistic early expiry — refresh the cache randomly before the TTL expires; (3) stale-while-revalidate — serve the stale cached value while one background thread refreshes it.

---

**Q: When should you NOT cache?**
A: Do not cache data that must be strongly consistent (payment balances, inventory counts where overselling is unacceptable). Do not cache data that changes faster than the TTL — the cache will always be stale, adding complexity without benefit. Do not cache high-cardinality, low-reuse data (every request is unique — you waste memory with zero hit rate). Do not add a cache before profiling and confirming that the database is the bottleneck; caches are complexity that must be paid for in code and operations.

---

**Q: What Redis commands are most important to know for system design?**
A: `SET key value EX seconds` — set a value with expiry. `GET key` — retrieve. `INCR key` — atomic increment, used for rate limiters and counters. `SETNX key value` — set only if key does not exist, the primitive for distributed locks. `ZADD key score member` / `ZRANGEBYSCORE` — sorted set operations, used for leaderboards and sliding-window rate limiters. `LPUSH` / `RPOP` — list operations, used for simple task queues. `EXPIRE key seconds` — add TTL to an existing key.

---

**Q: What is cache invalidation and why is it the hardest problem in caching?**
A: Cache invalidation is removing or updating cached data when the underlying source of truth changes. It is hard because the cache and database are decoupled systems that can diverge: a write to the database that fails to invalidate the cache leaves readers with stale data indefinitely. TTL-based expiry is simple and self-healing but always has a window of staleness. Event-driven invalidation (write to DB, publish invalidation event, cache subscribes) is accurate but adds operational complexity. Both strategies have failure modes.

---

**Q: What is a CDN and when should it be part of your design?**
A: A CDN (Content Delivery Network) caches static assets (images, JS, CSS, video) on geographically distributed edge servers close to users. Without a CDN, a user in Tokyo hitting an origin server in Virginia experiences ~150ms of network latency per asset. A CDN reduces that to ~5–20ms from a nearby edge node. Include a CDN when serving static or infrequently-changing public content to a global audience. CDNs also absorb DDoS traffic and reduce origin bandwidth costs. They do not help for dynamic, personalized, or real-time content.

---

## 4. Message Queues

**Q: What are the three message delivery guarantees?**
A: At-most-once: messages may be dropped but are never duplicated — fire-and-forget, no retries. At-least-once: messages are never permanently lost but may be delivered more than once on retry — requires consumers to be idempotent. Exactly-once: messages are delivered precisely once — the hardest to implement, requires distributed transactions or idempotency tracking and is expensive. Most production systems use at-least-once delivery with idempotent consumers, which achieves effective exactly-once behavior at much lower cost.

---

**Q: What is the difference between Kafka and RabbitMQ?**
A: Kafka is a distributed, partitioned, replicated log. Messages are persisted to disk, ordered within a partition, and retained for a configurable period (days or indefinitely). Consumers track their own offset and can replay history. Kafka excels at high-throughput event streaming, audit logs, and fan-out to multiple independent pipelines. RabbitMQ is a message broker that routes messages to queues and deletes them once acknowledged. RabbitMQ is better for task queues, complex routing topologies (exchanges, bindings, routing keys), and lower-volume workloads requiring flexible routing logic.

---

**Q: What is a consumer group in Kafka?**
A: A consumer group is a set of consumers that collectively consume a Kafka topic. Each topic partition is assigned to exactly one consumer in the group at a time, enabling parallel processing proportional to the partition count. If a consumer in the group fails, Kafka reassigns its partitions to other consumers in the group (rebalancing). Multiple independent consumer groups can read the same topic simultaneously without any interference — each group has its own committed offset. This is how Kafka enables fan-out to multiple processing pipelines from one topic.

---

**Q: What is a Dead Letter Queue and why is it necessary?**
A: A DLQ (Dead Letter Queue) is a queue where messages are sent after a configurable number of failed processing attempts. Without a DLQ, a "poison pill" message — one that consistently causes consumer errors — will block the queue indefinitely, preventing all subsequent messages from being processed. The DLQ isolates failed messages for inspection, debugging, and eventual replay. A DLQ is a required component of any production message queue system.

---

**Q: When should you use a message queue instead of a direct API call?**
A: Use a message queue when: (1) the consuming service is slower than the producing service and you need a backlog buffer; (2) the producer must not be blocked if the consumer is down; (3) you need fan-out — one event processed by multiple independent consumers; (4) the work is background and the producer does not need a synchronous response; (5) you need automatic retries with exponential backoff on consumer failure. Avoid queues for user-facing requests requiring an immediate response.

---

**Q: What is Kafka's partitioning strategy and why does partition key choice matter?**
A: Kafka topics are divided into partitions — each an ordered, immutable log. Producers assign messages to partitions by key hash (same key always lands on the same partition, preserving per-key order) or round-robin (maximum parallelism, no ordering). Partition count sets the maximum parallelism — a consumer group can run at most one consumer per partition. Partition key choice determines both ordering guarantees and load distribution: partition by user_id to preserve per-user event order; partition by a random key to maximize write throughput.

---

## 5. Load Balancing

**Q: What is the difference between L4 and L7 load balancing?**
A: L4 (transport layer) load balancing routes TCP/UDP connections based on IP address and port without inspecting application content. It is extremely fast and low-overhead. L7 (application layer) load balancing inspects the HTTP request and can route based on URL path, headers, cookies, or request body. L7 enables path-based routing (`/api` → API tier, `/static` → CDN origin), SSL termination, sticky sessions by cookie, and request rewrites. L7 is more powerful but adds processing overhead and latency.

---

**Q: What load balancing algorithms exist and when would you use each?**
A: Round-robin distributes requests in sequence — simple and effective when all servers are identical and requests are similar in cost. Least connections routes to the server with the fewest active connections — better when request processing time varies significantly. Weighted round-robin allocates more requests to higher-capacity servers. IP hash routes the same client IP to the same server consistently — used for stateful sessions. Power of two choices: pick two servers at random, route to the less loaded — nearly as good as least connections with far less overhead.

---

**Q: What are sticky sessions and why should you avoid them?**
A: Sticky sessions (session affinity) route all requests from the same client to the same server, typically via IP hash or a session cookie. This is needed when session state is stored in server memory rather than in a shared store. The problems: one server becomes overloaded while others sit idle, rolling deployments require careful connection draining, and if the assigned server goes down the session state is lost anyway. The correct solution is stateless servers with all session state in Redis — then any server can serve any request.

---

**Q: How do health checks work in a load balancer?**
A: The load balancer sends periodic probes to each backend — an HTTP GET to a `/health` endpoint or a TCP connect. If a server fails to respond within a timeout, or returns an error status, the load balancer removes it from the active pool. After a configurable number of successful probes, the server is reinstated. Active health checks probe servers regardless of traffic; passive health checks detect failures by observing errors on live requests. Production systems use both. A `/health` endpoint must reflect actual service health — a database connection check is more meaningful than just returning 200.

---

## 6. Scalability

**Q: What is the difference between horizontal and vertical scaling?**
A: Vertical scaling (scale up) adds more resources to a single machine — more CPUs, RAM, or faster disks. It requires no code changes but has a hard ceiling (the largest available instance size) and remains a single point of failure. Horizontal scaling (scale out) adds more machines and distributes load across them. It enables near-linear throughput growth and eliminates SPOFs, but requires stateless application design and a load balancer. Most modern web services are designed for horizontal scaling from the start.

---

**Q: What does it mean for an application to be stateless?**
A: A stateless application stores no session data in process memory between requests — every request carries all the information needed to process it, and any server instance can handle any request. State is stored externally in a shared store (database, Redis, cookie). Stateless services scale horizontally by adding instances without worrying about which server a user "belongs to." Stateful services (in-memory sessions, local file writes) require sticky sessions and cannot be freely scaled or restarted.

---

**Q: What is connection pool exhaustion and how do you diagnose it?**
A: Exhaustion occurs when all database connections in the pool are in use simultaneously and new requests must wait or fail. Symptoms: requests pile up with "connection timeout" errors in logs; database shows connections at maximum; response latency spikes suddenly. Causes: slow queries holding connections longer than expected; pool too small for traffic; missing query timeouts. Fixes in order: set query and connection timeouts; add a connection pooler (PgBouncer); add read replicas to distribute load; then address slow queries at their root.

---

**Q: What is a rate limiter and what are the main algorithms?**
A: A rate limiter controls how many requests a client can make in a time window. Token bucket: a bucket fills at a fixed rate up to a maximum capacity; each request consumes a token; burst traffic is permitted up to bucket capacity. Leaky bucket: requests enter a queue drained at a fixed rate — smooths bursts completely. Fixed window counter: counts requests per time bucket (e.g., per minute); simple but allows 2x the limit at window boundaries. Sliding window: uses a sorted set of timestamps in Redis to count requests in the most recent N seconds — accurate with no boundary spike.

---

**Q: What is backpressure and why does it matter at scale?**
A: Backpressure is the mechanism by which a downstream component signals to upstream producers to slow down when it is overwhelmed. Without backpressure, a slow consumer causes the producer's buffer to fill unboundedly, eventually causing out-of-memory crashes or data loss. In practice: message queues provide natural backpressure (the queue fills up), HTTP servers return 429 or 503, and streaming systems like Kafka use consumer lag as the signal. Designing systems that propagate backpressure gracefully is a hallmark of senior-level thinking.

---

## 7. Distributed Systems

**Q: What is the consensus problem and why is it hard?**
A: Consensus is getting multiple independent nodes to agree on a single value despite node failures and message delays. The FLP impossibility theorem proves no deterministic algorithm guarantees consensus in an asynchronous network with even one failing process. In practice, systems use algorithms like Raft that guarantee consensus under realistic assumptions (nodes fail by crashing, not by sending arbitrary incorrect data) and require a stable majority to make progress.

---

**Q: What does Raft guarantee?**
A: Raft elects a leader and requires the leader to receive acknowledgments from a quorum (majority) of nodes before committing any log entry. It guarantees: committed entries are never lost; all nodes eventually hold the same log; and the cluster makes forward progress as long as a majority of nodes are reachable and can communicate. Raft powers etcd (Kubernetes state store), CockroachDB, TiKV, and Consul. The penalty for split votes or leader failure is a pause of typically 150–300ms for re-election.

---

**Q: What is split-brain and how is it prevented?**
A: Split-brain occurs when a network partition divides a cluster so each segment believes it is the only functioning partition and independently accepts writes. When the partition heals, both sides have diverged and one set of writes must be discarded or merged. Prevention: require quorum — a write only commits when acknowledged by more than half the nodes. If neither partition has a majority, neither can commit writes. Additionally, fencing tokens (a monotonically increasing epoch number) ensure old leaders cannot commit writes after a new leader has been elected.

---

**Q: What is a vector clock and when is it used?**
A: A vector clock tracks causality in distributed systems — it determines whether event A happened before event B (A caused B), after, or concurrently (neither caused the other). Each node maintains a counter per node in the cluster. On each event the node increments its own counter. On receiving a message it takes the element-wise maximum of local and received clocks. Concurrent events with no causal relationship require conflict resolution logic (last-write-wins, merge, user resolution). Dynamo-style databases use vector clocks to detect and surface write conflicts.

---

**Q: What is quorum in a distributed system?**
A: Quorum is a majority — for N nodes, quorum is N/2 + 1. For a write to be durable it must be acknowledged by a write quorum W. For a read to be strongly consistent it must read from a read quorum R. When W + R > N, the write and read quorum sets overlap, guaranteeing every consistent read sees the most recent write. Common configuration: N=3, W=2, R=2. This tolerates one node failure while maintaining both durability and consistency.

---

**Q: What is consistent hashing and why does it minimize reshuffling?**
A: Consistent hashing places both nodes and keys on a conceptual ring by hashing both into the same hash space. Each key is assigned to the first node clockwise from it on the ring. When a node is added, only the keys between it and its predecessor move to it — no other keys are affected. When a node is removed, its keys move to its successor. This limits cache or partition movement to approximately K/N keys (K total keys, N nodes) on topology change, versus O(K) rehashing in modulo-based schemes.

---

**Q: What is the difference between leader-based and leaderless replication?**
A: In leader-based systems (MySQL replication, Kafka partitions, Raft groups), all writes go through a single elected primary. This simplifies consistency because there is one canonical write order, but creates a write bottleneck and requires re-election on primary failure. In leaderless systems (Cassandra, Amazon Dynamo), clients can write to any node and the system uses quorum writes/reads to achieve consistency. Leaderless systems offer higher write availability but have more complex conflict detection, require careful quorum tuning, and have weaker consistency guarantees by default.

---

## 8. API Design

**Q: What are the REST architectural constraints?**
A: Stateless — every request contains all information needed; no server-side session state between requests. Uniform interface — resources are identified by URIs and transferred as representations (JSON, XML); operations use standard HTTP methods. Client-server separation — UI concerns are decoupled from storage concerns. Cacheable — responses explicitly declare whether they can be cached. Layered system — clients cannot tell if they are connected directly to the origin or through intermediaries. Most "REST APIs" are actually HTTP APIs that do not fully comply with these constraints — REST is an architectural style, not a protocol.

---

**Q: What is idempotency and which HTTP methods should be idempotent?**
A: An operation is idempotent if making the same request multiple times produces the same result as making it once. GET, PUT, and DELETE must be idempotent per the HTTP spec. POST is not (each POST creates a new resource). Idempotency is critical for safe retries — if a PUT request times out, the client can safely retry without creating duplicates. For POST operations that must be retry-safe, use idempotency keys: a unique ID the client generates and sends with the request; the server stores the result and returns the same response for duplicate key requests.

---

**Q: How would you version a public API?**
A: Three approaches: URL versioning (`/v1/users`, `/v2/users`) — explicit, CDN-cacheable, easy to route, easy to test in a browser, but pollutes the URL space. Header versioning (`Accept: application/vnd.company+json; version=2`) — clean URLs but requires tooling to discover and is harder to cache. Query parameter versioning (`?version=2`) — easy to add but considered messy. URL versioning is the most common in practice because it is obvious, simple to route at the load balancer, and easy for consumers to understand. Additive-only changes (new fields, new endpoints) should not require a new version.

---

**Q: What is the difference between authentication and authorization?**
A: Authentication verifies identity — confirming who you are (via password, token, certificate, biometric). Authorization verifies permission — confirming what you are allowed to do after your identity is established. Authentication always precedes authorization. The common HTTP status code mistake: returning 401 (Unauthorized) when the user is authenticated but lacks permission — the correct code is 403 (Forbidden). 401 means the request lacks valid credentials; 403 means credentials are valid but access is denied.

---

**Q: What is GraphQL and when would you choose it over REST?**
A: GraphQL lets clients specify exactly the fields they need in a single request, eliminating over-fetching (REST returning unused fields) and under-fetching (needing multiple REST requests for related data). Choose GraphQL when client data needs vary widely (mobile vs. desktop), when you want to consolidate multiple REST calls into one, or when frontend teams need to iterate independently from backend schemas. The costs: query complexity requires depth and cost limits to prevent abuse; HTTP caching is harder (most requests are POSTs); tooling is more complex. GraphQL is not strictly better than REST — it trades one set of trade-offs for another.

---

**Q: What is cursor-based pagination and why is it better than offset pagination?**
A: Cursor-based pagination uses an opaque pointer (typically the last seen ID or timestamp) to fetch the next page. The query is `WHERE id > :cursor LIMIT 20`. Offset pagination uses `LIMIT 20 OFFSET 100`. Offset pagination breaks when data is inserted or deleted during traversal — items shift position and pages skip or duplicate records. Offset also becomes progressively slower on large offsets (the database must scan and discard rows). Cursor-based pagination is stable against concurrent modifications and performs consistently at any depth. Use cursor pagination for any live-updating data.

---

## 9. Security

**Q: What is OAuth2 and how does the authorization code flow work?**
A: OAuth2 lets users grant third-party applications limited access to their accounts without sharing their password. Authorization code flow: (1) user clicks "Login with Google," app redirects to Google with client_id and redirect_uri; (2) user authenticates and consents at Google; (3) Google redirects back to the app with a short-lived authorization code; (4) the app's server exchanges the code plus its client_secret directly with Google's token endpoint for an access token and refresh token. The exchange is server-side so the client_secret never touches the browser.

---

**Q: What is a JWT and what are its limitations?**
A: A JWT is a self-contained signed token that encodes claims (user_id, roles, expiry) as a base64-encoded JSON payload. The server signs it with a secret; any service with the signing key can verify it without a database lookup — enabling stateless authentication. Limitations: JWTs cannot be revoked before expiry without a server-side blocklist (which reintroduces centralized state). The payload is encoded but not encrypted — anyone can decode and read it; never include sensitive data in a JWT unless you also encrypt it (JWE). Treat JWTs like session cookies: use short expiry + refresh tokens, transmit only over HTTPS.

---

**Q: What is SQL injection and how is it prevented?**
A: SQL injection occurs when user-supplied input is interpreted as SQL code rather than data because the query is built by string concatenation. An attacker who controls input can append SQL that bypasses authentication, reads all data, or deletes tables. Prevention: always use parameterized queries (prepared statements) — the database driver separates the SQL structure from the data values and never interprets data as code. ORMs generate parameterized queries by default. Input validation and stored procedures add defense-in-depth but do not substitute for parameterization.

---

**Q: What is CORS and why does it exist?**
A: CORS (Cross-Origin Resource Sharing) is a browser security mechanism that restricts web pages from making requests to a different origin (domain, scheme, port) than the one that served the page. Without CORS, any website could use a logged-in user's cookies to make API calls to your service — a cross-site request forgery. Servers explicitly grant permission to specific origins via `Access-Control-Allow-Origin` response headers. The browser sends a preflight OPTIONS request before state-changing cross-origin requests to verify the server allows them. CORS is enforced only by browsers — server-to-server calls are unaffected.

---

**Q: What is the principle of least privilege and how does it apply to system design?**
A: Least privilege means each component receives only the minimum permissions required to perform its function. In system design: the API server's database user has SELECT/INSERT/UPDATE but not DROP or CREATE. Individual microservices have network access only to services they directly call. IAM roles for Lambda functions are scoped to specific S3 buckets and DynamoDB tables. Least privilege limits blast radius — a compromised API server with read-only DB credentials cannot destroy data even if the attacker has full server access.

---

**Q: What is the difference between symmetric and asymmetric encryption?**
A: Symmetric encryption uses the same key for both encryption and decryption (AES-256). It is fast and efficient for large payloads — used for database encryption, file encryption, and bulk data. The challenge is key distribution: how do two parties securely share the key? Asymmetric encryption uses a key pair: public key encrypts, private key decrypts (RSA, elliptic curve). It solves key distribution — share the public key freely. TLS uses asymmetric encryption to negotiate a shared symmetric session key (the handshake), then switches to symmetric encryption for the bulk of data transfer.

---

**Q: What is a DDoS attack and what are the primary mitigation strategies?**
A: A Distributed Denial of Service attack floods a system with traffic from many sources simultaneously to exhaust resources (bandwidth, CPU, connection table) and deny service to legitimate users. Mitigation: (1) CDN and anycast routing absorb volumetric attacks at the edge before they reach origin servers; (2) rate limiting per IP at the load balancer drops floods without processing them fully; (3) challenge-response (CAPTCHA, JS challenge) for HTTP floods; (4) services like Cloudflare or AWS Shield provide dedicated DDoS protection infrastructure. No single technique is sufficient; defense in depth is required.

---

## Navigation

| | |
|---|---|
| Home | [README.md](../README.md) |
| Interview Framework | [23 — Interview Framework](../23_interview_framework/the_45_minute_playbook.md) |
| Scenario Questions | [scenario_questions.md](./scenario_questions.md) |
| Company Patterns | [company_patterns.md](./company_patterns.md) |
