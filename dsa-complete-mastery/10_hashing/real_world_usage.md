# Hashing — Real World Usage

Hash maps and hash sets are the most widely deployed data structures in production systems.
Every major piece of software you interact with daily relies on hashing somewhere in its core.

---

## 1. Database Indexing

Relational databases support two main index types: B-tree and hash indexes.

A hash index computes `hash(column_value)` and stores a pointer to the row at that bucket.
Lookups are O(1) average because you hash the key and jump directly to the bucket.

PostgreSQL supports hash indexes explicitly:

```sql
CREATE INDEX users_email_hash_idx ON users USING hash(email);
```

Why B-tree is still preferred in most cases:

- Hash indexes cannot handle range queries (`WHERE age > 30`). There is no ordering in a hash table.
- Hash indexes do not support sorting (`ORDER BY`).
- B-trees are O(log n) for lookups but support ranges, ordering, and prefix scans.

Use hash indexes only for exact equality lookups on high-cardinality columns (e.g., UUID, email).

```python
# Simulating a hash index lookup in Python
hash_index = {}

rows = [
    {"id": 1, "email": "alice@example.com"},
    {"id": 2, "email": "bob@example.com"},
    {"id": 3, "email": "carol@example.com"},
]

for row in rows:
    hash_index[row["email"]] = row  # O(1) insert

result = hash_index.get("bob@example.com")  # O(1) lookup
print(result)  # {"id": 2, "email": "bob@example.com"}
```

---

## 2. Caching — Redis and Memcached

Redis and Memcached are in-memory key-value stores. Their entire data model is a hash map:
`key -> value` stored in RAM for sub-millisecond access.

Redis extends this with:

- TTL (Time To Live): each key has an expiry. Redis uses a lazy expiry + background sweep strategy.
- Eviction policies: when memory is full, Redis evicts keys using LRU, LFU, or random strategies.

```python
import redis

client = redis.Redis(host="localhost", port=6379)

# Store user session — expires in 3600 seconds
client.setex("session:user_42", 3600, '{"user_id": 42, "role": "admin"}')

# Lookup — O(1) hash map access
session = client.get("session:user_42")
print(session)

# Cache-aside pattern used in production
def get_user(user_id: int) -> dict:
    cache_key = f"user:{user_id}"
    cached = client.get(cache_key)
    if cached:
        return eval(cached)  # deserialize
    # Cache miss — hit the database
    user = db_fetch_user(user_id)
    client.setex(cache_key, 300, str(user))  # cache for 5 minutes
    return user
```

In Memcached, the hash map is sharded across multiple nodes using consistent hashing (see section 7).

---

## 3. Deduplication at Scale — Web Crawlers and Pipelines

Google's web crawler (Googlebot) visits billions of URLs. It cannot re-crawl duplicates.
The solution: maintain a hash set of visited URLs. O(1) membership test before each fetch.

At extreme scale (trillions of URLs), even a hash set is too large for RAM.
This is where Bloom filters come in: a probabilistic set that uses multiple hash functions
and a bit array. False positives are possible (might skip a new URL), false negatives are not.

```python
# Simple deduplication with a set
visited = set()

def should_crawl(url: str) -> bool:
    url_hash = hash(url)  # Python's built-in hash
    if url_hash in visited:
        return False
    visited.add(url_hash)
    return True

urls = ["https://example.com/page1", "https://example.com/page2", "https://example.com/page1"]
for url in urls:
    if should_crawl(url):
        print(f"Crawling: {url}")
    else:
        print(f"Skipping duplicate: {url}")

# Production: use a Bloom filter (pybloom_live library)
# from pybloom_live import BloomFilter
# bloom = BloomFilter(capacity=1_000_000_000, error_rate=0.001)
# bloom.add(url)  # false positive rate 0.1%, uses ~1.2GB RAM for 1B URLs
```

Data pipelines (Apache Kafka, Spark) use hash sets to deduplicate streaming events,
ensuring exactly-once processing semantics.

---

## 4. Symbol Tables in Compilers

