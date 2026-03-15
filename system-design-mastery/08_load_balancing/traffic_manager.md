# The Traffic Manager — Load Balancing From First Principles

> You built something people actually want to use. Congratulations.
> Now twice as many people showed up as your system can handle.
> This is not a bug. This is the problem load balancing solves.

---

## The Problem: One Restaurant, Five Hundred Hungry People

Imagine you open a restaurant. You hire one waiter — call him Server 1.

He's good. He can serve **50 tables** comfortably. On opening night, 50 people show up. Perfect.

Then word gets out.

On Friday night, **500 people** show up. Server 1 is sprinting between tables, forgetting orders, dropping plates. Customers are waiting 45 minutes to get a glass of water. A few give up and leave. Some tell their friends never to come back.

This is your web server during a traffic spike.

```
Friday night without load balancing:

[500 Clients] ──────────────────────────→ [ Server 1 ]
                                              ↑
                                     sweating, dropping requests,
                                     response times climbing to 10s
                                     some requests timing out entirely
```

You have two options:

```
Option A: Make Server 1 impossibly powerful (vertical scaling)
  → Buy a $200,000 machine with 128 cores and 2TB RAM
  → Eventually you hit a physical ceiling
  → Single point of failure: machine dies = everything dies

Option B: Hire more waiters (horizontal scaling + load balancing)
  → Buy 10 normal machines
  → Put someone at the door routing customers to available waiters
  → Cheaper, fault-tolerant, and scales further
```

That "someone at the door" is the **load balancer**.

---

## What a Load Balancer Actually Does

A load balancer sits between your clients and your servers. Clients talk to the load balancer. The load balancer decides which server handles each request.

```
                     ┌─────────────────────────────────────────┐
                     │           Load Balancer                  │
                     │                                         │
  [Client A] ──────→ │  Receives all incoming connections      │──→ [ Server 1 ]
  [Client B] ──────→ │  Decides routing based on algorithm     │──→ [ Server 2 ]
  [Client C] ──────→ │  Monitors server health                 │──→ [ Server 3 ]
  [Client D] ──────→ │  Hides backend topology from clients    │
                     └─────────────────────────────────────────┘
                              single public IP: 203.0.113.1
```

From the outside, your entire system looks like **one server** at one IP address. Clients have no idea three (or thirty) machines are working behind it.

The load balancer gives you three things immediately:

```
1. Capacity         — spread load so no single server drowns
2. Availability     — if one server crashes, route around it
3. Maintainability  — take servers down for updates without downtime
```

---

## Load Balancing Algorithms — How to Decide Who Gets the Next Request

The load balancer needs a strategy. Different situations call for different strategies. Here are the main ones, with analogies for each.

### Round Robin — Take Turns in Order

The simplest strategy. Request 1 goes to Server 1, request 2 to Server 2, request 3 to Server 3, request 4 back to Server 1, and so on.

```
Requests arriving: 1, 2, 3, 4, 5, 6, 7, 8, 9

Round Robin routing:
  Request 1 → Server 1
  Request 2 → Server 2
  Request 3 → Server 3
  Request 4 → Server 1  (back to start)
  Request 5 → Server 2
  Request 6 → Server 3
  ...

Each server gets exactly 1/3 of traffic.
```

**Analogy:** A teacher calling on students in alphabetical order, regardless of who's ready or who needs more time.

**Good for:** Servers that are identical and requests that take roughly the same amount of work.

**Breaks down:** When Server 1 is an old laptop and Server 3 is a beefy new machine — round robin gives them the same load, which isn't fair or efficient.

---

### Weighted Round Robin — Faster Servers Get More Work

Same idea as round robin, but each server gets a "weight" reflecting its capacity. A server with weight 3 gets three requests for every one request the weight-1 server gets.

```
Servers:
  Server 1: weight 1 (small instance, 2 cores)
  Server 2: weight 2 (medium instance, 4 cores)
  Server 3: weight 3 (large instance, 8 cores)

Request distribution in one cycle of 6 requests:
  Request 1 → Server 1
  Request 2 → Server 2
  Request 3 → Server 2
  Request 4 → Server 3
  Request 5 → Server 3
  Request 6 → Server 3
```

**Analogy:** A relay race where the fastest runner gets the most laps.

