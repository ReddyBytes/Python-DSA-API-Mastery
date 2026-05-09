<a id="top"></a>
# Bit Manipulation — Controlling the Machine at Binary Level

> Computers don't understand numbers like we do.
> They understand only 0 and 1.
>
> Bit manipulation means:
> Talking directly in computer's language.

Bit manipulation is:

- Fast
- Efficient
- Often used in optimization
- Frequently tested in interviews

Once you understand binary,
this becomes fun.

## 📖 Table of Contents

1. [Real Life Story — Light Switch Board](#1-real-life-story)
2. [Understanding Binary Numbers](#2-understanding-binary-numbers)
3. [Bitwise Operators](#3-bitwise-operators)
4. [Important Bit Tricks](#4-important-bit-tricks)
5. [XOR Special Properties](#5-xor-special-properties)
6. [Subset Generation Using Bits](#6-subset-generation-using-bits)
7. [Bitmasking](#7-bitmasking)
8. [Why Bit Manipulation Is Fast](#8-why-bit-manipulation-is-fast)
9. [Real-World Applications](#9-real-world-applications)
10. [Common Mistakes Reference](#10-common-mistakes-reference)
11. [Mental Model](#11-mental-model)
12. [Final Understanding](#12-final-understanding)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
bitwise operators (AND OR XOR NOT shifts) · check even/odd · power of two check

**Should Learn** — Important for real projects, comes up regularly:
XOR properties · bitmask for subsets · count set bits

**Good to Know** — Useful in specific situations, not always tested:
swap without temp · clear/set/toggle bit patterns

**Reference** — Know it exists, look up syntax when needed:
gray code · Hamming codes · parity checking

<a id="1-real-life-story"></a>
# 1. Real Life Story — Light Switch Board

Imagine a switch board with 8 switches.

Each switch can be:

ON (1)
OFF (0)

Example:

```
Switches: 1 0 1 1 0 0 1 0
```

That's a binary number.

Each switch represents a bit.

Bit manipulation means:
Turning switches ON or OFF intelligently.

## Visual: The Switch Board

Your computer doesn't understand numbers the way you do. It only understands one thing:
**is the electricity flowing, or not?**

On = 1. Off = 0.

A single bit is a light switch. Eight bits is a row of eight switches. That row of switches
is how your computer stores every number, every character, every pixel on your screen.

Let's take the number **13** and represent it as switches:

```
Binary:    1    1    0    1
           │    │    │    │
Switch:   [ON] [ON] [OFF][ON]
           │    │    │    │
Place:     8    4    2    1
```

Add the "ON" places: 8 + 4 + 0 + 1 = **13**

That's it. That's binary. Each position is worth twice the previous:
```
Position:  7    6    5    4    3    2    1    0
Value:    128   64   32   16    8    4    2    1
```

> [↑ Back to Top](#top)

<a id="2-understanding-binary-numbers"></a>
# 2. Understanding Binary Numbers

Example:

Decimal 5 in binary:

```
5 = 101
```

Position values:

```
(1 × 2²) + (0 × 2¹) + (1 × 2⁰)
```

Binary is base 2.

Each bit represents power of 2.

## Visual: Binary Number Examples

Let's check a few numbers:
```
13 = 8+4+1   = 1101₂   (4 bits)
10 = 8+2     = 1010₂   (4 bits)
 7 = 4+2+1   = 0111₂   (4 bits)
 8 = 8       = 1000₂   (4 bits, only one switch on)
```

> 📝 **Practice:** [Q1 — Read a Bit](./practice.md#q1--binary-representation--read-a-bit)

> [↑ Back to Top](#top)

<a id="3-bitwise-operators"></a>
# 3. Bitwise Operators

> 📝 **Practice:** [Q64 · bit-manipulation-basics](../dsa_practice_questions_100.md#q64--normal--bit-manipulation-basics)

## Visual: Six Operations on 13 and 10

Let's work with two numbers throughout:
```
13 = 1101₂
10 = 1010₂
```

## 🔹 AND (&)

1 & 1 = 1
Else = 0

Rule: output is 1 only if BOTH bits are 1. Like a series circuit — both switches must be on.

```
  13 = 1 1 0 1
  10 = 1 0 1 0
       -------
AND  = 1 0 0 0  =  8
```

Position by position:
```
Bit 3:  1 AND 1 = 1   (both on)
Bit 2:  1 AND 0 = 0   (one off)
Bit 1:  0 AND 1 = 0   (one off)
Bit 0:  1 AND 0 = 0   (one off)
```

Used for masking.

> 📝 **Practice:** [Q2 — Mask Out Lower Bits](./practice.md#q2--bitwise-and--mask-out-lower-bits)

## 🔹 OR (|)

1 | 0 = 1
0 | 0 = 0

Rule: output is 1 if EITHER bit is 1. Like a parallel circuit — either switch works.

```
  13 = 1 1 0 1
  10 = 1 0 1 0
       -------
OR   = 1 1 1 1  =  15
```

```
Bit 3:  1 OR 1 = 1   (either on)
Bit 2:  1 OR 0 = 1   (one on)
Bit 1:  0 OR 1 = 1   (one on)
Bit 0:  1 OR 0 = 1   (one on)
```

Used to set bits.

> 📝 **Practice:** [Q3 — Set a Specific Bit](./practice.md#q3--bitwise-or--set-a-specific-bit)

## 🔹 XOR (^)

Same bits → 0
Different bits → 1

Rule: output is 1 if bits are DIFFERENT. The "odd one out" operation.

```
  13 = 1 1 0 1
  10 = 1 0 1 0
       -------
XOR  = 0 1 1 1  =  7
```

```
Bit 3:  1 XOR 1 = 0   (same — cancel out)
Bit 2:  1 XOR 0 = 1   (different — keep)
Bit 1:  0 XOR 1 = 1   (different — keep)
Bit 0:  1 XOR 0 = 1   (different — keep)
```

Very powerful operator.

> 📝 **Practice:** [Q65 · xor-single-number](../dsa_practice_questions_100.md#q65--logical--xor-single-number)

> 📝 **Practice:** [Q4 — Flip Bits Selectively](./practice.md#q4--bitwise-xor--flip-bits-selectively)

## 🔹 NOT (~)

Flips bits.

Rule: 0 becomes 1, 1 becomes 0.

```
  13 = 0000 ... 0000 1101    (in 32/64-bit representation)
 ~13 = 1111 ... 1111 0010    (all bits flipped)
```

In Python: `~13 = -14`. Why -14 and not 2?

Because Python uses **two's complement** for negative numbers:
- Flipping all bits and interpreting the result as signed gives -(n+1)
- ~13 = -(13+1) = -14
- This is intentional — it makes arithmetic circuits simpler

Just remember: `~n = -(n+1)` in Python.

**Common mistake — Python's ~ gives -(n+1), not a 32-bit complement:** In C and Java, `~0` gives `0xFFFFFFFF`. In Python, integers have arbitrary precision so `~0 = -1`. When you need 32-bit unsigned NOT, use `(~n) & 0xFFFFFFFF`. For complement of only the meaningful bits, use `(~n) & ((1 << n.bit_length()) - 1)`.

## 🔹 Left Shift (<<)

Rule: slide all bits to the left, fill the right with zeros.

5 << 1:

101 → 1010 = 10

```
  13 = 1101
  13 << 1:
  Before: 0 0 0 0 1 1 0 1
  After:  0 0 0 1 1 0 1 0  =  26  (13 × 2)

  13 << 2:
  Before: 0 0 0 0 1 1 0 1
  After:  0 0 1 1 0 1 0 0  =  52  (13 × 4)
```

Multiply by 2. Each left shift multiplies by 2. This is FAST — the CPU does it in a single clock cycle.

**Common mistake — left shift overflow in 32-bit contexts:** In Python, `1 << 32` succeeds and produces a 33-bit value without error. If you are simulating 32-bit logic, validate that `0 <= pos < 32` before shifting and apply `& 0xFFFFFFFF` after the operation to mask back to 32 bits.

## 🔹 Right Shift (>>)

Rule: slide all bits to the right, drop the rightmost bit.

8 >> 1:

1000 → 0100 = 4

```
  13 = 1101
  13 >> 1:
  Before: 0 0 0 0 1 1 0 1
  After:  0 0 0 0 0 1 1 0  =  6  (13 ÷ 2, rounded down)

  13 >> 2:
  Before: 0 0 0 0 1 1 0 1
  After:  0 0 0 0 0 0 1 1  =  3  (13 ÷ 4, rounded down)
```

Divide by 2 (integer division). The dropped bits are just gone.

> 📝 **Practice:** [Q5 — Multiply and Divide by Powers of 2](./practice.md#q5--shifts--multiply-and-divide-by-powers-of-2)

> [↑ Back to Top](#top)

<a id="4-important-bit-tricks"></a>
# 4. Important Bit Tricks

## 🔹 Check If Number Is Even

Last bit 0 → even

```
if n & 1 == 0:
```

> 📝 **Practice:** [Q6 — Parity Check Without Modulo](./practice.md#q6--even-odd--parity-check-without-modulo)

## 🔹 Check If Power of Two

Power of two has only one 1 bit.

Example:
8 = 1000

Trick:

```
n & (n - 1) == 0
```

Works because:

1000
0111
----
0000

## Visual: Power of 2 — The Beautiful Trick

**Why does this work?** Powers of 2 have exactly ONE bit set:

```
1  = 0001
2  = 0010
4  = 0100
8  = 1000
16 = 10000
```

When you subtract 1 from a power of 2, all the lower bits flip ON and the single 1 turns OFF:

```
8     = 1 0 0 0
8 - 1 = 0 1 1 1
─────────────────
AND   = 0 0 0 0  ← Always zero for powers of 2!
```

Now check a NON-power of 2, like 6:

```
6     = 0 1 1 0
6 - 1 = 0 1 0 1
─────────────────
AND   = 0 1 0 0  ← Not zero! So 6 is NOT a power of 2.
```

The logic: for powers of 2, subtracting 1 flips exactly the bits we want to cancel out.
For anything else, there are "leftover" bits that don't cancel.

```python
def is_power_of_2(n):
    return n > 0 and (n & (n - 1)) == 0
```

**Common mistake — operator precedence in power-of-two check:** Writing `n & n - 1 == 0` is parsed as `n & (n-1 == 0)` because arithmetic `-` binds tighter than `&`, and `==` is lower than both — so you get `n & (False or True)` instead of the AND result compared to zero. Always write `(n & (n - 1)) == 0`.

> 📝 **Practice:** [Q11 — Power of 2 Check](./practice.md#q11--power-of-2--one-bit-trick)

## 🔹 Count Set Bits

Use:

Brian Kernighan's Algorithm:

```
while n:
    n = n & (n - 1)
    count += 1
```

Removes lowest set bit each time.

Time:
O(number of set bits)

## Visual: Brian Kernighan Step-by-Step

**Key insight:** `n & (n-1)` removes exactly the lowest set bit.

```
n = 13 = 1 1 0 1

Step 1: n = 13 = 1101
        n-1 = 12 = 1100
        13 & 12 = 1100 = 12
        (removed the lowest 1 bit, which was at position 0)
        count = 1

Step 2: n = 12 = 1100
        n-1 = 11 = 1011
        12 & 11 = 1000 = 8
        (removed the lowest 1 bit, which was at position 2)
        count = 2

Step 3: n = 8 = 1000
        n-1 = 7 = 0111
        8 & 7 = 0000 = 0
        (removed the lowest 1 bit, which was at position 3)
        count = 3

Step 4: n = 0. Stop.
```

**Result: 3 set bits** (13 = 1101, which has three 1s). Correct!

The algorithm runs in O(number of set bits), not O(total bits).
For a number with few set bits, this is much faster.

```python
def count_set_bits(n):
    count = 0
    while n:
        n &= (n - 1)   # remove lowest set bit
        count += 1
    return count
```

**Common mistake — using naive bit loop instead of Kernighan:** The naive loop `while n: count += n & 1; n >>= 1` is O(log n) — it iterates over every bit position including leading zeros. Brian Kernighan's `n &= (n-1)` runs in O(k) where k is the number of set bits. For a number like `1 << 30` (one bit set), the naive loop takes 31 iterations; Kernighan's takes 1. Python 3.10+ also provides `int.bit_count()`.

> 📝 **Practice:** [Q66 · count-set-bits](../dsa_practice_questions_100.md#q66--thinking--count-set-bits)

> 📝 **Practice:** [Q12 — Brian Kernighan Count](./practice.md#q12--count-set-bits--brian-kernighan) · [Q13 — Count Bits DP](./practice.md#q13--count-set-bits-dp--count-bits-0n-dp)

## 🔹 Swap Without Temp Variable

```
a = a ^ b
b = a ^ b
a = a ^ b
```

XOR trick.

> 📝 **Practice:** [Q15 — XOR Swap](./practice.md#q15--xor-swap--no-temp-variable)

## Visual: Cheat Sheet — Common Bit Tricks

```
Operation                    Code              Example (n=13=1101)
──────────────────────────────────────────────────────────────────
Check if power of 2          n & (n-1) == 0    12 & 11 = 8 ≠ 0  → Not power of 2
Remove lowest set bit        n & (n-1)         1101 & 1100 = 1100
Get lowest set bit           n & (-n)          1101 & 0011 = 0001
Set bit i                    n | (1 << i)      set bit 1: 1101 | 0010 = 1111
Clear bit i                  n & ~(1 << i)     clear bit 2: 1101 & 1011 = 1001
Toggle bit i                 n ^ (1 << i)      toggle bit 1: 1101 ^ 0010 = 1111
Check bit i                  (n >> i) & 1      check bit 2: (1101 >> 2) & 1 = 1
Multiply by 2^k              n << k            13 << 2 = 52
Divide by 2^k                n >> k            13 >> 2 = 3
```

> [↑ Back to Top](#top)

<a id="5-xor-special-properties"></a>
# 5. XOR Special Properties

1. a ^ a = 0
2. a ^ 0 = a
3. XOR is commutative

Used in:

Finding single number in array.

Example:

[2, 3, 2, 4, 4]

XOR all:
Result = 3

Because duplicates cancel.

## Visual: XOR — The Disappearing Trick

XOR has three magical properties:

```
Property 1:  a XOR 0 = a     (XOR with zero changes nothing)
Property 2:  a XOR a = 0     (XOR with yourself = zero — you cancel out)
Property 3:  a XOR b XOR a = b   (apply twice = disappear)
```

Property 3 is wild. Let's verify:

```
a = 5  = 101
b = 9  = 1001

a XOR b:   101 XOR 1001 = 1100 = 12
(12) XOR a: 1100 XOR 0101 = 1001 = 9 = b   ✓
```

The two `a`s cancelled each other out, leaving only `b`.

**Classic problem: Find the single number**

Given an array where every number appears exactly TWICE except one. Find the lone number.

```
Array: [4, 1, 2, 1, 2]
```

Brute force: count frequencies. O(n) space.

XOR trick: XOR everything together.

```
4 XOR 1 XOR 2 XOR 1 XOR 2

= 4 XOR (1 XOR 1) XOR (2 XOR 2)   (rearranging — XOR is associative and commutative)

= 4 XOR 0 XOR 0

= 4
```

Every number that appears twice XORs to 0. The lone number XORs with 0 and stays itself.
O(n) time, O(1) space. Beautiful.

```python
def find_single(nums):
    result = 0
    for num in nums:
        result ^= num       # XOR everything together
    return result           # pairs cancel, only singleton remains
```

**Common mistake — XOR missing number: forgetting to XOR the full expected range:** When finding a missing number from `[0..n]`, you must XOR every value in `range(0, n+1)` together with every array element. XORing only the array elements gives a wrong answer. Also ensure the range starts at 0, not 1 — if 0 is the missing number, starting the range at 1 silently fails.

> 📝 **Practice:** [Q14 — Single Number I](./practice.md#q14--xor-cancellation--single-number-i) · [Q19 — Single Number III](./practice.md#q19--xor-two-unique--single-number-iii--two-unique-elements) · [Q23 — Single Number II](./practice.md#q23--xor-mod3--single-number-ii--appears-three-times)

> [↑ Back to Top](#top)

<a id="6-subset-generation-using-bits"></a>
# 6. Subset Generation Using Bits

For n elements:

Total subsets = 2^n

Represent each subset as binary number.

Example:

Elements: [A, B, C]

Binary:
000 → []
001 → [C]
010 → [B]
011 → [B, C]
100 → [A]
...

Very clean method.

## Visual: Bitmask for Subsets — A Tiny Map

Imagine you have a set of 3 items: **[A, B, C]**.

Each subset can be represented as a 3-bit number:
- Bit 0 (value 1) = is A included?
- Bit 1 (value 2) = is B included?
- Bit 2 (value 4) = is C included?

```
Mask  Binary  Subset        Meaning
───────────────────────────────────────
  0   0 0 0   {}            Nothing selected
  1   0 0 1   {A}           Only A
  2   0 1 0   {B}           Only B
  3   0 1 1   {A, B}        A and B
  4   1 0 0   {C}           Only C
  5   1 0 1   {A, C}        A and C
  6   1 1 0   {B, C}        B and C
  7   1 1 1   {A, B, C}     Everything
```

For n items, there are 2ⁿ subsets. Each subset maps to a unique integer from 0 to 2ⁿ-1.

**Check if element i is in subset `mask`:**
```python
if mask & (1 << i):    # shift 1 to position i, then AND
    # element i is included
```

**Add element i to subset `mask`:**
```python
mask = mask | (1 << i)   # set bit i
```

**Remove element i from subset `mask`:**
```python
mask = mask & ~(1 << i)  # clear bit i
```

**Iterate over all subsets of n elements:**
```python
for mask in range(1 << n):      # 0 to 2^n - 1
    for i in range(n):
        if mask & (1 << i):
            # element i is in this subset
```

> 📝 **Practice:** [Q21 — Subset Enumeration](./practice.md#q21--bit-masking--subset-enumeration) · [Q22 — Subset Sum via Bitmask](./practice.md#q22--subset-sum--brute-force-via-bitmask)

> [↑ Back to Top](#top)

<a id="7-bitmasking"></a>
# 7. Bitmasking

Bitmask represents state.

Example:

For 4 items:

mask = 1010

Means:
Item 1 and Item 3 selected.

Used in:

- Traveling Salesman
- DP on subsets
- Game states

This is the foundation of **bitmask dynamic programming** — storing state as a bitmask to represent
which items have been "used" or "visited."

Advanced usage.

> 📝 **Practice:** [Q25 — Bitmask DP / TSP Skeleton](./practice.md#q25--bitmask-dp--traveling-salesman-skeleton)

> [↑ Back to Top](#top)

<a id="8-why-bit-manipulation-is-fast"></a>
# 8. Why Bit Manipulation Is Fast

Bit operations happen at hardware level.

Very low overhead.

Constant time operations.

Often faster than arithmetic.

Each left shift multiplies by 2 in a single CPU clock cycle. Each right shift divides by 2 the same way. Masking, setting, and clearing bits are all single-instruction operations on the CPU — no loops, no function calls.

> [↑ Back to Top](#top)

<a id="9-real-world-applications"></a>
# 9. Real-World Applications

- Encryption
- Compression
- Network protocols
- Operating systems
- Memory management
- Permission systems (UNIX file permissions)
- Flags in databases

Bit manipulation used heavily in systems.

> [↑ Back to Top](#top)

<a id="10-common-mistakes-reference"></a>
# 10. Common Mistakes Reference

This section summarises the key mistakes covered inline above.

**Common mistake — Python's ~ gives -(n+1):** `~n = -(n+1)` in Python due to arbitrary-precision two's complement. Simulate 32-bit NOT with `(~n) & 0xFFFFFFFF`.

**Common mistake — operator precedence without parentheses:** `n & n - 1 == 0` is NOT `(n & (n-1)) == 0`. Arithmetic `-` binds tighter than `&`; then `==` is lower than `&`. Result: `n & (n-1 == 0)`. Always parenthesize: `(n & (n - 1)) == 0`. Same rule applies to `(a & b) != 0` and `(flags & mask) == mask`.

**Common mistake — left shift in 32-bit contexts:** Python never overflows on shifts, but `1 << 32` produces a 33-bit value. Validate `0 <= pos < 32` and apply `& 0xFFFFFFFF` after set/clear/flip operations.

**Common mistake — XOR missing number range:** XOR the full expected range `range(0, n+1)`, not just the array. Missing `0` from the range silently breaks the algorithm when 0 is the absent value.

**Common mistake — naive bit loop vs Kernighan:** Naive `n & 1; n >>= 1` is O(log n). Brian Kernighan `n &= (n-1)` is O(k) where k = set bits. Prefer Kernighan in interviews; mention `int.bit_count()` for Python 3.10+.

Bit logic must be precise.

> [↑ Back to Top](#top)

<a id="11-mental-model"></a>
# 11. Mental Model

Think of bit manipulation as:

Controlling switches directly.

Instead of thinking in decimal,
think in ON/OFF states.

Every number is just pattern of switches.

Bit manipulation treats numbers as rows of switches: AND requires both on, OR needs one on,
XOR detects differences, and shifts multiply or divide by powers of 2 — giving you
direct hardware-speed control over data at the binary level.

> [↑ Back to Top](#top)

<a id="12-final-understanding"></a>
# 12. Final Understanding

Bit manipulation is:

- Working at binary level
- Extremely fast
- Powerful for optimization
- Used in subset problems
- Used in system-level programming
- Common in interviews

Mastering bits prepares you for:

- Advanced DP with bitmask
- System programming
- Competitive coding tricks
- Performance optimization

Bit manipulation is small but mighty.

> [↑ Back to Top](#top)

# 🔁 Navigation

Previous:
[21_dynamic_programming/interview.md](/02_DSA_Mastery/21_dynamic_programming/interview.md)

Next:
[22_bit_manipulation/interview.md](/02_DSA_Mastery/22_bit_manipulation/interview.md)
[23_segment_tree/theory.md](/02_DSA_Mastery/23_segment_tree/theory.md)

**[🏠 Back to README](../README.md)**

**Prev:** [← Dynamic Programming — Interview Q&A](../21_dynamic_programming/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheetsheet.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md)
