# Project 12 — 2FA / TOTP Authentication

> A TOTP code is like a time-locked safe that both you and the bank have a copy of — every 30 seconds the combination changes, and both sides compute it independently using nothing but the shared secret and the current time. No network call, no central oracle. Pure math.

**Learning Format:** Minimal Hints — requirements and concepts given. You figure out the implementation.
**What You Build:** Extend the JWT auth system (Project 05) with TOTP-based 2FA. Users can enable 2FA, scan a QR code with Google Authenticator or Authy, and must enter a 6-digit code at login. Backup codes handle recovery.
**Concepts Covered:** TOTP algorithm (RFC 6238), HMAC-SHA1 time-based codes, QR code generation, backup codes, 2FA enrollment flow, partial auth tokens

---

## Prerequisites

- Project 05 (JWT Auth System) — you will extend it
- Dependencies:

```bash
pip install pyotp "qrcode[pil]" pillow fastapi uvicorn python-jose bcrypt sqlalchemy python-dotenv
```

---

## How TOTP Works (Read This First)

**TOTP = HMAC-SHA1(secret, floor(unix_time / 30))**

Both the server and the authenticator app hold the same **shared secret** — a 32-character base32 string generated once at enrollment. Every 30 seconds, both sides independently compute a 6-digit code using the same formula. No network call. No state sync. Just math.

```
Enrollment:
  Server generates secret ──────────────────────────────────────────────┐
  Server stores secret in DB (pending until user confirms)              │
  Server builds otpauth:// URI with secret embedded                     │
  Server renders QR code from URI                                       │
  User scans QR code ─── Authenticator app stores secret locally ───────┘

Login (both sides run this independently):
  Server:        TOTP(secret, floor(now/30))  →  482931
  User's phone:  TOTP(secret, floor(now/30))  →  482931
                                                    ↑
                                               same result because same secret + same time window

  Code matches → issue session token
```

**Time drift:** Clocks are never perfectly in sync. Servers allow ±1 window (±30 seconds) to handle clock skew between server and phone.

**Why base32?** QR codes and URLs handle base32 cleanly. The secret is binary bytes encoded into a printable-safe alphabet.

---

## Step 1 — TOTP Secret Generation and QR Code

Build `POST /auth/2fa/enable` (requires a valid session JWT):

- Generate a new TOTP secret for the authenticated user
- Store it in the database marked as **pending** (not active — the user has not confirmed it yet)
- Build a valid `otpauth://totp/` URI that authenticator apps understand
- Render that URI as a PNG QR code and return it as a base64 data URL so it renders in a browser or API response
- Also return the raw secret string so users can enter it manually if they cannot scan

The QR code URI format is:

```
otpauth://totp/AppName:user@email.com?secret=BASE32SECRET&issuer=AppName
```

<details><summary>💡 Hint</summary>

`pyotp.random_base32()` generates the secret.

`pyotp.totp.TOTP(secret).provisioning_uri(name=user_email, issuer_name="MyApp")` builds the full otpauth URI automatically.

`qrcode.make(uri)` returns a PIL Image. To convert to a base64 data URL:

```python
import io, base64
buf = io.BytesIO()
img.save(buf, format="PNG")
data_url = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
```

</details>

---

## Step 2 — Verify and Activate 2FA

Build `POST /auth/2fa/verify` (requires a valid session JWT, body: `{"code": "482931"}`):

- Look up the **pending** TOTP secret for the authenticated user
- Verify the submitted 6-digit code against that secret
- If invalid: return 400 — do not activate
- If valid: mark 2FA as active in the database
- Generate 10 one-time backup codes and return them to the user — this is the **only time** they are shown
- Store backup codes hashed (not plaintext) in the database

The user must save the backup codes. They are for account recovery when the phone is lost.

<details><summary>💡 Hint — Verifying the code</summary>

```python
totp = pyotp.TOTP(secret)
totp.verify(submitted_code, valid_window=1)  # allows ±1 time window
```

`valid_window=1` means the previous, current, and next 30-second windows are all accepted.

</details>

<details><summary>💡 Hint — Backup codes</summary>

