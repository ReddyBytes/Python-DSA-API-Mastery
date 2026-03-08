# 🌐 Networking Fundamentals

> Every system design decision involving services, APIs, or data transfer
> depends on networking. Understanding the underlying protocols helps you
> make better decisions about latency, reliability, and security.

---

## 📋 Contents

```
1.  The OSI and TCP/IP models
2.  IP addressing and routing
3.  TCP — reliable, ordered delivery
4.  UDP — fast, unreliable delivery
5.  DNS — translating names to addresses
6.  HTTP/1.1 — the web protocol
7.  HTTP/2 — multiplexing and headers compression
8.  HTTP/3 / QUIC — UDP-based reliability
9.  TLS / HTTPS — encrypted transport
10. WebSockets — persistent bidirectional
11. Server-Sent Events (SSE)
12. gRPC and Protocol Buffers
13. Load balancer networking (L4 vs L7)
14. CDN networking
15. Network latency and optimization
```

---

## 1. The OSI and TCP/IP Models

```
OSI Model (7 layers)          TCP/IP Model (4 layers)    Examples
─────────────────────────────────────────────────────────────────────
7 Application                 Application                HTTP, DNS, SMTP
6 Presentation                     │                     TLS, encoding
5 Session                          │                     Session mgmt
4 Transport                   Transport                  TCP, UDP
3 Network                     Internet                   IP, ICMP, routing
2 Data Link                   Link                       Ethernet, WiFi, ARP
1 Physical                         │                     Cables, signals

Practical shortcut:
  You mostly care about: IP (Layer 3), TCP/UDP (Layer 4), HTTP (Layer 7)
  Load balancers operate at Layer 4 (TCP) or Layer 7 (HTTP)
```

---

## 2. IP Addressing

```
IPv4: 32-bit address (4 billion unique addresses)
  Format: 192.168.1.100
  Private ranges (not routable on internet):
    10.0.0.0/8      (10.x.x.x)
    172.16.0.0/12   (172.16-31.x.x)
    192.168.0.0/16  (192.168.x.x)
  Loopback: 127.0.0.1 (always your own machine)

IPv6: 128-bit address (340 undecillion unique addresses)
  Format: 2001:0db8:85a3::8a2e:0370:7334
  Loopback: ::1

CIDR notation:
  192.168.1.0/24  → 192.168.1.0 to 192.168.1.255 (256 addresses)
  10.0.0.0/8      → 10.0.0.0 to 10.255.255.255 (16M addresses)
  /24 = 8 host bits = 254 usable hosts

Ports:
  0-1023:    Well-known (HTTP=80, HTTPS=443, SSH=22, DNS=53, MySQL=3306)
  1024-49151: Registered
  49152-65535: Ephemeral (OS assigns for outbound connections)
```

---

## 3. TCP — Reliable, Ordered Delivery

### Three-way handshake
```
Client                         Server
  │─────────── SYN ─────────────→│   "I want to connect"
  │←────── SYN-ACK ──────────────│   "OK, I'm ready"
  │─────────── ACK ─────────────→│   "Let's go"
  │                               │
  │═══════ data flows ═══════════│
  │                               │
  │─────────── FIN ─────────────→│   "I'm done"
  │←─────── FIN-ACK ─────────────│
  │─────────── ACK ─────────────→│

Total: 1.5 RTT to establish, then data flows.
This 3-way handshake is why TCP has higher initial latency than UDP.
```

### TCP guarantees
```
1. Ordered delivery:     packets arrive in sequence
2. Reliable delivery:    lost packets are retransmitted
3. Error detection:      checksum on each segment
4. Flow control:         receiver advertises window size
5. Congestion control:   slow start, AIMD, CUBIC

The price: latency (retransmits, acks) and head-of-line blocking.
```

### TCP Head-of-Line Blocking
```
In TCP, if packet 3 is lost:
  Packet 4, 5, 6 must wait in buffer until 3 is retransmitted.
  Even if 4, 5, 6 arrived fine — delivery is blocked.

Impact: HTTP/1.1 multiplexing (pipelining) abandoned due to this.
Fix: HTTP/2 uses streams, HTTP/3 uses QUIC (UDP-based, no HOL blocking).
```

---

## 4. UDP — Fast, Unreliable Delivery

```
No handshake. No ordering. No retransmission.
Just: send a datagram, hope it arrives.

Why use UDP?
  - Lower latency (no setup, no retransmit wait)
  - Works for loss-tolerant applications

Use cases:
  DNS lookups:         Single request/response, retry at app layer
  Video streaming:     Small glitch < pause for retransmit
  Online games:        Stale position data worthless — just send new one
  QUIC (HTTP/3):       Implements reliability on top of UDP
  VoIP / WebRTC:       Latency > reliability for voice

UDP vs TCP comparison:
  TCP: Reliable, ordered, slower, connection-based
  UDP: Best-effort, unordered, faster, connectionless
```

