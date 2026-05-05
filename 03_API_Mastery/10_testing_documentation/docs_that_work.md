# 11 — API Documentation

> "A well-designed API without docs is unusable. Good docs are a product." — Every developer who has ever rage-quit a third-party integration.

---

## 1. Why Documentation Matters

Nobody reads the source code of your API. They read the docs. If the docs are wrong, incomplete, or don't have examples, developers will either waste hours guessing or abandon your API for a competitor.

Documentation does four things that code alone cannot:

- Tells developers what your API is for (context)
- Tells them what the expected inputs and outputs are (contract)
- Shows them how to use it with real examples (tutorial)
- Tells them what changed between versions (changelog)

Treat documentation as a first-class deliverable. Ship it when you ship the endpoint.

---

## 2. OpenAPI (Swagger) 3.0 — The Standard

OpenAPI 3.0 is a YAML or JSON specification that describes your entire API in a machine-readable format. It has become the industry standard for REST API documentation.

**What OpenAPI gives you:**

- Interactive documentation via Swagger UI or Redoc (try out endpoints in the browser)
- Client SDK generation in Python, JavaScript, Go, Java, and more
- Server stub generation
- Validation tooling
- A contract your entire team can reason about

**A minimal OpenAPI 3.0 spec:**

```yaml
openapi: 3.0.3
info:
  title: Orders API
  version: 1.0.0
  description: Manage customer orders.

paths:
  /orders:
    post:
      summary: Create an order
      operationId: createOrder
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateOrderRequest'
            example:
              customer_id: 42
              items:
                - product_id: 101
                  quantity: 2
      responses:
        '201':
          description: Order created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Order'
        '400':
          description: Validation error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /orders/{order_id}:
    get:
      summary: Get an order by ID
      parameters:
        - name: order_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: The order
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Order'
        '404':
          description: Order not found

components:
  schemas:
    CreateOrderRequest:
      type: object
      required: [customer_id, items]
      properties:
        customer_id:
          type: integer
        items:
          type: array
          items:
            $ref: '#/components/schemas/OrderItem'

    OrderItem:
      type: object
      required: [product_id, quantity]
      properties:
        product_id:
          type: integer
        quantity:
          type: integer
          minimum: 1

    Order:
      type: object
      properties:
        id:
          type: integer
        customer_id:
          type: integer
        status:
          type: string
          enum: [pending, confirmed, shipped, delivered, cancelled]
        total:
          type: number
        created_at:
          type: string
          format: date-time

    ErrorResponse:
      type: object
      properties:
        error:
          type: string
        details:
          type: array
          items:
            type: string
```

You can render this instantly with Swagger UI (open-source) or paste it into https://editor.swagger.io.