**Good for:** Heterogeneous fleets where servers have different specs, or when you're gradually rolling out new capacity.

---

### Least Connections — Send to Whoever Has Breathing Room

Instead of taking turns blindly, look at how busy each server currently is and send the next request to whichever has the fewest active connections.

```
Current state:
  Server 1: 45 active connections
  Server 2: 12 active connections  ← next request goes here
  Server 3: 38 active connections

New request arrives → routed to Server 2
```

**Analogy:** Choosing the shortest checkout line at a grocery store. You don't just go to the next register in rotation — you look at who's actually available.

**Good for:** Systems where requests have very different processing times. A file upload might hold a connection for 5 seconds while a health check holds it for 5ms. Least connections naturally balances the actual load, not just the count.

**The catch:** Slightly more overhead — the load balancer must track connection counts across all servers.

---

### IP Hash — Same Client, Same Server (Sticky Routing)

Hash the client's IP address to deterministically pick a server. The same client IP always maps to the same server.

```
Client IP: 192.168.1.100
Hash:      192.168.1.100 → hash → 3847261 % 3 servers → Server 2

Every request from 192.168.1.100 goes to Server 2.
Every request from 192.168.1.200 goes to Server 1 (different hash).
```

**Analogy:** A pharmacy where your prescription is always filled by the same pharmacist who knows your history.