When a compiler processes source code, it builds a symbol table:
a hash map from identifier name (string) to metadata (type, memory address, scope).

```python
# Simplified symbol table for a compiler
symbol_table = {}

def declare_variable(name: str, var_type: str, address: int):
    if name in symbol_table:
        raise NameError(f"Variable '{name}' already declared")
    symbol_table[name] = {"type": var_type, "address": address, "initialized": False}

def assign_variable(name: str, value):
    if name not in symbol_table:
        raise NameError(f"Undefined variable '{name}'")
    symbol_table[name]["initialized"] = True
    symbol_table[name]["value"] = value

def lookup(name: str):
    return symbol_table.get(name)

declare_variable("x", "int", 0x1000)
assign_variable("x", 42)
print(lookup("x"))  # {"type": "int", "address": 4096, "initialized": True, "value": 42}
```

Every modern language runtime (CPython, JVM, V8) uses hash maps for variable lookups.
In Python, every function's local variables are stored in a `locals()` dict — a hash map.

---

## 5. DNS Resolution Cache

When your browser visits `google.com`, the OS checks its DNS cache before querying a DNS server.
This cache is a hash map: `domain -> (IP address, TTL)`.

```python
import time

# OS-level DNS cache simulation
dns_cache = {}

def dns_lookup(domain: str) -> str:
    now = time.time()

    if domain in dns_cache:
        ip, expires_at = dns_cache[domain]
        if now < expires_at:
            print(f"Cache HIT: {domain} -> {ip}")
            return ip
        else:
            del dns_cache[domain]
            print(f"Cache EXPIRED: {domain}")

    # Simulate querying a DNS resolver
    ip = query_dns_resolver(domain)
    ttl = 300  # 5-minute TTL from DNS record
    dns_cache[domain] = (ip, now + ttl)
    print(f"Cache MISS: resolved {domain} -> {ip}")
    return ip

def query_dns_resolver(domain: str) -> str:
    mock_dns = {"google.com": "142.250.80.46", "github.com": "140.82.121.4"}
    return mock_dns.get(domain, "0.0.0.0")
```

On macOS/Linux, `nscd` (name service cache daemon) implements exactly this pattern.
The `/etc/hosts` file is a static flat-file hash map loaded at boot.

---

## 6. Password Hashing — bcrypt and SHA

Cryptographic hash functions (SHA-256, bcrypt, Argon2) are one-way functions:
easy to compute `hash(password)`, computationally infeasible to reverse.

This is different from a hash map (which uses hashing for lookup, not security).
The concept is the same — deterministic mapping — but the goals differ.

```python
import hashlib
import bcrypt

password = "my_secure_password"

# SHA-256 — fast, NOT suitable alone for password storage
sha_hash = hashlib.sha256(password.encode()).hexdigest()
print(f"SHA-256: {sha_hash}")
# Fast to compute means attackers can try billions of guesses/second with GPUs

# bcrypt — slow by design (work factor = 12 means ~250ms per hash)
# This makes brute-force attacks infeasible
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
print(f"bcrypt: {hashed}")

# Verification — compare hash, never store plaintext
is_valid = bcrypt.checkpw(password.encode(), hashed)
print(f"Password valid: {is_valid}")  # True

# bcrypt also embeds the salt in the hash string itself
# Format: $2b$12$<22-char-salt><31-char-hash>
```

Key insight: bcrypt/Argon2 are intentionally slow (adaptive work factor).
SHA-256 is fast — used for data integrity, not passwords.

---

## 7. Consistent Hashing in Distributed Systems

In a distributed cache (Memcached cluster, DynamoDB, Cassandra), you need to decide
which server stores a given key. Naive approach: `server = hash(key) % N`.

Problem: when you add or remove a server (N changes), almost every key remaps.
This causes a cache stampede — all traffic hits the database at once.

Consistent hashing solution: place both servers and keys on a hash ring (circle of 2^32 positions).
Each key is stored on the first server clockwise from its position.
Adding/removing a server only remaps keys in the adjacent segment (~1/N keys).

