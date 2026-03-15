# Queue — Real-World Usage

Queues are the nervous system of distributed systems. Every web server, printer,
CPU scheduler, and message broker is fundamentally a queue with extra logic around
it. Here is where the FIFO principle shows up in production.

---

## 1. Web Server Request Queue — Buffering HTTP Requests

When traffic spikes hit a web server (think a product launch or a viral post), the
server cannot process all requests simultaneously. Incoming HTTP connections are
buffered in a queue. Worker threads pull from the queue at a steady rate. This is
what Gunicorn (Python WSGI server), uWSGI, and Nginx all do internally.

`queue.Queue` in Python is thread-safe and uses locks + condition variables under
the hood — the same primitives that production request queues use.

```python
import queue
import threading
import time
import random
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class HttpRequest:
    request_id: int
    method: str
    path: str
    arrived_at: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        return f"[{self.request_id:04d}] {self.method} {self.path}"


def producer(request_queue: queue.Queue, num_requests: int, arrival_rate: float) -> None:
    """
    Simulates HTTP requests arriving (like nginx's accept() loop).
    arrival_rate: average requests per second.
    """
    for i in range(num_requests):
        req = HttpRequest(
            request_id=i,
            method=random.choice(["GET", "GET", "GET", "POST"]),  # GET-heavy, realistic
            path=random.choice(["/api/users", "/api/products", "/health", "/api/orders"]),
        )
        request_queue.put(req)
        time.sleep(1.0 / arrival_rate * random.uniform(0.5, 1.5))  # Poisson-like arrivals
    print("  [producer] All requests enqueued.")


def worker(worker_id: int, request_queue: queue.Queue, results: list) -> None:
    """
    Simulates a Gunicorn worker thread processing requests.
    Each request takes a variable amount of time (DB query, business logic).
    """
    while True:
        try:
            req = request_queue.get(timeout=2.0)  # block up to 2s for a request
        except queue.Empty:
            break   # no more work — worker shuts down

        # Simulate processing time: 50–200ms per request
        processing_ms = random.randint(50, 200)
        time.sleep(processing_ms / 1000)

        latency_ms = (datetime.now() - req.arrived_at).total_seconds() * 1000
        results.append(latency_ms)
        print(f"  [worker-{worker_id}] {req}  processed in {processing_ms}ms  "
              f"queued for {latency_ms:.0f}ms total")
        request_queue.task_done()


request_queue: queue.Queue = queue.Queue(maxsize=50)  # backlog capped at 50
results: list[float] = []

# 3 worker threads (like Gunicorn: `--workers 3`)
NUM_WORKERS = 3
workers = [
    threading.Thread(target=worker, args=(i, request_queue, results), daemon=True)
    for i in range(NUM_WORKERS)
]
for w in workers:
    w.start()

# Producer: 15 requests arriving at ~10 req/s
producer_thread = threading.Thread(
    target=producer, args=(request_queue, 15, 10.0)
)
producer_thread.start()
producer_thread.join()
request_queue.join()   # wait for all requests to be processed

for w in workers:
    w.join()

if results:
    print(f"\n  Average end-to-end latency: {sum(results)/len(results):.0f}ms")
    print(f"  Max latency (queue depth):  {max(results):.0f}ms")
```

---

## 2. Print Queue — FIFO Spooler

