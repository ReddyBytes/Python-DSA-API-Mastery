"""
01.1_memory_management/gc_examples.py
========================================
CONCEPT: Python's Garbage Collector — when reference counting isn't enough.
WHY THIS MATTERS: Reference counting alone cannot reclaim circular references.
In long-running servers, data pipelines, and ML training jobs, understanding
the GC prevents memory leaks that cause gradual server OOM crashes.
"""

import gc
import sys
import weakref

# =============================================================================
# SECTION 1: Reference counting — how Python normally frees memory
# =============================================================================

# CONCEPT: Every object has a reference count. When count reaches 0,
# Python immediately frees the memory — no GC needed. This handles ~95% of
# memory management in typical Python programs.

print("=== Section 1: Reference Counting ===")

class TrackedObject:
    """Announces creation and destruction so we can observe ref count behavior."""
    def __init__(self, name):
        self.name = name
        print(f"  [CREATED]  {self.name}")

    def __del__(self):
        # __del__ is called when ref count hits exactly 0
        print(f"  [DELETED]  {self.name}")

# Create, add reference, remove references
obj = TrackedObject("obj_A")
print(f"  Ref count (expect ~2): {sys.getrefcount(obj)}")
# WHY ~2: our variable `obj` + temporary ref created by getrefcount itself

ref2 = obj
print(f"  After ref2=obj, count: {sys.getrefcount(obj)}")  # ~3

del ref2   # count drops back to ~2
print(f"  After del ref2, count: {sys.getrefcount(obj)}")  # ~2

print("  Deleting last reference...")
del obj    # count → 0 → __del__ called IMMEDIATELY
print("  obj is gone (no GC needed for this — pure ref counting)")


# =============================================================================
# SECTION 2: The problem — circular references
# =============================================================================

# CONCEPT: When two objects reference each other, deleting external names
# leaves both objects with ref count > 0. Reference counting CANNOT collect
# these — they live forever until the cyclic GC runs.

print("\n=== Section 2: Circular References ===")

class Node:
    def __init__(self, name):
        self.name = name
        self.partner = None

    def __del__(self):
        print(f"  [DELETED] Node({self.name})")

# Disable GC so we can prove the problem without automatic cleanup
gc.disable()

# Create cycle: A → B → A
node_a = Node("A")
node_b = Node("B")
node_a.partner = node_b   # A holds a reference to B
node_b.partner = node_a   # B holds a reference to A → CYCLE

print(f"  node_a ref count: {sys.getrefcount(node_a)}")  # ~3 (var + B.partner + call)
print(f"  node_b ref count: {sys.getrefcount(node_b)}")  # ~3

print("  Deleting external names...")
del node_a
del node_b
# __del__ NOT called — both still have nonzero ref counts due to the cycle!
print("  (notice: no [DELETED] messages — they're stuck in memory)")

# Force the cyclic GC to find and collect them
print("  Running gc.collect()...")
collected = gc.collect()
print(f"  gc.collect() found and freed {collected} objects")

gc.enable()  # restore automatic GC


# =============================================================================
# SECTION 3: GC generations — why the GC is fast
# =============================================================================

# CONCEPT: The GC divides objects into 3 generations:
#   Gen 0 — newly allocated objects (scanned most often)
#   Gen 1 — survived at least one gen-0 collection
#   Gen 2 — long-lived objects (scanned rarely)
# Theory: "most objects die young." Scanning only gen-0 is cheap and handles
# most cycles. Gen-2 is only scanned after many gen-0 collections.

print("\n=== Section 3: GC Generations ===")

print(f"  GC is enabled: {gc.isenabled()}")
print(f"  Generation thresholds: {gc.get_threshold()}")
# Default: (700, 10, 10)
# Collect gen0 when 700 new objects allocated since last gen0 collection
# Collect gen1 when gen0 collected 10 times
# Collect gen2 when gen1 collected 10 times

print(f"  Current counts: {gc.get_count()}")
# (a, b, c): allocations since last collection at each generation level

# Manual collection per generation
gc.collect(0)   # collect only gen 0
gc.collect(1)   # collect gen 0 and 1
gc.collect(2)   # full collection — all generations
print(f"  Counts after full collect: {gc.get_count()}")


# =============================================================================
# SECTION 4: Inspecting what the GC is tracking
# =============================================================================

# CONCEPT: gc.get_objects() returns every object currently tracked.
# gc.garbage holds objects with __del__ methods caught in cycles
# (the "uncollectable" objects in Python <3.4, now usually empty).

print("\n=== Section 4: Inspecting Tracked Objects ===")

gc.collect()   # start clean

