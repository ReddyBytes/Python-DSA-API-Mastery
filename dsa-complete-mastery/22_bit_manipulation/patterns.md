# Bit Manipulation Patterns — The Bit Tricks Playbook

---

## The Story First

Computers speak binary. Every integer you write in Python — 42, 255, 1024 — is stored as a sequence of 0s and 1s. Bit manipulation lets you work directly with those 0s and 1s, bypassing arithmetic entirely.

Why does this matter? Because bit operations are the fastest operations a CPU can perform. And more importantly for interviews: they unlock elegant O(1) or O(log N) solutions to problems that would otherwise take much longer.

Think of a number's bits like a row of light switches. Each switch is either ON (1) or OFF (0). Bit manipulation lets you flip a specific switch, check if a switch is on, turn all switches off except one, and so on — all in a single CPU instruction.

```
Number 42:
Decimal:  42
Binary:   0 0 1 0 1 0 1 0
Position: 7 6 5 4 3 2 1 0

Switch positions:  7=OFF, 5=ON, 3=ON, 1=ON → 32 + 8 + 2 = 42
```

This document covers 8 core patterns. Master them and you'll handle any bit manipulation problem an interviewer throws at you.

---

## Python Bit Manipulation Caveat

Python integers are arbitrary precision — there's no 32-bit overflow. This is both a blessing and a curse:
- Blessing: no overflow errors to worry about
- Curse: some C-style tricks (like `n >> 31` for sign bit) don't work the same way

When a problem says "assume 32-bit integer", you may need to mask with `& 0xFFFFFFFF` to simulate overflow behavior. This guide will flag those cases explicitly.

---

## Pattern 1: Check / Set / Clear / Toggle a Bit

### The Four Fundamental Operations

These are your bread and butter. If you know nothing else about bits, know these four.

```
Number n, bit position i (0 = rightmost/least significant):

     n = ... b7 b6 b5 b4 b3 b2 b1 b0
                                 ↑
                             position i=1
```

#### Operation 1: CHECK — Is bit i set?

```
Formula: (n >> i) & 1

How it works:
  1. Shift n right by i positions → bit i is now at position 0
  2. AND with 1 → isolates the last bit → gives 0 or 1

Example: n = 42 = 00101010, check bit 3:
  42 >> 3 = 00000101 = 5
  5 & 1   = 00000001 = 1  → bit 3 is SET

Example: n = 42 = 00101010, check bit 4:
  42 >> 4 = 00000010 = 2
  2 & 1   = 00000000 = 0  → bit 4 is NOT SET

Visual:
  n:         0 0 1 0 1 0 1 0
  shift >>3: 0 0 0 0 0 1 0 1
  AND 1:     0 0 0 0 0 0 0 1   → result = 1 (bit was set)
```

#### Operation 2: SET — Turn bit i ON

```
Formula: n | (1 << i)

How it works:
  1. Create a mask with only bit i set: 1 << i
  2. OR with n → forces bit i to 1, leaves all other bits unchanged

Example: n = 42 = 00101010, set bit 4:
  1 << 4     = 00010000 = 16
  42 | 16    = 00111010 = 58

Visual:
  n:         0 0 1 0 1 0 1 0
  1<<4:      0 0 0 1 0 0 0 0
  OR:        0 0 1 1 1 0 1 0   → 58
```

#### Operation 3: CLEAR — Turn bit i OFF

```
Formula: n & ~(1 << i)

How it works:
  1. Create mask with only bit i set: 1 << i
  2. Flip all bits: ~(1 << i) → all 1s except position i
  3. AND with n → forces bit i to 0, leaves all other bits unchanged

Example: n = 42 = 00101010, clear bit 3:
  1 << 3     = 00001000 = 8
  ~8         = 11110111 (complement)
  42 & ~8    = 00100010 = 34

Visual:
  n:         0 0 1 0 1 0 1 0
  ~(1<<3):   1 1 1 1 0 1 1 1
  AND:       0 0 1 0 0 0 1 0   → 34
```

#### Operation 4: TOGGLE — Flip bit i

