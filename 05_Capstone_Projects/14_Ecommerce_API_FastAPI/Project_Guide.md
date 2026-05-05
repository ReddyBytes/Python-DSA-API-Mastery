# Project 14 — E-Commerce API in FastAPI

> An e-commerce API is the engine behind every online store — invisible to shoppers but handling every product browse, cart add, and checkout. Building one from scratch is the rite of passage for backend engineers: it touches auth, database design, business logic, transactions, testing, and deployment all at once.

---

## What You're Building

A production-grade REST API for an online store. Users register and log in, browse and filter products, place orders, and receive email confirmations — all backed by PostgreSQL with proper auth, transactions, and rate limiting.

```
Client → FastAPI → Auth Middleware → Routers (auth / products / orders)
                                           ↓
                                       Services → SQLAlchemy ORM → PostgreSQL
                                           ↓
                                    BackgroundTasks → Email (simulated)
```

---

## Difficulty

This is a **build yourself** project. You get:
- The spec (what to build)
- The acceptance criteria (what must work)
- The full solution at the end

No step-by-step guidance. Use the learning modules if you get stuck.

---

## Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| FastAPI | >=0.111.0 | Web framework + OpenAPI docs |
| SQLAlchemy | >=2.0.0 | ORM — models and queries |
| PostgreSQL | 15 | Primary database |
| pydantic-settings | >=2.0.0 | Config from environment variables |
| python-jose | >=3.3.0 | JWT encode/decode |
| passlib[bcrypt] | >=1.7.4 | Password hashing |
| slowapi | >=0.1.9 | Rate limiting |
| pytest + httpx | >=7.0.0 | Testing |

---

## Setup

```bash
pip install -e ".[dev]"
```

### pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "ecommerce-api"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.111.0",
    "uvicorn[standard]>=0.29.0",
    "sqlalchemy>=2.0.0",
    "psycopg2-binary>=2.9.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "slowapi>=0.1.9",
    "python-multipart>=0.0.9",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "httpx>=0.27.0",
    "pytest-asyncio>=0.23.0",
]

[tool.hatch.build.targets.wheel]
packages = ["src/ecommerce"]
```

### .env.example

```
DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce
SECRET_KEY=change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## File Structure

```
ecommerce_api/
├── src/
│   └── ecommerce/
│       ├── __init__.py
│       ├── main.py           ← FastAPI app factory
│       ├── config.py         ← settings via pydantic-settings
│       ├── database.py       ← engine + session + Base
│       ├── models/
│       │   ├── __init__.py
│       │   ├── user.py
│       │   ├── product.py
│       │   └── order.py
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── user.py
│       │   ├── product.py
│       │   └── order.py
│       ├── routers/
│       │   ├── __init__.py
│       │   ├── auth.py
│       │   ├── products.py
│       │   └── orders.py
│       ├── services/
│       │   ├── __init__.py
│       │   └── order.py
│       └── core/
│           ├── __init__.py
│           ├── security.py   ← JWT, hashing
│           └── dependencies.py
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_products.py
│   └── test_orders.py
├── pyproject.toml
├── Dockerfile
└── docker-compose.yml
```

---

## Spec

### Auth Endpoints

| Method | Path | Auth Required | Request Body | Response | Notes |
|--------|------|--------------|-------------|---------|-------|
| POST | /auth/register | No | email, password, full_name | 201 UserResponse | Reject duplicate email with 400 |
| POST | /auth/login | No | email, password | 200 Token | Wrong credentials → 401 |

### Product Endpoints

| Method | Path | Auth Required | Request Body | Response | Notes |
|--------|------|--------------|-------------|---------|-------|
| GET | /products/ | No | — | 200 ProductListResponse | Supports page, page_size, category, min_price, max_price |
| GET | /products/{id} | No | — | 200 ProductResponse | 404 if not found or inactive |
| POST | /products/ | Admin only | name, price, stock_quantity, category, description | 201 ProductResponse | 401 if no token, 403 if not admin |
| PATCH | /products/{id} | Admin only | Any product fields (all optional) | 200 ProductResponse | Only updates provided fields |
| DELETE | /products/{id} | Admin only | — | 204 No Content | Soft delete — sets is_active=False |

