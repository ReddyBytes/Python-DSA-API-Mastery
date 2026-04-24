# What is an API?

## It's Friday Afternoon

It's 4:47 PM on a Friday. You're done with work, you grab your phone, open Spotify, and
search for "Beatles". Two seconds later — Abbey Road, Let It Be, Rubber Soul, all of it,
right there.

Stop for a second. What just happened?

Your phone doesn't store every Beatles song. Spotify doesn't ship a hard drive to your
house when you install the app. So where did those songs come from? How did your app
"know" to show them?

Here's what actually happened behind the scenes:

```
Your Phone                          Spotify's Servers
    |                                       |
    |  "Hey, I want songs for 'Beatles'"    |
    |  ───────────────────────────────────> |
    |                                       |  [searches database]
    |                                       |  [finds 200+ songs]
    |                                       |
    |  "Here they are: Abbey Road, Let It Be, ..."
    |  <─────────────────────────────────── |
    |                                       |
```

Your phone talked to a server. The server responded. That exchange — that request and
response — is an API call.

And the rules that govern how that exchange happens — what format the request must be in,
what the response looks like, what errors look like — those rules together are the API.

**API = Application Programming Interface**

It's a defined way for two programs to talk to each other.

Not two humans. Not a human and a program. Two programs. The "interface" part means there
are agreed-upon rules. Both sides know the format. Both sides speak the same language.

Think of it like ordering coffee. There's an agreed-upon way to do it: you walk up, you
say what you want, the barista makes it, hands it to you. You don't go behind the counter
and start pulling shots yourself. There's an interface — the counter, the menu, the
standard ordering flow. APIs are that interface, but for software.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
HTTP methods (GET/POST/PUT/PATCH/DELETE) · HTTP status codes · JSON basics · request/response headers

**Should Learn** — Important for real projects, comes up regularly:
client-server separation · request anatomy · API types overview (REST/GraphQL/gRPC)

**Good to Know** — Useful in specific situations, not always tested:
HTTP version differences (1.1 vs 2 vs 3) · API taxonomy

**Reference** — Know it exists, look up syntax when needed:
specific HTTP spec details · header catalog

---

## Every App You Love Uses APIs

Let's play a quick game. Think of any app you use regularly. I'll show you the APIs
behind it.

**Instagram** — when you scroll your feed, your phone hits Instagram's API to get the
next batch of posts. When you tap the heart, it hits the API to record your like. When
you post a photo, your phone uploads it through the API.

**Google Maps** — when your Uber app shows a map, it's calling Google Maps' API to get
map tiles and directions. Uber built their own app, but they didn't build their own
mapping service. They just call Google's API.

**Stripe** — when you buy something online and enter your credit card, the website calls
Stripe's API to process the payment. They don't build payment processing themselves.
Why would they? Stripe already did it.

**Weather apps** — almost every weather app you've ever used doesn't have weather data.
They call a weather data API (like OpenWeatherMap or WeatherAPI) and just display what
they get back. The whole app is basically just a UI wrapper around API calls.

This is one of the most important ideas in modern software: **you don't build everything
yourself. You call APIs.**

---

## HTTP — The Language of the Web

Now, APIs can technically work over any communication system. But in practice, the
overwhelming majority of APIs you'll encounter use HTTP — the same protocol your browser
uses to load web pages.

HTTP stands for HyperText Transfer Protocol. It was designed in the early 90s for
transferring web pages, but it turned out to be such a good general-purpose communication
protocol that everything now uses it.

Here's the core idea: **HTTP is a request-response protocol.**

You send a request. You get a response. That's it. There's no ongoing connection
(usually), no back-and-forth negotiation. You ask a question, you get an answer.

Think of it like a postal letter:

```
You write a letter (REQUEST):
  - Who you're sending it to   → URL
  - What you want them to do   → HTTP Method (GET, POST, etc.)
  - Extra context              → Headers
  - The actual content         → Body

They write back (RESPONSE):
  - Did it work?               → Status Code (200, 404, etc.)
  - Extra context              → Headers
  - The actual answer          → Body
```

Let's look at what a real HTTP request actually looks like under the hood. When your
browser loads `https://api.github.com/users/octocat`, it sends something like this:

```
GET /users/octocat HTTP/1.1
Host: api.github.com
Accept: application/json
User-Agent: Mozilla/5.0
Authorization: Bearer ghp_yourtoken123
```

And GitHub's server responds with something like:

```
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: public, max-age=60
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59

{
  "login": "octocat",
  "id": 583231,
  "name": "The Octocat",
  "company": "GitHub",
  "blog": "https://github.blog",
  "location": "San Francisco, CA",
  "public_repos": 8
}
```

That's an API. A raw HTTP request going out, a raw HTTP response coming back. Everything
else — the libraries, the frameworks, the SDKs — they're just making this easier to
write and read.

> 📝 **Practice:** [Q18 · http-connection-keepalive](../api_practice_questions_100.md#q18--normal--http-connection-keepalive)

---

## HTTP Methods — The Verbs

Every HTTP request has a method. The method is a verb — it tells the server what kind of
action you want to perform.

There are five you'll use all the time:

```
GET    → fetch something
POST   → create something
PUT    → replace something (the whole thing)
PATCH  → update part of something
DELETE → remove something
```

Let's make these concrete with a real example. Imagine you're building an API for a
to-do list app. Here's how you'd use each verb:

**GET — Fetch something (read-only)**

```
GET /tasks          → give me all my tasks
GET /tasks/42       → give me task number 42
```

GET requests should never have side effects. Calling `GET /tasks` a hundred times should
give you the same result as calling it once (assuming nothing else changes). The server
never changes anything because of a GET. It just reads and returns.

**POST — Create something**

```
POST /tasks
Body: {"title": "Buy milk", "due": "2024-01-15"}

→ creates a new task, returns it with its new ID
```

POST has side effects. Every time you call `POST /tasks`, you create a new task. Call it
ten times, get ten tasks. This is why submitting a form twice sometimes double-submits —
it's making two POST requests.

**PUT — Replace something entirely**

```
PUT /tasks/42
Body: {"title": "Buy oat milk", "due": "2024-01-15", "done": false}

→ replaces task 42 completely with what you sent
```

With PUT, you send the entire resource. Whatever you send is what gets stored. If you
forget to include a field, that field gets wiped. PUT is nuclear — it replaces everything.

**PATCH — Update part of something**

```
PATCH /tasks/42
Body: {"done": true}

→ marks task 42 as done, leaves everything else unchanged
```

PATCH is surgical. You send only what changed. The server merges your changes into the
existing resource. This is what you want most of the time when "updating" something.

**DELETE — Remove something**

```
DELETE /tasks/42

→ deletes task 42, returns 204 No Content (usually)
```

Delete what it says on the tin. After a successful DELETE, the resource is gone.

---

## Status Codes — The Response Language

When the server responds, it includes a three-digit status code. This code tells you,
at a glance, whether things went well or not — and if not, roughly why.

They're organized into five groups:

```
1xx → Informational  (rare, you usually don't see these)
2xx → Success        (the request worked)
3xx → Redirection    (go look over there instead)
4xx → Client error   (you did something wrong)
5xx → Server error   (the server did something wrong)
```

The mental model: **2 is great, 4 is your fault, 5 is their fault.**

### 2xx — Success

**200 OK** — The classic. Everything worked, here's your data.

**201 Created** — You POSTed something, and it was created. You'll usually get the new
resource back in the response body.

**204 No Content** — Success, but there's nothing to return. Common for DELETE and some
PATCHes. "I did what you asked, nothing to send back."

### 3xx — Redirection

**301 Moved Permanently** — This URL has moved forever. Update your bookmarks. Your
browser will follow the redirect automatically.

**304 Not Modified** — "You already have the latest version." Used with caching. If you
ask "has this changed since yesterday?" and it hasn't, you get a 304. No body, just the
status code.

### 4xx — Client Error (you messed up)

**400 Bad Request** — Your request is malformed. Missing required fields, wrong data
types, invalid JSON. The server couldn't parse what you sent.

**401 Unauthorized** — You need to authenticate. You're not logged in (or your token
expired). "Who are you?"

**403 Forbidden** — You're authenticated, but you don't have permission. You're logged
in, but you're trying to access someone else's data. "I know who you are, but no."

**404 Not Found** — The resource doesn't exist. Wrong ID, wrong URL, or the thing was
deleted.

