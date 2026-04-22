# ⚡ Testing & Documentation — Cheatsheet

## Learning Priority

| Priority | Topics |
|---|---|
| Must Learn | TestClient setup · common assert patterns · auth testing · error path testing |
| Should Learn | load testing (Locust/k6) · mocking external APIs · fixture examples |
| Good to Know | Pact contract testing · property-based testing (Hypothesis) |
| Reference | chaos testing · SLA/latency testing |

---

## TestClient Setup (FastAPI)

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

# Or inline — simpler for small projects
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
```

---

## TestClient Usage

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# GET
response = client.get("/items/42")
response = client.get("/items", params={"status": "active", "page": 2})

# POST with JSON body
response = client.post(
    "/items",
    json={"name": "Widget", "price": 9.99},
)

# With auth header
response = client.get(
    "/profile",
    headers={"Authorization": "Bearer eyJ..."}
)

# PUT / PATCH / DELETE
response = client.put("/items/42", json={"name": "Updated", "price": 12.0})
response = client.patch("/items/42", json={"price": 12.0})
response = client.delete("/items/42")
```

---

## Common Assert Patterns

```python
# Status codes
assert response.status_code == 200
assert response.status_code == 201
assert response.status_code == 204
assert response.status_code == 400
assert response.status_code == 404

# Body
data = response.json()
assert data["name"] == "Widget"
assert data["price"] == 9.99
assert "id" in data                          # field exists
assert isinstance(data["tags"], list)         # correct type
assert len(data["items"]) == 3               # count

# Error response structure
error = response.json()["error"]
assert error["code"] == "VALIDATION_ERROR"
assert "email" in [d["field"] for d in error["details"]]

# Headers
assert response.headers["content-type"] == "application/json"
assert "Location" in response.headers
assert response.headers["X-RateLimit-Limit"] == "100"

# Collections
data = response.json()
assert "data" in data
assert "pagination" in data
assert data["pagination"]["has_next"] is True
```

---

## Fixture Examples

```python
import pytest
from fastapi.testclient import TestClient
from main import app, ITEMS   # in-memory store

# Reset in-memory state before each test
@pytest.fixture(autouse=True)
def clear_store():
    ITEMS.clear()
    yield
    ITEMS.clear()

# Database session fixture — rolls back after each test
@pytest.fixture
def db_session():
    session = SessionLocal()
    session.begin_nested()   # savepoint
    yield session
    session.rollback()       # always rolls back
    session.close()

# Pre-created test user
@pytest.fixture
def sample_user(db_session):
    user = User(email="test@example.com", name="Test User", role="viewer")
    db_session.add(user)
    db_session.flush()        # assigns ID without committing
    return user

# Pre-authenticated client
@pytest.fixture
def auth_client(sample_user):
    token = create_access_token(user_id=sample_user.id)
    client = TestClient(app)
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
```

---

## Testing Authentication

```python
import jwt

def make_token(user_id: int, role: str = "user", secret: str = "test-secret") -> str:
    return jwt.encode(
        {"sub": str(user_id), "role": role},
        secret,
        algorithm="HS256"
    )

# Valid user
def test_profile_with_valid_token(client):
    token = make_token(user_id=42)
    resp = client.get("/profile", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

# No token
def test_profile_without_token(client):
    resp = client.get("/profile")
    assert resp.status_code == 401

# Invalid / expired token
def test_profile_with_bad_token(client):
    resp = client.get("/profile", headers={"Authorization": "Bearer badtoken"})
    assert resp.status_code == 401

# Wrong role (403 not 401)
def test_admin_endpoint_wrong_role(client):
    token = make_token(user_id=42, role="user")   # not admin
    resp = client.delete("/admin/users/1", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403

# Accessing another user's data (IDOR test)
def test_cannot_access_other_users_data(client):
    token = make_token(user_id=42)
    resp = client.get("/users/99/orders", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code in (403, 404)
```

---

## Error Path Testing

```python
# Validation errors (missing fields)
def test_missing_required_field(client):
    resp = client.post("/orders", json={})
    assert resp.status_code in (400, 422)
    assert "error" in resp.json() or "detail" in resp.json()

# Invalid types
def test_invalid_field_type(client):
    resp = client.post("/orders", json={"quantity": "not-a-number"})
    assert resp.status_code == 422

# Not found
def test_resource_not_found(client):
    resp = client.get("/orders/99999")
    assert resp.status_code == 404

# Duplicate creation (conflict)
def test_duplicate_email(client):
    client.post("/users", json={"email": "alice@example.com"})
    resp = client.post("/users", json={"email": "alice@example.com"})
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "CONFLICT"

# 500 errors don't leak internals
def test_500_does_not_leak_stack_trace(client, monkeypatch):
    monkeypatch.setattr("app.services.get_db", lambda: (_ for _ in ()).throw(Exception("DB down")))
    resp = client.get("/items")
    assert resp.status_code == 500
    body = resp.json()
    assert "traceback" not in str(body).lower()
    assert "error" in body
```

