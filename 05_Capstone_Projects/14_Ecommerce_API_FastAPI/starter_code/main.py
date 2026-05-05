"""
E-Commerce API — Starter Skeleton
===================================
Runnable with:
    pip install fastapi uvicorn sqlalchemy pydantic python-jose passlib
    uvicorn main:app --reload

Then visit: http://localhost:8000/docs

This file gives you the core wiring. Expand each section following Project_Guide.md.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import Boolean, DateTime, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config (replace with pydantic-settings in production)
# ---------------------------------------------------------------------------

DATABASE_URL = "sqlite:///./ecommerce_dev.db"
SECRET_KEY = "dev-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency: yields a DB session, always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbDep = Annotated[Session, Depends(get_db)]

# ---------------------------------------------------------------------------
# SQLAlchemy models (stubs — expand in Step 2)
# ---------------------------------------------------------------------------


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# TODO: Add Product, Order, OrderItem models in Step 2

# ---------------------------------------------------------------------------
# Pydantic schemas (stubs — expand in Step 3)
# ---------------------------------------------------------------------------


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Placeholder schemas — replace with full versions from Project_Guide.md
class ProductResponse(BaseModel):
    id: int
    name: str
    price: float


class OrderCreate(BaseModel):
    items: list[dict]  # Replace with OrderItemCreate list in Step 3


# ---------------------------------------------------------------------------
# Security utilities (stubs — expand in Step 4)
# ---------------------------------------------------------------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DbDep,
) -> User:
    """JWT auth dependency — inject with Depends(get_current_user)."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="E-Commerce API",
    description="Starter skeleton — follow Project_Guide.md to complete each step.",
    version="0.1.0",
)


@app.on_event("startup")
def on_startup():
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database ready.")


# ---------------------------------------------------------------------------
# Route 1: Health check
# ---------------------------------------------------------------------------


@app.get("/health", tags=["Health"])
def health_check():
    """Confirms the API is running. No auth required."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


# ---------------------------------------------------------------------------
# Route 2: User registration + login (auth stub)
# ---------------------------------------------------------------------------


@app.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"],
)
def register(user_in: UserCreate, db: DbDep):
    """
    Register a new user.
    TODO (Step 4): Move to routers/auth.py. Add rate limiting (Step 10).
    """
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
    logger.info(f"New user registered: {user.email}")
    return user


@app.post("/auth/login", response_model=Token, tags=["Authentication"])
def login(user_in: UserCreate, db: DbDep):
    """
    Login and receive a JWT access token.
    TODO (Step 4): Accept OAuth2PasswordRequestForm for Swagger compatibility.
    """
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


# ---------------------------------------------------------------------------
# Route 3: Protected "me" endpoint — tests that JWT auth works
# ---------------------------------------------------------------------------


@app.get("/users/me", response_model=UserResponse, tags=["Users"])
def get_me(current_user: CurrentUser):
    """
    Returns the currently authenticated user.
    Requires: Authorization: Bearer <token>
    TODO (Step 5): Add product routes. (Step 6): Add order routes.
    """
    return current_user


# ---------------------------------------------------------------------------
# Placeholder routes (wired but not implemented — fill in per guide steps)
# ---------------------------------------------------------------------------


@app.get("/products/", tags=["Products"])
def list_products(
    page: int = 1,
    page_size: int = 20,
    category: str | None = None,
    db: DbDep = None,
):
    """
    TODO Step 5: Query Product model with filters and pagination.
    Return ProductListResponse.
    """
    return {"message": "Implement in Step 5", "page": page, "page_size": page_size}


@app.post("/orders/", status_code=201, tags=["Orders"])
def create_order(order_in: OrderCreate, current_user: CurrentUser, db: DbDep):
    """
    TODO Step 6: Call place_order(order_in, current_user.id, db).
    TODO Step 7: Add BackgroundTasks for email confirmation.
    """
    return {"message": "Implement in Step 6", "user_id": current_user.id}


# ---------------------------------------------------------------------------
# Entry point (for running directly with `python main.py`)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
