# Project 01: TCP Socket Chat Server

**Difficulty:** Fully Guided — every step has explanation, thinking prompts, hint, and answer.

**What you'll build:** A multi-client TCP chat server. One server process accepts any number of clients simultaneously. When one client sends a message, every other client sees it. Clients announce themselves by name when they join, and the server notifies everyone when someone leaves.

**Files you'll create:**
- `server.py` — listens for connections, manages clients, broadcasts messages
- `client.py` — connects to server, sends your input, prints incoming messages

**How to test:** run `server.py` in one terminal, then open two or three more terminals and run `client.py` in each.

---

## Step 1: Setup

> Like a contractor reviewing blueprints before breaking ground — understand the full structure before writing a single line.

**What you're doing:** Confirm you need no external libraries, create your two files, and mentally map out what each file will do.

**Concept:** Python's `socket` module is part of the **standard library** — no `pip install` needed. A socket is a two-way communication endpoint. Think of it like a phone: you dial a number (connect to an IP + port), someone picks up (the server accepts), and then you can both talk (send/receive data). `server.py` will be the switchboard operator — it sits and waits for calls, then routes messages between everyone connected. `client.py` is each person making a call.

**Think about it:**
- Before reading further: what do you think the server needs to do first before it can accept any connections?
- A chat server has two jobs at once: listen for new clients AND handle existing ones. How might you handle both at the same time in a single program?

<details>
<summary>💡 Hint</summary>

No code needed for this step — just create two empty files:

```bash
touch server.py
touch client.py
```

The server's first job will be creating a socket and telling the OS: "I want to receive connections on this port." The client's first job will be connecting to that port.

</details>

<details>
<summary>✅ Answer</summary>

```bash
# Create your project files
touch server.py
touch client.py
```

Add these skeleton comments to each file so you know what's coming:

```python
# server.py
# 1. Create a socket and bind it to a port
# 2. Listen for incoming connections
# 3. For each new connection, start a thread to handle it
# 4. Each thread: receive messages, broadcast to all other clients
```

```python
# client.py
# 1. Connect to the server
# 2. Start a thread to receive and print incoming messages
# 3. Main thread: read input() and send to server
```

**Why this works:** Separating send and receive into different threads (on the client) solves a core problem — `input()` blocks until the user presses Enter, but messages from other clients can arrive at any time. One thread waits for user input; the other waits for network data.

</details>

---

## Step 2: Create the Server Socket

> Like a restaurant opening its doors — before any customers can walk in, you need to pick a location (address), hang a sign (bind to a port), and unlock the door (listen).

**What you're doing:** Write the socket creation and configuration code that prepares the server to accept connections.

**Concept:** A **socket** is created with `socket.socket(family, type)`. The family `AF_INET` means IPv4 (the standard internet address format). The type `SOCK_STREAM` means TCP — a reliable, ordered, connection-based protocol (as opposed to `SOCK_DGRAM` for UDP, which is fire-and-forget). After creating the socket, `setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)` tells the OS to let you reuse the port immediately after restarting your server — without this, you get "Address already in use" errors during development. Then `bind((host, port))` claims that address, and `listen(max_backlog)` tells the OS how many pending connections to queue before refusing new ones.

**Think about it:**
- What happens if two programs try to bind to the same port? How does the OS handle that?
- Why do we need both `bind()` and `listen()`? What does each one actually do?

<details>
<summary>💡 Hint</summary>

```python
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(...)  # SOL_SOCKET, SO_REUSEADDR, 1
server.bind(('0.0.0.0', 5555))
server.listen(5)
```

`'0.0.0.0'` means "listen on all network interfaces" — useful so both `localhost` and your local IP work.

</details>

<details>
<summary>✅ Answer</summary>

```python
# server.py
import socket

HOST = '0.0.0.0'  # ← listen on all interfaces
PORT = 5555        # ← port number clients will connect to

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # ← IPv4, TCP
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # ← allow port reuse on restart
server.bind((HOST, PORT))  # ← claim this address
server.listen(5)           # ← queue up to 5 pending connections

print(f"Server listening on {HOST}:{PORT}")
```

**Why this works:** The OS manages a queue of incoming connection requests. `listen(5)` sets the maximum size of that queue — if 5 clients are waiting to be accepted and a 6th tries to connect, the 6th gets refused. For a chat server with low traffic, 5 is more than enough. The `SO_REUSEADDR` option is purely a developer convenience — in production, this is usually always set.

