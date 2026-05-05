# 10 — API Testing

> "Testing shows the presence of bugs, not their absence." — Dijkstra. For APIs, untested endpoints are broken endpoints waiting to be discovered in production.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
unit tests (business logic) · integration tests (TestClient) · auth testing · error path testing

**Should Learn** — Important for real projects, comes up regularly:
load testing (Locust/k6) · mocking external APIs · endpoint testing checklist

**Good to Know** — Useful in specific situations, not always tested:
Pact contract testing · fixture strategies

**Reference** — Know it exists, look up syntax when needed:
property-based testing (Hypothesis) · chaos testing · SLA/latency testing

---

## 1. Why API Tests Are Different

Testing a web API is not the same as testing a pure function. A few things make it distinct:

**You are testing over a network protocol.** Even in local tests, HTTP semantics matter — status codes, headers, content-type, redirects. A function returning `{"error": "not found"}` with a `200` status is wrong, even if the body looks right.

**State lives in a database.** Unlike a pure function, a `POST /orders` request writes to a database. Your tests need to control that state — set it up before, clean it up after.

**You are testing a contract.** Your API is a contract between your backend and every consumer (frontend, mobile app, other services). Breaking the contract silently is the most expensive bug you can ship.

**Three layers of testing for APIs:**

```
┌─────────────────────────────────────────────────────┐
│  Contract Tests  — does the shape match what         │
│                    consumers expect?                 │
├─────────────────────────────────────────────────────┤
│  Integration Tests — does the full HTTP stack work?  │
│                      (routes, auth, DB, serializers) │
├─────────────────────────────────────────────────────┤
│  Unit Tests        — does the business logic work?   │
│                      (no HTTP, no DB)                │
└─────────────────────────────────────────────────────┘
```

Run all three. They catch different things.

---

## 2. Unit Tests for API Logic

The business logic in your API — validation, calculations, transformations — should be testable without spinning up a server or touching a database. Extract it into plain functions or service classes.

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

---

## 3. Integration Tests

Integration tests call your actual running API (or a test version of it) over HTTP. They verify that routes, middleware, serializers, and the database all work together.

### FastAPI — TestClient

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

> 📝 **Practice:** [Q47 · testing-fastapi-testclient](../api_practice_questions_100.md#q47--normal--testing-fastapi-testclient)


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

### Flask — test_client

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

---

## 4. Contract Testing with Pact

Unit and integration tests verify that your code works. Contract tests verify that your API works for the people consuming it.

**The problem:** Your frontend team builds against your API. You change a field name from `user_name` to `username` without telling them. Their app breaks in production.

**The solution:** Consumer-driven contract testing. The consumer (frontend) defines what they expect from the API (the provider). Pact captures this as a contract file. The provider runs tests against the contract to verify it still holds.

```
Consumer (Frontend)              Provider (Backend)
─────────────────────            ─────────────────────
"I expect GET /users/1           "I will run tests to
 to return a JSON object         prove I still satisfy
 with 'id', 'email',             the consumer's
 and 'username' fields."  ──▶    recorded expectations."
         │                                │
         └──── Pact file (JSON) ──────────┘
```

**What breaks without contract tests:**

- Backend renames `user_name` → `username`. Frontend breaks.
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

> 📝 **Practice:** [Q67 · contract-testing](../api_practice_questions_100.md#q67--thinking--contract-testing)


The pact file is published to a Pact Broker. The backend (provider) team runs verification against it in CI. If the provider changes something the consumer expects, the CI pipeline fails before the change reaches production.

Pact is most valuable in microservice architectures or teams with separate frontend/backend development.

---

## 5. Testing Patterns

### Test Data Setup and Teardown

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

### Testing Authentication

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

### Testing Error Cases

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

### Mocking External APIs

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

---

## 6. Load Testing APIs

Functional tests verify correctness. Load tests verify that your API holds up under traffic.

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

---

## 7. Endpoint Testing Checklist

For every API endpoint, verify:

```
Happy path
  [ ] Returns correct status code (200, 201, 204...)
  [ ] Response body has the expected fields and types
  [ ] Side effects occurred (DB write, email sent, etc.)

Validation
  [ ] Missing required fields → 400 with clear error message
  [ ] Invalid field types → 400
  [ ] Out-of-range values → 400
  [ ] Malformed JSON body → 400

Authentication & Authorization
  [ ] No token → 401
  [ ] Invalid/expired token → 401
  [ ] Valid token, wrong role/scope → 403
  [ ] Accessing another user's resource → 403 or 404

Edge cases
  [ ] Resource not found → 404
  [ ] Duplicate creation → 409
  [ ] Concurrent modification → 409 or 422

Error handling
  [ ] 500 errors don't leak stack traces
  [ ] Error responses follow your error schema consistently
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← API Performance & Scaling](../09_api_performance_scaling/performance_guide.md) &nbsp;|&nbsp; **Next:** [API Documentation →](../10_testing_documentation/docs_that_work.md)

**Related Topics:** [FastAPI Core Guide](../07_fastapi/core_guide.md) · [Error Handling Standards](../06_error_handling_standards/error_guide.md) · [Production Deployment](../12_production_deployment/deployment_guide.md) · [API Documentation](../10_testing_documentation/docs_that_work.md)