```
Formula: n ^ (1 << i)

How it works:
  1. Create mask with only bit i set: 1 << i
  2. XOR with n → bit i flips (0→1, 1→0), all other bits unchanged
  (XOR with 0 = no change; XOR with 1 = flip)

Example: n = 42 = 00101010, toggle bit 5:
  1 << 5     = 00100000 = 32
  42 ^ 32    = 00001010 = 10    (bit 5 was ON, now OFF)

Example: n = 10 = 00001010, toggle bit 5:
  1 << 5     = 00100000 = 32
  10 ^ 32    = 00101010 = 42    (bit 5 was OFF, now ON)

Visual:
  n=42:      0 0 1 0 1 0 1 0
  1<<5:      0 0 1 0 0 0 0 0
  XOR:       0 0 0 0 1 0 1 0   → 10 (bit 5 flipped OFF)
```

### All Four in Code

```python
def check_bit(n: int, i: int) -> int:
    """Return 1 if bit i is set, else 0."""
    return (n >> i) & 1

def set_bit(n: int, i: int) -> int:
    """Return n with bit i forced to 1."""
    return n | (1 << i)

def clear_bit(n: int, i: int) -> int:
    """Return n with bit i forced to 0."""
    return n & ~(1 << i)

def toggle_bit(n: int, i: int) -> int:
    """Return n with bit i flipped."""
    return n ^ (1 << i)


# Demo
n = 42  # 00101010
print(f"n = {n} = {bin(n)}")
print(f"Bit 3 is: {check_bit(n, 3)}")   # 1 (set)
print(f"Bit 4 is: {check_bit(n, 4)}")   # 0 (not set)
print(f"Set bit 4: {set_bit(n, 4)} = {bin(set_bit(n, 4))}")      # 58 = 0b111010
print(f"Clear bit 3: {clear_bit(n, 3)} = {bin(clear_bit(n, 3))}") # 34 = 0b100010
print(f"Toggle bit 5: {toggle_bit(n, 5)} = {bin(toggle_bit(n, 5))}") # 10 = 0b1010
```

---

## Pattern 2: Count Set Bits (Popcount)

### The Problem

"Count the number of 1 bits in an integer's binary representation."

Also known as: popcount, Hamming weight, number of set bits.

### Three Methods — With Tradeoffs

#### Method 1: Naive Loop — O(log N)

```python
def count_bits_naive(n: int) -> int:
    count = 0
    while n:
        count += n & 1   # check last bit
        n >>= 1          # shift right
    return count

# For n = 42 = 101010:
# Iteration 1: n=101010, bit=0, count=0, n→10101
# Iteration 2: n=10101,  bit=1, count=1, n→1010
# Iteration 3: n=1010,   bit=0, count=1, n→101
# Iteration 4: n=101,    bit=1, count=2, n→10
# Iteration 5: n=10,     bit=0, count=2, n→1
# Iteration 6: n=1,      bit=1, count=3, n→0
# Result: 3 set bits
```

This loops through every bit position, including the 0s.

#### Method 2: Brian Kernighan — O(set bits)

The elegant trick: `n & (n-1)` removes the lowest set bit from n.

```
Why? n-1 flips the lowest set bit and all bits below it.
AND of n and n-1 clears the lowest set bit.

n     = 1 0 1 0 1 0    (42)
n-1   = 1 0 1 0 0 1    (41)
n&n-1 = 1 0 1 0 0 0    (40) ← lowest set bit (bit 1) removed!

Next: n=40 = 1 0 1 0 0 0
n-1  = 39 = 1 0 0 1 1 1
n&n-1= 40 & 39 = 1 0 0 0 0 0 = 32 ← next lowest set bit removed

Next: n=32, n-1=31, n&n-1=0 → done, 3 iterations → 3 set bits
```

```python
def count_bits_kernighan(n: int) -> int:
    count = 0
    while n:
        n &= n - 1   # remove lowest set bit
        count += 1
    return count

# Only loops as many times as there are 1 bits.
# For n with k set bits: k iterations.
# For sparse numbers (few set bits), this is much faster.
```

#### Method 3: Python One-Liner — O(log N) internally

```python
def count_bits_pythonic(n: int) -> int:
    return bin(n).count('1')

# bin(42) = '0b101010'
# '0b101010'.count('1') = 3
# Clean. Simple. Python-idiomatic.
# CPython also has int.bit_count() in Python 3.10+
```

```python
# Python 3.10+
n = 42
print(n.bit_count())  # → 3
```

### Applications

#### Hamming Distance

Number of bit positions that differ between two numbers:

