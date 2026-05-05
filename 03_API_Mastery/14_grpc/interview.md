# 🎯 gRPC — Interview Preparation

> This file prepares you to discuss gRPC like a working engineer.
> Not just definitions — but real-world usage, trade-offs, and production scenarios.

---

# 🔹 Basic Level Questions (0–2 Years)

**Q1: What is gRPC and how does it differ from a typical REST API?**

<details>
<summary>💡 Show Answer</summary>

gRPC is a high-performance RPC framework that uses HTTP/2 as the transport and Protocol Buffers as the wire format, compared to REST which typically uses HTTP/1.1 and JSON. The key differences are speed (binary serialization is faster than JSON text), strict schema (the .proto contract is required, not optional), native streaming support (four modes: unary, server streaming, client streaming, bidirectional), and code generation built in. REST wins on human readability and browser compatibility. gRPC is best for internal service-to-service calls; REST is better for public APIs.

</details>

<br>

**Q2: What is a .proto file and what does it define?**

<details>
<summary>💡 Show Answer</summary>

A .proto file is the schema contract for a gRPC service. It defines three things: messages (the data structures, equivalent to request/response bodies), services (the available RPCs), and the package namespace. Field numbers in messages are critical — they are how protobuf identifies fields on the wire, not the field names. Field numbers 1–15 use one byte of encoding overhead and should be reserved for frequently used fields. You generate Python client and server code from the .proto using `grpc_tools.protoc`.

</details>

<br>

**Q3: What are the four streaming modes in gRPC?**

<details>
<summary>💡 Show Answer</summary>

- Unary: one request, one response — the standard call, like a normal function
- Server streaming: one request, a stream of responses — used for large result sets or real-time feeds
- Client streaming: a stream of requests, one response — used for file uploads or bulk inserts
- Bidirectional streaming: both sides stream simultaneously — used for chat, collaborative editing, or game state sync

In protobuf syntax, the `stream` keyword is placed before the message type in the `returns` or argument position to declare a streaming mode.

</details>

<br>

**Q4: What gRPC status code would you return for a missing resource, and how does it map to HTTP?**

<details>
<summary>💡 Show Answer</summary>

You return `grpc.StatusCode.NOT_FOUND` (code 5), which maps to HTTP 404. In Python, you set this with `context.set_code(grpc.StatusCode.NOT_FOUND)` and `context.set_details("message")` before returning an empty response object. Other common mappings: `INVALID_ARGUMENT` (3) → 400, `PERMISSION_DENIED` (7) → 403, `UNAUTHENTICATED` (16) → 401, `UNAVAILABLE` (14) → 503. Always return the most specific code — do not default to `UNKNOWN`.

</details>

<br>

**Q5: How do you pass metadata (like headers) in a gRPC call?**

<details>
<summary>💡 Show Answer</summary>

gRPC metadata is the equivalent of HTTP headers. On the client, you pass a list of tuples to the `metadata` parameter: `stub.GetUser(request, metadata=[("x-request-id", "abc123"), ("authorization", "Bearer token")])`. On the server, you read it with `context.invocation_metadata()` which returns a list of key-value pairs. Metadata keys that start with `grpc-` are reserved by the framework. Binary metadata values are indicated by a `-bin` suffix on the key.

</details>

<br>

---

# 🔹 Intermediate Level Questions (2–5 Years)

**Q6: How do you handle timeouts and cancellations in gRPC, and why does it matter in production?**

<details>
<summary>💡 Show Answer</summary>

Timeouts are set as a `timeout` parameter (in seconds) on the client stub call. If exceeded, the client receives `DEADLINE_EXCEEDED` and sends a cancellation signal to the server. On the server side, you should check `context.is_active()` periodically inside streaming RPCs and break early if it returns False — otherwise you waste resources processing a request whose result will be discarded. In production, always set deadlines: without them, slow downstream services can exhaust your thread pool. Cascading deadline propagation across services (passing remaining timeout to downstream calls) prevents one slow service from hanging the entire call chain.

</details>

<br>

**Q7: What are gRPC interceptors and what are typical production uses?**

<details>
<summary>💡 Show Answer</summary>

Interceptors are middleware for gRPC, similar to FastAPI middleware or Django middleware. They wrap every RPC call and can add cross-cutting behavior without modifying individual handlers. Common production uses: authentication (validate JWT in every interceptor before the handler runs), request logging (log method name, duration, status code), distributed tracing injection (add trace ID to context), and error monitoring (catch unhandled exceptions and report to Sentry). Server-side interceptors implement `grpc.ServerInterceptor`. They are added at server creation time via the `interceptors` parameter.

</details>

<br>

**Q8: When would you choose server streaming over returning a large list in a single unary response?**

<details>
<summary>💡 Show Answer</summary>