</details>

---

## Step 3: Accept One Client

> Like a hotel receptionist picking up the phone — the call only comes in when a guest actually dials, and until then you're just waiting.

**What you're doing:** Write the code to accept a single incoming connection and receive one message from it.

**Concept:** `server.accept()` is a **blocking call** — your program pauses here and waits until a client connects. When a client does connect, `accept()` returns a tuple: `(conn, addr)` where `conn` is a new socket object representing that specific client's connection, and `addr` is a `(ip, port)` tuple showing where the client connected from. You now use `conn` to talk to that specific client — `server` is only for accepting new connections. `conn.recv(1024)` receives up to 1024 **bytes** — sockets deal in raw bytes, so you must call `.decode('utf-8')` to get a Python string.

**Think about it:**
- `accept()` returns a new socket (`conn`). Why is it a new socket instead of reusing `server`? What is `server` still being used for?
- What happens to your program after `accept()` returns? Can it accept another client?

<details>
<summary>💡 Hint</summary>

```python
conn, addr = server.accept()   # blocks until a client connects
print(f"New connection from {addr}")

message = conn.recv(1024)      # receive raw bytes
print(message.decode('utf-8')) # convert bytes → string

conn.send("Hello!".encode('utf-8'))  # send bytes back
```

After this `accept()` call, the server is still bound to the port and can accept more clients — but your code is now past the `accept()` line, so it won't get back to accepting until you put it in a loop.

</details>

<details>
<summary>✅ Answer</summary>

```python
# server.py (continued — add below the listen() call)

conn, addr = server.accept()  # ← blocks here until a client connects
print(f"Connected: {addr}")

while True:
    try:
        message = conn.recv(1024)        # ← receive up to 1024 bytes
        if not message:                  # ← empty bytes = client disconnected
            break
        print(message.decode('utf-8'))   # ← bytes → string
        conn.send(message)               # ← echo it back
    except:
        break

conn.close()
print(f"Disconnected: {addr}")
```

**Why this works:** `recv()` returns empty bytes (`b''`) when the remote side closes the connection — this is the standard signal that the connection is done. Always check for this, otherwise your loop will spin forever on empty data. The `try/except` catches cases where the client disconnects abruptly (e.g., kills the process) which would otherwise raise an exception.

</details>

---

## Step 4: Receive and Echo

> Like a parrot at a customer service desk — it doesn't understand anything, it just repeats what you said.

**What you're doing:** Confirm the encode/decode pattern works correctly, and understand why sockets use bytes not strings.

**Concept:** TCP sockets transmit raw **bytes** — not Python strings, not JSON, not anything with inherent structure. When you call `send()`, you must pass a `bytes` object. When you call `recv()`, you get bytes back. The conversion is explicit: `"hello".encode('utf-8')` produces `b'hello'`, and `b'hello'.decode('utf-8')` gives back `"hello"`. **UTF-8** is the encoding you should default to — it handles all Unicode characters. This might seem verbose, but it forces you to be explicit about encoding, which prevents subtle bugs when messages contain non-ASCII characters.

**Think about it:**
- What would happen if you called `conn.send("hello")` without `.encode()`? Try to predict the error.
- What's the significance of `recv(1024)`? What happens if a message is longer than 1024 bytes?

<details>
<summary>💡 Hint</summary>

```python
# Sending
conn.send("Hello, client!".encode('utf-8'))

# Receiving
raw = conn.recv(1024)        # bytes
text = raw.decode('utf-8')   # string
```

For the buffer size question: `recv(1024)` reads *up to* 1024 bytes in one call. For longer messages, you'd need to call `recv()` in a loop until you've read everything. For a simple chat server with short messages, 1024 or 4096 is fine.

</details>

<details>
<summary>✅ Answer</summary>

```python
# This is the complete encode/decode pattern used throughout the project

def send_message(conn, text):
    """Send a string to a socket connection."""
    conn.send(text.encode('utf-8'))  # ← string → bytes before sending

def receive_message(conn):
    """Receive a string from a socket connection. Returns None on disconnect."""
    try:
        raw = conn.recv(4096)       # ← receive up to 4096 bytes
        if not raw:                 # ← empty = disconnected
            return None
        return raw.decode('utf-8')  # ← bytes → string
    except:
        return None                 # ← any socket error = treat as disconnect
```