```python
def hammingDistance(x: int, y: int) -> int:
    # XOR gives 1 wherever bits differ, then count those 1s
    return bin(x ^ y).count('1')

# x=1=001, y=4=100
# XOR = 101 → 2 positions differ → Hamming distance = 2
print(hammingDistance(1, 4))  # 2
```

#### Total Hamming Distance (all pairs in array)

```python
def totalHammingDistance(nums: list) -> int:
    """For each bit position, count pairs that differ."""
    total = 0
    n = len(nums)
    for i in range(32):
        ones = sum(1 for x in nums if (x >> i) & 1)
        zeros = n - ones
        total += ones * zeros   # each (1,0) pair contributes 1 to total distance
    return total
```

#### Count Bits for All Numbers 0 to n

```python
def countBits(n: int) -> list:
    """dp[i] = number of set bits in i."""
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        # i has same bits as i with lowest set bit removed, plus 1
        dp[i] = dp[i & (i - 1)] + 1
    return dp

# OR equivalently:
def countBits_v2(n: int) -> list:
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        dp[i] = dp[i >> 1] + (i & 1)
        # dp[i>>1] = bits in i without last bit; (i&1) = last bit
    return dp
```

### When to Use Each

- **Naive loop**: Teaching purposes, very simple code, n is small
- **Kernighan**: When n is sparse (few 1s), or when you stop early (e.g., "check if exactly k bits set")
- **bin().count('1')**: Python interviews, clean code priority
- **bit_count()**: Python 3.10+, production code

---

## Pattern 3: Power of 2 / Isolate Lowest Set Bit

### The Problem

"Is n a power of 2?" — Powers of 2 have exactly one bit set: 1, 2, 4, 8, 16...

```
1  = 0000 0001  ← one bit
2  = 0000 0010  ← one bit
4  = 0000 0100  ← one bit
8  = 0000 1000  ← one bit
3  = 0000 0011  ← two bits, NOT power of 2
6  = 0000 0110  ← two bits, NOT power of 2
```

### The Trick: `n & (n-1) == 0`

```
For power of 2: n has exactly one bit set.
n-1 flips that bit and all below it (which are all 0).
n & (n-1) = 0 iff exactly one bit was set.

n=8:  1000
n-1=7: 0111
AND:   0000  → power of 2!

n=6:  0110
n-1=5: 0101
AND:   0100 ≠ 0  → NOT power of 2
```

```python
def isPowerOfTwo(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0

# Note: n > 0 guard needed because 0 & (-1) = 0, but 0 is not a power of 2.
# Also: negative numbers in Python won't satisfy n > 0.

print(isPowerOfTwo(1))   # True
print(isPowerOfTwo(16))  # True
print(isPowerOfTwo(6))   # False
print(isPowerOfTwo(0))   # False
```

### Isolate Lowest Set Bit: `n & (-n)`

In two's complement, `-n = ~n + 1`. This has the effect of isolating the lowest set bit.

```
n  =  01101000
-n =  10011000   (flip all bits then add 1)
n & -n = 00001000  ← only the lowest set bit remains

n = 42 = 101010
-42 in binary (two's complement): 010110
42 & -42 = 000010 = 2  ← lowest set bit is bit 1 (value = 2)
```

```python
def lowest_set_bit(n: int) -> int:
    """Return value of the lowest set bit."""
    return n & (-n)

print(lowest_set_bit(42))   # 2 (42 = 101010, lowest set bit = 1st bit = 2)
print(lowest_set_bit(40))   # 8 (40 = 101000, lowest set bit = 3rd bit = 8)
print(lowest_set_bit(32))   # 32 (32 = 100000, lowest set bit = 5th bit = 32)
```

### Applications

#### Enumerate All Non-Empty Subsets of a Set

```python
def all_subsets_using_bits(items: list) -> list:
    n = len(items)
    subsets = []
    for mask in range(1, 1 << n):   # 1 to 2^n - 1
        subset = [items[i] for i in range(n) if mask & (1 << i)]
        subsets.append(subset)
    return subsets

print(all_subsets_using_bits(['a', 'b', 'c']))
# mask=001 → ['a']
# mask=010 → ['b']
# mask=011 → ['a','b']
# mask=100 → ['c']
# mask=101 → ['a','c']
# mask=110 → ['b','c']
# mask=111 → ['a','b','c']
```

#### Check if Exactly One Bit is Set (Useful in Bitmask DP)

