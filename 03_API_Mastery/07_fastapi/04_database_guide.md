<a id="top"></a>

# FastAPI & Databases: Connecting to the Real World

> Vamsi's API can validate data, handle auth, and organize routes. Now it needs to actually remember things. This stage connects FastAPI to PostgreSQL — the combination used by most production Python backends.

<a id="toc"></a>

## Table of Contents

- [1. The Story](#1-the-story)
- [2. Setup and Installation](#2-setup-and-installation)
  - [Project Structure](#project-structure)
  - [Environment File](#environment-file)
- [3. Database Connection](#3-database-connection)
  - [Practice](#practice-connection)
- [4. SQLAlchemy Models](#4-sqlalchemy-models)
  - [Practice](#practice-models)
- [5. Pydantic Schemas vs SQLAlchemy Models](#5-pydantic-schemas-vs-sqlalchemy-models)
- [6. CRUD Operations](#6-crud-operations)
- [7. Routes and Database](#7-routes-and-database)
- [8. Alembic Migrations](#8-alembic-migrations)
  - [Initial Setup](#initial-setup)
  - [Configure alembic.ini](#configure-alembicini)
  - [Configure env.py](#configure-envpy)
  - [Creating and Running Migrations](#creating-and-running-migrations)
  - [Typical Workflow](#typical-workflow)
  - [Practice](#practice-migrations)
- [9. Async Database — SQLAlchemy 2.0](#9-async-database--sqlalchemy-20)
  - [Additional Dependencies](#additional-dependencies)
  - [Async Database Setup](#async-database-setup)
  - [Async CRUD](#async-crud)
  - [Async Routes](#async-routes)
  - [Sync vs Async — When to Use Which](#sync-vs-async--when-to-use-which)
- [10. Complete Working Application](#10-complete-working-application)
- [11. Summary](#11-summary)
- [12. Practice Questions](#12-practice-questions)

[Back to Top](#top)

<a id="1-the-story"></a>

# 1. The Story

Vamsi had built a solid FastAPI application — validated inputs, organized routes, clean dependencies. But every time he restarted the server during development, all his test data vanished. He was storing users in a Python dictionary, and dictionaries live only as long as the process runs.

"I need a real database," Vamsi said, staring at his terminal. He had heard of PostgreSQL, SQLAlchemy, and Alembic, but connecting them all together felt like wiring up a house for the first time. Which cable goes where? What breaks if you get the order wrong?

This guide follows Vamsi as he connects his FastAPI application to PostgreSQL for the first time — building a complete users API backed by a real database. Every tutorial that stores data in a Python dictionary eventually hits the same wall: restart the server and everything disappears. Real applications need a database.

The standard stack for FastAPI + databases is:

- **PostgreSQL** — the database (reliable, battle-tested, feature-rich)
- **SQLAlchemy** — the Python ORM (maps Python classes to database tables)
- **Alembic** — database migrations (manages schema changes over time)
- **psycopg2** — the PostgreSQL driver (SQLAlchemy uses it under the hood)

This stage builds a complete users API backed by a real PostgreSQL database.

[Back to Top](#top)

<a id="2-setup-and-installation"></a>

# 2. Setup and Installation

```bash
pip install sqlalchemy psycopg2-binary alembic python-dotenv passlib[bcrypt]
```

What each package does:

| Package | Purpose |
|---------|---------|
| `sqlalchemy` | ORM — maps Python classes to tables, handles queries |
| `psycopg2-binary` | PostgreSQL driver — SQLAlchemy speaks to Postgres through this |
| `alembic` | Migrations — tracks and applies database schema changes |
| `python-dotenv` | Loads `.env` files so you don't hardcode credentials |
| `passlib[bcrypt]` | Password hashing — never store plain text passwords |

<a id="project-structure"></a>

## Project Structure

```
myapp/
├── .env                    ← database URL and secrets (never commit this)
├── main.py                 ← FastAPI app, includes routers
├── database.py             ← engine, session, Base
├── models.py               ← SQLAlchemy table definitions
├── schemas.py              ← Pydantic input/output shapes
├── crud.py                 ← database operations
└── routers/
    └── users.py            ← route handlers
```

<a id="environment-file"></a>

## Environment File

```bash
# .env
DATABASE_URL=postgresql://myuser:mypassword@localhost:5432/mydb
SECRET_KEY=your-secret-key-here
```

Add `.env` to your `.gitignore` immediately. Never commit credentials.

> **Common Mistake:** Vamsi once accidentally committed his `.env` file to GitHub. Even after deleting it, the credentials were in the git history. Always add `.env` to `.gitignore` before your first commit, and if you slip up, rotate all exposed credentials immediately.

[Back to Top](#top)

<a id="3-database-connection"></a>

# 3. Database Connection — `database.py`

```python


# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/mydb")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Dependency for getting DB session — used by every route that needs the database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**What each piece does:**

`create_engine(DATABASE_URL)` — Creates the connection pool. SQLAlchemy maintains a pool of connections so your app isn't opening and closing a connection on every request.

`sessionmaker(autocommit=False, autoflush=False, bind=engine)` — A factory that creates `Session` objects. `autocommit=False` means changes aren't written to the database until you call `db.commit()`. `autoflush=False` means SQLAlchemy won't automatically send pending changes before each query.

`Base = declarative_base()` — The base class that all your SQLAlchemy models will inherit from. It provides the metaclass magic that turns Python class attributes into database columns.

`get_db()` — The FastAPI dependency. It opens a session, yields it to the route handler, and always closes it when the route finishes (even if the route raised an exception). This is the `yield` dependency pattern from the previous stage applied to database sessions.

> **Common Mistake:** Vamsi initially forgot the `finally: db.close()` block. Under load, his app ran out of database connections because sessions were never returned to the pool. The `try/finally` pattern ensures cleanup happens even when routes raise exceptions.

<a id="practice-connection"></a>

## Practice

> **Practice:** [Q36 - db-connection-pooling](../api_practice_questions_100.md#q36--thinking--db-connection-pooling)

[Back to Top](#top)

<a id="4-sqlalchemy-models"></a>

# 4. SQLAlchemy Models — `models.py`

SQLAlchemy models describe your database tables as Python classes. Each class is a table. Each class attribute is a column.

```python


# models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    orders = relationship("Order", back_populates="user")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), default="pending")
    total = Column(Integer, default=0)  # store in cents to avoid float issues
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)

    user = relationship("User", back_populates="orders")
```

**Column options explained:**

| Option | Meaning |
|--------|---------|
| `primary_key=True` | This column is the table's primary key |
| `index=True` | Create a database index — speeds up lookups on this column |
| `unique=True` | Enforce uniqueness at the database level |
| `nullable=False` | Column cannot be NULL — database enforces this |
| `default=True` | Python-side default (used when creating objects in code) |
| `server_default=func.now()` | Database-side default (PostgreSQL sets this) |

**Relationships:**

`relationship("Order", back_populates="user")` tells SQLAlchemy that a `User` has many `Order` objects, and they're linked by the `user_id` foreign key. After loading a user, you can access `user.orders` and SQLAlchemy will query for related orders automatically.

`back_populates` makes the relationship bidirectional — `order.user` navigates back to the user.

> **Common Mistake:** Vamsi initially used `default=func.now()` instead of `server_default=func.now()`. The difference: `default` sets the value in Python when the object is created, while `server_default` tells PostgreSQL to set it. If you use `default`, the timestamp comes from the application server's clock. With `server_default`, it comes from the database server — which is what you want for consistency across multiple app instances.

<a id="practice-models"></a>

## Practice

> **Practice:** [Q37 - orm-vs-raw-sql](../api_practice_questions_100.md#q37--interview--orm-vs-raw-sql)

[Back to Top](#top)

<a id="5-pydantic-schemas-vs-sqlalchemy-models"></a>

# 5. Pydantic Schemas vs SQLAlchemy Models — The Critical Distinction

This is the most important concept to internalize. There are **two completely separate things** that look similar but serve different purposes:

```
Request Body (JSON)
      │
      ▼
Pydantic Schema (validates, parses)       ← schemas.py
      │
      ▼
Service / CRUD layer
      │
      ▼
SQLAlchemy Model (reads/writes DB)        ← models.py
      │
      ▼
PostgreSQL Database
      │
      ▼
SQLAlchemy Model (query result)
      │
      ▼
Pydantic Schema (serializes to JSON)
      │
      ▼
Response Body (JSON)
```

**SQLAlchemy models** represent database tables. They have no concept of HTTP, validation, or JSON. They're for talking to the database.

**Pydantic schemas** represent what the API accepts and returns. They validate input, serialize output, and generate the Swagger documentation.

You will always have both, and they will often look similar but serve completely different roles.

```python
# schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ── User schemas ──────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    """What the client sends when registering. Password is plain text here —
    it gets hashed before it ever touches the database."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """All fields optional — PATCH semantics."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None


class UserResponse(BaseModel):
    """What the API returns. Note: no password field — never expose it."""
    id: int
    name: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # allows reading from SQLAlchemy model attributes


# ── Order schemas ─────────────────────────────────────────────────────────────

class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    total: int
    created_at: datetime

    class Config:
        from_attributes = True
```

**`class Config: from_attributes = True`** — Without this, Pydantic only reads data from dictionaries. With it, Pydantic can also read from objects by attribute access — which is how SQLAlchemy models work. You need this on every response schema that gets populated from a SQLAlchemy object.

**`EmailStr`** — Built into Pydantic (requires `pip install pydantic[email]`). Validates that the string looks like an email address, more rigorously than a manual `@` check.

> **Common Mistake:** Vamsi forgot `from_attributes = True` on his `UserResponse` schema and got a cryptic validation error when FastAPI tried to serialize the SQLAlchemy object. The error said something about expecting a dict but receiving a `User` object. This single config line bridges the gap between SQLAlchemy objects and Pydantic serialization.

[Back to Top](#top)

<a id="6-crud-operations"></a>

# 6. CRUD Operations — `crud.py`

The CRUD layer contains all database operations. Routes call these functions; they don't write SQL or query the database directly.

```python
# crud.py
from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate, UserUpdate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── User operations ───────────────────────────────────────────────────────────

def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def list_users(db: Session, skip: int = 0, limit: int = 20) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, updates: UserUpdate) -> User | None:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    update_data = updates.dict(exclude_unset=True)  # only fields the client sent
    for field, value in update_data.items():
        setattr(db_user, field, value)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True
```

**Key patterns explained:**

`db.query(User).filter(User.id == user_id).first()` — SQLAlchemy's query interface. `.filter()` adds a WHERE clause. `.first()` returns one result or `None`. `.all()` returns a list.

`db.add(db_user)` — Marks the object as "should be inserted". Nothing happens in the database yet.

`db.commit()` — Writes all pending changes to the database in a transaction. If anything fails, the whole transaction rolls back.

`db.refresh(db_user)` — After a commit, the object's `id` and `created_at` (set by the database) are populated. `refresh` loads them back into the Python object.

`updates.dict(exclude_unset=True)` — On a PATCH request, the client only sends fields they want to change. `exclude_unset=True` returns only the fields that were explicitly provided, not the ones that defaulted to `None`. This prevents accidentally overwriting existing data with `None`.

> **Common Mistake:** Vamsi once called `db.commit()` inside a loop that created multiple users. When the third insert failed (duplicate email), the first two were already committed and couldn't be rolled back. The fix: call `db.add()` for all objects first, then `db.commit()` once. If anything fails, the entire batch rolls back cleanly.

[Back to Top](#top)

<a id="7-routes-and-database"></a>

# 7. Routes and Database — The Full Stack

```python
# routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import crud
import schemas

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=schemas.UserResponse, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user. Returns 409 if email already exists."""
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    return crud.create_user(db, user)


@router.get("/", response_model=list[schemas.UserResponse])
def list_users(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """List users with offset pagination."""
    return crud.list_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID."""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, updates: schemas.UserUpdate, db: Session = Depends(get_db)):
    """Partially update a user. Only sends changed fields."""
    user = crud.update_user(db, user_id, updates)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user. Returns 204 No Content on success."""
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
```

And the main application file:

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import users

# Create tables on startup (for development — use Alembic in production)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Users API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
```

`Base.metadata.create_all(bind=engine)` reads all your SQLAlchemy models (any class that inherits from `Base`) and creates their tables if they don't exist. This is convenient for development but in production you manage schema changes through Alembic migrations.

[Back to Top](#top)

<a id="8-alembic-migrations"></a>

# 8. Alembic Migrations

`Base.metadata.create_all()` is great for getting started, but it has a critical limitation: once a table exists, it won't alter it. If you add a column to your model, `create_all` does nothing — the column doesn't appear in the database.

Alembic solves this. It tracks your schema history and generates SQL migration scripts.

<a id="initial-setup"></a>

## Initial Setup

```bash
alembic init alembic
```

This creates:
```
alembic/
├── env.py          ← configuration, tells Alembic about your models
├── versions/       ← migration scripts live here
alembic.ini         ← main config file
```

<a id="configure-alembicini"></a>

## Configure `alembic.ini`

Find this line and update it:
```ini
# alembic.ini
sqlalchemy.url = postgresql://myuser:mypassword@localhost:5432/mydb
```

Or better, use an environment variable:
```ini
sqlalchemy.url = %(DATABASE_URL)s
```

<a id="configure-envpy"></a>

## Configure `alembic/env.py`

Find the `target_metadata = None` line and replace it:

```python
# alembic/env.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import Base
from models import User, Order  # import all models so Alembic sees them

target_metadata = Base.metadata
```

Alembic needs to import your models to know what the "current" schema looks like. That's why you explicitly import them here.

<a id="creating-and-running-migrations"></a>

## Creating and Running Migrations

```bash
# Generate a migration script by comparing your models to the current database
alembic revision --autogenerate -m "create users and orders tables"

# Apply pending migrations to the database
alembic upgrade head

# Check current migration version
alembic current

# Roll back one migration

alembic downgrade -1


# View migration history
alembic history
```

After running `alembic revision --autogenerate`, inspect the generated file in `alembic/versions/`. Alembic is good at detecting new tables and columns but sometimes misses index changes or complex constraints. Always review the generated migration before running it.

> **Common Mistake:** Vamsi ran `alembic revision --autogenerate` without importing his new `Order` model in `env.py`. Alembic generated an empty migration because it didn't know the model existed. Always import every model in `alembic/env.py` so autogenerate can see the full schema.

<a id="typical-workflow"></a>

## Typical Workflow

```bash
# 1. Modify your SQLAlchemy model (add a column, new table, etc.)
# 2. Generate the migration
alembic revision --autogenerate -m "add profile_picture to users"

# 3. Review alembic/versions/xxxx_add_profile_picture_to_users.py
# 4. Apply it
alembic upgrade head

# 5. Deploy — run alembic upgrade head on the production server too
```

<a id="practice-migrations"></a>

## Practice

> **Practice:** [Q38 - n-plus-one-query](../api_practice_questions_100.md#q38--critical--n-plus-one-query)
>
> **Practice:** [Q96 - debug-n-plus-one-load](../api_practice_questions_100.md#q96--debug--debug-n-plus-one-load)

[Back to Top](#top)

<a id="9-async-database--sqlalchemy-20"></a>

# 9. Async Database — SQLAlchemy 2.0

The async version matters when your application is I/O-heavy and you want to handle many concurrent requests efficiently. Async routes don't block the event loop while waiting for the database.

<a id="additional-dependencies"></a>

## Additional Dependencies

```bash
pip install asyncpg sqlalchemy[asyncio]
```

`asyncpg` is the async PostgreSQL driver. `sqlalchemy[asyncio]` adds async support to SQLAlchemy.

<a id="async-database-setup"></a>

## Async Database Setup

```python
# database_async.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv()

# Note: postgresql+asyncpg:// not postgresql://
DATABASE_URL = os.getenv(
    "DATABASE_URL_ASYNC",
    "postgresql+asyncpg://user:pass@localhost/mydb"
)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

<a id="async-crud"></a>

## Async CRUD

```python
# crud_async.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import User
from schemas import UserCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_user(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def list_users(db: AsyncSession, skip: int = 0, limit: int = 20) -> list[User]:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    db_user = User(
        name=user.name,
        email=user.email,
        hashed_password=pwd_context.hash(user.password)
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
```

The key differences from sync SQLAlchemy:
- All database calls are `await`ed
- Queries use `select(Model).where(...)` instead of `db.query(Model).filter(...)`
- `result.scalar_one_or_none()` extracts a single result
- `result.scalars().all()` extracts a list

<a id="async-routes"></a>

## Async Routes

```python
# routers/users_async.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database_async import get_db
import crud_async as crud
import schemas

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=schemas.UserResponse, status_code=201)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    if await crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    return await crud.create_user(db, user)


@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

Routes that use async CRUD must themselves be `async def`. FastAPI handles both `def` and `async def` routes — sync routes run in a thread pool so they don't block the event loop.

<a id="sync-vs-async--when-to-use-which"></a>

## Sync vs Async — When to Use Which

| Scenario | Recommendation |
|----------|---------------|
| Simple CRUD app, small team | Sync — easier to debug, fewer footguns |
| High concurrency, many I/O operations | Async — better throughput |
| Mixed CPU + I/O work | Sync — CPU work blocks regardless |
| Learning FastAPI | Start sync, migrate async when needed |

Don't use async just because it sounds better. Sync SQLAlchemy is simpler, easier to debug, and fast enough for most applications. Async shines specifically when you have thousands of concurrent requests all waiting on I/O simultaneously.

> **Common Mistake:** Vamsi mixed sync and async database calls in the same route — calling a sync `db.query()` inside an `async def` route. This blocks the event loop and defeats the purpose of async. If your route is `async def`, all database operations in that route must use `await`. If you need sync operations, use a regular `def` route and let FastAPI handle the thread pool.

[Back to Top](#top)

<a id="10-complete-working-application"></a>

# 10. Complete Working Application

Putting it all together — a fully functional users API:

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers.users import router as users_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Users API",
    description="A production-ready users service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

To run:

```bash
# Start PostgreSQL (if using Docker)
docker run -d \
  --name postgres \
  -e POSTGRES_USER=myuser \
  -e POSTGRES_PASSWORD=mypassword \
  -e POSTGRES_DB=mydb \
  -p 5432:5432 \
  postgres:15

# Set environment variable
export DATABASE_URL=postgresql://myuser:mypassword@localhost:5432/mydb

# Start the API
uvicorn main:app --reload
```

Open `http://localhost:8000/docs` — you have a fully documented API backed by a real PostgreSQL database.

[Back to Top](#top)

<a id="11-summary"></a>

# 11. Summary

| Layer | File | Purpose |
|-------|------|---------|
| Connection | `database.py` | Engine, session factory, `get_db` dependency |
| Tables | `models.py` | SQLAlchemy classes — define what's in the database |
| API shapes | `schemas.py` | Pydantic classes — define what the API accepts and returns |
| DB logic | `crud.py` | All queries and mutations — nothing else goes here |
| Routes | `routers/users.py` | HTTP handling — calls CRUD, raises HTTP errors |
| App | `main.py` | Creates app, adds middleware, registers routers |
| Migrations | `alembic/` | Schema change history — how the database evolves |

The clean separation between layers is the entire point. `crud.py` doesn't know about HTTP. `models.py` doesn't know about JSON. `schemas.py` doesn't know about the database. Each file has one job, and changes in one layer don't ripple into others.

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                      │
├─────────────────────────────────────────────────────────────┤
│  Client Request                                              │
│       │                                                      │
│       ▼                                                      │
│  routers/users.py  (HTTP layer — validates, routes)          │
│       │                                                      │
│       ▼                                                      │
│  schemas.py        (Pydantic — parse input, shape output)    │
│       │                                                      │
│       ▼                                                      │
│  crud.py           (Business logic — queries, mutations)     │
│       │                                                      │
│       ▼                                                      │
│  models.py         (SQLAlchemy — table definitions)          │
│       │                                                      │
│       ▼                                                      │
│  database.py       (Connection pool — engine, sessions)      │
│       │                                                      │
│       ▼                                                      │
│  PostgreSQL        (Persistent storage)                      │
└─────────────────────────────────────────────────────────────┘
```

[Back to Top](#top)

<a id="12-practice-questions"></a>

# 12. Practice Questions

> **Practice:** [Q39 - db-transactions-rest](../api_practice_questions_100.md#q39--thinking--db-transactions-rest)

[Back to Top](#top)

<a id="fire-summary"></a>

# 🔥 Summary

| Concept | One-liner |
|---------|-----------|
| Database connection | `create_engine` + `sessionmaker` + `get_db` yield dependency |
| SQLAlchemy models | Python classes that map to PostgreSQL tables |
| Pydantic schemas | Validate API input, serialize API output — separate from DB models |
| CRUD layer | All database logic isolated in one file, routes never touch SQL |
| Alembic | Schema migration tool — generates and applies incremental SQL changes |
| Async SQLAlchemy | `asyncpg` + `select()` + `await` — use only when high concurrency demands it |
| `from_attributes = True` | Bridges SQLAlchemy objects to Pydantic serialization |
| Session lifecycle | Open per request, yield to route, close in finally block |
| `exclude_unset=True` | PATCH semantics — only update fields the client explicitly sent |
| `server_default` vs `default` | Database-side vs Python-side default values |

<a id="nav"></a>

## Navigation

**[Back to README](../README.md)**

**Prev:** [FastAPI Core Guide](03_core_guide.md)

**Next:** [FastAPI Advanced Guide](05_advanced_guide.md)

**Related Topics:** [FastAPI Core Guide](03_core_guide.md) | [Testing APIs](../10_testing_documentation/testing_apis.md) | [API Performance & Scaling](../09_api_performance_scaling/performance_guide.md)

[Back to Top](#top)