Use server streaming when: the result set is large enough that buffering it in memory before sending causes latency or memory pressure, when the client can begin processing early items while later ones are still being fetched, or when the result set is unbounded (a live event feed). The default gRPC message size limit is 4MB — a large unary response risks hitting this. With server streaming, each streamed message is small and the limit applies per message, not to the total stream. The downside: streaming RPCs are stateful connections and harder to load balance; unary calls are independent and fully stateless.

</details>

<br>

**Q9: How do you secure a gRPC service in production?**

<details>
<summary>💡 Show Answer</summary>

The primary mechanism is TLS via `grpc.ssl_channel_credentials()` on the client and `grpc.ssl_server_credentials()` on the server, using CA certificate, server cert, and private key. For mutual TLS (mTLS), both sides present certificates — common in service mesh environments. Authentication is typically done via metadata: the client sends a JWT token in metadata, and a server interceptor validates it before passing to the handler. For internal microservices, mTLS handles both encryption and service identity. Avoid `insecure_channel` in production — it is only acceptable in local development or inside a private service mesh that handles encryption at the infrastructure level.

</details>

<br>

**Q10: What is the difference between `sint32` and `int32` in protobuf, and when does it matter?**

<details>
<summary>💡 Show Answer</summary>

Both represent signed 32-bit integers, but they use different wire encodings. `int32` uses standard varint encoding — for negative numbers this always uses 10 bytes because protobuf varints encode the sign bit as the most significant bit. `sint32` uses ZigZag encoding, which maps negative integers to small positive integers (e.g., -1 → 1, -2 → 3) so they serialize compactly. If your field frequently holds negative values (e.g., temperature deltas, account balance changes), use `sint32`/`sint64`. For non-negative values or IDs, use `int32`/`int64` or `fixed32`/`fixed64`.

</details>

<br>

---

# 🔹 Advanced Level Questions (5+ Years)

**Q11: How does gRPC handle load balancing, and what are the limitations compared to REST?**

<details>
<summary>💡 Show Answer</summary>

gRPC runs over HTTP/2 which multiplexes multiple RPCs over a single TCP connection. This means traditional L4 load balancers (which balance at the TCP connection level) will route all RPCs from one client to the same backend — giving you no balancing at all. To actually balance gRPC traffic, you need L7 (application-layer) load balancing: either client-side load balancing (the client resolves multiple backend addresses and picks one per call), or an L7 proxy such as Envoy, Istio, or a service mesh that understands HTTP/2 frames. In Kubernetes, this is why you typically run a service mesh or use a headless service with client-side balancing rather than a standard ClusterIP service.

</details>

<br>

**Q12: How would you design a backward-compatible change to a .proto file without breaking existing clients?**

<details>
<summary>💡 Show Answer</summary>

Protobuf is designed for forward and backward compatibility if you follow the rules. Safe changes: adding new fields with new field numbers (old clients ignore unknown fields), adding new enum values, adding new RPC methods to a service. Unsafe changes: changing a field's type, reusing a field number that was previously removed, renaming a field (names don't matter on the wire, but do for code generation), removing a required field (proto3 has no required, but changing semantics breaks consumers). Best practice: never delete field numbers — reserve them with the `reserved` keyword so they cannot be accidentally reused. For major schema changes, version your package namespace (`package user.v1` → `package user.v2`) and run both versions concurrently during migration.

</details>

<br>

**Q13: What is gRPC-Web and why is it needed? What are the trade-offs?**

<details>
<summary>💡 Show Answer</summary>

Browsers cannot make raw HTTP/2 gRPC calls because the browser's Fetch and XHR APIs do not expose the HTTP/2 framing layer needed for gRPC's trailer-based protocol. gRPC-Web is a modified protocol that encodes gRPC calls in a format compatible with standard browser HTTP. It requires a proxy (Envoy is the reference implementation) that translates between gRPC-Web from the browser and standard gRPC for backend services. Trade-offs: you gain browser compatibility, but lose native bidirectional streaming (browser gRPC-Web only supports unary and server streaming), and you add a required proxy hop. For pure browser clients needing bidirectional streaming, WebSockets are a better fit. gRPC-Web is a good choice when you already have gRPC services and want to expose them to a web frontend without maintaining a REST translation layer.

</details>

<br>

**Q14: Walk through how you would instrument a gRPC service for production observability.**

<details>
<summary>💡 Show Answer</summary>

Four areas to cover: traces, metrics, logs, and health checks.

Traces: use a server interceptor to create a span per RPC call, set attributes for service name, RPC method, and status code, and propagate the trace context from incoming metadata using the W3C TraceContext format. The OpenTelemetry gRPC instrumentation library does this automatically.

Metrics: emit a counter for total RPC calls (labeled by method and status), and a histogram for RPC duration. These map directly to the four golden signals.

Logs: structured logs with trace_id and span_id injected so you can correlate logs with traces in Jaeger or Grafana Tempo.

Health checks: implement the gRPC Health Checking Protocol (`grpc.health.v1.Health`) — Kubernetes liveness and readiness probes understand this natively and it is more accurate than HTTP health endpoints for gRPC services.

</details>

<br>