```python
def exactly_one_bit(n: int) -> bool:
    return n > 0 and (n & (n-1)) == 0

# same as isPowerOfTwo
```

---

## Pattern 4: XOR Properties and Applications

### XOR Truth Table

```
A | B | A XOR B
0 | 0 |    0
0 | 1 |    1
1 | 0 |    1
1 | 1 |    0

XOR = "exactly one of these is 1"
     = "these two bits differ"
```

### The Three Magic Properties

```
Property 1: a ^ a = 0     (anything XOR itself = 0)
Property 2: a ^ 0 = a     (anything XOR 0 = itself)
Property 3: XOR is commutative and associative
            a ^ b = b ^ a
            (a ^ b) ^ c = a ^ (b ^ c)
```

These three properties together produce a powerful insight:

**If you XOR all numbers in a collection, every number that appears an EVEN number of times cancels to 0. Only numbers appearing an ODD number of times survive.**

```
[1, 2, 3, 2, 1]
XOR all: 1 ^ 2 ^ 3 ^ 2 ^ 1
       = (1^1) ^ (2^2) ^ 3
       = 0 ^ 0 ^ 3
       = 3
Result: 3 is the only number appearing an odd number of times!
```

### Application 1: Single Number I (One unique, rest appear twice)

```python
def singleNumber(nums: list) -> int:
    """Find the element that appears once. All others appear exactly twice."""
    result = 0
    for n in nums:
        result ^= n
    return result

# All pairs cancel (x ^ x = 0), solo element survives
print(singleNumber([4, 1, 2, 1, 2]))  # 4
print(singleNumber([2, 2, 1]))        # 1

# XOR visualization:
# [4, 1, 2, 1, 2]
# 4 ^ 1 = 5
# 5 ^ 2 = 7
# 7 ^ 1 = 6
# 6 ^ 2 = 4  ← answer
```

### Application 2: Single Number II (One unique, rest appear three times)

XOR alone won't work here — we need to count bits modulo 3.

```python
def singleNumber_II(nums: list) -> int:
    """Find element appearing once. All others appear exactly three times."""
    # Count each bit position modulo 3
    # The surviving bit at each position belongs to the unique element
    result = 0
    for i in range(32):
        bit_sum = sum((n >> i) & 1 for n in nums)
        if bit_sum % 3:
            result |= (1 << i)

    # Handle negative numbers (Python 32-bit simulation)
    if result >= (1 << 31):
        result -= (1 << 32)
    return result

print(singleNumber_II([2, 2, 3, 2]))   # 3
print(singleNumber_II([0, 1, 0, 1, 0, 1, 99]))  # 99
```

### Application 3: Single Number III (Two unique elements, rest appear twice)

```python
def singleNumber_III(nums: list) -> list:
    """Find two elements that appear exactly once. All others appear twice."""
    # Step 1: XOR all → get xor_all = a ^ b (where a, b are the two unique elements)
    xor_all = 0
    for n in nums:
        xor_all ^= n

    # Step 2: Find a bit where a and b differ (any set bit in xor_all works)
    # Use lowest set bit trick
    diff_bit = xor_all & (-xor_all)

    # Step 3: Split numbers into two groups:
    # Group 1: has diff_bit set   → XOR gives one of {a, b}
    # Group 2: doesn't have diff_bit set → XOR gives the other
    a, b = 0, 0
    for n in nums:
        if n & diff_bit:
            a ^= n
        else:
            b ^= n

    return [a, b]

print(singleNumber_III([1, 2, 1, 3, 2, 5]))  # [3, 5]
```

### XOR Cancellation Visualization

```
Array: [A, B, C, A, B]

XOR one by one:
Step 1: A
Step 2: A ^ B = (A^B)
Step 3: A^B ^ C = (A^B^C)
Step 4: A^B^C ^ A = (B^C)    ← A canceled with A!
Step 5: B^C ^ B = C           ← B canceled with B!

Result: C (the unpaired element)

Visually:
  A    B    C    A    B
  ▓▓   ░░   ██   ▓▓   ░░
  ↑    ↑    ↑    ↑    ↑
  Each ▓▓ cancels its partner ▓▓
  Each ░░ cancels its partner ░░
  Only ██ survives
```

---

## Pattern 5: Bit Masking for Subsets

### The Core Idea

