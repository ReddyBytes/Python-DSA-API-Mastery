# Project 05 — JWT Authentication System

Build a production-style authentication API with FastAPI. Users register, log in, and receive **JWT tokens** that protect private endpoints.

This is a minimal-hints project. Each step tells you what to build and gives you one collapsible hint. The full solution is at the bottom — open it only after you've tried.

---

## Step 1: Project Setup

**Requirements:**
- Create the project folder with this layout: `main.py`, `database.py`, `models.py`, `schemas.py`, `auth.py`, `dependencies.py`, `routers/auth.py`, `.env`
- Install all required packages in one command
- Load `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, and `REFRESH_TOKEN_EXPIRE_DAYS` from `.env` using python-dotenv
- Run the app with uvicorn on port 8000 and confirm the `/docs` page loads

**You need to know:**
- **python-dotenv**: Reads key=value pairs from a `.env` file into `os.environ` at startup
- **python-jose**: A Python library for signing and verifying JWT tokens
- **passlib**: A password hashing library that wraps bcrypt and other schemes
- **SQLAlchemy**: Python ORM for defining database tables as classes and querying them

<details>
<summary>💡 Hint</summary>

Install command:
```bash
pip install fastapi uvicorn[standard] "python-jose[cryptography]" "passlib[bcrypt]" sqlalchemy python-dotenv
```

In your entry point, call `load_dotenv()` before reading `os.getenv(...)`. Put your `SECRET_KEY` as a long random string in `.env` — never hardcode it.

</details>

---

## Step 2: Database Model

**Requirements:**
- Define a `User` SQLAlchemy model with columns: `id` (int, primary key, autoincrement), `email` (str, unique, indexed), `hashed_password` (str), `is_active` (bool, default True), `created_at` (datetime, default utcnow)
- Create a SQLite engine pointing to `./users.db`
- Create a `SessionLocal` factory for getting DB sessions
- Call `Base.metadata.create_all(bind=engine)` on startup so the table is created automatically

**You need to know:**
- **DeclarativeBase**: SQLAlchemy's base class — all model classes inherit from it so SQLAlchemy can track them
- **SessionLocal**: A factory (not a session itself) — you call it each request to get a fresh DB connection, then close it after
- **create_all**: Inspects all registered models and issues `CREATE TABLE IF NOT EXISTS` — safe to call on every startup

<details>
<summary>💡 Hint</summary>

Use `create_engine("sqlite:///./users.db", connect_args={"check_same_thread": False})` — the `check_same_thread` argument is required for SQLite when used with FastAPI's async request handling.

</details>

---

## Step 3: Password Hashing

**Requirements:**
- Create a `CryptContext` using the `bcrypt` scheme with `deprecated="auto"`
- Write `hash_password(plain: str) -> str` that returns the bcrypt hash
- Write `verify_password(plain: str, hashed: str) -> bool` that returns True only if they match
- These functions must live in `auth.py`

**You need to know:**
- **bcrypt**: A one-way hashing algorithm designed to be slow — it makes brute-force attacks expensive even if the database is stolen
- **CryptContext**: passlib's unified interface — it handles salt generation, hashing, and verification in one object so you never touch raw bcrypt directly
- **One-way hash**: You can verify a password against a hash, but you cannot reverse the hash back to the original password

<details>
<summary>💡 Hint</summary>

`CryptContext(schemes=["bcrypt"], deprecated="auto")` gives you a `pwd_context` object. Call `pwd_context.hash(plain)` to hash and `pwd_context.verify(plain, hashed)` to check. No salt management needed — bcrypt embeds the salt in the hash string.

</details>

---

## Step 4: JWT Token Creation

**Requirements:**
- Write `create_access_token(data: dict, expires_delta: timedelta) -> str` in `auth.py`
- The token payload must include the `sub` claim (subject = user email) and an `exp` claim (expiry timestamp)
- Sign with `SECRET_KEY` using algorithm `HS256`
- Access token expiry: 15 minutes. Refresh token expiry: 7 days
- Write a separate `create_refresh_token(data: dict) -> str` — same logic, different expiry

**You need to know:**
- **JWT (JSON Web Token)**: A base64-encoded, signed string with three parts: header, payload, signature — the server can verify the signature without a database lookup
- **`sub` claim**: JWT standard field for "subject" — conventionally the user identifier (email or user ID)
- **`exp` claim**: JWT standard field for expiry — `python-jose` checks this automatically on decode and raises an error if expired

<details>
<summary>💡 Hint</summary>

Use `jose.jwt.encode(payload_dict, SECRET_KEY, algorithm="HS256")`. Build the payload as `{**data, "exp": datetime.utcnow() + expires_delta}`. The `data` dict you pass in should be `{"sub": user.email}`.

</details>

---

## Step 5: JWT Token Verification

**Requirements:**
- Write `get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db))` in `dependencies.py`
- Use `OAuth2PasswordBearer(tokenUrl="/auth/login")` as the scheme — this reads the Bearer token from the `Authorization` header automatically
- Decode the token with `jose.jwt.decode(...)`, extract `sub` (email), fetch user from DB
- Raise `HTTPException(status_code=401, detail="Could not validate credentials")` for any failure: missing token, expired token, invalid signature, user not found

**You need to know:**
- **FastAPI dependency injection**: Marking a parameter with `Depends(fn)` tells FastAPI to call `fn` first and inject its return value — used to share DB sessions and auth logic across routes
- **OAuth2PasswordBearer**: A FastAPI helper that extracts the JWT from the `Authorization: Bearer <token>` header and raises 401 automatically if the header is missing
- **`JWTError`**: The exception `python-jose` raises for any decode failure — catch this and convert to a 401

<details>
<summary>💡 Hint</summary>

Wrap the entire decode + DB lookup in a `try/except JWTError`. After decoding, do `email = payload.get("sub")` — if it's `None`, raise 401. Then query `db.query(User).filter(User.email == email).first()` and raise 401 if the user is `None`.

</details>

---

## Step 6: Register Endpoint

**Requirements:**
- `POST /auth/register` accepts `{"email": "...", "password": "..."}` in the request body
- Check if the email already exists in DB — if so, return `400 Bad Request` with `"Email already registered"`
- Hash the password before storing — never store the plain-text password
- Insert the new user and commit
- Return `201 Created` with `{"id": ..., "email": ..., "is_active": ..., "created_at": ...}` — no `hashed_password` in the response

**You need to know:**
- **Pydantic schema separation**: Use one schema for the request body (`UserCreate` with `password`) and a different one for the response (`UserOut` with no password field) — FastAPI serializes the response using the `response_model`
- **`response_model_exclude`**: An alternative to separate schemas — you can exclude fields at the route level, but a dedicated response schema is cleaner
- **`status_code=201`**: Pass this to `@router.post(...)` to return HTTP 201 instead of the default 200

<details>
<summary>💡 Hint</summary>

Define `UserCreate(BaseModel)` with `email: str` and `password: str`. Define `UserOut(BaseModel)` with `id`, `email`, `is_active`, `created_at` — add `model_config = ConfigDict(from_attributes=True)` so Pydantic can read SQLAlchemy model instances directly.

</details>

---

## Step 7: Login Endpoint

**Requirements:**
- `POST /auth/login` accepts `{"email": "...", "password": "..."}` in the request body
- Fetch the user by email — if not found, return `401 Unauthorized` with `"Invalid credentials"` (do not reveal whether the email exists)
- Verify the password with `verify_password()` — if wrong, return the same `401` with the same generic message
- On success, create both an access token and a refresh token
- Return `{"access_token": "...", "refresh_token": "...", "token_type": "bearer"}`

**You need to know:**
- **Generic error messages**: Returning the same message for "email not found" and "wrong password" prevents attackers from using your login endpoint to enumerate valid emails
- **Refresh token**: A longer-lived token stored by the client — it is exchanged for a new access token when the short-lived one expires, without asking the user to log in again
- **`token_type: "bearer"`**: The OAuth2 convention for how the token should be sent — clients put it in `Authorization: Bearer <token>`

<details>
<summary>💡 Hint</summary>

Create both tokens with `{"sub": user.email}` as the data payload. The only difference between them is the `expires_delta` you pass. Return them together in a single response dict — no DB write needed for the refresh token in this basic version.

</details>

---

## Step 8: Protected Endpoint

**Requirements:**
- `GET /me` returns the currently authenticated user's profile
- Use `Depends(get_current_user)` to inject the user — do not repeat auth logic inside the route
- Return `{"id": ..., "email": ..., "is_active": ..., "created_at": ...}`
- If called without a valid token, FastAPI should automatically return `401`

**You need to know:**
- **FastAPI dependency chain**: Dependencies can call other dependencies — `get_current_user` calls `get_db` and `oauth2_scheme` internally, so the route only needs `Depends(get_current_user)`
- **`response_model`**: Setting this on the route decorator tells FastAPI to filter and validate the return value against the schema — extra fields (like `hashed_password`) are automatically stripped

<details>
<summary>💡 Hint</summary>

The route body is just two lines: the function signature with `current_user: User = Depends(get_current_user)` and a `return current_user`. All the auth work happens inside the dependency. Set `response_model=UserOut` on the decorator.

</details>

---

## Step 9: Refresh Token Endpoint

**Requirements:**
- `POST /refresh` accepts `{"refresh_token": "..."}` in the request body
- Decode and validate the refresh token — raise `401` if expired or invalid
- Issue a new access token (15 min) using the same `sub` from the refresh token payload
- Return `{"access_token": "...", "token_type": "bearer"}` — do not issue a new refresh token here
- Do not require the `Authorization` header for this endpoint — the refresh token is in the request body

**You need to know:**
- **Token rotation strategy**: Some systems issue a new refresh token on every refresh call (rotating refresh tokens) — this simpler version keeps the same refresh token until it expires in 7 days
- **Decode without `OAuth2PasswordBearer`**: For this endpoint, read the token from the request body directly using a Pydantic schema — `oauth2_scheme` only reads from the Authorization header

<details>
<summary>💡 Hint</summary>

Create a `RefreshRequest(BaseModel)` schema with `refresh_token: str`. In the route, call `jose.jwt.decode(body.refresh_token, SECRET_KEY, algorithms=["HS256"])` directly — same decode logic as `get_current_user`, just reading from a different place.

</details>

---

## Step 10: Test It

Run all four endpoints in order to confirm the full auth flow works end to end.

**Requirements:**
- Register a new user and confirm you get back user info (no password hash)
- Log in and save both tokens from the response
- Hit `/me` with the access token and confirm you get your profile back
- Hit `/me` with a bad token and confirm you get `401`
- Call `/refresh` with the refresh token and confirm you get a new access token
- Call `/me` with the new access token and confirm it still works

**You need to know:**
- **Bearer header format**: The Authorization header must be exactly `Authorization: Bearer <token>` — a missing space or wrong casing will cause a 401
- **curl `-X POST -H -d`**: `-X POST` sets the method, `-H "Content-Type: application/json"` sets the header, `-d '{...}'` sends the body

<details>
<summary>💡 Hint</summary>

Use these curl commands in order:

```bash
# Step 1 — register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "secret123"}'

