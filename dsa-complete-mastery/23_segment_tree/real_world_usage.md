# Segment Tree — Real-World Usage Guide

A segment tree is a binary tree built over an array where each node stores an aggregate value
(sum, min, max, count) for a contiguous subarray. Queries and updates both run in O(log n) time.
This guide shows six real-world applications with full Python implementations, explains why a
naive approach fails at scale, and compares the segment tree against alternatives.

---

## Why Segment Trees Matter in Production

The naive approach to range queries is a loop over the range: O(n) per query. At scale this
breaks down immediately:

- Financial system: 10,000 trades/second, 100 analysts each issuing 50 range queries/second
  → 5,000 queries/second × O(n) → unacceptable latency at n = 100,000 data points
- Game leaderboard: 1,000,000 players, 10,000 rank-range queries/second → O(n) is unusable

The segment tree brings every query and point update to O(log n), making these systems viable.

---

## Application 1 — Range Sum Queries in Financial Systems

### The Problem

A trading system records (timestamp, volume) pairs. Analysts need to answer: "What was the
total trading volume between time T1 and T2?" Timestamps are discretized into time slots
(e.g., 1-second buckets). Updates happen continuously as trades arrive. Queries arrive
simultaneously from multiple analysts.

### Why Segment Tree?

- Prefix sum array gives O(1) queries but O(n) updates (rebuild prefix sums after each trade).
- Segment tree gives O(log n) for both updates and queries — ideal for mixed workload.

### Implementation

```python
class TradingVolumeTracker:
    """
    Tracks trading volume per time slot and answers range sum queries.

    Time complexity:
        - add_trade: O(log n)
        - query_volume: O(log n)
    Space complexity: O(n)
    """

    def __init__(self, num_slots: int):
        """
        num_slots: number of time slots (e.g., 86400 for seconds in a day,
                   6.5 * 3600 = 23400 for a trading day in seconds)
        """
        self.n = num_slots
        self.tree = [0] * (4 * num_slots)  # 4n is safe upper bound for segment tree size

    def _update(self, node: int, start: int, end: int, idx: int, volume: int) -> None:
        """Internal: add volume at position idx."""
        if start == end:
            self.tree[node] += volume  # leaf node: accumulate volume
            return
        mid = (start + end) // 2
        if idx <= mid:
            self._update(2 * node, start, mid, idx, volume)
        else:
            self._update(2 * node + 1, mid + 1, end, idx, volume)
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def _query(self, node: int, start: int, end: int, left: int, right: int) -> int:
        """Internal: sum of volumes in [left, right]."""
        if right < start or end < left:
            return 0  # completely outside query range
        if left <= start and end <= right:
            return self.tree[node]  # completely inside query range
        mid = (start + end) // 2
        left_sum = self._query(2 * node, start, mid, left, right)
        right_sum = self._query(2 * node + 1, mid + 1, end, left, right)
        return left_sum + right_sum

    def add_trade(self, time_slot: int, volume: int) -> None:
        """
        Record a trade at a specific time slot.

        time_slot: integer index 0..n-1 (e.g., seconds since market open)
        volume:    number of shares traded
        """
        if not (0 <= time_slot < self.n):
            raise ValueError(f"time_slot {time_slot} out of range [0, {self.n - 1}]")
        self._update(1, 0, self.n - 1, time_slot, volume)

    def query_volume(self, start: int, end: int) -> int:
        """
        Return total trading volume between time slots [start, end] inclusive.

        start, end: integer time slot indices, 0-indexed
        """
        if start > end:
            raise ValueError("start must be <= end")
        start = max(0, start)
        end = min(self.n - 1, end)
        return self._query(1, 0, self.n - 1, start, end)

    def get_volume_at(self, time_slot: int) -> int:
        """Return volume at a specific time slot."""
        return self.query_volume(time_slot, time_slot)


# Example usage: NYSE trading day (9:30 AM to 4:00 PM = 23400 seconds)
def demo_trading():
    tracker = TradingVolumeTracker(num_slots=23400)

    # Simulate trades arriving throughout the day
    # (time_slot = seconds since 9:30:00 AM)
    trades = [
        (0,     5000),    # 9:30:00 AM — opening rush
        (0,    12000),    # 9:30:00 AM — more opening volume
        (1,     3000),    # 9:30:01 AM
        (60,    8000),    # 9:31:00 AM
        (300,   4500),    # 9:35:00 AM
        (1800, 15000),    # 10:00:00 AM
        (3600,  9000),    # 10:30:00 AM
        (23399, 22000),   # 3:59:59 PM — closing rush
    ]

    for slot, vol in trades:
        tracker.add_trade(slot, vol)

    # Query: total volume in first minute (slots 0-59)
    first_minute = tracker.query_volume(0, 59)
    print(f"Volume in first minute: {first_minute:,}")  # 20,000

    # Query: volume in first hour (slots 0-3599)
    first_hour = tracker.query_volume(0, 3599)
    print(f"Volume in first hour: {first_hour:,}")  # 47,500

    # Query: entire day
    full_day = tracker.query_volume(0, 23399)
    print(f"Total day volume: {full_day:,}")  # 78,500

    # Add more trades and re-query — O(log n) update
    tracker.add_trade(60, 2000)
    print(f"Volume in first minute after update: {tracker.query_volume(0, 59):,}")  # 20,000
    print(f"Volume at slot 60 after update: {tracker.get_volume_at(60):,}")  # 10,000

demo_trading()
```