For a set of n elements, there are exactly 2^n subsets (including empty set). Each subset can be represented as an n-bit number where bit i = 1 means "include element i."

```
Elements: [A, B, C]  (indices 0, 1, 2)

Mask = 000 (binary) = 0  → empty subset {}
Mask = 001 (binary) = 1  → {A}
Mask = 010 (binary) = 2  → {B}
Mask = 011 (binary) = 3  → {A, B}
Mask = 100 (binary) = 4  → {C}
Mask = 101 (binary) = 5  → {A, C}
Mask = 110 (binary) = 6  → {B, C}
Mask = 111 (binary) = 7  → {A, B, C}

Bit 0 (value 1) = include A?
Bit 1 (value 2) = include B?
Bit 2 (value 4) = include C?
```

### Template: Enumerate All Subsets

```python
def enumerate_subsets(elements: list) -> None:
    n = len(elements)
    for mask in range(1 << n):   # 0 to 2^n - 1
        subset = []
        for i in range(n):
            if mask & (1 << i):  # is bit i set?
                subset.append(elements[i])
        print(f"mask={bin(mask)[2:].zfill(n)}: {subset}")

enumerate_subsets([10, 20, 30])
# mask=000: []
# mask=001: [10]
# mask=010: [20]
# mask=011: [10, 20]
# mask=100: [30]
# mask=101: [10, 30]
# mask=110: [20, 30]
# mask=111: [10, 20, 30]
```

### Application: Subset Sum Problem

```python
def subsetSum(nums: list, target: int) -> bool:
    """Does any subset of nums sum to target?"""
    n = len(nums)
    for mask in range(1 << n):
        total = sum(nums[i] for i in range(n) if mask & (1 << i))
        if total == target:
            return True
    return False

print(subsetSum([3, 1, 4, 2], 6))   # True (3+1+2=6 or 4+2=6)
print(subsetSum([3, 1, 4, 2], 11))  # False
```

### Application: Assignment / Covering Problems

```python
def canAssign(tasks: list, workers: list) -> bool:
    """
    Can each task be assigned to exactly one worker?
    tasks[i] = list of workers capable of task i.
    workers is the full list of workers.
    """
    n = len(workers)
    worker_idx = {w: i for i, w in enumerate(workers)}

    # For each task, create a bitmask of capable workers
    capable = []
    for task_workers in tasks:
        mask = 0
        for w in task_workers:
            mask |= (1 << worker_idx[w])
        capable.append(mask)

    # Try all subsets... (simplified check)
    # Real solution uses bitmask DP or max bipartite matching
    return True  # placeholder
```

### When Bitmask Subset Enumeration is the Right Choice

- n is small (typically n ≤ 20 for bitmask solutions, n ≤ 25 with pruning)
- You need to try all combinations of elements
- Problems with "assign", "cover", "select" semantics over a small set
- Bitmask DP (next pattern) extends this idea

---

## Pattern 6: Bitmask DP

### The Problem

"Traveling Salesman Problem style": given n cities and distances between them, find the minimum cost tour visiting all cities exactly once.

Or more generally: problems where the state includes **which elements from a small set have been used**.

### The State

`dp[mask][i]` = minimum cost to have visited exactly the cities in `mask`, ending at city `i`.

```
mask = bitmask of visited cities
i    = current city (last visited)

dp[mask][i] → dp[mask | (1 << j)][j]   when we move from i to unvisited city j
```

### ASCII: Mask Progression for 3 Cities (0, 1, 2)

```
Start at city 0, need to visit 1 and 2.

mask = 001 (only city 0 visited), at city 0:
  → move to city 1: mask = 011, at city 1   cost += dist[0][1]
  → move to city 2: mask = 101, at city 2   cost += dist[0][2]

mask = 011 (cities 0,1 visited), at city 1:
  → move to city 2: mask = 111, at city 2   cost += dist[1][2]

mask = 101 (cities 0,2 visited), at city 2:
  → move to city 1: mask = 111, at city 1   cost += dist[2][1]

mask = 111 (all visited) → return to start

All possible paths:
  0→1→2→0: dist[0][1] + dist[1][2] + dist[2][0]
  0→2→1→0: dist[0][2] + dist[2][1] + dist[1][0]
```

### Complete TSP Implementation

