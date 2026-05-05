"""
01.1_memory_management/memory_optimization.py
===============================================
CONCEPT: Practical memory optimization techniques used in production Python.
WHY THIS MATTERS: In data pipelines, ML preprocessing, and high-traffic APIs,
memory efficiency directly impacts cost, speed, and whether your service crashes.
Techniques here can reduce memory usage by 50-80% in real scenarios.
"""

import sys
import gc
import tracemalloc

# =============================================================================
# SECTION 1: __slots__ — eliminate per-instance __dict__ overhead
# =============================================================================

# CONCEPT: Every normal class instance carries a __dict__ — a hash table of
# all its attributes. Flexible, but expensive: typically 200-400 bytes overhead.
# __slots__ replaces __dict__ with pre-allocated fixed slots.
# Result: 40-60% memory savings per instance, critical when creating millions.

print("=== Section 1: __slots__ ===")

class RegularUser:
    """Normal class — every instance has a __dict__."""
    def __init__(self, user_id, name, email, age):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.age = age

class SlottedUser:
    """__slots__ replaces __dict__ with fixed attribute slots."""
    __slots__ = ['user_id', 'name', 'email', 'age']   # only these attributes allowed

    def __init__(self, user_id, name, email, age):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.age = age

regular = RegularUser(1, "Alice", "alice@example.com", 30)
slotted = SlottedUser(1, "Alice", "alice@example.com", 30)

regular_total = sys.getsizeof(regular) + sys.getsizeof(regular.__dict__)
slotted_total = sys.getsizeof(slotted)   # no __dict__

print(f"  Regular instance: {sys.getsizeof(regular)}B obj + {sys.getsizeof(regular.__dict__)}B dict = {regular_total}B total")
print(f"  Slotted instance: {slotted_total}B total")
print(f"  Savings per instance: {regular_total - slotted_total}B ({100*(regular_total-slotted_total)//regular_total}%)")

# Tradeoff: __slots__ objects cannot have arbitrary attributes added
try:
    slotted.extra = "not allowed"
except AttributeError as e:
    print(f"  Can't add arbitrary attr: {e}")

# Tradeoff: can still inherit (but subclass needs its own __slots__ for savings)
# Good for: high-volume value objects (User, Product, Point, Embedding, etc.)

# Measure with 100k instances
tracemalloc.start()
regular_list = [RegularUser(i, f"U{i}", f"u{i}@x.com", 25) for i in range(100_000)]
s1 = tracemalloc.take_snapshot()
del regular_list; gc.collect()

slotted_list = [SlottedUser(i, f"U{i}", f"u{i}@x.com", 25) for i in range(100_000)]
s2 = tracemalloc.take_snapshot()
del slotted_list; gc.collect()
tracemalloc.stop()

total_reg = sum(s.size for s in s1.statistics("lineno")) / 1024 / 1024
total_slt = sum(s.size for s in s2.statistics("lineno")) / 1024 / 1024
print(f"\n  100k Regular instances: ~{total_reg:.1f} MB")
print(f"  100k Slotted instances: ~{total_slt:.1f} MB")


# =============================================================================
# SECTION 2: Generators — O(1) memory for any-size sequences
# =============================================================================

# CONCEPT: A list comprehension allocates ALL items at once.
# A generator expression (with parentheses) produces ONE item at a time.
# The generator object itself is ~112 bytes regardless of sequence length.
# For 1M items, this is the difference between 8MB and 112 bytes.

print("\n=== Section 2: Generators vs Lists ===")

n = 1_000_000

list_size = sys.getsizeof([x * x for x in range(n)])
gen_size  = sys.getsizeof((x * x for x in range(n)))

print(f"  List of {n:,} squares: {list_size / 1024 / 1024:.1f} MB")
print(f"  Generator for same:    {gen_size} bytes")
print(f"  Memory ratio: {list_size // gen_size:,}x")

# Generators compose: each stage processes ONE item, no intermediate lists
def read_records():
    """Simulate reading records from a file or DB — yields one at a time."""
    for i in range(100):
        yield {"id": i, "value": i * 10, "status": "active" if i % 2 == 0 else "inactive"}

def filter_active(records):
    """Only pass through active records — no intermediate list created."""
    for record in records:
        if record["status"] == "active":
            yield record

def enrich(records):
    """Add computed field — still lazy."""
    for record in records:
        record["doubled"] = record["value"] * 2
        yield record

# Full pipeline: O(1) memory regardless of how many records exist
pipeline = enrich(filter_active(read_records()))
result = list(pipeline)   # only materialize at the very end
print(f"\n  Pipeline processed {len(result)} active records")
print(f"  First result: {result[0]}")


# =============================================================================
# SECTION 3: Chunked processing — handle data larger than RAM
# =============================================================================

# CONCEPT: When data exceeds memory, process in fixed-size batches.
# Memory stays bounded at O(chunk_size) instead of O(total_data_size).
# Used in: database batch inserts, API pagination, ML dataset training.

print("\n=== Section 3: Chunked Processing ===")

def chunked(iterable, size):
    """
    Yield successive chunks of `size` from iterable.
    Only `size` items in memory at once — the previous chunk is released
    before the next is built.
    """
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []   # release — allows GC to reclaim memory
    if chunk:
        yield chunk      # remainder

# Process 1 million items in batches of 10k
total = 0
chunk_count = 0
for chunk in chunked(range(1_000_000), 10_000):
    chunk_sum = sum(chunk)   # process the chunk
    total += chunk_sum
    chunk_count += 1