Generate 10 random codes:

```python
import secrets
codes = [secrets.token_urlsafe(6) for _ in range(10)]
```

Hash each one with bcrypt before storing. When a user submits a backup code at login, iterate through their stored hashes and call `bcrypt.checkpw(submitted.encode(), stored_hash)`. On match, mark that row `used=True` and refuse it on future attempts.

</details>

---

## Step 3 — Modify the Login Flow

The login flow becomes two stages when 2FA is active.

**Stage 1** — `POST /auth/login` (password check, same as before):

- Verify email and password as in Project 05
- If the user does **not** have 2FA active: return the full session JWT as before
- If the user **does** have 2FA active: return a short-lived **partial token** instead of a full session JWT

**Stage 2** — `POST /auth/2fa/complete` (TOTP check):

- Accept the partial token and a 6-digit TOTP code
- Validate the partial token (correct type, not expired)
- Verify the TOTP code against the user's stored secret
- If both pass: issue a full session JWT

This two-stage design matters: a partial token cannot access protected routes. The attacker who steals a password still cannot reach protected endpoints without the TOTP device.

<details><summary>💡 Hint — What is a partial token?</summary>

A JWT with a special `type` claim:

```python
{"sub": str(user_id), "type": "2fa_pending", "exp": datetime.utcnow() + timedelta(minutes=5)}
```

The `/auth/2fa/complete` endpoint decodes it and asserts `payload["type"] == "2fa_pending"` before proceeding. Your normal route dependency should assert `payload["type"] == "session"` and reject partial tokens outright.

</details>

---

## Step 4 — Backup Code Login

Build `POST /auth/2fa/backup` (body: `{"partial_token": "...", "backup_code": "abc123"}`):

- Decode and validate the partial token — must be type `"2fa_pending"` and not expired
- Look up all unused backup codes for that user
- Iterate through stored hashes: check the submitted code against each one with bcrypt
- If a match is found: mark that backup code row as used, issue a full session JWT
- If no match: return 401

One backup code works exactly once. Attempting to reuse it returns 401.

---

## Step 5 — Disable 2FA

Build `POST /auth/2fa/disable` (requires full session JWT, body: `{"code": "482931"}`):

- Authenticate the request with the session JWT
- Verify the submitted TOTP code against the user's active secret (do not skip this — prevents an attacker with a stolen session token from locking out the real user)
- If valid: clear `totp_secret`, set `totp_active = False`, delete all backup code rows for this user

Require the TOTP code on disable, not just the session token.

---

## Step 6 — Database Schema

Extend the schema from Project 05. You need two additions:

**On the `users` table**, add:
- `totp_secret` — nullable string, stores the pending or active secret
- `totp_pending` — bool, True while secret is generated but not yet verified
- `totp_active` — bool, True after successful verification

**New `backup_codes` table**:
- `id` — integer primary key
- `user_id` — foreign key to users
- `code_hash` — string (bcrypt hash of the plaintext backup code)
- `used` — bool, default False

Keep the schema migration simple: if you are using SQLite with `create_all`, just add the columns and let SQLAlchemy recreate the table on first run (or drop and recreate the DB during development).

---

## Step 7 — Test All Paths

Write test cases (manual curl or pytest) covering every branch:

- [ ] Enable 2FA: QR code and plaintext secret returned
- [ ] Verify with correct TOTP code: 2FA activated, 10 backup codes returned
- [ ] Verify with wrong TOTP code: 400 returned, 2FA not activated
- [ ] Login without 2FA active: full session JWT returned directly
- [ ] Login with 2FA active: partial token returned (not a session JWT)
- [ ] Complete login with correct TOTP: full session JWT returned
- [ ] Complete login with wrong TOTP: 401 returned
- [ ] Complete login with valid backup code: full JWT returned, backup code marked used
- [ ] Attempt to reuse an already-used backup code: 401 returned
- [ ] Disable 2FA with correct TOTP: success, secret cleared
- [ ] Disable 2FA with wrong TOTP: 401 returned, 2FA still active
- [ ] Access a protected route with a partial token: 401 returned

---

## Acceptance Criteria