### Performance Comparison

| Operation | Naive (array) | Prefix sum | Segment tree |
|---|---|---|---|
| Update | O(1) | O(n) rebuild | O(log n) |
| Range query | O(n) | O(1) | O(log n) |
| Use when | Rare queries | Rare updates | Frequent both |

---

## Application 2 — Range Minimum Query (Weather / Sensor Systems)

### The Problem

A temperature monitoring system records daily low temperatures. Users ask: "What was the
coldest temperature between day D1 and day D2?" The system supports both updates (sensor
correction, re-readings) and range minimum queries.

### Implementation

```python
import math

class TemperatureMonitor:
    """
    Records daily temperatures and answers range minimum queries.

    Initialized with a list of temperatures.
    Supports point updates (correcting a reading) and range min queries.

    Time complexity: build O(n), update O(log n), min_temp O(log n)
    """

    def __init__(self, temperatures: list[float]):
        self.n = len(temperatures)
        self.tree = [math.inf] * (4 * self.n)
        if self.n > 0:
            self._build(temperatures, 1, 0, self.n - 1)

    def _build(self, temps: list[float], node: int, start: int, end: int) -> None:
        if start == end:
            self.tree[node] = temps[start]
            return
        mid = (start + end) // 2
        self._build(temps, 2 * node, start, mid)
        self._build(temps, 2 * node + 1, mid + 1, end)
        self.tree[node] = min(self.tree[2 * node], self.tree[2 * node + 1])

    def _update(self, node: int, start: int, end: int, idx: int, value: float) -> None:
        if start == end:
            self.tree[node] = value
            return
        mid = (start + end) // 2
        if idx <= mid:
            self._update(2 * node, start, mid, idx, value)
        else:
            self._update(2 * node + 1, mid + 1, end, idx, value)
        self.tree[node] = min(self.tree[2 * node], self.tree[2 * node + 1])

    def _query(self, node: int, start: int, end: int, left: int, right: int) -> float:
        if right < start or end < left:
            return math.inf  # outside range: return identity for min
        if left <= start and end <= right:
            return self.tree[node]
        mid = (start + end) // 2
        left_min = self._query(2 * node, start, mid, left, right)
        right_min = self._query(2 * node + 1, mid + 1, end, left, right)
        return min(left_min, right_min)

    def update(self, day: int, temp: float) -> None:
        """Correct or update the temperature reading for a specific day (0-indexed)."""
        if not (0 <= day < self.n):
            raise IndexError(f"day {day} out of range")
        self._update(1, 0, self.n - 1, day, temp)

    def min_temp(self, start_day: int, end_day: int) -> float:
        """Return the minimum temperature recorded between start_day and end_day (inclusive)."""
        if start_day > end_day:
            raise ValueError("start_day must be <= end_day")
        start_day = max(0, start_day)
        end_day = min(self.n - 1, end_day)
        return self._query(1, 0, self.n - 1, start_day, end_day)

    def max_temp(self, start_day: int, end_day: int) -> float:
        """
        To support max queries, we would maintain a separate max tree.
        This demonstration shows how min and max require separate trees
        unless you store both in a combined node (see RangeAggregator).
        """
        raise NotImplementedError(
            "max_temp requires a separate max segment tree. See RangeAggregator."
        )


# Example: January daily low temperatures (Celsius) — 31 days
def demo_temperature():
    january_lows = [
        -3.2, -5.1,  0.4,  2.1, -1.3,  # days 0-4
        -7.8, -9.2, -6.5, -4.0, -2.1,  # days 5-9
         1.2,  3.4,  2.8,  0.0, -1.9,  # days 10-14
        -4.5, -6.1, -5.3, -3.7, -2.2,  # days 15-19
         0.8,  2.3,  1.1, -0.5, -2.8,  # days 20-24
        -5.0, -7.3, -8.1, -6.9, -4.4,  # days 25-29
        -1.0                            # day 30
    ]

    monitor = TemperatureMonitor(january_lows)

    # What was the coldest day this month?
    coldest = monitor.min_temp(0, 30)
    print(f"Coldest temperature in January: {coldest}°C")  # -9.2

    # What was the coldest day in the first week?
    week1_cold = monitor.min_temp(0, 6)
    print(f"Coldest in week 1 (days 0-6): {week1_cold}°C")  # -9.2 (day 6)

    # Coldest in week 2 (days 7-13)?
    week2_cold = monitor.min_temp(7, 13)
    print(f"Coldest in week 2 (days 7-13): {week2_cold}°C")  # -6.5 (day 7)

    # Sensor correction: day 6 reading was wrong, actual was -8.0
    monitor.update(6, -8.0)
    week1_cold_corrected = monitor.min_temp(0, 6)
    print(f"Coldest in week 1 after correction: {week1_cold_corrected}°C")  # -8.0

    # Range query: coldest during a storm period (days 25-30)?
    storm = monitor.min_temp(25, 30)
    print(f"Coldest during storm period: {storm}°C")  # -8.1

demo_temperature()
```

