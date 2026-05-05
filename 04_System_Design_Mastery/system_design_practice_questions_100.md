# System Design — 100 Practice Questions

> From fundamentals to real-world design decisions. All answers hidden until you click. Designed to build engineering judgment, not just recall.

---

## How to Use This File

1. **Read the question. Stop. Think first.** Don't open the answer until you've formed your own response — even a rough one.
2. **Use the 5-step framework** (below) to structure your thinking before checking.
3. **After reading the answer**, ask yourself: "What did I miss? What was I close on?" That gap is what you actually learned.

---

## How to Think: 5-Step Framework

Apply this to every question before opening the answer:

1. **Restate** — What is this question actually asking? (functional requirement? constraint? tradeoff?)
2. **Identify the concept** — What system design principle is being tested? (scalability? consistency? availability?)
3. **Recall the rule** — What is the standard behavior or tradeoff for that concept?
4. **Apply to the specific case** — Walk through how it applies to this scenario with real numbers or components.
5. **Sanity check** — Does your answer cover the constraint? Is there an obvious tradeoff you haven't mentioned?

---

## Progress Tracker

- [ ] **Tier 1 — Fundamentals** (Q1–Q33): Scaling, databases, caching, load balancing, messaging
- [ ] **Tier 2 — Distributed Patterns** (Q34–Q66): Replication, sharding, consensus, CQRS, observability
- [ ] **Tier 3 — Advanced Distributed Systems** (Q67–Q75): Fan-out, hot partitions, thundering herd, global design
- [ ] **Tier 4 — Interview / Scenario** (Q76–Q90): Explain-it, compare-it, production incident diagnosis
- [ ] **Tier 5 — Critical Thinking** (Q91–Q100): Open-ended design, debug production incidents, major system design

---

## Question Type Legend

| Tag | What it tests |
|---|---|
| `[Normal]` | Recall and apply — straightforward definition or comparison |
| `[Thinking]` | Reason about internals — why does it work this way? |
| `[Critical]` | Tricky edge case or gotcha that trips up even experienced engineers |
| `[Interview]` | Explain or compare — structured answer expected |
| `[Design]` | Architecture or approach decision — opinionated recommendation required |

---

## 🏗️ Tier 1 — Fundamentals

---

### Q1 · [Normal] · `horizontal-vs-vertical-scaling`

> **What is horizontal scaling (scale out) vs vertical scaling (scale up)? Give a real example of each. What are the limits of vertical scaling?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Vertical scaling** means adding more resources (CPU, RAM, disk) to an existing machine. **Horizontal scaling** means adding more machines to share the load.

Example of vertical: upgrading a PostgreSQL server from 16 GB RAM to 128 GB RAM to handle more connections and cache more data in memory.

Example of horizontal: adding three more web server instances behind a load balancer to handle more HTTP requests in parallel.

**How to think through this:**
1. Vertical scaling is simple — no code changes, no coordination — but it has a hard ceiling: the largest machine a cloud provider offers (e.g., AWS `u-24tb1.metal` is ~$219/hr and there is nothing bigger).
2. Once you hit the hardware ceiling, vertical scaling stops. You also create a **single point of failure** — if that one giant machine dies, everything dies.
3. Horizontal scaling introduces complexity (stateless services, distributed state, load balancing) but is theoretically unbounded. The ceiling is your wallet, not the hardware catalog.

**Key takeaway:** Vertical scaling buys you time cheaply; horizontal scaling is the only path to true scale, but it forces you to solve distributed systems problems.

</details>