- [ ] `POST /auth/2fa/enable` returns a base64 QR code image and plaintext secret
- [ ] `POST /auth/2fa/verify` with a valid code activates 2FA and returns 10 backup codes
- [ ] `POST /auth/login` returns a partial token (not a full JWT) when 2FA is active
- [ ] `POST /auth/2fa/complete` validates TOTP within ±1 window and returns a full session JWT
- [ ] `POST /auth/2fa/backup` accepts one backup code exactly once
- [ ] `POST /auth/2fa/disable` requires a live TOTP code before clearing the secret
- [ ] Protected routes reject partial tokens

---

## What You Learned

- TOTP is pure math — no network roundtrip needed at verification time, just a shared secret and the current Unix timestamp
- Partial tokens enforce 2FA at the token layer, not just the route layer — even if a route check is missed, the token type itself is wrong
- Backup codes are credentials: hash them with bcrypt, show them once, mark them used on consumption
- `valid_window=1` in pyotp handles the real-world clock skew problem without weakening security significantly

---

## ✅ Full Reference Solution

<details><summary>✅ Show complete reference implementation</summary>

### File layout

```
12_2FA_TOTP/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── auth.py
├── dependencies.py
├── routers/
│   └── auth.py
└── .env
```

### `.env`

```
SECRET_KEY=supersecretkey-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
PARTIAL_TOKEN_EXPIRE_MINUTES=5
APP_NAME=MyApp
```

---

### `database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

### `models.py`

```python
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 2FA fields
    totp_secret = Column(String, nullable=True)       # pending or active secret
    totp_pending = Column(Boolean, default=False)     # secret generated, not yet verified
    totp_active = Column(Boolean, default=False)      # secret verified, 2FA is live


class BackupCode(Base):
    __tablename__ = "backup_codes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code_hash = Column(String, nullable=False)
    used = Column(Boolean, default=False)
```

---

### `schemas.py`

```python
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    requires_2fa: bool = False


class TOTPVerify(BaseModel):
    code: str


class TOTPComplete(BaseModel):
    partial_token: str
    code: str


class BackupLogin(BaseModel):
    partial_token: str
    backup_code: str


class DisableRequest(BaseModel):
    code: str
```

---

### `auth.py`

```python
import os
import io
import base64
import secrets
from datetime import datetime, timedelta

import bcrypt
import pyotp
import qrcode
from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
PARTIAL_TOKEN_EXPIRE_MINUTES = int(os.getenv("PARTIAL_TOKEN_EXPIRE_MINUTES", 5))
APP_NAME = os.getenv("APP_NAME", "MyApp")


# ── Password helpers ─────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ── JWT helpers ───────────────────────────────────────────────────────────────

def create_token(subject: str, token_type: str = "session", expires_minutes: int = None) -> str:
    if expires_minutes is None:
        expires_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    payload = {"sub": subject, "type": token_type, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Raises JWTError on invalid/expired tokens."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def create_session_token(user_id: int) -> str:
    return create_token(str(user_id), token_type="session",
                        expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES)


def create_partial_token(user_id: int) -> str:
    return create_token(str(user_id), token_type="2fa_pending",
                        expires_minutes=PARTIAL_TOKEN_EXPIRE_MINUTES)


# ── TOTP helpers ──────────────────────────────────────────────────────────────

def generate_totp_secret() -> str:
    return pyotp.random_base32()


def build_provisioning_uri(secret: str, email: str) -> str:
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=email,
        issuer_name=APP_NAME,
    )


def totp_qr_data_url(uri: str) -> str:
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def verify_totp_code(secret: str, code: str) -> bool:
    return pyotp.TOTP(secret).verify(code, valid_window=1)


# ── Backup code helpers ───────────────────────────────────────────────────────

def generate_backup_codes(n: int = 10) -> list[str]:
    return [secrets.token_urlsafe(6) for _ in range(n)]


def hash_backup_code(code: str) -> str:
    return bcrypt.hashpw(code.encode(), bcrypt.gensalt()).decode()


def verify_backup_code(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())
```

---

### `dependencies.py`

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

