# Hashing: The Magic Locker Room

---

## The Story Begins

Imagine you work at a gym. Every morning, 500 members walk in and need to find their locker.

**Bad approach (Linear Search):** "Is this locker yours? No. Is this one? No. Is this one?..."
That could take 500 checks. Terrible.

**Good approach (Hashing):** Each member's name goes through a formula that spits out a locker number.
You walk straight to your locker. No searching. Done.

That formula? That's the **hash function**.
That locker room? That's the **hash table**.

---

## The Magic Formula

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

---

## O(1) Lookup: Why It's So Fast

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

---

## A Simple Hash Function: Let's Watch "apple" Get Hashed

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

Visually:

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

Let's try "banana":

```
b=98, a=97, n=110, a=97, n=110, a=97
Sum = 609
609 % 10 = 9  →  index 9
```

---

## The Problem: Collisions (Two Lockers, Same Number)

What if two different names hash to the same locker?

```
"banana" → 609 % 10 = 9
"orange" → 642 % 10 = 2

Hmm, those are different. Let's try another example.

"listen" → sum = 107+105+115+116+101+110 = 654 → 654 % 10 = 4
"silent" → sum = 115+105+108+101+110+116 = 655 → 655 % 10 = 5

Fine so far. Let's cook up a collision:

"abc"  → 97+98+99   = 294 → 294 % 7 = 0
"bca"  → 98+99+97   = 294 → 294 % 7 = 0
```

Both "abc" and "bca" want locker 0. That's a collision.

```
Hash Table (size 7):

Index:  [ 0 ] [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ]
         ↑↑
    "abc" and "bca" both want to go here!
    COLLISION!
```

Real hash functions are much cleverer (they use bit mixing, prime numbers, etc.),
but collisions can still happen. So we need a plan.

---

## Collision Strategy 1: Chaining (Each Locker Has a Shelf)

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

---

## Collision Strategy 2: Open Addressing (Try the Next Locker)

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

This is called **linear probing**.

```
Lookup "bca":
1. Hash → index 0
2. Check index 0: "abc" ≠ "bca"
3. Check index 1: "bca" = "bca" ✓ Found!
```

---

## Load Factor: When the Locker Room Gets Too Crowded

**Load factor = (number of items) / (table size)**

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

Rule of thumb: **keep load factor below 0.75** (Python uses 2/3 as the threshold).

When you hit the threshold, the table **resizes** (doubles in size) and rehashes everything.
Expensive once, but it keeps future operations fast.

---

## Python Dict Internals: Open Addressing Done Right

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

---

## Problem Walkthrough: Two Sum

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

The hash map lets us check "have I seen 2 before?" in O(1) instead of scanning the array again.

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

---

## Problem Walkthrough: Group Anagrams

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

Use the sorted version as a hash map key:

```
Step by step:

See "eat" → key "aet" → map: {"aet": ["eat"]}
See "tea" → key "aet" → map: {"aet": ["eat", "tea"]}
See "tan" → key "ant" → map: {"aet": ["eat","tea"], "ant": ["tan"]}
See "ate" → key "aet" → map: {"aet": ["eat","tea","ate"], "ant": ["tan"]}
See "nat" → key "ant" → map: {"aet": ["eat","tea","ate"], "ant": ["tan","nat"]}
See "bat" → key "abt" → map: {"aet": [...], "ant": [...], "abt": ["bat"]}

Final: values of the map = [[...], [...], [...]]
```

---

## Quick Tool: Counter

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

---

## Summary: When to Reach for a Hash Map

```
Question you're asking          →   Use a hash map for

"Have I seen X before?"         →   Set or dict (membership check)
"How many times have I seen X?" →   Counter or dict
"What was X paired with?"       →   Dict (key→value store)
"Group things by property Y"    →   defaultdict(list) keyed by Y
"Find complement in array"      →   Dict (Two Sum pattern)
```

**Time complexity:**

```
Operation    Average    Worst case
─────────────────────────────────
Insert       O(1)       O(n)  ← rare, happens during resize
Lookup       O(1)       O(n)  ← rare, terrible hash function
Delete       O(1)       O(n)  ← rare
```

The worst case rarely happens with good hash functions.
In practice, treat all hash table operations as O(1).

---

## The One-Liner Mental Model

> A hash table is a locker room where the locker number is calculated from your key,
> not searched for. Direct access. No searching. That's why it's O(1).

If you remember nothing else, remember that.