**Why this works:** Wrapping send/receive in helper functions keeps the encoding logic in one place. If you later want to switch to a different encoding or add message framing, you change it once. The `try/except` in `receive_message` handles the common case where a client disconnects unexpectedly — the socket raises an exception rather than returning empty bytes.

</details>

---

## Step 5: Handle Multiple Clients with Threading

> Like a bank with multiple tellers — instead of one cashier serving customers one at a time, each customer gets their own teller the moment they walk in.

**What you're doing:** Refactor `server.accept()` into a loop, and spawn a new thread for each client so the server can handle many clients simultaneously.

**Concept:** The problem with the current code is that `recv()` **blocks** — while you're waiting for client A to send something, client B can't connect. The solution is **threading**: each client gets its own thread that independently blocks on `recv()`. The main thread's only job becomes accepting new connections in a loop. `threading.Thread(target=func, args=(conn,))` creates a new thread that will call `func(conn)`. Setting `thread.daemon = True` means the thread will be automatically killed when the main program exits — without this, your server would hang on Ctrl+C while waiting for client threads to finish. `thread.start()` actually launches the thread.

**Think about it:**
- Why does the main thread need to stay in a loop after spawning threads? What happens if the main thread exits?
- What's a "daemon thread"? Why do we want client handler threads to be daemons?

<details>
<summary>💡 Hint</summary>

```python
import threading

def handle_client(conn, addr):
    # ... receive and broadcast loop for one client

while True:
    conn, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.daemon = True   # ← dies when main thread dies
    thread.start()
```

Move all the recv/send logic into `handle_client`. The `while True` loop at the bottom just keeps accepting new connections forever.

</details>

<details>
<summary>✅ Answer</summary>

```python
# server.py — rewritten with threading

import socket
import threading

HOST = '0.0.0.0'
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(5)
print(f"Server listening on {HOST}:{PORT}")

def handle_client(conn, addr):
    """Runs in its own thread for each connected client."""
    print(f"New connection: {addr}")
    try:
        while True:
            message = conn.recv(4096)        # ← blocks, waiting for this client's message
            if not message:                  # ← empty bytes = client disconnected
                break
            print(f"[{addr}] {message.decode('utf-8')}")
            conn.send(message)               # ← echo back for now
    except:
        pass
    finally:
        conn.close()                         # ← always close socket on exit
        print(f"Disconnected: {addr}")

while True:                                  # ← main thread: just accept forever
    conn, addr = server.accept()             # ← blocks until next client connects
    thread = threading.Thread(
        target=handle_client,
        args=(conn, addr)
    )
    thread.daemon = True                     # ← killed automatically when main exits
    thread.start()                           # ← launch the thread
```

**Why this works:** Each `handle_client` call runs in its own thread, so it can block on `recv()` independently. While thread A is waiting for a message from client A, thread B is simultaneously waiting for client B — and the main thread is waiting for a brand-new client to connect. All three waits happen at the same time without any of them blocking the others.

</details>

---

## Step 6: Track Connected Clients

> Like a whiteboard at a co-working space listing who's in the building — you need a central registry so you know who to notify when something happens.

**What you're doing:** Add a global list of connected client sockets so the server knows who to broadcast to.

**Concept:** Broadcasting requires knowing every connected socket. A **global list** (`clients = []`) lets every thread see the same collection. However, threads run concurrently — if two threads try to modify the list at the same time (one adding a client, one removing a client), you can get a **race condition**: corrupted data or a crash. A `threading.Lock()` solves this: before modifying the list, a thread "acquires" the lock (blocks if another thread holds it), makes its change, then "releases" the lock. The `with lock:` syntax handles acquire and release automatically, even if an exception occurs.

**Think about it:**
- What specifically could go wrong if two threads modify a list simultaneously without a lock? Try to describe a concrete failure scenario.
- Why do we need to remove a client from the list when they disconnect? What happens if we don't?

<details>
<summary>💡 Hint</summary>

```python
clients = []
lock = threading.Lock()

# Adding a client (in handle_client, at the start)
with lock:
    clients.append(conn)

# Removing a client (in handle_client, in finally block)
with lock:
    clients.remove(conn)
```

Put these at the start and end of `handle_client`. The `with lock:` block is the key pattern.

</details>

<details>
<summary>✅ Answer</summary>