**422 Unprocessable Entity** — Your request was technically valid JSON, but the content
failed validation. Like sending `{"age": -5}` — that's valid JSON, but a negative age
doesn't make sense.

**429 Too Many Requests** — You've hit the rate limit. Slow down. The response usually
includes a `Retry-After` header telling you when to try again.

### 5xx — Server Error (they messed up)

**500 Internal Server Error** — Something blew up on the server. Generic catch-all for
"we didn't handle this correctly."

**502 Bad Gateway** — The server got a bad response from something behind it (usually a
proxy or load balancer talking to an upstream service).

**503 Service Unavailable** — The server is down or overloaded. Try again later.

**504 Gateway Timeout** — The server gave up waiting for something behind it to respond.

### A mnemonic to remember them

- **2xx** — Two thumbs up. Everything's fine.
- **4xx** — For the client. You messed up.
- **5xx** — Five-alarm fire on the server. Their fault.
- **401 vs 403** — 401 is "who are you?" (not authenticated). 403 is "I know you, but
  no" (not authorized). The numbers don't help much, but the question does: did they
  log in yet?
- **404** — Everyone knows this one. Not found.
- **429** — 42, the meaning of life, you're doing too much of it. Slow down.

---

## Headers — The Metadata

Every HTTP request and response has headers. Think of headers as the envelope of a
letter — they contain information about the message itself, not the message content.

Headers are key-value pairs:

```
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
Accept: application/json
Cache-Control: max-age=3600
```

Here are the headers you'll encounter constantly:

### Content-Type

Tells the recipient what format the body is in.

```
Content-Type: application/json          → the body is JSON
Content-Type: application/x-www-form-urlencoded  → HTML form data
Content-Type: multipart/form-data       → file uploads
Content-Type: text/html                 → HTML page
Content-Type: text/plain                → plain text
```

If you send JSON without setting `Content-Type: application/json`, some servers will
reject your request because they don't know how to parse what you sent.

### Authorization

How you prove who you are.

```
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo0Mn0...
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
Authorization: ApiKey sk_live_abc123xyz
```

The most common pattern today is `Bearer <token>` where the token is a JWT (JSON Web
Token) — covered in the security module.

### Accept

You use this in requests to tell the server what format you want back.

```
Accept: application/json    → please respond with JSON
Accept: text/html           → please respond with HTML
Accept: */*                 → I'll take anything
```

Most APIs only speak JSON, so this is often not needed. But some APIs can return
multiple formats, and this header lets you choose.

### Cache-Control

Controls caching behavior — both in responses (server tells client how long to cache)
and in requests (client tells intermediaries what to do).

```
Cache-Control: max-age=3600          → cache this for 1 hour
Cache-Control: no-cache              → revalidate before using cache
Cache-Control: no-store              → don't cache this at all (sensitive data)
Cache-Control: private               → only the browser can cache, not CDNs
Cache-Control: public                → anyone (CDNs, proxies) can cache this
```

### User-Agent

Identifies the software making the request. Servers can use this for analytics or to
reject bots.

```
User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0)
User-Agent: python-requests/2.31.0
User-Agent: MyApp/1.0 (+https://myapp.com)
```

### X-RateLimit Headers

Not standard HTTP, but conventional. Many APIs include these so you know how close you
are to hitting rate limits.

```
X-RateLimit-Limit: 1000        → 1000 requests per hour allowed
X-RateLimit-Remaining: 842     → 842 remaining this hour
X-RateLimit-Reset: 1609459200  → Unix timestamp when limit resets
```

---

## JSON — The Common Language

