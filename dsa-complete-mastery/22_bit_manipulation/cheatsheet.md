# Bit Manipulation — Cheatsheet

---

## Bit Operations Quick Reference

| Operation     | Symbol | Example (a=6=110, b=3=011) | Result       |
|---------------|--------|---------------------------|--------------|
| AND           | `&`    | 6 & 3                     | 2  (010)     |
| OR            | `\|`   | 6 \| 3                    | 7  (111)     |
| XOR           | `^`    | 6 ^ 3                     | 5  (101)     |
| NOT           | `~`    | ~6                        | -7 (two's complement) |
| Left shift    | `<<`   | 6 << 1                    | 12 (1100)    |
| Right shift   | `>>`   | 6 >> 1                    | 3  (011)     |

**Shift rules:**
- `n << k` = multiply by 2^k
- `n >> k` = floor divide by 2^k
- Python `~n` = `-(n+1)` (signed, infinite precision integers)

---

## Essential Bit Tricks

```python
# Check if bit i is set
(n >> i) & 1           # or: n & (1 << i) != 0

# Set bit i
n | (1 << i)

# Clear bit i
n & ~(1 << i)

# Toggle bit i
n ^ (1 << i)

# Check even / odd
n & 1                  # 0 = even, 1 = odd

# Check power of 2
n > 0 and (n & (n-1)) == 0

# Isolate lowest set bit (rightmost 1)
n & (-n)               # e.g., 12 (1100) -> 4 (0100)

# Clear lowest set bit
n & (n - 1)            # e.g., 12 (1100) -> 8 (1000)

# Get value of lowest set bit position
(n & -n).bit_length() - 1

# Check if two numbers have opposite signs
(x ^ y) < 0

# Swap without temp variable
a ^= b
b ^= a
a ^= b

# Absolute value (branchless)
mask = n >> 31         # all 0s or all 1s
abs_n = (n + mask) ^ mask

# Round down to nearest power of 2
1 << (n.bit_length() - 1)

# Round up to nearest power of 2
1 << n.bit_length() if n & (n-1) else n
```

---

## XOR Properties

| Property          | Formula               | Use                                  |
|-------------------|-----------------------|--------------------------------------|
| Identity          | x ^ 0 = x             | XOR with 0 has no effect             |
| Self-inverse      | x ^ x = 0             | Same value XORed twice cancels       |
| Commutative       | x ^ y = y ^ x         | Order doesn't matter                 |
| Associative       | (x^y)^z = x^(y^z)     | Can regroup operations               |
| Inverse of itself | x ^ y ^ y = x         | XOR then un-XOR restores original    |

---

## Common XOR Interview Patterns

```python
# Find single number (all others appear twice)
def single_number(nums):
    result = 0
    for n in nums:
        result ^= n
    return result

# Find two unique numbers (all others appear twice)
def single_number_ii(nums):
    xor = 0
    for n in nums: xor ^= n
    diff_bit = xor & (-xor)          # isolate any differing bit
    a = 0
    for n in nums:
        if n & diff_bit:
            a ^= n
    return a, xor ^ a

# Find missing number in [0..n]
def missing_number(nums):
    n = len(nums)
    result = n
    for i, v in enumerate(nums):
        result ^= i ^ v
    return result

# Swap two variables without temp
a, b = 5, 9
a ^= b; b ^= a; a ^= b   # a=9, b=5

# Check if substring has all unique chars (bitmask for 26 letters)
def all_unique(s):
    mask = 0
    for c in s:
        bit = 1 << (ord(c) - ord('a'))
        if mask & bit: return False
        mask |= bit
    return True
```

---

## Bit Count Algorithms

```python
# Python built-in (most efficient)
bin(n).count('1')
n.bit_count()           # Python 3.10+

# Brian Kernighan's Algorithm — O(number of set bits)
def count_bits(n):
    count = 0
    while n:
        n &= n - 1       # clear lowest set bit
        count += 1
    return count

# DP bit count — O(n) for range [0, n]
def count_bits_range(n):
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        dp[i] = dp[i >> 1] + (i & 1)
    return dp
```

---

## Bitmask DP — Subset Enumeration

```python
# Enumerate all subsets of n elements
n = 4
for mask in range(1 << n):
    subset = [i for i in range(n) if mask & (1 << i)]

# Enumerate all subsets of a given mask (including empty)
mask = 0b1011
sub = mask
while sub > 0:
    # process sub
    sub = (sub - 1) & mask     # next smaller subset

# TSP / Assignment problem template
# dp[mask][i] = cost to visit all nodes in mask, ending at i
INF = float('inf')
n = 4
dp = [[INF] * n for _ in range(1 << n)]
dp[1][0] = 0                   # start at node 0

for mask in range(1 << n):
    for u in range(n):
        if not (mask >> u & 1): continue
        if dp[mask][u] == INF: continue
        for v in range(n):
            if mask >> v & 1: continue
            new_mask = mask | (1 << v)
            dp[new_mask][v] = min(dp[new_mask][v], dp[mask][u] + dist[u][v])

# Answer: min over all ending nodes (with all visited)
full_mask = (1 << n) - 1
ans = min(dp[full_mask][i] + dist[i][0] for i in range(n))
```

---

## Python Bit Utilities

```python
# Binary representation
bin(10)                 # '0b1010'
bin(10)[2:]             # '1010' (strip prefix)
f'{10:08b}'             # '00001010' (zero-padded, 8 bits)

# Parse binary string to int
int('1010', 2)          # 10
int('0b1010', 2)        # error — strip prefix first

# Bit length
(10).bit_length()       # 4 (needs at least 4 bits to represent)

# Count set bits
bin(255).count('1')     # 8
(255).bit_count()       # 8 (Python 3.10+)

# Negative numbers
~5                      # -6   (bitwise NOT = -(n+1))
-1 in binary            # ...11111111 (infinite 1s in Python)
(-1) & 0xFF             # 255  (mask to get unsigned 8-bit)
```

---

## Complexity Table

| Operation                   | Time     | Notes                               |
|-----------------------------|----------|-------------------------------------|
| Single bit operation        | O(1)     | AND, OR, XOR, shift                 |
| Count set bits (Kernighan)  | O(k)     | k = number of set bits              |
| Count set bits (Python)     | O(1)     | Built-in bit_count()                |
| Enumerate all subsets       | O(2^n)   | For bitmask DP                      |
| Enumerate subsets of mask   | O(3^n)   | Sum of subset sizes across all masks|

---

## Gotchas

- Python integers are arbitrary precision — no 32/64-bit overflow like C/Java
- `~n = -(n+1)` in Python (not unsigned flip like C)
- To simulate 32-bit unsigned: `n & 0xFFFFFFFF`
- To simulate 32-bit signed: `n if n < 2**31 else n - 2**32`
- XOR swap fails if `a` and `b` point to the same variable (`a is b`)
- `n & (n-1) == 0` returns True for n=0 — always check `n > 0` separately
- Left shift on large n creates very large integers in Python (no overflow)