```python
# server.py — add tracking

import socket
import threading

HOST = '0.0.0.0'
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(5)

clients = []           # ← global list of all active connections
lock = threading.Lock()  # ← protects clients list from concurrent modification

def handle_client(conn, addr):
    with lock:
        clients.append(conn)  # ← register this client
    print(f"Connected: {addr} | Total clients: {len(clients)}")

    try:
        while True:
            message = conn.recv(4096)
            if not message:
                break
            print(f"[{addr}] {message.decode('utf-8')}")
    except:
        pass
    finally:
        with lock:
            clients.remove(conn)  # ← unregister on disconnect
        conn.close()
        print(f"Disconnected: {addr} | Total clients: {len(clients)}")

while True:
    conn, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.daemon = True
    thread.start()
```

**Why this works:** The `with lock:` blocks ensure only one thread touches `clients` at a time. Without the lock, imagine Thread A iterates over `clients` to broadcast while Thread B simultaneously removes an item — Thread A might try to send to a socket that no longer exists in the list, causing an index error or sending to a closed socket.

</details>

---

## Step 7: Broadcast to All Clients

> Like a PA system in a shopping mall — one announcement reaches every speaker simultaneously, and if one speaker is broken, the others still work.

**What you're doing:** Replace the echo-back with a broadcast that sends each message to every other connected client.

**Concept:** **Broadcasting** means iterating over all connected sockets and sending the message to each one, skipping the sender. The tricky part is handling clients that disconnect mid-broadcast. When you try to `send()` to a closed socket, Python raises a `BrokenPipeError` (on Unix) or `ConnectionResetError` (on Windows). Catching these exceptions per-client allows the broadcast to continue to the remaining clients even if one fails. Calling `client.close()` on the failed socket and removing it from the list during the broadcast keeps the list clean.

**Think about it:**
- Why do we skip the sender when broadcasting? What would happen if we didn't?
- If a client disconnects right as we're broadcasting, what exception do we expect? How should we handle it?

<details>
<summary>💡 Hint</summary>

```python
def broadcast(message, sender_conn):
    with lock:
        for client in clients[:]:       # ← copy the list to iterate safely
            if client != sender_conn:   # ← don't echo back to sender
                try:
                    client.send(message)
                except:
                    client.close()
                    clients.remove(client)
```

The `clients[:]` slice creates a copy — important because you might remove items during iteration.

</details>

<details>
<summary>✅ Answer</summary>

```python
# server.py — add broadcast function

import socket
import threading

HOST = '0.0.0.0'
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(5)

clients = []
lock = threading.Lock()

def broadcast(message, sender_conn):
    """Send message (bytes) to all clients except the sender."""
    with lock:
        for client in clients[:]:        # ← iterate a copy so we can remove safely
            if client is not sender_conn: # ← skip the sender
                try:
                    client.send(message) # ← send raw bytes
                except:
                    client.close()       # ← clean up broken connection
                    clients.remove(client)

def handle_client(conn, addr):
    with lock:
        clients.append(conn)

    try:
        while True:
            message = conn.recv(4096)
            if not message:
                break
            print(f"[{addr}] {message.decode('utf-8')}")
            broadcast(message, conn)     # ← send to everyone else
    except:
        pass
    finally:
        with lock:
            if conn in clients:
                clients.remove(conn)
        conn.close()

while True:
    conn, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.daemon = True
    thread.start()
```

**Why this works:** Iterating over `clients[:]` (a snapshot copy) instead of `clients` directly means that if we remove an item during the loop, the iteration continues cleanly over the original copy. Without the copy, modifying a list while iterating it causes items to be skipped.

</details>

---

## Step 8: Ask for Username on Connect

> Like a hotel check-in counter — the first thing you do when you arrive is give your name, and then everyone knows who you are for the rest of your stay.

**What you're doing:** Make the server ask each new client for a name, store it, and include it in every message. Announce when users join and leave.

**Concept:** The **username registration** pattern treats the very first message from each client as special — instead of broadcasting it, the server stores it as that client's name. A **dictionary** `{conn: name}` maps each socket to its owner's name. This is better than a list because lookup by socket is O(1). The `with lock:` guard applies to the dictionary just like the list, since multiple threads share it. When a message arrives later, you look up `clients_names[conn]` to get the sender's name and prepend it: `f"[{name}]: {message}"`.