---

## Application 3 — Lazy Propagation for Bulk Updates

### The Problem

An e-commerce platform has `n` products indexed 0 to n-1, each with a base price. A flash sale
applies a percentage discount to all products in a category, which maps to a contiguous range of
product IDs. Without lazy propagation, updating every product in a range takes O(n) per bulk
operation. With lazy propagation, we defer updates and apply them only when needed: O(log n) per
bulk update and O(log n) per point query.

### The Lazy Propagation Concept

Instead of immediately applying a bulk update to all leaf nodes, we store a "pending update" at
the highest node that covers the entire range. This pending update is called the lazy tag. When we
later need to query or update a child node, we first push the lazy tag down to the children and
clear it from the parent. This "lazy" deferral ensures each operation touches only O(log n) nodes.

### Implementation

```python
class PriceDatabase:
    """
    Stores product prices and supports:
    - bulk_discount(start, end, percent): apply X% discount to products [start, end]
    - bulk_markup(start, end, percent): apply X% markup to products [start, end]
    - get_price(product_id): current price of product
    - range_sum(start, end): total revenue if all products in range sell once

    Uses lazy propagation for bulk multiplicative updates.

    Time complexity:
        - bulk_discount/markup: O(log n)
        - get_price: O(log n)
        - range_sum: O(log n)
    """

    def __init__(self, prices: list[float]):
        self.n = len(prices)
        self.tree = [0.0] * (4 * self.n)   # sum tree
        self.lazy = [1.0] * (4 * self.n)   # multiplicative lazy tags (1.0 = no pending update)
        self._build(prices, 1, 0, self.n - 1)

    def _build(self, prices: list[float], node: int, start: int, end: int) -> None:
        if start == end:
            self.tree[node] = prices[start]
            return
        mid = (start + end) // 2
        self._build(prices, 2 * node, start, mid)
        self._build(prices, 2 * node + 1, mid + 1, end)
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def _push_down(self, node: int, start: int, end: int) -> None:
        """
        Push the lazy multiplier at node down to its children.
        Called before accessing children so they have accurate values.
        """
        if self.lazy[node] != 1.0:
            mid = (start + end) // 2
            left_size = mid - start + 1
            right_size = end - mid

            # Apply multiplier to children's sum trees
            self.tree[2 * node] *= self.lazy[node]
            self.tree[2 * node + 1] *= self.lazy[node]

            # Pass the multiplier down to children's lazy tags
            self.lazy[2 * node] *= self.lazy[node]
            self.lazy[2 * node + 1] *= self.lazy[node]

            # Clear the lazy tag at this node
            self.lazy[node] = 1.0

    def _update_range(
        self, node: int, start: int, end: int,
        left: int, right: int, multiplier: float
    ) -> None:
        """Apply a multiplicative update to all elements in [left, right]."""
        if right < start or end < left:
            return  # completely outside update range
        if left <= start and end <= right:
            # Completely inside: apply lazily
            self.tree[node] *= multiplier
            self.lazy[node] *= multiplier
            return
        # Partially overlapping: push down, then recurse
        self._push_down(node, start, end)
        mid = (start + end) // 2
        self._update_range(2 * node, start, mid, left, right, multiplier)
        self._update_range(2 * node + 1, mid + 1, end, left, right, multiplier)
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def _query_range(
        self, node: int, start: int, end: int, left: int, right: int
    ) -> float:
        """Return sum of elements in [left, right]."""
        if right < start or end < left:
            return 0.0
        if left <= start and end <= right:
            return self.tree[node]
        self._push_down(node, start, end)
        mid = (start + end) // 2
        return (
            self._query_range(2 * node, start, mid, left, right)
            + self._query_range(2 * node + 1, mid + 1, end, left, right)
        )

    def bulk_discount(self, start: int, end: int, percent: float) -> None:
        """
        Apply percent% discount to all products with IDs in [start, end].

        Example: bulk_discount(10, 50, 10) reduces prices by 10%.
        Multiplier = (100 - percent) / 100 = 0.90 for 10% off.
        """
        if percent < 0 or percent > 100:
            raise ValueError("percent must be between 0 and 100")
        multiplier = (100.0 - percent) / 100.0
        self._update_range(1, 0, self.n - 1, start, end, multiplier)

    def bulk_markup(self, start: int, end: int, percent: float) -> None:
        """
        Apply percent% markup to all products with IDs in [start, end].

        Example: bulk_markup(10, 50, 5) increases prices by 5%.
        Multiplier = (100 + percent) / 100 = 1.05 for 5% increase.
        """
        multiplier = (100.0 + percent) / 100.0
        self._update_range(1, 0, self.n - 1, start, end, multiplier)

    def get_price(self, product_id: int) -> float:
        """Return the current price of a single product."""
        return self._query_range(1, 0, self.n - 1, product_id, product_id)

    def range_sum(self, start: int, end: int) -> float:
        """Return total price of all products in [start, end]."""
        return self._query_range(1, 0, self.n - 1, start, end)


# Example
def demo_pricing():
    # 10 products with prices $10 to $100
    prices = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
    db = PriceDatabase(prices)

    print("Initial prices:")
    for i in range(10):
        print(f"  Product {i}: ${db.get_price(i):.2f}")

    # Flash sale: 20% off products 2-5 (category "Electronics")
    db.bulk_discount(2, 5, 20)
    print("\nAfter 20% discount on products 2-5:")
    for i in range(6):
        print(f"  Product {i}: ${db.get_price(i):.2f}")
    # Products 0,1: unchanged. Products 2-5: 30→24, 40→32, 50→40, 60→48

    # Additional 10% off products 3-4 (deeper sale)
    db.bulk_discount(3, 4, 10)
    print(f"\nProduct 3 after stacked discounts: ${db.get_price(3):.2f}")
    # 32.0 * 0.90 = 28.80

    # Check total revenue of category 2-5
    total = db.range_sum(2, 5)
    print(f"Total price of products 2-5: ${total:.2f}")
    # 24.0 + 28.80 + 36.0 + 48.0 = 136.80

    # Markup products 7-9 by 5% (premium items)
    db.bulk_markup(7, 9, 5)
    print(f"\nProduct 8 after 5% markup: ${db.get_price(8):.2f}")  # 90 * 1.05 = 94.50

demo_pricing()
```

