# Project 02: WebSocket Realtime Chat

**Difficulty:** Partially Guided — every step has a concept explanation and complete answer, but no explicit hint. Read the concept, think through the code structure, then expand the answer.

**What you'll build:** A real-time chat server using the `websockets` library and `asyncio`. The server handles multiple clients without threads. A single `index.html` file acts as the client — open it in a browser and chat across tabs.

**Files you'll create:**
- `server.py` — async WebSocket server, manages connections, broadcasts messages
- `index.html` — self-contained browser client, no build step required

**How to test:** run `server.py` in one terminal, open `index.html` in two or three browser tabs.

---

## Step 1: Why WebSockets Over Raw Sockets

> Like upgrading from walkie-talkies to a proper phone line — raw sockets work, but WebSockets add a shared language that browsers already speak.

**What you're doing:** Understand the problem WebSockets solve, when to use them vs raw TCP, and install the library.

**Concept:** In Project 03 you used raw TCP sockets — bytes flowing directly between Python processes. Browsers cannot do this. A browser can only communicate using protocols it understands: HTTP and **WebSocket**. A **WebSocket** connection starts as an ordinary HTTP request (a GET with an `Upgrade: websocket` header), the server accepts the upgrade, and from that point both sides can send messages in either direction at any time. This is fundamentally different from regular HTTP, where the client always initiates each request and the server only responds. **HTTP polling** — where the browser repeatedly asks "anything new?" every few seconds — was the workaround before WebSockets. It wastes bandwidth, adds latency, and hammers your server. WebSockets eliminate all of that with a persistent, full-duplex connection. The `websockets` Python library implements the WebSocket protocol on top of asyncio, so you get async I/O without threads.

**Before looking at the answer:**
- What does "full-duplex" mean? How is it different from HTTP request/response?
- Name a real product that uses WebSockets. What would break if it used polling instead?

<details>
<summary>✅ Answer</summary>

```bash
pip install websockets
```

```
HTTP polling (old way):
  Browser:  "Anything new?"  →  Server: "No."   (every 2 seconds, forever)
  Browser:  "Anything new?"  →  Server: "No."
  Browser:  "Anything new?"  →  Server: "Yes! Here's a message."

WebSocket (new way):
  Browser:  "Upgrade to WebSocket?"  →  Server: "OK."
  --- persistent connection open ---
  Server:   "New message from Alice!"  (whenever it arrives)
  Server:   "New message from Bob!"
  Browser:  "Sending: Hello!"
  --- connection stays open until either side closes it ---
```

**Key insight:** WebSockets are the right tool when the server needs to push data to the client unprompted — chat, live dashboards, collaborative editing, stock tickers, multiplayer games. For infrequent, client-initiated data fetching, regular HTTP is simpler and sufficient.

</details>

---

## Step 2: Hello WebSocket

> Like writing your first "Hello World" but for a two-way radio — you need to prove both sides can talk before building anything bigger.

**What you're doing:** Write a minimal WebSocket server that accepts one connection, receives a message, and sends one back.

**Concept:** The `websockets` library is built on **asyncio**, Python's single-threaded concurrency model. Instead of threads, asyncio uses an **event loop** — a single loop that continuously checks: "is any I/O ready?" When a coroutine awaits something (a network read, a sleep, a connection), it suspends and hands control back to the event loop, which can then run other coroutines. A **coroutine** is a function defined with `async def` — it doesn't run when called, it returns a coroutine object. You run it by `await`ing it from inside another coroutine, or by passing it to `asyncio.run()`. `websockets.serve(handler, host, port)` returns an async context manager that starts the server. Inside `handler`, `await websocket.recv()` suspends until a message arrives, and `await websocket.send(msg)` suspends until the message is delivered. Unlike `socket.recv()`, these yield control to the event loop while waiting, so other coroutines can run.

**Before looking at the answer:**
- What is the difference between calling `some_coroutine()` and `await some_coroutine()`? What does each return?
- If asyncio is single-threaded, how can it handle two clients sending messages at the same time?

<details>
<summary>✅ Answer</summary>