class SampleObject:
    def __init__(self, n):
        self.n = n

samples = [SampleObject(i) for i in range(5)]

# Count how many SampleObject instances the GC is tracking
tracked = [o for o in gc.get_objects() if isinstance(o, SampleObject)]
print(f"  SampleObject instances tracked: {len(tracked)}")

del samples
gc.collect()

tracked_after = [o for o in gc.get_objects() if isinstance(o, SampleObject)]
print(f"  After del + gc.collect(): {len(tracked_after)} tracked")

# gc.garbage should be empty in normal code
print(f"  gc.garbage (uncollectable): {gc.garbage}")


# =============================================================================
# SECTION 5: Weak references — caching without preventing cleanup
# =============================================================================

# CONCEPT: A weakref.ref() creates a reference that does NOT increment the
# object's reference count. If all strong references are gone, the object
# is collected even while the weak reference exists (it returns None after).
#
# KEY USE CASE: Caches. You want to reuse objects if they're still alive,
# but you don't want the cache itself to keep objects alive forever.

print("\n=== Section 5: Weak References ===")

class HeavyDocument:
    def __init__(self, doc_id):
        self.doc_id = doc_id
        self.data = list(range(1000))   # simulates large data

    def __del__(self):
        print(f"  [DELETED] HeavyDocument({self.doc_id})")

doc = HeavyDocument(42)
weak = weakref.ref(doc)    # does NOT increment ref count

print(f"  weak() while alive: {weak()}")          # returns the object
print(f"  doc_id via weak: {weak().doc_id}")       # access normally

del doc   # object's ref count → 0 → immediately collected
print(f"  weak() after del doc: {weak()}")         # None

# WeakValueDictionary: a self-cleaning cache
print("\n  WeakValueDictionary cache demo:")
cache = weakref.WeakValueDictionary()

doc1 = HeavyDocument(1)
doc2 = HeavyDocument(2)
cache[1] = doc1
cache[2] = doc2
print(f"  Cache size: {len(cache)}")   # 2

del doc1   # doc1 ref count → 0 → deleted AND auto-removed from cache
print(f"  Cache size after del doc1: {len(cache)}")  # 1 — cleaned automatically


# =============================================================================
# SECTION 6: GC callbacks — production monitoring
# =============================================================================

# CONCEPT: You can attach callbacks that fire before/after each GC run.
# Production services use this to: measure GC pause times, log collection
# frequency, alert when uncollectable objects accumulate.

print("\n=== Section 6: GC Callbacks ===")

events = []

def on_gc(phase, info):
    """
    phase: 'start' | 'stop'
    info:  {'generation': int, 'collected': int, 'uncollectable': int}
    """
    events.append(f"{phase} gen={info.get('generation')} collected={info.get('collected', '?')}")

gc.callbacks.append(on_gc)

# Create a cycle to ensure GC finds something
a_list = []
b_list = [a_list]
a_list.append(b_list)
del a_list, b_list

gc.collect()

for event in events[-4:]:   # show the last few events
    print(f"  GC event: {event}")

gc.callbacks.remove(on_gc)


# =============================================================================
# SECTION 7: tracemalloc — diagnosing memory growth
# =============================================================================

# CONCEPT: tracemalloc records which line of code allocated each block of memory.
# Take a snapshot before and after a suspect operation, then compare to find leaks.

import tracemalloc

print("\n=== Section 7: tracemalloc Leak Detection ===")

tracemalloc.start()
snapshot_before = tracemalloc.take_snapshot()

# Simulate a memory leak: storing objects globally without cleanup
global_registry = {}
for i in range(5_000):
    # Each dict here is allocated and stored — never freed
    global_registry[i] = {"id": i, "data": list(range(20))}

snapshot_after = tracemalloc.take_snapshot()
diff = snapshot_after.compare_to(snapshot_before, "lineno")

print("  Top 3 allocations since baseline:")
for stat in diff[:3]:
    print(f"    {stat}")

tracemalloc.stop()

# FIX: always clean up, or use WeakValueDictionary, or process in chunks
global_registry.clear()
gc.collect()


print("\n=== All GC examples complete ===")
print("Key takeaways:")
print("  1. Reference counting handles normal cleanup instantly (no GC needed)")
print("  2. Cyclic GC handles circular references — runs automatically in background")
print("  3. 3 generations: new objects scanned often, long-lived objects rarely")
print("  4. Use weakref for caches — objects not kept alive by cache alone")
print("  5. gc.callbacks for production monitoring of GC pauses")
print("  6. tracemalloc: snapshot before/after to find exactly what's leaking")