### Why Not Update Every Element Directly?

Without lazy propagation, `bulk_discount(0, n-1, 10)` visits every leaf node: O(n).
With lazy propagation, only O(log n) nodes are touched: the ranges that are fully covered
get a tag, and children are only updated when they are actually accessed.

For a catalog of 1,000,000 products:
- Without lazy: 1,000,000 operations per bulk discount
- With lazy: ~40 operations (log2(1,000,000) ≈ 20 levels × ~2 nodes per level)

---

## Application 4 — Database Range Aggregations

### The Problem

A database needs to support range aggregations (COUNT, SUM, MIN, MAX) over an array of records
efficiently, with mixed reads and writes. SQL databases use B-trees for indexed access but
segment trees appear in analytical databases (columnar stores) for in-memory range aggregation.

### Implementation: Multi-Operation Aggregator

```python
import math
from dataclasses import dataclass

@dataclass
class AggNode:
    """Node in the segment tree storing all four aggregates."""
    total: float = 0.0
    minimum: float = math.inf
    maximum: float = -math.inf
    count: int = 0


class RangeAggregator:
    """
    Supports O(log n) range COUNT, SUM, MIN, MAX queries with O(log n) point updates.

    Use case: analytical database column where records have numeric values.
    The index represents a record ID (0-indexed), and the value is a numeric field.

    Example: table of order amounts — count/sum/min/max over a range of order IDs.
    """

    def __init__(self, values: list[float]):
        self.n = len(values)
        self.tree: list[AggNode] = [AggNode() for _ in range(4 * self.n)]
        self._build(values, 1, 0, self.n - 1)

    def _build(self, values: list[float], node: int, start: int, end: int) -> None:
        if start == end:
            self.tree[node] = AggNode(
                total=values[start],
                minimum=values[start],
                maximum=values[start],
                count=1
            )
            return
        mid = (start + end) // 2
        self._build(values, 2 * node, start, mid)
        self._build(values, 2 * node + 1, mid + 1, end)
        self._merge_up(node)

    def _merge_up(self, node: int) -> None:
        left = self.tree[2 * node]
        right = self.tree[2 * node + 1]
        self.tree[node] = AggNode(
            total=left.total + right.total,
            minimum=min(left.minimum, right.minimum),
            maximum=max(left.maximum, right.maximum),
            count=left.count + right.count
        )

    def _update(self, node: int, start: int, end: int, idx: int, value: float) -> None:
        if start == end:
            self.tree[node] = AggNode(
                total=value, minimum=value, maximum=value, count=1
            )
            return
        mid = (start + end) // 2
        if idx <= mid:
            self._update(2 * node, start, mid, idx, value)
        else:
            self._update(2 * node + 1, mid + 1, end, idx, value)
        self._merge_up(node)

    def _query(
        self, node: int, start: int, end: int, left: int, right: int
    ) -> AggNode:
        if right < start or end < left:
            return AggNode()  # identity element: 0 sum, inf min, -inf max, 0 count
        if left <= start and end <= right:
            return self.tree[node]
        mid = (start + end) // 2
        left_result = self._query(2 * node, start, mid, left, right)
        right_result = self._query(2 * node + 1, mid + 1, end, left, right)
        return AggNode(
            total=left_result.total + right_result.total,
            minimum=min(left_result.minimum, right_result.minimum),
            maximum=max(left_result.maximum, right_result.maximum),
            count=left_result.count + right_result.count
        )

    def update(self, record_id: int, value: float) -> None:
        """Update the value of record with given ID."""
        self._update(1, 0, self.n - 1, record_id, value)

    def range_count(self, start: int, end: int) -> int:
        """COUNT(*) for records in [start, end]."""
        return self._query(1, 0, self.n - 1, start, end).count

    def range_sum(self, start: int, end: int) -> float:
        """SUM(value) for records in [start, end]."""
        return self._query(1, 0, self.n - 1, start, end).total

    def range_min(self, start: int, end: int) -> float:
        """MIN(value) for records in [start, end]."""
        return self._query(1, 0, self.n - 1, start, end).minimum

    def range_max(self, start: int, end: int) -> float:
        """MAX(value) for records in [start, end]."""
        return self._query(1, 0, self.n - 1, start, end).maximum

    def range_avg(self, start: int, end: int) -> float:
        """AVG(value) for records in [start, end]."""
        result = self._query(1, 0, self.n - 1, start, end)
        if result.count == 0:
            return 0.0
        return result.total / result.count


# Example: order amounts for 10 orders (IDs 0-9)
def demo_aggregator():
    order_amounts = [150.0, 230.0, 89.0, 512.0, 75.0, 340.0, 189.0, 620.0, 95.0, 410.0]
    agg = RangeAggregator(order_amounts)

    # SQL equivalent: SELECT COUNT(*), SUM(amount), MIN(amount), MAX(amount), AVG(amount)
    #                 FROM orders WHERE order_id BETWEEN 2 AND 7
    print("Orders 2-7:")
    print(f"  COUNT: {agg.range_count(2, 7)}")     # 6
    print(f"  SUM:   ${agg.range_sum(2, 7):.2f}")  # 1824.00
    print(f"  MIN:   ${agg.range_min(2, 7):.2f}")  # 75.00
    print(f"  MAX:   ${agg.range_max(2, 7):.2f}")  # 620.00
    print(f"  AVG:   ${agg.range_avg(2, 7):.2f}")  # 304.00

    # Order 3 gets a refund and is corrected
    agg.update(3, 412.0)
    print(f"\nAfter correcting order 3 to $412:")
    print(f"  SUM orders 2-7: ${agg.range_sum(2, 7):.2f}")  # 1724.00

demo_aggregator()
```