> 📖 **Theory:** [Scaling Strategies](./02_system_fundamentals/theory.md#vertical-scaling-scale-up)

---

### Q2 · [Normal] · `latency-vs-throughput`

> **Differentiate latency and throughput. If you improve throughput by adding servers, does latency automatically improve? Why or why not?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Latency** is the time it takes for a single request to complete (milliseconds). **Throughput** is the number of requests the system can handle per unit of time (requests per second).

Adding servers improves throughput — you can handle more concurrent requests. Latency does not automatically improve.

**How to think through this:**
1. Imagine a restaurant. Throughput is how many tables get served per hour. Latency is how long one table waits from ordering to receiving food. Adding more waiters helps throughput (more tables served) but if the kitchen is slow, each individual table still waits just as long.
2. If a single request is slow because of a slow database query or a downstream API call, adding more servers does nothing for that request's latency. The bottleneck is not concurrency — it is the critical path of that one request.
3. Latency can actually increase under high load (queuing delay) even with more servers, if coordination overhead (distributed locks, network hops) is introduced. **Little's Law**: `L = λW` — average latency (`W`) rises when the system is saturated regardless of added capacity.

**Key takeaway:** Throughput and latency are independent axes; scaling out helps the former, but fixing latency requires shortening the critical path of a single request.

</details>

> 📖 **Theory:** [Latency vs Throughput](./02_system_fundamentals/theory.md#5-latency-vs-throughput)

---

### Q3 · [Interview] · `availability-reliability-durability`

> **Define availability, reliability, and durability. Give a concrete example where all three differ. What does "five nines" availability mean in practice (downtime per year)?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
- **Availability**: the percentage of time a system is reachable and responding. "Is it up right now?"
- **Reliability**: the probability the system performs its intended function correctly over time, including under load or partial failure. "Does it do the right thing consistently?"
- **Durability**: the guarantee that data, once written, is not lost. "Will my data survive a crash?"

Concrete example — a distributed object store:
- **High availability, low reliability**: S3 returns HTTP 200 for every GET, but occasionally returns a stale or corrupted object due to a replication bug. It is up, but wrong.
- **High reliability, low availability**: A single PostgreSQL primary with full ACID guarantees. When it is up, it always returns correct data. But if it crashes, it takes 5 minutes to restore — low availability during that window.
- **High durability, low availability**: A tape backup system. Your data is safe forever, but retrieving it takes hours.

**Five nines (99.999%)** = 5.26 minutes of downtime per year. In contrast:
- 99.9% (three nines) = 8.76 hours/year
- 99.99% (four nines) = 52.6 minutes/year
- 99.999% (five nines) = 5.26 minutes/year

**How to think through this:**
1. Availability is measured by uptime monitors — it is a binary "up or down" measure aggregated over time.
2. Reliability requires the system to be correct when up — a system with silent data corruption has low reliability even at 100% uptime.
3. Durability is storage-specific — AWS S3 advertises 11 nines of durability (data loss probability of 1 in 100 billion per year) by storing objects across multiple AZs.

**Key takeaway:** A system can be available but unreliable (it responds with wrong answers), reliable but not durable (correct until a disk fails), and durable but unavailable (data is safe but inaccessible) — treat them as separate SLAs.

</details>

> 📖 **Theory:** [Availability & Reliability](./02_system_fundamentals/theory.md#3-availability)

---

### Q4 · [Thinking] · `cap-theorem`

> **State the CAP theorem. What are the three properties and why can you only guarantee two in a distributed system? Give an example of a CP and an AP system.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The **CAP theorem** (Brewer, 2000) states: a distributed system can guarantee at most two of the following three properties simultaneously:

- **Consistency (C)**: every read receives the most recent write or an error
- **Availability (A)**: every request receives a response (not an error), though it may not be the latest data
- **Partition tolerance (P)**: the system continues operating even when network messages between nodes are dropped or delayed

**How to think through this:**
1. In any real distributed system, network partitions happen — routers fail, packets drop, data centers lose connectivity. Partition tolerance is therefore not optional; you must design for it. The real choice is between C and A during a partition.
2. During a partition: if you want consistency, you must refuse requests on the isolated nodes (sacrifice availability). If you want availability, you must let isolated nodes serve potentially stale data (sacrifice consistency).
3. There is no way to be both fully consistent and fully available when nodes cannot communicate — you cannot know if your data is current without talking to the other nodes, and talking to them is impossible during a partition.

**CP system example**: **HBase** or **Zookeeper**. During a partition, they will reject writes on the non-leader partition rather than allow divergence. Consistency is preserved at the cost of availability.

**AP system example**: **Cassandra** or **DynamoDB**. During a partition, all nodes continue accepting reads and writes. When the partition heals, conflicts are resolved (last-write-wins or vector clocks). Availability is preserved at the cost of strong consistency.

**Key takeaway:** CAP forces you to choose your failure mode — refuse requests (CP) or serve potentially stale data (AP) — and that choice should be driven by what your users can tolerate.

</details>

> 📖 **Theory:** [CAP Theorem](./02_system_fundamentals/theory.md#6-cap-theorem)

---

### Q5 · [Thinking] · `eventual-vs-strong-consistency`

> **What is the difference between strong consistency and eventual consistency? Give a real-world example where eventual consistency causes a visible bug to users.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Strong consistency** guarantees that after a write completes, any subsequent read — from any node — sees that write. The system behaves as if there is one copy of the data.

**Eventual consistency** guarantees that if no new updates are made, all replicas will converge to the same value — eventually. In the meantime, different nodes may return different values for the same key.

**How to think through this:**
1. Strong consistency requires coordination (quorum reads/writes, leader-based consensus) which adds latency and reduces availability during partitions.
2. Eventual consistency avoids that coordination cost — writes go to any node immediately, and replication happens in the background. This is faster and more available but creates a window where reads disagree across replicas.
3. The window of inconsistency can be milliseconds or seconds depending on replication lag and network conditions.

**Real-world visible bug**: You post a comment on a social media post. The write goes to replica A. Your friend is reading from replica B, which hasn't replicated yet. Your friend refreshes the page and does not see your comment, even though you posted it 3 seconds ago. The comment "disappears" from your friend's perspective, then reappears on next refresh when replication catches up. This is the "read-your-own-write" consistency violation that eventual consistency does not prevent by default.

**Another example**: A user updates their email address. They immediately try to log in with the new email. The login service reads from a lagging replica that still has the old email, and authentication fails. From the user's perspective, the system is broken.

**Key takeaway:** Eventual consistency trades correctness windows for performance and availability — acceptable for shopping cart counts or social feeds, dangerous for anything involving identity, payments, or inventory.

</details>

> 📖 **Theory:** [Consistency Models](./02_system_fundamentals/theory.md#8-consistency-models)

---

### Q6 · [Normal] · `load-balancer-purpose`

> **What is a load balancer and what problems does it solve? What is the difference between layer 4 (transport) and layer 7 (application) load balancing?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **load balancer** is a component that distributes incoming requests across a pool of backend servers. It solves three core problems: prevents any single server from being overwhelmed, enables horizontal scaling by making multiple servers appear as one, and provides high availability by routing around failed instances.

**Layer 4 (transport-layer) load balancing** operates on IP addresses and TCP/UDP ports. It forwards packets without inspecting the content. It is fast and low-overhead but "dumb" — it cannot make routing decisions based on the request content.

**Layer 7 (application-layer) load balancing** reads the full HTTP request — headers, URL path, cookies, body. It can route `/api/*` to one server farm and `/static/*` to another, terminate TLS, inspect cookies for session affinity, and apply WAF rules. More powerful but more CPU-intensive.

**How to think through this:**
1. L4 is essentially NAT at high speed — it sees `TCP SYN` to port 443 and forwards it. The backend handles TLS.
2. L7 terminates TLS at the load balancer, reads the HTTP request, applies routing rules (path-based, host-based, header-based), then forwards a new TCP connection to the backend.
3. Most production systems use L7 (AWS ALB, nginx, HAProxy in HTTP mode) because content-aware routing is essential. L4 (AWS NLB) is chosen when you need extreme throughput, non-HTTP protocols, or static IP addresses.

**Key takeaway:** L4 is fast and protocol-agnostic; L7 is intelligent and HTTP-aware — choose based on whether you need routing decisions or raw forwarding speed.

</details>

> 📖 **Theory:** [Load Balancer](./08_load_balancing/theory.md#load-balancing--theory)

---

### Q7 · [Normal] · `load-balancing-algorithms`

> **Name and explain four load-balancing algorithms: round robin, weighted round robin, least connections, and IP hash. When would you use IP hash over round robin?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
- **Round robin**: requests are distributed to servers in a fixed rotation — server 1, 2, 3, 1, 2, 3... Simple and uniform when all servers and requests are equivalent.
- **Weighted round robin**: servers have weights reflecting their capacity. A server with weight 3 receives 3 requests for every 1 sent to a server with weight 1. Used when servers have different hardware specs.
- **Least connections**: each new request goes to the server with the fewest active connections. Handles unequal request durations well — avoids piling up on a server processing a slow long-running request.
- **IP hash**: the client's IP address is hashed to determine which server handles the request. The same IP always maps to the same server (assuming the server pool doesn't change).

**When to use IP hash over round robin**: when your application is **stateful** and session state is stored in server memory (not a shared store like Redis). With round robin, a user's second request might land on a different server that has no knowledge of their session. IP hash provides **session affinity** (also called sticky sessions) — the user always hits the same server. Use IP hash when you cannot or haven't yet externalized session state.

**How to think through this:**
1. Round robin breaks down when requests have highly variable latency — a server stuck on a slow query keeps getting new requests it cannot process.
2. Least connections is superior for long-lived connections (WebSockets, file uploads) where connection count is a meaningful proxy for load.
3. IP hash has a failure mode: if one server handles users from a large corporate NAT (all sharing one IP), that server gets hammered. Also, adding/removing a server breaks hash mappings.

**Key takeaway:** Prefer least connections for variable workloads; use IP hash only as a workaround for stateful servers, and aim to eliminate that need by externalizing session state.

</details>

> 📖 **Theory:** [Load Balancing Algorithms](./08_load_balancing/theory.md)

---

### Q8 · [Normal] · `cdn-what-and-why`

> **What is a Content Delivery Network (CDN)? What types of content benefit most from a CDN? What is an origin server and edge node in this context?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **Content Delivery Network (CDN)** is a geographically distributed network of servers that caches and serves content from locations close to end users. Instead of every user's request traveling to your data center in Virginia, a user in Tokyo gets served from a CDN node in Tokyo.

The **origin server** is your actual backend — the authoritative source of content. The **edge node** (also called a Point of Presence, or PoP) is a CDN server geographically close to the user that caches content fetched from the origin.

**Content that benefits most**:
- Static assets: JavaScript bundles, CSS files, images, fonts — never change per-user, can be cached indefinitely with versioned URLs
- Video and audio streams: large files that would saturate a single origin's bandwidth
- Large file downloads: software releases, PDFs
- HTML pages for static sites: pre-rendered pages with long TTLs

**How to think through this:**
1. The benefit is twofold: reduced latency (physical proximity) and reduced origin load (cache absorbs repeated requests). A CDN with a 95% cache hit ratio means 95% of requests never reach your origin.
2. Dynamic, personalized content (user dashboards, real-time feeds) cannot be cached at edge nodes and does not benefit from CDN caching — though CDN can still help by terminating TLS closer to the user and maintaining persistent connections to origin.
3. CDNs also provide DDoS protection by absorbing volumetric attacks at the edge before they reach the origin.

**Key takeaway:** CDNs solve the speed-of-light problem for static content — put the data where the users are, and your origin only handles cache misses and dynamic requests.

</details>

> 📖 **Theory:** [CDN](./07_storage_cdn/theory.md#storage--cdn--theory)

---

### Q9 · [Thinking] · `dns-system-design`

> **How does DNS work in the context of system design? What is a DNS resolver, authoritative server, and TTL? How can DNS be used for load balancing and failover?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**DNS (Domain Name System)** translates human-readable hostnames (e.g., `api.example.com`) into IP addresses. In system design, DNS is often the first layer of traffic routing.

- **DNS resolver**: a server (typically run by the user's ISP or a public provider like `8.8.8.8`) that recursively queries the DNS hierarchy on behalf of the client and caches the result.
- **Authoritative server**: the server that holds the actual DNS records for a domain. When a resolver asks "what is the IP of `api.example.com`?", the authoritative server provides the final answer.
- **TTL (Time To Live)**: the number of seconds a DNS record can be cached. After TTL expires, resolvers must re-query the authoritative server.

**DNS for load balancing**: return multiple A records for the same hostname. The resolver returns all IPs, and clients typically use the first one (round robin at the DNS level). This is called **DNS round robin**. It is coarse and cannot account for server health.

**DNS for failover**: monitor the health of your primary server. If it goes down, update the DNS record to point to the backup server. TTL determines how quickly the change propagates — a TTL of 60 seconds means most clients see the new IP within 1 minute. Pre-lowering TTL before planned maintenance is a best practice.

**How to think through this:**
1. DNS-based load balancing is low-fidelity — once the client has the IP, all requests go there until TTL expires. A failing server keeps receiving requests until DNS propagates the change.
2. Short TTLs enable fast failover but increase load on authoritative servers and can cause cache stampede issues.
3. Services like Route 53 support **health-check-based routing**: if the primary endpoint fails health checks, Route 53 automatically stops returning its IP and returns the failover IP instead — DNS becomes an active health-aware router.

**Key takeaway:** DNS is a coarse routing layer — invaluable for geo-routing and failover, but not a substitute for a real load balancer that can make per-request health decisions.

</details>

> 📖 **Theory:** [DNS](./01_networking_basics/theory.md#5-dns--domain-name-system)

---

### Q10 · [Normal] · `api-gateway-role`

> **What is an API gateway? List five things an API gateway can do that removes the responsibility from individual services.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
An **API gateway** is a single entry point that sits between external clients and internal services. It acts as a reverse proxy, but with intelligence about the API layer.

Five things it handles so individual services don't have to:

1. **Authentication and authorization**: validate JWT tokens, API keys, or OAuth2 bearer tokens centrally. Services receive pre-validated requests with a trusted identity header — they do not need to implement auth logic themselves.
2. **Rate limiting and throttling**: enforce per-client, per-endpoint, or global request rate limits. Without this, every service would need its own rate limiter.
3. **Request routing and versioning**: route `/v1/users` to the v1 user service and `/v2/users` to the v2 user service. Services do not need to handle routing or version negotiation.
4. **SSL/TLS termination**: terminate HTTPS at the gateway and communicate with internal services over plain HTTP on the private network, reducing certificate management burden across services.
5. **Request/response transformation**: translate between external API formats and internal service formats (e.g., rename fields, convert XML to JSON), or aggregate responses from multiple services into a single response (**API composition**).

**How to think through this:**
1. Without a gateway, every service re-implements auth, rate limiting, and logging — inconsistently.
2. The gateway creates a clean boundary between "external concerns" (security, routing, throttling) and "business logic" (what services actually do).
3. The tradeoff: the gateway becomes a critical component — it must be highly available, low latency, and horizontally scalable.

**Key takeaway:** An API gateway is a cross-cutting concerns aggregator — it centralizes the boring-but-critical infrastructure logic so each service can focus purely on its domain.

</details>

> 📖 **Theory:** [API Gateway](./15_cloud_architecture/theory.md)

---

### Q11 · [Interview] · `reverse-proxy-vs-forward-proxy`

> **Compare a reverse proxy vs a forward proxy. What does each protect? Give a real example of each in production systems.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **forward proxy** sits between clients and the internet, acting on behalf of clients. Clients know about the proxy; external servers do not know the real client identity. It protects and controls the client.

A **reverse proxy** sits between the internet and backend servers, acting on behalf of servers. Clients know only the proxy; they do not know how many or which backend servers exist. It protects and controls the server infrastructure.

**Forward proxy — real example**: A corporate network routes all outbound HTTP traffic through a Squid proxy. The proxy enforces browsing policies (block social media), caches repeated requests, and logs all traffic for compliance. Employees' real IPs are hidden from external websites. Tor is another example — each node forwards on behalf of the client.

**Reverse proxy — real example**: nginx deployed in front of three Node.js application servers. External clients hit nginx on port 443. nginx terminates TLS, applies rate limits, and forwards requests to one of the three app servers. The app servers are not exposed to the internet at all. AWS ALB, Cloudflare, and API gateways are all reverse proxies.

**How to think through this:**
1. The naming is from the server's perspective: a forward proxy serves the client by going "forward" toward the internet. A reverse proxy serves the server by intercepting requests coming "in reverse" from the internet.
2. Forward proxy = client anonymity + egress control. Reverse proxy = server protection + load distribution + TLS termination.
3. In many architectures, both exist simultaneously — a corporate forward proxy for employees, and a reverse proxy (CDN + load balancer) protecting internal services.

**Key takeaway:** Forward proxy hides and controls the client; reverse proxy hides and protects the server — they are mirror images serving opposite sides of the connection.

</details>

> 📖 **Theory:** [Reverse Proxy](./01_networking_basics/theory.md)

---

### Q12 · [Thinking] · `database-index`

> **What is a database index and what problem does it solve? Why does adding more indexes slow down writes? Why is an index on a low-cardinality column bad?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **database index** is a separate data structure (typically a B-tree) that maintains a sorted mapping from column values to row locations. Without an index, finding rows matching `WHERE email = 'alice@example.com'` requires a full table scan — reading every row. With an index on `email`, the database binary-searches the index in O(log n) time.

**Why writes slow down with more indexes**: every INSERT, UPDATE, or DELETE must update not just the table row but every index that includes the modified columns. If a table has 8 indexes, a single INSERT triggers 8 index tree updates, each requiring disk I/O and potentially tree rebalancing. Write throughput decreases linearly with the number of indexes.

**Why low-cardinality indexes are bad**: **cardinality** is the number of distinct values in a column. A column like `gender` has 2–3 distinct values. An index on it is nearly useless because even after using the index, the database must read 33–50% of all rows — a full table scan is often faster (sequential I/O vs random I/O). The index adds write overhead with no meaningful read benefit. Low-cardinality columns should use partial indexes (e.g., `WHERE status = 'pending'` when most rows are `'completed'`) or be combined with a high-cardinality column in a composite index.

**How to think through this:**
1. An index trades write performance and storage space for read performance.
2. The selectivity of an index determines its value — the more it narrows down rows, the more useful it is.
3. Composite indexes must be ordered correctly for the query optimizer to use them — the leftmost prefix rule applies in B-tree indexes.

**Key takeaway:** Indexes are read optimizations with a write tax — only add them for high-cardinality, frequently-queried columns, and measure the write impact before deploying to production.

</details>

> 📖 **Theory:** [Database Indexes](./05_databases/theory.md)

---

### Q13 · [Normal] · `btree-vs-hash-index`

> **Compare B-tree indexes vs hash indexes. What operations does each support efficiently? When would a hash index outperform a B-tree index?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **B-tree index** stores keys in a balanced sorted tree. It supports equality lookups, range queries (`BETWEEN`, `>`, `<`), prefix matches, and `ORDER BY` operations. Lookup complexity is O(log n).

A **hash index** stores keys in a hash table. It only supports exact equality lookups (`=`). It does not support range queries, sorting, or prefix matching. Lookup complexity is O(1) average.

**When hash outperforms B-tree**: for pure equality lookups on a column with many distinct values (e.g., `WHERE session_id = ?`), a hash index is faster because it is O(1) vs O(log n). The difference is most noticeable at very large scale where the B-tree becomes deep. Redis uses hash tables internally for its key-value lookups for exactly this reason.

**How to think through this:**
1. B-tree is the universal default because most real queries involve ranges or sorting — not just equality. PostgreSQL's default index type is B-tree.
2. Hash indexes are memory-resident in most databases (e.g., PostgreSQL hash indexes weren't crash-safe before v10). They cannot support multi-column range queries at all.
3. For a `users` table where you always look up by exact primary key UUID, a hash index would be theoretically faster — but the practical difference is minimal at typical table sizes, and B-tree's versatility wins.

**Key takeaway:** Use B-tree by default because it handles all query types; consider hash only for high-volume pure-equality lookups where O(1) vs O(log n) is measurably significant.

</details>

> 📖 **Theory:** [B-Tree vs Hash Index](./05_databases/theory.md)

---

### Q14 · [Normal] · `database-sharding`

> **What is database sharding? What problem does it solve? What is a shard key and why is choosing a bad one catastrophic?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Database sharding** is horizontal partitioning of data across multiple independent database instances (shards), each holding a subset of the total data. Unlike replication (where all nodes have all data), each shard holds only a portion.

Problem it solves: a single database instance has limits on storage, write throughput, and connection count. Once a table has billions of rows and terabytes of data, even with indexes and tuning, a single node cannot keep up. Sharding distributes both data and write load across multiple nodes.

A **shard key** is the column (or combination of columns) used to determine which shard a row belongs to. The shard key is used in a routing function: `hash(shard_key) % num_shards` → shard ID.

**Why a bad shard key is catastrophic**:
1. **Hot shards**: if you shard a social media platform by `country_code`, the US shard receives 40% of all traffic while smaller country shards sit idle. One shard becomes the bottleneck, defeating the purpose of sharding.
2. **Uneven data distribution**: sharding user activity by `created_at` date puts all new writes on the most recent date's shard. Historical shards are cold, the current shard is overloaded.
3. **Inability to rebalance without downtime**: once data is written to shards, changing the shard key requires a full data migration — an extremely expensive offline operation.
4. **Cross-shard queries**: if your access patterns require joining data across shards (e.g., "all orders from all users in this region"), each query becomes a scatter-gather across many shards, destroying performance.


**How to think through this:**
1. Start with the problem: a single DB node hits limits on storage, write throughput, and connections at scale.
2. Sharding solves this by distributing both **data** and **writes** across independent nodes — each node owns a subset of rows.
3. The shard key determines distribution: a bad key creates a hot shard that receives all traffic, defeating the purpose entirely.

**Key takeaway:** The shard key decision is effectively permanent and determines your system's scalability ceiling — choose a key with high cardinality and uniform distribution that aligns with your primary access patterns.

</details>

> 📖 **Theory:** [Database Sharding](./05_databases/theory.md)

---

### Q15 · [Thinking] · `database-replication`

> **What is primary-replica replication? How does it help read scalability? What is replication lag and what consistency issues does it cause for reads?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Primary-replica replication** (also called master-slave) is a database pattern where one node (the **primary**) accepts all writes and asynchronously (or synchronously) copies those changes to one or more **replica** nodes. Replicas are read-only copies of the primary.

Read scalability: direct all write traffic to the primary and distribute read traffic across replicas. If reads are 90% of your workload, adding replicas nearly linearly scales read capacity. This is the most common scaling pattern for read-heavy applications.

**Replication lag** is the delay between when a write completes on the primary and when it appears on replicas. In asynchronous replication, replicas apply changes from the primary's write-ahead log in the background. During periods of high write load, lag can grow from milliseconds to seconds.

**Consistency issues caused by replication lag**:
1. **Read-your-own-writes violation**: a user updates their profile photo. The write goes to the primary. They immediately reload the page; the read goes to a replica that hasn't applied the update yet. They see the old photo. The system appears to have lost their change.
2. **Monotonic read violation**: a user reads a comment from replica A (up to date), then their next request hits replica B (lagging). The comment they just saw is now gone. Time appears to go backwards.
3. **Stale inventory reads**: a user reads available stock from a replica (shows 5 units). Another user has already purchased all units and that write hasn't replicated yet. The first user adds to cart, then fails at checkout due to no inventory.

**How to think through this:**
1. Synchronous replication (primary waits for replica ACK before confirming write) eliminates lag but doubles write latency and breaks if any replica is slow.
2. The fix for read-your-own-writes is to always route a user's reads to the primary for a short window after they perform a write, or to use a session-level read-after-write guarantee.

**Key takeaway:** Replication lag turns your replica reads into a time machine pointing to the past — design your read routing strategy around which users and operations can tolerate that staleness.

</details>

> 📖 **Theory:** [Database Replication](./05_databases/theory.md)

---

### Q16 · [Normal] · `cache-when-to-use`

> **What is a cache in system design? Give three scenarios where a cache dramatically reduces database load. What makes data "cacheable"?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **cache** is a fast, in-memory data store that holds copies of frequently accessed data to avoid repeated expensive computations or database reads. Redis and Memcached are the dominant caching layers in system design.

Three scenarios where caches dramatically reduce DB load:

1. **User session data**: millions of HTTP requests per second need to verify a session token. Without a cache, each request hits the database. With Redis storing `session_id → user_id`, lookups are sub-millisecond and the database never sees session verification queries.
2. **Product catalog**: an e-commerce site with 100,000 products serves product detail pages. The product data changes rarely but is read millions of times per day. Caching product objects eliminates the vast majority of SELECT queries.
3. **Leaderboard / aggregated counts**: a game's global leaderboard requires expensive aggregation queries across millions of rows. Pre-compute and cache the top-100 list, update it every 60 seconds. The database runs that expensive query once per minute instead of once per page load.

**What makes data cacheable**:
- **Read-heavy, write-infrequent**: data is read far more than it changes (otherwise the cache is stale constantly)
- **Expensive to compute or fetch**: justifies the complexity of maintaining a cache
- **Tolerates staleness**: the application can function correctly if the cached value is slightly out of date (a few seconds to minutes)
- **Shareable across users**: public or shared data is more cache-efficient than user-specific data (though per-user caching is valid for session data)


**How to think through this:**
1. Ask: what is expensive to compute or fetch repeatedly? Databases, external APIs, and CPU-heavy calculations are prime cache candidates.
2. Cache is effective when data is: read frequently, written rarely, and acceptable to serve slightly stale.
3. The three scenarios show different motivations: reducing DB load, reducing latency, and reducing expensive computation.

**Key takeaway:** Cache what is expensive to recompute, read far more than written, and safe to serve slightly stale — if all three are true, the cache ROI is enormous.

</details>

> 📖 **Theory:** [When to Cache](./06_caching/theory.md)

---

### Q17 · [Normal] · `cache-hit-miss`

> **What is a cache hit vs a cache miss? What is cache hit ratio and why does it matter? What happens at high traffic if hit ratio drops from 90% to 70%?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **cache hit** occurs when the requested data is found in the cache and returned without touching the database. A **cache miss** occurs when the data is not in the cache; the system fetches it from the database, returns it to the client, and typically populates the cache for future requests.

**Cache hit ratio** = (hits / total requests) × 100. It measures what fraction of requests are served from cache. It is the primary metric for cache effectiveness.

**Impact of hit ratio drop from 90% to 70%**:

At 90% hit ratio with 1,000 requests/sec: 100 requests/sec reach the database.
At 70% hit ratio with 1,000 requests/sec: 300 requests/sec reach the database — a 3× increase in database load, with the same traffic.

At high traffic (e.g., 50,000 req/sec):
- 90% hit ratio: 5,000 req/sec to DB (manageable)
- 70% hit ratio: 15,000 req/sec to DB (likely overwhelms the database, causing cascading failure)

This is a **cache stampede** risk: if the hit ratio drops suddenly (e.g., due to a cache restart, mass eviction, or a new traffic pattern), the database is flooded with requests it was never provisioned to handle — it falls over, and the application goes down.

**How to think through this:**
1. Database provisioning is typically sized for the miss traffic at healthy hit ratio, not total traffic. A hit ratio drop exposes this gap instantly.
2. Techniques to protect against sudden drop: **cache warming** on startup, **probabilistic early expiration** (refresh before TTL expires), and **circuit breakers** that shed load if DB latency spikes.

**Key takeaway:** Hit ratio is not just a performance metric — it is a safety margin; the database is provisioned for miss traffic, and a sudden drop can cause a total outage.

</details>

> 📖 **Theory:** [Cache Hit & Miss](./06_caching/theory.md)

---

### Q18 · [Normal] · `cache-eviction-policies`

> **Explain LRU, LFU, and FIFO cache eviction policies. Give a use case where each is the most appropriate choice.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**LRU (Least Recently Used)**: evicts the item that has not been accessed for the longest time. Operates on access recency.

**LFU (Least Frequently Used)**: evicts the item with the fewest total accesses over time. Operates on access frequency.

**FIFO (First In, First Out)**: evicts the item that was inserted into the cache first, regardless of access pattern. Operates on insertion order.

**Use case where each fits best**:

**LRU — web page cache**: users browse recently viewed products, news articles, or social media posts. Recency is a strong signal for future access — what you looked at 5 seconds ago is more likely to be needed again than what you looked at last week. LRU naturally keeps the "hot window" of recent content in cache. Redis's default eviction policy (`allkeys-lru`) uses LRU.

**LFU — CDN or content recommendation cache**: certain content (a viral video, a popular product) is accessed millions of times over weeks. LRU would evict it if nothing accessed it in the last hour. LFU retains it because of its cumulative high access count. Use LFU when popularity (not recency) predicts future access — media streaming, ads serving, product catalogs.

**FIFO — simple time-windowed data**: rate limiter buckets, temporary session tokens, or any cache where items have a fixed useful lifetime and recency/frequency don't matter. FIFO is simple, deterministic, and has no per-item metadata overhead. Use it when all items have equal expected utility and you just need to cap the cache size.


**How to think through this:**
1. Eviction policies exist because caches have fixed size — when full, something must be removed to make room.
2. Each policy embeds an assumption about access patterns: LRU assumes recency predicts future access; LFU assumes frequency predicts it; FIFO makes no assumption.
3. Match the policy to the workload: sessions need LRU (recency matters), trending content needs LFU (popularity matters), batch processing can use FIFO.

**Key takeaway:** LRU = recency wins, LFU = popularity wins, FIFO = fairness / simplicity — match the eviction policy to what predicts future cache utility in your access pattern.

</details>

> 📖 **Theory:** [Cache Eviction](./06_caching/theory.md)

---

### Q19 · [Normal] · `message-queue-purpose`

> **What is a message queue? What two problems does it solve that a direct API call does not? Name two popular message queue systems.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **message queue** is a durable buffer between a producer (the service that generates work) and a consumer (the service that processes it). The producer writes messages to the queue; the consumer reads and processes them independently, at its own pace.

**Two problems it solves that a direct API call cannot**:

1. **Temporal decoupling (handling downstream unavailability)**: with a direct API call, if the downstream service is down, the call fails. The producer must retry, implement backoff logic, or lose the work. With a message queue, the producer writes the message to the queue and succeeds immediately. When the downstream service recovers, it processes the queued messages. The producer never needs to know the consumer was unavailable.

2. **Rate decoupling (absorbing traffic spikes)**: a direct API call requires the consumer to handle every request at the same rate as the producer. During a traffic spike, the consumer is overwhelmed. A message queue acts as a shock absorber — the producer dumps messages into the queue at burst rate; the consumer processes them at its maximum sustainable rate. The queue depth grows during the spike and drains when traffic normalizes. The consumer never needs to be provisioned for peak throughput.

**Two popular message queue systems**:
- **Apache Kafka**: distributed, append-only log; designed for high-throughput event streaming; messages are retained for configurable periods and can be replayed; used for event sourcing, stream processing, and analytics pipelines.
- **Amazon SQS / RabbitMQ**: traditional job queues; messages are consumed and deleted; designed for task distribution, background jobs, and microservice communication.


**How to think through this:**
1. Start with what a direct API call cannot do: if the receiver is down, the message is lost. A queue decouples sender from receiver.
2. The two core problems solved: **temporal decoupling** (sender and receiver don't need to be up simultaneously) and **load leveling** (absorb traffic spikes).
3. Message queues enable async processing — the sender gets an immediate acknowledgment and moves on; the receiver processes at its own pace.

**Key takeaway:** A message queue is a time machine and a pressure valve — it lets producer and consumer work at different times and different rates without either failing.

</details>

> 📖 **Theory:** [Message Queues](./09_message_queues/theory.md#message-queues--theory)

---

### Q20 · [Thinking] · `sync-vs-async-communication`

> **Compare synchronous and asynchronous service communication. What happens to Service A if Service B is down in each model? When is async communication essential?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
In **synchronous communication**, Service A makes a call to Service B and waits for the response before continuing. The two services are temporally coupled — A cannot proceed without B's answer (REST HTTP calls, gRPC are synchronous by default).

In **asynchronous communication**, Service A publishes a message or event and immediately continues without waiting. Service B processes the message in its own time. A message queue or event bus (Kafka, SQS, RabbitMQ) sits between them.

**What happens if Service B is down**:
- **Synchronous**: Service A's request fails immediately. A must handle the error — retry, return an error to the user, or degrade gracefully. If A cannot function without B's response (e.g., B performs authentication), A's functionality is impaired or broken. Cascading failures are common: if B is slow (not just down), A holds open connections waiting, exhausts its thread pool, and also becomes unresponsive.
- **Asynchronous**: Service A successfully publishes its message and continues. The message sits in the queue. When B recovers, it processes the backlog. From A's perspective, nothing failed. The user experience depends on whether the operation is fire-and-forget (email notification) or has a visible result.

**When async is essential**:
1. **Long-running work**: image processing, video transcoding, ML inference — operations that take seconds to minutes. Holding an HTTP connection open that long is impractical.
2. **Fan-out**: one event must trigger many consumers (a user signup triggers: send welcome email, create billing record, provision storage quota, update analytics). Async pub/sub handles all consumers without the producer knowing about them.
3. **Resilience requirements**: when the system must continue accepting work even if downstream processors are degraded — e-commerce order intake must never stop even if the fulfillment system is down.
4. **Traffic spike absorption**: batch job submission, webhook processing, IoT sensor ingestion.


**How to think through this:**
1. In synchronous communication, Service A waits blocked while B processes. If B is slow or down, A is slow or down too — failures cascade.
2. In async communication, A sends a message and continues immediately. B processes when ready. A and B are temporally decoupled.
3. The key question is: does the caller need an immediate result? If yes, sync. If it can accept eventual completion, async enables resilience and scalability.

**Key takeaway:** Synchronous communication is simpler but creates tight availability coupling — if one service is slow or down, it takes others with it; async communication trades immediacy for resilience.

</details>

> 📖 **Theory:** [Sync vs Async](./09_message_queues/theory.md)

---

### Q21 · [Normal] · `what-is-microservice`

> **What is a microservice? What are the two key characteristics that distinguish it from a module inside a monolith?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **microservice** is an independently deployable service that owns a single bounded domain of business functionality and communicates with other services exclusively via network APIs (HTTP, gRPC, message queue).

The two characteristics that distinguish a microservice from a module in a monolith:

1. **Independent deployability**: a module in a monolith is compiled and deployed with the entire application — changing the auth module requires redeploying the whole codebase. A microservice is deployed as its own process, container, or binary. You can deploy a new version of the payment service without touching the user service, the catalog service, or anything else. This requires that the service's API contracts are stable (versioned, backward compatible).

2. **Process and data isolation**: modules in a monolith share memory, a single process, and almost always a single database. A microservice runs in its own process and owns its own data store — no other service directly reads or writes its database. All data access goes through the service's API. This isolation enables independent scaling, independent technology choices, and prevents one service's database bug from corrupting another's data. The database-per-service pattern is the defining structural difference.

**How to think through this:**
1. These two properties are what enable independent team ownership — two teams can develop, test, and release their services without coordination.
2. Both properties also create the complexity of microservices: network calls fail (unlike in-process calls), and no database-level JOIN across services means you must handle distributed queries and consistency yourself.

**Key takeaway:** A microservice is not just "a small service" — it is specifically a service that can be deployed and scaled independently, which requires both process isolation and owning its own data.

</details>

> 📖 **Theory:** [Microservices](./12_microservices/theory.md#microservices--theory)

---

### Q22 · [Interview] · `monolith-vs-microservice`

> **Compare a monolith vs a microservices architecture. When should a startup stay with a monolith? What signals suggest it is time to break it apart?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **monolith** is a single deployable unit where all functionality — user management, billing, product catalog, notifications — runs in one process and shares one database. A **microservices architecture** decomposes that system into independently deployable services, each owning its domain and data.

**Monolith advantages**: simple to develop, test, debug, and deploy early on. A single codebase, a single database, in-process function calls (no network latency or failure), easy local development setup, simple observability (one log stream, one trace). Operational complexity is minimal.

**Microservices advantages**: independent scalability (scale only the bottlenecked service), independent deployability (teams ship without coordination), technology flexibility (each service picks the right DB and language), fault isolation (one service crashing doesn't kill others), and team autonomy at scale.

**When a startup should stay with a monolith**: almost always, at first. Until you have 15+ engineers, stable domain boundaries, measurable scaling bottlenecks, and the operational maturity (Kubernetes, distributed tracing, CI/CD per service), microservices add enormous overhead for zero benefit. The rule of thumb: start monolith, break apart when the pain of the monolith exceeds the pain of distribution.

**Signals it is time to break apart**:
1. **Deployment bottleneck**: a small change to the notification service requires QA and approval for the entire codebase, slowing all teams down
2. **Scaling mismatch**: the image processing component needs 10× the CPU of every other component, but you must scale the entire monolith to scale it
3. **Team ownership conflicts**: multiple large teams merging code into one repo causes constant conflicts and coordination overhead
4. **Technology constraints**: one component would benefit enormously from a different language or data store that is impossible to introduce in a monolith
5. **Blast radius**: a memory leak in one module takes down the entire application repeatedly

**How to think through this:**
1. The "modular monolith" is an underrated intermediate step — enforce module boundaries (no cross-module DB access, interface-only communication) within a monolith. This gives you team clarity without distributed systems complexity.
2. Extract the service with the clearest boundary and highest independent scaling need first. Don't big-bang decompose.

**Key takeaway:** A well-structured monolith beats a poorly-executed microservices architecture every time — microservices are an organizational scaling solution, not a technical one; use them when team coordination, not code complexity, is the bottleneck.

</details>

> 📖 **Theory:** [Monolith vs Microservices](./12_microservices/theory.md#microservices--theory)

---

### Q23 · [Thinking] · `rest-in-system-design`

> **In system design interviews, when an interviewer says "use a REST API between services," what are they really asking you to consider? What are the hidden tradeoffs of REST for internal service communication?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
When an interviewer says "use REST," they are signaling: define the interface contract between services — what does each endpoint accept, what does it return, and who calls whom? They are asking you to think about synchronous request-response communication and its implications.

What they want you to address:
- Endpoint design, request/response schemas, HTTP methods and status codes
- Authentication between services (mTLS, service tokens)
- Versioning strategy for the API contract
- Error handling and retry behavior

**Hidden tradeoffs of REST for internal (service-to-service) communication**:

1. **Performance overhead**: HTTP/1.1 with JSON is verbose. Every request pays for TCP connection establishment (or connection pool overhead), HTTP header parsing, and JSON serialization/deserialization. For high-frequency internal calls (thousands/sec between services), this adds meaningful latency and CPU cost. gRPC with Protocol Buffers is typically 5–10× more efficient for internal communication.

2. **Schema drift and lack of enforcement**: REST APIs with JSON have no built-in schema enforcement at the transport layer. A producer can rename a field; consumers silently receive `null` and fail in unexpected ways. Protobuf (gRPC) and Avro/Confluent Schema Registry (Kafka) enforce contracts at the protocol level.

3. **Synchronous coupling**: REST is synchronous by default — the caller blocks waiting for a response. This propagates failure (if the downstream is slow, the upstream is slow) and ties service latency budgets together. Internal calls that don't require an immediate response are often better served by an async message queue.

4. **Versioning complexity**: maintaining `/v1` and `/v2` endpoints in parallel is manageable but adds long-term operational burden. gRPC and message schemas handle backward compatibility more gracefully.

**How to think through this:**
1. REST is excellent for external-facing APIs (clients are diverse, tooling is universal). For internal service calls with high throughput requirements, gRPC is often better.
2. In interviews, acknowledging these tradeoffs and suggesting "REST for external APIs, gRPC for internal service communication" signals senior-level thinking.

**Key takeaway:** REST is a default assumption, not always the best answer — for internal services, consider gRPC for performance and schema safety, and async messaging when temporal decoupling is needed.

</details>

> 📖 **Theory:** [REST in System Design](./03_api_design/theory.md)

---

### Q24 · [Interview] · `relational-vs-nosql`

> **Compare relational databases and NoSQL databases. What does "schema-on-write" vs "schema-on-read" mean? Give a concrete example where NoSQL is the right choice.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Relational databases** (PostgreSQL, MySQL) store data in tables with a fixed schema, enforce ACID transactions, and support complex queries with JOINs. Structure is strictly enforced before data is written.

**NoSQL databases** is a broad category including document stores (MongoDB), key-value stores (Redis, DynamoDB), wide-column stores (Cassandra, HBase), and graph databases (Neo4j). They trade ACID guarantees and rigid schemas for flexibility, horizontal scalability, and performance for specific access patterns.

**Schema-on-write** (relational): the schema is defined before any data is written. Every row must conform to the table definition. Adding a field requires an ALTER TABLE migration — a controlled, explicit change. This enforces data integrity at write time.

**Schema-on-read** (NoSQL documents): data is written in any shape; the schema is interpreted when reading. A MongoDB document in the `users` collection can have any fields — `{"name": "alice", "age": 30}` and `{"name": "bob", "preferences": {"theme": "dark"}}` coexist. The application code interprets structure at read time. Flexible, but errors (missing fields, wrong types) are discovered late at runtime.

**Concrete example where NoSQL is right**: a product catalog for an e-commerce platform with heterogeneous product types. A laptop has `ram`, `cpu`, `screen_size`. A t-shirt has `sizes`, `colors`, `material`. A book has `isbn`, `author`, `page_count`. Modelling this relationally requires either a gigantic table with hundreds of nullable columns, or an entity-attribute-value (EAV) pattern that is complex and slow to query. A document store (MongoDB, DynamoDB) naturally stores each product as a document with exactly the fields relevant to its type, and queries remain simple.

**How to think through this:**
1. Choose relational when: data has relationships requiring JOINs, transactions span multiple entities, data shape is stable, and consistency is critical (financial systems, order management).
2. Choose NoSQL when: schema is variable or evolving rapidly, access patterns are simple and known upfront, horizontal write scale is required, or you need specialized access patterns (time series, graph traversal).

**Key takeaway:** Schema-on-write prioritizes data integrity at the cost of flexibility; schema-on-read prioritizes flexibility at the cost of runtime correctness guarantees — pick based on whether your domain's structure is known and stable.

</details>

> 📖 **Theory:** [SQL vs NoSQL](./05_databases/theory.md)

---

### Q25 · [Design] · `sql-vs-nosql-when`

> **You are designing a system with these requirements: user profiles (flexible attributes), order history (relational joins), product catalog (read-heavy), and activity logs (high write). Which data store type would you use for each and why?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**User profiles — Document store (MongoDB or DynamoDB)**:
User attributes are heterogeneous and evolve over time. A free user has different attributes than an enterprise user. Users add social logins, preferences, and metadata at different rates. Schema-on-read flexibility and the absence of a JOIN requirement make a document store the right fit. Access pattern is almost always by `user_id` (key-value style), which documents handle efficiently.

**Order history — Relational database (PostgreSQL)**:
Orders inherently involve multiple entities: an order references users, line items, products, payments, shipping addresses. Answering business queries requires JOINs: "orders placed by users who signed up in Q3, broken down by product category." These are natural relational queries. ACID transactions are critical — placing an order must atomically debit inventory and create the order record. Use PostgreSQL.

**Product catalog — Relational or document store with a caching layer (Redis/CDN)**:
Product data is read millions of times more than it is written. The store choice (Postgres or MongoDB both work) matters less than the caching strategy. Cache product objects in Redis with a TTL of minutes. For a large catalog with diverse product types (see Q24), a document store avoids the schema flexibility problems. For a simpler catalog with uniform products, Postgres with a Redis cache is clean and sufficient.

**Activity logs — Wide-column store or append-only log (Cassandra or Apache Kafka)**:
Activity logs are an immutable, high-volume, time-series append workload. Millions of events per second (clicks, page views, API calls) with no UPDATE or DELETE operations. Cassandra handles extreme write throughput by distributing writes across nodes with no coordination overhead. Kafka is ideal if the logs need to be streamed to downstream consumers (analytics, ML pipelines) in real time. Avoid a relational database here — writes will saturate it quickly, and there are no JOINs needed.

**How to think through this:**
1. The key questions: What are the access patterns? What are the consistency requirements? Does the schema need to flex?
2. The caching layer is often as important as the primary store — a read-heavy workload is a caching problem as much as a database selection problem.

**Key takeaway:** Match the data store to the dominant access pattern and consistency requirement for each data type — a real system uses 3–5 different stores, not one.

</details>

> 📖 **Theory:** [When to use SQL vs NoSQL](./05_databases/theory.md)

---

### Q26 · [Design] · `read-heavy-write-heavy`

> **How do you design differently for a read-heavy system vs a write-heavy system? Give two concrete architectural techniques for each.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**Read-heavy system design techniques**:

1. **Read replicas + query routing**: add multiple read replicas to the primary database and route all read queries to replicas, all writes to the primary. Scales read capacity linearly with replica count. Used by most large-scale web applications (Facebook, Twitter timelines, e-commerce product pages). The tradeoff is replication lag (see Q15).

2. **Multi-layer caching**: add Redis or Memcached in front of the database. Cache frequently read objects (user profiles, product data, config values) with TTLs appropriate to the acceptable staleness. A CDN for static assets handles the edge layer. A well-tuned cache stack can serve 95%+ of read traffic without touching the database, allowing the DB to handle only cache misses and writes.

**Write-heavy system design techniques**:

1. **Async write buffering via message queue**: instead of writing directly to the database on every user action, publish events to a message queue (Kafka). A consumer service batches and writes to the database at a controlled rate. This decouples the write rate from the database's absorption capacity and prevents a traffic spike from overwhelming the DB. Used in IoT ingestion pipelines, analytics event collection, and audit logging.

2. **Sharding + write partitioning**: distribute write load across multiple database shards (see Q14). Each shard handles a subset of keys and absorbs a fraction of total write volume. Alternatively, use a write-optimized data store (Cassandra, DynamoDB) designed for high write throughput via log-structured merge trees (LSM trees), which convert random writes into sequential disk I/O — dramatically faster than B-tree update-in-place on spinning disks.

**How to think through this:**
1. In practice, most systems are read-heavy (10:1 to 100:1 read-to-write ratio). Pure write-heavy systems (telemetry, logging, IoT) are specialized.
2. For mixed workloads, CQRS (Command Query Responsibility Segregation) separates the read and write models entirely — different schemas, stores, and services for reads vs writes.

**Key takeaway:** Read-heavy systems scale by multiplying read paths (replicas, caches); write-heavy systems scale by distributing write paths (sharding, async buffering) and choosing write-optimized storage engines.

</details>

> 📖 **Theory:** [Read/Write Patterns](./11_scalability_patterns/theory.md)

---

### Q27 · [Thinking] · `master-slave-replication`

> **In primary-replica (master-slave) replication, what happens if the primary fails? What is the risk of an automatic failover that promotes the replica with the most replication lag?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
When the primary fails, the system must promote a replica to become the new primary. This process is called **failover**. In managed databases (AWS RDS Multi-AZ, Google Cloud SQL), failover is automatic and typically completes in 20–60 seconds. In self-managed setups, a consensus-based sentinel (Redis Sentinel) or orchestration tool (Patroni for PostgreSQL) handles promotion.

**Risk of promoting the lagging replica**:

If the promoted replica has **replication lag** — it has not yet applied all of the old primary's writes — those missing writes are **permanently lost**. This is a **data loss event**.

Example: the primary processes 1,000 writes before crashing. The best replica received 980 of them (20 writes stuck in the replication stream). If this replica is promoted, those 20 write operations are gone forever — no log to replay, no way to recover them unless you have point-in-time backup (which only recovers to the last snapshot, not real-time).

**Compounding risk — split brain**: before failover, if the "failed" primary is actually alive but network-partitioned, you now have two nodes accepting writes simultaneously: the old primary (unreachable but running) and the newly promoted replica. When the partition heals, you have conflicting write histories with no deterministic merge strategy.

**How to think through this:**
1. To minimize lag at failover, use **synchronous replication** for the primary replica — the primary does not ACK a write until at least one replica confirms receipt. Zero replication lag, but write latency doubles.
2. Most systems use a compromise: one synchronous replica (for failover safety) and several asynchronous replicas (for read scalability).
3. **STONITH (Shoot The Other Node In The Head)** — in serious HA setups, before promoting the replica, the system fences (forcibly powers off) the old primary to prevent split brain. It is a dramatic name for a critical safety mechanism.

**Key takeaway:** Automatic failover to a lagging replica trades data loss risk for speed of recovery — synchronous replication eliminates the lag at the cost of write latency, and the right choice depends on your data loss tolerance (RPO).

</details>

> 📖 **Theory:** [Primary-Replica Replication](./05_databases/theory.md)

---

### Q28 · [Critical] · `multi-master-conflicts`

> **What is a conflict in multi-master database replication? Give a concrete example: two users edit the same record simultaneously on different masters. How do systems resolve this?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
In **multi-master replication**, two or more nodes each accept writes independently. Changes are replicated to peer nodes asynchronously. A **conflict** occurs when two nodes accept concurrent writes to the same data item before either write has been replicated to the other node — creating a divergent state that must be reconciled.

**Concrete example**:
- User Alice and User Bob both have access to a shared document. The document has a field `title = "Draft"`.
- Alice is connected to Master A and updates the title to `"Final Report"` at T=100ms.
- Bob is connected to Master B and updates the title to `"Approved"` at T=105ms.
- Replication between A and B has a 200ms lag.
- At T=200ms, both masters apply the change from the other. Master A now has two versions: `"Final Report"` (local) and `"Approved"` (incoming). Master B has the same conflict.
- Which value "wins"?

**Conflict resolution strategies**:

1. **Last-write-wins (LWW)**: the write with the highest timestamp wins. Simple, but clocks across distributed nodes are never perfectly synchronized (**clock skew**). A node with a slightly fast clock always wins, regardless of the actual order of operations. This causes silent, invisible data loss. DynamoDB and Cassandra use LWW by default.

2. **Application-level conflict resolution**: the database surfaces the conflict to the application and lets it decide. CouchDB works this way — both versions are stored as "conflicting revisions," and the application must merge or pick one. Correct but requires significant application complexity.

3. **Vector clocks / version vectors**: track causality between writes, not just timestamps. If write B happened after write A (B has A's vector clock entry), B wins without conflict. If A and B are concurrent (neither has seen the other), it is a true conflict requiring resolution. Riak used vector clocks; this is the theoretically correct approach.

4. **Operational transformation / CRDTs (Conflict-Free Replicated Data Types)**: for specific data types (counters, sets, append-only lists), mathematical structures guarantee that any merge of concurrent writes produces the same result regardless of order. Google Docs uses operational transformation. Redis CRDT (for Redis Enterprise Active-Active) uses CRDTs. CRDTs eliminate conflicts by constraining what operations are allowed.

**How to think through this:**
1. Multi-master is the hardest consistency problem in distributed systems. Most systems avoid it unless geographic availability (active-active multi-region) demands it.
2. The safest approach for most applications: single primary with read replicas, and accept the availability tradeoff during primary failover.

**Key takeaway:** Multi-master conflicts are inevitable when concurrent writes race across replication lag — LWW is simple but lossy, CRDTs eliminate the problem class entirely for compatible data types, everything else requires application involvement.

</details>

> 📖 **Theory:** [Multi-Master Replication](./05_databases/theory.md)

---

### Q29 · [Normal] · `db-partitioning-strategies`

> **Compare three database partitioning strategies: range partitioning, hash partitioning, and directory-based partitioning. What is a hot partition and which strategy is most prone to it?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Range partitioning**: rows are assigned to partitions based on a range of the partition key's values. Example: orders from 2020 go to partition 1, 2021 to partition 2, 2022 to partition 3. Time-series data is naturally range-partitioned. Range queries (`WHERE created_at BETWEEN '2022-01-01' AND '2022-12-31'`) are efficient — they read only the relevant partition.

**Hash partitioning**: the partition key is hashed and the result modulo the partition count determines the destination. Example: `hash(user_id) % 10` assigns users evenly across 10 partitions. Distribution is statistically uniform; no knowledge of the data distribution is required. Range queries are inefficient — they must scan all partitions.

**Directory-based partitioning**: a lookup table (directory service) maps each key to its partition explicitly. Example: a directory stores `{user_id: 10001 → shard 3, user_id: 10002 → shard 7}`. Maximum flexibility — keys can be reassigned to different partitions without changing the hash function. The directory itself becomes a critical dependency and potential bottleneck.

**Hot partition**: a **hot partition** is one that receives disproportionately more traffic than others — it becomes the system bottleneck even as other partitions sit underutilized. The performance of the entire system is constrained by the hot partition.

**Most prone to hot partitions**: **range partitioning**. In a time-series system partitioned by date, all new writes go to the current day's partition. That partition is constantly hot while historical partitions are cold. Similarly, range partitioning by a skewed key (e.g., country code where the US dominates) creates a structurally hot partition for the most common value.

Hash partitioning distributes load by randomizing assignment, making hot partitions less likely — unless many users share the same hash key (e.g., a viral celebrity's data all hashes to the same shard).


**How to think through this:**
1. Partitioning strategies differ in how they decide which shard owns a given row — the partition function.
2. Range partitioning is intuitive (dates, IDs) but creates hot partitions for recent data. Hash partitioning distributes evenly but loses range query locality.
3. A hot partition happens when one partition receives disproportionate traffic — the goal is to choose a strategy that balances load across partitions.

**Key takeaway:** Range partitioning optimizes for range queries and ordered scans at the cost of hot partition risk; hash partitioning optimizes for write distribution but sacrifices range query efficiency — the tradeoff is always between query efficiency and load uniformity.

</details>

> 📖 **Theory:** [Partitioning Strategies](./05_databases/theory.md)

---

### Q30 · [Thinking] · `consistent-hashing`

> **What problem does consistent hashing solve that simple modulo hashing (`key % n`) doesn't? How many keys are remapped when a node is added or removed in consistent hashing?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Simple modulo hashing** (`key % n`) maps keys to nodes by dividing the key hash by the node count. This works until `n` changes.

The problem: when a node is added or removed, `n` changes, so `key % n` produces different results for almost every key. If you had 10 nodes and add 1 (n=11), `key % 10` and `key % 11` give different results for ~91% of keys. Effectively, you must remap ~90% of all cached data to different nodes — a **cache invalidation avalanche**. Every remapped key is a cache miss, slamming the origin servers simultaneously. At scale, this causes an outage.

**Consistent hashing** solves this by mapping both keys and nodes onto a circular ring (hash space from 0 to 2³²). A key is assigned to the first node encountered when traversing the ring clockwise from the key's hash position.

**When a node is added**: only the keys that previously would have been assigned to the next node clockwise (the new node's neighbor) are remapped to the new node. Approximately `K/n` keys are remapped (where K = total keys, n = number of nodes) — about 1/n of keys, not all of them.

**When a node is removed**: only the keys that were assigned to the removed node are remapped to the next clockwise node. Again, approximately `K/n` keys.

For a 10-node cluster: adding or removing a node remaps ~10% of keys vs ~91% with modulo hashing. The disruption is minimized and predictable.

**Virtual nodes**: in practice, each physical node is represented by many virtual nodes on the ring (100–200 per node). This evens out the load distribution — without virtual nodes, unequal spacing on the ring causes some nodes to handle far more keys than others.

**How to think through this:**
1. Consistent hashing is used in distributed caches (Memcached clustering, Redis Cluster), CDN routing, and distributed object storage (Amazon Dynamo, Apache Cassandra).
2. The insight is elegant: hash the servers, not just the keys, and use proximity on a ring for assignment. Topology changes become local, not global.

**Key takeaway:** Consistent hashing ensures that adding or removing a node only disrupts ~1/n of all key assignments — transforming a catastrophic cache flush into a controlled, proportional migration.

</details>

> 📖 **Theory:** [Consistent Hashing](./11_scalability_patterns/theory.md)

---

### Q31 · [Normal] · `redis-use-cases`

> **List five distinct use cases for Redis beyond simple key-value caching. For each, explain what Redis feature makes it suitable.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

1. **Session store**: store HTTP session data (`session_id → {user_id, roles, preferences}`). Feature: Redis Strings with TTL. When the session expires, Redis automatically deletes it (no background cleanup job needed). Sub-millisecond read latency for every authenticated request. Scales independently from the application database.

2. **Rate limiter**: enforce API rate limits (e.g., 100 requests per minute per user). Feature: Redis `INCR` with `EXPIRE` (or the `SET NX EX` pattern). A single atomic operation increments a counter and sets an expiry. Because it is atomic, there are no race conditions even with many concurrent requests from the same user hitting different application servers.

3. **Leaderboard / sorted ranking**: maintain a real-time game leaderboard where scores update constantly and the top-N must be retrievable instantly. Feature: Redis **Sorted Sets** (`ZADD`, `ZRANGE`, `ZRANK`). O(log n) insert and update, O(log n + m) range retrieval. Leaderboards of millions of players are trivially fast.

4. **Pub/Sub messaging**: fan out real-time notifications to connected clients (e.g., live chat, real-time dashboard updates). Feature: Redis **Pub/Sub**. Publishers post to a channel; all subscribers receive the message instantly. Lightweight for scenarios where message persistence is not required (use Kafka if messages must survive a restart).

5. **Distributed lock**: coordinate access to a shared resource across multiple application servers (e.g., ensure only one server runs a cron job at a time). Feature: **Redlock** algorithm using `SET key value NX EX timeout`. `NX` ensures only one process acquires the lock (atomic test-and-set), `EX` ensures the lock releases automatically if the holder crashes, preventing deadlock.


**How to think through this:**
1. Redis is not just a cache — its data structures (strings, lists, sets, sorted sets, hashes, streams, pub/sub) enable different use cases.
2. For each use case, identify which Redis feature is the fit: sorted set for leaderboards, pub/sub for real-time messaging, TTL for sessions, lists for queues.
3. Redis keeps everything in memory — all these use cases share the property that fast in-memory access is the critical requirement.

**Key takeaway:** Redis is not just a cache — its atomic data structures (sorted sets, lists, hashes) and expiry mechanics make it a Swiss army knife for coordination, rate limiting, and real-time ranking problems.

</details>

> 📖 **Theory:** [Redis Use Cases](./06_caching/theory.md)

---

### Q32 · [Interview] · `redis-vs-memcached`

> **Compare Redis and Memcached. What does Redis offer that Memcached doesn't? When would Memcached still be the right choice?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Memcached** is a simple, multi-threaded, in-memory key-value store. It supports only strings as values, has no persistence, no replication, and no built-in data structures. It is purpose-built for one job: fast object caching.

**Redis** is a multi-purpose in-memory data structure server. It supports strings, lists, sets, sorted sets, hashes, bitmaps, streams, and geospatial indexes. It offers optional persistence (RDB snapshots, AOF write-ahead log), replication, Pub/Sub, Lua scripting, transactions, and cluster mode.

**What Redis offers that Memcached doesn't**:
- **Rich data structures**: sorted sets for leaderboards, lists for queues, sets for unique counting — Memcached only stores strings, requiring the application to serialize/deserialize everything
- **Persistence**: Redis can persist data to disk (RDB or AOF), surviving restarts. Memcached is always ephemeral — a restart clears everything
- **Replication and high availability**: Redis Sentinel and Redis Cluster provide primary-replica replication, automatic failover, and horizontal scaling. Memcached has no native replication
- **Atomic operations on data structures**: `INCR`, `LPUSH`, `ZADD` — server-side atomic mutations avoid read-modify-write race conditions
- **Pub/Sub and Streams**: event messaging and log-structured streams are built in

**When Memcached is still the right choice**:
1. **Multi-threaded, multi-core utilization**: Memcached uses a true multi-threaded architecture and scales more linearly across CPU cores for pure cache workloads. Redis has historically been single-threaded for command processing (though Redis 6+ added I/O threading), making Memcached marginally faster at peak throughput for pure string-get operations.
2. **Extreme simplicity**: if the only requirement is caching serialized objects and the operational simplicity of a zero-feature system is valuable (nothing to configure wrong, no persistence to manage), Memcached's smaller surface area is a genuine advantage.
3. **Legacy systems**: existing Memcached deployments where the overhead of migration outweighs Redis's additional features.

**How to think through this:**
1. For greenfield projects, Redis is the default choice — the additional features have zero cost if unused, and the operational overhead is comparable.
2. Memcached's main advantage (multi-threading) is narrowing as Redis adds threading in newer versions.

**Key takeaway:** Redis has made Memcached largely obsolete for new systems — its richer feature set costs nothing when unused, but Memcached retains a marginal throughput edge for pure multi-core cache-only workloads.

</details>

> 📖 **Theory:** [Redis vs Memcached](./06_caching/theory.md)

---

### Q33 · [Thinking] · `cassandra-data-model`

> **Why does Cassandra require you to model data around queries, not entities? What is a partition key vs clustering key? Give an example schema for a "messages by user" access pattern.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Cassandra is a distributed wide-column store designed for extreme write throughput and linear horizontal scalability. It achieves this by making a fundamental architectural tradeoff: **no JOINs, no ad-hoc queries, no secondary indexes at scale**. All data must be co-located for efficient retrieval, and co-location is determined by the partition key at write time — which means you must know your queries before you design your schema.

In a relational database, you model entities (users, messages, orders) and write queries against them at read time using JOINs and arbitrary WHERE clauses. In Cassandra, the schema encodes the query — you design a table specifically to answer one access pattern, and everything is pre-joined.

**Partition key**: determines which node in the cluster stores the data (via consistent hashing). All rows with the same partition key are stored together on the same node. A query must include the partition key in the WHERE clause to avoid a full cluster scan (which Cassandra will refuse or perform very slowly). The partition key determines data locality.

**Clustering key**: within a partition, rows are sorted by the clustering key on disk. This enables efficient range scans within a partition (`WHERE partition_key = X AND clustering_key BETWEEN A AND B`). The clustering key is the intra-partition sort order.

**Example schema for "messages by user" access pattern**:

Access pattern: "give me all messages for user X, ordered by time descending"

```cql
CREATE TABLE messages_by_user (
    user_id    UUID,
    sent_at    TIMESTAMP,
    message_id UUID,
    content    TEXT,
    sender_id  UUID,
    PRIMARY KEY ((user_id), sent_at, message_id)
) WITH CLUSTERING ORDER BY (sent_at DESC, message_id DESC);
```

- `user_id` is the **partition key**: all messages for a given user are stored on the same node. A query `WHERE user_id = ?` hits exactly one node.
- `sent_at, message_id` are **clustering keys**: within that user's partition, messages are stored sorted by time descending on disk. Fetching the 50 most recent messages is a sequential disk read — extremely fast.
- `message_id` is included in the clustering key to ensure uniqueness when two messages arrive at the same millisecond.

**How to think through this:**
1. If you also need "give me all messages in a conversation," you build a second table: `messages_by_conversation (conversation_id, sent_at, message_id, ...)`. Denormalization is intentional and required — Cassandra's model accepts storage cost to avoid query cost.
2. Partition size matters: a user who sends 100 million messages will have a 100 million row partition. Very large partitions (>100 MB) degrade performance. You may need to bucket by time: `PRIMARY KEY ((user_id, month), sent_at, message_id)`.

**Key takeaway:** Cassandra's partition key is a pre-computed routing decision baked into the schema — you pay for query flexibility at write time (schema complexity, data duplication) to get guaranteed O(1) read latency at query time.

</details>

> 📖 **Theory:** [Cassandra Data Model](./05_databases/theory.md)

## 🗄️ Tier 2 — Data Stores & Distributed Patterns

---

### Q34 · [Normal] · `time-series-databases`

> **What is a time-series database? What makes it different from a relational database? Name two popular time-series databases and a use case for each.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **time-series database (TSDB)** is a database optimized for storing and querying data points indexed by time — typically high-frequency, append-only measurements like metrics, sensor readings, or financial ticks.

**How to think through this:**
1. Relational databases are designed for arbitrary reads and writes across normalized rows. Time-series data has a completely different access pattern: writes are almost always appends at "now," and reads are almost always range scans over a time window, often with aggregations (avg, max, rate of change).
2. TSDBs exploit this by storing data in time-ordered chunks, compressing similar values together (delta encoding, Gorilla compression), and automatically expiring old data via retention policies — none of which a relational database does natively.
3. Two popular TSDBs: **InfluxDB** — used for infrastructure metrics (CPU, memory, network) where you need fast ingest and built-in rollup queries. **TimescaleDB** — a PostgreSQL extension for time-series; used for IoT sensor data where teams want SQL familiarity plus time-optimized storage.

**Key takeaway:** TSDBs trade general-purpose flexibility for extreme efficiency at the one pattern time-series data always exhibits — high-write, time-range-query, append-only.

</details>

> 📖 **Theory:** [Time-Series Databases](./20_data_systems/theory.md#chapter-7-stream-processing--real-time-data-pipelines)

---

### Q35 · [Normal] · `blob-storage-patterns`

> **How does blob storage (like S3) work? What is an object, bucket, and key? When should you store data in S3 vs a database vs a CDN?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Blob storage** (Binary Large Object storage) is a flat, infinitely scalable object store. Unlike a filesystem, there is no hierarchy — just a flat namespace of objects addressed by a key.

**How to think through this:**
1. A **bucket** is a logical container scoped to a region and account. An **object** is any arbitrary blob of bytes — a video file, a JSON document, a trained ML model. A **key** is the unique string that names that object within a bucket (e.g., `uploads/user-42/avatar.png`). The key can contain slashes but the system treats them as part of the name, not as real directories.
2. **S3 vs database**: Store structured, queryable, relational data in a database. Store large, opaque blobs in S3 — images, videos, logs, backups, ML artifacts. Databases are expensive per GB and not optimized for large binary payloads.
3. **S3 vs CDN**: S3 is your origin store — the source of truth. A CDN sits in front of S3 and caches content at edge nodes close to users. You store in S3 always; you add a CDN in front when you need low-latency global delivery to end users.

**Key takeaway:** S3 is the durable origin; a database is for structured queries; a CDN is the delivery layer — they are not alternatives, they stack.

</details>

> 📖 **Theory:** [Blob Storage](./07_storage_cdn/theory.md#storage--cdn--theory)

---

### Q36 · [Thinking] · `cdn-cache-invalidation`

> **You deploy a new JavaScript bundle but users are still getting the old version from the CDN. What is the problem and what are two strategies to fix it?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The CDN has **cached the old file** at its edge nodes under the same URL. Until the cached object's TTL expires, new requests return the stale version from cache — your origin server is never consulted.

**How to think through this:**
1. CDNs cache by URL. If your bundle is at `/static/app.js` before and after the deploy, the CDN has no way to know the content changed. It will serve the cached version until it expires.
2. **Strategy 1 — Content-addressed URLs (fingerprinting):** This is the correct long-term fix. Include a hash of the file contents in the filename: `/static/app.a3f9c2b1.js`. Every new build produces a new URL. The CDN never serves stale content because the URL itself changes with the content. TTLs can be set to years. Your HTML references the new hash.
3. **Strategy 2 — Cache purge/invalidation API:** Most CDNs (CloudFront, Fastly, Cloudflare) offer an API to explicitly invalidate a cached object by URL. You trigger this as part of your deployment pipeline. It works but has latency (propagation takes seconds to minutes), often costs money per invalidation, and is a patch — not a structural fix. You also have to remember to call it on every deploy.

**Key takeaway:** Fingerprinted URLs solve cache invalidation permanently by making stale serving structurally impossible; cache purges are an operational escape hatch, not a design.

</details>

> 📖 **Theory:** [CDN Invalidation](./07_storage_cdn/theory.md#storage--cdn--theory)

---

### Q37 · [Normal] · `push-vs-pull-cdn`

> **What is the difference between push CDN and pull CDN? When would you choose push over pull for a specific content type?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **pull CDN** fetches content from your origin server the first time a user requests it, caches it at the edge, and serves subsequent requests from cache. A **push CDN** requires you to proactively upload content to the CDN's edge nodes before any user requests it.

**How to think through this:**
1. Pull CDN is the default model. The first request to a cold edge node triggers an origin fetch (cache miss). After that, it's served from cache until TTL expires. Good for dynamic or unpredictably accessed content. Low operational overhead — you just point the CDN at your origin.
2. Push CDN requires you to push files to every edge node yourself (via an API or rsync-style tool). The CDN never fetches from your origin on demand. You control what is cached and when.
3. Choose push when: content is large and static, you know in advance it will be requested globally (e.g., a new software release binary, a large game update, a scheduled video stream), and you want to pre-warm the cache before traffic hits to eliminate all cache misses and origin load. Push CDN is ideal for **large file distribution** where a first-request origin fetch would be too slow or too expensive.

**Key takeaway:** Pull CDN is simpler and handles unpredictable traffic well; push CDN is right when you know what will be requested and want zero cold-start latency at the edge.

</details>

> 📖 **Theory:** [Push vs Pull CDN](./07_storage_cdn/theory.md#storage--cdn--theory)

---

### Q38 · [Thinking] · `cache-write-strategies`

> **Compare write-through, write-behind (write-back), and cache-aside caching strategies. In which scenario does cache-aside cause stale data? In which does write-behind risk data loss?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
These three strategies describe what happens to the cache when a write occurs.

**How to think through this:**
1. **Write-through**: Every write goes to the cache and the database synchronously before acknowledging success. Cache is always consistent with the database. Tradeoff: higher write latency (two writes per operation). Good for read-heavy workloads where you need strong consistency.
2. **Write-behind (write-back)**: Writes go to the cache immediately; the database write is deferred and batched asynchronously. Very low write latency. Risk: if the cache node crashes before flushing to the database, those writes are lost. The gap between cache write and DB write is a window of potential data loss.
3. **Cache-aside (lazy loading)**: The application manages the cache manually — on a cache miss, the app reads from the database and populates the cache. On writes, the app writes to the database and invalidates (or updates) the cache. **Stale data scenario**: if two concurrent writers hit the database and then both try to update the cache, a race condition can leave an older value in the cache. Also, between a DB write and cache invalidation, any reader sees the old cached value.

**Key takeaway:** Write-through is safe but slow; write-behind is fast but lossy on failure; cache-aside is flexible but requires careful invalidation to avoid stale reads.

</details>

> 📖 **Theory:** [Cache Write Strategies](./06_caching/theory.md)

---

### Q39 · [Thinking] · `connection-pooling`

> **Why is database connection pooling essential for high-traffic services? What happens if your pool is exhausted? What is the correct pool size for a CPU-bound vs IO-bound service?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Connection pooling** maintains a set of reusable database connections so that each request doesn't pay the full cost of establishing a new TCP connection, authenticating, and negotiating with the database on every query.

**How to think through this:**
1. Opening a new database connection is expensive: TCP handshake, TLS handshake, authentication, and session setup can take tens to hundreds of milliseconds. Under load, doing this per request adds unacceptable latency and overwhelms the database's connection limit (PostgreSQL defaults to 100 max connections).
2. If the pool is exhausted — all connections are in use — new requests must wait. This manifests as timeout errors or queue buildup. If the pool is too small for your concurrency, requests pile up; if too large, you overwhelm the database with concurrent queries.
3. **CPU-bound services** (heavy computation per request, few DB calls): fewer concurrent DB connections are needed. A small pool (matching CPU core count) is appropriate. **IO-bound services** (many concurrent requests each waiting on DB, network, etc.): each request spends most of its time waiting, so more connections can be usefully in-flight simultaneously. Rule of thumb from PgBouncer docs: pool size = (core_count * 2) + effective_spindle_count, but for IO-bound microservices you tune upward based on measured wait time.

**Key takeaway:** Pool exhaustion causes request queuing and timeouts; size the pool based on your workload's concurrency and DB wait characteristics, not just request rate.

</details>

> 📖 **Theory:** [Connection Pooling](./05_databases/theory.md)

---

### Q40 · [Interview] · `oltp-vs-olap`

> **Compare OLTP and OLAP workloads. Why can't you run analytics queries on your production transactional database? What architecture separates them?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**OLTP (Online Transaction Processing)** handles high-frequency, low-latency operations: inserts, updates, point reads — the operations that run your application. **OLAP (Online Analytical Processing)** handles complex aggregations over large datasets — the queries that answer business questions.

**How to think through this:**
1. OLTP queries touch a small number of rows with predictable access patterns (fetch user by ID, insert an order). They need row-oriented storage, indexes on primary/foreign keys, and fast single-row operations. OLAP queries scan millions of rows and aggregate across entire columns (total revenue last quarter by region). They need column-oriented storage, no live writes competing for IO, and large memory for sort/hash operations.
2. Running an OLAP query on your production OLTP database is dangerous: a full-table scan competes with live traffic for disk IO, locks rows, and spikes CPU — degrading the latency that your application users experience. A single poorly-written analytics query can take down production.
3. The standard architecture: replicate data from OLTP databases (via CDC or ETL) into a separate **data warehouse** (Redshift, BigQuery, Snowflake). Analytics queries run there, isolated from production. The warehouse uses columnar storage optimized for aggregation. Some teams add an intermediate **data lake** (S3 + Glue/Athena) for raw, unstructured data.

**Key takeaway:** OLTP and OLAP have fundamentally opposing storage and query characteristics — sharing one system forces painful tradeoffs that hurt both workloads.

</details>

> 📖 **Theory:** [OLTP vs OLAP](./20_data_systems/theory.md#chapter-1-oltp-vs-olap--two-different-jobs)

---

### Q41 · [Normal] · `data-warehousing`

> **What is a data warehouse? What is the ETL vs ELT pattern? Name one popular data warehouse and one use case it handles well.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **data warehouse** is a centralized analytical store that integrates data from multiple source systems, optimizes it for read-heavy aggregation queries, and serves business intelligence and reporting workloads.

**How to think through this:**
1. **ETL (Extract, Transform, Load)**: Data is extracted from sources, transformed (cleaned, joined, reshaped) in an intermediate compute layer, and then loaded into the warehouse. The warehouse only receives clean, structured data. Traditional approach — made sense when warehouse storage and compute were expensive.
2. **ELT (Extract, Load, Transform)**: Raw data is loaded into the warehouse first, then transformed inside the warehouse using SQL. Modern warehouses (BigQuery, Snowflake, Redshift) have cheap storage and powerful in-warehouse compute, so it's faster to let the warehouse do the transformation. ELT also preserves raw data, making it easier to re-transform if requirements change.
3. **Snowflake** is a popular cloud data warehouse. A use case it handles well: a retail company aggregating sales transactions from 50 regional databases, combining them with inventory and marketing spend data, and running daily reports on margin by product category across regions — a workload requiring petabyte-scale joins that would crush any OLTP system.

**Key takeaway:** ELT has largely replaced ETL in modern stacks because cheap cloud warehouse compute makes in-place transformation faster and more flexible than pre-processing outside.

</details>

> 📖 **Theory:** [Data Warehousing](./20_data_systems/theory.md#chapter-4-etl-vs-elt--when-to-transform)

---

### Q42 · [Thinking] · `event-sourcing`

> **What is event sourcing? How does it differ from storing current state? What is a projection? Give a concrete example where event sourcing is valuable.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Event sourcing** is a pattern where instead of storing the current state of an entity, you store the full sequence of events that led to that state. The current state is always derived by replaying events from the beginning (or from a snapshot).

**How to think through this:**
1. Traditional storage: a `users` table has a row for each user with their current balance, name, address. When balance changes, you overwrite the field. History is lost unless you add audit tables manually. Event sourcing instead stores: `AccountOpened{balance: 0}`, `MoneyDeposited{amount: 500}`, `MoneyWithdrawn{amount: 200}` — the sequence is the source of truth. Current balance (300) is computed by replaying.
2. A **projection** is a read model built by processing the event stream. You can have multiple projections from the same events: one for current balance, one for transaction history, one for fraud detection patterns. Projections are derived and rebuildable — if you need a new view, you replay history and build it.
3. Concrete example: **banking ledger**. A bank needs to know not just the current balance but the full audit trail for every account, dispute resolution, and regulatory compliance. Event sourcing gives you this for free — you never need to retrofit audit logging because the events are the log.

**Key takeaway:** Event sourcing trades storage space for a complete, replayable history — invaluable when the sequence of changes matters as much as the current state.

</details>

> 📖 **Theory:** [Event Sourcing](./18_design_patterns/theory.md#observer-event-bus)

---

### Q43 · [Normal] · `cqrs-pattern`

> **What is CQRS (Command Query Responsibility Segregation)? What problem does it solve? How is it often combined with event sourcing?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**CQRS** separates the model used to handle writes (commands that change state) from the model used to handle reads (queries that return data). A single data model optimized for both is often a poor fit for both.

**How to think through this:**
1. The problem: in complex domains, the data shape that makes writes correct (normalized, consistent, business-rule-enforcing) is different from the shape that makes reads fast (denormalized, pre-joined, sorted for UI consumption). Forcing one model to do both creates impedance mismatch — you either denormalize your write model or you make reads slow.
2. With CQRS, the **command side** handles validation, business rules, and writes to the authoritative store. The **query side** maintains one or more read-optimized projections (often in a separate database, e.g., Elasticsearch for search, Redis for hot lookups). Reads scale independently from writes.
3. CQRS pairs naturally with event sourcing: the command side emits events; the query side subscribes to those events and updates its read models (projections). The event log is the integration point between the two sides. This is sometimes called the **CQRS+ES** pattern — common in domain-driven design (DDD) implementations.

**Key takeaway:** CQRS acknowledges that read and write workloads have different shapes and scales them independently, at the cost of eventual consistency between the two sides.

</details>

> 📖 **Theory:** [CQRS Pattern](./18_design_patterns/theory.md#command)

---

### Q44 · [Thinking] · `saga-pattern`

> **What is the Saga pattern for distributed transactions? Compare choreography-based vs orchestration-based sagas. What is a compensating transaction?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **Saga** is a pattern for managing a long-running business transaction that spans multiple microservices, each with its own database. Rather than a single ACID transaction (impossible across services), a saga is a sequence of local transactions with explicit rollback logic.

**How to think through this:**
1. In a **choreography-based saga**, each service publishes events and other services react to them. No central coordinator: Order Service places order → emits `OrderPlaced` → Inventory Service reserves stock → emits `StockReserved` → Payment Service charges card. If payment fails, Payment emits `PaymentFailed` → Inventory reacts and releases the reservation. Decentralized but hard to trace and reason about as complexity grows.
2. In an **orchestration-based saga**, a central **Saga Orchestrator** drives the workflow by explicitly calling each service in order and handling failures. The orchestrator knows the full flow and issues compensating calls when a step fails. Easier to debug and observe. Creates a coordination bottleneck and couples the orchestrator to all participants.
3. A **compensating transaction** is the business-logic inverse of a completed local transaction. If you cannot undo a database write (because the transaction already committed), you compensate: if payment succeeded but shipping failed, you issue a refund — that refund is the compensating transaction for the payment step.

**Key takeaway:** Sagas achieve distributed consistency through explicit compensation rather than rollback — you must design the "undo" for every step upfront.

</details>

> 📖 **Theory:** [Saga Pattern](./18_design_patterns/theory.md#5-patterns-in-distributed-systems)

---

### Q45 · [Critical] · `two-phase-commit`

> **Explain two-phase commit (2PC). What is the "coordinator failure" problem that makes 2PC dangerous in practice? Why do modern distributed systems avoid it?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Two-phase commit (2PC)** is a distributed protocol for achieving atomicity across multiple nodes. Phase 1 (Prepare): the coordinator asks all participants "can you commit?" Each votes yes or no. Phase 2 (Commit): if all voted yes, coordinator sends Commit; if any voted no, sends Abort.

**How to think through this:**
1. The fatal flaw is **coordinator failure during Phase 2**. Imagine: all participants voted "yes" and are now holding locks, waiting for the commit message. The coordinator crashes before sending it. The participants are stuck — they cannot commit (they haven't been told to) and they cannot abort (they voted yes and don't know if others did too). They hold locks indefinitely, blocking all other transactions touching those rows.
2. This is called the **blocking problem** of 2PC. The protocol cannot make progress without the coordinator recovering. In a distributed system, you must assume coordinators can fail. Recovery requires the coordinator to come back up and re-send the Phase 2 message — during which your system is frozen.
3. Modern distributed systems avoid 2PC because: it is a blocking protocol (not partition-tolerant), it requires synchronized, reliable coordinators, and it degrades performance due to the two round-trips and lock-holding. Instead, they use **sagas** for business transactions, **optimistic concurrency**, or **consensus protocols** (Raft/Paxos) for system-level coordination where they must guarantee agreement.

**Key takeaway:** 2PC is theoretically elegant but operationally fragile — coordinator failure leaves participants in a locked, undecidable state with no way forward.

</details>

> 📖 **Theory:** [Two-Phase Commit](./10_distributed_systems/theory.md#two-phase-commit-2pc)

---

### Q46 · [Thinking] · `outbox-pattern`

> **What is the Outbox pattern? What problem does it solve that a direct database write + message publish cannot guarantee? How does a message relay process it?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The **Outbox pattern** guarantees that a database write and a message publication either both happen or neither happens, without using a distributed transaction. It does this by writing the message into a database table (the "outbox") in the same local transaction as the business data.

**How to think through this:**
1. The problem: you write an order to your database, then try to publish an `OrderCreated` event to Kafka. Between the DB write and the Kafka publish, your service crashes. The order exists in the database but the event was never published. Downstream services never know the order exists. You have inconsistency with no way to detect it. Alternatively, if you publish first and the DB write fails, you have a ghost event.
2. The Outbox pattern fixes this: within the same database transaction, write the order row AND write a row to an `outbox` table with the serialized event payload. The transaction is atomic — both succeed or both fail. The event is now durably stored in your database.
3. A **message relay** (or **transactional outbox poller**) — often implemented via **Change Data Capture (CDC)** reading the database's write-ahead log (e.g., Debezium) — watches the outbox table for new rows and publishes them to Kafka. Once confirmed published, rows are marked sent or deleted. The relay is a separate process that can retry independently.

**Key takeaway:** The Outbox pattern moves the dual-write problem from "DB + message broker" to "DB + DB" (a single atomic transaction), delegating broker publication to a reliable relay.

</details>

> 📖 **Theory:** [Outbox Pattern](./18_design_patterns/theory.md#design-patterns-for-system-design)

---

### Q47 · [Normal] · `distributed-idempotency`

> **What is idempotency in distributed systems? Give two examples of operations that are naturally idempotent and two that are not. How do you make a non-idempotent operation idempotent?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
An operation is **idempotent** if performing it multiple times produces the same result as performing it once. In distributed systems, networks are unreliable and retries are common — idempotency ensures retries are safe.

**How to think through this:**
1. Naturally idempotent: **Setting a value** (`UPDATE users SET name = 'Alice' WHERE id = 1` — running it 10 times has the same result as once). **Deleting a resource by ID** (deleting an already-deleted resource returns 404 or success — no side effect). Also: HTTP GET, HTTP PUT (full replace), `SET` operations in caches.
2. Naturally non-idempotent: **Charging a credit card** (running it twice charges twice). **Incrementing a counter** (`UPDATE orders SET count = count + 1` — each execution adds 1, so 10 retries = 10 increments). Also: HTTP POST to create a resource, sending an email.
3. Making a non-idempotent operation idempotent: use an **idempotency key**. The client generates a unique key (UUID) per logical operation and sends it with the request. The server stores the key in a database with the result after the first execution. On any retry with the same key, the server returns the stored result without re-executing. Stripe's payment API is a classic example — clients pass an `Idempotency-Key` header.

**Key takeaway:** Idempotency keys convert stateful "run-once" operations into safe retry-able ones by making the server remember and replay previous outcomes.

</details>

> 📖 **Theory:** [Distributed Idempotency](./10_distributed_systems/theory.md#distributed-systems)

---

### Q48 · [Normal] · `dead-letter-queues`

> **What is a dead-letter queue (DLQ)? Why do messages end up there? What should a system do with DLQ messages — retry, alert, or discard?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **dead-letter queue (DLQ)** is a secondary queue where messages are moved after they have failed processing a configurable number of times. It is a safety net that prevents a bad message from blocking or polluting the main queue indefinitely.

**How to think through this:**
1. Messages end up in the DLQ for several reasons: the message is **malformed** (cannot be deserialized — a schema mismatch, a corrupt payload); the consumer has a **bug** that throws an exception on a specific input; a **downstream dependency** (database, third-party API) is unavailable; or the message **violates a business rule** that was not caught upstream (e.g., references a deleted entity).
2. The right response depends on why the message failed:
   - **Retry with alerting**: If the failure was due to a transient dependency outage, the message is valid and should be retried once the dependency is restored. Alert an on-call engineer so it doesn't sit unresolved.
   - **Inspect and replay**: If it was a bug that's now fixed, fix the bug, then replay the DLQ messages.
   - **Discard with logging**: If the message is genuinely invalid and represents bad data that should never have been produced, discard it after logging the payload for audit purposes.
3. Never silently discard DLQ messages. The DLQ is a signal that something is wrong — in the producer, the consumer, or the contract between them.

**Key takeaway:** A DLQ is not a trash can — it is a diagnostic queue that requires human or automated triage to understand and resolve the underlying failure.

</details>

> 📖 **Theory:** [Dead Letter Queues](./09_message_queues/theory.md)

---

### Q49 · [Thinking] · `backpressure-queues`

> **What is backpressure in a message queue system? What happens when a consumer falls behind a producer indefinitely? How do modern queue systems apply backpressure?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Backpressure** is the mechanism by which a slow consumer signals to a fast producer to slow down or stop sending, preventing unbounded queue growth and system collapse.

**How to think through this:**
1. Without backpressure: a producer publishes 10,000 messages/sec; a consumer processes 1,000 messages/sec. The queue grows by 9,000 messages/sec. Eventually, the queue hits its memory or disk limit and either starts dropping messages, crashes, or degrades in performance for all consumers. The lag grows unboundedly and old messages may expire before being processed.
2. In the absence of backpressure, the upstream service is essentially operating in a fantasy — it thinks work is getting done because messages are accepted, but the downstream system is drowning. This is a classic distributed systems failure mode.
3. Modern systems apply backpressure in different ways: **Kafka** doesn't push to consumers — consumers poll at their own pace, so there is natural backpressure (the consumer controls its throughput). **RabbitMQ** has a `prefetch` setting (`basic.qos`) that limits how many unacknowledged messages are delivered to a consumer, throttling flow. **TCP** has built-in backpressure via receive window sizing. **Reactive Streams** (RxJava, Project Reactor) have a formal backpressure contract where subscribers request N items. The principle: systems should fail fast and loudly upstream rather than silently overflow downstream.

**Key takeaway:** Backpressure shifts failure visibility from an invisible downstream drowning to an explicit upstream slowdown — making the bottleneck observable and controllable.

</details>

> 📖 **Theory:** [Backpressure](./09_message_queues/theory.md)

---

### Q50 · [Thinking] · `distributed-consensus`

> **What problem does distributed consensus solve? What is the Raft algorithm trying to achieve? Why is it hard when network partitions occur?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Distributed consensus** is the problem of getting a group of nodes that can fail or be partitioned to agree on a single value — and to do so reliably, so the agreed value is durable and consistent.

**How to think through this:**
1. The problem matters whenever multiple nodes must share state: leader election (who is the primary?), distributed locks (who holds the lock?), log replication (what is the committed sequence of operations?). Without consensus, split-brain scenarios occur where two nodes each believe they are the leader and both accept writes, producing divergent state.
2. **Raft** is a consensus algorithm designed to be understandable (compared to Paxos). It elects a single **leader** who accepts all writes. The leader replicates log entries to a majority of **followers** before committing. If the leader fails, followers hold an election. Raft guarantees that a committed log entry is durable — it will appear in the log of any future leader.
3. Network partitions make consensus hard because of the **CAP theorem**: during a partition, nodes on each side of the split cannot communicate. A node cannot distinguish "the leader is dead" from "I am partitioned from the leader." Raft handles this by requiring a **majority quorum** to elect a leader and commit entries — a minority partition cannot elect a new leader or make progress, avoiding split-brain. But this means the minority partition is unavailable. You must choose: consistency (Raft's choice) or availability during a partition.

**Key takeaway:** Raft achieves consensus by requiring majority agreement for every decision, making split-brain impossible at the cost of availability for the minority partition.

</details>

> 📖 **Theory:** [Distributed Consensus](./10_distributed_systems/theory.md#raft-consensus-algorithm)

---

### Q51 · [Normal] · `leader-election`

> **What is leader election in distributed systems? Give two examples of when a distributed system needs a leader. How does ZooKeeper or etcd facilitate this?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Leader election** is the process by which distributed nodes agree on one node acting as the coordinator for a specific responsibility, typically because that responsibility requires serialized, authoritative decision-making.

**How to think through this:**
1. Two examples: **Database primary selection** — in a replicated database cluster (e.g., PostgreSQL with Patroni), exactly one node must accept writes at any time. A leader election determines which node is the primary; if it fails, a new election picks a standby to promote. **Job scheduler** — in a distributed cron system (e.g., Airflow schedulers in HA mode), exactly one scheduler should trigger a given DAG run to avoid double-triggering. The leader takes responsibility; other instances stand by.
2. **ZooKeeper** facilitates leader election using **ephemeral nodes** — nodes that exist only while the client that created them maintains an active session. Each candidate creates an ephemeral sequential node (e.g., `/election/candidate-0000001`). The candidate with the lowest sequence number is the leader. If the leader crashes, its session expires, the ephemeral node is deleted, and the next candidate (now holding the lowest number) takes over. ZooKeeper's watches notify candidates of this change.
3. **etcd** does the same via a **lease**-based mechanism: a candidate acquires a key (e.g., `/leader`) with a TTL-backed lease. It must periodically renew the lease. If it fails to renew (crashes, network partition), the lease expires, the key is deleted, and another candidate can acquire it.

**Key takeaway:** Both ZooKeeper and etcd turn leader election into a "who holds the lock?" problem, using TTLs or session lifetimes to automatically release leadership on failure.

</details>

> 📖 **Theory:** [Leader Election](./10_distributed_systems/theory.md#8-leader-election)

---

### Q52 · [Critical] · `distributed-locks`

> **What is a distributed lock? Why is a Redis SETNX-based lock dangerous without a TTL? What is Redlock and what problem does it address?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **distributed lock** ensures that only one process across multiple nodes can execute a critical section at a time — the distributed equivalent of a mutex.

**How to think through this:**
1. A naive Redis implementation: `SETNX lock_key "owner"` (SET if Not eXists). This acquires the lock if the key doesn't exist. The problem: if the process that acquired the lock crashes before calling `DEL lock_key`, the lock is held forever. No other process can acquire it. The system deadlocks. This is the **missing TTL** problem.
2. The fix is `SET lock_key "owner" NX PX 30000` — set with NX (only if not exists) and a TTL of 30 seconds. If the holder crashes, the lock auto-expires. But now there's a new problem: if the holder's operation takes longer than 30 seconds (e.g., a GC pause, slow network), the lock expires while it's still "held," another process acquires it, and now two processes are in the critical section simultaneously. TTL creates a **safety window**, not a guarantee.
3. **Redlock** is the Redis distributed lock algorithm by Salvatore Sanfilippo. It addresses the single-Redis-node failure problem: if your Redis node crashes, all locks are lost (or if persistence is enabled, phantom locks from before a crash can reappear). Redlock acquires the lock on a majority of N independent Redis nodes (e.g., 3 of 5). A lock is valid only if acquired on a majority within a bounded time window. Martin Kleppmann argued Redlock still has issues under clock skew and process pauses — this is a known debate in the field, and for truly critical sections, most teams recommend consensus-based locks (etcd, ZooKeeper).

**Key takeaway:** Redis locks with TTL are fine for advisory coordination but not for strong mutual exclusion guarantees — use etcd or ZooKeeper when correctness under failure is non-negotiable.

</details>

> 📖 **Theory:** [Distributed Locks](./10_distributed_systems/theory.md#distributed-systems)

---

### Q53 · [Design] · `rate-limiting-at-scale`

> **Design a rate limiting system that enforces 100 req/sec per user across 20 API servers. Redis is available. Should you use token bucket or sliding window? Where does the state live?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Use a **Redis-backed sliding window log or sliding window counter** shared across all 20 API servers. For 100 req/sec per user, the **token bucket** or **sliding window counter** are both viable — the choice depends on your tolerance for burst traffic.

**How to think through this:**
1. **State must live in Redis**, not in-process. Each of your 20 API servers handles a fraction of a user's requests. If rate limit counters are in-process, a user gets 100 req/sec per server (2,000 total across 20). Centralized state in Redis ensures all servers see the same counter for each user.
2. **Token bucket** allows short bursts above the average rate (a user can consume 100 tokens instantly if they've accumulated them). Good for APIs where bursty usage is acceptable. **Sliding window counter** is stricter: it counts requests in a rolling time window and rejects any that exceed the limit. Better for enforcement purity. For most external APIs, sliding window is the better default — it prevents gaming via burst patterns.
3. Implementation: use a Redis **Lua script** (atomic) or **Redis sorted set** (sliding window log: store each request timestamp, trim entries older than 1 second, count remaining). The Lua script approach with `INCR` + `EXPIRE` is simpler for fixed windows. For precise sliding windows, the sorted set approach is canonical. The key per user: `rate_limit:{user_id}`. Set TTL to 1 second (or the window size). Run the check-and-increment atomically to avoid race conditions. At 20 servers, each request makes one Redis round-trip — acceptable if Redis is co-located or low-latency.

**Key takeaway:** Centralize rate limit state in Redis with atomic operations; choose sliding window over token bucket when you need consistent enforcement without burst allowances.

</details>

> 📖 **Theory:** [Rate Limiting at Scale](./11_scalability_patterns/theory.md)

---

### Q54 · [Normal] · `service-discovery`

> **What is service discovery in microservices? Compare client-side vs server-side discovery. How does Kubernetes handle service discovery?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Service discovery** is the mechanism by which services find each other's network locations at runtime, without hardcoded IPs or hostnames — necessary because in containerized environments, service instances start, stop, and move constantly.

**How to think through this:**
1. **Client-side discovery**: the calling service queries a **service registry** (e.g., Consul, Eureka) directly, retrieves a list of healthy instances, and applies its own load-balancing logic (round-robin, least-connections) to pick one. The client is smarter and more flexible, but every client must implement registry querying and load balancing. Netflix Ribbon uses this model.
2. **Server-side discovery**: the calling service sends requests to a **load balancer or API gateway**, which queries the registry and forwards to a healthy instance. The client is unaware of the registry. Simpler clients, but the load balancer is now a required infrastructure component. AWS ALB + ECS uses this model.
3. **Kubernetes** uses a hybrid, DNS-based approach. When you create a `Service` object, Kubernetes assigns it a stable **ClusterIP** and a DNS name (e.g., `payment-service.production.svc.cluster.local`). The cluster's CoreDNS resolves this to the ClusterIP. `kube-proxy` on each node maintains `iptables` or IPVS rules that intercept traffic to the ClusterIP and load-balance it across healthy pod endpoints. The calling service just uses the DNS name — the platform handles the rest.

**Key takeaway:** Kubernetes abstracts service discovery entirely into DNS and virtual IPs, making microservices portable without any client-side discovery library.

</details>

> 📖 **Theory:** [Service Discovery](./12_microservices/theory.md#microservices--theory)

---

### Q55 · [Thinking] · `circuit-breaker-microservices`

> **Why do you need a circuit breaker in microservices? Describe a cascade failure scenario that a circuit breaker would prevent. What is the difference between "open" and "half-open" state?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **circuit breaker** is a stability pattern that prevents a failing downstream service from dragging down the entire call chain. Without one, threads waiting on a slow service pile up, exhaust thread pools, and cascade the failure upstream.

**How to think through this:**
1. Cascade failure scenario: User Service calls Recommendation Service, which is experiencing high latency (DB is overloaded). Each call takes 30 seconds to time out. User Service has a thread pool of 50 threads. All 50 threads are now blocked waiting on Recommendation Service. New requests to User Service queue up with no threads to handle them. User Service now appears down to its callers. Those callers start queueing too. Within minutes, the entire service graph is unresponsive — all caused by one slow downstream service.
2. A circuit breaker sits around the call to Recommendation Service. When the failure rate exceeds a threshold (e.g., 50% of calls fail in a 10-second window), the circuit **opens**. In open state, calls to Recommendation Service are immediately rejected (or a fallback is returned) without actually making the network call. Thread pools drain. User Service recovers.
3. After a configured timeout, the circuit enters **half-open** state: a small number of probe requests are allowed through. If they succeed, the circuit **closes** again (normal operation resumes). If they fail, it reopens. Half-open prevents premature recovery attempts that would re-flood an still-struggling downstream service.

**Key takeaway:** The circuit breaker converts "cascading slow failure" into "fast, contained failure" — failing immediately when a dependency is unhealthy instead of holding resources hostage while waiting.

</details>

> 📖 **Theory:** [Circuit Breaker](./12_microservices/theory.md)

---

### Q56 · [Normal] · `bulkhead-pattern`

> **What is the bulkhead pattern? What is it named after? Give a concrete implementation example: a service has two types of operations — how do bulkheads prevent one from starving the other?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The **bulkhead pattern** isolates critical resources (thread pools, connection pools, semaphores) per consumer type so that a failure or overload in one category cannot exhaust resources needed by another.

**How to think through this:**
1. The name comes from ship hull design: a bulkhead is a partition that divides a ship's hull into watertight compartments. If one compartment floods, the others remain intact. The ship stays afloat. The pattern is the same idea applied to software resource pools.
2. Concrete example: an API service handles two operation types — **user-facing search requests** (latency-sensitive, must be fast) and **bulk export jobs** (slow, resource-intensive, initiated by background processes). Without bulkheads, both share a single thread pool of 100 threads. If 50 export jobs run simultaneously and each holds a thread for 10 seconds, only 50 threads are left for search. Under load, search latency spikes. Users suffer.
3. With bulkheads: allocate separate thread pools — 80 threads for search, 20 for exports (or separate semaphores/connection pools). Export jobs can never acquire search threads. Search is always guaranteed 80 threads regardless of export load. The tradeoff: total capacity is less flexible — a quiet search period can't lend idle threads to exports unless you implement dynamic sizing.

**Key takeaway:** Bulkheads prevent the noisy-neighbor problem within a service by partitioning resource pools so high consumption in one workload cannot starve another.

</details>

> 📖 **Theory:** [Bulkhead Pattern](./12_microservices/theory.md)

---

### Q57 · [Normal] · `sidecar-pattern`

> **What is the sidecar pattern in microservices? What responsibilities are commonly moved to a sidecar? How does it relate to a service mesh?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The **sidecar pattern** deploys a secondary container alongside your main service container in the same pod (in Kubernetes), sharing the same network namespace and lifecycle. The sidecar handles cross-cutting concerns so the main service doesn't have to.

**How to think through this:**
1. Cross-cutting concerns that belong in a sidecar: **mTLS termination and certificate rotation** (your service code doesn't need to know about TLS), **observability** (metrics collection, trace context injection, log shipping), **traffic shaping** (retries, timeouts, circuit breaking), **service discovery** (the sidecar proxies outbound calls, resolving destinations), and **security policy enforcement**.
2. The key property: the sidecar intercepts all inbound and outbound traffic via `iptables` rules that redirect traffic through the sidecar proxy (e.g., Envoy). Your service code thinks it's making direct network calls. It never knows the sidecar exists.
3. A **service mesh** (e.g., Istio, Linkerd) is the orchestration layer that deploys and configures sidecars fleet-wide. Every service in the mesh gets a sidecar (typically Envoy Proxy). The mesh provides a **control plane** that centrally configures all sidecars with routing rules, mTLS certificates, observability settings, and traffic policies. The sidecar pattern is the mechanism; the service mesh is the platform that manages sidecars at scale.

**Key takeaway:** Sidecars externalize infrastructure concerns from application code; a service mesh makes sidecar deployment and configuration uniform and centrally managed across the entire fleet.

</details>

> 📖 **Theory:** [Sidecar Pattern](./12_microservices/theory.md)

---

### Q58 · [Design] · `bff-pattern`

> **What is the Backend-for-Frontend (BFF) pattern? When is it useful? Compare it to a generic API gateway.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The **Backend-for-Frontend (BFF)** pattern creates a dedicated backend service for each type of frontend client (mobile app, web app, third-party API). Each BFF is tailored to exactly what its client needs — aggregating, transforming, and filtering data from downstream services.

**How to think through this:**
1. The problem it solves: a mobile app needs a single API call that returns a condensed user profile + recent orders + unread notifications (low bandwidth, one round-trip). The web app needs a richer profile with more fields and paginated orders. A generic API exposes raw service data and forces both clients to make multiple calls and stitch responses together — adding latency and client-side complexity.
2. With BFF: the Mobile BFF fetches from User Service, Order Service, and Notification Service, assembles exactly the mobile payload, and returns it in one call. The Web BFF does the same but with a different shape. Each BFF is owned by the frontend team that uses it, so they can iterate on the API contract independently without coordinating with backend teams.
3. **Compared to a generic API gateway**: an API gateway is infrastructure — it handles auth, rate limiting, TLS termination, routing, and protocol translation for all clients uniformly. A BFF is business logic — it's a service that knows the specific needs of its client and composes data from multiple backends. They are not alternatives: you typically have an API gateway in front of your BFFs. The gateway does common cross-cutting concerns; the BFF does client-specific aggregation.

**Key takeaway:** BFF lets each client type have an API contract tailored to its needs, owned by the team that builds the frontend — a generic gateway enforces policies but doesn't know what any specific client needs.

</details>

> 📖 **Theory:** [BFF Pattern](./12_microservices/theory.md)

---

### Q59 · [Thinking] · `service-mesh`

> **What is a service mesh (e.g., Istio)? What problems does it solve that an API gateway does not? What is the cost of adding a service mesh?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **service mesh** is a dedicated infrastructure layer that manages all service-to-service (east-west) communication within a microservices cluster. It deploys a sidecar proxy (Envoy) alongside every service instance, intercepting all network traffic and enforcing policies uniformly.

**How to think through this:**
1. An **API gateway** sits at the edge of your cluster, handling **north-south** traffic — requests from external clients entering the system. It does auth, rate limiting, routing, and TLS termination at the ingress point. It has no visibility into or control over how Service A talks to Service B inside the cluster.
2. A service mesh solves **east-west** problems: mutual TLS between all internal services (zero-trust networking), fine-grained traffic management (canary deployments between internal services, weighted routing), distributed tracing across service boundaries without code changes, circuit breaking, retries, and timeouts enforced uniformly — all without modifying application code. An API gateway cannot provide mTLS between Service A and Service B, or observe the latency of their communication.
3. The cost of a service mesh is real and significant: every request now passes through two sidecar proxies (sender-side and receiver-side Envoy), adding **~1-5ms latency per hop** and significant CPU overhead. The control plane (Istiod) adds operational complexity, new failure modes, and a steep learning curve. Debugging becomes harder when network behavior is abstracted into a separate layer. Many teams adopt a service mesh too early and struggle with the operational burden before they get the benefits.

**Key takeaway:** A service mesh solves east-west security, observability, and traffic control that an API gateway cannot reach — but at the cost of meaningful latency overhead and substantial operational complexity.

</details>

> 📖 **Theory:** [Service Mesh](./12_microservices/theory.md#microservices--theory)

---

### Q60 · [Interview] · `blue-green-canary`

> **Compare blue-green deployment and canary deployment. What are the tradeoffs in terms of: rollback speed, production traffic risk, infrastructure cost, and feedback loop?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Both patterns deploy new versions alongside old ones in production, but they differ in how traffic is shifted and how risk is managed.

**How to think through this:**
1. **Blue-green**: run two identical environments (blue = current, green = new). After deploying to green and running smoke tests, switch 100% of traffic from blue to green instantly (via load balancer). Rollback is instant — flip traffic back to blue. The entire switch happens at once.
2. **Canary**: route a small percentage of production traffic (e.g., 1%, 5%) to the new version while the rest goes to the old version. Gradually increase the percentage as confidence grows. Rollback means routing 0% to the new version.
3. Tradeoff comparison:
   - **Rollback speed**: Blue-green is faster (one traffic flip). Canary is slightly slower (route back to 0%, but almost as fast).
   - **Production traffic risk**: Blue-green is binary — when you flip, 100% of users hit the new version. A bug affects everyone immediately. Canary exposes only a small user cohort initially — a bug affects 1% of users, giving you time to catch it before full rollout.
   - **Infrastructure cost**: Blue-green requires running two full production environments simultaneously — double the infrastructure. Canary only requires a few extra instances for the small percentage slice — lower cost.
   - **Feedback loop**: Canary provides a real production signal at low risk before full rollout. You observe actual user behavior, error rates, and latency at 1% before committing. Blue-green gives you no incremental signal — you get full production feedback only after the full flip.

**Key takeaway:** Blue-green optimizes for rollback simplicity and deployment speed at double infrastructure cost; canary optimizes for risk reduction and production signal at lower cost but requires more operational sophistication.

</details>

> 📖 **Theory:** [Blue-Green & Canary](./15_cloud_architecture/theory.md#chapter-5-multi-region-deployment)

---

### Q61 · [Normal] · `feature-flags`

> **What is a feature flag? Give three use cases beyond simple on/off toggling. What is "flag debt" and how do you manage it?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **feature flag** (also called a feature toggle) is a configuration mechanism that allows you to change system behavior at runtime without deploying new code, by checking a flag value that controls whether a code path executes.

**How to think through this:**
1. Three use cases beyond on/off toggling:
   - **Canary releases / percentage rollouts**: enable a feature for 5% of users, monitor metrics, gradually increase to 100%. The flag controls who gets the new experience, not just whether it exists.
   - **A/B testing / experimentation**: route users into control and treatment groups based on flag assignment, measure conversion rates, and make data-driven decisions about which variant to ship.
   - **Kill switches for operational safety**: a flag that disables a non-critical, expensive feature (e.g., real-time recommendations) under high load to protect core functionality. The flag is normally on but can be flipped instantly during an incident without a deploy.
2. **Flag debt** is the accumulation of feature flags that are no longer needed — their rollout is complete, the experiment is done, or the toggle was a temporary workaround. Dead flags add code branches that are never exercised, create confusion about which path is active, and make the codebase harder to reason about. In extreme cases, nested flag conditions become unmaintainable.
3. Managing flag debt: set a **creation date and owner** for every flag in your flag management system (LaunchDarkly, Unleash, etc.). Establish a **TTL policy** — flags must be cleaned up within 30-60 days of reaching 100% rollout. Use automated tooling to detect stale flags. Treat flag removal as a first-class engineering task, not optional cleanup.

**Key takeaway:** Feature flags are powerful beyond simple toggling, but they create debt if not actively retired — flag lifecycle management is as important as flag creation.

</details>

> 📖 **Theory:** [Feature Flags](./18_design_patterns/theory.md)

---

### Q62 · [Normal] · `chaos-engineering`

> **What is chaos engineering? What is a chaos experiment and a steady-state hypothesis? Name one famous example of chaos engineering in production.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Chaos engineering** is the discipline of deliberately injecting failures into a production system to proactively discover weaknesses before they cause unplanned outages. It is the practice of "breaking things on purpose, in a controlled way, to learn how they break."

**How to think through this:**
1. A **chaos experiment** has a structured methodology: define a **steady-state hypothesis** (a measurable baseline of normal system behavior — e.g., "p99 latency is below 200ms and error rate is below 0.1%"), inject a failure (terminate an instance, inject network latency, corrupt a dependency response), observe whether the system maintains the steady state, and analyze deviations. If the system deviates, you've found a real weakness.
2. The steady-state hypothesis is critical because it defines "normal." Without a quantitative baseline, you cannot tell whether a failure is affecting users or being absorbed by the system's resilience mechanisms. The goal is not destruction — it is controlled learning.
3. The most famous example: **Netflix Chaos Monkey**. Netflix built and open-sourced a tool that randomly terminates EC2 instances in production during business hours. The goal was to force Netflix engineers to build services that tolerate instance failure gracefully. This led to the broader **Simian Army** (Chaos Gorilla for AZ failures, Chaos Kong for regional failures). Netflix's philosophy: "the best way to avoid failures is to fail constantly."

**Key takeaway:** Chaos engineering turns unknown system vulnerabilities into known, measured findings — chaos experiments reveal the gap between how you think your system handles failure and how it actually does.

</details>

> 📖 **Theory:** [Chaos Engineering](./14_observability/theory.md)

---

### Q63 · [Normal] · `observability-pillars`

> **What are the three pillars of observability? For a production API service, give one specific example of what you'd collect for each pillar and what question it helps answer.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The three pillars of observability are **metrics**, **logs**, and **traces**. Together they let you understand the internal state of a system from its external outputs.

**How to think through this:**
1. **Metrics** are numerical measurements aggregated over time. Example: `http_request_duration_seconds` histogram tracked by endpoint, HTTP status code, and region. Question it answers: "Is our p99 latency for the `/checkout` endpoint above SLO right now, and is it isolated to one region?" Metrics are cheap to store and fast to query — ideal for dashboards and alerting.
2. **Logs** are timestamped, structured records of discrete events. Example: a structured JSON log line on every API request: `{"timestamp": "...", "user_id": "u-123", "endpoint": "/checkout", "status": 500, "error": "payment_timeout", "trace_id": "abc-123"}`. Question it answers: "What exactly happened to user u-123's checkout request at 14:23:07 — which downstream call failed and why?" Logs give you the narrative of individual events.
3. **Traces** are records of a request's journey across multiple services, showing timing and causality. Example: a distributed trace showing a `/checkout` request spanning API Gateway → Order Service → Inventory Service → Payment Service, with each span's duration and any errors. Question it answers: "Which service in the call chain is responsible for the extra 800ms in our checkout p99, and which specific database query inside that service is the bottleneck?" Traces connect behavior across service boundaries.

**Key takeaway:** Metrics tell you something is wrong, logs tell you what happened, and traces tell you where in the distributed system it happened — you need all three to debug production effectively.

</details>

> 📖 **Theory:** [Observability Pillars](./14_observability/theory.md)

---

### Q64 · [Interview] · `slo-sla-sli`

> **Define SLI, SLO, and SLA. Give a concrete example for a web API: what would the SLI be, what SLO target, and what SLA commitment to customers?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**SLI** (Service Level Indicator) is the actual measured metric. **SLO** (Service Level Objective) is the target you set for that metric internally. **SLA** (Service Level Agreement) is the contractual commitment to customers, with consequences (refunds, credits) for breach.

**How to think through this:**
1. The relationship: SLI is what you measure, SLO is the bar you aim for internally, and SLA is the weaker bar you promise externally. SLAs are always set below SLOs — you promise customers less than you target internally so that you have a buffer. If your SLO and SLA were the same, every SLO miss would trigger a customer penalty and a breach notification.
2. Concrete example for a payment processing API:
   - **SLI**: the proportion of `/v1/payments` requests that receive a successful response (HTTP 2xx) within 500ms, measured as a rolling 28-day ratio. This is your "request success rate" — a ratio SLI.
   - **SLO**: 99.9% of requests succeed within 500ms over a 28-day window. This is your internal target. Your error budget is 0.1% of requests — roughly 43 minutes of total failure time per month.
   - **SLA**: 99.5% availability committed to paying customers in the contract, with service credits of 10% of monthly fees per percentage point below that threshold. This is what you can be held accountable for contractually.
3. SLIs should be user-centric (measure what users experience), not system-centric (don't use "CPU below 80%" as an SLI — CPU doesn't directly tell you whether users are affected).

**Key takeaway:** SLIs measure reality, SLOs set internal standards, SLAs make promises to customers — always set SLAs below SLOs to preserve operational headroom.

</details>

> 📖 **Theory:** [SLO/SLA/SLI](./14_observability/theory.md)

---

### Q65 · [Thinking] · `alerting-strategies`

> **What is alert fatigue? Compare threshold-based alerting vs SLO burn-rate alerting. Why does SLO burn-rate alerting have fewer false positives?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Alert fatigue** occurs when on-call engineers receive so many alerts — many of them non-actionable or transient — that they begin ignoring or dismissing alerts reflexively, missing real incidents buried in the noise.

**How to think through this:**
1. **Threshold-based alerting**: "Alert if error rate > 1% for 5 minutes." Simple to configure, but generates false positives: a momentary spike to 1.1% at 3 AM on a Sunday with zero user impact triggers a page. It also generates false negatives: a sustained 0.9% error rate (just below threshold) for hours never alerts, even though it may be violating your SLO.
2. **SLO burn-rate alerting**: instead of alerting on raw metric values, you alert on how fast you are consuming your **error budget**. If your SLO is 99.9% over 30 days, your error budget is 0.1% of requests (43.2 minutes). A burn-rate alert fires when you are burning through that budget faster than sustainable. For example: "Alert if the 1-hour burn rate is >14x" (consuming the monthly budget in ~2 days). The alert fires only when user experience is materially at risk relative to your SLO.
3. **Why fewer false positives**: a momentary spike that lasts 2 minutes consumes a tiny fraction of the monthly budget — burn-rate alerting ignores it. Threshold alerting fires immediately. SLO burn-rate is calibrated to real user impact over time, not instantaneous fluctuations. The Google SRE workbook recommends a combination of a fast burn-rate alert (high urgency, short window) and a slow burn-rate alert (lower urgency, longer window) to cover both sudden and gradual degradation.

**Key takeaway:** SLO burn-rate alerting ties pages to actual user impact relative to your commitments — eliminating the false positives of threshold alerting that don't materially violate the SLO.

</details>

> 📖 **Theory:** [Alerting Strategies](./14_observability/theory.md)

---

### Q66 · [Critical] · `replication-lag`

> **A user updates their profile and immediately refreshes the page — they see the old data. What is happening? How do you fix this with read-your-own-writes consistency? What is the tradeoff?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The user's write went to the **primary** database replica, but the subsequent read was served by a **read replica** that has not yet received and applied that write. This delay is called **replication lag**.

**How to think through this:**
1. In a typical read-heavy architecture, writes go to the primary and reads are distributed across multiple read replicas for scalability. Replication from primary to replica is asynchronous — it happens in near-real-time but not instantaneously. Under normal conditions, lag is milliseconds. Under load, or during a network hiccup, it can be seconds or more. If a user writes and reads within that lag window, the read replica serves stale data.
2. **Read-your-own-writes (RYOW) consistency** is the guarantee that a user always sees the result of their own most recent write, even if that write hasn't propagated to all replicas. Implementation options:
   - **Always read from primary after a write**: after the profile update, route all reads for that user to the primary for a short window (e.g., 1 minute, tracked in a session cookie or cache entry). After the window, resume reading from replicas.
   - **Track replication position**: note the primary's replication log position after the write. Route the user's next read to any replica that has caught up to at least that position. If none have, fall back to the primary.
   - **Sticky session routing**: always route a given user's reads to the same replica, combined with ensuring their writes go there too — complex and reduces load distribution.
3. The tradeoff: RYOW increases load on the primary (by routing some reads there) and adds complexity to your routing layer. It only guarantees that the write author sees their own writes — other users may still see stale data until replication catches up. It is not full strong consistency.

**Key takeaway:** Read-your-own-writes consistency routes a user's post-write reads to the primary (or a sufficiently caught-up replica) — it prevents the jarring "my change disappeared" experience at the cost of slightly higher primary load.

</details>

> 📖 **Theory:** [Replication Lag](./05_databases/theory.md)

## ⚡ Tier 3 — Advanced Distributed Systems

---

### Q67 · [Design] · `fan-out-social-feed`

> **Design the data flow for a Twitter-like social feed. Compare fan-out on write vs fan-out on read. What is the hybrid approach used by large-scale systems?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Fan-out on write** (push model): when a user posts, the tweet is immediately written to every follower's feed cache. Reads are fast — the feed is pre-computed. Writes are expensive — a celebrity with 10M followers triggers 10M cache writes per tweet.

**Fan-out on read** (pull model): when a user opens their feed, the system fetches tweets from all accounts they follow and merges them. Reads are expensive — following 500 accounts means 500 lookups per feed load. Writes are cheap — one write to the author's timeline.

**Hybrid approach (Twitter's actual model):**
- For users with fewer than ~10K followers: fan-out on write. Pre-populate feed caches.
- For **celebrity accounts** (high follower count): fan-out on read. Their tweets are fetched and merged at read time.
- At read time, the system merges the pre-computed feed with any celebrity tweets the user follows.

**How to think through this:**
1. Identify the asymmetry: most users are readers, not posters. Reads must be fast.
2. The bottleneck shifts based on follower count. Fan-out on write is O(followers) writes per post.
3. Celebrities break fan-out on write — 10M writes for one tweet is unacceptable. Pull at read time instead.
4. The hybrid minimises worst-case: normal users get fast reads via pre-built feeds; celebrity writes don't blow up the write path.

**Key takeaway:** There is no universally correct fan-out strategy — the right answer depends on the follower distribution, and large systems use a hybrid that switches strategy based on account size.

</details>

> 📖 **Theory:** [Fan-Out Pattern](./21_real_time_systems/theory.md#write-to-influxdb)

---

### Q68 · [Thinking] · `write-heavy-optimisations`

> **Your service receives 100,000 writes/second. List four architectural techniques to handle this load without scaling the database vertically.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
1. **Write buffering / batching**: accumulate writes in memory (e.g., an in-process queue or a service like Kafka) and flush to the database in bulk. Turns 100K individual row inserts into batched bulk inserts, which are dramatically more efficient.
2. **Write-ahead log offloading / event sourcing**: append events to a fast, sequential log (Kafka, Kinesis) first. Consumers process the log asynchronously and persist to the database at a sustainable rate. The log absorbs the burst.
3. **Horizontal sharding**: distribute writes across multiple database nodes by partitioning on a key (user ID, region). 100K writes/sec across 10 shards = 10K writes/sec per node — well within range for most databases.
4. **CQRS with a write-optimised store**: use a separate write store optimised for append-heavy workloads (e.g., Cassandra, ScyllaDB, or a time-series DB like InfluxDB) and project reads to a separate read-optimised store. Each store is tuned for its workload.

**How to think through this:**
1. The core problem is write amplification and lock contention on a single database.
2. The first lever is reducing the number of round trips (batching).
3. The second lever is making writes asynchronous (decoupling via a log or queue).
4. The third lever is distributing the load (sharding, CQRS).

**Key takeaway:** High write throughput is almost always solved by making writes asynchronous, batched, or distributed — not by making a single database faster.

</details>

> 📖 **Theory:** [Write-Heavy Optimization](./11_scalability_patterns/theory.md)

---

### Q69 · [Critical] · `hot-partition`

> **A Cassandra cluster has one node at 90% CPU while others sit at 10%. What is a hot partition and how does it happen? Give two strategies to fix it.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **hot partition** occurs when a disproportionate share of reads or writes routes to a single partition key, causing one node to handle far more load than others. Cassandra assigns data to nodes based on the partition key hash. If one key — say `user_id = "beyonce"` or `date = "2024-01-01"` — receives millions of requests, all traffic for that key lands on the same node.

**How it happens:**
- **Cardinality mismatch**: using a low-cardinality key (e.g., `status = "active"`) as the partition key means millions of rows and requests all route to one or two nodes.
- **Celebrity / viral content**: a single entity (user, event, product) suddenly receives disproportionate traffic. The hash is consistent, so all that traffic hits one node.
- **Time-series anti-pattern**: using a date or hour as the partition key causes all current writes to go to one node ("write hotspot"), with older nodes sitting idle.

**Two strategies to fix it:**

1. **Partition key salting / composite keys**: append a random suffix (bucket number 0–N) to the partition key, e.g., `user_id#3`. Distribute writes across N partitions. Reads must scatter-gather across all N buckets and merge results. This distributes the load at the cost of read complexity.

2. **Application-level sharding / tiered storage for hot entities**: detect hot keys (via monitoring or a frequency sketch like **Count-Min Sketch**) and route them to a dedicated cache layer (Redis) or a separate, over-provisioned Cassandra keyspace. The hot key never reaches the general cluster.

**How to think through this:**
1. First confirm it's a partition issue, not a node hardware problem — check that other nodes are genuinely idle.
2. Identify the hot key using Cassandra's `nodetool tpstats` and read/write metrics per partition.
3. Solutions either spread the key (salting) or absorb it elsewhere (cache).

**Key takeaway:** Hot partitions are a data modelling problem, not an infrastructure problem — the fix must happen at the key design level or by absorbing traffic before it hits the partition.

</details>

> 📖 **Theory:** [Hot Partition](./05_databases/theory.md)

---

### Q70 · [Thinking] · `thundering-herd`

> **What is the thundering herd problem? Give two scenarios where it occurs in distributed systems. How do mutex/lock, jitter, and probabilistic early expiration each address it?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The **thundering herd problem** occurs when a large number of processes or threads simultaneously wake up or send requests in response to a single event, overwhelming a downstream resource.

**Two scenarios:**
1. **Cache expiry stampede**: a popular cache key expires. Thousands of concurrent requests all find a cache miss simultaneously and all query the database at once. The database, which was previously shielded by the cache, receives a sudden spike it cannot handle.
2. **Service restart / reconnect storm**: a message broker or service restarts. Hundreds of consumers all reconnect and re-subscribe at exactly the same moment, flooding the broker with connection and resubscription requests.

**How each mitigation works:**

- **Mutex / lock (cache lock pattern)**: when a cache miss occurs, only one thread acquires a lock and fetches from the database. All other threads wait or serve a stale value. The database receives exactly one request instead of thousands. Downside: waiting threads add latency.

- **Jitter**: introduce random delay before retry or reconnection. Instead of all clients retrying at T+1s, they retry at T+(random 0–2s). This spreads the load over time, converting a spike into a curve. Commonly used in exponential backoff: `base_delay * 2^attempt + random(0, base_delay)`.

- **Probabilistic early expiration (PER)**: before the TTL expires, each request has a small probability of treating the key as expired and proactively regenerating it. The probability increases as expiry approaches. This means the cache is refreshed before it expires, so no simultaneous miss event occurs.

**How to think through this:**
1. The root cause is synchronisation — many clients react to the same event at the same time.
2. Mutex serialises the reaction. Jitter desynchronises timing. PER prevents the miss from occurring at all.
3. Each has a cost: mutex adds latency, jitter adds delay, PER adds background computation.

**Key takeaway:** The thundering herd is a synchronisation problem — every mitigation works by breaking the simultaneity, either by serialising access, randomising timing, or pre-emptively refreshing before the herd can form.

</details>

> 📖 **Theory:** [Thundering Herd](./11_scalability_patterns/theory.md)

---

### Q71 · [Interview] · `tail-latency-p99`

> **Why is p99 latency more important than average latency for user experience? What is the "long tail" effect? What are three common causes of p99 latency spikes?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Average latency** is misleading because it is dominated by the fast majority. If 99 requests complete in 10ms and 1 takes 1000ms, the average is ~20ms — which sounds fine, but 1% of your users are waiting a full second.

**p99 latency** is the latency at the 99th percentile: 99% of requests are faster than this value. It represents the worst experience that is still "normal" (not an outlier). For user-facing systems, 1% of requests is often thousands of users per minute.

The **long tail effect**: in complex systems, a user request often fans out to multiple backend services. If each service has a p99 of 50ms, a request that calls 10 services in parallel has a ~10% chance of hitting that 50ms tail on at least one call. The tail of the aggregate distribution is far worse than any individual service's tail.

**Three common causes of p99 latency spikes:**
1. **Garbage collection pauses (GC)**: JVM and Go runtimes periodically pause execution for GC. A full GC pause of 200ms on any request in flight causes a spike. These are bursty and hard to see in averages.
2. **Lock contention**: a shared resource (database connection pool, mutex, thread pool) becomes a bottleneck under load. Requests queue behind the lock. p50 stays low because most requests don't contend; p99 captures the ones that do.
3. **Cold cache / cold start**: a first request after a cache eviction, a new node joining, or a deployment must fetch from a slow upstream. Subsequent requests are fast. The first request — which lands in the tail — is orders of magnitude slower.

**How to think through this:**
1. In a microservices architecture, tails compound. You cannot ignore them.
2. p99 is the canary: it tells you what's lurking before it becomes a p50 problem.
3. Diagnosis requires percentile-level metrics (histograms), not averages.

**Key takeaway:** Average latency hides the users who are suffering — p99 is the metric that tells you what your worst-normal experience actually feels like.

</details>

> 📖 **Theory:** [Tail Latency](./11_scalability_patterns/theory.md)

---

### Q72 · [Normal] · `back-of-envelope`

> **Why do system design interviews ask for back-of-envelope calculations? What are the three numbers you should always know: typical read/write latency, storage costs, and network bandwidth?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Back-of-envelope (BOE) calculations serve two purposes in design interviews: (1) they prove you can reason about scale before committing to an architecture, and (2) they expose bottlenecks early — a calculation that shows 10TB/day of writes immediately tells you that a single relational database is the wrong tool.

**The three categories of numbers to know:**

**Latency (approximate):**
- L1 cache: ~1ns
- Main memory (RAM) access: ~100ns
- SSD random read: ~100µs
- Network within same datacenter: ~500µs–1ms
- HDD seek: ~10ms
- Cross-region network: ~100ms
- Rule of thumb: memory is 1000x faster than SSD, SSD is 100x faster than disk

**Storage costs (rough order of magnitude, cloud):**
- Object storage (S3): ~$0.023/GB/month
- SSD block storage (EBS gp3): ~$0.08/GB/month
- In-memory (ElastiCache/Redis): ~$0.25–$0.50/GB/month
- Rule of thumb: memory costs ~10x SSD, SSD costs ~3–4x object storage

**Network bandwidth:**
- Gigabit NIC: 125 MB/s
- Modern server NIC: 1–10 GB/s
- CDN edge: effectively unlimited for popular content
- Cross-region replication: budget for latency, not just throughput
- Rule of thumb: assume 1 Gbps (~100 MB/s) per server for conservative estimates

**How to think through this:**
1. BOE catches architectural mismatch early — no one should spend 20 minutes designing a sharded database only to find the data fits in 50GB.
2. The numbers don't need to be exact. Order-of-magnitude correctness is the goal.
3. Always derive: requests/sec → data/sec → storage/year → cost.

**Key takeaway:** Back-of-envelope math is how senior engineers avoid over-engineering — knowing the numbers tells you when a simple solution is sufficient and when scale forces complexity.

</details>

> 📖 **Theory:** [Back-of-Envelope](./23_interview_framework/theory.md)

---

### Q73 · [Design] · `designing-for-failure`

> **What does "design for failure" mean in distributed systems? List five concrete techniques for making a system gracefully degrade when dependencies fail.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
"Design for failure" means building systems that assume components will fail — networks partition, services crash, databases slow down — and ensuring that failures are isolated, bounded, and handled without cascading into full system outages.

**Five concrete techniques:**

1. **Circuit breaker**: wrap calls to external services in a circuit breaker. After N consecutive failures, the circuit "opens" and immediately returns a fallback (error, cached value, default) without attempting the call. This prevents a slow dependency from exhausting your thread pool. The circuit half-opens after a timeout to probe recovery. Libraries: Hystrix, Resilience4j.

2. **Timeout + retry with exponential backoff and jitter**: every network call must have a timeout. Retries must use exponential backoff (not immediate retry, which amplifies load) with jitter (to avoid retry storms). Without timeouts, a stalled dependency stalls all threads waiting on it.

3. **Bulkhead isolation**: allocate separate thread pools or connection pools for different dependencies. If the payment service thread pool exhausts, it cannot consume threads destined for the user service. Failure is isolated to one bulkhead. Named after ship compartments that prevent flooding from sinking the whole vessel.

4. **Graceful degradation / fallback responses**: define what a "good enough" response looks like when a dependency is unavailable. A recommendation service going down should not crash the homepage — return a cached list of popular items instead. Identify every hard dependency and ask: "Can we serve something useful without this?"

5. **Health checks + load balancer integration**: services expose `/health` endpoints. Load balancers or service meshes (Envoy, Istio) continuously probe health and remove unhealthy instances from the rotation automatically. Combine with **readiness** (is this instance ready to receive traffic?) and **liveness** (is this instance still alive?) checks.

**How to think through this:**
1. Map every dependency. For each: what happens if it's slow? What if it's down?
2. Assign a failure mode: fail fast (circuit breaker), degrade (fallback), or queue (async).
3. Test failure paths explicitly — chaos engineering (Netflix Chaos Monkey) forces this discipline.

**Key takeaway:** A system that degrades gracefully under failure is more valuable than a system that is fast under normal conditions — the failure path is the one that matters most in production.

</details>

> 📖 **Theory:** [Design for Failure](./10_distributed_systems/theory.md)

---

### Q74 · [Thinking] · `data-replication-lag`

> **What causes replication lag in a primary-replica database setup? What is "replica drift" and how does it compound over time? How do you monitor and alert on replication lag?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
In a **primary-replica** setup, the primary writes changes to a replication log (WAL in PostgreSQL, binlog in MySQL). Replicas connect to the primary, read the log, and apply changes. **Replication lag** is the delay between a write being committed on the primary and the same write being visible on a replica.

**Causes of replication lag:**
- **Single-threaded replay**: many databases apply the replication log serially on the replica. The primary writes with multiple concurrent threads; the replica replays one operation at a time. Under heavy write load, the replica falls behind.
- **Long-running transactions**: a large batch update on the primary produces a large transaction in the log. The replica must apply the entire transaction before it can move forward, causing a spike in lag.
- **Network latency / bandwidth saturation**: the log stream between primary and replica is constrained by network. A busy primary generating 500MB/s of WAL on a 1Gbps link leaves little headroom.
- **Resource contention on replica**: if the replica is simultaneously serving heavy read traffic, CPU and I/O contention slows down log application.

**Replica drift** is the state where a replica's data diverges from the primary not just in recency but in correctness — e.g., due to manual writes to a replica, DDL operations applied inconsistently, or silent replication errors. Drift compounds because each unsynced state creates a foundation for further divergence. Detecting drift requires periodic full-table checksumming (e.g., `pt-table-checksum` in MySQL), not just lag monitoring.

**Monitoring and alerting:**
- **PostgreSQL**: `SELECT now() - pg_last_xact_replay_timestamp() AS replication_lag;` on the replica. Expose via Prometheus + postgres_exporter.
- **MySQL**: `SHOW SLAVE STATUS\G` → `Seconds_Behind_Master`. Alert at >30s, page at >5min.
- **Alert thresholds**: set based on SLA. If your app reads from replicas and tolerates 5s staleness, alert at 10s lag.
- **Drift detection**: run `pt-table-checksum` weekly or after large migrations. Alert on any checksum mismatch.

**How to think through this:**
1. Lag is a symptom, not a root cause. Diagnose: is it serial replay, network, or resource contention?
2. Drift is more dangerous than lag — lag is temporary, drift can be permanent data corruption.
3. Monitor lag continuously; check for drift periodically.

**Key takeaway:** Replication lag is expected under load but must be bounded — unbounded lag means your replicas are not actually providing the read scaling or failover safety you designed for.

</details>

> 📖 **Theory:** [Replication Lag](./05_databases/theory.md)

---

### Q75 · [Design] · `global-system-design`

> **You need to serve users in the US, Europe, and Asia with low latency. What architectural patterns do you use? Cover: data residency, active-active vs active-passive, and conflict resolution.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Data residency** requirements come first — GDPR mandates EU user data stays in the EU; some financial regulations restrict cross-border data movement. Architect regions as first-class concerns: each region owns a partition of user data determined by the user's home region. A EU user's data lives in Frankfurt. Their requests are routed there by GeoDNS.

**Active-active vs active-passive:**

- **Active-passive**: one region is primary; others are read replicas or hot standbys. All writes go to the primary. Reads can be served regionally if staleness is tolerable. Failover promotes a passive region. Simple to reason about; writes always incur cross-region latency for users not in the primary region.

- **Active-active**: each region accepts reads AND writes for its local users. No cross-region write latency. Harder to implement because concurrent writes to different regions on the same data create conflicts.

For most user-facing applications: use **active-active with regional data ownership**. A US user's writes go to the US region; an EU user's writes go to the EU region. Regions only need to sync data that is genuinely shared (e.g., a shared document, a global leaderboard).

**Conflict resolution** (required for truly shared mutable data in active-active):
- **Last write wins (LWW)**: simplest. Use a wall-clock or logical timestamp; the later write wins. Risk: clock skew causes silent data loss.
- **CRDTs (Conflict-free Replicated Data Types)**: data structures that merge deterministically — counters, sets, maps. No conflict possible by design. Good for counters and presence.
- **Application-level merge**: surface conflicts to the application layer and implement domain-specific logic (e.g., Google Docs uses operational transformation; version vectors track causal history).
- **Event sourcing**: append-only logs per region, merge logs at read time using a defined ordering.

**Additional patterns:**
- **GeoDNS + Anycast routing**: route users to the nearest region.
- **Edge caching (CDN)**: static and semi-static content cached at 100+ edge nodes globally. Reduces origin load by 90%+.
- **Regional isolation with async cross-region replication**: each region can operate independently (no strong consistency across regions); changes replicate asynchronously with defined lag SLAs.

**How to think through this:**
1. Start with compliance: what data can and cannot leave which region?
2. Decide write strategy: can you partition writes by user home region? If yes, active-active is clean.
3. Shared mutable state is the hard problem — minimise it, then pick a conflict strategy appropriate to the domain.

**Key takeaway:** Global systems are won by partitioning data ownership by region, not by synchronising everything — true global consensus is slow, and the goal is to make most operations entirely local.

</details>

> 📖 **Theory:** [Global System Design](./15_cloud_architecture/theory.md#dynamodb-global-tables-active-active-multi-region-writes)

## 🏋️ Tier 4 — Interview / Scenario

---

### Q76 · [Interview] · `explain-cap-junior`

> **Explain the CAP theorem to a junior developer. Use an analogy (not the partition/node/client abstraction). Give them a rule of thumb for remembering it.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Imagine a bank with two branches: one in New York, one in London. They share the same account data.

You walk into the New York branch and deposit $1,000. A second later, someone calls the London branch and asks for your balance. The network cable between the two branches is cut.

The London branch has three options:
1. Tell the caller your old balance (wrong answer, but the branch stays open) — this is **availability over consistency**.
2. Refuse to answer until the cable is repaired (correct answer only when synced) — this is **consistency over availability**.
3. Pretend the network is never cut — this is **not an option in reality**.

That's CAP. **Consistency** means every node gives the same answer. **Availability** means every node gives *some* answer. **Partition tolerance** means the system keeps running even when the network between nodes breaks.

The catch: network partitions happen in any distributed system. You cannot opt out of P. So the real choice is: when the network breaks, do you want correct data (C) or a response at all (A)?

**Rule of thumb:** "Pick two, but P is mandatory — so really, you're choosing C or A when things go wrong."

- **CP systems** (correct but possibly unavailable): HBase, Zookeeper, etcd. Used for coordination, leader election.
- **AP systems** (always answer, possibly stale): Cassandra, DynamoDB (default), CouchDB. Used for user-facing data where staleness is tolerable.

**How to think through this:**
1. CAP is about failure modes, not normal operation. Under normal conditions, most systems appear CA.
2. The question to ask is: "What do we do when a network partition happens?"
3. This is a business decision disguised as a technical one — it depends on what "wrong" costs vs what "down" costs.

**Key takeaway:** CAP is not about choosing three properties — it is about deciding which guarantee you sacrifice when the network inevitably breaks.

</details>

> 📖 **Theory:** [CAP Theorem](./02_system_fundamentals/theory.md#6-cap-theorem)

---

### Q77 · [Interview] · `explain-eventual-consistency`

> **Explain eventual consistency using a real-world, non-technical analogy. Then explain when it is and isn't acceptable in software systems.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Think about Wikipedia. Anyone can edit an article. When you save an edit, it does not instantly appear for every reader worldwide — different CDN edge nodes and caches serve the old version for minutes or hours. But eventually, every reader sees your change. No single version is "locked" while others sync. The system converges to the same state given enough time.

That is **eventual consistency**: all replicas will agree on the same value *eventually*, but there is no guarantee of when, and during the window of inconsistency, different nodes may return different values.

**When eventual consistency is acceptable:**
- **Social media likes/follower counts**: if a tweet shows 9,999 likes instead of 10,000 for a few seconds, no user is harmed.
- **Product catalog / search indexes**: a new product appearing in search results 30 seconds after it is created is fine.
- **User profile updates**: a profile photo change taking a few seconds to propagate globally is tolerable.
- **Shopping cart reads**: seeing a slightly stale cart is acceptable; the final checkout validation uses a consistent read.

**When eventual consistency is NOT acceptable:**
- **Financial transactions**: a bank account debit must be visible to all systems immediately. Double-spending is a consistency violation with real consequences.
- **Inventory systems**: "only 1 left in stock" must be accurate — overselling is a business-critical consistency failure.
- **Authentication / sessions**: a password change must be immediately enforced. A stale session allowing login after account deletion is a security issue.
- **Leader election / distributed locks**: if two nodes both believe they are leader, you have a split-brain. This requires strong consistency.

**How to think through this:**
1. Ask: "What is the cost of reading stale data?" If the cost is cosmetic, eventual consistency is fine. If the cost is money, security, or correctness, use strong consistency.
2. Also ask: "How long is 'eventually'?" Eventual consistency in 100ms is very different from eventual consistency in 10 minutes.

**Key takeaway:** Eventual consistency is a trade — you exchange correctness guarantees for availability and performance, and whether that trade is acceptable depends entirely on the domain.

</details>

> 📖 **Theory:** [Eventual Consistency](./02_system_fundamentals/theory.md#8-consistency-models)

---

### Q78 · [Interview] · `explain-sharding-analogy`

> **Explain database sharding to someone who has only worked with a single database. Use a real-world analogy. What is the main challenge of sharding that the analogy should convey?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Imagine a single filing cabinet that holds every customer's folder. For years it works fine. Then your company grows to 10 million customers — the cabinet is overflowing, and finding any folder takes too long because the cabinet is always busy.

Your solution: get 10 cabinets and a simple rule — customers whose last name starts with A–C go in cabinet 1, D–F in cabinet 2, and so on. Each cabinet handles 1/10th of the work. This is **sharding** — splitting data across multiple independent databases (shards), each responsible for a subset of the total data.

**The main challenge the analogy must convey — cross-shard operations:**

Now imagine you need to find every customer who spent over $10,000 last year. With one cabinet, you just look through it. With 10 cabinets, you must search all 10 and combine the results. That is expensive and slow.

Worse: what if a customer gets married and their last name changes from "Adams" to "Zhang"? Their folder needs to physically move from cabinet 1 to cabinet 10. This is **resharding** — and in a real database, it means migrating data live without downtime, one of the hardest operational problems in distributed systems.

**Practical details:**
- The rule that determines which shard owns a record is the **shard key**. Choosing it poorly causes **hot shards** (one cabinet is always busy, others are idle).
- Queries that span multiple shards (**cross-shard joins**) cannot use database-level joins — they must be done in application code after fetching from multiple shards.
- Transactions that touch multiple shards require **distributed transactions** (expensive) or must be avoided by design.

**How to think through this:**
1. Sharding solves the vertical scaling limit by distributing data, not just load.
2. The shard key is the most important design decision — it determines data distribution and what queries are efficient.
3. The price is query complexity and operational overhead. Shard only when you must.

**Key takeaway:** Sharding solves scale by distributing data, but it transfers complexity from the database to the application and operations team — the main challenge is not splitting data, it is handling everything that crosses shard boundaries.

</details>

> 📖 **Theory:** [Database Sharding](./05_databases/theory.md)

---

### Q79 · [Interview] · `explain-consistent-hashing`

> **Explain consistent hashing to a developer who understands modulo hashing. What does the "ring" represent? Why does it matter when a node leaves?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
With **modulo hashing**, you assign a key to a node with `hash(key) % N` where N is the number of nodes. It's simple. The problem: when N changes (a node joins or leaves), almost every key remaps to a different node. If you have a cache with 10 nodes and add an 11th, ~90% of cache keys now point to a different node — an instant cache invalidation storm.

**Consistent hashing** solves this. Imagine a circular number line from 0 to 2^32 (a "ring"). Both nodes and keys are hashed onto this ring. To find which node owns a key, you walk clockwise around the ring from the key's position until you hit a node. That node owns the key.

When you **add a node**, it takes over the keys that were previously "walked" to its clockwise neighbour. Only those keys need to move — roughly `K/N` keys, where K is total keys and N is total nodes. Every other key is unaffected.

When a **node leaves**, its keys are absorbed by its clockwise neighbour. Again, only the keys that were assigned to the departed node move.

**Why this matters:**
- Modulo hashing: adding 1 node to 10 → remaps ~90% of keys.
- Consistent hashing: adding 1 node to 10 → remaps ~10% of keys.

**Virtual nodes (vnodes)**: in practice, each physical node is represented by multiple positions on the ring (e.g., 150 virtual nodes per physical node). This ensures even distribution even with a small number of physical nodes, and allows fine-grained load balancing by adjusting how many virtual nodes a node holds.

**Where it's used:** Cassandra, DynamoDB, Memcached (ketama), and most distributed caches use consistent hashing for data placement.

**How to think through this:**
1. The ring is just a hash space where position determines ownership.
2. Consistent hashing minimises remapping by making each node responsible for a contiguous segment of the hash space.
3. Virtual nodes fix the uneven distribution that small ring sizes create.

**Key takeaway:** Consistent hashing solves the resharding problem by ensuring that only a minimal fraction of keys need to move when the cluster topology changes.

</details>

> 📖 **Theory:** [Consistent Hashing](./11_scalability_patterns/theory.md)

---

### Q80 · [Interview] · `explain-rate-limiting-pm`

> **A product manager asks: "We're getting too many 429 errors — can't we just remove rate limiting?" Give a clear explanation of why rate limiting protects both the service and legitimate users.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Rate limiting is not about punishing users — it is about ensuring that one user cannot degrade the experience for everyone else. Here is the concrete explanation:

**Without rate limiting, a single bad actor can take down the service for everyone.** Imagine we have 10,000 API calls/second of capacity. A single client — whether a bug in their code, a scraper, or a DDoS attack — starts sending 8,000 calls/second. Every other user now has access to only 2,000 calls/second of capacity. Their requests slow down or fail. The 429 errors that one client is seeing are protecting the 99% of clients who are not misbehaving.

**It also protects us from our own bugs.** A client app with a retry loop bug can unintentionally generate thousands of requests per second. Without rate limiting, that bug takes down our service. With rate limiting, the buggy client gets 429s, our service stays healthy, and we have time to diagnose the bug.

**The 429 errors you are seeing are the rate limiter working correctly.** The question is not "should we remove it" but "why is this client hitting the limit?" The right action is to investigate: is the client legitimate and we set the limit too low? Or are they abusing the API?

**The fix is not to remove rate limiting — it is to:**
1. Set appropriate limits based on legitimate use cases.
2. Communicate limits clearly in API documentation.
3. Provide higher-tier limits for known high-volume partners via API keys.

**How to think through this:**
1. 429s are a signal, not a problem. The problem is the cause of the 429s.
2. Removing rate limiting to fix 429 errors is like removing a fire alarm to fix a noise complaint.
3. Rate limiting is also a cost control mechanism — uncapped API calls = uncapped compute costs.

**Key takeaway:** Rate limiting is not a restriction on users — it is a fairness mechanism that protects all users from each other, and the service from both attackers and accidental abuse.

</details>

> 📖 **Theory:** [Rate Limiting](./11_scalability_patterns/theory.md)

---

### Q81 · [Interview] · `compare-sql-nosql`

> **Your interviewer asks: "We're building a new feature and debating SQL vs NoSQL. How do you decide?" Give a structured framework for making the decision, not just a list of tradeoffs.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Rather than listing tradeoffs, use a five-question framework:

**1. What does the data look like?**
- Highly relational, with many entities that reference each other? SQL. A user has orders, orders have items, items have suppliers — this is a relational model.
- Document-shaped, semi-structured, schema varies per record? NoSQL document store (MongoDB, DynamoDB). A user profile with 200 optional fields, or a product catalog where every category has different attributes.

**2. What queries will you run?**
- Ad-hoc, complex joins, aggregations, analytical queries? SQL. The relational model and query planner are built for this.
- Simple lookups by primary key or a narrow set of access patterns? NoSQL. Cassandra, DynamoDB, and Redis are extremely fast at "give me user X's data" but painful for "find all users who did Y within Z timeframe."

**3. What is the scale of writes?**
- Moderate writes with complex reads? SQL scales well with replicas.
- Millions of writes per second, append-heavy, time-series? NoSQL (Cassandra, ScyllaDB, InfluxDB) — LSM-tree storage is built for this.

**4. Do you need ACID transactions?**
- Money, inventory, reservations — any situation where partial writes cause correctness problems? SQL (or NewSQL like CockroachDB, Spanner).
- Can you tolerate eventual consistency? Does each record operate independently? NoSQL is viable.

**5. What does your team know?**
- A team that knows PostgreSQL deeply will outperform a team struggling with Cassandra data modelling. Operational familiarity is a real cost. Do not adopt NoSQL for scale you do not yet have.

**Decision heuristic:** Start with PostgreSQL. It is the default correct answer for most features at most companies. Migrate when you have a specific, measured problem that relational databases cannot solve.

**How to think through this:**
1. NoSQL is not "better at scale" — it is "better at specific scale patterns with specific access patterns."
2. The access pattern question is the most important — NoSQL requires you to model data around queries, not around entities.

**Key takeaway:** Choose SQL by default and choose NoSQL only when you can name the specific constraint (write throughput, schema flexibility, geographic distribution) that SQL cannot meet.

</details>

> 📖 **Theory:** [SQL vs NoSQL](./05_databases/theory.md)

---

### Q82 · [Interview] · `compare-kafka-rabbitmq`

> **Compare Kafka and RabbitMQ. What is the fundamental architectural difference (log vs queue)? When would you choose each?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The fundamental difference is the storage model.

**RabbitMQ** is a **message broker with a queue model**. Messages are pushed to consumers. Once a consumer acknowledges a message, it is deleted. The broker manages delivery state. Multiple consumers compete for messages from the same queue (competing consumers pattern). It is optimised for task distribution and point-to-point messaging.

**Kafka** is a **distributed log**. Messages are appended to a log and retained for a configurable period (days, weeks, or forever). Consumers read from the log using an offset — a pointer to their position. The broker does not track per-message delivery state. Multiple independent consumer groups can read the same messages simultaneously, each maintaining their own offset. It is optimised for event streaming, replay, and fan-out.

**Key differences:**

| | RabbitMQ | Kafka |
|---|---|---|
| Model | Queue (push) | Log (pull) |
| Message retention | Deleted after ack | Retained by time/size |
| Replay messages | No | Yes |
| Multiple consumers | Competing (one gets it) | Independent (all can read) |
| Ordering guarantee | Per-queue | Per-partition |
| Throughput | High (100K msg/s) | Very high (millions/s) |
| Best for | Task queues, RPC | Event streaming, audit logs |

**Choose RabbitMQ when:**
- You are distributing tasks across workers (email sending, image processing).
- You need complex routing (topic exchanges, header matching).
- Messages should not be re-processed after acknowledgment.
- You want push-based delivery with low operational complexity.

**Choose Kafka when:**
- Multiple systems need to consume the same event stream independently (analytics, audit, ML pipeline).
- You need to replay historical events (reprocessing, backfilling a new service).
- You need very high throughput (10M+ messages/day).
- Event ordering and durability are critical (financial event logs).

**How to think through this:**
1. If the question is "who processes this task?" — RabbitMQ.
2. If the question is "what happened, and who needs to know?" — Kafka.

**Key takeaway:** RabbitMQ is for work distribution; Kafka is for event broadcasting and durable event history — the choice is about whether messages are tasks to complete or facts to record.

</details>

> 📖 **Theory:** [Kafka vs RabbitMQ](./09_message_queues/theory.md)

---

### Q83 · [Interview] · `compare-monolith-microservice`

> **A CTO asks: "Should we break our monolith into microservices?" Give a structured answer covering: when it makes sense, when it doesn't, and the hidden costs of microservices.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Start by asking: "What problem are you trying to solve?" Microservices are an architectural solution — but they only make sense if the problem they solve is worse than the problems they introduce.

**When microservices make sense:**
- **Independent scaling**: one part of your system (e.g., video encoding) needs 10x the compute of the rest. Extracting it as a service lets you scale it independently without scaling everything.
- **Independent deployment**: multiple teams are blocked by deploy contention. A monolith means one team's change can break another's release. Service boundaries give teams autonomy.
- **Technology heterogeneity**: one service genuinely needs a different language or runtime (e.g., a Python ML service alongside a Java API).
- **Fault isolation**: a bug in one component should not take down the entire system.
- **Team scale**: you have 5+ teams, each owning a clear business domain. Conway's Law: the architecture should match the team structure.

**When microservices do not make sense:**
- Small team (fewer than 10 engineers): the coordination overhead dominates.
- Early-stage product: the domain model is not yet stable. Microservices freeze boundaries prematurely; a wrong service split is extremely expensive to undo.
- No operational maturity: microservices require container orchestration (Kubernetes), distributed tracing, centralised logging, service meshes, and on-call culture. Without this infrastructure, microservices are harder to run than a monolith.
- The monolith is fast enough: if the bottleneck is a slow database query, decomposing the service does not fix it.

**Hidden costs (the ones the CTO may not be accounting for):**
- **Distributed transactions**: what was one database transaction is now a multi-service saga. This is significantly harder to implement correctly.
- **Observability tax**: tracing a single user request across 10 services requires distributed tracing (Jaeger, Zipkin), centralised logging (ELK), and service-level metrics. None of this is free.
- **Network latency**: in-process function calls become network calls. Each hop adds latency and a failure mode.
- **Operational surface area**: 10 services means 10 deployment pipelines, 10 sets of alerts, 10 Kubernetes deployments to maintain.
- **Testing complexity**: integration testing across service boundaries is harder than testing a monolith.

**Recommended path:** Start with a **well-structured modular monolith** — clear internal boundaries, no cross-module database sharing — and extract services when you have a specific, measured scaling or autonomy problem.


**How to think through this:**
1. Start by identifying what problem the CTO is trying to solve — microservices are a solution, not a goal.
2. Microservices make sense when teams need independent deployments, services have wildly different scaling needs, or a monolith's complexity is causing organizational friction.
3. The hidden costs are high: distributed transactions, network latency between services, complex observability, and operational overhead — these costs are only justified if the benefits are larger.

**Key takeaway:** Microservices solve organisational and scaling problems, not technical ones — and their hidden operational costs often exceed their benefits until a team reaches the size and maturity to absorb them.

</details>

> 📖 **Theory:** [Monolith vs Microservices](./12_microservices/theory.md#microservices--theory)

---

### Q84 · [Interview] · `compare-redis-db-sessions`

> **Your team debates storing user sessions in Redis vs the relational database. Give tradeoffs across: read speed, scalability, persistence, operational complexity.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**Read speed:**
- **Redis**: sub-millisecond reads from in-memory store. Session validation on every API request adds ~0.5ms overhead.
- **Relational DB**: session lookup is a primary-key read on an indexed table — fast, but typically 1–5ms with connection pool overhead. Under high concurrency, sessions compete with application queries for database connections.
- **Winner: Redis** — the session check is on the hot path of every request; the difference matters at scale.

**Scalability:**
- **Redis**: scales horizontally via Redis Cluster. Session data is small (kilobytes); a single Redis node handles millions of sessions. Adding nodes is straightforward.
- **Relational DB**: sessions add read/write load to the same database handling business data. At high traffic, session writes (create, update, delete) consume a measurable fraction of database capacity. Scaling the database to handle sessions scales everything, which is expensive.
- **Winner: Redis** — offloading sessions from the relational database is a standard scaling pattern precisely because it removes high-frequency, low-value load from the primary data store.

**Persistence:**
- **Redis**: in-memory by default. If Redis restarts without persistence configured (RDB/AOF), all sessions are lost — every user is logged out. With AOF persistence enabled, recovery is possible but adds write overhead.
- **Relational DB**: sessions are durable by default. A database restart does not log users out.
- **Winner: Relational DB** — if session loss is unacceptable (e.g., financial application mid-transaction), the database provides durability without configuration.

**Operational complexity:**
- **Redis**: another service to deploy, monitor, patch, and back up. Requires Redis Cluster configuration for HA. Redis eviction policies (LRU, LFU) must be tuned to prevent active sessions being evicted under memory pressure.
- **Relational DB**: sessions are just another table. No additional infrastructure. Session TTL requires a cleanup job (DELETE WHERE expires_at < NOW()).
- **Winner: Relational DB** for simplicity; **Redis** at scale.

**Recommendation:** Use Redis for sessions at scale. Use the relational database for sessions in early-stage applications or when operational simplicity is prioritised. Enable Redis persistence (AOF) if session loss is unacceptable.


**How to think through this:**
1. Sessions need fast reads (every authenticated request reads the session), so storage latency is the key constraint.
2. Redis wins on speed: sub-millisecond reads, no ORM overhead, and horizontal scaling. The database is slower and adds load to a critical shared resource.
3. The tradeoff is persistence and tooling: databases are durable and have mature query tools; Redis requires backup configuration and loses data on restart without persistence enabled.

**Key takeaway:** Redis wins on speed and scalability at the cost of operational overhead and careful persistence configuration — the right choice depends on whether you are optimising for simplicity (early stage) or performance (scale).

</details>

> 📖 **Theory:** [Redis vs DB Sessions](./06_caching/theory.md)

---

### Q85 · [Interview] · `compare-rest-grpc-internal`

> **For internal service-to-service communication, compare REST and gRPC. What does gRPC offer that REST doesn't? What are the operational costs of adopting gRPC?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**REST over HTTP/1.1** is the default for service-to-service communication: human-readable JSON, widely understood, easy to debug with curl, and supported by every language and framework. For most internal services, it is sufficient.

**gRPC** is a high-performance RPC framework built on HTTP/2 that uses **Protocol Buffers** (protobuf) for serialisation.

**What gRPC offers that REST doesn't:**

1. **Performance**: protobuf is a binary serialisation format — typically 5–10x smaller payload than JSON and 2–5x faster to serialise/deserialise. Under high message volume (10K+ messages/second), this matters.

2. **HTTP/2 multiplexing**: multiple requests share a single TCP connection with no head-of-line blocking. REST over HTTP/1.1 typically requires multiple connections or pipelining hacks.

3. **Streaming**: gRPC natively supports server-streaming, client-streaming, and bidirectional streaming RPCs. REST has no native streaming primitive (you work around it with SSE or WebSockets).

4. **Strongly-typed contracts**: `.proto` files define the exact API contract. Code is generated for both client and server. Type mismatches are compile-time errors, not runtime surprises.

5. **Deadlines / cancellation**: gRPC propagates deadlines across service calls. If a top-level request times out, cancellation propagates down the call chain, freeing resources.

**Operational costs of adopting gRPC:**

1. **Tooling immaturity**: you cannot curl a gRPC endpoint. Debugging requires `grpcurl` or Bloom RPC. Browser clients cannot call gRPC directly (requires gRPC-Web and a proxy layer).

2. **Schema evolution discipline**: changing a `.proto` file requires coordination. Field numbers must not be reused. Without careful versioning, you create incompatibilities between service versions during rolling deployments.

3. **Language/framework support**: support is excellent in Go, Java, and C++. Python and Ruby support is functional but less polished. Some older frameworks have limited gRPC support.

4. **Load balancer compatibility**: HTTP/1.1 load balancing is simple (round-robin per request). HTTP/2 multiplexes multiple requests over one connection — L4 load balancers see one long-lived connection, not per-request load. You need L7-aware load balancing (Envoy, Istio) for proper gRPC load distribution.

**When to choose gRPC:** High-frequency internal calls where latency and throughput matter, streaming use cases, polyglot environments where protobuf codegen simplifies client maintenance.

**When to stick with REST:** Simple CRUD services, external APIs, teams not yet invested in protobuf tooling, anywhere HTTP/JSON debuggability is more valuable than marginal performance gains.


**How to think through this:**
1. For internal services, the main constraints are: performance, type safety between services, and ease of schema evolution.
2. gRPC wins on all three for internal use: binary encoding (10x smaller than JSON), generated clients enforce the contract at compile time, and Protocol Buffers support backward-compatible schema evolution.
3. The cost of gRPC is ecosystem complexity: harder to debug (binary protocol), requires tooling for schema management, and browser clients need gRPC-Web proxies.

**Key takeaway:** gRPC offers real performance and type-safety benefits for high-throughput internal communication, but it introduces tooling and operational complexity that must be weighed against actual measured performance needs.

</details>

> 📖 **Theory:** [REST vs gRPC](./03_api_design/theory.md)

---

### Q86 · [Design] · `production-db-bottleneck`

> **Your production database is at 90% CPU. Writes take 500ms. You have 5 minutes to mitigate before the service goes down. What do you do immediately? What do you fix next week?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Immediate mitigation (within 5 minutes):**

1. **Kill long-running queries**: run `SELECT * FROM pg_stat_activity WHERE state = 'active' ORDER BY duration DESC;` (PostgreSQL) or `SHOW PROCESSLIST` (MySQL). Identify queries running for minutes and kill them with `SELECT pg_cancel_backend(pid)`. A single runaway query can consume 50%+ of CPU.

2. **Enable connection pooling / check for connection storms**: if the connection count is abnormally high, you may be in a connection storm. Check `pg_stat_activity` count. If connections exceed the pool limit, PgBouncer or connection limits need immediate adjustment.

3. **Identify and block abusive callers**: check slow query log or APM (Datadog, New Relic). If one API endpoint is responsible for 80% of load, use a feature flag or circuit breaker to temporarily disable it. Taking one endpoint offline to save the whole service is the right call.

4. **Scale read replicas and reroute reads**: if your application can tolerate slightly stale reads, shift all read traffic to replicas immediately. This removes select-heavy load from the primary.

5. **Increase instance size if on cloud (last resort)**: if RDS/Cloud SQL, initiate a vertical scale. This takes 5–15 minutes but buys time. Do this in parallel while investigating, not instead of investigating.

**Medium-term fix (next week):**

1. **Add missing indexes**: run `EXPLAIN ANALYZE` on the slowest queries. Sequential scans on large tables are the most common cause of unexpected CPU spikes. Add targeted indexes.

2. **Implement query result caching**: for frequently-run, read-heavy queries with acceptable staleness, introduce a Redis cache layer. The goal is to shield the database from repeated identical queries.

3. **Review and fix N+1 query patterns**: application-level ORM misuse (loading 1000 users, then fetching profile for each individually) is a common cause of write-amplified load. Use query profiling to find and fix these.

4. **Connection pooling in front of the database**: deploy PgBouncer or ProxySQL to limit actual database connections and queue excess connections at the proxy layer.

5. **Implement read/write split in the application**: ensure all read paths explicitly use the replica connection string. Many applications default all traffic to primary.

**How to think through this:**
1. The 5-minute triage is about reducing load immediately — kill what is consuming the most, not about fixing root cause.
2. The root cause is almost always: missing index, runaway query, or write amplification.
3. Verify with metrics that each action had an effect before the next one.

**Key takeaway:** In a database crisis, your first job is to reduce the rate of incoming work, not to fix the root cause — kill bad queries, shed load, buy time, then fix properly.

</details>

> 📖 **Theory:** [DB Bottleneck](./05_databases/theory.md#databases--theory)

---

### Q87 · [Design] · `production-cache-stampede`

> **Your Redis cache key for a popular product page expires. 10,000 requests simultaneously hit the database. This brings the database down. What is this called? How do you prevent it?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
This is called a **cache stampede** (also: **thundering herd on cache miss** or **dog-pile effect**). It occurs when a high-traffic cache key expires and all concurrent requests that were being served by the cache simultaneously find a miss and query the database at the same time.

**Prevention strategies (from simple to robust):**

1. **Cache locking (mutex on cache miss)**: when a cache miss occurs, the first thread acquires a distributed lock (using `SET key NX EX` in Redis — atomic set-if-not-exists). Only that thread fetches from the database and repopulates the cache. All other threads either wait for the lock or serve a stale value. Simple to implement; adds lock-wait latency for the first cohort of requests.

2. **Stale-while-revalidate**: serve the stale cache value to all incoming requests while one background thread asynchronously refreshes the cache. The cache never has a "hard miss" for high-traffic keys — users see stale data for milliseconds, not a 500 error. Requires two TTLs: a "soft" TTL (when to start refreshing) and a "hard" TTL (when the value is truly expired).

3. **Probabilistic early expiration (XFetch algorithm)**: before the TTL expires, each request independently decides with a small probability to treat the key as expired and refresh it. The probability increases as expiry approaches. This ensures the key is refreshed before it actually expires, eliminating the simultaneous miss window.

4. **Request coalescing at the application layer**: maintain a pending-request map. If a cache miss occurs for key X, the first request starts a fetch and registers a promise. Subsequent requests for X while the fetch is in-flight subscribe to the same promise. When the fetch completes, all subscribers receive the result in one shot. Libraries like `singleflight` in Go implement this pattern.

5. **Staggered TTLs**: when setting cache keys for similar items, add a small random jitter to the TTL (e.g., base TTL ± random 10%). This prevents all similar keys from expiring simultaneously, spreading cache misses over time.

**For this specific scenario:** The pragmatic fix is cache locking or stale-while-revalidate. The product page data does not need to be perfectly fresh — serve stale while one background process refreshes.


**How to think through this:**
1. Identify the failure mode: when a cache key expires, the first request finds a cache miss and hits the database. But at high traffic, thousands of concurrent requests all find the same miss simultaneously.
2. This is a **cache stampede** (also called thundering herd) — the database receives a sudden spike exactly when it least needs it (the cache just expired).
3. Prevention strategies address the root cause: ensure only one request regenerates the cache (mutex/lock), or prevent simultaneous expiry (probabilistic early refresh, jitter on TTL).

**Key takeaway:** A cache stampede is caused by synchronised expiry and synchronised demand — the fix is to break the synchrony, either by serialising who fetches (lock), pre-expiring asynchronously (stale-while-revalidate), or staggering TTLs.

</details>

> 📖 **Theory:** [Cache Stampede](./06_caching/theory.md)

---

### Q88 · [Design] · `production-cascade-failure`

> **Service A calls Service B, which calls Service C. Service C starts timing out. Within 60 seconds, all three services are down. What happened? What architectural patterns would have prevented this?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
This is a **cascading failure** caused by **thread pool exhaustion and resource starvation propagating upstream**.

**What happened, step by step:**
1. Service C starts timing out. Instead of returning immediately, it holds connections open until the timeout (e.g., 30 seconds).
2. Service B calls Service C and waits. Each in-flight call to C holds a thread in B's thread pool.
3. New requests to B keep arriving. Each one calls C and waits. B's thread pool fills up — all threads are waiting on C.
4. Service B is now unable to process any new requests (thread pool exhausted). It starts timing out or returning 503s.
5. Service A calls B, which is now also slow. A's threads fill up waiting for B. Within seconds, A is also down.
6. All three services are down, even though the root cause was only in C.

**Patterns that would have prevented this:**

1. **Circuit breaker on each downstream call**: Service B should have a circuit breaker around its calls to C. After N timeouts, the circuit opens and B immediately returns an error (or fallback) instead of waiting. B's thread pool never fills up because it never holds threads waiting on a dead C.

2. **Timeout configuration that is shorter than upstream timeout**: if C has a 30s timeout, B must have a 25s timeout, and A must have a 20s timeout. This ensures that upstream callers fail fast before their own timeouts expire. Without this, the slowness of C is multiplied at each layer.

3. **Bulkhead isolation**: allocate a separate, bounded thread pool for calls to each downstream service. Even if all threads in the "C caller" pool are blocked, the pool for "database calls" or "other services" is unaffected. The failure is contained to one bulkhead.

4. **Async / non-blocking I/O**: with reactive or async frameworks (Netty, Node.js, asyncio), threads are not held idle waiting for I/O. A slow downstream does not consume a thread — it consumes a callback slot, which is much cheaper. Reduces the blast radius of downstream slowness.

5. **Fallback responses**: B should have a defined degraded response when C is unavailable. Rather than blocking indefinitely, B returns a cached value, a default, or a partial response. This allows A to continue functioning even when C is fully down.


**How to think through this:**
1. Identify the failure mode: synchronous call chains mean each service's timeout is bounded by its slowest dependency. When C slows down, B fills up waiting, then A fills up waiting.
2. This is a **cascade failure** — the failure propagates upstream because services are tightly coupled via synchronous calls with no failure isolation.
3. Prevention requires decoupling: circuit breakers stop calling a known-failed service, bulkheads limit how many threads can wait for a slow dependency, and timeouts prevent indefinite blocking.

**Key takeaway:** Cascading failures are not caused by the failing service — they are caused by the absence of isolation patterns in the services that depend on it; every synchronous call without a circuit breaker and timeout is a potential chain in a cascade.

</details>

> 📖 **Theory:** [Cascade Failure](./12_microservices/theory.md)

---

### Q89 · [Design] · `production-hot-partition-cassandra`

> **Your on-call gets paged: one Cassandra node is at 95% CPU while others are at 15%. You suspect a hot partition. How do you confirm this, mitigate immediately, and fix the root cause?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Step 1 — Confirm it is a hot partition (not a node hardware issue):**

Run `nodetool tpstats` on the hot node — compare thread pool utilisation vs healthy nodes. Then run `nodetool cfstats <keyspace>.<table>` on the hot node and compare read/write counts per table against other nodes. If one table shows 10x more operations on the hot node, the partition key for that table is suspect.

Use `nodetool toppartitions <keyspace> <table> 10000 10` to list the top partitions by read/write count over a sample window. This directly identifies which partition key value is receiving disproportionate traffic.

Cross-reference with application APM (Datadog, Honeycomb): find which application queries are targeting the hot node's token range and which partition key values appear in the hot queries.

**Step 2 — Immediate mitigation:**

- **Add a Redis cache in front of the hot partition key**: if the hot key is read-heavy (e.g., a viral item, a top user), cache the result in Redis with a short TTL. This absorbs the read traffic before it reaches Cassandra.
- **Rate-limit or throttle the endpoint hitting the hot key**: if it is an API endpoint, apply rate limiting to reduce the request volume temporarily while the fix is deployed.
- **If write-heavy**: route writes through a queue (Kafka) and have consumers write at a controlled, throttled rate. This smooths burst writes.
- **Do not restart the node** — it will rejoin with the same token assignment and immediately become hot again.

**Step 3 — Fix the root cause:**

- **Salted partition keys**: append a bucket suffix to the partition key — `item_id#<bucket>` where bucket = `hash(request_id) % N`. Writes distribute across N partitions. Reads must scatter-gather across all N buckets.
- **Redesign the partition key**: if the hot key is a date (write hotspot) or a low-cardinality value, redesign the schema. Use `(date, user_id)` instead of `(date)` alone to distribute writes.
- **Move the hot entity to a dedicated keyspace / table**: create a "celebrity items" table with a different schema specifically optimised for high-traffic entities. Route those entities there at the application layer.
- **Add virtual nodes (vnodes)** if not already enabled: ensures more even distribution as token ranges are subdivided.


**How to think through this:**
1. Confirm the diagnosis: check Cassandra metrics for which partition key is generating the hot node. A hot partition means one partition key is responsible for a disproportionate share of requests.
2. Immediate mitigation: add caching in front of the hot partition to reduce Cassandra load; or if writes are the problem, add an application-side buffer.
3. Root cause fix: the shard key has low cardinality or temporal skew — redesign the partition key to include a bucket suffix (e.g., `user_id + bucket`) to distribute load.

**Key takeaway:** Confirming a hot partition takes 5 minutes with the right Cassandra tools — the mitigation is always to absorb traffic elsewhere, and the fix is always a partition key redesign.

</details>

> 📖 **Theory:** [Cassandra Hot Partition](./05_databases/theory.md)

---

### Q90 · [Design] · `production-url-shortener`

> **Design a URL shortener (like bit.ly). Cover: encoding scheme, database choice, read/write ratio, caching strategy, and how you handle 1 billion redirects/day.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Scale context:** 1 billion redirects/day = ~11,600 redirects/second. Writes (URL creation) are far fewer — assume 1M new URLs/day = ~12 writes/second. This is a read-heavy system with a ~1000:1 read:write ratio.

**Encoding scheme:**
Generate a 7-character **base62** code (a-z, A-Z, 0-9) — 62^7 = ~3.5 trillion unique codes. Generation strategies:
- **Random**: generate a random 7-char code, check for collision in the DB. Collision probability is low at small scale but requires a uniqueness check.
- **Counter + base62 encoding**: maintain a global counter (or distributed counter via Redis INCR). Encode the integer in base62. Guaranteed unique, no collision check needed. Risk: sequential codes are predictable (minor security concern).
- **MD5/SHA hash truncation**: hash the long URL, take the first 7 characters. Deterministic — same URL always produces the same short code. Collision probability low but non-zero; retry with a salt on collision.

**Database choice:**
The core data model is simple: `short_code → {long_url, created_at, user_id, click_count}`. This is a key-value lookup.

- **Primary store**: PostgreSQL or MySQL for durability and ACID writes. The write volume (12/sec) is trivial for a relational database.
- **Alternatively**: DynamoDB or Cassandra if you want to scale the key-value read path independently.
- **Redis**: the critical caching layer (see below), not the primary store.

**Caching strategy:**
With 11,600 redirects/second, hitting the database for every redirect is expensive and unnecessary. The access pattern follows a Zipf distribution — a small number of short codes receive the vast majority of traffic.

- Cache the top N (e.g., 10M) short_code → long_url mappings in Redis with a TTL of 24 hours.
- A single 64GB Redis instance can hold tens of millions of URL mappings.
- Cache hit ratio target: >99%. The 1% misses that go to the database still amount to ~116/second — easily handled.
- On write (new short URL created), no cache update needed — the first request for the new code populates the cache (lazy loading).

**Handling 1 billion redirects/day:**
- **Read path**: DNS → Load balancer → Stateless redirect service (50+ instances) → Redis cache → (on miss) Database → HTTP 301/302 redirect
- **Stateless redirect servers**: each instance simply looks up the code in Redis and returns a redirect. Horizontally scalable to any volume.
- **HTTP 301 vs 302**: 301 is permanent (browsers cache it — reduces future requests to our service), 302 is temporary (we see every click, useful for analytics). For analytics, use 302.
- **Click counting**: do not write to the database on every redirect. Emit a click event to Kafka; a separate consumer aggregates counts and writes to the database in batches.

**How to think through this:**
1. Identify the read:write ratio first — it determines that caching is the most important architectural decision.
2. The redirect service must be stateless and horizontally scalable.
3. Avoid synchronous writes on the hot redirect path — move analytics to async.

**Key takeaway:** A URL shortener at scale is fundamentally a caching problem — the database is write-once-read-many per URL, and an in-memory cache can serve >99% of traffic without touching the database.

</details>

> 📖 **Theory:** [URL Shortener](./22_case_studies/theory.md)

## 🧠 Tier 5 — Critical Thinking

---

### Q91 · [Design] · `design-twitter-feed`

> **Design Twitter's home feed. A user follows 500 accounts. Each account posts 10 tweets/day. The user has 50K followers. Choose fan-out-on-write or fan-out-on-read. Show the data model and the tradeoff that drives your choice.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Back-of-envelope:**
- User follows 500 accounts × 10 tweets/day = 5,000 new tweets/day in their feed = ~0.06 new tweets/second
- User has 50K followers → each tweet this user posts triggers 50K fan-out writes
- At 10 tweets/day × 50K followers = 500K writes/day per user to fan-out feeds
- At Twitter scale with 200M active users posting: fan-out write volume is massive but manageable with the hybrid approach

**Data model:**

```
tweets table:
  tweet_id    BIGINT (Snowflake ID — time-sortable)
  user_id     BIGINT
  content     TEXT (max 280 chars)
  created_at  TIMESTAMP
  media_ids   ARRAY[BIGINT]

follows table:
  follower_id  BIGINT
  followee_id  BIGINT
  PRIMARY KEY (follower_id, followee_id)

feed_cache (Redis sorted set per user):
  KEY:   feed:{user_id}
  SCORE: tweet_id (Snowflake — encodes time, sortable)
  VALUE: tweet_id
  → Store only tweet IDs, not full content (hydrate at read time)
  → Keep last 800 tweet IDs per user (Twitter's documented approach)
```

**Choice: fan-out-on-write (push) with celebrity exception**

For regular users (< 1M followers), use fan-out on write:
- On post: look up all followers from the `follows` table → write tweet_id into each follower's `feed:{user_id}` sorted set in Redis via background workers (Kafka consumers)
- Feed read: fetch top N tweet IDs from sorted set → batch-fetch tweet content from tweets cache

For celebrity accounts (> 1M followers, or configurable threshold):
- Do NOT fan-out on write — 1M+ Redis writes per tweet is too expensive
- On feed read: fetch the user's pre-computed feed from Redis → also fetch the last N tweets from each celebrity the user follows → merge and sort by tweet_id in application memory

**The tradeoff that drives this choice:**
The core tradeoff is **write amplification vs read complexity**.

Fan-out on write: write cost is O(followers) per post. For celebrities, this is unacceptably high. But for regular users with ~500 followers, the write cost is trivial and reads are O(1) — just read the pre-built sorted set.

Fan-out on read: read cost is O(following_count) per feed load. A user following 500 accounts triggers 500 lookups per feed view. At 200M daily active users each checking their feed 10+ times/day, this is 1 trillion lookups/day — untenable.

The hybrid solves both: regular users get O(1) reads (pre-built feeds), celebrity writes stay bounded (read-time merge for the small number of celebrities any user follows).


**How to think through this:**
1. Start with back-of-envelope: how many feed writes per second does fan-out-on-write require? How many reads does fan-out-on-read require? The answer determines which is cheaper at scale.
2. Fan-out-on-write: precompute each user's feed at post time. Reads are O(1) but writes are O(followers) — great for reads, expensive for celebrity accounts with millions of followers.
3. Fan-out-on-read: compute the feed at read time by querying all followed accounts. Writes are O(1) but reads are expensive. The hybrid approach: fan-out for regular users, fan-on-read for celebrities.

**Key takeaway:** The fan-out choice is driven by the asymmetry in follower counts — the hybrid approach acknowledges that a single strategy cannot be optimal for both celebrities and regular users simultaneously.

</details>

> 📖 **Theory:** [Social Feed Design](./21_real_time_systems/theory.md)

---

### Q92 · [Design] · `design-rate-limiter-service`

> **Design a distributed rate limiter that enforces per-user limits across 50 API servers. Cover: algorithm choice, where state is stored, how servers synchronise, and what happens if Redis goes down.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Algorithm choice: sliding window log or token bucket**

- **Fixed window counter** (`INCR` + `EXPIRE` per minute): simple, O(1) per check, but allows burst at window boundaries (user can send 2x the limit in a 1-second window spanning two minutes).
- **Sliding window counter**: uses two fixed windows weighted by the fraction of time elapsed. Approximates sliding window with O(1) space and minimal Redis operations. Good balance.
- **Token bucket**: most natural for API rate limiting. A bucket holds up to N tokens; tokens refill at rate R/second. Each request consumes one token. Allows burst up to bucket capacity, then enforces average rate. Requires storing `{tokens, last_refill_time}` per user.
- **Choice: token bucket with Redis** — it models real API usage patterns best (allows short bursts, enforces sustained limits). Implemented with a Lua script for atomic read-modify-write.

**Where state is stored:**
Redis is the single source of truth for rate limit state. The rate limiter state for user `u` is stored as:

```
KEY: ratelimit:{user_id}
HASH fields:
  tokens:         float (current token count)
  last_refill:    UNIX timestamp (milliseconds)
TTL: set to max refill time (e.g., 2x window)
```

A single Lua script atomically:
1. Reads `tokens` and `last_refill`
2. Computes tokens to add since `last_refill` (= elapsed_time × refill_rate, capped at max)
3. If remaining tokens >= 1: decrements and allows. Returns remaining count.
4. If tokens < 1: denies. Returns retry-after time.

The Lua script executes atomically on a single Redis node — no race conditions.

**How 50 API servers synchronise:**
All 50 servers call the same Redis cluster for every rate limit check. There is no local state on the API servers. This centralises enforcement:
- Use Redis Cluster with 3+ shards for throughput. User rate limit keys are distributed across shards by key hash.
- Each rate limit check = one Redis round trip (~0.5ms). At 50K req/sec total, this is 50K Redis operations/sec — well within Redis capacity (1M+ ops/sec).
- Alternatively: use Redis pipeline to batch multiple checks, reducing round trips.

**Approximate counting with local counters (optional optimisation):**
For very high throughput, each server maintains a local in-memory counter and syncs to Redis every 100ms. This reduces Redis load by 100x at the cost of slightly inaccurate limits (a user might exceed the limit by up to `N_servers × local_increment` during the sync window). Acceptable for non-financial rate limiting.

**What happens if Redis goes down:**

Option A — **Fail open** (allow all requests): Redis unavailable → no rate limiting → serve traffic. Risk: a user or attacker can send unlimited traffic during the outage. Acceptable for non-security-critical limits (UX throttling).

Option B — **Fail closed** (reject all requests): Redis unavailable → return 429 for all requests. Risk: the rate limiter outage causes a full service outage. Unacceptable for most services.

Option C — **Fallback to local rate limiting**: each API server maintains a local token bucket per user. On Redis failure, enforce a conservative local limit (e.g., 10% of the global limit). This degrades gracefully — limiting is less accurate but traffic still flows. Resume Redis-based enforcement when Redis recovers. **This is the recommended approach.**

**Circuit breaker on the Redis call**: wrap the Redis rate limit check in a circuit breaker. If Redis is consistently timing out, open the circuit and fall back to local limiting. Close the circuit when Redis recovers (probe with health checks).


**How to think through this:**
1. The core challenge: rate limiting state (request counts) must be consistent across all 50 API servers — each server cannot maintain its own local state.
2. Choose an algorithm: sliding window log is most accurate but memory-intensive; token bucket is efficient and handles bursts well; fixed window is simplest but allows burst at window boundaries.
3. Store state in Redis (shared across all servers): the rate limit counter for each user lives in Redis, and each API server atomically increments it using a Lua script or INCR + EXPIRE.

**Key takeaway:** A distributed rate limiter's reliability depends on the fallback strategy when its state store fails — the right answer for most services is graceful degradation to local limiting, not hard failure.

</details>

> 📖 **Theory:** [Rate Limiter Design](./11_scalability_patterns/theory.md)

---

### Q93 · [Design] · `design-distributed-cache`

> **Design a distributed in-memory cache system (think Redis Cluster). Cover: data partitioning, replication, what happens on node failure, and consistency guarantees you can offer.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Data partitioning — consistent hashing with hash slots:**

Divide the key space into **16,384 hash slots** (Redis Cluster's approach). Each key is hashed: `slot = CRC16(key) % 16384`. Slots are distributed across nodes — e.g., with 6 nodes, each owns ~2730 slots. Adding or removing a node means migrating only the affected slot range.

Hash tags `{user_id}` allow related keys to land on the same slot (and thus the same node), enabling multi-key operations on co-located data.

**Replication:**

Each node (primary) has one or more **replica nodes** that receive asynchronous replication of writes. The standard configuration is 1 primary + 1 replica per shard (6 nodes for 3 shards).

Replication is asynchronous: the primary acknowledges the write before the replica applies it. This gives **eventual consistency** — a very brief window exists where the primary has the write and the replica does not.

For stronger durability: use `WAIT N T` (wait for N replicas to acknowledge within T milliseconds) on critical writes. This converts individual writes to semi-synchronous.

**Node failure handling:**

When a primary node fails:
1. Replicas detect failure via gossip protocol (each node pings others; missing heartbeats trigger failure detection).
2. After a configurable timeout (`cluster-node-timeout`, default 15s), the cluster marks the node as failed.
3. The replica for the failed primary initiates a **failover election** via the RAFT-like Cluster protocol. It requests votes from other primaries. If it gets a majority, it promotes itself to primary.
4. The cluster updates the slot ownership table. Clients (which maintain a copy of the slot map) reconnect to the new primary.
5. During the election window (typically a few seconds), writes to the affected slots return errors. Clients must retry.

If both a primary and its only replica fail simultaneously, the slots owned by those nodes become unavailable. The cluster can be configured to stop serving all traffic (`cluster-require-full-coverage yes`) or to continue serving available slots (`no`).

**Consistency guarantees:**

- **Within a single key**: reads and writes to the same key go to the same shard (the shard is the consistency boundary). Redis provides strong consistency within a single node — operations are single-threaded.
- **Across keys on different shards**: no cross-shard atomicity. Multi-key operations (MGET, transactions) only work if all keys are on the same shard (use hash tags).
- **On failover**: asynchronous replication means acknowledged writes may be lost if the primary fails before replicating. Replication lag is typically under 100ms. This is the **at-most-once** window — a small number of writes may be lost on primary failure.
- **Reads from replicas** (READONLY mode): you can read from replicas for lower latency / load distribution, but you may read stale data. Opt-in per connection.

**Summary of guarantees:**
- Single-node operations: strongly consistent (serialised)
- Cross-node operations: no atomicity
- Writes: at-most-once durability (async replication)
- Optional semi-sync with `WAIT` for stronger durability at latency cost


**How to think through this:**
1. A distributed cache needs to solve three problems: how to partition data across nodes, how to handle node failures without losing data, and what consistency guarantee to offer.
2. Data partitioning: consistent hashing minimizes key remapping when nodes are added/removed — each node owns a range of the hash ring.
3. Replication handles node failure: each key is stored on N nodes (primary + replicas). The tradeoff is consistency vs availability: wait for all replicas (strong) or one (eventual).

**Key takeaway:** Distributed cache design is fundamentally about accepting asynchronous replication for performance — the consistency guarantees are strong within a shard but best-effort across shards and across failure windows.

</details>

> 📖 **Theory:** [Distributed Cache Design](./06_caching/theory.md)

---

### Q94 · [Critical] · `debug-p99-latency-spikes`

> **Your API has consistent p50=10ms but p99=800ms. This has been true for 3 weeks. Average CPU and memory are normal. What are the four most likely causes and how would you diagnose each?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The pattern — stable p50, high p99, normal average CPU/memory, persisting for weeks — rules out traffic spikes and suggests a structural issue that affects a small percentage of requests consistently.

**Cause 1: Garbage collection pauses**

GC pauses stop all threads for 50–300ms. They occur periodically — roughly 1–5% of request windows. This maps perfectly to a high p99 with normal p50.

Diagnosis:
- Enable GC logging: `-Xlog:gc*` (JVM) or `GODEBUG=gctrace=1` (Go)
- Correlate GC pause timestamps with the p99 spikes in your APM (Datadog, Jaeger traces)
- Check heap utilisation: if heap is consistently >70%, GC is running frequently
- Fix: tune heap size, switch to G1GC or ZGC (JVM), reduce allocation rate, switch to slab allocators

**Cause 2: Database connection pool exhaustion / lock contention**

When all connections in the pool are in use, incoming requests queue. The queue wait time is invisible to the database but shows up in end-to-end latency. p50 is fast because most requests get a connection immediately; p99 represents the requests that had to wait.

Diagnosis:
- Check connection pool metrics: `pool.waiting_requests`, `pool.idle_connections` in your metrics
- Check `pg_stat_activity` for `waiting` connections (PostgreSQL) or lock wait metrics in MySQL
- Set connection pool logging to verbose and look for "waiting for connection" log entries
- Correlate with traffic patterns: does p99 worsen under load?
- Fix: increase pool size (carefully — too large causes database connection exhaustion), add read replicas, optimise slow queries that hold connections longer

**Cause 3: Downstream service p99 propagating upstream**

Your service calls an external service (database, cache, microservice). That external service has its own p99 spike. You are inheriting it.

Diagnosis:
- Instrument every downstream call with a span (distributed tracing — Jaeger, Zipkin, Honeycomb)
- Look at the p99 trace: which span is consuming the 800ms? Database call? External API call? Cache miss?
- Check the downstream service's own p99 metrics independently
- Fix: add caching for the slow downstream call, set a timeout shorter than your SLA, use a fallback

**Cause 4: Thread contention / synchronised code block**

A synchronized block, mutex, or `ReentrantLock` in your application code serialises a small number of requests. The majority complete without contention (fast); the ones that must wait for the lock are delayed.

Diagnosis:
- Take a thread dump or CPU profiler snapshot during a p99 spike
- Look for threads in `BLOCKED` or `WAITING` state
- In Go: `pprof` mutex contention profile (`go tool pprof -mutex`)
- In Java: `jstack` or async-profiler flame graph
- Look for hot lock paths — often in logging, metric emission, or shared caches
- Fix: eliminate the lock (immutable data structures, lock-free algorithms), reduce critical section size, use per-thread state instead of shared state

**Structured diagnostic process:**
1. Add distributed tracing if not present — you cannot debug p99 without span-level breakdown
2. Identify which span within the 800ms traces is slow
3. Cross-reference with GC logs, connection pool metrics, and thread dumps
4. Fix the root cause in the slowest span first


**How to think through this:**
1. p50=10ms but p99=800ms means 99% of requests are fast but 1% take 80x longer — average metrics hide this completely. p99 affects 1 in 100 users, which at scale is significant.
2. Common causes of high tail latency without high average: garbage collection pauses, lock contention, slow external calls on some code paths, or database queries hitting an unindexed path occasionally.
3. Diagnose by looking at the outliers, not the average: distributed tracing shows which service/query is slow for the affected 1%, not the fast 99%.

**Key takeaway:** A stable, structural p99 spike with normal averages is almost always caused by GC pauses, lock contention, or a downstream dependency — distributed tracing is the fastest path to identifying which one.

</details>

> 📖 **Theory:** [Diagnosing Latency](./14_observability/theory.md)

---

### Q95 · [Critical] · `debug-replica-lag`

> **Your database replica is falling further behind the primary every hour. It started at 5 seconds lag, now it is 2 minutes and growing. The primary has normal load. Average CPU on the replica is 40%. What are the four likely causes and how do you fix each?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Growing lag with normal primary load and low replica CPU means the replica can process work, but the rate of incoming changes exceeds its replay speed. The bottleneck is not raw compute — it is replay throughput.

**Cause 1: Single-threaded replication replay**

PostgreSQL (before parallel logical replication) and older MySQL configurations apply the replication log serially, one operation at a time. The primary can execute writes with many concurrent threads; the replica applies them one by one. Under sustained write load, the serial replay cannot keep up.

Diagnosis: Check `pg_stat_replication` on primary — look at `sent_lsn` vs `replay_lsn` on replica. Check if `max_parallel_apply_workers_per_subscription` is set to 1 (PostgreSQL 16+) or if MySQL `slave_parallel_workers` is 0.

Fix: Enable parallel replication. In PostgreSQL 16+, enable parallel apply. In MySQL: set `slave_parallel_workers = 8` and `slave_parallel_type = LOGICAL_CLOCK`. This allows independent transactions to replay in parallel, matching the primary's write parallelism.

**Cause 2: Long-running transactions on the primary generating large WAL events**

A large batch job (bulk insert of 10M rows, large UPDATE, index rebuild) generates a single massive transaction in the WAL. The replica must apply the entire transaction atomically before it can advance. During this time, lag grows proportionally to the transaction size.

Diagnosis: On the primary, run `SELECT * FROM pg_stat_activity WHERE state = 'active' AND xact_start < now() - interval '60 seconds'` — look for long-running transactions. Check `pg_locks` for long-held locks. Correlate the start of the lag growth with query timing.

Fix: Break large batch operations into smaller transactions (process in chunks of 10K rows). Apply large DDL operations (index creation) using `CREATE INDEX CONCURRENTLY` which generates less WAL contention. Schedule bulk operations during off-peak hours.

**Cause 3: Replica I/O bottleneck (disk write speed)**

The replica's CPU is at 40% but its disk I/O may be saturated. Replication replay is I/O-intensive — the replica writes WAL and then applies it to data files. If the replica is on a lower-tier disk (HDD vs SSD, or a slow EBS volume) than the primary, it will fall behind under sustained write load even with spare CPU.

Diagnosis: Check `iostat -x 1` or CloudWatch `VolumeWriteOps`/`VolumeWriteBytes` on the replica. Compare I/O utilisation on primary vs replica. Look for `await` time (I/O wait) approaching the disk's limits.

Fix: Upgrade replica disk to match primary (same SSD tier, same IOPS provisioning). Ensure replica and primary have equivalent storage performance. On AWS RDS, ensure `gp3` IOPS allocation is the same on replica as primary.

**Cause 4: Lock conflicts on the replica between replay and read queries**

If the replica is serving heavy read traffic simultaneously, long-running read queries can hold shared locks on tables that replication replay needs to write. The replay process must wait for the read to finish. This is a known PostgreSQL issue: `hot_standby_feedback` and `max_standby_streaming_delay` parameters control how long replica waits before cancelling conflicting queries.

Diagnosis: On the replica, check `pg_stat_activity` for queries with high `duration`. Check `pg_locks` for lock conflicts. Look at PostgreSQL logs for `canceling statement due to conflict with recovery` messages — this confirms the pattern but indicates conflicts are being resolved; if `max_standby_streaming_delay` is set high, replay waits silently.

Fix: Set `max_standby_streaming_delay = 30s` (limit how long replay waits for reads). Set `hot_standby_feedback = on` (tells primary not to vacuum away rows still needed by replica reads). Route long analytical queries to a separate read replica or offline analytics store rather than the streaming replica.

**Immediate mitigation while investigating:** Stop non-essential read traffic to the replica to give replay cycles priority. This often stops the lag growth immediately and confirms I/O or lock contention as the cause.


**How to think through this:**
1. Replication lag means the replica is falling behind applying the primary's changes — it receives them but cannot apply them fast enough.
2. Common causes: high write throughput on primary exceeds replica's apply speed; large transactions that block replication; replica on slower hardware; or a long-running query on the replica holding locks.
3. Growing lag (not steady) indicates the replica is consistently behind the primary's write rate — the fix is either reduce primary write volume, optimize replica apply speed, or add more replicas to distribute read load.

**Key takeaway:** Growing replication lag with normal primary load is almost always a replay throughput problem — serial replay, large transactions, I/O limits, or read contention — and parallel replay configuration is the highest-leverage fix to try first.

</details>

> 📖 **Theory:** [Replica Lag Diagnosis](./05_databases/theory.md)

---

### Q96 · [Critical] · `debug-duplicate-messages`

> **Your message queue consumer is processing some messages twice. No errors are logged. The queue has at-least-once delivery semantics. Why is this happening? How do you make the consumer safe to run twice?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Why duplicates happen with at-least-once delivery:**

At-least-once delivery means the broker guarantees a message will be delivered, but may deliver it more than once. Duplicates occur when:

1. **Consumer processes the message but crashes before acknowledging**: the broker does not receive the ACK. After a visibility timeout (SQS default: 30s) or heartbeat timeout (Kafka), the broker re-delivers the message to the same or another consumer. The first processing completed — the second is a duplicate.

2. **Consumer ACKs the message but the ACK is lost in transit**: the broker does not receive the ACK due to a network partition. It re-delivers. Both processings completed successfully.

3. **Consumer takes longer than the visibility timeout to process**: SQS makes the message visible again before the first consumer has finished. A second consumer picks it up. Now two consumers process the same message simultaneously.

4. **Manual offset commit failures (Kafka)**: consumer processes a batch, commits the offset, but the commit fails due to a broker issue. On restart, the consumer re-reads from the last successfully committed offset.

No errors are logged because these are not errors from the consumer's perspective — the consumer simply receives and processes a valid message each time.

**How to make the consumer idempotent (safe to run twice):**

**Idempotency** means applying the same operation multiple times produces the same result as applying it once.

**Strategy 1 — Idempotency key in the database:**
Every message has a unique message ID (SQS `MessageId`, Kafka `offset+partition`). Before processing, check a `processed_messages` table:
```sql
INSERT INTO processed_messages (message_id, processed_at)
VALUES (:id, NOW())
ON CONFLICT (message_id) DO NOTHING
RETURNING message_id;
```
If the INSERT returns a row, process the message. If it returns nothing (conflict), the message was already processed — skip it. The check and the business logic should be wrapped in a transaction.

**Strategy 2 — Natural idempotency in the operation:**
Design operations that are inherently idempotent: `SET balance = X` is idempotent (running twice sets to X both times). `INCREMENT balance BY X` is not idempotent (running twice adds 2X). Wherever possible, replace delta operations with absolute state operations.

**Strategy 3 — Conditional writes:**
Use a version number or `updated_at` timestamp. The consumer's update includes a WHERE clause: `UPDATE orders SET status = 'shipped' WHERE id = :id AND status = 'processing'`. The second execution finds status already `'shipped'` and updates 0 rows — no harm done.

**Strategy 4 — Increase the visibility timeout:**
For SQS, set the visibility timeout to 2–3x the maximum expected processing time. This prevents a slow consumer from causing a re-delivery while still processing. Not a fix for the root cause, but reduces duplicate frequency.

**Fixing the root cause:** audit your consumer's processing time distribution. If p99 processing time (e.g., 45s) exceeds visibility timeout (30s), extend the timeout or call `ChangeMessageVisibility` to extend it dynamically during long processing.


**How to think through this:**
1. At-least-once delivery guarantees a message is delivered — but it does not guarantee it is delivered exactly once. Network retries and consumer restarts can cause re-delivery.
2. The root cause is that the consumer has no memory of which messages it has already processed — so when a message is re-delivered (even without an error), it processes it again.
3. The fix is **idempotent consumers**: before processing a message, check if its message ID has been processed before. Store processed IDs in a database or Redis with a TTL. If already seen, skip.

**Key takeaway:** At-least-once delivery makes duplicates structurally inevitable — the only correct response is to design consumers to be idempotent, not to rely on the queue delivering exactly once.

</details>

> 📖 **Theory:** [Duplicate Messages](./09_message_queues/theory.md)

---

### Q97 · [Design] · `design-decision-monolith-startup`

> **You are the first engineer at a startup. The CTO wants microservices from day one. Make the case for or against, with specific reasoning for a team of 3 engineers shipping an MVP in 3 months.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Recommendation: strongly against microservices. Build a well-structured modular monolith.**

Here is the specific case for a 3-person team with a 3-month MVP deadline:

**The core argument: microservices are an organisational scaling solution, not a technical one.**

Microservices solve two problems: (1) multiple teams deploying independently without blocking each other, and (2) scaling individual components with different resource profiles. With 3 engineers, you have neither problem. There is no inter-team coordination overhead to eliminate. You do not yet know which components will need independent scaling.

**The concrete costs microservices impose on a 3-person team:**

1. **Infrastructure overhead you cannot afford to build**: microservices require Kubernetes (or ECS), service discovery, distributed tracing, centralised logging (ELK/Loki), a service mesh or at minimum HTTP client libraries with retries and circuit breakers, and separate CI/CD pipelines per service. Configuring and maintaining this infrastructure correctly takes weeks of engineering time — time that should be spent on the product.

2. **Distributed systems complexity at exactly the wrong time**: a network call between services can fail. This means every inter-service call needs timeouts, retries, and error handling. In a monolith, a function call either returns or throws — no network failure modes. At MVP stage, you do not want to spend time debugging a service mesh misconfig when you should be talking to users.

3. **The domain model is not stable enough for service boundaries**: the most expensive mistake in microservices is drawing the wrong service boundary. Splitting services along incorrect domain boundaries requires cross-service refactoring — distributed transactions, data migration, API versioning. In a monolith, refactoring a module boundary is a local code change. At MVP stage, you will change your mind about domain boundaries multiple times.

4. **Deployment complexity multiplies**: 5 microservices = 5 Dockerfiles, 5 Kubernetes deployments, 5 sets of environment variables, 5 deployment manifests, 5 services to monitor. One engineer will spend half their time on DevOps, not product.

**What to build instead: a modular monolith with clean internal boundaries.**

Structure the codebase as if it might be split later:
- Clear module/package boundaries: `users/`, `payments/`, `orders/`
- No direct database access across modules (each module owns its tables)
- No circular dependencies between modules
- Define interfaces between modules explicitly

This gives you the option to extract a service later — when you actually have the problem that requires it — without incurring the cost today. Companies like Shopify, Stack Overflow, and Basecamp run at significant scale on well-structured monoliths.

**The only exception:** if a specific component has a fundamentally different technology requirement from day one (e.g., a Python ML inference service alongside a Go API), extract exactly that one service. Keep everything else in the monolith.


**How to think through this:**
1. Evaluate the tradeoff honestly: microservices solve specific problems (independent scaling, independent deployment, team autonomy) but introduce significant overhead.
2. For a 3-engineer startup with a 3-month MVP deadline: the overhead of microservices (separate deployments, service discovery, distributed tracing, network calls, contracts between services) will slow you down more than they help.
3. The right answer is almost always: start monolith, ship the MVP, identify the boundaries that actually need independence based on real usage, then extract services where the pain is real.

**Key takeaway:** Microservices from day one at a 3-person startup is premature optimisation — you are paying the full operational cost of distributed systems before you have the scale or team size to justify it, and you are making the hardest architectural decisions before you understand your domain.

</details>

> 📖 **Theory:** [Startup Architecture](./12_microservices/theory.md#microservices--theory)

---

### Q98 · [Design] · `design-decision-sql-nosql-profiles`

> **You are designing a user profile system. Profiles have 10 fixed fields (name, email) and up to 200 optional attributes that vary by user type (gamer, professional, creator). Choose SQL or NoSQL and justify every aspect of the decision.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Recommendation: PostgreSQL with JSONB for the variable attributes, and a traditional schema for the fixed fields.**

This is not a "SQL vs NoSQL" binary — it is a question of which storage model handles the data shape correctly. The answer is a hybrid that uses PostgreSQL as the single store.

**Why not pure NoSQL (MongoDB or DynamoDB)?**

The fixed fields (name, email, created_at, subscription_tier, etc.) are highly relational. Email uniqueness enforcement, user authentication queries (`WHERE email = :email`), subscription-based filtering — these all benefit from SQL's constraint enforcement and query flexibility. Moving to a document store to get schema flexibility does not justify losing ACID guarantees on identity data.

DynamoDB in particular would require knowing all access patterns upfront. "Get user by email" and "get user by ID" are straightforward. But "find all professional users in Germany with more than 3 years of experience" — a query you will inevitably need for analytics, admin tools, or feature targeting — is painful in DynamoDB and requires either a GSI (Global Secondary Index) or a separate analytics store.

**Why not pure SQL with EAV (Entity-Attribute-Value)?**

One common SQL approach for variable attributes is EAV: a `user_attributes` table with `(user_id, attribute_name, attribute_value)`. This works at small scale but is operationally terrible:
- A single profile read requires joining 200 rows and pivoting in application code
- Querying "find all gamers where rank > Gold" requires a self-join per attribute
- No type enforcement: `attribute_value` is always TEXT

Do not use EAV for this use case.

**Why not 200 nullable columns?**

A users table with 200 optional columns is technically valid in PostgreSQL but is a maintenance and readability disaster. Schema migrations require `ALTER TABLE` on a large table. Most columns are NULL for most users. The schema conveys no useful information about which attributes apply to which user type.

**The correct approach: PostgreSQL with a split schema**

```sql
CREATE TABLE users (
  user_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email         TEXT UNIQUE NOT NULL,
  name          TEXT NOT NULL,
  user_type     TEXT NOT NULL CHECK (user_type IN ('gamer', 'professional', 'creator')),
  created_at    TIMESTAMPTZ DEFAULT now(),
  subscription  TEXT,
  attributes    JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_type  ON users(user_type);
CREATE INDEX idx_users_attrs ON users USING GIN (attributes);
```

The 10 fixed fields get proper columns with constraints, indexes, and types. The 200 variable attributes go into a `JSONB` column.

**Why JSONB specifically:**
- JSONB is stored as binary, not as raw text. Reads are fast.
- GIN indexes on JSONB allow efficient querying: `WHERE attributes @> '{"rank": "Gold"}'`
- You can add `CHECK` constraints on the JSONB if needed
- Schema migrations for new attribute types require no `ALTER TABLE` — just start writing the new key
- PostgreSQL's `jsonb_set`, `->`, `->>` operators allow atomic updates to specific fields

**Query examples that work efficiently:**
```sql
-- Get user by email (indexed)
SELECT * FROM users WHERE email = 'user@example.com';

-- Find all Gamer users with Gold rank or above
SELECT * FROM users
WHERE user_type = 'gamer'
  AND attributes @> '{"rank": "Gold"}';

-- Find professionals in Germany
SELECT * FROM users
WHERE user_type = 'professional'
  AND attributes->>'country' = 'DE';
```

**What you give up:** strict schema enforcement on the attributes. A `gamers` table with explicit columns for `rank`, `platform`, `hours_played` would give you compile-time safety and clearer documentation. If the attribute set for each user type is stable and well-known, typed tables per user type (table inheritance in PostgreSQL) may be cleaner at the cost of more complex queries.

**Scale considerations:** PostgreSQL with JSONB handles hundreds of millions of rows comfortably. The GIN index may need tuning at extreme scale. At that point, you can add a search layer (Elasticsearch) for complex attribute queries while keeping PostgreSQL as the system of record.


**How to think through this:**
1. The access pattern is: 10 fixed fields + up to 200 optional fields that vary by user type. This is a sparse, heterogeneous data structure.
2. SQL with a rigid schema would require either 200 nullable columns (wasteful, hard to query) or an EAV (Entity-Attribute-Value) table (flexible but slow and complex to query).
3. NoSQL (document store like MongoDB) is the natural fit: each user document contains exactly the fields relevant to their type, no nulls, schema-on-read, and easily extended with new field types.

**Key takeaway:** Semi-structured profile data with a fixed core does not require NoSQL — PostgreSQL JSONB provides schema flexibility for variable attributes while preserving relational integrity for identity fields and supporting complex queries without a separate data store.

</details>

> 📖 **Theory:** [User Profiles Design](./05_databases/theory.md)

---

### Q99 · [Design] · `design-notification-100m`

> **Design a notification system for 100M users. Notifications can be: in-app, push (iOS/Android), email, and SMS. A single event can trigger notifications to 10M users simultaneously. Cover: fan-out architecture, delivery guarantees, and how to handle undeliverable notifications.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Scale context:**
- 100M users × avg 10 notifications/day = 1B notifications/day = ~11,600/second baseline
- Fan-out event to 10M users: need to enqueue 10M notification jobs quickly (within seconds to minutes, not hours)
- Channel mix: in-app (cheapest, own infrastructure), push (APNs/FCM, rate limited), email (SES/SendGrid, rate limited), SMS (Twilio, most expensive)

**Architecture overview:**

```
Event Source (payment, follow, post)
        |
        v
  [Event Bus — Kafka]
        |
  [Notification Service]
     - Reads user preferences (which channels, opt-outs)
     - Decides: should user receive this notification?
     - Publishes to per-channel queues
        |
   _____|________________________________________
  |         |              |                    |
[In-app  [Push Queue]  [Email Queue]      [SMS Queue]
 Queue]      |              |                    |
  |    [Push Worker]  [Email Worker]       [SMS Worker]
  |    APNs/FCM       SES/SendGrid         Twilio
  |
[In-app DB: Redis + PostgreSQL]
```

**Fan-out for 10M users:**

A naive approach — Notification Service reads 10M user IDs and enqueues 10M messages synchronously — is too slow and memory-intensive in a single service.

Use **batch fan-out workers**:
1. The triggering event writes a single `broadcast_notification` record: `{event_id, template_id, target_audience: "followers_of:user_X", created_at}`.
2. A **fan-out service** reads this record and queries the audience in batches of 10K users.
3. For each batch, it publishes 10K messages to the channel queues. At 10K messages/batch × 1,000 batches = 10M messages total, spread across ~10 minutes with parallel workers.
4. Priority tiers: time-sensitive notifications (security alerts, OTP) get a high-priority queue with dedicated workers. Bulk notifications (newsletter, "X liked your post") use a standard queue.

**Per-channel workers:**

- **In-app**: store `{user_id, notification_id, content, read: false, created_at}` in Redis (for fast unread count) and PostgreSQL (for durable history). On user open, fetch unread from Redis; mark as read via API.
- **Push (APNs/FCM)**: each worker calls APNs/FCM. Batch up to 500 tokens per request (FCM supports batch). APNs/FCM returns per-token delivery status. Rate: FCM supports ~600K messages/min per project.
- **Email**: batch via SES/SendGrid bulk API. Deduplicate within a time window (do not send 5 emails in 5 minutes to the same user from separate events).
- **SMS**: most expensive ($0.0075/message) — only for high-priority notifications (OTP, fraud alert) after user opt-in.

**Delivery guarantees:**

Use **at-least-once** delivery via Kafka with consumer offset commits after successful delivery. If push delivery fails (APNs/FCM timeout), the message is requeued with exponential backoff.

**Exactly-once** is not achievable across third-party providers. Instead, implement idempotency: each notification has a `notification_id`; workers check a `delivered_notifications` log before sending and record delivery atomically.

**Delivery status pipeline**: APNs/FCM/SES provide delivery callbacks (webhook or polling). Write delivery events back to Kafka → status consumer updates `notification_events` table → used for analytics and debugging.

**Handling undeliverable notifications:**

1. **Invalid push tokens (APNs: 410, FCM: `NotRegistered`)**: the device was unregistered or the app was uninstalled. Remove the token from the user's device registry immediately. Do not retry. This is a common and expected failure.

2. **User has no valid tokens** (all tokens invalidated): fall back to the next preferred channel. Check user notification preferences: if push fails, try in-app. If email is also opted-out, discard.

3. **Rate limiting from APNs/FCM**: back off exponentially. Keep a per-provider rate limiter in the worker. Do not retry bulk notifications aggressively — requeue with delay.

4. **Dead letter queue (DLQ)**: after 3 retry attempts, move to a DLQ. A separate process monitors the DLQ: for high-priority notifications (OTP), alert on-call; for low-priority (likes), discard after TTL.

5. **TTL-based expiry**: most notifications are time-sensitive. A "X liked your post" notification that fails to deliver within 24 hours should be discarded, not delivered days later. Set per-type TTLs on the queue.

6. **Notification inbox as fallback**: all notifications are stored in the in-app inbox regardless of push delivery status. Even if APNs fails, the user sees the notification on next app open.


**How to think through this:**
1. Start with scale: 100M users, multiple notification channels (in-app, push, email, SMS), and a single event triggering up to 10M simultaneous notifications — this is a **fan-out** problem at massive scale.
2. The core architecture is: event → fan-out service → per-channel queues → per-channel workers. Each channel (push, email, SMS) has its own queue and worker pool with different throughput and reliability characteristics.
3. Delivery guarantees differ by channel: in-app is best-effort; push requires tracking delivery receipts; email and SMS have their own provider retry semantics. Design the dead-letter queue and retry logic per channel.

**Key takeaway:** Notification systems at scale require tiered fan-out (batch workers, not synchronous expansion), per-channel queues with independent workers, and a graceful degradation strategy where failed delivery on one channel falls back to another rather than dropping the notification silently.

</details>

> 📖 **Theory:** [Notification System](./21_real_time_systems/theory.md)

---

### Q100 · [Design] · `design-global-cdn`

> **Design a global content delivery system for a video streaming service with 500M users across 6 continents, 10TB of video content added daily, and a requirement that any video starts playing within 2 seconds globally. Cover: storage architecture, edge caching strategy, and how you handle cache misses for new uploads.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Scale context:**
- 500M users × avg 2 hours/day × 5 Mbps average bitrate = ~580 Petabytes/day of egress — entirely served from edge, not origin
- 10TB new content/day: manageable upload pipeline, but requires fast global propagation for new videos
- 2-second start time globally: the video manifest and first 4–8 seconds of content (for 2-second buffer) must be at a nearby edge node

**Storage architecture (three tiers):**

```
[Origin Storage — 3 regions (US, EU, APAC)]
  └── Object store (S3 / GCS): cold master files
      - Original uploaded video (4K, raw)
      - Transcoded variants: 1080p, 720p, 480p, 360p per codec (H.264, AV1)
      - HLS/DASH segment files (.m3u8 manifest + .ts/.m4s chunks)

[Regional Distribution Cache — 15–20 PoPs]
  └── High-capacity SSD cache servers (100TB–1PB per PoP)
      - Full video library cache for top ~20% of content (Zipf distribution)
      - Serves as origin for edge nodes

[Edge Nodes — 200–300 PoPs globally]
  └── Medium-capacity SSD cache (10–50TB per node)
      - Serves <50ms from 90%+ of users
      - Caches popular content for local geography
```

**Transcoding pipeline (for the 10TB/day upload requirement):**

Upload → Object Storage (raw) → Transcoding Queue (Kafka) → Transcoding Workers (GPU fleet, auto-scaling) → Output: HLS segments + manifests stored back in object storage per quality tier → CDN ingestion notification triggers pre-warming

Transcoding time: 4K to all variants typically 2–5 minutes per hour of content. 10TB/day is ~30,000 hours of content assuming 5 Mbps source — peak GPU fleet must process this within the upload window.

**Edge caching strategy:**

- **Content addressing by segment**: HLS splits video into 2–10 second `.ts` or `.m4s` segments with a unique URL per segment. Segment URLs are immutable (content-addressed or versioned). CDN caches aggressively with long TTLs (24h–7 days). Only the manifest `.m3u8` has a short TTL.

- **Cache tiering**: Edge → Regional PoP → Origin. An edge cache miss fetches from the nearest regional PoP (fast, sub-10ms), not from the origin (cross-continent, 100ms+). Regional PoPs serve as the main cache tier; edges hold the hot tail.

- **Pre-warming for popular content**: when a video crosses a virality threshold (view velocity spike detected via streaming analytics), proactively push the first 60 seconds of segments to all regional PoPs and top edge nodes. This is triggered by the recommendation engine (trending algorithm) before users hit the edge.

- **Geo-aware routing**: use Anycast BGP routing — users are routed to the nearest edge PoP by the network layer, without DNS round-trips. Fallback to GeoDNS-based routing.

**Handling cache misses for new uploads (the 2-second constraint):**

New uploads are the hardest case: the content has never been cached and may be requested from any continent within seconds of upload (e.g., a viral tweet shares a newly uploaded video).

Strategy:

1. **Post-upload edge ingestion**: immediately after transcoding completes, the ingestion pipeline pushes the first 30–60 seconds of each quality tier to all 15–20 regional PoPs (not all 300 edge nodes — too expensive for cold content). This takes ~60–120 seconds.

2. **Pull-through caching on first miss**: if a user requests content not yet at their edge node, the edge node fetches from the regional PoP (which has it within 60 seconds of upload). The edge-to-PoP fetch is fast (<10ms latency, high bandwidth). The segment is cached at the edge for subsequent requests.

3. **Adaptive bitrate startup optimisation**: the video player requests the lowest quality tier first (360p — small segments, 200KB). This almost always hits cache even for cold content. The player then upgrades to higher quality as higher-quality segments arrive. This satisfies the 2-second start constraint even on a partial cache hit.

4. **Manifest caching with short TTL**: the `.m3u8` manifest has a 10–30 second TTL so that new segments are discoverable quickly. Segment files themselves have very long TTLs.

5. **Origin shield**: the regional PoP acts as an **origin shield** — all edge cache misses go to the regional PoP, never directly to the origin object store. This prevents the origin from being overwhelmed by a simultaneous cache miss storm on new content across 200 edge nodes.

**Consistency and purge strategy:**

Video content is immutable after transcoding — no cache invalidation needed for content files. Manifests change during live streams; use short TTLs or server-sent events to notify players of manifest updates. For deleted content (DMCA, privacy), send a purge request to all PoPs via the CDN management API. Purge propagation across 300 PoPs takes 10–30 seconds.


**How to think through this:**
1. Start with the scale constraints: 500M users, 6 continents, 10TB new content daily, 2-second start time globally. This requires edge nodes close to users and intelligent cache placement.
2. Edge caching strategy: popular content is cached at edge nodes closest to users. A cache miss at the edge pulls from a regional origin server, which in turn pulls from the global origin. This is a multi-tier cache.
3. The hardest problem is new content: it hasn't been cached yet and may need to start playing within 2 seconds globally. Pre-positioning (pushing new content to edge before requests arrive) is the solution for known popular content.

**Key takeaway:** Global video CDN performance is determined by three decisions: segment-based content addressing for aggressive caching, a tiered PoP hierarchy that keeps the hot content library near every user, and adaptive bitrate startup that begins playback on the cheapest-to-cache quality tier while higher quality loads in the background.

</details>

> 📖 **Theory:** [Global CDN Design](./07_storage_cdn/theory.md#storage--cdn--theory)
