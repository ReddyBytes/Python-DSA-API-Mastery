<a id="top"></a>

# gRPC — When JSON Is Too Slow

> Naveen's Story: Naveen is a Telugu microservices architect building high-performance inter-service communication at a company processing 100,000 calls per second between services. He discovered that JSON serialization was burning 10 seconds of CPU overhead per second — and that silent contract breakage at 2am on Black Friday was the real cost of REST at scale. This is his journey into gRPC.

<a id="toc"></a>

## Table of Contents

- [1. The 100,000 Calls Per Second Problem](#the-100000-calls-per-second-problem)
- [2. Learning Priority](#learning-priority)
- [3. What gRPC Is](#what-grpc-is)
- [4. Protocol Buffers — The Schema](#protocol-buffers-the-schema)
  - [Generating Code from the Schema](#generating-code-from-the-schema)
- [5. The 4 Communication Modes](#the-4-communication-modes)
  - [Unary — One Request, One Response](#unary-one-request-one-response)
  - [Server Streaming — One Request, Many Responses](#server-streaming-one-request-many-responses)
  - [Client Streaming — Many Requests, One Response](#client-streaming-many-requests-one-response)
  - [Bidirectional Streaming — Streams in Both Directions](#bidirectional-streaming-streams-in-both-directions)
- [6. Python gRPC — A Minimal Client and Server](#python-grpc-a-minimal-client-and-server)
- [7. gRPC vs REST — An Honest Comparison](#grpc-vs-rest-an-honest-comparison)
- [8. When gRPC Wins](#when-grpc-wins)
- [9. When REST Wins](#when-rest-wins)
- [10. The Mental Model](#the-mental-model)
- [11. Summary](#summary)
- [12. gRPC Interceptors — Cross-Cutting Concerns](#grpc-interceptors-cross-cutting-concerns)
  - [Server-Side Interceptor](#server-side-interceptor)
  - [Client-Side Interceptor](#client-side-interceptor)
- [13. Fire Summary](#fire-summary)

[Back to Top](#top)

<a id="the-100000-calls-per-second-problem"></a>

# 1. The 100,000 Calls Per Second Problem

Naveen is working at a company with a microservices architecture. Dozens of services.
Hundreds of engineers. The checkout service calls the inventory service every time
someone places an order. The recommendation service calls the user service on every
page load.

On a typical Tuesday afternoon, that's 100,000 inter-service calls per second.

They're all using REST with JSON.

Here's what happens at that scale:

```
Each service call:

  Serialize Python dict -> JSON string      ~50 microseconds
  Send over HTTP/1.1
  Other side receives JSON string
  Parse JSON string -> Python dict          ~50 microseconds

  Total JSON overhead: ~100 microseconds per call

At 100,000 calls/second:
  100,000 x 100 microseconds = 10 seconds of pure parsing overhead
  ... per second.
```

That's before any business logic runs. Just serialization and deserialization.

And there's another problem nobody talks about until it bites you:

```
CheckoutService calls InventoryService:
  POST /inventory/check
  Body: {"product_id": "SKU-9923", "quantity": 2}

InventoryService returns:
  {"available": true, "stock_count": 47}

Three months later, InventoryService team renames "stock_count" to "quantity_available"
because it was ambiguous.

CheckoutService breaks.
Silently.
At 2am.
On Black Friday.
```

No compiler caught it. No IDE warned you. The JSON key changed, and the contract
between two services — written only in documentation and tribal knowledge — silently
broke.

This is the world REST and JSON create in large service-to-service communication.
Google, operating at orders of magnitude larger than almost any company, had this
problem in the early 2010s. Their answer was gRPC.

"That was the moment I stopped treating REST as the default for everything," Naveen recalls. "When you've seen a silent contract break take down checkout on the busiest day of the year, you start demanding compile-time guarantees between services."

[Back to Top](#top)

<a id="learning-priority"></a>

# 2. Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
.proto file · service definition · Python server/client

**Should Learn** — Important for real projects:
streaming modes

**Good to Know** — Useful in specific situations:
gRPC-web

**Reference** — Know it exists, look up syntax when needed:
Protocol Buffers advanced features

[Back to Top](#top)

<a id="what-grpc-is"></a>

# 3. What gRPC Is

gRPC is a high-performance, open-source remote procedure call framework originally
developed by Google, open-sourced in 2015.

The name stands for "gRPC Remote Procedure Calls" (yes, it's recursive).

Three things make it different from REST:

**1. HTTP/2 under the hood.**
REST typically uses HTTP/1.1 which has a fundamental limitation: one request at a time
per connection (without pipelining, which is poorly supported). HTTP/2 supports
multiplexing — multiple requests and responses flying over one connection simultaneously.
It also compresses headers and uses a binary framing layer, which is faster than HTTP/1.1's
text-based format.

**2. Protocol Buffers for serialization.**
Instead of JSON (text-based, parsed character by character), gRPC uses Protocol Buffers
(Protobuf) — a binary serialization format also developed by Google. Binary is 3-10x
smaller than the equivalent JSON and significantly faster to parse because the CPU works
with native binary representations rather than converting text.

```
JSON (text):
{"id": 42, "name": "Alice Chen", "email": "alice@example.com", "age": 34}
-> 72 bytes, needs text parsing

Protobuf (binary):
<binary blob>
-> ~28 bytes, decoded directly into struct
```

**3. Strongly typed schema via .proto files.**
Both services agree on a `.proto` file — the contract. The proto compiler generates
client and server code in your language of choice. If the schema changes in a
breaking way, compilation fails before you deploy.

```
Types are checked at compile time.
The field-rename-at-2am problem becomes a compiler error.
```

Naveen explains the mental shift: "With REST, your contract lives in documentation that nobody reads. With gRPC, your contract lives in code that the compiler enforces. That's the difference between a gentleman's agreement and a legal contract."

[Back to Top](#top)

<a id="protocol-buffers-the-schema"></a>

# 4. Protocol Buffers — The Schema

The `.proto` file is where you define your services and messages. It's the source
of truth for both sides of the conversation.

```protobuf
syntax = "proto3";

package user;

// --- Service definitions ---
// These define the RPC methods your service exposes.

service UserService {
  // Unary: one request, one response
  rpc GetUser (GetUserRequest) returns (User);

  // Server streaming: one request, stream of responses
  rpc ListUsers (ListUsersRequest) returns (stream User);

  // Client streaming: stream of requests, one response
  rpc CreateUsers (stream CreateUserRequest) returns (BulkCreateResult);

  // Bidirectional streaming: streams both ways
  rpc SyncUsers (stream UserSyncEvent) returns (stream UserSyncAck);
}

// --- Message definitions ---
// These are the data structures — like types in GraphQL or models in REST.

message GetUserRequest {
  string user_id = 1;     // The = 1 is the field number (not a default value)
}

message ListUsersRequest {
  int32 page = 1;
  int32 page_size = 2;
}

message CreateUserRequest {
  string name = 1;
  string email = 2;
}

message User {
  string id = 1;
  string name = 2;
  string email = 3;
  int32 age = 4;
  bool is_active = 5;
}

message BulkCreateResult {
  int32 created_count = 1;
  repeated string user_ids = 2;   // 'repeated' means list/array
  repeated string errors = 3;
}
```

Field numbers (`= 1`, `= 2`, etc.) are how Protobuf identifies fields in the binary
encoding. This is what allows backward compatibility — you can add new fields with
new numbers without breaking existing clients who just ignore unknown field numbers.

**Never change a field number. Never reuse a field number.**
Add new fields. Mark old ones as `reserved`. This is the compatibility contract.

> **Practice:** [Q64 - protocol-buffers](../api_practice_questions_100.md#q64--normal--protocol-buffers)

<a id="generating-code-from-the-schema"></a>

## Generating Code from the Schema

This is one of gRPC's superpowers. You write the schema once, and the proto compiler
generates typed client and server code in your language:

```bash
# Install the protobuf compiler and Python plugin
pip install grpcio grpcio-tools

# Generate Python code from the proto file
python -m grpc_tools.protoc \
  --proto_path=. \
  --python_out=. \
  --grpc_python_out=. \
  user.proto

# This generates:
#   user_pb2.py      <- message classes (User, GetUserRequest, etc.)
#   user_pb2_grpc.py <- service stubs (UserServiceStub, UserServiceServicer)
```

The generated code is what your engineers import and use. Nobody writes serialization
code by hand.

[Back to Top](#top)

<a id="the-4-communication-modes"></a>

# 5. The 4 Communication Modes

This is where gRPC genuinely extends beyond what REST can do. REST is request-response,
full stop. gRPC supports four communication patterns:

<a id="unary-one-request-one-response"></a>

## Unary — One Request, One Response

The classic pattern. Identical to REST in structure but faster.

```
Client                              Server
  |                                   |
  |  GetUser(user_id="42")            |
  |  ────────────────────────────>    |
  |                                   |  [fetch user from DB]
  |  User{id:"42", name:"Alice", ...} |
  |  <────────────────────────────    |
  |                                   |
```

```protobuf
rpc GetUser (GetUserRequest) returns (User);
```

Use this for: most API calls that map to a single data fetch or operation.

<a id="server-streaming-one-request-many-responses"></a>

## Server Streaming — One Request, Many Responses

The client sends one request. The server sends back a stream of responses, one at
a time, over the same connection. The client processes them as they arrive.

```
Client                              Server
  |                                   |
  |  ListUsers(page_size=100)         |
  |  ────────────────────────────>    |
  |                                   |  [start scanning DB]
  |  User{id:"1", name:"Alice"}       |
  |  <────────────────────────────    |
  |  User{id:"2", name:"Bob"}         |
  |  <────────────────────────────    |
  |  User{id:"3", name:"Carol"}       |
  |  <────────────────────────────    |
  |  ... (stream continues)           |
  |  <────────────────────────────    |
  |  [end of stream]                  |
  |  <────────────────────────────    |
```

```protobuf
rpc ListUsers (ListUsersRequest) returns (stream User);
```

Use this for: large data sets where you want to start processing before all data
arrives, real-time feeds, log streaming, export operations.

<a id="client-streaming-many-requests-one-response"></a>

## Client Streaming — Many Requests, One Response

The client sends a stream of messages. When done, the server responds once with
a summary or aggregated result.

```
Client                              Server
  |                                   |
  |  CreateUser{name:"Alice",...}     |
  |  ────────────────────────────>    |  [buffer]
  |  CreateUser{name:"Bob",...}       |
  |  ────────────────────────────>    |  [buffer]
  |  CreateUser{name:"Carol",...}     |
  |  ────────────────────────────>    |  [buffer]
  |  [end of stream]                  |
  |  ────────────────────────────>    |  [process all 3]
  |                                   |
  |  BulkCreateResult{created:3}      |
  |  <────────────────────────────    |
```

```protobuf
rpc CreateUsers (stream CreateUserRequest) returns (BulkCreateResult);
```

Use this for: bulk uploads, telemetry data ingestion, large file upload in chunks,
sensor readings where you want one acknowledgement after batching.

<a id="bidirectional-streaming-streams-in-both-directions"></a>

## Bidirectional Streaming — Streams in Both Directions

Both sides send streams of messages simultaneously over the same connection.
The order and timing of sends and receives is up to the application.

```
Client                              Server
  |                                   |
  |  UserSyncEvent{user_id:"1",...}   |
  |  ────────────────────────────>    |
  |                                   |  [process user 1]
  |  UserSyncEvent{user_id:"2",...}   |
  |  ────────────────────────────>    |
  |  UserSyncAck{user_id:"1", ok:true}|
  |  <────────────────────────────    |
  |  UserSyncEvent{user_id:"3",...}   |
  |  ────────────────────────────>    |
  |  UserSyncAck{user_id:"2", ok:true}|
  |  <────────────────────────────    |
  |  ... (both streams continue)      |
```

```protobuf
rpc SyncUsers (stream UserSyncEvent) returns (stream UserSyncAck);
```

Use this for: real-time collaborative applications, bidirectional message brokers,
game server communication, live trading systems, interactive media streams.

[Back to Top](#top)

<a id="python-grpc-a-minimal-client-and-server"></a>

# 6. Python gRPC — A Minimal Client and Server

Let's build a working gRPC service in Python. We'll implement `GetUser` (unary)
and `ListUsers` (server streaming).

**The proto file** (`user.proto`):
```protobuf
syntax = "proto3";

service UserService {
  rpc GetUser (GetUserRequest) returns (User);
  rpc ListUsers (ListUsersRequest) returns (stream User);
}

message GetUserRequest { string user_id = 1; }
message ListUsersRequest { int32 page_size = 1; }
message User {
  string id = 1;
  string name = 2;
  string email = 3;
}
```

Generate the Python stubs:
```bash
python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. user.proto
```

**The server** (`server.py`):
```python
import grpc
import time
from concurrent import futures
import user_pb2
import user_pb2_grpc

# Fake data store
USERS = {
    "1": {"id": "1", "name": "Alice Chen",  "email": "alice@example.com"},
    "2": {"id": "2", "name": "Bob Smith",   "email": "bob@example.com"},
    "3": {"id": "3", "name": "Carol Davis", "email": "carol@example.com"},
}

class UserServiceServicer(user_pb2_grpc.UserServiceServicer):

    def GetUser(self, request, context):
        user = USERS.get(request.user_id)
        if not user:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"User {request.user_id} not found")
            return user_pb2.User()

        return user_pb2.User(
            id=user["id"],
            name=user["name"],
            email=user["email"]
        )

    def ListUsers(self, request, context):
        # Server streaming: yield one user at a time
        limit = request.page_size or 10
        for i, user in enumerate(USERS.values()):
            if i >= limit:
                break
            yield user_pb2.User(
                id=user["id"],
                name=user["name"],
                email=user["email"]
            )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(UserServiceServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Server started on port 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
```

**The client** (`client.py`):
```python
import grpc
import user_pb2
import user_pb2_grpc

def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = user_pb2_grpc.UserServiceStub(channel)

        # Unary call
        print("--- GetUser ---")
        response = stub.GetUser(user_pb2.GetUserRequest(user_id="1"))
        print(f"Got user: {response.name} ({response.email})")

        # Server streaming call
        print("\n--- ListUsers ---")
        for user in stub.ListUsers(user_pb2.ListUsersRequest(page_size=10)):
            print(f"  {user.id}: {user.name}")

if __name__ == "__main__":
    run()
```

Run in two terminals:
```bash
# Terminal 1
python server.py

# Terminal 2
python client.py
```

[Back to Top](#top)

<a id="grpc-vs-rest-an-honest-comparison"></a>

# 7. gRPC vs REST — An Honest Comparison

```
                    REST (HTTP/1.1 + JSON)    gRPC (HTTP/2 + Protobuf)
─────────────────────────────────────────────────────────────────────────
Serialization:      JSON (text)               Protobuf (binary)
Payload size:       Baseline                  3-10x smaller
Parse speed:        Slower (text parsing)     Faster (binary decoding)
Schema:             Optional (OpenAPI)        Required (.proto)
Type safety:        None at runtime           Enforced by generated code
Code generation:    Limited                   Full client/server stubs
Streaming:          SSE (server only)         4 modes, native
Browser support:    Universal                 Needs gRPC-Web proxy
Human readable:     Yes                       No (binary)
Debugging:          Easy (curl, browser)      Harder (needs tooling)
Caching:            HTTP cache works          Manual
Learning curve:     Low                       Medium-High
Ecosystem:          Huge                      Large, growing
Best for:           Public APIs, browser      Internal services, perf
```

Real numbers from benchmarks (approximate, varies by payload and hardware):

```
Operation: Serialize + send + deserialize a 1KB message, 10,000 times

REST/JSON:     ~4.2 seconds
gRPC/Protobuf: ~1.1 seconds

Throughput improvement: ~3.8x faster
Memory usage: gRPC ~60% lower
```

These numbers matter when you're doing millions of calls per day between services.

> **Practice:** [Q63 - grpc-vs-rest](../api_practice_questions_100.md#q63--interview--grpc-vs-rest)

Naveen's take: "I show these benchmarks to every team that says 'REST is fine for internal calls.' REST IS fine — until it isn't. Know where your inflection point is."

[Back to Top](#top)

<a id="when-grpc-wins"></a>

# 8. When gRPC Wins

**Internal microservice communication.** This is gRPC's home turf. Service-to-service
calls inside your infrastructure, where you control both sides of the wire, can almost
always benefit from gRPC's speed and type safety. The compilation-time contract
checking alone prevents entire classes of production incidents.

**Low-latency requirements.** Financial systems, game backends, ad-tech — anywhere
that milliseconds matter, gRPC's lower serialization overhead adds up. At high request
volumes, 100 microseconds per call becomes meaningful.

**Polyglot environments.** Your frontend team writes TypeScript, backend is Python,
data pipeline is Go, ML inference is C++. Write one `.proto` file. Generate typed
clients in all four languages. Everyone is guaranteed to speak the same contract.

```
user.proto
   |
   |── grpc_tools.protoc ──> Python server stubs
   |── protoc-gen-go ──────> Go client stubs
   |── protoc-gen-ts ──────> TypeScript client stubs
   └── protoc-gen-cpp ─────> C++ client stubs
```

**Streaming data.** Server streaming for large result sets, client streaming for
bulk ingestion, bidirectional for real-time sync — gRPC handles all of these natively
at the protocol level. With REST, streaming requires Server-Sent Events or WebSockets
with bespoke implementations.

[Back to Top](#top)

<a id="when-rest-wins"></a>

# 9. When REST Wins

**Public APIs.** If you're building an API that external developers will consume,
gRPC is a poor choice. They can't use curl to test it. They can't call it from a
browser without a gRPC-Web proxy. They need tooling to inspect binary payloads.
REST + OpenAPI gives developers a much better experience.

**Browser clients.** gRPC relies on HTTP/2 features that browsers don't fully expose
through standard JavaScript APIs. gRPC-Web exists as a workaround, but it requires
a proxy (like Envoy) in front of your gRPC service to translate. That's extra
infrastructure and complexity. If your primary client is a browser, REST is simpler.

**Simplicity and debuggability.** You can't curl a gRPC endpoint. You can't open
DevTools and read the request payload. You need grpcurl, a service reflection setup,
and some patience. When you're building something new and need to iterate quickly,
REST's simplicity wins. gRPC's tooling is improving, but it still requires more
investment than REST.

**Small teams and simple services.** gRPC's benefits are real but require upfront
investment: maintaining proto files, setting up code generation in CI, learning the
error model. For a small team building a straightforward CRUD service, that overhead
often isn't worth it.

[Back to Top](#top)

<a id="the-mental-model"></a>

# 10. The Mental Model

```
REST                            gRPC
──────────────────────          ──────────────────────────────
URL + HTTP verb                 Service + method name
JSON (text, flexible)           Protobuf (binary, strict)
HTTP/1.1 (one req at a time)    HTTP/2 (multiplexed)
Human readable                  Machine efficient
Contract optional               Contract required (.proto)
Browser-native                  Needs gRPC-Web in browser
Simple to start                 More setup, more power
Public-facing APIs              Internal service mesh
```

gRPC is not a replacement for REST. They solve different problems. REST is the
handshake for the world — readable, universal, works everywhere. gRPC is the
high-speed internal backbone — typed, binary, fast.

The companies running at scale use both. REST for anything facing the outside world.
gRPC for the service-to-service communication that powers it all underneath.

[Back to Top](#top)

<a id="summary"></a>

# 11. Summary

```
What it is:    Remote procedure call framework from Google
Protocol:      HTTP/2 (multiplexed, binary framing, header compression)
Serialization: Protocol Buffers (3-10x smaller than JSON, faster to parse)
Schema:        .proto files — required, strongly typed, compiled
Code gen:      One schema -> typed client/server in 10+ languages
4 modes:       Unary | Server streaming | Client streaming | Bidirectional
Wins at:       Internal services, high throughput, polyglot environments
Loses at:      Public APIs, browser clients, simplicity
```

gRPC makes a specific trade: it gives up human-readability and browser-native support
in exchange for speed, type safety, and streaming power. That trade is worth it
in the right context — and knowing that context is what separates engineers who
cargo-cult technology from those who choose it deliberately.

[Back to Top](#top)

<a id="grpc-interceptors-cross-cutting-concerns"></a>

# 12. gRPC Interceptors — Cross-Cutting Concerns

> Just as FastAPI middleware wraps every HTTP request, gRPC interceptors wrap every RPC call — the right place to add authentication, logging, metrics, and retry logic without touching each handler.

**gRPC interceptors** (called **middleware** in HTTP terms) run before and after every RPC call on both server and client sides. They're the standard pattern for authentication, structured logging, request ID injection, and metrics collection.

<a id="server-side-interceptor"></a>

## Server-Side Interceptor

```python
import grpc
import time
import logging

class LoggingInterceptor(grpc.ServerInterceptor):
    """Log every incoming RPC with timing."""

    def intercept_service(self, continuation, handler_call_details):
        method = handler_call_details.method   # <- "/package.Service/Method"

        def intercept_call(request, context):
            start = time.time()
            try:
                response = continuation(handler_call_details)(request, context)
                duration_ms = (time.time() - start) * 1000
                logging.info(f"gRPC {method} OK  {duration_ms:.1f}ms")
                return response
            except Exception as e:
                duration_ms = (time.time() - start) * 1000
                logging.error(f"gRPC {method} ERR {duration_ms:.1f}ms — {e}")
                raise

        return grpc.unary_unary_rpc_method_handler(intercept_call)

class AuthInterceptor(grpc.ServerInterceptor):
    """Validate bearer token on every RPC."""

    SKIP_AUTH = {"/grpc.health.v1.Health/Check"}   # <- health checks skip auth

    def intercept_service(self, continuation, handler_call_details):
        method = handler_call_details.method
        if method in self.SKIP_AUTH:
            return continuation(handler_call_details)   # <- pass through

        def check_auth(request, context):
            metadata = dict(context.invocation_metadata())
            token = metadata.get("authorization", "").removeprefix("Bearer ")

            if not validate_token(token):
                context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid token")

            return continuation(handler_call_details)(request, context)

        return grpc.unary_unary_rpc_method_handler(check_auth)

# Register interceptors when creating server:
server = grpc.server(
    futures.ThreadPoolExecutor(max_workers=10),
    interceptors=[AuthInterceptor(), LoggingInterceptor()]   # <- order matters
)
```

<a id="client-side-interceptor"></a>

## Client-Side Interceptor

```python
class RetryInterceptor(grpc.UnaryUnaryClientInterceptor):
    """Retry on transient failures with exponential backoff."""

    RETRIABLE = {grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.RESOURCE_EXHAUSTED}

    def intercept_unary_unary(self, continuation, client_call_details, request):
        for attempt in range(3):
            response = continuation(client_call_details, request)
            try:
                return response.result()        # <- raises on error
            except grpc.RpcError as e:
                if e.code() not in self.RETRIABLE or attempt == 2:
                    raise
                time.sleep(2 ** attempt)        # <- backoff: 1s, 2s, 4s
                logging.warning(f"Retry {attempt+1} for {e.code()}")

# Create channel with interceptors:
channel = grpc.intercept_channel(
    grpc.insecure_channel("localhost:50051"),
    RetryInterceptor()
)
stub = UserServiceStub(channel)
```

**Interceptor execution order:**
```
Request:   Interceptor1 -> Interceptor2 -> Handler
Response:  Handler -> Interceptor2 -> Interceptor1

[AuthInterceptor, LoggingInterceptor]:
  Request:  Auth checks first -> Logging wraps second
  Response: Logging records time -> Auth doesn't act on response
```

**Common interceptors in production:**
- **Authentication** — validate token, inject user context
- **Logging** — structured RPC logs with method, status, duration
- **Metrics** — increment counters, record histograms per method
- **Request ID** — inject/propagate trace ID via metadata
- **Retry** — client-side retry for transient failures

[Back to Top](#top)

<a id="fire-summary"></a>

# 13. Fire Summary

| Concept | One-Liner |
|---------|-----------|
| gRPC | High-performance RPC framework using HTTP/2 + Protobuf, open-sourced by Google |
| Protocol Buffers | Binary serialization format — 3-10x smaller than JSON, strongly typed |
| .proto file | The contract between services — compiled into client/server code |
| Field numbers | Binary identifiers in Protobuf — never reuse, never change |
| Unary RPC | One request, one response — the REST equivalent |
| Server streaming | One request, stream of responses back |
| Client streaming | Stream of requests, one response back |
| Bidirectional | Both sides stream simultaneously over one connection |
| Code generation | One .proto generates typed stubs in 10+ languages |
| Interceptors | Middleware for gRPC — auth, logging, retry, metrics |
| gRPC-Web | Proxy layer enabling browser clients to call gRPC services |
| When to use gRPC | Internal services, high throughput, polyglot, streaming |
| When to use REST | Public APIs, browser clients, simplicity, small teams |

[Back to Top](#top)

<a id="navigation"></a>

## Navigation

[Back to README](../README.md) | [Prev: GraphQL](../13_graphql/theory.md) | [Next: API Gateway Patterns](../15_api_gateway/theory.md)

Related Topics: [GraphQL](../13_graphql/theory.md) | [API Gateway Patterns](../15_api_gateway/theory.md) | [API Performance and Scaling](../09_api_performance_scaling/theory.md)