> 📝 **Practice:** [Q66 · openapi-benefits](../api_practice_questions_100.md#q66--normal--openapi-benefits)

---

## 3. Auto-Generating Docs in Python

Writing OpenAPI YAML by hand for every endpoint is tedious and error-prone. Python frameworks can generate it automatically.

### FastAPI — Zero Config

FastAPI generates OpenAPI docs directly from your type hints and Pydantic models. You write normal Python; the docs appear automatically.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

app = FastAPI(
    title="Orders API",
    description="Manage customer orders. All prices in USD cents.",
    version="1.0.0"
)

class OrderStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    shipped = "shipped"

class OrderItemIn(BaseModel):
    product_id: int = Field(..., description="ID of the product to order")
    quantity: int = Field(..., ge=1, description="Must be at least 1")

class OrderIn(BaseModel):
    customer_id: int
    items: list[OrderItemIn]

class OrderOut(BaseModel):
    id: int
    customer_id: int
    status: OrderStatus
    total_cents: int
    created_at: datetime

    class Config:
        # Example shown in Swagger UI
        json_schema_extra = {
            "example": {
                "id": 1,
                "customer_id": 42,
                "status": "pending",
                "total_cents": 1999,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }

@app.post(
    "/orders",
    response_model=OrderOut,
    status_code=201,
    summary="Create a new order",
    description="Creates an order for a customer. Returns the order with its assigned ID and initial status."
)
def create_order(order: OrderIn):
    # ... implementation
    pass

@app.get(
    "/orders/{order_id}",
    response_model=OrderOut,
    responses={
        404: {"description": "Order not found"}
    }
)
def get_order(order_id: int):
    raise HTTPException(status_code=404, detail="Order not found")
```

Visit `http://localhost:8000/docs` for Swagger UI, or `http://localhost:8000/redoc` for Redoc.

The OpenAPI JSON itself is at `/openapi.json` — use it to generate client SDKs.

### Flask — flasgger

```python
from flask import Flask, jsonify
from flasgger import Swagger, swag_from

app = Flask(__name__)
swagger = Swagger(app)

@app.get("/orders/<int:order_id>")
@swag_from({
    "summary": "Get order by ID",
    "parameters": [
        {"name": "order_id", "in": "path", "type": "integer", "required": True}
    ],
    "responses": {
        200: {"description": "The order"},
        404: {"description": "Order not found"}
    }
})
def get_order(order_id):
    return jsonify({"id": order_id})
```

Or use `flask-restx`, which provides a higher-level DSL and generates OpenAPI automatically from resource classes.

---

## 4. Writing Good API Docs

Auto-generation gives you structure. Good docs require you to fill in the meaning.

**Every endpoint should document:**

```
Name        — Short, action-oriented: "Create a payment intent"
Description — When and why to use this endpoint, not just what it does
Parameters  — Name, type, required?, default, validation rules, example
Request body — Full schema with field descriptions and a real example
Response    — Schema for each status code (200, 201, 400, 401, 404, 422, 500)
Error cases — Every error this endpoint can return, and what causes it
Example     — A real request and a real response, not just a schema
```

**Don't document what — document why and when.**

Bad:
```
POST /payments
Creates a payment.
```

Good:
```
POST /payments
Creates a payment intent and charges the provided payment method.
Use this endpoint when the customer confirms checkout. The payment is
processed synchronously — a 200 response means the charge succeeded.

If the card is declined, you receive a 402 with a decline_code.
If the payment requires 3D Secure authentication, you receive a 200
with status: "requires_action" and a redirect_url.
```

**Include real examples, not just schemas.** Schemas tell developers what's possible. Examples show developers what's normal.

```yaml
# In your OpenAPI spec — add examples alongside schemas
example:
  request:
    amount: 2000
    currency: "usd"
    payment_method: "pm_card_visa"
    description: "Order #1042 — 2x Widget"
  response:
    id: "pi_3NqXkB2eZvKYlo2C1234"
    status: "succeeded"
    amount: 2000
    currency: "usd"
    created: 1706180400
```

---

## 5. Developer Experience

Good docs cover the reference. Great docs help developers get unblocked fast.

### Quickstart Guide

Get a developer to their first successful API call in under 5 minutes.

```markdown
## Quickstart — Your First API Call

1. Get your API key from the dashboard.

2. Make your first request:

curl -X GET https://api.example.com/v1/products \
  -H "Authorization: Bearer YOUR_API_KEY"

3. You'll see:

{
  "data": [...],
  "total": 42,
  "page": 1
}

That's it. You're in.
```

### Authentication Guide

Never make developers guess how to authenticate. Show the exact header, the exact format, copy-paste ready.

```markdown
## Authentication

All requests require an API key in the Authorization header:

Authorization: Bearer sk_live_abc123xyz

Getting your key: Dashboard → Settings → API Keys → Create Key

Test keys (sk_test_...) hit a sandbox environment — no real charges.
Live keys (sk_live_...) are for production.

Never commit API keys to source control. Use environment variables:

export EXAMPLE_API_KEY=sk_live_abc123xyz
```

### Error Reference

List every error code your API produces with a human explanation and a recommended action.

```markdown
## Error Reference

| Code | HTTP | Meaning | What to do |
|------|------|---------|------------|
| invalid_api_key | 401 | API key is missing or invalid | Check the key in your dashboard |
| resource_not_found | 404 | The requested resource doesn't exist | Check the ID |
| validation_error | 400 | Request body failed validation | See the `details` array for specifics |
| rate_limited | 429 | Too many requests | Retry after the `Retry-After` header value |
| card_declined | 402 | Payment method was declined | Show the `decline_code` to your support team |
| internal_error | 500 | Something went wrong on our end | Retry with exponential backoff; contact support if it persists |
```

### Changelog

Tell developers exactly what changed and when. Version without a changelog is a breaking change waiting to happen.

```markdown
## Changelog

### v2.0.0 — 2024-03-01
BREAKING: `user_name` field renamed to `username` across all endpoints.
BREAKING: Removed deprecated `GET /v1/users` (use `GET /v2/users`).
NEW: Cursor-based pagination on all list endpoints.
NEW: `POST /v2/payments/refund` endpoint.

### v1.5.0 — 2024-01-15
NEW: `GET /orders?status=` filter parameter.
FIX: `created_at` now returns ISO 8601 format consistently.
DEPRECATED: `GET /v1/users` — will be removed in v2.0.
```

---

## 6. The Stripe Docs Model

Stripe's API documentation is widely considered the gold standard. Here is what they get right:

**Consistent, predictable structure.** Every resource has the same shape — object description, attributes table, list of methods. Once you understand one resource, you understand them all.

**Real code examples in every language.** Every endpoint shows working code in curl, Python, Node.js, Ruby, Go, and Java, side by side. Developers copy and run the example, then modify it.

**Contextual explanations, not just schemas.** The docs explain the business scenario, not just the API call. "Use payment intents when you want to collect payment details before confirming a charge" — that sentence saves hours of confusion.

**A separate testing environment.** Test API keys, test card numbers, simulated failure scenarios — everything to let developers build with confidence before going live.

**The error reference is a first-class document.** Stripe lists every error code, what causes it, and what action the developer should take. No guessing.

**Versioning is explicit and documented.** Stripe versions by date (`2024-01-01`). Each version has a changelog entry. Older versions are supported indefinitely for existing integrations.

You don't need Stripe's team to apply these principles. Even a single-developer project benefits from consistent structure, real examples, and an error reference.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Testing APIs](../10_testing_documentation/testing_apis.md) &nbsp;|&nbsp; **Next:** [Security in Production →](../11_api_security_production/security_hardening.md)

**Related Topics:** [Testing APIs](../10_testing_documentation/testing_apis.md) · [REST Best Practices](../03_rest_best_practices/patterns.md) · [FastAPI Core Guide](../07_fastapi/core_guide.md)