```python
# server.py — minimal hello WebSocket

import asyncio
import websockets

async def handler(websocket):           # ← called once per connected client
    message = await websocket.recv()    # ← suspend until client sends something
    print(f"Received: {message}")
    await websocket.send(f"Echo: {message}")  # ← suspend until sent

async def main():
    # websockets.serve returns a server context manager
    async with websockets.serve(handler, "localhost", 8765):  # ← start server on port 8765
        print("Server running on ws://localhost:8765")
        await asyncio.Future()          # ← run forever (Future that never resolves)

asyncio.run(main())                     # ← start the event loop
```

**Key insight:** `await asyncio.Future()` is the idiomatic way to keep an asyncio program running forever — a `Future` that is never resolved means the `await` never returns, so `main()` never exits. The event loop keeps running, handling connections in the background.

</details>

---

## Step 3: Track Connected Clients

> Like a venue's clicker counter at the door — you need to know exactly who's inside at any given moment, and update the count every time someone enters or leaves.

**What you're doing:** Add a global set to track all active WebSocket connections, registering on connect and unregistering on disconnect.

**Concept:** A **set** (not a list) is the right data structure here for two reasons: sets guarantee uniqueness (a websocket object can only appear once even if you add it twice), and membership testing is O(1) vs O(n) for lists. Because asyncio is **single-threaded**, you do not need a lock — only one coroutine runs at a time, so there is no risk of concurrent modification. This is one of asyncio's practical advantages over threading. The pattern is always the same: `connected.add(websocket)` at the top of the handler, then a `try/finally` block wrapping the message loop, with `connected.discard(websocket)` in the `finally`. Using `discard` instead of `remove` means no exception is raised if the socket somehow isn't in the set — more defensive.

**Before looking at the answer:**
- Why does `finally` guarantee cleanup even if an exception occurs? Describe a scenario where this matters for a chat server.
- What is the difference between `set.remove(x)` and `set.discard(x)`?

<details>
<summary>✅ Answer</summary>

```python
# server.py — with connection tracking

import asyncio
import websockets

connected = set()  # ← global set of all active websocket connections

async def handler(websocket):
    connected.add(websocket)            # ← register on connect
    print(f"Client connected. Total: {len(connected)}")

    try:
        async for message in websocket:  # ← iterate messages until connection closes
            print(f"Received: {message}")
            await websocket.send(f"Echo: {message}")
    except websockets.ConnectionClosed:  # ← normal close event
        pass
    finally:
        connected.discard(websocket)    # ← always unregister, even on error
        print(f"Client disconnected. Total: {len(connected)}")

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("Server running on ws://localhost:8765")
        await asyncio.Future()

asyncio.run(main())
```

**Key insight:** `async for message in websocket:` is cleaner than writing a `while True: await websocket.recv()` loop — it automatically handles the `ConnectionClosed` exception and exits the loop when the client disconnects, making the `try/except` optional (though keeping it is still good practice for clarity).

</details>

---

## Step 4: Broadcast Function

> Like a radio tower: one signal goes in, and every antenna in range receives it simultaneously — not one after another.

**What you're doing:** Write an async broadcast function that sends a message to all connected clients except the sender.

**Concept:** The naive approach is a `for` loop with `await websocket.send(msg)` for each client. This works but is **sequential** — you wait for client A's send to complete before starting client B's. With `asyncio.gather()`, you can start all the sends simultaneously and await them all at once. `asyncio.gather(*coroutines)` schedules all the coroutines concurrently on the event loop and returns when all of them complete. This is the asyncio equivalent of "do all of these things at the same time." `websockets.ConnectionClosed` is raised when you try to send to a client that has already disconnected — wrapping each send in a try/except (or using `gather` with `return_exceptions=True`) prevents one dead client from interrupting the broadcast to the others.

**Before looking at the answer:**
- What does the `*` in `asyncio.gather(*list_of_coroutines)` do? What would happen without it?
- Why might you want `return_exceptions=True` in `gather` rather than letting exceptions propagate?

<details>
<summary>✅ Answer</summary>

```python
# broadcast function — add to server.py

async def broadcast(message, sender):
    """Send message to all connected clients except the sender."""
    if not connected:                    # ← nothing to do if no one else is connected
        return

    recipients = {ws for ws in connected if ws is not sender}  # ← set comprehension, skip sender

    if recipients:
        # gather runs all sends concurrently, return_exceptions=True prevents one failure from
        # cancelling sends to other clients
        await asyncio.gather(
            *[ws.send(message) for ws in recipients],  # ← unpack list into individual args
            return_exceptions=True                      # ← collect exceptions instead of raising
        )
```