---

## Application 5 — Competitive Gaming Leaderboard

### The Problem

A game has millions of players sorted by score. The game needs to answer: "Who are the players
ranked 100 to 200 globally?" Players' scores change constantly. Rank is dynamic — it is the
position in a sorted order, not a fixed ID. A segment tree over score buckets can count how many
players have a score in a given range, which is the foundation for rank-based queries.

### Implementation

```python
class LeaderboardRank:
    """
    Leaderboard using a segment tree over score buckets.

    Scores are integer values in [0, max_score].
    The segment tree stores the count of players at each score.

    Operations:
        add_player(score): register a player with a score
        update_score(old_score, new_score): player's score changed
        count_players_with_score_in(lo, hi): how many players have score in [lo, hi]
        rank_of_score(score): how many players have a HIGHER score (1-indexed rank)
        players_at_rank_range(rank_lo, rank_hi): how many players are in that rank band

    Time complexity: all operations O(log max_score)
    """

    def __init__(self, max_score: int):
        self.max_score = max_score
        self.tree = [0] * (4 * (max_score + 1))
        self.n = max_score + 1  # scores are 0..max_score inclusive

    def _update(self, node: int, start: int, end: int, idx: int, delta: int) -> None:
        if start == end:
            self.tree[node] += delta
            return
        mid = (start + end) // 2
        if idx <= mid:
            self._update(2 * node, start, mid, idx, delta)
        else:
            self._update(2 * node + 1, mid + 1, end, idx, delta)
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def _query(self, node: int, start: int, end: int, left: int, right: int) -> int:
        if right < start or end < left:
            return 0
        if left <= start and end <= right:
            return self.tree[node]
        mid = (start + end) // 2
        return (
            self._query(2 * node, start, mid, left, right)
            + self._query(2 * node + 1, mid + 1, end, left, right)
        )

    def add_player(self, score: int) -> None:
        """Register a new player with the given score."""
        self._update(1, 0, self.n - 1, score, 1)

    def remove_player(self, score: int) -> None:
        """Remove a player with the given score."""
        self._update(1, 0, self.n - 1, score, -1)

    def update_score(self, old_score: int, new_score: int) -> None:
        """Player's score changed from old_score to new_score."""
        self.remove_player(old_score)
        self.add_player(new_score)

    def count_players_in_score_range(self, lo: int, hi: int) -> int:
        """How many players have a score between lo and hi (inclusive)?"""
        return self._query(1, 0, self.n - 1, lo, hi)

    def rank_of_score(self, score: int) -> int:
        """
        How many players have a STRICTLY HIGHER score?
        This is the 0-indexed rank (0 = best).
        Add 1 for 1-indexed rank.
        """
        if score >= self.max_score:
            return 0
        return self._query(1, 0, self.n - 1, score + 1, self.max_score)

    def total_players(self) -> int:
        """Total number of registered players."""
        return self._query(1, 0, self.n - 1, 0, self.n - 1)


# Example: game with scores 0-1000
def demo_leaderboard():
    board = LeaderboardRank(max_score=1000)

    # Add 10 players with various scores
    player_scores = [850, 920, 750, 980, 810, 670, 900, 760, 840, 955]
    for score in player_scores:
        board.add_player(score)

    print(f"Total players: {board.total_players()}")  # 10

    # Player with score 850: what is their rank?
    rank = board.rank_of_score(850) + 1  # +1 for 1-indexed
    print(f"Rank of player with score 850: {rank}")  # Players above 850: 920,980,900,955 → rank 5

    # How many players have score between 800 and 900?
    mid_range = board.count_players_in_score_range(800, 900)
    print(f"Players with score 800-900: {mid_range}")  # 850, 810, 900, 840 → 4

    # Player improves score from 750 to 890
    board.update_score(750, 890)
    print(f"After update: rank of 890: {board.rank_of_score(890) + 1}")  # 920,980,900,955 → rank 5

demo_leaderboard()
```

