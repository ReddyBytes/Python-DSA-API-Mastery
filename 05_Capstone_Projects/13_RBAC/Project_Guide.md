# Project 13 — RBAC: Role-Based Access Control Middleware

> Analogy: A badge system in an office building — your badge level (role) determines which rooms (routes) you can enter, and the security system checks it at every door without asking the manager each time.

**Learning Format:** Build Yourself — Spec + acceptance criteria only. No guided steps.
**What You Build:** A reusable RBAC system for FastAPI: roles, permissions, a middleware/decorator that enforces them, JWT claims carrying role info, an admin API to manage roles.
**Concepts Covered:** RBAC model (roles/permissions/users), permission matrices, FastAPI dependency injection for auth, decorator pattern, JWT role claims, audit logging

---

## The Spec

Build a FastAPI application with the following:

### Data Model

**Users** have one or more **Roles**.
**Roles** have one or more **Permissions**.
**Permissions** are strings like `"posts:read"`, `"posts:write"`, `"users:delete"`, `"admin:*"`.

Predefined roles (seed these in DB):

| Role | Permissions |
|---|---|
| `guest` | `posts:read` |
| `user` | `posts:read`, `posts:write`, `comments:read`, `comments:write` |
| `moderator` | `posts:read`, `posts:write`, `posts:delete`, `comments:read`, `comments:write`, `comments:delete` |
| `admin` | all permissions (wildcard: `admin:*`) |

---

### Required Endpoints

**Auth:**
- `POST /auth/register` — create user, assign role (default: `user`)
- `POST /auth/login` — returns JWT with `{"sub": user_id, "roles": ["user"], "permissions": ["posts:read", "posts:write", ...]}`

**Posts (example resource):**
- `GET /posts` — requires `posts:read`
- `POST /posts` — requires `posts:write`
- `DELETE /posts/{id}` — requires `posts:delete`

**Admin:**
- `GET /admin/users` — requires `admin:*`
- `POST /admin/users/{user_id}/roles` — assign role to user, requires `admin:*`
- `DELETE /admin/roles/{role}/users/{user_id}` — remove role from user, requires `admin:*`

---

### Access Control Requirements

1. Build a `require_permission(permission: str)` FastAPI dependency that:
   - Extracts and validates the JWT
   - Checks if the user has the required permission (either directly or via wildcard `admin:*`)
   - Returns 403 with `{"error": "Insufficient permissions"}` if not
   - Returns 401 if no token

2. Usage:

```python
@app.delete("/posts/{post_id}")
async def delete_post(post_id: int, user=Depends(require_permission("posts:delete"))):
    ...
```

3. Wildcard rule: a user with `admin:*` passes ALL permission checks.

4. Multi-role: a user can have multiple roles. Permissions are the union of all roles' permissions.

---

### Audit Log Requirements

Every permission-denied event must be logged:

```
2024-01-15 10:32:01 | DENIED | user_id=42 | required=posts:delete | user_permissions=posts:read,posts:write | path=DELETE /posts/99
```

---

### Database

Use SQLite with these tables:

- `users` (id, email, password_hash, created_at)
- `roles` (id, name, description)
- `permissions` (id, role_id, permission_string)
- `user_roles` (user_id, role_id)

---

## Acceptance Criteria

- [ ] Guest user can `GET /posts` but gets 403 on `POST /posts`
- [ ] Regular user can `GET` and `POST /posts` but gets 403 on `DELETE /posts`
- [ ] Moderator can delete posts but gets 403 on `/admin` routes
- [ ] Admin passes all permission checks including `/admin` routes
- [ ] Assigning a role to a user immediately affects their next login JWT
- [ ] Permission denied events appear in the audit log with full context
- [ ] Multi-role user gets union of all role permissions
- [ ] `admin:*` wildcard bypasses all permission checks

---

## Architecture Notes

These notes exist to prevent architectural mistakes — they do NOT give away implementation details:

1. Permissions go in the JWT at login time (not fetched from DB on each request) — this is the performance tradeoff. Accept it here.
2. The `require_permission` function must be a FastAPI `Depends`-compatible function that returns a user object on success.
3. Wildcard matching: `admin:*` should match any `resource:action` string. Use a simple string prefix check.
4. For the audit log, use Python's standard `logging` module with a dedicated `rbac.audit` logger.

---

## What You Should Try Before Looking at the Solution

1. Start with the DB schema and seeding
2. Build auth (register/login) with role-embedded JWT
3. Build `require_permission` as a dependency
4. Add posts routes using the dependency
5. Add admin routes
6. Add audit logging
7. Test all 8 acceptance criteria

---

## ✅ Full Reference Solution

<details><summary>✅ Show complete reference implementation</summary>

```python
"""
Project 14 — RBAC: Role-Based Access Control Middleware
Complete reference implementation.

Dependencies:
    pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt] python-multipart

Run:
    uvicorn main:app --reload
"""

import logging
import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SECRET_KEY = "change-this-in-production-use-secrets-module"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
DB_PATH = "rbac.db"

# ---------------------------------------------------------------------------
# Logging — audit logger
# ---------------------------------------------------------------------------

logging.basicConfig(
    format="%(asctime)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
audit_logger = logging.getLogger("rbac.audit")

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = get_db()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            email        TEXT    NOT NULL UNIQUE,
            password_hash TEXT   NOT NULL,
            created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS roles (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS permissions (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            role_id           INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
            permission_string TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS user_roles (
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
            PRIMARY KEY (user_id, role_id)
        );
    """)

    # Seed default roles only if table is empty
    existing = cur.execute("SELECT COUNT(*) FROM roles").fetchone()[0]
    if existing == 0:
        seed_roles = [
            ("guest",     "Read-only access to public content",       ["posts:read"]),
            ("user",      "Standard authenticated user",              ["posts:read", "posts:write", "comments:read", "comments:write"]),
            ("moderator", "Can delete posts and comments",            ["posts:read", "posts:write", "posts:delete", "comments:read", "comments:write", "comments:delete"]),
            ("admin",     "Full administrative access",               ["admin:*"]),
        ]
        for name, description, perms in seed_roles:
            cur.execute("INSERT INTO roles (name, description) VALUES (?, ?)", (name, description))
            role_id = cur.lastrowid
            for perm in perms:
                cur.execute("INSERT INTO permissions (role_id, permission_string) VALUES (?, ?)", (role_id, perm))

    conn.commit()
    conn.close()


def get_user_by_email(email: str) -> Optional[sqlite3.Row]:
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return row


def get_user_by_id(user_id: int) -> Optional[sqlite3.Row]:
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return row


def get_role_by_name(name: str) -> Optional[sqlite3.Row]:
    conn = get_db()
    row = conn.execute("SELECT * FROM roles WHERE name = ?", (name,)).fetchone()
    conn.close()
    return row


def get_user_roles(user_id: int) -> list[str]:
    conn = get_db()
    rows = conn.execute(
        """
        SELECT r.name FROM roles r
        JOIN user_roles ur ON ur.role_id = r.id
        WHERE ur.user_id = ?
        """,
        (user_id,),
    ).fetchall()
    conn.close()
    return [row["name"] for row in rows]


def get_user_permissions(user_id: int) -> list[str]:
    """Return the union of all permissions across all of a user's roles."""
    conn = get_db()
    rows = conn.execute(
        """
        SELECT DISTINCT p.permission_string
        FROM permissions p
        JOIN user_roles ur ON ur.role_id = p.role_id
        WHERE ur.user_id = ?
        """,
        (user_id,),
    ).fetchall()
    conn.close()
    return [row["permission_string"] for row in rows]


def assign_role_to_user(user_id: int, role_id: int) -> None:
    conn = get_db()
    conn.execute(
        "INSERT OR IGNORE INTO user_roles (user_id, role_id) VALUES (?, ?)",
        (user_id, role_id),
    )
    conn.commit()
    conn.close()


def remove_role_from_user(user_id: int, role_id: int) -> None:
    conn = get_db()
    conn.execute(
        "DELETE FROM user_roles WHERE user_id = ? AND role_id = ?",
        (user_id, role_id),
    )
    conn.commit()
    conn.close()


def list_all_users() -> list[sqlite3.Row]:
    conn = get_db()
    rows = conn.execute("SELECT id, email, created_at FROM users").fetchall()
    conn.close()
    return rows

# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def create_access_token(user_id: int) -> str:
    roles = get_user_roles(user_id)
    permissions = get_user_permissions(user_id)
    payload = {
        "sub": str(user_id),
        "roles": roles,
        "permissions": permissions,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT. Raises JWTError on failure."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

# ---------------------------------------------------------------------------
# Permission checking
# ---------------------------------------------------------------------------

def has_permission(user_permissions: list[str], required: str) -> bool:
    """
    Return True if the user holds the required permission.

    Rules:
    - Exact match: "posts:read" in user_permissions
    - Wildcard:    "admin:*"   in user_permissions bypasses ALL checks
    """
    if "admin:*" in user_permissions:
        return True
    return required in user_permissions

# ---------------------------------------------------------------------------
# FastAPI dependency: require_permission
# ---------------------------------------------------------------------------

bearer_scheme = HTTPBearer(auto_error=False)


def require_permission(permission: str):
    """
    Factory that returns a FastAPI dependency enforcing a specific permission.

    Usage:
        @app.get("/posts")
        async def list_posts(user=Depends(require_permission("posts:read"))):
            ...
    """
    async def dependency(
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    ) -> dict:
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            payload = decode_token(credentials.credentials)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = int(payload["sub"])
        user_permissions: list[str] = payload.get("permissions", [])

        if not has_permission(user_permissions, permission):
            # Audit log: every denial with full context
            audit_logger.warning(
                "DENIED | user_id=%d | required=%s | user_permissions=%s | path=%s %s",
                user_id,
                permission,
                ",".join(user_permissions),
                request.method,
                request.url.path,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": "Insufficient permissions"},
            )

        return {"user_id": user_id, "roles": payload.get("roles", []), "permissions": user_permissions}

    return dependency

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = "user"  # optional override; defaults to "user"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CreatePostRequest(BaseModel):
    title: str
    body: str


class AssignRoleRequest(BaseModel):
    role: str

# ---------------------------------------------------------------------------
# App lifecycle
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="RBAC Middleware Demo", lifespan=lifespan)

# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------

@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest):
    if get_user_by_email(body.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    role = get_role_by_name(body.role)
    if not role:
        raise HTTPException(status_code=400, detail=f"Role '{body.role}' does not exist")

    password_hash = pwd_context.hash(body.password)

    conn = get_db()
    cur = conn.execute(
        "INSERT INTO users (email, password_hash) VALUES (?, ?)",
        (body.email, password_hash),
    )
    user_id = cur.lastrowid
    conn.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role["id"]))
    conn.commit()
    conn.close()

    return {"user_id": user_id, "email": body.email, "role": body.role}


@app.post("/auth/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    user = get_user_by_email(body.email)
    if not user or not pwd_context.verify(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user["id"])
    return {"access_token": token, "token_type": "bearer"}

# ---------------------------------------------------------------------------
# Posts routes
# ---------------------------------------------------------------------------

# In-memory post store — sufficient for demonstrating RBAC (not the focus)
_posts: dict[int, dict] = {}
_post_counter = 0


@app.get("/posts")
async def list_posts(user=Depends(require_permission("posts:read"))):
    return {"posts": list(_posts.values()), "requested_by": user["user_id"]}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(body: CreatePostRequest, user=Depends(require_permission("posts:write"))):
    global _post_counter
    _post_counter += 1
    post = {"id": _post_counter, "title": body.title, "body": body.body, "author_id": user["user_id"]}
    _posts[_post_counter] = post
    return post


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, user=Depends(require_permission("posts:delete"))):
    if post_id not in _posts:
        raise HTTPException(status_code=404, detail="Post not found")
    del _posts[post_id]

# ---------------------------------------------------------------------------
# Admin routes
# ---------------------------------------------------------------------------

@app.get("/admin/users")
async def admin_list_users(user=Depends(require_permission("admin:*"))):
    rows = list_all_users()
    return {
        "users": [
            {
                "id": row["id"],
                "email": row["email"],
                "created_at": row["created_at"],
                "roles": get_user_roles(row["id"]),
            }
            for row in rows
        ]
    }


@app.post("/admin/users/{user_id}/roles", status_code=status.HTTP_200_OK)
async def admin_assign_role(
    user_id: int,
    body: AssignRoleRequest,
    _admin=Depends(require_permission("admin:*")),
):
    target = get_user_by_id(user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    role = get_role_by_name(body.role)
    if not role:
        raise HTTPException(status_code=400, detail=f"Role '{body.role}' does not exist")

    assign_role_to_user(user_id, role["id"])
    return {"user_id": user_id, "assigned_role": body.role, "all_roles": get_user_roles(user_id)}


@app.delete("/admin/roles/{role}/users/{user_id}", status_code=status.HTTP_200_OK)
async def admin_remove_role(
    role: str,
    user_id: int,
    _admin=Depends(require_permission("admin:*")),
):
    target = get_user_by_id(user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    role_row = get_role_by_name(role)
    if not role_row:
        raise HTTPException(status_code=404, detail=f"Role '{role}' does not exist")

    remove_role_from_user(user_id, role_row["id"])
    return {"user_id": user_id, "removed_role": role, "remaining_roles": get_user_roles(user_id)}
```