**Key insight:** `return_exceptions=True` means `gather` returns a list where each element is either the result of the coroutine or the exception it raised. Without this flag, the first exception would propagate out of `gather` and skip the remaining recipients. With it, all sends run regardless, and you can inspect the results list if you want to log failures.

</details>

---

## Step 5: Username Registration

> Like a username prompt on the first screen of a game — the very first thing you type is your name, and from then on everything you do is attributed to it.

**What you're doing:** Treat each client's first message as their username, store it, and announce joins and leaves with the current user count.

**Concept:** Username registration follows the same pattern as Project 03 but with async syntax: the first `await websocket.recv()` call receives the name, which is stored in a **dictionary** `{websocket: username}`. This dict is global and shared across all handler coroutines. Because asyncio is single-threaded, no locking is needed — coroutines yield control only at `await` points, so no two coroutines can be modifying the dict simultaneously. When a client disconnects, `del users[websocket]` removes their entry in the `finally` block. The join/leave announcements include `len(connected)` to give everyone a sense of the room's size.

**Before looking at the answer:**
- Why is a dictionary keyed by `websocket` better than a list of `(websocket, name)` tuples for this use case?
- At what point in `handler()` should you add the client to `connected` — before or after receiving the username? What are the trade-offs?

<details>
<summary>✅ Answer</summary>

```python
# server.py — complete version with usernames and broadcast

import asyncio
import websockets

connected = set()
users = {}  # ← {websocket: username}

async def broadcast(message, sender=None):
    """Broadcast message string to all connected clients except sender."""
    recipients = {ws for ws in connected if ws is not sender}
    if recipients:
        await asyncio.gather(
            *[ws.send(message) for ws in recipients],
            return_exceptions=True
        )

async def handler(websocket):
    # Step 1: Get username (first message)
    try:
        username = await websocket.recv()         # ← first message is the name
        username = username.strip() or "Anonymous"
    except websockets.ConnectionClosed:
        return                                    # ← client left before sending name

    # Step 2: Register
    connected.add(websocket)
    users[websocket] = username
    user_count = len(connected)

    print(f"{username} joined. Users online: {user_count}")
    await broadcast(
        f"*** {username} joined | {user_count} online ***",
        sender=websocket                          # ← don't send join notice to the joiner
    )
    await websocket.send(f"Welcome, {username}! {user_count - 1} other(s) online.")

    # Step 3: Message loop
    try:
        async for message in websocket:
            formatted = f"[{username}]: {message}"
            print(formatted)
            await broadcast(formatted, sender=websocket)
    except websockets.ConnectionClosed:
        pass
    finally:
        # Step 4: Clean up
        connected.discard(websocket)
        users.pop(websocket, None)                # ← pop with default avoids KeyError
        user_count = len(connected)

        print(f"{username} left. Users online: {user_count}")
        await broadcast(f"*** {username} left | {user_count} online ***")

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("WebSocket server running on ws://localhost:8765")
        await asyncio.Future()

asyncio.run(main())
```

**Key insight:** Using `users.pop(websocket, None)` instead of `del users[websocket]` in the `finally` block is defensive — if the connection closed before the username was stored (e.g., the client disconnected during the initial `recv()`), `del` would raise a `KeyError`. `pop` with a default silently handles the missing key.

</details>

---

## Step 6: Build the HTML Client

> Like building a store's front window — the server has been humming along perfectly, but without a visible interface nobody knows it's there or how to use it.

**What you're doing:** Write a single `index.html` that connects via browser WebSocket, lets the user set a username, sends messages, and shows incoming messages and user count.

**Concept:** Browsers have a native **WebSocket API** — no library needed. `new WebSocket('ws://localhost:8765')` creates a connection. The object exposes four event callbacks: `ws.onopen` (connection established), `ws.onmessage` (message received — `event.data` holds the string), `ws.onerror` (connection error), and `ws.onclose` (connection closed). `ws.send(string)` sends a message. The browser's WebSocket implementation handles the HTTP upgrade handshake automatically. The first message your client sends will be the username (matching what the server expects). All subsequent messages are chat content. This design decision — "first message is special" — is a **stateful protocol convention** that you and the server agree on.