---

## 5. DNS — Domain Name System

```
Hierarchy:
  Root (.)
    ├── .com (TLD)
    │     └── google.com (authoritative NS)
    │               └── www.google.com → 142.250.64.68
    └── .org
          └── wikipedia.org → 208.80.154.224

Resolution flow:
  1. Check local cache (OS / browser)
  2. Query recursive resolver (usually ISP or 8.8.8.8)
  3. Resolver asks root → TLD → authoritative NS
  4. Returns IP, cached at each level for TTL

Record types:
  A       → hostname to IPv4 address
  AAAA    → hostname to IPv6 address
  CNAME   → alias to another hostname
  MX      → mail server for domain
  TXT     → arbitrary text (SPF, DKIM, verification)
  NS      → nameservers for domain
  SRV     → service location (port, priority, weight)

TTL (Time To Live):
  Controls how long records are cached.
  Low TTL (60s): changes propagate fast, but more DNS traffic
  High TTL (86400s): faster lookups, but changes are slow to propagate
  Before a migration: lower TTL days in advance!

DNS load balancing:
  Round-robin: return multiple A records in rotation
  Geo DNS: return different IPs based on client location
  Health-check DNS: remove unhealthy IPs from rotation
```

---

## 6. HTTP/1.1

```
Stateless request-response protocol over TCP.

Request format:
  GET /api/users HTTP/1.1
  Host: api.example.com
  Accept: application/json
  Authorization: Bearer <token>
  Connection: keep-alive

  [body for POST/PUT/PATCH]

Response format:
  HTTP/1.1 200 OK
  Content-Type: application/json
  Content-Length: 234
  Cache-Control: max-age=3600

  {"users": [...]}

Methods and idempotency:
  GET     → read, idempotent, cacheable
  POST    → create, NOT idempotent, not cacheable
  PUT     → replace, idempotent
  PATCH   → partial update, not necessarily idempotent
  DELETE  → delete, idempotent (delete again = same result)
  HEAD    → like GET but no body (check existence)
  OPTIONS → discover allowed methods (used for CORS)

Status codes:
  2xx  Success:  200 OK, 201 Created, 204 No Content
  3xx  Redirect: 301 Permanent, 302 Temporary, 304 Not Modified
  4xx  Client:   400 Bad Request, 401 Unauth, 403 Forbidden,
                 404 Not Found, 409 Conflict, 429 Too Many Requests
  5xx  Server:   500 Internal Error, 502 Bad Gateway, 503 Unavailable
                 504 Gateway Timeout

HTTP/1.1 limitations:
  - One request at a time per connection (pipelining unreliable)
  - Large headers (sent uncompressed, repeated every request)
  - Head-of-line blocking
  Fix: HTTP/2
```

---

## 7. HTTP/2

```
Improvements over HTTP/1.1:
  1. Multiplexing: multiple requests on ONE TCP connection
     → No more opening 6 parallel connections per browser
     → Requests interleaved as frames

  2. Header compression (HPACK):
     Only send headers that changed since last request
     → Repeated headers like Cookie, User-Agent sent once

  3. Server push:
     Server proactively sends resources before client asks
     "You'll need style.css, here it is" → reduces RTTs

  4. Binary framing:
     Frames instead of text
     → More efficient parsing, less ambiguity

Frame types:
  DATA     → actual request/response body
  HEADERS  → HTTP headers
  SETTINGS → connection configuration
  WINDOW_UPDATE → flow control
  PING     → liveness check
  RST_STREAM → cancel stream

Still has TCP head-of-line blocking:
  Multiplexed streams all share one TCP connection.
  If a TCP packet is lost → all streams wait.
  HTTP/3 solves this.
```

---

## 8. HTTP/3 / QUIC

```
QUIC: Quick UDP Internet Connections
  Built on UDP, implements reliability, ordering, and congestion control
  at the application layer.

Why UDP?
  UDP packets are independent — losing one doesn't block others.
  QUIC implements per-stream ordering (not global).

Advantages over HTTP/2:
  1. No TCP head-of-line blocking (streams truly independent)
  2. Faster connection setup: 0-RTT or 1-RTT (vs TCP 1.5 RTT + TLS 1 RTT)
  3. Connection migration: works across network changes (WiFi → cellular)

Connection setup comparison:
  HTTP/1.1 + TLS 1.2: 3 RTT (TCP 1.5 + TLS 2)
  HTTP/2  + TLS 1.3:  2 RTT (TCP 1.5 + TLS 0.5)
  HTTP/3  + QUIC:     1 RTT (1st connection), 0 RTT (resumed)

Status: ~30% of web traffic uses HTTP/3 (2024)
Support: Chrome, Firefox, Safari, Nginx, Cloudflare, major CDNs
```