**Think about it:**
- Why store `{conn: name}` instead of `{addr: name}`? What's the difference, and which is more reliable as a key?
- When a client disconnects, what do you need to clean up? Make a list before looking at the answer.

<details>
<summary>💡 Hint</summary>

```python
client_names = {}  # {conn: name}

# At the start of handle_client:
conn.send("Enter your name: ".encode('utf-8'))
name = conn.recv(4096).decode('utf-8').strip()

with lock:
    client_names[conn] = name

# In finally block:
with lock:
    del client_names[conn]
```

Use `broadcast(f"[{name}] joined!".encode('utf-8'), conn)` to announce the join.

</details>

<details>
<summary>✅ Answer</summary>

```python
# server.py — complete version with usernames

import socket
import threading

HOST = '0.0.0.0'
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(5)
print(f"Server listening on {HOST}:{PORT}")

clients = []
client_names = {}      # ← {conn: name} — maps socket to username
lock = threading.Lock()

def broadcast(message, sender_conn):
    """Broadcast bytes to all clients except sender."""
    with lock:
        for client in clients[:]:
            if client is not sender_conn:
                try:
                    client.send(message)
                except:
                    client.close()
                    clients.remove(client)

def handle_client(conn, addr):
    # Step 1: Get the client's name
    try:
        conn.send("Enter your name: ".encode('utf-8'))  # ← prompt for name
        name = conn.recv(4096).decode('utf-8').strip()  # ← receive name
        if not name:
            name = str(addr)                            # ← fallback if empty
    except:
        conn.close()
        return

    # Step 2: Register client
    with lock:
        clients.append(conn)
        client_names[conn] = name                       # ← store name

    print(f"{name} connected from {addr}")
    broadcast(f"*** {name} joined the chat ***\n".encode('utf-8'), conn)  # ← announce join

    # Step 3: Message loop
    try:
        while True:
            raw = conn.recv(4096)
            if not raw:
                break
            message = raw.decode('utf-8').strip()
            formatted = f"[{name}]: {message}\n"        # ← prefix with sender name
            print(formatted, end='')
            broadcast(formatted.encode('utf-8'), conn)  # ← send to everyone else
    except:
        pass
    finally:
        # Step 4: Clean up on disconnect
        with lock:
            if conn in clients:
                clients.remove(conn)
            if conn in client_names:
                del client_names[conn]                  # ← remove name entry
        conn.close()
        broadcast(f"*** {name} left the chat ***\n".encode('utf-8'), None)  # ← announce leave
        print(f"{name} disconnected")

while True:
    conn, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.daemon = True
    thread.start()
```

**Why this works:** Using `conn` (the socket object) as the dictionary key is more reliable than `addr` because two different connections from the same IP would share an `addr` but never share a `conn` object. The `finally` block guarantees cleanup even if an exception occurs mid-conversation — both the clients list and the names dict are cleaned up.

</details>

---

## Step 9: Build the Client

> Like building the phone handset — you've had the telephone exchange working for a while, but now you need something people can actually hold and talk into.

**What you're doing:** Write `client.py` — connect to the server, handle receiving and sending simultaneously using two threads.

**Concept:** The client has a **concurrency problem**: it needs to do two things at the same time — wait for the user to type something (which blocks on `input()`), and watch for incoming messages from the server (which blocks on `recv()`). The solution is the same as the server: **two threads**. Thread 1 (a daemon thread) loops on `recv()` and prints any incoming messages. Thread 2 is the main thread, which loops on `input()` and sends whatever the user types. Because the receive thread is a daemon, it will exit automatically when the main thread exits.

**Think about it:**
- The client connects to `'127.0.0.1'` (localhost). When would you change this to a different IP address?
- What should happen when the receive thread detects the server has closed the connection? How can you signal the main thread to stop?

<details>
<summary>💡 Hint</summary>

```python
import socket
import threading

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 5555))

def receive():
    while True:
        try:
            msg = client.recv(4096).decode('utf-8')
            if not msg:
                break
            print(msg, end='')
        except:
            break

thread = threading.Thread(target=receive)
thread.daemon = True
thread.start()

# Main thread: send loop
while True:
    msg = input()
    client.send(msg.encode('utf-8'))
```

</details>

<details>
<summary>✅ Answer</summary>

