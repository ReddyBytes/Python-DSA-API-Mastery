# ⚡ Cheatsheet: gRPC

---

## Learning Priority

**Must Learn** — foundation for any gRPC work:
.proto file syntax · service/rpc definition · protobuf scalar types · unary vs streaming

**Should Learn** — required for production gRPC:
Python server/client skeleton · gRPC status codes · metadata headers · interceptors

**Good to Know** — advanced usage:
Bidirectional streaming · deadlines/timeouts · gRPC-Web · reflection

**Reference** — look up when needed:
Proto3 field options · well-known types (google.protobuf.Timestamp) · gRPC health check protocol

---

## .proto File Syntax

```protobuf
syntax = "proto3";

package user.v1;

// Import well-known types
import "google/protobuf/timestamp.proto";
import "google/protobuf/empty.proto";

// Message definition
message User {
  string id = 1;             // field name = field number (1-15 use 1 byte, prefer for frequent fields)
  string email = 2;
  string name = 3;
  bool active = 4;
  repeated string roles = 5; // repeated = list/array
  google.protobuf.Timestamp created_at = 6;
}

// Nested message
message Address {
  string street = 1;
  string city = 2;
  string country_code = 3;  // ISO 3166-1 alpha-2
}

// Enum
enum UserStatus {
  USER_STATUS_UNSPECIFIED = 0;  // proto3: 0 is always the default; always define it
  USER_STATUS_ACTIVE = 1;
  USER_STATUS_SUSPENDED = 2;
  USER_STATUS_DELETED = 3;
}

// Request / Response messages
message GetUserRequest {
  string user_id = 1;
}

message ListUsersRequest {
  int32 page_size = 1;
  string page_token = 2;
}

message ListUsersResponse {
  repeated User users = 1;
  string next_page_token = 2;
}

message CreateUserRequest {
  string email = 1;
  string name = 2;
}
```

---

## Service and RPC Definition

```protobuf
service UserService {
  // Unary — one request, one response (like HTTP request/response)
  rpc GetUser(GetUserRequest) returns (User);
  rpc CreateUser(CreateUserRequest) returns (User);
  rpc DeleteUser(GetUserRequest) returns (google.protobuf.Empty);

  // Server streaming — one request, stream of responses
  rpc ListUsers(ListUsersRequest) returns (stream User);
  rpc WatchUserEvents(GetUserRequest) returns (stream UserEvent);

  // Client streaming — stream of requests, one response
  rpc BulkCreateUsers(stream CreateUserRequest) returns (BulkCreateResponse);

  // Bidirectional streaming — stream both ways
  rpc Chat(stream ChatMessage) returns (stream ChatMessage);
}
```

---

## Protobuf Scalar Types

| Proto Type | Python Type | Notes |
|------------|------------|-------|
| `string` | `str` | UTF-8 encoded |
| `bytes` | `bytes` | Arbitrary byte sequence |
| `bool` | `bool` | |
| `int32` | `int` | 32-bit signed int |
| `int64` | `int` | 64-bit signed int |
| `uint32` | `int` | 32-bit unsigned |
| `uint64` | `int` | 64-bit unsigned |
| `float` | `float` | 32-bit IEEE 754 |
| `double` | `float` | 64-bit IEEE 754 |
| `fixed32` | `int` | 4 bytes, efficient for values often > 2^28 |
| `fixed64` | `int` | 8 bytes, efficient for values often > 2^56 |
| `sint32` | `int` | ZigZag encoding — efficient for negative ints |
| `sint64` | `int` | ZigZag encoding — efficient for negative ints |

**Rule of thumb:** Use `int32`/`int64` for most integers. Use `sint32`/`sint64` if the value is often negative. Use `fixed32`/`fixed64` for IDs and hashes.

---

## Generate Python Code from .proto

```bash
# Install
pip install grpcio grpcio-tools

# Generate Python stubs
python -m grpc_tools.protoc \
  -I./proto \                          # include path
  --python_out=./generated \           # message classes
  --grpc_python_out=./generated \      # service stubs
  ./proto/user/v1/user.proto

# Files generated:
# generated/user/v1/user_pb2.py        — message classes
# generated/user/v1/user_pb2_grpc.py   — service stubs
```

---

## Python gRPC Server

```python
import grpc
from concurrent import futures
import user_pb2
import user_pb2_grpc

class UserServiceServicer(user_pb2_grpc.UserServiceServicer):
    """Implement the service defined in .proto"""

    def GetUser(self, request, context):
        """Unary RPC"""
        user = db.get_user(request.user_id)
        if not user:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"User {request.user_id} not found")
            return user_pb2.User()
        return user_pb2.User(id=user["id"], email=user["email"], name=user["name"])

    def ListUsers(self, request, context):
        """Server streaming RPC — yield each response"""
        page_size = request.page_size or 50
        for user in db.iter_users(page_size=page_size):
            yield user_pb2.User(id=user["id"], email=user["email"])
            # Check if client cancelled
            if context.is_active() is False:
                break

    def BulkCreateUsers(self, request_iterator, context):
        """Client streaming RPC — iterate over incoming stream"""
        count = 0
        for req in request_iterator:
            db.create_user(email=req.email, name=req.name)
            count += 1
        return user_pb2.BulkCreateResponse(created_count=count)

def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ("grpc.max_receive_message_length", 10 * 1024 * 1024),   # 10MB
            ("grpc.max_send_message_length", 10 * 1024 * 1024),
        ]
    )
    user_pb2_grpc.add_UserServiceServicer_to_server(UserServiceServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("gRPC server listening on :50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
```