**Before looking at the answer:**
- The browser WebSocket sends strings by default. Does this match what the Python `websockets` server receives? What would you need to change to send JSON instead?
- What happens in the UI if you call `ws.send()` before `ws.onopen` fires? How would you prevent this?

<details>
<summary>✅ Answer</summary>

```html
<!-- index.html — complete self-contained WebSocket chat client -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>WebSocket Chat</title>
  <style>
    body { font-family: monospace; max-width: 700px; margin: 40px auto; padding: 0 20px; background: #111; color: #eee; }
    h1 { color: #7af; }
    #chat-box { height: 400px; overflow-y: auto; border: 1px solid #444; padding: 10px; margin-bottom: 10px; background: #1a1a1a; border-radius: 4px; }
    .message { margin: 4px 0; }
    .system { color: #888; font-style: italic; }
    .own { color: #7af; }
    #status { color: #aaa; font-size: 0.85em; margin-bottom: 10px; }
    #input-row { display: flex; gap: 8px; }
    #message-input { flex: 1; padding: 8px; background: #222; color: #eee; border: 1px solid #444; border-radius: 4px; }
    button { padding: 8px 16px; background: #335; color: #eee; border: 1px solid #558; border-radius: 4px; cursor: pointer; }
    button:hover { background: #447; }
    #name-row { display: flex; gap: 8px; margin-bottom: 10px; }
    #name-input { padding: 8px; background: #222; color: #eee; border: 1px solid #444; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>WebSocket Chat</h1>
  <div id="status">Not connected</div>

  <div id="name-row">
    <input id="name-input" type="text" placeholder="Your name" maxlength="20">
    <button onclick="connect()">Connect</button>
  </div>

  <div id="chat-box"></div>

  <div id="input-row">
    <input id="message-input" type="text" placeholder="Type a message..." disabled>
    <button onclick="sendMessage()" id="send-btn" disabled>Send</button>
  </div>

  <script>
    let ws = null;  // ← WebSocket instance, null until connected

    function connect() {
      const name = document.getElementById('name-input').value.trim();
      if (!name) {
        alert('Please enter a name first.');
        return;
      }

      // Create WebSocket connection
      ws = new WebSocket('ws://localhost:8765');  // ← connect to Python server

      ws.onopen = function() {
        // Connection is open — first message must be the username
        ws.send(name);                              // ← server expects name as first message
        setStatus('Connected as ' + name);
        document.getElementById('message-input').disabled = false;
        document.getElementById('send-btn').disabled = false;
        document.getElementById('name-input').disabled = true;
        document.querySelector('#name-row button').disabled = true;
        document.getElementById('message-input').focus();
        addMessage('Connected to server.', 'system');
      };

      ws.onmessage = function(event) {
        // Determine message style: own messages, system messages, or others
        const text = event.data;
        const myName = document.getElementById('name-input').value.trim();
        let cls = 'message';
        if (text.startsWith('***')) {
          cls = 'system';                           // ← join/leave notices
        } else if (text.startsWith('[' + myName + ']:')) {
          cls = 'own';                              // ← shouldn't happen (server skips sender)
        }
        addMessage(text, cls);
      };

      ws.onerror = function() {
        addMessage('Connection error. Is the server running?', 'system');
        setStatus('Error');
      };

      ws.onclose = function() {
        addMessage('Disconnected from server.', 'system');
        setStatus('Disconnected');
        document.getElementById('message-input').disabled = true;
        document.getElementById('send-btn').disabled = true;
      };
    }

    function sendMessage() {
      const input = document.getElementById('message-input');
      const text = input.value.trim();
      if (!text || !ws || ws.readyState !== WebSocket.OPEN) return;  // ← guard: only send if connected

      ws.send(text);                                // ← send to server
      addMessage('[You]: ' + text, 'own');          // ← show in own chat box immediately
      input.value = '';
    }

    function addMessage(text, cssClass) {
      const box = document.getElementById('chat-box');
      const div = document.createElement('div');
      div.className = cssClass;
      div.textContent = text;                       // ← textContent prevents XSS (not innerHTML)
      box.appendChild(div);
      box.scrollTop = box.scrollHeight;             // ← auto-scroll to latest message
    }

    function setStatus(text) {
      document.getElementById('status').textContent = text;
    }

    // Allow Enter key to send
    document.getElementById('message-input').addEventListener('keydown', function(e) {
      if (e.key === 'Enter') sendMessage();
    });
  </script>
</body>
</html>
```