import auth
from database import get_db
from models import User

bearer = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = auth.decode_token(token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid or expired token")

    if payload.get("type") != "session":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Full session token required")

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User not found")
    return user
```

---

### `routers/auth.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session

import auth
from database import get_db
from dependencies import get_current_user
from models import BackupCode, User
from schemas import (
    BackupLogin,
    DisableRequest,
    Token,
    TOTPComplete,
    TOTPVerify,
    UserCreate,
    UserLogin,
)

router = APIRouter(prefix="/auth", tags=["auth"])


# ── Registration ──────────────────────────────────────────────────────────────

@router.post("/register", status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=payload.email,
        hashed_password=auth.hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email}


# ── Login (stage 1) ───────────────────────────────────────────────────────────

@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not auth.verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.totp_active:
        # Return partial token — caller must complete with TOTP
        partial = auth.create_partial_token(user.id)
        return Token(access_token=partial, token_type="bearer", requires_2fa=True)

    token = auth.create_session_token(user.id)
    return Token(access_token=token, token_type="bearer")


# ── 2FA Enable ────────────────────────────────────────────────────────────────

@router.post("/2fa/enable")
def enable_2fa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.totp_active:
        raise HTTPException(status_code=400, detail="2FA is already active")

    secret = auth.generate_totp_secret()
    uri = auth.build_provisioning_uri(secret, current_user.email)
    qr_data_url = auth.totp_qr_data_url(uri)

    current_user.totp_secret = secret
    current_user.totp_pending = True
    current_user.totp_active = False
    db.commit()

    return {
        "qr_code": qr_data_url,
        "secret": secret,
        "message": "Scan the QR code with your authenticator app, then call /auth/2fa/verify",
    }


# ── 2FA Verify (activate) ─────────────────────────────────────────────────────

@router.post("/2fa/verify")
def verify_2fa(
    payload: TOTPVerify,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.totp_pending or not current_user.totp_secret:
        raise HTTPException(status_code=400, detail="No pending 2FA setup found")

    if not auth.verify_totp_code(current_user.totp_secret, payload.code):
        raise HTTPException(status_code=400, detail="Invalid TOTP code")

    # Activate 2FA
    current_user.totp_active = True
    current_user.totp_pending = False

    # Generate and store backup codes
    plaintext_codes = auth.generate_backup_codes(10)
    for code in plaintext_codes:
        db.add(BackupCode(
            user_id=current_user.id,
            code_hash=auth.hash_backup_code(code),
        ))

    db.commit()

    return {
        "message": "2FA activated. Save these backup codes — they will not be shown again.",
        "backup_codes": plaintext_codes,
    }


# ── 2FA Complete (stage 2 login with TOTP) ────────────────────────────────────

@router.post("/2fa/complete", response_model=Token)
def complete_2fa(payload: TOTPComplete, db: Session = Depends(get_db)):
    try:
        decoded = auth.decode_token(payload.partial_token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired partial token")

    if decoded.get("type") != "2fa_pending":
        raise HTTPException(status_code=401, detail="Not a 2FA partial token")

    user = db.query(User).filter(User.id == int(decoded["sub"])).first()
    if not user or not user.totp_active or not user.totp_secret:
        raise HTTPException(status_code=401, detail="2FA not configured for this user")

    if not auth.verify_totp_code(user.totp_secret, payload.code):
        raise HTTPException(status_code=401, detail="Invalid TOTP code")

    token = auth.create_session_token(user.id)
    return Token(access_token=token, token_type="bearer")


# ── 2FA Backup code login ─────────────────────────────────────────────────────

@router.post("/2fa/backup", response_model=Token)
def backup_login(payload: BackupLogin, db: Session = Depends(get_db)):
    try:
        decoded = auth.decode_token(payload.partial_token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired partial token")

    if decoded.get("type") != "2fa_pending":
        raise HTTPException(status_code=401, detail="Not a 2FA partial token")

    user = db.query(User).filter(User.id == int(decoded["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    unused_codes = (
        db.query(BackupCode)
        .filter(BackupCode.user_id == user.id, BackupCode.used == False)
        .all()
    )

    matched: BackupCode | None = None
    for bc in unused_codes:
        if auth.verify_backup_code(payload.backup_code, bc.code_hash):
            matched = bc
            break

    if not matched:
        raise HTTPException(status_code=401, detail="Invalid or already-used backup code")

    matched.used = True
    db.commit()

    token = auth.create_session_token(user.id)
    return Token(access_token=token, token_type="bearer")


# ── Disable 2FA ───────────────────────────────────────────────────────────────

@router.post("/2fa/disable")
def disable_2fa(
    payload: DisableRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.totp_active or not current_user.totp_secret:
        raise HTTPException(status_code=400, detail="2FA is not active")

    if not auth.verify_totp_code(current_user.totp_secret, payload.code):
        raise HTTPException(status_code=401, detail="Invalid TOTP code — cannot disable 2FA")

    current_user.totp_secret = None
    current_user.totp_pending = False
    current_user.totp_active = False

    db.query(BackupCode).filter(BackupCode.user_id == current_user.id).delete()
    db.commit()

    return {"message": "2FA has been disabled"}


# ── Protected example route ───────────────────────────────────────────────────

@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "totp_active": current_user.totp_active,
    }
```

---

### `main.py`

```python
from fastapi import FastAPI
from database import Base, engine
from routers import auth as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="2FA / TOTP Auth System")
app.include_router(auth_router.router)
```

---

### Manual test walkthrough (curl)

```bash
# 1. Register
curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"secret123"}' | python3 -m json.tool

# 2. Login without 2FA — get full session JWT directly
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"secret123"}' | python3 -m json.tool

# Store the token
TOKEN="<paste access_token here>"

# 3. Enable 2FA — get QR code data URL and secret
curl -s -X POST http://localhost:8000/auth/2fa/enable \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Store the secret
SECRET="<paste secret here>"

# 4. Generate a TOTP code from the secret (in Python):
# python3 -c "import pyotp; print(pyotp.TOTP('$SECRET').now())"

# 5. Verify and activate 2FA
CODE="<6-digit code from step 4>"
curl -s -X POST http://localhost:8000/auth/2fa/verify \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"code\":\"$CODE\"}" | python3 -m json.tool
# Save the backup codes from the response

# 6. Login with 2FA active — should return partial token + requires_2fa=true
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"secret123"}' | python3 -m json.tool

PARTIAL="<paste partial access_token here>"

# 7. Complete login with TOTP
CODE2="$(python3 -c "import pyotp; print(pyotp.TOTP('$SECRET').now())")"
curl -s -X POST http://localhost:8000/auth/2fa/complete \
  -H "Content-Type: application/json" \
  -d "{\"partial_token\":\"$PARTIAL\",\"code\":\"$CODE2\"}" | python3 -m json.tool

FULL_TOKEN="<paste full session token here>"

# 8. Access protected route
curl -s http://localhost:8000/auth/me \
  -H "Authorization: Bearer $FULL_TOKEN" | python3 -m json.tool

# 9. Login with backup code (repeat step 6 to get a fresh partial token)
BACKUP="<one of the backup codes from step 5>"
curl -s -X POST http://localhost:8000/auth/2fa/backup \
  -H "Content-Type: application/json" \
  -d "{\"partial_token\":\"$PARTIAL\",\"backup_code\":\"$BACKUP\"}" | python3 -m json.tool

# 10. Try the same backup code again — should return 401
curl -s -X POST http://localhost:8000/auth/2fa/backup \
  -H "Content-Type: application/json" \
  -d "{\"partial_token\":\"$PARTIAL\",\"backup_code\":\"$BACKUP\"}" | python3 -m json.tool

# 11. Disable 2FA
CODE3="$(python3 -c "import pyotp; print(pyotp.TOTP('$SECRET').now())")"
curl -s -X POST http://localhost:8000/auth/2fa/disable \
  -H "Authorization: Bearer $FULL_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"code\":\"$CODE3\"}" | python3 -m json.tool
```

</details>

---

## Next Project

[Project 14 — RBAC Middleware](../13_RBAC/Project_Guide.md)
