# ⚡ Cheatsheet: API Gateway

---

## Learning Priority

**Must Learn** — fundamental to any production microservice setup:
Gateway pattern concept · rate limiting headers · common gateway features

**Should Learn** — comes up in system design interviews:
BFF (Backend for Frontend) pattern · Kong vs AWS API Gateway vs Nginx comparison

**Good to Know** — useful when owning the infra:
Plugin chains · service mesh vs API gateway distinction · mTLS termination at gateway

**Reference** — look up when needed:
Kong plugin API · AWS API Gateway resource policies · Nginx `limit_req_zone` syntax

---

## API Gateway Pattern

```
Client
  |
  | (single entry point — HTTPS on port 443)
  v
+------------------+
|   API Gateway    |  — auth, rate limiting, routing, SSL termination,
|                  |    logging, tracing, caching, request transformation
+------------------+
  |         |         |
  v         v         v
Service A  Service B  Service C
(users)    (orders)   (inventory)
```

**What the gateway handles (so services don't have to):**
- TLS termination
- Authentication / token validation
- Rate limiting per client
- Request routing by path/header/method
- Load balancing across service instances
- Logging and distributed tracing injection
- Response caching
- Request/response transformation

---

## Rate Limit Header Names

```
# Standard (IETF draft — prefer these)
RateLimit-Limit: 1000            # quota for the current window
RateLimit-Remaining: 847         # requests left
RateLimit-Reset: 1706180460      # Unix timestamp of window reset

# Widely used non-standard (X- prefix) — you will see these in practice
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1706180460

# On 429 Too Many Requests — always include this
Retry-After: 37                  # seconds until client can retry
```

---

## BFF (Backend for Frontend) Pattern

```
Mobile App          Web App            Admin Dashboard
    |                  |                     |
    v                  v                     v
+----------+    +----------+    +--------------------+
| Mobile   |    | Web BFF  |    | Admin BFF          |
| BFF      |    | (full    |    | (aggregated views, |
| (compact |    |  data)   |    |  bulk operations)  |
|  payloads|    +----------+    +--------------------+
+----------+          |                  |
         \            |                 /
          \     +-----+----------------+
           \    |     Internal APIs    |
            \   | (users, orders,      |
             +->|  inventory, billing) |
                +---------------------+
```

**When to use BFF:**
- Different clients need different response shapes from the same data
- Mobile needs compact payloads; web needs richer data
- Reduces over-fetching without full GraphQL adoption
- Aggregates multiple microservice calls into one client request

**When not to use BFF:**
- Single client type
- Small team (extra service to maintain)
- Simple data requirements — a REST API is enough

---

## Common Gateway Features Table

| Feature | Description | Benefit |
|---------|-------------|---------|
| SSL/TLS termination | Decrypt HTTPS at gateway; services use HTTP internally | Simplifies service certs |
| Authentication | Validate JWT / API key before routing | Services trust gateway, skip auth logic |
| Rate limiting | Per-client / per-IP / per-route quotas | Protects backend services |
| Routing | Route by path, header, hostname, method | Single entry point for all services |
| Load balancing | Round-robin, least-conn, weighted | No need for separate LB per service |
| Circuit breaker | Stop routing to failing services | Prevents cascade failures |
| Retry logic | Retry idempotent requests on 5xx | Improves resilience |
| Request transformation | Add/remove headers, reshape body | Decouple client format from service format |
| Response caching | Cache GET responses by key | Reduce backend load |
| Logging | Structured request logs with trace ID | Unified audit trail |
| Distributed tracing | Inject trace/span headers | End-to-end observability |
| CORS handling | Centralized CORS policy | Services don't implement CORS |
| WAF integration | Block known attack patterns | Security at the edge |

---

## Kong vs AWS API Gateway vs Nginx Comparison

| Dimension | Kong | AWS API Gateway | Nginx |
|-----------|------|-----------------|-------|
| Type | Open-source gateway (Lua/Go plugins) | Managed AWS service | HTTP server / reverse proxy |
| Deployment | Self-hosted or Kong Cloud | Fully managed (serverless) | Self-hosted |
| Configuration | Admin API + declarative YAML | AWS Console / CDK / Terraform | `nginx.conf` |
| Auth plugins | JWT, OAuth, API keys, HMAC | Cognito, Lambda authorizers, API keys | Manual (scripting) |
| Rate limiting | Built-in plugin | Built-in (usage plans) | `limit_req_zone` module |
| Extensibility | Plugin system (Lua, Go, JS) | Lambda authorizers | Custom modules (complex) |
| Observability | Prometheus, Datadog, OTEL plugins | CloudWatch native | Log format config |
| Cost | Free (OSS); paid enterprise | Per request + data transfer | Free |
| Learning curve | Medium | Medium (AWS concepts) | Low to medium |
| Best for | Multi-cloud, complex plugin needs | AWS-native stack | Simple reverse proxy, static/dynamic mix |
| gRPC support | Yes | Yes (REST to gRPC transcoding) | Yes (with config) |
| WebSocket support | Yes | Yes | Yes |

---

## Kong Declarative Config Skeleton

```yaml
# kong.yaml (deck sync)
_format_version: "3.0"

services:
  - name: user-service
    url: http://user-service:8080
    routes:
      - name: user-routes
        paths:
          - /api/v1/users
        methods:
          - GET
          - POST
          - PUT
          - DELETE
    plugins:
      - name: jwt
        config:
          secret_is_base64: false
      - name: rate-limiting
        config:
          minute: 1000
          hour: 10000
          policy: redis
          redis_host: redis
      - name: request-transformer
        config:
          add:
            headers:
              - "X-Gateway-Version:1.0"
```

---

## AWS API Gateway Skeleton (CloudFormation / SAM)

```yaml
# serverless API with Lambda backend
Resources:
  ApiGateway:
    Type: AWS::Serverless::Api
    Properties:
      StageName: prod
      Auth:
        DefaultAuthorizer: CognitoAuthorizer
        Authorizers:
          CognitoAuthorizer:
            UserPoolArn: !GetAtt UserPool.Arn
      MethodSettings:
        - HttpMethod: "*"
          ResourcePath: "/*"
          ThrottlingBurstLimit: 500
          ThrottlingRateLimit: 1000

  UserFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: handlers.user
      Runtime: python3.11
      Events:
        GetUser:
          Type: Api
          Properties:
            RestApiId: !Ref ApiGateway
            Path: /users/{userId}
            Method: GET
```

---

## Nginx Reverse Proxy with Rate Limiting

```nginx
http {
    # Rate limit zones (defined at http level)
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;
    limit_req_zone $http_authorization zone=token_limit:10m rate=1000r/m;

    upstream api_backend {
        least_conn;
        server api-1:8000;
        server api-2:8000;
        server api-3:8000;
        keepalive 32;
    }

    server {
        listen 443 ssl;
        server_name api.example.com;

        ssl_certificate /etc/ssl/certs/api.crt;
        ssl_certificate_key /etc/ssl/private/api.key;

        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            limit_req_status 429;

            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            proxy_connect_timeout 5s;
            proxy_read_timeout 60s;
        }
    }
}
```

---

## When to Use / Avoid

| Pattern | Use When | Avoid When |
|---------|----------|------------|
| API Gateway | Multiple microservices, centralized auth/logging | Single monolith (unnecessary complexity) |
| BFF | Multiple client types with different data needs | Single client or simple uniform API |
| Kong (self-hosted) | Multi-cloud, need custom plugins, data sovereignty | All-in on AWS (use API Gateway instead) |
| AWS API Gateway | AWS Lambda/ECS backend, need minimal infra ops | High-volume, latency-sensitive (adds ~10ms) |
| Nginx as gateway | Simple routing, already using Nginx, low traffic | Complex auth/plugin needs (use Kong) |
| Service mesh (Istio) | mTLS between services, fine-grained traffic policy | Teams new to Kubernetes (high complexity) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← gRPC](../14_grpc/cheatsheet.md) &nbsp;|&nbsp; **Next:** [API Design Patterns →](../16_api_design_patterns/cheatsheet.md)

**Related Topics:** [Production Deployment](../12_production_deployment/) · [API Security](../11_api_security_production/) · [Real-World APIs](../18_real_world_apis/)