**Key insight:** `ws.readyState !== WebSocket.OPEN` is a critical guard — the WebSocket can be in four states (CONNECTING, OPEN, CLOSING, CLOSED). Calling `ws.send()` in any state other than OPEN throws an error. Always check `readyState` before sending. Also note `textContent` not `innerHTML` — always use `textContent` when displaying user-supplied strings to prevent XSS injection.

</details>

---

## Step 7: Run and Test

> Like opening night — all the pieces are built, now you run the whole show and find out what actually happens.

**What you're doing:** Start the server, open the HTML client in multiple browser tabs, and verify real-time messaging works.

**Concept:** Opening `index.html` directly in a browser (via `file://`) works fine for this project because the WebSocket connects to `localhost` — no web server needed to serve the HTML. Each browser tab is an independent WebSocket connection. When you open two tabs and both connect, the server has two entries in `connected`. A message from Tab 1 should appear in Tab 2 within milliseconds — no polling, no delay. The browser DevTools Network tab is invaluable here: click the WS connection entry and watch frames appear in real time as messages are exchanged.

**Before looking at the answer:**
- If you open the HTML in a browser and see "Connection error", what are the three most likely causes?
- What does the Network tab in DevTools show you about a WebSocket connection that a regular HTTP request doesn't have?

<details>
<summary>✅ Answer</summary>

```bash
# Terminal 1 — start the server
python server.py
# Expected:
# WebSocket server running on ws://localhost:8765
```

```
# Open index.html in your browser (two ways):
# Option 1: drag the file into Chrome/Firefox
# Option 2: right-click → Open With → browser
```

```
Tab 1:
  - Enter name: Alice → click Connect
  - Status shows: Connected as Alice
  - Chat shows: Connected to server.
  - Chat shows: Welcome, Alice! 0 other(s) online.

Tab 2:
  - Enter name: Bob → click Connect
  - Tab 1 now shows: *** Bob joined | 2 online ***
  - Tab 2 shows: Welcome, Bob! 1 other(s) online.

Tab 1: type "Hello Bob!" → press Enter
  - Tab 2 shows: [Alice]: Hello Bob!
  - Server terminal shows: [Alice]: Hello Bob!

Close Tab 2:
  - Tab 1 shows: *** Bob left | 1 online ***
```

**Debugging checklist:**
```
"Connection error" in browser:
  1. Is server.py running? Check terminal for errors.
  2. Is port 8765 in use? Try: lsof -i :8765
  3. Is the URL in index.html ws://localhost:8765? Correct any typos.

Message not appearing in other tab:
  1. Did both tabs complete the name/connect flow?
  2. Check server terminal — did it log both connections?
  3. Open DevTools → Network → click the ws:// entry → Frames tab
```

**Key insight:** The Frames tab in DevTools (Chrome: DevTools → Network → click WS connection → Frames) shows every WebSocket message sent and received in real time. Arrows indicate direction: up arrow = sent by browser, down arrow = received. This is the most useful debugging tool for WebSocket clients.

</details>

---

## Step 8: Compare with Project 03

> Like comparing a hand-drawn map to Google Maps — both get you there, but they work differently, cost differently, and break differently.

**What you're doing:** Reflect on the architectural differences between the TCP threading approach and the WebSocket async approach, and understand when to reach for each.