---

## Python gRPC Client

```python
import grpc
import user_pb2
import user_pb2_grpc

def get_user_client():
    # Insecure (dev only)
    channel = grpc.insecure_channel("localhost:50051")

    # TLS (production)
    # with open("ca.crt", "rb") as f:
    #     creds = grpc.ssl_channel_credentials(f.read())
    # channel = grpc.secure_channel("api.example.com:443", creds)

    return user_pb2_grpc.UserServiceStub(channel)

# Unary call
stub = get_user_client()
try:
    user = stub.GetUser(
        user_pb2.GetUserRequest(user_id="42"),
        timeout=5.0,                         # deadline in seconds
        metadata=[("x-request-id", "abc")]   # like HTTP headers
    )
    print(user.email)
except grpc.RpcError as e:
    print(f"gRPC error: {e.code()} — {e.details()}")

# Server streaming
for user in stub.ListUsers(user_pb2.ListUsersRequest(page_size=100)):
    print(user.id, user.email)

# Client streaming
def generate_users():
    for email in ["a@x.com", "b@x.com", "c@x.com"]:
        yield user_pb2.CreateUserRequest(email=email, name=email.split("@")[0])

response = stub.BulkCreateUsers(generate_users())
print(f"Created: {response.created_count}")
```

---

## gRPC Status Codes

| Code | Name | Meaning | HTTP Equivalent |
|------|------|---------|-----------------|
| 0 | OK | Success | 200 |
| 1 | CANCELLED | Client cancelled | 499 |
| 2 | UNKNOWN | Unknown error | 500 |
| 3 | INVALID_ARGUMENT | Bad request | 400 |
| 4 | DEADLINE_EXCEEDED | Timeout | 504 |
| 5 | NOT_FOUND | Resource not found | 404 |
| 6 | ALREADY_EXISTS | Conflict | 409 |
| 7 | PERMISSION_DENIED | Forbidden | 403 |
| 9 | FAILED_PRECONDITION | State mismatch | 400 |
| 10 | ABORTED | Concurrency conflict | 409 |
| 14 | UNAVAILABLE | Service down | 503 |
| 16 | UNAUTHENTICATED | Missing/invalid creds | 401 |

---

## Unary vs Streaming Comparison

| Type | Request | Response | Use Case |
|------|---------|----------|----------|
| Unary | Single message | Single message | Standard request/response (get, create, update) |
| Server streaming | Single message | Stream of messages | Large result sets, real-time feed, file download |
| Client streaming | Stream of messages | Single message | File upload, bulk insert, telemetry ingestion |
| Bidirectional | Stream of messages | Stream of messages | Chat, collaborative editing, game state sync |

---

## gRPC vs REST Comparison

| Dimension | gRPC | REST |
|-----------|------|------|
| Protocol | HTTP/2 | HTTP/1.1 or HTTP/2 |
| Data format | Protocol Buffers (binary) | JSON (text) |
| Schema contract | Required (.proto) | Optional (OpenAPI) |
| Code generation | Built-in | Optional (OpenAPI generators) |
| Performance | Faster (binary, multiplexing) | Slower (text, no multiplexing) |
| Browser support | Via gRPC-Web proxy | Native |
| Streaming | Native (4 modes) | SSE / WebSocket workarounds |
| Human readability | Low (binary wire format) | High (JSON) |
| Tooling | Growing | Mature (curl, Postman, etc.) |
| Best for | Internal microservice calls | Public APIs, browser clients |

---

## When to Use / Avoid

| Scenario | Use gRPC | Use REST |
|----------|----------|----------|
| Internal service-to-service calls | Yes | No |
| High-throughput, low-latency internal API | Yes | No |
| Browser/mobile client direct access | No (use gRPC-Web or REST) | Yes |
| Public API | No | Yes |
| Strongly typed contract needed | Yes | Optional (OpenAPI) |
| Streaming data (telemetry, events) | Yes | Limited |
| Team unfamiliar with protobuf | No | Yes |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← GraphQL](../13_graphql/cheatsheet.md) &nbsp;|&nbsp; **Next:** [API Gateway →](../15_api_gateway/cheatsheet.md)

**Related Topics:** [GraphQL](../13_graphql/) · [API Gateway](../15_api_gateway/) · [Real-Time APIs](../17_websockets/)