---

## 9. TLS / HTTPS

```
TLS (Transport Layer Security) encrypts traffic between client and server.
HTTPS = HTTP + TLS.

TLS 1.3 Handshake (simplified):
  Client → Server: ClientHello (TLS version, ciphers, key share)
  Server → Client: ServerHello + Certificate + key share
  Client verifies certificate with CA
  Both derive session keys
  Encrypted data flows

Key concepts:
  Certificate:   Server's public key + identity, signed by a Certificate Authority
  CA:            Trusted party that vouches for certificate authenticity
  SNI:           Server Name Indication — which domain in the TLS hello
                 (allows multiple certs on one IP)

Certificate types:
  DV (Domain Validated):  just proves you own the domain
  OV (Org Validated):     + verifies the organization
  EV (Extended):          + rigorous legal verification
  Wildcard: *.example.com → valid for any subdomain

HSTS (HTTP Strict Transport Security):
  Server tells browser: "Always use HTTPS for this domain"
  Prevents downgrade attacks

TLS termination in infrastructure:
  Client → (TLS) → Load Balancer → (plain HTTP) → App Servers
  OR
  Client → (TLS) → Load Balancer → (TLS) → App Servers (end-to-end)
```

---

## 10. WebSockets

```
Full-duplex, persistent connection between client and server.
Started as HTTP upgrade:

  GET /ws HTTP/1.1
  Upgrade: websocket
  Connection: Upgrade
  Sec-WebSocket-Key: <base64-key>

  101 Switching Protocols
  Upgrade: websocket
  Sec-WebSocket-Accept: <hash>

After handshake:
  → Both sides can send frames at any time
  → Low overhead (2-10 byte frame header vs full HTTP headers)
  → Persistent connection (no reconnect overhead)

Use cases:
  Chat applications, collaborative editing, live dashboards,
  real-time notifications, multiplayer games, trading terminals

Scaling WebSockets:
  Problem: sticky connections → can't just add servers
  Solution: stateless + pub/sub backend:
    Client → WebSocket server → Redis pub/sub → other servers → their clients

  When user A sends message:
    Server A publishes to Redis channel
    All servers subscribed to that channel → push to their connected clients

WebSocket vs SSE vs polling:
  Polling:    Client repeatedly asks "anything new?"   → wasteful
  Long poll:  Client asks, server holds until data     → better
  SSE:        Server pushes to client (one direction)  → simple
  WebSocket:  Bidirectional                            → full duplex
```

---

## 11. Server-Sent Events (SSE)

```
One-way: server pushes events to client over HTTP.
Client cannot send back (use separate HTTP requests for that).

HTTP response:
  Content-Type: text/event-stream
  Cache-Control: no-cache
  Connection: keep-alive

  data: {"type": "price_update", "symbol": "AAPL", "price": 185.23}

  event: notification
  data: {"message": "Your order was shipped"}
  id: 42

Client (JavaScript):
  const es = new EventSource('/events');
  es.onmessage = (e) => console.log(JSON.parse(e.data));
  es.addEventListener('notification', (e) => handleNotification(e.data));

SSE advantages over WebSockets:
  + Works over standard HTTP (no upgrade)
  + Automatic reconnection built-in
  + Works with HTTP/2 multiplexing
  + Simpler — just HTTP

Use when: server needs to push, client just consumes
  Live feeds, notifications, progress updates, stock tickers
```

---

## 12. gRPC and Protocol Buffers

```
gRPC: Google's RPC framework. Built on HTTP/2.
Protocol Buffers: binary serialization format.

Advantages:
  + Strongly typed (schema enforced)
  + Compact binary encoding (~5-10× smaller than JSON)
  + Code generation in 10+ languages
  + HTTP/2 multiplexing + streaming

Define service in .proto:
  syntax = "proto3";

  service UserService {
    rpc GetUser(GetUserRequest) returns (User) {}
    rpc ListUsers(ListUsersRequest) returns (stream User) {}
    rpc BulkCreate(stream CreateUserRequest) returns (Summary) {}
    rpc Chat(stream Message) returns (stream Message) {}
  }

  message User {
    int64 id = 1;
    string name = 2;
    string email = 3;
    bool is_active = 4;
  }

Stream types:
  Unary:           one request → one response (like HTTP)
  Server streaming: one request → stream of responses
  Client streaming: stream of requests → one response
  Bidirectional:   stream both ways

gRPC vs REST:
  gRPC:
    + Binary (fast), streaming, bidirectional, typed
    - Hard to debug (not human-readable), limited browser support
    Use for: internal service-to-service, high throughput

  REST:
    + Human-readable, universal browser support, simple
    - Text overhead, no native streaming, no type enforcement
    Use for: public APIs, external clients, simplicity
```