```python
import math

def tsp_bitmask(dist: list) -> int:
    """
    Minimum cost Hamiltonian cycle starting and ending at city 0.
    dist[i][j] = cost to travel from city i to city j.
    """
    n = len(dist)
    FULL_MASK = (1 << n) - 1   # all bits set = all cities visited

    # dp[mask][i] = min cost to be at city i with 'mask' cities visited
    INF = float('inf')
    dp = [[INF] * n for _ in range(1 << n)]

    # Start at city 0
    dp[1][0] = 0   # mask=0001, at city 0, cost=0

    for mask in range(1 << n):
        for i in range(n):
            if dp[mask][i] == INF:
                continue
            if not (mask & (1 << i)):
                continue   # city i not in visited set, invalid state

            # Try moving to every unvisited city j
            for j in range(n):
                if mask & (1 << j):
                    continue   # j already visited
                new_mask = mask | (1 << j)
                new_cost = dp[mask][i] + dist[i][j]
                if new_cost < dp[new_mask][j]:
                    dp[new_mask][j] = new_cost

    # Find minimum cost to return to city 0 from any city, having visited all
    result = min(dp[FULL_MASK][i] + dist[i][0] for i in range(1, n))
    return result


# Example: 4 cities
dist = [
    [0, 10, 15, 20],
    [10,  0, 35, 25],
    [15, 35,  0, 30],
    [20, 25, 30,  0]
]
print(tsp_bitmask(dist))  # 80 (0→1→3→2→0 = 10+25+30+15 = 80)
```

### Complexity

- States: O(2^n × n)
- Transitions: O(n) per state
- Total: O(2^n × n^2)
- For n=20: 2^20 × 400 ≈ 400 million (feasible but tight)
- For n=25: too slow
- Sweet spot: n ≤ 20

### Related Problems

- **Minimum cost to collect all keys in a grid** — bitmask = which keys collected
- **Shortest superstring** — bitmask = which strings have been appended
- **Parallel courses with prerequisites** — bitmask = which courses completed
- **Stickers to spell word** — bitmask = which characters covered

---

## Pattern 7: Bit Tricks for Math

### Multiply and Divide by Powers of 2

```python
# Left shift = multiply by 2^k
n = 5
print(n << 1)   # 10 (5 × 2)
print(n << 2)   # 20 (5 × 4)
print(n << 3)   # 40 (5 × 8)

# Right shift = integer divide by 2^k (floor division)
n = 40
print(n >> 1)   # 20 (40 // 2)
print(n >> 2)   # 10 (40 // 4)
print(n >> 3)   #  5 (40 // 8)
```

### Check Even or Odd

```python
def is_even(n: int) -> bool:
    return (n & 1) == 0

def is_odd(n: int) -> bool:
    return (n & 1) == 1

print(is_even(42))  # True
print(is_odd(7))    # True
```

The last bit (bit 0) determines even/odd: 0 = even, 1 = odd.

### XOR Swap (No Temp Variable)

```python
def xor_swap(a, b):
    """Swap a and b using XOR."""
    a ^= b   # a = a XOR b
    b ^= a   # b = (a XOR b) XOR b = a (original)
    a ^= b   # a = (a XOR b) XOR a = b (original)
    return a, b

x, y = 10, 20
x, y = xor_swap(x, y)
print(x, y)  # 20 10

# In Python: just use x, y = y, x
# XOR swap is mainly a C/assembly trick
# IMPORTANT: xor_swap(a, a) returns (0, 0)! Never swap a variable with itself.
```

### Gray Code

Gray code is a sequence where consecutive numbers differ by exactly one bit. Used in digital circuits and error correction.

```
n=0: 000
n=1: 001
n=2: 011
n=3: 010
n=4: 110
n=5: 111
n=6: 101
n=7: 100
Notice: each row differs from the previous by exactly 1 bit.

Formula: gray(n) = n XOR (n >> 1)

gray(0) = 0 XOR 0 = 0    = 000
gray(1) = 1 XOR 0 = 1    = 001
gray(2) = 2 XOR 1 = 3    = 011
gray(3) = 3 XOR 1 = 2    = 010
gray(4) = 4 XOR 2 = 6    = 110
```

```python
def gray_code(n: int) -> list:
    """Return Gray code sequence of length 2^n."""
    return [i ^ (i >> 1) for i in range(1 << n)]

print(gray_code(3))  # [0, 1, 3, 2, 6, 7, 5, 4]
```