# Step 2 — login, save the tokens
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "secret123"}'

# Step 3 — use access token (paste your token)
curl http://localhost:8000/me \
  -H "Authorization: Bearer <access_token>"

# Step 4 — refresh
curl -X POST http://localhost:8000/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'
```

</details>

---

## Full Solution

<details>
<summary>✅ Complete working code (only open after you've tried)</summary>

### `.env.example`

```bash
SECRET_KEY=your-super-secret-key-change-this-in-production  # ← long random string, never commit the real one
ACCESS_TOKEN_EXPIRE_MINUTES=15                               # ← short-lived access token
REFRESH_TOKEN_EXPIRE_DAYS=7                                  # ← long-lived refresh token
```

---

### `database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()  # ← must run before any os.getenv() calls

SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"  # ← file-based SQLite in current dir

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # ← required for SQLite + FastAPI threading model
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # ← factory, not a session

class Base(DeclarativeBase):  # ← all models inherit from this so SQLAlchemy can track them
    pass
```

---

### `models.py`

```python
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"  # ← name of the table in SQLite

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)  # ← unique + indexed for fast login lookups
    hashed_password = Column(String, nullable=False)                 # ← never store plain-text passwords
    is_active = Column(Boolean, default=True)                        # ← allows soft-disabling accounts
    created_at = Column(DateTime, default=datetime.utcnow)           # ← audit trail