Every OS print spooler (Windows Print Spooler, CUPS on Linux/macOS) uses a FIFO
queue. Jobs are accepted immediately (so the user's application is not blocked) and
printed in order. This decouples the fast producer (user clicking "Print") from the
slow consumer (the printer).

```python
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from queue import Queue
from typing import Optional


@dataclass
class PrintJob:
    job_id: int
    document_name: str
    pages: int
    submitted_by: str
    submitted_at: datetime = field(default_factory=datetime.now)


class PrintQueue:
    """
    FIFO print spooler.
    Mirrors: CUPS (Common Unix Printing System), Windows Print Spooler.
    """

    def __init__(self, printer_name: str):
        self.printer_name = printer_name
        self._queue: Queue[PrintJob] = Queue()
        self._job_counter = 0
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def add_job(self, document_name: str, pages: int, submitted_by: str) -> int:
        self._job_counter += 1
        job = PrintJob(self._job_counter, document_name, pages, submitted_by)
        self._queue.put(job)
        print(f"  Queued job #{job.job_id}: '{document_name}' ({pages}p) by {submitted_by}")
        return job.job_id

    def _print_loop(self) -> None:
        while self._running or not self._queue.empty():
            try:
                job = self._queue.get(timeout=0.5)
            except Exception:
                continue

            print(f"  Printing job #{job.job_id}: '{job.document_name}' "
                  f"({job.pages} pages) — started")
            time.sleep(job.pages * 0.1)   # 100ms per page
            print(f"  Printing job #{job.job_id}: done.  "
                  f"Queue depth: {self._queue.qsize()}")
            self._queue.task_done()

    def start_printer(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._print_loop, daemon=True)
        self._thread.start()

    def stop_printer(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join()


printer = PrintQueue("HP LaserJet Pro")
printer.start_printer()

printer.add_job("Q4 Financial Report.pdf",  45, "alice")
printer.add_job("Meeting Agenda.docx",       2, "bob")
printer.add_job("Architecture Diagram.pdf",  8, "carol")

time.sleep(1.5)
printer.add_job("Quick Note.txt",            1, "alice")  # arrives while others printing

printer.stop_printer()
```

---

## 3. BFS in Social Networks — Degrees of Separation

LinkedIn's "2nd connection" and Facebook's "People You May Know" are implemented
with Breadth-First Search over a friend graph. BFS uses a queue: start from the
source node, enqueue all neighbors, then their neighbors, stopping when the target
is found or the desired depth is reached.

BFS guarantees the shortest path in an unweighted graph — which is exactly what
"degrees of separation" means.

```python
from collections import deque
from typing import Dict, List, Optional


def find_shortest_path(
    graph: Dict[str, List[str]],
    source: str,
    target: str,
) -> Optional[List[str]]:
    """
    BFS to find the shortest friendship chain between two people.
    Returns the path [source, ..., target] or None if not connected.

    Used by: LinkedIn (degree of connection), Facebook (friend suggestions),
             Twitter (follow recommendations).
    """
    if source == target:
        return [source]

    # Queue holds (current_node, path_to_here)
    queue: deque[tuple[str, List[str]]] = deque()
    queue.append((source, [source]))
    visited = {source}

    while queue:
        current, path = queue.popleft()

        for neighbor in graph.get(current, []):
            if neighbor in visited:
                continue
            new_path = path + [neighbor]
            if neighbor == target:
                return new_path
            visited.add(neighbor)
            queue.append((neighbor, new_path))

    return None   # not connected


def degrees_of_separation(path: Optional[List[str]]) -> str:
    if path is None:
        return "Not connected"
    n = len(path) - 1
    if n == 1: return "1st connection (direct)"
    if n == 2: return "2nd connection"
    return f"{n}th connection"


# Social graph (undirected — each edge added both ways)
connections: Dict[str, List[str]] = {
    "Alice":   ["Bob", "Carol", "Dave"],
    "Bob":     ["Alice", "Eve", "Frank"],
    "Carol":   ["Alice", "Grace"],
    "Dave":    ["Alice"],
    "Eve":     ["Bob", "Heidi"],
    "Frank":   ["Bob", "Ivan"],
    "Grace":   ["Carol", "Ivan"],
    "Heidi":   ["Eve"],
    "Ivan":    ["Frank", "Grace", "Judy"],
    "Judy":    ["Ivan"],
}

pairs = [
    ("Alice", "Ivan"),
    ("Alice", "Judy"),
    ("Heidi", "Judy"),
    ("Dave",  "Heidi"),
]

for src, dst in pairs:
    path = find_shortest_path(connections, src, dst)
    deg  = degrees_of_separation(path)
    chain = " → ".join(path) if path else "no path"
    print(f"  {src} → {dst}: {deg}")
    print(f"    Path: {chain}\n")
```

---

## 4. Round-Robin Process Scheduling — Circular Queue

Every OS kernel (Linux, Windows, macOS) uses a variant of round-robin scheduling
for CPU time slices. Each process gets a fixed quantum (e.g., 10ms on Linux). When
the quantum expires, the process goes to the back of the queue and the next process
runs. A circular queue models this naturally.

```python
from collections import deque
from dataclasses import dataclass


@dataclass
class Process:
    pid: int
    name: str
    burst_time: int      # total CPU time needed (ms)
    remaining: int = 0

    def __post_init__(self):
        self.remaining = self.burst_time


class RoundRobinScheduler:
    """
    Simplified OS round-robin scheduler.
    Used by: Linux CFS (Completely Fair Scheduler) inspiration,
             Windows thread scheduler, JVM thread scheduler.
    """

    def __init__(self, quantum_ms: int):
        self.quantum = quantum_ms
        self._queue: deque[Process] = deque()
        self._time = 0

    def add_process(self, pid: int, name: str, burst_time: int) -> None:
        self._queue.append(Process(pid, name, burst_time))

    def run(self) -> None:
        total_processes = len(self._queue)
        waiting_time = {p.pid: 0 for p in self._queue}
        arrival = {p.pid: 0 for p in self._queue}   # all arrive at t=0

        print(f"Scheduler: quantum={self.quantum}ms, processes={total_processes}\n")
        print(f"  {'Time':>6}  {'PID':<5} {'Process':<15} {'Remaining':>10}  {'Status'}")
        print("  " + "-" * 55)

        completed = 0
        while self._queue:
            proc = self._queue.popleft()   # deque as circular queue

            run_for = min(self.quantum, proc.remaining)
            proc.remaining -= run_for
            self._time += run_for

            status = "DONE" if proc.remaining == 0 else "preempted"
            print(f"  {self._time:>6}  {proc.pid:<5} {proc.name:<15} "
                  f"{proc.remaining:>10}ms  {status}")

            if proc.remaining > 0:
                self._queue.append(proc)   # back of the queue
            else:
                completed += 1
                turnaround = self._time - arrival[proc.pid]
                waiting_time[proc.pid] = turnaround - proc.burst_time

        avg_wait = sum(waiting_time.values()) / total_processes
        print(f"\n  All {completed} processes complete at t={self._time}ms")
        print(f"  Average waiting time: {avg_wait:.1f}ms")


scheduler = RoundRobinScheduler(quantum_ms=20)
scheduler.add_process(1, "nginx-worker",   burst_time=50)
scheduler.add_process(2, "postgres-bg",    burst_time=30)
scheduler.add_process(3, "python-app",     burst_time=80)
scheduler.add_process(4, "redis-aof",      burst_time=20)
scheduler.run()
```

---

## 5. Rate Limiting — Token Bucket with a Sliding Window Deque

Rate limiting is how APIs protect themselves from abuse and enforce fair usage.
GitHub, Stripe, and Twilio all use it. The sliding window algorithm keeps a deque
of request timestamps; on each request, expired timestamps are popped from the left,
and the deque's length tells you how many requests happened in the window.

```python
import time
from collections import deque
from typing import Tuple


class RateLimiter:
    """
    Sliding window rate limiter using a deque of timestamps.
    Each entry is the Unix timestamp of a request.

    Used by: GitHub API (5000 req/hr), Stripe API, Twilio, AWS API Gateway.
    The deque's popleft() removes expired timestamps in O(1) amortised.
    """

    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests = max_requests
        self.window = window_seconds
        self._timestamps: deque[float] = deque()

    def is_allowed(self, user_id: str) -> Tuple[bool, int]:
        """
        Returns (allowed, requests_remaining).
        Call this before processing each API request.
        """
        now = time.monotonic()

        # Remove timestamps outside the sliding window
        while self._timestamps and self._timestamps[0] < now - self.window:
            self._timestamps.popleft()

        if len(self._timestamps) < self.max_requests:
            self._timestamps.append(now)
            remaining = self.max_requests - len(self._timestamps)
            return True, remaining
        else:
            return False, 0

    def reset_in(self) -> float:
        """Seconds until the oldest request falls outside the window."""
        if not self._timestamps:
            return 0.0
        now = time.monotonic()
        return max(0.0, self._timestamps[0] + self.window - now)


# Simulate an API endpoint with limit: 5 requests per 2 seconds
limiter = RateLimiter(max_requests=5, window_seconds=2.0)

print("Simulating 8 rapid API requests:")
for i in range(8):
    allowed, remaining = limiter.is_allowed("user-42")
    status = "ALLOWED" if allowed else f"RATE LIMITED (retry in {limiter.reset_in():.2f}s)"
    print(f"  Request {i+1}: {status}  remaining={remaining}")
    time.sleep(0.1)   # 100ms between requests — faster than rate limit allows

print("\nWaiting 2 seconds for window to reset...")
time.sleep(2.1)

allowed, remaining = limiter.is_allowed("user-42")
print(f"  Request after wait: {'ALLOWED' if allowed else 'RATE LIMITED'}  remaining={remaining}")
```

---

## 6. Message Queue Systems — Publish/Subscribe (Kafka Concept)

Apache Kafka, RabbitMQ, AWS SQS, and Google Pub/Sub are all fundamentally ordered
queues with publish/subscribe semantics. Producers write messages to a topic (queue);
multiple consumer groups independently read from the queue at their own pace,
tracking their position with an offset.

This decouples services so that a slow consumer does not block a fast producer —
the queue buffers the difference.

```python
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict, List, Optional


@dataclass
class Message:
    offset: int
    topic: str
    payload: dict
    published_at: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        return f"[offset={self.offset}] {self.topic}: {self.payload}"


class Topic:
    """
    An append-only log of messages (like a Kafka partition).
    Consumers track their own offset independently.
    """

    def __init__(self, name: str, retention: int = 1000):
        self.name = name
        self._log: List[Message] = []
        self._retention = retention
        self._next_offset = 0

    def publish(self, payload: dict) -> Message:
        msg = Message(offset=self._next_offset, topic=self.name, payload=payload)
        self._log.append(msg)
        self._next_offset += 1
        # Enforce retention (Kafka has time/size-based retention)
        if len(self._log) > self._retention:
            self._log.pop(0)
        return msg

    def consume(self, from_offset: int, max_messages: int = 10) -> List[Message]:
        """Return up to max_messages starting from from_offset."""
        start = from_offset - (self._next_offset - len(self._log))
        start = max(start, 0)
        return self._log[start:start + max_messages]

    @property
    def latest_offset(self) -> int:
        return self._next_offset


class MessageBus:
    """
    Simple in-memory message bus with topics and consumer groups.
    Concept mirrors: Apache Kafka, AWS SQS/SNS, Google Pub/Sub, RabbitMQ.
    """

    def __init__(self):
        self._topics: Dict[str, Topic] = {}
        self._consumer_offsets: Dict[str, Dict[str, int]] = {}   # group → topic → offset

    def create_topic(self, name: str) -> Topic:
        self._topics[name] = Topic(name)
        return self._topics[name]

    def publish(self, topic_name: str, payload: dict) -> Message:
        if topic_name not in self._topics:
            self.create_topic(topic_name)
        return self._topics[topic_name].publish(payload)

    def subscribe(self, group: str, topic_name: str, from_beginning: bool = False) -> None:
        """Register a consumer group for a topic."""
        if group not in self._consumer_offsets:
            self._consumer_offsets[group] = {}
        topic = self._topics.get(topic_name)
        if topic:
            start = 0 if from_beginning else topic.latest_offset
            self._consumer_offsets[group][topic_name] = start

    def poll(self, group: str, topic_name: str, max_messages: int = 5) -> List[Message]:
        """Fetch unread messages for a consumer group."""
        offset = self._consumer_offsets.get(group, {}).get(topic_name, 0)
        topic  = self._topics.get(topic_name)
        if not topic:
            return []
        messages = topic.consume(from_offset=offset, max_messages=max_messages)
        if messages:
            # Advance the committed offset (like Kafka's consumer.commitSync())
            self._consumer_offsets[group][topic_name] = messages[-1].offset + 1
        return messages


# --- Demo: e-commerce order pipeline ---
bus = MessageBus()
bus.create_topic("orders")

# Subscribe two independent consumer groups BEFORE publishing
bus.subscribe("inventory-service", "orders", from_beginning=True)
bus.subscribe("email-service",     "orders", from_beginning=True)

# Producer: order-service publishes events
print("=== Publishing order events ===")
for order_id, product, qty in [(1001, "MacBook Pro", 1), (1002, "AirPods", 2), (1003, "iPad", 1)]:
    msg = bus.publish("orders", {"order_id": order_id, "product": product, "qty": qty, "status": "created"})
    print(f"  Published: {msg}")

print("\n=== inventory-service consuming ===")
for msg in bus.poll("inventory-service", "orders", max_messages=10):
    print(f"  Reserve stock for order {msg.payload['order_id']}: "
          f"{msg.payload['qty']}x {msg.payload['product']}")

print("\n=== email-service consuming (independently, same messages) ===")
for msg in bus.poll("email-service", "orders", max_messages=10):
    print(f"  Send confirmation for order {msg.payload['order_id']} — {msg.payload['product']}")

print("\n=== New order arrives after consumers already ran ===")
bus.publish("orders", {"order_id": 1004, "product": "iPhone 15", "qty": 1, "status": "created"})

print("\n=== inventory-service polls again (only gets new message) ===")
for msg in bus.poll("inventory-service", "orders", max_messages=10):
    print(f"  Reserve stock for order {msg.payload['order_id']}: {msg.payload['product']}")

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [Common Mistakes →](./common_mistakes.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