### Absolute Value Without Branch (C-style)

```
In C (32-bit int):
  mask = n >> 31    → -1 if negative (all 1s), 0 if positive (all 0s)
  (n ^ mask) - mask → absolute value

  If n >= 0: mask=0, (n^0)-0 = n
  If n < 0:  mask=-1=0xFFFFFFFF
             n ^ mask = ~n (flip all bits)
             ~n - (-1) = ~n + 1 = -n (two's complement negation)
```

```python
def abs_no_branch_32bit(n: int) -> int:
    """Absolute value using bit tricks (32-bit signed integer simulation)."""
    # Python caveat: >> on negative numbers in Python doesn't behave like C
    # Python uses arbitrary precision, so we must mask to 32 bits
    n = n & 0xFFFFFFFF           # simulate 32-bit
    if n >= (1 << 31):           # if sign bit set, it's negative in 32-bit
        n -= (1 << 32)           # convert to Python's negative representation
    mask = n >> 31               # -1 if negative, 0 if non-negative
    return (n ^ mask) - mask

print(abs_no_branch_32bit(-5))   # 5
print(abs_no_branch_32bit(5))    # 5
print(abs_no_branch_32bit(0))    # 0
# In Python: just use abs(n) — the above is a conceptual exercise
```

### Find the Missing Number

```python
def missingNumber(nums: list) -> int:
    """
    Array has n numbers from range [0, n], one number is missing.
    XOR approach: XOR all numbers AND all indices 0..n
    Pairs cancel, missing number remains.
    """
    n = len(nums)
    result = n   # start with n (the last expected number)
    for i, num in enumerate(nums):
        result ^= i ^ num
    return result

print(missingNumber([3, 0, 1]))   # 2
print(missingNumber([9,6,4,2,3,5,7,0,1]))  # 8
```

---

## Pattern 8: Counting Bits in Range

### Problem 1: Count Total Set Bits in [1, n]

How many total 1-bits appear in all numbers from 1 to n?

#### Approach: Bit-by-Bit Counting

For each bit position i, count how many numbers in [1, n] have bit i set.

```
For bit position i:
  - Numbers cycle with period 2^(i+1)
  - In each cycle, the first 2^i numbers have bit i = 0
  - The next 2^i numbers have bit i = 1
  - Then reset

For bit i, count in [0, n]:
  full_cycles = (n + 1) // (2^(i+1))
  remainder   = (n + 1) % (2^(i+1))
  count_i = full_cycles * 2^i + max(0, remainder - 2^i)
```

```python
def countSetBitsInRange(n: int) -> int:
    """Count total 1-bits in all numbers from 1 to n."""
    total = 0
    bit_val = 1   # 2^i
    while bit_val <= n:
        cycle = bit_val * 2        # 2^(i+1)
        full_cycles = (n + 1) // cycle
        remainder = (n + 1) % cycle
        total += full_cycles * bit_val
        total += max(0, remainder - bit_val)
        bit_val <<= 1
    return total

print(countSetBitsInRange(5))
# Numbers 1-5: 1(1), 10(1), 11(2), 100(1), 101(2) → total = 7

print(countSetBitsInRange(7))
# 1,2,3,4,5,6,7 → 1,1,2,1,2,2,3 → total = 12
```

### Problem 2: Count Numbers in [0, n] with Exactly k Bits Set

#### Approach: Digit DP (on binary representation)

```python
from functools import lru_cache

def countNumbersWithKBits(n: int, k: int) -> int:
    """Count numbers in [0, n] with exactly k bits set."""
    bits = bin(n)[2:]   # binary string of n
    L = len(bits)

    @lru_cache(maxsize=None)
    def dp(pos: int, remaining: int, tight: bool) -> int:
        """
        pos: current bit position (from MSB)
        remaining: how many more 1-bits we can place
        tight: are we still constrained to <= n's digits?
        """
        if remaining < 0:
            return 0
        if pos == L:
            return 1 if remaining == 0 else 0

        limit = int(bits[pos]) if tight else 1
        result = 0
        for digit in range(limit + 1):
            new_tight = tight and (digit == limit)
            result += dp(pos + 1, remaining - digit, new_tight)

        return result

    return dp(0, k, True)

print(countNumbersWithKBits(5, 1))   # 0,1,2,4 with 1 bit → 1,2,4 → 3
print(countNumbersWithKBits(7, 2))   # 3,5,6 → 3 numbers
print(countNumbersWithKBits(15, 2))  # 3,5,6,9,10,12 → 6 numbers
```