print(f"  Processed {chunk_count} chunks, total sum = {total:,}")
print(f"  Peak memory: always ≤ 10,000 items — never 1,000,000")

# Real-world: batch database writes
def batch_insert(records, batch_size=1000):
    """Inserts records in batches to avoid loading all into memory."""
    for batch in chunked(records, batch_size):
        # db.bulk_insert(batch)   ← would be the actual DB call
        pass   # simulated
    print(f"  Inserted {sum(1 for _ in range(len(records)))} records in batches")


# =============================================================================
# SECTION 4: String interning for datasets with repeated values
# =============================================================================

# CONCEPT: In datasets where thousands of rows share the same string value
# (e.g., "active", "US", "ERROR"), Python may allocate a new string object
# per row. sys.intern() forces all equal strings to share ONE object.
# For 1M rows with 5 unique status values: 5 objects vs 1,000,000 objects.

print("\n=== Section 4: String Interning ===")

import sys as _sys

# Verify interning works
s1 = _sys.intern("frequently_used_status")
s2 = _sys.intern("frequently_used_status")
print(f"  Interned strings are same object: {s1 is s2}")   # True

# Without intern: each row gets its own string object (common with CSV parsing)
statuses_raw = ["active" if i % 2 == 0 else "inactive" for i in range(100_000)]
# Python MAY intern these (short, identifier-like) — but you can't rely on it

# With explicit intern: guaranteed single object per unique value
statuses_interned = [_sys.intern("active" if i % 2 == 0 else "inactive")
                     for i in range(100_000)]

# Check: when interned, `is` comparisons (used in dict key lookup) are O(1)
print(f"  'active' is 'active' (interned): {statuses_interned[0] is statuses_interned[2]}")

print("  String interning is valuable for: status codes, country codes,")
print("  category labels — any column with very few unique string values")


# =============================================================================
# SECTION 5: Avoiding unnecessary copies
# =============================================================================

# CONCEPT: Copy operations use memory. Know when you need a copy vs
# when a reference is safe (read-only access).

print("\n=== Section 5: Avoiding Unnecessary Copies ===")

large_data = list(range(500_000))

# WASTEFUL: copies the entire list just to iterate over it
def process_with_copy(data):
    copy = list(data)      # full copy, doubles memory usage
    return sum(copy)       # only needed a sum — no mutation intended

# CORRECT: iterate directly for read-only access
def process_direct(data):
    return sum(data)       # reads original, no allocation

print(f"  process_with_copy: {process_with_copy(large_data)}")
print(f"  process_direct:    {process_direct(large_data)}")
print(f"  Same result, process_direct uses half the memory")

# WHEN you DO need a copy: you're going to mutate the data
def get_sorted_top_10(data):
    copy = sorted(data, reverse=True)   # sorted() returns new list — OK, necessary
    return copy[:10]

print(f"  Top 10: {get_sorted_top_10(large_data[:20])}")


# =============================================================================
# SECTION 6: del + gc.collect() for manual cleanup
# =============================================================================

# CONCEPT: In memory-intensive scripts (ML training, data processing),
# explicitly deleting large objects and triggering GC reclaims memory
# before the next large allocation. Critical when total data > 50% of RAM.

print("\n=== Section 6: Manual Memory Release ===")

def process_phase(phase_name, data_size):
    """Simulates a memory-intensive processing phase."""
    print(f"  [{phase_name}] Allocating {data_size:,} items...")
    work_data = list(range(data_size))     # ~4MB per 500k ints
    result = sum(work_data)

    # Done with this phase — explicitly free before next phase
    del work_data
    gc.collect()   # forces immediate cleanup
    print(f"  [{phase_name}] Done, result={result:,}, memory released")
    return result

# Each phase runs with bounded memory — no accumulation across phases
r1 = process_phase("Phase 1", 500_000)
r2 = process_phase("Phase 2", 500_000)
r3 = process_phase("Phase 3", 500_000)
print(f"  All 3 phases completed: {r1 + r2 + r3:,}")


# =============================================================================
# SECTION 7: tracemalloc for production leak diagnosis
# =============================================================================

# CONCEPT: tracemalloc is the standard tool for finding memory leaks.
# It records WHERE each allocation happened (file + line number).
# The workflow: start → baseline snapshot → run suspect code → compare.

print("\n=== Section 7: Memory Leak Detection with tracemalloc ===")

tracemalloc.start()
baseline = tracemalloc.take_snapshot()

# Simulate a leak: adding to a global list without cleanup
leaky_cache = []
for i in range(2_000):
    leaky_cache.append({"id": i, "data": list(range(50))})

after_leak = tracemalloc.take_snapshot()
diff = after_leak.compare_to(baseline, "lineno")

print("  Top 3 memory growth lines:")
for stat in diff[:3]:
    print(f"    {stat}")

tracemalloc.stop()

# Cleanup
del leaky_cache
gc.collect()


print("\n=== All optimization techniques demonstrated ===")
print("Production memory checklist:")
print("  ✓ __slots__ — for classes with millions of instances")
print("  ✓ Generators — never load more into memory than you need right now")
print("  ✓ Chunked processing — process data larger than RAM in batches")
print("  ✓ sys.intern() — for datasets with high-cardinality string columns")
print("  ✓ Avoid unnecessary copies — pass references for read-only access")
print("  ✓ del + gc.collect() — release memory between heavy phases")
print("  ✓ tracemalloc — snapshot comparison to find exactly what's leaking")
