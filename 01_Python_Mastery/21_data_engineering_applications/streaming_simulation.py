"""
21_data_engineering_applications/streaming_simulation.py
==========================================================
CONCEPT: Streaming data processing — handling continuous, unbounded data
streams as events arrive in real time.
WHY THIS MATTERS: Modern data systems (Kafka, Kinesis, Flink, Spark Streaming)
process data as it arrives rather than in batches. The patterns here — windowed
aggregations, event time processing, stateful streaming — are the foundations
of all stream processing frameworks.

Prerequisite: Modules 01–13 (generators, threading, asyncio concepts, OOP)
"""

import time
import random
import threading
import queue
import json
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Iterator, Callable, Any

# =============================================================================
# SECTION 1: Event stream simulation — continuous data generation
# =============================================================================

print("=== Section 1: Event Stream Generator ===")


@dataclass
class Event:
    """Represents a single event in the stream."""
    event_id:   str
    event_type: str
    user_id:    int
    value:      float
    timestamp:  float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "event_id":   self.event_id,
            "event_type": self.event_type,
            "user_id":    self.user_id,
            "value":      round(self.value, 2),
            "timestamp":  self.timestamp,
        }


def event_stream(events_per_second: float = 10.0,
                 total_events: int = 50) -> Iterator[Event]:
    """
    Generator that simulates a real-time event stream.
    Yields events at `events_per_second` rate until `total_events` emitted.
    In production: replace with kafka-python consumer, kinesis client, etc.
    """
    event_types = ["page_view", "click", "purchase", "search", "error"]
    delay = 1.0 / events_per_second

    for i in range(total_events):
        yield Event(
            event_id   = f"evt_{i+1:05d}",
            event_type = random.choice(event_types),
            user_id    = random.randint(1, 20),
            value      = random.uniform(0, 100),
            timestamp  = time.time(),
        )
        time.sleep(delay)


# Generate a small burst of events (fast for demo)
events = list(event_stream(events_per_second=1000, total_events=30))
type_counts = defaultdict(int)
for e in events:
    type_counts[e.event_type] += 1

print(f"  Generated {len(events)} events:")
for etype, count in sorted(type_counts.items()):
    print(f"    {etype:12}: {count:3} events")


# =============================================================================
# SECTION 2: Tumbling window aggregation
# =============================================================================

# CONCEPT: A TUMBLING WINDOW groups events into non-overlapping fixed-size
# time buckets. Events in bucket [t, t+window) are aggregated together.
# Window closes at t+window — results are finalized.
# Use for: per-minute/per-hour summaries, batch-style analytics on streams.

print("\n=== Section 2: Tumbling Window Aggregation ===")


