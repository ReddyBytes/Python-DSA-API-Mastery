<a id="top"></a>

# API Testing and Documentation

> "Padma had a rule on her team in Hyderabad: no endpoint ships without a test AND a doc page. 'If you cannot prove it works,' she told every new hire, 'and you cannot explain how to use it, then it does not exist.'"

## Table of Contents

- [1. Why API Tests Are Different](#why-api-tests-are-different)
- [2. Unit Tests for API Logic](#unit-tests-for-api-logic)
- [3. Integration Tests](#integration-tests)
  - [FastAPI TestClient](#fastapi-testclient)
  - [Flask test_client](#flask-test-client)
- [4. Contract Testing with Pact](#contract-testing-with-pact)
- [5. Testing Patterns](#testing-patterns)
  - [Test Data Setup and Teardown](#test-data-setup-and-teardown)
  - [Testing Authentication](#testing-authentication)
  - [Testing Error Cases](#testing-error-cases)
  - [Mocking External APIs](#mocking-external-apis)
- [6. Load Testing APIs](#load-testing-apis)
- [7. Endpoint Testing Checklist](#endpoint-testing-checklist)
- [8. Why Documentation Matters](#why-documentation-matters)
- [9. OpenAPI Swagger 3.0 The Standard](#openapi-swagger-30-the-standard)
- [10. Auto-Generating Docs in Python](#auto-generating-docs-in-python)
  - [FastAPI Zero Config](#fastapi-zero-config)
  - [Flask flasgger](#flask-flasgger)
- [11. Writing Good API Docs](#writing-good-api-docs)
- [12. Developer Experience](#developer-experience)
  - [Quickstart Guide](#quickstart-guide)
  - [Authentication Guide](#authentication-guide)
  - [Error Reference](#error-reference)
  - [Changelog](#changelog)
- [13. The Stripe Docs Model](#the-stripe-docs-model)
- [14. Summary](#summary)

<a id="why-api-tests-are-different"></a>

## 1. Why API Tests Are Different

Padma's first day at a new company, the senior dev told her "we test our APIs just like regular functions." She watched him write a test that checked a returned dictionary's keys. The test passed. Then they deployed, and the frontend team filed three bugs: wrong status code, missing pagination headers, and a field renamed without notice.

"You tested the logic," Padma told him gently. "You did not test the contract."

Testing a web API is not the same as testing a pure function. A few things make it distinct:

**You are testing over a network protocol.** Even in local tests, HTTP semantics matter — status codes, headers, content-type, redirects. A function returning `{"error": "not found"}` with a `200` status is wrong, even if the body looks right.

**State lives in a database.** Unlike a pure function, a `POST /orders` request writes to a database. Your tests need to control that state — set it up before, clean it up after.

**You are testing a contract.** Your API is a contract between your backend and every consumer (frontend, mobile app, other services). Breaking the contract silently is the most expensive bug you can ship.

**Three layers of testing for APIs:**

```
+---------------------------------------------------------+
|  Contract Tests  -- does the shape match what            |
|                    consumers expect?                     |
+---------------------------------------------------------+
|  Integration Tests -- does the full HTTP stack work?     |
|                      (routes, auth, DB, serializers)     |
+---------------------------------------------------------+
|  Unit Tests        -- does the business logic work?      |
|                      (no HTTP, no DB)                    |
+---------------------------------------------------------+
```

Run all three. They catch different things.

[Back to Top](#top)

<a id="unit-tests-for-api-logic"></a>

## 2. Unit Tests for API Logic

The business logic in your API — validation, calculations, transformations — should be testable without spinning up a server or touching a database. Extract it into plain functions or service classes.

Padma calls these "desk tests" — you should be able to run them at your desk with no network, no Docker, no database. If you cannot, your logic is too coupled to the framework.

```python
# services/order_service.py

def calculate_order_total(items: list[dict], discount_pct: float = 0) -> float:
    """Calculate total price after discount."""
    subtotal = sum(item["price"] * item["quantity"] for item in items)
    discount = subtotal * (discount_pct / 100)
    return round(subtotal - discount, 2)


def validate_order(items: list[dict]) -> list[str]:
    """Return list of validation errors. Empty list = valid."""
    errors = []
    if not items:
        errors.append("Order must contain at least one item.")
    for item in items:
        if item.get("quantity", 0) <= 0:
            errors.append(f"Item '{item.get('name')}' has invalid quantity.")
        if item.get("price", 0) < 0:
            errors.append(f"Item '{item.get('name')}' has negative price.")
    return errors
```

```python
# tests/test_order_service.py
import pytest
from services.order_service import calculate_order_total, validate_order

def test_total_no_discount():
    items = [{"price": 10.0, "quantity": 2}, {"price": 5.0, "quantity": 1}]
    assert calculate_order_total(items) == 25.0

def test_total_with_discount():
    items = [{"price": 100.0, "quantity": 1}]
    assert calculate_order_total(items, discount_pct=10) == 90.0

def test_empty_order_is_invalid():
    errors = validate_order([])
    assert "Order must contain at least one item." in errors

def test_negative_quantity_is_invalid():
    items = [{"name": "Widget", "price": 5.0, "quantity": -1}]
    errors = validate_order(items)
    assert len(errors) == 1
```

Keep these tests fast. No network, no database, no I/O. They should run in milliseconds.

[Back to Top](#top)

<a id="integration-tests"></a>

## 3. Integration Tests

Integration tests call your actual running API (or a test version of it) over HTTP. They verify that routes, middleware, serializers, and the database all work together.

"Unit tests tell you the engine works," Padma explains. "Integration tests tell you the car actually drives when you turn the key."

<a id="fastapi-testclient"></a>

**FastAPI TestClient**

FastAPI's `TestClient` wraps `httpx` and runs your app in-process. No separate server needed.

```python


# main.py (simplified)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

ITEMS = {}

@app.post("/items", status_code=201)
def create_item(item: Item):
    item_id = len(ITEMS) + 1
    ITEMS[item_id] = item
    return {"id": item_id, **item.dict()}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in ITEMS:
        raise HTTPException(status_code=404, detail="Item not found")
    return ITEMS[item_id]
```

> **Practice:** [Q47 - testing-fastapi-testclient](../api_practice_questions_100.md#q47--normal--testing-fastapi-testclient)


```python
# tests/test_items_api.py
import pytest
from fastapi.testclient import TestClient
from main import app, ITEMS

@pytest.fixture(autouse=True)
def clear_items():
    """Reset in-memory store before each test."""
    ITEMS.clear()
    yield
    ITEMS.clear()

client = TestClient(app)

def test_create_item_returns_201():
    response = client.post("/items", json={"name": "Widget", "price": 9.99})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Widget"
    assert data["price"] == 9.99
    assert "id" in data

def test_get_item_not_found_returns_404():
    response = client.get("/items/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

def test_create_then_retrieve():
    create_resp = client.post("/items", json={"name": "Gadget", "price": 19.99})
    item_id = create_resp.json()["id"]

    get_resp = client.get(f"/items/{item_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Gadget"
```

<a id="flask-test-client"></a>

**Flask test_client**

```python
# app.py
from flask import Flask, jsonify, request

app = Flask(__name__)
USERS = {}

@app.post("/users")
def create_user():
    data = request.get_json()
    if not data or "email" not in data:
        return jsonify({"error": "email is required"}), 400
    uid = len(USERS) + 1
    USERS[uid] = data
    return jsonify({"id": uid, **data}), 201
```

```python
# tests/test_users_api.py
import pytest
from app import app, USERS

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c
    USERS.clear()

def test_create_user_success(client):
    resp = client.post("/users", json={"email": "alice@example.com"})
    assert resp.status_code == 201
    assert resp.get_json()["email"] == "alice@example.com"

def test_create_user_missing_email(client):
    resp = client.post("/users", json={"name": "Alice"})
    assert resp.status_code == 400
    assert "error" in resp.get_json()
```

[Back to Top](#top)

<a id="contract-testing-with-pact"></a>

## 4. Contract Testing with Pact

Unit and integration tests verify that your code works. Contract tests verify that your API works for the people consuming it.

Padma learned this the hard way. Her backend team renamed `user_name` to `username` in a Friday deploy. The mobile team did not find out until Monday morning when their app crashed for 200,000 users. "We had 100% test coverage," she says. "But none of those tests represented the consumer's expectations."

**The problem:** Your frontend team builds against your API. You change a field name from `user_name` to `username` without telling them. Their app breaks in production.

**The solution:** Consumer-driven contract testing. The consumer (frontend) defines what they expect from the API (the provider). Pact captures this as a contract file. The provider runs tests against the contract to verify it still holds.

```
Consumer (Frontend)              Provider (Backend)
---------------------            ---------------------
"I expect GET /users/1           "I will run tests to
 to return a JSON object         prove I still satisfy
 with 'id', 'email',             the consumer's
 and 'username' fields."  -->    recorded expectations."
         |                                |
         +---- Pact file (JSON) ----------+
```

**What breaks without contract tests:**

- Backend renames `user_name` to `username`. Frontend breaks.
- Backend removes a field the mobile app depends on. App crashes.
- Backend changes the shape of an error response. Frontend shows a blank screen instead of an error message.

**Pact concept in Python (consumer side):**

```python


# consumer/test_user_consumer.py
import pytest
from pact import Consumer, Provider

pact = Consumer("frontend").has_pact_with(Provider("user-api"))

def test_get_user():
    expected = {
        "id": 1,
        "email": "alice@example.com",
        "username": "alice"
    }

    (pact
     .given("user 1 exists")
     .upon_receiving("a request for user 1")
     .with_request("GET", "/users/1")
     .will_respond_with(200, body=expected))

    with pact:
        import requests
        result = requests.get(pact.uri + "/users/1")
        assert result.json()["username"] == "alice"
```

> **Practice:** [Q67 - contract-testing](../api_practice_questions_100.md#q67--thinking--contract-testing)


The pact file is published to a Pact Broker. The backend (provider) team runs verification against it in CI. If the provider changes something the consumer expects, the CI pipeline fails before the change reaches production.

Pact is most valuable in microservice architectures or teams with separate frontend/backend development.

[Back to Top](#top)

<a id="testing-patterns"></a>

## 5. Testing Patterns

Padma keeps a "patterns playbook" on her team's wiki. Every time someone invents a new testing trick, it goes in the playbook. These are the patterns that come up on every single API project.

<a id="test-data-setup-and-teardown"></a>

**Test Data Setup and Teardown**

Use pytest fixtures to manage test data lifecycle:

```python
@pytest.fixture
def db_session():
    """Create a fresh DB session per test, roll back after."""
    session = SessionLocal()
    session.begin_nested()   # savepoint
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def sample_user(db_session):
    user = User(email="test@example.com", name="Test User")
    db_session.add(user)
    db_session.flush()
    return user
```

For integration tests with a real database, consider using a separate test database (configured via `DATABASE_URL` environment variable) and running migrations before the test suite.

<a id="testing-authentication"></a>

**Testing Authentication**

Pass tokens directly in test headers. Don't test the auth server — test that your API correctly enforces auth.

```python
# Generate a test token (for JWT-based auth)
import jwt

def make_token(user_id: int, secret: str = "test-secret") -> str:
    return jwt.encode({"sub": str(user_id), "role": "user"}, secret, algorithm="HS256")

def test_protected_endpoint_with_valid_token(client):
    token = make_token(user_id=42)
    resp = client.get("/profile", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

def test_protected_endpoint_without_token(client):
    resp = client.get("/profile")
    assert resp.status_code == 401

def test_protected_endpoint_with_wrong_role(client):
    token = make_token(user_id=42)  # "user" role, not "admin"
    resp = client.delete("/admin/users/1", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
```

<a id="testing-error-cases"></a>

**Testing Error Cases**

Error paths are where most bugs live. Test them explicitly.

```python
def test_400_validation_error(client):
    # Missing required field
    resp = client.post("/orders", json={})
    assert resp.status_code == 400
    assert "errors" in resp.json()

def test_404_not_found(client):
    resp = client.get("/orders/99999")
    assert resp.status_code == 404

def test_409_duplicate_resource(client):
    client.post("/users", json={"email": "alice@example.com"})
    resp = client.post("/users", json={"email": "alice@example.com"})
    assert resp.status_code == 409

def test_500_handled_gracefully(client, monkeypatch):
    # Simulate an internal error
    monkeypatch.setattr("services.order_service.get_db", lambda: (_ for _ in ()).throw(Exception("DB down")))
    resp = client.get("/orders")
    assert resp.status_code == 500
    # Should not leak a stack trace
    assert "traceback" not in resp.json().get("detail", "").lower()
```

<a id="mocking-external-apis"></a>

**Mocking External APIs**

When your API calls a third-party service (Stripe, SendGrid, Twilio), you don't want real HTTP calls in tests. Use `responses` or `httpretty` to intercept them.

```python
# Using the `responses` library
import responses as resp_mock
import requests

@resp_mock.activate
def test_email_notification_sent():
    # Mock the SendGrid API
    resp_mock.add(
        resp_mock.POST,
        "https://api.sendgrid.com/v3/mail/send",
        json={"message": "Queued"},
        status=202
    )

    result = send_welcome_email("alice@example.com")

    assert result is True
    assert len(resp_mock.calls) == 1
    assert "alice@example.com" in resp_mock.calls[0].request.body
```

```python
# Using httpretty
import httpretty
import json

@httpretty.activate
def test_payment_gateway_failure():
    httpretty.register_uri(
        httpretty.POST,
        "https://api.stripe.com/v1/charges",
        body=json.dumps({"error": {"message": "Card declined"}}),
        status=402
    )

    with pytest.raises(PaymentDeclinedError):
        charge_card(amount=100, token="tok_visa")
```

[Back to Top](#top)

<a id="load-testing-apis"></a>

## 6. Load Testing APIs

Functional tests verify correctness. Load tests verify that your API holds up under traffic.

Padma runs load tests every sprint, not just before launch. "Performance bugs are like termites," she says. "By the time you notice them, the damage is already done."

**Locust** — write load tests in Python:

```python
# locustfile.py
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def get_products(self):
        self.client.get("/products")

    @task(1)
    def create_order(self):
        self.client.post("/orders", json={
            "product_id": 1,
            "quantity": 2
        })
```

Run with: `locust -f locustfile.py --host=http://localhost:8000`

**k6** — JavaScript-based, more CI-friendly, runs as a binary:

```javascript
// k6 script
import http from 'k6/http';
import { check } from 'k6';

export let options = { vus: 50, duration: '30s' };

export default function () {
    let res = http.get('http://localhost:8000/products');
    check(res, { 'status is 200': (r) => r.status === 200 });
}
```

Run with: `k6 run script.js`

Use load tests to find: N+1 query problems, missing database indexes, memory leaks under sustained traffic, and rate limit thresholds.

[Back to Top](#top)

<a id="endpoint-testing-checklist"></a>

## 7. Endpoint Testing Checklist

For every API endpoint, verify:

```
Happy path
  [ ] Returns correct status code (200, 201, 204...)
  [ ] Response body has the expected fields and types
  [ ] Side effects occurred (DB write, email sent, etc.)

Validation
  [ ] Missing required fields -> 400 with clear error message
  [ ] Invalid field types -> 400
  [ ] Out-of-range values -> 400
  [ ] Malformed JSON body -> 400

Authentication and Authorization
  [ ] No token -> 401
  [ ] Invalid/expired token -> 401
  [ ] Valid token, wrong role/scope -> 403
  [ ] Accessing another user's resource -> 403 or 404

Edge cases
  [ ] Resource not found -> 404
  [ ] Duplicate creation -> 409
  [ ] Concurrent modification -> 409 or 422

Error handling
  [ ] 500 errors don't leak stack traces
  [ ] Error responses follow your error schema consistently
```

Padma prints this checklist and tapes it next to every developer's monitor. "If your PR does not cover every box, it does not get merged."

[Back to Top](#top)

<a id="why-documentation-matters"></a>

## 8. Why Documentation Matters

Padma has a second rule, equal in importance to her testing rule: "Code without docs is a gift that expires in six months."

Nobody reads the source code of your API. They read the docs. If the docs are wrong, incomplete, or don't have examples, developers will either waste hours guessing or abandon your API for a competitor.

Documentation does four things that code alone cannot:

- Tells developers what your API is for (context)
- Tells them what the expected inputs and outputs are (contract)
- Shows them how to use it with real examples (tutorial)
- Tells them what changed between versions (changelog)

Treat documentation as a first-class deliverable. Ship it when you ship the endpoint.

```
+------------------------------------------------------+
|              The Documentation Stack                  |
+------------------------------------------------------+
|  Changelog      -- what changed and when             |
+------------------------------------------------------+
|  Guides         -- quickstart, auth, errors          |
+------------------------------------------------------+
|  API Reference  -- every endpoint, param, response   |
+------------------------------------------------------+
|  OpenAPI Spec   -- machine-readable contract         |
+------------------------------------------------------+
```

[Back to Top](#top)

<a id="openapi-swagger-30-the-standard"></a>

## 9. OpenAPI Swagger 3.0 The Standard

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

> **Practice:** [Q66 - openapi-benefits](../api_practice_questions_100.md#q66--normal--openapi-benefits)

[Back to Top](#top)

<a id="auto-generating-docs-in-python"></a>

## 10. Auto-Generating Docs in Python

Writing OpenAPI YAML by hand for every endpoint is tedious and error-prone. Python frameworks can generate it automatically.

<a id="fastapi-zero-config"></a>

**FastAPI Zero Config**

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

<a id="flask-flasgger"></a>

**Flask flasgger**

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

[Back to Top](#top)

<a id="writing-good-api-docs"></a>

## 11. Writing Good API Docs

Auto-generation gives you structure. Good docs require you to fill in the meaning.

Padma reviews every auto-generated doc page before it ships. "Swagger UI with no descriptions is like a menu with no prices and no dish names — just ingredient lists."

**Every endpoint should document:**

```
Name        -- Short, action-oriented: "Create a payment intent"
Description -- When and why to use this endpoint, not just what it does
Parameters  -- Name, type, required?, default, validation rules, example
Request body -- Full schema with field descriptions and a real example
Response    -- Schema for each status code (200, 201, 400, 401, 404, 422, 500)
Error cases -- Every error this endpoint can return, and what causes it
Example     -- A real request and a real response, not just a schema
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
processed synchronously -- a 200 response means the charge succeeded.

If the card is declined, you receive a 402 with a decline_code.
If the payment requires 3D Secure authentication, you receive a 200
with status: "requires_action" and a redirect_url.
```

**Include real examples, not just schemas.** Schemas tell developers what's possible. Examples show developers what's normal.

```yaml
# In your OpenAPI spec -- add examples alongside schemas
example:
  request:
    amount: 2000
    currency: "usd"
    payment_method: "pm_card_visa"
    description: "Order #1042 -- 2x Widget"
  response:
    id: "pi_3NqXkB2eZvKYlo2C1234"
    status: "succeeded"
    amount: 2000
    currency: "usd"
    created: 1706180400
```

[Back to Top](#top)

<a id="developer-experience"></a>

## 12. Developer Experience

Good docs cover the reference. Great docs help developers get unblocked fast.

Padma measures developer experience by one metric: "How many minutes from sign-up to first successful API call?" If the answer is more than five, the docs have failed.

<a id="quickstart-guide"></a>

**Quickstart Guide**

Get a developer to their first successful API call in under 5 minutes.

```markdown
## Quickstart -- Your First API Call

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

<a id="authentication-guide"></a>

**Authentication Guide**

Never make developers guess how to authenticate. Show the exact header, the exact format, copy-paste ready.

```markdown
## Authentication

All requests require an API key in the Authorization header:

Authorization: Bearer sk_live_abc123xyz

Getting your key: Dashboard -> Settings -> API Keys -> Create Key

Test keys (sk_test_...) hit a sandbox environment -- no real charges.
Live keys (sk_live_...) are for production.

Never commit API keys to source control. Use environment variables:

export EXAMPLE_API_KEY=sk_live_abc123xyz
```

<a id="error-reference"></a>

**Error Reference**

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

<a id="changelog"></a>

**Changelog**

Tell developers exactly what changed and when. Version without a changelog is a breaking change waiting to happen.

```markdown
## Changelog

### v2.0.0 -- 2024-03-01
BREAKING: `user_name` field renamed to `username` across all endpoints.
BREAKING: Removed deprecated `GET /v1/users` (use `GET /v2/users`).
NEW: Cursor-based pagination on all list endpoints.
NEW: `POST /v2/payments/refund` endpoint.

### v1.5.0 -- 2024-01-15
NEW: `GET /orders?status=` filter parameter.
FIX: `created_at` now returns ISO 8601 format consistently.
DEPRECATED: `GET /v1/users` -- will be removed in v2.0.
```

[Back to Top](#top)

<a id="the-stripe-docs-model"></a>

## 13. The Stripe Docs Model

Stripe's API documentation is widely considered the gold standard. Padma uses it as the benchmark whenever she sets up docs for a new API. Here is what they get right:

**Consistent, predictable structure.** Every resource has the same shape — object description, attributes table, list of methods. Once you understand one resource, you understand them all.

**Real code examples in every language.** Every endpoint shows working code in curl, Python, Node.js, Ruby, Go, and Java, side by side. Developers copy and run the example, then modify it.

**Contextual explanations, not just schemas.** The docs explain the business scenario, not just the API call. "Use payment intents when you want to collect payment details before confirming a charge" — that sentence saves hours of confusion.

**A separate testing environment.** Test API keys, test card numbers, simulated failure scenarios — everything to let developers build with confidence before going live.

**The error reference is a first-class document.** Stripe lists every error code, what causes it, and what action the developer should take. No guessing.

**Versioning is explicit and documented.** Stripe versions by date (`2024-01-01`). Each version has a changelog entry. Older versions are supported indefinitely for existing integrations.

You don't need Stripe's team to apply these principles. Even a single-developer project benefits from consistent structure, real examples, and an error reference.

[Back to Top](#top)

<a id="summary"></a>

## 14. Summary

Padma's complete philosophy in two sentences: "Test it before you ship it. Document it before they use it."

| Area | Key Takeaway |
|------|-------------|
| Unit tests | Extract logic into pure functions, test without HTTP or DB |
| Integration tests | TestClient (FastAPI) or test_client (Flask), test full HTTP stack |
| Contract tests | Pact captures consumer expectations, prevents silent breaking changes |
| Auth testing | Test enforcement (401/403), not the auth server itself |
| Error testing | Every error path tested explicitly, no leaked stack traces |
| Load testing | Locust (Python) or k6 (JS), run every sprint not just pre-launch |
| OpenAPI | Machine-readable spec, auto-generated from type hints in FastAPI |
| Good docs | Document why and when, not just what; include real examples |
| Developer experience | Quickstart, auth guide, error reference, changelog |
| Stripe model | Consistent structure, multi-language examples, business context |

**Learning Priority:**

- **Must Learn:** unit tests, integration tests (TestClient), auth testing, error path testing, OpenAPI basics
- **Should Learn:** load testing (Locust/k6), mocking external APIs, endpoint testing checklist, auto-generated docs
- **Good to Know:** Pact contract testing, Stripe docs model, fixture strategies
- **Reference:** property-based testing (Hypothesis), chaos testing, SLA/latency testing

**[Back to README](../README.md)**

**Prev:** [API Performance and Scaling](../09_api_performance_scaling/theory.md) | **Next:** [API Security and Production](../11_api_security_production/theory.md)

**Related Topics:** [FastAPI Core Guide](../07_fastapi/theory.md) | [Error Handling Standards](../06_error_handling_standards/theory.md) | [REST Best Practices](../03_rest_best_practices/theory.md) | [Production Deployment](../12_production_deployment/theory.md)