### Order Endpoints

| Method | Path | Auth Required | Request Body | Response | Notes |
|--------|------|--------------|-------------|---------|-------|
| POST | /orders/ | Yes | items: [{product_id, quantity}] | 201 OrderResponse | Stock check + decrement in one transaction |
| GET | /orders/ | Yes | — | 200 list[OrderResponse] | Returns only the current user's orders |

---

## Business Rules

1. Passwords must be hashed with bcrypt — never stored plain
2. JWT access tokens expire in 30 minutes
3. Only admin users can create, update, or delete products
4. Soft delete products (`is_active = False`) — never hard delete
5. Order placement checks stock BEFORE writing anything
6. Stock decrement and order creation happen in one transaction
7. `with_for_update()` row lock prevents race conditions on simultaneous orders
8. Confirmation email sent as a BackgroundTask after order — the client does not wait
9. Email validation on registration (reject invalid format via Pydantic EmailStr)
10. Price must be > 0 (validated in Pydantic schema with `field_validator`)

---

## Database Design

```
users
------
id              INT PK
email           VARCHAR(255) UNIQUE NOT NULL
hashed_password VARCHAR(255) NOT NULL
full_name       VARCHAR(255) NOT NULL
is_active       BOOL DEFAULT TRUE
is_admin        BOOL DEFAULT FALSE
created_at      DATETIME

products
--------
id              INT PK
name            VARCHAR(255) NOT NULL
description     TEXT
price           NUMERIC(10,2) NOT NULL
stock_quantity  INT DEFAULT 0
category        VARCHAR(100)
is_active       BOOL DEFAULT TRUE
created_at      DATETIME

orders
------
id              INT PK
user_id         INT FK → users.id
status          ENUM(pending, confirmed, shipped, delivered, cancelled)
total_amount    NUMERIC(10,2) NOT NULL
created_at      DATETIME

order_items
-----------
id              INT PK
order_id        INT FK → orders.id
product_id      INT FK → products.id
quantity        INT NOT NULL
unit_price      NUMERIC(10,2) NOT NULL
```

---

## Acceptance Criteria

```
[ ] POST /auth/register creates user, returns 201 (no password in response)
[ ] POST /auth/register with duplicate email returns 400
[ ] POST /auth/login with correct credentials returns JWT token
[ ] POST /auth/login with wrong password returns 401
[ ] GET /products/ returns paginated list (page, page_size, total)
[ ] GET /products/?category=electronics filters correctly
[ ] GET /products/?min_price=10&max_price=50 filters correctly
[ ] POST /products/ without auth returns 401
[ ] POST /products/ with non-admin token returns 403
[ ] POST /products/ with admin token creates product, returns 201
[ ] PATCH /products/{id} updates only provided fields
[ ] DELETE /products/{id} soft-deletes (is_active=False, still in DB)
[ ] POST /orders/ places order, decrements stock, returns 201
[ ] POST /orders/ with insufficient stock returns 400 with clear message
[ ] POST /orders/ for two products at once is atomic (both succeed or both fail)
[ ] GET /orders/ returns only the current user's orders
[ ] All pytest tests in tests/ pass
[ ] docker-compose up starts API + PostgreSQL successfully
[ ] Rate limit: POST /auth/login returns 429 after 5 requests/minute
```

---

## Where to Look When Stuck

| If stuck on | Go read |
|-------------|---------|
| JWT / password hashing | `03_API_Mastery/05_authentication/securing_apis.md` |
| SQLAlchemy models | `03_API_Mastery/07_fastapi/database_guide.md` |
| FastAPI `Depends()` | `03_API_Mastery/07_fastapi/core_guide.md` |
| pytest + TestClient | `01_Python_Mastery/17_testing/theory.md` |
| Background tasks | `03_API_Mastery/07_fastapi/advanced_guide.md` |
| Docker | `Container-Engineering` repo |

---