**Good for:** Situations where a client's state lives on a specific server and you can't (or won't) move it. We'll come back to exactly when and why in the Sticky Sessions section.

**The catch:** If Server 2 goes down, all Server 2 clients get reassigned. Also, if most users happen to hash to the same server (rare but possible with skewed IP ranges), you get uneven load.

---

### Random — Just Pick One

Pick a server randomly for each request. Sounds naive, but with a large number of requests the law of large numbers makes this nearly as good as round robin.

```
Incoming requests → pick Server 1, 2, or 3 randomly
After 1,000 requests: each server has roughly 333 requests
After 10,000 requests: distribution is very close to 1/3 each
```

**Good for:** Simple implementations, or as a fallback when you can't track connection state. Some distributed systems use random selection combined with "power of two choices" — pick two random servers and send to whichever has fewer connections. This gives most of the benefit of least-connections with very little overhead.

---

## L4 vs L7 Load Balancing — The Two Layers

This distinction matters enormously in real system design. It comes down to how much the load balancer can "see" about the traffic it's routing.

```
OSI model reminder (simplified):

  Layer 7: Application  — HTTP, headers, URLs, cookies, request body
  Layer 6: Presentation
  Layer 5: Session
  Layer 4: Transport    — TCP/UDP, source IP, destination IP, port numbers
  Layer 3: Network      — IP packets
  Layer 2: Data Link
  Layer 1: Physical
```

### L4 Load Balancing — The Fast, Blind Router

An L4 load balancer operates at the TCP/UDP layer. It sees:
- Source IP and port
- Destination IP and port
- That's it

It doesn't open the packets. It doesn't read HTTP headers. It doesn't know if you're requesting `/api/users` or `/static/logo.png`. It just routes TCP connections.

```
L4 Load Balancer view:

  Incoming connection:
    From: 203.0.113.50:49221
    To:   10.0.0.1:443

  Decision: "I'll forward this TCP stream to Server 2"
  (doesn't know what's inside the stream)
```

**Advantages:**
```
+ Extremely fast — no packet inspection needed
+ Works for any TCP/UDP protocol (HTTP, HTTPS, PostgreSQL, Redis, anything)
+ Very low latency overhead
+ Simple: less that can go wrong
```

**Disadvantages:**
```
- Can't make routing decisions based on content
- Can't do URL-based routing
- Can't inspect or modify HTTP headers
- Can't handle WebSocket upgrades intelligently
```

**Use when:** You need raw throughput and low latency, and your routing logic is simple. Database connection load balancers are often L4. AWS Network Load Balancer (NLB) operates at L4.

---

### L7 Load Balancing — The Smart, Content-Aware Router

An L7 load balancer operates at the HTTP layer. It terminates the TCP connection, reads the full HTTP request, makes a routing decision, then opens a new connection to the backend server.

```
L7 Load Balancer view:

  Incoming HTTP request:
    GET /api/v2/users/42
    Host: api.yourapp.com
    Authorization: Bearer eyJhbGc...
    Cookie: session_id=abc123

  Decision options:
    → Path starts with /api → route to API server pool
    → Path starts with /static → route to CDN or static file server
    → Has Authorization header → route to authenticated server pool
    → Cookie contains A/B test flag → route to experiment server
```

This is what makes L7 powerful: **content-based routing**.

```
Real-world L7 routing example:

  yourapp.com/             → Web server pool (handles React app)
  yourapp.com/api/*        → API server pool (handles business logic)
  yourapp.com/static/*     → Static asset server (or pass to CDN)
  yourapp.com/admin/*      → Admin server (different security group)
  yourapp.com/ws           → WebSocket server pool
  api.yourapp.com          → API server pool (hostname-based routing)
  grpc.yourapp.com         → gRPC server pool
```

**Advantages:**
```
+ URL and path-based routing
+ Header inspection and modification
+ Cookie-based sticky sessions
+ SSL termination (decrypt once at LB, plain HTTP to backends)
+ Request/response manipulation (add headers, gzip, etc.)
+ Better health checks (check HTTP status codes, not just TCP)
+ A/B testing and canary deployments
```

**Disadvantages:**
```
- More CPU overhead (must parse HTTP)
- Higher latency than L4 (connection termination + inspection)
- Only works for HTTP/HTTPS traffic
- More complex, more configuration
```

**Use when:** You're routing HTTP traffic and need intelligent routing based on URLs, headers, or cookies. AWS Application Load Balancer (ALB) operates at L7. Nginx and HAProxy can do both.

---

### Choosing: L4 or L7?

```
┌──────────────────────────────────────────────────────────────┐
│                     Quick Decision Guide                      │
├──────────────────────────────────────────────────────────────┤
│  Need URL-based routing?              → L7                   │
│  Need cookie-based sticky sessions?   → L7                   │
│  Need SSL termination?                → L7 (usually)         │
│  Need A/B testing at routing level?   → L7                   │
│  Need to balance database connections?→ L4                   │
│  Need absolute minimal latency?       → L4                   │
│  Traffic isn't HTTP?                  → L4                   │
│  Handling WebSockets, gRPC?           → L7 (with HTTP/2)     │
└──────────────────────────────────────────────────────────────┘
```

In practice: most web applications use **L7 load balancing** at the edge, and may use L4 internally for database or cache clustering.

---

## Sticky Sessions — When You Need the Same Client to Land on the Same Server

Normally, load balancers treat each request as independent. Request 1 from you might go to Server 2. Request 2 from you might go to Server 3. That's fine if your servers are stateless.

But what if they're not?

### The Problem Story

Imagine an older e-commerce site. The developer stored shopping cart data in server memory — a Python dict, in the process, on Server 1:

```python
# On Server 1, in memory (bad design, but real):
sessions = {
    "user_abc123": {"cart": ["item_1", "item_2"], "total": 89.99}
}
```

Now the user adds a third item. If that request lands on Server 2, Server 2 has no idea what's in the cart. The user sees an empty cart. Chaos.

```
Without sticky sessions (stateful server, bad outcome):

  User adds item 1 → Server 1 (cart: [item_1])
  User adds item 2 → Server 2 (Server 2 doesn't know item_1 exists!)
  User checks cart → Server 3 (cart: ???)
```

Sticky sessions tell the load balancer: "once a user lands on Server X, always send that user to Server X for the duration of their session."

```
With sticky sessions (IP hash or cookie):

  User adds item 1 → Server 1 (cart: [item_1])
  User adds item 2 → Server 1 (cart: [item_1, item_2])
  User checks cart → Server 1 (cart: [item_1, item_2]) ✓
```

### How Sticky Sessions Work

**Method 1: IP Hash** — as described above, hash the client IP to always pick the same server.

**Method 2: Cookie-based affinity** — the load balancer sets a cookie on the first response:
```
Set-Cookie: SERVERID=server2; Path=/; HttpOnly

Now every request from this browser includes:
Cookie: SERVERID=server2

Load balancer reads this cookie and routes to Server 2.
```

### The Real Problem with Sticky Sessions

Sticky sessions fix a symptom, not the disease. The actual problem is that you have stateful servers.

```
Sticky session limitations:
  → Server 2 dies → all Server 2 users lose their sessions instantly
  → Traffic becomes unbalanced (some users are "heavy" users)
  → Can't scale down gracefully (can't remove a server with active sessions)
  → Makes deployments harder (must drain users from servers before restart)
```

The right answer is: **make your servers stateless**.

Move session state out of server memory and into a shared store:

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Server 1   │    │   Server 2   │    │   Server 3   │
│              │    │              │    │              │
│  No local    │    │  No local    │    │  No local    │
│  session     │    │  session     │    │  session     │
│  state       │    │  state       │    │  state       │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌──────▼───────┐
                    │    Redis     │
                    │              │
                    │  session:    │
                    │  user_abc123 │
                    │  → cart data │
                    └──────────────┘
```

Now any server can handle any request. Sticky sessions become unnecessary. This is the architectural rule behind "share nothing" server design.

---

## Health Checks — How the Load Balancer Knows a Server Is Down

A load balancer routing traffic to a dead server is worse than no load balancer at all. Health checks are how the LB avoids this.

### Active Health Checks — Regular Pings

The load balancer proactively sends health check requests to every server on a schedule:

```
Every 10 seconds, Load Balancer sends:
  GET /health → Server 1  (expects: HTTP 200)
  GET /health → Server 2  (expects: HTTP 200)
  GET /health → Server 3  (expects: HTTP 200)

Server 2 returns HTTP 500 → marked as unhealthy
Server 2 removed from rotation → traffic goes to Server 1 and 3
```

A good `/health` endpoint checks everything the service depends on:

```python
@app.route("/health")
def health():
    checks = {}
    try:
        db.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "down"
        return jsonify(checks), 500

    try:
        redis_client.ping()
        checks["cache"] = "ok"
    except Exception:
        checks["cache"] = "down"
        return jsonify(checks), 500

    return jsonify(checks), 200   # {"database": "ok", "cache": "ok"}
```

### Passive Health Checks — Observing Failures in Real Traffic

Instead of sending explicit health pings, passive health checks let the load balancer observe real request outcomes. If Server 2 returns 5 consecutive errors or times out 3 times in a row, it gets marked unhealthy and pulled from rotation.

```
Passive monitoring:

  Request to Server 2 → response: HTTP 200 ✓
  Request to Server 2 → response: HTTP 200 ✓
  Request to Server 2 → response: timeout  ✗
  Request to Server 2 → response: timeout  ✗
  Request to Server 2 → response: timeout  ✗

  → Server 2 marked unhealthy, removed from rotation
  → After 30 seconds, try a health check ping
  → If passes, re-add to rotation
```

Both methods are often used together: active checks catch problems between requests, passive checks catch issues that active checks miss (the server passes the ping but crashes on real work).

### Graceful Shutdown — Don't Cut the Cord

When you need to take a server down for a deployment or maintenance, you don't want to kill it mid-request. The right pattern is:

```
Graceful shutdown sequence:

Step 1: Signal the load balancer to stop sending NEW requests to this server
        (set server to "draining" state)

Step 2: Wait for all IN-FLIGHT requests to complete
        (could take a few seconds)

Step 3: Server process exits cleanly

Step 4: Deploy new version, restart server

Step 5: Server passes health checks

Step 6: Load balancer re-adds server to rotation
```

Kubernetes does this automatically with rolling deployments. In AWS, ALB supports "deregistration delay" (default 300 seconds) for exactly this purpose.

---

## High Availability for the Load Balancer Itself

You've added a load balancer to avoid a single point of failure. But now the load balancer is a single point of failure.

What happens when it goes down?

### Active-Passive Load Balancer Pair

The standard solution: run two load balancers. One is active, one is standby. A floating virtual IP (VIP) is assigned to the active one.

```
Normal operation:
                            ┌─────────────────┐
Virtual IP ─────────────→  │  LB Primary     │──→ Servers
203.0.113.1                 │  (ACTIVE)       │
                            └─────────────────┘
                            ┌─────────────────┐
                            │  LB Secondary   │
                            │  (STANDBY)      │
                            └─────────────────┘
                            Primary and Secondary heartbeat each other

Failover (primary fails):
                            ┌─────────────────┐
                            │  LB Primary     │  ← DEAD
                            └─────────────────┘
                            ┌─────────────────┐
Virtual IP ─────────────→  │  LB Secondary   │──→ Servers
203.0.113.1                 │  (NOW ACTIVE)   │
(same IP, new machine)      └─────────────────┘
```

Clients never know anything happened — the VIP moved, but the IP they're connecting to is the same. This is implemented using protocols like VRRP (Virtual Router Redundancy Protocol) or keepalived on Linux.

### DNS Failover

For multi-region setups, DNS can route traffic between geographically separate load balancers:

```
DNS: api.yourapp.com
  → US-East LB: 203.0.113.1  (primary, TTL: 30s)
  → EU-West LB: 203.0.113.2  (backup)

US-East data center has an outage:
  → DNS health check detects US-East is down
  → DNS record updated to point only to EU-West
  → Within ~30 seconds (TTL), all clients route to EU-West
```

The TTL matters here: a 300-second TTL means 5 minutes of disruption during failover. Reduce it for faster recovery, but it increases DNS server load.

### Anycast

Anycast is a routing technique where multiple servers share the same IP address, and the network automatically routes each client to the nearest one. This is how Cloudflare, Google DNS (8.8.8.8), and large CDN networks work.

```
IP: 1.1.1.1 (Cloudflare DNS)
  → Server in London    ← UK users route here
  → Server in New York  ← US East users route here
  → Server in Singapore ← SEA users route here
  → Server in Sydney    ← AU users route here

All share the same IP. BGP routing protocol handles selection.
If the London server goes down, UK users automatically reroute to Frankfurt.
```

---

## Real-World Load Balancers

A quick reference for what you'll encounter in the industry:

```
Nginx         Open source. Can do L4 and L7. Used as reverse proxy,
              load balancer, and static file server. Very common.
              Config is declarative (nginx.conf). Handles millions
              of connections with low memory footprint.

HAProxy       Open source. Purpose-built for load balancing.
              High performance L4 and L7. Used extensively for
              TCP load balancing, often chosen over Nginx when
              maximum LB throughput is the priority.

AWS ALB       Amazon Application Load Balancer. Managed L7 LB.
(Application  Supports URL routing, WebSockets, HTTP/2, Lambda
Load Balancer)targets. Pay-per-use. No infrastructure to manage.

AWS NLB       Amazon Network Load Balancer. Managed L4 LB.
(Network LB)  Static IP address, handles millions of RPS with
              ultra-low latency. Good for non-HTTP TCP workloads.

Cloudflare LB Runs on top of Cloudflare's global Anycast network.
              Built-in DDoS protection, global health checks,
              geo-steering. More expensive, but the edge presence
              is unmatched.
```

---

## The Mental Models to Carry Forward

```
1. The load balancer is not magic. It's a router with a health monitor.
   Its value is: capacity + availability + maintainability.

2. L4 is fast and dumb. L7 is smart and slightly slower.
   Most web apps need L7. Most database clusters need L4.

3. Sticky sessions are a smell. They mean your servers aren't
   stateless. The fix is moving state to a shared store (Redis),
   not papering over it with affinity routing.

4. Your load balancer must also be highly available.
   Active-passive pairs with a floating VIP are the standard.

5. Health checks are the immune system of your load balancing setup.
   A /health endpoint that doesn't check the database is lying to you.
```

---

## Mini Exercises

**1.** You have 3 servers: Server A (8 cores), Server B (4 cores), Server C (4 cores).
You're using round robin. Latency is climbing on Server A. Why, and what algorithm should you switch to?

**2.** A user reports that they add items to their cart and they disappear. You're using round robin.
What's the most likely cause? What are two fixes — one quick (but fragile), one correct?

**3.** Your app serves `/api/*` traffic (dynamic, needs authentication) and `/static/*`
traffic (images, JS, CSS). How would you design the L7 routing rules to handle these
differently? Which pool would you route each to?

**4.** The load balancer itself is running on a single server. Your CTO asks: "What's our
single point of failure?" How do you explain the risk, and what do you propose?

**5.** An engineer proposes: "Let's set our DNS TTL to 1 second so we can do instant
failover." What's the tradeoff they're ignoring?

---

## Navigation

| | |
|---|---|
| Previous | [07 — Storage & CDN](../07_storage_cdn/theory.md) |
| Next | [09 — Message Queues](../09_message_queues/why_queues_exist.md) |
| Home | [README.md](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