```

---

### `schemas.py`

```python
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

class UserCreate(BaseModel):           # ← input schema — includes raw password
    email: EmailStr                    # ← Pydantic validates email format automatically
    password: str

class UserOut(BaseModel):              # ← output schema — never includes hashed_password
    id: int
    email: str
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)  # ← lets Pydantic read SQLAlchemy ORM objects

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):        # ← login response — both tokens
    access_token: str
    refresh_token: str
    token_type: str = "bearer"         # ← OAuth2 convention

class RefreshRequest(BaseModel):       # ← refresh endpoint input
    refresh_token: str

class AccessTokenResponse(BaseModel):  # ← refresh endpoint output — new access token only
    access_token: str
    token_type: str = "bearer"
```

---

### `auth.py`

```python
import os
from datetime import datetime, timedelta

from jose import jwt                           # ← python-jose for JWT encode/decode
from passlib.context import CryptContext       # ← passlib for bcrypt hashing

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-change-me")  # ← read from .env
ALGORITHM = "HS256"                                                  # ← HMAC-SHA256 signing algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")   # ← bcrypt with automatic upgrade support

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)             # ← bcrypt generates and embeds the salt automatically

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)   # ← extracts salt from hash, rehashes plain, compares

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()                    # ← never mutate the caller's dict
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode["exp"] = expire                  # ← jose checks this claim automatically on decode
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode["exp"] = expire
    to_encode["type"] = "refresh"              # ← custom claim to distinguish refresh from access tokens
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