## You're On Your Own

Good luck. Return to the full solution only after you've made a genuine attempt.

---

## Full Solution

<details>
<summary>Complete solution — only open after you've built it</summary>

### config.py

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@localhost:5432/ecommerce"
    secret_key: str = "change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    app_name: str = "E-Commerce API"

    model_config = SettingsConfigDict(env_file=".env")  # ← reads from .env automatically

settings = Settings()
```

---

### database.py

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from ecommerce.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    """Dependency that yields a database session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # ← runs even if an exception is raised
```

---

### models/user.py

```python
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ecommerce.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")  # ← lazy loads by default
```

---

### models/product.py

```python
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Text, Numeric, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ecommerce.database import Base

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)  # ← Numeric avoids float rounding errors
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
    category: Mapped[str | None] = mapped_column(String(100), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)  # ← soft delete flag
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    order_items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="product")
```

---

### models/order.py

```python
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Numeric, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ecommerce.database import Base
import enum

class OrderStatus(str, enum.Enum):  # ← str mixin makes it JSON-serializable
    pending = "pending"
    confirmed = "confirmed"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.pending
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)  # ← snapshot price at order time

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")
```

---

### schemas/user.py

```python
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

# --- Input schemas (what the client sends) ---

class UserCreate(BaseModel):
    email: EmailStr          # ← Pydantic validates email format automatically
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# --- Output schemas (what the API returns) ---

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    created_at: datetime
    # ← hashed_password is intentionally excluded

    model_config = ConfigDict(from_attributes=True)  # ← allows ORM object → Pydantic

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

---

### schemas/product.py

```python
from pydantic import BaseModel, ConfigDict, field_validator
from decimal import Decimal
from datetime import datetime

class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: Decimal
    stock_quantity: int = 0
    category: str | None = None

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Price must be greater than zero")
        return v

class ProductUpdate(BaseModel):
    name: str | None = None          # ← all fields optional — only update what's provided
    description: str | None = None
    price: Decimal | None = None
    stock_quantity: int | None = None
    category: str | None = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    stock_quantity: int
    category: str | None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
```

---

### schemas/order.py

```python
from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime
from ecommerce.models.order import OrderStatus

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: list[OrderItemCreate]

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal

    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: OrderStatus
    total_amount: Decimal
    created_at: datetime
    items: list[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)
```

---

### core/security.py

```python
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from ecommerce.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # ← bcrypt is the only active scheme

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)  # ← timing-safe comparison

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})  # ← "exp" is the standard JWT expiry claim
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None  # ← any decode failure (expired, tampered, wrong key) returns None
```

---

### core/dependencies.py

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ecommerce.database import get_db
from ecommerce.core.security import decode_access_token
from ecommerce.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # ← tells Swagger UI where to get a token

def get_current_user(
    token: str = Depends(oauth2_scheme),  # ← extracts Bearer token from Authorization header
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},  # ← required by OAuth2 spec
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    email: str | None = payload.get("sub")  # ← "sub" (subject) is the standard claim for user identity
    if email is None:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
```

---

### routers/auth.py

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ecommerce.database import get_db
from ecommerce.models.user import User
from ecommerce.schemas.user import UserCreate, UserLogin, UserResponse, Token
from ecommerce.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),  # ← never store plain text
        full_name=user_in.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)  # ← reloads the object from DB so auto-generated fields (id, created_at) are populated
    return user

@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token = create_access_token({"sub": user.email})  # ← embed email as the token subject
    return {"access_token": token, "token_type": "bearer"}
```

---

### routers/products.py

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from ecommerce.database import get_db
from ecommerce.models.product import Product
from ecommerce.models.user import User
from ecommerce.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
)
from ecommerce.core.dependencies import get_current_user

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/", response_model=ProductListResponse)
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: str | None = Query(None),
    min_price: float | None = Query(None),
    max_price: float | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Product).filter(Product.is_active == True)  # ← never return soft-deleted products

    if category:
        query = query.filter(Product.category == category)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    total = query.count()
    products = query.offset((page - 1) * page_size).limit(page_size).all()  # ← offset-based pagination

    return ProductListResponse(
        items=products, total=total, page=page, page_size=page_size
    )

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(
        Product.id == product_id, Product.is_active == True
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    product = Product(**product_in.model_dump())  # ← unpack Pydantic model into ORM constructor
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in product_in.model_dump(exclude_unset=True).items():  # ← exclude_unset = only fields the client sent
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_active = False  # ← soft delete: record stays in DB for order history integrity
    db.commit()
```