class TumblingWindow:
    """
    Groups stream events into non-overlapping time windows.
    window_size: bucket duration in seconds.
    """

    def __init__(self, window_size: float):
        self.window_size = window_size
        self._buckets: dict = {}   # window_start → list of events

    def _window_key(self, timestamp: float) -> float:
        """Map a timestamp to the start of its window bucket."""
        return (timestamp // self.window_size) * self.window_size

    def add(self, event: Event) -> None:
        key = self._window_key(event.timestamp)
        if key not in self._buckets:
            self._buckets[key] = []
        self._buckets[key].append(event)

    def get_closed_windows(self, current_time: float) -> list[tuple[float, list]]:
        """
        Return all windows that ended before current_time.
        These windows are "closed" — no more events will arrive in them.
        """
        closed = []
        cutoff = self._window_key(current_time)

        for key in sorted(self._buckets.keys()):
            if key < cutoff:
                closed.append((key, self._buckets.pop(key)))

        return closed

    def aggregate_window(self, window_start: float, window_events: list) -> dict:
        """Aggregate all events in one closed window."""
        if not window_events:
            return {}

        event_type_counts = defaultdict(int)
        for e in window_events:
            event_type_counts[e.event_type] += 1

        return {
            "window_start":  window_start,
            "window_end":    window_start + self.window_size,
            "total_events":  len(window_events),
            "unique_users":  len({e.user_id for e in window_events}),
            "total_value":   round(sum(e.value for e in window_events), 2),
            "avg_value":     round(sum(e.value for e in window_events) / len(window_events), 2),
            "event_types":   dict(event_type_counts),
        }


# Assign artificial timestamps spread over 3 seconds to demo windowing
window = TumblingWindow(window_size=1.0)   # 1-second buckets
base_time = time.time()
for i, event in enumerate(events):
    event.timestamp = base_time + i * 0.1   # spread 30 events over 3 seconds
    window.add(event)

# Process closed windows (simulate time advancing)
current = base_time + 3.5   # "now" is 3.5s into the stream
closed  = window.get_closed_windows(current)
print(f"  {len(closed)} closed 1-second windows:")
for ts, window_events in closed:
    agg = window.aggregate_window(ts, window_events)
    print(f"    [{agg['total_events']:2} events | "
          f"{agg['unique_users']} users | "
          f"avg_value={agg['avg_value']:.1f}]")


# =============================================================================
# SECTION 3: Sliding window — rolling metrics
# =============================================================================

# CONCEPT: SLIDING WINDOW keeps a rolling buffer of the last N seconds/events.
# Unlike tumbling windows, it moves forward with each new event.
# Use for: real-time dashboards, anomaly detection, moving averages.

print("\n=== Section 3: Sliding Window (Rolling Metrics) ===")


class SlidingWindowMetrics:
    """
    Maintains rolling statistics over the last `window_seconds`.
    Automatically evicts events older than the window.
    """

    def __init__(self, window_seconds: float):
        self.window_seconds = window_seconds
        self._events: deque = deque()

    def add(self, event: Event) -> None:
        self._events.append(event)
        self._evict_old(event.timestamp)

    def _evict_old(self, current_time: float) -> None:
        """Remove events outside the window."""
        cutoff = current_time - self.window_seconds
        while self._events and self._events[0].timestamp < cutoff:
            self._events.popleft()

    def snapshot(self) -> dict:
        """Current window statistics."""
        if not self._events:
            return {"count": 0, "avg_value": 0.0, "unique_users": 0}

        return {
            "count":        len(self._events),
            "avg_value":    round(sum(e.value for e in self._events) / len(self._events), 2),
            "unique_users": len({e.user_id for e in self._events}),
            "event_types":  dict(
                (k, sum(1 for e in self._events if e.event_type == k))
                for k in {e.event_type for e in self._events}
            ),
        }


slider = SlidingWindowMetrics(window_seconds=1.5)
print("  Sliding 1.5s window — snapshot every 10 events:")
for i, event in enumerate(events[:30]):
    slider.add(event)
    if (i + 1) % 10 == 0:
        snap = slider.snapshot()
        print(f"  After event {i+1:2}: window_size={snap['count']:2}, "
              f"avg={snap['avg_value']:5.1f}, users={snap['unique_users']}")


# =============================================================================
# SECTION 4: Stateful stream processing — per-user aggregation
# =============================================================================

# CONCEPT: Many streaming use cases require per-key state (e.g., per-user
# session tracking, per-device running totals). State is maintained in memory
# (or in an external store for distributed systems).
# This pattern underlies Kafka Streams, Flink stateful functions, etc.

print("\n=== Section 4: Stateful Per-User Processing ===")


class UserSessionTracker:
    """
    Tracks per-user session state from the event stream.
    Each user gets their own running aggregate — state persists across events.
    """

    def __init__(self, session_timeout: float = 2.0):
        self.session_timeout = session_timeout
        self._state: dict = {}   # user_id → session state

    def process(self, event: Event) -> dict:
        """Update state for the user who triggered this event."""
        uid = event.user_id
        now = event.timestamp

        if uid not in self._state or now - self._state[uid]["last_seen"] > self.session_timeout:
            # New session
            self._state[uid] = {
                "session_id":    f"sess_{uid}_{int(now)}",
                "user_id":       uid,
                "session_start": now,
                "last_seen":     now,
                "event_count":   0,
                "total_value":   0.0,
            }

        state = self._state[uid]
        state["last_seen"]   = now
        state["event_count"] += 1
        state["total_value"] += event.value
        return dict(state)

    def active_sessions(self, current_time: float) -> list:
        """Return all sessions active within session_timeout."""
        return [
            s for s in self._state.values()
            if current_time - s["last_seen"] <= self.session_timeout
        ]

    def finalized_sessions(self, current_time: float) -> list:
        """Return and remove timed-out sessions (for downstream writing)."""
        timed_out = [
            s for s in self._state.values()
            if current_time - s["last_seen"] > self.session_timeout
        ]
        for s in timed_out:
            del self._state[s["user_id"]]
        return timed_out


tracker = UserSessionTracker(session_timeout=0.5)

# Process events
for event in events[:20]:
    tracker.process(event)

current = events[19].timestamp + 0.1
active  = tracker.active_sessions(current)
print(f"  Active sessions after 20 events: {len(active)}")
for s in sorted(active, key=lambda x: x["user_id"])[:5]:
    print(f"    user_{s['user_id']:2}: {s['event_count']} events, "
          f"value={s['total_value']:.1f}")


# =============================================================================
# SECTION 5: Producer/consumer streaming with a Queue
# =============================================================================

# CONCEPT: Real streaming systems separate producers (who generate events)
# from consumers (who process them) via a queue (Kafka, SQS, RabbitMQ).
# This decouples rates and enables parallel consumption.

print("\n=== Section 5: Producer/Consumer Stream ===")


def stream_producer(q: queue.Queue, n_events: int) -> None:
    """Generate events and put them on the queue."""
    event_types = ["view", "click", "buy"]
    for i in range(n_events):
        evt = Event(
            event_id   = f"e_{i+1:04d}",
            event_type = random.choice(event_types),
            user_id    = random.randint(1, 10),
            value      = round(random.uniform(1, 100), 2),
        )
        q.put(evt)
        time.sleep(0.002)   # 500 events/sec
    q.put(None)   # sentinel: signals consumer to stop


def stream_consumer(q: queue.Queue, worker_id: int, results: list) -> None:
    """Consume events, aggregate per event_type."""
    agg = defaultdict(float)
    count = 0
    while True:
        try:
            evt = q.get(timeout=1.0)
        except queue.Empty:
            break

        if evt is None:
            q.put(None)   # re-queue for other consumers
            break

        agg[evt.event_type] += evt.value
        count += 1

    results.append({"worker": worker_id, "events": count, "agg": dict(agg)})


results = []
event_queue = queue.Queue(maxsize=50)   # back-pressure: producer blocks if full

producer = threading.Thread(target=stream_producer, args=(event_queue, 30))
consumer = threading.Thread(target=stream_consumer, args=(event_queue, 1, results))

start = time.perf_counter()
producer.start()
consumer.start()
producer.join()
consumer.join()
elapsed = time.perf_counter() - start

r = results[0]
print(f"  Processed {r['events']} events in {elapsed*1000:.1f}ms")
print(f"  Aggregated by type:")
for etype, total in sorted(r["agg"].items()):
    print(f"    {etype:6}: total_value={total:.2f}")


print("\n=== Streaming simulation complete ===")
print("Stream processing patterns:")
print("  Event generator  → simulate or consume real Kafka/Kinesis stream")
print("  Tumbling window  → non-overlapping buckets, periodic summaries")
print("  Sliding window   → rolling N-second metrics, anomaly detection")
print("  Stateful per-key → session tracking, per-user aggregation")
print("  Queue pipeline   → decouple producer/consumer rates with back-pressure")