### Problem 3: Counting Bits for 0..n (LeetCode 338)

```python
def countBits_range(n: int) -> list:
    """
    Return array where result[i] = number of 1-bits in i.
    For all i from 0 to n.
    """
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        # dp[i] = dp[i without its lowest set bit] + 1
        # i without lowest set bit = i & (i-1)
        dp[i] = dp[i & (i - 1)] + 1
    return dp

print(countBits_range(5))   # [0, 1, 1, 2, 1, 2]
# 0=0bits, 1=1bit, 2=1bit, 3=2bits, 4=1bit, 5=2bits
```

---

## Bit Manipulation Problem Recognition Cheatsheet

```
Trigger Phrase                                 → Pattern
------------------------------------------------------------
"number of 1 bits" / "Hamming weight"          → Pattern 2 (Popcount)
"power of two"                                 → Pattern 3 (n & n-1 == 0)
"find the single element" / "appears once"     → Pattern 4 (XOR)
"find two non-repeating elements"              → Pattern 4 (XOR split)
"all subsets" / "enumerate combinations"       → Pattern 5 (Bitmask Subsets)
"visit all nodes / cities optimally"           → Pattern 6 (Bitmask DP)
"k set bits in range"                          → Pattern 8 (Digit DP)
"maximum XOR"                                  → Trie Pattern 3 (Binary Trie)
"even / odd check"                             → Pattern 7 (n & 1)
"missing number in range"                      → Pattern 7 (XOR trick)
```

---

## Common Mistakes and How to Avoid Them

```python
# Mistake 1: Wrong operator precedence
# WRONG:
if n & 1 == 0:   # Python parses as n & (1 == 0) = n & False = 0!

# CORRECT:
if (n & 1) == 0:  # always parenthesize bit operations in conditions

# Mistake 2: XOR swap with same variable
a = 5
a ^= a   # a = 0! (a XOR a = 0)
# Never swap a variable with itself using XOR

# Mistake 3: Python's >> on negatives
# Python uses arithmetic right shift (sign-extends)
# -1 >> 1 = -1 (not 2^31 - 1 like in C)
# If simulating 32-bit, mask first: (n & 0xFFFFFFFF) >> 1

# Mistake 4: Forgetting edge case n=0 for isPowerOfTwo
def isPowerOfTwo_wrong(n):
    return n & (n-1) == 0   # Returns True for n=0! (0 & -1 = 0)

def isPowerOfTwo_correct(n):
    return n > 0 and (n & (n-1)) == 0

# Mistake 5: Off-by-one in bitmask DP
# For n elements, full mask = (1 << n) - 1, NOT (1 << n)
# (1 << n) - 1 = 2^n - 1 = all n bits set

# Mistake 6: Modifying loop variable
for mask in range(1 << n):
    mask |= (1 << 0)   # Don't do this! Doesn't affect loop in Python (new binding)
    # Python creates new binding; original mask isn't changed in the loop counter
```

---

## Quick Reference: All Bit Operations

```python
# Basic operations
(n >> i) & 1          # check bit i
n | (1 << i)          # set bit i
n & ~(1 << i)         # clear bit i
n ^ (1 << i)          # toggle bit i

# Bit counting
bin(n).count('1')     # popcount (Pythonic)
n.bit_count()         # popcount (Python 3.10+)
n &= n - 1; count += 1  # Kernighan: remove lowest set bit

# Bit tests
n & (n-1) == 0        # power of 2 (or zero)
n & 1                 # is odd?
n & (-n)              # isolate lowest set bit

# Math tricks
n << k                # n * 2^k
n >> k                # n // 2^k
n ^ (n >> 1)          # gray code

# XOR applications
a ^ a = 0             # cancellation
a ^ 0 = a             # identity
XOR all → unique element

# Subset enumeration
for mask in range(1 << n):
    for i in range(n):
        if mask & (1 << i): ...  # element i in this subset

# Bitmask DP state
full_mask = (1 << n) - 1
is_visited = mask & (1 << i)
visit_i = mask | (1 << i)
unvisit_i = mask ^ (1 << i)  # only if i was visited
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [Real World Usage →](./real_world_usage.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