```python
import hashlib
import bisect

class ConsistentHashRing:
    def __init__(self, replicas: int = 150):
        self.replicas = replicas  # virtual nodes per server
        self.ring = {}
        self.sorted_keys = []

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_server(self, server: str):
        for i in range(self.replicas):
            virtual_key = self._hash(f"{server}:{i}")
            self.ring[virtual_key] = server
            bisect.insort(self.sorted_keys, virtual_key)

    def remove_server(self, server: str):
        for i in range(self.replicas):
            virtual_key = self._hash(f"{server}:{i}")
            del self.ring[virtual_key]
            self.sorted_keys.remove(virtual_key)

    def get_server(self, key: str) -> str:
        if not self.ring:
            return None
        h = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, h) % len(self.sorted_keys)
        return self.ring[self.sorted_keys[idx]]

ring = ConsistentHashRing()
ring.add_server("cache-1")
ring.add_server("cache-2")
ring.add_server("cache-3")

print(ring.get_server("user:1001"))   # cache-2
print(ring.get_server("product:500")) # cache-1

ring.add_server("cache-4")  # Only ~25% of keys remap
print(ring.get_server("user:1001"))   # may shift, but most keys stay
```

Amazon DynamoDB, Apache Cassandra, and Riak all use consistent hashing variants.

---

## 8. Python Dict Internals — Open Addressing Hash Table

Python's `dict` is a hash table using open addressing with pseudo-random probing.
Understanding its internals explains Python performance characteristics.

Key facts:
- Load factor threshold: Python resizes (doubles) when the dict is 2/3 full.
- Collision resolution: uses a probe sequence based on the hash value, not linear probing.
- Since Python 3.7, dicts maintain insertion order (implementation detail promoted to spec in 3.7).
- Compact dict layout (Python 3.6+): indices array + dense entries array reduces memory usage.

```python
# Demonstrating Python dict collision behavior

# Python's hash for small integers is the integer itself
print(hash(1))    # 1
print(hash(2))    # 2

# Strings use SipHash (randomized per process for security)
print(hash("hello"))  # different every process run

# Custom class showing hash/eq contract
class BadHash:
    """All instances hash to the same bucket — worst case O(n) dict ops."""
    def __hash__(self):
        return 42  # every instance maps to slot 42 % table_size

    def __eq__(self, other):
        return self is other

d = {}
for i in range(5):
    d[BadHash()] = i  # Each collision forces probing to find next empty slot
print(f"Dict with 5 colliding keys: {len(d)} entries")

# Real dict sizing behavior
d = {}
import sys
sizes = []
for i in range(20):
    d[i] = i
    sizes.append(sys.getsizeof(d))

# Dict grows in steps: 8 -> 16 -> 32 -> 64 ...
unique_sizes = list(dict.fromkeys(sizes))
print(f"Dict size progression (bytes): {unique_sizes}")

# Hash table invariant: dict resizes when len > 2/3 * table_size
# This keeps average probe length close to 1 (fast lookups)
```

Why Python dicts are fast in practice:
- Integer and string keys have O(1) hash computation.
- The probe sequence converges quickly for typical load factors.
- CPython's dict is implemented in C with cache-line-friendly memory layout.

---

## Summary

| Use Case | Hash Structure | Why Hashing |
|---|---|---|
| Database index | Hash index | O(1) equality lookup |
| Redis/Memcached | Hash map in RAM | O(1) key-value access |
| Web crawler dedup | Hash set / Bloom filter | O(1) membership test |
| Compiler symbol table | Hash map | O(1) variable lookup |
| DNS cache | Hash map with TTL | O(1) domain resolution |
| Password storage | Cryptographic hash | One-way, irreversible |
| Distributed cache routing | Consistent hash ring | Minimal remapping on resize |
| Python dict | Open-addressing hash table | Language-level O(1) access |

Hashing is not just an interview topic.
It is the mechanism that makes O(1) lookup possible across every layer of the stack.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Collision Handling](./collision_handling.md) &nbsp;|&nbsp; **Next:** [Common Mistakes →](./common_mistakes.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Collision Handling](./collision_handling.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
