<a id="top"></a>
# Hashing — The Power of Instant Lookup

> Hashing is about one thing:
>
> **Turning search into instant access.**
>
> Without hashing, many real-world systems would be painfully slow.

Hashing is not just a data structure.
It is a strategy to reduce lookup time.

## 📖 Table of Contents

1. [Real Life Analogy — Library Without and With Hashing](#1-real-life-analogy)
2. [What Is Hashing?](#2-what-is-hashing)
3. [Hash Table Structure](#3-hash-table-structure)
4. [Collision — The Core Challenge](#4-collision)
5. [Load Factor](#5-load-factor)
6. [Hashing in Python (Dictionary and Set)](#6-hashing-in-python)
7. [Why Strings Are Immutable (Connection to Hashing)](#7-why-strings-are-immutable)
8. [Common Hashing Patterns in Interviews](#8-common-hashing-patterns)
9. [Example — Two Sum](#9-example-two-sum)
10. [Space-Time Trade-Off](#10-space-time-trade-off)
11. [Worst Case of Hashing](#11-worst-case-of-hashing)
12. [Hash Function Properties](#12-hash-function-properties)
13. [Real-World Usage of Hashing](#13-real-world-usage)
14. [When NOT to Use Hashing](#14-when-not-to-use-hashing)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
hash function · collision resolution (chaining vs open addressing) · O(1) average operations

**Should Learn** — Important for real projects, comes up regularly:
load factor · resizing · Python dict and set internals

**Good to Know** — Useful in specific situations, not always tested:
hash table vulnerabilities · quadratic probing and double hashing

**Reference** — Know it exists, look up syntax when needed:
cryptographic hashing · bloom filters · consistent hashing · cuckoo hashing

<a id="1-real-life-analogy"></a>
# 1. Real Life Analogy — Library Without and With Hashing

Imagine a library with 1 million books.

### Without Hashing

You search for a book by scanning shelves one by one.

Time grows as number of books grows.

This is linear search → O(n)

### With Hashing

Each book has a unique code.
You directly go to that shelf.

Instant access.

That is hashing.

Instead of searching,
you compute the location.

## Visual: The Locker Room

Imagine you work at a gym. Every morning, 500 members walk in and need to find their locker.

**Bad approach (Linear Search):** "Is this locker yours? No. Is this one? No. Is this one?..."
That could take 500 checks. Terrible.

**Good approach (Hashing):** Each member's name goes through a formula that spits out a locker number.
You walk straight to your locker. No searching. Done.

That formula? That's the **hash function**.
That locker room? That's the **hash table**.

```
Your Name  →  [ Hash Function ]  →  Locker Number

"Alice"    →  [ magic math  ]   →  Locker 3
"Bob"      →  [ magic math  ]   →  Locker 17
"Charlie"  →  [ magic math  ]   →  Locker 42
```

The hash function takes any input and returns a number (the index).

Two golden rules:
1. Same input ALWAYS gives same output (deterministic)
2. Output is always a valid index (bounded)

```
"Alice"  →  hash  →  3     ← always 3, every single time
"Alice"  →  hash  →  3     ← yep, still 3
"Alice"  →  hash  →  3     ← you get the idea
```

> [↑ Back to Top](#top)

<a id="2-what-is-hashing"></a>
# 2. What Is Hashing?

Hashing uses a function called a **hash function**.

The hash function:

Input → Key
Output → Index

Example:

```
hash("apple") → 4
hash("banana") → 7
```

Index tells where data should be stored.

This allows:

Insertion → O(1) average
Search → O(1) average
Deletion → O(1) average

Hashing is about fast lookup.

## Visual: O(1) Lookup — Why It's So Fast

The locker room has 100 lockers (indices 0-99).

You need locker 17.

```
Lockers:  [0] [1] [2] ... [17] ... [99]
                           ↑
                    go directly here
```

You don't check lockers 0 through 16. You don't check 18 through 99.
You walk straight to 17.

That's O(1). Constant time. Doesn't matter if you have 100 lockers or 1,000,000 lockers.

## Visual: A Simple Hash Function — Watching "apple" Get Hashed

Here's the simplest possible hash function:
- Add up all the ASCII values of the characters
- Take the result mod the table size

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

Step by step:

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

And "banana":

```
b=98, a=97, n=110, a=97, n=110, a=97
Sum = 609
609 % 10 = 9  →  index 9
```

> 📝 **Practice:** [Q2 · dict-vs-list-timing](./practice.md#q2--why-dict-lookup-is-o1-average) · [Q3 · O1-average-vs-On-worst](./practice.md#q3--o1-average-vs-on-worst-case)

> [↑ Back to Top](#top)

<a id="3-hash-table-structure"></a>
# 3. Hash Table Structure

Internally:

```
Index: 0 1 2 3 4 5 6 7
Value: - - - - A - - B
```

Hash function decides index.

But there is a problem.

Two keys may produce same index.

That is called collision.

## Visual: Hash Table Time Complexity Summary

```
Operation    Average    Worst case
─────────────────────────────────
Insert       O(1)       O(n)  ← rare, happens during resize
Lookup       O(1)       O(n)  ← rare, terrible hash function
Delete       O(1)       O(n)  ← rare
```

The worst case rarely happens with good hash functions.
In practice, treat all hash table operations as O(1).

> 📝 **Practice:** [Q9 · chaining-vs-open-addressing](./practice.md#q9--chaining-vs-open-addressing)

> [↑ Back to Top](#top)

<a id="4-collision"></a>
# 4. Collision — The Core Challenge

Example:

```
hash("cat") → 3
hash("tac") → 3
```

Both want index 3.

We must resolve collision.

Two main strategies:

## Visual: What a Collision Looks Like

```
"abc"  → 97+98+99   = 294 → 294 % 7 = 0
"bca"  → 98+99+97   = 294 → 294 % 7 = 0
```

Both "abc" and "bca" want the same index:

```
Hash Table (size 7):

Index:  [ 0 ] [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ]
         ↑↑
    "abc" and "bca" both want to go here!
    COLLISION!
```

Real hash functions are much cleverer (they use bit mixing, prime numbers, etc.),
but collisions can still happen. So we need a plan.

## 🔹 Separate Chaining

Each index stores a linked list.

```
Index 3 → cat → tac → act
```

## Visual: Chaining in Detail

Instead of one item per locker, each locker holds a **linked list**.
When two things collide, they share the same locker but form a chain.

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

When you look up "bca":
1. Hash "bca" → index 0
2. Walk the chain at index 0: "abc"? No. "bca"? Yes! Found it.

**Best case:** O(1) — you're the only one in your locker
**Worst case:** O(n) — everyone collided into the same locker (terrible hash function)

Time complexity:
O(1) average
O(n) worst case

## 🔹 Open Addressing

If index occupied,
find next available slot.

Techniques:
- Linear probing
- Quadratic probing
- Double hashing

## Visual: Open Addressing (Linear Probing)

If locker 0 is taken, try locker 1. If that's taken, try locker 2. And so on.

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

Lookup "bca":
1. Hash → index 0
2. Check index 0: "abc" ≠ "bca"
3. Check index 1: "bca" = "bca" — Found!

> 📝 **Practice:** [Q80 · hash-collision-resolution](../dsa_practice_questions_100.md#q80--interview--hash-collision-resolution)

> [↑ Back to Top](#top)

<a id="5-load-factor"></a>
# 5. Load Factor

Load factor = (number of elements) / (table size)

If load factor becomes high:
Collisions increase.

When load factor crosses threshold (e.g., 0.7):
Table resizes.

Resizing:
- Create bigger table
- Rehash all elements

This is why hash operations are amortized O(1).

## Visual: Load Factor and Crowding

```
Items: 3, Table size: 10  →  Load factor = 0.3  (30% full)
Items: 7, Table size: 10  →  Load factor = 0.7  (70% full)
Items: 9, Table size: 10  →  Load factor = 0.9  (90% full) ← danger zone
```

As load factor increases, collisions get more frequent:

```
Load 0.3:  □□□■□□□□□□   ← few collisions, fast
Load 0.7:  ■□■■■□■■□■   ← some collisions, still ok
Load 0.9:  ■■■■■□■■■■   ← many collisions, slowing down
```

Rule of thumb: keep load factor below 0.75 (Python uses 2/3 as the threshold).

When you hit the threshold, the table resizes (doubles in size) and rehashes everything.
Expensive once, but it keeps future operations fast.

> 📝 **Practice:** [Q10 · load-factor-and-resizing](./practice.md#q10--load-factor-and-resizing)

> [↑ Back to Top](#top)

<a id="6-hashing-in-python"></a>
# 6. Hashing in Python (Dictionary and Set)

Python provides:

- dict
- set

Both use hash tables internally.

Example:

```python
d = {}
d["apple"] = 10
```

Lookup:

```python
d["apple"]
```

Average:
O(1)

## Visual: Python Dict Internals — Open Addressing Done Right

Python's `dict` uses open addressing (not chaining).

```python
d = {}
d["name"] = "Alice"   # hash("name") → some index
d["age"]  = 30        # hash("age")  → different index
d["city"] = "NYC"     # hash("city") → different index
```

Under the hood:

```
Python dict internal array:

Slot 0:  empty
Slot 1:  empty
Slot 2:  hash=..., key="age",  value=30
Slot 3:  empty
Slot 4:  hash=..., key="name", value="Alice"
Slot 5:  empty
Slot 6:  hash=..., key="city", value="NYC"
Slot 7:  empty
```

**Why Python 3.7+ preserves insertion order:**

Python 3.7 added a separate compact array that tracks insertion order.
The hash table slots still hold the data, but a second array remembers the order you inserted.

```
Insertion order array: ["name", "age", "city"]  ← remembers this order
Hash table:            scrambled by hash values  ← fast lookup
```

When you iterate, Python follows the insertion order array. Best of both worlds.

**Common mistake — Counter subtraction drops data:** `Counter(a) - Counter(b)` silently drops all zero and negative counts, causing silent data loss. Use `.subtract()` to preserve the full picture, or use an explicit loop over `needed.items()` for checking whether one string can be built from another.

**Common mistake — KeyError on first increment:** Writing `counts[key] += 1` on a plain `dict` raises `KeyError` the first time a key appears. Use `counts.get(key, 0) + 1`, `defaultdict(int)`, or `Counter` instead.

**Common mistake — modifying a dict during iteration:** Deleting keys from a dict while looping over it raises `RuntimeError: dictionary changed size during iteration`. Collect the keys to delete first (`[k for k in d if ...]`), then delete them, or build a new dict with a comprehension.

> 📝 **Practice:** [Q20 · hash-map-vs-hash-set](../dsa_practice_questions_100.md#q20--critical--hash-map-vs-hash-set) · [Q86 · production-wrong-data-structure](../dsa_practice_questions_100.md#q86--design--production-wrong-data-structure)
> 📝 **Practice:** [Q11 · python-dict-internals](./practice.md#q11--python-dict-internals--open-addressing) · [Q12 · set-operations](./practice.md#q12--python-set-operations--union-intersection-difference)

> [↑ Back to Top](#top)

<a id="7-why-strings-are-immutable"></a>
# 7. Why Strings Are Immutable (Connection to Hashing)

Hash tables require keys to be immutable.

Why?

If key changes after hashing,
its index becomes incorrect.

That's why:

- Strings → immutable
- Tuples → hashable
- Lists → not hashable

Understanding this shows depth.

**Common mistake — using a list as a dict key:** Lists are mutable, so they cannot be hashed. `d[[1, 2, 3]] = "value"` raises `TypeError: unhashable type: 'list'`. Convert with `tuple([1, 2, 3])` when order matters, or `frozenset([1, 2, 3])` when it does not.

**Common mistake — using `sorted(word)` as a dict key:** `sorted()` returns a list, which is not hashable. Convert it to a string with `"".join(sorted(word))` or to a tuple with `tuple(sorted(word))` before using it as a key.

| Key type | Hashable | Use when |
|---|---|---|
| `tuple(lst)` | Yes | Order matters (e.g., anagram grouping) |
| `frozenset(lst)` | Yes | Order does NOT matter |
| `"".join(sorted(lst))` | Yes | String-based canonical form |

> 📝 **Practice:** [Q4 · hashability-rules](./practice.md#q4--hashability-rules--what-can-be-a-key) · [Q13 · frozenset-as-dict-key](./practice.md#q13--frozenset-as-dict-key)

> [↑ Back to Top](#top)

<a id="8-common-hashing-patterns"></a>
# 8. Common Hashing Patterns in Interviews

Most problems using hashing involve:

- Frequency counting
- Duplicate detection
- Two-sum problem
- Anagram checking
- Subarray sum
- Grouping elements

Hashing reduces nested loops.

## Visual: When to Reach for a Hash Map

```
Question you're asking          →   Use a hash map for

"Have I seen X before?"         →   Set or dict (membership check)
"How many times have I seen X?" →   Counter or dict
"What was X paired with?"       →   Dict (key→value store)
"Group things by property Y"    →   defaultdict(list) keyed by Y
"Find complement in array"      →   Dict (Two Sum pattern)
```

## Visual: Group Anagrams Walkthrough

Group words that are anagrams of each other.

**Input:** `["eat", "tea", "tan", "ate", "nat", "bat"]`
**Output:** `[["eat","tea","ate"], ["tan","nat"], ["bat"]]`

**The insight:** Two words are anagrams if and only if they have the same sorted characters.

```
"eat" → sorted → "aet"
"tea" → sorted → "aet"
"ate" → sorted → "aet"    ← all three map to the same key!

"tan" → sorted → "ant"
"nat" → sorted → "ant"    ← these two map to the same key!

"bat" → sorted → "abt"    ← alone
```

Step by step:

```
See "eat" → key "aet" → map: {"aet": ["eat"]}
See "tea" → key "aet" → map: {"aet": ["eat", "tea"]}
See "tan" → key "ant" → map: {"aet": ["eat","tea"], "ant": ["tan"]}
See "ate" → key "aet" → map: {"aet": ["eat","tea","ate"], "ant": ["tan"]}
See "nat" → key "ant" → map: {"aet": ["eat","tea","ate"], "ant": ["tan","nat"]}
See "bat" → key "abt" → map: {"aet": [...], "ant": [...], "abt": ["bat"]}

Final: values of the map = [[...], [...], [...]]
```

## Visual: Counter — Frequency Made Easy

Python's `Counter` is a hash map that counts things automatically.

```python
from collections import Counter

Counter("mississippi")
# Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})
```

Visually, it builds this map:

```
"mississippi"
  m → 1
  i → 4  (positions 1, 4, 7, 10)
  s → 4  (positions 2, 3, 5, 6)
  p → 2  (positions 8, 9)

Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})
```

Use cases:
- Word frequency counting
- Anagram detection: `Counter("eat") == Counter("tea")` → True
- Finding the most common element: `.most_common(1)`

> 📝 **Practice:** [Q5 · frequency-counting](./practice.md#q5--frequency-counting-with-a-dict) · [Q7 · seen-set-pattern](./practice.md#q7--seen-set-pattern--duplicate-detection) · [Q8 · complement-lookup-two-sum](./practice.md#q8--complement-lookup--two-sum) · [Q14 · anagram-grouping](./practice.md#q14--anagram-grouping)

> [↑ Back to Top](#top)

<a id="9-example-two-sum"></a>
# 9. Example — Two Sum

Without hashing:

Double loop → O(n²)

With hashing:

Store visited numbers in set/dictionary.

For each element:
Check if (target - current) exists.

Time:
O(n)

Hashing transforms problem.

## Visual: Two Sum Step by Step

Classic problem. Given an array and a target, find two numbers that add up to the target.

**Input:** `[2, 7, 11, 15]`, target = `9`
**Output:** indices `[0, 1]` (because 2 + 7 = 9)

**The naive approach (O(n²)):** check every pair.

```
Pairs to check:
(2,7), (2,11), (2,15), (7,11), (7,15), (11,15)
That's 6 checks for 4 items. For 1000 items → 499,500 checks. Yikes.
```

**The hash map approach (O(n)):**

For each number, ask: "Is there a number I've already seen that completes the pair?"

That question translates to: "Does `target - current_number` exist in my map?"

```
Step 1: See 2
  - Need: 9 - 2 = 7. Is 7 in map? { } → No.
  - Store: {2: index_0}

  Map: {2: 0}

Step 2: See 7
  - Need: 9 - 7 = 2. Is 2 in map? {2: 0} → YES!
  - Return: [map[2], current_index] = [0, 1]

  Done! Found [0, 1]
```

```
Array:  [  2  ,  7  , 11  , 15  ]
         ↑
         current

Map: {}
Need (9-2)=7 in map? No.
Store 2→0.

Array:  [  2  ,  7  , 11  , 15  ]
                 ↑
                 current

Map: {2: 0}
Need (9-7)=2 in map? YES → return [0, 1]
```

**Common mistake — Two Sum self-pairing:** Using `seen = set(nums)` (values only) lets the same element pair with itself when `target == 2 * nums[i]`. Always store `value → index` in a dict, and insert the current element **after** the lookup so the current index can never pair with itself.

> 📝 **Practice:** [Q8 · two-sum](./practice.md#q8--complement-lookup--two-sum)

> [↑ Back to Top](#top)

<a id="10-space-time-trade-off"></a>
# 10. Space-Time Trade-Off

Hashing trades space for speed.

You use extra memory
to reduce time complexity.

Senior-level understanding:
Always consider memory constraints.

> 📝 **Practice:** [Q6 · set-membership-beats-list](./practice.md#q6--set-membership-beats-list-lookup)

> [↑ Back to Top](#top)

<a id="11-worst-case-of-hashing"></a>
# 11. Worst Case of Hashing

If many collisions occur:

Hash table degrades to linked list.

Worst case:
O(n)

Good hash function minimizes collision probability.

> 📝 **Practice:** [Q3 · O1-average-vs-On-worst](./practice.md#q3--o1-average-vs-on-worst-case) · [Q25 · hash-table-vulnerability](./practice.md#q25--hash-table-vulnerability--adversarial-inputs)

> [↑ Back to Top](#top)

<a id="12-hash-function-properties"></a>
# 12. Hash Function Properties

A good hash function should:

- Be fast
- Distribute keys uniformly
- Minimize collisions
- Be deterministic

Poor hash functions cause performance issues.

> 📝 **Practice:** [Q25 · hash-table-vulnerability](./practice.md#q25--hash-table-vulnerability--adversarial-inputs)

> [↑ Back to Top](#top)

<a id="13-real-world-usage"></a>
# 13. Real-World Usage of Hashing

Hashing powers:

- Database indexing
- Caching systems
- Password storage (hashed)
- Routing tables
- Compilers (symbol tables)
- Blockchain (cryptographic hashing)

Hashing is foundational to modern computing.

> 📝 **Practice:** [Q23 · lru-cache](./practice.md#q23--lru-cache--hashmap--doubly-linked-list) · [Q24 · consistent-hashing](./practice.md#q24--consistent-hashing-concept)

> [↑ Back to Top](#top)

<a id="14-when-not-to-use-hashing"></a>
# 14. When NOT to Use Hashing

Avoid hashing when:

- Order matters
- Sorted traversal required
- Memory is highly constrained
- Deterministic iteration order needed

Use tree-based structures instead.

> 📝 **Practice:** [Q21 · design-hashmap-from-scratch](./practice.md#q21--design-hashmap-from-scratch) · [Q22 · design-hashset-from-scratch](./practice.md#q22--design-hashset-from-scratch)

> [↑ Back to Top](#top)

# Final Understanding

Hashing:

- Enables instant lookup
- Uses hash function to compute index
- Handles collisions carefully
- Trades memory for speed
- Powers dictionaries and sets

It is one of the most powerful tools in algorithm design.

If you master hashing,
many medium-level problems become easy.

## The One-Liner Mental Model

> A hash table is a locker room where the locker number is calculated from your key,
> not searched for. Direct access. No searching. That's why it's O(1).

**[🏠 Back to README](../README.md)**

**Prev:** [← Queue — Interview Q&A](../09_queue/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheetsheet.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) · [Practice](./practice.md) · [Collision Handling](./collision_handling.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md)