**Concept:** Project 03 used **one thread per client** — simple to reason about (each thread handles one client, blocking I/O is fine), but threads are expensive. Each thread consumes memory (~8MB stack by default on Linux), and the OS pays context-switching costs when hundreds of threads are active. Project 04 uses **one event loop for all clients** — a single thread multiplexes thousands of connections via async I/O, with much lower overhead per connection. However, asyncio code is harder to reason about: any CPU-heavy computation blocks the entire event loop (since there's only one thread), and bugs where you forget `await` are silent and subtle. Neither is universally better — choose based on your workload and your team's familiarity.

**Before looking at the answer:**
- Think of a workload where threading would actually outperform asyncio. Describe it.
- If your WebSocket handler needed to do a slow database query for every message, what would happen to all other connected clients? How would you fix it?

<details>
<summary>✅ Answer</summary>

```
asyncio + websockets handles the slow DB query problem with:
  await asyncio.to_thread(slow_db_query, args)
  # runs the blocking call in a thread pool, yielding control to the event loop
  # other clients continue receiving messages while the query runs
```

**Comparison table:**

| | Project 03 (TCP + threading) | Project 04 (WebSocket + asyncio) |
|---|---|---|
| Concurrency model | One thread per client | One event loop, all clients |
| Library | `socket` (stdlib) | `websockets` (third-party) |
| Client type | Python only | Any browser |
| Protocol | Raw TCP bytes | WebSocket (HTTP upgrade) |
| CPU-heavy tasks | Fine — each thread runs independently | Blocks event loop — use `asyncio.to_thread()` |
| Memory per connection | ~8MB (thread stack) | ~few KB (coroutine frame) |
| Max practical connections | ~hundreds | Tens of thousands |
| Code complexity | Simpler mental model | Must understand async/await |
| Shared state protection | `threading.Lock()` required | No lock needed (single thread) |
| Browser-compatible | No | Yes |
| Debugging | Thread stack traces | async stack traces (harder) |

**Key insight:** For most real-world chat applications, asyncio wins on scalability. But if you're building a tool that only Python processes will connect to (microservices, CLI tools, internal automation), raw TCP sockets with threads are completely valid — no external library, simpler code, and the thread overhead doesn't matter at small scale.

</details>

---

## What You Built

```
  Browser Tab 1 (Alice)          Browser Tab 2 (Bob)
  ┌──────────────────┐           ┌──────────────────┐
  │   index.html     │           │   index.html     │
  │                  │           │                  │
  │  WebSocket API   │           │  WebSocket API   │
  └────────┬─────────┘           └────────┬─────────┘
           │ ws://localhost:8765           │ ws://localhost:8765
           │                              │
           └──────────────┬───────────────┘
                          │
             ┌────────────┴─────────────┐
             │        server.py         │
             │                          │
             │  asyncio event loop      │
             │                          │
             │  connected = {ws_A,ws_B} │
             │  users = {ws_A: "Alice", │
             │           ws_B: "Bob"}   │
             │                          │
             │  handler(ws_A)  ←──────── coroutine, suspended at recv()
             │  handler(ws_B)  ←──────── coroutine, suspended at recv()
             │                          │
             │  broadcast() runs when   │
             │  either handler receives │
             └──────────────────────────┘
```

## What You Learned

- **WebSocket protocol** — how an HTTP connection upgrades to a full-duplex persistent channel
- **asyncio event loop** — single-threaded concurrency via cooperative yielding at `await` points
- **async/await** — how coroutines suspend and resume without blocking the thread
- **asyncio.gather** — running multiple coroutines concurrently and collecting results
- **Browser WebSocket API** — `new WebSocket()`, `onopen`, `onmessage`, `onclose`, `ws.send()`
- **No-lock concurrency** — why shared state in asyncio doesn't need locks (single thread, yields only at await)
- **return_exceptions=True** — how to prevent one coroutine failure from cancelling a group in `gather`
- **Async context managers** — `async with websockets.serve(...)` for resource lifecycle management

## How It Connects to Project 03

| Dimension | Project 03: TCP Socket | Project 04: WebSocket |
|---|---|---|
| Transport | Raw TCP | TCP + HTTP upgrade |
| Python concurrency | `threading.Thread` per client | `asyncio` event loop |
| Shared state safety | `threading.Lock()` | No lock needed |
| Client type | Python `socket` | Any browser |
| Send/receive | `conn.send(bytes)` / `conn.recv()` | `await ws.send(str)` / `await ws.recv()` |
| Disconnect detection | `recv()` returns `b''` or raises | `ConnectionClosed` exception |
| Scalability ceiling | Hundreds of clients | Tens of thousands |
| External dependency | None (stdlib) | `pip install websockets` |

## Extend It

- Add rooms: parse `/join [room]` as a command, maintain a `rooms = {name: set()}` dict, broadcast only within the room
- Show a typing indicator: send a special `{"type": "typing", "user": name}` JSON message when the input field changes, clear it after 2 seconds
- Add message history for new joiners: maintain a `deque(maxlen=50)` of recent messages, send the full history to each new connection before announcing their join