---

### services/order.py

```python
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException
from ecommerce.models.product import Product
from ecommerce.models.order import Order, OrderItem
from ecommerce.schemas.order import OrderCreate

def place_order(order_in: OrderCreate, user_id: int, db: Session) -> Order:
    """
    Create an order inside a single transaction.
    Raises HTTPException if any product is out of stock or not found.
    """
    items_to_create = []
    total = Decimal("0.00")

    # --- Validate all items BEFORE touching the database state ---
    for item in order_in.items:
        product = db.query(Product).filter(
            Product.id == item.product_id,
            Product.is_active == True,
        ).with_for_update().first()  # ← row-level lock: no other transaction can update this row until we commit

        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product {item.product_id} not found",
            )
        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product '{product.name}'. "
                       f"Available: {product.stock_quantity}, requested: {item.quantity}",
            )
        items_to_create.append((product, item.quantity, product.price))
        total += product.price * item.quantity

    # --- All checks passed — write in one transaction ---
    order = Order(user_id=user_id, total_amount=total)
    db.add(order)
    db.flush()  # ← assigns order.id without committing — needed so OrderItem can reference it

    for product, quantity, unit_price in items_to_create:
        product.stock_quantity -= quantity  # ← decrement stock atomically with order creation
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
            unit_price=unit_price,  # ← snapshot price — won't change if product price changes later
        )
        db.add(order_item)

    db.commit()  # ← single commit: if anything fails above, the whole thing rolls back
    db.refresh(order)
    return order
```

---

### routers/orders.py

```python
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from ecommerce.database import get_db
from ecommerce.models.user import User
from ecommerce.schemas.order import OrderCreate, OrderResponse
from ecommerce.services.order import place_order
from ecommerce.core.dependencies import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])

def send_confirmation_email(email: str, order_id: int):
    """Background task — replace with real email library (SendGrid, SES, etc.)."""
    print(f"[EMAIL] Sending order confirmation to {email} for order #{order_id}")

@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(
    order_in: OrderCreate,
    background_tasks: BackgroundTasks,  # ← FastAPI injects this automatically
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = place_order(order_in, current_user.id, db)
    background_tasks.add_task(send_confirmation_email, current_user.email, order.id)  # ← runs after response is sent
    return order

@router.get("/", response_model=list[OrderResponse])
def list_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return current_user.orders  # ← SQLAlchemy relationship loads the orders automatically
```

---

### main.py

```python
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from ecommerce.config import settings
from ecommerce.database import Base, engine
from ecommerce.models import user, product, order  # noqa: F401 — imports register models with Base.metadata
from ecommerce.routers import auth, products, orders

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# --- Rate limiter setup ---
limiter = Limiter(key_func=get_remote_address)  # ← rate limit by client IP

app = FastAPI(title=settings.app_name)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # ← returns 429 automatically

# --- Create tables on startup ---
Base.metadata.create_all(bind=engine)  # ← in production, use Alembic migrations instead

# --- Register routers ---
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)

# --- Global exception handler ---
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled error on {request.method} {request.url}: {exc}", exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},  # ← never leak internal error details to clients
    )
```

Note: to apply the rate limit to the login route, update `routers/auth.py`:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

limiter = Limiter(key_func=get_remote_address)

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")  # ← 5 login attempts per IP per minute
async def login(request: Request, credentials: UserLogin, db: Session = Depends(get_db)):
    # same body as before
    ...
