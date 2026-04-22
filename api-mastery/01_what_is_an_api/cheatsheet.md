# ⚡ What is an API — Cheatsheet

## Learning Priority

| Priority | Topics |
|---|---|
| Must Learn | HTTP methods · status codes · request/response anatomy · JSON basics · headers |
| Should Learn | client-server separation · API types (REST/GraphQL/gRPC) · curl usage |
| Good to Know | HTTP version differences · API taxonomy |
| Reference | specific HTTP spec details · full header catalog |

---

## HTTP Methods — The Verbs

| Method | Action | Has Body | Safe | Idempotent | Success Code |
|---|---|---|---|---|---|
| GET | Read/fetch | No | Yes | Yes | 200 |
| POST | Create | Yes | No | No | 201 |
| PUT | Full replace | Yes | No | Yes | 200 |
| PATCH | Partial update | Yes | No | No* | 200 |
| DELETE | Remove | No | No | Yes | 204 |

*PATCH can be designed as idempotent, but usually isn't.

```
GET    /tasks          → all tasks
GET    /tasks/42       → task 42
POST   /tasks          → create task
PUT    /tasks/42       → replace task 42 (send ALL fields)
PATCH  /tasks/42       → update part of task 42 (send only changed fields)
DELETE /tasks/42       → delete task 42
```

---

## Status Codes Reference

### 2xx — Success (things worked)
| Code | Name | When to use |
|---|---|---|
| 200 | OK | Standard success (GET, PATCH, PUT) |
| 201 | Created | POST that created a resource |
| 204 | No Content | DELETE, actions with no body to return |

### 3xx — Redirection
| Code | Name | When to use |
|---|---|---|
| 301 | Moved Permanently | URL has changed forever |
| 304 | Not Modified | Cached version is still fresh (ETag/If-None-Match) |

### 4xx — Client Error (you messed up)
| Code | Name | When to use |
|---|---|---|
| 400 | Bad Request | Malformed request, missing/invalid fields |
| 401 | Unauthorized | Not authenticated ("who are you?") |
| 403 | Forbidden | Authenticated, but no permission ("I know you, but no") |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Valid JSON, but fails business validation |
| 429 | Too Many Requests | Rate limit exceeded |

### 5xx — Server Error (they messed up)
| Code | Name | When to use |
|---|---|---|
| 500 | Internal Server Error | Unhandled exception on the server |
| 502 | Bad Gateway | Upstream service returned bad response |
| 503 | Service Unavailable | Server down or overloaded |
| 504 | Gateway Timeout | Upstream service timed out |

**Mnemonic:** 2 thumbs up · 4 is the client's fault · 5 is their fault

---

## Request Anatomy

```
GET /users/octocat HTTP/1.1
Host: api.github.com                ← which server
Accept: application/json            ← what format do I want back
Authorization: Bearer ghp_abc123    ← prove who I am
User-Agent: my-app/1.0              ← who is calling

[no body for GET]
```

```
POST /users HTTP/1.1
Host: api.example.com
Content-Type: application/json     ← what format am I sending
Authorization: Bearer eyJhb...
Accept: application/json

{                                   ← request body (for POST/PUT/PATCH)
  "name": "Alice",
  "email": "alice@example.com"
}
```

---

## Response Anatomy

```
HTTP/1.1 200 OK
Content-Type: application/json     ← format of the body
Cache-Control: private, max-age=60 ← caching instructions
X-RateLimit-Remaining: 59          ← how many calls left

{                                   ← response body
  "id": 42,
  "name": "Alice",
  "email": "alice@example.com"
}
```

---

## Common Headers Cheatsheet

### Request Headers
| Header | Purpose | Example |
|---|---|---|
| `Content-Type` | Format of request body | `application/json` |
| `Accept` | Format you want in response | `application/json` |
| `Authorization` | Credentials | `Bearer eyJhb...` |
| `User-Agent` | Identifies caller | `python-requests/2.31.0` |
| `If-None-Match` | Conditional: only if changed | `"abc123"` (ETag value) |

### Response Headers
| Header | Purpose | Example |
|---|---|---|
| `Content-Type` | Format of response body | `application/json; charset=utf-8` |
| `Cache-Control` | How long to cache | `max-age=3600` |
| `ETag` | Fingerprint for caching | `"33a64df551..."` |
| `Location` | URL of new resource (POST) | `/api/v1/users/128` |
| `Retry-After` | Seconds to wait (429) | `60` |
| `X-RateLimit-Limit` | Max requests per window | `1000` |
| `X-RateLimit-Remaining` | Requests left | `842` |
| `X-RateLimit-Reset` | Unix ts when window resets | `1609459200` |

### Content-Type Values
```
application/json                    → JSON body (most APIs)
application/x-www-form-urlencoded   → HTML form data
multipart/form-data                 → file uploads
text/html                           → HTML page
text/plain                          → plain text
```

---

## curl Examples

```bash
# GET request
curl https://api.github.com/users/octocat

# GET with auth header
curl -H "Authorization: Bearer TOKEN" https://api.example.com/me

# POST with JSON body
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"name": "Alice", "email": "alice@example.com"}'

# PATCH (partial update)
curl -X PATCH https://api.example.com/users/42 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"role": "admin"}'

# DELETE
curl -X DELETE https://api.example.com/users/42 \
  -H "Authorization: Bearer TOKEN"

# See response headers (-i) and verbose output (-v)
curl -i https://api.example.com/users
curl -v https://api.example.com/users
```

---

## Python requests Quick Reference

```python
import requests

# GET
r = requests.get("https://api.github.com/users/octocat")
r.status_code       # 200
r.json()            # dict
r.text              # raw string
r.headers["Content-Type"]

# POST
r = requests.post(
    "https://api.example.com/users",
    headers={"Authorization": "Bearer TOKEN"},
    json={"name": "Alice"}       # auto-sets Content-Type: application/json
)

# PATCH / PUT / DELETE
requests.patch(url, json={...}, headers={...})
requests.put(url, json={...}, headers={...})
requests.delete(url, headers={...})

# Check for errors
r.raise_for_status()   # raises HTTPError if 4xx or 5xx
```

---

## JSON Types

```json
{
  "name":       "Alice",        // string — always double-quoted
  "age":        30,             // number — no quotes
  "is_admin":   true,           // boolean — true/false, lowercase
  "middle_name": null,          // null — represents "nothing"
  "scores":     [95, 87, 92],   // array — ordered list
  "address": {                  // object — nested key-value pairs
    "city": "Austin"
  }
}
```

**JSON has no native: date, Decimal, bytes, set, or tuple types.**

---

## API Types Overview

| Type | Style | Best for |
|---|---|---|
| REST | Resource-based, HTTP methods | Most public APIs, standard CRUD |
| GraphQL | Query language, ask for exact fields | Complex UIs, flexible data needs |
| gRPC | Binary protocol, schema-first | High-performance backend-to-backend |
| WebSockets | Persistent two-way connection | Chat, live dashboards, real-time |

---

## Navigation

**[Back to README](../README.md)**

**Theory:** [story.md](./story.md)

**Prev:** — &nbsp;|&nbsp; **Next:** [REST Fundamentals →](../02_rest_fundamentals/cheatsheet.md)

**Related:** [02 REST Fundamentals](../02_rest_fundamentals/cheatsheet.md) · [05 Authentication](../05_authentication/cheatsheet.md) · [06 Error Handling](../06_error_handling_standards/cheatsheet.md)