---

## 13. Load Balancer Networking: L4 vs L7

```
Layer 4 (Transport) Load Balancer:
  Operates on TCP/UDP.
  Routes based on: source IP, destination IP, port number.
  Does NOT inspect HTTP content.

  Client  ──TCP──→  L4 LB  ──TCP──→  Server
                 (routes by IP/port)

  Pro: fast (no content parsing), handles any TCP protocol
  Con: can't route by URL path, HTTP method, headers, cookie

  Examples: AWS NLB, HAProxy TCP mode

Layer 7 (Application) Load Balancer:
  Operates on HTTP/HTTPS.
  Routes based on: URL path, HTTP method, headers, cookies, body.
  Terminates TLS, re-encrypts (or passes plain HTTP internally).

  Client  ──HTTPS──→  L7 LB  ──HTTP──→  Server
                  (reads HTTP headers, routes by content)

  Rules examples:
    /api/*        → backend API servers
    /static/*     → CDN / object storage
    X-Version: 2  → new server pool (canary deploy)
    Cookie: beta  → beta server pool (A/B testing)

  Pro: smart routing, TLS termination, can add auth/rate limiting
  Con: slower (must parse HTTP), more complex
  Examples: AWS ALB, Nginx, HAProxy HTTP mode

When to use which:
  L4: you don't need HTTP-aware routing, need maximum throughput
  L7: you need URL-based routing, sticky sessions, TLS offload
```

---

## 14. CDN Networking

```
CDN (Content Delivery Network): distributed cache at edge locations.

How it works:
  1. User requests https://example.com/image.jpg
  2. DNS resolves to nearest CDN PoP (Point of Presence)
  3. CDN PoP checks cache:
     HIT:  return cached content, never touch origin
     MISS: fetch from origin, cache with TTL, return to user

CDN benefits:
  + Latency: serve from 20ms away instead of 150ms (US→EU)
  + DDoS protection: absorb traffic at edge
  + Bandwidth: offload origin (99% traffic can be CDN-served)
  + TLS: terminate at edge, warm connections to origin

Content types:
  Static:  always cache (images, JS, CSS, fonts)
  Dynamic: cache selectively (API responses with short TTL)
  Private: never cache (user-specific data — use auth headers)

Cache control headers:
  Cache-Control: public, max-age=86400    → CDN caches 1 day
  Cache-Control: private, max-age=3600   → browser only, not CDN
  Cache-Control: no-cache                → revalidate every time
  Cache-Control: no-store                → never cache
  ETag: "abc123"                         → conditional request validation
  Vary: Accept-Encoding                  → separate cache per encoding

CDN providers: Cloudflare, AWS CloudFront, Fastly, Akamai

Push vs Pull CDN:
  Pull: CDN fetches content from origin on first miss
        Simple, lazy — works for most cases
  Push: You upload content to CDN proactively
        Better for large files, predictable patterns
```

---

## 15. Network Latency and Optimization

```
Latency numbers:
  L1 cache hit:            0.5 ns
  L2 cache hit:            7 ns
  RAM access:              100 ns
  Network (same rack):     5 μs
  SSD random read:         150 μs
  Network (same DC):       500 μs   ← 1 service call
  Network (cross DC, US):  5 ms
  SSD sequential read:     1 ms
  Network (US → EU):       150 ms
  Network (US → Australia):200 ms

Reducing latency:
  1. Move computation closer to data (minimize hops)
  2. Use CDN for static content (edge caching)
  3. HTTP/2 or HTTP/3 (fewer round trips)
  4. Connection pooling (reuse TCP connections)
  5. Persistent connections (avoid 3-way handshake per request)
  6. DNS pre-resolve (prefetch DNS for likely links)
  7. TCP fast open (1-RTT connection on resumed)

Connection pooling:
  Opening TCP connection = ~1 RTT (three-way handshake)
  Opening TLS = additional 1-2 RTT
  With pool: reuse established connections → near-zero setup overhead
  Python: requests.Session, SQLAlchemy pool, Redis connection pool

RTT math:
  Client → LB → App Server → DB → App Server → LB → Client
  = 1 RTT (client→LB) + 1 RTT (app→DB) + 1 RTT (LB→client)
  = 3 RTT total = 3 × 500μs = 1.5ms (same DC)
  = 3 × 150ms = 450ms (transcontinental!)
  → Minimize cross-region hops
```

---

## 🔁 Navigation

| | |
|---|---|
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ← Previous | [00 — Computer Fundamentals](../00_computer_fundamentals/story.md) |
| ➡️ Next | [02 — System Fundamentals](../02_system_fundamentals/theory.md) |
| 🏠 Home | [README.md](../README.md) |