```

---

### tests/conftest.py

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ecommerce.main import app
from ecommerce.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # ← required for SQLite in multi-threaded use
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)   # ← fresh schema before each test
    yield
    Base.metadata.drop_all(bind=engine)     # ← tear down after each test — no state bleeds between tests

@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db  # ← swap real DB for test DB
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()  # ← always clean up overrides after the test

@pytest.fixture
def registered_user(client):
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
    })
    assert response.status_code == 201
    return response.json()

@pytest.fixture
def auth_headers(client):
    client.post("/auth/register", json={
        "email": "user@example.com",
        "password": "password123",
        "full_name": "Test User",
    })
    response = client.post("/auth/login", json={
        "email": "user@example.com",
        "password": "password123",
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

---

### tests/test_auth.py

```python
def test_register_success(client):
    response = client.post("/auth/register", json={
        "email": "new@example.com",
        "password": "securepass",
        "full_name": "New User",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert "hashed_password" not in data  # ← critical: password must never appear in API response

def test_register_duplicate_email(client, registered_user):
    response = client.post("/auth/register", json={
        "email": "test@example.com",  # ← same as registered_user fixture
        "password": "another",
        "full_name": "Dupe",
    })
    assert response.status_code == 400

def test_login_success(client, registered_user):
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "testpassword123",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password(client, registered_user):
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401
```

---

### tests/test_products.py

```python
def test_list_products_empty(client):
    response = client.get("/products/")
    assert response.status_code == 200
    assert response.json()["total"] == 0

def test_get_product_not_found(client):
    response = client.get("/products/999")
    assert response.status_code == 404

def test_create_product_requires_auth(client):
    response = client.post("/products/", json={
        "name": "Widget", "price": "9.99", "stock_quantity": 10
    })
    assert response.status_code == 401  # ← no token provided

def test_create_product_requires_admin(client, auth_headers):
    response = client.post("/products/", json={
        "name": "Widget", "price": "9.99", "stock_quantity": 10
    }, headers=auth_headers)
    assert response.status_code == 403  # ← regular user, not admin
```

---

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir .    # ← installs only production deps (no [dev] extras)

COPY src/ ./src/

ENV PYTHONPATH=/app/src             # ← makes `from ecommerce.xxx import` work without installing as editable

CMD ["uvicorn", "ecommerce.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### docker-compose.yml

```yaml
version: "3.9"

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ecommerce
      POSTGRES_PASSWORD: ecommerce
      POSTGRES_DB: ecommerce
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ecommerce"]
      interval: 5s
      timeout: 5s
      retries: 5

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://ecommerce:ecommerce@db:5432/ecommerce
      SECRET_KEY: local-dev-secret-change-in-prod
    depends_on:
      db:
        condition: service_healthy  # ← waits for postgres healthcheck to pass before starting api
    volumes:
      - ./src:/app/src               # ← hot reload in dev: code changes reflect without rebuilding image

volumes:
  pgdata:
```

```bash
docker-compose up --build
docker-compose down -v  # ← -v removes named volumes (pgdata) — full clean slate
```

</details>

---

## Reflection

After completing this project, you can independently:

- Design a multi-table relational schema and map it to SQLAlchemy ORM models
- Implement JWT authentication with bcrypt password hashing from scratch
- Write role-based access control using FastAPI dependency injection
- Build paginated, filtered list endpoints with query parameters
- Handle transactional writes with row-level locking to prevent race conditions
- Fire background tasks that run after the HTTP response is already sent
- Test a FastAPI app with pytest using dependency overrides and in-memory SQLite
- Containerize a Python API with Docker and wire it to PostgreSQL via docker-compose

---

## What's Next

- **Project 05 — JWT Auth Deep Dive**: Focused study on token refresh, blacklisting, and OAuth2 flows — `03_API_Mastery/05_authentication/`
- **Project 08 — Celery Background Tasks**: Replace `BackgroundTasks` with a production-grade Celery + Redis queue for retries and failure handling — `03_API_Mastery/07_fastapi/advanced_guide.md`

---

## Navigation

| | |
|---|---|
| Back | [README.md](./README.md) |
| Architecture | [Architecture.md](./Architecture.md) |