---

## Application 6 — Fenwick Tree (Binary Indexed Tree) as Alternative

### What Is a Fenwick Tree?

A Fenwick Tree (also called Binary Indexed Tree or BIT) is a data structure that supports:
- Point updates: O(log n)
- Prefix sum queries: O(log n)
- Range sum queries: O(log n) via two prefix sum queries

It is more concise than a segment tree (5-10 lines of code vs 30-50), uses half the memory
(only 1 array of size n+1 instead of 4n), and has better cache performance. The trade-off is
that it only naturally supports operations where the inverse operation exists (sum/subtraction,
XOR), not min/max.

### When to Use Fenwick Tree vs Segment Tree

| Feature | Fenwick Tree | Segment Tree |
|---|---|---|
| Code complexity | Very simple | Moderate |
| Memory | O(n) | O(4n) |
| Supported ops | Sum, XOR (invertible) | Sum, min, max, any |
| Lazy propagation | Not directly | Yes |
| Range updates | Complex workaround | Natural with lazy |
| Implementation time | 5 minutes | 15-20 minutes |

### Implementation

```python
class FenwickTree:
    """
    Binary Indexed Tree (Fenwick Tree) for prefix sum queries and point updates.

    Internally, tree[i] stores the sum of a specific range of elements.
    The range each index is responsible for is determined by the lowest set bit
    of the index (i & -i).

    Key insight: i & -i (the lowest set bit) tells you how many elements
    tree[i] is responsible for. This creates a telescoping structure where
    prefix sums can be computed by hopping through only O(log n) nodes.

    Indexing is 1-based internally for simplicity.
    """

    def __init__(self, n: int):
        self.n = n
        self.tree = [0] * (n + 1)  # 1-indexed: positions 1..n

    def update(self, i: int, delta: int) -> None:
        """
        Add delta to element at position i (1-indexed).

        Traverses the tree by repeatedly adding the lowest set bit to i.
        This updates all ancestors responsible for position i.
        """
        while i <= self.n:
            self.tree[i] += delta
            i += i & (-i)  # i & -i: lowest set bit; moves to next ancestor

    def prefix_sum(self, i: int) -> int:
        """
        Return sum of elements at positions 1..i (inclusive, 1-indexed).

        Traverses the tree by repeatedly removing the lowest set bit from i.
        This sums up all relevant nodes.
        """
        total = 0
        while i > 0:
            total += self.tree[i]
            i -= i & (-i)  # remove lowest set bit; moves to previous relevant node
        return total

    def range_sum(self, l: int, r: int) -> int:
        """
        Return sum of elements at positions l..r (inclusive, 1-indexed).

        range_sum(l, r) = prefix_sum(r) - prefix_sum(l-1)
        """
        if l > r:
            return 0
        if l == 1:
            return self.prefix_sum(r)
        return self.prefix_sum(r) - self.prefix_sum(l - 1)

    def point_query(self, i: int) -> int:
        """Return the value at position i (1-indexed)."""
        return self.range_sum(i, i)

    @classmethod
    def from_array(cls, arr: list[int]) -> "FenwickTree":
        """
        Build a Fenwick tree from an existing array in O(n) time.

        The naive approach (calling update for each element) is O(n log n).
        This O(n) construction directly sets tree values using the BIT structure.
        """
        n = len(arr)
        bit = cls(n)
        # Copy array into tree (1-indexed)
        for i in range(1, n + 1):
            bit.tree[i] += arr[i - 1]
            parent = i + (i & -i)  # parent in BIT structure
            if parent <= n:
                bit.tree[parent] += bit.tree[i]
        return bit


# Example: same trading volume problem solved with Fenwick tree
def demo_fenwick():
    print("=== Fenwick Tree Demo ===\n")

    # 10 time slots with initial volumes
    volumes = [5000, 3000, 8000, 4500, 9000, 2000, 7500, 6000, 1500, 11000]
    bit = FenwickTree.from_array(volumes)

    # Range sum: total volume in slots 3-7 (1-indexed)
    print(f"Volume in slots 3-7: {bit.range_sum(3, 7):,}")
    # 8000 + 4500 + 9000 + 2000 + 7500 = 31000

    # Point update: add 2500 to slot 5
    bit.update(5, 2500)
    print(f"Volume at slot 5 after update: {bit.point_query(5):,}")  # 9000 + 2500 = 11500

    # Prefix sum: total from beginning to slot 6
    print(f"Total volume through slot 6: {bit.prefix_sum(6):,}")
    # 5000+3000+8000+4500+11500+2000 = 34000

    # Full range
    print(f"Total across all slots: {bit.prefix_sum(10):,}")
    # 5000+3000+8000+4500+11500+2000+7500+6000+1500+11000 = 60000

    print("\n=== Bit Manipulation Walkthrough ===")
    print("prefix_sum(6) traversal (6 in binary = 110):")
    i = 6
    steps = []
    while i > 0:
        steps.append(f"  i={i} (binary={bin(i)}), tree[{i}]={bit.tree[i]}, i -= {i & -i} → {i - (i & -i)}")
        i -= i & (-i)
    for step in steps:
        print(step)

    print("\nupdate(3, 1000) traversal (3 in binary = 011):")
    temp_bit = FenwickTree(10)
    i = 3
    while i <= temp_bit.n:
        print(f"  update tree[{i}] (binary={bin(i)}), next i += {i & -i} → {i + (i & -i)}")
        i += i & (-i)


demo_fenwick()
```

### Understanding the Bit Manipulation

The core of a Fenwick tree is the expression `i & -i`, which extracts the lowest set bit of `i`:

```
i =  6 → binary 0110 → i & -i = 0010 = 2
i = 12 → binary 1100 → i & -i = 0100 = 4
i =  8 → binary 1000 → i & -i = 1000 = 8
i =  5 → binary 0101 → i & -i = 0001 = 1
```

During `prefix_sum(i)`, we subtract `i & -i` to hop to the previous relevant node.
During `update(i, delta)`, we add `i & -i` to hop to the next ancestor.

This creates a binary tree structure where each node covers `i & -i` elements, and
prefix sums can be decomposed into at most `O(log n)` such blocks.

### Complete Comparison: When to Use Each

**Use Fenwick tree when:**
- You only need range sum / prefix sum
- You need point updates
- You want the simplest possible implementation
- Memory is a concern (half the space of segment tree)
- You are in a timed contest and need fast implementation

**Use segment tree when:**
- You need min, max, or custom aggregate functions
- You need range updates (lazy propagation)
- You need more complex operations like "find first element in range > X"
- You need to support multiple aggregate types simultaneously (see RangeAggregator)
