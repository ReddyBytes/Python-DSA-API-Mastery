# 💻 Practice — Bit Manipulation

## Quick Index

| Q# | Topic | Difficulty |
|---|---|---|
| [Q1](#q1) | Binary representation | 🟢 |
| [Q2](#q2) | Bitwise AND masking | 🟢 |
| [Q3](#q3) | Bitwise OR | 🟢 |
| [Q4](#q4) | Bitwise XOR | 🟢 |
| [Q5](#q5) | Left/right shifts | 🟢 |
| [Q6](#q6) | Even/odd check | 🟢 |
| [Q7](#q7) | Check bit i | 🟢 |
| [Q8](#q8) | Set bit i | 🟢 |
| [Q9](#q9) | Clear bit i | 🟡 |
| [Q10](#q10) | Toggle bit i | 🟡 |
| [Q11](#q11) | Power of 2 check | 🟡 |
| [Q12](#q12) | Brian Kernighan | 🟡 |
| [Q13](#q13) | Count bits 0..n DP | 🟡 |
| [Q14](#q14) | XOR single number | 🟡 |
| [Q15](#q15) | XOR swap | 🟡 |
| [Q16](#q16) | Missing number | 🟡 |
| [Q17](#q17) | Isolate LSB | 🟡 |
| [Q18](#q18) | Hamming distance | 🟡 |
| [Q19](#q19) | Two unique elements | 🟠 |
| [Q20](#q20) | Bitwise complement | 🟠 |
| [Q21](#q21) | Subset enumeration | 🟠 |
| [Q22](#q22) | Subset sum via mask | 🟠 |
| [Q23](#q23) | XOR mod 3 trick | 🟠 |
| [Q24](#q24) | Bit adder (XOR carry) | 🟠 |
| [Q25](#q25) | Bitmask DP (TSP) | 🟠 |

---

<a id="q1"></a>
### Q1 · binary-representation · Read a Bit

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


🟢 Basic

**Problem:** Given integer `n = 42`, write it in binary by hand. How many bits are set? What is the value of bit 3 (position 3, 0-indexed from the right)?

<details>
<summary>💡 Hint</summary>

Divide 42 repeatedly by 2, collecting remainders from bottom to top. Alternatively, identify which powers of 2 sum to 42. Bit 3 has **positional value** `2^3 = 8`.

</details>

<details>
<summary>✅ Answer</summary>

```python
n = 42
print(bin(n))         # 0b101010
print(n.bit_length()) # 6 (positions 0-5)

# Manual: 42 = 32 + 8 + 2 = 2^5 + 2^3 + 2^1
# Binary: 0b 1 0 1 0 1 0
# Pos:         5 4 3 2 1 0

set_bits = bin(n).count('1')  # 3 set bits
bit_3_value = (n >> 3) & 1    # 1 (bit 3 IS set — contributes 8)

print(f"Set bits: {set_bits}")   # 3
print(f"Bit 3: {bit_3_value}")   # 1
```

**Why:** Binary is base 2 — each position represents a power of 2. Bit 3 means `2^3 = 8`. Since 42 = 32 + 8 + 2, bit 3 is ON.

</details>

> 💻 Try it: [practice_local.py → Q1](./practice_local.py)

---

<a id="q2"></a>
### Q2 · bitwise-and · Mask Out Lower Bits

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


🟢 Basic

**Problem:** You have `n = 0b11011011` (219 in decimal). Use a **bitmask** with `&` to extract only the lower 4 bits (bits 0-3). What is the result?

<details>
<summary>💡 Hint</summary>

A mask of `0b00001111` (value 15) has exactly the lower 4 bits set. AND-ing with it forces all upper bits to 0 and keeps the lower 4 unchanged.

</details>

<details>
<summary>✅ Answer</summary>

```python
n    = 0b11011011   # 219
mask = 0b00001111   # 15 — lower nibble mask

result = n & mask
print(bin(result))  # 0b1011 = 11

# Visual:
#   1 1 0 1 1 0 1 1   (219)
# & 0 0 0 0 1 1 1 1   (15)
# = 0 0 0 0 1 0 1 1   (11)
```

**Why:** `&` (AND) outputs 1 only where BOTH bits are 1. The mask acts as a filter — 0 in the mask forces 0 in output; 1 in the mask passes through the original bit unchanged. This **masking** pattern is the foundation of permission systems, flag checks, and nibble extraction.

</details>

> 💻 Try it: [practice_local.py → Q2](./practice_local.py)

---

<a id="q3"></a>
### Q3 · bitwise-or · Set a Specific Bit

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


🟢 Basic

**Problem:** Given `flags = 0b0101` (read and execute permissions set), use `|` to add the **write permission** at bit position 1 (value `0b0010`). What is the result?

<details>
<summary>💡 Hint</summary>

OR forces a bit to 1 without touching any other bits. Create a mask with only the target bit set, then OR it with the original value.

</details>

<details>
<summary>✅ Answer</summary>

```python
READ  = 0b001   # 1
WRITE = 0b010   # 2
EXEC  = 0b100   # 4

flags = READ | EXEC   # 0b0101 = 5 (read + execute)
flags |= WRITE        # add write permission

print(bin(flags))     # 0b111 = 7 (all three set)
print(flags)          # 7

# Visual:
#   0 1 0 1   (original flags)
# | 0 0 1 0   (WRITE mask)
# = 0 1 1 1   (7)
```

**Why:** `|` (OR) forces any 0 bit to 1 when the mask bit is 1, and leaves 1 bits unchanged. It is the standard way to **set** a bit. UNIX file permissions (rwx) are the most famous real-world example.

</details>

> 💻 Try it: [practice_local.py → Q3](./practice_local.py)

---

<a id="q4"></a>
### Q4 · bitwise-xor · Flip Bits Selectively

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


🟢 Basic

**Problem:** Given `n = 0b1010` (10), use `^` (XOR) to flip bits 0 and 2. What is the result?

<details>
<summary>💡 Hint</summary>

XOR with 1 flips a bit; XOR with 0 leaves it unchanged. Create a mask with 1s at the positions you want to flip.

</details>

<details>
<summary>✅ Answer</summary>

```python
n    = 0b1010   # 10
mask = 0b0101   # flip positions 0 and 2

result = n ^ mask
print(bin(result))  # 0b1111 = 15

# Visual:
#   1 0 1 0   (10)
# ^ 0 1 0 1   (mask)
# = 1 1 1 1   (15)

# XOR truth table: same bits → 0, different bits → 1
# 1 ^ 0 = 1, 0 ^ 1 = 1, 1 ^ 1 = 0, 0 ^ 0 = 0
```

**Why:** XOR is the "difference" operator. Bit 0: `0 ^ 1 = 1` (flipped). Bit 2: `0 ^ 1 = 1` (flipped). Bits 1 and 3 stay the same because their mask bits are 0.

</details>

> 💻 Try it: [practice_local.py → Q4](./practice_local.py)

---

<a id="q5"></a>
### Q5 · shifts · Multiply and Divide by Powers of 2

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


🟢 Basic

**Problem:** Without using `*` or `//`, compute `5 * 8` and `96 // 16` using only bit shifts.

<details>
<summary>💡 Hint</summary>

Left shift by `k` multiplies by `2^k`. Right shift by `k` divides (integer floor) by `2^k`. Think: what power of 2 is 8? What power of 2 is 16?

</details>

<details>
<summary>✅ Answer</summary>

```python
# 5 * 8 = 5 * 2^3 = 5 << 3
n = 5
print(n << 3)   # 40

# 96 // 16 = 96 // 2^4 = 96 >> 4
n = 96
print(n >> 4)   # 6

# Verify:
assert 5 << 3 == 40
assert 96 >> 4 == 6

# Extra: right shift on odd numbers truncates (floor division)
print(7 >> 1)   # 3 (= 7 // 2)
print(9 >> 2)   # 2 (= 9 // 4)
```

**Why:** In binary, `101` left-shifted by 3 becomes `101000` = 40. Shifts are single CPU instructions — faster than multiply/divide in low-level contexts, and often used in hash functions, pixel math, and network encoding.

</details>

> 💻 Try it: [practice_local.py → Q5](./practice_local.py)

---

<a id="q6"></a>
### Q6 · even-odd · Parity Check Without Modulo

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


🟢 Basic

**Problem:** Write `is_even(n)` and `is_odd(n)` without using `%`. Why does the last bit determine parity?

<details>
<summary>💡 Hint</summary>

All even numbers end in binary `0`. All odd numbers end in binary `1`. The last bit (bit 0) IS the parity bit. AND with 1 isolates it.

</details>

<details>
<summary>✅ Answer</summary>

```python
def is_even(n: int) -> bool:
    return (n & 1) == 0

def is_odd(n: int) -> bool:
    return (n & 1) == 1

print(is_even(42))   # True  (42 = ...10 in binary)
print(is_odd(7))     # True  (7  = ...111 in binary)
print(is_even(0))    # True
print(is_odd(-3))    # True  (-3 in two's complement ends in 1)

# Works for negative numbers too in Python
for n in [-5, -4, 0, 3, 100]:
    print(f"{n:4}: even={is_even(n)}, odd={is_odd(n)}")
```

**Why:** Any number that is a sum of even powers of 2 (`2^1, 2^2, ...`) is even. Adding `2^0 = 1` makes it odd. The last bit is literally the "ones place" — the only place where the even/odd distinction lives.

</details>

> 💻 Try it: [practice_local.py → Q6](./practice_local.py)

---

<a id="q7"></a>
### Q7 · check-bit · Is Bit i Set?

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


🟢 Basic

**Problem:** Implement `check_bit(n, i)` that returns `1` if bit `i` is set in `n`, else `0`. Test with `n=42`, `i=3` and `n=42`, `i=4`.

<details>
<summary>💡 Hint</summary>

Two equivalent approaches: (1) shift `n` right by `i` positions so bit `i` lands at position 0, then AND with 1. (2) create a mask `1 << i` and AND with `n` — nonzero means it's set.

</details>

<details>
<summary>✅ Answer</summary>

```python
def check_bit(n: int, i: int) -> int:
    return (n >> i) & 1

# n = 42 = 0b101010
#            543210  ← bit positions
print(check_bit(42, 3))   # 1 (bit 3 = value 8, contributes to 42)
print(check_bit(42, 4))   # 0 (bit 4 = value 16, NOT in 42)
print(check_bit(42, 1))   # 1 (bit 1 = value 2, contributes to 42)
print(check_bit(42, 0))   # 0 (42 is even, bit 0 is off)

# Visual for n=42, i=3:
#   42 >> 3 = 0b000101 = 5
#   5  &  1 = 0b000001 = 1  → set!
```

**Why:** Shifting right moves the target bit to position 0. AND with 1 isolates it, discarding everything else. This is the most common bit inspection pattern in embedded systems, permission checks, and flags.

</details>

> 💻 Try it: [practice_local.py → Q7](./practice_local.py)

---

<a id="q8"></a>
### Q8 · set-bit · Turn Bit i ON

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


🟢 Basic

**Problem:** Implement `set_bit(n, i)` that returns `n` with bit `i` forced to 1. Then implement `clear_bit(n, i)` that forces bit `i` to 0. Test both on `n=42`, `i=4`.

<details>
<summary>💡 Hint</summary>

For set: OR with a mask that has only bit `i` on (`1 << i`). For clear: AND with the bitwise NOT of that mask (`~(1 << i)`), which has all bits on EXCEPT position `i`.

</details>

<details>
<summary>✅ Answer</summary>

```python
def set_bit(n: int, i: int) -> int:
    return n | (1 << i)

# n=42=0b101010, i=4:
# 1 << 4    = 0b010000 = 16
# 42 | 16   = 0b111010 = 58
print(set_bit(42, 4))    # 58

# Verify bit 4 is now on:
print((58 >> 4) & 1)     # 1 ✓

# Setting an already-set bit is idempotent:
print(set_bit(42, 3))    # 42 (bit 3 was already set)
```

**Why:** `1 << i` creates a mask with exactly one bit on. OR-ing with it forces that bit to 1 regardless of what it was before. The mask leaves all other bits unchanged because `x | 0 = x`.

</details>

> 💻 Try it: [practice_local.py → Q8](./practice_local.py)

---

<a id="q9"></a>
### Q9 · clear-bit · Turn Bit i OFF

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


🟡 Intermediate

**Problem:** Implement `clear_bit(n, i)` using AND and NOT. What is `clear_bit(42, 3)`? Why do you need `~` here and not for set/toggle?

<details>
<summary>💡 Hint</summary>

To force a bit to 0, you need a mask that is 0 at position `i` and 1 everywhere else. `~(1 << i)` does exactly that — flip all bits of the single-bit mask. Then AND forces the target bit to 0 while preserving all others.

</details>

<details>
<summary>✅ Answer</summary>

```python
def clear_bit(n: int, i: int) -> int:
    return n & ~(1 << i)

# n=42=0b101010, i=3:
# 1 << 3       = 0b001000 = 8
# ~8 (Python)  = -9 = ...11110111  (all bits 1 except position 3)
# 42 & ~8      = 0b101010 & ...11110111 = 0b100010 = 34

print(clear_bit(42, 3))   # 34
print(bin(clear_bit(42, 3)))  # 0b100010

# Clearing an already-clear bit is also idempotent:
print(clear_bit(42, 4))   # 42 (bit 4 was already 0)

# Why NOT needed: AND naturally kills a bit when mask has 0 there.
# For set (OR): mask needs a 1 at target → just use 1 << i
# For clear (AND): mask needs a 0 at target → must invert: ~(1 << i)
# For toggle (XOR): mask needs a 1 at target → just use 1 << i
```

**Why:** `AND with 0 = 0` (force off). `AND with 1 = original` (preserve). So the clear mask needs 0 at the target position and 1s everywhere else — the complement of the single-bit mask.

</details>

> 💻 Try it: [practice_local.py → Q9](./practice_local.py)

---

<a id="q10"></a>
### Q10 · toggle-bit · Flip Bit i

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


🟡 Intermediate

**Problem:** Implement `toggle_bit(n, i)`. Then call it twice on the same bit — what do you get? Why?

<details>
<summary>💡 Hint</summary>

XOR with 1 flips a bit; XOR with 0 leaves it unchanged. Build a mask with 1 only at position `i`.

</details>

<details>
<summary>✅ Answer</summary>

```python
def toggle_bit(n: int, i: int) -> int:
    return n ^ (1 << i)

# n=42=0b101010, i=5 (bit 5 is ON in 42):
print(toggle_bit(42, 5))    # 10  (bit 5 flipped OFF: 101010 → 001010)
print(toggle_bit(10, 5))    # 42  (bit 5 flipped ON:  001010 → 101010)

# Applying twice returns original:
n = 42
n = toggle_bit(n, 5)
n = toggle_bit(n, 5)
print(n)   # 42 — idempotent when applied twice

# Why? XOR is its own inverse: (a ^ b) ^ b = a
# Toggling twice: (n ^ mask) ^ mask = n ^ (mask ^ mask) = n ^ 0 = n
```

**Why:** XOR is reversible — applying the same mask twice cancels out. This makes toggle the "flip" operation used in blinking LEDs, animation frames, crypto primitives, and undo systems.

</details>

> 💻 Try it: [practice_local.py → Q10](./practice_local.py)

---

<a id="q11"></a>
### Q11 · power-of-2 · One Bit Trick

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


🟡 Intermediate

**Problem:** Implement `is_power_of_two(n)` using a single bit operation. Why must you guard against `n = 0`? Show why `n & (n-1)` works.

<details>
<summary>💡 Hint</summary>

Powers of 2 have exactly one bit set: `1=001`, `2=010`, `4=100`, `8=1000`. Subtracting 1 from a power of 2 flips that single bit and turns on all lower bits. AND-ing the two gives 0.

</details>

<details>
<summary>✅ Answer</summary>

```python
def is_power_of_two(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0

# Why n > 0 guard?
# 0 & (-1) = 0  →  0 would pass the n & (n-1) == 0 test incorrectly!

print(is_power_of_two(1))    # True   (1 = 2^0)
print(is_power_of_two(16))   # True   (16 = 2^4)
print(is_power_of_two(6))    # False  (6 = 110 — two bits set)
print(is_power_of_two(0))    # False  (guard catches this)
print(is_power_of_two(-4))   # False  (guard catches negatives)

# Trace for n=8 (1000):
#   n     = 1000
#   n - 1 = 0111
#   n & (n-1) = 0000  → power of two!

# Trace for n=6 (0110):
#   n     = 0110
#   n - 1 = 0101
#   n & (n-1) = 0100 ≠ 0  → NOT a power of two

# CRITICAL: always parenthesize! n & (n - 1) == 0, NOT n & n - 1 == 0
```

**Why:** When `n` is a power of 2, it has exactly one 1-bit. `n-1` flips that bit and turns on all lower bits. AND-ing them produces all zeros — a clean O(1) check with no loops or division.

</details>

> 💻 Try it: [practice_local.py → Q11](./practice_local.py)

---

<a id="q12"></a>
### Q12 · count-set-bits · Brian Kernighan

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


🟡 Intermediate

**Problem:** Implement `count_set_bits(n)` using Brian Kernighan's algorithm. Count the set bits in `n = 0b10110100`. Explain why this is faster than the naive loop.

<details>
<summary>💡 Hint</summary>

`n & (n-1)` removes the **lowest set bit** from `n`. Count how many times you can do this before `n` reaches 0. The loop runs exactly as many times as there are 1-bits.

</details>

<details>
<summary>✅ Answer</summary>

```python
def count_set_bits(n: int) -> int:
    count = 0
    while n:
        n &= n - 1   # clear the lowest set bit
        count += 1
    return count

# n = 0b10110100 = 180
# Iteration 1: n=10110100, n&(n-1)=10110000, count=1
# Iteration 2: n=10110000, n&(n-1)=10100000, count=2
# Iteration 3: n=10100000, n&(n-1)=10000000, count=3
# Iteration 4: n=10000000, n&(n-1)=00000000, count=4
# Result: 4 set bits in exactly 4 iterations

print(count_set_bits(0b10110100))  # 4

# Naive loop: 8 iterations (one per bit position, including zeros)
# Kernighan:  4 iterations (one per SET bit only) → O(k) not O(bits)

# Python 3.10+ shortcut:
print((0b10110100).bit_count())    # 4
# Pythonic shortcut:
print(bin(0b10110100).count('1'))  # 4
```

**Why:** The naive loop always runs `O(bit_length)` times. Kernighan's runs exactly `O(k)` times where `k` is the number of set bits. For sparse numbers (like `2^30`), naive takes 31 iterations; Kernighan takes 1.

</details>

> 💻 Try it: [practice_local.py → Q12](./practice_local.py)

---

<a id="q13"></a>
### Q13 · count-set-bits-dp · Count Bits 0..n DP

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)


🟡 Intermediate

**Problem:** Given `n = 5`, return an array `result` where `result[i]` = number of set bits in `i`, for all `i` from 0 to 5. Solve in O(n) time with a DP recurrence.

<details>
<summary>💡 Hint</summary>

Every number `i` can be split: `i >> 1` (right-shift removes last bit) has a known popcount already computed. Add `i & 1` (the last bit) to it.

</details>

<details>
<summary>✅ Answer</summary>

```python
def count_bits_range(n: int) -> list:
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        dp[i] = dp[i >> 1] + (i & 1)
        # i >> 1 = i without its last bit (already computed)
        # i & 1  = value of last bit (0 or 1)
    return dp

print(count_bits_range(5))
# [0, 1, 1, 2, 1, 2]
# 0→0 bits, 1→1 bit, 2(10)→1 bit, 3(11)→2 bits, 4(100)→1 bit, 5(101)→2 bits

# Alternative recurrence using Kernighan's insight:
def count_bits_range_v2(n: int) -> list:
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        dp[i] = dp[i & (i - 1)] + 1  # i with lowest set bit removed, plus 1
    return dp

print(count_bits_range_v2(5))   # [0, 1, 1, 2, 1, 2]
```

**Why:** Both recurrences leverage previously computed sub-problems. `dp[i >> 1]` is always computed before `dp[i]` since `i >> 1 < i`. This avoids recomputing set bits for each number from scratch.

</details>

> 💻 Try it: [practice_local.py → Q13](./practice_local.py)

---

<a id="q14"></a>
### Q14 · xor-cancellation · Single Number I

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)


🟡 Intermediate

**Problem:** Given `nums = [4, 1, 2, 1, 2]`, find the element that appears exactly once. All others appear exactly twice. Solve in O(n) time and O(1) space using XOR.

<details>
<summary>💡 Hint</summary>

XOR has two key properties: `a ^ a = 0` (cancellation) and `a ^ 0 = a` (identity). XOR all elements together — pairs cancel, the lone element survives.

</details>

<details>
<summary>✅ Answer</summary>

```python
def single_number(nums: list) -> int:
    result = 0
    for n in nums:
        result ^= n
    return result

print(single_number([4, 1, 2, 1, 2]))   # 4
print(single_number([2, 2, 1]))          # 1
print(single_number([1]))                # 1

# Trace: [4, 1, 2, 1, 2]
# 0 ^ 4 = 4
# 4 ^ 1 = 5
# 5 ^ 2 = 7
# 7 ^ 1 = 6   ← 1 cancels
# 6 ^ 2 = 4   ← 2 cancels
# Result: 4

# Why XOR? Because:
# (a ^ a) = 0  — every duplicate pair annihilates
# (0 ^ x) = x  — solo element is left standing
# XOR is commutative/associative, so order doesn't matter
```

**Why:** Any number XOR-ed with itself gives 0. Any 0 XOR-ed with a number gives that number back. So the only survivor is the element with no pair.

</details>

> 💻 Try it: [practice_local.py → Q14](./practice_local.py)

---

<a id="q15"></a>
### Q15 · xor-swap · No Temp Variable

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)


🟡 Intermediate

**Problem:** Swap `a = 10` and `b = 20` using only XOR operations — no temp variable. Prove step-by-step why it works. What edge case must you avoid?

<details>
<summary>💡 Hint</summary>

Three XOR assignments: `a ^= b`, `b ^= a`, `a ^= b`. Trace through what `a` and `b` hold after each step using the identity `(x ^ y) ^ y = x`.

</details>

<details>
<summary>✅ Answer</summary>

```python
def xor_swap(a: int, b: int) -> tuple:
    a ^= b   # a = a XOR b
    b ^= a   # b = (a XOR b) XOR b = a  (original a!)
    a ^= b   # a = (a XOR b) XOR a = b  (original b!)
    return a, b

a, b = 10, 20
a, b = xor_swap(a, b)
print(a, b)   # 20 10

# Step-by-step proof:
# Let original a = A, b = B
# After a ^= b:  a = A^B,  b = B
# After b ^= a:  a = A^B,  b = B^(A^B) = A^(B^B) = A^0 = A
# After a ^= b:  a = (A^B)^A = B^(A^A) = B^0 = B,  b = A
# ✓ a=B, b=A — swapped!

# CRITICAL EDGE CASE: never xor_swap with same variable/alias!
x = 5
# x ^= x → x = 0 (x XOR x = 0, data lost!)
# Safe in Python: just use x, y = y, x
```

**Why:** XOR is its own inverse: `(a ^ b) ^ b = a`. The three-step dance applies this inverse twice, threading the original values back through. Swapping a variable with itself destroys both copies (both become 0).

</details>

> 💻 Try it: [practice_local.py → Q15](./practice_local.py)

---

<a id="q16"></a>
### Q16 · xor-missing-number · Find the Gap

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)


🟡 Intermediate

**Problem:** An array contains `n` distinct values from `[0, n]` — one number is missing. Find the missing number using XOR in O(n) time, O(1) space. Test on `[3, 0, 1]`.

<details>
<summary>💡 Hint</summary>

XOR all expected values `0..n` together with all actual values in the array. Numbers that appear in both cancel. The only value left is the missing one.

</details>

<details>
<summary>✅ Answer</summary>

```python
def missing_number(nums: list) -> int:
    n = len(nums)
    result = n   # start with n (the last expected value)
    for i, num in enumerate(nums):
        result ^= i ^ num   # XOR expected index AND actual value
    return result

print(missing_number([3, 0, 1]))           # 2
print(missing_number([9,6,4,2,3,5,7,0,1])) # 8
print(missing_number([1, 2, 3]))           # 0  (missing 0)

# Trace for [3, 0, 1] (n=3):
# result = 3
# i=0, num=3: result ^= 0 ^ 3 = 3 ^ 0 ^ 3 = 0
# i=1, num=0: result ^= 1 ^ 0 = 0 ^ 1 ^ 0 = 1
# i=2, num=1: result ^= 2 ^ 1 = 1 ^ 2 ^ 1 = 2  ← answer!

# COMMON MISTAKE: starting range at 1 misses when 0 is the missing value
# CORRECT: range must be 0 to n inclusive
```

**Why:** For each value `v` that IS present, it appears as both an "expected" value and an "actual" value — they cancel. Only the missing value appears in the expected set but not the actual set, so it survives.

</details>

> 💻 Try it: [practice_local.py → Q16](./practice_local.py)

---

<a id="q17"></a>
### Q17 · isolate-lsb · Isolate Lowest Set Bit

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)


🟡 Intermediate

**Problem:** Given `n = 42 = 0b101010`, use a bit trick to extract only its lowest set bit. What is the result? What formula gives the lowest set bit, and how does it work in two's complement?

<details>
<summary>💡 Hint</summary>

Two's complement negation: `-n = ~n + 1`. This flips all bits then adds 1, which carries into the position of the lowest set bit. AND-ing `n & (-n)` isolates exactly that bit.

</details>

<details>
<summary>✅ Answer</summary>

```python
def lowest_set_bit(n: int) -> int:
    return n & (-n)

print(lowest_set_bit(42))   # 2  (42=101010, lowest set bit is bit 1 = value 2)
print(lowest_set_bit(40))   # 8  (40=101000, lowest set bit is bit 3 = value 8)
print(lowest_set_bit(32))   # 32 (32=100000, only one bit set)
print(lowest_set_bit(12))   # 4  (12=1100,   lowest set bit is bit 2 = value 4)

# How it works for n=42 (101010):
# -42 in two's complement: flip all bits → 010101, add 1 → 010110
# 42  & (-42) = 101010 & 010110 = 000010 = 2  ✓

# Application: Brian Kernighan uses n & (n-1) to REMOVE lowest set bit
# This formula ISOLATES it (keeps only that bit)
# Use n & (-n) when you need the VALUE of the lowest set bit
# Use n & (n-1) when you need to CLEAR it
```

**Why:** In two's complement, `-n` is the unique number such that `n + (-n) = 0`. The addition produces a carry that ripples up from the lowest set bit, leaving all bits below it flipped and all bits above it unchanged. AND isolates the single bit where both `n` and `-n` agree.

</details>

> 💻 Try it: [practice_local.py → Q17](./practice_local.py)

---

<a id="q18"></a>
### Q18 · hamming-distance · Bits That Differ

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)


🟡 Intermediate

**Problem:** The **Hamming distance** between two integers is the number of bit positions where they differ. Compute `hamming_distance(1, 4)` and `hamming_distance(93, 73)`. Solve in two lines.

<details>
<summary>💡 Hint</summary>

XOR produces 1 wherever two bits differ. Count the 1-bits in the XOR result.

</details>

<details>
<summary>✅ Answer</summary>

```python
def hamming_distance(x: int, y: int) -> int:
    return bin(x ^ y).count('1')

print(hamming_distance(1, 4))    # 2
# 1   = 001
# 4   = 100
# XOR = 101  → 2 differing bits

print(hamming_distance(93, 73))  # 2
# 93  = 1011101
# 73  = 1001001
# XOR = 0010100  → 2 differing bits

# Brian Kernighan version (faster for sparse differences):
def hamming_distance_kernighan(x: int, y: int) -> int:
    xor = x ^ y
    count = 0
    while xor:
        xor &= xor - 1
        count += 1
    return count

print(hamming_distance_kernighan(1, 4))   # 2
```

**Why:** XOR is the "difference" operator — bit by bit, it marks every position where the inputs disagree. Counting the 1s in the XOR is identical to counting differing positions. Used in error-correcting codes and DNA sequence analysis.

</details>

> 💻 Try it: [practice_local.py → Q18](./practice_local.py)

---

<a id="q19"></a>
### Q19 · xor-two-unique · Single Number III — Two Unique Elements

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)


🟠 Advanced

**Problem:** Given `nums = [1, 2, 1, 3, 2, 5]`, find the two elements that appear exactly once. All others appear exactly twice. Solve in O(n) time and O(1) space.

<details>
<summary>💡 Hint</summary>

Step 1: XOR all elements to get `a ^ b` (the two uniques XOR'd together). Step 2: Find any bit where `a` and `b` differ — use the **lowest set bit** of `a ^ b`. Step 3: Split the array into two groups using that bit. XOR each group — the uniques separate into different groups.

</details>

<details>
<summary>✅ Answer</summary>

```python
def single_number_iii(nums: list) -> list:
    # Step 1: xor_all = a ^ b
    xor_all = 0
    for n in nums:
        xor_all ^= n

    # Step 2: find a bit where a and b differ
    # (any set bit in xor_all works — use the lowest)
    diff_bit = xor_all & (-xor_all)

    # Step 3: partition numbers into two groups
    a, b = 0, 0
    for n in nums:
        if n & diff_bit:
            a ^= n   # group 1: has diff_bit set
        else:
            b ^= n   # group 2: doesn't have diff_bit set

    return [a, b]

print(single_number_iii([1, 2, 1, 3, 2, 5]))   # [3, 5] (order may vary)

# Trace for [1, 2, 1, 3, 2, 5]:
# xor_all = 1^2^1^3^2^5 = 3^5 = 6 (0b110)
# diff_bit = 6 & (-6) = 2 (bit 1 — a bit where 3 and 5 differ)
# Group A (bit 1 set):   2, 2, 6... → XOR = ?
# Group B (bit 1 unset): 1, 1, 3, 5 → XOR = 3^5 no... let's verify:
# 3=011 has bit 1 set; 5=101 does NOT have bit 1 set
# So 3 goes to group A, 5 to group B. Duplicates cancel.
```

**Why:** `a ^ b` tells us that `a` and `b` are not equal. The set bits in `a ^ b` mark positions where they differ. Splitting the array by one of those bits guarantees `a` and `b` land in different groups. Within each group, duplicates cancel by XOR, leaving only one unique element.

</details>

> 💻 Try it: [practice_local.py → Q19](./practice_local.py)

---

<a id="q20"></a>
### Q20 · bitwise-complement · Flip Only Significant Bits

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)


🟠 Advanced

**Problem:** The **bitwise complement** of `n` flips only its significant bits (not infinite leading 0s). Compute `complement(5)` — the answer should be `2` (`101 → 010`), not Python's `~5 = -6`. Why is naive `~n` wrong here?

<details>
<summary>💡 Hint</summary>

Python integers have arbitrary precision — `~5` flips ALL bits including infinite leading 1s in two's complement, giving -6. You only want to flip the bits `n` actually uses. Use `n.bit_length()` to find how many bits to flip.

</details>

<details>
<summary>✅ Answer</summary>

```python
def complement(n: int) -> int:
    if n == 0:
        return 1
    bit_length = n.bit_length()
    mask = (1 << bit_length) - 1   # all 1s up to n's bit length
    return (~n) & mask              # flip, then mask to significant bits

print(complement(5))    # 2   (101 → 010)
print(complement(1))    # 0   (1   → 0)
print(complement(7))    # 0   (111 → 000)
print(complement(10))   # 5   (1010 → 0101)

# Why ~n is wrong in Python:
print(~5)               # -6  (Python: ...111111111010, not just 010)

# Trace for n=5 (101):
# bit_length = 3
# mask = (1 << 3) - 1 = 7 = 0b111
# ~5 = -6 = ...11111010  (arbitrary precision)
# -6 & 7 = ...11111010 & 000...0111 = 0b010 = 2  ✓
```

**Why:** Python integers are conceptually infinite-precision two's complement — `~5` flips all bits, including the infinite leading zeros (which become infinite leading 1s, i.e., a negative number). Masking with `(1 << bit_length) - 1` restricts the flip to only the meaningful bits.

</details>

> 💻 Try it: [practice_local.py → Q20](./practice_local.py)

---

<a id="q21"></a>
### Q21 · bit-masking · Subset Enumeration

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)


🟠 Advanced

**Problem:** Given `elements = [10, 20, 30]`, enumerate ALL subsets (including empty set) using bit masking. For each subset, print the bitmask in binary and the subset contents.

<details>
<summary>💡 Hint</summary>

For `n` elements, there are `2^n` subsets. Represent each subset as a number from `0` to `2^n - 1`. Bit `i` being set means element `i` is included. Iterate `mask` from `0` to `(1 << n) - 1`.

</details>

<details>
<summary>✅ Answer</summary>

```python
def enumerate_subsets(elements: list) -> None:
    n = len(elements)
    for mask in range(1 << n):   # 0 to 2^n - 1
        subset = [elements[i] for i in range(n) if mask & (1 << i)]
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

# Count: 2^3 = 8 subsets total ✓

# To check if element i is in mask:
def in_subset(mask: int, i: int) -> bool:
    return bool(mask & (1 << i))

# To add element i to mask:
def add_to_subset(mask: int, i: int) -> int:
    return mask | (1 << i)
```

**Why:** Each bit in the mask is an independent yes/no decision for one element. With `n` elements and 2 choices each, there are exactly `2^n` combinations — exactly the number of integers from `0` to `2^n - 1`. This is the foundation of bitmask DP.

</details>

> 💻 Try it: [practice_local.py → Q21](./practice_local.py)

---

<a id="q22"></a>
### Q22 · subset-sum · Brute Force via Bitmask

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)


🟠 Advanced

**Problem:** Given `nums = [3, 1, 4, 2]` and `target = 6`, use bitmask enumeration to determine if any subset sums to the target. Return the first such subset found.

<details>
<summary>💡 Hint</summary>

Enumerate all `2^n` subsets using a mask. For each mask, sum the elements where the corresponding bit is set. Check if the sum equals the target.

</details>

<details>
<summary>✅ Answer</summary>

```python
def subset_sum(nums: list, target: int):
    n = len(nums)
    for mask in range(1 << n):
        total = sum(nums[i] for i in range(n) if mask & (1 << i))
        if total == target:
            subset = [nums[i] for i in range(n) if mask & (1 << i)]
            return subset
    return None

print(subset_sum([3, 1, 4, 2], 6))    # [4, 2] or [3, 1, 2]
print(subset_sum([3, 1, 4, 2], 11))   # None

# Complexity: O(2^n * n) — only feasible for small n (n ≤ 20)
# For large n, use dynamic programming instead

# Count all subsets summing to target:
def count_subset_sum(nums: list, target: int) -> int:
    n = len(nums)
    count = 0
    for mask in range(1 << n):
        if sum(nums[i] for i in range(n) if mask & (1 << i)) == target:
            count += 1
    return count

print(count_subset_sum([3, 1, 4, 2], 6))   # 2 (3+1+2=6 and 4+2=6)
```

**Why:** Bitmask enumeration tries all possible subsets exhaustively. For small `n` (up to ~20), this is practical. The `mask & (1 << i)` pattern is the standard idiom for "is element `i` included in this subset?"

</details>

> 💻 Try it: [practice_local.py → Q22](./practice_local.py)

---

<a id="q23"></a>
### Q23 · xor-mod3 · Single Number II — Appears Three Times

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)


🟠 Advanced

**Problem:** Given `nums = [2, 2, 3, 2]`, find the element that appears exactly once. All others appear exactly three times. XOR alone won't work — explain why, and implement the correct solution.

<details>
<summary>💡 Hint</summary>

XOR cancels pairs (`a ^ a = 0`), but triples need modulo-3 arithmetic. For each of the 32 bit positions, count how many numbers have that bit set. If the count is not divisible by 3, the unique element has that bit set.

</details>

<details>
<summary>✅ Answer</summary>

```python
def single_number_ii(nums: list) -> int:
    """Find the element appearing once; all others appear exactly three times."""
    result = 0
    for i in range(32):
        bit_sum = sum((n >> i) & 1 for n in nums)
        if bit_sum % 3:
            result |= (1 << i)

    # Python 32-bit signed conversion (for negative numbers):
    if result >= (1 << 31):
        result -= (1 << 32)
    return result

print(single_number_ii([2, 2, 3, 2]))          # 3
print(single_number_ii([0, 1, 0, 1, 0, 1, 99])) # 99

# Why XOR alone fails:
# [2, 2, 3, 2] → 2^2^3^2 = 3^2 = 1  ← WRONG (XOR only handles pairs)
# XOR accumulates mod-2; we need mod-3 counting

# How this works:
# For each bit position, count how many numbers have it set.
# If count % 3 == 0: unique element has 0 in that position
# If count % 3 == 1: unique element has 1 in that position
# (Because 3 copies of any bit contribute count % 3 == 0)
```

**Why:** XOR is modulo-2 arithmetic bit by bit. When duplicates appear 3 times, we need modulo-3 counting. Summing each bit across all numbers and taking `% 3` isolates the unique element's contribution at each bit position.

</details>

> 💻 Try it: [practice_local.py → Q23](./practice_local.py)

---

<a id="q24"></a>
### Q24 · bit-adder · Add Without Arithmetic

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)


🟠 Advanced

**Problem:** Implement addition of two non-negative integers using only XOR (sum without carry) and AND + left shift (carry). No `+`, `-`, `*`, or `/` operators. Handle the Python infinite-precision caveat with a 32-bit mask.

<details>
<summary>💡 Hint</summary>

In binary addition: `a XOR b` gives the bits that differ (the sum without carry). `(a AND b) << 1` gives the carry bits. Repeat until carry is zero. Mask to 32 bits to prevent Python's integers from growing infinitely.

</details>

<details>
<summary>✅ Answer</summary>

```python
def add_no_arithmetic(a: int, b: int) -> int:
    """Add two 32-bit integers using only bitwise operations."""
    MASK = 0xFFFFFFFF   # 32-bit mask
    MAX  = 0x7FFFFFFF   # max positive 32-bit signed integer

    while b & MASK:
        carry = (a & b) << 1   # carry: positions where both bits are 1
        a = a ^ b              # sum without carry
        b = carry
        a &= MASK              # keep 32-bit width
        b &= MASK

    # Convert back to Python signed if result is negative in 32-bit
    return a if a <= MAX else ~(a ^ MASK)

print(add_no_arithmetic(1, 2))    # 3
print(add_no_arithmetic(0, 0))    # 0
print(add_no_arithmetic(100, 200)) # 300

# Step trace for 5 + 3:
# a=101, b=011
# carry = (101 & 011) << 1 = 001 << 1 = 010
# a     = 101 ^ 011 = 110
# b     = 010
# Next iteration:
# carry = (110 & 010) << 1 = 010 << 1 = 100
# a     = 110 ^ 010 = 100
# b     = 100
# Next:
# carry = (100 & 100) << 1 = 100 << 1 = 1000
# a     = 100 ^ 100 = 000
# b     = 1000
# ... continues, final a = 8 = 5+3 ✓
```

**Why:** Binary addition is XOR (sum) plus AND-shifted (carry). Repeating until the carry becomes zero simulates full addition. The 32-bit mask is critical in Python — without it, the carry `<< 1` grows without bound for negative numbers.

</details>

> 💻 Try it: [practice_local.py → Q24](./practice_local.py)

---

<a id="q25"></a>
### Q25 · bitmask-dp · Traveling Salesman Skeleton

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)


🟠 Advanced

**Problem:** Given 4 cities and a distance matrix, use **bitmask DP** to find the minimum cost Hamiltonian cycle starting and ending at city 0. Explain the state `dp[mask][i]` and the transition formula.

<details>
<summary>💡 Hint</summary>

State: `dp[mask][i]` = minimum cost to have visited exactly the cities in `mask`, currently at city `i`. Transition: from state `(mask, i)`, move to unvisited city `j`: `dp[mask | (1 << j)][j] = dp[mask][i] + dist[i][j]`. Answer: `min(dp[FULL_MASK][i] + dist[i][0])` for all `i`.

</details>

<details>
<summary>✅ Answer</summary>

```python
def tsp_bitmask(dist: list) -> int:
    """Minimum cost Hamiltonian cycle starting/ending at city 0."""
    n = len(dist)
    FULL_MASK = (1 << n) - 1   # all cities visited
    INF = float('inf')

    # dp[mask][i] = min cost to visit cities in 'mask', ending at city i
    dp = [[INF] * n for _ in range(1 << n)]
    dp[1][0] = 0   # mask=0001: visited city 0 only, at city 0, cost=0

    for mask in range(1 << n):
        for i in range(n):
            if dp[mask][i] == INF:
                continue
            if not (mask & (1 << i)):
                continue   # city i not in this state's visited set

            # Extend: move from i to each unvisited city j
            for j in range(n):
                if mask & (1 << j):
                    continue   # j already visited
                new_mask = mask | (1 << j)
                new_cost = dp[mask][i] + dist[i][j]
                if new_cost < dp[new_mask][j]:
                    dp[new_mask][j] = new_cost

    # Return to city 0 from the last city visited
    return min(dp[FULL_MASK][i] + dist[i][0] for i in range(1, n))

dist = [
    [0, 10, 15, 20],
    [10,  0, 35, 25],
    [15, 35,  0, 30],
    [20, 25, 30,  0]
]
print(tsp_bitmask(dist))   # 80 (path: 0→1→3→2→0 = 10+25+30+15=80)

# Complexity: O(2^n * n^2)
# Feasible for n ≤ 20 (2^20 * 400 ≈ 400M operations)
# FULL_MASK = (1 << n) - 1, NOT (1 << n) — off-by-one is a common mistake
```

**Why:** The bitmask encodes "which cities have been visited" as a single integer. Each subset of cities is a unique integer. We enumerate transitions from smaller masks to larger masks (adding one city at a time). The DP avoids re-exploring the same (visited-set, current-city) pair multiple times.

</details>

> 💻 Try it: [practice_local.py → Q25](./practice_local.py)

---

## Navigation

---
**[⬅️ Theory](./theory.md)** · **[💻 Local Practice](./practice_local.py)**

**Prev:** [← 21_dynamic_programming](../21_dynamic_programming/practice.md) | **Next:** [23_segment_tree →](../23_segment_tree/practice.md)