---

## Mocking External APIs

```python
# Using responses library (pip install responses)
import responses as resp_mock

@resp_mock.activate
def test_email_notification_sent():
    resp_mock.add(
        resp_mock.POST,
        "https://api.sendgrid.com/v3/mail/send",
        json={"message": "Queued"},
        status=202
    )
    result = send_welcome_email("alice@example.com")
    assert result is True
    assert len(resp_mock.calls) == 1

# Using pytest monkeypatch
def test_payment_service_called(client, monkeypatch):
    called_with = []

    def mock_charge(amount, customer_id):
        called_with.append({"amount": amount, "customer_id": customer_id})
        return {"id": "ch_123", "status": "succeeded"}

    monkeypatch.setattr("app.services.payment.charge_card", mock_charge)

    resp = client.post("/orders", json={"amount": 1000, "customer_id": 42})
    assert resp.status_code == 201
    assert called_with[0]["amount"] == 1000
```

---

## OpenAPI Auto-Docs Endpoints

```
GET /docs         → Swagger UI (interactive, try endpoints live)
GET /redoc        → ReDoc (alternative, cleaner read-only view)
GET /openapi.json → Raw OpenAPI 3.x schema (JSON)
```

```python
# Customize in app init
app = FastAPI(
    title="My API",
    version="1.0.0",
    description="API for managing orders",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Disable docs in production
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
```

---

## Response Schema Validation

```python
from pydantic import BaseModel, ValidationError

class PaginatedResponse(BaseModel):
    data: list
    pagination: dict

def test_list_response_shape(client):
    resp = client.get("/orders")
    assert resp.status_code == 200

    # Validate response structure against a Pydantic model
    try:
        PaginatedResponse(**resp.json())
    except ValidationError as e:
        pytest.fail(f"Response shape is wrong: {e}")

    # Or assert individual fields
    body = resp.json()
    assert "data" in body
    assert "pagination" in body
    assert "total" in body["pagination"]
    assert "has_next" in body["pagination"]
```

---

## Load Testing Quick Reference

```python
# locustfile.py (pip install locust)
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)                                    # weight: called 3x more often
    def browse_products(self):
        self.client.get("/products")

    @task(1)
    def create_order(self):
        self.client.post("/orders", json={
            "product_id": 1, "quantity": 2
        })
```

```bash
# Run Locust
locust -f locustfile.py --host=http://localhost:8000
# Open http://localhost:8089 for web UI

# k6 (JavaScript, CI-friendly)
k6 run --vus 50 --duration 30s script.js
```

---

## Endpoint Testing Checklist

```
Happy path
  [ ] Returns correct status code (200, 201, 204)
  [ ] Response body has expected fields and types
  [ ] Side effects occurred (DB written, email queued, etc.)

Validation
  [ ] Missing required field → 400/422 with clear error
  [ ] Invalid field type → 400/422
  [ ] Out-of-range value → 400/422
  [ ] Malformed JSON → 400

Authentication & Authorization
  [ ] No token → 401
  [ ] Invalid / expired token → 401
  [ ] Valid token, wrong role → 403
  [ ] Accessing another user's resource → 403 or 404

Edge cases
  [ ] Resource not found → 404
  [ ] Duplicate creation → 409
  [ ] Concurrent modification → 409 or 422

Error handling
  [ ] 500 errors don't leak stack traces or internal paths
  [ ] Error responses follow consistent error schema
```

---

## Navigation

**[Back to README](../README.md)**

**Theory:** [testing_apis.md](./testing_apis.md) · [docs_that_work.md](./docs_that_work.md)

**Prev:** [← Performance & Scaling](../09_api_performance_scaling/cheatsheet.md) &nbsp;|&nbsp; **Next:** [API Security Production →](../11_api_security_production/)

**Related:** [06 Error Handling](../06_error_handling_standards/cheatsheet.md) · [07 FastAPI](../07_fastapi/cheatsheet.md) · [09 Performance](../09_api_performance_scaling/cheatsheet.md)