---

### `dependencies.py`

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from auth import SECRET_KEY, ALGORITHM
from database import SessionLocal
from models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # ← reads Bearer token from Authorization header

def get_db():
    """Yield a DB session per request, always close it after."""
    db = SessionLocal()
    try:
        yield db                # ← FastAPI calls this before the route, injects db, then runs finally
    finally:
        db.close()              # ← always close even if the route raises an exception

def get_current_user(
    token: str = Depends(oauth2_scheme),  # ← oauth2_scheme raises 401 automatically if header is missing
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},  # ← OAuth2 spec requires this header on 401
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # ← raises JWTError if expired or tampered
        email: str = payload.get("sub")  # ← sub claim holds the user identifier
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception      # ← catches expired, invalid signature, malformed token

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception      # ← valid token but user was deleted from DB
    return user
```

---

### `routers/auth.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from auth import (
    SECRET_KEY, ALGORITHM,
    hash_password, verify_password,
    create_access_token, create_refresh_token,
)
from database import SessionLocal
from dependencies import get_db, get_current_user
from models import User
from schemas import (
    UserCreate, UserOut,
    LoginRequest, TokenResponse,
    RefreshRequest, AccessTokenResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])  # ← all routes in this file get /auth prefix

@router.post("/register", response_model=UserOut, status_code=201)  # ← 201 Created for new resources
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")  # ← 400 not 409 to keep it simple

    new_user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),  # ← hash before storing, never store plain text
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)       # ← re-fetches the row so id and created_at are populated
    return new_user            # ← UserOut schema strips hashed_password from the response

@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",             # ← same message for both failures — don't leak which one
        )

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)
```

---

### `main.py`

```python
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

import models
from database import Base, engine
from dependencies import get_current_user, get_db
from models import User
from routers import auth as auth_router
from schemas import AccessTokenResponse, RefreshRequest, UserOut
from auth import SECRET_KEY, ALGORITHM, create_access_token
from jose import JWTError, jwt
from fastapi import HTTPException, status

Base.metadata.create_all(bind=engine)  # ← create tables on startup if they don't exist

app = FastAPI(title="JWT Auth System")

app.include_router(auth_router.router)  # ← mounts all /auth/* routes

@app.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):  # ← dependency handles all auth logic
    return current_user                                         # ← UserOut strips hashed_password

@app.post("/refresh", response_model=AccessTokenResponse)
def refresh_token(body: RefreshRequest):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )
    try:
        payload = jwt.decode(body.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")         # ← check custom claim to reject access tokens here
        if email is None or token_type != "refresh":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    new_access_token = create_access_token(data={"sub": email})  # ← issue fresh access token
    return AccessTokenResponse(access_token=new_access_token)
```

---

### Run it

```bash
# Start the server
uvicorn main:app --reload --port 8000

# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "hunter2"}'

# Login — copy both tokens from response
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "hunter2"}'

# Hit protected route
curl http://localhost:8000/me \
  -H "Authorization: Bearer <paste_access_token_here>"

# Refresh
curl -X POST http://localhost:8000/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<paste_refresh_token_here>"}'
```

</details>

---

Back to [Capstone Projects README](../README.md) | Next: [Project 08 — Celery Task Queue](../08_Celery_Task_Queue/Project_Guide.md)