---

### Testing All 8 Acceptance Criteria

Save the script below as `test_rbac.sh`, run `chmod +x test_rbac.sh`, and start the server (`uvicorn main:app --reload`) in another terminal first.

```bash
#!/usr/bin/env bash
# test_rbac.sh — validates all 8 acceptance criteria
BASE="http://localhost:8000"

echo "=== Registering test users ==="
curl -s -X POST "$BASE/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"guest@example.com","password":"pass","role":"guest"}' | python3 -m json.tool

curl -s -X POST "$BASE/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass","role":"user"}' | python3 -m json.tool

curl -s -X POST "$BASE/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"mod@example.com","password":"pass","role":"moderator"}' | python3 -m json.tool

curl -s -X POST "$BASE/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"pass","role":"admin"}' | python3 -m json.tool

echo ""
echo "=== Logging in — collecting tokens ==="
GUEST_TOKEN=$(curl -s -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"guest@example.com","password":"pass"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

USER_TOKEN=$(curl -s -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

MOD_TOKEN=$(curl -s -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"mod@example.com","password":"pass"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

ADMIN_TOKEN=$(curl -s -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"pass"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "Tokens collected."

# ---- Criterion 1: Guest can GET /posts but not POST ----
echo ""
echo "=== [1] Guest: GET /posts (expect 200) ==="
curl -s -o /dev/null -w "HTTP %{http_code}\n" "$BASE/posts" \
  -H "Authorization: Bearer $GUEST_TOKEN"

echo "=== [1] Guest: POST /posts (expect 403) ==="
curl -s -o /dev/null -w "HTTP %{http_code}\n" -X POST "$BASE/posts" \
  -H "Authorization: Bearer $GUEST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"t","body":"b"}'

# ---- Criterion 2: User can GET and POST but not DELETE ----
echo ""
echo "=== [2] User: POST /posts (expect 201) ==="
POST_ID=$(curl -s -X POST "$BASE/posts" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Hello","body":"World"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Created post id=$POST_ID"

echo "=== [2] User: DELETE /posts/$POST_ID (expect 403) ==="
curl -s -o /dev/null -w "HTTP %{http_code}\n" -X DELETE "$BASE/posts/$POST_ID" \
  -H "Authorization: Bearer $USER_TOKEN"

# ---- Criterion 3: Moderator can DELETE posts but not /admin ----
echo ""
echo "=== [3] Moderator: DELETE /posts/$POST_ID (expect 204) ==="
curl -s -o /dev/null -w "HTTP %{http_code}\n" -X DELETE "$BASE/posts/$POST_ID" \
  -H "Authorization: Bearer $MOD_TOKEN"

echo "=== [3] Moderator: GET /admin/users (expect 403) ==="
curl -s -o /dev/null -w "HTTP %{http_code}\n" "$BASE/admin/users" \
  -H "Authorization: Bearer $MOD_TOKEN"

# ---- Criterion 4: Admin passes all checks ----
echo ""
echo "=== [4] Admin: GET /admin/users (expect 200) ==="
curl -s -o /dev/null -w "HTTP %{http_code}\n" "$BASE/admin/users" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# ---- Criterion 5: Role assignment affects next login JWT ----
echo ""
echo "=== [5] Assign 'moderator' role to guest, then re-login ==="
GUEST_ID=$(curl -s "$BASE/admin/users" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -c "
import sys, json
users = json.load(sys.stdin)['users']
print(next(u['id'] for u in users if u['email']=='guest@example.com'))
")
echo "Guest user_id=$GUEST_ID"

curl -s -X POST "$BASE/admin/users/$GUEST_ID/roles" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role":"moderator"}' | python3 -m json.tool

NEW_GUEST_TOKEN=$(curl -s -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"guest@example.com","password":"pass"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "=== [5] Guest (now with moderator role): POST /posts (expect 201) ==="
curl -s -o /dev/null -w "HTTP %{http_code}\n" -X POST "$BASE/posts" \
  -H "Authorization: Bearer $NEW_GUEST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"guest post","body":"now allowed"}'

# ---- Criterion 6: Audit log — check server stdout for DENIED lines ----
echo ""
echo "=== [6] Trigger a denial and check server logs manually for DENIED audit line ==="
curl -s -o /dev/null -w "HTTP %{http_code}\n" -X DELETE "$BASE/posts/999" \
  -H "Authorization: Bearer $USER_TOKEN"

# ---- Criterion 7: Multi-role union permissions ----
echo ""
echo "=== [7] Verify multi-role user has union of permissions ==="
curl -s "$BASE/admin/users" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -c "
import sys, json
users = json.load(sys.stdin)['users']
guest = next(u for u in users if u['email']=='guest@example.com')
print('Guest roles:', guest['roles'])
"

# ---- Criterion 8: admin:* wildcard already verified by criterion 4 ----
echo ""
echo "=== [8] admin:* wildcard: Admin DELETE /posts/1 (expect 404 not 403 — wildcard works) ==="
curl -s -w "\nHTTP %{http_code}\n" -X DELETE "$BASE/posts/1" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

echo ""
echo "=== All criteria tested. Review output above. ==="
```

</details>

---

## Congratulations — Cycle 3 Complete

You have now built:

- Project 11: OAuth Client — login via GitHub and Google
- Project 12: OAuth Server — your own authorization server
- Project 13: 2FA/TOTP — time-based second factor with backup codes
- Project 14: RBAC — permission enforcement as middleware

These four projects together form a complete, production-grade authentication and authorization system. Most real products use some combination of all four.

---

## What Comes Next

| Track | Next step |
|---|---|
| If you want to go deeper on auth | Study OpenID Connect Discovery, PKCE in detail, token revocation (RFC 7009) |
| If you want to scale | Add Redis for token blacklisting, distributed rate limiting on auth endpoints |
| If you want to go to production | Add mTLS between services, rotate JWT signing keys, add SIEM integration for audit logs |

---

## Back to All Projects

[← Back to Capstone Projects README](../README.md)