```python
# client.py — complete version

import socket
import threading
import sys

HOST = '127.0.0.1'  # ← server address (localhost for local testing)
PORT = 5555

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((HOST, PORT))       # ← connect to the server
except ConnectionRefusedError:
    print("Could not connect to server. Is it running?")
    sys.exit(1)

def receive():
    """Daemon thread: continuously receive and print messages from server."""
    while True:
        try:
            message = client.recv(4096)   # ← blocks until server sends something
            if not message:               # ← empty = server closed connection
                print("\nDisconnected from server.")
                break
            print(message.decode('utf-8'), end='')  # ← print without extra newline
        except:
            print("\nConnection lost.")
            break

# Start receiver thread
recv_thread = threading.Thread(target=receive)
recv_thread.daemon = True               # ← exits when main thread exits
recv_thread.start()

# Main thread: send loop
try:
    while True:
        message = input()               # ← blocks waiting for user to type + Enter
        if message:
            client.send(message.encode('utf-8'))  # ← send to server
except KeyboardInterrupt:
    pass
finally:
    client.close()                      # ← always close socket
    print("\nGoodbye!")
```

**Why this works:** The receive thread runs independently of `input()`. When you're mid-sentence typing a message, incoming messages from other clients will print above your cursor without interrupting your typing. This is a simple but functional approach — a more polished client would use a library like `curses` to manage the terminal display properly.

</details>

---

## Step 10: Graceful Disconnect

> Like a polite guest saying goodbye before leaving — you want to close connections cleanly so the host (server) knows you've left and can update the guest list.

**What you're doing:** Ensure that when a client closes (Ctrl+C or closes terminal), the server correctly detects the disconnect and removes them from the list.

**Concept:** When a TCP connection closes normally, the closing side sends a **FIN packet** and the other side receives empty bytes (`b''`) on the next `recv()` call — this is the clean case your code already handles. When a process is killed abruptly (Ctrl+C, terminal close), the OS sends a **RST packet**, which causes `recv()` to raise an exception rather than return empty bytes — this is why the `except` clause is important. On the client side, catching `KeyboardInterrupt` lets you call `client.close()` explicitly, which sends the FIN and gives the server a clean disconnect signal.

**Think about it:**
- If a client machine loses network connectivity (e.g., WiFi drops), neither a FIN nor a RST is sent. How does the server eventually find out that client is gone?
- In the broadcast function, broken clients are removed when a send fails. Is there a scenario where a dead client stays in the list for a long time?

<details>
<summary>💡 Hint</summary>

The client already handles this in the `finally` block. Key additions:

```python
# client.py — in the main loop
except KeyboardInterrupt:
    print("\nDisconnecting...")
finally:
    client.close()
```

On the server, the `finally` block in `handle_client` already handles cleanup. The key is that `recv()` returning `b''` OR raising an exception both lead to the `finally` block.

</details>

<details>
<summary>✅ Answer</summary>

```python
# client.py — final version with graceful disconnect

import socket
import threading
import sys

HOST = '127.0.0.1'
PORT = 5555

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((HOST, PORT))
except ConnectionRefusedError:
    print("Could not connect to server. Is it running?")
    sys.exit(1)

def receive():
    """Receive loop — runs as daemon thread."""
    while True:
        try:
            message = client.recv(4096)
            if not message:
                print("\nServer closed the connection.")
                sys.exit(0)              # ← exit cleanly when server disconnects
            print(message.decode('utf-8'), end='', flush=True)  # ← flush ensures immediate display
        except OSError:
            break                        # ← socket was closed by main thread

recv_thread = threading.Thread(target=receive, daemon=True)
recv_thread.start()

try:
    while True:
        message = input()
        if not message:
            continue                     # ← ignore empty Enter presses
        client.send(message.encode('utf-8'))
except (KeyboardInterrupt, EOFError):    # ← EOFError handles terminal close
    print("\nDisconnecting...")
finally:
    try:
        client.close()                   # ← sends FIN to server
    except:
        pass
```

**Why this works:** `flush=True` in the receive thread ensures messages print immediately even without a newline — otherwise Python might buffer output. `EOFError` covers the case where stdin is closed (e.g., the terminal window closes), which is different from Ctrl+C. Both lead to the same `finally` cleanup.

</details>

---

## Step 11: Test It

> Like a fire drill — you need to run the whole system for real to find out what actually breaks.

**What you're doing:** Run the server and multiple clients, verify the chat works end-to-end, and understand what you should see.