APIs could respond with anything — XML, CSV, plain text, binary data. And historically,
many did. (Ask any developer who's worked with SOAP APIs and watch their eye twitch.)

But today, almost every web API you'll encounter uses JSON.

**JSON = JavaScript Object Notation**

Despite the name, it's not just for JavaScript. Every major programming language can
parse it. It's human-readable. It maps naturally to the data structures every programmer
already knows (dictionaries/objects, lists/arrays, strings, numbers, booleans).

### JSON types

```json
{
  "name": "Alice",           ← string (always double-quoted)
  "age": 30,                 ← number (no quotes)
  "is_admin": true,          ← boolean (true or false, no quotes)
  "middle_name": null,       ← null (represents "nothing")
  "scores": [95, 87, 92],    ← array (ordered list)
  "address": {               ← object (nested key-value pairs)
    "street": "123 Main St",
    "city": "Austin",
    "zip": "78701"
  }
}
```

### A real API response

Here's what GitHub's API actually returns when you ask for a user:

```json
{
  "login": "torvalds",
  "id": 1024025,
  "node_id": "MDQ6VXNlcjEwMjQwMjU=",
  "avatar_url": "https://avatars.githubusercontent.com/u/1024025",
  "url": "https://api.github.com/users/torvalds",
  "html_url": "https://github.com/torvalds",
  "type": "User",
  "site_admin": false,
  "name": "Linus Torvalds",
  "company": "Linux Foundation",
  "blog": "",
  "location": "Portland, OR",
  "email": null,
  "bio": null,
  "public_repos": 7,
  "public_gists": 0,
  "followers": 245000,
  "following": 0,
  "created_at": "2011-09-03T15:26:22Z",
  "updated_at": "2024-01-10T02:05:01Z"
}
```

This is exactly what you get back from the API. Your code receives this as a string,
parses it into a dictionary (or whatever your language calls it), and works with the
data.

A few things to notice:
- Dates are strings in ISO 8601 format (`"2024-01-10T02:05:01Z"`). JSON doesn't have a
  date type, so dates are always strings.
- `null` means the field exists but has no value (different from the field not existing
  at all).
- Numbers are just numbers — no quotes, no special handling.

---

## Your First API Call

Enough theory. Let's actually call an API.

We'll use Python's `requests` library — the most popular HTTP library in Python, and
honestly one of the best-designed libraries in any language.

First, install it if you haven't:

```bash
pip install requests
```

Now let's hit the GitHub API. No authentication needed for public data:

```python
import requests

# Make a GET request to the GitHub API

response = requests.get("https://api.github.com/users/octocat")


# Check if it worked
print(response.status_code)  # 200

# Get the response as a Python dictionary
data = response.json()
print(data["name"])    # "The Octocat"
print(data["login"])   # "octocat"
print(data["public_repos"])  # 8
```

> 📝 **Practice:** [Q16 · request-lifecycle](../api_practice_questions_100.md#q16--normal--request-lifecycle)


That's it. That's an API call.

Let's look at what `requests` gives you back:

```python
import requests

response = requests.get("https://api.github.com/users/octocat")

# Status code
print(response.status_code)   # 200

# Response headers
print(response.headers["Content-Type"])       # application/json; charset=utf-8
print(response.headers["X-RateLimit-Remaining"])  # 59

# Response body as text (raw string)
print(response.text)  # '{"login":"octocat","id":583231,...}'

# Response body parsed as JSON (Python dict)
print(response.json())  # {'login': 'octocat', 'id': 583231, ...}
```

Now let's make a more interesting request — one with authentication and error handling:

```python
import requests

def get_github_user(username, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.get(
        f"https://api.github.com/users/{username}",
        headers=headers
    )

    # Check if the request succeeded
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        print(f"User '{username}' not found")
        return None
    elif response.status_code == 401:
        print("Bad credentials")
        return None
    else:
        print(f"Unexpected error: {response.status_code}")
        return None

user = get_github_user("torvalds")
if user:
    print(f"{user['name']} has {user['followers']} followers")
```

And let's make a POST request — actually creating something:

```python
import requests

# GitHub lets you create issues via their API
# You'd need a real token for this to work

token = "ghp_yourtokenhere"
repo_owner = "your-username"
repo_name = "your-repo"

response = requests.post(
    f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.github.v3+json"
    },
    json={                                 # requests serializes this to JSON for you
        "title": "Something is broken",
        "body": "Steps to reproduce:\n1. Do the thing\n2. It breaks",
        "labels": ["bug"]
    }
)

if response.status_code == 201:           # 201 Created, not 200 OK
    issue = response.json()
    print(f"Created issue #{issue['number']}: {issue['title']}")
    print(f"URL: {issue['html_url']}")
```

Notice: a successful POST returns `201 Created`, not `200 OK`. New resource created,
different status code.

---

## The Client-Server Model Revisited

We keep saying "client" and "server." Let's make sure this is crystal clear, because
it's more nuanced than you might think.

```
CLIENT                              SERVER
(makes requests)                    (handles requests)
     |                                    |
     |  ──── request ───────────────────> |
     |  <─── response ───────────────── |
     |                                    |
```

**Client = the one asking. Server = the one answering.**

That seems obvious, but here's where it gets interesting: the roles aren't fixed. The
same machine can be a client in one conversation and a server in another.

**Your browser is a client:**
```
Browser ──── GET https://twitter.com ───────────────> Twitter's server
Browser <─── HTML, CSS, JavaScript ─────────────────
```

**The Twitter server is a client when it calls other services:**
```
Twitter's server ──── POST https://api.cdn.com/upload ──> CDN service
Twitter's server <─── 201 Created ─────────────────────
```

**Your mobile app is a client:**
```
Uber app ──── GET /nearby-drivers?lat=30.2&lng=-97.7 ──> Uber's server
Uber app <─── [{driver}, {driver}, {driver}] ──────────
```

**Your backend is a client when calling third-party APIs:**
```
Your server ──── POST https://api.stripe.com/charges ──> Stripe
Your server <─── {charge object} ──────────────────────
```

The API is always described from the **client's perspective** — the perspective of the
caller. When someone says "the Stripe API," they mean "here's how to call Stripe from
your code." Stripe is the server. You are the client.

This is important for understanding documentation. API docs tell you how to make
requests — what URL to hit, what to include, what you'll get back. They're written for
the client (you).

---

## APIs Are Everywhere — And That's the Point

Here's the modern software architecture reality:

```
                    Your Mobile App
                          |
                          | (API calls)
                          v
                    Your Backend
                     /    |    \
                    /     |     \
                   v      v      v
               Stripe  Twilio  SendGrid
              (payments)(SMS)  (email)
                   \      |      /
                    \     |     /
                     v    v    v
                    (vendor APIs)
```

You don't build payment processing. You call Stripe's API.
You don't build SMS infrastructure. You call Twilio's API.
You don't build email delivery. You call SendGrid's API.

This is why understanding APIs is so fundamental. Modern software development is largely
about:
1. Building your own API (so your frontend can talk to your backend)
2. Calling other people's APIs (so you don't reinvent the wheel)

---

## REST vs APIs in General

One more thing before we go deeper. You'll hear "REST API" everywhere. REST is not the
only kind of API. It's just the most common kind.

```
REST        → Resource-based, uses HTTP methods, returns JSON
              (What most APIs you'll use are)

GraphQL     → Query language, you ask for exactly what you want
              (Facebook invented it, used in complex UIs)

gRPC        → Binary protocol, super fast, used between backend services
              (Google's contribution, common in microservices)

WebSockets  → Persistent two-way connection, real-time
              (Chat apps, live dashboards, collaborative tools)
```

We'll cover all of these. But REST is where we start because:
1. It's what most public APIs use
2. It builds on HTTP concepts you already have context for
3. Every other type makes more sense once you understand REST's tradeoffs

---

## Summary

Here's what you just learned:

```
API          = a defined way for two programs to talk
HTTP         = the protocol most APIs use (request-response)
HTTP Request = method + URL + headers + body
HTTP Response = status code + headers + body

Methods:
  GET    → read
  POST   → create
  PUT    → replace
  PATCH  → update part of
  DELETE → delete

Status codes:
  2xx → success
  4xx → you messed up
  5xx → they messed up

Headers     = metadata about the request/response
JSON        = the format most APIs use for data
requests    = Python library for making HTTP requests
```

You've got the foundation. Now let's go deeper into REST specifically — the most
common API style you'll encounter.

---

## 📝 Practice Questions

> 📝 **Practice:** [Q17 · http2-vs-http1](../api_practice_questions_100.md#q17--thinking--http2-vs-http1)

---

**[🏠 Back to README](../README.md)**

**Prev:** — &nbsp;|&nbsp; **Next:** [REST Fundamentals →](../02_rest_fundamentals/rest_explained.md)

**Related Topics:** [REST Fundamentals](../02_rest_fundamentals/rest_explained.md) · [Error Handling Standards](../06_error_handling_standards/error_guide.md) · [Authentication & Authorization](../05_authentication/securing_apis.md)
