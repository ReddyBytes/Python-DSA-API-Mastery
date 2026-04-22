# Project 01 — Build Guide: E-Commerce API in FastAPI

Work through each step in order. Every step produces runnable code — commit after each one.

---

## Step 1: Project Structure Setup

Think of this as laying the floor plan before building the walls. The `src` layout keeps your app code separate from config and tests.

### Directory layout

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
│       │   ├── auth.py
│       │   └── order.py
│       └── core/
│           ├── __init__.py
│           ├── security.py   ← JWT, hashing
│           └── exceptions.py
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_products.py
│   └── test_orders.py
├── pyproject.toml
├── Dockerfile
└── docker-compose.yml
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

### config.py

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@localhost:5432/ecommerce"
    secret_key: str = "change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    app_name: str = "E-Commerce API"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
```

---

## Step 2: Database Models

**SQLAlchemy models** are Python classes that map directly to database tables. Think of each class as a blueprint for a table — each class attribute is a column.

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
        db.close()
```

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

    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")
```

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
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
    category: Mapped[str | None] = mapped_column(String(100), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    order_items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="product")
```

### models/order.py

```python
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Numeric, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ecommerce.database import Base
import enum

class OrderStatus(str, enum.Enum):
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
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")
```

**Create all tables on startup:**

```python
# In main.py, before the app starts
from ecommerce.database import Base, engine
from ecommerce.models import user, product, order  # noqa: F401 — imports needed for metadata

Base.metadata.create_all(bind=engine)
```

---

## Step 3: Pydantic Schemas

**Pydantic schemas** are separate from SQLAlchemy models. The ORM model owns the database; the Pydantic schema owns the API contract (what comes in, what goes out).

### schemas/user.py

```python
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

# --- Input schemas (what the client sends) ---

class UserCreate(BaseModel):
    email: EmailStr
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

    model_config = ConfigDict(from_attributes=True)  # allows ORM -> Pydantic

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

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
    name: str | None = None
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

## Step 4: Authentication (JWT + Password Hashing)

Think of the auth system as a nightclub: the bouncer (JWT middleware) checks your wristband (token) before letting you into any protected room. The token was issued when you first proved your identity (login).

### core/security.py

```python
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from ecommerce.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None
```

### Auth dependency (used by protected routes)

```python
# In core/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ecommerce.database import get_db
from ecommerce.core.security import decode_access_token
from ecommerce.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    email: str | None = payload.get("sub")
    if email is None:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
```

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
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}
```

---

## Step 5: Product CRUD Routes (with Pagination and Filtering)

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
    query = db.query(Product).filter(Product.is_active == True)

    if category:
        query = query.filter(Product.category == category)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    total = query.count()
    products = query.offset((page - 1) * page_size).limit(page_size).all()

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
    product = Product(**product_in.model_dump())
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
    for field, value in product_in.model_dump(exclude_unset=True).items():
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
    product.is_active = False  # soft delete
    db.commit()
```

---

## Step 6: Order Placement Logic (Inventory + Transactions)

Order placement is the most critical path. Two rules:
1. Check stock before writing anything.
2. Decrement stock and create the order in a single transaction — either everything commits or nothing does.

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
        ).with_for_update().first()  # row-level lock prevents race conditions

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
    db.flush()  # get order.id without committing yet

    for product, quantity, unit_price in items_to_create:
        product.stock_quantity -= quantity
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
            unit_price=unit_price,
        )
        db.add(order_item)

    db.commit()
    db.refresh(order)
    return order
```

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
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = place_order(order_in, current_user.id, db)
    background_tasks.add_task(send_confirmation_email, current_user.email, order.id)
    return order

@router.get("/", response_model=list[OrderResponse])
def list_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return current_user.orders
```

---

## Step 7: Background Tasks (Email Confirmation)

FastAPI's `BackgroundTasks` runs the function after the HTTP response is sent — the client doesn't wait for the email.

Already wired in Step 6. To simulate a real integration, swap `print()` with:

```python
import smtplib
from email.mime.text import MIMEText

def send_confirmation_email(email: str, order_id: int):
    msg = MIMEText(f"Your order #{order_id} has been confirmed!")
    msg["Subject"] = "Order Confirmed"
    msg["From"] = "noreply@shop.com"
    msg["To"] = email
    # with smtplib.SMTP("smtp.example.com", 587) as server:
    #     server.sendmail(msg["From"], [msg["To"]], msg.as_string())
    print(f"[SIMULATED EMAIL] To: {email}, Subject: {msg['Subject']}")
```

For production, use Celery + Redis to handle failures and retries. That's covered in `api-mastery/07_fastapi/advanced_guide.md`.

---

## Step 8: Testing with pytest + TestClient

The test strategy: use an in-memory SQLite database for speed, inject it via dependency override, and test each layer separately.

### tests/conftest.py

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ecommerce.main import app
from ecommerce.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

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
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

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
    assert "hashed_password" not in data  # never expose this

def test_register_duplicate_email(client, registered_user):
    response = client.post("/auth/register", json={
        "email": "test@example.com",
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
    assert response.status_code == 401
```

### Run tests

```bash
pytest tests/ -v
pytest tests/ -v --tb=short   # shorter tracebacks
pytest tests/test_auth.py -v  # single file
```

---

## Step 9: Dockerize with docker-compose

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir .

COPY src/ ./src/

ENV PYTHONPATH=/app/src

CMD ["uvicorn", "ecommerce.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

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
        condition: service_healthy
    volumes:
      - ./src:/app/src  # hot reload in dev

volumes:
  pgdata:
```

```bash
docker-compose up --build
docker-compose down -v  # tear down including volumes
```

---

## Step 10: Logging, Error Handling, and Rate Limiting

### Structured logging (main.py)

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)
```

### Global exception handler

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
```

### Rate limiting with SlowAPI

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to a route:
@router.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials: UserLogin, db: Session = Depends(get_db)):
    ...
```

### What to log

| Event | Level | What to include |
|-------|-------|----------------|
| Request received | INFO | method, path, user_id if authenticated |
| Order placed | INFO | order_id, user_id, total_amount |
| Auth failure | WARNING | email, IP address |
| Unhandled exception | ERROR | full traceback |
| DB connection issue | CRITICAL | connection string (redacted) |

---

## Navigation

| | |
|---|---|
| Back | [README.md](./README.md) |
| Architecture | [Architecture.md](./Architecture.md) |
| Starter Code | [starter_code/main.py](./starter_code/main.py) |