**Concept:** Testing a networked application requires multiple terminal windows running simultaneously. Each `client.py` process is an independent client — they don't share memory or variables, they communicate only through the server. When you type in one client terminal and see it appear in another, that message traveled: your input → `client.send()` → TCP → `server.recv()` → `broadcast()` → TCP → `client.recv()` → `print()` in the other terminal.

**Think about it:**
- What order must you start things in? Can you start a client before the server?
- What output do you expect to see in the server terminal when two clients are connected?

<details>
<summary>💡 Hint</summary>

Open three terminal windows. Start the server first, then each client:

```bash
# Terminal 1
python server.py

# Terminal 2
python client.py

# Terminal 3
python client.py
```

Watch all three terminals as you type in terminals 2 and 3.

</details>

<details>
<summary>✅ Answer</summary>

```bash
# Terminal 1 — Start the server
python server.py
# Expected output:
# Server listening on 0.0.0.0:5555
```

```bash
# Terminal 2 — First client
python client.py
# Server prompts: Enter your name:
# Type: Alice
# Expected: nothing yet (waiting for messages)
```

```bash
# Terminal 3 — Second client
python client.py
# Server prompts: Enter your name:
# Type: Bob
# Expected in Terminal 2: *** Bob joined the chat ***
```

```bash
# Terminal 2 — Alice sends a message
# Type: Hello Bob!
# Expected in Terminal 3: [Alice]: Hello Bob!
# Expected in Terminal 1 (server): [Alice]: Hello Bob!
```

```bash
# Terminal 3 — Bob replies
# Type: Hey Alice!
# Expected in Terminal 2: [Bob]: Hey Alice!
```

```bash
# Terminal 3 — Bob disconnects (Ctrl+C)
# Expected in Terminal 2: *** Bob left the chat ***
# Expected in Terminal 1: Bob disconnected
```

**Server terminal expected output:**
```
Server listening on 0.0.0.0:5555
Alice connected from ('127.0.0.1', 52341)
Bob connected from ('127.0.0.1', 52342)
[Alice]: Hello Bob!
[Bob]: Hey Alice!
Bob disconnected
```

**Why this works:** Each message flows from sender → server → all other clients. The server is the single point of coordination — clients never communicate directly with each other. This is the **hub-and-spoke** architecture.

</details>

---

## What You Built

```
                    ┌─────────────────────────────┐
                    │         server.py           │
                    │                             │
                    │  clients = [conn_A, conn_B, │
                    │             conn_C]         │
                    │                             │
                    │  handle_client() × 3        │
                    │  (one thread per client)    │
                    │                             │
                    │  broadcast() → all others   │
                    └──────┬──────────┬───────────┘
                           │          │
              TCP           │          │           TCP
    ┌──────────────────────┘          └────────────────────────┐
    │                                                          │
┌───┴────────┐                                        ┌────────┴───┐
│ client.py  │                                        │ client.py  │
│  (Alice)   │                                        │   (Bob)    │
│            │                                        │            │
│ recv thread│                                        │ recv thread│
│ main thread│                                        │ main thread│
│  (input)   │                                        │  (input)   │
└────────────┘                                        └────────────┘
```

Alice types → server receives → broadcasts to Bob (and any others)
Bob types → server receives → broadcasts to Alice (and any others)

## What You Learned

- **TCP sockets** — reliable, ordered, connection-based communication using `socket.socket(AF_INET, SOCK_STREAM)`
- **Blocking I/O** — `accept()`, `recv()`, and `input()` all block the current thread until data arrives
- **Threading** — spawning threads per connection to handle multiple clients simultaneously without blocking
- **Daemon threads** — background threads that exit automatically when the main thread exits
- **Thread safety** — using `threading.Lock()` to protect shared data structures from concurrent modification
- **Broadcast pattern** — iterating over all connections to relay a message to every connected peer
- **Encode/decode** — sockets transmit bytes; always `.encode('utf-8')` before sending and `.decode('utf-8')` after receiving
- **Graceful cleanup** — using `try/finally` to guarantee socket cleanup and list removal even on unexpected disconnect

## Extend It (Optional)

- Add `/quit` command to disconnect cleanly
- Add private messaging: `/msg [name] [message]`
- Add a `/list` command showing all connected users
- Persist chat history to a file using `open()` and appending each message
- Add timestamps to each message: `[14:32] [Alice]: Hello`
- Handle the case where two clients try to use the same username
