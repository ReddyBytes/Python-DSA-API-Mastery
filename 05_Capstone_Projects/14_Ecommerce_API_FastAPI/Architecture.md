# Project 01 — Architecture: E-Commerce API

---

## Component Diagram

```
                         CLIENT
                    (browser / mobile)
                           |
                           | HTTP/JSON
                           v
              +------------------------+
              |   FastAPI Application  |
              |                        |
              |  +-----------------+   |
              |  |  Auth Router    |   |  POST /auth/register
              |  |  /auth/*        |   |  POST /auth/login
              |  +-----------------+   |
              |                        |
              |  +-----------------+   |
              |  | Product Router  |   |  GET  /products/
              |  |  /products/*    |   |  POST /products/       (admin)
              |  +-----------------+   |  PATCH /products/{id}  (admin)
              |                        |  DELETE /products/{id} (admin)
              |  +-----------------+   |
              |  |  Order Router   |   |  POST /orders/
              |  |  /orders/*      |   |  GET  /orders/
              |  +-----------------+   |
              |                        |
              |  +-----------------+   |
              |  | Dependency      |   |
              |  | Injection Layer |   |  get_db(), get_current_user()
              |  | (core/deps)     |   |
              |  +-----------------+   |
              |                        |
              |  +-----------------+   |
              |  | Service Layer   |   |  place_order() — business logic
              |  | (services/)     |   |
              |  +-----------------+   |
              |                        |
              |  +-----------------+   |
              |  | SQLAlchemy ORM  |   |  User, Product, Order, OrderItem
              |  | (models/)       |   |
              |  +-----------------+   |
              +------------------------+
                           |
                           | SQL (psycopg2)
                           v
              +------------------------+
              |      PostgreSQL        |
              |  users                 |
              |  products              |
              |  orders                |
              |  order_items           |
              +------------------------+

              +------------------------+
              |   Background Worker    |
              |  (FastAPI BackgroundTasks)
              |  - Email confirmation  |
              +------------------------+
```

---

## Data Model (ER Diagram)

```
USERS
-----
id              PK  INTEGER
email               VARCHAR(255)  UNIQUE
hashed_password     VARCHAR(255)
full_name           VARCHAR(255)
is_active           BOOLEAN
is_admin            BOOLEAN
created_at          DATETIME

     |
     | 1 : many
     v

ORDERS
------
id              PK  INTEGER
user_id         FK  → users.id
status              ENUM (pending, confirmed, shipped, delivered, cancelled)
total_amount        NUMERIC(10,2)
created_at          DATETIME

     |
     | 1 : many
     v

ORDER_ITEMS
-----------
id              PK  INTEGER
order_id        FK  → orders.id
product_id      FK  → products.id
quantity            INTEGER
unit_price          NUMERIC(10,2)

     ^
     | many : 1
     |

PRODUCTS
--------
id              PK  INTEGER
name                VARCHAR(255)
description         TEXT
price               NUMERIC(10,2)
stock_quantity      INTEGER
category            VARCHAR(100)
is_active           BOOLEAN
created_at          DATETIME
```

---

## API Endpoint Table

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | None | Create new user account |
| POST | `/auth/login` | None | Exchange credentials for JWT token |
| GET | `/products/` | None | List products (paginated, filterable) |
| GET | `/products/{id}` | None | Get single product |
| POST | `/products/` | Admin JWT | Create product |
| PATCH | `/products/{id}` | Admin JWT | Partially update product |
| DELETE | `/products/{id}` | Admin JWT | Soft-delete product |
| POST | `/orders/` | User JWT | Place an order |
| GET | `/orders/` | User JWT | List current user's orders |

---

## Authentication Flow

```
1. Client sends POST /auth/login  { email, password }
          |
          v
2. Server queries users table for email
          |
          v
3. passlib.verify_password(plain, hashed)
          |        |
       PASS       FAIL → 401 Unauthorized
          |
          v
4. create_access_token({ "sub": email, "exp": now + 30min })
          |
          v
5. Return { access_token, token_type: "bearer" }
          |
          v
6. Client stores token, sends on every protected request:
   Authorization: Bearer <token>
          |
          v
7. get_current_user() dependency:
   - Extracts token from header
   - jose.jwt.decode(token, SECRET_KEY)
   - Looks up user by "sub" claim
   - Returns User ORM object to route handler
```

---

## Request Lifecycle (Order Placement)

```
POST /orders/
  { items: [{ product_id: 1, quantity: 2 }] }

  1. JWT middleware validates token → injects current_user
  2. OrderCreate Pydantic schema validates request body
  3. place_order(order_in, current_user.id, db) called
  4.   FOR each item:
  5.     SELECT ... FROM products WHERE id=? FOR UPDATE   ← row lock
  6.     Check product.is_active == True
  7.     Check product.stock_quantity >= requested_quantity
  8.   INSERT INTO orders ...
  9.   db.flush()  ← get order.id, no commit yet
  10.  FOR each item:
  11.    UPDATE products SET stock_quantity = stock_quantity - qty
  12.    INSERT INTO order_items ...
  13.  db.commit()   ← single atomic write
  14. BackgroundTasks.add_task(send_confirmation_email, ...)
  15. Return 201 OrderResponse JSON
  16. [BACKGROUND] send_confirmation_email fires after response
```

---

## Design Decisions

### Why separate models and schemas?

SQLAlchemy models and Pydantic schemas serve different masters. The ORM model maps to a table and knows about database-specific things (foreign keys, indexes, lazy loading). The Pydantic schema defines the API contract — what fields the client sends and what the API returns. Mixing them creates problems: you can't add a `password` field to a `UserResponse` schema even if it's on the model. Keeping them separate makes this impossible.

### Why use `with_for_update()` during order placement?

Without a row lock, two concurrent requests could both read `stock_quantity = 1`, both pass the inventory check, and both decrement — leaving you at `-1`. The `FOR UPDATE` lock forces the second transaction to wait until the first commits, preventing the race condition.

### Why soft-delete products?

Hard-deleting a product breaks foreign key constraints on `order_items`. Soft-delete (`is_active = False`) preserves historical order data while hiding the product from new listings.

### Why a service layer for orders?

Order placement has real business logic: multi-step validation, locking, summing totals, creating two record types. If this logic lived in the route handler, it would be impossible to test without an HTTP client. The service function is pure Python — testable with just a DB session.

### Why SQLite for tests?

PostgreSQL requires a running server. SQLite runs in-process with zero setup. For 95% of query patterns, SQLAlchemy generates compatible SQL for both. The 5% differences (e.g., `FOR UPDATE` is a no-op on SQLite) are acceptable in unit tests — just make sure your integration tests (Step 9 Docker) run against real PostgreSQL.

---

## Navigation

| | |
|---|---|
| Back | [README.md](./README.md) |
| Build Guide | [Project_Guide.md](./Project_Guide.md) |
| Starter Code | [starter_code/main.py](./starter_code/main.py) |
