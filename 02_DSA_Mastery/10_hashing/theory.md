<a id="top"></a>
# 📘 10 – Hashing in Python

## 📖 Table of Contents

- [📌 Learning Priority](#learning-priority)
- [1. What Is Hashing?](#1-what-is-hashing)
  - [Visual: The Locker Room](#visual-locker-room)
  - [Visual: A Simple Hash Function](#visual-hash-function)
- [2. Hash Table Structure](#2-hash-table-structure)
- [3. Collision — The Core Challenge](#3-collision)
  - [Separate Chaining](#separate-chaining)
  - [Visual: Chaining in Detail](#visual-chaining)
  - [Open Addressing](#open-addressing)
  - [Visual: Linear Probing](#visual-probing)
- [4. Load Factor and Resizing](#4-load-factor)
  - [Visual: Load Factor and Crowding](#visual-load-factor)
- [5. Hashing in Python — Dict and Set](#5-hashing-python)
  - [Visual: Python Dict Internals](#visual-dict-internals)
- [6. Why Immutability Matters for Hashing](#6-immutability)
- [7. Common Hashing Patterns](#7-patterns)
  - [Visual: When to Reach for a Hash Map](#visual-when-hashmap)
  - [Group Anagrams Walkthrough](#group-anagrams)
  - [Two Sum Step by Step](#two-sum)
- [8. Hash Function Properties](#8-hash-properties)
- [🔥 Summary](#summary)

<a id="learning-priority"></a>
## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
hash function · collision resolution (chaining vs open addressing) · O(1) average operations

**Should Learn** — Important for real projects, comes up regularly:
load factor · resizing · Python dict and set internals

**Good to Know** — Useful in specific situations, not always tested:
hash table vulnerabilities · quadratic probing and double hashing

**Reference** — Know it exists, look up syntax when needed:
cryptographic hashing · bloom filters · consistent hashing · cuckoo hashing

Jaya is a librarian with 1 million books. When a reader asks for a specific title, she has two choices: walk through every shelf one by one (O(n) — minutes for a million books), or use her index card system that tells her the exact shelf number instantly (O(1) — one lookup). That index card system is **hashing** — a way to convert any key into a direct address. Today Jaya will learn how this magical system works, what goes wrong when two books point to the same shelf, and why hashing powers almost every fast lookup in computing.

<a id="1-what-is-hashing"></a>
# 1. What Is Hashing?

Jaya discovers that hashing is about one thing: **turning search into instant access**. Instead of scanning through data, you compute where the data should be — and go straight there.

A **hash function** takes a key and produces an index:

```
hash("apple")  → 4
hash("banana") → 7
```

This allows: Insert O(1) average, Search O(1) average, Delete O(1) average.

<a id="visual-locker-room"></a>
## Visual: The Locker Room

Jaya's library has a locker room with 100 lockers. Each book gets assigned a locker number based on its title. To find a book, she does not check lockers 0 through 99 — she computes the locker number from the title and goes straight there.

```
Without hashing (linear search):
  Check locker 0... nope
  Check locker 1... nope
  Check locker 2... nope
  ...
  Check locker 47... FOUND!
  Time: O(n) — checked 47 lockers

With hashing (direct access):
  hash("The Great Gatsby") → 47
  Go straight to locker 47 → FOUND!
  Time: O(1) — one calculation, one lookup
```

<a id="visual-hash-function"></a>
## Visual: A Simple Hash Function

The simplest hash function: add up ASCII values, take modulo table size.

```
"apple" → ASCII values:

a = 97
p = 112
p = 112
l = 108
e = 101
---------
Sum = 530

Table size = 10
530 mod 10 = 0

"apple" → index 0
```

```
"apple"
  │
  ▼
[a=97] + [p=112] + [p=112] + [l=108] + [e=101]
  │
  ▼
sum = 530
  │
  ▼
530 % 10 = 0
  │
  ▼
index 0
```

And "banana": `b=98 + a=97 + n=110 + a=97 + n=110 + a=97 = 609. 609 % 10 = 9 → index 9`.

> 📝 **Practice:** [Q2 · dict-vs-list-timing](./practice.md#q2--why-dict-lookup-is-o1-average) · [Q3 · O1-average-vs-On-worst](./practice.md#q3--o1-average-vs-on-worst-case)

> [↑ Back to Top](#top)

<a id="2-hash-table-structure"></a>
# 2. Hash Table Structure

Jaya builds her first hash table — an array where the hash function decides which slot each item goes into. It looks simple, but there is one critical problem lurking.

```
Index: 0 1 2 3 4 5 6 7
Value: - - - - A - - B
```

The hash function decides the index. But what happens when two keys produce the same index? That is called a **collision** — and solving it is the core challenge of hashing.

```
Operation    Average    Worst case
─────────────────────────────────
Insert       O(1)       O(n)  ← rare, happens during resize
Lookup       O(1)       O(n)  ← rare, terrible hash function
Delete       O(1)       O(n)  ← rare
```

In practice, treat all hash table operations as O(1).

> 📝 **Practice:** [Q9 · chaining-vs-open-addressing](./practice.md#q9--chaining-vs-open-addressing)

> [↑ Back to Top](#top)

<a id="3-collision"></a>
# 3. Collision — The Core Challenge

Jaya assigns two books to the same locker — `hash("cat") → 3` and `hash("tac") → 3`. Both want locker 3. She needs a plan for when this happens.

<a id="visual-collision"></a>
## Visual: What a Collision Looks Like

```
"abc"  → 97+98+99   = 294 → 294 % 7 = 0
"bca"  → 98+99+97   = 294 → 294 % 7 = 0

Hash Table (size 7):

Index:  [ 0 ] [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ]
         ↑↑
    "abc" and "bca" both want to go here!
    COLLISION!
```

Two main strategies:

<a id="separate-chaining"></a>
## Separate Chaining

Each index stores a linked list. Colliding items share the locker but form a chain.

<a id="visual-chaining"></a>
## Visual: Chaining in Detail

```
Hash Table with Chaining:

Index 0:  → ["abc"] → ["bca"] → None
Index 1:  → ["dog"] → None
Index 2:  → None
Index 3:  → ["cat"] → ["bat"] → ["rat"] → None
Index 4:  → None
Index 5:  → ["xyz"] → None
Index 6:  → None
```

Lookup "bca": hash → index 0 → walk chain: "abc"? No. "bca"? Yes!

Best case: O(1). Worst case: O(n) — everyone in the same chain.

<a id="open-addressing"></a>
## Open Addressing

If the slot is occupied, find the next available one.

Techniques: linear probing, quadratic probing, double hashing.

<a id="visual-probing"></a>
## Visual: Linear Probing

```
Inserting "abc" → index 0:
[ "abc" ] [     ] [     ] [     ] [     ] [     ] [     ]
  ↑ placed here

Inserting "bca" → also wants index 0, but it's TAKEN:
[ "abc" ] [     ] [     ] ...
  ↑ taken! try index 1...
[ "abc" ] [ "bca" ] [     ] ...
           ↑ placed here!
```

Lookup "bca": hash → index 0 → "abc" ≠ "bca" → try index 1 → "bca" = "bca" → Found!

> 📝 **Practice:** [Q80 · hash-collision-resolution](../dsa_practice_questions_100.md#q80--interview--hash-collision-resolution)

> [↑ Back to Top](#top)

<a id="4-load-factor"></a>
# 4. Load Factor and Resizing

Jaya notices that as more books fill the lockers, collisions become more frequent. The locker room gets crowded. The **load factor** measures this crowding: `elements / table_size`.

When load factor crosses a threshold (~0.7), the table resizes — creates a bigger table, rehashes everything. Expensive once, but keeps future operations fast.

<a id="visual-load-factor"></a>
## Visual: Load Factor and Crowding

```
Items: 3, Table size: 10  →  Load factor = 0.3  (30% full)
Items: 7, Table size: 10  →  Load factor = 0.7  (70% full)
Items: 9, Table size: 10  →  Load factor = 0.9  (90% full) ← danger zone
```

```
Load 0.3:  □□□■□□□□□□   ← few collisions, fast
Load 0.7:  ■□■■■□■■□■   ← some collisions, still ok
Load 0.9:  ■■■■■□■■■■   ← many collisions, slowing down
```

Python uses 2/3 as the threshold. This is why hash operations are amortized O(1).

> 📝 **Practice:** [Q10 · load-factor-and-resizing](./practice.md#q10--load-factor-and-resizing)

> [↑ Back to Top](#top)

<a id="5-hashing-python"></a>
# 5. Hashing in Python — Dict and Set

Jaya learns that Python's `dict` and `set` are both hash tables under the hood. Every time she writes `d["key"] = value`, Python hashes the key, finds the slot, and stores the value.

```python
d = {}
d["name"] = "Alice"
d["age"] = 25

print(d["name"])   # O(1) lookup
print("age" in d)  # O(1) membership check
```

```python
s = set()
s.add("apple")
s.add("banana")

print("apple" in s)   # O(1) — hash table lookup
```

<a id="visual-dict-internals"></a>
## Visual: Python Dict Internals

Python's dict uses **open addressing** with a randomized probe sequence (not simple linear probing). Each slot stores `(hash, key, value)`.

```
Python dict internal layout (simplified):

Slot 0: (hash=530, "apple", 4.99)
Slot 1: (empty)
Slot 2: (empty)
Slot 3: (hash=294, "cat", 7.50)
Slot 4: (empty)
Slot 5: (hash=609, "banana", 2.99)
Slot 6: (empty)
Slot 7: (empty)

Lookup "apple":
  1. hash("apple") → 530
  2. 530 % 8 = 2... check slot 2: empty? probe next
  3. Find slot 0: hash matches, key matches → return 4.99
```

Since Python 3.7, `dict` preserves insertion order. This is a guarantee, not an implementation detail.

Only **hashable** (immutable) objects can be dict keys or set members. Lists, dicts, and sets are NOT hashable — they are mutable.

> [↑ Back to Top](#top)

<a id="6-immutability"></a>
# 6. Why Immutability Matters for Hashing

Jaya understands why her locker system requires permanent labels — if a book's title could change after being assigned to a locker, the locker number would become wrong, and she would never find the book again.

In Python, dict keys and set members must be immutable because:
1. The hash is computed at insertion time
2. If the object changes, its hash changes
3. The object is now in the wrong slot — it becomes unfindable

```python
# Lists are mutable → NOT hashable
d = {}
d[[1, 2]] = "hello"   # TypeError: unhashable type: 'list'

# Tuples are immutable → hashable
d[(1, 2)] = "hello"   # works!
```

This is why strings are immutable — they need to be hashable for use as dict keys. Python caches the hash value of a string after first computation, making repeated lookups even faster.

> [↑ Back to Top](#top)

<a id="7-patterns"></a>
# 7. Common Hashing Patterns

Jaya discovers that hash maps are the Swiss Army knife of interview problems. Any time you need to count, group, or look up values quickly, a hash map is usually the answer.

<a id="visual-when-hashmap"></a>
## Visual: When to Reach for a Hash Map

```
Problem asks for...              Use...
─────────────────────────────────────────────
Count frequency of elements  →  Counter / dict
Find duplicates              →  set
Group by property            →  defaultdict(list)
Two sum / pair finding       →  dict (complement lookup)
Check membership             →  set (O(1) vs list O(n))
```

<a id="group-anagrams"></a>
## Group Anagrams Walkthrough

```
Input: ["eat", "tea", "tan", "ate", "nat", "bat"]

Step 1: Sort each word → use as key
  "eat" → "aet"
  "tea" → "aet"
  "tan" → "ant"
  "ate" → "aet"
  "nat" → "ant"
  "bat" → "abt"

Step 2: Group by sorted key
  "aet" → ["eat", "tea", "ate"]
  "ant" → ["tan", "nat"]
  "abt" → ["bat"]
```

```python
from collections import defaultdict

def group_anagrams(strs):
    groups = defaultdict(list)
    for s in strs:
        key = tuple(sorted(s))
        groups[key].append(s)
    return list(groups.values())
```

## Counter — Frequency Made Easy

```python
from collections import Counter

text = "mississippi"
freq = Counter(text)
print(freq)
# Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})

print(freq.most_common(2))  # [('i', 4), ('s', 4)]
```

<a id="two-sum"></a>
## Two Sum Step by Step

Jaya's most famous interview problem: find two numbers that add up to a target.

```
nums = [2, 7, 11, 15], target = 9

Brute force: check every pair → O(n²)
Hash map: for each number, check if (target - number) exists → O(n)
```

```
Step 1: num=2, complement=9-2=7
  seen = {}
  7 not in seen → add {2: 0}

Step 2: num=7, complement=9-7=2
  seen = {2: 0}
  2 IS in seen! → return [0, 1]
```

```python
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
```

> [↑ Back to Top](#top)

<a id="8-hash-properties"></a>
# 8. Hash Function Properties

Jaya learns what makes a good hash function — it must distribute keys evenly across the table to minimize collisions.

A good hash function must be:
- **Deterministic** — same input always produces same output
- **Uniform** — distributes keys evenly across the table
- **Fast** — O(1) to compute
- **Minimizes collisions** — different inputs produce different outputs (ideally)

A bad hash function (e.g., always returning 0) turns the hash table into a linked list — O(n) for everything.

> [↑ Back to Top](#top)

<a id="summary"></a>
## 🔥 Summary

| Concept | Key Takeaway |
|---------|-------------|
| Hashing | Convert key → index for O(1) access |
| Hash function | Must be deterministic, uniform, fast |
| Collision | Two keys → same index. Solve with chaining or probing |
| Chaining | Linked list at each slot |
| Open addressing | Find next available slot |
| Load factor | elements/size — resize when > ~0.7 |
| Python dict/set | Hash tables. Keys must be immutable (hashable) |
| Immutability | Mutable keys break hash tables — object becomes unfindable |
| Two Sum | Complement lookup with hash map — O(n) |

**Space-time trade-off:** Hash tables trade memory for speed. They use extra space (the table array + overhead) to achieve O(1) time. This is the fundamental deal.

**Worst case:** If every key hashes to the same index, the table degrades to O(n). This happens with adversarial inputs or terrible hash functions. Python mitigates this with randomized hashing (hash randomization since Python 3.3).

**Real-world usage:**
- **Databases** — hash indexes for O(1) lookups
- **Caching** — Redis, Memcached, LRU cache
- **Compilers** — symbol tables
- **Networking** — routing tables, load balancers (consistent hashing)
- **Security** — password hashing (bcrypt, SHA-256)
- **Deduplication** — detecting duplicate files

**When NOT to use hashing:**
- Order matters (use sorted tree instead)
- Sorted traversal required (hash tables are unordered)
- Memory is highly constrained (hash tables have overhead)

> A hash table is a locker room where the locker number is calculated from your key, not searched for. Direct access. No searching. That is why it is O(1).

> 📝 **Practice:** [Q21 · design-hashmap-from-scratch](./practice.md#q21--design-hashmap-from-scratch) · [Q22 · design-hashset-from-scratch](./practice.md#q22--design-hashset-from-scratch)

# 🔁 Navigation

**[🏠 Back to README](../README.md)**

| Direction | Module |
|---|---|
| ⬅ Prev Module | [09_queue → theory.md](../09_queue/theory.md) |
| ➡ Next Module | [11_two_pointers → theory.md](../11_two_pointers/theory.md) |

**This folder:**
[theory.md](./theory.md) · [Practice](./practice.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)

**Related modules:**
[09 Queue →](../09_queue/theory.md) · [11 Two Pointers →](../11_two_pointers/theory.md) · [03 Strings →](../03_strings/theory.md) · [15 BST →](../15_binary_search_trees/theory.md)

**Jump to specific topics in other files:**
- Anagram detection with hashing → [03_strings § Anagram Detection](../03_strings/theory.md#anagram-detection)
- Two Sum variations → [11_two_pointers § theory.md](../11_two_pointers/theory.md)
- Hash map in graph algorithms → [18_graphs § theory.md](../18_graphs/theory.md)
- LRU Cache (hash map + linked list) → [07_linked_list § Real-World Impact](../07_linked_list/theory.md#8-real-world)

> [↑ Back to Top](#top)
